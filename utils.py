"""
Utility functions for data loading and processing
"""

import pandas as pd
import json
import re
from datetime import datetime
import streamlit as st

def get_source_type_config():
    """
    Return configuration for different source types
    Used for consistent labeling, icons, and colors across the app
    """
    return {
        'gartner_review': {
            'label': 'Customer Review',
            'short_label': 'Reviews',
            'icon': '👤',
            'color': '#2D6FDD',
            'description': 'Direct user feedback from Gartner Peer Insights',
            'badge': '👤 Customer Review'
        },
        'analyst_insight': {
            'label': 'Analyst Intelligence',
            'short_label': 'Analyst',
            'icon': '🎓',
            'color': '#059669',
            'description': 'Industry analyst observations and insights',
            'badge': '🎓 Analyst Intelligence'
        }
    }

def get_source_badge(source_type):
    """Get display badge for a source type"""
    config = get_source_type_config()
    return config.get(source_type, {}).get('badge', source_type)

def get_source_icon(source_type):
    """Get icon for a source type"""
    config = get_source_type_config()
    return config.get(source_type, {}).get('icon', '📊')

def get_source_label(source_type):
    """Get human-readable label for a source type"""
    config = get_source_type_config()
    return config.get(source_type, {}).get('label', source_type)

def get_source_color(source_type):
    """Get color for a source type"""
    config = get_source_type_config()
    return config.get(source_type, {}).get('color', '#6c757d')

def data_source_badge(source_type):
    """
    Display a small badge indicating data source
    source_type: 'customer_review', 'ai_analysis', or actual source type
    """
    if source_type == 'customer_review':
        return "📄 *XLSX - Customer Review*"
    elif source_type == 'ai_analysis':
        return "🤖 *XLSX - AI Analysis*"
    elif source_type in get_source_type_config():
        return get_source_badge(source_type)
    else:
        return ""

def parse_lessons_learned(lessons_text):
    """
    Parse the Lessons Learned field which contains two questions:
    1. "What do you like most about the product or service?"
    2. "What do you dislike most about the product or service?"
    
    Returns a dict with 'likes' and 'dislikes' keys
    """
    if not lessons_text or pd.isna(lessons_text):
        return {'likes': '', 'dislikes': ''}
    
    text = str(lessons_text).strip()
    
    # Try to split by the dislike question
    like_pattern = r"What do you like most about the product or service\?"
    dislike_pattern = r"What do you dislike most about the product or service\?"
    
    # Find the positions
    like_match = re.search(like_pattern, text, re.IGNORECASE)
    dislike_match = re.search(dislike_pattern, text, re.IGNORECASE)
    
    likes = ''
    dislikes = ''
    
    if like_match and dislike_match:
        # Both questions found
        like_start = like_match.end()
        dislike_start = dislike_match.start()
        
        likes = text[like_start:dislike_start].strip()
        dislikes = text[dislike_match.end():].strip()
    elif like_match:
        # Only like question found
        likes = text[like_match.end():].strip()
    elif dislike_match:
        # Only dislike question found
        dislikes = text[dislike_match.end():].strip()
    else:
        # No structured questions, return as-is in likes
        likes = text
    
    return {'likes': likes, 'dislikes': dislikes}

def get_dimension_colors():
    """
    Return consistent color scheme for the 5 main dimensions
    Use across all charts in the app for visual consistency
    """
    return {
        'product': '#1f77b4',           # Blue
        'gtm': '#ff7f0e',               # Orange
        'market_direction': '#2ca02c',  # Green
        'implementation': '#d62728',    # Red
        'customer_experience': '#9467bd' # Purple
    }

def get_dimension_color(dimension):
    """Get color for a specific dimension"""
    colors = get_dimension_colors()
    return colors.get(dimension, '#7f7f7f')  # Default gray if not found

def get_product_colors():
    """
    Return consistent color scheme for products based on actual brand colors
    Use when grouping/coloring by product
    """
    return {
        'Dayforce': '#2D6FDD',      # Dayforce bright blue (from logo) - ONLY blue
        'Workday': '#FB9F00',       # Workday orange/amber (official brand)
        'UKG Pro': '#7C3AED',       # UKG purple/violet (distinctive, non-blue)
        'ADP WFN': '#D7282F',       # ADP red (ADP official brand color)
        'SAP SF': '#10B981'         # SAP emerald green (distinctive, non-blue)
    }

