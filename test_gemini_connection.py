"""Gemini API接続テスト用スクリプト。
使い方: .envファイルにGEMINI_API_KEY=あなたのキー を書いてから実行する。
    python test_gemini_connection.py
"""
import os
import sys

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("エラー: 環境変数 GEMINI_API_KEY が設定されていません。")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("Geminiに接続中...")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="こんにちは。これは接続テストです。一言で挨拶を返してください。",
)

print("--- 応答 ---")
print(response.text)
print("--- 接続成功 ---")
