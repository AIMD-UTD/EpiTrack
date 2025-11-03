import requests
import spacy
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY", "f5fb544ed1984e49b9ae342dccc4006c")

# Database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Initialize spaCy model (load once, reuse)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️  spaCy model 'en_core_web_sm' not found. Installing...")
    print("   Run: python -m spacy download en_core_web_sm")
    raise

# List of diseases 
groups = [
    ["covid", "influenza", "flu", "coronavirus", "pandemic", "measles", "mumps"],
    ["ebola", "zika", "dengue", "malaria", "tuberculosis", "polio", "cholera"],
    ["hepatitis", "rabies", "norovirus", "rsv", "monkeypox", "avian flu", "swine flu"],
    ["plague", "smallpox", "west nile", "yellow fever", "chikungunya"]
]

# Keywords for NLP analysis
health_keywords = [
    "outbreak", "cases", "hospital", "disease", "ICU", "virus", "infection",
    "symptoms", "diagnosed", "CDC", "WHO", "sick", "illness", "health alert", 
    "quarantine", "epidemic", "transmission", "hospitalization", "pandemic"
]

context_terms = "outbreak OR infection OR epidemic OR cases OR symptoms OR hospitalization OR transmission OR health alert OR disease OR CDC OR WHO OR quarantine"
exclude_terms = "NOT vaccine NOT politics NOT sports NOT costume NOT photography NOT Halloween NOT movie"

def get_db_connection():
    """Establish connection to Neon PostgreSQL database"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    return psycopg2.connect(DATABASE_URL)

def create_table_if_not_exists(conn):
    """Create articles table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT UNIQUE NOT NULL,
            source TEXT,
            published_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            keywords JSONB,
            confidence_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_link ON articles(link);
        CREATE INDEX IF NOT EXISTS idx_published_at ON articles(published_at);
        CREATE INDEX IF NOT EXISTS idx_confidence_score ON articles(confidence_score);
    """)
    conn.commit()
    cursor.close()

def analyze_article_with_nlp(text):
    """
    Analyze article text using spaCy NLP
    Returns keywords found and confidence score
    """
    if not text:
        return [], 0.0
    
    doc = nlp(text.lower())
    
    # Extract keywords and entities
    found_keywords = []
    keyword_counts = {}
    
    # Check for health-related keywords
    for keyword in health_keywords:
        if keyword.lower() in text.lower():
            found_keywords.append(keyword)
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Extract named entities (diseases, organizations, etc.)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"] or "disease" in ent.text.lower() or "virus" in ent.text.lower():
            entities.append(ent.text)
    
    # Calculate confidence score based on keyword frequency and relevance
    # More keywords found = higher confidence
    keyword_score = min(len(found_keywords) / len(health_keywords) * 100, 100)
    entity_score = min(len(entities) * 5, 30)  # Max 30 points for entities
    text_length_score = min(len(text) / 1000 * 10, 10)  # Max 10 points for text length
    
    confidence = keyword_score + entity_score + text_length_score
    confidence = min(confidence, 100.0)  # Cap at 100
    
    # Combine keywords and unique entities
    all_keywords = list(set(found_keywords + entities))
    
    return all_keywords, round(confidence, 2)

def save_articles_to_db(articles, conn):
    """Save articles to PostgreSQL database with deduplication"""
    if not articles:
        print("No articles to save")
        return
    
    cursor = conn.cursor()
    saved_count = 0
    skipped_count = 0
    
    for article in articles:
        try:
            # Check if article already exists (by link)
            cursor.execute("SELECT id FROM articles WHERE link = %s", (article['link'],))
            if cursor.fetchone():
                skipped_count += 1
                continue
            
            # Insert new article
            cursor.execute("""
                INSERT INTO articles (title, description, link, source, published_at, keywords, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                article['title'],
                article['description'],
                article['link'],
                article['source'],
                article['published_at'],
                json.dumps(article['keywords']),
                article['confidence_score']
            ))
            saved_count += 1
        except Exception as e:
            print(f"Error saving article {article.get('link', 'unknown')}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    print(f"✓ Saved {saved_count} new articles. Skipped {skipped_count} duplicates.")

def fetch_and_save_news():
    """Fetch news articles, analyze with NLP, and save to database"""
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        print("   Please set it in your .env file or environment variables")
        return
    
    # Connect to database
    try:
        conn = get_db_connection()
        create_table_if_not_exists(conn)
        print(f"[{datetime.now()}] Connected to database successfully")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return
    
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
        try:
            response = requests.get(url)
            data = response.json()
            if 'articles' in data:
                all_results.extend(data['articles'])
            else:
                print("Error or no articles returned:", data)
        except Exception as e:
            print(f"Error fetching news: {e}")
            continue

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

    print(f"Total filtered relevant articles: {len(filtered)}")
    
    # Process articles with NLP
    processed_articles = []
    for a in filtered:
        # Combine title and description for NLP analysis
        article_text = f"{a.get('title', '')} {a.get('description', '')}"
        
        # Analyze with spaCy
        keywords, confidence = analyze_article_with_nlp(article_text)
        
        # Parse published date
        published_at = None
        try:
            published_at = datetime.fromisoformat(a.get('publishedAt', '').replace('Z', '+00:00'))
        except:
            pass
        
        processed_articles.append({
            'title': a.get('title', ''),
            'description': a.get('description', ''),
            'link': a.get('url', ''),
            'source': a.get('source', {}).get('name', ''),
            'published_at': published_at,
            'keywords': keywords,
            'confidence_score': confidence
        })
    
    # Save to database
    save_articles_to_db(processed_articles, conn)
    conn.close()
    print(f"✓ Processed {len(processed_articles)} articles with NLP analysis")

if __name__ == "__main__":
    fetch_and_save_news()
