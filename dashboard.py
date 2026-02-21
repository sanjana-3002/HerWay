import pandas as pd

df = pd.read_csv("neighborhood_sentiment_summary.csv")
df = df[df["risk_rating"] != "Insufficient Data"]
df = df.sort_values("negative_ratio", ascending=False)

high = df[df["risk_rating"] == "High Risk"]
medium = df[df["risk_rating"] == "Medium Risk"]
low = df[df["risk_rating"] == "Lower Risk"]

def make_rows(data):
    rows = ""
    for _, r in data.iterrows():
        rows += f"""
        <tr>
            <td><b>{r['neighborhood']}</b></td>
            <td>{r['total_posts']}</td>
            <td style='color:#ff6b6b'>{r['negative_fear']}</td>
            <td style='color:#ffd93d'>{r['neutral_concern']}</td>
            <td style='color:#6bcb77'>{r['positive_reassuring']}</td>
            <td>{int(r['negative_ratio']*100)}%</td>
        </tr>"""
    return rows

html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HerSafe Chicago - Safety Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0f0f1a; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; padding: 30px; }}
        h1 {{ text-align: center; font-size: 2.2em; color: #fff; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #aaa; margin-bottom: 40px; font-size: 1em; }}

        .stats-row {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; flex-wrap: wrap; }}
        .stat-box {{ background: #1a1a2e; border-radius: 12px; padding: 20px 30px; text-align: center; min-width: 150px; }}
        .stat-box .number {{ font-size: 2.5em; font-weight: bold; }}
        .stat-box .label {{ font-size: 0.85em; color: #aaa; margin-top: 5px; }}
        .red {{ color: #ff6b6b; }} .orange {{ color: #ffa94d; }}
        .green {{ color: #6bcb77; }} .white {{ color: #fff; }}

        .section {{ margin-bottom: 35px; }}
        .section h2 {{ font-size: 1.3em; margin-bottom: 12px; padding: 8px 15px;
                       border-radius: 8px; display: inline-block; }}
        .high-title {{ background: rgba(255,107,107,0.15); color: #ff6b6b; }}
        .med-title  {{ background: rgba(255,169,77,0.15);  color: #ffa94d; }}
        .low-title  {{ background: rgba(107,203,119,0.15); color: #6bcb77; }}

        table {{ width: 100%; border-collapse: collapse; background: #1a1a2e; border-radius: 10px; overflow: hidden; }}
        th {{ background: #16213e; padding: 12px 15px; text-align: left; font-size: 0.85em; color: #aaa; text-transform: uppercase; }}
        td {{ padding: 11px 15px; border-bottom: 1px solid #222; font-size: 0.95em; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #16213e; }}

        .footer {{ text-align: center; color: #555; margin-top: 40px; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>HerSafe Chicago</h1>
    <p class="subtitle">Community Safety Signals from Reddit &middot; {len(df)} neighborhoods analyzed &middot; {df['total_posts'].sum()} posts</p>

    <div class="stats-row">
        <div class="stat-box"><div class="number red">{len(high)}</div><div class="label">High Risk Neighborhoods</div></div>
        <div class="stat-box"><div class="number orange">{len(medium)}</div><div class="label">Medium Risk Neighborhoods</div></div>
        <div class="stat-box"><div class="number green">{len(low)}</div><div class="label">Lower Risk Neighborhoods</div></div>
        <div class="stat-box"><div class="number white">{df['total_posts'].sum()}</div><div class="label">Total Posts Analyzed</div></div>
        <div class="stat-box"><div class="number white">{df['negative_fear'].sum()}</div><div class="label">Fearful Posts Detected</div></div>
    </div>

    <div class="section">
        <h2 class="high-title">High Risk Neighborhoods</h2>
        <table>
            <tr><th>Neighborhood</th><th>Total Posts</th><th>Fearful</th><th>Concerned</th><th>Reassuring</th><th>Fear %</th></tr>
            {make_rows(high)}
        </table>
    </div>

    <div class="section">
        <h2 class="med-title">Medium Risk Neighborhoods</h2>
        <table>
            <tr><th>Neighborhood</th><th>Total Posts</th><th>Fearful</th><th>Concerned</th><th>Reassuring</th><th>Fear %</th></tr>
            {make_rows(medium)}
        </table>
    </div>

    <div class="section">
        <h2 class="low-title">Lower Risk Neighborhoods</h2>
        <table>
            <tr><th>Neighborhood</th><th>Total Posts</th><th>Fearful</th><th>Concerned</th><th>Reassuring</th><th>Fear %</th></tr>
            {make_rows(low)}
        </table>
    </div>

    <div class="footer">
        HerSafe &middot; Data sourced from Reddit community posts &middot; For research purposes only
    </div>
</body>
</html>"""

with open("hersafe_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard saved as hersafe_dashboard.html")
print("Open it in your browser!")