import requests
from bs4 import BeautifulSoup
def scrape_with_bs(url: str) -> dict:
    print("🔥 hit bs")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = str(soup.title.string) if soup.title and soup.title.string else "No title found"
        raw_text = soup.get_text(separator=' ', strip=True)

        return {
            "title": title,
            "text": raw_text
        }
    except Exception as e:
        print("❌ Error in scrape_with_bs:", str(e))
        return {"error": str(e)}