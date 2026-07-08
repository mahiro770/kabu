import hashlib
import os

from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account

load_dotenv()

PUBLIC_COLLECTION = "public_watchlist"
PUBLIC_DOC_ID = "default"
PERSONAL_COLLECTION = "personal_watchlists"
COMMUNITY_COLLECTION = "community_watchlists"

_client = None


def _credentials_from_secrets():
    """Streamlit CloudのSecrets（[firestore_credentials]テーブル）から認証情報を組み立てる。"""
    try:
        import streamlit as st
        return dict(st.secrets["firestore_credentials"])
    except Exception:
        return None


def _get_client():
    global _client
    if _client is None:
        key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if key_path and os.path.exists(key_path):
            _client = firestore.Client.from_service_account_json(key_path)
        elif (creds_info := _credentials_from_secrets()) is not None:
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            _client = firestore.Client(credentials=credentials, project=creds_info["project_id"])
        else:
            _client = firestore.Client()
    return _client


def _hash_passphrase(passphrase: str) -> str:
    return hashlib.sha256(passphrase.encode("utf-8")).hexdigest()


def load_watchlist() -> list:
    """誰でも見られる公開リスト。"""
    doc = _get_client().collection(PUBLIC_COLLECTION).document(PUBLIC_DOC_ID).get()
    return doc.to_dict().get("items", []) if doc.exists else []


def save_watchlist(watchlist: list) -> None:
    _get_client().collection(PUBLIC_COLLECTION).document(PUBLIC_DOC_ID).set({"items": watchlist})


def _get_record(collection: str, key: str) -> dict | None:
    """keyが既に登録済みなら {"passphrase_hash":.., "items":[..]} を返す。未登録・旧形式ならNone。"""
    doc = _get_client().collection(collection).document(key).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return data if isinstance(data, dict) and "items" in data else None


def _verify_passphrase(collection: str, key: str, passphrase: str) -> bool:
    record = _get_record(collection, key)
    if record is None:
        return True
    return record.get("passphrase_hash") == _hash_passphrase(passphrase)


def _claim_name(collection: str, key: str, passphrase: str) -> None:
    """未登録（または旧形式）のkeyを合言葉付きで新規登録する。"""
    if _get_record(collection, key) is None:
        _get_client().collection(collection).document(key).set(
            {"passphrase_hash": _hash_passphrase(passphrase), "items": []}
        )


def _reset_passphrase(collection: str, key: str, new_passphrase: str) -> None:
    """既存のitemsを保持したまま合言葉だけを再設定する。"""
    doc_ref = _get_client().collection(collection).document(key)
    existing = doc_ref.get()
    items = existing.to_dict().get("items", []) if existing.exists else []
    doc_ref.set({"passphrase_hash": _hash_passphrase(new_passphrase), "items": items})


def _load_items(collection: str, key: str) -> list:
    record = _get_record(collection, key)
    return record["items"] if record else []


def _save_items(collection: str, key: str, items: list) -> None:
    doc_ref = _get_client().collection(collection).document(key)
    existing = doc_ref.get()
    passphrase_hash = existing.to_dict().get("passphrase_hash") if existing.exists else None
    doc_ref.set({"passphrase_hash": passphrase_hash, "items": items})


# ─── 個人リスト（名前 + 合言葉ごと） ──────────────────────────────────────────
def get_personal_record(username: str) -> dict | None:
    return _get_record(PERSONAL_COLLECTION, username)


def verify_personal_passphrase(username: str, passphrase: str) -> bool:
    return _verify_passphrase(PERSONAL_COLLECTION, username, passphrase)


def claim_personal_name(username: str, passphrase: str) -> None:
    _claim_name(PERSONAL_COLLECTION, username, passphrase)


def reset_personal_passphrase(username: str, new_passphrase: str) -> None:
    _reset_passphrase(PERSONAL_COLLECTION, username, new_passphrase)


def load_personal_watchlist(username: str) -> list:
    return _load_items(PERSONAL_COLLECTION, username)


def save_personal_watchlist(username: str, watchlist: list) -> None:
    _save_items(PERSONAL_COLLECTION, username, watchlist)


# ─── コミュニティリスト（コミュニティ名 + 合言葉ごと） ────────────────────────
def get_community_record(name: str) -> dict | None:
    return _get_record(COMMUNITY_COLLECTION, name)


def verify_community_passphrase(name: str, passphrase: str) -> bool:
    return _verify_passphrase(COMMUNITY_COLLECTION, name, passphrase)


def claim_community_name(name: str, passphrase: str) -> None:
    _claim_name(COMMUNITY_COLLECTION, name, passphrase)


def reset_community_passphrase(name: str, new_passphrase: str) -> None:
    _reset_passphrase(COMMUNITY_COLLECTION, name, new_passphrase)


def load_community_watchlist(name: str) -> list:
    return _load_items(COMMUNITY_COLLECTION, name)


def save_community_watchlist(name: str, watchlist: list) -> None:
    _save_items(COMMUNITY_COLLECTION, name, watchlist)
