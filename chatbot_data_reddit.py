import pandas as pd
import ast
import re
from collections import Counter

# ---- LOAD DATA ----
df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
df["hour"] = pd.to_datetime(df["date"], unit="s").dt.hour
df["is_night"] = df["hour"].apply(lambda h: h >= 20 or h < 4)
df["year"] = pd.to_datetime(df["date"], unit="s").dt.year

# ---- NAME MAPPING ----
official_to_reddit = {
    "Lake View":              "Lakeview",
    "Lower West Side":        "Pilsen",
    "South Lawndale":         "Little Village",
    "Greater Grand Crossing": "Grand Crossing",
    "New City":               "Back of the Yards",
    "Armour Square":          "Chinatown",
    "West Town":              "Wicker Park",
    "Near North Side":        "River North",
    "Near South Side":        "South Loop",
    "Near West Side":         "West Loop",
    "Lincoln Square":         "Ravenswood",
    "East Garfield Park":     "Garfield Park",
    "Belmont Cragin":         "Cragin",
    "Gage Park":              "Marquette Park",
    "Edgewater":              "Andersonville",
}

female_keywords = [
    "woman", "women", "female", "girl", "she", "her",
    "solo female", "as a woman", "catcall", "followed by a man",
    "street harassment", "wife", "girlfriend", "daughter"
]

# ---- LOAD NEIGHBORHOOD LIST ----
merged = pd.read_csv("data/processed/herway_final_merged.csv")
all_neighborhoods = merged["neighborhood"].tolist()

print("Building Reddit chatbot data...")
rows = []