def get_product_color(product):
    """Get color for a specific product"""
    colors = get_product_colors()
    return colors.get(product, '#6c757d')  # Default gray if not found

def load_data(filepath=None):
    """
    LEGACY FUNCTION - Maintained for backward compatibility
    Load and preprocess the Excel data - combines Sept and Oct 2025 files
    
    For new multi-source implementation, use load_unified_data() instead
    """
    # Load both old data files and combine them (legacy)
    sept_df = pd.read_excel('data/market_sensing_data_gartner_ai_output_sept2025.xlsx')
    oct_df = pd.read_excel('data/market_sensing_data_gartner_ai_output_oct2025.xlsx')
    
    # Combine the dataframes
    df = pd.concat([sept_df, oct_df], ignore_index=True)
    
    # Add source type for legacy data
    df['source_type'] = 'gartner_review'
    df['source_name'] = 'Gartner Peer Insights'
    
    # Parse dates
    df['parsed_date'] = pd.to_datetime(df['Review Date'], format='%d/%m/%Y', errors='coerce')
    
    # Standardize text content field
    df['text_content'] = df['Overall Comment']
    
    # Parse ai_output JSON
    df['ai_parsed'] = df['ai_output'].apply(parse_ai_output)
    
    # Parse the 6 new topic columns and create consolidated lists
    topic_columns = ['product_topics', 'gtm_topics', 'market_direction_topics', 
                     'implementation_topics', 'customer_experience_topics', 'other_topics']
    
    # Create a unified topics_list for backward compatibility
    df['topics_list'] = df.apply(lambda row: parse_all_topics(row, topic_columns), axis=1)
    
    # Parse individual topic columns
    for col in topic_columns:
        df[f'{col}_list'] = df[col].apply(parse_topics)
    
    # Calculate dimension-level scores from sub-dimensions (this also calls clean_score_columns internally)
    df = calculate_dimension_scores(df)
    
    return df

