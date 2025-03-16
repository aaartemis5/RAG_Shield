import requests
import json
import schedule
import time
from langchain.schema import Document
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("OTX_API_KEY")

# AlienVault OTX API Key
API_KEY = api_key
OTX_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"
JSON_FILE = "otx_threat_intelligence.json"

# Function to Fetch Threat Intelligence Data
def fetch_pulses():
    headers = {"X-OTX-API-KEY": API_KEY}
    response = requests.get(OTX_URL, headers=headers)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Error: {response.status_code}")
        return []

# Function to Convert Data into LangChain Document Format
def process_pulses(pulses):
    documents = []

    for pulse in pulses:
        doc = Document(
            page_content=pulse.get("description", "No description available."),
            metadata={
                "title": pulse.get("name"),
                "author": pulse.get("author_name"),
                "created": pulse.get("created"),
                "tags": pulse.get("tags", []),
                "indicators": [indicator["indicator"] for indicator in pulse.get("indicators", [])]
            }
        )
        documents.append(doc)

    return documents

# Function to Save Data as JSON
def save_to_json(documents):
    formatted_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]

    try:
        with open(JSON_FILE, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Append new data to existing file
    existing_data.extend(formatted_data)

    with open(JSON_FILE, "w") as file:
        json.dump(existing_data, file, indent=4)

    print(f"✅ Data saved to {JSON_FILE} (Updated {len(formatted_data)} records)")

# Function to Run the Full Process
def run():
    print(f"🔄 Fetching data at {datetime.now()}")
    pulses = fetch_pulses()
    if pulses:
        documents = process_pulses(pulses)
        save_to_json(documents)

# Schedule to Run Every 5 Hours
schedule.every(5).hours.do(run)

# Initial Run
run()

# Keep Running in Background
while True:
    schedule.run_pending()
    time.sleep(60)
