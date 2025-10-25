"""
Executive Summary Page
High-level dashboard with key metrics and trends
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import calculate_competitive_position, get_sentiment_color, get_sentiment_label, data_source_badge

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import get_sentiment_color, get_sentiment_label, calculate_competitive_position

def render(filtered_df, full_df):
    """Render the Executive Summary page"""
    
    st.header("📈 Executive Summary")
    st.markdown("**Strategic overview of customer sentiment and market position**")
    st.caption(f"{data_source_badge('customer_review')} for ratings | {data_source_badge('ai_analysis')} for sentiment dimensions")
    
    # Display data scope indicator
    products_in_view = sorted(filtered_df['Product'].unique().tolist())
    if len(products_in_view) == 1:
        if products_in_view[0] == 'Dayforce':
            st.info(f"🎯 **Viewing: {products_in_view[0]} Only** - All metrics show Dayforce performance")
        else:
            st.info(f"📊 **Viewing: {products_in_view[0]} Only**")
    else:
        if 'Dayforce' in products_in_view:
            st.warning(f"📊 **Viewing: {len(products_in_view)} Products** - Metrics include Dayforce + competitors ({', '.join([p for p in products_in_view if p != 'Dayforce'])}). Use sidebar filters to focus on Dayforce only.")
        else:
            st.info(f"📊 **Viewing: {len(products_in_view)} Products** - {', '.join(products_in_view)}")
    
    # Explanation of metrics
    with st.expander("ℹ️ About These Metrics", expanded=False):
        st.markdown("""
        **AI Sentiment Scores (1-5):** The scores below are derived from AI analysis of customer review text, 
        not from direct reviewer ratings. The AI evaluates sentiment across 5 strategic dimensions:
        
        - **Product**: Product capabilities and features
        - **GTM**: Go-to-market strategy and positioning  
        - **Market Direction**: Vision and market leadership
        - **Implementation**: Onboarding and deployment experience
        - **Customer Experience**: Support and overall satisfaction
        
        These complement the **Overall User Rating** (also 1-5) which is the direct star rating from reviewers.
        """)
    
    # Key Metrics Row
    st.subheader("🤖 AI Sentiment Scores by Dimension")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': '📦 Product (AI)',
        'gtm': '🚀 GTM (AI)',
        'market_direction': '🧭 Market Direction (AI)',
        'implementation': '⚙️ Implementation (AI)',
        'customer_experience': '😊 Customer Exp. (AI)'
    }
    
    cols = [col1, col2, col3, col4, col5]
    
    for i, dim in enumerate(dimensions):
        with cols[i]:
            avg_score = filtered_df[dim].mean()
            color = get_sentiment_color(avg_score)
            delta = avg_score - full_df[dim].mean() if len(filtered_df) < len(full_df) else 0
            
            st.metric(
                label=dimension_labels[dim],
                value=f"{avg_score:.2f}",
                delta=f"{delta:+.2f}" if delta != 0 else None
            )
            st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold;'>{get_sentiment_label(avg_score)}</div>", 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two-column layout for main content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Sentiment Trends Over Time")
        
        # Prepare data for time series
        trend_df = filtered_df.copy()
        trend_df['Month'] = trend_df['parsed_date'].dt.to_period('M').astype(str)
        
        # Aggregate by month
        monthly_avg = trend_df.groupby('Month')[dimensions].mean().reset_index()
        
        # Create line chart
        fig = go.Figure()
        
        for dim in dimensions:
            fig.add_trace(go.Scatter(
                x=monthly_avg['Month'],
                y=monthly_avg[dim],
                mode='lines+markers',
                name=dimension_labels[dim],
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Average AI Sentiment Scores by Month",
            xaxis_title="Month",
            yaxis_title="AI Sentiment Score (1-5)",
            yaxis=dict(range=[0, 5]),
            hovermode='x unified',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Review Distribution
        st.subheader("📝 Review Distribution")
        
        col_dist1, col_dist2 = st.columns(2)
        
        with col_dist1:
            # By Product
            product_counts = filtered_df['Product'].value_counts()
            fig_product = px.pie(
                values=product_counts.values,
                names=product_counts.index,
                title="Reviews by Product",
                hole=0.4
            )
            fig_product.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_product, use_container_width=True)
        
        with col_dist2:
            # By Rating
            rating_counts = filtered_df['Overall User Rating'].value_counts().sort_index()
            fig_rating = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                title="Reviews by Overall Rating (Reviewer Ratings)",
                labels={'x': 'Rating', 'y': 'Count'},
                color=rating_counts.values,
                color_continuous_scale='RdYlGn'
            )
            fig_rating.update_layout(showlegend=False)
            st.plotly_chart(fig_rating, use_container_width=True)
    
    with col_right:
        st.subheader("🏆 Competitive Position")
        
        # Calculate competitive position
        comp_df = calculate_competitive_position(filtered_df)
        
        # Display ranking
        for idx, row in comp_df.iterrows():
            rank = idx + 1
            product = row['Product']
            score = row['overall_avg']
            review_count = row['Review Count']
            
            is_dayforce = row['Is Dayforce']
            
            # Create card for each product
            color = "#d1ecf1" if is_dayforce else "#f8f9fa"
            border_color = "#0c5460" if is_dayforce else "#dee2e6"
            
            st.markdown(f"""
            <div style="background-color: {color}; padding: 15px; margin: 10px 0; 
                        border-radius: 5px; border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; color: #333;">#{rank} {product}</h3>
                        <p style="margin: 5px 0; color: #666;">{review_count} reviews</p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: {get_sentiment_color(score)};">{score:.2f}</h2>
                        <p style="margin: 0; font-size: 0.8em;">{get_sentiment_label(score)}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("📌 Key Insights")
        
        # Generate insights
        dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
        
        if len(dayforce_df) > 0:
            dayforce_avg = dayforce_df[dimensions].mean().mean()
            market_avg = filtered_df[dimensions].mean().mean()
            
            if dayforce_avg > market_avg:
                st.markdown(f"""
                <div class="insight-box">
                    <strong>✅ Market Leader</strong><br/>
                    Dayforce scores {(dayforce_avg - market_avg):.2f} points above market average
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="insight-box">
                    <strong>⚠️ Opportunity Gap</strong><br/>
                    Dayforce is {(market_avg - dayforce_avg):.2f} points behind market average
                </div>
                """, unsafe_allow_html=True)
            
            # Find strongest dimension
            strongest_dim = dayforce_df[dimensions].mean().idxmax()
            strongest_score = dayforce_df[strongest_dim].mean()
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>💪 Strongest Area</strong><br/>
                {dimension_labels[strongest_dim]}: {strongest_score:.2f}/5.0
            </div>
            """, unsafe_allow_html=True)
            
            # Find weakest dimension
            weakest_dim = dayforce_df[dimensions].mean().idxmin()
            weakest_score = dayforce_df[weakest_dim].mean()
            
            st.markdown(f"""
            <div class="action-box">
                <strong>🎯 Focus Area</strong><br/>
                {dimension_labels[weakest_dim]}: {weakest_score:.2f}/5.0<br/>
                <small>Requires strategic attention</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent trends
        if len(filtered_df) > 0:
            recent_reviews = filtered_df.nlargest(5, 'parsed_date')
            recent_avg = recent_reviews[dimensions].mean().mean()
            overall_avg = filtered_df[dimensions].mean().mean()
            
            trend_direction = "↗️ Improving" if recent_avg > overall_avg else "↘️ Declining"
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>📈 Recent Trend</strong><br/>
                {trend_direction}<br/>
                <small>Latest 5 reviews: {recent_avg:.2f} vs overall {overall_avg:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
