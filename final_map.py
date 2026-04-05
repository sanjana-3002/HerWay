import pandas as pd
import ast
import folium
from collections import Counter

# ---- LOAD DATA ----
merged = pd.read_csv("hersafe_final_merged.csv")
sentiment_df = pd.read_csv("chicago_safety_sentiment.csv")
sentiment_df["neighborhoods_mentioned"] = sentiment_df["neighborhoods_mentioned"].apply(ast.literal_eval)
sentiment_df["safety_flags"] = sentiment_df["safety_flags"].apply(ast.literal_eval)
sentiment_df["hour"] = pd.to_datetime(sentiment_df["date"], unit="s").dt.hour
sentiment_df["is_night"] = sentiment_df["hour"].apply(lambda h: h >= 20 or h < 4)
sentiment_df["title"] = sentiment_df["title"].fillna("")

# ---- NEIGHBORHOOD COORDINATES ----
neighborhood_coords = {
    "Albany Park": (41.9681, -87.7227),
    "Archer Heights": (41.8100, -87.7200),
    "Armour Square": (41.8504, -87.6326),
    "Ashburn": (41.7481, -87.7139),
    "Auburn Gresham": (41.7442, -87.6513),
    "Austin": (41.8999, -87.7700),
    "Avalon Park": (41.7445, -87.5800),
    "Avondale": (41.9399, -87.7133),
    "Belmont Cragin": (41.9399, -87.7650),
    "Beverly": (41.7000, -87.6700),
    "Bridgeport": (41.8345, -87.6440),
    "Brighton Park": (41.8200, -87.6950),
    "Burnside": (41.7200, -87.6050),
    "Calumet Heights": (41.7317, -87.5800),
    "Chatham": (41.7484, -87.6125),
    "Chicago Lawn": (41.7750, -87.6900),
    "Clearing": (41.7851, -87.7650),
    "Douglas": (41.8281, -87.6153),
    "Dunning": (41.9500, -87.8000),
    "East Garfield Park": (41.8799, -87.7133),
    "East Side": (41.7317, -87.5500),
    "Edgewater": (41.9794, -87.6592),
    "Edison Park": (41.9900, -87.8100),
    "Englewood": (41.7795, -87.6438),
    "Forest Glen": (41.9900, -87.7650),
    "Fuller Park": (41.8100, -87.6300),
    "Gage Park": (41.7900, -87.7100),
    "Garfield Ridge": (41.7850, -87.7700),
    "Grand Boulevard": (41.8107, -87.6153),
    "Greater Grand Crossing": (41.7617, -87.6062),
    "Hegewisch": (41.6500, -87.5500),
    "Hermosa": (41.9196, -87.7227),
    "Humboldt Park": (41.8999, -87.7227),
    "Hyde Park": (41.7943, -87.5907),
    "Irving Park": (41.9538, -87.7133),
    "Jefferson Park": (41.9700, -87.7650),
    "Kenwood": (41.8000, -87.5900),
    "Lake View": (41.9430, -87.6431),
    "Lincoln Park": (41.9214, -87.6513),
    "Lincoln Square": (41.9731, -87.6741),
    "Logan Square": (41.9214, -87.7068),
    "Loop": (41.8827, -87.6278),
    "Lower West Side": (41.8557, -87.6600),
    "McKinley Park": (41.8296, -87.6726),
    "Montclare": (41.9196, -87.8000),
    "Morgan Park": (41.6894, -87.6672),
    "Mount Greenwood": (41.6950, -87.7100),
    "Near North Side": (41.9000, -87.6338),
    "Near South Side": (41.8673, -87.6278),
    "Near West Side": (41.8746, -87.6672),
    "New City": (41.8057, -87.6572),
    "North Center": (41.9538, -87.6726),
    "North Lawndale": (41.8500, -87.7200),
    "North Park": (41.9794, -87.7133),
    "Norwood Park": (41.9860, -87.8065),
    "Oakland": (41.8150, -87.5900),
    "O'Hare": (41.9742, -87.9073),
    "Portage Park": (41.9586, -87.7650),
    "Pullman": (41.7050, -87.6050),
    "Riverdale": (41.6400, -87.6050),
    "Rogers Park": (42.0083, -87.6647),
    "Roseland": (41.7006, -87.6200),
    "South Chicago": (41.7317, -87.5671),
    "South Deering": (41.6900, -87.5500),
    "South Lawndale": (41.8287, -87.7178),
    "South Shore": (41.7606, -87.5671),
    "Uptown": (41.9651, -87.6572),
    "Washington Heights": (41.7200, -87.6400),
    "Washington Park": (41.7895, -87.6200),
    "West Elsdon": (41.7850, -87.7300),
    "West Englewood": (41.7762, -87.6640),
    "West Garfield Park": (41.8799, -87.7400),
    "West Lawn": (41.7750, -87.7050),
    "West Pullman": (41.6750, -87.6350),
    "West Ridge": (41.9981, -87.6900),
    "West Town": (41.8963, -87.6672),
    "Woodlawn": (41.7734, -87.5960),
}

