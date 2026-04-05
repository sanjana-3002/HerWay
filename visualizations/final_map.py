import pandas as pd
import ast
import folium
from collections import Counter

# ================================================
# HERSAFE CHICAGO — FINAL INTERACTIVE MAP
# All 77 neighborhoods, 3 data sources
# ================================================

# ---- LOAD DATA ----
merged = pd.read_csv("data/processed/hersafe_final_merged.csv")
sentiment_df = pd.read_csv("data/processed/chicago_safety_sentiment.csv")
sentiment_df["neighborhoods_mentioned"] = sentiment_df["neighborhoods_mentioned"].apply(ast.literal_eval)
sentiment_df["safety_flags"] = sentiment_df["safety_flags"].apply(ast.literal_eval)
sentiment_df["hour"] = pd.to_datetime(sentiment_df["date"], unit="s").dt.hour
sentiment_df["is_night"] = sentiment_df["hour"].apply(lambda h: h >= 20 or h < 4)
sentiment_df["title"] = sentiment_df["title"].fillna("")

# ---- SAFE CONVERTERS ----
def safe_int(val, default=0):
    try:
        if pd.isna(val):
            return default
        return int(float(val))
    except:
        return default

def safe_float(val, default=0.0):
    try:
        if pd.isna(val):
            return default
        return float(val)
    except:
        return default

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
    reddit_fear = safe_float(row.get("reddit_fear_ratio"))
    crime_norm = safe_float(row.get("crime_score_norm"))
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

# ---- TRAVELER CONTENT GENERATORS ----
def get_safety_tips(row):
    tips = []
    crime_night = safe_float(row.get("crime_night_pct"))
    crime_violent = safe_float(row.get("crime_violent_pct"))
    crime_peak = str(row.get("crime_peak_hour") or "")
    light_complaints = safe_int(row.get("street_light_complaints"))
    avg_resolution = safe_float(row.get("avg_resolution_hours"))
    reddit_fear = safe_float(row.get("reddit_fear_ratio"))
    arrest_rate = safe_float(row.get("crime_arrest_rate"))

    if crime_night >= 45:
        tips.append("High proportion of crime occurs at night — plan travel during daylight when possible")
    elif crime_night >= 35:
        tips.append("Moderate night-time crime — stay aware after dark and stick to busy streets")

    if crime_violent >= 40:
        tips.append("High violent crime rate — stay in populated, well-lit areas and avoid isolated spots")
    elif crime_violent >= 30:
        tips.append("Moderate violent crime — travel in groups at night if possible")

    if light_complaints >= 500:
        tips.append("Many street lighting complaints reported — carry a light source at night")
    elif light_complaints >= 200:
        tips.append("Some street lighting issues reported in this area")

    if crime_peak and crime_peak != "N/A":
        tips.append(f"Crime peaks around {crime_peak} — extra caution during this time")

    if avg_resolution >= 400:
        tips.append("City service response is slower here — infrastructure issues may persist longer")

    if reddit_fear >= 0.4:
        tips.append("Community members frequently report feeling unsafe — trust your instincts")
    elif reddit_fear <= 0.15:
        tips.append("Community generally reports feeling comfortable in this area")

    if arrest_rate >= 25:
        tips.append("Above-average arrest rate suggests active policing in the area")

    return tips[:4]

def get_best_times(row):
    crime_peak = str(row.get("crime_peak_hour") or "N/A")
    crime_peak_day = str(row.get("crime_peak_day") or "N/A")
    crime_night = safe_float(row.get("crime_night_pct"))
    crime_peak_month = str(row.get("crime_peak_month") or "N/A")

    if crime_night >= 45:
        safest = "Daytime hours, especially weekday mornings"
    elif crime_night >= 35:
        safest = "Afternoon and early evening (before 8pm)"
    else:
        safest = "Generally safe throughout the day"

    risky_parts = []
    if crime_peak and crime_peak != "N/A":
        risky_parts.append(crime_peak)
    if crime_peak_day and crime_peak_day != "N/A":
        risky_parts.append(f"{crime_peak_day}s")
    if crime_peak_month and crime_peak_month != "N/A":
        risky_parts.append(f"especially in {crime_peak_month}")

    riskiest = " · ".join(risky_parts) if risky_parts else "No clear peak identified"
    return safest, riskiest

