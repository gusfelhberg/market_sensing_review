"""
File Upload and Template Generation Utilities
Handles data file uploads, validation, and template downloads
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime

# Required columns for each file type
GARTNER_REQUIRED_COLUMNS = [
    'Review Date', 'Product', 'Headline', 'Overall Comment', 
    'Overall User Rating', 'ai_output',
    'degree_of_meeting_functional_requirements', 'product_functionality',
    'quality_of_product_user_experience', 'quality_of_the_evaluation_and_contracting_process',
    'pricing_and_packaging_clarity', 'value_for_money',
    'fit_of_product_strategy_to_market_needs', 'clarity_of_product_roadmap',
    'extent_of_planned_product_innovation', 'ease_and_quality_of_integration_and_deployment',
    'quality_of_user_training_and_post_go_live_support', 'implementation_cost',
    'quality_and_timeliness_of_support', 'customer_success_management_and_value_realization',
    'customer_community', 'product_topics', 'gtm_topics', 'market_direction_topics',
    'implementation_topics', 'customer_experience_topics', 'other_topics'
]

ANALYST_REQUIRED_COLUMNS = [
    'Date', 'Firm', 'Analyst', 'Insight', 'ai_output',
    'degree_of_meeting_functional_requirements', 'product_functionality',
    'quality_of_product_user_experience', 'quality_of_the_evaluation_and_contracting_process',
    'pricing_and_packaging_clarity', 'value_for_money',
    'fit_of_product_strategy_to_market_needs', 'clarity_of_product_roadmap',
    'extent_of_planned_product_innovation', 'ease_and_quality_of_integration_and_deployment',
    'quality_of_user_training_and_post_go_live_support', 'implementation_cost',
    'quality_and_timeliness_of_support', 'customer_success_management_and_value_realization',
    'customer_community', 'product_topics', 'gtm_topics', 'market_direction_topics',
    'implementation_topics', 'customer_experience_topics', 'other_topics'
]

def validate_columns(df, required_columns, file_type):
    """
    Validate that uploaded file has required columns
    Returns (is_valid, missing_columns, extra_columns)
    """
    uploaded_columns = set(df.columns)
    required_columns_set = set(required_columns)
    
    missing = required_columns_set - uploaded_columns
    extra = uploaded_columns - required_columns_set
    
    is_valid = len(missing) == 0
    
    return is_valid, list(missing), list(extra)

def generate_gartner_template():
    """Generate a template Excel file for Gartner reviews"""
    
    data = {
        'Review Date': ['15/10/2025', '20/10/2025'],
        'Review URL': ['https://www.gartner.com/reviews/market/cloud-hcm-suites/vendor/ceridian/product/dayforce/review/view/5479281', 
                       'https://www.gartner.com/reviews/market/cloud-hcm-suites/vendor/ceridian/product/dayforce/review/view/5479282'],
        'Product': ['Dayforce', 'SAP SF'],
        'Reviewer Role ': ['HR Manager', 'VP of Human Resources'],
        'Reviewer Industry': ['Financial Services', 'Manufacturing'],
        'Reviewer Function': ['Human Resources', 'Human Resources'],
        'Reviewer Firm Size': ['1,001-5,000 employees', '5,001-10,000 employees'],
        'Country': ['United States', 'Canada'],
        'Headline': ['Great payroll and time tracking solution', 'Comprehensive but complex system'],
        'Overall Comment': ['Dayforce has been instrumental in streamlining our payroll processes. The system is intuitive and the support team is responsive.', 
                           'The platform offers extensive functionality but requires significant implementation effort. Training is essential for user adoption.'],
        'Lessons Learned': ['What do you like most about the product or service? The integrated approach to payroll and time tracking. What do you dislike most about the product or service? Initial setup complexity.',
                           'What do you like most about the product or service? Comprehensive feature set. What do you dislike most about the product or service? Steep learning curve.'],
        'Overall User Rating': [4.5, 3.5],
        'Evaluation & Contracting': [4.0, 3.5],
        'Integration & Deployment': [4.5, 3.0],
        'Service & Support': [4.5, 4.0],
        'Product Capabilities': [4.5, 4.0],
        'text_blob': ['', ''],
        'text_blob_description': ['', ''],
        'additional_information': ['', ''],
        'ai_output': ['', ''],
        'degree_of_meeting_functional_requirements': [4.5, 3.5],
        'product_functionality': [4.5, 4.0],
        'quality_of_product_user_experience': [4.0, 3.5],
        'quality_of_the_evaluation_and_contracting_process': [4.0, 3.5],
        'pricing_and_packaging_clarity': [4.0, 3.0],
        'value_for_money': [4.5, 3.5],
        'fit_of_product_strategy_to_market_needs': [4.5, 4.0],
        'clarity_of_product_roadmap': [4.0, 3.5],
        'extent_of_planned_product_innovation': [4.5, 4.0],
        'ease_and_quality_of_integration_and_deployment': [4.0, 3.0],
        'quality_of_user_training_and_post_go_live_support': [4.5, 3.5],
        'implementation_cost': [3.5, 3.0],
        'quality_and_timeliness_of_support': [4.5, 4.0],
        'customer_success_management_and_value_realization': [4.0, 3.5],
        'customer_community': [4.0, 3.5],
        'product_topics': ['["payroll", "time tracking", "integration"]', '["complex", "training", "features"]'],
        'gtm_topics': ['["support", "implementation"]', '["pricing", "contract"]'],
        'market_direction_topics': ['["innovation", "roadmap"]', '["strategy"]'],
        'implementation_topics': ['["integration", "deployment"]', '["setup", "complexity"]'],
        'customer_experience_topics': ['["intuitive", "user-friendly"]', '["learning curve", "training"]'],
        'other_topics': ['[]', '[]'],
        'ai_judge_output': ['', ''],
        'is_factually_correct': ['true', 'true'],
        'is_concise': ['true', 'true'],
        'is_relevant': ['true', 'true'],
        'is_safe': ['true', 'true']
    }
    
    df = pd.DataFrame(data)
    return df

def generate_analyst_template():
    """Generate a template Excel file for analyst insights"""
    
    data = {
        'Date': ['2025-10-15', '2025-10-18'],
        'Interaction': ['Analyst Inquiry', 'Briefing'],
        'Insight': ['Dayforce continues to strengthen its position in the North American market with innovative workforce management features. The recent updates to predictive scheduling show strong customer adoption.',
                   'The integration between payroll and talent management modules provides significant value to mid-market customers. However, implementation complexity remains a concern for smaller organizations.'],
        'Firm': ['Gartner', 'Forrester'],
        'Analyst': ['John Smith', 'Sarah Johnson'],
        'text_blob': ['', ''],
        'text_blob_description': ['', ''],
        'additional_information': ['', ''],
        'ai_output': ['', ''],
        'degree_of_meeting_functional_requirements': [4.5, 4.0],
        'product_functionality': [4.5, 4.0],
        'quality_of_product_user_experience': [4.0, 3.5],
        'quality_of_the_evaluation_and_contracting_process': [4.0, 3.5],
        'pricing_and_packaging_clarity': [3.5, 3.5],
        'value_for_money': [4.0, 3.5],
        'fit_of_product_strategy_to_market_needs': [4.5, 4.0],
        'clarity_of_product_roadmap': [4.5, 4.0],
        'extent_of_planned_product_innovation': [4.5, 4.0],
        'ease_and_quality_of_integration_and_deployment': [3.5, 3.5],
        'quality_of_user_training_and_post_go_live_support': [4.0, 3.5],
        'implementation_cost': [3.5, 3.0],
        'quality_and_timeliness_of_support': [4.0, 4.0],
        'customer_success_management_and_value_realization': [4.0, 3.5],
        'customer_community': [4.0, 3.5],
        'product_topics': ['["workforce management", "predictive scheduling", "innovation"]', '["integration", "payroll", "talent management"]'],
        'gtm_topics': ['["market position", "adoption"]', '["mid-market", "value proposition"]'],
        'market_direction_topics': ['["North American market", "growth"]', '["market trends"]'],
        'implementation_topics': ['["customer adoption"]', '["complexity", "implementation challenges"]'],
        'customer_experience_topics': ['["features", "updates"]', '["customer value"]'],
        'other_topics': ['[]', '[]'],
        'ai_judge_output': ['', ''],
        'is_factually_correct': ['true', 'true'],
        'is_concise': ['true', 'true'],
        'is_relevant': ['true', 'true'],
        'is_safe': ['true', 'true']
    }
    
    df = pd.DataFrame(data)
    return df

def create_excel_download(df, filename):
    """Convert dataframe to Excel file for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Template')
    output.seek(0)
    return output