def load_unified_data():
    """
    Load and unify data from multiple sources:
    1. Gartner Customer Reviews
    2. Analyst Intelligence Insights
    
    Returns a unified DataFrame with source_type field for filtering
    """
    
    # Load Gartner reviews
    gartner_df = pd.read_excel('data/market_sensing_data_ai_output_gartner.xlsx')
    
    # Load Analyst insights
    analyst_df = pd.read_excel('data/market_sensing_data_ai_output_analyst.xlsx')
    
    # Add source identification
    gartner_df['source_type'] = 'gartner_review'
    gartner_df['source_name'] = 'Gartner Peer Insights'
    
    analyst_df['source_type'] = 'analyst_insight'
    analyst_df['source_name'] = analyst_df['Firm']
    
    # Harmonize date fields
    gartner_df['date'] = pd.to_datetime(gartner_df['Review Date'], format='%d/%m/%Y', errors='coerce')
    analyst_df['date'] = pd.to_datetime(analyst_df['Date'], errors='coerce')
    
    gartner_df['parsed_date'] = gartner_df['date']
    analyst_df['parsed_date'] = analyst_df['date']
    
    # Harmonize product field (analyst insights are Dayforce-only)
    analyst_df['Product'] = 'Dayforce'
    
    # Harmonize text content field
    gartner_df['text_content'] = gartner_df['Overall Comment'].fillna('')
    analyst_df['text_content'] = analyst_df['Insight'].fillna('')
    
    # Preserve source-specific metadata
    gartner_df['review_url'] = gartner_df.get('Review URL', '')
    gartner_df['headline'] = gartner_df.get('Headline', '')
    gartner_df['reviewer_role'] = gartner_df.get('Reviewer Role ', '')
    gartner_df['reviewer_industry'] = gartner_df.get('Reviewer Industry', '')
    gartner_df['reviewer_firm_size'] = gartner_df.get('Reviewer Firm Size', '')
    gartner_df['lessons_learned'] = gartner_df.get('Lessons Learned', '')
    gartner_df['overall_rating'] = pd.to_numeric(gartner_df.get('Overall User Rating', None), errors='coerce')
    gartner_df['analyst_firm'] = None  # Not applicable for reviews
    gartner_df['analyst_name'] = None  # Not applicable for reviews
    gartner_df['interaction'] = ''  # Not applicable for reviews
    
    analyst_df['analyst_firm'] = analyst_df['Firm']
    analyst_df['analyst_name'] = analyst_df['Analyst']
    analyst_df['interaction'] = analyst_df.get('Interaction', '')
    analyst_df['review_url'] = ''  # No URL for analyst insights
    analyst_df['headline'] = analyst_df['text_content'].str[:100] + '...'  # Create pseudo-headline
    analyst_df['overall_rating'] = None  # No rating for analyst insights
    analyst_df['reviewer_role'] = None  # Not applicable for analyst insights
    analyst_df['reviewer_industry'] = None  # Not applicable for analyst insights
    analyst_df['reviewer_firm_size'] = None  # Not applicable for analyst insights
    analyst_df['lessons_learned'] = ''  # Not applicable for analyst insights
    
    # Parse ai_output for both sources
    gartner_df['ai_parsed'] = gartner_df['ai_output'].apply(parse_ai_output)
    analyst_df['ai_parsed'] = analyst_df['ai_output'].apply(parse_ai_output)
    
    # Parse topic columns
    topic_columns = ['product_topics', 'gtm_topics', 'market_direction_topics', 
                     'implementation_topics', 'customer_experience_topics', 'other_topics']
    
    for df in [gartner_df, analyst_df]:
        # Create unified topics_list
        df['topics_list'] = df.apply(lambda row: parse_all_topics(row, topic_columns), axis=1)
        
        # Parse individual topic columns
        for col in topic_columns:
            df[f'{col}_list'] = df[col].apply(parse_topics)
    
    # Calculate dimension scores from sub-dimensions
    gartner_df = calculate_dimension_scores(gartner_df)
    analyst_df = calculate_dimension_scores(analyst_df)
    
    # Combine dataframes
    # Identify common columns
    common_cols = list(set(gartner_df.columns) & set(analyst_df.columns))
    
    # Ensure all essential columns are present
    essential_cols = ['source_type', 'source_name', 'Product', 'parsed_date', 'date', 'text_content',
                      'product', 'gtm', 'market_direction', 'implementation', 'customer_experience',
                      'topics_list', 'product_topics_list', 'gtm_topics_list', 
                      'market_direction_topics_list', 'implementation_topics_list',
                      'customer_experience_topics_list', 'other_topics_list',
                      'headline', 'overall_rating', 'analyst_firm', 'analyst_name', 
                      'reviewer_role', 'reviewer_industry', 'reviewer_firm_size', 'lessons_learned',
                      'interaction', 'review_url']
    
    # Add sub-dimension columns to essential
    sub_dimension_cols = [
        'degree_of_meeting_functional_requirements', 'product_functionality',
        'quality_of_product_user_experience', 'quality_of_the_evaluation_and_contracting_process',
        'pricing_and_packaging_clarity', 'value_for_money',
        'fit_of_product_strategy_to_market_needs', 'clarity_of_product_roadmap',
        'extent_of_planned_product_innovation', 'ease_and_quality_of_integration_and_deployment',
        'quality_of_user_training_and_post_go_live_support', 'implementation_cost',
        'quality_and_timeliness_of_support', 'customer_success_management_and_value_realization',
        'customer_community'
    ]
    essential_cols.extend(sub_dimension_cols)
    
    # Use only common columns that are essential
    use_cols = [col for col in essential_cols if col in common_cols]
    
    # Combine using only common columns
    unified_df = pd.concat([
        gartner_df[use_cols],
        analyst_df[use_cols]
    ], ignore_index=True)
    
    # Ensure overall_rating is numeric after combining
    unified_df['overall_rating'] = pd.to_numeric(unified_df['overall_rating'], errors='coerce')
    
    return unified_df

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
    """Parse topics from string representation of list and convert to lowercase"""
    if pd.isna(topics_text):
        return []
    
    try:
        # Remove brackets and quotes, split by comma
        topics_text = str(topics_text)
        topics_text = topics_text.strip("[]")
        topics = [t.strip().strip("'\"").lower() for t in topics_text.split(',')]
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

