"""
Review Browser Page
Browse and filter all reviews with full details
"""

import streamlit as st
import pandas as pd
from utils import get_sentiment_color, data_source_badge

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import get_sentiment_color, get_sentiment_label

def render(filtered_df, full_df):
    """Render the Review Browser page"""
    
    st.title("📋 Review Browser")
    st.markdown("*Browse and filter all reviews in the current selection*")
    st.caption(f"Review content: {data_source_badge('customer_review')} | AI sentiment scores: {data_source_badge('ai_analysis')}")
    
    # Dimensions for analysis
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': 'Product (AI)',
        'gtm': 'GTM (AI)',
        'market_direction': 'Market Direction (AI)',
        'implementation': 'Implementation (AI)',
        'customer_experience': 'Customer Experience (AI)'
    }
    
    # Parse topics
    analysis_df = filtered_df.copy()
    analysis_df['topics_list'] = analysis_df['topics'].apply(
        lambda x: eval(x) if pd.notna(x) and isinstance(x, str) else []
    )
    
    st.markdown("---")
    
    # Create filter columns
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        # Product filter
        review_products = ['All'] + sorted(analysis_df['Product'].unique().tolist())
        selected_review_product = st.selectbox(
            "Product",
            review_products,
            key='review_browser_product'
        )
    
    with filter_col2:
        # Rating filter
        rating_options = ['All', '5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
        selected_rating = st.selectbox(
            "Rating",
            rating_options,
            key='review_browser_rating'
        )
    
    with filter_col3:
        # Industry filter
        review_industries = ['All'] + sorted(analysis_df['Reviewer Industry'].dropna().unique().tolist())
        selected_review_industry = st.selectbox(
            "Industry",
            review_industries,
            key='review_browser_industry'
        )
    
    with filter_col4:
        # Company size filter
        review_sizes = ['All'] + sorted(analysis_df['Reviewer Firm Size'].dropna().unique().tolist())
        selected_review_size = st.selectbox(
            "Company Size",
            review_sizes,
            key='review_browser_size'
        )
    
    # Apply filters
    browse_df = analysis_df.copy()
    
    if selected_review_product != 'All':
        browse_df = browse_df[browse_df['Product'] == selected_review_product]
    
    if selected_rating != 'All':
        rating_value = int(selected_rating.split()[0])
        browse_df = browse_df[browse_df['Overall User Rating'] == rating_value]
    
    if selected_review_industry != 'All':
        browse_df = browse_df[browse_df['Reviewer Industry'] == selected_review_industry]
    
    if selected_review_size != 'All':
        browse_df = browse_df[browse_df['Reviewer Firm Size'] == selected_review_size]
    
    # Display summary
    st.markdown(f"**Showing {len(browse_df)} of {len(analysis_df)} reviews**")
    
    # Sorting options
    sort_col1, sort_col2 = st.columns([3, 1])
    
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            ['Review Date (Newest)', 'Review Date (Oldest)', 'Rating (Highest)', 'Rating (Lowest)', 
             'Product Sentiment (Highest)', 'Product Sentiment (Lowest)'],
            key='review_browser_sort'
        )
    
    with sort_col2:
        reviews_per_page = st.selectbox(
            "Reviews per page",
            [10, 25, 50, 100],
            index=1,
            key='review_browser_per_page'
        )
    
    # Apply sorting
    if sort_by == 'Review Date (Newest)':
        browse_df = browse_df.sort_values('parsed_date', ascending=False)
    elif sort_by == 'Review Date (Oldest)':
        browse_df = browse_df.sort_values('parsed_date', ascending=True)
    elif sort_by == 'Rating (Highest)':
        browse_df = browse_df.sort_values('Overall User Rating', ascending=False)
    elif sort_by == 'Rating (Lowest)':
        browse_df = browse_df.sort_values('Overall User Rating', ascending=True)
    elif sort_by == 'Product Sentiment (Highest)':
        browse_df = browse_df.sort_values('product', ascending=False)
    elif sort_by == 'Product Sentiment (Lowest)':
        browse_df = browse_df.sort_values('product', ascending=True)
    
    # Pagination
    total_reviews = len(browse_df)
    total_pages = (total_reviews - 1) // reviews_per_page + 1 if total_reviews > 0 else 1
    
    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    
    with page_col2:
        current_page = st.number_input(
            f"Page (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            key='review_browser_page'
        )
    
    # Get page of reviews
    start_idx = (current_page - 1) * reviews_per_page
    end_idx = start_idx + reviews_per_page
    page_reviews = browse_df.iloc[start_idx:end_idx]
    
    # Display reviews
    if len(page_reviews) > 0:
        for idx, row in page_reviews.iterrows():
            # Calculate average sentiment across dimensions
            avg_sentiment = row[dimensions].mean()
            sentiment_color = get_sentiment_color(avg_sentiment)
            
            # Create review card
            with st.expander(
                f"⭐ {row['Overall User Rating']}/5 | {row['Product']} | {row['Review Date']} | {row['Reviewer Industry']} | {row['Reviewer Firm Size']}",
                expanded=False
            ):
                # Header with key info
                header_cols = st.columns([2, 1, 1])
                
                with header_cols[0]:
                    st.markdown(f"### {row['Headline']}")
                
                with header_cols[1]:
                    st.metric("Overall Rating (Reviewer)", f"{row['Overall User Rating']}/5")
                
                with header_cols[2]:
                    st.metric("Avg AI Sentiment", f"{avg_sentiment:.2f}")
                
                st.markdown("---")
                
                # Reviewer details
                detail_cols = st.columns(4)
                with detail_cols[0]:
                    st.markdown(f"**Role:** {row['Reviewer Role ']}")
                with detail_cols[1]:
                    st.markdown(f"**Function:** {row['Reviewer Function']}")
                with detail_cols[2]:
                    st.markdown(f"**Industry:** {row['Reviewer Industry']}")
                with detail_cols[3]:
                    st.markdown(f"**Size:** {row['Reviewer Firm Size']}")
                
                st.markdown("---")
                
                # Review content
                st.markdown("**Overall Comment:**")
                st.markdown(row['Overall Comment'])
                
                if pd.notna(row.get('Lessons Learned')):
                    st.markdown("---")
                    st.markdown("**Lessons Learned:**")
                    st.markdown(row['Lessons Learned'])
                
                st.markdown("---")
                
                # Sentiment dimensions
                st.markdown("**AI Sentiment by Dimension:**")
                dim_cols = st.columns(5)
                
                for i, dim in enumerate(dimensions):
                    with dim_cols[i]:
                        score = row[dim]
                        color = get_sentiment_color(score)
                        st.markdown(f"""
                        <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center;">
                            <strong>{dimension_labels[dim]}</strong><br/>
                            <span style="font-size: 1.5em;">{score:.1f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show Gartner ratings if available
                gartner_ratings = []
                if pd.notna(row.get('Evaluation & Contracting')):
                    gartner_ratings.append(f"Evaluation & Contracting: {row['Evaluation & Contracting']}")
                if pd.notna(row.get('Integration & Deployment')):
                    gartner_ratings.append(f"Integration & Deployment: {row['Integration & Deployment']}")
                if pd.notna(row.get('Service & Support')):
                    gartner_ratings.append(f"Service & Support: {row['Service & Support']}")
                if pd.notna(row.get('Product Capabilities')):
                    gartner_ratings.append(f"Product Capabilities: {row['Product Capabilities']}")
                
                if gartner_ratings:
                    st.markdown("---")
                    st.markdown("**Gartner Category Ratings (Reviewer Ratings):**")
                    for rating in gartner_ratings:
                        st.markdown(f"- {rating}/5")
                
                st.markdown("---")
                
                # Topics
                if row['topics_list']:
                    st.markdown("**Topics:**")
                    topics_html = " ".join([
                        f'<span style="background-color: #e3f2fd; padding: 5px 10px; border-radius: 15px; margin: 2px; display: inline-block;">{topic}</span>'
                        for topic in row['topics_list']
                    ])
                    st.markdown(topics_html, unsafe_allow_html=True)
                
                # AI Insights (if available)
                if pd.notna(row.get('review_insights', '')):
                    st.markdown("---")
                    st.markdown("**AI-Generated Insights:**")
                    st.info(row['review_insights'])
                
                # Pain Points (if available)
                if pd.notna(row.get('review_pain_points', '')):
                    st.markdown("**Pain Points:**")
                    st.warning(row['review_pain_points'])
    else:
        st.info("No reviews match the selected filters.")