for official_name in all_neighborhoods:
    reddit_name = official_to_reddit.get(official_name, official_name)

    # get all posts for this neighborhood
    n_df = df[
        df["neighborhoods_mentioned"].apply(
            lambda x: official_name in x or reddit_name in x
        )
    ]

    if len(n_df) == 0:
        # still add a row so every neighborhood is represented
        rows.append({
            "neighborhood":                  official_name,
            "reddit_has_data":               False,
            "reddit_total_posts":            0,
            "reddit_fearful_count":          0,
            "reddit_reassuring_count":       0,
            "reddit_neutral_count":          0,
            "reddit_fear_ratio_pct":         0,
            "reddit_night_posts":            0,
            "reddit_night_fear_pct":         0,
            "reddit_female_posts":           0,
            "reddit_female_fearful_count":   0,
            "reddit_top_safety_keywords":    "",
            "reddit_fearful_titles":         "",
            "reddit_reassuring_titles":      "",
            "reddit_fearful_text_snippets":  "",
            "reddit_female_fearful_titles":  "",
            "reddit_year_range":             "",
            "reddit_summary": f"No Reddit community data available for {official_name}."
        })
        continue

    fearful_df    = n_df[n_df["sentiment"] == "Negative/Fear"]
    reassuring_df = n_df[n_df["sentiment"] == "Positive/Reassuring"]
    neutral_df    = n_df[n_df["sentiment"] == "Neutral/Concern"]
    night_df      = n_df[n_df["is_night"]]
    night_fearful = fearful_df[fearful_df["is_night"]]

    # top keywords from fearful posts
    all_flags = []
    for flags in fearful_df["safety_flags"]:
        all_flags.extend(flags)
    top_keywords = ", ".join([k for k, _ in Counter(all_flags).most_common(5)])

    # primary posts — neighborhood in title and only one neighborhood mentioned
    def is_primary(row):
        mentioned = row["neighborhoods_mentioned"]
        title = str(row["title"]).lower()
        if len(mentioned) != 1:
            return False
        return official_name.lower() in title or reddit_name.lower() in title

    primary_df         = n_df[n_df.apply(is_primary, axis=1)]
    primary_fearful    = primary_df[primary_df["sentiment"] == "Negative/Fear"]
    primary_reassuring = primary_df[primary_df["sentiment"] == "Positive/Reassuring"]

    # fearful titles — primary first then fill with general
    fearful_titles_list = list(dict.fromkeys(
        primary_fearful["title"].head(3).tolist() +
        fearful_df["title"].head(3).tolist()
    ))[:5]
    fearful_titles = " | ".join(fearful_titles_list)

    # reassuring titles
    reassuring_titles_list = list(dict.fromkeys(
        primary_reassuring["title"].head(2).tolist() +
        reassuring_df["title"].head(2).tolist()
    ))[:3]
    reassuring_titles = " | ".join(reassuring_titles_list)

    # short text snippets from top fearful posts (highest confidence)
    fearful_texts = " ||| ".join([
        str(text)[:250]
        for text in fearful_df.nlargest(3, "confidence")["combined"].tolist()
        if str(text).strip() and str(text) != "nan"
    ])

    # night stats
    night_fear_pct = round(len(night_fearful) / len(night_df) * 100) \
                     if len(night_df) > 0 else 0

    # female perspective
    female_df = n_df[n_df["combined"].apply(
        lambda x: any(
            re.search(r'\b' + re.escape(kw) + r'\b', str(x).lower())
            for kw in female_keywords
        )
    )]
    female_fearful = female_df[female_df["sentiment"] == "Negative/Fear"]
    female_fearful_titles = " | ".join(
        female_fearful["title"].head(3).tolist()
    )

    # fear ratio
    fear_pct = round(len(fearful_df) / len(n_df) * 100, 1)

    # auto summary for chatbot to use directly
    if fear_pct >= 50:
        tone = "frequently express concern"
    elif fear_pct >= 25:
        tone = "share mixed experiences"
    else:
        tone = "are mostly positive"

    kw_text = top_keywords.split(",")[0].strip() if top_keywords else "safety"
    summary = (
        f"Reddit community members {tone} about {official_name}. "
        f"{len(n_df)} posts analyzed between "
        f"{int(n_df['year'].min())} and {int(n_df['year'].max())}. "
        f"{fear_pct}% of posts express fear or concern. "
        f"Most commonly mentioned safety concern: {kw_text}. "
        f"Night-time fear rate: {night_fear_pct}%."
    )

    rows.append({
        "neighborhood":                  official_name,
        "reddit_has_data":               True,
        "reddit_total_posts":            len(n_df),
        "reddit_fearful_count":          len(fearful_df),
        "reddit_reassuring_count":       len(reassuring_df),
        "reddit_neutral_count":          len(neutral_df),
        "reddit_fear_ratio_pct":         fear_pct,
        "reddit_night_posts":            len(night_df),
        "reddit_night_fear_pct":         night_fear_pct,
        "reddit_female_posts":           len(female_df),
        "reddit_female_fearful_count":   len(female_fearful),
        "reddit_top_safety_keywords":    top_keywords,
        "reddit_fearful_titles":         fearful_titles,
        "reddit_reassuring_titles":      reassuring_titles,
        "reddit_fearful_text_snippets":  fearful_texts,
        "reddit_female_fearful_titles":  female_fearful_titles,
        "reddit_year_range":             f"{int(n_df['year'].min())}–{int(n_df['year'].max())}",
        "reddit_summary":                summary
    })

# ---- SAVE ----
chatbot_df = pd.DataFrame(rows)
chatbot_df = chatbot_df.sort_values("neighborhood").reset_index(drop=True)
chatbot_df.to_csv("reddit_chatbot_data.csv", index=False)

print(f"\nDone!")
print(f"Total neighborhoods: {len(chatbot_df)}")
print(f"With Reddit data:    {chatbot_df['reddit_has_data'].sum()}")
print(f"Without Reddit data: {(~chatbot_df['reddit_has_data']).sum()}")

print("\n--- Sample: Loop ---")
loop = chatbot_df[chatbot_df["neighborhood"] == "Loop"].iloc[0]
for col in chatbot_df.columns:
    print(f"  {col}: {str(loop[col])[:90]}")

print("\nSaved: reddit_chatbot_data.csv")
