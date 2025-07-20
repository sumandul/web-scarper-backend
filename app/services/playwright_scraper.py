from playwright.sync_api import sync_playwright

def scrape_with_playwright(url: str) -> dict:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            content = page.title()
            browser.close()
            return {"title": content}
    except Exception as e:
        return {"error": str(e)}
