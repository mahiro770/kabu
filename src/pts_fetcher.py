import sys

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://finance.yahoo.co.jp/",
}


def _num(text: str) -> float | None:
    text = text.strip().replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def get_pts_price(ticker: str) -> dict | None:
    """夜間PTS株価（ジャパンネクスト証券J-Market、17時〜翌6時）をYahoo!ファイナンスから取得する
    （日本株のみ）。ボット判定等で取得できない、またはその日の夜間PTS取引がない場合は
    例外を投げずNoneを返す。"""
    if not ticker.endswith(".T"):
        return None
    code = ticker[:-2]
    try:
        resp = requests.get(f"https://finance.yahoo.co.jp/quote/{code}.T", headers=HEADERS, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        row = soup.select_one('[class*="ptsPriceRow"]')
        if row is None:
            title = soup.find("title")
            msg = (
                f"[pts_fetcher DEBUG] ({ticker}) status={resp.status_code} "
                f"len={len(resp.text)} title={title.get_text(strip=True) if title else None} "
                f"body_snippet={resp.text[:300]!r}"
            )
            print(msg, flush=True)
            print(msg, file=sys.stderr, flush=True)
            return None
        price_el = row.select_one('[class*="ptsPrice"] [class*="StyledNumber__value"]')
        if price_el is None:
            return None
        price = _num(price_el.get_text())
        if price is None:
            return None

        change_el = row.select_one('[class*="PriceChangeLabel__primary"] [class*="StyledNumber__value"]')
        pct_el = row.select_one('[class*="PriceChangeLabel__secondary"] [class*="StyledNumber__value"]')
        return {
            "price": price,
            "change": _num(change_el.get_text()) if change_el else None,
            "change_pct": _num(pct_el.get_text()) if pct_el else None,
        }
    except Exception as e:
        print(f"夜間PTSデータ取得エラー ({ticker}): {e}")
        return None
