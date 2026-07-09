import sys

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


def _num(cell) -> float | None:
    text = cell.get_text(strip=True).replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _fetch_from_kabutan(code: str, weeks: int) -> list[dict]:
    resp = requests.get(f"https://kabutan.jp/stock/?code={code}", headers=HEADERS, timeout=10)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    header = soup.find("h2", string=lambda s: s and "信用取引" in s)
    if header is None:
        return []
    table = header.find_next("table")

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
            "source": "kabutan",
        })
    return history


def _num_irbank(cell) -> float | None:
    # セル内は「残高 +増減」の2行形式なので先頭の残高のみ取り出す
    raw = cell.get_text(" ", strip=True).split(" ")[0].replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _fetch_from_irbank(code: str, weeks: int) -> list[dict]:
    resp = requests.get(f"https://irbank.net/{code}/margin", headers=HEADERS, timeout=10)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="tbc")
    if table is None:
        title = soup.find("title")
        msg = (
            f"[margin_fetcher DEBUG] IR BANK ({code}) status={resp.status_code} "
            f"len={len(resp.text)} title={title.get_text(strip=True) if title else None} "
            f"body_snippet={resp.text[:300]!r}"
        )
        print(msg, flush=True)
        print(msg, file=sys.stderr, flush=True)
        return []

    history = []
    current_year = None
    for row in table.select("tbody tr"):
        first_td = row.find("td")
        if first_td is None:
            continue
        if first_td.get("data-k") is None:
            # 年区切り行（例:「2026」）。データ行はdata-k属性を持つ
            text = first_td.get_text(strip=True)
            if text.isdigit() and len(text) == 4:
                current_year = text
            continue
        if current_year is None:
            continue
        cells = row.find_all("td")
        if len(cells) < 6:
            continue
        date_text = first_td.get_text(strip=True)
        buy = _num_irbank(cells[1])
        sell = _num_irbank(cells[3])
        ratio = _num_irbank(cells[5])
        history.append({
            "date": f"{current_year}-{date_text.replace('/', '-')}",
            # 株探は千株単位で表示するため、IR BANKの実株数もそろえる
            "buy_balance": buy / 1000 if buy is not None else None,
            "sell_balance": sell / 1000 if sell is not None else None,
            "ratio": ratio,
            "source": "irbank",
        })
        if len(history) >= weeks:
            break
    return history


def get_margin_trading_history(ticker: str, weeks: int = 5) -> list[dict]:
    """信用取引残高（買い残・売り残・倍率、週次）を直近weeks件取得する（日本株のみ）。
    株探をまず試し、クラウドのデータセンターIPがボット判定されて取得できない場合は
    IR BANKにフォールバックする。両方失敗した場合は例外を投げず空リストを返す
    （呼び出し側は関連リンクへの誘導で代替する）。"""
    if not ticker.endswith(".T"):
        return []
    code = ticker[:-2]
    try:
        history = _fetch_from_kabutan(code, weeks)
        if history:
            return history
    except Exception as e:
        print(f"信用取引データ取得エラー (株探, {ticker}): {e}")

    try:
        return _fetch_from_irbank(code, weeks)
    except Exception as e:
        print(f"信用取引データ取得エラー (IR BANK, {ticker}): {e}")
        return []


def get_margin_trading(ticker: str) -> dict | None:
    """信用取引残高（買い残・売り残・倍率、直近週次）を取得する（日本株のみ）。"""
    history = get_margin_trading_history(ticker, weeks=1)
    return history[0] if history else None
