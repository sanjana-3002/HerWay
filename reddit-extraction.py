import requests
import pandas as pd
import time

headers = {"User-Agent": "HerSafe-Research/1.0"}

def scrape_subreddit(subreddit, keywords, pages=3):
    posts = []
    after = None
    
    for page in range(pages):
        print(f"  Scraping r/{subreddit} - page {page+1}...")
        
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
            print(f"  Error {res.status_code} on r/{subreddit}, skipping...")
            break
        
        data = res.json()
        children = data["data"]["children"]
        
        if not children:
            print(f"  No more posts in r/{subreddit}")
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

# ---- CHICAGO SPECIFIC SUBREDDITS ----
subreddits = [
    "chicago",
    "AskChicago", 
    "ChicagoSports",      # sometimes has neighborhood discussions
    "TwoXChromosomes",    # women sharing safety experiences
    "AskWomen",
    "femalefashionadvice" # surprisingly active safety discussion thread
]

# ---- KEYWORDS RELEVANT TO HERSAFE ----
keywords = "street unsafe harassment followed scared avoid dark alone night walking"

# ---- RUN THE SCRAPER ----
all_posts = []

for sub in subreddits:
    print(f"\nScraping r/{sub}...")
    posts = scrape_subreddit(sub, keywords, pages=3)
    all_posts.extend(posts)
    print(f"  Got {len(posts)} posts from r/{sub}")
    time.sleep(3)  # pause between subreddits

# ---- SAVE TO CSV ----
df = pd.DataFrame(all_posts)

# Remove empty posts
df = df[df["title"].str.strip() != ""]
df = df.drop_duplicates(subset=["title"])

df.to_csv("chicago_safety_reddit.csv", index=False)
print(f"\nDone! Collected {len(df)} total posts")
print(df.head())

df = pd.read_csv("chicago_safety_reddit.csv")
print("Total posts:", len(df))
print("\nColumn names:", df.columns.tolist())
print("\nSample titles:")
print(df["title"].head(10).tolist())
print("\nSample text:")
print(df["text"].head(3).tolist())