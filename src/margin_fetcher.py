import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_margin_trading(ticker: str) -> dict | None:
    """信用取引残高（買い残・売り残・倍率、直近週次）を株探から取得する（日本株のみ）。"""
    if not ticker.endswith(".T"):
        return None
    code = ticker[:-2]
    try:
        resp = requests.get(f"https://kabutan.jp/stock/?code={code}", headers=HEADERS, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        header = soup.find("h2", string=lambda s: s and "信用取引" in s)
        if header is None:
            return None
        table = header.find_next("table")
        row = table.select_one("tbody tr")
        if row is None:
            return None
        cells = row.find_all(["th", "td"])
        if len(cells) < 4:
            return None

        def _num(cell) -> float | None:
            text = cell.get_text(strip=True).replace(",", "")
            try:
                return float(text)
            except ValueError:
                return None

        date_el = cells[0].find("time")
        return {
            "date": date_el.get("datetime") if date_el else cells[0].get_text(strip=True),
            "sell_balance": _num(cells[1]),
            "buy_balance": _num(cells[2]),
            "ratio": _num(cells[3]),
        }
    except Exception as e:
        print(f"信用取引データ取得エラー ({ticker}): {e}")
        return None