def get_transit_notes(row):
    crime_night = safe_float(row.get("crime_night_pct"))
    light_complaints = safe_int(row.get("street_light_complaints"))
    crime_top_location = str(row.get("crime_top_location") or "")
    notes = []

    if "STREET" in crime_top_location.upper():
        notes.append("Most incidents occur on streets — stay alert while walking")
    if "CTA" in crime_top_location.upper() or "TRANSIT" in crime_top_location.upper():
        notes.append("Transit locations are a hotspot — be vigilant on public transport")
    if crime_night >= 45:
        notes.append("Late night transit carries higher risk — travel with others if possible")
    elif crime_night >= 35:
        notes.append("Night transit moderately elevated — sit near driver or in busy cars")
    else:
        notes.append("Transit risk is relatively low compared to other areas")
    if light_complaints >= 300:
        notes.append("Poor street lighting reported — avoid unlit shortcuts")

    return notes[:3]

def get_traveler_summary(row, official_name, risk):
    crime_violent = safe_float(row.get("crime_violent_pct"))
    reddit_fear = safe_float(row.get("reddit_fear_ratio"))
    crime_night = safe_float(row.get("crime_night_pct"))

    if risk == "High Risk":
        if crime_violent >= 40:
            return f"{official_name} has high violent crime — exercise significant caution, especially at night."
        else:
            return f"{official_name} sees elevated crime activity — stay aware of your surroundings at all times."
    elif risk == "Medium Risk":
        if crime_night >= 40:
            return f"{official_name} is manageable during the day but crime risk rises significantly after dark."
        elif reddit_fear >= 0.3:
            return f"Residents flag safety concerns in {official_name} — especially when walking alone."
        else:
            return f"{official_name} has moderate risk — standard urban awareness is advised."
    else:
        if reddit_fear <= 0.15:
            return f"{official_name} is generally well-regarded by the community — a relatively comfortable area to visit."
        else:
            return f"{official_name} has lower overall risk — isolated concerns exist but are not widespread."

# ---- HTML HELPERS ----
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

def tips_html(tips):
    if not tips:
        return "<div style='color:#555; font-size:11px;'>No specific tips generated</div>"
    return "".join([
        f"""<div style='display:flex; gap:8px; align-items:flex-start;
                       margin-bottom:7px;'>
                <span style='color:#ffd93d; font-size:12px; margin-top:1px;'>&#8250;</span>
                <span style='font-size:11px; color:#bbb; line-height:1.5;'>{tip}</span>
            </div>"""
        for tip in tips
    ])