# ---- COLOR MAP ----
color_map = {
    "High Risk":    "#ff6b6b",
    "Medium Risk":  "#ffa94d",
    "Lower Risk":   "#6bcb77",
    "Partial Data": "#7a8fa6",
}

# ---- OFFICIAL TO REDDIT NAME MAPPING ----
official_to_reddit = {
    "Lake View":            "Lakeview",
    "Lower West Side":      "Pilsen",
    "South Lawndale":       "Little Village",
    "Greater Grand Crossing": "Grand Crossing",
    "New City":             "Back of the Yards",
    "Armour Square":        "Chinatown",
    "West Town":            "Wicker Park",
    "Near North Side":      "River North",
    "Near South Side":      "South Loop",
    "Near West Side":       "West Loop",
    "Lincoln Square":       "Ravenswood",
    "East Garfield Park":   "Garfield Park",
    "Belmont Cragin":       "Cragin",
    "Gage Park":            "Marquette Park",
    "Edgewater":            "Andersonville",
}

# ---- REDDIT HELPERS ----
def is_primary(row, neighborhood):
    mentioned = row["neighborhoods_mentioned"]
    title = str(row["title"]).lower()
    if len(mentioned) != 1:
        return False
    if neighborhood.lower() not in title:
        return False
    return True

def get_reddit_posts(official_name):
    reddit_name = official_to_reddit.get(official_name, official_name)
    n_df = sentiment_df[
        sentiment_df["neighborhoods_mentioned"].apply(
            lambda x: official_name in x or reddit_name in x
        )
    ]
    return n_df, reddit_name

def get_community_voice(official_name):
    n_df, reddit_name = get_reddit_posts(official_name)
    if len(n_df) == 0:
        return [], []
    primary = n_df[n_df.apply(
        lambda r: is_primary(r, official_name) or is_primary(r, reddit_name),
        axis=1
    )]
    fearful = primary[primary["sentiment"] == "Negative/Fear"]["title"].head(2).tolist()
    reassuring = primary[primary["sentiment"] == "Positive/Reassuring"]["title"].head(1).tolist()
    return fearful, reassuring

def get_top_keywords(official_name):
    n_df, _ = get_reddit_posts(official_name)
    fearful = n_df[n_df["sentiment"] == "Negative/Fear"]
    all_flags = []
    for flags in fearful["safety_flags"]:
        all_flags.extend(flags)
    return [k for k, _ in Counter(all_flags).most_common(4)]

# ---- VALIDATION SIGNAL ----
def get_validation(row):
    reddit_fear = float(row.get("reddit_fear_ratio") or 0)
    crime_norm = float(row.get("crime_score_norm") or 0)
    if reddit_fear >= 0.3 and crime_norm >= 0.5:
        return "#ff6b6b", "Both official data and community posts signal concern here"
    elif reddit_fear < 0.2 and crime_norm < 0.4:
        return "#6bcb77", "Official data and community posts both suggest lower concern"
    elif reddit_fear >= 0.3 and crime_norm < 0.4:
        return "#ffa94d", "Community feels more unsafe than official data alone suggests"
    elif reddit_fear < 0.2 and crime_norm >= 0.4:
        return "#4a9eff", "Official data shows risk — community perception is relatively calm"
    else:
        return "#ffd93d", "Mixed signals across data sources"

