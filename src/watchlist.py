import hashlib
import json
import os

WATCHLIST_FILE = "watchlist.json"
PERSONAL_WATCHLIST_FILE = "personal_watchlists.json"
COMMUNITY_WATCHLIST_FILE = "community_watchlists.json"


def _hash_passphrase(passphrase: str) -> str:
    return hashlib.sha256(passphrase.encode("utf-8")).hexdigest()


def load_watchlist() -> list:
    """誰でも見られる公開リスト。"""
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_watchlist(watchlist: list) -> None:
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=2)


def _load_all(file_path: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_all(file_path: str, data: dict) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_record(file_path: str, key: str) -> dict | None:
    """keyが既に登録済みなら {"passphrase_hash":.., "items":[..]} を返す。未登録ならNone。"""
    record = _load_all(file_path).get(key)
    if record and "items" in record:
        return record
    return None


def _verify_passphrase(file_path: str, key: str, passphrase: str) -> bool:
    record = _get_record(file_path, key)
    if record is None:
        return True
    return record.get("passphrase_hash") == _hash_passphrase(passphrase)


def _claim_name(file_path: str, key: str, passphrase: str) -> None:
    """未登録のkeyを合言葉付きで新規登録する（既に登録済みなら何もしない）。"""
    data = _load_all(file_path)
    if key not in data:
        data[key] = {"passphrase_hash": _hash_passphrase(passphrase), "items": []}
        _save_all(file_path, data)


def _load_items(file_path: str, key: str) -> list:
    record = _get_record(file_path, key)
    return record["items"] if record else []


def _save_items(file_path: str, key: str, items: list) -> None:
    data = _load_all(file_path)
    record = data.get(key, {"passphrase_hash": None, "items": []})
    record["items"] = items
    data[key] = record
    _save_all(file_path, data)


# ─── 個人リスト（名前 + 合言葉ごと） ──────────────────────────────────────────
def get_personal_record(username: str) -> dict | None:
    return _get_record(PERSONAL_WATCHLIST_FILE, username)


def verify_personal_passphrase(username: str, passphrase: str) -> bool:
    return _verify_passphrase(PERSONAL_WATCHLIST_FILE, username, passphrase)


def claim_personal_name(username: str, passphrase: str) -> None:
    _claim_name(PERSONAL_WATCHLIST_FILE, username, passphrase)


def load_personal_watchlist(username: str) -> list:
    return _load_items(PERSONAL_WATCHLIST_FILE, username)


def save_personal_watchlist(username: str, watchlist: list) -> None:
    _save_items(PERSONAL_WATCHLIST_FILE, username, watchlist)


# ─── コミュニティリスト（コミュニティ名 + 合言葉ごと） ────────────────────────
def get_community_record(name: str) -> dict | None:
    return _get_record(COMMUNITY_WATCHLIST_FILE, name)


def verify_community_passphrase(name: str, passphrase: str) -> bool:
    return _verify_passphrase(COMMUNITY_WATCHLIST_FILE, name, passphrase)


def claim_community_name(name: str, passphrase: str) -> None:
    _claim_name(COMMUNITY_WATCHLIST_FILE, name, passphrase)


def load_community_watchlist(name: str) -> list:
    return _load_items(COMMUNITY_WATCHLIST_FILE, name)


def save_community_watchlist(name: str, watchlist: list) -> None:
    _save_items(COMMUNITY_WATCHLIST_FILE, name, watchlist)