def render_file_upload_section():
    """Render the file upload section in the sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📤 Upload Data")
    
    with st.sidebar.expander("Upload New Data Files", expanded=False):
        st.markdown("Upload your own data files to replace the current dataset.")
        
        # Template downloads
        st.markdown("### 📥 Download Templates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            gartner_template = generate_gartner_template()
            gartner_excel = create_excel_download(gartner_template, 'gartner_template.xlsx')
            st.download_button(
                label="📊 Reviews",
                data=gartner_excel,
                file_name="gartner_reviews_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Template for customer reviews"
            )
        
        with col2:
            analyst_template = generate_analyst_template()
            analyst_excel = create_excel_download(analyst_template, 'analyst_template.xlsx')
            st.download_button(
                label="🎓 Analyst",
                data=analyst_excel,
                file_name="analyst_insights_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Template for analyst insights"
            )
        
        st.markdown("### 📤 Upload Files")
        
        # File uploaders
        gartner_file = st.file_uploader(
            "Customer Reviews (Gartner format)",
            type=['xlsx', 'xls'],
            key='gartner_upload',
            help="Upload customer reviews in Gartner Peer Insights format"
        )
        
        analyst_file = st.file_uploader(
            "Analyst Insights",
            type=['xlsx', 'xls'],
            key='analyst_upload',
            help="Upload analyst interaction insights"
        )
        
        # Validate uploaded files
        if gartner_file is not None:
            try:
                gartner_df = pd.read_excel(gartner_file)
                is_valid, missing, extra = validate_columns(gartner_df, GARTNER_REQUIRED_COLUMNS, 'Gartner')
                
                if is_valid:
                    st.success(f"✅ Reviews file valid! ({len(gartner_df)} rows)")
                    st.session_state['uploaded_gartner'] = gartner_df
                else:
                    st.error("❌ Reviews file has column issues:")
                    if missing:
                        st.warning(f"**Missing columns:** {', '.join(missing[:5])}" + 
                                 (f" and {len(missing)-5} more..." if len(missing) > 5 else ""))
                    if extra:
                        st.info(f"Extra columns found: {len(extra)} (will be ignored)")
            except Exception as e:
                st.error(f"Error reading Reviews file: {str(e)}")
        
        if analyst_file is not None:
            try:
                analyst_df = pd.read_excel(analyst_file)
                is_valid, missing, extra = validate_columns(analyst_df, ANALYST_REQUIRED_COLUMNS, 'Analyst')
                
                if is_valid:
                    st.success(f"✅ Analyst file valid! ({len(analyst_df)} rows)")
                    st.session_state['uploaded_analyst'] = analyst_df
                else:
                    st.error("❌ Analyst file has column issues:")
                    if missing:
                        st.warning(f"**Missing columns:** {', '.join(missing[:5])}" + 
                                 (f" and {len(missing)-5} more..." if len(missing) > 5 else ""))
                    if extra:
                        st.info(f"Extra columns found: {len(extra)} (will be ignored)")
            except Exception as e:
                st.error(f"Error reading Analyst file: {str(e)}")
        
        # Apply button
        if st.button("🔄 Load Uploaded Files", help="Replace current data with uploaded files"):
            if 'uploaded_gartner' in st.session_state and 'uploaded_analyst' in st.session_state:
                # Save uploaded files to data directory
                try:
                    st.session_state['uploaded_gartner'].to_excel('./data/market_sensing_data_ai_output_gartner.xlsx', index=False)
                    st.session_state['uploaded_analyst'].to_excel('./data/market_sensing_data_ai_output_analyst.xlsx', index=False)
                    st.success("✅ Files uploaded successfully! Reloading app...")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving files: {str(e)}")
            else:
                st.warning("⚠️ Please upload both files before loading")