# ---- HTML HELPERS ----
def crime_type_pills(crime_types_str):
    if not crime_types_str or str(crime_types_str) == "nan":
        return ""
    return "".join([
        f"""<span style='background:#ff6b6b18; border:1px solid #ff6b6b33;
            padding:2px 8px; border-radius:10px; font-size:11px;
            margin:2px; display:inline-block; color:#ffaaaa;'>
            {t.strip()}</span>"""
        for t in str(crime_types_str).split("|")[:3]
    ])

def keyword_pills(keywords):
    if not keywords:
        return "<span style='color:#555; font-size:11px;'>None detected</span>"
    return "".join([
        f"""<span style='background:#ffd93d18; border:1px solid #ffd93d33;
            padding:2px 8px; border-radius:10px; font-size:11px;
            margin:2px; display:inline-block; color:#ffd93d;'>{kw}</span>"""
        for kw in keywords
    ])

def voice_cards(fearful_titles, reassuring_titles):
    html = ""
    for t in fearful_titles:
        html += f"""
        <div style='background:#ff6b6b12; border-left:3px solid #ff6b6b;
                    padding:7px 10px; margin:4px 0; border-radius:0 8px 8px 0;
                    font-size:11px; color:#ddd; line-height:1.4;'>
            "{t}"
        </div>"""
    for t in reassuring_titles:
        html += f"""
        <div style='background:#6bcb7712; border-left:3px solid #6bcb77;
                    padding:7px 10px; margin:4px 0; border-radius:0 8px 8px 0;
                    font-size:11px; color:#ddd; line-height:1.4;'>
            "{t}"
        </div>"""
    return html or "<div style='color:#555; font-size:11px;'>No primary posts found</div>"

def section_header(icon, label, color):
    return f"""
    <div style='font-size:11px; color:{color}; text-transform:uppercase;
                letter-spacing:1px; margin-bottom:8px; font-weight:bold;'>
        {icon} {label}
    </div>"""

def stat_box(value, label, color):
    return f"""
    <div style='flex:1; text-align:center; background:{color}12;
                border:1px solid {color}25; border-radius:8px; padding:8px 4px;'>
        <div style='font-size:17px; font-weight:bold; color:{color};'>
            {value}
        </div>
        <div style='font-size:9px; color:#888; margin-top:2px;
                    text-transform:uppercase; letter-spacing:0.5px;'>
            {label}
        </div>
    </div>"""

def sentiment_bar(fear_pct, neutral_pct):
    pos_pct = max(0, 100 - fear_pct - neutral_pct)
    return f"""
    <div style='margin:8px 0 4px;'>
        <div style='height:6px; border-radius:3px; overflow:hidden;
                    background:#ffffff0a; display:flex;'>
            <div style='width:{fear_pct}%; background:#ff6b6b;'></div>
            <div style='width:{neutral_pct}%; background:#ffd93d;'></div>
            <div style='width:{pos_pct}%; background:#6bcb77;'></div>
        </div>
        <div style='display:flex; justify-content:space-between;
                    font-size:9px; margin-top:3px;'>
            <span style='color:#ff6b6b;'>Fearful {fear_pct}%</span>
            <span style='color:#ffd93d;'>Neutral {neutral_pct}%</span>
            <span style='color:#6bcb77;'>Positive {pos_pct}%</span>
        </div>
    </div>"""

