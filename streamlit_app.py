# Import packages
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from utils.st_utils import StDataUtils

# Setting the lay out
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Create a title
st.title("Dashboard Sales")

# Get the data
u = StDataUtils()

# Get clean_data
data = u.get_clean_data()

# Get default values
default_ = {
    'start_date': data['orders']['order_purchase_timestamp'].min(),
    'end_date': data['orders']['order_purchase_timestamp'].max(),
    'order_status': data['orders']['order_status'].unique(),
    'product_categories': data['product_category_name_translations']['product_category_name_english'].unique(),
    'cities': data['geolocations']['geolocation_city'].unique(),
    'states': data['geolocations']['geolocation_state'].unique()
}

# Add sidebar for filters
with st.sidebar:
    st.write('Date')
    start_date = st.date_input('From', value=default_['start_date'])
    end_date = st.date_input('To', value=default_['end_date'])
    order_status = st.multiselect(
        'Order status',
        options=default_['order_status'],
        default=['delivered']
    )
    product_categories = st.multiselect(
        'Product category',
        options=default_['product_categories']
    )
    cities = st.multiselect(
        'City',
        options=default_['cities']
    )
    states = st.multiselect(
        'State',
        options=default_['states']
    )

# Get filtered_data
filtered_df = u.get_filtered_data(data, start_date, end_date, order_status, product_categories, cities, states)

# Get start_date & end_date proper
start_date_proper = filtered_df['order_purchase_timestamp'].min().date()
end_date_proper = filtered_df['order_purchase_timestamp'].max().date()

# Get filtered data for counting success rate
filtered_df_2 = u.get_filtered_data(data, start_date_proper, end_date_proper, [], product_categories, cities, states)

# Get funnel_df and success rate
funnel_df = u.get_order_funnel(filtered_df_2)
latest_success_rate, mom_success_rate = u.get_order_success_rate(funnel_df)

# Get main and other metrics
monthly_metrics_df = u.get_metrics_by_month(filtered_df)
main_metrics = u.get_main_metrics(monthly_metrics_df)

# product_df = u.get_product_data(filtered_df)
# monthly_product_df = u.get_product_data_by_month(filtered_df)

# monthly_review_df = u.get_review_by_month(filtered_df)

# metrics_by_locations_df = u.get_metrics_by_locations(filtered_df)

# rfm_df = u.get_rfm_analysis(filtered_df)

# Add first rows as main metrics
st.header('Main Metrics')

st.subheader(f'''Metrics of {end_date_proper.strftime("%b '%y")}''')
main_col_1, main_col_2, main_col_3, main_col_4 = st.columns(4)
with main_col_1:
    with st.container(border=True):
        st.metric(
            label="Total Revenue*",
            value=f"{main_metrics['revenue_w_o_freight'][0]:,.0f}",
            delta=f"{main_metrics['revenue_w_o_freight_mom'][0]:0.1%}"
        )
    st.markdown("""<small>* Revenue w/o freight</small>""", unsafe_allow_html=True)
with main_col_2:
    with st.container(border=True):
        st.metric(
            label="Order Count",
            value=f"{main_metrics['order_count'][0]:,.0f}",
            delta=f"{main_metrics['order_count_mom'][0]:0.1%}"
        )
with main_col_3:
    with st.container(border=True):
        st.metric(
            label="Active Customer",
            value=f"{main_metrics['customer_count'][0]:,.0f}",
            delta=f"{main_metrics['customer_count_mom'][0]:0.1%}"
        )
with main_col_4:
    with st.container(border=True):
        st.metric(
            label="Order Success Rate",
            value=f"{latest_success_rate:0.0%}",
            delta=f"{mom_success_rate:0.1%}"
        )