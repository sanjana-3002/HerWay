# HerWay — Chicago Women's Safety Analysis

A data pipeline that analyzes Reddit posts, city crime records, and 311 service requests to map neighborhood-level safety conditions in Chicago — with a focus on women's experiences.

**Author:** Sanjana Waghray  
**Institution:** Illinois Institute of Technology

---

## What This Project Does

Most safety apps rely only on official crime data. HerWay layers in real community voices from Reddit to capture what women actually feel and experience on the ground — fear of walking alone, street harassment, avoiding certain areas at night. The result is an interactive map that combines three different data sources into a single risk score per neighborhood.

---

## Data Sources

| Source | File | What It Captures |
|--------|------|-----------------|
| Reddit posts | `chicago_safety_reddit.csv` | 1,218 posts from r/chicago, r/AskChicago, r/TwoXChromosomes |
| Chicago crime data | `community_crime_profile.csv` | Incident counts, violent crime %, night crime %, arrest rates |
| City 311 requests | `neighbourhood_311.csv` | Street light outages, abandoned buildings, service response times |

---

## How It Works — Step by Step

```
reddit-extraction.py
  → Scrapes safety-related Reddit posts from Chicago subreddits
  → Output: chicago_safety_reddit.csv

visualizations/analysis.py  (formerly safety-analysis.py)
  → Reads each post and checks for Chicago neighborhood names
  → Scores each post by how many safety keywords it contains
  → Output: chicago_safety_located.csv

sentiment-analysis.py
  → Runs each post through a RoBERTa sentiment model
  → Labels posts as Negative/Fear, Neutral/Concern, or Positive/Reassuring
  → Builds per-neighborhood sentiment summaries
  → Output: chicago_safety_sentiment.csv, neighborhood_sentiment_summary.csv

merge_final.py
  → Merges Reddit sentiment + crime data + 311 data by neighborhood
  → Normalizes all scores to 0–1
  → Computes a combined risk score (crime 40%, Reddit 25%, violent crime 20%, 311 10%, lighting 5%)
  → Tags each neighborhood with its data coverage level
  → Output: hersafe_final_merged.csv

final_map.py
  → Builds the final interactive map with all three data sources
  → Popups show detailed breakdown per neighborhood
  → Output: hersafe_final_map.html

safety-analysis.py
  → Earlier version of the map (Reddit + sentiment only)
  → Output: hersafe_chicago_map.html

dashboard.py
  → Generates an HTML dashboard with sortable tables by risk level
  → Output: hersafe_dashboard.html

gender_analysis.py
  → Identifies posts written from a female perspective
  → Analyzes how women's safety concerns differ by neighborhood and time of day
  → Output: gender_analysis.html

trend_analysis.py
  → Tracks how fear ratios have changed year-over-year since 2013
  → Output: trend_analysis.html

visualizations.py
  → Generates charts: bubble charts, fear rate bars, heatmaps, word clouds
  → Output: visualizations/ folder
```

---

## Risk Score Formula

The combined score used to assign risk labels is:

```
combined_score = (crime_incidents × 0.40)
               + (reddit_fear_ratio × 0.25)
               + (violent_crime_pct × 0.20)
               + (311_requests × 0.10)
               + (street_light_complaints × 0.05)
```

Risk labels are only assigned with confidence when a neighborhood has data from all three sources. Neighborhoods with partial data are marked with an asterisk (`*`).

---

## Output Files

| File | Description |
|------|-------------|
| `hersafe_final_map.html` | Main interactive map (all three sources) |
| `hersafe_dashboard.html` | Sortable dashboard by risk level |
| `gender_analysis.html` | Women-specific safety breakdown |
| `trend_analysis.html` | Year-over-year fear trends |
| `visualizations/hersafe_chicago_map.html` | Reddit-only map (earlier version) |
| `hersafe_final_merged.csv` | Full merged dataset with all scores |

Open any `.html` file in a browser — no server needed.

---

## Setup

```bash
pip install pandas numpy folium transformers plotly
```

Run scripts in this order:
1. `reddit-extraction.py` — only needed if re-scraping
2. `visualizations/analysis.py`
3. `sentiment-analysis.py`
4. `merge_final.py`
5. `final_map.py` / `dashboard.py` / `gender_analysis.py` / `trend_analysis.py`

---

## Project Context

Built as part of the Soremo initiative at Illinois Tech. The goal is to understand urban safety from a community perspective, not just through official statistics — and to make that data accessible to women navigating Chicago.

Data is sourced from public Reddit posts and open city datasets. This project is for research purposes only.
