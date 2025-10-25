"""
Utility functions for data loading and processing
"""

import pandas as pd
import json
import re
from datetime import datetime
import streamlit as st

def data_source_badge(source_type):
    """
    Display a small badge indicating data source
    source_type: 'customer_review' or 'ai_analysis'
    """
    if source_type == 'customer_review':
        return "📄 *XLSX - Customer Review*"
    elif source_type == 'ai_analysis':
        return "🤖 *XLSX - AI Analysis*"
    else:
        return ""

def load_data(filepath):
    """Load and preprocess the Excel data"""
    df = pd.read_excel(filepath)
    
    # Parse dates
    df['parsed_date'] = pd.to_datetime(df['Review Date'], format='%d/%m/%Y', errors='coerce')
    
    # Parse ai_output JSON
    df['ai_parsed'] = df['ai_output'].apply(parse_ai_output)
    
    # Extract topics from topics column
    df['topics_list'] = df['topics'].apply(parse_topics)
    
    # Extract insights and pain points
    df['insights_list'] = df['review_insights'].apply(parse_text_field)
    df['pain_points_list'] = df['review_pain_points'].apply(parse_text_field)
    
    return df

def parse_ai_output(ai_output_text):
    """Parse the ai_output field to extract structured data"""
    if pd.isna(ai_output_text):
        return {}
    
    try:
        # The ai_output appears to be a Prediction object in string format
        # Extract the key components using regex
        result = {}
        
        # Extract reasoning
        reasoning_match = re.search(r"reasoning='([^']*)'", ai_output_text, re.DOTALL)
        if reasoning_match:
            result['reasoning'] = reasoning_match.group(1)
        
        # Extract review_insights
        insights_match = re.search(r"review_insights='([^']*)'", ai_output_text, re.DOTALL)
        if insights_match:
            result['review_insights'] = insights_match.group(1)
        
        # Extract review_pain_points
        pain_match = re.search(r"review_pain_points='([^']*)'", ai_output_text, re.DOTALL)
        if pain_match:
            result['review_pain_points'] = pain_match.group(1)
        
        return result
    except Exception as e:
        return {}

def parse_topics(topics_text):
    """Parse topics from string representation of list"""
    if pd.isna(topics_text):
        return []
    
    try:
        # Remove brackets and quotes, split by comma
        topics_text = str(topics_text)
        topics_text = topics_text.strip("[]")
        topics = [t.strip().strip("'\"") for t in topics_text.split(',')]
        return [t for t in topics if t]
    except:
        return []

def parse_text_field(text):
    """Parse text fields that might contain lists or structured data"""
    if pd.isna(text):
        return []
    
    text = str(text)
    
    # If it looks like a list
    if text.startswith('[') and text.endswith(']'):
        try:
            items = eval(text)
            return items if isinstance(items, list) else [text]
        except:
            return [text]
    
    # Split by periods or newlines for bullet points
    items = re.split(r'[.]\s+|\n', text)
    return [item.strip() for item in items if item.strip()]

def get_sentiment_color(score):
    """Return color based on sentiment score (1-5 scale)"""
    if score >= 4.5:
        return '#2ecc71'  # Green - Excellent
    elif score >= 4.0:
        return '#3498db'  # Blue - Good
    elif score >= 3.5:
        return '#f39c12'  # Orange - Average
    elif score >= 3.0:
        return '#e67e22'  # Dark Orange - Below Average
    else:
        return '#e74c3c'  # Red - Poor

def get_sentiment_label(score):
    """Return label based on sentiment score"""
    if score >= 4.5:
        return '🌟 Excellent'
    elif score >= 4.0:
        return '👍 Good'
    elif score >= 3.5:
        return '😐 Average'
    elif score >= 3.0:
        return '⚠️ Below Average'
    else:
        return '❌ Poor'

def format_date(date_str):
    """Format date string consistently"""
    try:
        dt = pd.to_datetime(date_str, format='%d/%m/%Y')
        return dt.strftime('%b %d, %Y')
    except:
        return str(date_str)

