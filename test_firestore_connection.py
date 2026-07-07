"""Firestore接続テスト用スクリプト。
使い方: .envファイルにGOOGLE_APPLICATION_CREDENTIALS=サービスアカウントキーのパス を書いてから実行する。
    python test_firestore_connection.py
"""
import os
import sys

from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()

key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if not key_path or not os.path.exists(key_path):
    print(f"エラー: GOOGLE_APPLICATION_CREDENTIALS が見つかりません（{key_path}）。")
    sys.exit(1)

print("Firestoreに接続中...")
client = firestore.Client.from_service_account_json(key_path)

doc_ref = client.collection("_connection_test").document("ping")
doc_ref.set({"message": "接続テスト", "ok": True})
print("--- 書き込み成功 ---")

doc = doc_ref.get()
print("--- 読み取り結果 ---")
print(doc.to_dict())

doc_ref.delete()
print("--- テストデータ削除完了 ---")
print("--- 接続成功 ---")
