import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

NIKKEI_STOCKS_URL = "https://www.nikkei.com/markets/stocks/"
YAHOO_BUSINESS_RSS_URL = "https://news.yahoo.co.jp/rss/topics/business.xml"


def fetch_nikkei_headlines(limit: int = 20) -> list[dict]:
    try:
        resp = requests.get(NIKKEI_STOCKS_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items = {}
        seen_titles = set()
        for a in soup.select('a[href^="/article/"]'):
            title = a.get_text(strip=True)
            href = a.get("href")
            if not title or href in items or title in seen_titles:
                continue
            items[href] = {
                "title": title,
                "url": f"https://www.nikkei.com{href}",
                "source": "日本経済新聞",
            }
            seen_titles.add(title)
            if len(items) >= limit:
                break
        return list(items.values())
    except Exception as e:
        print(f"日経ニュース取得エラー: {e}")
        return []


def fetch_yahoo_business_news(limit: int = 10) -> list[dict]:
    try:
        resp = requests.get(YAHOO_BUSINESS_RSS_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        items = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            if not title:
                continue
            items.append({
                "title": title,
                "url": url,
                "source": "Yahoo!ニュース",
            })
            if len(items) >= limit:
                break
        return items
    except Exception as e:
        print(f"Yahoo!ニュース取得エラー: {e}")
        return []


def fetch_all_news(nikkei_limit: int = 20, yahoo_limit: int = 8) -> list[dict]:
    return fetch_nikkei_headlines(nikkei_limit) + fetch_yahoo_business_news(yahoo_limit)
