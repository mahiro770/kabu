import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://kabutan.jp/",
}


def get_major_shareholders_jp(ticker: str) -> list[dict] | None:
    """大株主（有価証券報告書ベースの保有比率上位）を株探から取得する（日本株のみ）。"""
    if not ticker.endswith(".T"):
        return None
    code = ticker[:-2]
    try:
        resp = requests.get(f"https://kabutan.jp/stock/holder?code={code}", headers=HEADERS, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.select_one("table.stock_holder_1")
        if table is None:
            # TODO(diagnostic, remove after investigating): 本番環境でこのセクションが
            # 消える原因（IPブロック/CAPTCHA/構造変化）を切り分けるための一時ログ。
            print(
                f"[holder_fetcher DEBUG] ({ticker}) status={resp.status_code} "
                f"len={len(resp.text)} title_snippet={soup.title.get_text(strip=True) if soup.title else 'N/A'} "
                f"body_snippet={resp.text[:300]!r}"
            )
            return None

        def _num(text: str) -> float | None:
            text = text.strip().replace(",", "")
            try:
                return float(text)
            except ValueError:
                return None

        holders = []
        for tr in table.select("tbody tr"):
            name_el = tr.find("th")
            cells = tr.find_all("td")
            if name_el is None or len(cells) < 3:
                continue
            pct = _num(cells[1].get_text())
            shares = _num(cells[2].get_text())
            holders.append({
                "name": name_el.get_text(strip=True),
                "pct": pct / 100 if pct is not None else None,
                "shares": shares,
                "value": None,
            })
        return holders or None
    except Exception as e:
        print(f"大株主データ取得エラー ({ticker}): {type(e).__name__}: {e}")
        return None
