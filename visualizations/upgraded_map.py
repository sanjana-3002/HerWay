import pandas as pd
import ast
import folium
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# ---- LOAD DATA ----
df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["hour"] = pd.to_datetime(df["date"], unit="s").dt.hour
df["day_of_week"] = pd.to_datetime(df["date"], unit="s").dt.day_name()
df["is_night"] = df["hour"].apply(lambda h: True if (h >= 20 or h < 4) else False)
df["title"] = df["title"].fillna("")
df["text"] = df["text"].fillna("")
df["combined"] = df["title"] + " " + df["text"]

summary = pd.read_csv("data/processed/neighborhood_sentiment_summary.csv")
summary = summary[summary["risk_rating"] != "Insufficient Data"]

# ---- NEIGHBORHOOD COORDINATES ----
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
    "Douglas": (41.8281, -87.6200),
    "East Side": (41.7317, -87.5500),
    "Morgan Park": (41.6894, -87.6672),
    "Brighton Park": (41.8200, -87.6950),
    "East Garfield Park": (41.8799, -87.7133),
}

# ---- TFIDF UNIQUE KEYWORDS PER NEIGHBORHOOD ----
print("Computing TF-IDF keywords per neighborhood...")

stopwords = set([
    "chicago", "the", "a", "an", "and", "or", "but", "in", "on", "at",
    "to", "for", "of", "with", "is", "it", "this", "that", "was", "are",
    "be", "have", "has", "had", "do", "did", "will", "would", "could",
    "should", "i", "my", "me", "we", "you", "your", "he", "she", "they",
    "just", "like", "really", "very", "so", "not", "no", "if", "from",
    "by", "about", "as", "up", "out", "there", "when", "what", "which",
    "who", "how", "one", "any", "all", "more", "also", "get", "go",
    "been", "than", "then", "some", "can", "into", "re", "ve", "ll",
    "don", "doesn", "didn", "isn", "aren", "wasn", "weren", "much",
    "even", "never", "always", "still", "now", "here", "see", "going",
    "want", "know", "think", "feel", "people", "area", "neighborhood",
    "place", "street", "city", "chicago", "block", "south", "north",
    "east", "west", "near", "around", "back", "good", "great", "bad",
    "time", "year", "day", "night", "pretty", "sure", "thing", "lot",
    "look", "come", "need", "make", "say", "take", "walk", "live",
    "move", "way", "side", "part", "right", "left", "new", "old"
])

def clean_for_tfidf(text):
    text = re.sub(r'http\S+', '', str(text))
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.lower().split()
    return " ".join([w for w in words if w not in stopwords and len(w) > 3])

# build one document per neighborhood
neighborhood_docs = {}
all_neighborhoods = summary["neighborhood"].tolist()

for n in all_neighborhoods:
    n_df = df[df["neighborhoods_mentioned"].apply(lambda x: n in x)]
    if len(n_df) > 0:
        combined_text = " ".join(n_df["combined"].tolist())
        neighborhood_docs[n] = clean_for_tfidf(combined_text)

# run tfidf
if len(neighborhood_docs) > 1:
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    doc_list = list(neighborhood_docs.values())
    doc_names = list(neighborhood_docs.keys())
    tfidf_matrix = tfidf.fit_transform(doc_list)
    feature_names = tfidf.get_feature_names_out()

    tfidf_keywords = {}
    for i, n in enumerate(doc_names):
        scores = tfidf_matrix[i].toarray()[0]
        top_indices = scores.argsort()[-5:][::-1]
        tfidf_keywords[n] = [feature_names[j] for j in top_indices if scores[j] > 0]
else:
    tfidf_keywords = {}

print(f"  TF-IDF done for {len(tfidf_keywords)} neighborhoods")

# ---- PRIMARY NEIGHBORHOOD FILTER ----
def is_primary(row, neighborhood):
    """Only use post if neighborhood is the ONLY one mentioned
       AND the neighborhood name appears in the title itself"""
    mentioned = row["neighborhoods_mentioned"]
    title = str(row["title"]).lower()
    neighborhood_lower = neighborhood.lower()

    # must be only neighborhood mentioned
    if len(mentioned) != 1:
        return False

    # neighborhood name should appear in title for it to be truly about that area
    if neighborhood_lower not in title:
        return False

    return True

