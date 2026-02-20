import pandas as pd
import re

df = pd.read_csv("chicago_safety_reddit.csv")
print("Total posts:", len(df))
print("\nColumn names:", df.columns.tolist())
print("\nSample titles:")
print(df["title"].head(10).tolist())
print("\nSample text:")
print(df["text"].head(3).tolist())

# ---- CHICAGO NEIGHBORHOODS LIST ----
chicago_neighborhoods = [
    "Loop", "River North", "Gold Coast", "Lincoln Park", "Lakeview",
    "Wicker Park", "Bucktown", "Logan Square", "Pilsen", "Bridgeport",
    "Hyde Park", "Woodlawn", "Englewood", "West Englewood", "Auburn Gresham",
    "Chatham", "South Shore", "Bronzeville", "Douglas", "Grand Boulevard",
    "Washington Park", "Grand Crossing", "Roseland", "Pullman", "Hegewisch",
    "Rogers Park", "Edgewater", "Uptown", "Ravenswood", "North Center",
    "Irving Park", "Avondale", "Humboldt Park", "Garfield Park", "West Garfield Park",
    "East Garfield Park", "Austin", "West Town", "Ukrainian Village", "Noble Square",
    "Little Village", "Back of the Yards", "McKinley Park", "Brighton Park",
    "Clearing", "Archer Heights", "Gage Park", "Chicago Lawn", "West Lawn",
    "Marquette Park", "Ashburn", "Beverly", "Morgan Park", "Mount Greenwood",
    "Norwood Park", "Jefferson Park", "Forest Glen", "North Park", "Albany Park",
    "Portage Park", "Dunning", "Belmont Cragin", "Hermosa", "Montclare",
    "Galewood", "Cragin", "Riverdale", "Calumet Heights", "South Chicago",
    "East Side", "South Deering", "Millenium Park", "Navy Pier", "Magnificent Mile",
    "South Loop", "Near North Side", "Near West Side", "Streeterville",
    "Andersonville", "Boystown", "Printer's Row", "Greek Town", "Chinatown",
    "Little Italy", "University Village", "Fulton Market", "West Loop",
    "Fulton Park", "Washington Heights", "Fernwood"
]

# ---- SAFETY KEYWORDS TO FLAG ----
safety_keywords = [
    "unsafe", "harassment", "harassed", "followed", "scared", "scary",
    "avoid", "dangerous", "danger", "attack", "attacked", "mugged",
    "robbery", "threat", "threatened", "afraid", "fear", "dark",
    "alone", "sketchy", "catcall", "catcalled", "creepy", "stalked",
    "knife", "gun", "shooting", "assault", "uncomfortable", "uneasy"
]

def extract_neighborhoods(text):
    if not isinstance(text, str):
        return []
    found = []
    for neighborhood in chicago_neighborhoods:
        # case insensitive match
        if re.search(r'\b' + re.escape(neighborhood) + r'\b', text, re.IGNORECASE):
            found.append(neighborhood)
    return found

def extract_safety_flags(text):
    if not isinstance(text, str):
        return []
    found = []
    for keyword in safety_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            found.append(keyword)
    return found

def safety_score(flags):
    return len(flags)  # more keywords = higher concern score

# ---- APPLY TO DATAFRAME ----
# combine title + text for better coverage
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")

df["neighborhoods_mentioned"] = df["combined"].apply(extract_neighborhoods)
df["safety_flags"] = df["combined"].apply(extract_safety_flags)
df["safety_score"] = df["safety_flags"].apply(safety_score)

# ---- FILTER: only keep posts that mention at least one neighborhood ----
df_located = df[df["neighborhoods_mentioned"].apply(len) > 0].copy()
df_located = df_located.sort_values("safety_score", ascending=False)

# ---- SAVE ----
df_located.to_csv("chicago_safety_located.csv", index=False)

print(f"Total posts: {len(df)}")
print(f"Posts with Chicago neighborhoods: {len(df_located)}")
print(f"\nTop 10 posts by safety concern:\n")

for _, row in df_located.head(10).iterrows():
    print(f"Title: {row['title']}")
    print(f"Neighborhoods: {row['neighborhoods_mentioned']}")
    print(f"Safety flags: {row['safety_flags']}")
    print(f"Score: {row['safety_score']}")
    print("---")