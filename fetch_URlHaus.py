import requests
import json
import schedule
import time
from langchain.schema import Document
from datetime import datetime

# ✅ URLhaus API Endpoint
URLHAUS_RECENT_URL = "https://urlhaus-api.abuse.ch/v1/urls/recent/"

# ✅ JSON File to Store Data
JSON_FILE = "urlhaus_threats.json"

# ✅ Number of URLs to fetch (Limit to avoid processing overload)
URL_LIMIT = 50

# ✅ Function to Fetch the Latest Malicious URLs from URLhaus
def fetch_recent_malware_urls():
    headers = {"Accept": "application/json"}
    
    print("\n🚀 [1/4] Fetching latest malware URLs from URLhaus...")
    response = requests.get(URLHAUS_RECENT_URL, headers=headers)  

    if response.status_code == 200:
        url_data = response.json().get("urls", [])[:URL_LIMIT]

        if not url_data:
            print("⚠️ No new threats found in URLhaus.")
            return []

        # Extract relevant details and handle missing fields
        malicious_urls = []
        for idx, entry in enumerate(url_data, start=1):
            url_info = {
                "url": entry.get("url", "Unknown"),
                "date_added": entry.get("date_added", "Unknown"),
                "threat": entry.get("threat", "Unknown"),
                "reporter": entry.get("reporter", "Unknown"),
                "status": entry.get("status", "Unknown"),
                "malware_type": entry.get("tags", [])
            }
            malicious_urls.append(url_info)
            print(f"🔍 [{idx}/{len(url_data)}] Retrieved: {url_info['url']} - {url_info['threat']}")

        print(f"✅ Total {len(malicious_urls)} malware URLs fetched.")
        return malicious_urls
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return []

# ✅ Function to Process Data and Convert to LangChain Document Format
def process_malware_data(malicious_urls):
    if not malicious_urls:
        print("⚠️ No URLs to process.")
        return []

    print("\n🛠️ [2/4] Processing fetched malware data...")

    documents = []
    for index, entry in enumerate(malicious_urls, start=1):
        doc = Document(
            page_content=f"Malicious URL: {entry['url']}. Threat Type: {entry['threat']}. Detected on: {entry['date_added']}. Status: {entry['status']}.",
            metadata={
                "url": entry["url"],
                "threat_type": entry["threat"],
                "date_added": entry["date_added"],
                "reporter": entry["reporter"],
                "status": entry["status"],
                "malware_type": entry["malware_type"],
                "source": "URLhaus API"
            }
        )
        documents.append(doc)
        print(f"📄 [{index}/{len(malicious_urls)}] Processed: {entry['url']}")

    print(f"✅ Total {len(documents)} threats processed into LangChain format.")
    return documents

# ✅ Function to Save Data to JSON
def save_to_json(documents):
    if not documents:
        print("⚠️ No data to save.")
        return

    formatted_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]

    try:
        with open(JSON_FILE, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Replace old data with only the latest threats
    existing_data = formatted_data

    print("\n💾 [3/4] Saving processed data to JSON...")
    with open(JSON_FILE, "w") as file:
        json.dump(existing_data, file, indent=4)

    print(f"✅ Data saved to {JSON_FILE} (Total records: {len(formatted_data)})")

# ✅ Function to Run the Full Process
def run():
    print(f"\n🔄 Fetching URLhaus Threat Data at {datetime.now()}")
    
    # Step 1: Fetch URLs
    malicious_urls = fetch_recent_malware_urls()

    # Step 2: Process Data
    documents = process_malware_data(malicious_urls)

    # Step 3: Save Data
    save_to_json(documents)

    print("🎉 [4/4] Data update complete!\n")

# ✅ Schedule to Run Every 5 Hours
schedule.every(5).hours.do(run)

# ✅ Initial Run
run()

# ✅ Keep Running in Background
while True:
    schedule.run_pending()
    time.sleep(60)
