import re

import requests
import yfinance as yf
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


def _search_yahoo_jp(query: str) -> list[dict]:
    """Yahoo!ファイナンス(日本)の検索結果から日本語の会社名でティッカーを引く。"""
    try:
        resp = requests.get(
            "https://finance.yahoo.co.jp/search/", params={"query": query}, headers=HEADERS, timeout=10
        )
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for article in soup.select('article[class*="SearchItem"]'):
            a = article.find("a", href=True)
            h2 = article.find("h2")
            if not a or not h2:
                continue
            m = re.search(r"/quote/([A-Z0-9]+\.[A-Z]+)", a["href"])
            if not m:
                continue
            results.append({"ticker": m.group(1), "name": h2.get_text(strip=True)})
        return results
    except Exception:
        return []


def _search_yfinance_global(query: str) -> list[dict]:
    """Yahoo Financeのグローバル検索から英語の会社名でティッカーを引く（米国株など）。"""
    try:
        quotes = yf.Search(query, max_results=8).quotes
        return [
            {"ticker": q["symbol"], "name": q.get("longname") or q.get("shortname") or q["symbol"]}
            for q in quotes
            if q.get("quoteType") == "EQUITY"
        ]
    except Exception:
        return []


def search_stock(query: str) -> list[dict]:
    """会社名（日本語・英語）からティッカー候補を検索する。"""
    query = query.strip()
    if not query:
        return []
    results = _search_yahoo_jp(query)
    if results:
        return results
    return _search_yfinance_global(query)
