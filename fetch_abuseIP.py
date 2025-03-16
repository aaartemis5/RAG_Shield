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
api_key = os.getenv("ABUSE_API_KEY")

# ✅ AbuseIPDB API Key (Replace with your valid API key)
ABUSEIPDB_API_KEY = api_key

# ✅ API Endpoints
ABUSEIPDB_BLACKLIST_URL = "https://api.abuseipdb.com/api/v2/blacklist"
ABUSEIPDB_CHECK_URL = "https://api.abuseipdb.com/api/v2/check"

# ✅ JSON File to Store Data
JSON_FILE = "abuseipdb_threats.json"

# ✅ Number of malicious IPs to retrieve (max = 10000, but limit to avoid rate limits)
IP_LIMIT = 50

# Function to Fetch the Latest Malicious IPs from AbuseIPDB Blacklist
def fetch_blacklisted_ips():
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    params = {"confidenceMinimum": 90}  # Only get high-confidence malicious IPs

    print("\n🔄 Fetching latest blacklisted IPs...")
    response = requests.get(ABUSEIPDB_BLACKLIST_URL, headers=headers, params=params)

    if response.status_code == 200:
        ip_data = response.json().get("data", [])[:IP_LIMIT]
        malicious_ips = [entry["ipAddress"] for entry in ip_data]
        print(f"✅ Retrieved {len(malicious_ips)} malicious IPs.")
        return malicious_ips
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return []

# Function to Fetch Detailed Reports for Each IP
def fetch_ip_details(ip, index, total):
    headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 30}  # Get last 30 days of reports

    print(f"📄 [{index}/{total}] Checking detailed report for IP: {ip}...")
    response = requests.get(ABUSEIPDB_CHECK_URL, headers=headers, params=params)

    if response.status_code == 200:
        ip_data = response.json().get("data", {})
        reports = ip_data.get("reports", [])

        # Extract relevant details
        abuse_details = {
            "ip": ip,
            "abuse_score": ip_data.get("abuseConfidenceScore", 0),
            "country": ip_data.get("countryCode", "Unknown"),
            "domain": ip_data.get("domain", "Unknown"),
            "isp": ip_data.get("isp", "Unknown"),
            "last_reported": ip_data.get("lastReportedAt", "Never"),
            "categories": ip_data.get("usageType", "Unknown"),
            "total_reports": ip_data.get("totalReports", 0),
            "recent_reports": [{"date": r["reportedAt"], "category": r["categories"]} for r in reports]
        }

        print(f"✅ [{index}/{total}] Retrieved detailed data for {ip}.")
        return abuse_details
    else:
        print(f"⚠️ [{index}/{total}] Error fetching details for {ip}: {response.status_code}")
        return None

# Function to Process Data and Convert to LangChain Document Format
def process_ip_data(malicious_ips):
    documents = []

    for index, ip in enumerate(malicious_ips, start=1):
        ip_details = fetch_ip_details(ip, index, len(malicious_ips))
        if ip_details:
            doc = Document(
                page_content=f"IP {ip_details['ip']} has been reported {ip_details['total_reports']} times. Abuse Score: {ip_details['abuse_score']}. ISP: {ip_details['isp']}. Country: {ip_details['country']}.",
                metadata=ip_details
            )
            documents.append(doc)

    return documents

# Function to Save Data to JSON
def save_to_json(documents):
    formatted_data = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]

    try:
        with open(JSON_FILE, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Replace old data with only the latest malicious IPs
    existing_data = formatted_data

    with open(JSON_FILE, "w") as file:
        json.dump(existing_data, file, indent=4)

    print(f"✅ Data saved to {JSON_FILE} (Total records: {len(formatted_data)})")

# Function to Run the Full Process
def run():
    print(f"\n🔄 Fetching AbuseIPDB Data at {datetime.now()}")
    malicious_ips = fetch_blacklisted_ips()

    if malicious_ips:
        print(f"🛠️ Processing {len(malicious_ips)} IPs...")
        documents = process_ip_data(malicious_ips)
        save_to_json(documents)
        print("🎉 Data update complete!\n")
    else:
        print("⚠️ No new malicious IPs found.\n")

# Schedule to Run Every 5 Hours
schedule.every(5).hours.do(run)

# Initial Run
run()

# Keep Running in Background
while True:
    schedule.run_pending()
    time.sleep(60)
