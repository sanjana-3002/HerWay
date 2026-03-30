import pandas as pd

df = pd.read_csv("chicago_safety_sentiment.csv")
df["date_parsed"] = pd.to_datetime(df["date"], unit="s")
df["year"] = df["date_parsed"].dt.year
df["month"] = df["date_parsed"].dt.month

print("Date range:", df["date_parsed"].min(), "to", df["date_parsed"].max())
print("\nPosts per year:")
print(df["year"].value_counts().sort_index())
print("\nSentiment by year:")
print(df.groupby(["year", "sentiment"]).size().unstack(fill_value=0))