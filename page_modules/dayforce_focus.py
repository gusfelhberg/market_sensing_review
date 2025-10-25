"""
Dayforce Focus Page
Dayforce-centric analysis with competitive context
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_sentiment_color, get_sentiment_label, extract_pain_points, data_source_badge
from collections import Counter

def render(filtered_df, full_df):
    """Render the Dayforce Focus page"""
    
    st.header("🎯 Dayforce Strategic Intelligence")
    st.markdown("**Dayforce performance with competitive context for strategic decision-making**")
    
    # Get Dayforce data
    dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
    competitors_df = filtered_df[filtered_df['Product'] != 'Dayforce']
    
    if len(dayforce_df) == 0:
        st.warning("⚠️ No Dayforce reviews in current selection. Adjust filters to include Dayforce data.")
        return
    
    # Key Performance Indicators
    st.subheader("📊 Dayforce Performance Dashboard")
    st.caption(data_source_badge('ai_analysis'))
    st.info("**AI Sentiment Scores:** The dimension scores below are AI-generated sentiment analysis (1-5) from review text, complementing the Overall User Rating.")
    
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': 'Product (AI)',
        'gtm': 'GTM (AI)',
        'market_direction': 'Market Direction (AI)',
        'implementation': 'Implementation (AI)',
        'customer_experience': 'Customer Exp. (AI)'
    }
    
    # Create 5 columns for dimension comparison
    cols = st.columns(5)
    
    for i, dim in enumerate(dimensions):
        with cols[i]:
            dayforce_score = dayforce_df[dim].mean()
            market_avg = competitors_df[dim].mean() if len(competitors_df) > 0 else 0
            gap = dayforce_score - market_avg
            
            # Determine if we're leading or lagging
            if gap > 0.2:
                status = "🏆 Leading"
                delta_color = "normal"
            elif gap > 0:
                status = "✅ Above Market"
                delta_color = "normal"
            elif gap > -0.2:
                status = "⚡ At Par"
                delta_color = "off"
            else:
                status = "🎯 Opportunity"
                delta_color = "inverse"
            
            st.metric(
                label=dimension_labels[dim],
                value=f"{dayforce_score:.2f}",
                delta=f"{gap:+.2f} vs market",
                delta_color=delta_color
            )
            st.caption(status)
    
    st.markdown("---")
    
    # Two column layout
    col_main, col_sidebar = st.columns([2, 1])
    
    with col_main:
        # Competitive positioning chart
        st.subheader("📈 Dayforce vs Competition")
        st.caption(data_source_badge('ai_analysis'))
        
        # Calculate averages by product
        product_scores = []
        for product in filtered_df['Product'].unique():
            product_df = filtered_df[filtered_df['Product'] == product]
            avg_scores = {}
            for dim in dimensions:
                avg_scores[dim] = product_df[dim].mean()
            
            product_scores.append({
                'Product': product,
                'Is Dayforce': product == 'Dayforce',
                **avg_scores
            })
        
        comp_df = pd.DataFrame(product_scores)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        for dim in dimensions:
            # Separate Dayforce from competitors
            dayforce_row = comp_df[comp_df['Is Dayforce']]
            competitor_rows = comp_df[~comp_df['Is Dayforce']].sort_values(dim, ascending=False)
            
            all_products = list(competitor_rows['Product']) + [''] + list(dayforce_row['Product'])
            all_scores = list(competitor_rows[dim]) + [None] + list(dayforce_row[dim])
            
            colors = ['lightgray'] * len(competitor_rows) + ['white'] + ['#0c5460']
            
            fig.add_trace(go.Bar(
                name=dimension_labels[dim],
                x=all_products,
                y=all_scores,
                marker_color=colors if dim == dimensions[0] else None,
                showlegend=True
            ))
        
        fig.update_layout(
            title="AI Sentiment Performance Across All Dimensions (Dayforce Highlighted)",
            yaxis_title="AI Sentiment Score (1-5)",
            xaxis_title="Product",
            barmode='group',
            yaxis=dict(range=[0, 5.5]),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Where We Win vs Where We Lose
        st.subheader("💪 Competitive Advantages & Gaps")
        st.caption(data_source_badge('ai_analysis'))
        
        col_win, col_lose = st.columns(2)
        
        advantages = []
        gaps = []
        
        for dim in dimensions:
            dayforce_score = dayforce_df[dim].mean()
            
            # Find best competitor in this dimension
            comp_scores = []
            for product in competitors_df['Product'].unique():
                prod_df = competitors_df[competitors_df['Product'] == product]
                comp_scores.append({
                    'product': product,
                    'score': prod_df[dim].mean()
                })
            
            if comp_scores:
                best_competitor = max(comp_scores, key=lambda x: x['score'])
                gap = dayforce_score - best_competitor['score']
                
                if gap > 0:
                    advantages.append({
                        'dimension': dimension_labels[dim],
                        'dayforce': dayforce_score,
                        'competitor': best_competitor['product'],
                        'comp_score': best_competitor['score'],
                        'advantage': gap
                    })
                else:
                    gaps.append({
                        'dimension': dimension_labels[dim],
                        'dayforce': dayforce_score,
                        'competitor': best_competitor['product'],
                        'comp_score': best_competitor['score'],
                        'gap': abs(gap)
                    })
        
        with col_win:
            st.markdown("### ✅ Where We Lead")
            
            if advantages:
                advantages.sort(key=lambda x: x['advantage'], reverse=True)
                for adv in advantages:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid #28a745;">
                        <strong>{adv['dimension']}</strong><br/>
                        Dayforce: {adv['dayforce']:.2f} | {adv['competitor']}: {adv['comp_score']:.2f}<br/>
                        <small>Advantage: +{adv['advantage']:.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No clear competitive advantages in current selection")
        
        with col_lose:
            st.markdown("### 🎯 Where We Trail")
            
            if gaps:
                gaps.sort(key=lambda x: x['gap'], reverse=True)
                for gap_item in gaps:
                    urgency_color = "#dc3545" if gap_item['gap'] > 0.3 else "#ffc107"
                    urgency_bg = "#f8d7da" if gap_item['gap'] > 0.3 else "#fff3cd"
                    
                    st.markdown(f"""
                    <div style="background-color: {urgency_bg}; padding: 12px; margin: 8px 0; 
                                border-radius: 5px; border-left: 4px solid {urgency_color};">
                        <strong>{gap_item['dimension']}</strong><br/>
                        Dayforce: {gap_item['dayforce']:.2f} | {gap_item['competitor']}: {gap_item['comp_score']:.2f}<br/>
                        <small>Gap: -{gap_item['gap']:.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Leading in all dimensions!")
    
    with col_sidebar:
        st.subheader("📌 Key Insights")
        st.caption(data_source_badge('ai_analysis'))
        
        # Overall position
        dayforce_overall = dayforce_df[dimensions].mean().mean()
        market_overall = competitors_df[dimensions].mean().mean() if len(competitors_df) > 0 else 0
        
        if dayforce_overall > market_overall:
            st.success(f"**Overall Leader**\n\n{dayforce_overall:.2f} vs Market {market_overall:.2f}")
        else:
            st.warning(f"**Below Market**\n\n{dayforce_overall:.2f} vs Market {market_overall:.2f}")
        
        st.markdown("---")
        
        # Review volume
        st.metric("Dayforce Reviews", len(dayforce_df))
        st.metric("Competitor Reviews", len(competitors_df))
        
        # Voice share
        voice_share = len(dayforce_df) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("Voice Share", f"{voice_share:.1f}%")
        
        st.markdown("---")
        
        # Recent trend
        if len(dayforce_df) >= 5:
            recent = dayforce_df.nlargest(5, 'parsed_date')
            older = dayforce_df.nsmallest(5, 'parsed_date')
            
            recent_avg = recent[dimensions].mean().mean()
            older_avg = older[dimensions].mean().mean()
            trend = recent_avg - older_avg
            
            if trend > 0.1:
                st.success(f"**📈 Improving**\n\nRecent: {recent_avg:.2f}\nEarlier: {older_avg:.2f}")
            elif trend < -0.1:
                st.warning(f"**📉 Declining**\n\nRecent: {recent_avg:.2f}\nEarlier: {older_avg:.2f}")
            else:
                st.info(f"**➡️ Stable**\n\nRecent: {recent_avg:.2f}\nEarlier: {older_avg:.2f}")
    
    st.markdown("---")
    
    # Dayforce-specific pain points and strengths
    st.subheader("🔍 Deep Dive: Dayforce Feedback Analysis")
    st.caption(data_source_badge('ai_analysis'))
    
    tab1, tab2, tab3 = st.tabs(["Pain Points", "Strengths", "Competitive Gaps"])
    
    with tab1:
        st.markdown("### 😣 Customer Pain Points")
        st.markdown("*What are Dayforce customers struggling with?*")
        
        pain_points = extract_pain_points(dayforce_df, 'Dayforce')
        
        if pain_points:
            # Categorize by severity
            high_sev = [p for p in pain_points if p['overall_rating'] <= 3]
            med_sev = [p for p in pain_points if 3 < p['overall_rating'] < 4]
            low_sev = [p for p in pain_points if p['overall_rating'] >= 4]
            
            col_sev1, col_sev2, col_sev3 = st.columns(3)
            with col_sev1:
                st.metric("🔴 Critical", len(high_sev), help="From reviews rated ≤3")
            with col_sev2:
                st.metric("🟡 Moderate", len(med_sev), help="From reviews rated 3-4")
            with col_sev3:
                st.metric("🟢 Minor", len(low_sev), help="From reviews rated ≥4")
            
            # Show critical pain points
            if high_sev:
                st.markdown("#### 🔴 Critical Issues (Immediate Attention Required)")
                for i, pain in enumerate(high_sev[:5], 1):
                    date_str = pain['date'].strftime('%Y-%m-%d') if pd.notna(pain['date']) else 'N/A'
                    st.markdown(f"""
                    <div style="background-color: #f8d7da; padding: 15px; margin: 10px 0; 
                                border-radius: 5px; border-left: 4px solid #dc3545;">
                        <strong>#{i}.</strong> {pain['pain_point'][:250]}<br/>
                        <small>📅 {date_str} | ⭐ {pain['overall_rating']}/5</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show moderate pain points
            if med_sev:
                st.markdown("#### 🟡 Moderate Issues")
                for i, pain in enumerate(med_sev[:3], 1):
                    date_str = pain['date'].strftime('%Y-%m-%d') if pd.notna(pain['date']) else 'N/A'
                    st.markdown(f"**{i}.** {pain['pain_point'][:200]}... *({date_str}, Rating: {pain['overall_rating']}/5)*")
        else:
            st.info("No pain points found in current selection")
    
    with tab2:
        st.markdown("### ✨ What Customers Love About Dayforce")
        
        # Extract positive comments
        positive_reviews = dayforce_df[dayforce_df['Overall User Rating'] >= 4]
        
        if len(positive_reviews) > 0:
            # Extract topics from positive reviews
            topics = []
            for topics_list in positive_reviews['topics_list']:
                topics.extend(topics_list)
            
            topic_counts = Counter(topics)
            top_topics = topic_counts.most_common(10)
            
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("**Most Praised Features:**")
                for topic, count in top_topics[:5]:
                    pct = count / len(positive_reviews) * 100
                    st.markdown(f"- **{topic}** ({count} mentions, {pct:.0f}%)")
            
            with col_top2:
                # Dimension strengths
                st.markdown("**Strongest Dimensions:**")
                dim_scores = positive_reviews[dimensions].mean().sort_values(ascending=False)
                for dim, score in dim_scores.items():
                    st.markdown(f"- **{dimension_labels[dim]}**: {score:.2f}/5.0")
            
            st.markdown("---")
            st.markdown("**Sample Positive Feedback:**")
            
            for idx, row in positive_reviews.nlargest(3, 'Overall User Rating').iterrows():
                st.markdown(f"""
                <div style="background-color: #d4edda; padding: 15px; margin: 10px 0; 
                            border-radius: 5px; border-left: 4px solid #28a745;">
                    <strong>"{row['Headline']}"</strong><br/>
                    {row['Overall Comment'][:300]}...<br/>
                    <small>⭐ {row['Overall User Rating']}/5 | {row['Reviewer Role ']} | {row['Reviewer Industry']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No highly-rated reviews in current selection")
    
    with tab3:
        st.markdown("### 🥊 Competitive Gap Analysis")
        st.markdown("*What are competitors doing better?*")
        
        # For each gap, show what competitors are doing well
        if gaps:
            for gap_item in gaps:
                dim = [k for k, v in dimension_labels.items() if v == gap_item['dimension']][0]
                competitor = gap_item['competitor']
                
                with st.expander(f"{gap_item['dimension']}: {competitor} leads by {gap_item['gap']:.2f} points"):
                    # Get competitor reviews for this dimension
                    comp_reviews = competitors_df[
                        (competitors_df['Product'] == competitor) &
                        (competitors_df[dim] >= 4)
                    ]
                    
                    if len(comp_reviews) > 0:
                        st.markdown(f"**Why {competitor} excels in {gap_item['dimension']}:**")
                        
                        # Sample high-scoring competitor reviews
                        for idx, row in comp_reviews.nlargest(2, dim).iterrows():
                            st.markdown(f"""
                            <div style="background-color: #fff3cd; padding: 12px; margin: 8px 0; 
                                        border-radius: 5px; border-left: 3px solid #ffc107;">
                                <strong>{row['Headline']}</strong><br/>
                                {row['Overall Comment'][:200]}...<br/>
                                <small>{dim.replace('_', ' ').title()} Score: {row[dim]}/5</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("**Action Items:**")
                        st.markdown(generate_gap_closure_recommendations(gap_item['dimension'], competitor))
                    else:
                        st.info(f"No detailed feedback available for {competitor} in this dimension")
        else:
            st.success("🎉 Dayforce leads in all dimensions!")
    
    st.markdown("---")
    
    # Reviewer segments
    st.subheader("👥 Dayforce Customer Segments")
    
    col_seg1, col_seg2 = st.columns(2)
    
    with col_seg1:
        # By industry
        st.markdown("**Performance by Industry:**")
        industry_perf = dayforce_df.groupby('Reviewer Industry')[dimensions].mean().mean(axis=1).sort_values(ascending=False)
        
        fig = px.bar(
            x=industry_perf.values,
            y=industry_perf.index,
            orientation='h',
            title="Average Sentiment by Industry",
            labels={'x': 'Avg Score', 'y': 'Industry'},
            color=industry_perf.values,
            color_continuous_scale='RdYlGn',
            range_color=[3, 5]
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_seg2:
        # By company size
        st.markdown("**Performance by Company Size:**")
        size_perf = dayforce_df.groupby('Reviewer Firm Size')[dimensions].mean().mean(axis=1).sort_values(ascending=False)
        
        fig = px.bar(
            x=size_perf.values,
            y=size_perf.index,
            orientation='h',
            title="Average Sentiment by Company Size",
            labels={'x': 'Avg Score', 'y': 'Company Size'},
            color=size_perf.values,
            color_continuous_scale='RdYlGn',
            range_color=[3, 5]
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def generate_gap_closure_recommendations(dimension, competitor):
    """Generate recommendations for closing competitive gaps"""
    
    recommendations = {
        'Product': f"""
        - Conduct feature-by-feature comparison with {competitor}
        - Survey existing customers on must-have features
        - Accelerate product roadmap for identified gaps
        - Consider strategic acquisitions or partnerships
        """,
        'GTM': f"""
        - Analyze {competitor}'s sales and marketing materials
        - Revise value proposition and positioning
        - Enhance sales enablement and training
        - Develop industry-specific messaging and case studies
        """,
        'Market Direction': f"""
        - Increase visibility of product vision and roadmap
        - Enhance executive thought leadership presence
        - Communicate innovation strategy more effectively
        - Host customer advisory boards for strategic input
        """,
        'Implementation': f"""
        - Benchmark implementation methodology against {competitor}
        - Invest in implementation team training and certification
        - Develop standardized playbooks for faster deployment
        - Enhance project management and customer communication
        """,
        'Customer Exp.': f"""
        - Study {competitor}'s support model and response times
        - Invest in customer success infrastructure
        - Implement proactive monitoring and outreach
        - Enhance self-service tools and knowledge base
        """
    }
    
    return recommendations.get(dimension, "Conduct detailed competitive analysis and customer research")
