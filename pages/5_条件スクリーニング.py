import streamlit as st

from src.fundamental_screener import screen_stocks
from src.sectors import SECTOR_JA
from src.translate import translate_names_to_ja_parallel
from src.ui import inject_theme


def _has_japanese(text: str) -> bool:
    return any('぀' <= c <= 'ヿ' or '一' <= c <= '鿿' for c in text)

st.set_page_config(
    page_title="条件スクリーニング",
    page_icon="🔎",
    layout="wide",
)
inject_theme()

st.markdown("# 🔎 条件スクリーニング")
st.caption(
    "時価総額・売上高・PER・ROE・PBR・配当利回り・セクターなどの条件で銘柄を検索します。"
    "Yahoo!ファイナンスの公式データを使うため、中小型株も含めて幅広く検索できます。"
)

if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = ""


def _filter_box(label: str, key_prefix: str, step: float = 1.0, help_zero: str = "上限（0で上限なし）"):
    with st.container(border=True, key=f"sigcard_filter_{key_prefix}"):
        st.markdown(f"**{label}**")
        c_min, c_max = st.columns(2)
        min_val = c_min.number_input("下限", value=0.0, step=step, key=f"{key_prefix}_min")
        max_val = c_max.number_input(help_zero, value=0.0, step=step, key=f"{key_prefix}_max")
    return min_val, max_val


with st.container(border=True, key="seccard_screen_filters"):
    region_label = st.radio("市場", ["日本株", "米国株"], horizontal=True)
    region = "jp" if region_label == "日本株" else "us"
    unit = "億円" if region == "jp" else "億ドル"

    row1 = st.columns(3)
    with row1[0]:
        mcap_min_val, mcap_max_val = _filter_box(f"時価総額（{unit}）", "mcap", step=10.0)
    with row1[1]:
        rev_min_val, rev_max_val = _filter_box(f"売上高（{unit}）", "rev", step=10.0)
    with row1[2]:
        per_min_val, per_max_val = _filter_box("PER（倍）", "per", step=1.0)

    row2 = st.columns(3)
    with row2[0]:
        roe_min_val, roe_max_val = _filter_box("ROE（%）", "roe", step=1.0)
    with row2[1]:
        pbr_min_val, pbr_max_val = _filter_box("PBR（倍）", "pbr", step=0.1)
    with row2[2]:
        div_min_val, div_max_val = _filter_box("配当利回り（%）", "div", step=0.5)

    with st.container(border=True, key="sigcard_filter_sector"):
        st.markdown("**セクター**")
        sector_ja = st.selectbox("指定なしで全業種", ["指定なし"] + list(SECTOR_JA.values()),
                                  label_visibility="collapsed")

    search_btn = st.button("🔎 検索", type="primary", use_container_width=True)

if search_btn:
    with st.spinner("検索中..."):
        screen_result = screen_stocks(
            region=region,
            market_cap_min=mcap_min_val * 1e8 if mcap_min_val > 0 else None,
            market_cap_max=mcap_max_val * 1e8 if mcap_max_val > 0 else None,
            revenue_min=rev_min_val * 1e8 if rev_min_val > 0 else None,
            revenue_max=rev_max_val * 1e8 if rev_max_val > 0 else None,
            per_min=per_min_val if per_min_val > 0 else None,
            per_max=per_max_val if per_max_val > 0 else None,
            roe_min=roe_min_val if roe_min_val != 0 else None,
            roe_max=roe_max_val if roe_max_val != 0 else None,
            pbr_min=pbr_min_val if pbr_min_val > 0 else None,
            pbr_max=pbr_max_val if pbr_max_val > 0 else None,
            div_yield_min=div_min_val if div_min_val > 0 else None,
            div_yield_max=div_max_val if div_max_val > 0 else None,
            sector_ja=None if sector_ja == "指定なし" else sector_ja,
            size=50,
        )

    # 日本株の会社名は英語表記のことが多いため、日本語に翻訳する。
    # 1件ずつ翻訳すると件数分のHTTPリクエストが直列化して遅いため並列化する。
    names = {
        q.get("symbol", ""): q.get("shortName", q.get("symbol", "")).strip()
        for q in screen_result["quotes"]
    }
    if region == "jp":
        to_translate = {sym: n for sym, n in names.items() if not _has_japanese(n)}
        if to_translate:
            with st.spinner("会社名を日本語に翻訳中..."):
                translated = translate_names_to_ja_parallel(list(to_translate.values()))
                names.update(zip(to_translate.keys(), translated))

    st.session_state.screen_result = screen_result
    st.session_state.screen_names = names
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
        names = st.session_state.screen_names
        for q in quotes:
            symbol = q.get("symbol", "")
            name = names.get(symbol, symbol)
            mcap = q.get("marketCap")
            per = q.get("trailingPE")
            pbr = q.get("priceToBook")
            div_yield = q.get("dividendYield")
            price = q.get("regularMarketPrice")
            change_pct = q.get("regularMarketChangePercent")

            with st.container(border=True, key=f"sigcard_result_{symbol}"):
                top = st.columns([4, 2, 1])
                top[0].markdown(f"**{name}**")
                top[0].caption(symbol)
                top[1].metric(
                    "現在値",
                    f"{price:,.0f} {currency}" if price is not None else "N/A",
                    f"{change_pct:+.2f}%" if change_pct is not None else None,
                )
                if top[2].button("分析", key=f"jump_{symbol}", use_container_width=True):
                    st.session_state.current_ticker = symbol
                    st.switch_page("app.py")

                bottom = st.columns(4)
                bottom[0].metric("時価総額", f"{mcap / 1e8:,.0f}{result_unit}" if mcap is not None else "N/A")
                bottom[1].metric("PER", f"{per:.1f}倍" if per is not None else "N/A")
                bottom[2].metric("PBR", f"{pbr:.2f}倍" if pbr is not None else "N/A")
                bottom[3].metric("配当利回り", f"{div_yield:.2f}%" if div_yield is not None else "N/A")
