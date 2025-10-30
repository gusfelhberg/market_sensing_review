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

# Load data - combines Sept and Oct 2025 files
@st.cache_data
def get_data():
    return load_data()

try:
    df = get_data()
    st.session_state.data = df
except FileNotFoundError as e:
    st.error(f"Data file not found: {str(e)}")
    st.info("Make sure both 'market_sensing_data_gartner_ai_output_sept2025.xlsx' and 'market_sensing_data_gartner_ai_output_oct2025.xlsx' are in the project directory.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please check that the data files are properly formatted.")
    st.stop()

# Sidebar header
st.sidebar.markdown("## 📂 Data Source")
st.sidebar.info("📊 **Real Gartner Data**\nCombined: Sept + Oct 2025")
st.sidebar.markdown("---")

# Parse dates
date_col = 'Review Date'
df['parsed_date'] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')

# Use all data - no filters
filtered_df = df.copy()

# Sidebar - Data Statistics
st.sidebar.header("📊 Dataset Overview")
st.sidebar.metric("Total Reviews", len(df))

# Count by product
dayforce_count = len(df[df['Product'] == 'Dayforce'])
competitor_count = len(df[df['Product'] != 'Dayforce'])
st.sidebar.metric("Dayforce Reviews", dayforce_count)
st.sidebar.metric("Competitor Reviews", competitor_count)

# Date range
min_date = df['parsed_date'].min()
max_date = df['parsed_date'].max()
st.sidebar.markdown("---")
st.sidebar.markdown("**Date Range:**")
st.sidebar.text(f"{min_date.strftime('%b %d, %Y')} to\n{max_date.strftime('%b %d, %Y')}")

# Product breakdown
st.sidebar.markdown("---")
st.sidebar.markdown("**Products:**")
product_counts = df['Product'].value_counts()
for product, count in product_counts.items():
    st.sidebar.text(f"• {product}: {count}")

# Main content
st.markdown('<p class="main-header">HCM Market Sensing Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Strategic Intelligence for Dayforce Product Excellence</p>', unsafe_allow_html=True)

# Data scope message
dayforce_count = len(filtered_df[filtered_df['Product'] == 'Dayforce'])
competitor_count = len(filtered_df[filtered_df['Product'] != 'Dayforce'])
competitor_names = sorted([p for p in filtered_df['Product'].unique() if p != 'Dayforce'])

st.markdown(f"""
<div style="background-color: #d1ecf1; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; border-left: 4px solid #0c5460;">
    📊 <strong>Full Dataset Analysis</strong> - {dayforce_count} Dayforce reviews + {competitor_count} competitor reviews ({', '.join(competitor_names)})
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
