import pandas as pd
import json

# Load the Excel file
df = pd.read_excel('data/market_sensing_data_gartner_ai_sentiment.xlsx')

# Display basic information
print("=" * 80)
print("DATA STRUCTURE OVERVIEW")
print("=" * 80)
print(f"\nTotal rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\n" + "=" * 80)
print("COLUMN NAMES")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

print("\n" + "=" * 80)
print("DATA TYPES")
print("=" * 80)
print(df.dtypes)

print("\n" + "=" * 80)
print("SAMPLE DATA (First 3 rows)")
print("=" * 80)
print(df.head(3))

print("\n" + "=" * 80)
print("UNIQUE VALUES IN KEY COLUMNS")
print("=" * 80)

# Check for product column
product_cols = [col for col in df.columns if 'product' in col.lower()]
if product_cols:
    print(f"\nProducts in '{product_cols[0]}':")
    print(df[product_cols[0]].value_counts())

# Check for date columns
date_cols = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
if date_cols:
    print(f"\nDate range in '{date_cols[0]}':")
    print(f"From: {df[date_cols[0]].min()} to {df[date_cols[0]].max()}")

# Check sentiment columns
sentiment_cols = ['product', 'gtm', 'market_direction', 'implementation', 'customer_experience']
existing_sentiment_cols = [col for col in sentiment_cols if col in df.columns]
if existing_sentiment_cols:
    print(f"\nSentiment score ranges:")
    for col in existing_sentiment_cols:
        print(f"  {col}: {df[col].min():.2f} to {df[col].max():.2f}")

# Check ai_output structure
if 'ai_output' in df.columns:
    print("\n" + "=" * 80)
    print("AI_OUTPUT STRUCTURE (First example)")
    print("=" * 80)
    first_ai_output = df['ai_output'].iloc[0]
    if isinstance(first_ai_output, str):
        try:
            parsed = json.loads(first_ai_output)
            print(json.dumps(parsed, indent=2)[:1000] + "...")
        except:
            print(first_ai_output[:1000] + "...")
    else:
        print(first_ai_output)

print("\n" + "=" * 80)
print("MISSING VALUES")
print("=" * 80)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Percentage': missing_pct
})
print(missing_df[missing_df['Missing Count'] > 0])
