"""
Analyst Intelligence Page
Dedicated analysis of industry analyst insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_sentiment_color, get_source_icon
from collections import Counter
import numpy as np

def render(filtered_df, full_df):
    """Render the Analyst Intelligence page"""
    
    st.header("🎓 Analyst Intelligence")
    st.markdown("**Strategic market insights from industry analyst interactions**")
    
    # Filter to analyst insights only
    analyst_df = filtered_df[filtered_df['source_type'] == 'analyst_insight']
    
    if len(analyst_df) == 0:
        st.warning("⚠️ No analyst insights in current selection. This page analyzes analyst intelligence specifically.")
        st.info("Use the sidebar filter to include 'Analyst Intelligence' source.")
        return
    
    st.info(f"📊 Analyzing {len(analyst_df)} analyst insights from {analyst_df['parsed_date'].min().strftime('%b %Y')} to {analyst_df['parsed_date'].max().strftime('%b %Y')}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        firms = analyst_df['analyst_firm'].nunique()
        st.metric("Analyst Firms", firms)
    
    with col2:
        analysts = analyst_df['analyst_name'].nunique()
        st.metric("Individual Analysts", analysts)
    
    with col3:
        avg_sentiment = analyst_df[['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']].mean().mean()
        st.metric("Avg Sentiment", f"{avg_sentiment:.2f}/5.0")
    
    with col4:
        # Most active firm
        top_firm = analyst_df['analyst_firm'].value_counts().index[0]
        st.metric("Most Active Firm", top_firm)
    
    st.markdown("---")
    
    # Tab structure
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Firm Analysis",
        "👤 Analyst Profiles",
        "📈 Sentiment Trends",
        "💬 Key Insights"
    ])
    
    # ===== TAB 1: FIRM ANALYSIS =====
    with tab1:
        st.subheader("Analyst Firm Analysis")
        st.markdown("*Compare perspectives across different analyst firms*")
        
        # Firm distribution
        firm_counts = analyst_df['analyst_firm'].value_counts()
        
        col_chart, col_table = st.columns([2, 1])
        
        with col_chart:
            fig = px.pie(
                values=firm_counts.values,
                names=firm_counts.index,
                title="Insights by Analyst Firm",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col_table:
            st.markdown("**Firm Breakdown**")
            for firm, count in firm_counts.head(10).items():
                st.markdown(f"**{firm}**: {count} insights")
        
        st.markdown("---")
        
        # Sentiment by firm
        st.markdown("### 📊 Sentiment Analysis by Firm")
        
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product',
            'gtm': 'Go-to-Market',
            'market_direction': 'Market Direction',
            'implementation': 'Implementation',
            'customer_experience': 'Customer Experience'
        }
        
        # Select firms to compare
        top_firms = firm_counts.head(5).index.tolist()
        selected_firms = st.multiselect(
            "Select firms to compare",
            options=firm_counts.index.tolist(),
            default=top_firms[:3] if len(top_firms) >= 3 else top_firms,
            help="Choose which analyst firms to include in the comparison"
        )
        
        if selected_firms:
            firm_sentiment_data = []
            for firm in selected_firms:
                firm_df = analyst_df[analyst_df['analyst_firm'] == firm]
                for dim in dimensions:
                    avg_score = firm_df[dim].dropna().mean()
                    if pd.notna(avg_score):
                        firm_sentiment_data.append({
                            'Firm': firm,
                            'Dimension': dimension_labels[dim],
                            'Score': avg_score,
                            'Count': firm_df[dim].notna().sum()
                        })
            
            firm_sent_df = pd.DataFrame(firm_sentiment_data)
            
            if not firm_sent_df.empty:
                # Heatmap
                pivot_df = firm_sent_df.pivot(index='Firm', columns='Dimension', values='Score')
                
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x="Dimension", y="Firm", color="Score"),
                    x=pivot_df.columns,
                    y=pivot_df.index,
                    color_continuous_scale='RdYlGn',
                    aspect="auto",
                    title="Sentiment Heatmap by Firm and Dimension"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed comparison
                st.markdown("### 📋 Detailed Firm Comparison")
                
                for firm in selected_firms:
                    with st.expander(f"**{firm}** - Detailed View"):
                        firm_df = analyst_df[analyst_df['analyst_firm'] == firm]
                        
                        col_info, col_scores = st.columns([1, 2])
                        
                        with col_info:
                            st.metric("Total Insights", len(firm_df))
                            analysts_count = firm_df['analyst_name'].nunique()
                            st.metric("Analysts", analysts_count)
                            
                            # Date range
                            min_date = firm_df['parsed_date'].min()
                            max_date = firm_df['parsed_date'].max()
                            st.caption(f"Period: {min_date.strftime('%b %Y')} - {max_date.strftime('%b %Y')}")
                        
                        with col_scores:
                            st.markdown("**Dimension Scores**")
                            for dim in dimensions:
                                score = firm_df[dim].dropna().mean()
                                if pd.notna(score):
                                    color = get_sentiment_color(score)
                                    st.markdown(f"""
                                    <div style="background-color: #f8f9fa; padding: 8px; margin: 5px 0; 
                                                border-radius: 5px; border-left: 4px solid {color};">
                                        <strong>{dimension_labels[dim]}</strong>: {score:.2f}/5.0
                                    </div>
                                    """, unsafe_allow_html=True)
        else:
            st.info("Select at least one firm to see comparison")
    
    # ===== TAB 2: ANALYST PROFILES =====
    with tab2:
        st.subheader("Individual Analyst Profiles")
        st.markdown("*Track sentiment and focus areas by individual analyst*")
        
        # Analyst distribution
        analyst_counts = analyst_df['analyst_name'].value_counts()
        
        st.markdown(f"### 👥 {len(analyst_counts)} Individual Analysts")
        
        # Filter: minimum insights per analyst
        min_insights = st.slider(
            "Minimum insights per analyst",
            min_value=1,
            max_value=int(analyst_counts.max()),
            value=2,
            help="Filter to analysts with at least this many insights"
        )
        
        active_analysts = analyst_counts[analyst_counts >= min_insights]
        
        st.info(f"Showing {len(active_analysts)} analysts with {min_insights}+ insights")
        
        # Select analyst to profile
        selected_analyst = st.selectbox(
            "Select analyst to profile",
            options=active_analysts.index.tolist(),
            help="Choose an analyst to see detailed profile"
        )
        
        if selected_analyst:
            analyst_data = analyst_df[analyst_df['analyst_name'] == selected_analyst]
            
            st.markdown(f"## 📊 {selected_analyst} Profile")
            
            # Overview metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Insights", len(analyst_data))
            
            with col2:
                firm = analyst_data['analyst_firm'].iloc[0]
                st.metric("Firm", firm)
            
            with col3:
                date_range = f"{analyst_data['parsed_date'].min().strftime('%b %Y')} - {analyst_data['parsed_date'].max().strftime('%b %Y')}"
                st.metric("Active Period", date_range)
            
            st.markdown("---")
            
            # Sentiment profile
            col_sent, col_topics = st.columns(2)
            
            with col_sent:
                st.markdown("**Sentiment Profile**")
                
                for dim in dimensions:
                    score = analyst_data[dim].dropna().mean()
                    if pd.notna(score):
                        color = get_sentiment_color(score)
                        count = analyst_data[dim].notna().sum()
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 10px; margin: 5px 0; 
                                    border-radius: 5px; border-left: 4px solid {color};">
                            <strong>{dimension_labels[dim]}</strong><br/>
                            Score: {score:.2f}/5.0 ({count} mentions)
                        </div>
                        """, unsafe_allow_html=True)
            
            with col_topics:
                st.markdown("**Focus Areas**")
                
                # Extract topics
                analyst_topics = []
                for topics_list in analyst_data['topics_list']:
                    if isinstance(topics_list, list):
                        analyst_topics.extend(topics_list)
                
                if analyst_topics:
                    topic_counter = Counter(analyst_topics)
                    for topic, count in topic_counter.most_common(10):
                        st.markdown(f"• **{topic}**: {count} mentions")
                else:
                    st.info("No topics extracted")
            
            # Recent insights
            st.markdown("---")
            st.markdown("**Recent Insights**")
            
            for idx, row in analyst_data.nlargest(3, 'parsed_date').iterrows():
                date_str = row['parsed_date'].strftime('%b %d, %Y')
                text = row['text_content'][:200] + "..." if len(row['text_content']) > 200 else row['text_content']
                
                st.markdown(f"""
                <div style="background-color: #e7f3ff; padding: 12px; margin: 8px 0; border-radius: 5px;">
                    <small><strong>{date_str}</strong></small><br/>
                    {text}
                </div>
                """, unsafe_allow_html=True)
    
    # ===== TAB 3: SENTIMENT TRENDS =====
    with tab3:
        st.subheader("Sentiment Trends Over Time")
        st.markdown("*How has analyst sentiment evolved?*")
        
        # Time series analysis
        analyst_df_sorted = analyst_df.sort_values('parsed_date')
        
        # Group by month or quarter
        time_grouping = st.radio(
            "Time granularity",
            options=['Monthly', 'Quarterly'],
            horizontal=True
        )
        
        if time_grouping == 'Monthly':
            analyst_df_sorted['period'] = analyst_df_sorted['parsed_date'].dt.to_period('M').astype(str)
        else:
            analyst_df_sorted['period'] = analyst_df_sorted['parsed_date'].dt.to_period('Q').astype(str)
        
        # Select dimensions to track
        selected_dims = st.multiselect(
            "Select dimensions to track",
            options=dimensions,
            default=dimensions,
            format_func=lambda x: dimension_labels[x]
        )
        
        if selected_dims:
            # Calculate average by period
            trend_data = analyst_df_sorted.groupby('period')[selected_dims].mean().reset_index()
            
            # Plot
            fig = go.Figure()
            
            for dim in selected_dims:
                fig.add_trace(go.Scatter(
                    x=trend_data['period'],
                    y=trend_data[dim],
                    name=dimension_labels[dim],
                    mode='lines+markers',
                    line=dict(width=2),
                    marker=dict(size=8)
                ))
            
            # Add target line
            fig.add_hline(y=4.0, line_dash="dash", line_color="green",
                         annotation_text="Target (4.0)", annotation_position="right")
            
            fig.update_layout(
                title=f"Analyst Sentiment Trends ({time_grouping})",
                xaxis_title="Period",
                yaxis_title="Average Score",
                yaxis=dict(range=[2.5, 5]),
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend insights
            st.markdown("### 📊 Trend Analysis")
            
            if len(trend_data) >= 2:
                for dim in selected_dims:
                    recent = trend_data[dim].iloc[-1]
                    previous = trend_data[dim].iloc[-2]
                    change = recent - previous
                    
                    # Check if values are valid
                    if pd.isna(change) or pd.isna(recent) or pd.isna(previous):
                        st.info(f"➡️ **{dimension_labels[dim]}**: Insufficient data for trend analysis")
                    elif abs(change) > 0.2:
                        if change > 0:
                            st.success(f"📈 **{dimension_labels[dim]}**: Improving (+{change:.2f}) - from {previous:.2f} to {recent:.2f}")
                        else:
                            st.error(f"📉 **{dimension_labels[dim]}**: Declining ({change:.2f}) - from {previous:.2f} to {recent:.2f}")
                    else:
                        st.info(f"➡️ **{dimension_labels[dim]}**: Stable ({change:+.2f})")
        else:
            st.info("Select at least one dimension to see trends")
    
    # ===== TAB 4: KEY INSIGHTS =====
    with tab4:
        st.subheader("Key Analyst Insights")
        st.markdown("*Highlighted observations from analyst interactions*")
        
        # Most recent insights
        st.markdown("### 🕐 Recent Analyst Observations")
        
        recent_count = st.slider("Number of recent insights to show", 5, 20, 10)
        
        for idx, row in analyst_df.nlargest(recent_count, 'parsed_date').iterrows():
            date_str = row['parsed_date'].strftime('%b %d, %Y')
            firm = row['analyst_firm']
            analyst = row['analyst_name']
            text = row['text_content'][:300] + "..." if len(row['text_content']) > 300 else row['text_content']
            
            # Get sentiment indicators
            dimensions_present = []
            for dim in dimensions:
                if pd.notna(row[dim]):
                    score = row[dim]
                    color = get_sentiment_color(score)
                    dimensions_present.append(f'<span style="color: {color};">●</span> {dimension_labels[dim]}: {score:.1f}')
            
            sentiment_str = ' | '.join(dimensions_present) if dimensions_present else 'No scores'
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; 
                        border-radius: 5px; border-left: 4px solid #059669;">
                <strong>🎓 {firm} - {analyst}</strong><br/>
                <small>{date_str}</small><br/><br/>
                {text}<br/><br/>
                <small>{sentiment_str}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Most discussed topics by analysts
        st.markdown("### 🔍 Analyst Focus Topics")
        
        all_topics = []
        for topics_list in analyst_df['topics_list']:
            if isinstance(topics_list, list):
                all_topics.extend(topics_list)
        
        if all_topics:
            topic_counter = Counter(all_topics)
            top_topics = topic_counter.most_common(15)
            
            topic_df = pd.DataFrame(top_topics, columns=['Topic', 'Frequency'])
            
            fig = px.bar(
                topic_df,
                x='Frequency',
                y='Topic',
                orientation='h',
                title='Most Discussed Topics by Analysts',
                color='Frequency',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No topics extracted from analyst insights")