def parse_all_topics(row, topic_columns):
    """Combine all topic columns into a single list"""
    all_topics = []
    for col in topic_columns:
        topics = parse_topics(row[col])
        all_topics.extend(topics)
    return all_topics

def clean_score_columns(df):
    """Convert 'not_mentioned' to NaN in score columns and ensure numeric types"""
    score_columns = [
        'degree_of_meeting_functional_requirements',
        'product_functionality',
        'quality_of_product_user_experience',
        'quality_of_the_evaluation_and_contracting_process',
        'pricing_and_packaging_clarity',
        'value_for_money',
        'fit_of_product_strategy_to_market_needs',
        'clarity_of_product_roadmap',
        'extent_of_planned_product_innovation',
        'ease_and_quality_of_integration_and_deployment',
        'quality_of_user_training_and_post_go_live_support',
        'implementation_cost',
        'quality_and_timeliness_of_support',
        'customer_success_management_and_value_realization',
        'customer_community'
    ]
    
    for col in score_columns:
        if col in df.columns:
            # Replace 'not_mentioned' with NaN
            df[col] = df[col].replace('not_mentioned', pd.NA)
            # Convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def calculate_dimension_scores(df):
    """Calculate average scores for each of the 5 main dimensions from their 3 sub-dimensions"""
    
    # First ensure all sub-dimension columns are numeric
    df = clean_score_columns(df)
    
    # Product dimension (average of 3 sub-dimensions)
    product_cols = ['degree_of_meeting_functional_requirements', 'product_functionality', 'quality_of_product_user_experience']
    df['product'] = df[product_cols].mean(axis=1, skipna=True)
    
    # GTM dimension
    gtm_cols = ['quality_of_the_evaluation_and_contracting_process', 'pricing_and_packaging_clarity', 'value_for_money']
    df['gtm'] = df[gtm_cols].mean(axis=1, skipna=True)
    
    # Market Direction dimension
    market_cols = ['fit_of_product_strategy_to_market_needs', 'clarity_of_product_roadmap', 'extent_of_planned_product_innovation']
    df['market_direction'] = df[market_cols].mean(axis=1, skipna=True)
    
    # Implementation dimension
    impl_cols = ['ease_and_quality_of_integration_and_deployment', 'quality_of_user_training_and_post_go_live_support', 'implementation_cost']
    df['implementation'] = df[impl_cols].mean(axis=1, skipna=True)
    
    # Customer Experience dimension
    cx_cols = ['quality_and_timeliness_of_support', 'customer_success_management_and_value_realization', 'customer_community']
    df['customer_experience'] = df[cx_cols].mean(axis=1, skipna=True)
    
    return df

