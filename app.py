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

# Import authentication and feedback system
import auth
import feedback_system

# Initialize session state for authentication
auth.init_session_state()

# Check if user is authenticated
if not auth.is_authenticated():
    auth.render_login_page()
    st.stop()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 4.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 2rem;
        color: #666;
        margin-top: 0;
        margin-bottom: 40px;
        font-weight: 500;
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
    /* Make tab text bigger and more visible */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.3rem;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        padding: 12px 24px;
    }
</style>
""", unsafe_allow_html=True)

# Import utility functions
from utils import load_unified_data, parse_ai_output, get_sentiment_color, format_date, get_source_type_config, get_source_label, get_source_icon

# Load unified multi-source data
@st.cache_data
def get_data():
    return load_unified_data()

# Load data
df = get_data()
# Sidebar header
st.sidebar.markdown("## 📂 Data Sources")

# Source breakdown
source_counts = df['source_type'].value_counts()
source_config = get_source_type_config()

for source_type, count in source_counts.items():
    icon = get_source_icon(source_type)
    label = get_source_label(source_type)
    st.sidebar.markdown(f"{icon} **{label}**: {count} insights")

st.sidebar.markdown("---")

# No source filter - use all data
filtered_df = df.copy()

# Sidebar - Data Statistics
st.sidebar.header("📊 Dataset Overview")
st.sidebar.metric("Total Insights", len(filtered_df))

# Count by product in filtered data
dayforce_count = len(filtered_df[filtered_df['Product'] == 'Dayforce'])
competitor_count = len(filtered_df[filtered_df['Product'] != 'Dayforce'])
st.sidebar.metric("Dayforce Insights", dayforce_count)
st.sidebar.metric("Competitor Insights", competitor_count)

# Date range
if len(filtered_df) > 0:
    min_date = filtered_df['parsed_date'].min()
    max_date = filtered_df['parsed_date'].max()
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Date Range:**")
    st.sidebar.text(f"{min_date.strftime('%b %d, %Y')} to\n{max_date.strftime('%b %d, %Y')}")

    # Product breakdown
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Products:**")
    product_counts = filtered_df['Product'].value_counts()
    for product, count in product_counts.items():
        st.sidebar.text(f"• {product}: {count}")

# User info and logout button in sidebar
auth.render_user_info_sidebar()

# Main content
st.markdown('<h1 style="font-size: 3.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 0px; line-height: 1.1;">HCM Market Intelligence Platform</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="font-size: 1.8rem; color: #666; margin-top: 5px; margin-bottom: 30px; font-weight: 400;">Multi-Source Strategic Intelligence for Dayforce Excellence</h2>', unsafe_allow_html=True)

# Initialize session state for active tab (helps reduce tab jumps on first interaction)
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# Tab selection with session state
tab_options = [
    "🌟 Strategic Overview",
    "👤 Customer Voice",
    "🎓 Analyst Intelligence",
    "🎯 Dayforce Focus",
    "💡 Topic Intelligence",
    "🎬 Action Insights",
    "📋 Browse Data"
]

# Add Admin Feedback Dashboard tab if user is admin
if auth.is_admin():
    tab_options.append("🔑 Admin Feedback")

# Create tabs with explicit selection tracking
if auth.is_admin():
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(tab_options)
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_options)

# Import page modules
from page_modules import strategic_overview, analyst_intelligence, dayforce_focus, sentiment_analysis, topic_intelligence, action_recommendations, review_browser

with tab1:
    strategic_overview.render(filtered_df, df)

with tab2:
    # Customer Voice = Enhanced Sentiment Analysis (Gartner reviews focus)
    sentiment_analysis.render(filtered_df, df)

with tab3:
    analyst_intelligence.render(filtered_df, df)

with tab4:
    dayforce_focus.render(filtered_df, df)

with tab5:
    topic_intelligence.render(filtered_df, df)

with tab6:
    action_recommendations.render(filtered_df, df)

with tab7:
    review_browser.render(filtered_df, df)

# Admin-only feedback dashboard tab
if auth.is_admin():
    with tab8:
        feedback_system.render_admin_feedback_dashboard()