# ---- POPUP BUILDERS ----
def build_full_popup(row, official_name, color, risk):
    """Popup for neighborhoods with ALL 3 sources"""

    # crime values
    crime_total = int(row.get("crime_total_incidents") or 0)
    crime_types = row.get("crime_top_types", "")
    crime_violent = round(float(row.get("crime_violent_pct") or 0), 1)
    crime_night = round(float(row.get("crime_night_pct") or 0), 1)
    crime_peak = str(row.get("crime_peak_hour") or "N/A")
    crime_day = str(row.get("crime_peak_day") or "N/A")

    # 311 values
    total_311 = int(row.get("requests_311_total") or 0)
    common_complaint = str(row.get("most_common_complaint") or "N/A")
    light_complaints = int(row.get("street_light_complaints") or 0)
    avg_res = int(row.get("avg_resolution_hours") or 0)

    # reddit values
    reddit_posts = int(row.get("reddit_total_posts") or 0)
    reddit_fear_pct = round(float(row.get("reddit_fear_ratio") or 0) * 100, 1)
    reddit_neutral = round(float(row.get("reddit_neutral_concern") or 0) /
                           max(reddit_posts, 1) * 100)
    reddit_positive = int(row.get("reddit_positive_reassuring") or 0)
    combined_score = round(float(row.get("combined_score") or 0), 3)

    fearful_titles, reassuring_titles = get_community_voice(official_name)
    keywords = get_top_keywords(official_name)
    validation_color, validation_text = get_validation(row)

    return f"""
    <div style='width:340px; font-family:Arial,sans-serif; background:#0d0d1a;
                color:#eee; padding:16px; border-radius:14px;
                border:1px solid #1e1e30; max-height:620px; overflow-y:auto;'>

        <!-- HEADER -->
        <div style='display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:4px;'>
            <h3 style='margin:0; color:white; font-size:17px;
                       font-weight:700;'>{official_name}</h3>
            <div style='background:{color}25; border:1px solid {color}60;
                        padding:4px 11px; border-radius:20px;
                        font-size:11px; color:{color};
                        font-weight:bold;'>{risk}</div>
        </div>
        <div style='font-size:10px; color:#555; margin-bottom:12px;'>
            Combined Score: <span style='color:#aaa;'>{combined_score}</span>
            &nbsp;&middot;&nbsp; All 3 data sources
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <!-- CRIME -->
        <div style='margin-bottom:14px;'>
            {section_header("&#128680;", "Crime Data", "#ff6b6b")}
            <div style='background:#ff6b6b0a; border:1px solid #ff6b6b1a;
                        border-radius:10px; padding:12px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{crime_total:,}", "Incidents", "#ff6b6b")}
                    {stat_box(f"{crime_violent}%", "Violent", "#ffa94d")}
                    {stat_box(f"{crime_night}%", "At Night", "#4a9eff")}
                </div>
                <div style='font-size:11px; color:#888; margin-bottom:6px;'>
                    Top crime types:
                </div>
                {crime_type_pills(crime_types)}
                <div style='font-size:11px; color:#666; margin-top:8px;'>
                    Peaks {crime_peak} &middot; {crime_day}s
                </div>
            </div>
        </div>

        <!-- 311 -->
        <div style='margin-bottom:14px;'>
            {section_header("&#128222;", "311 Service Requests", "#4a9eff")}
            <div style='background:#4a9eff0a; border:1px solid #4a9eff1a;
                        border-radius:10px; padding:12px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{total_311:,}", "Requests", "#4a9eff")}
                    {stat_box(f"{light_complaints:,}", "Light Outages", "#ffd93d")}
                    {stat_box(f"{avg_res}h", "Avg Resolution", "#aaa")}
                </div>
                <div style='font-size:11px; color:#666;'>
                    Most common: {common_complaint}
                </div>
            </div>
        </div>

        <!-- REDDIT -->
        <div style='margin-bottom:14px;'>
            {section_header("&#128172;", "Community Voice (Reddit)", "#ffd93d")}
            <div style='background:#ffd93d0a; border:1px solid #ffd93d1a;
                        border-radius:10px; padding:12px;'>
                <div style='display:flex; gap:6px; margin-bottom:8px;'>
                    {stat_box(str(reddit_posts), "Posts", "#ffd93d")}
                    {stat_box(f"{reddit_fear_pct}%", "Fearful", "#ff6b6b")}
                    {stat_box(str(reddit_positive), "Positive", "#6bcb77")}
                </div>
                {sentiment_bar(int(reddit_fear_pct), reddit_neutral)}
                <div style='font-size:11px; color:#888;
                            margin:8px 0 4px;'>Safety signals:</div>
                {keyword_pills(keywords)}
                <div style='font-size:11px; color:#888;
                            margin:10px 0 4px;'>What people are saying:</div>
                {voice_cards(fearful_titles, reassuring_titles)}
            </div>
        </div>

        <!-- VALIDATION -->
        <div style='background:{validation_color}0f;
                    border:1px solid {validation_color}30;
                    border-radius:10px; padding:11px 13px;'>
            <div style='font-size:10px; color:{validation_color};
                        text-transform:uppercase; letter-spacing:1px;
                        margin-bottom:4px; font-weight:bold;'>
                Source Agreement
            </div>
            <div style='font-size:11px; color:#bbb; line-height:1.5;'>
                {validation_text}
            </div>
        </div>

    </div>"""