# ---- POPUP BUILDERS ----
def build_full_popup(row, official_name, color, risk):
    """Full popup for neighborhoods with ALL 3 data sources"""

    crime_total     = safe_int(row.get("crime_total_incidents"))
    crime_types     = row.get("crime_top_types", "")
    crime_violent   = safe_float(row.get("crime_violent_pct"))
    crime_night     = safe_float(row.get("crime_night_pct"))
    crime_peak      = str(row.get("crime_peak_hour") or "N/A")
    crime_day       = str(row.get("crime_peak_day") or "N/A")
    total_311       = safe_int(row.get("requests_311_total"))
    common_complaint= str(row.get("most_common_complaint") or "N/A")
    light_complaints= safe_int(row.get("street_light_complaints"))
    avg_res         = safe_int(row.get("avg_resolution_hours"))
    reddit_posts    = safe_int(row.get("reddit_total_posts"))
    reddit_fear_pct = round(safe_float(row.get("reddit_fear_ratio")) * 100, 1)
    reddit_neutral  = round(safe_float(row.get("reddit_neutral_concern")) /
                            max(reddit_posts, 1) * 100)
    reddit_positive = safe_int(row.get("reddit_positive_reassuring"))
    combined_score  = round(safe_float(row.get("combined_score")), 3)

    fearful_titles, reassuring_titles = get_community_voice(official_name)
    keywords = get_top_keywords(official_name)
    validation_color, validation_text = get_validation(row)

    traveler_summary = get_traveler_summary(row, official_name, risk)
    safety_tips      = get_safety_tips(row)
    safest_time, riskiest_time = get_best_times(row)
    transit_notes    = get_transit_notes(row)

    return f"""
    <div style='width:340px; font-family:Arial,sans-serif; background:#0d0d1a;
                color:#eee; padding:16px; border-radius:14px;
                border:1px solid #1e1e30; max-height:680px; overflow-y:auto;'>

        <div style='display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:4px;'>
            <h3 style='margin:0; color:white; font-size:17px;
                       font-weight:700;'>{official_name}</h3>
            <div style='background:{color}25; border:1px solid {color}60;
                        padding:4px 11px; border-radius:20px;
                        font-size:11px; color:{color};
                        font-weight:bold;'>{risk}</div>
        </div>
        <div style='font-size:10px; color:#555; margin-bottom:10px;'>
            Score: <span style='color:#aaa;'>{combined_score}</span>
            &nbsp;&middot;&nbsp; Crime + 311 + Reddit
        </div>

        <div style='background:{color}0d; border-left:3px solid {color};
                    border-radius:0 8px 8px 0; padding:10px 12px;
                    margin-bottom:14px; font-size:12px; color:#ccc;
                    font-style:italic; line-height:1.5;'>
            {traveler_summary}
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128680;", "Crime Data", "#ff6b6b")}
            <div style='border-left:2px solid #ff6b6b22; padding-left:10px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{crime_total:,}", "Incidents", "#ff6b6b")}
                    {stat_box(f"{crime_violent}%", "Violent", "#ffa94d")}
                    {stat_box(f"{crime_night}%", "At Night", "#4a9eff")}
                </div>
                <div style='font-size:11px; color:#888; margin-bottom:6px;'>
                    Top types:
                </div>
                {crime_type_pills(crime_types)}
                <div style='font-size:11px; color:#555; margin-top:8px;'>
                    Peaks {crime_peak} &middot; {crime_day}s
                </div>
            </div>
        </div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128222;", "311 Service Requests", "#4a9eff")}
            <div style='border-left:2px solid #4a9eff22; padding-left:10px;'>
                <div style='display:flex; gap:6px; margin-bottom:8px;'>
                    {stat_box(f"{total_311:,}", "Requests", "#4a9eff")}
                    {stat_box(f"{light_complaints:,}", "Light Outages", "#ffd93d")}
                    {stat_box(f"{avg_res}h", "Avg Fix Time", "#aaa")}
                </div>
                <div style='font-size:11px; color:#555;'>
                    Most common: {common_complaint}
                </div>
            </div>
        </div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128172;", "Community Voice (Reddit)", "#ffd93d")}
            <div style='border-left:2px solid #ffd93d22; padding-left:10px;'>
                <div style='display:flex; gap:6px; margin-bottom:8px;'>
                    {stat_box(str(reddit_posts), "Posts", "#ffd93d")}
                    {stat_box(f"{reddit_fear_pct}%", "Fearful", "#ff6b6b")}
                    {stat_box(str(reddit_positive), "Positive", "#6bcb77")}
                </div>
                {sentiment_bar(int(reddit_fear_pct), reddit_neutral)}
                <div style='font-size:11px; color:#888; margin:8px 0 4px;'>
                    Safety signals:
                </div>
                {keyword_pills(keywords)}
                <div style='font-size:11px; color:#888; margin:10px 0 4px;'>
                    What people say:
                </div>
                {voice_cards(fearful_titles, reassuring_titles)}
            </div>
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128205;", "Traveler Guide", "#aaccff")}

            <div style='margin-bottom:10px;'>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Safety Tips
                </div>
                {tips_html(safety_tips)}
            </div>

            <div style='margin-bottom:10px;'>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Best Times to Visit
                </div>
                <div style='display:flex; gap:6px;'>
                    <div style='flex:1; background:#6bcb7710;
                                border:1px solid #6bcb7725;
                                border-radius:8px; padding:8px;'>
                        <div style='font-size:9px; color:#6bcb77;
                                    margin-bottom:4px;'>SAFER</div>
                        <div style='font-size:11px; color:#bbb;
                                    line-height:1.4;'>{safest_time}</div>
                    </div>
                    <div style='flex:1; background:#ff6b6b10;
                                border:1px solid #ff6b6b25;
                                border-radius:8px; padding:8px;'>
                        <div style='font-size:9px; color:#ff6b6b;
                                    margin-bottom:4px;'>PEAK RISK</div>
                        <div style='font-size:11px; color:#bbb;
                                    line-height:1.4;'>{riskiest_time}</div>
                    </div>
                </div>
            </div>

            <div>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Transit and Getting Around
                </div>
                {tips_html(transit_notes)}
            </div>
        </div>

        <div style='background:{validation_color}0a;
                    border:1px solid {validation_color}25;
                    border-radius:10px; padding:10px 12px;'>
            <div style='font-size:10px; color:{validation_color};
                        text-transform:uppercase; letter-spacing:1px;
                        margin-bottom:4px; font-weight:bold;'>
                Source Agreement
            </div>
            <div style='font-size:11px; color:#aaa; line-height:1.5;'>
                {validation_text}
            </div>
        </div>

    </div>"""


