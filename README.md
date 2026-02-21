'''chicago_safety_reddit.csv        → raw data (1218 posts)
        ↓
analysis.py / safety-analysis.py → location extraction
        ↓
chicago_safety_located.csv       → posts with neighborhoods
        ↓
sentiment-analysis.py            → sentiment labeling
        ↓
chicago_safety_sentiment.csv     → posts with sentiment
neighborhood_sentiment_summary.csv → scores per neighborhood
        ↓
hersafe_chicago_map.html         → interactive map'''
