import re
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

_PCT_RE = re.compile(r"([\d.]+)%")


def _num(text: str) -> float | None:
    text = text.strip().replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _fetch_from_kabutan(code: str) -> list[dict] | None:
    resp = requests.get(f"https://kabutan.jp/stock/holder?code={code}", headers=HEADERS, timeout=10)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.select_one("table.stock_holder_1")
    if table is None:
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
            "source": "kabutan",
        })
    return holders or None


def _parse_irbank_shares(text: str) -> int | None:
    """「124万株」「2億4975万株」のような表記を株数に変換する。"""
    text = text.strip().replace("株", "")
    total = 0
    matched = False
    m_oku = re.search(r"([\d,]+)億", text)
    if m_oku:
        total += int(m_oku.group(1).replace(",", "")) * 100_000_000
        text = text[m_oku.end():]
        matched = True
    m_man = re.search(r"([\d,]+)万", text)
    if m_man:
        total += int(m_man.group(1).replace(",", "")) * 10_000
        text = text[m_man.end():]
        matched = True
    remainder = text.replace(",", "").strip()
    if remainder.isdigit():
        total += int(remainder)
        matched = True
    return total if matched else None


def _fetch_from_irbank(code: str) -> list[dict] | None:
    resp = requests.get(f"https://irbank.net/{code}", headers=HEADERS, timeout=10)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")
    heading = soup.find("h2", id="c_share")
    if heading is None:
        title = soup.find("title")
        msg = (
            f"[holder_fetcher DEBUG] IR BANK main ({code}) status={resp.status_code} "
            f"len={len(resp.text)} title={title.get_text(strip=True) if title else None} "
            f"body_snippet={resp.text[:300]!r}"
        )
        print(msg, flush=True)
        print(msg, file=sys.stderr, flush=True)
        return None
    link = heading.find("a", class_="nxq")
    if link is None or not link.get("href"):
        return None
    share_url = f"https://irbank.net{link['href']}"

    resp2 = requests.get(share_url, headers=HEADERS, timeout=10)
    resp2.encoding = resp2.apparent_encoding
    soup2 = BeautifulSoup(resp2.text, "html.parser")
    table = soup2.find("table", class_="cs")
    if table is None:
        title2 = soup2.find("title")
        msg = (
            f"[holder_fetcher DEBUG] IR BANK share ({code}) status={resp2.status_code} "
            f"len={len(resp2.text)} title={title2.get_text(strip=True) if title2 else None} "
            f"body_snippet={resp2.text[:300]!r}"
        )
        print(msg, flush=True)
        print(msg, file=sys.stderr, flush=True)
        return None

    # 大量保有報告は保有比率の変動履歴（イベントログ）なので、
    # 保有者ごとに最新（＝一番上に出てくる）行だけを採用して現在の保有状況とみなす
    seen_ids = set()
    holders = []
    for tr in table.select("tbody tr"):
        name_cell = tr.find("td", class_="lf")
        if name_cell is None:
            continue
        link_el = name_cell.find("a")
        if link_el is None:
            continue
        holder_id = link_el.get("href")
        if holder_id in seen_ids:
            continue
        seen_ids.add(holder_id)

        cells = tr.find_all("td")
        if len(cells) < 4:
            continue
        status_text = cells[2].get_text(strip=True)
        matches = _PCT_RE.findall(status_text)
        if not matches:
            continue
        pct = float(matches[-1]) / 100
        shares = _parse_irbank_shares(cells[3].get_text(strip=True))
        holders.append({
            "name": link_el.get_text(strip=True),
            "pct": pct,
            "shares": shares,
            "value": None,
            "source": "irbank",
        })

    # 保有比率が実質ゼロまで下がった（＝報告義務を外れた）保有者は除外する
    holders = [h for h in holders if h["pct"] and h["pct"] >= 0.01]
    holders.sort(key=lambda h: h["pct"], reverse=True)
    return holders[:10] or None


def get_major_shareholders_jp(ticker: str) -> list[dict] | None:
    """大株主（有価証券報告書等に基づく保有比率上位）を取得する（日本株のみ）。
    株探をまず試し、クラウドのデータセンターIPがボット判定されて取得できない場合は
    IR BANKの大量保有報告（5%ルール開示）にフォールバックする。
    両方失敗した場合は例外を投げずNoneを返す（呼び出し側は関連リンクへの誘導で代替する）。"""
    if not ticker.endswith(".T"):
        return None
    code = ticker[:-2]
    try:
        holders = _fetch_from_kabutan(code)
        if holders:
            return holders
    except Exception as e:
        print(f"大株主データ取得エラー (株探, {ticker}): {e}")

    try:
        return _fetch_from_irbank(code)
    except Exception as e:
        print(f"大株主データ取得エラー (IR BANK, {ticker}): {e}")
        return None
