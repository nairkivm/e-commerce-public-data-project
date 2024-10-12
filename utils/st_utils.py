import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from unidecode import unidecode

import sys
import os
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..'
        )
    )
)

from utils.utils import DataUtils
from utils.constants import Constants

class StDataUtils(DataUtils):

    @st.cache_data
    def get_clean_data(_self) -> pd.DataFrame:
        # Initialize the constants
        c = Constants()

        # Extract all data into dictionary of pandas DataFrames
        data = {}
        for source_ in c.source.keys():
            data[source_] = pd.read_csv(c.source[source_])

        # Create modified_data variable
        modified_data = data

        # Correct invalid column names
        column_replacement = {
            'product_name_lenght': 'product_name_length',
            'product_description_lenght': 'product_description_length'
        }
        modified_data['products'] = (
            modified_data['products']
            .rename(columns=column_replacement)
        )

        # Remove duplicated data
        modified_data['geolocations'] = (
            modified_data['geolocations']
            .drop_duplicates(subset='geolocation_zip_code_prefix', ignore_index=True)
        )

        # Handle missing value
        ## Handle missing value for
        ## - product_photos_qty column in products table
        ##   - Use imputation method with value=0
        modified_data['products']['product_photos_qty'] = (
            modified_data['products']['product_photos_qty']
            .fillna(value=0)
        )

        ## Handle missing value for
        ## - product_weight_g, product_length_cm, product_height_cm, product_width_cm columns in products table
        ##   - Use imputation method with value=mean
        missing_value_columns = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
        for col in missing_value_columns:
            modified_data['products'][col] = (
                modified_data['products'][col]
                .fillna(value=modified_data['products'][col].mean())
            )

        # Handle outlier value for
        ## - review_score in order_reviews table
        ##   - Use imputation method with value = mean

        ## Add a custom method to pandas DataFrame
        def impute_outlier(df: pd.DataFrame, col: str):
            Q1 = (df[col]).quantile(0.25)
            Q3 = (df[col]).quantile(0.75)
            IQR = Q3 - Q1
            
            maximum = Q3 + (1.5*IQR)
            minimum = Q1 - (1.5*IQR)

            condition_lower_than = df[col] < minimum
            condition_more_than = df[col] > maximum

            mean = df[col].mean()

            df.loc[condition_more_than, col] = mean
            df.loc[condition_lower_than, col] = mean

            return df

        ## Apply the method
        modified_data['order_reviews'] = impute_outlier(
            modified_data['order_reviews'],
            'review_score'
        )

        ## Ensure the result is between 'review_score' range [1,5] (0 = no participation)
        max_condition = modified_data['order_reviews']['review_score'] > 5
        min_condition = (modified_data['order_reviews']['review_score'] < 1) & (modified_data['order_reviews']['review_score'].notna())

        modified_data['order_reviews'].loc[max_condition, 'order_reviews'] = 5
        modified_data['order_reviews'].loc[min_condition, 'order_reviews'] = 1

        ## Ad-hoc: Normalize the city names
        modified_data['geolocations']['geolocation_city'] = modified_data['geolocations']['geolocation_city'].apply(unidecode)
        modified_data['customers']['customer_city'] = modified_data['customers']['customer_city'].apply(unidecode)
        modified_data['sellers']['seller_city'] = modified_data['sellers']['seller_city'].apply(unidecode)


        # Match the data types
        for table_ in c.requirements.keys():
            modified_data[table_] = (
                modified_data[table_]
                .astype(c.requirements[table_])
            )
        
        return modified_data


    @st.cache_data
    def get_filtered_data(_self,
                          data: dict, 
                          start_date: datetime, 
                          end_date: datetime,
                          order_status: list,
                          product_categories: list,
                          cities: list,
                          states: list) -> pd.DataFrame:

        # Filter the data
        ## Initialize the filter with true values
        start_filter = pd.Series([True for i, rows in data['orders'].iterrows()])
        end_filter = start_filter
        order_status_filter = start_filter

        ## Modify the filter based on the conditions
        if start_date:
            start_filter = (data['orders']['order_purchase_timestamp'].dt.date >= start_date)
        if end_date:
            end_filter = (data['orders']['order_purchase_timestamp'].dt.date <= end_date)
        if order_status:
            order_status_filter = (data['orders']['order_status'].isin(order_status))
        
        ## Filter the data (orders_df)
        orders_df = data['orders'][(start_filter & end_filter & order_status_filter)]

        ## For product_category_filter, create an order_items_df first
        order_items_df = (
            pd.merge(
                data['order_items'][['order_id', 'price', 'freight_value', 'product_id']],
                data['products'][['product_id', 'product_category_name']],
                how="left",
                on="product_id"
            )
            .merge(
                data['product_category_name_translations'][['product_category_name', 'product_category_name_english']],
                how="left",
                on="product_category_name"
            )
            .drop(columns=['product_category_name'])
        )

        ## Initialize the filter with true values
        product_category_filter = pd.Series([True for i, rows in order_items_df.iterrows()])

        ## Modify the filter based on the conditions
        if product_categories:
            product_category_filter = (order_items_df['product_category_name_english'].isin(product_categories))

        ## Filter the data (order_items_df)
        order_items_df = order_items_df[product_category_filter]

        ## Initialize the filter with true values
        cities_filter = pd.Series([True for i, rows in data['customers'].iterrows()])
        states_filter = cities_filter

        ## Modify the filter based on the conditions
        if cities:
            cities_filter = (data['customers']['customer_city'].isin([str(x).lower for x in cities]))
        if states:
            states_filter = (data['customers']['customer_state'].isin([str(x).lower for x in states]))
        
        ## Filter the data (customers_df)
        customers_df = data['customers'][(cities_filter & states_filter)][['customer_id', 'customer_unique_id', 'customer_city', 'customer_state', 'customer_zip_code_prefix']]

        # Merge all dfs
        filtered_df = (
            pd.merge(
                orders_df,
                order_items_df,
                how="left",
                on="order_id"
            )
            .merge(
                data['order_reviews'][['review_id', 'order_id', 'review_score']],
                how="left",
                on="order_id"
            )
            .merge(
                customers_df,
                how="left",
                on="customer_id"
            )
            .merge(
                data['geolocations'][['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state']],
                how="left",
                left_on="customer_zip_code_prefix",
                right_on="geolocation_zip_code_prefix"
            )
            .drop(columns=['geolocation_zip_code_prefix'])
        )

        return filtered_df

    @st.cache_data
    def get_order_funnel(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        # Note: filtered_df in this context is filtered_df without order_status_filter
        # Get funnel_df
        funnel_df = filtered_df.copy()

        ## Add year month column
        funnel_df['month'] = funnel_df['order_purchase_timestamp'].dt.strftime('%Y-%m')
        funnel_df = (
            funnel_df
            .groupby(['month','order_status'])
            .agg({
                "order_id": "nunique"
            })
            .reset_index()
            .rename(columns={'order_id': 'order_count'})
            .sort_values(by=['month','order_status'])
            .reset_index(drop=True)
        )
        return funnel_df
    
    @st.cache_data
    def get_order_success_rate(_self, funnel_df: pd.DataFrame) -> tuple:
        # Get latest & previous month
        prev_month, latest_month = sorted(list(funnel_df['month'].unique()))[-2:]

        # Get succes_df 
        success_df = funnel_df.copy()  
        success_df = success_df[success_df['order_status'] == 'delivered']

        # Get success count latest month
        try:
            latest_success_count = success_df[success_df['month'] == latest_month]['order_count'].values[0]
        except IndexError:
            latest_success_count = 0

        # Get success count previous month
        try:
            previous_success_count = success_df[success_df['month'] == prev_month]['order_count'].values[0]
        except IndexError:
            previous_success_count = 0
        
        # Get total_df
        total_df = funnel_df.copy()  
        total_df = total_df.groupby('month').agg({'order_count': 'sum'}).reset_index().sort_values(by='month').reset_index(drop=True)

        # Get total count latest month
        try:
            latest_total_count = total_df[total_df['month'] == latest_month]['order_count'].values[0]
        except IndexError:
            latest_total_count = 0

        # Get total count previous month
        try:
            previous_total_count = total_df[total_df['month'] == prev_month]['order_count'].values[0]
        except IndexError:
            previous_total_count = 0

        latest_success_rate = latest_success_count / latest_total_count
        previous_success_rate = previous_success_count / previous_total_count
        try:
            mom_success_rate = (latest_success_rate - previous_success_rate) / previous_success_rate
        except ZeroDivisionError:
            mom_success_rate = 0
        
        return latest_success_rate, mom_success_rate
    
    @st.cache_data
    def get_metrics_by_month(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the data
        metrics_df = (
            filtered_df
            .resample(rule='ME', on='order_purchase_timestamp')
            .agg({
                "order_id": "nunique",
                "customer_unique_id": "nunique",
                "price": "sum"
            })
            .reset_index()
            .rename(columns={
                'order_purchase_timestamp': 'month',
                'customer_unique_id': 'customer_count',
                'order_id': 'order_count',
                'price': 'revenue_w_o_freight'
            })
            .sort_values(by='month', ascending=True)
            .reset_index(drop=True)
        )

        return metrics_df
    
    @st.cache_data
    def get_metrics_by_quarter(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the data
        metrics_df = (
            filtered_df
            .resample(rule='QE', on='order_purchase_timestamp')
            .agg({
                "order_id": "nunique",
                "customer_unique_id": "nunique",
                "price": "sum"
            })
            .reset_index()
            .rename(columns={
                'order_purchase_timestamp': 'Quarter',
                'customer_unique_id': 'Customer',
                'order_id': 'Order',
                'price': 'Revenue'
            })
            .sort_values(by='Quarter', ascending=False)
            .reset_index(drop=True)
        )
        metrics_df['Quarter'] = metrics_df['Quarter'].dt.to_period('Q')

        return metrics_df
    
    @st.cache_data
    def get_main_metrics(_self, metrics_df: pd.DataFrame) -> dict:

        # Create a dummy dataframe
        df = metrics_df.copy()
        
        # Get main metrics: order_count, customer_count, revenue_w_o_freight latest month
        df = df.sort_values(by='month', ascending=False).reset_index(drop=True)
        
        # Calculate m-o-m progress
        df['order_count_mom'] = (df['order_count'] - df['order_count'].shift(-1)) / df['order_count'].shift(-1)
        df['customer_count_mom'] = (df['customer_count'] - df['customer_count'].shift(-1)) / df['customer_count'].shift(-1)
        df['revenue_w_o_freight_mom'] = (df['revenue_w_o_freight'] - df['revenue_w_o_freight'].shift(-1)) / df['revenue_w_o_freight'].shift(-1)

        result = df.head(1).to_dict()

        return result
    
    @st.cache_data
    def calculate_flowing_count(_self, filtered_df: pd.DataFrame):
        # Calculate aggregated df (df)
        df = (
            filtered_df
            .groupby(['order_status'])
            .nunique()[['order_id']]
            .sort_values(by='order_id', ascending=False)
            .reset_index()
            .rename(columns={'order_id':'count'})
        )

        # Get flow reference
        flow_ref_df = pd.DataFrame(_self.order_status_level).explode('to', ignore_index=True)
        
        # Initialize final_df & temp_df
        final_df = pd.DataFrame(columns=['level', 'from', 'to'])
        temp_df = pd.DataFrame(columns=['order_status', 'count'])

        for i in sorted(flow_ref_df['level'].unique(), reverse=True):
            
            ref_df = flow_ref_df[flow_ref_df['level'] == i]
            
            if temp_df.shape[0] == 0:
                temp_df = df
            else:
                temp_df = (
                    pd.concat([
                        temp_df, 
                        df[df['order_status'].isin(ref_df['from'])]
                    ], axis=0)
                    .groupby('order_status')
                    .agg({'count': 'sum'})
                    .reset_index()
                )

            temp_df = (
                ref_df
                .merge(
                    temp_df,
                    how='left',
                    left_on='to',
                    right_on='order_status'
                )
                .groupby(['level', 'from', 'to'])
                .agg({
                    'count': 'sum'
                })
                .reset_index()
            )
            
            if final_df.shape[0] > 0:
                final_df = pd.concat([final_df, temp_df], axis=0)
            else:
                final_df = temp_df
            
            temp_df = (
                temp_df[['from', 'count']]
                .groupby(['from'])
                .agg({'count': 'sum'})
                .reset_index()
                .rename(columns={'from': 'order_status'})
            )
        
        final_df = final_df.fillna(0)
        final_df['count'] = final_df['count'].astype('int64')
        final_df['level'] = final_df['level'].astype('str')
        final_df['target'] = final_df['to'].map(final_df.groupby('from').max()['level'], na_action='ignore')
        final_df = final_df.reset_index(drop=True)
        condition = final_df['from'] == final_df['to']
        final_df['to'] = final_df['to'].mask(condition, final_df['to'] + "'")
        
        status = list(pd.unique(final_df[['from', 'to']].values.ravel()))

        return status, final_df

    @st.cache_data
    def get_product_data(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:

        # Create a dummy dataframe
        df = filtered_df.copy()

        # Aggregate the data
        agg_df = (
            df
            .groupby(['product_category_name_english'])
            .agg({
                'order_id': 'count',
                'price': 'sum',
                'review_score': 'mean'
            })
            .sort_values(by='order_id', ascending=False)
            .reset_index()
            .rename(columns={
                'order_id': 'product_count',
                'price': 'revenue_w_o_freight'
            })
        )

        return agg_df
    
    @st.cache_data
    def get_top_product_by_unit(_self, product_df: pd.DataFrame) -> pd.DataFrame:
        # Get top 5 product by unit (product_count)
        top_products = product_df.sort_values(by='product_count', ascending=False).head()['product_category_name_english']

        # Mask non top product + format the text
        top_product_unit_df = product_df.copy()
        top_product_unit_df['product_category_name_english'] = (
            top_product_unit_df['product_category_name_english']
            .mask(~(top_product_unit_df['product_category_name_english'].isin(top_products)), 'Others')
            .str.replace('_', ' ')
            .str.title()
        )

        # Aggregate the result
        top_product_unit_df = (
            top_product_unit_df
            .groupby('product_category_name_english')
            .sum()[['product_count']]
            .reset_index()
            .rename(columns={
                'product_category_name_english': 'Category',
                'product_count': 'Product count'
            })
        )

        return top_product_unit_df
    
    @st.cache_data
    def get_top_product_by_revenue(_self, product_df: pd.DataFrame, use_mask: bool=False) -> pd.DataFrame:
        # Get top 5 product by revenue (revenue_w_o_freight)
        top_products = product_df.sort_values(by='revenue_w_o_freight', ascending=False).head()['product_category_name_english']

        # Mask non top product
        top_product_revenue_df = product_df.copy()
        if use_mask == False:
            top_product_revenue_df['product_category_name_english'] = (
                top_product_revenue_df['product_category_name_english']
                .mask(~(top_product_revenue_df['product_category_name_english'].isin(top_products)), 'Others')
            )
        # Format the category text
        top_product_revenue_df['product_category_name_english'] = (
            top_product_revenue_df['product_category_name_english']
            .str.replace('_', ' ')
            .str.title()
        )
        # Aggregate the result
        top_product_revenue_df = (
            top_product_revenue_df
            .groupby('product_category_name_english')
            .sum()[['revenue_w_o_freight']]
            .reset_index()
            .rename(columns={
                'product_category_name_english': 'Category',
                'revenue_w_o_freight': 'Revenue'
            })
            .sort_values(by='Revenue', ascending=False)
            .reset_index(drop=True)
        )

        return top_product_revenue_df
    
    @st.cache_data
    def get_product_data_by_month(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:

        # Create a dummy dataframe
        df = filtered_df.copy()

        # Create month column
        df['month'] = df['order_purchase_timestamp'].dt.strftime('%Y-%m')

        # Aggregate the data
        agg_df = (
            df
            .groupby(['month', 'product_category_name_english'])
            .agg({
                'order_id': 'count',
                'price': 'sum',
                'review_score': 'mean'
            })
            .sort_values(by='month', ascending=False)
            .reset_index()
            .rename(columns={
                'order_id': 'product_count',
                'price': 'revenue_w_o_freight'
            })
        )

        return agg_df
    
    @st.cache_data
    def get_monthly_top_product(_self, monthly_product_df: pd.DataFrame, month: str) -> pd.DataFrame:
        # Filter based on month
        top_product_revenue_df = monthly_product_df[monthly_product_df['month'] == month].copy()

        # Format the category text
        top_product_revenue_df['product_category_name_english'] = (
            top_product_revenue_df['product_category_name_english']
            .str.replace('_', ' ')
            .str.title()
        )
        # Aggregate the result
        top_product_revenue_df = (
            top_product_revenue_df
            .groupby('product_category_name_english')
            .sum()[['revenue_w_o_freight']]
            .reset_index()
            .rename(columns={
                'product_category_name_english': 'Category',
                'revenue_w_o_freight': 'Revenue'
            })
            .sort_values(by='Revenue', ascending=False)
            .reset_index(drop=True)
        )

        return top_product_revenue_df

    @st.cache_data
    def get_review_by_month(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the data
        review_df = (
            filtered_df
            .resample(rule='ME', on='order_purchase_timestamp')
            .agg({
                'review_score': 'mean'
            })
            .reset_index()
            .rename(columns={'order_purchase_timestamp':'month'})
            .sort_values(by='month', ascending=True)
            .reset_index(drop=True)
        )

        return review_df
    
    @st.cache_data
    def get_metrics_by_locations(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the data
        metrics_df = (
            filtered_df
            .groupby('customer_zip_code_prefix')
            .agg({
                "order_id": "nunique",
                "customer_unique_id": "nunique",
                'price': 'sum',
                'review_score': 'mean',
                'geolocation_lat': 'max',
                'geolocation_lng': 'max',
                'geolocation_city': 'max',
                'geolocation_state': 'max'
            })
            .reset_index()
            .rename(columns={
                'customer_unique_id': 'customer_count',
                'order_id': 'order_count',
                'price': 'revenue_w_o_freight'
            })
            .dropna(subset=['geolocation_lat', 'geolocation_lng'])
            .reset_index(drop=True)
        )

        return metrics_df
    
    @st.cache_data
    def get_top_states_by_revenue(_self, metrics_by_locations_df: pd.DataFrame) -> pd.DataFrame:
        # Get top 5 states by revenue (revenue_w_o_freight)
        top_states = (
            metrics_by_locations_df
            .groupby('geolocation_state')
            .sum()
            .reset_index()
            .sort_values(by='revenue_w_o_freight', ascending=False)
            .head()
            ['geolocation_state']
        )

        # Mask non top state + format the text
        top_states_revenue_df = metrics_by_locations_df.copy()
        top_states_revenue_df['geolocation_state'] = (
            top_states_revenue_df['geolocation_state']
            .mask(~(top_states_revenue_df['geolocation_state'].isin(top_states)), 'Others')
            .str.replace('_', ' ')
            .str.upper()
        )

        # Aggregate the result
        top_states_revenue_df = (
            top_states_revenue_df
            .groupby('geolocation_state')
            .sum()[['revenue_w_o_freight']]
            .reset_index()
            .rename(columns={
                'geolocation_state': 'State',
                'revenue_w_o_freight': 'Revenue'
            })
        )

        return top_states_revenue_df

    @st.cache_data
    def get_rfm_analysis(_self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        ## Create an rfm dataframe
        rfm_df = (
            filtered_df
            .groupby(by="customer_unique_id", as_index=False)
            .agg({
                "order_purchase_timestamp": "max", 
                "order_id": "nunique",
                "price": "sum" 
            })
        )
        rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
        rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
        recent_date = filtered_df["order_purchase_timestamp"].dt.date.max() + timedelta(days=1)
        rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
        rfm_df = rfm_df.drop(columns=['max_order_timestamp'])
        rfm_df = rfm_df.reset_index()

        return rfm_df