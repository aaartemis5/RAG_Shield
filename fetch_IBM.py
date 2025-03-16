import requests
import feedparser
import json
from datetime import datetime
from langchain.schema import Document

# IBM Security Blog RSS Feed URL
RSS_FEED_URL = "https://www.ibm.com/blog/category/security/feed/"

# JSON File to Store Data
JSON_FILE = "ibm_security_blog.json"

# Number of articles to fetch
ARTICLE_LIMIT = 10

def fetch_rss_feed(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.content

def parse_rss_feed(feed_content):
    feed = feedparser.parse(feed_content)
    articles = []
    for entry in feed.entries[:ARTICLE_LIMIT]:
        article = {
            "title": entry.title,
            "link": entry.link,
            "date": entry.published,
            "summary": entry.summary
        }
        articles.append(article)
    return articles

def process_articles(articles):
    documents = []
    for article in articles:
        doc = Document(
            page_content=article["summary"],
            metadata={
                "title": article["title"],
                "date": article["date"],
                "link": article["link"],
                "source": RSS_FEED_URL
            }
        )
        documents.append(doc)
    return documents

def save_to_json(documents):
    formatted_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]
    with open(JSON_FILE, "w") as file:
        json.dump(formatted_data, file, indent=4)
    print(f"✅ Data saved to {JSON_FILE} (Total articles stored: {len(formatted_data)})")

def run():
    print(f"\n🔄 Fetching IBM Security Blog RSS Feed at {datetime.now()}")
    feed_content = fetch_rss_feed(RSS_FEED_URL)
    articles = parse_rss_feed(feed_content)
    if articles:
        print(f"🛠️ Processing {len(articles)} articles...")
        documents = process_articles(articles)
        save_to_json(documents)
        print("🎉 Data update complete!\n")
    else:
        print("⚠️ No articles found.\n")

# Execute the script
run()
