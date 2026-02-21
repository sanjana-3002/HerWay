chicago_safety_reddit.csv  
→ Raw Reddit dataset (1,218 safety-related posts)

        ↓

analysis.py / safety_analysis.py  
→ Extract neighborhood names from post text using location parsing

        ↓

chicago_safety_located.csv  
→ Posts enriched with mapped Chicago neighborhoods

        ↓

sentiment_analysis.py  
→ Sentiment classification (positive / neutral / negative)

        ↓

chicago_safety_sentiment.csv  
→ Posts with sentiment labels

neighborhood_sentiment_summary.csv  
→ Aggregated safety score per neighborhood

        ↓

hersafe_chicago_map.html  
→ Interactive visualization of neighborhood-level safety insights
