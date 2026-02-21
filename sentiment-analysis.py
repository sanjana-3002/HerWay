import pandas as pd
import ast
from transformers import pipeline

# ---- LOAD DATA ----
df = pd.read_csv("chicago_safety_located.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)

# combine title + text
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")

# truncate to 512 chars (model limit)
df["combined"] = df["combined"].str[:512]

print(f"Loaded {len(df)} posts, running sentiment analysis...")
print("This may take 2-3 minutes on first run (downloading model)...\n")

# ---- LOAD SENTIMENT MODEL ----
# this model is trained on tweets so it understands informal language well
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    truncation=True,
    max_length=512
)

# ---- LABELS ----
# this model returns: LABEL_0 = negative, LABEL_1 = neutral, LABEL_2 = positive
label_map = {
    "LABEL_0": "😨 Negative/Fear",
    "LABEL_1": "⚠️ Neutral/Concern",
    "LABEL_2": "✅ Positive/Reassuring"
}

# ---- RUN SENTIMENT ----
def get_sentiment(text):
    try:
        result = sentiment_model(text)[0]
        label = label_map.get(result["label"], result["label"])
        confidence = round(result["score"], 3)
        return label, confidence
    except Exception as e:
        return "⚠️ Neutral/Concern", 0.0

sentiments = []
confidences = []

for i, text in enumerate(df["combined"]):
    if i % 20 == 0:
        print(f"Processing post {i+1}/{len(df)}...")
    label, conf = get_sentiment(text)
    sentiments.append(label)
    confidences.append(conf)

df["sentiment"] = sentiments
df["confidence"] = confidences

# ---- SAVE FULL RESULTS ----
df.to_csv("chicago_safety_sentiment.csv", index=False)

# ---- NEIGHBORHOOD SENTIMENT SUMMARY ----
print("\n\n========== NEIGHBORHOOD SENTIMENT BREAKDOWN ==========\n")

neighborhood_summary = {}

for _, row in df.iterrows():
    for neighborhood in row["neighborhoods_mentioned"]:
        if neighborhood not in neighborhood_summary:
            neighborhood_summary[neighborhood] = {
                "😨 Negative/Fear": 0,
                "⚠️ Neutral/Concern": 0,
                "✅ Positive/Reassuring": 0,
                "total": 0
            }
        neighborhood_summary[neighborhood][row["sentiment"]] += 1
        neighborhood_summary[neighborhood]["total"] += 1

# turn into dataframe
summary_rows = []
for neighborhood, counts in neighborhood_summary.items():
    total = counts["total"]
    negative = counts["😨 Negative/Fear"]
    neutral = counts["⚠️ Neutral/Concern"]
    positive = counts["✅ Positive/Reassuring"]

    # risk rating based on proportion of negative posts
    negative_ratio = negative / total if total > 0 else 0
    if negative_ratio >= 0.5:
        risk = "🔴 High Risk"
    elif negative_ratio >= 0.3:
        risk = "🟠 Medium Risk"
    else:
        risk = "🟢 Lower Risk"

    summary_rows.append({
        "neighborhood": neighborhood,
        "total_posts": total,
        "negative_fear": negative,
        "neutral_concern": neutral,
        "positive_reassuring": positive,
        "negative_ratio": round(negative_ratio, 2),
        "risk_rating": risk
    })

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values("negative_ratio", ascending=False)

print(summary_df[["neighborhood", "total_posts", "negative_fear", 
                   "positive_reassuring", "risk_rating"]].to_string(index=False))

summary_df.to_csv("neighborhood_sentiment_summary.csv", index=False)

print("\n\n========== OVERALL SENTIMENT BREAKDOWN ==========")
print(df["sentiment"].value_counts())

print("\n\n========== SAMPLE POSTS BY SENTIMENT ==========")

print("\n--- 3 Most Fearful Posts ---")
fearful = df[df["sentiment"] == "😨 Negative/Fear"].nlargest(3, "confidence")
for _, row in fearful.iterrows():
    print(f"Title: {row['title']}")
    print(f"Neighborhoods: {row['neighborhoods_mentioned']}")
    print(f"Confidence: {row['confidence']}")
    print("---")

print("\n--- 3 Most Reassuring Posts ---")
reassuring = df[df["sentiment"] == "✅ Positive/Reassuring"].nlargest(3, "confidence")
for _, row in reassuring.iterrows():
    print(f"Title: {row['title']}")
    print(f"Neighborhoods: {row['neighborhoods_mentioned']}")
    print(f"Confidence: {row['confidence']}")
    print("---")

print("\nDone! Files saved:")
print("  - chicago_safety_sentiment.csv (full data with sentiment per post)")
print("  - neighborhood_sentiment_summary.csv (summary per neighborhood)")