import pandas as pd
import re

# ---- LOAD DATA ----
df = pd.read_csv("chicago_safety_reddit.csv")
df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
print(f"Total posts loaded: {len(df)}")

# ---- CHICAGO NEIGHBORHOODS ----
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
    "East Side", "South Deering", "Millennium Park", "Navy Pier", "Magnificent Mile",
    "South Loop", "Near North Side", "Near West Side", "Streeterville",
    "Andersonville", "Boystown", "Printer's Row", "Greektown", "Chinatown",
    "Little Italy", "University Village", "Fulton Market", "West Loop",
    "Fulton Park", "Washington Heights", "Fernwood"
]

# names that only count if Chicago is mentioned nearby
ambiguous = ["Austin", "Clearing", "Beverly", "Douglas", "Pullman",
             "Riverdale", "Fernwood", "Ashburn"]

# ---- SAFETY KEYWORDS ----
safety_keywords = [
    "unsafe", "harassment", "harassed", "followed", "scared", "scary",
    "avoid", "dangerous", "danger", "attack", "attacked", "mugged",
    "robbery", "threat", "threatened", "afraid", "fear", "dark",
    "alone", "sketchy", "catcall", "catcalled", "creepy", "stalked",
    "knife", "gun", "shooting", "assault", "uncomfortable", "uneasy",
    "intimidating", "grabbed", "chased", "aggressive", "threatening",
    "suspicious", "worried", "terrified", "horrified", "traumatized"
]

# ---- CHICAGO CONTEXT CHECK ----
def is_chicago_relevant(text, subreddit, neighborhood):
    text_lower = text.lower()
    subreddit_lower = str(subreddit).lower()

    # always trust chicago-specific subreddits
    if any(s in subreddit_lower for s in ["chicago", "askchicago"]):
        return True

    # ambiguous names need explicit Chicago mention in text
    if neighborhood in ambiguous:
        return any(w in text_lower for w in ["chicago", " chi ", "illinois", " il "])

    # for all others, if Chicago mentioned anywhere trust it
    if "chicago" in text_lower:
        return True

    return False

# ---- EXTRACTION FUNCTIONS ----
def extract_neighborhoods(row):
    text = row["combined"]
    subreddit = row["subreddit"]
    if not isinstance(text, str):
        return []
    found = []
    for neighborhood in chicago_neighborhoods:
        if re.search(r'\b' + re.escape(neighborhood) + r'\b', text, re.IGNORECASE):
            if is_chicago_relevant(text, subreddit, neighborhood):
                found.append(neighborhood)
    return found

def extract_safety_flags(text):
    if not isinstance(text, str):
        return []
    return [kw for kw in safety_keywords
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE)]

# ---- APPLY ----
print("Extracting neighborhoods and safety flags...")
df["neighborhoods_mentioned"] = df.apply(extract_neighborhoods, axis=1)
df["safety_flags"] = df["combined"].apply(extract_safety_flags)
df["safety_score"] = df["safety_flags"].apply(len)

# keep only posts with at least one neighborhood
df_located = df[df["neighborhoods_mentioned"].apply(len) > 0].copy()
df_located = df_located.sort_values("safety_score", ascending=False)

# ---- SAVE ----
df_located.to_csv("chicago_safety_located.csv", index=False)

print(f"\nTotal posts: {len(df)}")
print(f"Posts with Chicago neighborhoods: {len(df_located)}")

print(f"\nTop 10 posts by safety concern:\n")
for _, row in df_located.head(10).iterrows():
    print(f"Title: {row['title']}")
    print(f"Neighborhoods: {row['neighborhoods_mentioned']}")
    print(f"Safety flags: {row['safety_flags']}")
    print(f"Score: {row['safety_score']}")
    print("---")

# ---- NEIGHBORHOOD FREQUENCY ----
from collections import Counter
neighborhood_counts = Counter()
for neighborhoods in df_located["neighborhoods_mentioned"]:
    for n in neighborhoods:
        neighborhood_counts[n] += 1

print(f"\nTop 20 most mentioned Chicago neighborhoods:")
for neighborhood, count in neighborhood_counts.most_common(20):
    print(f"  {neighborhood}: {count} posts")