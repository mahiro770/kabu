import streamlit as st

from src.fundamental_screener import screen_stocks
from src.sectors import SECTOR_JA
from src.ui import inject_theme

st.set_page_config(
    page_title="条件スクリーニング",
    page_icon="🔎",
    layout="wide",
)
inject_theme()

st.markdown("# 🔎 条件スクリーニング")
st.caption(
    "時価総額・売上高・PER・ROE・セクターなどの条件で銘柄を検索します。"
    "Yahoo!ファイナンスの公式データを使うため、中小型株も含めて幅広く検索できます。"
)

if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = ""

with st.container(border=True, key="seccard_screen_filters"):
    region_label = st.radio("市場", ["日本株", "米国株"], horizontal=True)
    region = "jp" if region_label == "日本株" else "us"
    unit = "億円" if region == "jp" else "億ドル"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**時価総額（{unit}）**")
        mcap_min, mcap_max = st.columns(2)
        mcap_min_val = mcap_min.number_input("下限", min_value=0.0, value=0.0, step=10.0, key="mcap_min")
        mcap_max_val = mcap_max.number_input("上限（0で上限なし）", min_value=0.0, value=0.0, step=10.0, key="mcap_max")
    with c2:
        st.markdown(f"**売上高（{unit}）**")
        rev_min, rev_max = st.columns(2)
        rev_min_val = rev_min.number_input("下限", min_value=0.0, value=0.0, step=10.0, key="rev_min")
        rev_max_val = rev_max.number_input("上限（0で上限なし）", min_value=0.0, value=0.0, step=10.0, key="rev_max")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**PER（倍）**")
        per_min, per_max = st.columns(2)
        per_min_val = per_min.number_input("下限", min_value=0.0, value=0.0, step=1.0, key="per_min")
        per_max_val = per_max.number_input("上限（0で上限なし）", min_value=0.0, value=0.0, step=1.0, key="per_max")
    with c4:
        st.markdown("**ROE（%）**")
        roe_min, roe_max = st.columns(2)
        roe_min_val = roe_min.number_input("下限", value=0.0, step=1.0, key="roe_min")
        roe_max_val = roe_max.number_input("上限（0で上限なし）", value=0.0, step=1.0, key="roe_max")

    sector_ja = st.selectbox("セクター（指定なしで全業種）", ["指定なし"] + list(SECTOR_JA.values()))

    search_btn = st.button("🔎 検索", type="primary", use_container_width=True)

if search_btn:
    with st.spinner("検索中..."):
        st.session_state.screen_result = screen_stocks(
            region=region,
            market_cap_min=mcap_min_val * 1e8 if mcap_min_val > 0 else None,
            market_cap_max=mcap_max_val * 1e8 if mcap_max_val > 0 else None,
            revenue_min=rev_min_val * 1e8 if rev_min_val > 0 else None,
            revenue_max=rev_max_val * 1e8 if rev_max_val > 0 else None,
            per_min=per_min_val if per_min_val > 0 else None,
            per_max=per_max_val if per_max_val > 0 else None,
            roe_min=roe_min_val if roe_min_val != 0 else None,
            roe_max=roe_max_val if roe_max_val != 0 else None,
            sector_ja=None if sector_ja == "指定なし" else sector_ja,
            size=50,
        )
        st.session_state.screen_currency = "JPY" if region == "jp" else "USD"
        st.session_state.screen_unit = unit

# 検索結果はsession_stateで保持し、結果内の「分析」ボタン押下によるrerunでも
# 消えないようにする（st.button()のTrueは押した直後の1回のrerunでしか続かない）
result = st.session_state.get("screen_result")
if result is not None:
    quotes = result["quotes"]
    if not quotes:
        st.info("条件に合う銘柄が見つかりませんでした。条件を緩めてお試しください。")
    else:
        st.markdown(f"### 該当 {result['total']:,} 銘柄中、上位{len(quotes)}件（時価総額順）")
        currency = st.session_state.screen_currency
        result_unit = st.session_state.screen_unit
        for q in quotes:
            symbol = q.get("symbol", "")
            name = q.get("shortName", symbol)
            mcap = q.get("marketCap")
            per = q.get("trailingPE")
            price = q.get("regularMarketPrice")
            change_pct = q.get("regularMarketChangePercent")

            with st.container(border=True, key=f"sigcard_result_{symbol}"):
                cols = st.columns([3, 2, 2, 2, 1])
                cols[0].markdown(f"**{name}**")
                cols[0].caption(symbol)
                cols[1].metric(
                    "現在値",
                    f"{price:,.0f} {currency}" if price is not None else "N/A",
                    f"{change_pct:+.2f}%" if change_pct is not None else None,
                )
                cols[2].metric("時価総額", f"{mcap / 1e8:,.0f}{result_unit}" if mcap is not None else "N/A")
                cols[3].metric("PER", f"{per:.1f}倍" if per is not None else "N/A")
                if cols[4].button("分析", key=f"jump_{symbol}", use_container_width=True):
                    st.session_state.current_ticker = symbol
                    st.switch_page("app.py")
