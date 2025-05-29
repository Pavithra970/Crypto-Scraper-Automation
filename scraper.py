import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import pymongo
import pytz
from datetime import datetime

# Set up headless Chrome options for GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")  # GitHub Actions' default path
driver = webdriver.Chrome(service=service, options=options)

# Open CryptoCompare
url = "https://www.cryptocompare.com/coins/list/all/USD/1"
driver.get(url)
time.sleep(5)

# Extract Data
rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
crypto_data = []
ist = pytz.timezone("Asia/Kolkata")
timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

for row in rows:
    try:
        columns = row.find_elements(By.TAG_NAME, "td")
        coin_name = columns[2].text
        price = columns[3].text
        total_vol = columns[5].text
        top_tier_vol = columns[6].text

        crypto_data.append({
            "Coin Name": coin_name,
            "Price": price,
            "Total Vol": total_vol,
            "Top Tier Vol": top_tier_vol,
            "Timestamp (IST)": timestamp
        })
    except Exception as e:
        print(f"Skipping row due to error: {e}")

driver.quit()

# Save CSV
df = pd.DataFrame(crypto_data)

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["CryptoData"]
    collection = db["CryptoPrices"]
    if crypto_data:
        collection.insert_many(crypto_data)
        print("Data successfully inserted into MongoDB Atlas!")

print("Scraping completed! Data saved to crypto_prices.csv and MongoDB Atlas.")
