"""
Action Insights Page
Display customer insights and improvement opportunities from multi-source analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import identify_improvement_opportunities, extract_pain_points, get_sentiment_color, data_source_badge, get_source_label, get_source_icon
import feedback_system


def _clean_text(value, default=""):
    """Return a clean string, avoiding NaN placeholders."""
    if isinstance(value, str):
        text = value.strip()
        return text if text else default
    if pd.notna(value):
        text = str(value).strip()
        if text and text.lower() != "nan":
            return text
    return default


def _safe_extract_text(row, keys, default):
    """Try multiple column keys to provide meaningful fallback copy."""
    for key in keys:
        if key in row:
            cleaned = _clean_text(row.get(key), default)
            if cleaned and cleaned != default:
                return cleaned
    return default

def render(filtered_df, full_df):
    """Render the Action Insights page with multi-source intelligence"""
    
    # Page header with inline feedback buttons
    col1, col2, col3 = st.columns([8, 1.2, 1.2])
    with col1:
        st.header("🎬 Action Insights")
    with col2:
        if st.button("💬 Feedback", key="feedback_btn_action", type="primary"):
            feedback_system.show_feedback_modal("Action Insights", "Action Insights", "", "")
    with col3:
        username = feedback_system.auth.get_current_user()
        is_admin = feedback_system.auth.is_admin()
        feedback_count = len(feedback_system.get_section_feedback("Action Insights", None if is_admin else username))
        if is_admin:
            view_label = f"All Feedbacks ({feedback_count})" if feedback_count > 0 else "All Feedbacks (0)"
        else:
            view_label = f"My Feedbacks ({feedback_count})" if feedback_count > 0 else "My Feedbacks (0)"
        if st.button(view_label, key="view_feedback_btn_action", type="primary", help="View feedback"):
            feedback_system.show_feedback_viewer_modal("Action Insights")
    
    st.markdown("**Strategic improvement opportunities synthesized from multiple intelligence sources**")
    
    # Focus on Dayforce
    dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
    
    if len(dayforce_df) == 0:
        st.warning("⚠️ No Dayforce insights in the current selection. Please adjust filters to include Dayforce data.")
        return
    
    # Show source breakdown for Dayforce insights
    sources_in_dayforce = dayforce_df['source_type'].value_counts()
    has_multiple_sources = len(sources_in_dayforce) > 1
    
    if has_multiple_sources:
        source_breakdown = []
        for source_type, count in sources_in_dayforce.items():
            icon = get_source_icon(source_type)
            label = get_source_label(source_type)
            source_breakdown.append(f"{icon} {count} {label}")
        
        st.info(f"🎯 **Multi-Source Synthesis**: {len(dayforce_df)} Dayforce insights | {' + '.join(source_breakdown)}")
    else:
        source_type = sources_in_dayforce.index[0]
        icon = get_source_icon(source_type)
        label = get_source_label(source_type)
        st.info(f"{icon} **{label}**: Analyzing {len(dayforce_df)} Dayforce insights")
    
    # Priority Matrix
    st.subheader("🎯 Strategic Priority Matrix for Dayforce")
    st.markdown("*Identify where to focus Dayforce resources for maximum impact*")
    
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
                
                # Show sub-dimensions and topics side by side
                col_subdim, col_topic = st.columns(2)
                
                with col_subdim:
                    st.markdown("**🔍 Sub-Dimension Scores:**")
                    sub_dims = opp.get('sub_dimension_scores', {})
                    if sub_dims:
                        # Sort by score to show weakest first
                        sorted_subdims = sorted(sub_dims.items(), key=lambda x: x[1] if pd.notna(x[1]) else 0)
                        for sub_dim, score in sorted_subdims[:5]:
                            if pd.notna(score):
                                nice_name = sub_dim.replace('_', ' ').title()
                                color = '🔴' if score < 3.5 else '🟡' if score < 4.0 else '🟢'
                                st.markdown(f"{color} {nice_name}: {score:.2f}/5")
                    else:
                        st.info("No sub-dimension data available")
                
                with col_topic:
                    st.markdown("**📌 Related Topics:**")
                    if opp.get('top_topics'):
                        for topic, count in opp['top_topics']:
                            st.markdown(f"- {topic} ({count} mentions)")
                    else:
                        st.info("No specific topics identified")
                
                # Show sub-dimension breakdown
                st.markdown("### � Sub-Dimension Analysis")
                # st.caption(data_source_badge('ai_analysis'))
                
                # Get sub-dimensions for this opportunity
                sub_dims = opp.get('sub_dimension_scores', {})
                if sub_dims:
                    st.markdown("**Performance breakdown:**")
                    for sub_dim, score in sorted(sub_dims.items(), key=lambda x: x[1]):
                        if pd.notna(score):
                            # Format sub-dimension name nicely
                            nice_name = sub_dim.replace('_', ' ').title()
                            color = '#28a745' if score >= 4 else '#ffc107' if score >= 3.5 else '#dc3545'
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 10px; margin: 5px 0; 
                                        border-radius: 5px; border-left: 4px solid {color};">
                                <strong>{nice_name}</strong>: {score:.2f}/5.0
                            </div>
                            """, unsafe_allow_html=True)
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
                # Format the pain point description from sub-dimensions
                top_issues = list(pain['low_sub_dimensions'].items())[:2]
                issues_str = ', '.join([f"{dim} ({score:.1f})" for dim, score in top_issues])
                
                raw_headline = pain.get('headline') if isinstance(pain, dict) else None
                headline = _clean_text(raw_headline, 'Critical Issue')
                if headline.lower() == 'no headline':
                    headline = 'Critical Issue'
                date_str = pain['date'].strftime('%Y-%m-%d') if pd.notna(pain['date']) else 'N/A'
                
                st.markdown(f"""
                <div style="background-color: #f8d7da; padding: 15px; margin: 10px 0; 
                            border-radius: 5px; border-left: 4px solid #dc3545;">
                    <strong>#{i}. {headline}</strong><br/>
                    Issues: {issues_str}<br/>
                    <small>Review date: {date_str} | 
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
    
