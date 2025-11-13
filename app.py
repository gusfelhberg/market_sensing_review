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
    /* Make tab text bigger and more visible */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Import utility functions
from utils import load_unified_data, parse_ai_output, get_sentiment_color, format_date, get_source_type_config, get_source_label, get_source_icon
import os

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None

# Check if data files exist
GARTNER_FILE = 'data/market_sensing_data_ai_output_gartner.xlsx'
ANALYST_FILE = 'data/market_sensing_data_ai_output_analyst.xlsx'

files_exist = os.path.exists(GARTNER_FILE) and os.path.exists(ANALYST_FILE)

# Load unified multi-source data
@st.cache_data
def get_data():
    return load_unified_data()

# Try to load data if files exist
if files_exist:
    try:
        df = get_data()
        st.session_state.data = df
        data_loaded = True
    except Exception as e:
        st.error(f"⚠️ Error loading data files: {str(e)}")
        st.info("The data files exist but couldn't be loaded. Please check file format or upload new files below.")
        data_loaded = False
        df = None
else:
    data_loaded = False
    df = None

# Show appropriate UI based on data availability
if not data_loaded:
    # Show prominent upload interface when no data is available
    st.sidebar.markdown("## 📤 Upload Data Files")
    st.sidebar.warning("⚠️ No data files found!")
    st.sidebar.info("Please upload your data files to get started.")
    
    from file_upload_utils import render_file_upload_section
    render_file_upload_section()
    
    # Show main message
    st.markdown('<p class="main-header">HCM Market Intelligence Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Source Strategic Intelligence for Dayforce Excellence</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #fff3cd; padding: 30px; border-radius: 10px; border-left: 5px solid #ffc107; margin: 40px 0; text-align: center;">
        <h2>📊 Welcome to the HCM Market Intelligence Platform</h2>
        <p style="font-size: 1.1rem; margin: 20px 0;">
            To begin your analysis, please upload your data files using the sidebar.
        </p>
        <p style="font-size: 1rem; color: #666;">
            <strong>Step 1:</strong> Download the templates from the sidebar<br/>
            <strong>Step 2:</strong> Prepare your data following the template format<br/>
            <strong>Step 3:</strong> Upload your files and validate them<br/>
            <strong>Step 4:</strong> Click "Load Uploaded Files" to start analyzing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Data loaded successfully - show normal interface
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

# Source filter
source_options = ['All Sources'] + [
    f"{get_source_icon(st)} {get_source_label(st)}"
    for st in df['source_type'].unique()
]

selected_source_display = st.sidebar.selectbox(
    "Filter by Source",
    options=source_options,
    help="Filter all analysis to specific source type"
)

# Map display back to source type
if selected_source_display == 'All Sources':
    selected_source = None
else:
    # Extract source type from display string
    for source_type in df['source_type'].unique():
        if get_source_label(source_type) in selected_source_display:
            selected_source = source_type
            break

st.sidebar.markdown("---")

# Apply source filter
if selected_source:
    filtered_df = df[df['source_type'] == selected_source].copy()
    st.sidebar.info(f"Viewing: {get_source_label(selected_source)} only")
else:
    filtered_df = df.copy()
    st.sidebar.info("Viewing: All Sources combined")

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

# File upload section (collapsed by default when data exists)
st.sidebar.markdown("---")
from file_upload_utils import render_file_upload_section
render_file_upload_section()

# Main content
st.markdown('<p class="main-header">HCM Market Intelligence Platform</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Source Strategic Intelligence for Dayforce Excellence</p>', unsafe_allow_html=True)

# Data scope message with source breakdown
dayforce_count = len(filtered_df[filtered_df['Product'] == 'Dayforce'])
competitor_count = len(filtered_df[filtered_df['Product'] != 'Dayforce'])

# Get source breakdown
if selected_source:
    source_label = get_source_label(selected_source)
    source_icon = get_source_icon(selected_source)
    competitor_names = sorted([p for p in filtered_df['Product'].unique() if p != 'Dayforce'])
    
    if competitor_names:
        st.markdown(f"""
        <div style="background-color: #d1ecf1; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; border-left: 4px solid #0c5460;">
            {source_icon} <strong>{source_label} Analysis</strong> - {dayforce_count} Dayforce insights + {competitor_count} competitor insights ({', '.join(competitor_names)})
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: #d1ecf1; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; border-left: 4px solid #0c5460;">
            {source_icon} <strong>{source_label} Analysis</strong> - {dayforce_count} Dayforce insights
        </div>
        """, unsafe_allow_html=True)
else:
    # Multi-source view
    source_breakdown = []
    for source_type in df['source_type'].unique():
        count = len(filtered_df[filtered_df['source_type'] == source_type])
        icon = get_source_icon(source_type)
        label = get_source_label(source_type)
        source_breakdown.append(f"{icon} {count} {label}")
    
    competitor_names = sorted([p for p in filtered_df['Product'].unique() if p != 'Dayforce'])
    
    st.markdown(f"""
    <div style="background-color: #d1ecf1; padding: 12px; border-radius: 5px; margin-bottom: 20px; text-align: center; border-left: 4px solid #0c5460;">
        📊 <strong>Multi-Source Intelligence</strong> - {dayforce_count} Dayforce + {competitor_count} Competitor insights<br/>
        <small>{' | '.join(source_breakdown)}</small>
    </div>
    """, unsafe_allow_html=True)

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

# Create tabs with explicit selection tracking
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
