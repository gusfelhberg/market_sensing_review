"""
Strategic Overview Page
Multi-source unified intelligence dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_sentiment_color, get_source_label, get_source_icon, get_source_color, get_source_type_config
from collections import Counter
import numpy as np

def render(filtered_df, full_df):
    """Render the Strategic Overview page with multi-source intelligence"""
    
    st.header("🌟 Strategic Overview")
    st.markdown("**Unified intelligence across customer reviews and analyst perspectives**")
    
    # Check what sources we have
    sources_present = filtered_df['source_type'].unique()
    has_multiple_sources = len(sources_present) > 1
    
    if has_multiple_sources:
        st.info("📊 **Multi-Source View Active** - Analyzing insights from multiple perspectives for comprehensive intelligence")
    else:
        source_label = get_source_label(sources_present[0])
        source_icon = get_source_icon(sources_present[0])
        st.info(f"{source_icon} **Single Source View** - Viewing {source_label} only. Use sidebar filter to view all sources.")
    
    # Key metrics row
    st.markdown("### 📊 Intelligence Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_insights = len(filtered_df)
        st.metric("Total Insights", total_insights)
        if has_multiple_sources:
            for source_type in sources_present:
                count = len(filtered_df[filtered_df['source_type'] == source_type])
                icon = get_source_icon(source_type)
                label = get_source_label(source_type)
                st.caption(f"{icon} {count} {label}")
    
    with col2:
        dayforce_count = len(filtered_df[filtered_df['Product'] == 'Dayforce'])
        st.metric("Dayforce Insights", dayforce_count)
        if dayforce_count > 0:
            pct = (dayforce_count / total_insights) * 100
            st.caption(f"{pct:.0f}% of total")
    
    with col3:
        # Date range
        if len(filtered_df) > 0:
            date_range_days = (filtered_df['parsed_date'].max() - filtered_df['parsed_date'].min()).days
            st.metric("Time Coverage", f"{date_range_days} days")
            st.caption(f"{filtered_df['parsed_date'].min().strftime('%b %Y')} - {filtered_df['parsed_date'].max().strftime('%b %Y')}")
    
    with col4:
        # Product coverage
        products = filtered_df['Product'].nunique()
        st.metric("Products Covered", products)
        product_list = sorted(filtered_df['Product'].unique())
        st.caption(f"{', '.join(product_list[:3])}")
    
    st.markdown("---")
    
    # Tab structure for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Unified Sentiment",
        "🔄 Source Comparison", 
        "🎯 Key Insights",
        "📊 Topic Analysis"
    ])
    
    # ===== TAB 1: UNIFIED SENTIMENT =====
    with tab1:
        st.subheader("Unified Sentiment Dashboard")
        st.markdown("*Combined view across all sources for comprehensive perception*")
        
        # Focus on Dayforce
        dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
        
        if len(dayforce_df) == 0:
            st.warning("No Dayforce data in current selection")
            return
        
        # Overall dimension scores
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product',
            'gtm': 'Go-to-Market',
            'market_direction': 'Market Direction',
            'implementation': 'Implementation',
            'customer_experience': 'Customer Experience'
        }
        
        # Calculate average scores across all sources
        dim_scores = []
        for dim in dimensions:
            avg_score = dayforce_df[dim].dropna().mean()
            count = dayforce_df[dim].notna().sum()
            dim_scores.append({
                'Dimension': dimension_labels[dim],
                'Score': avg_score,
                'Count': count
            })
        
        dim_df = pd.DataFrame(dim_scores)
        
        # Visualization
        col_viz, col_metrics = st.columns([2, 1])
        
        with col_viz:
            fig = go.Figure()
            
            # Add bar chart
            colors = [get_sentiment_color(score) for score in dim_df['Score']]
            
            fig.add_trace(go.Bar(
                x=dim_df['Dimension'],
                y=dim_df['Score'],
                marker_color=colors,
                text=dim_df['Score'].round(2),
                textposition='outside',
                hovertemplate='%{x}<br>Score: %{y:.2f}<extra></extra>'
            ))
            
            # Add target line
            fig.add_hline(y=4.0, line_dash="dash", line_color="green",
                         annotation_text="Target (4.0)", annotation_position="right")
            
            fig.update_layout(
                title="Dayforce Sentiment by Dimension (All Sources)",
                yaxis_title="Average Score (1-5)",
                yaxis=dict(range=[0, 5.5]),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_metrics:
            st.markdown("**Dimension Performance**")
            for _, row in dim_df.iterrows():
                score = row['Score']
                if score >= 4.0:
                    status = "🟢 Strong"
                elif score >= 3.5:
                    status = "🟡 Good"
                else:
                    status = "🔴 Needs Focus"
                
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 8px; margin: 5px 0; border-radius: 5px;">
                    <strong>{row['Dimension']}</strong><br/>
                    {score:.2f}/5.0 - {status}<br/>
                    <small>{row['Count']} insights</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Source breakdown if multiple sources
        if has_multiple_sources:
            st.markdown("### 📊 Sentiment by Source")
            st.markdown("*How do different sources perceive Dayforce?*")
            
            # Create comparison data
            source_comparison = []
            for source_type in sources_present:
                source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                for dim in dimensions:
                    avg_score = source_df[dim].dropna().mean()
                    if pd.notna(avg_score):
                        source_comparison.append({
                            'Source': get_source_label(source_type),
                            'Dimension': dimension_labels[dim],
                            'Score': avg_score
                        })
            
            comp_df = pd.DataFrame(source_comparison)
            
            if not comp_df.empty:
                # Pivot for grouped bar chart
                pivot_df = comp_df.pivot(index='Dimension', columns='Source', values='Score')
                
                fig = go.Figure()
                
                for source in pivot_df.columns:
                    source_type = [st for st in sources_present if get_source_label(st) == source][0]
                    color = get_source_color(source_type)
                    
                    fig.add_trace(go.Bar(
                        name=source,
                        x=pivot_df.index,
                        y=pivot_df[source],
                        marker_color=color
                    ))
                
                fig.update_layout(
                    barmode='group',
                    title="Sentiment Comparison by Source",
                    yaxis_title="Average Score",
                    yaxis=dict(range=[0, 5]),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # ===== TAB 2: SOURCE COMPARISON =====
    with tab2:
        st.subheader("Source Comparison Analysis")
        st.markdown("*Side-by-side comparison of customer and analyst perspectives*")
        
        if not has_multiple_sources:
            st.info("Select 'All Sources' in the sidebar to see source comparison.")
            return
        
        # Dayforce only for this analysis
        dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
        
        # Create side-by-side comparison
        col_left, col_right = st.columns(2)
        
        for idx, source_type in enumerate(sources_present):
            source_df = dayforce_df[dayforce_df['source_type'] == source_type]
            icon = get_source_icon(source_type)
            label = get_source_label(source_type)
            color = get_source_color(source_type)
            
            col = col_left if idx == 0 else col_right
            
            with col:
                st.markdown(f"### {icon} {label}")
                st.markdown(f"**{len(source_df)} insights**")
                
                # Calculate dimension scores
                for dim in dimensions:
                    avg_score = source_df[dim].dropna().mean()
                    if pd.notna(avg_score):
                        status_color = get_sentiment_color(avg_score)
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 10px; margin: 5px 0; 
                                    border-radius: 5px; border-left: 4px solid {status_color};">
                            <strong>{dimension_labels[dim]}</strong><br/>
                            Score: {avg_score:.2f}/5.0
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Convergence/Divergence Analysis
        st.markdown("### 🔍 Convergence & Divergence Analysis")
        st.markdown("*Where do sources agree or differ in their perception?*")
        
        if len(sources_present) >= 2:
            source_scores = {}
            for source_type in sources_present:
                source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                scores = {}
                for dim in dimensions:
                    scores[dim] = source_df[dim].dropna().mean()
                source_scores[source_type] = scores
            
            # Calculate differences
            convergence_data = []
            source_types = list(sources_present)
            if len(source_types) >= 2:
                for dim in dimensions:
                    score1 = source_scores[source_types[0]].get(dim)
                    score2 = source_scores[source_types[1]].get(dim)
                    
                    if pd.notna(score1) and pd.notna(score2):
                        diff = abs(score1 - score2)
                        avg = (score1 + score2) / 2
                        
                        if diff < 0.3:
                            status = "✅ Aligned"
                            color = "#d4edda"
                        elif diff < 0.7:
                            status = "⚠️ Moderate Gap"
                            color = "#fff3cd"
                        else:
                            status = "❌ Divergent"
                            color = "#f8d7da"
                        
                        convergence_data.append({
                            'dimension': dimension_labels[dim],
                            'diff': diff,
                            'avg': avg,
                            'status': status,
                            'color': color,
                            'score1': score1,
                            'score2': score2
                        })
            
            if convergence_data:
                for item in sorted(convergence_data, key=lambda x: x['diff'], reverse=True):
                    st.markdown(f"""
                    <div style="background-color: {item['color']}; padding: 12px; margin: 8px 0; border-radius: 5px;">
                        <strong>{item['dimension']}</strong> - {item['status']}<br/>
                        {get_source_label(source_types[0])}: {item['score1']:.2f} | 
                        {get_source_label(source_types[1])}: {item['score2']:.2f}<br/>
                        <small>Difference: {item['diff']:.2f} points</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ===== TAB 3: KEY INSIGHTS =====
    with tab3:
        st.subheader("Key Strategic Insights")
        st.markdown("*Critical findings synthesized across all sources*")
        
        dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
        
        # Identify strengths and opportunities
        dimension_scores = {}
        for dim in dimensions:
            dimension_scores[dim] = dayforce_df[dim].dropna().mean()
        
        strengths = {k: v for k, v in dimension_scores.items() if v >= 4.0}
        opportunities = {k: v for k, v in dimension_scores.items() if v < 3.5}
        
        col_str, col_opp = st.columns(2)
        
        with col_str:
            st.markdown("### ✅ Key Strengths")
            if strengths:
                for dim, score in sorted(strengths.items(), key=lambda x: x[1], reverse=True):
                    st.success(f"**{dimension_labels[dim]}**: {score:.2f}/5.0")
                    
                    # Show what's working by source
                    if has_multiple_sources:
                        for source_type in sources_present:
                            source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                            source_score = source_df[dim].dropna().mean()
                            if pd.notna(source_score):
                                icon = get_source_icon(source_type)
                                label = get_source_label(source_type)
                                st.caption(f"{icon} {label}: {source_score:.2f}")
            else:
                st.info("No dimensions scoring above 4.0")
        
        with col_opp:
            st.markdown("### 🎯 Improvement Opportunities")
            if opportunities:
                for dim, score in sorted(opportunities.items(), key=lambda x: x[1]):
                    st.error(f"**{dimension_labels[dim]}**: {score:.2f}/5.0")
                    
                    # Show concern by source
                    if has_multiple_sources:
                        for source_type in sources_present:
                            source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                            source_score = source_df[dim].dropna().mean()
                            if pd.notna(source_score):
                                icon = get_source_icon(source_type)
                                label = get_source_label(source_type)
                                st.caption(f"{icon} {label}: {source_score:.2f}")
            else:
                st.success("All dimensions performing well!")
        
        st.markdown("---")
        
        # Multi-source validated insights
        if has_multiple_sources:
            st.markdown("### 🎯 Multi-Source Validated Insights")
            st.markdown("*Issues or strengths confirmed across both perspectives*")
            
            # Find dimensions where both sources agree on sentiment
            validated_concerns = []
            validated_strengths = []
            
            for dim in dimensions:
                scores_by_source = {}
                for source_type in sources_present:
                    source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                    score = source_df[dim].dropna().mean()
                    if pd.notna(score):
                        scores_by_source[source_type] = score
                
                if len(scores_by_source) >= 2:
                    all_low = all(s < 3.5 for s in scores_by_source.values())
                    all_high = all(s >= 4.0 for s in scores_by_source.values())
                    
                    if all_low:
                        avg = sum(scores_by_source.values()) / len(scores_by_source)
                        validated_concerns.append((dim, avg, scores_by_source))
                    elif all_high:
                        avg = sum(scores_by_source.values()) / len(scores_by_source)
                        validated_strengths.append((dim, avg, scores_by_source))
            
            if validated_concerns:
                st.markdown("**⚠️ Validated Concerns** (Both sources agree)")
                for dim, avg, scores in validated_concerns:
                    st.markdown(f"""
                    <div style="background-color: #f8d7da; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid #dc3545;">
                        <strong>{dimension_labels[dim]}</strong> - Average: {avg:.2f}/5.0<br/>
                        {' | '.join([f"{get_source_icon(st)} {score:.2f}" for st, score in scores.items()])}
                    </div>
                    """, unsafe_allow_html=True)
            
            if validated_strengths:
                st.markdown("**✅ Validated Strengths** (Both sources agree)")
                for dim, avg, scores in validated_strengths:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid #28a745;">
                        <strong>{dimension_labels[dim]}</strong> - Average: {avg:.2f}/5.0<br/>
                        {' | '.join([f"{get_source_icon(st)} {score:.2f}" for st, score in scores.items()])}
                    </div>
                    """, unsafe_allow_html=True)
    
    # ===== TAB 4: TOPIC ANALYSIS =====
    with tab4:
        st.subheader("Cross-Source Topic Analysis")
        st.markdown("*What themes emerge across different intelligence sources?*")
        
        dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
        
        # Aggregate topics across all sources
        all_topics = []
        for topics_list in dayforce_df['topics_list']:
            if isinstance(topics_list, list):
                all_topics.extend(topics_list)
        
        topic_counter = Counter(all_topics)
        
        if topic_counter:
            # Top topics overall
            st.markdown("### 📌 Top Topics Across All Sources")
            
            top_topics = topic_counter.most_common(15)
            
            topic_df = pd.DataFrame(top_topics, columns=['Topic', 'Count'])
            
            fig = px.bar(
                topic_df,
                x='Count',
                y='Topic',
                orientation='h',
                title='Most Discussed Topics'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Topic breakdown by source
            if has_multiple_sources:
                st.markdown("---")
                st.markdown("### 🔍 Topic Frequency by Source")
                
                source_topic_data = []
                for source_type in sources_present:
                    source_df = dayforce_df[dayforce_df['source_type'] == source_type]
                    source_topics = []
                    for topics_list in source_df['topics_list']:
                        if isinstance(topics_list, list):
                            source_topics.extend(topics_list)
                    
                    source_counter = Counter(source_topics)
                    for topic, count in source_counter.most_common(10):
                        source_topic_data.append({
                            'Source': get_source_label(source_type),
                            'Topic': topic,
                            'Count': count
                        })
                
                source_topic_df = pd.DataFrame(source_topic_data)
                
                # Show as grouped bar
                if not source_topic_df.empty:
                    # Get top topics overall
                    top_10_topics = [t[0] for t in topic_counter.most_common(10)]
                    filtered_st_df = source_topic_df[source_topic_df['Topic'].isin(top_10_topics)]
                    
                    if not filtered_st_df.empty:
                        fig = px.bar(
                            filtered_st_df,
                            x='Count',
                            y='Topic',
                            color='Source',
                            orientation='h',
                            barmode='group',
                            title='Topic Comparison by Source'
                        )
                        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No topics extracted from current selection")