def build_partial_popup(row, official_name, color, risk, coverage):
    """Popup for neighborhoods with Crime + 311 only"""

    crime_total      = safe_int(row.get("crime_total_incidents"))
    crime_types      = row.get("crime_top_types", "")
    crime_violent    = safe_float(row.get("crime_violent_pct"))
    crime_night      = safe_float(row.get("crime_night_pct"))
    crime_peak       = str(row.get("crime_peak_hour") or "N/A")
    crime_day        = str(row.get("crime_peak_day") or "N/A")
    total_311        = safe_int(row.get("requests_311_total"))
    common_complaint = str(row.get("most_common_complaint") or "N/A")
    light_complaints = safe_int(row.get("street_light_complaints"))
    avg_res          = safe_int(row.get("avg_resolution_hours"))
    combined_score   = round(safe_float(row.get("combined_score")), 3)

    traveler_summary = get_traveler_summary(row, official_name, risk)
    safety_tips      = get_safety_tips(row)
    safest_time, riskiest_time = get_best_times(row)
    transit_notes    = get_transit_notes(row)

    return f"""
    <div style='width:320px; font-family:Arial,sans-serif; background:#0d0d1a;
                color:#eee; padding:16px; border-radius:14px;
                border:1px solid #1e1e30;'>

        <div style='display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:4px;'>
            <h3 style='margin:0; color:white; font-size:17px;
                       font-weight:700;'>{official_name}</h3>
            <div style='background:{color}25; border:1px solid {color}60;
                        padding:4px 11px; border-radius:20px;
                        font-size:11px; color:{color};
                        font-weight:bold;'>{risk}</div>
        </div>
        <div style='font-size:10px; color:#555; margin-bottom:10px;'>
            Score: <span style='color:#aaa;'>{combined_score}</span>
            &nbsp;&middot;&nbsp; Official data only
        </div>

        <div style='background:{color}0d; border-left:3px solid {color};
                    border-radius:0 8px 8px 0; padding:10px 12px;
                    margin-bottom:14px; font-size:12px; color:#ccc;
                    font-style:italic; line-height:1.5;'>
            {traveler_summary}
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128680;", "Crime Data", "#ff6b6b")}
            <div style='border-left:2px solid #ff6b6b22; padding-left:10px;'>
                <div style='display:flex; gap:6px; margin-bottom:10px;'>
                    {stat_box(f"{crime_total:,}", "Incidents", "#ff6b6b")}
                    {stat_box(f"{crime_violent}%", "Violent", "#ffa94d")}
                    {stat_box(f"{crime_night}%", "At Night", "#4a9eff")}
                </div>
                {crime_type_pills(crime_types)}
                <div style='font-size:11px; color:#555; margin-top:8px;'>
                    Peaks {crime_peak} &middot; {crime_day}s
                </div>
            </div>
        </div>

        <div style='margin-bottom:14px;'>
            {section_header("&#128222;", "311 Service Requests", "#4a9eff")}
            <div style='border-left:2px solid #4a9eff22; padding-left:10px;'>
                <div style='display:flex; gap:6px; margin-bottom:8px;'>
                    {stat_box(f"{total_311:,}", "Requests", "#4a9eff")}
                    {stat_box(f"{light_complaints:,}", "Light Outages", "#ffd93d")}
                    {stat_box(f"{avg_res}h", "Avg Fix Time", "#aaa")}
                </div>
                <div style='font-size:11px; color:#555;'>
                    Most common: {common_complaint}
                </div>
            </div>
        </div>

        <div style='background:#ffffff05; border:1px solid #1e1e30;
                    border-radius:10px; padding:10px 12px; margin-bottom:14px;'>
            <div style='font-size:10px; color:#444; text-transform:uppercase;
                        letter-spacing:1px; margin-bottom:4px;'>
                &#128172; Community Voice
            </div>
            <div style='font-size:11px; color:#444; line-height:1.5;'>
                No Reddit community data available for this area.
            </div>
        </div>

        <div style='height:1px; background:#1e1e30; margin-bottom:14px;'></div>

        <div>
            {section_header("&#128205;", "Traveler Guide", "#aaccff")}

            <div style='margin-bottom:10px;'>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Safety Tips
                </div>
                {tips_html(safety_tips)}
            </div>

            <div style='margin-bottom:10px;'>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Best Times to Visit
                </div>
                <div style='display:flex; gap:6px;'>
                    <div style='flex:1; background:#6bcb7710;
                                border:1px solid #6bcb7725;
                                border-radius:8px; padding:8px;'>
                        <div style='font-size:9px; color:#6bcb77;
                                    margin-bottom:4px;'>SAFER</div>
                        <div style='font-size:11px; color:#bbb;
                                    line-height:1.4;'>{safest_time}</div>
                    </div>
                    <div style='flex:1; background:#ff6b6b10;
                                border:1px solid #ff6b6b25;
                                border-radius:8px; padding:8px;'>
                        <div style='font-size:9px; color:#ff6b6b;
                                    margin-bottom:4px;'>PEAK RISK</div>
                        <div style='font-size:11px; color:#bbb;
                                    line-height:1.4;'>{riskiest_time}</div>
                    </div>
                </div>
            </div>

            <div>
                <div style='font-size:10px; color:#555; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:1px;'>
                    Transit and Getting Around
                </div>
                {tips_html(transit_notes)}
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
    coverage = str(row.get("data_coverage", ""))
    risk = str(row.get("final_risk", "Lower Risk")).replace("*", "").strip()
    color = color_map.get(risk, "#7a8fa6")

    if official_name not in neighborhood_coords:
        continue

    lat, lon = neighborhood_coords[official_name]

    reddit_posts = safe_int(row.get("reddit_total_posts"))
    crime_total  = safe_int(row.get("crime_total_incidents"))
    radius = max(6, min(20, 6 + reddit_posts / 10)) if reddit_posts > 0 \
             else max(5, min(12, 5 + crime_total / 2000))

    if coverage == "All 3 Sources":
        popup_html = build_full_popup(row, official_name, color, risk)
    else:
        popup_html = build_partial_popup(row, official_name, color, risk, coverage)

    crime_str  = f"{crime_total:,} incidents" if crime_total > 0 else "No crime data"
    reddit_str = f"{reddit_posts} posts" if reddit_posts > 0 else "No Reddit data"
    coverage_label = "All sources" if coverage == "All 3 Sources" else "Official data only"

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
            f"<div style='background:#0d0d1a; padding:8px 12px;"
            f"border-radius:8px; border:1px solid #1e1e30;'>"
            f"<b style='color:white; font-size:13px;'>{official_name}</b><br>"
            f"<span style='color:{color}; font-size:11px;'>{risk}</span><br>"
            f"<span style='color:#555; font-size:10px;'>{coverage_label}</span><br>"
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

m.save("outputs/maps/hersafe_final_map.html")
print(f"Done! {processed} neighborhoods mapped")
print("Open hersafe_final_map.html in your browser!")
