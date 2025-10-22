from newsdataapi import NewsDataApiClient
import pandas as pd
from datetime import datetime, timedelta

# Initialize with API key
api = NewsDataApiClient(apikey="pub_4fecaf09d4e74663b4c8719d9ae2945d")
#end_date = datetime.now().strftime("%Y-%m-%d")
#start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# Fetch the latest news mentioning 'disease'
response = api.news_api(
    q="COVID-19 OR influenza OR flu OR coronavirus OR pandemic",  # add more diseases here
    category="health"  # This helps filter for health-related news
    
)

for article in response["results"]:
    print("Title:", article["title"])
    print("Date:", article["pubDate"])
    print("Description:", article["description"])
    print("Link:", article["link"])
    print("--------------------------")

# List of dictionaries for each article
data = [
            {
                "title": a["title"],
                "date": a["pubDate"],
                "description": a["description"],
                "link": a["link"]
            }
            # For every article, we get the key info and storie it in dict
            for a in response["results"] 
        ]

# Create a dataframe with pandas
df = pd.DataFrame(data)

# Convert to a csv file
df.to_csv("disease_news.csv", index=False)