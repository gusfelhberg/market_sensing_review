"""
Dayforce Focus Page
Dayforce-centric analysis with competitive context and multi-source awareness
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_sentiment_color, get_sentiment_label, extract_pain_points, data_source_badge, parse_lessons_learned, get_source_label, get_source_icon, get_source_type_config
from collections import Counter

def render(filtered_df, full_df):
    """Render the Dayforce Focus page"""
    
    st.header("🎯 Dayforce Strategic Intelligence")
    st.markdown("**Dayforce performance with competitive context and multi-source insights**")
    
    # Get Dayforce data
    dayforce_df = filtered_df[filtered_df['Product'] == 'Dayforce']
    competitors_df = filtered_df[filtered_df['Product'] != 'Dayforce']
    
    if len(dayforce_df) == 0:
        st.warning("⚠️ No Dayforce insights in current selection. Adjust filters to include Dayforce data.")
        return
    
    # Show source breakdown
    sources_in_dayforce = dayforce_df['source_type'].value_counts()
    has_multiple_sources = len(sources_in_dayforce) > 1
    
    if has_multiple_sources:
        source_breakdown = []
        for source_type, count in sources_in_dayforce.items():
            icon = get_source_icon(source_type)
            label = get_source_label(source_type)
            source_breakdown.append(f"{icon} {count} {label}")
        
        st.info(f"📊 **Multi-Source Analysis**: {len(dayforce_df)} Dayforce insights | {' + '.join(source_breakdown)}")
    else:
        source_type = sources_in_dayforce.index[0]
        icon = get_source_icon(source_type)
        label = get_source_label(source_type)
        st.info(f"{icon} **{label}**: {len(dayforce_df)} Dayforce insights")
    
    # Key Performance Indicators
    st.subheader("📊 Dayforce Performance Dashboard")
    st.caption("Combined AI sentiment scores across all sources")
    
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': 'Product',
        'gtm': 'GTM',
        'market_direction': 'Market Direction',
        'implementation': 'Implementation',
        'customer_experience': 'Customer Exp.'
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
        
        # Add view selector
        view_mode = st.radio(
            "View by:",
            options=["By Dimension", "By Product"],
            horizontal=True,
            key='dayforce_chart_view'
        )
        
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
        
        # Create grouped bar chart with consistent colors
        from utils import get_dimension_color, get_product_color
        fig = go.Figure()
        
        if view_mode == "By Dimension":
            # Group by dimension - each dimension shows all products
            for dim in dimensions:
                fig.add_trace(go.Bar(
                    name=dimension_labels[dim],
                    x=comp_df['Product'],
                    y=comp_df[dim],
                    marker_color=get_dimension_color(dim),
                    showlegend=True
                ))
            
            fig.update_layout(
                title="AI Sentiment Performance - Grouped by Dimension",
                xaxis_title="Product"
            )
        else:
            # Group by product - each product shows all dimensions
            # Use distinct product colors for legend/identification
            for idx, row in comp_df.iterrows():
                product = row['Product']
                scores = [row[dim] for dim in dimensions]
                
                fig.add_trace(go.Bar(
                    name=product,
                    x=[dimension_labels[dim] for dim in dimensions],
                    y=scores,
                    marker_color=get_product_color(product),
                    showlegend=True,
                    hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Score: %{y:.2f}<extra></extra>'
                ))
            
            fig.update_layout(
                title="AI Sentiment Performance - Grouped by Product",
                xaxis_title="Dimension"
            )
        
        fig.update_layout(
            yaxis_title="AI Sentiment Score (1-5)",
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
    
    tab1, tab2, tab3 = st.tabs(["Customer Pain Points", "Customer Strengths", "Competitive Intelligence"])
    
    with tab1:
        st.markdown("### 😣 Critical Issues from Customer Reviews")
        st.markdown("*Each issue is linked to a specific customer review with actionable details*")
        
        pain_points = extract_pain_points(dayforce_df, 'Dayforce')
        
        if pain_points:
            # Categorize by severity
            critical = [p for p in pain_points if p['overall_rating'] <= 3]
            moderate = [p for p in pain_points if 3 < p['overall_rating'] < 4]
            minor = [p for p in pain_points if p['overall_rating'] >= 4]
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔴 Critical", len(critical), help="Reviews rated ≤3.0")
            with col2:
                st.metric("🟡 Moderate", len(moderate), help="Reviews rated 3.0-4.0")
            with col3:
                st.metric("🟢 Minor", len(minor), help="Reviews rated ≥4.0")
            with col4:
                # Most common failing sub-dimension
                all_failing_dims = []
                for p in pain_points:
                    all_failing_dims.extend(p['low_sub_dimensions'].keys())
                if all_failing_dims:
                    most_common = Counter(all_failing_dims).most_common(1)[0]
                    st.metric("Top Issue", most_common[0], help=f"Mentioned in {most_common[1]} reviews")
            
            st.markdown("---")
            
            # Critical Issues - Show full details
            if critical:
                st.markdown("#### 🔴 Critical Issues (Reviews rated ≤3.0)")
                st.markdown("*These require immediate attention as they come from highly dissatisfied customers*")
                
                for i, pain in enumerate(critical, 1):
                    date_str = pain['date'].strftime('%b %d, %Y') if pd.notna(pain['date']) else 'Date N/A'
                    headline = pain['headline'] if pd.notna(pain['headline']) and str(pain['headline']).strip() else "Critical Review"
                    
                    with st.expander(f"🔴 #{i}. {headline} (Rating: {pain['overall_rating']}/5 | {date_str})"):
                        # Review metadata
                        col_meta1, col_meta2 = st.columns(2)
                        with col_meta1:
                            st.markdown(f"""
                            **Reviewer Profile:**
                            - Role: {pain['reviewer_role'] if pd.notna(pain['reviewer_role']) else 'N/A'}
                            - Industry: {pain['reviewer_industry'] if pd.notna(pain['reviewer_industry']) else 'N/A'}
                            - Company Size: {pain['reviewer_firm_size'] if pd.notna(pain['reviewer_firm_size']) else 'N/A'}
                            """)
                        with col_meta2:
                            st.markdown(f"""
                            **Review Details:**
                            - Overall Rating: ⭐ {pain['overall_rating']}/5
                            - Date: {date_str}
                            - [View Original Review]({pain['review_url']})
                            """)
                        
                        # Failing sub-dimensions
                        st.markdown("**📉 Sub-Dimensions with Low Scores:**")
                        dim_cols = st.columns(min(3, len(pain['low_sub_dimensions'])))
                        for idx, (dim, score) in enumerate(pain['low_sub_dimensions'].items()):
                            with dim_cols[idx % 3]:
                                color = "#dc3545" if score < 2.5 else "#ffc107"
                                st.markdown(f"""
                                <div style="background-color: {color}22; padding: 8px; margin: 4px 0; 
                                            border-radius: 4px; border-left: 3px solid {color};">
                                    <strong>{dim}</strong><br/>
                                    Score: {score:.1f}/5.0
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # AI-extracted pain points
                        if pain['ai_pain_points'] and str(pain['ai_pain_points']).strip():
                            st.markdown("**🤖 AI-Extracted Key Issues:**")
                            st.markdown(f"> {pain['ai_pain_points']}")
                        
                        # Related topics
                        if pain['related_topics']:
                            st.markdown(f"**🏷️ Related Topics:** {', '.join(pain['related_topics'][:5])}")
                        
                        # Full review text
                        if pain['overall_comment'] and pd.notna(pain['overall_comment']):
                            st.markdown("**💬 Full Review Comment:**")
                            st.markdown(f"*{pain['overall_comment']}*")
                        
                        # Lessons learned - parsed into likes and dislikes
                        if pain['lessons_learned'] and pd.notna(pain['lessons_learned']):
                            lessons = parse_lessons_learned(pain['lessons_learned'])
                            st.markdown("**📚 Lessons Learned (from reviewer):**")
                            
                            if lessons['likes']:
                                st.markdown("**👍 What they like most:**")
                                st.success(lessons['likes'])
                            
                            if lessons['dislikes']:
                                st.markdown("**👎 What they dislike most:**")
                                st.warning(lessons['dislikes'])
            
            # Moderate Issues - Summary view
            if moderate:
                st.markdown("---")
                st.markdown("#### 🟡 Moderate Issues (Reviews rated 3.0-4.0)")
                
                for i, pain in enumerate(moderate[:5], 1):
                    date_str = pain['date'].strftime('%b %d, %Y') if pd.notna(pain['date']) else 'Date N/A'
                    headline = pain['headline'] if pd.notna(pain['headline']) and str(pain['headline']).strip() else "Moderate Concern"
                    
                    # Get top 2 failing dimensions
                    top_issues = list(pain['low_sub_dimensions'].items())[:2]
                    issues_str = ', '.join([f"{dim} ({score:.1f})" for dim, score in top_issues])
                    
                    with st.expander(f"🟡 {headline} ({date_str}) - Rating: {pain['overall_rating']}/5"):
                        st.markdown(f"**Key Issues:** {issues_str}")
                        if pain['ai_pain_points']:
                            st.markdown(f"**Details:** {pain['ai_pain_points']}")
                        if pain['review_url']:
                            st.markdown(f"[View Full Review]({pain['review_url']})")
                
                if len(moderate) > 5:
                    st.info(f"Showing 5 of {len(moderate)} moderate issues. Expand sections above for details.")
            
            # Analysis by sub-dimension
            st.markdown("---")
            st.markdown("#### 📊 Pain Points by Sub-Dimension")
            
            # Count issues by sub-dimension
            dim_issues = {}
            for pain in pain_points:
                for dim, score in pain['low_sub_dimensions'].items():
                    if dim not in dim_issues:
                        dim_issues[dim] = []
                    dim_issues[dim].append({
                        'score': score,
                        'rating': pain['overall_rating'],
                        'headline': pain['headline']
                    })
            
            # Sort by frequency
            dim_issues_sorted = sorted(dim_issues.items(), key=lambda x: len(x[1]), reverse=True)
            
            for dim, issues in dim_issues_sorted[:5]:
                avg_score = sum(i['score'] for i in issues) / len(issues)
                with st.expander(f"{dim} - {len(issues)} issues (Avg Score: {avg_score:.1f}/5.0)"):
                    for issue in issues[:3]:
                        st.markdown(f"- {issue['headline']} (Score: {issue['score']:.1f}, Overall Rating: {issue['rating']}/5)")
                    if len(issues) > 3:
                        st.markdown(f"*...and {len(issues)-3} more issues*")
        else:
            st.success("✅ No significant pain points found! All reviews show healthy sub-dimension scores.")
    
    with tab2:
        st.markdown("### ✨ What Customers Love About Dayforce")
        st.markdown("*Detailed analysis of positive feedback with specific sub-dimension strengths*")
        
        # Extract positive reviews (4+ rating) and high-scoring sub-dimensions (4.0+)
        # Filter for reviews that have ratings (exclude analyst insights)
        reviews_with_ratings = dayforce_df[dayforce_df['overall_rating'].notna()]
        positive_reviews = reviews_with_ratings[reviews_with_ratings['overall_rating'] >= 4]
        
        if len(positive_reviews) > 0:
            # Define sub-dimensions with readable names
            sub_dimensions = {
                'degree_of_meeting_functional_requirements': 'Functional Requirements',
                'product_functionality': 'Product Functionality',
                'quality_of_product_user_experience': 'User Experience',
                'quality_of_the_evaluation_and_contracting_process': 'Evaluation & Contracting',
                'pricing_and_packaging_clarity': 'Pricing Clarity',
                'value_for_money': 'Value for Money',
                'fit_of_product_strategy_to_market_needs': 'Market Strategy Fit',
                'clarity_of_product_roadmap': 'Roadmap Clarity',
                'extent_of_planned_product_innovation': 'Innovation Plans',
                'ease_and_quality_of_integration_and_deployment': 'Integration & Deployment',
                'quality_of_user_training_and_post_go_live_support': 'Training & Support',
                'implementation_cost': 'Implementation Cost',
                'quality_and_timeliness_of_support': 'Support Quality',
                'customer_success_management_and_value_realization': 'Customer Success',
                'customer_community': 'Customer Community'
            }
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⭐ Highly Satisfied", len(positive_reviews), 
                         help="Reviews with 4+ overall rating")
            with col2:
                avg_rating = positive_reviews['overall_rating'].mean()
                st.metric("Average Rating", f"{avg_rating:.2f}/5.0")
            with col3:
                # Find most praised sub-dimension
                sub_dim_avgs = {}
                for col, name in sub_dimensions.items():
                    if col in positive_reviews.columns:
                        avg = positive_reviews[col].mean()
                        sub_dim_avgs[name] = avg
                if sub_dim_avgs:
                    top_dim = max(sub_dim_avgs.items(), key=lambda x: x[1])
                    st.metric("Top Sub-Dimension", top_dim[0][:20], 
                             help=f"Score: {top_dim[1]:.2f}/5.0")
            
            st.markdown("---")
            
            # Extract topics from positive reviews
            topics = []
            for topics_list in positive_reviews['topics_list']:
                topics.extend(topics_list)
            
            topic_counts = Counter(topics)
            top_topics = topic_counts.most_common(10)
            
            col_top1, col_top2 = st.columns(2)
            
            with col_top1:
                st.markdown("**📌 Most Praised Features/Topics:**")
                for topic, count in top_topics[:7]:
                    pct = count / len(positive_reviews) * 100
                    st.markdown(f"- **{topic}** ({count} mentions, {pct:.0f}%)")
            
            with col_top2:
                # Dimension strengths
                st.markdown("**📈 Strongest Dimensions (AI Scores):**")
                dim_scores = positive_reviews[dimensions].mean().sort_values(ascending=False)
                for dim, score in dim_scores.items():
                    st.markdown(f"- **{dimension_labels[dim]}**: {score:.2f}/5.0")
            
            st.markdown("---")
            st.markdown("#### 🌟 Featured Positive Reviews")
            
            # Show top 5 positive reviews with full details
            for i, (idx, row) in enumerate(positive_reviews.nlargest(5, 'overall_rating').iterrows(), 1):
                headline = row['headline'] if pd.notna(row['headline']) and str(row['headline']).strip() else "Highly Satisfied Customer"
                date_str = row['parsed_date'].strftime('%b %d, %Y') if pd.notna(row['parsed_date']) else 'Date N/A'
                
                with st.expander(f"⭐ #{i}. {headline} (Rating: {row['overall_rating']}/5 | {date_str})"):
                    # Review metadata
                    col_meta1, col_meta2 = st.columns(2)
                    with col_meta1:
                        st.markdown(f"""
                        **Reviewer Profile:**
                        - Role: {row['reviewer_role'] if pd.notna(row['reviewer_role']) else 'N/A'}
                        - Industry: {row['reviewer_industry'] if pd.notna(row['reviewer_industry']) else 'N/A'}
                        - Company Size: {row['reviewer_firm_size'] if pd.notna(row['reviewer_firm_size']) else 'N/A'}
                        """)
                    with col_meta2:
                        st.markdown(f"""
                        **Review Details:**
                        - Overall Rating: ⭐ {row['overall_rating']}/5
                        - Date: {date_str}
                        - [View Original Review]({row['review_url']})
                        """)
                    
                    # High-scoring sub-dimensions
                    high_scores = {}
                    for col, name in sub_dimensions.items():
                        if col in row.index:
                            score = row[col]
                            if pd.notna(score) and score >= 4.0:
                                high_scores[name] = score
                    
                    if high_scores:
                        st.markdown("**📊 Top-Rated Sub-Dimensions:**")
                        # Sort by score
                        sorted_scores = sorted(high_scores.items(), key=lambda x: x[1], reverse=True)
                        dim_cols = st.columns(min(3, len(sorted_scores)))
                        for idx_dim, (dim, score) in enumerate(sorted_scores[:6]):
                            with dim_cols[idx_dim % 3]:
                                st.markdown(f"""
                                <div style="background-color: #d4edda; padding: 8px; margin: 4px 0; 
                                            border-radius: 4px; border-left: 3px solid #28a745;">
                                    <strong>{dim}</strong><br/>
                                    Score: {score:.1f}/5.0
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # AI insights
                    ai_parsed = row.get('ai_parsed', {})
                    if isinstance(ai_parsed, dict) and ai_parsed.get('review_insights'):
                        st.markdown("**🤖 AI-Extracted Insights:**")
                        st.markdown(f"> {ai_parsed['review_insights']}")
                    
                    # Full review text
                    if pd.notna(row['text_content']):
                        st.markdown("**💬 Full Review:**")
                        st.markdown(f"*{row['text_content']}*")
                    
                    # Lessons learned - parsed into likes and dislikes
                    if pd.notna(row['lessons_learned']):
                        lessons = parse_lessons_learned(row['lessons_learned'])
                        st.markdown("**📚 Lessons Learned (from reviewer):**")
                        
                        if lessons['likes']:
                            st.markdown("**👍 What they like most:**")
                            st.success(lessons['likes'])
                        
                        if lessons['dislikes']:
                            st.markdown("**👎 What they dislike most:**")
                            st.warning(lessons['dislikes'])
            
            # Analysis by sub-dimension excellence
            st.markdown("---")
            st.markdown("#### 🏆 Excellence by Sub-Dimension")
            st.markdown("*Which sub-dimensions consistently receive high scores?*")
            
            # Calculate average scores for each sub-dimension
            sub_dim_performance = {}
            for col, name in sub_dimensions.items():
                if col in positive_reviews.columns:
                    # Only calculate if there are non-null values
                    valid_scores = positive_reviews[col].dropna()
                    if len(valid_scores) > 0:
                        avg_score = valid_scores.mean()
                        # Count high scores only from valid (non-null) scores
                        high_count = len(valid_scores[valid_scores >= 4.5])
                        sub_dim_performance[name] = {
                            'avg': avg_score,
                            'high_count': high_count,
                            'total': len(valid_scores)  # Count only reviews with valid scores
                        }
            
            # Sort by average score (only show if we have data)
            if sub_dim_performance:
                sorted_performance = sorted(sub_dim_performance.items(), 
                                           key=lambda x: x[1]['avg'], 
                                           reverse=True)
                
                for dim, perf in sorted_performance[:8]:
                    pct = (perf['high_count'] / perf['total'] * 100) if perf['total'] > 0 else 0
                    st.markdown(f"""
                    <div style="background-color: #d4edda22; padding: 10px; margin: 5px 0; 
                                border-radius: 5px; border-left: 3px solid #28a745;">
                        <strong>{dim}</strong>: {perf['avg']:.2f}/5.0 average 
                        ({perf['high_count']}/{perf['total']} reviews rated 4.5+, {pct:.0f}%)
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No sub-dimension scores available for analysis")
        else:
            st.info("No highly-rated reviews in current selection")
    
    with tab3:
        st.markdown("### 🥊 Competitive Intelligence")
        st.markdown("*Detailed analysis of where competitors excel - learn from their customer feedback*")
        
        # For each gap, show what competitors are doing well
        if gaps:
            # Summary of gaps
            st.markdown("**📊 Gap Summary:**")
            gap_summary_cols = st.columns(len(gaps))
            for idx, gap_item in enumerate(gaps):
                with gap_summary_cols[idx]:
                    st.metric(
                        label=gap_item['dimension'].replace(' (AI)', ''),
                        value=f"{gap_item['dayforce']:.2f}",
                        delta=f"-{gap_item['gap']:.2f}",
                        delta_color="inverse",
                        help=f"{gap_item['competitor']} leads with {gap_item['comp_score']:.2f}"
                    )
            
            st.markdown("---")
            
            for gap_item in gaps:
                dim = [k for k, v in dimension_labels.items() if v == gap_item['dimension']][0]
                competitor = gap_item['competitor']
                
                st.markdown(f"### {gap_item['dimension']}: {competitor} leads by {gap_item['gap']:.2f} points")
                st.markdown(f"*{competitor}: {gap_item['comp_score']:.2f} | Dayforce: {gap_item['dayforce']:.2f}*")
                
                # Get competitor reviews for this dimension
                comp_reviews = competitors_df[
                    (competitors_df['Product'] == competitor) &
                    (competitors_df[dim] >= 3.5)  # Show reviews with decent scores in this dimension
                ].nlargest(5, dim)  # Top 5 reviews
                
                if len(comp_reviews) > 0:
                    st.markdown(f"**🔍 Why {competitor} excels - Direct from customer reviews:**")
                    
                    # Show detailed competitor reviews
                    for i, (idx, row) in enumerate(comp_reviews.iterrows(), 1):
                        headline = row['headline'] if pd.notna(row['headline']) and str(row['headline']).strip() else f"{competitor} Review"
                        date_str = row['parsed_date'].strftime('%b %d, %Y') if pd.notna(row['parsed_date']) else 'Date N/A'
                        
                        with st.expander(f"📄 {competitor} Review #{i}: {headline} ({dim.replace('_', ' ').title()} Score: {row[dim]:.1f}/5)"):
                            # Review metadata
                            col_meta1, col_meta2 = st.columns(2)
                            with col_meta1:
                                st.markdown(f"""
                                **Reviewer Profile:**
                                - Role: {row['reviewer_role'] if pd.notna(row['reviewer_role']) else 'N/A'}
                                - Industry: {row['reviewer_industry'] if pd.notna(row['reviewer_industry']) else 'N/A'}
                                - Company Size: {row['reviewer_firm_size'] if pd.notna(row['reviewer_firm_size']) else 'N/A'}
                                """)
                            with col_meta2:
                                st.markdown(f"""
                                **Review Metrics:**
                                - Overall Rating: ⭐ {row['overall_rating']}/5
                                - {dimension_labels[dim]}: {row[dim]:.1f}/5
                                - Date: {date_str}
                                - [View Original Review]({row['review_url']})
                                """)
                            
                            # AI insights from competitor review
                            ai_parsed = row.get('ai_parsed', {})
                            if isinstance(ai_parsed, dict):
                                if ai_parsed.get('review_insights'):
                                    st.markdown("**🤖 Key Insights:**")
                                    st.markdown(f"> {ai_parsed['review_insights']}")
                                
                                if ai_parsed.get('reasoning'):
                                    st.markdown("**💡 Why this matters:**")
                                    st.markdown(f"> {ai_parsed['reasoning'][:300]}...")
                            
                            # Full comment
                            if pd.notna(row['text_content']):
                                st.markdown("**💬 Full Review:**")
                                st.info(row['text_content'])
                            
                            # Topics discussed
                            if row.get('topics_list'):
                                topics = row['topics_list'][:8]
                                st.markdown(f"**🏷️ Topics Discussed:** {', '.join(topics)}")
                    
                    # Compare Dayforce reviews in same dimension
                    st.markdown(f"---")
                    st.markdown(f"**📉 Dayforce Performance in {gap_item['dimension']}:**")
                    
                    dayforce_in_dim = dayforce_df[dayforce_df[dim].notna()].nsmallest(3, dim)
                    
                    if len(dayforce_in_dim) > 0:
                        st.markdown("*Bottom 3 Dayforce reviews in this dimension:*")
                        for idx, row in dayforce_in_dim.iterrows():
                            headline = row['headline'] if pd.notna(row['headline']) and str(row['headline']).strip() else "Dayforce Review"
                            overall_rating = row['overall_rating'] if pd.notna(row['overall_rating']) else 'N/A'
                            st.markdown(f"- **{headline}** - Score: {row[dim]:.1f}/5, Overall: {overall_rating}/5")
                    
                    st.markdown("---")
                    st.markdown("**💡 Strategic Action Items:**")
                    st.markdown(generate_gap_closure_recommendations(gap_item['dimension'], competitor))
                else:
                    st.info(f"No detailed feedback available for {competitor} in this dimension")
                
                st.markdown("---")
        else:
            st.success("🎉 Dayforce leads in all dimensions! No competitive gaps identified.")
            st.balloons()
    
    st.markdown("---")
    
    # Reviewer segments
    st.subheader("👥 Dayforce Customer Segments")
    
    col_seg1, col_seg2 = st.columns(2)
    
    with col_seg1:
        # By industry
        st.markdown("**Performance by Industry:**")
        industry_perf = dayforce_df.groupby('reviewer_industry')[dimensions].mean().mean(axis=1).sort_values(ascending=False)
        
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
        size_perf = dayforce_df.groupby('reviewer_firm_size')[dimensions].mean().mean(axis=1).sort_values(ascending=False)
        
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