def calculate_sentiment_stats(df, dimension):
    """Calculate statistics for a sentiment dimension"""
    if dimension not in df.columns:
        return None
    
    return {
        'mean': df[dimension].mean(),
        'median': df[dimension].median(),
        'std': df[dimension].std(),
        'min': df[dimension].min(),
        'max': df[dimension].max(),
        'count': df[dimension].count()
    }

def get_trending_topics(df, top_n=10):
    """Get most frequently mentioned topics"""
    all_topics = []
    for topics_list in df['topics_list']:
        all_topics.extend(topics_list)
    
    # Count frequencies
    from collections import Counter
    topic_counts = Counter(all_topics)
    
    return topic_counts.most_common(top_n)

def get_topics_by_sentiment(df, dimension, threshold=3.5):
    """Get topics grouped by sentiment (above/below threshold)"""
    low_sentiment = []
    high_sentiment = []
    
    for idx, row in df.iterrows():
        score = row.get(dimension, 0)
        topics = row.get('topics_list', [])
        
        if score < threshold:
            low_sentiment.extend(topics)
        else:
            high_sentiment.extend(topics)
    
    from collections import Counter
    return {
        'low': Counter(low_sentiment).most_common(10),
        'high': Counter(high_sentiment).most_common(10)
    }

def extract_pain_points(df, product=None):
    """Extract pain points, optionally filtered by product"""
    pain_points = []
    
    filtered_df = df if product is None else df[df['Product'] == product]
    
    for idx, row in filtered_df.iterrows():
        if 'pain_points_list' in row and row['pain_points_list']:
            for pain in row['pain_points_list']:
                if pain and len(pain) > 10:  # Filter out very short items
                    pain_points.append({
                        'pain_point': pain,
                        'product': row['Product'],
                        'date': row['parsed_date'],
                        'overall_rating': row.get('Overall User Rating', 0)
                    })
    
    return pain_points

def calculate_competitive_position(df, our_product='Dayforce'):
    """Calculate competitive positioning metrics"""
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    
    results = []
    for product in df['Product'].unique():
        product_df = df[df['Product'] == product]
        
        product_stats = {
            'Product': product,
            'Review Count': len(product_df),
            'Is Dayforce': product == our_product
        }
        
        for dim in dimensions:
            product_stats[f'{dim}_avg'] = product_df[dim].mean()
            product_stats[f'{dim}_std'] = product_df[dim].std()
        
        # Overall average across all dimensions
        dim_averages = [product_df[dim].mean() for dim in dimensions]
        product_stats['overall_avg'] = sum(dim_averages) / len(dim_averages)
        
        results.append(product_stats)
    
    return pd.DataFrame(results).sort_values('overall_avg', ascending=False).reset_index(drop=True)

def identify_improvement_opportunities(df, our_product='Dayforce', threshold=3.8):
    """Identify areas where Dayforce is below threshold"""
    dayforce_df = df[df['Product'] == our_product]
    
    if len(dayforce_df) == 0:
        return []
    
    dimensions = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
    opportunities = []
    
    for dim in dimensions:
        avg_score = dayforce_df[dim].mean()
        if avg_score < threshold:
            # Get related pain points and topics
            low_reviews = dayforce_df[dayforce_df[dim] < threshold]
            pain_points = []
            topics = []
            
            for idx, row in low_reviews.iterrows():
                pain_points.extend(row.get('pain_points_list', []))
                topics.extend(row.get('topics_list', []))
            
            from collections import Counter
            top_pain_points = Counter(pain_points).most_common(5)
            top_topics = Counter(topics).most_common(5)
            
            opportunities.append({
                'dimension': dim,
                'avg_score': avg_score,
                'gap_from_target': threshold - avg_score,
                'affected_reviews': len(low_reviews),
                'top_pain_points': top_pain_points,
                'top_topics': top_topics
            })
    
    return sorted(opportunities, key=lambda x: x['gap_from_target'], reverse=True)
