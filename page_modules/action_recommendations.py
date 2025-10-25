"""
Action Insights Page
Display customer insights and improvement opportunities from review analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import identify_improvement_opportunities, extract_pain_points, get_sentiment_color, data_source_badge

def render(filtered_df, full_df):
    """Render the Action Insights page"""
    
    st.header("🎬 Action Insights")
    st.markdown("**Customer insights and improvement opportunities for Dayforce**")
    st.caption(data_source_badge('ai_analysis'))
    
    # Display data scope indicator
    st.info("🎯 **Focus: Dayforce** - All insights are extracted from customer review AI analysis in the XLSX file")
    
    # Focus on Dayforce
    dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
    
    if len(dayforce_df) == 0:
        st.warning("⚠️ No Dayforce reviews in the current selection. Please adjust filters to include Dayforce data.")
        
        # Show general insights for all products
        st.subheader("📊 General Market Insights")
        
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product Capabilities (AI Sentiment)',
            'gtm': 'Go-to-Market (AI Sentiment)',
            'market_direction': 'Market Direction (AI Sentiment)',
            'implementation': 'Implementation (AI Sentiment)',
            'customer_experience': 'Customer Experience (AI Sentiment)'
        }
        
        # Market averages
        st.markdown("**Market Performance by Dimension:**")
        
        for dim in dimensions:
            avg_score = filtered_df[dim].mean()
            col = get_sentiment_color(avg_score)
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 10px; margin: 5px 0; 
                        border-radius: 5px; border-left: 4px solid {col};">
                <strong>{dimension_labels[dim]}</strong>: {avg_score:.2f}/5.0
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Priority Matrix
    st.subheader("🎯 Strategic Priority Matrix for Dayforce")
    st.markdown("*Identify where to focus Dayforce resources for maximum impact*")
    st.caption(data_source_badge('ai_analysis'))
    
    # Identify opportunities
    opportunities = identify_improvement_opportunities(filtered_df, 'Dayforce', threshold=4.0)
    
    if opportunities:
        # Display opportunities in priority order
        for i, opp in enumerate(opportunities, 1):
            dimension_labels = {
                'product': 'Product Capabilities (AI Sentiment)',
                'gtm': 'Go-to-Market Strategy (AI Sentiment)',
                'market_direction': 'Market Direction & Vision (AI Sentiment)',
                'implementation': 'Implementation & Onboarding (AI Sentiment)',
                'customer_experience': 'Customer Experience & Support (AI Sentiment)'
            }
            
            dim_label = dimension_labels.get(opp['dimension'], opp['dimension'])
            score = opp['avg_score']
            gap = opp['gap_from_target']
            
            # Determine urgency
            if gap > 0.5:
                urgency = "🔴 High Priority"
                bg_color = "#f8d7da"
                border_color = "#dc3545"
            elif gap > 0.3:
                urgency = "🟡 Medium Priority"
                bg_color = "#fff3cd"
                border_color = "#ffc107"
            else:
                urgency = "🟢 Low Priority"
                bg_color = "#d1ecf1"
                border_color = "#17a2b8"
            
            with st.expander(f"#{i} - {dim_label} - {urgency}", expanded=(i == 1)):
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 20px; margin: 10px 0; 
                            border-radius: 5px; border-left: 5px solid {border_color};">
                    <h3 style="margin-top: 0;">Current Status</h3>
                    <p><strong>Current Score:</strong> {score:.2f}/5.0</p>
                    <p><strong>Target Score:</strong> 4.0/5.0</p>
                    <p><strong>Gap:</strong> {gap:.2f} points</p>
                    <p><strong>Affected Reviews:</strong> {opp['affected_reviews']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_pain, col_topic = st.columns(2)
                
                with col_pain:
                    st.markdown("**🔍 Top Pain Points:**")
                    if opp['top_pain_points']:
                        for pain, count in opp['top_pain_points']:
                            if pain and len(pain) > 5:
                                st.markdown(f"- {pain[:200]}... ({count} mentions)")
                    else:
                        st.info("No specific pain points identified")
                
                with col_topic:
                    st.markdown("**📌 Related Topics:**")
                    if opp['top_topics']:
                        for topic, count in opp['top_topics']:
                            st.markdown(f"- {topic} ({count} mentions)")
                    else:
                        st.info("No specific topics identified")
                
                # Show insights from review_insights column (XLSX - AI Analysis)
                st.markdown("### 💡 Key Insights")
                st.caption(data_source_badge('ai_analysis'))
                
                # Get insights for this dimension from low-performing reviews
                low_reviews = dayforce_df[dayforce_df[opp['dimension']] < 4.0]
                if len(low_reviews) > 0 and 'insights_list' in low_reviews.columns:
                    all_insights = []
                    for idx, row in low_reviews.iterrows():
                        insights = row.get('insights_list')
                        if isinstance(insights, (list, tuple)) and len(insights) > 0:
                            all_insights.extend(insights)
                    
                    if all_insights:
                        # Show top insights (deduplicated)
                        unique_insights = list(set(all_insights))[:5]
                        for insight in unique_insights:
                            if insight and len(insight.strip()) > 10:
                                st.markdown(f"""
                                <div style="background-color: #d1ecf1; padding: 15px; margin: 10px 0; 
                                            border-radius: 5px; border-left: 4px solid #0c5460;">
                                    {insight}
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No specific insights available for this dimension")
                else:
                    st.info("No specific insights available for this dimension")
    else:
        st.success("🎉 Excellent! Dayforce is performing above target (4.0) in all dimensions!")
        
        # Show what's working well
        st.subheader("✨ What's Working Well")
        st.caption(data_source_badge('ai_analysis'))
        
        dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
        dimension_labels = {
            'product': 'Product Capabilities (AI)',
            'gtm': 'Go-to-Market (AI)',
            'market_direction': 'Market Direction (AI)',
            'implementation': 'Implementation (AI)',
            'customer_experience': 'Customer Experience (AI)'
        }
        
        for dim in dimensions:
            score = dayforce_df[dim].mean()
            st.markdown(f"**{dimension_labels[dim]}**: {score:.2f}/5.0 ✅")
    
    st.markdown("---")
    
    # Pain Points Analysis
    st.subheader("😣 Customer Pain Points")
    st.markdown("*What are customers struggling with?*")
    st.caption(data_source_badge('ai_analysis'))
    
    pain_points = extract_pain_points(filtered_df, 'Dayforce')
    
    if pain_points:
        # Group by severity (based on overall rating)
        high_severity = [p for p in pain_points if p['overall_rating'] <= 3]
        medium_severity = [p for p in pain_points if 3 < p['overall_rating'] < 4]
        low_severity = [p for p in pain_points if p['overall_rating'] >= 4]
        
        col_sev1, col_sev2, col_sev3 = st.columns(3)
        
        with col_sev1:
            st.metric("🔴 High Severity", len(high_severity))
            st.caption("From reviews rated ≤3")
        
        with col_sev2:
            st.metric("🟡 Medium Severity", len(medium_severity))
            st.caption("From reviews rated 3-4")
        
        with col_sev3:
            st.metric("🟢 Low Severity", len(low_severity))
            st.caption("From reviews rated ≥4")
        
        # Display high severity pain points
        if high_severity:
            st.markdown("### 🔴 High Severity Pain Points")
            for i, pain in enumerate(high_severity[:5], 1):
                st.markdown(f"""
                <div style="background-color: #f8d7da; padding: 15px; margin: 10px 0; 
                            border-radius: 5px; border-left: 4px solid #dc3545;">
                    <strong>#{i}</strong> {pain['pain_point'][:300]}<br/>
                    <small>Review date: {pain['date'].strftime('%Y-%m-%d') if pd.notna(pain['date']) else 'N/A'} | 
                    Rating: {pain['overall_rating']}/5</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No pain points extracted from current selection")
    
    st.markdown("---")
    
    # Trend Analysis & Predictions
    st.subheader("📈 Trend Analysis")
    st.markdown("*Are things getting better or worse?*")
    st.caption(data_source_badge('ai_analysis'))
    
    if len(dayforce_df) >= 3:
        # Sort by date
        trend_df = dayforce_df.sort_values('parsed_date')
        
        # Get date range
        min_date = trend_df['parsed_date'].min()
        max_date = trend_df['parsed_date'].max()
        mid_date = min_date + (max_date - min_date) / 2
        
        # Date range filters
        st.markdown("**Define Time Periods for Comparison:**")
        col_early, col_recent = st.columns(2)
        
        with col_early:
            st.markdown("**📅 Earlier Period**")
            early_start = st.date_input(
                "Start Date",
                value=min_date.date(),
                min_value=min_date.date(),
                max_value=max_date.date(),
                key='trend_early_start'
            )
            early_end = st.date_input(
                "End Date",
                value=mid_date.date(),
                min_value=min_date.date(),
                max_value=max_date.date(),
                key='trend_early_end'
            )
        
        with col_recent:
            st.markdown("**📅 Recent Period**")
            recent_start = st.date_input(
                "Start Date",
                value=(mid_date + pd.Timedelta(days=1)).date(),
                min_value=min_date.date(),
                max_value=max_date.date(),
                key='trend_recent_start'
            )
            recent_end = st.date_input(
                "End Date",
                value=max_date.date(),
                min_value=min_date.date(),
                max_value=max_date.date(),
                key='trend_recent_end'
            )
        
        # Filter data based on selected periods
        first_half = trend_df[
            (trend_df['parsed_date'].dt.date >= early_start) & 
            (trend_df['parsed_date'].dt.date <= early_end)
        ]
        second_half = trend_df[
            (trend_df['parsed_date'].dt.date >= recent_start) & 
            (trend_df['parsed_date'].dt.date <= recent_end)
        ]
        
        # Display period info
        st.info(f"**Earlier Period:** {early_start.strftime('%b %d, %Y')} to {early_end.strftime('%b %d, %Y')} ({len(first_half)} reviews) | **Recent Period:** {recent_start.strftime('%b %d, %Y')} to {recent_end.strftime('%b %d, %Y')} ({len(second_half)} reviews)")
        
        if len(first_half) > 0 and len(second_half) > 0:
            dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
            dimension_labels = {
                'product': 'Product (AI)',
                'gtm': 'GTM (AI)',
                'market_direction': 'Market Dir. (AI)',
                'implementation': 'Implementation (AI)',
                'customer_experience': 'Cust. Exp. (AI)'
            }
            
            trend_data = []
            for dim in dimensions:
                first_avg = first_half[dim].mean()
                second_avg = second_half[dim].mean()
                change = second_avg - first_avg
                
                trend_data.append({
                    'Dimension': dimension_labels[dim],
                    'Earlier Period': first_avg,
                    'Recent Period': second_avg,
                    'Change': change,
                    'Trend': '📈 Improving' if change > 0.1 else ('📉 Declining' if change < -0.1 else '➡️ Stable')
                })
            
            trend_comparison_df = pd.DataFrame(trend_data)
            
            # Visualize trends
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name=f'Earlier ({early_start.strftime("%b %Y")} - {early_end.strftime("%b %Y")})',
                x=trend_comparison_df['Dimension'],
                y=trend_comparison_df['Earlier Period'],
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Bar(
                name=f'Recent ({recent_start.strftime("%b %Y")} - {recent_end.strftime("%b %Y")})',
                x=trend_comparison_df['Dimension'],
                y=trend_comparison_df['Recent Period'],
                marker_color='darkblue'
            ))
            
            fig.update_layout(
                barmode='group',
                yaxis_title="AI Sentiment Score (1-5)",
                yaxis=dict(range=[0, 5.5]),
                height=400,
                title="AI Sentiment Trends: Earlier vs Recent Period"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show trend table
            st.dataframe(
                trend_comparison_df[['Dimension', 'Earlier Period', 'Recent Period', 'Change', 'Trend']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("⚠️ Not enough reviews in one or both periods. Adjust the date ranges to include more reviews.")
    else:
        st.info("Not enough Dayforce reviews to perform trend analysis")
    
    st.markdown("---")
    
    # Customer Insights from Reviews
    st.subheader("💡 Customer Insights")
    st.markdown("*What customers are saying about Dayforce*")
    st.caption(data_source_badge('ai_analysis'))
    
    # Get all insights from Dayforce reviews
    if 'insights_list' in dayforce_df.columns:
        all_insights = []
        for idx, row in dayforce_df.iterrows():
            insights = row.get('insights_list')
            if isinstance(insights, (list, tuple)) and len(insights) > 0:
                for insight in insights:
                    if insight and len(insight.strip()) > 10:
                        all_insights.append({
                            'insight': insight,
                            'rating': row['Overall User Rating'],
                            'date': row.get('parsed_date', row.get('Review Date'))
                        })
        
        if all_insights:
            # Group by sentiment (positive vs negative)
            positive_insights = [i for i in all_insights if i['rating'] >= 4]
            improvement_insights = [i for i in all_insights if i['rating'] < 4]
            
            col_pos, col_imp = st.columns(2)
            
            with col_pos:
                st.markdown("### ✅ Positive Feedback")
                if positive_insights:
                    for i, item in enumerate(positive_insights[:5], 1):
                        st.markdown(f"""
                        <div style="background-color: #d4edda; padding: 12px; margin: 8px 0; 
                                    border-radius: 5px; border-left: 4px solid #28a745;">
                            <small>Rating: {item['rating']}/5</small><br/>
                            {item['insight']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No positive insights found")
            
            with col_imp:
                st.markdown("### 🔧 Areas for Improvement")
                if improvement_insights:
                    for i, item in enumerate(improvement_insights[:5], 1):
                        st.markdown(f"""
                        <div style="background-color: #fff3cd; padding: 12px; margin: 8px 0; 
                                    border-radius: 5px; border-left: 4px solid #ffc107;">
                            <small>Rating: {item['rating']}/5</small><br/>
                            {item['insight']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No improvement insights found")
        else:
            st.info("No insights available in current selection")
    else:
        st.warning("Insights column not found in data")

