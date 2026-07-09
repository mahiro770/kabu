import io
import re
import sys

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

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


_JPX_ARCHIVE_URL = "https://www.jpx.co.jp/markets/statistics-equities/margin/05.html"
_JPX_ROW_RE = re.compile(r"\b(\d{4}\d)\s+(JP\w{10})\s+(.+)$")
_JPX_ARROW_RE = re.compile(r"[▲△▼]")
_JPX_SPLIT_NUM_RE = re.compile(r"(\d),\s+(\d{3})\b")
_JPX_DATE_RE = re.compile(r"syumatsu(\d{4})(\d{2})(\d{2})")


def _find_latest_jpx_pdf_url() -> str | None:
    resp = requests.get(_JPX_ARCHIVE_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    hrefs = [
        a["href"] for a in soup.find_all("a", href=True)
        if "syumatsu" in a["href"] and a["href"].lower().endswith(".pdf")
    ]
    if not hrefs:
        return None
    hrefs.sort()  # ファイル名に日付(YYYYMMDD)が含まれるため文字列ソートで最新を特定できる
    latest = hrefs[-1]
    return f"https://www.jpx.co.jp{latest}" if latest.startswith("/") else latest


def _fetch_from_jpx(code: str) -> dict | None:
    """東証公式の「銘柄別信用取引週末残高」PDFから最新週のみを取得する。
    全銘柄が1つの複数ページPDFにまとまっているため、直近1週間分の
    スナップショットのみ返す（過去の推移は提供できない）。"""
    pdf_url = _find_latest_jpx_pdf_url()
    if pdf_url is None:
        return None
    resp = requests.get(pdf_url, headers=HEADERS, timeout=20)
    reader = PdfReader(io.BytesIO(resp.content))

    for page in reader.pages:
        text = page.extract_text()
        if not text or code not in text:
            continue
        for line in text.split("\n"):
            m = _JPX_ROW_RE.search(line)
            if m is None or not m.group(1).startswith(code):
                continue
            rest = _JPX_ARROW_RE.sub("", m.group(3))
            rest = _JPX_SPLIT_NUM_RE.sub(r"\1,\2", rest)
            tokens = rest.split()
            if len(tokens) < 3:
                continue
            try:
                sell = float(tokens[0].replace(",", ""))
                buy = float(tokens[2].replace(",", ""))
            except ValueError:
                continue

            date_m = _JPX_DATE_RE.search(pdf_url)
            date_str = "-".join(date_m.groups()) if date_m else None
            return {
                "date": date_str,
                "sell_balance": sell / 1000,
                "buy_balance": buy / 1000,
                "ratio": buy / sell if sell else None,
                "source": "jpx",
            }
    return None


def get_margin_trading_history(ticker: str, weeks: int = 5) -> list[dict]:
    """信用取引残高（買い残・売り残・倍率、週次）を直近weeks件取得する（日本株のみ）。
    株探→IR BANK→東証公式PDFの順に試し、クラウドのデータセンターIPがボット判定されて
    取得できない場合は次のソースにフォールバックする。東証PDFは最新1週間分のみ提供。
    すべて失敗した場合は例外を投げず空リストを返す（呼び出し側は関連リンクへの誘導で代替する）。"""
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
        history = _fetch_from_irbank(code, weeks)
        if history:
            return history
    except Exception as e:
        print(f"信用取引データ取得エラー (IR BANK, {ticker}): {e}")

    try:
        latest = _fetch_from_jpx(code)
        return [latest] if latest else []
    except Exception as e:
        print(f"信用取引データ取得エラー (JPX, {ticker}): {e}")
        return []


def get_margin_trading(ticker: str) -> dict | None:
    """信用取引残高（買い残・売り残・倍率、直近週次）を取得する（日本株のみ）。"""
    history = get_margin_trading_history(ticker, weeks=1)
    return history[0] if history else None
