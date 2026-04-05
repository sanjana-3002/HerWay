import pandas as pd
import ast
from collections import Counter

df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["hour"] = pd.to_datetime(df["date"], unit="s").dt.hour
df["is_night"] = df["hour"].apply(lambda h: True if (h >= 20 or h < 4) else False)

for test in ["Englewood", "Loop", "Logan Square"]:
    n_df = df[df["neighborhoods_mentioned"].apply(lambda x: test in x)]
    fearful = n_df[n_df["sentiment"] == "Negative/Fear"]
    
    print(f"\n{'='*40}")
    print(f"NEIGHBORHOOD: {test}")
    print(f"Total posts: {len(n_df)}")
    print(f"Fearful: {len(fearful)}")
    print(f"Night posts: {n_df['is_night'].sum()}")
    
    all_flags = []
    for flags in fearful["safety_flags"]:
        all_flags.extend(flags)
    print(f"Top keywords: {Counter(all_flags).most_common(4)}")
    
    print(f"Sample fearful titles:")
    for title in fearful["title"].head(3).tolist():
        print(f"  - {title}")