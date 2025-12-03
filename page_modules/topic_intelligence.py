"""
Topic Intelligence Page
Analyze trending topics and their associated sentiment with multi-source awareness
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from utils import (
    get_trending_topics,
    get_topics_by_sentiment,
    get_sentiment_color,
    data_source_badge,
    parse_lessons_learned,
    get_source_label,
    get_source_icon,
)
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import feedback_system

def calculate_topic_overlap(df1, df2):
    """Calculate percentage of topics that appear in both dataframes"""
    topics1 = set()
    for topics_list in df1['topics_list']:
        topics1.update(topics_list)
    
    topics2 = set()
    for topics_list in df2['topics_list']:
        topics2.update(topics_list)
    
    if not topics1 or not topics2:
        return 0
    
    overlap = topics1.intersection(topics2)
    return (len(overlap) / len(topics1.union(topics2))) * 100

def render_topic_comparison(focus_df, compare_df, focus_label, compare_label):
    """Render detailed topic comparison between two products"""
    
    # Get topics for each product
    focus_topics = Counter()
    for topics_list in focus_df['topics_list']:
        focus_topics.update(topics_list)
    
    compare_topics = Counter()
    for topics_list in compare_df['topics_list']:
        compare_topics.update(topics_list)
    
    # Categorize topics
    focus_only = set(focus_topics.keys()) - set(compare_topics.keys())
    compare_only = set(compare_topics.keys()) - set(focus_topics.keys())
    shared_topics = set(focus_topics.keys()).intersection(set(compare_topics.keys()))
    
    # Display summary
    col_cat1, col_cat2, col_cat3 = st.columns(3)
    
    with col_cat1:
        st.markdown(f"### 🎯 {focus_label} Only")
        st.metric("Unique Topics", len(focus_only))
        if focus_only:
            st.markdown("**Top Unique Topics:**")
            for topic in sorted(focus_only, key=lambda t: focus_topics[t], reverse=True)[:5]:
                st.markdown(f"- **{topic}** ({focus_topics[topic]} mentions)")
    
    with col_cat2:
        st.markdown(f"### 🔗 Shared Topics")
        st.metric("Common Topics", len(shared_topics))
        if shared_topics:
            st.markdown("**Sentiment Differences:**")
            
            # Calculate sentiment for shared topics
            differences = []
            for topic in shared_topics:
                focus_sentiment = calculate_topic_sentiment(focus_df, topic)
                compare_sentiment = calculate_topic_sentiment(compare_df, topic)
                diff = focus_sentiment - compare_sentiment
                differences.append((topic, diff, focus_sentiment, compare_sentiment, 
                                  focus_topics[topic], compare_topics[topic]))
            
            # Sort by absolute difference
            differences.sort(key=lambda x: abs(x[1]), reverse=True)
            
            for topic, diff, focus_sent, comp_sent, focus_count, comp_count in differences[:5]:
                if diff > 0:
                    icon = "✅"
                    color = "#d4edda"
                elif diff < 0:
                    icon = "⚠️"
                    color = "#fff3cd"
                else:
                    icon = "➡️"
                    color = "#f8f9fa"
                
                st.markdown(f"""
                <div style="background-color: {color}; padding: 8px; margin: 5px 0; 
                            border-radius: 4px; font-size: 0.85em;">
                    {icon} <strong>{topic}</strong><br/>
                    {focus_label}: {focus_sent:.2f} ({focus_count}x) | 
                    {compare_label}: {comp_sent:.2f} ({comp_count}x)
                </div>
                """, unsafe_allow_html=True)
    
    with col_cat3:
        st.markdown(f"### ⚔️ {compare_label} Only")
        st.metric("Unique Topics", len(compare_only))
        if compare_only:
            st.markdown("**Top Unique Topics:**")
            for topic in sorted(compare_only, key=lambda t: compare_topics[t], reverse=True)[:5]:
                st.markdown(f"- **{topic}** ({compare_topics[topic]} mentions)")
    
    st.markdown("---")
    
    # Detailed shared topics analysis
    if shared_topics:
        st.subheader(f"📊 Shared Topics: Where {focus_label} Wins/Loses")
        
        col_win, col_lose = st.columns(2)
        
        # Separate into wins and losses
        wins = [d for d in differences if d[1] > 0.2]  # Focus sentiment > 0.2 higher
        losses = [d for d in differences if d[1] < -0.2]  # Focus sentiment > 0.2 lower
        
        with col_win:
            st.markdown(f"### ✅ {focus_label} Stronger Sentiment")
            if wins:
                for topic, diff, focus_sent, comp_sent, focus_count, comp_count in wins[:10]:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid #28a745;">
                        <strong>{topic}</strong><br/>
                        {focus_label}: ⭐ {focus_sent:.2f} ({focus_count} mentions)<br/>
                        {compare_label}: {comp_sent:.2f} ({comp_count} mentions)<br/>
                        <small>Advantage: +{diff:.2f} points</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"No topics where {focus_label} has significantly better sentiment")
        
        with col_lose:
            st.markdown(f"### ⚠️ {compare_label} Stronger Sentiment")
            if losses:
                for topic, diff, focus_sent, comp_sent, focus_count, comp_count in losses[:10]:
                    st.markdown(f"""
                    <div style="background-color: #fff3cd; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid #ffc107;">
                        <strong>{topic}</strong><br/>
                        {focus_label}: {focus_sent:.2f} ({focus_count} mentions)<br/>
                        {compare_label}: ⭐ {comp_sent:.2f} ({comp_count} mentions)<br/>
                        <small>Gap: {diff:.2f} points</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success(f"{focus_label} matches or exceeds {compare_label} in all shared topics!")
    
    st.markdown("---")
    
    # Strategic implications
    st.subheader("🎯 Strategic Implications")
    
    col_impl1, col_impl2 = st.columns(2)
    
    with col_impl1:
        st.markdown("### 💡 Opportunities")
        opportunities = []
        
        # Unique competitor topics = learning opportunities
        if compare_only:
            opportunities.append({
                'title': f"Learn from {compare_label}'s unique focus areas",
                'detail': f"{compare_label} is discussing {len(compare_only)} topics not mentioned in {focus_label} reviews. Consider if these represent gaps or opportunities.",
                'action': f"Investigate: {', '.join(list(compare_only)[:3])}"
            })
        
        # Topics where competitor has better sentiment
        if losses:
            top_loss = losses[0]
            opportunities.append({
                'title': f"Close sentiment gap on '{top_loss[0]}'",
                'detail': f"{compare_label} scores {top_loss[3]:.2f} vs {focus_label} {top_loss[2]:.2f}",
                'action': f"Analyze {compare_label} reviews to understand what they do better"
            })
        
        # Unique focus topics with low sentiment
        if focus_only:
            for topic in focus_only:
                topic_sentiment = calculate_topic_sentiment(focus_df, topic)
                if topic_sentiment < 3.8:
                    opportunities.append({
                        'title': f"Address unique pain point: '{topic}'",
                        'detail': f"Only mentioned in {focus_label} reviews with low sentiment ({topic_sentiment:.2f})",
                        'action': f"This may be a {focus_label}-specific issue requiring attention"
                    })
                    break
        
        for i, opp in enumerate(opportunities[:3], 1):
            st.markdown(f"""
            <div style="background-color: #d1ecf1; padding: 15px; margin: 10px 0; 
                        border-radius: 5px; border-left: 4px solid #0c5460;">
                <strong>{i}. {opp['title']}</strong><br/>
                {opp['detail']}<br/>
                <small>💡 Action: {opp['action']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col_impl2:
        st.markdown("### 💪 Leverage Points")
        leverage = []
        
        # Unique focus topics with high sentiment
        if focus_only:
            for topic in focus_only:
                topic_sentiment = calculate_topic_sentiment(focus_df, topic)
                if topic_sentiment >= 4.2:
                    leverage.append({
                        'title': f"Unique strength: '{topic}'",
                        'detail': f"Only {focus_label} is praised for this ({topic_sentiment:.2f} sentiment)",
                        'action': "Highlight in competitive positioning and marketing"
                    })
                    break
        
        # Topics where focus has better sentiment
        if wins:
            top_win = wins[0]
            leverage.append({
                'title': f"Competitive advantage on '{top_win[0]}'",
                'detail': f"{focus_label} scores {top_win[2]:.2f} vs {compare_label} {top_win[3]:.2f}",
                'action': f"Use in sales battles against {compare_label}"
            })
        
        # High mention topics with good sentiment
        for topic in shared_topics:
            focus_count = focus_topics[topic]
            focus_sentiment = calculate_topic_sentiment(focus_df, topic)
            if focus_count >= 5 and focus_sentiment >= 4.0:
                leverage.append({
                    'title': f"Proven strength: '{topic}'",
                    'detail': f"Frequently mentioned ({focus_count}x) with strong sentiment ({focus_sentiment:.2f})",
                    'action': "Amplify in customer success stories and testimonials"
                })
                break
        
        for i, lev in enumerate(leverage[:3], 1):
            st.markdown(f"""
            <div style="background-color: #d4edda; padding: 15px; margin: 10px 0; 
                        border-radius: 5px; border-left: 4px solid #28a745;">
                <strong>{i}. {lev['title']}</strong><br/>
                {lev['detail']}<br/>
                <small>💪 Action: {lev['action']}</small>
            </div>
            """, unsafe_allow_html=True)

def calculate_topic_sentiment(df, topic):
    """Calculate average sentiment for reviews mentioning a specific topic"""
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    
    topic_reviews = df[df['topics_list'].apply(lambda x: topic in x)]
    
    if len(topic_reviews) == 0:
        return 0
    
    return topic_reviews[dimensions].mean().mean()

def render(filtered_df, full_df):
    """Render the Topic Intelligence page with multi-source awareness"""
    
    # Ensure parsed_date column exists (should already be present from unified data loading)
    if 'parsed_date' not in filtered_df.columns:
        # Fallback: try to parse from date column if needed
        if 'date' in filtered_df.columns:
            filtered_df['parsed_date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
        else:
            filtered_df['parsed_date'] = pd.NaT
    
    # Page header with inline feedback buttons
    col1, col2, col3 = st.columns([8, 1.2, 1.2])
    with col1:
        st.header("💡 Topic Intelligence")
    with col2:
        if st.button("💬 Feedback", key="feedback_btn_topic", type="primary"):
            feedback_system.show_feedback_modal("Topic Intelligence", "Topic Intelligence", "", "")
    with col3:
        username = feedback_system.auth.get_current_user()
        is_admin = feedback_system.auth.is_admin()
        feedback_count = len(feedback_system.get_section_feedback("Topic Intelligence", None if is_admin else username))
        if is_admin:
            view_label = f"All Feedbacks ({feedback_count})" if feedback_count > 0 else "All Feedbacks (0)"
        else:
            view_label = f"My Feedbacks ({feedback_count})" if feedback_count > 0 else "My Feedbacks (0)"
        if st.button(view_label, key="view_feedback_btn_topic", type="primary", help="View feedback"):
            feedback_system.show_feedback_viewer_modal("Topic Intelligence")
    
    st.markdown("**Understand what customers and analysts are discussing and their perspectives**")
    
    # Show source breakdown
    sources_present = filtered_df['source_type'].value_counts()
    has_multiple_sources = len(sources_present) > 1
    
    if has_multiple_sources:
        source_info = []
        for source_type, count in sources_present.items():
            icon = get_source_icon(source_type)
            label = get_source_label(source_type)
            source_info.append(f"{icon} {count} {label}")
        st.info(f"📊 **Multi-Source Topic Analysis**: {' + '.join(source_info)}")
    else:
        source_type = sources_present.index[0]
        icon = get_source_icon(source_type)
        label = get_source_label(source_type)
        st.info(f"{icon} **{label}**: Analyzing {len(filtered_df)} insights")
    
    st.markdown("---")
    
    # Add source filter option
    col_source, col_product1, col_compare_toggle, col_product2 = st.columns([1, 2, 1, 2])
    
    with col_source:
        if has_multiple_sources:
            source_filter = st.selectbox(
                "📊 Source Filter",
                ['All Sources'] + [get_source_label(st) for st in sources_present.index],
                help="Filter topics by source"
            )
            
            # Apply source filter
            if source_filter != 'All Sources':
                source_type_map = {get_source_label(st): st for st in sources_present.index}
                selected_source_type = source_type_map[source_filter]
                filtered_df = filtered_df[filtered_df['source_type'] == selected_source_type]
        else:
            st.markdown("**Source:**")
            st.caption(get_source_label(sources_present.index[0]))
    
    with col_product1:
        focus_product = st.selectbox(
            "🎯 Primary Focus",
            ['All Products', 'Dayforce'] + [p for p in sorted(filtered_df['Product'].unique()) if p != 'Dayforce'],
            index=1,  # Default to Dayforce
            help="Select product to analyze in detail"
        )
    
    with col_compare_toggle:
        st.markdown("&nbsp;")  # Spacing
        compare_enabled = st.checkbox(
            "📊 Compare",
            value=False,
            help="Compare topics with a competitor"
        )
    
    with col_product2:
        if compare_enabled:
            competitor_options = [p for p in sorted(filtered_df['Product'].unique()) if p != focus_product]
            compare_product = st.selectbox(
                "⚔️ Compare With",
                competitor_options if competitor_options else ['No competitors'],
                help="Select competitor to compare against"
            )
        else:
            compare_product = None
            st.markdown("&nbsp;")  # Spacing
    
    # Filter data based on selection
    if focus_product == 'All Products':
        focus_df = filtered_df.copy()
        focus_label = "All Products"
    else:
        focus_df = filtered_df[filtered_df['Product'] == focus_product].copy()
        focus_label = focus_product
    
    if compare_enabled and compare_product:
        compare_df = filtered_df[filtered_df['Product'] == compare_product].copy()
    else:
        compare_df = None
    
    st.markdown("---")
    
    # Show selection summary with clear scope indicator
    if compare_enabled and compare_df is not None and not compare_df.empty:
        st.success(f"📊 **Comparison Mode Active:** Analyzing {focus_label} vs. {compare_product}")
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric(f"{focus_label} Reviews", len(focus_df))
        with col_sum2:
            st.metric(f"{compare_product} Reviews", len(compare_df))
        with col_sum3:
            overlap = calculate_topic_overlap(focus_df, compare_df)
            st.metric("Topic Overlap", f"{overlap:.0f}%")
    else:
        if focus_label == 'Dayforce':
            st.success(f"🎯 **Analyzing: {focus_label} Only** ({len(focus_df)} reviews) - All insights below are Dayforce-specific")
        else:
            st.info(f"📊 **Analyzing: {focus_label}** ({len(focus_df)} reviews)")
    
    st.markdown("---")
    
    # Top topics overview - use comparison mode if enabled
    if compare_enabled and compare_df is not None and not compare_df.empty:
        # Render full comparison view
        render_topic_comparison(focus_df, compare_df, focus_label, compare_product)
    else:
        # Render standard single-product view
        st.subheader(f"🔥 Trending Topics - {focus_label}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get top topics
            top_topics = get_trending_topics(focus_df, top_n=20)
            
            if top_topics:
                topics_df = pd.DataFrame(top_topics, columns=['Topic', 'Count'])
                
                fig = px.bar(
                    topics_df.head(15),
                    x='Count',
                    y='Topic',
                    orientation='h',
                    title="Most Mentioned Topics",
                    labels={'Count': 'Number of Mentions', 'Topic': 'Topic'},
                    color='Count',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No topics found in the selected data.")
        
        with col2:
            st.markdown("**Topic Statistics**")
            
            # Calculate topic stats
            all_topics = []
            for topics_list in filtered_df['topics_list']:
                all_topics.extend(topics_list)
            
            unique_topics = len(set(all_topics))
            total_mentions = len(all_topics)
            avg_topics_per_review = total_mentions / len(filtered_df) if len(filtered_df) > 0 else 0
            
            st.metric("Unique Topics", unique_topics)
            st.metric("Total Mentions", total_mentions)
            st.metric("Avg Topics/Review", f"{avg_topics_per_review:.1f}")
            
        st.markdown("---")
            
        # Product filter for topics
        st.markdown("**Filter by Product**")
        product_filter = st.selectbox(
            "Select Product",
            ['All'] + sorted(focus_df['Product'].unique().tolist()),
            key='topic_product_filter'
        )
    
        st.markdown("---")
        
        # Topic sentiment analysis
        st.subheader("😊 Topic Sentiment Analysis")
        st.markdown("*AI sentiment scores (1-5) by dimension for topics*")
        
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product (AI)',
            'gtm': 'GTM (AI)',
            'market_direction': 'Market Dir. (AI)',
            'implementation': 'Implementation (AI)',
            'customer_experience': 'Cust. Exp. (AI)'
        }
        
        selected_dimension = st.selectbox(
            "Analyze topics by dimension",
            dimensions,
            format_func=lambda x: dimension_labels[x],
            key='topic_dimension_select'
        )
        
        # Filter by product if selected
        analysis_df = focus_df.copy()
        if product_filter != 'All':
            analysis_df = analysis_df[analysis_df['Product'] == product_filter]
    
        # Get topics by sentiment
        topics_by_sentiment = get_topics_by_sentiment(analysis_df, selected_dimension, threshold=4.0)
        
        col_low, col_high = st.columns(2)
        
        with col_low:
            st.markdown("### ⚠️ Topics with Lower Sentiment")
            st.markdown("*Topics appearing in reviews with scores < 4.0*")
            
            low_topics = topics_by_sentiment['low']
            
            if low_topics:
                low_df = pd.DataFrame(low_topics[:10], columns=['Topic', 'Count'])
                
                for idx, row in low_df.iterrows():
                    st.markdown(f"""
                    <div style="background-color: #fee; padding: 10px; margin: 5px 0; 
                                border-radius: 5px; border-left: 3px solid #e74c3c;">
                        <strong>{row['Topic']}</strong><br/>
                        <small>{row['Count']} mentions in low-scoring reviews</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No topics in low-sentiment reviews")
        
        with col_high:
            st.markdown("### ✅ Topics with Higher Sentiment")
            st.markdown("*Topics appearing in reviews with scores ≥ 4.0*")
            
            high_topics = topics_by_sentiment['high']
            
            if high_topics:
                high_df = pd.DataFrame(high_topics[:10], columns=['Topic', 'Count'])
                
                for idx, row in high_df.iterrows():
                    st.markdown(f"""
                    <div style="background-color: #efe; padding: 10px; margin: 5px 0; 
                                border-radius: 5px; border-left: 3px solid #2ecc71;">
                        <strong>{row['Topic']}</strong><br/>
                        <small>{row['Count']} mentions in high-scoring reviews</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No topics in high-sentiment reviews")
            
        st.markdown("---")
        
        # Topic co-occurrence (topics mentioned together)
        st.subheader("🔗 Topic Co-occurrence")
        st.markdown("*Which topics are frequently mentioned together?*")
        
        # Build co-occurrence matrix
        topic_pairs = Counter()
        
        for topics_list in analysis_df['topics_list']:
            topics = list(set(topics_list))  # Remove duplicates within same review
            for i in range(len(topics)):
                for j in range(i+1, len(topics)):
                    pair = tuple(sorted([topics[i], topics[j]]))
                    topic_pairs[pair] += 1
        
        # Display top pairs
        if topic_pairs:
            top_pairs = topic_pairs.most_common(15)
            
            col_pair1, col_pair2 = st.columns([2, 1])
            
            with col_pair1:
                pairs_df = pd.DataFrame([
                    {'Topic 1': pair[0], 'Topic 2': pair[1], 'Co-occurrences': count}
                    for pair, count in top_pairs
                ])
                
                st.dataframe(
                    pairs_df,
                    use_container_width=True,
                    hide_index=True
                )
            
            with col_pair2:
                st.markdown("**Interpretation**")
                st.markdown("""
                Topics that appear together frequently may indicate:
                - Related feature areas
                - Connected customer journeys
                - Bundled concerns or praises
                - System integration points
                """)
        else:
            st.info("Not enough data to identify topic co-occurrences")
        
        st.markdown("---")
        
        # Deep dive into specific topic
        st.subheader("🔍 Topic Deep Dive")
        # st.caption(f"{data_source_badge('ai_analysis')} | Review content: {data_source_badge('customer_review')}")
        
        # Get all unique topics from analysis_df (respects product filter)
        all_topics_filtered = []
        for topics_list in analysis_df['topics_list']:
            all_topics_filtered.extend(topics_list)
        all_unique_topics = sorted(list(set(all_topics_filtered)))
        
        if all_unique_topics:
            # Calculate topic frequencies
            topic_counts = {}
            for topic in all_unique_topics:
                topic_counts[topic] = sum(1 for topics_list in analysis_df['topics_list'] if topic in topics_list)
            
            # Filter out topics with 0 occurrences
            topics_with_counts = [(topic, count) for topic, count in topic_counts.items() if count > 0]
            topics_with_counts.sort(key=lambda x: x[1], reverse=True)  # Sort by count descending
            
            # Create topic options with counts
            topic_options = [f"{topic} ({count})" for topic, count in topics_with_counts]
            
            # Product filter and topic selection
            col_topic, col_product_filter = st.columns([2, 1])
            
            with col_topic:
                selected_option = st.selectbox(
                    "Select a topic to analyze in detail",
                    topic_options,
                    key='topic_deep_dive'
                )
                # Extract the topic name from the selection (remove the count part)
                selected_topic = selected_option.rsplit(' (', 1)[0]
            
            with col_product_filter:
                # Product filter for topic deep dive
                topic_products = ['All Products'] + sorted(analysis_df['Product'].unique().tolist())
                selected_topic_product = st.selectbox(
                    "Filter by Product",
                    topic_products,
                    key='topic_deep_dive_product'
                )

            
            # Filter reviews containing this topic
            topic_reviews = analysis_df[analysis_df['topics_list'].apply(lambda x: selected_topic in x)]
            
            # Apply product filter if not "All Products"
            if selected_topic_product != 'All Products':
                topic_reviews = topic_reviews[topic_reviews['Product'] == selected_topic_product]
            
            if len(topic_reviews) > 0:
                col_td1, col_td2, col_td3 = st.columns(3)
                
                with col_td1:
                    st.metric("Total Mentions", len(topic_reviews))
                
                with col_td2:
                    avg_sentiment = topic_reviews[dimensions].mean().mean()
                    st.metric("Avg AI Sentiment", f"{avg_sentiment:.2f}")
                
                with col_td3:
                    product_breakdown = topic_reviews['Product'].value_counts()
                    top_product = product_breakdown.index[0] if len(product_breakdown) > 0 else "N/A"
                    st.metric("Top Product", top_product)
                
                # Sentiment breakdown by dimension
                st.markdown("**Sentiment by Dimension**")
                
                dimension_scores = topic_reviews[dimensions].mean()
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=[dimension_labels[d] for d in dimensions],
                        y=[dimension_scores[d] for d in dimensions],
                        marker_color=[get_sentiment_color(dimension_scores[d]) for d in dimensions],
                        text=[f"{dimension_scores[d]:.2f}" for d in dimensions],
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    title=f"AI Sentiment Scores for '{selected_topic}'",
                    yaxis_title="AI Sentiment Score (1-5)",
                    yaxis=dict(range=[0, 5.5]),
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show all reviews
                st.markdown(f"**All Reviews Mentioning This Topic** ({len(topic_reviews)} reviews)")

                # Sort reviews by rating ascending (surface problem areas first)
                # Filter to only reviews with ratings (exclude analyst insights)
                reviews_with_ratings = topic_reviews[topic_reviews['overall_rating'].notna()]
                topic_reviews_sorted = reviews_with_ratings.sort_values(by='overall_rating', ascending=True)

                for idx, row in topic_reviews_sorted.iterrows():
                    overall_rating = row.get('overall_rating', pd.NA)
                    rating_value = overall_rating if pd.notna(overall_rating) else 'N/A'
                    date_value = row.get('parsed_date') if 'parsed_date' in row else pd.NaT
                    if pd.isna(date_value):
                        # Parsed date should already be available from unified data
                        date_str = 'Date N/A'
                    else:
                        date_str = date_value.strftime('%b %d, %Y')

                    headline = row.get('headline')
                    if not pd.notna(headline) or not str(headline).strip():
                        comment_text = str(row.get('text_content', '')).strip()
                        if comment_text:
                            first_sentence = comment_text.split('.')[0][:70].strip()
                            headline = first_sentence + ('...' if len(comment_text) > len(first_sentence) else '')
                        else:
                            headline = f"{row.get('Product', 'Product')} Review"

                    reviewer_role = row.get('reviewer_role', 'Role N/A')
                    reviewer_industry = row.get('reviewer_industry', 'Industry N/A')
                    reviewer_size = row.get('reviewer_firm_size', 'Company size N/A')
                    reviewer_country = row.get('Country', 'Country N/A')

                    # Determine styling icon based on rating
                    if pd.notna(overall_rating):
                        if overall_rating <= 3:
                            header_icon = '🔴'
                        elif overall_rating < 4:
                            header_icon = '🟡'
                        else:
                            header_icon = '🟢'
                    else:
                        header_icon = '🛈'

                    expander_label = f"{header_icon} {headline} | {row.get('Product', 'Product')} | ⭐ {rating_value}/5 | {date_str}"

                    with st.expander(expander_label):
                        col_meta1, col_meta2 = st.columns(2)
                        with col_meta1:
                            st.markdown("**Reviewer Profile**")
                            st.markdown(f"- Role: {reviewer_role if pd.notna(reviewer_role) else 'Role N/A'}")
                            st.markdown(f"- Industry: {reviewer_industry if pd.notna(reviewer_industry) else 'Industry N/A'}")
                            st.markdown(f"- Company Size: {reviewer_size if pd.notna(reviewer_size) else 'Company size N/A'}")
                            st.markdown(f"- Country: {reviewer_country if pd.notna(reviewer_country) else 'Country N/A'}")

                        with col_meta2:
                            st.markdown("**Review Details**")
                            st.markdown(f"- Product: {row.get('Product', 'N/A')}")
                            st.markdown(f"- Review Date: {date_str}")
                            if pd.notna(overall_rating):
                                st.markdown(f"- Overall Rating: ⭐ {overall_rating}/5")
                            review_url = row.get('review_url')
                            if review_url and pd.notna(review_url):
                                st.markdown(f"- [View Original Review]({review_url})")

                        # Review narrative
                        comment_text = row.get('text_content')
                        if pd.notna(comment_text) and str(comment_text).strip():
                            st.markdown("**💬 Full Review Comment**")
                            st.markdown(f"*{comment_text}*")

                        # Lessons learned parsed into likes/dislikes
                        lessons_raw = row.get('lessons_learned')
                        if pd.notna(lessons_raw) and str(lessons_raw).strip():
                            lessons = parse_lessons_learned(lessons_raw)
                            if lessons['likes'] or lessons['dislikes']:
                                st.markdown("**📚 Lessons Learned (from reviewer)**")
                                if lessons['likes']:
                                    st.markdown("**👍 What they like most:**")
                                    st.success(lessons['likes'])
                                if lessons['dislikes']:
                                    st.markdown("**👎 What they dislike most:**")
                                    st.warning(lessons['dislikes'])

                        # Topics associated with this review
                        topics_for_review = row.get('topics_list', [])
                        if topics_for_review:
                            st.markdown("**🏷️ Topics Highlighted in this Review**")
                            st.markdown(", ".join(sorted(set(topics_for_review))))

                        # Dimension scores
                        st.markdown("**📈 AI Sentiment Dimension Scores**")
                        dim_cols = st.columns(len(dimensions))
                        for i, dim in enumerate(dimensions):
                            with dim_cols[i]:
                                score_val = row.get(dim)
                                display_val = f"{score_val:.2f}" if pd.notna(score_val) else "N/A"
                                st.metric(dimension_labels[dim], display_val)

                        # Gartner category ratings if available
                        gartner_ratings = []
                        if pd.notna(row.get('Evaluation & Contracting')):
                            gartner_ratings.append(f"Evaluation & Contracting: {row['Evaluation & Contracting']}/5")
                        if pd.notna(row.get('Integration & Deployment')):
                            gartner_ratings.append(f"Integration & Deployment: {row['Integration & Deployment']}/5")
                        if pd.notna(row.get('Service & Support')):
                            gartner_ratings.append(f"Service & Support: {row['Service & Support']}/5")
                        if pd.notna(row.get('Product Capabilities')):
                            gartner_ratings.append(f"Product Capabilities: {row['Product Capabilities']}/5")

                        if gartner_ratings:
                            st.markdown("**🏅 Gartner Category Ratings (Reviewer)**")
                            for rating in gartner_ratings:
                                st.markdown(f"- {rating}")
            else:
                st.info(f"No reviews found mentioning '{selected_topic}' in the current selection.")
        else:
            st.info("No topics available for deep dive analysis.")

