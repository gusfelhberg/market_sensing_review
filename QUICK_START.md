# Quick Start Guide - HCM Market Sensing Dashboard

## Getting Started

### 1. Start the Application

```bash
# Navigate to the project directory
cd /Users/gustavo.felhberg/Library/CloudStorage/OneDrive-CeridianHCMInc/dev/marked_sensing

# Activate virtual environment
source venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### 2. Navigate the Dashboard

The dashboard has 5 main tabs:

#### 📈 Executive Summary
**Purpose:** High-level overview for quick decision-making

**Key Metrics:**
- Sentiment scores across all 5 dimensions (Product, GTM, Market Direction, Implementation, Customer Experience)
- Competitive ranking
- Sentiment trends over time
- Market position insights

**Use Cases:**
- Quick status check on market position
- Identify top priorities at a glance
- Track overall sentiment trends
- Understand competitive standing

#### 🎯 Sentiment Analysis
**Purpose:** Deep dive into specific sentiment dimensions

**Features:**
- Select any dimension for detailed analysis
- Compare Dayforce vs competitors
- View trend over time
- Explore correlation between dimensions
- Read detailed reviews filtered by score

**Use Cases:**
- Investigate why a particular dimension is underperforming
- Compare performance across products
- Identify patterns in customer feedback
- Find specific reviews for deeper understanding

#### 💡 Topic Intelligence
**Purpose:** Understand what customers are talking about

**Features:**
- Trending topics visualization
- Topics associated with positive vs negative sentiment
- Topic co-occurrence analysis (which topics appear together)
- Deep dive into specific topics

**Use Cases:**
- Identify emerging themes in customer feedback
- Find topics that drive negative sentiment
- Understand customer priorities
- Discover related areas of concern

#### ⚔️ Competitive Insights
**Purpose:** Benchmark against competitors

**Features:**
- Radar chart showing competitive position
- Dimension-by-dimension comparison
- Strengths and weaknesses analysis
- Head-to-head product comparison
- Downloadable competitive scorecard

**Use Cases:**
- Understand competitive advantages
- Identify areas where competitors excel
- Support strategic planning
- Create competitive sales materials

#### 🎬 Action Recommendations
**Purpose:** Turn insights into action

**Features:**
- Priority matrix showing improvement opportunities
- Specific recommendations with timelines
- Pain point severity analysis
- Trend predictions
- Quick win opportunities

**Use Cases:**
- Prioritize improvement initiatives
- Allocate resources effectively
- Create action plans
- Track impact of improvements over time

### 3. Using Filters

The sidebar provides powerful filtering capabilities:

**Date Range:** 
- Use date picker to focus on specific time periods
- Compare recent vs historical performance

**Product Filter:**
- Select "All" to see market-wide trends
- Select specific products for focused analysis
- Select multiple products for comparison

**Reviewer Attributes:**
- Filter by industry to understand vertical-specific issues
- Filter by role to see perspective of different user types
- Filter by company size to segment by organization scale

**Tips:**
- Start with "All" filters to see the big picture
- Apply filters progressively to drill down
- Use date range to identify trends
- Combine filters to find specific insights (e.g., "Healthcare" + "Large Enterprise")

### 4. Interpreting Sentiment Scores

**Score Ranges (1-5 scale):**
- 🌟 5.0 - Excellent
- 👍 4.0-4.9 - Good
- 😐 3.5-3.9 - Average
- ⚠️ 3.0-3.4 - Below Average
- ❌ <3.0 - Poor

**Target:** Aim for 4.0+ across all dimensions

### 5. Common Workflows

#### Weekly Executive Review
1. Open Executive Summary tab
2. Check key metrics vs last week
3. Review competitive position
4. Note any significant changes
5. Export data if needed

#### Product Planning Session
1. Go to Sentiment Analysis
2. Select "Product Capabilities" dimension
3. Filter to Dayforce reviews
4. Check trend over time
5. Review detailed feedback for low-scoring reviews
6. Go to Topic Intelligence to see related topics
7. Go to Action Recommendations for prioritized improvements

#### Competitive Analysis for Sales
1. Go to Competitive Insights
2. Select dimension relevant to sales opportunity
3. Compare Dayforce vs specific competitor
4. Note strengths to emphasize
5. Download competitive scorecard
6. Use insights to prepare pitch

#### Quarterly Strategy Meeting
1. Review Executive Summary for overall trends
2. Check each dimension in Sentiment Analysis
3. Analyze Topic Intelligence for emerging themes
4. Study Competitive Insights for market position
5. Review Action Recommendations for quarterly priorities
6. Set targets and KPIs for next quarter

### 6. Exporting Data

- Competitive scorecard can be downloaded as CSV
- Take screenshots of charts for presentations
- Use filters to create custom views before exporting

### 7. Best Practices

**Regular Review:**
- Check dashboard weekly for trend awareness
- Monthly deep dives into specific dimensions
- Quarterly strategic reviews

**Data Quality:**
- Ensure data file is regularly updated
- Verify date ranges are current
- Check for any data anomalies

**Actionable Insights:**
- Don't just observe - take action
- Assign owners to improvement opportunities
- Track impact of changes over time
- Close the feedback loop with customers

**Sharing Insights:**
- Schedule regular stakeholder briefings
- Create standardized reporting templates
- Share specific insights with relevant teams
- Use data to support strategic decisions

### 8. Troubleshooting

**App won't start:**
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify data file is in the correct location

**No data showing:**
- Check that filters aren't too restrictive
- Ensure data file has recent reviews
- Verify file path is correct

**Charts not loading:**
- Refresh the browser
- Check browser console for errors
- Try a different browser

**Performance issues:**
- Reduce date range
- Apply more specific filters
- Close other applications

### 9. Getting Help

For technical issues or questions:
- Check the README.md for detailed documentation
- Contact the Market Intelligence team
- Review Streamlit documentation at https://docs.streamlit.io

---

**Remember:** This dashboard is a tool to support decision-making. The real value comes from acting on the insights it provides!
