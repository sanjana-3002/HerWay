import pandas as pd
import ast
import re
import folium
from transformers import pipeline
from collections import Counter

# ---- LOAD LOCATED DATA ----
df = pd.read_csv("chicago_safety_located.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")

print(f"Posts to analyze: {len(df)}")
print("Running sentiment analysis, this will take ~5 minutes...\n")

# ---- SENTIMENT MODEL ----
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    truncation=True,
    max_length=512
)

label_map = {
    "LABEL_0": "Negative/Fear",
    "LABEL_1": "Neutral/Concern",
    "LABEL_2": "Positive/Reassuring"
}

def get_sentiment(text):
    try:
        result = sentiment_model(str(text)[:512])[0]
        return label_map.get(result["label"], result["label"]), round(result["score"], 3)
    except:
        return "Neutral/Concern", 0.0

sentiments, confidences = [], []
for i, text in enumerate(df["combined"]):
    if i % 50 == 0:
        print(f"  Processing {i+1}/{len(df)}...")
    label, conf = get_sentiment(text)
    sentiments.append(label)
    confidences.append(conf)

df["sentiment"] = sentiments
df["confidence"] = confidences
df.to_csv("chicago_safety_sentiment.csv", index=False)
print("Sentiment analysis complete!\n")

# ---- NEIGHBORHOOD SUMMARY ----
summary = {}
for _, row in df.iterrows():
    for n in row["neighborhoods_mentioned"]:
        if n not in summary:
            summary[n] = {
                "Negative/Fear": 0,
                "Neutral/Concern": 0,
                "Positive/Reassuring": 0,
                "total": 0,
                "total_safety_score": 0
            }
        summary[n][row["sentiment"]] += 1
        summary[n]["total"] += 1
        summary[n]["total_safety_score"] += row["safety_score"]

rows = []
for n, c in summary.items():
    total = c["total"]
    neg = c["Negative/Fear"]
    neg_ratio = neg / total if total > 0 else 0

    if total < 3:
        risk = "Insufficient Data"
        color = "gray"
    elif neg_ratio >= 0.5:
        risk = "High Risk"
        color = "red"
    elif neg_ratio >= 0.3:
        risk = "Medium Risk"
        color = "orange"
    else:
        risk = "Lower Risk"
        color = "green"

    rows.append({
        "neighborhood": n,
        "total_posts": total,
        "negative_fear": neg,
        "neutral_concern": c["Neutral/Concern"],
        "positive_reassuring": c["Positive/Reassuring"],
        "negative_ratio": round(neg_ratio, 2),
        "total_safety_score": c["total_safety_score"],
        "risk_rating": risk,
        "color": color
    })

summary_df = pd.DataFrame(rows)
summary_df = summary_df.sort_values("negative_ratio", ascending=False)
summary_df.to_csv("neighborhood_sentiment_summary.csv", index=False)

print("========== NEIGHBORHOOD SENTIMENT BREAKDOWN ==========\n")
print(summary_df[["neighborhood", "total_posts", "negative_fear",
                   "positive_reassuring", "negative_ratio",
                   "risk_rating"]].to_string(index=False))

print("\n\n========== OVERALL SENTIMENT ==========")
print(df["sentiment"].value_counts())

