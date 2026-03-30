import pandas as pd
df = pd.read_csv("chicago_safety_sentiment.csv")
print(df.columns.tolist())
print(df.head(2))