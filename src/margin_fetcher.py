import sys

import requests
from bs4 import BeautifulSoup


def _debug(msg: str) -> None:
    # TODO(diagnostic, remove after investigating): print()だけだとクラウド環境の
    # ログにバッファリングされて出てこないことがあるため、flush + stderrの両方に出す。
    print(msg, flush=True)
    print(msg, file=sys.stderr, flush=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://kabutan.jp/",
}


def get_margin_trading_history(ticker: str, weeks: int = 5) -> list[dict]:
    """信用取引残高（買い残・売り残・倍率、週次）を直近weeks件、株探から取得する（日本株のみ）。"""
    _debug(f"[margin_fetcher DEBUG] called with ticker={ticker!r}")
    if not ticker.endswith(".T"):
        return []
    code = ticker[:-2]
    try:
        resp = requests.get(f"https://kabutan.jp/stock/?code={code}", headers=HEADERS, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        header = soup.find("h2", string=lambda s: s and "信用取引" in s)
        if header is None:
            _debug(
                f"[margin_fetcher DEBUG] ({ticker}) status={resp.status_code} "
                f"len={len(resp.text)} title_snippet={soup.title.get_text(strip=True) if soup.title else 'N/A'} "
                f"body_snippet={resp.text[:300]!r}"
            )
            return []
        table = header.find_next("table")

        def _num(cell) -> float | None:
            text = cell.get_text(strip=True).replace(",", "")
            try:
                return float(text)
            except ValueError:
                return None

        history = []
        for row in table.select("tbody tr")[:weeks]:
            cells = row.find_all(["th", "td"])
            if len(cells) < 4:
                continue
            date_el = cells[0].find("time")
            history.append({
                "date": date_el.get("datetime") if date_el else cells[0].get_text(strip=True),
                "sell_balance": _num(cells[1]),
                "buy_balance": _num(cells[2]),
                "ratio": _num(cells[3]),
            })
        return history
    except Exception as e:
        _debug(f"信用取引データ取得エラー ({ticker}): {type(e).__name__}: {e}")
        return []


def get_margin_trading(ticker: str) -> dict | None:
    """信用取引残高（買い残・売り残・倍率、直近週次）を株探から取得する（日本株のみ）。"""
    history = get_margin_trading_history(ticker, weeks=1)
    return history[0] if history else None
