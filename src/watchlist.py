import hashlib
import json
import os

WATCHLIST_FILE = "watchlist.json"
PERSONAL_WATCHLIST_FILE = "personal_watchlists.json"


def _hash_passphrase(passphrase: str) -> str:
    return hashlib.sha256(passphrase.encode("utf-8")).hexdigest()


def load_watchlist() -> list:
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_watchlist(watchlist: list) -> None:
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=2)


def _load_all_personal() -> dict:
    if os.path.exists(PERSONAL_WATCHLIST_FILE):
        with open(PERSONAL_WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_personal_record(username: str) -> dict | None:
    """名前が既に登録済みなら {"passphrase_hash":.., "items":[..]} を返す。未登録ならNone。"""
    record = _load_all_personal().get(username)
    if record and "items" in record:
        return record
    return None


def verify_passphrase(username: str, passphrase: str) -> bool:
    record = get_personal_record(username)
    if record is None:
        return True
    return record.get("passphrase_hash") == _hash_passphrase(passphrase)


def claim_personal_name(username: str, passphrase: str) -> None:
    """未登録の名前を合言葉付きで新規登録する（既に登録済みなら何もしない）。"""
    data = _load_all_personal()
    if username not in data:
        data[username] = {"passphrase_hash": _hash_passphrase(passphrase), "items": []}
        with open(PERSONAL_WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_personal_watchlist(username: str) -> list:
    """名前ごとの個人リストを読み込む（同じ名前でアクセスすると復元される）。"""
    record = get_personal_record(username)
    return record["items"] if record else []


def save_personal_watchlist(username: str, watchlist: list) -> None:
    data = _load_all_personal()
    record = data.get(username, {"passphrase_hash": None, "items": []})
    record["items"] = watchlist
    data[username] = record
    with open(PERSONAL_WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
