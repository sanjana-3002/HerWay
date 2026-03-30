import pandas as pd
import ast
import folium
from collections import Counter

# ---- LOAD DATA ----
df = pd.read_csv("chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["hour"] = pd.to_datetime(df["date"], unit="s").dt.hour
df["is_night"] = df["hour"].apply(lambda h: True if (h >= 20 or h < 4) else False)

summary = pd.read_csv("neighborhood_sentiment_summary.csv")
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
    "Humboldt Park": (41.8999, -87.7227),
    "Douglas": (41.8281, -87.6200),
    "East Side": (41.7317, -87.5500),
    "South Chicago": (41.7317, -87.5671),
    "Morgan Park": (41.6894, -87.6672),
    "Brighton Park": (41.8200, -87.6950),
    "East Garfield Park": (41.8799, -87.7133),
    "Irving Park": (41.9538, -87.7133),
}

# ---- NOISE TITLES TO FILTER ----
# posts that mention many neighborhoods and pollute summaries
noise_titles = [
    "Why do people say the city is more dangerous than it is",
    "Please help me become street-smart",
    "Questions about my safety in Chicago"
]

def is_noise(title):
    return any(n.lower() in str(title).lower() for n in noise_titles)

# ---- SUMMARY GENERATOR ----
def generate_popup_data(neighborhood, df):
    n_df = df[
        df["neighborhoods_mentioned"].apply(lambda x: neighborhood in x) &
        ~df["title"].apply(is_noise)
    ]

    if len(n_df) == 0:
        return None

    total = len(n_df)
    fearful = n_df[n_df["sentiment"] == "Negative/Fear"]
    reassuring = n_df[n_df["sentiment"] == "Positive/Reassuring"]
    night_df = n_df[n_df["is_night"]]
    night_fear = fearful[fearful["is_night"]]

    fear_pct = round(len(fearful) / total * 100) if total > 0 else 0
    night_pct = round(len(night_df) / total * 100) if total > 0 else 0
    night_fear_pct = round(len(night_fear) / len(night_df) * 100) if len(night_df) > 0 else 0

    # top keywords from fearful posts
    all_flags = []
    for flags in fearful["safety_flags"]:
        all_flags.extend(flags)
    top_keywords = [k for k, _ in Counter(all_flags).most_common(4)]

    # real post titles (exclude noise, pick most relevant)
    fearful_titles = []
    if len(fearful) > 0 and "title" in fearful.columns:
        fearful_titles = fearful[~fearful["title"].apply(is_noise)]["title"].head(2).tolist()

    reassuring_titles = []
    if len(reassuring) > 0 and "title" in reassuring.columns:
        reassuring_titles = reassuring[~reassuring["title"].apply(is_noise)]["title"].head(1).tolist()  

    # auto generate text summary
    if len(fearful) == 0:
        summary_text = "Community posts are mostly positive about this area."
    elif fear_pct >= 50:
        kw_text = ", ".join(top_keywords[:3]) if top_keywords else "safety concerns"
        summary_text = f"Community frequently mentions {kw_text} in this area."
    elif fear_pct >= 25:
        kw_text = ", ".join(top_keywords[:2]) if top_keywords else "some concerns"
        summary_text = f"Some community concern around {kw_text}, mixed with positive experiences."
    else:
        summary_text = "Mostly positive community experiences with some isolated concerns."

    return {
        "total": total,
        "fear_pct": fear_pct,
        "night_pct": night_pct,
        "night_fear_pct": night_fear_pct,
        "top_keywords": top_keywords,
        "fearful_titles": fearful_titles,
        "reassuring_titles": reassuring_titles,
        "summary_text": summary_text,
        "n_fearful": len(fearful),
        "n_reassuring": len(reassuring),
        "n_neutral": len(n_df[n_df["sentiment"] == "Neutral/Concern"])
    }

# ---- BUILD MAP ----
print("Building upgraded map...")
m = folium.Map(
    location=[41.8827, -87.6278],
    zoom_start=11,
    tiles="CartoDB dark_matter"
)

# color and risk config
color_map = {
    "High Risk": "#ff6b6b",
    "Medium Risk": "#ffa94d",
    "Lower Risk": "#6bcb77",
}

processed = 0
skipped = 0

