import requests
from bs4 import BeautifulSoup
import re
import time

def get_city_state(zipcode: str):
    """Fetch city and state from zipcode using Zippopotam.us API."""
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zipcode}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            city = data['places'][0]['place name']
            state = data['places'][0]['state abbreviation']
            return f"{city}, {state}"
        return None
    except Exception as e:
        print(f"Error fetching zip code {zipcode}: {e}")
        return None

from googlesearch import search

def find_official_website(city_state: str):
    """Search for the official municipal website using Google Search."""
    query = f"official municipal government website for {city_state}"
    try:
        results = list(search(query, num_results=3))
        print(f"DEBUG GOOGLE RESULTS: {results}")
        if results:
            for url in results:
                if '.gov' in url or '.us' in url or 'city' in url or 'town' in url:
                    return url
            return results[0]
    except Exception as e:
        print(f"Error searching for website for {city_state}: {e}")
    return None

def scrape_municipal_data(url: str):
    """
    Generic scraper that attempts to find emails, phone numbers,
    and links to meeting minutes/board members on the homepage.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"error": f"Failed to retrieve {url} (status {response.status_code})"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Extract Emails
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = list(set(re.findall(email_pattern, soup.get_text())))
        
        # 2. Extract Phone Numbers (very generic pattern)
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = list(set(re.findall(phone_pattern, soup.get_text())))
        
        # 3. Extract relevant links (e.g., Council, Minutes, Board)
        keywords = ['council', 'board', 'mayor', 'minute', 'agenda', 'government', 'departments']
        relevant_links = []
        for a_tag in soup.find_all('a', href=True):
            text = a_tag.get_text().lower()
            href = a_tag['href']
            if any(kw in text for kw in keywords) or any(kw in href.lower() for kw in keywords):
                # Ensure it's a full URL or make it absolute (simplified)
                if href.startswith('/'):
                    href = url.rstrip('/') + href
                relevant_links.append({"text": text.strip(), "url": href})
        
        # Deduplicate links
        unique_links = []
        seen = set()
        for link in relevant_links:
            if link['url'] not in seen and len(link['text']) > 0:
                seen.add(link['url'])
                unique_links.append(link)
                
        return {
            "source_url": url,
            "emails_found": emails,
            "phones_found": phones,
            "relevant_links": unique_links[:20]  # Cap to top 20
        }
    except Exception as e:
        return {"error": str(e)}

def process_zipcode(zipcode: str):
    """Complete pipeline for a single zip code."""
    result = {"zipcode": zipcode, "data": None, "error": None}
    
    # 1. Map to city
    city_state = get_city_state(zipcode)
    if not city_state:
        result["error"] = "Invalid or unknown zip code."
        return result
    
    result["city_state"] = city_state
    
    # 2. Find website
    # Adding a small delay to avoid rate limiting on search
    time.sleep(1)
    url = find_official_website(city_state)
    if not url:
        result["error"] = "Could not find an official website."
        return result
    
    result["website"] = url
    
    # 3. Scrape
    scraped_data = scrape_municipal_data(url)
    result["data"] = scraped_data
    
    return result
