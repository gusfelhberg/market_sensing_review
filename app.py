"""
HCM Market Sensing - Executive Dashboard
Strategic insights for product and customer experience decisions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import re

# Page configuration
st.set_page_config(
    page_title="HCM Market Sensing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .insight-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .action-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #0c5460;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Import utility functions
from utils import load_data, parse_ai_output, get_sentiment_color, format_date

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None

# Load data based on selection
@st.cache_data
def get_data(data_source):
    if data_source == "Synthetic Data":
        return load_data('market_sensing_data_synthetic.xlsx')
    else:
        return load_data('market_sensing_data_gartner_ai_sentiment.xlsx')

# Sidebar - Data Source Selection (at the top)
st.sidebar.markdown("## 📂 Data Source")
data_source = st.sidebar.radio(
    "Select Dataset",
    ["Synthetic Data", "Real Data"],
    index=0,
    help="Synthetic: 145 reviews with realistic scenarios | Real: Original 24 Gartner reviews"
)

st.sidebar.markdown("---")

try:
    df = get_data(data_source)
    st.session_state.data = df
except FileNotFoundError as e:
    st.error(f"Data file not found: {str(e)}")
    st.info("Make sure both 'market_sensing_data_synthetic.xlsx' and 'market_sensing_data_gartner_ai_sentiment.xlsx' are in the project directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar - Filters
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

# Date filter
date_col = 'Review Date'
df['parsed_date'] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
min_date = df['parsed_date'].min()
max_date = df['parsed_date'].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Product filter
products = ['All'] + sorted(df['Product'].unique().tolist())
selected_products = st.sidebar.multiselect(
    "Products",
    options=products,
    default=['All']
)

# Reviewer attributes
industries = ['All'] + sorted(df['Reviewer Industry'].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("Industry", industries)

roles = ['All'] + sorted(df['Reviewer Role '].dropna().unique().tolist())
selected_role = st.sidebar.selectbox("Reviewer Role", roles)

firm_sizes = ['All'] + sorted(df['Reviewer Firm Size'].dropna().unique().tolist())
selected_firm_size = st.sidebar.selectbox("Company Size", firm_sizes)

# Apply filters
filtered_df = df.copy()

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['parsed_date'].dt.date >= start_date) &
        (filtered_df['parsed_date'].dt.date <= end_date)
    ]

# Product filter
if 'All' not in selected_products and selected_products:
    filtered_df = filtered_df[filtered_df['Product'].isin(selected_products)]

# Other filters
if selected_industry != 'All':
    filtered_df = filtered_df[filtered_df['Reviewer Industry'] == selected_industry]
if selected_role != 'All':
    filtered_df = filtered_df[filtered_df['Reviewer Role '] == selected_role]
if selected_firm_size != 'All':
    filtered_df = filtered_df[filtered_df['Reviewer Firm Size'] == selected_firm_size]

st.sidebar.markdown("---")
st.sidebar.metric("Reviews in Selection", len(filtered_df))
st.sidebar.metric("Total Reviews", len(df))

# Main content
st.markdown('<p class="main-header">HCM Market Sensing Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Strategic Intelligence for Dayforce Product Excellence</p>', unsafe_allow_html=True)

# Data source indicator and filter scope
data_icon = "🧪" if data_source == "Synthetic Data" else "📊"
data_color = "#d1ecf1" if data_source == "Synthetic Data" else "#d4edda"

# Determine filter scope
products_in_filter = sorted(filtered_df['Product'].unique().tolist())
if 'Dayforce' in products_in_filter and len(products_in_filter) == 1:
    filter_scope = "🎯 <strong>Dayforce Only</strong> - All insights are Dayforce-specific"
    scope_color = "#d4edda"
elif 'Dayforce' in products_in_filter:
    competitors = [p for p in products_in_filter if p != 'Dayforce']
    filter_scope = f"📊 <strong>Dayforce + {len(competitors)} Competitor(s)</strong> - Use sidebar to filter"
    scope_color = "#fff3cd"
else:
    filter_scope = f"⚠️ <strong>Competitors Only</strong> - No Dayforce data in current filter"
    scope_color = "#f8d7da"

st.markdown(f"""
<div style="background-color: {data_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center;">
    {data_icon} <strong>Data Source:</strong> {data_source}
</div>
<div style="background-color: {scope_color}; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
    {filter_scope}
</div>
""", unsafe_allow_html=True)

# Initialize session state for active tab (helps reduce tab jumps on first interaction)
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# Tab selection with session state
tab_options = [
    "🎯 Dayforce Focus",
    "📈 Executive Summary",
    "🎯 Sentiment Analysis",
    "💡 Topic Intelligence",
    "⚔️ Competitive Insights",
    "🎬 Action Insights",
    "📋 Review Browser"
]

# Create tabs with explicit selection tracking
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_options)

# Import page modules
from page_modules import dayforce_focus, executive_summary, sentiment_analysis, topic_intelligence, competitive_insights, action_recommendations, review_browser

with tab1:
    dayforce_focus.render(filtered_df, df)

with tab2:
    executive_summary.render(filtered_df, df)

with tab3:
    sentiment_analysis.render(filtered_df, df)

with tab4:
    topic_intelligence.render(filtered_df, df)

with tab5:
    competitive_insights.render(filtered_df, df)

with tab6:
    action_recommendations.render(filtered_df, df)

with tab7:
    review_browser.render(filtered_df, df)
