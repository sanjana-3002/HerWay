import pandas as pd
import ast
import re
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- LOAD DATA ----
df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
df["hour"] = pd.to_datetime(df["date"], unit="s").dt.hour
df["year"] = pd.to_datetime(df["date"], unit="s").dt.year
df["is_night"] = df["hour"].apply(lambda h: True if (h >= 20 or h < 4) else False)

# ---- GENDER KEYWORD LISTS ----
female_keywords = [
    # identity
    "woman", "women", "female", "girl", "lady", "ladies",
    "she", "her", "herself",
    # experiences specific to women
    "solo female", "as a woman", "being a woman",
    "young woman", "young women", "older woman",
    "catcall", "catcalled", "catcalling",
    "followed by a man", "followed by men",
    "street harassment", "sexual harassment",
    "felt unsafe as", "walk alone as",
    "traveling alone as", "moving alone as",
    "wife", "girlfriend", "daughter",
    "femicide", "assault on women",
    "harassment as a woman"
]

male_keywords = [
    "man", "men", "male", "guy", "guys", "dude",
    "he", "him", "himself",
    "as a man", "being a man",
    "husband", "boyfriend", "son"
]

neutral_keywords = [
    "person", "people", "someone", "anyone",
    "they", "them", "their",
    "resident", "visitor", "tourist",
    "commuter", "pedestrian"
]

def detect_perspective(text):
    text_lower = str(text).lower()

    female_score = sum(
        1 for kw in female_keywords
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
    )
    male_score = sum(
        1 for kw in male_keywords
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
    )

    if female_score > 0 and female_score >= male_score:
        return "Female Perspective"
    elif male_score > 0 and male_score > female_score:
        return "Male Perspective"
    else:
        return "Neutral/Unknown"

# ---- APPLY GENDER DETECTION ----
print("Detecting gender perspective in posts...")
df["perspective"] = df["combined"].apply(detect_perspective)

print(f"\nPerspective breakdown:")
print(df["perspective"].value_counts())

# ---- FEMALE SPECIFIC ANALYSIS ----
female_df = df[df["perspective"] == "Female Perspective"]
male_df = df[df["perspective"] == "Male Perspective"]
neutral_df = df[df["perspective"] == "Neutral/Unknown"]

print(f"\nFemale perspective posts: {len(female_df)}")
print(f"Male perspective posts:   {len(male_df)}")
print(f"Neutral posts:            {len(neutral_df)}")

# fear ratio by perspective
def fear_ratio(subset):
    if len(subset) == 0:
        return 0
    return round(len(subset[subset["sentiment"] == "Negative/Fear"]) / len(subset) * 100, 1)

print(f"\nFear ratio by perspective:")
print(f"  Female: {fear_ratio(female_df)}%")
print(f"  Male:   {fear_ratio(male_df)}%")
print(f"  Neutral:{fear_ratio(neutral_df)}%")

# ---- NEIGHBORHOOD ANALYSIS BY GENDER ----
print("\nTop neighborhoods in female perspective posts:")
female_neighborhoods = Counter()
for neighborhoods in female_df["neighborhoods_mentioned"]:
    for n in neighborhoods:
        female_neighborhoods[n] += 1

for n, count in female_neighborhoods.most_common(10):
    n_female = female_df[female_df["neighborhoods_mentioned"].apply(lambda x: n in x)]
    fr = fear_ratio(n_female)
    print(f"  {n}: {count} posts, {fr}% fearful")

# ---- NIGHT SAFETY BY GENDER ----
female_night = female_df[female_df["is_night"]]
male_night = male_df[male_df["is_night"]]

print(f"\nNight-time fear rates:")
print(f"  Female at night: {fear_ratio(female_night)}%")
print(f"  Male at night:   {fear_ratio(male_night)}%")

# ---- TOP SAFETY CONCERNS FOR WOMEN ----
all_female_flags = []
for flags in female_df[female_df["sentiment"] == "Negative/Fear"]["safety_flags"]:
    all_female_flags.extend(flags)

print(f"\nTop safety concerns in female perspective posts:")
for flag, count in Counter(all_female_flags).most_common(10):
    print(f"  {flag}: {count}")

