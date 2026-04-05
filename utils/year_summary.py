import pandas as pd

df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
df["year"] = pd.to_datetime(df["date"], unit="s").dt.year

for year in [2023, 2024, 2025]:
    y = df[df["year"] == year]
    total = len(y)
    fear = len(y[y["sentiment"] == "Negative/Fear"])
    pos = len(y[y["sentiment"] == "Positive/Reassuring"])
    print(f"{year}: {total} posts | Fear: {fear} ({round(fear/total*100)}%) | Positive: {pos} ({round(pos/total*100)}%)")