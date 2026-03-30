import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ---- LOAD DATA ----
df = pd.read_csv("chicago_safety_sentiment.csv")
df["date_parsed"] = pd.to_datetime(df["date"], unit="s")
df["year"] = df["date_parsed"].dt.year
df["month"] = df["date_parsed"].dt.month
df["month_name"] = df["date_parsed"].dt.strftime("%b")
df["year_month"] = df["date_parsed"].dt.strftime("%Y-%m")
df["quarter"] = df["date_parsed"].dt.to_period("Q").astype(str)

import ast
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)

print("Building trend analysis...")

# ---- YEARLY FEAR RATIO (2013 onwards) ----
yearly = df[df["year"] >= 2013].copy()
yearly_grouped = yearly.groupby(["year", "sentiment"]).size().unstack(fill_value=0)
yearly_grouped["total"] = yearly_grouped.sum(axis=1)
yearly_grouped["fear_ratio"] = (
    yearly_grouped.get("Negative/Fear", 0) / yearly_grouped["total"] * 100
).round(1)
yearly_grouped["reassuring_ratio"] = (
    yearly_grouped.get("Positive/Reassuring", 0) / yearly_grouped["total"] * 100
).round(1)
yearly_grouped["neutral_ratio"] = (
    yearly_grouped.get("Neutral/Concern", 0) / yearly_grouped["total"] * 100
).round(1)
yearly_grouped = yearly_grouped.reset_index()

# ---- MONTHLY TREND 2023-2026 ----
recent = df[df["year"] >= 2023].copy()
monthly = recent.groupby(["year_month", "sentiment"]).size().unstack(fill_value=0)
monthly["total"] = monthly.sum(axis=1)
monthly["fear_ratio"] = (
    monthly.get("Negative/Fear", 0) / monthly["total"] * 100
).round(1)
monthly = monthly.reset_index().sort_values("year_month")

# ---- NEIGHBORHOOD TREND (top 5 neighborhoods) ----
top_neighborhoods = ["Loop", "Logan Square", "Uptown", "Rogers Park", "Hyde Park"]

neighborhood_yearly = []
for n in top_neighborhoods:
    n_df = df[
        (df["neighborhoods_mentioned"].apply(lambda x: n in x)) &
        (df["year"] >= 2020)
    ]
    if len(n_df) == 0:
        continue
    n_grouped = n_df.groupby(["year", "sentiment"]).size().unstack(fill_value=0)
    n_grouped["total"] = n_grouped.sum(axis=1)
    n_grouped["fear_ratio"] = (
        n_grouped.get("Negative/Fear", 0) / n_grouped["total"] * 100
    ).round(1)
    n_grouped = n_grouped.reset_index()
    n_grouped["neighborhood"] = n
    neighborhood_yearly.append(n_grouped[["year", "fear_ratio", "neighborhood", "total"]])

neighborhood_trend_df = pd.concat(neighborhood_yearly, ignore_index=True) if neighborhood_yearly else pd.DataFrame()

# ---- BUILD INTERACTIVE CHARTS ----
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=[
        "Overall Fear Ratio by Year (2013-2026)",
        "Sentiment Breakdown by Year",
        "Monthly Fear Trend (2023-2026)",
        "Post Volume by Year",
        "Neighborhood Fear Trends (2020-2026)",
        "2025 vs 2024 — Sentiment Comparison"
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.1
)

colors = {
    "Negative/Fear": "#ff6b6b",
    "Neutral/Concern": "#ffd93d",
    "Positive/Reassuring": "#6bcb77"
}

# ---- CHART 1: Fear ratio trend line ----
fig.add_trace(go.Scatter(
    x=yearly_grouped["year"],
    y=yearly_grouped["fear_ratio"],
    mode="lines+markers+text",
    name="Fear Ratio %",
    line=dict(color="#ff6b6b", width=3),
    marker=dict(size=10, color="#ff6b6b"),
    text=yearly_grouped["fear_ratio"].astype(str) + "%",
    textposition="top center",
    textfont=dict(size=9, color="#ff6b6b"),
    showlegend=False
), row=1, col=1)

# add COVID annotation
fig.add_vline(
    x=2020, line_dash="dash",
    line_color="rgba(255,255,255,0.2)",
    row=1, col=1
)
fig.add_annotation(
    x=2020, y=yearly_grouped["fear_ratio"].max(),
    text="COVID", showarrow=False,
    font=dict(color="rgba(255,255,255,0.4)", size=10),
    row=1, col=1
)

# ---- CHART 2: Stacked sentiment by year ----
for sentiment, color in colors.items():
    col_name = sentiment
    if col_name in yearly_grouped.columns:
        fig.add_trace(go.Bar(
            x=yearly_grouped["year"],
            y=yearly_grouped[col_name],
            name=sentiment.split("/")[1],
            marker_color=color,
            showlegend=True
        ), row=1, col=2)

