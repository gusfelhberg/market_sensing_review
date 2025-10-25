# HCM Market Sensing Dashboard

An executive-level strategic intelligence platform for analyzing customer sentiment across HCM product reviews from Gartner and other sources.

## Overview

This Streamlit application provides comprehensive analysis of customer reviews for Dayforce and competitor HCM products (SAP SuccessFactors, Workday, UKG Pro, ADP WFN) across 5 key dimensions:

- **Product Capabilities** - Core product features and functionality
- **Go-to-Market (GTM)** - Sales, marketing, and positioning effectiveness
- **Market Direction** - Vision, roadmap, and strategic direction
- **Implementation** - Onboarding and deployment experience
- **Customer Experience** - Support, service, and overall satisfaction

## Key Features

### 🎯 Dayforce Focus (NEW)
- Dayforce-centric performance dashboard
- Competitive advantages and gaps analysis
- Dimension-by-dimension competitive positioning
- Critical pain points with severity levels
- Customer segment performance (industry, size)
- Specific gap closure recommendations
- "Where We Win" vs "Where We Trail" insights

### 📈 Executive Summary
- High-level KPIs across all sentiment dimensions
- Competitive position ranking
- Sentiment trends over time
- Key insights and focus areas

### 🎯 Sentiment Analysis
- Deep dive into each dimension
- Comparative analysis across products
- Trend analysis over time
- Correlation between dimensions
- Detailed review exploration

### 💡 Topic Intelligence
- Trending topics and themes
- Topic-sentiment correlation
- Topic co-occurrence analysis
- Deep dive into specific topics
- Pain point identification

### ⚔️ Competitive Insights
- Market position radar charts
- Dimension-by-dimension comparison
- Strengths and weaknesses analysis
- Head-to-head product comparison
- Competitive scorecard

### 🎬 Action Recommendations
- Strategic priority matrix
- Data-driven improvement recommendations
- Pain point severity analysis
- Trend predictions
- Quick win opportunities

## Installation

1. Ensure you have Python 3.9+ installed

2. Create and activate virtual environment (if not already done):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your data file `market_sensing_data_gartner_ai_sentiment.xlsx` is in the project root directory

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. The application will open in your default web browser at `http://localhost:8501`

## Data Structure

The application works with two data files:
- `market_sensing_data_synthetic.xlsx` - Synthetic dataset with 145 reviews (used by default)
- `market_sensing_data_gartner_ai_sentiment.xlsx` - Original Gartner data

To generate new synthetic data:
```bash
python generate_synthetic_data.py
```

See `SYNTHETIC_DATA_GUIDE.md` for details on the synthetic dataset.

The Excel file contains the following columns:

**Review Information:**
- Review Date
- Review URL
- Product
- Headline
- Overall Comment
- Lessons Learned

**Reviewer Attributes:**
- Reviewer Role
- Reviewer Industry
- Reviewer Function
- Reviewer Firm Size
- Country

**Numerical Ratings (1-5):**
- Overall User Rating
- Evaluation & Contracting
- Integration & Deployment
- Service & Support
- Product Capabilities

**AI-Generated Sentiment (1-5):**
- product
- gtm
- market_direction
- implementation
- customer_experience

**AI Analysis:**
- ai_output (JSON with reasoning and insights)
- review_insights
- review_pain_points
- topics

## Filters

The sidebar provides comprehensive filtering:
- **Date Range** - Filter reviews by time period
- **Products** - Select specific products to analyze
- **Industry** - Filter by reviewer industry
- **Reviewer Role** - Filter by job function
- **Company Size** - Filter by organization size

## Strategic Use Cases

### For Product Teams
- Identify feature gaps vs competitors
- Understand customer pain points
- Prioritize product roadmap based on sentiment data
- Track product perception over time

### For Customer Success
- Understand implementation challenges
- Identify areas needing better support
- Track customer experience trends
- Proactively address common issues

### For Marketing/GTM
- Understand competitive positioning
- Identify messaging opportunities
- Find customer success story candidates
- Track brand perception vs competitors

### For Executive Leadership
- Overall market position assessment
- Strategic priority identification
- Trend analysis and predictions
- ROI of improvement initiatives

## Project Structure

```
marked_sensing/
├── app.py                          # Main application
├── utils.py                        # Data processing utilities
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── pages/                          # Page modules
│   ├── __init__.py
│   ├── executive_summary.py       # Executive dashboard
│   ├── sentiment_analysis.py      # Sentiment deep dive
│   ├── topic_intelligence.py      # Topic analysis
│   ├── competitive_insights.py    # Competitive comparison
│   └── action_recommendations.py  # Strategic recommendations
└── market_sensing_data_gartner_ai_sentiment.xlsx  # Data file
```

## Notes

- All sentiment scores are on a 1-5 scale
- Scores ≥4.5 are considered "Excellent"
- Scores 4.0-4.4 are considered "Good"  
- Scores 3.5-3.9 are considered "Average"
- Scores 3.0-3.4 are considered "Below Average"
- Scores <3.0 are considered "Poor"

## Support

For issues or questions, contact the Market Intelligence team.

---

**Built for Dayforce Strategic Intelligence**
