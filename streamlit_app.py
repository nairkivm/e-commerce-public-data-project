# Import packages
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from utils.st_utils import StDataUtils
import plotly.graph_objects as go
import plotly.express as px
import random

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

# Get order flow data
flow_status, order_flow_df = u.calculate_flowing_count(filtered_df_2)

# Get main and other metrics
monthly_metrics_df = u.get_metrics_by_month(filtered_df)
quarterly_metrics_df = u.get_metrics_by_quarter(filtered_df)
main_metrics = u.get_main_metrics(monthly_metrics_df)

product_df = u.get_product_data(filtered_df)
top_product_revenue_df = u.get_top_product_by_revenue(product_df)
top_product_revenue_no_mask_df = u.get_top_product_by_revenue(product_df, use_mask=True)


monthly_product_df = u.get_product_data_by_month(filtered_df)
monthly_top_product_df = u.get_monthly_top_product(monthly_product_df, end_date_proper.strftime('%Y-%m'))

monthly_review_df = u.get_review_by_month(filtered_df)

metrics_by_locations_df = u.get_metrics_by_locations(filtered_df)
top_states_revenue_df = u.get_top_states_by_revenue(metrics_by_locations_df)

rfm_df = u.get_rfm_analysis(filtered_df)


sections = [
    "Overview",
    "Product Portofolio",
    "Demographic Analysis"
]
tabs = st.tabs(sections) 