fig.update_layout(barmode="stack")

# ---- CHART 3: Monthly fear trend 2023-2026 ----
fig.add_trace(go.Scatter(
    x=monthly["year_month"],
    y=monthly["fear_ratio"],
    mode="lines+markers",
    name="Monthly Fear %",
    line=dict(color="#ffa94d", width=2),
    marker=dict(size=6),
    fill="tozeroy",
    fillcolor="rgba(255,107,107,0.1)",
    showlegend=False
), row=2, col=1)

# add threshold line
fig.add_hline(
    y=30, line_dash="dash",
    line_color="#ff6b6b50",
    annotation_text="High risk threshold",
    annotation_font_color="#ff6b6b80",
    row=2, col=1
)

# ---- CHART 4: Post volume by year ----
bar_colors = [
    "#ff6b6b" if y == 2020 else "#6bcb77" if y >= 2023 else "#4a9eff"
    for y in yearly_grouped["year"]
]
fig.add_trace(go.Bar(
    x=yearly_grouped["year"],
    y=yearly_grouped["total"],
    name="Post Volume",
    marker_color=bar_colors,
    showlegend=False,
    text=yearly_grouped["total"],
    textposition="outside",
    textfont=dict(size=9, color="white")
), row=2, col=2)

# ---- CHART 5: Neighborhood trends ----
neighborhood_colors = ["#ff6b6b", "#6bcb77", "#ffd93d", "#4a9eff", "#ff94d2"]
if not neighborhood_trend_df.empty:
    for i, n in enumerate(top_neighborhoods):
        n_data = neighborhood_trend_df[neighborhood_trend_df["neighborhood"] == n]
        if len(n_data) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=n_data["year"],
            y=n_data["fear_ratio"],
            mode="lines+markers",
            name=n,
            line=dict(color=neighborhood_colors[i % len(neighborhood_colors)], width=2),
            marker=dict(size=8),
            showlegend=True
        ), row=3, col=1)

# ---- CHART 6: 2024 vs 2025 comparison ----
comparison_years = [2024, 2025]
comparison_data = yearly_grouped[yearly_grouped["year"].isin(comparison_years)]

sentiments_to_compare = ["Negative/Fear", "Neutral/Concern", "Positive/Reassuring"]
for sentiment in sentiments_to_compare:
    if sentiment in comparison_data.columns:
        fig.add_trace(go.Bar(
            name=f"{sentiment.split('/')[1]}",
            x=comparison_data["year"].astype(str),
            y=comparison_data[sentiment],
            marker_color=colors[sentiment],
            showlegend=False,
            text=comparison_data[sentiment],
            textposition="inside",
            textfont=dict(color="white", size=10)
        ), row=3, col=2)

# ---- LAYOUT ----
fig.update_layout(
    title=dict(
        text="HerSafe Chicago — Temporal Trend Analysis (2013-2026)",
        font=dict(size=20, color="white")
    ),
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white", family="Arial"),
    height=1000,
    legend=dict(
        bgcolor="#1a1a2e",
        bordercolor="#333",
        borderwidth=1
    ),
    barmode="stack"
)

# axis styling
for i in range(1, 4):
    for j in range(1, 3):
        fig.update_xaxes(
            gridcolor="#ffffff10",
            linecolor="#333",
            row=i, col=j
        )
        fig.update_yaxes(
            gridcolor="#ffffff10",
            linecolor="#333",
            row=i, col=j
        )

fig.write_html("trend_analysis.html")
print("Saved trend_analysis.html!")

# ---- KEY INSIGHTS ----
print("\n========== KEY INSIGHTS ==========\n")

# year with highest fear ratio
max_year = yearly_grouped.loc[yearly_grouped["fear_ratio"].idxmax()]
print(f"Highest fear ratio year: {int(max_year['year'])} ({max_year['fear_ratio']}%)")

min_year = yearly_grouped.loc[yearly_grouped["fear_ratio"].idxmin()]
print(f"Lowest fear ratio year:  {int(min_year['year'])} ({min_year['fear_ratio']}%)")

# 2024 vs 2025
y2024 = yearly_grouped[yearly_grouped["year"] == 2024]["fear_ratio"].values
y2025 = yearly_grouped[yearly_grouped["year"] == 2025]["fear_ratio"].values
if len(y2024) > 0 and len(y2025) > 0:
    diff = round(y2025[0] - y2024[0], 1)
    direction = "increased" if diff > 0 else "decreased"
    print(f"\n2024 fear ratio: {y2024[0]}%")
    print(f"2025 fear ratio: {y2025[0]}%")
    print(f"Fear ratio {direction} by {abs(diff)}% from 2024 to 2025")

print("\nOpen trend_analysis.html in your browser!")