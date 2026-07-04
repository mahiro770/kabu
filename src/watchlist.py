import json
import os

WATCHLIST_FILE = "watchlist.json"
PERSONAL_WATCHLIST_FILE = "personal_watchlists.json"


def load_watchlist() -> list:
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_watchlist(watchlist: list) -> None:
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=2)


def load_personal_watchlist(username: str) -> list:
    """名前ごとの個人リストを読み込む（同じ名前でアクセスすると復元される）。"""
    if os.path.exists(PERSONAL_WATCHLIST_FILE):
        with open(PERSONAL_WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(username, [])
    return []


def save_personal_watchlist(username: str, watchlist: list) -> None:
    data = {}
    if os.path.exists(PERSONAL_WATCHLIST_FILE):
        with open(PERSONAL_WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[username] = watchlist
    with open(PERSONAL_WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