with tabs[0]:
    # Add first rows as overview
    st.header('Overview')

    st.subheader(f'''Main Metrics of {end_date_proper.strftime("%b '%y")}''')
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

    sub_col_1_1, sub_col_1_2 = st.columns([1,2])
    with sub_col_1_1:
        st.subheader('Main metrics per quarter')
        st.dataframe(quarterly_metrics_df)

    with sub_col_1_2:
        st.subheader('Revenue and order count per month')
        # Create a bar chart for Sales
        bar = go.Bar(
            x=monthly_metrics_df['month'],
            y=monthly_metrics_df['revenue_w_o_freight'],
            name='Revenue',
            yaxis='y1'
        )

        # Create a line chart for Profit
        line = go.Scatter(
            x=monthly_metrics_df['month'],
            y=monthly_metrics_df['order_count'],
            mode='lines+markers',
            name='Order count',
            yaxis='y2'
        )

        # Create layout with secondary y-axis
        layout = go.Layout(
            yaxis=dict(
                title='Revenue',
                side='left',
                range=[0, max(monthly_metrics_df['revenue_w_o_freight']) * 1.1]  # Adjust the range to start at zero
            ),
            yaxis2=dict(
                title='Order count',
                overlaying='y',
                side='right',
                range=[0, max(monthly_metrics_df['order_count']) * 1.1]
            )
        )

        # Combine the bar and line charts
        fig = go.Figure(data=[bar, line], layout=layout)

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    sub_col_2_1, sub_col_2_2 = st.columns([1,2])
    with sub_col_2_1:
        st.subheader('States based on total revenue')
        # Create the pie chart
        fig = px.pie(top_states_revenue_df[['State', 'Revenue']], names='State', values='Revenue')

        # Display the pie chart in Streamlit
        st.plotly_chart(fig)

    with sub_col_2_2:
        st.subheader('Monthly active customers')
        # Create a bar chart for Sales
        bar = go.Bar(
            x=monthly_metrics_df['month'],
            y=monthly_metrics_df['customer_count'],
            name='Revenue',
            yaxis='y1'
        )

        # Create layout with secondary y-axis
        layout = go.Layout(
            yaxis=dict(
                title='Customer count',
                side='left',
                range=[0, max(monthly_metrics_df['customer_count']) * 1.1]  # Adjust the range to start at zero
            )
        )

        # Combine the bar and line charts
        fig = go.Figure(data=bar, layout=layout)

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    sub_col_3_1, sub_col_3_2 = st.columns([1,2])
    with sub_col_3_1:
        st.subheader('Product categories based on total revenue')
        # Create the pie chart
        fig = px.pie(top_product_revenue_df[['Category', 'Revenue']], names='Category', values='Revenue')

        # Display the pie chart in Streamlit
        st.plotly_chart(fig)

    with sub_col_3_2:
        st.subheader('Order flow based on status')
        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = flow_status,
            ),
            link = dict(
            source = [flow_status.index(x) for x in order_flow_df['from']], # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = [flow_status.index(x) for x in order_flow_df['to']],
            value = list(order_flow_df['count'])
        ))])

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    # Add first rows as overview
    st.header('Product Portofolio')

    pp_col_1_1, pp_col_1_2 = st.columns([3, 1])
    with pp_col_1_1:

        st.subheader('Best and Worst Performing Product Categories by Revenue')
        pp_col_1_1_col1, pp_col_1_1_col2 = st.columns(2)
        with pp_col_1_1_col1:
            # Create the horizontal bar chart
            fig = px.bar(
                top_product_revenue_no_mask_df.head(), 
                x='Revenue', 
                y='Category', 
                orientation='h',
                title='Best Performing Product',
                color='Category',
                color_discrete_sequence=["#72BCD4"] + ["#D3D3D3"]*4
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        with pp_col_1_1_col2:
            # Create the horizontal bar chart
            fig = px.bar(
                top_product_revenue_no_mask_df.tail(),
                x='Revenue', 
                y='Category', 
                orientation='h',
                title='Worst Performing Product',
                color='Category',
                color_discrete_sequence= ["#D3D3D3"]*4 + ["#72BCD4"]
            )
            fig.update_layout(yaxis={'categoryorder':'total descending', 'side': 'right'}, showlegend=False)
            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
    
    with pp_col_1_2:

        st.subheader("Best Categories' Revenue This Month")
        with st.container(border=True):
            st.metric(
                label=f"#1: {monthly_top_product_df['Category'].iloc[0]}",
                value=f"{monthly_top_product_df['Revenue'].iloc[0]:,.0f}"
            )
        with st.container(border=True):
            st.metric(
                label=f"#2: {monthly_top_product_df['Category'].iloc[1]}",
                value=f"{monthly_top_product_df['Revenue'].iloc[1]:,.0f}"
            )
        with st.container(border=True):
            st.metric(
                label=f"#3: {monthly_top_product_df['Category'].iloc[2]}",
                value=f"{monthly_top_product_df['Revenue'].iloc[2]:,.0f}"
            )


    pp_col_2_1, pp_col_2_2 = st.columns([3, 1])
    with pp_col_2_1:
        st.subheader('Average Review Score by Month')
        # Create a line chart for Profit
        line = go.Scatter(
            x=monthly_review_df['month'],
            y=monthly_review_df['review_score'],
            mode='lines+markers',
            name='Score review'
        )
        # Combine the bar and line charts
        fig = go.Figure(data=line)

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader(f"Average review score vs revenue (corr: {product_df['review_score'].corr(product_df['revenue_w_o_freight']):.2f})")
        # Create a scatter plot
        fig = px.scatter(x=product_df['review_score'], y=product_df['revenue_w_o_freight'], trendline='ols')
        fig.update_layout(
            xaxis_title='Review score',
            yaxis_title='Revenue',
        )
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with pp_col_2_2:
        st.subheader('Review Score This Month')
        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = monthly_review_df['review_score'].iloc[-1],
            mode = "gauge+number+delta",
            title = {'text': "Score [1-5]"},
            delta = {'reference': monthly_review_df['review_score'].iloc[-2], 'relative': True, 'valueformat': '.00%'},
            gauge = {
                'axis': {'range': [None, 5]},    
                'steps' : [
                    {'range': [0, 1], 'color': "indianred"},
                    {'range': [1, 3.5], 'color': "khaki"},
                    {'range': [3.5, 5], 'color': "lightgreen"}
                ],
                'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 4}
            }
        ))
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    # Add first rows as overview
    st.header('Demographic Analysis')
    
    st.subheader('Where are the customers?')
    loc_c_1, loc_c_2, loc_c_3 = st.columns([1,1,4])
    with loc_c_1:
        location_options = st.selectbox(label='Select by', options=['State', 'City'], index=0)
    with loc_c_2:
        metrics_options = st.selectbox(label='Based on', options=['Revenue', 'Order count', 'Customer count'], index=0)
    location_dict = {'City': 'geolocation_city', 'State': 'geolocation_state'}
    metrics_dict = {'Revenue': 'revenue_w_o_freight', 'Order count': 'order_count', 'Customer count': 'customer_count'}
    # Generate random colors for each category
    unique_categories = metrics_by_locations_df[location_dict[location_options]].unique()
    color_map = {category: random.choice(u.css_colors) for category in unique_categories}

    # Add color column to the dataframe
    metrics_by_locations_df['color'] = metrics_by_locations_df[location_dict[location_options]].map(color_map)

    loc_c2_1, loc_c2_2 = st.columns(2)
    with loc_c2_1:
        st.markdown(f'#### Map grouped by {str(location_options).lower()} based on {str(metrics_options).lower()}')
        st.map(
            data=metrics_by_locations_df,
            latitude='geolocation_lat',
            longitude='geolocation_lng',
            color='color',
            size=metrics_dict[metrics_options]
        )
    with loc_c2_2:
        st.markdown(f'#### Top {location_options} by {metrics_options}')
        agg_dict = {'Revenue': {'price': 'sum'}, 'Order count': {"order_id": "nunique"}, 'Customer count': {"customer_unique_id": "nunique"}}
        metrics_grouped = (
            filtered_df
            .groupby(location_dict[location_options])
            .agg(agg_dict[metrics_options])
            .reset_index()
            .rename(columns={
                'customer_unique_id': 'Customer count',
                'order_id': 'Order count',
                'price': 'Revenue',
                'geolocation_city': 'City',
                'geolocation_state': 'State'
            })
            .sort_values(by=metrics_options, ascending=False)
            .reset_index(drop=True)
        )
        # Create the horizontal bar chart
        fig = px.bar(
            metrics_grouped.head(), 
            x=metrics_options, 
            y=location_options, 
            orientation='h',
            color=location_options,
            color_discrete_sequence=["#72BCD4"] + ["#D3D3D3"]*4
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Recency, Frquency, and Monetary (RFM) Analysis')
    # Visualize the data
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
    
    sns.barplot(y="recency", x="index", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)
    
    sns.barplot(y="frequency", x="index", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)
    
    sns.barplot(y="monetary", x="index", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)
    
    plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
    st.pyplot(fig=fig, use_container_width=True)