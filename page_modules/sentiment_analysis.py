"""
Enhanced Sentiment Analysis Page
Strategic insights with sub-dimension analysis and topic correlation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_sentiment_color, get_sentiment_label, data_source_badge, get_sub_dimensions_for_dimension
from collections import Counter
import numpy as np

def render(filtered_df, full_df):
    """Render the Enhanced Sentiment Analysis page"""
    
    st.header("🎯 Strategic Sentiment Analysis")
    st.markdown("**Granular analysis across 5 dimensions and 15 sub-dimensions with actionable insights**")
    st.caption(data_source_badge('ai_analysis'))
    
    # Product selector (default to Dayforce when available)
    available_products = sorted([p for p in filtered_df['Product'].dropna().unique()])
    
    if not available_products:
        st.warning("⚠️ No product data available in current selection. Adjust filters to include review data.")
        return

    default_product_index = available_products.index('Dayforce') if 'Dayforce' in available_products else 0
    selected_product = st.selectbox(
        "Select product for sentiment analysis",
        options=available_products,
        index=default_product_index,
        help="All visualizations on this page will use the selected product"
    )

    product_df = filtered_df[filtered_df['Product'] == selected_product]

    if len(product_df) == 0:
        st.warning(f"⚠️ No {selected_product} reviews in current selection. Adjust filters to include this product.")
        return
    
    st.info(
        f"📊 Analyzing {len(product_df)} {selected_product} reviews from "
        f"{product_df['parsed_date'].min().strftime('%b %Y')} to {product_df['parsed_date'].max().strftime('%b %Y')}"
    )
    
    # Tab structure for different analysis views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Sub-Dimension Overview",
        "📈 Trend Analysis", 
        "🔍 Root Cause Analysis",
        "⚔️ Competitive Context"
    ])
    
    # ===== TAB 1: SUB-DIMENSION OVERVIEW =====
    with tab1:
        st.subheader("15 Sub-Dimensions Performance Heatmap")
        st.markdown("*Identify specific areas of strength and weakness at a glance*")
        
        # Create sub-dimension performance matrix
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product',
            'gtm': 'GTM',
            'market_direction': 'Market Direction',
            'implementation': 'Implementation',
            'customer_experience': 'Customer Experience'
        }
        
        # Build heatmap data
        heatmap_data = []
        for dim in dimensions:
            sub_dims = get_sub_dimensions_for_dimension(dim)
            for sub_dim in sub_dims:
                scores = product_df[sub_dim].dropna()
                if len(scores) > 0:
                    avg_score = scores.mean()
                    coverage = len(scores)
                    nice_name = sub_dim.replace('_', ' ').title()
                    
                    heatmap_data.append({
                        'Dimension': dimension_labels[dim],
                        'Sub-Dimension': nice_name,
                        'Score': avg_score,
                        'Coverage': coverage,
                        'Status': '🔴 Critical' if avg_score < 3.5 else '🟡 Attention' if avg_score < 4.0 else '🟢 Strong'
                    })

        heatmap_df = pd.DataFrame(heatmap_data)

        if heatmap_df.empty:
            st.info("Not enough sub-dimension data to render the heatmap for this product.")
        else:
            # Display metrics first
            col1, col2, col3 = st.columns(3)
            with col1:
                critical_count = len(heatmap_df[heatmap_df['Score'] < 3.5])
                st.metric("🔴 Critical Areas", critical_count, help="Sub-dimensions scoring below 3.5")
            with col2:
                attention_count = len(heatmap_df[(heatmap_df['Score'] >= 3.5) & (heatmap_df['Score'] < 4.0)])
                st.metric("🟡 Needs Attention", attention_count, help="Sub-dimensions scoring 3.5-4.0")
            with col3:
                strong_count = len(heatmap_df[heatmap_df['Score'] >= 4.0])
                st.metric("🟢 Strong Performance", strong_count, help="Sub-dimensions scoring 4.0+")

            st.markdown("---")

            # Create visual heatmap
            fig = px.sunburst(
                heatmap_df,
                path=['Dimension', 'Sub-Dimension'],
                values='Coverage',
                color='Score',
                color_continuous_scale='RdYlGn',
                range_color=[2.5, 5],
                title="Performance Hierarchy: Dimensions → Sub-Dimensions"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Detailed table with drill-down
            st.subheader("Detailed Sub-Dimension Breakdown")

            for dim in dimensions:
                with st.expander(f"**{dimension_labels[dim]}** - Expand for details"):
                    dim_data = heatmap_df[heatmap_df['Dimension'] == dimension_labels[dim]]
                    dim_data_sorted = dim_data.sort_values('Score')

                    # Overall dimension score
                    overall = product_df[dim].dropna().mean()
                    st.metric(f"{dimension_labels[dim]} Overall Score", f"{overall:.2f}/5.0")

                    # Sub-dimensions
                    for _, row in dim_data_sorted.iterrows():
                        col_left, col_right = st.columns([3, 1])
                        with col_left:
                            status_icon = "🔴" if row['Score'] < 3.5 else "🟡" if row['Score'] < 4.0 else "🟢"
                            st.markdown(f"{status_icon} **{row['Sub-Dimension']}**")
                        with col_right:
                            st.markdown(f"**{row['Score']:.2f}**/5.0 ({row['Coverage']} reviews)")
    
    # ===== TAB 2: TREND ANALYSIS =====
    with tab2:
        st.subheader("📈 Sentiment Trends Over Time")
        st.markdown("*Track how sentiment changes across dimensions to identify deteriorating areas*")
        
        # Add time period selector
        col_period, col_dimension = st.columns([1, 2])
        with col_period:
            time_window = st.selectbox(
                "Time Window",
                ["Monthly", "Quarterly", "All Time"],
                help="Group reviews by time period"
            )
        
        with col_dimension:
            selected_dims = st.multiselect(
                "Select Dimensions to Track",
                options=dimensions,
                default=dimensions,
                format_func=lambda x: dimension_labels[x]
            )
        
        if selected_dims:
            # Prepare time series data
            product_time = product_df.copy()
            product_time['Month'] = product_time['parsed_date'].dt.to_period('M').astype(str)
            product_time['Quarter'] = product_time['parsed_date'].dt.to_period('Q').astype(str)
            
            group_col = 'Month' if time_window == "Monthly" else 'Quarter' if time_window == "Quarterly" else None
            
            if group_col:
                # Group by time period
                time_scores = product_time.groupby(group_col)[selected_dims].mean().reset_index()
                
                # Create line chart with consistent colors
                from utils import get_dimension_color
                fig = go.Figure()
                
                for dim in selected_dims:
                    fig.add_trace(go.Scatter(
                        x=time_scores[group_col],
                        y=time_scores[dim],
                        name=dimension_labels[dim],
                        mode='lines+markers',
                        line=dict(width=2, color=get_dimension_color(dim)),
                        marker=dict(size=8, color=get_dimension_color(dim))
                    ))
                
                # Add threshold lines
                fig.add_hline(y=4.0, line_dash="dash", line_color="green", 
                             annotation_text="Target (4.0)", annotation_position="right")
                fig.add_hline(y=3.5, line_dash="dash", line_color="orange",
                             annotation_text="Warning (3.5)", annotation_position="right")
                
                fig.update_layout(
                    title=f"Sentiment Trend ({time_window})",
                    xaxis_title="Time Period",
                    yaxis_title="Average Score",
                    yaxis=dict(range=[2.5, 5]),
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Trend insights
                st.markdown("### 📊 Trend Insights")
                
                for dim in selected_dims:
                    if len(time_scores) >= 2:
                        recent_score = time_scores[dim].iloc[-1]
                        previous_score = time_scores[dim].iloc[-2]
                        change = recent_score - previous_score
                        
                        # Check if values are valid
                        if pd.isna(change) or pd.isna(recent_score) or pd.isna(previous_score):
                            st.info(f"➡️ **{dimension_labels[dim]}**: Insufficient data for trend analysis")
                        elif abs(change) > 0.2:
                            if change > 0:
                                st.success(f"📈 **{dimension_labels[dim]}**: Improving (+{change:.2f}) - from {previous_score:.2f} to {recent_score:.2f}")
                            else:
                                st.error(f"📉 **{dimension_labels[dim]}**: Declining ({change:.2f}) - from {previous_score:.2f} to {recent_score:.2f}")
                        else:
                            st.info(f"➡️ **{dimension_labels[dim]}**: Stable ({change:+.2f})")
            else:
                st.info("Select Monthly or Quarterly to see trends over time")
    
    # ===== TAB 3: ROOT CAUSE ANALYSIS =====
    with tab3:
        st.subheader("🔍 Root Cause Analysis")
        st.markdown("*Understand WHY scores are low by analyzing associated topics and sub-dimensions*")
        
        # Dimension selector
        analysis_dim = st.selectbox(
            "Select Dimension for Deep Dive",
            options=dimensions,
            format_func=lambda x: dimension_labels[x],
            key='root_cause_dim'
        )

        dim_score = product_df[analysis_dim].dropna().mean()

        col_overview, col_status = st.columns([2, 1])
        with col_overview:
            st.metric(f"{dimension_labels[analysis_dim]} Overall Score", f"{dim_score:.2f}/5.0")
        with col_status:
            if dim_score < 3.5:
                st.error("🔴 Critical - Immediate action needed")
            elif dim_score < 4.0:
                st.warning("🟡 Below target - Monitor closely")
            else:
                st.success("🟢 Meeting expectations")

        st.markdown("---")

        # Sub-dimension breakdown
        st.markdown("### 📊 Sub-Dimension Performance")

        sub_dims = get_sub_dimensions_for_dimension(analysis_dim)
        sub_dim_data = []

        for sub_dim in sub_dims:
            scores = product_df[sub_dim].dropna()
            if len(scores) > 0:
                avg = scores.mean()
                low_count = (scores < 3.5).sum()
                sub_dim_data.append({
                    'sub_dim': sub_dim,
                    'nice_name': sub_dim.replace('_', ' ').title(),
                    'avg': avg,
                    'count': len(scores),
                    'low_count': low_count
                })

        sub_dim_data_sorted = sorted(sub_dim_data, key=lambda x: x['avg'])

        for item in sub_dim_data_sorted:
            col_name, col_score, col_issues = st.columns([3, 1, 1])

            status_color = "🔴" if item['avg'] < 3.5 else "🟡" if item['avg'] < 4.0 else "🟢"

            with col_name:
                st.markdown(f"{status_color} **{item['nice_name']}**")
            with col_score:
                st.markdown(f"**{item['avg']:.2f}**/5.0")
            with col_issues:
                if item['low_count'] > 0:
                    st.markdown(f"⚠️ {item['low_count']} low reviews")

        st.markdown("---")

        # Topic correlation with negative sentiment
        st.markdown("### 🔍 Topics Associated with Negative Sentiment")
        st.markdown(f"*What are customers talking about when they rate {dimension_labels[analysis_dim]} poorly?*")

        # Get low-scoring reviews for this dimension
        low_reviews = product_df[product_df[analysis_dim] < 3.5]
        high_reviews = product_df[product_df[analysis_dim] >= 4.0]
        
        # Map dimension to topic column
        topic_col_map = {
            'product': 'product_topics_list',
            'gtm': 'gtm_topics_list',
            'market_direction': 'market_direction_topics_list',
            'implementation': 'implementation_topics_list',
            'customer_experience': 'customer_experience_topics_list'
        }
        
        topic_col = topic_col_map.get(analysis_dim)
        
        if topic_col and len(low_reviews) > 0:
            # Extract topics from low-scoring reviews
            negative_topics = []
            for topic_list in low_reviews[topic_col]:
                if isinstance(topic_list, list):
                    negative_topics.extend(topic_list)
            
            # Extract topics from high-scoring reviews for comparison
            positive_topics = []
            for topic_list in high_reviews[topic_col]:
                if isinstance(topic_list, list):
                    positive_topics.extend(topic_list)
            
            if negative_topics:
                neg_counter = Counter(negative_topics)
                pos_counter = Counter(positive_topics)
                
                col_neg, col_pos = st.columns(2)
                
                with col_neg:
                    st.markdown(f"#### 🔴 Topics in Low-Scored Reviews ({len(low_reviews)} reviews)")
                    for topic, count in neg_counter.most_common(10):
                        pct = (count / len(low_reviews)) * 100
                        st.markdown(f"- **{topic}**: {count} mentions ({pct:.0f}% of low reviews)")
                
                with col_pos:
                    st.markdown(f"#### 🟢 Topics in High-Scored Reviews ({len(high_reviews)} reviews)")
                    if positive_topics:
                        for topic, count in pos_counter.most_common(10):
                            pct = (count / len(high_reviews)) * 100 if len(high_reviews) > 0 else 0
                            st.markdown(f"- **{topic}**: {count} mentions ({pct:.0f}% of high reviews)")
                    else:
                        st.info("No high-scoring reviews for comparison")
                
                # Key insight: Topics that appear mainly in negative reviews
                st.markdown("---")
                st.markdown("#### 💡 Key Insight: Problem Areas")
                st.markdown("*Topics that appear significantly more in low-scored vs high-scored reviews:*")
                
                problem_topics = []
                for topic, neg_count in neg_counter.most_common(20):
                    pos_count = pos_counter.get(topic, 0)
                    neg_rate = neg_count / len(low_reviews) if len(low_reviews) > 0 else 0
                    pos_rate = pos_count / len(high_reviews) if len(high_reviews) > 0 else 0
                    
                    if neg_rate > pos_rate and neg_count >= 2:
                        problem_topics.append({
                            'topic': topic,
                            'negative_mentions': neg_count,
                            'positive_mentions': pos_count,
                            'problem_score': neg_rate - pos_rate
                        })
                
                if problem_topics:
                    problem_topics_sorted = sorted(problem_topics, key=lambda x: x['problem_score'], reverse=True)
                    
                    for item in problem_topics_sorted[:5]:
                        st.markdown(f"""
                        <div style="background-color: #f8d7da; padding: 15px; margin: 10px 0; 
                                    border-radius: 5px; border-left: 4px solid #dc3545;">
                            <strong>🎯 {item['topic']}</strong><br/>
                            Appears in {item['negative_mentions']} low-scored reviews vs {item['positive_mentions']} high-scored reviews<br/>
                            <small>This topic is strongly associated with negative sentiment</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No clear problem topics identified - issues may be systemic rather than topic-specific")
            else:
                st.info(f"No specific topics mentioned in low-scoring {dimension_labels[analysis_dim]} reviews")
        else:
            st.info(f"Not enough low-scoring reviews for {dimension_labels[analysis_dim]} to analyze topics")
    
    # ===== TAB 4: COMPETITIVE CONTEXT =====
    with tab4:
        st.subheader("⚔️ Competitive Benchmark")
        st.markdown(f"*How does {selected_product} compare to competitors at the sub-dimension level?*")

        competitors_df = filtered_df[filtered_df['Product'] != selected_product]

        if len(competitors_df) > 0:
            # Select dimension for comparison
            comp_dim = st.selectbox(
                "Select Dimension to Compare",
                options=dimensions,
                format_func=lambda x: dimension_labels[x],
                key='comp_dim'
            )
            
            sub_dims = get_sub_dimensions_for_dimension(comp_dim)
            
            # Build comparison data
            comparison_data = []
            
            for sub_dim in sub_dims:
                nice_name = sub_dim.replace('_', ' ').title()
                
                # Selected product score
                df_score = product_df[sub_dim].dropna().mean()
                
                # Competitor average
                comp_score = competitors_df[sub_dim].dropna().mean()
                
                if pd.notna(df_score):
                    comparison_data.append({
                        'Sub-Dimension': nice_name,
                        selected_product: df_score,
                        'Competitors Avg': comp_score if pd.notna(comp_score) else 0,
                        'Gap': df_score - (comp_score if pd.notna(comp_score) else 0)
                    })
            
            comp_df = pd.DataFrame(comparison_data)

            if comp_df.empty:
                st.info("Not enough overlapping review data to compare sub-dimensions against competitors.")
            else:
                # Visualization
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name=selected_product,
                    y=comp_df['Sub-Dimension'],
                    x=comp_df[selected_product],
                    orientation='h',
                    marker_color='#0c5460'
                ))

                fig.add_trace(go.Bar(
                    name='Competitors Average',
                    y=comp_df['Sub-Dimension'],
                    x=comp_df['Competitors Avg'],
                    orientation='h',
                    marker_color='lightgray'
                ))

                fig.update_layout(
                    title=f"{selected_product} vs Competitors: {dimension_labels[comp_dim]} Sub-Dimensions",
                    xaxis_title="Average Score",
                    barmode='group',
                    height=400,
                    xaxis=dict(range=[0, 5])
                )

                st.plotly_chart(fig, use_container_width=True)

                # Gap analysis
                st.markdown("### Gap Analysis")

                for _, row in comp_df.iterrows():
                    if row['Gap'] > 0.3:
                        st.success(f"🏆 **{row['Sub-Dimension']}**: Leading by +{row['Gap']:.2f} points")
                    elif row['Gap'] < -0.3:
                        st.error(f"🎯 **{row['Sub-Dimension']}**: Trailing by {row['Gap']:.2f} points - Priority area")
                    else:
                        st.info(f"➡️ **{row['Sub-Dimension']}**: Competitive ({row['Gap']:+.2f})")
        else:
            st.warning("No competitor data in current selection")


def calculate_sentiment_stats(df, dimension):
    """Calculate statistics for a sentiment dimension"""
    if dimension not in df.columns:
        return None
    
    # Filter out NaN values for calculations
    valid_scores = df[dimension].dropna()
    
    if len(valid_scores) == 0:
        return None
    
    return {
        'mean': valid_scores.mean(),
        'median': valid_scores.median(),
        'std': valid_scores.std(),
        'min': valid_scores.min(),
        'max': valid_scores.max(),
        'count': len(valid_scores)
    }
