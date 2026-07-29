import scraper
import json

print("Testing scraper directly on cambridgema.gov...")
result = scraper.scrape_municipal_data("https://www.cambridgema.gov/")
print(json.dumps(result, indent=2))