def build_partial_popup(row, official_name, color, risk, coverage):
    """Popup for neighborhoods with Crime + 311 only — no Reddit"""

    crime_total = int(row.get("crime_total_incidents") or 0)
    crime_types = row.get("crime_top_types", "")
    crime_violent = round(float(row.get("crime_violent_pct") or 0), 1)
    crime_night = round(float(row.get("crime_night_pct") or 0), 1)
    crime_peak = str(row.get("crime_peak_hour") or "N/A")
    crime_day = str(row.get("crime_peak_day") or "N/A")

    total_311 = int(row.get("requests_311_total") or 0)
    common_complaint = str(row.get("most_common_complaint") or "N/A")
    light_complaints = int(row.get("street_light_complaints") or 0)
    avg_res = int(row.get("avg_resolution_hours") or 0)
    combined_score = round(float(row.get("combined_score") or 0), 3)

    return f"""
    <div style='width:320px; font-family:Arial,sans-serif; background:#0d0d1a;
                color:#eee; padding:16px; border-radius:14px;
                border:1px solid #1e1e30;'>

        <!-- HEADER -->
        <div style='display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:4px;'>
            <h3 style='margin:0; color:white; font-size:17px;
                       font-weight:700;'>{official_name}</h3>
            <div style='background:{color}25; border:1px solid {color}60;
                        padding:4px 11px; border-radius:20px;
                        font-size:11px; color:{color};
                        font-weight:bold;'>{risk}</div>
        </div>
        <div style='font-size:10px; color:#555; margin-bottom:12px;'>
            Score: <span style='color:#aaa;'>{combined_score}</span>
            &nbsp;&middot;&nbsp; Official data only
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <!-- CRIME -->
        <div style='margin-bottom:14px;'>
            {section_header("&#128680;", "Crime Data", "#ff6b6b")}
            <div style='background:#ff6b6b0a; border:1px solid #ff6b6b1a;
                        border-radius:10px; padding:12px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{crime_total:,}", "Incidents", "#ff6b6b")}
                    {stat_box(f"{crime_violent}%", "Violent", "#ffa94d")}
                    {stat_box(f"{crime_night}%", "At Night", "#4a9eff")}
                </div>
                {crime_type_pills(crime_types)}
                <div style='font-size:11px; color:#666; margin-top:8px;'>
                    Peaks {crime_peak} &middot; {crime_day}s
                </div>
            </div>
        </div>

        <!-- 311 -->
        <div style='margin-bottom:14px;'>
            {section_header("&#128222;", "311 Service Requests", "#4a9eff")}
            <div style='background:#4a9eff0a; border:1px solid #4a9eff1a;
                        border-radius:10px; padding:12px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{total_311:,}", "Requests", "#4a9eff")}
                    {stat_box(f"{light_complaints:,}", "Light Outages", "#ffd93d")}
                    {stat_box(f"{avg_res}h", "Avg Resolution", "#aaa")}
                </div>
                <div style='font-size:11px; color:#666;'>
                    Most common: {common_complaint}
                </div>
            </div>
        </div>

        <!-- NO REDDIT NOTE -->
        <div style='background:#ffffff06; border:1px solid #ffffff0f;
                    border-radius:10px; padding:11px 13px;'>
            <div style='font-size:10px; color:#7a8fa6; text-transform:uppercase;
                        letter-spacing:1px; margin-bottom:4px; font-weight:bold;'>
                &#128172; Community Voice
            </div>
            <div style='font-size:11px; color:#555; line-height:1.5;'>
                No Reddit community data available for this area.
                Official data shown only.
            </div>
        </div>

    </div>"""


