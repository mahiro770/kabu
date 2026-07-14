import streamlit as st

from src.data_fetcher import get_stock_data
from src.technical_analysis import add_indicators, get_signals, detect_candlestick_patterns
from src.pattern_library import (
    INDICATOR_PATTERNS, CANDLESTICK_PATTERNS,
    generate_indicator_example, generate_candlestick_example,
)
from src.chart_builder import build_pattern_example_chart, build_pattern_candlestick_chart
from src.watchlist import load_watchlist
from src.ui import inject_theme

st.set_page_config(
    page_title="チャート学習",
    page_icon="📚",
    layout="wide",
)
inject_theme()

st.markdown("# 📚 チャート学習")
st.caption("代表的なテクニカル指標・ローソク足パターンの見方と、今そのパターンが出ているウォッチリスト銘柄をまとめて確認できます")

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


def _kind_badge(kind: str) -> str:
    cls = {"buy": "signal-buy", "sell": "signal-sell"}.get(kind, "signal-neutral")
    label = {"buy": "買いサイン", "sell": "売りサイン"}.get(kind, "中立・転換の予兆")
    return f'<span class="{cls}">{label}</span>'


@st.cache_data(show_spinner=False, ttl=300)
def _get_ticker_patterns(ticker: str) -> dict | None:
    df = get_stock_data(ticker, "6mo")
    if df is None or df.empty or len(df) < 60:
        return None
    df = add_indicators(df)
    return {
        "signals": get_signals(df),
        "candle": detect_candlestick_patterns(df),
    }


def _watchlist_tickers() -> list[dict]:
    seen = {}
    for wl in (
        st.session_state.watchlist,
        st.session_state.personal_watchlist,
        st.session_state.community_watchlist,
    ):
        for wt in wl:
            seen.setdefault(wt["ticker"], wt["name"])
    return [{"ticker": t, "name": n} for t, n in seen.items()]


watchlist_items = _watchlist_tickers()

indicator_matches: dict[str, list[dict]] = {key: [] for key in INDICATOR_PATTERNS}
candle_matches: dict[str, list[dict]] = {key: [] for key in CANDLESTICK_PATTERNS}

if watchlist_items:
    with st.spinner("ウォッチリスト銘柄を分析中..."):
        for wt in watchlist_items:
            result = _get_ticker_patterns(wt["ticker"])
            if result is None:
                continue
            for key in INDICATOR_PATTERNS:
                if result["signals"].get(key) == "買い":
                    indicator_matches[key].append(wt)
            for key in CANDLESTICK_PATTERNS:
                if result["candle"].get(key):
                    candle_matches[key].append(wt)


def _render_matches(matches: list[dict], key_prefix: str) -> None:
    if not watchlist_items:
        st.caption("ウォッチリストに銘柄を追加すると、該当銘柄がここに表示されます。")
        return
    if not matches:
        st.caption("現在ウォッチリスト内に該当する銘柄はありません。")
        return
    st.markdown("**現在この形が出ている銘柄:**")
    cols = st.columns(min(len(matches), 4) or 1)
    for i, wt in enumerate(matches):
        with cols[i % len(cols)]:
            if st.button(wt["name"], key=f"{key_prefix}_{wt['ticker']}", use_container_width=True):
                st.session_state.current_ticker = wt["ticker"]
                st.switch_page("app.py")


st.markdown("## 📈 テクニカル指標パターン")
st.caption("価格チャートと合わせて表示される8つの指標が、どんな形になると買いサインとされるかの解説です")

indicator_keys = list(INDICATOR_PATTERNS.keys())
for row_start in range(0, len(indicator_keys), 2):
    cols = st.columns(2)
    for col, key in zip(cols, indicator_keys[row_start:row_start + 2]):
        info = INDICATOR_PATTERNS[key]
        with col.container(border=True, key=f"seccard_ind_{key}"):
            st.markdown(f"#### {info['name']}")
            st.markdown(_kind_badge(info["kind"]), unsafe_allow_html=True)
            fig = build_pattern_example_chart(generate_indicator_example(key))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                             key=f"chart_ind_{key}", theme=None)
            st.markdown(f"**{info['summary']}**")
            st.caption(info["detail"])
            _render_matches(indicator_matches[key], f"ind_{key}")

st.markdown("## 🕯️ ローソク足パターン")
st.caption("1本〜2本のローソク足の形から読み取れる、代表的な売買サインです")

candle_keys = list(CANDLESTICK_PATTERNS.keys())
for row_start in range(0, len(candle_keys), 2):
    cols = st.columns(2)
    for col, key in zip(cols, candle_keys[row_start:row_start + 2]):
        info = CANDLESTICK_PATTERNS[key]
        with col.container(border=True, key=f"seccard_candle_{key}"):
            st.markdown(f"#### {info['name']}")
            st.markdown(_kind_badge(info["kind"]), unsafe_allow_html=True)
            fig = build_pattern_candlestick_chart(generate_candlestick_example(key))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                             key=f"chart_candle_{key}", theme=None)
            st.markdown(f"**{info['summary']}**")
            st.caption(info["detail"])
            _render_matches(candle_matches[key], f"candle_{key}")
