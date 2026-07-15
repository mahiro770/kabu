from concurrent.futures import ThreadPoolExecutor

import streamlit as st


@st.cache_data(show_spinner=False, ttl=86400)
def translate_name_to_ja(name: str) -> str:
    """英語の会社名を日本語に翻訳する。ベストエフォートで、失敗時は元の文字列を返す。"""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="en", target="ja").translate(name)
    except Exception:
        return name


def translate_names_to_ja_parallel(names: list[str], max_workers: int = 15) -> list[str]:
    """複数の会社名を並列に翻訳する（スクリーニング結果一覧など、件数が多い場合用）。
    1件ずつ順番に呼ぶと件数分のHTTPリクエストが直列化して非常に遅くなるため、
    スレッドプールでI/O待ちを重ねて短縮する。"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(translate_name_to_ja, names))
