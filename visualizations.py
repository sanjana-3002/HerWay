import pandas as pd
import ast
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# ---- LOAD DATA ----
df = pd.read_csv("chicago_safety_sentiment.csv")
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
df["date"] = pd.to_datetime(df["date"], unit="s")
df["hour"] = df["date"].dt.hour
df["day_of_week"] = df["date"].dt.day_name()
df["is_night"] = df["hour"].apply(lambda h: "Night (8pm-4am)" if (h >= 20 or h < 4) else "Evening (4pm-8pm)" if h >= 16 else "Day (4am-4pm)")

summary = pd.read_csv("neighborhood_sentiment_summary.csv")
summary = summary[summary["risk_rating"] != "Insufficient Data"]

print("Data loaded! Building visualizations...\n")

# ================================================
# STEP 1 — WORD CLOUDS
# ================================================
print("Building word clouds...")

stopwords = set([
    "chicago", "the", "a", "an", "and", "or", "but", "in", "on", "at",
    "to", "for", "of", "with", "is", "it", "this", "that", "was", "are",
    "be", "have", "has", "had", "do", "did", "will", "would", "could",
    "should", "may", "might", "i", "my", "me", "we", "our", "you", "your",
    "he", "she", "they", "his", "her", "their", "its", "just", "like",
    "really", "very", "so", "not", "no", "if", "from", "by", "about",
    "as", "up", "out", "there", "when", "what", "which", "who", "how",
    "one", "any", "all", "more", "also", "get", "go", "been", "than",
    "then", "some", "can", "into", "area", "place", "neighborhood",
    "people", "think", "know", "feel", "time", "re", "ve", "ll", "don",
    "doesn", "didn", "isn", "aren", "wasn", "weren", "much", "even",
    "never", "always", "still", "now", "here", "see", "going", "want"
])

fearful_text = " ".join(df[df["sentiment"] == "Negative/Fear"]["combined"].tolist())
reassuring_text = " ".join(df[df["sentiment"] == "Positive/Reassuring"]["combined"].tolist())
neutral_text = " ".join(df[df["sentiment"] == "Neutral/Concern"]["combined"].tolist())

def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.lower().split()
    return " ".join([w for w in words if w not in stopwords and len(w) > 3])

fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.patch.set_facecolor('#0f0f1a')

configs = [
    (fearful_text,    "Fearful Posts",      "Reds",    axes[0]),
    (neutral_text,    "Concerned Posts",    "YlOrBr",  axes[1]),
    (reassuring_text, "Reassuring Posts",   "Greens",  axes[2]),
]

for text, title, colormap, ax in configs:
    cleaned = clean_text(text)
    if not cleaned.strip():
        ax.text(0.5, 0.5, "Not enough data", ha="center", va="center",
                color="white", fontsize=14, transform=ax.transAxes)
    else:
        wc = WordCloud(
            width=600, height=400,
            background_color="#0f0f1a",
            colormap=colormap,
            max_words=80,
            stopwords=stopwords,
            collocations=False,
            prefer_horizontal=0.8
        ).generate(cleaned)
        ax.imshow(wc, interpolation="bilinear")

    ax.set_title(title, color="white", fontsize=16, fontweight="bold", pad=15)
    ax.axis("off")
    ax.set_facecolor("#0f0f1a")