# ---- BUILD MAP ----
print("Building final HerSafe map with all 77 neighborhoods...")
m = folium.Map(
    location=[41.8827, -87.6278],
    zoom_start=11,
    tiles="CartoDB dark_matter"
)

processed = 0
for _, row in merged.iterrows():
    official_name = row["neighborhood"]
    coverage = row.get("data_coverage", "")
    risk = str(row.get("final_risk", "Lower Risk")).replace("*", "").strip()
    color = color_map.get(risk, "#7a8fa6")

    if coverage == "Partial Data":
        color = "#7a8fa6"

    if official_name not in neighborhood_coords:
        continue

    lat, lon = neighborhood_coords[official_name]

    # reddit post count for circle size
    reddit_posts = int(row.get("reddit_total_posts") or 0)
    crime_total = int(row.get("crime_total_incidents") or 0)
    radius = max(6, min(20, 6 + reddit_posts / 10)) if reddit_posts > 0 \
             else max(5, min(12, 5 + crime_total / 2000))

    # build correct popup type
    if coverage == "All 3 Sources":
        popup_html = build_full_popup(row, official_name, color, risk)
    else:
        popup_html = build_partial_popup(row, official_name, color, risk, coverage)

    # tooltip
    crime_str = f"{crime_total:,} incidents" if crime_total > 0 else "No crime data"
    reddit_str = f"{reddit_posts} posts" if reddit_posts > 0 else "No Reddit data"
    coverage_str = "All sources" if coverage == "All 3 Sources" else "Official data only"

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.65,
        weight=2,
        popup=folium.Popup(popup_html, max_width=360),
        tooltip=folium.Tooltip(
            f"<div style='background:#0d0d1a; padding:8px 12px; "
            f"border-radius:8px; border:1px solid #1e1e30;'>"
            f"<b style='color:white; font-size:13px;'>{official_name}</b><br>"
            f"<span style='color:{color}; font-size:11px;'>{risk}</span><br>"
            f"<span style='color:#555; font-size:10px;'>{coverage_str}</span><br>"
            f"<span style='color:#aaa; font-size:11px;'>"
            f"{crime_str} &middot; {reddit_str}</span></div>",
            sticky=False
        )
    ).add_to(m)
    processed += 1

# ---- LEGEND ----
legend_html = """
<div style='position:fixed; bottom:30px; left:30px; z-index:1000;
            background:#0d0d1a; padding:18px; border-radius:14px;
            color:white; font-family:Arial; font-size:13px;
            border:1px solid #1e1e30; min-width:215px;'>

    <div style='font-size:16px; font-weight:bold; margin-bottom:2px;'>
        HerSafe Chicago
    </div>
    <div style='color:#555; font-size:11px; margin-bottom:14px;'>
        Crime &middot; 311 &middot; Reddit Combined
    </div>

    <div style='margin-bottom:6px;'>
        <span style='color:#ff6b6b; font-size:15px;'>&#9679;</span>
        <span style='margin-left:8px;'>High Risk</span>
    </div>
    <div style='margin-bottom:6px;'>
        <span style='color:#ffa94d; font-size:15px;'>&#9679;</span>
        <span style='margin-left:8px;'>Medium Risk</span>
    </div>
    <div style='margin-bottom:6px;'>
        <span style='color:#6bcb77; font-size:15px;'>&#9679;</span>
        <span style='margin-left:8px;'>Lower Risk</span>
    </div>
    <div style='margin-bottom:14px;'>
        <span style='color:#7a8fa6; font-size:15px;'>&#9679;</span>
        <span style='margin-left:8px;'>Official Data Only</span>
    </div>

    <div style='border-top:1px solid #1e1e30; padding-top:10px;
                font-size:10px; color:#555; line-height:2;'>
        &#128680; Crime data<br>
        &#128222; 311 complaints<br>
        &#128172; Reddit community posts<br><br>
        Hover to preview<br>
        Click for full breakdown
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

m.save("hersafe_final_map.html")
print(f"Done! {processed} neighborhoods mapped")
print("Open hersafe_final_map.html in your browser!")