for _, row in summary.iterrows():
    neighborhood = row["neighborhood"]
    risk = row["risk_rating"]
    color = color_map.get(risk, "gray")

    if neighborhood not in neighborhood_coords:
        skipped += 1
        continue

    lat, lon = neighborhood_coords[neighborhood]
    popup_data = generate_popup_data(neighborhood, df)

    if popup_data is None:
        skipped += 1
        continue

    # scale circle by post count
    radius = 6 + (popup_data["total"] / 8)

    # build fearful titles html
    fearful_titles_html = ""
    for title in popup_data["fearful_titles"]:
        fearful_titles_html += f"""
        <div style='background:#ff6b6b22; border-left:3px solid #ff6b6b;
                    padding:6px 8px; margin:4px 0; border-radius:4px;
                    font-size:11px; color:#ddd;'>
            "{title}"
        </div>"""

    reassuring_titles_html = ""
    for title in popup_data["reassuring_titles"]:
        reassuring_titles_html += f"""
        <div style='background:#6bcb7722; border-left:3px solid #6bcb77;
                    padding:6px 8px; margin:4px 0; border-radius:4px;
                    font-size:11px; color:#ddd;'>
            "{title}"
        </div>"""

    keywords_html = ""
    for kw in popup_data["top_keywords"]:
        keywords_html += f"""
        <span style='background:#ffffff15; padding:2px 8px;
                     border-radius:10px; font-size:11px;
                     margin:2px; display:inline-block;
                     color:#eee;'>{kw}</span>"""

    # full popup html
    popup_html = f"""
    <div style='width:300px; font-family:Arial, sans-serif;
                background:#1a1a2e; color:#eee;
                padding:16px; border-radius:12px;'>

        <h3 style='margin:0 0 4px 0; color:white;
                   font-size:16px;'>{neighborhood}</h3>

        <div style='background:{color}33; border:1px solid {color};
                    padding:5px 10px; border-radius:6px;
                    margin-bottom:12px; display:inline-block;
                    font-size:12px; color:{color}; font-weight:bold;'>
            {risk}
        </div>

        <div style='background:#ffffff08; padding:10px;
                    border-radius:8px; margin-bottom:12px;
                    font-size:12px; color:#ccc; font-style:italic;'>
            {popup_data["summary_text"]}
        </div>

        <div style='display:flex; gap:8px; margin-bottom:12px;'>
            <div style='flex:1; background:#ff6b6b22; padding:8px;
                        border-radius:8px; text-align:center;'>
                <div style='font-size:18px; font-weight:bold;
                            color:#ff6b6b;'>{popup_data["fear_pct"]}%</div>
                <div style='font-size:10px; color:#aaa;'>Fearful</div>
            </div>
            <div style='flex:1; background:#ffd93d22; padding:8px;
                        border-radius:8px; text-align:center;'>
                <div style='font-size:18px; font-weight:bold;
                            color:#ffd93d;'>{popup_data["total"]}</div>
                <div style='font-size:10px; color:#aaa;'>Total Posts</div>
            </div>
            <div style='flex:1; background:#4a9eff22; padding:8px;
                        border-radius:8px; text-align:center;'>
                <div style='font-size:18px; font-weight:bold;
                            color:#4a9eff;'>{popup_data["night_fear_pct"]}%</div>
                <div style='font-size:10px; color:#aaa;'>Night Fear</div>
            </div>
        </div>

        <div style='margin-bottom:10px;'>
            <div style='font-size:11px; color:#888;
                        margin-bottom:5px;'>TOP KEYWORDS</div>
            {keywords_html if keywords_html else
             "<span style='color:#666; font-size:11px;'>None detected</span>"}
        </div>

        <div style='margin-bottom:8px;'>
            <div style='font-size:11px; color:#888;
                        margin-bottom:4px;'>COMMUNITY VOICE</div>
            {fearful_titles_html if fearful_titles_html else
             "<div style='color:#666; font-size:11px;'>No fearful posts</div>"}
            {reassuring_titles_html}
        </div>

        <div style='border-top:1px solid #333; padding-top:8px;
                    margin-top:8px; font-size:10px; color:#666;'>
            Reddit data only · Crime + 311 data coming soon
        </div>
    </div>
    """

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.65,
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=folium.Tooltip(
            f"<b style='color:white'>{neighborhood}</b>"
            f"<br><span style='color:{color}'>{risk}</span>"
            f"<br><span style='color:#aaa; font-size:11px'>"
            f"{popup_data['total']} posts · {popup_data['fear_pct']}% fearful</span>",
            style="background:#1a1a2e; border:none; color:white;"
                  "padding:8px; border-radius:6px;"
        )
    ).add_to(m)

    processed += 1

# ---- LEGEND ----
legend_html = """
<div style='position:fixed; bottom:30px; left:30px; z-index:1000;
            background:#1a1a2e; padding:16px; border-radius:12px;
            color:white; font-family:Arial; font-size:13px;
            border:1px solid #333;'>
    <b style='font-size:15px'>HerSafe Chicago</b><br>
    <span style='color:#888; font-size:11px'>
        Reddit Community Safety Signals
    </span><br><br>
    <span style='color:#ff6b6b'>&#9679;</span> High Risk<br>
    <span style='color:#ffa94d'>&#9679;</span> Medium Risk<br>
    <span style='color:#6bcb77'>&#9679;</span> Lower Risk<br><br>
    <span style='color:#888; font-size:11px'>
        Circle size = post count<br>
        Hover to preview · Click for details
    </span>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

m.save("hersafe_upgraded_map.html")

print(f"Done! {processed} neighborhoods mapped, {skipped} skipped")
print("Open hersafe_upgraded_map.html in your browser!")