# ---- SAMPLE FEMALE PERSPECTIVE POSTS ----
print(f"\nSample female perspective fearful posts:")
female_fearful = female_df[female_df["sentiment"] == "Negative/Fear"].nlargest(5, "confidence")
for _, row in female_fearful.iterrows():
    print(f"  - {row['title']}")
    print(f"    Neighborhoods: {row['neighborhoods_mentioned']}")
    print(f"    Keywords: {row['safety_flags']}")
    print()

# ---- SAVE FEMALE FOCUSED CSV ----
female_df.to_csv("data/processed/chicago_female_safety.csv", index=False)

# ---- BUILD VISUALIZATIONS ----
print("Building gender analysis charts...")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Fear Ratio by Perspective",
        "Perspective Breakdown",
        "Top Neighborhoods — Female Perspective",
        "Night vs Day Fear by Perspective"
    ],
    specs=[
        [{"type": "xy"}, {"type": "domain"}],
        [{"type": "xy"}, {"type": "xy"}]
    ],
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)

# ---- CHART 1: Fear ratio comparison ----
perspectives = ["Female Perspective", "Male Perspective", "Neutral/Unknown"]
fear_ratios = [fear_ratio(female_df), fear_ratio(male_df), fear_ratio(neutral_df)]
bar_colors = ["#ff94d2", "#4a9eff", "#aaaaaa"]

fig.add_trace(go.Bar(
    x=perspectives,
    y=fear_ratios,
    marker_color=bar_colors,
    text=[f"{r}%" for r in fear_ratios],
    textposition="outside",
    textfont=dict(color="white", size=12),
    showlegend=False
), row=1, col=1)

fig.add_hline(
    y=20,
    line_dash="dash",
    line_color="rgba(255,107,107,0.5)",
    annotation_text="Overall avg (20%)",
    annotation_font_color="rgba(255,107,107,0.8)",
    row=1, col=1
)

# ---- CHART 2: Perspective breakdown pie ----
fig.add_trace(go.Pie(
    labels=["Female", "Male", "Neutral"],
    values=[len(female_df), len(male_df), len(neutral_df)],
    marker_colors=["#ff94d2", "#4a9eff", "#aaaaaa"],
    hole=0.4,
    textinfo="label+percent",
    showlegend=False
), row=1, col=2)

# ---- CHART 3: Top neighborhoods female ----
top_female_hoods = female_neighborhoods.most_common(10)
hood_names = [h[0] for h in top_female_hoods]
hood_counts = [h[1] for h in top_female_hoods]
hood_fear = []
for n in hood_names:
    n_df = female_df[female_df["neighborhoods_mentioned"].apply(lambda x: n in x)]
    hood_fear.append(fear_ratio(n_df))

fig.add_trace(go.Bar(
    x=hood_names,
    y=hood_counts,
    name="Post Count",
    marker_color=[
        "#ff6b6b" if f >= 30 else "#ffa94d" if f >= 15 else "#6bcb77"
        for f in hood_fear
    ],
    text=hood_counts,
    textposition="outside",
    textfont=dict(color="white", size=10),
    showlegend=False
), row=2, col=1)

# ---- CHART 4: Night vs Day fear by perspective ----
categories = ["Female\nDay", "Female\nNight", "Male\nDay", "Male\nNight"]
female_day = female_df[~female_df["is_night"]]
values = [
    fear_ratio(female_day),
    fear_ratio(female_night),
    fear_ratio(male_df[~male_df["is_night"]]),
    fear_ratio(male_night)
]
chart_colors = ["#ff94d2", "#ff5599", "#4a9eff", "#0055cc"]

fig.add_trace(go.Bar(
    x=categories,
    y=values,
    marker_color=chart_colors,
    text=[f"{v}%" for v in values],
    textposition="outside",
    textfont=dict(color="white", size=11),
    showlegend=False
), row=2, col=2)

# ---- LAYOUT ----
fig.update_layout(
    title=dict(
        text="HerSafe Chicago — Gender Perspective Analysis",
        font=dict(size=20, color="white")
    ),
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white", family="Arial"),
    height=800
)

for i in range(1, 3):
    for j in range(1, 3):
        fig.update_xaxes(gridcolor="#333333", linecolor="#333", row=i, col=j)
        fig.update_yaxes(gridcolor="#333333", linecolor="#333", row=i, col=j)

fig.write_html("outputs/charts/gender_analysis.html")
print("Saved gender_analysis.html!")
print("Also saved chicago_female_safety.csv")