# ---- DATA RELIABILITY BADGE ----
def reliability_badge(total_posts):
    if total_posts >= 20:
        return ("Strong", "#6bcb77", "&#9679;&#9679;&#9679;")
    elif total_posts >= 8:
        return ("Moderate", "#ffd93d", "&#9679;&#9679;&#9675;")
    else:
        return ("Limited", "#ff6b6b", "&#9679;&#9675;&#9675;")

# ---- SUMMARY GENERATOR ----
def generate_popup_data(neighborhood, df):
    n_df = df[df["neighborhoods_mentioned"].apply(lambda x: neighborhood in x)]

    if len(n_df) == 0:
        return None

    total = len(n_df)
    fearful = n_df[n_df["sentiment"] == "Negative/Fear"]
    reassuring = n_df[n_df["sentiment"] == "Positive/Reassuring"]
    neutral = n_df[n_df["sentiment"] == "Neutral/Concern"]
    night_df = n_df[n_df["is_night"]]
    day_df = n_df[~n_df["is_night"]]
    night_fear = fearful[fearful["is_night"]]
    day_fear = fearful[~fearful["is_night"]]

    fear_pct = round(len(fearful) / total * 100) if total > 0 else 0
    neutral_pct = round(len(neutral) / total * 100) if total > 0 else 0
    reassuring_pct = round(len(reassuring) / total * 100) if total > 0 else 0
    night_fear_pct = round(len(night_fear) / len(night_df) * 100) if len(night_df) > 0 else 0
    day_fear_pct = round(len(day_fear) / len(day_df) * 100) if len(day_df) > 0 else 0

    # primary posts only for community voice
    primary_df = n_df[n_df.apply(lambda r: is_primary(r, neighborhood), axis=1)]
    primary_fearful = primary_df[primary_df["sentiment"] == "Negative/Fear"]
    primary_reassuring = primary_df[primary_df["sentiment"] == "Positive/Reassuring"]

    fearful_titles = primary_fearful["title"].head(2).tolist() if len(primary_fearful) > 0 else []
    reassuring_titles = primary_reassuring["title"].head(1).tolist() if len(primary_reassuring) > 0 else []

    # safety keywords from lexicon
    all_flags = []
    for flags in fearful["safety_flags"]:
        all_flags.extend(flags)
    top_safety_keywords = [k for k, _ in Counter(all_flags).most_common(4)]

    # tfidf unique keywords
    unique_keywords = tfidf_keywords.get(neighborhood, [])[:4]

    # auto summary text
    # map keywords to readable phrases
    keyword_phrases = {
        "avoid": "areas people suggest avoiding",
        "dangerous": "perceived danger",
        "unsafe": "feelings of unsafety",
        "alone": "concerns about walking alone",
        "dark": "poor lighting at night",
        "mugged": "robbery incidents",
        "harassed": "street harassment",
        "scared": "feeling scared",
        "sketchy": "sketchy conditions",
        "shooting": "gun violence",
        "followed": "being followed",
        "creepy": "threatening behavior",
        "knife": "weapon-related incidents",
        "fear": "general fear",
        "threat": "threatening situations",
        "aggressive": "aggressive behavior"
    }

    def keywords_to_phrase(keywords):
        phrases = [keyword_phrases.get(k, k) for k in keywords[:2]]
        return " and ".join(phrases) if phrases else "safety concerns"
    if fear_pct >= 50:
        phrase = keywords_to_phrase(top_safety_keywords)
        summary_text = f"Community posts show significant concern — people mention {phrase} in this area."
    elif fear_pct >= 25:
        phrase = keywords_to_phrase(top_safety_keywords)
        summary_text = f"Mixed signals — some posts mention {phrase}, alongside positive experiences."
    elif fear_pct >= 10:
        summary_text = "Mostly positive community experiences with occasional isolated concerns."
    else:
        summary_text = "Community posts are largely positive and reassuring about this area."

    # peak concern time
    if night_fear_pct > day_fear_pct + 15:
        time_signal = f"Concerns spike at night ({night_fear_pct}% of night posts are fearful)"
    elif day_fear_pct > night_fear_pct + 15:
        time_signal = f"Concerns more common during the day ({day_fear_pct}% of day posts fearful)"
    else:
        time_signal = f"Concerns spread evenly across day and night"

    return {
        "total": total,
        "fear_pct": fear_pct,
        "neutral_pct": neutral_pct,
        "reassuring_pct": reassuring_pct,
        "night_fear_pct": night_fear_pct,
        "day_fear_pct": day_fear_pct,
        "top_safety_keywords": top_safety_keywords,
        "unique_keywords": unique_keywords,
        "fearful_titles": fearful_titles,
        "reassuring_titles": reassuring_titles,
        "summary_text": summary_text,
        "time_signal": time_signal,
        "n_fearful": len(fearful),
        "n_reassuring": len(reassuring),
        "n_neutral": len(neutral),
        "reliability": reliability_badge(total)
    }

