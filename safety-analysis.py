

import pandas as pd
import folium
import ast
from collections import Counter

df = pd.read_csv("chicago_safety_located.csv")

# convert string lists back to actual lists
df["neighborhoods_mentioned"] = df["neighborhoods_mentioned"].apply(ast.literal_eval)
df["safety_flags"] = df["safety_flags"].apply(ast.literal_eval)

# ---- COUNT SAFETY SCORE PER NEIGHBORHOOD ----
neighborhood_scores = Counter()
neighborhood_post_count = Counter()

for _, row in df.iterrows():
    for neighborhood in row["neighborhoods_mentioned"]:
        neighborhood_scores[neighborhood] += row["safety_score"]
        neighborhood_post_count[neighborhood] += 1

# turn into dataframe
summary = pd.DataFrame({
    "neighborhood": list(neighborhood_scores.keys()),
    "total_safety_score": list(neighborhood_scores.values()),
    "num_posts": [neighborhood_post_count[n] for n in neighborhood_scores.keys()]
})
summary = summary.sort_values("total_safety_score", ascending=False)

print("Top 15 neighborhoods by safety concern:\n")
print(summary.head(15).to_string(index=False))
summary.to_csv("neighborhood_safety_summary.csv", index=False)

# ---- CHICAGO NEIGHBORHOOD COORDINATES ----
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
    "Rogers Park": (42.0083, -87.6647),
    "South Shore": (41.7606, -87.5671),
    "Grand Boulevard": (41.8107, -87.6153),
    "Washington Heights": (41.7200, -87.6400),
    "Cragin": (41.9196, -87.7650),
    "Printer's Row": (41.8757, -87.6278),
    "North Center": (41.9538, -87.6726),
}

# ---- BUILD THE MAP ----
m = folium.Map(location=[41.8827, -87.6278], zoom_start=11, 
               tiles="CartoDB dark_matter")  # dark theme fits HerSafe

max_score = summary["total_safety_score"].max()

for _, row in summary.iterrows():
    neighborhood = row["neighborhood"]
    score = row["total_safety_score"]
    posts = row["num_posts"]
    
    if neighborhood not in neighborhood_coords:
        continue
    
    lat, lon = neighborhood_coords[neighborhood]
    
    # color based on safety score - red = high concern, yellow = medium, green = low
    if score >= max_score * 0.6:
        color = "red"
    elif score >= max_score * 0.3:
        color = "orange"
    else:
        color = "lightgreen"
    
    # size of circle based on score
    radius = 200 + (score / max_score) * 800
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=radius / 100,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=folium.Popup(
            f"<b>{neighborhood}</b><br>"
            f"Safety Concern Score: {score}<br>"
            f"Posts mentioning this area: {posts}",
            max_width=200
        ),
        tooltip=neighborhood
    ).add_to(m)

# ---- LEGEND ----
legend_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
     background-color: #1a1a1a; padding: 15px; border-radius: 8px;
     color: white; font-family: Arial; font-size: 13px;">
    <b>HerSafe - Chicago Safety Map</b><br>
    <i>Based on Reddit community reports</i><br><br>
    🔴 High concern<br>
    🟠 Medium concern<br>
    🟢 Low concern<br><br>
    <small>Click circles for details</small>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

m.save("hersafe_chicago_map.html")
print("\nMap saved as hersafe_chicago_map.html")
print("Open it in your browser to see the interactive map!")