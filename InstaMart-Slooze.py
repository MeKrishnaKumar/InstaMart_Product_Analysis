import os
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

# CONFIGURATION
BASE_URL = "https://dir.indiamart.com/search.mp?ss={}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# The categories you want to scrape
KEYWORDS = ["electronic", "industrial machinery", "laptops", "textiles", "iphone", "memory", "processor"]

data = []

def fetch_and_save(keyword):
    """
    1. Checks if we already downloaded this page.
    2. If not, downloads it LIVE from IndiaMART and saves it.
    3. Returns the filename.
    """
    filename = f"{keyword} - Indiamart.html"
    
    # If file exists, skip download (Caching)
    if os.path.exists(filename):
        print(f"[CACHE] Found local file: {filename}")
        return filename
    
    # If not, crawl it (Live)
    print(f"[LIVE] Downloading {keyword} from IndiaMART...")
    try:
        url = BASE_URL.format(keyword.replace(" ", "+"))
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # Save it so we don't have to download it again
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        # IMPORTANT: Sleep to respect the website (Anti-Blocking)
        time.sleep(random.uniform(3, 6))
        return filename
        
    except Exception as e:
        print(f"Failed to fetch {keyword}: {e}")
        return None

# --- MAIN EXECUTION ---
for keyword in KEYWORDS:
    # STEP 1: Get the file (Either from Cache or Live Web)
    file_name = fetch_and_save(keyword)
    
    if not file_name:
        continue

    # STEP 2: Parse it (Your existing logic)
    print(f"Parsing {file_name}...")
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            
            # Generalized Search (Same as before)
            cards = soup.find_all("div", class_="card")
            
            for card in cards:
                try:
                    price = card.find("p", class_="price").get_text(strip=True)
                except: price = ""
                
                try:
                    name = card.find("a", class_="cardlinks").get_text(strip=True)
                except: name = ""
                
                try:
                    comp = card.select_one("a.cardlinks.elps.elps1").get_text(strip=True)
                except: comp = ""
                
                try:
                    loc = card.find("span", class_="highlight").get_text(strip=True)
                except: loc = ""
                
                try:
                    rating = card.select_one("span.bo.color").get_text(strip=True)
                except: rating = ""

                if name or price:
                    data.append({
                        "Keyword": keyword,
                        "Price": price,
                        "Name": name,
                        "Company": comp,
                        "Location": loc,
                        "Rating": rating
                    })

    except Exception as e:
        print(f"Error parsing {file_name}: {e}")

# Save to Excel
if data:
    df = pd.DataFrame(data)
    df.to_excel("Indiamart_Final_Submission.xlsx", index=False)
    print("Done! Data saved.")