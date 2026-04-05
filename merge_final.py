import pandas as pd
import numpy as np

# ================================================
# HERSAFE CHICAGO — FINAL DATA MERGE v2
# Includes ALL neighborhoods with data coverage tags
# ================================================

# ---- LOAD ALL THREE DATASETS ----
reddit = pd.read_csv("neighborhood_sentiment_summary.csv")
data_311 = pd.read_csv("neighbourhood_311.csv", encoding="utf-8-sig")
crime = pd.read_csv("community_crime_profile.csv")

# ---- CLEAN COLUMN NAMES ----
data_311 = data_311.rename(columns={"Neighbourhoods": "neighborhood"})
reddit["neighborhood"] = reddit["neighborhood"].str.strip()
data_311["neighborhood"] = data_311["neighborhood"].str.strip()
crime["neighborhood"] = crime["neighborhood"].str.strip()

# ---- FIX CAPITALIZATION MISMATCHES IN CRIME DATA ----
crime["neighborhood"] = crime["neighborhood"].replace({
    "Mckinley Park": "McKinley Park",
    "Ohare":         "O'Hare"
})

# remove Unknown row
crime = crime[crime["neighborhood"] != "Unknown"]

print(f"Reddit: {len(reddit)} neighborhoods")
print(f"311:    {len(data_311)} neighborhoods")
print(f"Crime:  {len(crime)} neighborhoods")

# ---- REDDIT NAME MAPPING ----
# Reddit uses popular names, official datasets use community area names
reddit_to_official = {
    "Lakeview":           "Lake View",
    "McKinley Park":      "McKinley Park",
    "Back of the Yards":  "New City",
    "Pilsen":             "Lower West Side",
    "Little Village":     "South Lawndale",
    "Bronzeville":        "Douglas",
    "Wicker Park":        "West Town",
    "Bucktown":           "West Town",
    "Ukrainian Village":  "West Town",
    "Noble Square":       "West Town",
    "Gold Coast":         "Near North Side",
    "River North":        "Near North Side",
    "Streeterville":      "Near North Side",
    "Magnificent Mile":   "Near North Side",
    "South Loop":         "Near South Side",
    "Printer's Row":      "Near South Side",
    "West Loop":          "Near West Side",
    "Fulton Market":      "Near West Side",
    "Chinatown":          "Armour Square",
    "Little Italy":       "Near West Side",
    "University Village": "Near West Side",
    "Andersonville":      "Edgewater",
    "Boystown":           "Lake View",
    "Ravenswood":         "Lincoln Square",
    "Grand Crossing":     "Greater Grand Crossing",
    "Garfield Park":      "East Garfield Park",
    "Cragin":             "Belmont Cragin",
    "Fulton Park":        "East Garfield Park",
    "Navy Pier":          "Near North Side",
    "Millennium Park":    "Loop",
    "Marquette Park":     "Gage Park",
}

reddit["neighborhood_official"] = reddit["neighborhood"].apply(
    lambda x: reddit_to_official.get(x, x)
)

# ---- AGGREGATE REDDIT BY OFFICIAL NAME ----
reddit_agg = reddit.groupby("neighborhood_official").agg(
    reddit_total_posts=("total_posts", "sum"),
    reddit_negative_fear=("negative_fear", "sum"),
    reddit_neutral_concern=("neutral_concern", "sum"),
    reddit_positive_reassuring=("positive_reassuring", "sum"),
    reddit_total_safety_score=("total_safety_score", "sum")
).reset_index()

reddit_agg["reddit_fear_ratio"] = (
    reddit_agg["reddit_negative_fear"] /
    reddit_agg["reddit_total_posts"]
).round(3)

reddit_agg = reddit_agg.rename(columns={"neighborhood_official": "neighborhood"})
print(f"\nReddit after aggregation: {len(reddit_agg)} neighborhoods")

# ---- SELECT KEY COLUMNS FROM 311 ----
cols_311 = [
    "neighborhood",
    "TOTAL_REQUESTS",
    "AVG_RESOLUTION_HOURS",
    "MEDIAN_RESOLUTION_HOURS",
    "SR_TYPE_Street Light Out Complaint",
    "SR_TYPE_Vacant/Abandoned Building Complaint",
    "SR_TYPE_Street Light Out Complaint_PCT",
    "SR_TYPE_Vacant/Abandoned Building Complaint_PCT",
    "MOST_COMMON_SR_TYPE",
    "PEAK_REQUEST_HOUR"
]
data_311_clean = data_311[cols_311].copy()
data_311_clean = data_311_clean.rename(columns={
    "TOTAL_REQUESTS":                                  "requests_311_total",
    "AVG_RESOLUTION_HOURS":                            "avg_resolution_hours",
    "MEDIAN_RESOLUTION_HOURS":                         "median_resolution_hours",
    "SR_TYPE_Street Light Out Complaint":              "street_light_complaints",
    "SR_TYPE_Vacant/Abandoned Building Complaint":     "vacant_building_complaints",
    "SR_TYPE_Street Light Out Complaint_PCT":          "street_light_pct",
    "SR_TYPE_Vacant/Abandoned Building Complaint_PCT": "vacant_building_pct",
    "MOST_COMMON_SR_TYPE":                             "most_common_complaint",
    "PEAK_REQUEST_HOUR":                               "peak_complaint_hour"
})

