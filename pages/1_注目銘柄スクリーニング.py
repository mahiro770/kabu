import streamlit as st

from src.ai_analyst import list_model_choices
from src.news_fetcher import fetch_nikkei_headlines, fetch_yahoo_business_news
from src.stock_screener import screen_stocks_stream_with_timeout
from src.ui import inject_theme

st.set_page_config(
    page_title="注目銘柄スクリーニング",
    page_icon="📰",
    layout="wide",
)
inject_theme()

st.markdown("# 📰 注目銘柄スクリーニング")
st.caption("経済ニュースの見出しをAIが分析し、翌営業日以降に注目すべき銘柄を抽出します")

with st.sidebar:
    st.markdown("## ⚙️ 設定")
    available_models = list_model_choices()
    model_label = lambda c: f"✨ {c.name} (Gemini)" if c.provider == "gemini" else f"🦙 {c.name}"
    selected_models = st.multiselect(
        "AIモデル（複数選択で比較可能）", available_models,
        default=available_models[:1],
        format_func=model_label,
    )
    timeout_sec = st.slider("応答タイムアウト（秒）", 30, 300, 90, step=10,
                             help="モデルからの応答（チャンク）がこの秒数以上止まった場合、そのモデルを諦めて次に進みます")
    nikkei_n = st.slider("日経の見出し件数", 5, 40, 20)
    yahoo_n = st.slider("Yahoo!ニュースの見出し件数", 3, 8, 8)

run_btn = st.button("📡 ニュースを取得してAIスクリーニングを実行", type="primary")

if run_btn:
    if not selected_models:
        st.warning("AIモデルを1つ以上選択してください。")
    else:
        with st.spinner("ニュースを取得中..."):
            news_items = fetch_nikkei_headlines(nikkei_n) + fetch_yahoo_business_news(yahoo_n)

        if not news_items:
            st.error("ニュースを取得できませんでした。時間をおいて再度お試しください。")
        else:
            with st.expander(f"取得した見出し一覧（{len(news_items)}件）", expanded=False):
                for item in news_items:
                    st.markdown(f"- [{item['title']}]({item['url']})　`{item['source']}`")

            st.divider()
            st.info("AIが見出しを分析し、注目銘柄を抽出します。**投資は自己責任でお願いします。**")

            tabs = st.tabs([model_label(m) for m in selected_models]) if len(selected_models) > 1 else [st.container()]
            for tab, model in zip(tabs, selected_models):
                with tab:
                    placeholder = st.empty()
                    full_text = ""
                    with st.spinner(f"{model_label(model)} が分析中...（最大{timeout_sec}秒応答がなければ打ち切ります）"):
                        for chunk in screen_stocks_stream_with_timeout(news_items, model, timeout_sec):
                            full_text += chunk
                            placeholder.markdown(full_text)
else:
    st.markdown("""
---
### 使い方

| ステップ | 内容 |
|--------|------|
| 1️⃣ | サイドバーでAIモデルと見出しの取得件数を設定 |
| 2️⃣ | 「ニュースを取得してAIスクリーニングを実行」をクリック |
| 3️⃣ | 日経・Yahoo!ニュースの見出しをAIがまとめて分析 |
| 4️⃣ | 翌営業日以降に注目すべき銘柄のランキングを確認 |

### データソース
- 日本経済新聞 マーケット速報（見出しのみ、本文は取得しません）
- Yahoo!ニュース・トピックス（経済）RSS

※本機能はニュース見出しのみに基づく速報的な参考情報です。投資判断は自己責任で行ってください。
""")
