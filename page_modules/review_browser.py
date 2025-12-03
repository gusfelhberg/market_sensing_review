"""
Review Browser Page
Browse and filter all insights with full details and source information
"""

import streamlit as st
import pandas as pd
from utils import get_sentiment_color, data_source_badge, get_source_label, get_source_icon, get_source_badge
import plotly.express as px
import plotly.graph_objects as go
import feedback_system

def render(filtered_df, full_df):
    """Render the Review Browser page with source awareness"""
    
    # Page header with inline feedback buttons
    col1, col2, col3 = st.columns([8, 1.2, 1.2])
    with col1:
        st.title("📋 Data Browser")
    with col2:
        if st.button("💬 Feedback", key="feedback_btn_browser", type="primary"):
            feedback_system.show_feedback_modal("Data Browser", "Data Browser", "", "")
    with col3:
        username = feedback_system.auth.get_current_user()
        is_admin = feedback_system.auth.is_admin()
        feedback_count = len(feedback_system.get_section_feedback("Data Browser", None if is_admin else username))
        if is_admin:
            view_label = f"All Feedbacks ({feedback_count})" if feedback_count > 0 else "All Feedbacks (0)"
        else:
            view_label = f"My Feedbacks ({feedback_count})" if feedback_count > 0 else "My Feedbacks (0)"
        if st.button(view_label, key="view_feedback_btn_browser", type="primary", help="View feedback"):
            feedback_system.show_feedback_viewer_modal("Data Browser")
    
    st.markdown("*Browse and filter all insights from multiple sources*")
    
    # Show source breakdown
    sources_present = filtered_df['source_type'].value_counts()
    source_info = []
    for source_type, count in sources_present.items():
        icon = get_source_icon(source_type)
        label = get_source_label(source_type)
        source_info.append(f"{icon} {count} {label}")
    
    st.caption(f"📊 Sources: {' | '.join(source_info)}")
    
    # Dimensions for analysis
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': 'Product',
        'gtm': 'GTM',
        'market_direction': 'Market Direction',
        'implementation': 'Implementation',
        'customer_experience': 'Customer Experience'
    }
    
    # Use the already-parsed topics_list from data loading
    analysis_df = filtered_df.copy()
    # Ensure topics_list exists (it should be created during data loading)
    if 'topics_list' not in analysis_df.columns:
        analysis_df['topics_list'] = [[] for _ in range(len(analysis_df))]
    
    st.markdown("---")
    
    # Create filter columns
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        # Source filter
        source_options = ['All Sources'] + [get_source_label(st) for st in sources_present.index]
        selected_source = st.selectbox(
            "Source Type",
            source_options,
            key='review_browser_source'
        )
    
    with filter_col2:
        # Product filter
        review_products = ['All'] + sorted(analysis_df['Product'].unique().tolist())
        selected_review_product = st.selectbox(
            "Product",
            review_products,
            key='review_browser_product'
        )
    
    with filter_col3:
        # Rating filter (only for reviews with ratings)
        has_ratings = 'overall_rating' in analysis_df.columns and analysis_df['overall_rating'].notna().any()
        if has_ratings:
            rating_options = ['All', '5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star']
            selected_rating = st.selectbox(
                "Rating",
                rating_options,
                key='review_browser_rating'
            )
        else:
            st.markdown("**Rating**")
            st.caption("N/A")
            selected_rating = 'All'
    
    with filter_col4:
        # Dimension filter
        dim_options = ['All Dimensions'] + [dimension_labels[d] for d in dimensions]
        selected_dimension = st.selectbox(
            "Focus Dimension",
            dim_options,
            key='review_browser_dimension'
        )
    
    # Apply filters
    browse_df = analysis_df.copy()
    
    if selected_source != 'All Sources':
        source_type_map = {get_source_label(st): st for st in sources_present.index}
        selected_source_type = source_type_map[selected_source]
        browse_df = browse_df[browse_df['source_type'] == selected_source_type]
    
    if selected_review_product != 'All':
        browse_df = browse_df[browse_df['Product'] == selected_review_product]
    
    if selected_rating != 'All' and has_ratings:
        rating_value = int(selected_rating.split()[0])
        browse_df = browse_df[browse_df['overall_rating'] == rating_value]
    
    # Display summary
    st.markdown(f"**Showing {len(browse_df)} of {len(analysis_df)} insights**")
    
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
        # Only sort rows that have ratings (exclude analyst insights)
        browse_df = browse_df.sort_values('overall_rating', ascending=False, na_position='last')
    elif sort_by == 'Rating (Lowest)':
        # Only sort rows that have ratings (exclude analyst insights)
        browse_df = browse_df.sort_values('overall_rating', ascending=True, na_position='last')
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
            
            # Get source badge
            source_badge = get_source_badge(row.get('source_type', 'N/A'))
            
            # Format rating display (N/A for analyst insights)
            overall_rating = row.get('overall_rating')
            rating_display = f"{overall_rating}/5" if pd.notna(overall_rating) else "N/A"
            
            # Format date display
            date_value = row.get('parsed_date')
            date_display = date_value.strftime('%Y-%m-%d') if pd.notna(date_value) else "N/A"
            
            # Get metadata with fallbacks
            product = row.get('Product', 'N/A')
            reviewer_industry = row.get('reviewer_industry', 'N/A')
            reviewer_size = row.get('reviewer_firm_size', 'N/A')
            
            # Create review card
            with st.expander(
                f"{source_badge} | ⭐ {rating_display} | {product} | {date_display} | {reviewer_industry} | {reviewer_size}",
                expanded=False
            ):
                # Header with key info
                header_cols = st.columns([2, 1, 1])
                
                with header_cols[0]:
                    headline = row.get('headline', 'Review')
                    st.markdown(f"### {headline}")
                
                with header_cols[1]:
                    st.metric("Overall Rating", rating_display)
                
                with header_cols[2]:
                    st.metric("Avg AI Sentiment", f"{avg_sentiment:.2f}")
                
                st.markdown("---")
                
                # Reviewer/Source details
                detail_cols = st.columns(4)
                with detail_cols[0]:
                    reviewer_role = row.get('reviewer_role', row.get('analyst_name', 'N/A'))
                    st.markdown(f"**Role/Analyst:** {reviewer_role}")
                with detail_cols[1]:
                    firm_or_function = row.get('analyst_firm', row.get('Reviewer Function', 'N/A'))
                    st.markdown(f"**Firm/Function:** {firm_or_function}")
                with detail_cols[2]:
                    reviewer_industry = row.get('reviewer_industry', 'N/A')
                    st.markdown(f"**Industry:** {reviewer_industry}")
                with detail_cols[3]:
                    reviewer_size = row.get('reviewer_firm_size', 'N/A')
                    st.markdown(f"**Size:** {reviewer_size}")
                
                st.markdown("---")
                
                # Review/Insight content
                st.markdown("**Content:**")
                text_content = row.get('text_content', 'N/A')
                st.markdown(text_content)
                
                lessons_learned = row.get('lessons_learned')
                if pd.notna(lessons_learned) and str(lessons_learned).strip():
                    st.markdown("---")
                    st.markdown("**Lessons Learned:**")
                    st.markdown(lessons_learned)
                
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
                
                # Show dimension-specific topics
                st.markdown("---")
                st.markdown("**Topics by Dimension:**")
                
                topic_categories = [
                    ('Product', 'product_topics_list', '🔧'),
                    ('GTM', 'gtm_topics_list', '💼'),
                    ('Market Direction', 'market_direction_topics_list', '🎯'),
                    ('Implementation', 'implementation_topics_list', '⚙️'),
                    ('Customer Experience', 'customer_experience_topics_list', '🤝'),
                    ('Other', 'other_topics_list', '📌')
                ]
                
                for label, col, emoji in topic_categories:
                    if col in row and row[col]:
                        topics = row[col]
                        if topics:
                            topics_str = ', '.join(topics[:5])  # Limit to first 5
                            st.markdown(f"{emoji} **{label}:** {topics_str}")
                
                # Show low-scoring dimensions as pain points
                st.markdown("---")
                st.markdown("**Performance Indicators:**")
                
                score_cols = [
                    ('degree_of_meeting_functional_requirements', 'Functional Requirements'),
                    ('product_functionality', 'Product Functionality'),
                    ('quality_of_product_user_experience', 'User Experience'),
                    ('quality_and_timeliness_of_support', 'Support Quality'),
                    ('value_for_money', 'Value for Money')
                ]
                
                low_scores = []
                for col, label in score_cols:
                    if col in row and pd.notna(row[col]):
                        score = row[col]
                        if score < 3.5:
                            low_scores.append(f"{label}: {score}/5")
                
                if low_scores:
                    st.warning("**Areas of Concern:**\n" + "\n- ".join([''] + low_scores))
    else:
        st.info("No reviews match the selected filters.")