# ---- REBUILD MAP ----
neighborhood_coords = {
    "Loop": (41.8827, -87.6278),
    "River North": (41.8936, -87.6338),
    "Gold Coast": (41.9031, -87.6285),
    "Lincoln Park": (41.9214, -87.6513),
    "Lakeview": (41.9430, -87.6431),
    "Wicker Park": (41.9082, -87.6796),
    "Bucktown": (41.9178, -87.6827),
    "Logan Square": (41.9214, -87.7068),
    "Pilsen": (41.8557, -87.6600),
    "Bridgeport": (41.8345, -87.6440),
    "Hyde Park": (41.7943, -87.5907),
    "Woodlawn": (41.7734, -87.5960),
    "Englewood": (41.7795, -87.6438),
    "West Englewood": (41.7762, -87.6640),
    "Auburn Gresham": (41.7442, -87.6513),
    "Chatham": (41.7484, -87.6125),
    "South Shore": (41.7606, -87.5671),
    "Bronzeville": (41.8281, -87.6153),
    "Washington Park": (41.7895, -87.6200),
    "Grand Crossing": (41.7617, -87.6062),
    "Roseland": (41.7006, -87.6200),
    "Rogers Park": (42.0083, -87.6647),
    "Edgewater": (41.9794, -87.6592),
    "Uptown": (41.9651, -87.6572),
    "Ravenswood": (41.9731, -87.6741),
    "Irving Park": (41.9538, -87.7133),
    "Avondale": (41.9399, -87.7133),
    "Humboldt Park": (41.8999, -87.7227),
    "Garfield Park": (41.8799, -87.7227),
    "West Garfield Park": (41.8799, -87.7400),
    "East Garfield Park": (41.8799, -87.7133),
    "Austin": (41.8999, -87.7700),
    "West Town": (41.8963, -87.6672),
    "Ukrainian Village": (41.8932, -87.6763),
    "Little Village": (41.8287, -87.7178),
    "Back of the Yards": (41.8057, -87.6572),
    "McKinley Park": (41.8296, -87.6726),
    "Albany Park": (41.9681, -87.7227),
    "Portage Park": (41.9586, -87.7650),
    "Belmont Cragin": (41.9399, -87.7650),
    "Hermosa": (41.9196, -87.7227),
    "Norwood Park": (41.9860, -87.8065),
    "Clearing": (41.7851, -87.7650),
    "South Loop": (41.8673, -87.6278),
    "Near North Side": (41.9000, -87.6338),
    "Near West Side": (41.8746, -87.6672),
    "Streeterville": (41.8920, -87.6200),
    "Andersonville": (41.9794, -87.6672),
    "Chinatown": (41.8504, -87.6326),
    "West Loop": (41.8827, -87.6479),
    "Fulton Market": (41.8868, -87.6513),
    "Fulton Park": (41.8799, -87.7650),
    "South Chicago": (41.7317, -87.5671),
    "North Park": (41.9794, -87.7133),
    "Grand Boulevard": (41.8107, -87.6153),
    "Washington Heights": (41.7200, -87.6400),
    "Cragin": (41.9196, -87.7650),
    "Printer's Row": (41.8757, -87.6278),
    "North Center": (41.9538, -87.6726),
    "Navy Pier": (41.8919, -87.6051),
    "Magnificent Mile": (41.8956, -87.6243),
    "Millennium Park": (41.8826, -87.6226),
    "Boystown": (41.9440, -87.6490),
    "Greektown": (41.8785, -87.6490),
    "Little Italy": (41.8746, -87.6600),
    "Hyde Park": (41.7943, -87.5907),
    "Andersonville": (41.9794, -87.6672),
    "Uptown": (41.9651, -87.6572),
    "Humboldt Park": (41.8999, -87.7227),
}

print("\n\nBuilding updated map...")
m = folium.Map(location=[41.8827, -87.6278], zoom_start=11,
               tiles="CartoDB dark_matter")

for _, row in summary_df.iterrows():
    n = row["neighborhood"]
    if n not in neighborhood_coords:
        continue

    lat, lon = neighborhood_coords[n]
    color = row["color"]
    total = row["total_posts"]
    neg = row["negative_fear"]
    pos = row["positive_reassuring"]
    neutral = row["neutral_concern"]
    risk = row["risk_rating"]
    ratio = row["negative_ratio"]

    # scale circle size by number of posts (more data = bigger circle)
    radius = 5 + (total / 10)

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.65,
        popup=folium.Popup(
            f"<b style='font-size:14px'>{n}</b><br><br>"
            f"<b>Risk Rating:</b> {risk}<br>"
            f"<b>Total Posts:</b> {total}<br>"
            f"😨 Fearful: {neg} posts<br>"
            f"⚠️ Concerned: {neutral} posts<br>"
            f"✅ Reassuring: {pos} posts<br>"
            f"<b>Fear Ratio:</b> {ratio}",
            max_width=220
        ),
        tooltip=f"{n} — {risk}"
    ).add_to(m)

# legend
legend_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
     background-color: #1a1a1a; padding: 15px; border-radius: 10px;
     color: white; font-family: Arial; font-size: 13px; 
     border: 1px solid #444;">
    <b style="font-size:15px">HerSafe Chicago</b><br>
    <i style="font-size:11px">Reddit Community Safety Signals</i><br><br>
    🔴 High Risk (&gt;50% fearful posts)<br>
    🟠 Medium Risk (30–50% fearful)<br>
    🟢 Lower Risk (&lt;30% fearful)<br>
    ⚫ Insufficient Data (&lt;3 posts)<br><br>
    <i style="font-size:11px">Circle size = number of posts<br>
    Click circles for details</i>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
m.save("hersafe_chicago_map.html")

print("Map saved! Open hersafe_chicago_map.html in your browser.")
print("\nDone! Files updated:")
print("  - chicago_safety_sentiment.csv")
print("  - neighborhood_sentiment_summary.csv")
print("  - hersafe_chicago_map.html")