# ---- SELECT KEY COLUMNS FROM CRIME ----
cols_crime = [
    "neighborhood",
    "total_incidents",
    "top_crime_types",
    "violent_pct",
    "domestic_pct",
    "arrest_rate_pct",
    "night_crime_pct",
    "peak_hour_label",
    "peak_day",
    "peak_month",
    "top_location"
]
crime_clean = crime[cols_crime].copy()
crime_clean = crime_clean.rename(columns={
    "total_incidents":  "crime_total_incidents",
    "top_crime_types":  "crime_top_types",
    "violent_pct":      "crime_violent_pct",
    "domestic_pct":     "crime_domestic_pct",
    "arrest_rate_pct":  "crime_arrest_rate",
    "night_crime_pct":  "crime_night_pct",
    "peak_hour_label":  "crime_peak_hour",
    "peak_day":         "crime_peak_day",
    "peak_month":       "crime_peak_month",
    "top_location":     "crime_top_location"
})

# ---- MERGE ALL THREE (outer join keeps everything) ----
merged = reddit_agg.merge(crime_clean, on="neighborhood", how="outer")
merged = merged.merge(data_311_clean, on="neighborhood", how="outer")

# ---- TAG DATA COVERAGE ----
def tag_coverage(row):
    has_reddit = pd.notna(row.get("reddit_fear_ratio"))
    has_crime  = pd.notna(row.get("crime_total_incidents"))
    has_311    = pd.notna(row.get("requests_311_total"))

    if has_reddit and has_crime and has_311:
        return "All 3 Sources"
    elif has_crime and has_311 and not has_reddit:
        return "Crime + 311 Only"
    elif has_reddit and has_crime and not has_311:
        return "Reddit + Crime Only"
    elif has_reddit and has_311 and not has_crime:
        return "Reddit + 311 Only"
    elif has_crime and not has_311 and not has_reddit:
        return "Crime Only"
    elif has_311 and not has_crime and not has_reddit:
        return "311 Only"
    elif has_reddit and not has_crime and not has_311:
        return "Reddit Only"
    else:
        return "No Data"

merged["data_coverage"] = merged.apply(tag_coverage, axis=1)

print(f"\nData coverage breakdown:")
print(merged["data_coverage"].value_counts())

# ---- NORMALIZE SCORES TO 0-1 ----
def normalize(series):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return series * 0
    return (series - min_val) / (max_val - min_val)

# fill NaN with median before normalizing
# this prevents missing data from breaking the score
for col in ["reddit_fear_ratio", "crime_total_incidents",
            "requests_311_total", "crime_violent_pct"]:
    merged[col] = merged[col].fillna(merged[col].median())

merged["street_light_complaints"] = merged["street_light_complaints"].fillna(0)

merged["reddit_score_norm"]  = normalize(merged["reddit_fear_ratio"])
merged["crime_score_norm"]   = normalize(merged["crime_total_incidents"])
merged["violent_score_norm"] = normalize(merged["crime_violent_pct"])
merged["complaints_norm"]    = normalize(merged["requests_311_total"])
merged["lighting_norm"]      = normalize(merged["street_light_complaints"])

# ---- COMBINED SCORE ----
# weights: Crime 40%, Reddit 25%, Violent 20%, 311 10%, Lighting 5%
# note: neighborhoods missing a source get median filled value
# the data_coverage column tells you how reliable each score is
merged["combined_score"] = (
    merged["crime_score_norm"]   * 0.40 +
    merged["reddit_score_norm"]  * 0.25 +
    merged["violent_score_norm"] * 0.20 +
    merged["complaints_norm"]    * 0.10 +
    merged["lighting_norm"]      * 0.05
).round(3)

# ---- FINAL RISK LABEL ----
def assign_risk(row):
    score = row["combined_score"]
    coverage = row["data_coverage"]

    # only give confident risk labels to neighborhoods
    # with strong data coverage
    if coverage == "All 3 Sources":
        if score >= 0.65:   return "High Risk"
        elif score >= 0.40: return "Medium Risk"
        else:               return "Lower Risk"
    elif coverage in ["Crime + 311 Only", "Reddit + Crime Only"]:
        if score >= 0.65:   return "High Risk*"
        elif score >= 0.40: return "Medium Risk*"
        else:               return "Lower Risk*"
    else:
        return "Partial Data"

merged["final_risk"] = merged.apply(assign_risk, axis=1)
merged = merged.sort_values("combined_score", ascending=False)

# ---- SAVE ----
merged.to_csv("hersafe_final_merged.csv", index=False)

# ---- PRINT SUMMARY ----
print("\n========== ALL 3 SOURCES — TOP 15 ==========\n")
full = merged[merged["data_coverage"] == "All 3 Sources"]
display_cols = [
    "neighborhood", "combined_score", "final_risk",
    "reddit_fear_ratio", "crime_total_incidents",
    "crime_violent_pct", "requests_311_total"
]
print(full[display_cols].head(15).to_string(index=False))

print("\n========== CRIME + 311 ONLY (no Reddit) ==========\n")
partial = merged[merged["data_coverage"] == "Crime + 311 Only"]
print(partial[["neighborhood", "crime_total_incidents",
               "crime_violent_pct", "requests_311_total",
               "final_risk"]].to_string(index=False))

print("\n========== RISK DISTRIBUTION ==========")
print(merged["final_risk"].value_counts())

print(f"\nTotal neighborhoods in map: {len(merged)}")
print("Saved: hersafe_final_merged.csv")
