# Score Types Guide

## Two Types of Scores in the Dashboard

This dashboard uses **two distinct types of scores**, both on a 1-5 scale:

### 1. Review Ratings (Direct from Reviewers)
- **Source:** Direct ratings provided by Gartner reviewers
- **Column:** `Overall User Rating`
- **Other Rating Columns:** 
  - Evaluation & Contracting
  - Integration & Deployment
  - Service & Support
  - Product Capabilities
- **Description:** These are star ratings (1-5) that reviewers explicitly gave when submitting their review
- **Labels in Dashboard:** "Overall Rating (Reviewer)", "Reviewer Ratings"
- **Used In:** 
  - Reviews by Overall Rating chart (Executive Summary)
  - Review sorting and filtering
  - Severity classification (Critical/Moderate/Minor)

### 2. AI Sentiment Scores (Model-Generated)
- **Source:** AI analysis of review text (comments, pros/cons, lessons learned)
- **Columns:** 
  - `product` - Product capabilities and features sentiment
  - `gtm` - Go-to-market and positioning sentiment
  - `market_direction` - Strategic direction and vision sentiment
  - `implementation` - Implementation and deployment sentiment
  - `customer_experience` - Support and service sentiment
- **Description:** Natural language processing analyzes the actual review text to determine sentiment across 5 strategic dimensions
- **Labels in Dashboard:** All dimension labels include "(AI)" or "(AI Sentiment)" suffix
- **Used In:**
  - All sentiment dimension charts and metrics
  - Trend analysis
  - Competitive benchmarking
  - Topic sentiment analysis
  - Priority matrices

## How They Differ

| Aspect | Review Ratings | AI Sentiment Scores |
|--------|---------------|---------------------|
| **Source** | Reviewer's explicit rating | AI analysis of text |
| **Granularity** | Overall + 4 Gartner categories | 5 strategic dimensions |
| **Bias** | May not reflect text sentiment | Analyzes actual comments |
| **Consistency** | Direct rating choice | Standardized text analysis |
| **Coverage** | Only rated aspects | All text content |

## Why Both Matter

1. **Review Ratings** show what reviewers consciously think about the product
2. **AI Sentiment Scores** reveal underlying sentiment in their actual feedback
3. **Gaps between them** can indicate:
   - Rating fatigue (giving neutral 3s while text is positive/negative)
   - Halo effects (overall experience colors specific ratings)
   - Unrecognized pain points (negative text with okay ratings)

## Dashboard Labeling Strategy

All metrics, charts, and visualizations now clearly indicate which score type they display:

- ✅ Chart titles include "AI Sentiment" when showing AI scores
- ✅ Y-axis labels specify "AI Sentiment Score (1-5)" vs "Rating"
- ✅ Dimension labels include "(AI)" or "(AI Sentiment)" suffix
- ✅ Metric labels specify "AI Score" or "(Reviewer)" 
- ✅ Explanatory banners at top of pages clarify the distinction
- ✅ Executive Summary has expandable "About These Metrics" section

## Updated Pages

All pages have been updated to clarify score types:

1. **Executive Summary** - Explains both types, labels all AI dimensions
2. **Sentiment Analysis** - Banner explaining AI sentiment, labeled dimensions
3. **Dayforce Focus** - Info banner about AI scores, labeled dimensions
4. **Competitive Insights** - All charts and metrics labeled
5. **Topic Intelligence** - Topic sentiment clearly marked as AI
6. **Action Recommendations** - All priority matrices use labeled AI scores

## For Decision-Making

When reviewing insights:
- **Strategic decisions** → Focus on AI sentiment patterns (reveals true feedback)
- **Quick health checks** → Review ratings (overall satisfaction)
- **Discrepancies** → Investigate when ratings and AI sentiment diverge significantly
- **Trend analysis** → AI sentiment is more consistent over time
- **Competitive comparison** → Both types provide value from different angles