def calculate_avg_ignoring_not_mentioned(row):
    """Calculate average of values, ignoring 'not_mentioned' strings and NaN"""
    values = []
    for val in row:
        if pd.notna(val) and val != 'not_mentioned':
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                continue
    
    if values:
        return sum(values) / len(values)
    else:
        return pd.NA

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
    """Extract pain points from low-scoring reviews with full review details"""
    pain_points = []
    
    filtered_df = df if product is None else df[df['Product'] == product]
    
    # Define all sub-dimension score columns with readable names
    score_columns = {
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
    
    for idx, row in filtered_df.iterrows():
        # Identify low-scoring sub-dimensions (below 3.5)
        low_scores = {}
        for col, display_name in score_columns.items():
            score = row.get(col, pd.NA)
            if pd.notna(score) and score < 3.5:
                low_scores[display_name] = score
        
        if low_scores:
            # Sort by score (worst first)
            sorted_low_scores = dict(sorted(low_scores.items(), key=lambda x: x[1]))
            
            # Get AI-extracted pain points if available
            ai_parsed = row.get('ai_parsed', {})
            ai_pain_points = ai_parsed.get('review_pain_points', '') if isinstance(ai_parsed, dict) else ''
            
            # Get associated topics
            all_topics = row.get('topics_list', [])
            
            # Handle NaN values for text fields
            headline = row.get('Headline', '')
            overall_comment = row.get('Overall Comment', '')
            overall_comment = overall_comment if pd.notna(overall_comment) else ''
            
            # Create a meaningful headline if missing
            if not pd.notna(headline) or not str(headline).strip():
                # Try to extract a headline from the AI pain points or overall comment
                if ai_pain_points and len(str(ai_pain_points).strip()) > 0:
                    # Use first 60 chars of AI pain points as headline
                    headline = str(ai_pain_points)[:60].strip()
                    if len(str(ai_pain_points)) > 60:
                        headline += "..."
                elif overall_comment and len(overall_comment) > 0:
                    # Use first sentence or 60 chars of comment
                    first_sentence = str(overall_comment).split('.')[0][:60].strip()
                    headline = first_sentence + ("..." if len(first_sentence) == 60 else "")
                else:
                    # Generate headline from failing dimensions
                    top_failing = list(sorted_low_scores.items())[:2]
                    if top_failing:
                        dims = ', '.join([dim for dim, _ in top_failing])
                        headline = f"Issues with {dims}"
                    else:
                        headline = f"Review from {row.get('Reviewer Role ', 'Customer')}"
            
            lessons_learned = row.get('Lessons Learned', '')
            lessons_learned = lessons_learned if pd.notna(lessons_learned) else ''
            
            review_url = row.get('Review URL', '')
            review_url = review_url if pd.notna(review_url) else ''
            
            pain_points.append({
                'review_id': idx,
                'product': row['Product'],
                'date': row['parsed_date'],
                'overall_rating': row.get('Overall User Rating', 0),
                'headline': headline,
                'overall_comment': overall_comment,
                'lessons_learned': lessons_learned,
                'review_url': review_url,
                'reviewer_role': row.get('Reviewer Role ', ''),
                'reviewer_industry': row.get('Reviewer Industry', ''),
                'reviewer_firm_size': row.get('Reviewer Firm Size', ''),
                'low_sub_dimensions': sorted_low_scores,
                'ai_pain_points': ai_pain_points,
                'related_topics': all_topics[:5]  # Top 5 topics
            })
    
    # Sort by overall rating (worst first), then by number of low scores
    pain_points.sort(key=lambda x: (x['overall_rating'], len(x['low_sub_dimensions'])))
    
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
        # Calculate average, excluding NaN values
        avg_score = dayforce_df[dim].dropna().mean()
        
        if pd.notna(avg_score) and avg_score < threshold:
            # Get related topics from low-scoring reviews
            low_reviews = dayforce_df[dayforce_df[dim] < threshold]
            topics = []
            
            for idx, row in low_reviews.iterrows():
                topics.extend(row.get('topics_list', []))
            
            from collections import Counter
            top_topics = Counter(topics).most_common(5)
            
            # Get sub-dimension details for this dimension
            sub_dims = get_sub_dimensions_for_dimension(dim)
            sub_dim_scores = {}
            for sub_dim in sub_dims:
                if sub_dim in dayforce_df.columns:
                    sub_dim_scores[sub_dim] = dayforce_df[sub_dim].dropna().mean()
            
            opportunities.append({
                'dimension': dim,
                'avg_score': avg_score,
                'gap_from_target': threshold - avg_score,
                'affected_reviews': len(low_reviews),
                'top_topics': top_topics,
                'sub_dimension_scores': sub_dim_scores
            })
    
    return sorted(opportunities, key=lambda x: x['gap_from_target'], reverse=True)

def get_sub_dimensions_for_dimension(dimension):
    """Return the 3 sub-dimensions for a given main dimension"""
    mapping = {
        'product': ['degree_of_meeting_functional_requirements', 'product_functionality', 'quality_of_product_user_experience'],
        'gtm': ['quality_of_the_evaluation_and_contracting_process', 'pricing_and_packaging_clarity', 'value_for_money'],
        'market_direction': ['fit_of_product_strategy_to_market_needs', 'clarity_of_product_roadmap', 'extent_of_planned_product_innovation'],
        'implementation': ['ease_and_quality_of_integration_and_deployment', 'quality_of_user_training_and_post_go_live_support', 'implementation_cost'],
        'customer_experience': ['quality_and_timeliness_of_support', 'customer_success_management_and_value_realization', 'customer_community']
    }
    return mapping.get(dimension, [])
