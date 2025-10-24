import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = os.getenv("NEWSAPI_KEY", "f5fb544ed1984e49b9ae342dccc4006c")

# List of diseases 
groups = [
    ["covid", "influenza", "flu", "coronavirus", "pandemic", "measles", "mumps"],
    ["ebola", "zika", "dengue", "malaria", "tuberculosis", "polio", "cholera"],
    ["hepatitis", "rabies", "norovirus", "rsv", "monkeypox", "avian flu", "swine flu"],
    ["plague", "smallpox", "west nile", "yellow fever", "chikungunya"]
]

context_terms = "outbreak OR infection OR epidemic OR cases OR symptoms OR hospitalization OR transmission OR health alert OR disease OR CDC OR WHO OR quarantine"
exclude_terms = "NOT vaccine NOT politics NOT sports NOT costume NOT photography NOT Halloween NOT movie"

def fetch_and_save_news():
    all_results = []
    for disease_group in groups:
        diseases_or = " OR ".join(disease_group)
        query = f"({diseases_or}) AND ({context_terms}) {exclude_terms}"
        url = (
            f'https://newsapi.org/v2/everything'
            f'?q={query}'
            f'&language=en'
            f'&sortBy=publishedAt'
            f'&pageSize=100'
            f'&apiKey={API_KEY}'
        )
        print(f"[{datetime.now()}] Fetching with query: {query[:80]}...")
        response = requests.get(url)
        data = response.json()
        if 'articles' in data:
            all_results.extend(data['articles'])
        else:
            print("Error or no articles returned:", data)

    # Post-filter for health relevance
    relevant_terms = [
        "outbreak", "cases", "hospital", "disease", "ICU", "virus", "infection",
        "symptoms", "diagnosed", "CDC", "WHO", "sick", "illness", "health alert", "quarantine", "epidemic"
    ]
    filtered = [
    a for a in all_results
    if any(
        term in ((a.get('title') or '') + (a.get('description') or '')).lower()
        for term in relevant_terms
    )
]


    print(f"Total deduplicated relevant articles: {len(filtered)}")
    result = []
    for a in filtered:
        result.append({
            'title': a.get('title', ''),
            'date': a.get('publishedAt', ''),
            'description': a.get('description', ''),
            'link': a.get('url', ''),
            'source': a.get('source', {}).get('name', ''),
            'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Create CSV file using data
    df = pd.DataFrame(result)
    if os.path.exists("newsapi_news.csv"):
        existing_df = pd.read_csv("newsapi_news.csv")
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['link'], keep='last')
        combined_df.to_csv("newsapi_news.csv", index=False)
        print(f"✓ Added {len(df)} articles. Total unique: {len(combined_df)}")
    else:
        df.to_csv("newsapi_news.csv", index=False)
        print(f"✓ Created new file with {len(df)} health-focused articles")

if __name__ == "__main__":
    fetch_and_save_news()