plt.suptitle("HerSafe Chicago — What People Are Saying",
             color="white", fontsize=20, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("wordclouds.png", dpi=150, bbox_inches="tight",
            facecolor="#0f0f1a", edgecolor="none")
plt.close()
print("  wordclouds.png saved!")

# ================================================
# STEP 2 — TIME ANALYSIS
# ================================================
print("Building time analysis charts...")

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.patch.set_facecolor('#0f0f1a')

for ax in axes.flatten():
    ax.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# --- Chart 1: Posts by Hour of Day ---
ax1 = axes[0, 0]
fearful_hours = df[df["sentiment"] == "Negative/Fear"]["hour"]
reassuring_hours = df[df["sentiment"] == "Positive/Reassuring"]["hour"]

ax1.hist(fearful_hours, bins=24, range=(0,24), alpha=0.7,
         color="#ff6b6b", label="Fearful", edgecolor="none")
ax1.hist(reassuring_hours, bins=24, range=(0,24), alpha=0.7,
         color="#6bcb77", label="Reassuring", edgecolor="none")
ax1.set_title("Posts by Hour of Day", color="white", fontsize=14, fontweight="bold")
ax1.set_xlabel("Hour (24hr)", color="#aaa")
ax1.set_ylabel("Number of Posts", color="#aaa")
ax1.legend(facecolor="#1a1a2e", labelcolor="white")
ax1.axvspan(20, 24, alpha=0.08, color="yellow", label="Night")
ax1.axvspan(0, 4, alpha=0.08, color="yellow")

# --- Chart 2: Day/Night Split by Sentiment ---
ax2 = axes[0, 1]
time_sentiment = df.groupby(["is_night", "sentiment"]).size().unstack(fill_value=0)
colors = {"Negative/Fear": "#ff6b6b", "Neutral/Concern": "#ffd93d",
          "Positive/Reassuring": "#6bcb77"}
time_sentiment.plot(kind="bar", ax=ax2, color=[colors.get(c, "gray")
                    for c in time_sentiment.columns], edgecolor="none", width=0.7)
ax2.set_title("Time of Day vs Sentiment", color="white", fontsize=14, fontweight="bold")
ax2.set_xlabel("", color="#aaa")
ax2.set_ylabel("Number of Posts", color="#aaa")
ax2.tick_params(axis='x', rotation=15)
ax2.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

# --- Chart 3: Day of Week ---
ax3 = axes[1, 0]
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_sentiment = df.groupby(["day_of_week", "sentiment"]).size().unstack(fill_value=0)
day_sentiment = day_sentiment.reindex(day_order)
day_sentiment.plot(kind="bar", ax=ax3, color=[colors.get(c, "gray")
                   for c in day_sentiment.columns], edgecolor="none", width=0.7)
ax3.set_title("Day of Week vs Sentiment", color="white", fontsize=14, fontweight="bold")
ax3.set_xlabel("", color="#aaa")
ax3.set_ylabel("Number of Posts", color="#aaa")
ax3.tick_params(axis='x', rotation=30)
ax3.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

# --- Chart 4: Night Fear Rate by Top Neighborhoods ---
ax4 = axes[1, 1]
top_neighborhoods = ["Loop", "Lincoln Park", "Lakeview", "Logan Square",
                     "Uptown", "Rogers Park", "Hyde Park", "Englewood",
                     "Austin", "Humboldt Park"]

night_fear = []
for n in top_neighborhoods:
    n_df = df[df["neighborhoods_mentioned"].apply(lambda x: n in x)]
    night_df = n_df[n_df["is_night"] == "Night (8pm-4am)"]
    if len(night_df) > 0:
        fear_rate = len(night_df[night_df["sentiment"] == "Negative/Fear"]) / len(night_df)
    else:
        fear_rate = 0
    night_fear.append(fear_rate * 100)

bar_colors = ["#ff6b6b" if f >= 40 else "#ffa94d" if f >= 20 else "#6bcb77"
              for f in night_fear]
bars = ax4.barh(top_neighborhoods, night_fear, color=bar_colors, edgecolor="none")
ax4.set_title("Night-Time Fear Rate by Neighborhood", color="white",
              fontsize=14, fontweight="bold")
ax4.set_xlabel("% of Night Posts that are Fearful", color="#aaa")
ax4.axvline(x=30, color="#ffd93d", linestyle="--", alpha=0.5, linewidth=1)

for i, (bar, val) in enumerate(zip(bars, night_fear)):
    ax4.text(val + 0.5, bar.get_y() + bar.get_height()/2,
             f"{val:.0f}%", va="center", color="white", fontsize=9)

plt.suptitle("HerSafe Chicago — Time Analysis of Safety Concerns",
             color="white", fontsize=18, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("time_analysis.png", dpi=150, bbox_inches="tight",
            facecolor="#0f0f1a", edgecolor="none")
plt.close()
print("  time_analysis.png saved!")

# ================================================
# STEP 3 — ADVANCED INTERACTIVE VISUALIZATIONS
# ================================================
print("Building advanced Plotly visualizations...")

# --- Chart A: Bubble Chart — Fear vs Reassurance per Neighborhood ---
fig_bubble = px.scatter(
    summary,
    x="positive_reassuring",
    y="negative_fear",
    size="total_posts",
    color="risk_rating",
    hover_name="neighborhood",
    hover_data={"total_posts": True, "negative_ratio": True,
                "risk_rating": False, "color": False},
    color_discrete_map={
        "High Risk": "#ff6b6b",
        "Medium Risk": "#ffa94d",
        "Lower Risk": "#6bcb77"
    },
    title="Neighborhood Safety — Fear vs Reassurance (bubble size = total posts)",
    labels={
        "positive_reassuring": "Reassuring Posts",
        "negative_fear": "Fearful Posts",
        "risk_rating": "Risk Level"
    }
)
fig_bubble.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    title_font_size=16
)
fig_bubble.write_html("chart_bubble.html")
print("  chart_bubble.html saved!")

# --- Chart B: Stacked Bar — Sentiment breakdown for top 20 neighborhoods ---
top20 = summary.nlargest(20, "total_posts").sort_values("negative_ratio", ascending=True)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Fearful", x=top20["neighborhood"], y=top20["negative_fear"],
    marker_color="#ff6b6b"
))
fig_bar.add_trace(go.Bar(
    name="Concerned", x=top20["neighborhood"], y=top20["neutral_concern"],
    marker_color="#ffd93d"
))
fig_bar.add_trace(go.Bar(
    name="Reassuring", x=top20["neighborhood"], y=top20["positive_reassuring"],
    marker_color="#6bcb77"
))
fig_bar.update_layout(
    barmode="stack",
    title="Sentiment Breakdown — Top 20 Most Mentioned Neighborhoods",
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    xaxis_tickangle=-35,
    legend=dict(bgcolor="#1a1a2e"),
    title_font_size=16
)
fig_bar.write_html("chart_sentiment_breakdown.html")
print("  chart_sentiment_breakdown.html saved!")

