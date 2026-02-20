import pandas as pd

df = pd.read_csv("chicago_safety_reddit.csv")
print("Total posts:", len(df))
print("\nColumn names:", df.columns.tolist())
print("\nSample titles:")
print(df["title"].head(10).tolist())
print("\nSample text:")
print(df["text"].head(3).tolist())