# ---- BUILD MAP ----
print("Building upgraded map v2...")

m = folium.Map(
    location=[41.8827, -87.6278],
    zoom_start=11,
    tiles="CartoDB dark_matter"
)

# pulsing animation CSS for high risk circles
pulse_css = """
<style>
@keyframes pulse {
    0%   { stroke-opacity: 1; stroke-width: 2; }
    50%  { stroke-opacity: 0.3; stroke-width: 8; }
    100% { stroke-opacity: 1; stroke-width: 2; }
}
.high-risk-pulse {
    animation: pulse 2s infinite;
}
</style>
"""
m.get_root().html.add_child(folium.Element(pulse_css))

color_map = {
    "High Risk":   "#ff6b6b",
    "Medium Risk": "#ffa94d",
    "Lower Risk":  "#6bcb77",
}

processed = 0

for _, row in summary.iterrows():
    neighborhood = row["neighborhood"]
    risk = row["risk_rating"]
    color = color_map.get(risk, "gray")

    if neighborhood not in neighborhood_coords:
        continue

    lat, lon = neighborhood_coords[neighborhood]
    pd_data = generate_popup_data(neighborhood, df)

    if pd_data is None:
        continue

    reliability_label, reliability_color, reliability_dots = pd_data["reliability"]

    # sentiment bar widths
    fear_w = pd_data["fear_pct"]
    neutral_w = pd_data["neutral_pct"]
    reassuring_w = pd_data["reassuring_pct"]

    # keywords html — safety lexicon
    safety_kw_html = ""
    for kw in pd_data["top_safety_keywords"]:
        safety_kw_html += f"""<span style='background:#ff6b6b22; border:1px solid #ff6b6b55;
            padding:2px 8px; border-radius:10px; font-size:11px;
            margin:2px; display:inline-block; color:#ffaaaa;'>{kw}</span>"""

    # keywords html — tfidf unique
    tfidf_kw_html = ""
    for kw in pd_data["unique_keywords"]:
        tfidf_kw_html += f"""<span style='background:#4a9eff22; border:1px solid #4a9eff55;
            padding:2px 8px; border-radius:10px; font-size:11px;
            margin:2px; display:inline-block; color:#aaccff;'>{kw}</span>"""

    # community voice html
    fearful_html = ""
    for title in pd_data["fearful_titles"]:
        fearful_html += f"""
        <div style='background:#ff6b6b18; border-left:3px solid #ff6b6b;
                    padding:6px 8px; margin:3px 0; border-radius:0 6px 6px 0;
                    font-size:11px; color:#ddd;'>"{title}"</div>"""

    reassuring_html = ""
    for title in pd_data["reassuring_titles"]:
        reassuring_html += f"""
        <div style='background:#6bcb7718; border-left:3px solid #6bcb77;
                    padding:6px 8px; margin:3px 0; border-radius:0 6px 6px 0;
                    font-size:11px; color:#ddd;'>"{title}"</div>"""

    if not fearful_html and not reassuring_html:
        voice_html = "<div style='color:#666; font-size:11px;'>No primary posts found</div>"
    else:
        voice_html = fearful_html + reassuring_html

    popup_html = f"""
    <div style='width:320px; font-family:Arial, sans-serif;
                background:#0f0f1a; color:#eee;
                padding:16px; border-radius:12px;
                border:1px solid #333;'>

        <!-- HEADER -->
        <div style='display:flex; justify-content:space-between;
                    align-items:flex-start; margin-bottom:10px;'>
            <h3 style='margin:0; color:white; font-size:17px;'>{neighborhood}</h3>
            <div style='text-align:right;'>
                <div style='background:{color}33; border:1px solid {color};
                            padding:3px 10px; border-radius:6px;
                            font-size:11px; color:{color}; font-weight:bold;
                            margin-bottom:4px;'>{risk}</div>
                <div style='font-size:10px; color:{reliability_color};'>
                    {reliability_dots} {reliability_label} data</div>
            </div>
        </div>

        <!-- SUMMARY TEXT -->
        <div style='background:#ffffff08; padding:10px 12px;
                    border-radius:8px; margin-bottom:12px;
                    font-size:12px; color:#ccc; font-style:italic;
                    border-left:3px solid {color};'>
            {pd_data["summary_text"]}
        </div>

        <!-- STAT BOXES -->
        <div style='display:flex; gap:6px; margin-bottom:12px;'>
            <div style='flex:1; background:#ff6b6b18; padding:8px 4px;
                        border-radius:8px; text-align:center;
                        border:1px solid #ff6b6b33;'>
                <div style='font-size:20px; font-weight:bold;
                            color:#ff6b6b;'>{pd_data["fear_pct"]}%</div>
                <div style='font-size:9px; color:#aaa; margin-top:2px;'>FEARFUL</div>
            </div>
            <div style='flex:1; background:#ffffff0a; padding:8px 4px;
                        border-radius:8px; text-align:center;
                        border:1px solid #ffffff15;'>
                <div style='font-size:20px; font-weight:bold;
                            color:#fff;'>{pd_data["total"]}</div>
                <div style='font-size:9px; color:#aaa; margin-top:2px;'>POSTS</div>
            </div>
            <div style='flex:1; background:#4a9eff18; padding:8px 4px;
                        border-radius:8px; text-align:center;
                        border:1px solid #4a9eff33;'>
                <div style='font-size:20px; font-weight:bold;
                            color:#4a9eff;'>{pd_data["night_fear_pct"]}%</div>
                <div style='font-size:9px; color:#aaa; margin-top:2px;'>NIGHT FEAR</div>
            </div>
            <div style='flex:1; background:#6bcb7718; padding:8px 4px;
                        border-radius:8px; text-align:center;
                        border:1px solid #6bcb7733;'>
                <div style='font-size:20px; font-weight:bold;
                            color:#6bcb77;'>{pd_data["reassuring_pct"]}%</div>
                <div style='font-size:9px; color:#aaa; margin-top:2px;'>POSITIVE</div>
            </div>
        </div>

        <!-- SENTIMENT BAR -->
        <div style='margin-bottom:12px;'>
            <div style='font-size:10px; color:#888;
                        margin-bottom:5px; text-transform:uppercase;
                        letter-spacing:1px;'>Sentiment Distribution</div>
            <div style='display:flex; height:8px; border-radius:4px;
                        overflow:hidden; background:#ffffff10;'>
                <div style='width:{fear_w}%; background:#ff6b6b;'></div>
                <div style='width:{neutral_w}%; background:#ffd93d;'></div>
                <div style='width:{reassuring_w}%; background:#6bcb77;'></div>
            </div>
            <div style='display:flex; justify-content:space-between;
                        font-size:9px; color:#666; margin-top:3px;'>
                <span style='color:#ff6b6b;'>Fearful {fear_w}%</span>
                <span style='color:#ffd93d;'>Neutral {neutral_w}%</span>
                <span style='color:#6bcb77;'>Positive {reassuring_w}%</span>
            </div>
        </div>

        <!-- TIME SIGNAL -->
        <div style='background:#ffffff08; padding:7px 10px;
                    border-radius:6px; margin-bottom:10px;
                    font-size:11px; color:#bbb;'>
            &#128337; {pd_data["time_signal"]}
        </div>

        <!-- KEYWORDS -->
        <div style='margin-bottom:10px;'>
            <div style='font-size:10px; color:#888; margin-bottom:4px;
                        text-transform:uppercase; letter-spacing:1px;'>
                Safety Signals</div>
            {safety_kw_html if safety_kw_html else
             "<span style='color:#555; font-size:11px;'>None detected</span>"}
        </div>

        <div style='margin-bottom:10px;'>
            <div style='font-size:10px; color:#888; margin-bottom:4px;
                        text-transform:uppercase; letter-spacing:1px;'>
                Unique to this area</div>
            {tfidf_kw_html if tfidf_kw_html else
             "<span style='color:#555; font-size:11px;'>Insufficient data</span>"}
        </div>

        <!-- COMMUNITY VOICE -->
        <div style='margin-bottom:10px;'>
            <div style='font-size:10px; color:#888; margin-bottom:4px;
                        text-transform:uppercase; letter-spacing:1px;'>
                Community Voice</div>
            {voice_html}
        </div>

        <!-- FOOTER -->
        <div style='border-top:1px solid #222; padding-top:8px;
                    font-size:10px; color:#555; display:flex;
                    justify-content:space-between;'>
            <span>Reddit data only</span>
            <span>Crime + 311 coming soon</span>
        </div>
    </div>
    """

    # pulsing effect for high risk via JS
    radius = 6 + (pd_data["total"] / 8)

    circle = folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.65,
        weight=2,
        popup=folium.Popup(popup_html, max_width=340),
        tooltip=folium.Tooltip(
            f"<div style='background:#1a1a2e; padding:8px 12px; "
            f"border-radius:8px; border:1px solid #333;'>"
            f"<b style='color:white; font-size:13px;'>{neighborhood}</b><br>"
            f"<span style='color:{color}; font-size:11px;'>{risk}</span><br>"
            f"<span style='color:#aaa; font-size:11px;'>"
            f"{pd_data['total']} posts &nbsp;|&nbsp; "
            f"{pd_data['fear_pct']}% fearful</span></div>",
            sticky=False
        )
    )
    circle.add_to(m)
    processed += 1