# --- Chart C: Heatmap — Hour vs Day of Week fear density ---
pivot = df[df["sentiment"] == "Negative/Fear"].groupby(
    ["day_of_week", "hour"]
).size().reset_index(name="count")

pivot_table = pivot.pivot(index="day_of_week", columns="hour", values="count").fillna(0)
pivot_table = pivot_table.reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

fig_heat = px.imshow(
    pivot_table,
    color_continuous_scale="Reds",
    title="Fearful Posts Heatmap — Hour vs Day of Week",
    labels=dict(x="Hour of Day", y="Day of Week", color="Fearful Posts"),
    aspect="auto"
)
fig_heat.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    title_font_size=16
)
fig_heat.write_html("chart_heatmap.html")
print("  chart_heatmap.html saved!")

# --- Chart D: Fear ratio trend line across neighborhoods ---
sorted_df = summary[summary["total_posts"] >= 5].sort_values("negative_ratio", ascending=False)

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=sorted_df["neighborhood"],
    y=sorted_df["negative_ratio"] * 100,
    mode="lines+markers",
    line=dict(color="#ffa94d", width=2),
    marker=dict(
        size=sorted_df["total_posts"] / 3,
        color=sorted_df["negative_ratio"],
        colorscale="RdYlGn_r",
        showscale=True,
        colorbar=dict(title="Fear Ratio")
    ),
    hovertemplate="<b>%{x}</b><br>Fear Rate: %{y:.1f}%<extra></extra>"
))
fig_line.add_hline(y=50, line_dash="dash", line_color="#ff6b6b",
                   annotation_text="High Risk threshold (50%)")
fig_line.add_hline(y=30, line_dash="dash", line_color="#ffa94d",
                   annotation_text="Medium Risk threshold (30%)")
fig_line.update_layout(
    title="Fear Rate Across Neighborhoods (min 5 posts, marker size = post count)",
    xaxis_tickangle=-40,
    template="plotly_dark",
    paper_bgcolor="#0f0f1a",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    yaxis_title="Fear Rate %",
    title_font_size=16
)
fig_line.write_html("chart_fearrate.html")
print("  chart_fearrate.html saved!")

print("\n✓ All visualizations complete! Open these files in your browser:")
print("  - wordclouds.png")
print("  - time_analysis.png")
print("  - chart_bubble.html")
print("  - chart_sentiment_breakdown.html")
print("  - chart_heatmap.html")
print("  - chart_fearrate.html")