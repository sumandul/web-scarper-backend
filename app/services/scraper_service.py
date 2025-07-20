from app.services.bs_scraper import scrape_with_bs
from app.services.playwright_scraper import scrape_with_playwright
from app.services.enrichment_service import enrich_content
import uuid

def perform_scraping(url: str, scraper_type: str) -> dict:
    # Step 1: Scrape the page
    # print(scraper_type,'suman')
    if scraper_type == "playwright":
        result = scrape_with_playwright(url)
    else:
        print('hello suman scraper')
        result = scrape_with_bs(url)
        print(result,'sayssss')
    raw_text = result.get("title", "")
    print(raw_text,'text')

    # Step 2: AI enrichment
    enriched = enrich_content(raw_text)
    print(enriched,'ppppppp')

    # Step 3: Combine and return everything
    return {
        "job_id": str(uuid.uuid4()),
        "status": "completed",
        "data": {
            "url": url,
            "headline": enriched["summaries"]["Headline"],
            "tldr": enriched["summaries"]["TL;DR"],
            "summary": enriched["summaries"]["Full Summary"],
            "topics": enriched["topics"],
            "entities": enriched["entities"],
            "seo_tags": enriched["seo_tags"],
            "sentiment": enriched["sentiment"],
            "raw": raw_text
        }
    }
