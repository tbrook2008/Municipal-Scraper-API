from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import scraper
import asyncio

app = FastAPI(
    title="Municipal Data Scraper API",
    description="An API that takes zipcodes and returns municipal data (board members, meeting minutes, contact info) scraped from local government websites.",
    version="1.0.0"
)

class ZipcodeRequest(BaseModel):
    zipcodes: List[str]

@app.get("/")
def read_root():
    return {"message": "Municipal Data Scraper API is running. Go to /docs for the Swagger UI."}

@app.post("/scrape")
async def scrape_municipalities(request: ZipcodeRequest):
    if not request.zipcodes:
        raise HTTPException(status_code=400, detail="List of zipcodes cannot be empty.")
    
    if len(request.zipcodes) > 10:
        raise HTTPException(status_code=400, detail="Maximum of 10 zipcodes allowed per request.")
    
    # For a production app, consider using Celery or background tasks for heavy scraping.
    # We will process them synchronously in an async wrapper for this micro-API.
    
    results = []
    # To avoid blocking the event loop completely for long requests, run in executor
    for zip_code in request.zipcodes:
        result = await asyncio.to_thread(scraper.process_zipcode, zip_code)
        results.append(result)
        
    return {"results": results}
