import requests
import pandas as pd
import time

headers = {"User-Agent": "HerSafe-Research/1.0"}

def scrape_subreddit(subreddit, keywords, pages=5):
    posts = []
    after = None
    
    for page in range(pages):
        print(f"  r/{subreddit} - page {page+1}...")
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": keywords,
            "restrict_sr": True,
            "sort": "relevance",
            "limit": 100,
            "after": after
        }
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print(f"  Error {res.status_code}, skipping...")
            break
        data = res.json()
        children = data["data"]["children"]
        if not children:
            break
        for post in children:
            p = post["data"]
            posts.append({
                "title": p.get("title", ""),
                "text": p.get("selftext", ""),
                "subreddit": p.get("subreddit", ""),
                "score": p.get("score", 0),
                "date": p.get("created_utc", ""),
                "num_comments": p.get("num_comments", 0),
                "url": "https://reddit.com" + p.get("permalink", "")
            })
        after = data["data"]["after"]
        time.sleep(2)
    return posts

# ---- MORE SUBREDDITS + MORE KEYWORD VARIATIONS ----
searches = [
    ("chicago", "street safety night alone woman"),
    ("chicago", "neighborhood avoid dangerous"),
    ("chicago", "harassment followed scared"),
    ("chicago", "safe walk alone night"),
    ("chicago", "crime mugged attacked"),
    ("AskChicago", "safe neighborhood"),
    ("AskChicago", "avoid dangerous area"),
    ("AskChicago", "walking alone night"),
    ("TwoXChromosomes", "chicago street unsafe"),
    ("AskWomen", "chicago safety alone"),
]

all_posts = []
for subreddit, keywords in searches:
    print(f"\nScraping r/{subreddit} with: '{keywords}'")
    posts = scrape_subreddit(subreddit, keywords, pages=5)
    all_posts.extend(posts)
    print(f"  Got {len(posts)} posts")
    time.sleep(3)

df = pd.DataFrame(all_posts)
df = df[df["title"].str.strip() != ""]
df = df.drop_duplicates(subset=["title"])

# load existing data and combine
existing = pd.read_csv("chicago_safety_reddit.csv")
combined = pd.concat([existing, df], ignore_index=True)
combined = combined.drop_duplicates(subset=["title"])

combined.to_csv("chicago_safety_reddit.csv", index=False)
print(f"\nDone! Total posts now: {len(combined)}")

print(f"\nDone! Collected {len(df)} total posts")
print(df.head())
print("Total posts:", len(df))
print("\nColumn names:", df.columns.tolist())
print("\nSample titles:")
print(df["title"].head(10).tolist())
print("\nSample text:")
print(df["text"].head(3).tolist())