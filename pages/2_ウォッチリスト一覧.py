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


OTHER_LABEL = "その他"


def _render_item(wt: dict, wl: list, i: int, save_fn, key_prefix: str) -> None:
    with st.container(border=True, key=f"wlcard_{key_prefix}_{i}"):
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
                color = "#7fb69c" if quote["change"] >= 0 else "#c98f89"
                fig = build_watchlist_line_chart(quote["close"], color, is_intraday)
                st.plotly_chart(
                    fig, width="stretch", config={"displayModeBar": False},
                    key=f"{key_prefix}_spark_{i}", theme=None,
                )

        col_memo, col_group, col_save = st.columns([4, 2, 1])
        with col_memo:
            memo_val = st.text_area(
                "メモ", value=wt.get("memo", ""), key=f"{key_prefix}_memo_{i}",
                height=68, placeholder="メモを入力（例: 決算待ち、押し目待ちなど）",
            )
        with col_group:
            group_val = st.text_input(
                "フォルダ", value=wt.get("group", ""), key=f"{key_prefix}_group_{i}",
                placeholder="例: 自動車産業",
            )
        with col_save:
            st.markdown("<div style='height: 1.9rem'></div>", unsafe_allow_html=True)
            if save_fn is not None and st.button("保存", key=f"{key_prefix}_save_{i}", use_container_width=True):
                wt["memo"] = memo_val
                wt["group"] = group_val.strip()
                save_fn(wl)
                st.toast("保存しました")
                st.rerun()


def _render_dashboard(wl: list, save_fn, key_prefix: str) -> None:
    if not wl:
        st.caption("銘柄が登録されていません。ホーム画面から追加してください。")
        return

    groups: dict[str, list[tuple[int, dict]]] = {}
    for i, wt in enumerate(wl):
        group_name = (wt.get("group") or "").strip() or OTHER_LABEL
        groups.setdefault(group_name, []).append((i, wt))

    group_names = sorted(g for g in groups if g != OTHER_LABEL)
    if OTHER_LABEL in groups:
        group_names.append(OTHER_LABEL)

    folder_key = f"{key_prefix}_folder_select"
    if folder_key in st.session_state and st.session_state[folder_key] not in group_names:
        del st.session_state[folder_key]

    selected_group = st.radio(
        "フォルダを選択", group_names, key=folder_key, horizontal=True,
        format_func=lambda g: f"📁 {g}",
    )

    for i, wt in groups[selected_group]:
        _render_item(wt, wl, i, save_fn, key_prefix)


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
