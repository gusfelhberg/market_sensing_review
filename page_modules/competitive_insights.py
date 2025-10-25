"""
Competitive Insights Page
Analyze Dayforce performance relative to competitors
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import calculate_competitive_position, get_sentiment_color, data_source_badge

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import calculate_competitive_position, get_sentiment_color

def render(filtered_df, full_df):
    """Render the Competitive Insights page"""
    
    st.header("⚔️ Competitive Intelligence")
    st.markdown("**How does Dayforce stack up against the competition?**")
    st.caption(data_source_badge('ai_analysis'))
    
    st.info("🎯 **Focus: Dayforce vs. Market** - All comparisons benchmark Dayforce against competitors using AI sentiment scores (1-5)")
    
    # Calculate competitive position
    comp_df = calculate_competitive_position(filtered_df)
    
    # Overall competitive landscape
    st.subheader("🏆 Market Position Overview")
    
    # Create radar chart comparing all products
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    dimension_labels = {
        'product': 'Product (AI)',
        'gtm': 'GTM (AI)',
        'market_direction': 'Market Dir. (AI)',
        'implementation': 'Implementation (AI)',
        'customer_experience': 'Cust. Exp. (AI)'
    }
    
    fig = go.Figure()
    
    for idx, row in comp_df.iterrows():
        product = row['Product']
        values = [row[f'{dim}_avg'] for dim in dimensions]
        values.append(values[0])  # Close the radar chart
        
        # Highlight Dayforce
        line_width = 4 if row['Is Dayforce'] else 2
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[dimension_labels[d] for d in dimensions] + [dimension_labels[dimensions[0]]],
            fill='toself',
            name=product,
            line=dict(width=line_width)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=True,
        title="Competitive Position Across All Dimensions",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Dimension-by-dimension comparison
    st.subheader("📊 Dimension-by-Dimension Comparison")
    
    selected_dim = st.selectbox(
        "Select dimension to analyze",
        dimensions,
        format_func=lambda x: dimension_labels[x]
    )
    
    col_comp1, col_comp2 = st.columns([2, 1])
    
    with col_comp1:
        # Bar chart for selected dimension
        dim_data = comp_df[['Product', f'{selected_dim}_avg', 'Review Count', 'Is Dayforce']].copy()
        dim_data = dim_data.sort_values(f'{selected_dim}_avg', ascending=False)
        
        colors = ['#0c5460' if is_dayforce else '#6c757d' for is_dayforce in dim_data['Is Dayforce']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=dim_data['Product'],
                y=dim_data[f'{selected_dim}_avg'],
                marker_color=colors,
                text=dim_data[f'{selected_dim}_avg'].round(2),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<br>Reviews: %{customdata}<extra></extra>',
                customdata=dim_data['Review Count']
            )
        ])
        
        fig.update_layout(
            title=f"{dimension_labels[selected_dim]} Comparison",
            yaxis_title="AI Sentiment Score (1-5)",
            xaxis_title="Product",
            yaxis=dict(range=[0, 5.5]),
            height=400
        )
        
        # Add average line
        avg_score = dim_data[f'{selected_dim}_avg'].mean()
        fig.add_hline(y=avg_score, line_dash="dash", line_color="red",
                     annotation_text=f"Market Avg: {avg_score:.2f}")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_comp2:
        st.markdown("**Competitive Position**")
        
        # Find Dayforce position
        dayforce_data = comp_df[comp_df['Is Dayforce']]
        
        if len(dayforce_data) > 0:
            dayforce_score = dayforce_data.iloc[0][f'{selected_dim}_avg']
            market_avg = comp_df[f'{selected_dim}_avg'].mean()
            rank = (comp_df[f'{selected_dim}_avg'] > dayforce_score).sum() + 1
            total_products = len(comp_df)
            
            st.metric("Dayforce AI Score", f"{dayforce_score:.2f}")
            st.metric("Market Average", f"{market_avg:.2f}")
            st.metric("Market Rank", f"#{rank} of {total_products}")
            
            gap = dayforce_score - market_avg
            if gap > 0:
                st.success(f"✅ {gap:.2f} points ahead of market")
            else:
                st.warning(f"⚠️ {abs(gap):.2f} points behind market")
            
            st.markdown("---")
            
            # Show competitors ahead/behind
            competitors_ahead = comp_df[comp_df[f'{selected_dim}_avg'] > dayforce_score]
            competitors_behind = comp_df[comp_df[f'{selected_dim}_avg'] < dayforce_score]
            
            if len(competitors_ahead) > 0:
                st.markdown("**Ahead of Dayforce:**")
                for _, row in competitors_ahead.iterrows():
                    diff = row[f'{selected_dim}_avg'] - dayforce_score
                    st.markdown(f"- {row['Product']}: +{diff:.2f}")
            
            if len(competitors_behind) > 0:
                st.markdown("**Behind Dayforce:**")
                for _, row in competitors_behind.iterrows():
                    diff = dayforce_score - row[f'{selected_dim}_avg']
                    st.markdown(f"- {row['Product']}: +{diff:.2f}")
        else:
            st.info("No Dayforce reviews in current selection")
    
    st.markdown("---")
    
    # Strengths and weaknesses
    st.subheader("💪 Strengths & Weaknesses Analysis")
    
    dayforce_data = filtered_df[filtered_df['Product'] == 'Dayforce']
    
    if len(dayforce_data) > 0:
        col_str, col_weak = st.columns(2)
        
        with col_str:
            st.markdown("### ✅ Dayforce Strengths")
            st.markdown("*Dimensions where Dayforce leads the market*")
            
            strengths = []
            for dim in dimensions:
                dayforce_score = dayforce_data[dim].mean()
                market_score = filtered_df[dim].mean()
                
                if dayforce_score > market_score:
                    gap = dayforce_score - market_score
                    strengths.append((dimension_labels[dim], dayforce_score, gap))
            
            strengths.sort(key=lambda x: x[2], reverse=True)
            
            if strengths:
                for label, score, gap in strengths:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 15px; margin: 10px 0; 
                                border-radius: 5px; border-left: 4px solid #28a745;">
                        <strong>{label}</strong><br/>
                        Score: {score:.2f} | +{gap:.2f} vs market<br/>
                        <small>Leading competitive advantage</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No dimensions where Dayforce leads the market in current selection")
        
        with col_weak:
            st.markdown("### ⚠️ Improvement Opportunities")
            st.markdown("*Dimensions where Dayforce trails the market*")
            
            weaknesses = []
            for dim in dimensions:
                dayforce_score = dayforce_data[dim].mean()
                market_score = filtered_df[dim].mean()
                
                if dayforce_score < market_score:
                    gap = market_score - dayforce_score
                    weaknesses.append((dimension_labels[dim], dayforce_score, gap))
            
            weaknesses.sort(key=lambda x: x[2], reverse=True)
            
            if weaknesses:
                for label, score, gap in weaknesses:
                    st.markdown(f"""
                    <div style="background-color: #fff3cd; padding: 15px; margin: 10px 0; 
                                border-radius: 5px; border-left: 4px solid #ffc107;">
                        <strong>{label}</strong><br/>
                        Score: {score:.2f} | -{gap:.2f} vs market<br/>
                        <small>Focus area for improvement</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Dayforce leads or matches market in all dimensions!")
    else:
        st.info("No Dayforce reviews available in the current selection for analysis")
    
    st.markdown("---")
    
    # Competitive matrix
    st.subheader("📋 Competitive Scorecard")
    
    # Create a detailed comparison table
    scorecard_data = []
    
    for _, row in comp_df.iterrows():
        product_row = {
            'Product': row['Product'],
            'Reviews': int(row['Review Count']),
            'Overall': f"{row['overall_avg']:.2f}"
        }
        
        for dim in dimensions:
            product_row[dimension_labels[dim]] = f"{row[f'{dim}_avg']:.2f}"
        
        scorecard_data.append(product_row)
    
    scorecard_df = pd.DataFrame(scorecard_data)
    
    # Style the dataframe
    st.dataframe(
        scorecard_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Download option
    st.download_button(
        label="📥 Download Competitive Analysis",
        data=scorecard_df.to_csv(index=False),
        file_name="competitive_analysis.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Head-to-head comparison
    st.subheader("🥊 Head-to-Head Comparison")
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        product1 = st.selectbox(
            "Select first product",
            comp_df['Product'].tolist(),
            index=0
        )
    
    with col_h2:
        product2 = st.selectbox(
            "Select second product",
            comp_df['Product'].tolist(),
            index=1 if len(comp_df) > 1 else 0
        )
    
    if product1 != product2:
        p1_data = comp_df[comp_df['Product'] == product1].iloc[0]
        p2_data = comp_df[comp_df['Product'] == product2].iloc[0]
        
        # Create comparison chart
        comparison_data = {
            'Dimension': [dimension_labels[d] for d in dimensions],
            product1: [p1_data[f'{d}_avg'] for d in dimensions],
            product2: [p2_data[f'{d}_avg'] for d in dimensions]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=product1,
            x=comparison_df['Dimension'],
            y=comparison_df[product1],
            marker_color='#3498db'
        ))
        
        fig.add_trace(go.Bar(
            name=product2,
            x=comparison_df['Dimension'],
            y=comparison_df[product2],
            marker_color='#e74c3c'
        ))
        
        fig.update_layout(
            title=f"{product1} vs {product2}",
            yaxis_title="AI Sentiment Score (1-5)",
            yaxis=dict(range=[0, 5.5]),
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            st.markdown(f"**{product1}**")
            st.metric("Overall AI Score", f"{p1_data['overall_avg']:.2f}")
            st.metric("Review Count", int(p1_data['Review Count']))
        
        with col_sum2:
            st.markdown(f"**{product2}**")
            st.metric("Overall AI Score", f"{p2_data['overall_avg']:.2f}")
            st.metric("Review Count", int(p2_data['Review Count']))