# ---- LEGEND ----
legend_html = """
<div style='position:fixed; bottom:30px; left:30px; z-index:1000;
            background:#0f0f1a; padding:18px; border-radius:12px;
            color:white; font-family:Arial; font-size:13px;
            border:1px solid #333; min-width:200px;'>
    <div style='font-size:16px; font-weight:bold;
                margin-bottom:3px;'>HerSafe Chicago</div>
    <div style='color:#666; font-size:11px;
                margin-bottom:14px;'>Reddit Community Safety Signals</div>

    <div style='margin-bottom:6px;'>
        <span style='color:#ff6b6b; font-size:16px;'>&#9679;</span>
        <span style='margin-left:6px;'>High Risk</span>
    </div>
    <div style='margin-bottom:6px;'>
        <span style='color:#ffa94d; font-size:16px;'>&#9679;</span>
        <span style='margin-left:6px;'>Medium Risk</span>
    </div>
    <div style='margin-bottom:14px;'>
        <span style='color:#6bcb77; font-size:16px;'>&#9679;</span>
        <span style='margin-left:6px;'>Lower Risk</span>
    </div>

    <div style='border-top:1px solid #333; padding-top:10px;
                font-size:10px; color:#666; line-height:1.8;'>
        Circle size = post volume<br>
        Hover to preview<br>
        Click for full analysis
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

m.save("outputs/maps/hersafe_upgraded_map_v2.html")
print(f"\nDone! {processed} neighborhoods mapped")
print("Open hersafe_upgraded_map_v2.html in your browser!")