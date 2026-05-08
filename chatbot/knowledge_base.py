"""
HerWay Knowledge Base
Loads and prepares the three data sources into a per-neighborhood lookup.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load_crime(path: Path) -> dict:
    df = pd.read_csv(path)
    result = {}
    for _, row in df.iterrows():
        name = str(row["neighborhood"]).strip()
        result[name] = {
            "total_incidents":  int(row["total_incidents"]),
            "top_crime_types":  str(row["top_crime_types"]),
            "violent_pct":      float(row["violent_pct"]),
            "domestic_pct":     float(row["domestic_pct"]),
            "arrest_rate_pct":  float(row["arrest_rate_pct"]),
            "peak_hour":        str(row["peak_hour_label"]),
            "peak_day":         str(row["peak_day"]),
            "night_crime_pct":  float(row["night_crime_pct"]),
            "top_location":     str(row["top_location"]),
            "peak_month":       str(row["peak_month"]),
        }
    return result


def _load_reddit(path: Path) -> dict:
    df = pd.read_csv(path)
    result = {}
    for _, row in df.iterrows():
        name = str(row["neighborhood"]).strip()
        result[name] = {
            "has_data":               bool(row["reddit_has_data"]),
            "total_posts":            int(row["reddit_total_posts"]),
            "fearful_count":          int(row["reddit_fearful_count"]),
            "reassuring_count":       int(row["reddit_reassuring_count"]),
            "neutral_count":          int(row["reddit_neutral_count"]),
            "fear_ratio_pct":         float(row["reddit_fear_ratio_pct"]),
            "night_posts":            int(row["reddit_night_posts"]),
            "night_fear_pct":         float(row["reddit_night_fear_pct"]),
            "female_posts":           int(row["reddit_female_posts"]),
            "female_fearful_count":   int(row["reddit_female_fearful_count"]),
            "top_keywords":           str(row["reddit_top_safety_keywords"]),
            "fearful_titles":         str(row["reddit_fearful_titles"]),
            "reassuring_titles":      str(row["reddit_reassuring_titles"]),
            "fearful_snippets":       str(row["reddit_fearful_text_snippets"]),
            "female_fearful_titles":  str(row["reddit_female_fearful_titles"]),
            "year_range":             str(row["reddit_year_range"]),
            "summary":                str(row["reddit_summary"]),
        }
    return result


def _load_311(path: Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    df = df[df["NEIGHBOURHOOD"].notna() & (df["NEIGHBOURHOOD"] != "UNKNOWN")]

    agg = df.groupby("NEIGHBOURHOOD").agg(
        total_requests      = ("SR_TYPE",         "count"),
        abandoned_vehicle   = ("SR_TYPE",         lambda x: (x == "Abandoned Vehicle Complaint").sum()),
        street_light_out    = ("SR_TYPE",         lambda x: (x == "Street Light Out Complaint").sum()),
        alley_light_out     = ("SR_TYPE",         lambda x: (x == "Alley Light Out Complaint").sum()),
        vacant_building     = ("SR_TYPE",         lambda x: (x == "Vacant/Abandoned Building Complaint").sum()),
        top_complaint       = ("SR_TYPE",         lambda x: x.value_counts().idxmax()),
        avg_resolution_days = ("RESOLUTION_DAYS", "mean"),
    ).reset_index()

    result = {}
    for _, row in agg.iterrows():
        name = str(row["NEIGHBOURHOOD"]).strip()
        result[name] = {
            "total_requests":       int(row["total_requests"]),
            "top_complaint":        str(row["top_complaint"]),
            "abandoned_vehicle":    int(row["abandoned_vehicle"]),
            "street_light_out":     int(row["street_light_out"]),
            "alley_light_out":      int(row["alley_light_out"]),
            "vacant_building":      int(row["vacant_building"]),
            "avg_resolution_days":  round(float(row["avg_resolution_days"]), 1),
        }
    return result


def build_knowledge_base() -> dict:
    """
    Returns a dict keyed by neighborhood name:
    {
        "Austin": {
            "crime":  { ... },
            "reddit": { ... },
            "s311":   { ... },
        },
        ...
    }
    """
    print("Loading knowledge base...")

    crime  = _load_crime(DATA_DIR / "community_crime_profile.csv")
    reddit = _load_reddit(DATA_DIR / "reddit_chatbot_data.csv")
    s311   = _load_311(DATA_DIR / "311_requests_with_neighbourhood.csv")

    # Union of all neighborhood names across the 3 sources
    all_neighborhoods = sorted(
        set(crime.keys()) | set(reddit.keys()) | set(s311.keys())
    )

    kb = {}
    for name in all_neighborhoods:
        kb[name] = {
            "crime":  crime.get(name,  {}),
            "reddit": reddit.get(name, {}),
            "s311":   s311.get(name,   {}),
        }

    print(f"Knowledge base ready — {len(kb)} neighborhoods loaded.")
    return kb


def build_context(neighborhood: str, kb: dict) -> str:
    """
    Build a structured text context block for a given neighborhood
    to inject into the GPT prompt.
    """
    if neighborhood not in kb:
        return f"No data found for neighborhood: {neighborhood}"

    data    = kb[neighborhood]
    crime   = data.get("crime",  {})
    reddit  = data.get("reddit", {})
    s311    = data.get("s311",   {})

    lines = [f"### {neighborhood} — Data Summary\n"]

    # ── Crime ──────────────────────────────────────────────────────────────
    if crime:
        lines.append("**Crime Data (2025):**")
        lines.append(f"- Total reported incidents: {crime.get('total_incidents', 'N/A'):,}")
        lines.append(f"- Top crime types: {crime.get('top_crime_types', 'N/A')}")
        lines.append(f"- Violent crime: {crime.get('violent_pct', 'N/A')}% of incidents")
        lines.append(f"- Domestic incidents: {crime.get('domestic_pct', 'N/A')}% of incidents")
        lines.append(f"- Arrest rate: {crime.get('arrest_rate_pct', 'N/A')}%")
        lines.append(f"- Peak time: {crime.get('peak_hour', 'N/A')} on {crime.get('peak_day', 'N/A')}s")
        lines.append(f"- Night incidents (6pm–6am): {crime.get('night_crime_pct', 'N/A')}%")
        lines.append(f"- Most common crime location: {crime.get('top_location', 'N/A')}")
        lines.append(f"- Busiest month: {crime.get('peak_month', 'N/A')}")
        lines.append("")

    # ── Reddit ─────────────────────────────────────────────────────────────
    if reddit and reddit.get("has_data"):
        lines.append("**Reddit Community Discussions:**")
        lines.append(f"- Posts analyzed: {reddit.get('total_posts', 0)} ({reddit.get('year_range', 'N/A')})")
        lines.append(f"- Fearful posts: {reddit.get('fearful_count', 0)} | Reassuring: {reddit.get('reassuring_count', 0)} | Neutral: {reddit.get('neutral_count', 0)}")
        lines.append(f"- Fear ratio: {reddit.get('fear_ratio_pct', 0)}% of posts express fear or concern")
        lines.append(f"- Night-related posts: {reddit.get('night_posts', 0)} ({reddit.get('night_fear_pct', 0)}% fearful)")
        lines.append(f"- Posts by/about women: {reddit.get('female_posts', 0)} ({reddit.get('female_fearful_count', 0)} fearful)")
        lines.append(f"- Top safety keywords: {reddit.get('top_keywords', 'N/A')}")
        lines.append(f"- Summary: {reddit.get('summary', 'N/A')}")
        if reddit.get("fearful_titles") and reddit["fearful_titles"] != "nan":
            lines.append(f"- Fearful post titles: {reddit.get('fearful_titles', '')[:300]}")
        if reddit.get("reassuring_titles") and reddit["reassuring_titles"] != "nan":
            lines.append(f"- Reassuring post titles: {reddit.get('reassuring_titles', '')[:300]}")
        lines.append("")
    else:
        lines.append("**Reddit Community Discussions:** No data available for this neighborhood.\n")

    # ── 311 ────────────────────────────────────────────────────────────────
    if s311:
        lines.append("**311 Service Requests:**")
        lines.append(f"- Total complaints filed: {s311.get('total_requests', 0):,}")
        lines.append(f"- Most common complaint: {s311.get('top_complaint', 'N/A')}")
        lines.append(f"- Abandoned vehicles: {s311.get('abandoned_vehicle', 0):,}")
        lines.append(f"- Street lights out: {s311.get('street_light_out', 0):,}")
        lines.append(f"- Alley lights out: {s311.get('alley_light_out', 0):,}")
        lines.append(f"- Vacant/abandoned buildings: {s311.get('vacant_building', 0):,}")
        lines.append(f"- Average resolution time: {s311.get('avg_resolution_days', 'N/A')} days")
        lines.append("")
    else:
        lines.append("**311 Service Requests:** No data available for this neighborhood.\n")

    return "\n".join(lines)
