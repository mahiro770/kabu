import streamlit as st

from src.data_fetcher import get_stock_data
from src.chart_builder import build_watchlist_line_chart
from src.watchlist import (
    load_watchlist, save_watchlist,
    save_personal_watchlist, save_community_watchlist,
)
from src.ui import inject_theme

st.set_page_config(
    page_title="ウォッチリスト一覧",
    page_icon="📋",
    layout="wide",
)
inject_theme()

st.markdown("# 📋 ウォッチリスト一覧")
st.caption("登録銘柄の現在値・値動き・メモをまとめて確認できます")

PERIOD_OPTIONS = {
    "1日": ("1d", "5m"),
    "1週": ("5d", "30m"),
    "1カ月": ("1mo", "1d"),
    "6カ月": ("6mo", "1d"),
    "1年": ("1y", "1d"),
    "2年": ("2y", "1d"),
}
period_label = st.radio("期間", list(PERIOD_OPTIONS.keys()), index=2, horizontal=True)
period, interval = PERIOD_OPTIONS[period_label]
is_intraday = period_label in ("1日", "1週")

if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        w if isinstance(w, dict) else {"ticker": w, "name": w}
        for w in load_watchlist()
    ]
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = ""
if "personal_watchlist_owner" not in st.session_state:
    st.session_state.personal_watchlist_owner = None
    st.session_state.personal_watchlist = []
if "community_watchlist_owner" not in st.session_state:
    st.session_state.community_watchlist_owner = None
    st.session_state.community_watchlist = []


@st.cache_data(show_spinner=False, ttl=300)
def _get_watchlist_quote(ticker: str, period: str, interval: str) -> dict | None:
    df = get_stock_data(ticker, period, interval)
    if df is None or df.empty:
        return None
    close = df["close"].dropna()
    if close.empty:
        return None
    current = close.iloc[-1]
    prev = close.iloc[-2] if len(close) > 1 else current
    change = current - prev
    change_pct = (change / prev * 100) if prev else 0.0
    return {"close": close, "current": current, "change": change, "change_pct": change_pct}


def _render_dashboard(wl: list, save_fn, key_prefix: str) -> None:
    if not wl:
        st.caption("銘柄が登録されていません。ホーム画面から追加してください。")
        return

    for i, wt in enumerate(wl):
        ticker = wt["ticker"]
        quote = _get_watchlist_quote(ticker, period, interval)
        col_name, col_price, col_chart = st.columns([2, 2, 4])
        with col_name:
            if st.button(wt["name"], key=f"{key_prefix}_sel_{i}", use_container_width=True):
                st.session_state.current_ticker = ticker
                st.switch_page("app.py")
            st.caption(ticker)
        if quote is None:
            col_price.caption("データ取得失敗")
            col_chart.caption("—")
        else:
            currency = "JPY" if ticker.endswith(".T") else "USD"
            with col_price:
                st.metric(
                    "現在値",
                    f"{quote['current']:,.0f} {currency}",
                    f"{quote['change']:+,.0f} ({quote['change_pct']:+.2f}%)",
                )
            with col_chart:
                color = "#34d399" if quote["change"] >= 0 else "#f87171"
                fig = build_watchlist_line_chart(quote["close"], color, is_intraday)
                st.plotly_chart(
                    fig, width="stretch", config={"displayModeBar": False},
                    key=f"{key_prefix}_spark_{i}",
                )

        col_memo, col_memo_btn = st.columns([5, 1])
        with col_memo:
            memo_val = st.text_area(
                "メモ", value=wt.get("memo", ""), key=f"{key_prefix}_memo_{i}",
                height=68, label_visibility="collapsed", placeholder="メモを入力（例: 決算待ち、押し目待ちなど）",
            )
        with col_memo_btn:
            if save_fn is not None and st.button("保存", key=f"{key_prefix}_memo_save_{i}", use_container_width=True):
                wt["memo"] = memo_val
                save_fn(wl)
                st.toast("メモを保存しました")

        st.divider()


tab_public, tab_community, tab_personal = st.tabs(["🌐 公開", "🏘️ コミュニティ", "👤 個人"])
with tab_public:
    _render_dashboard(st.session_state.watchlist, save_watchlist, "dash_public")
with tab_community:
    community_name = st.session_state.community_watchlist_owner
    if not community_name:
        st.info("ホーム画面のサイドバーでコミュニティ名と合言葉を入力すると、ここに表示されます。")
    else:
        _render_dashboard(
            st.session_state.community_watchlist,
            lambda wl: save_community_watchlist(community_name, wl),
            "dash_community",
        )
with tab_personal:
    username = st.session_state.personal_watchlist_owner
    if not username:
        st.info("ホーム画面のサイドバーで名前と合言葉を入力すると、ここに表示されます。")
    else:
        _render_dashboard(
            st.session_state.personal_watchlist,
            lambda wl: save_personal_watchlist(username, wl),
            "dash_personal",
        )
