# Data Source Mapping

This document shows exactly which XLSX columns are used throughout the application.

## XLSX Column Categories

### 📄 XLSX - Customer Review
These columns contain direct customer input from reviews:
- `Headline` - Review title written by customer
- `Overall Comment` - Main review text from customer
- `Lessons Learned` - Customer's lessons learned
- `Overall User Rating` - Customer's overall star rating (1-5)
- `Evaluation & Contracting` - Customer rating for evaluation phase
- `Integration & Deployment` - Customer rating for integration
- `Service & Support` - Customer rating for support
- `Product Capabilities` - Customer rating for product features

### 🤖 XLSX - AI Analysis
These columns contain AI-generated analysis of the reviews:
- `ai_output` - JSON with AI sentiment analysis
- `product` - AI sentiment score (1-5) for product capabilities
- `gtm` - AI sentiment score (1-5) for go-to-market
- `market_direction` - AI sentiment score (1-5) for market direction
- `implementation` - AI sentiment score (1-5) for implementation
- `customer_experience` - AI sentiment score (1-5) for customer experience
- `review_insights` - AI-extracted key insights from review text
- `review_pain_points` - AI-extracted pain points from review text
- `topics` - AI-identified topics discussed in review

## Data Usage by Page

### Dayforce Focus
- **Customer Review Data**: Overall User Rating, review ratings
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience, review_pain_points, topics

### Executive Summary
- **Customer Review Data**: Overall User Rating, Evaluation & Contracting, Integration & Deployment, Service & Support, Product Capabilities
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience

### Sentiment Analysis
- **Customer Review Data**: Overall User Rating
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience
- **Review Content**: Headline, Overall Comment

### Topic Intelligence
- **AI Analysis Data**: topics, product, gtm, market_direction, implementation, customer_experience
- **Review Content**: Headline, Overall Comment, Review Date

### Competitive Insights
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience
- **Customer Review Data**: Product name, Overall User Rating

### Action Insights
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience, review_insights, review_pain_points, topics
- **Customer Review Data**: Overall User Rating, Review Date

### Review Browser
- **Customer Review Data**: All review columns (Headline, Overall Comment, Lessons Learned, ratings)
- **AI Analysis Data**: product, gtm, market_direction, implementation, customer_experience, topics

## Important Notes

1. **All data comes from the XLSX file** - No external data sources or hardcoded recommendations
2. **AI scores are pre-computed** - The sentiment scores (1-5) for product, gtm, etc. come directly from XLSX columns
3. **Insights are extracted** - review_insights and review_pain_points are AI-extracted and stored in XLSX
4. **Topics are pre-identified** - Topics come from the 'topics' column in XLSX
5. **All visualizations and metrics** - Calculated from the XLSX column data only

## Removed Features

The following features were removed because they were NOT from the XLSX file:
- Hardcoded action recommendations (generic advice not based on specific data)
- Custom "quick wins" generation (template-based recommendations)
- Any analysis that didn't directly use XLSX column data
