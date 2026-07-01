import streamlit as st

st.set_page_config(
    page_title="株式AI分析",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    div[data-testid="metric-container"] { background: #1e2130; border-radius: 8px; padding: 0.5rem 1rem; }
    .signal-buy { color: #26a69a; font-weight: bold; font-size: 1.1rem; }
    .signal-sell { color: #ef5350; font-weight: bold; font-size: 1.1rem; }
    .signal-neutral { color: #ffa726; font-weight: bold; font-size: 1.1rem; }
    .fin-label { font-size: 0.8rem; color: #aaa; }
</style>
""", unsafe_allow_html=True)

from src.data_fetcher import get_stock_data, get_stock_info
from src.technical_analysis import add_indicators, get_signals, get_summary_stats
from src.chart_builder import build_price_chart, build_rsi_chart, build_macd_chart, build_comparison_chart
from src.ai_analyst import analyze_stock_stream, list_ollama_models
from src.watchlist import load_watchlist, save_watchlist

# セクター日本語マッピング
SECTOR_JA = {
    "Consumer Cyclical": "一般消費財・サービス",
    "Technology": "情報技術",
    "Industrials": "資本財・サービス",
    "Financial Services": "金融サービス",
    "Healthcare": "ヘルスケア",
    "Basic Materials": "素材",
    "Energy": "エネルギー",
    "Communication Services": "コミュニケーション・サービス",
    "Real Estate": "不動産",
    "Consumer Defensive": "生活必需品",
    "Utilities": "公益事業",
}

INDUSTRY_JA = {
    "Auto Manufacturers": "自動車メーカー",
    "Semiconductors": "半導体",
    "Consumer Electronics": "家電",
    "Banks - Regional": "地方銀行",
    "Banks - Diversified": "総合銀行",
    "Internet Retail": "ネット小売",
    "Software - Infrastructure": "インフラソフトウェア",
    "Software - Application": "アプリケーションソフトウェア",
    "Specialty Retail": "専門小売",
    "Electronic Components": "電子部品",
    "Insurance - Diversified": "総合保険",
    "Oil & Gas Integrated": "石油・ガス統合",
    "Drug Manufacturers - General": "医薬品メーカー",
    "Telecom Services": "通信サービス",
}


def _has_japanese(text: str) -> bool:
    return any('぀' <= c <= 'ヿ' or '一' <= c <= '鿿' for c in text)


@st.cache_data(show_spinner=False, ttl=86400)
def _translate_name_to_ja(name: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="en", target="ja").translate(name)
    except Exception:
        return name


def get_display_name(info: dict, lang: str, is_japan: bool = False) -> str:
    long_ = info.get("longName") or info.get("shortName") or ""
    if lang == "日本語":
        short = info.get("shortName", "")
        if _has_japanese(short):
            return short
        if _has_japanese(long_):
            return long_
        # 日本株は社名を翻訳して取得
        if is_japan and long_:
            return _translate_name_to_ja(long_)
    return long_


def get_sector_display(info: dict, lang: str) -> str:
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    if lang == "日本語":
        sector = SECTOR_JA.get(sector, sector)
        industry = INDUSTRY_JA.get(industry, industry)
    return sector, industry


@st.cache_data(show_spinner=False, ttl=3600)
def translate_to_ja(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        # 5000文字の制限があるので分割
        if len(text) <= 4999:
            return GoogleTranslator(source="en", target="ja").translate(text)
        parts = [text[i:i+4999] for i in range(0, len(text), 4999)]
        return "".join(GoogleTranslator(source="en", target="ja").translate(p) for p in parts)
    except Exception:
        return text


def signal_badge(sig: str) -> str:
    cls = {"買い": "signal-buy", "やや買い": "signal-buy",
           "売り": "signal-sell", "やや売り": "signal-sell"}.get(sig, "signal-neutral")
    return f'<span class="{cls}">{sig}</span>'


def _fmt_fin(val, fmt: str = ".1f", suffix: str = "") -> str:
    if val is None:
        return "N/A"
    try:
        return f"{val:{fmt}}{suffix}"
    except Exception:
        return "N/A"


def _fmt_pct(val) -> str:
    if val is None:
        return "N/A"
    return f"{val * 100:.2f}%"


def _fmt_cap(val, currency: str) -> str:
    if val is None:
        return "N/A"
    if currency == "JPY":
        if val >= 1e12:
            return f"{val/1e12:.2f}兆円"
        return f"{val/1e8:.0f}億円"
    else:
        if val >= 1e12:
            return f"${val/1e12:.2f}T"
        if val >= 1e9:
            return f"${val/1e9:.1f}B"
        return f"${val/1e6:.0f}M"


def display_financials(info: dict, currency: str, lang: str = "日本語") -> None:
    ja = lang == "日本語"
    mult = "倍" if ja else "x"

    sector, industry = get_sector_display(info, lang)
    if sector or industry:
        label = "セクター / 業種" if ja else "Sector / Industry"
        st.caption(f"{label}: **{sector}** / {industry}")

    st.markdown("#### バリュエーション" if ja else "#### Valuation")
    v1, v2, v3, v4, v5 = st.columns(5)
    v1.metric("PER（実績）" if ja else "P/E (TTM)", _fmt_fin(info.get("trailingPE"), ".1f", mult))
    v2.metric("PER（予想）" if ja else "P/E (Fwd)", _fmt_fin(info.get("forwardPE"), ".1f", mult))
    v3.metric("PBR" if ja else "P/B", _fmt_fin(info.get("priceToBook"), ".2f", mult))
    v4.metric("EPS", _fmt_fin(info.get("trailingEps"), ".2f"))
    v5.metric("時価総額" if ja else "Market Cap", _fmt_cap(info.get("marketCap"), currency))

    st.markdown("#### 収益性" if ja else "#### Profitability")
    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("ROE", _fmt_pct(info.get("returnOnEquity")))
    p2.metric("ROA", _fmt_pct(info.get("returnOnAssets")))
    p3.metric("純利益率" if ja else "Net Margin", _fmt_pct(info.get("profitMargins")))
    p4.metric("営業利益率" if ja else "Operating Margin", _fmt_pct(info.get("operatingMargins")))
    p5.metric("粗利益率" if ja else "Gross Margin", _fmt_pct(info.get("grossMargins")))

    st.markdown("#### 成長性・財務健全性" if ja else "#### Growth & Financial Health")
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("売上成長率" if ja else "Revenue Growth", _fmt_pct(info.get("revenueGrowth")))
    g2.metric("利益成長率" if ja else "Earnings Growth", _fmt_pct(info.get("earningsGrowth")))
    g3.metric("流動比率" if ja else "Current Ratio", _fmt_fin(info.get("currentRatio"), ".2f"))
    g4.metric("D/Eレシオ" if ja else "D/E Ratio", _fmt_fin(info.get("debtToEquity"), ".2f"))
    div = info.get("dividendYield")
    if div is not None:
        div_str = f"{div:.2f}%" if div > 0.5 else f"{div*100:.2f}%"
    else:
        div_str = "N/A"
    g5.metric("配当利回り" if ja else "Dividend Yield", div_str)

    # 会社概要
    summary = info.get("longBusinessSummary") or info.get("description")
    if summary:
        label = "会社概要" if ja else "Business Summary"
        with st.expander(label):
            if ja and not _has_japanese(summary):
                with st.spinner("翻訳中..."):
                    summary = translate_to_ja(summary)
            st.write(summary)


if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = ""

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 ウォッチリスト")

    new_ticker = st.text_input("銘柄追加（例: 7203.T）", key="add_ticker_input",
                               placeholder="7203.T / AAPL")
    if st.button("追加", use_container_width=True):
        t = new_ticker.strip().upper()
        if t and t not in st.session_state.watchlist:
            st.session_state.watchlist.append(t)
            save_watchlist(st.session_state.watchlist)
            st.rerun()

    st.divider()

    if st.session_state.watchlist:
        for i, wt in enumerate(st.session_state.watchlist):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                if st.button(wt, key=f"wl_{i}", use_container_width=True):
                    st.session_state.current_ticker = wt
                    st.rerun()
            with col_b:
                if st.button("✕", key=f"del_{i}", help="削除"):
                    st.session_state.watchlist.pop(i)
                    save_watchlist(st.session_state.watchlist)
                    st.rerun()
    else:
        st.caption("銘柄を追加してください")

    st.divider()
    st.markdown("## ⚙️ 設定")

    selected_model = st.selectbox("AIモデル", list_ollama_models())

    lang = st.radio("表示言語", ["日本語", "English"], horizontal=True)

    period = st.selectbox(
        "分析期間",
        ["3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        format_func=lambda x: {
            "3mo": "3ヶ月", "6mo": "6ヶ月", "1y": "1年", "2y": "2年", "5y": "5年"
        }[x],
    )

# ─── Main ────────────────────────────────────────────────────────────────────
st.markdown("# 📈 株式AI分析ツール")
st.caption("テクニカル分析 × AI で買い場・売り場をアシスト")

col_input, col_btn = st.columns([5, 1])
with col_input:
    ticker_input = st.text_input(
        "銘柄コード",
        value=st.session_state.current_ticker,
        placeholder="日本株: 7203.T（トヨタ）　米国株: AAPL（Apple）",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("分析", type="primary", use_container_width=True)

ticker = ticker_input.strip().upper()

if ticker and (analyze_btn or (st.session_state.current_ticker == ticker and ticker)):
    st.session_state.current_ticker = ticker

    # 日本株か米国株かで比較インデックスを決定
    is_japan = ticker.endswith(".T")
    index_ticker = "^N225" if is_japan else "^GSPC"
    index_name = "日経平均" if is_japan else "S&P 500"

    with st.spinner(f"{ticker} のデータを取得中..."):
        df = get_stock_data(ticker, period)
        info = get_stock_info(ticker)
        idx_df = get_stock_data(index_ticker, period)

    if df is None or df.empty:
        st.error(f"「{ticker}」のデータを取得できませんでした。銘柄コードを確認してください。")
        st.info("日本株は末尾に `.T` を付けてください（例: トヨタ → `7203.T`）")
    else:
        df = add_indicators(df)
        signals = get_signals(df)
        stats = get_summary_stats(df, info)

        name = get_display_name(info, lang, is_japan)
        currency = info.get("currency", "JPY" if is_japan else "USD")
        current = df["close"].iloc[-1]
        prev = df["close"].iloc[-2] if len(df) > 1 else current
        change = current - prev
        change_pct = change / prev * 100

        st.markdown(f"### {name}　`{ticker}`")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("現在値", f"{current:,.0f} {currency}",
                  f"{change:+,.0f} ({change_pct:+.2f}%)")
        c2.metric("52週高値", f"{stats['week52_high']:,.0f}")
        c3.metric("52週安値", f"{stats['week52_low']:,.0f}")
        c4.metric("RSI(14)", f"{df['rsi'].iloc[-1]:.1f}" if not df["rsi"].isna().all() else "N/A")
        c5.metric("ボラティリティ", f"{stats['volatility']:.1f}%")

        overall = signals.get("overall", "中立")
        badge_html = signal_badge(overall)
        c6.markdown("**総合シグナル**")
        c6.markdown(badge_html, unsafe_allow_html=True)

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["📈 価格チャート", "📊 インジケーター", "💹 財務指標", "🤖 AI分析"])

        with tab1:
            show_ma = st.multiselect(
                "表示する移動平均線",
                ["MA20", "MA50", "MA200", "BB"],
                default=["MA20", "MA50"],
            )
            fig_price = build_price_chart(df, ticker, show_ma)
            st.plotly_chart(fig_price, width="stretch")

            st.markdown("#### テクニカルシグナル")
            sc1, sc2, sc3, sc4 = st.columns(4)
            for col, label, key in [
                (sc1, "MAクロス", "ma_cross"),
                (sc2, "RSI", "rsi"),
                (sc3, "MACD", "macd"),
                (sc4, "ボリンジャー", "bb"),
            ]:
                sig = signals.get(key, "中立")
                col.markdown(f"**{label}**")
                col.markdown(signal_badge(sig), unsafe_allow_html=True)

            # 日経平均／S&P500 比較
            st.markdown(f"#### {index_name}との比較")
            if idx_df is not None and not idx_df.empty:
                fig_cmp = build_comparison_chart(df, idx_df, ticker, index_name)
                st.plotly_chart(fig_cmp, width="stretch")

                # 超過リターン表示
                def period_return(d, days):
                    idx = min(days, len(d) - 1)
                    if idx <= 0:
                        return None
                    return (d["close"].iloc[-1] / d["close"].iloc[-idx] - 1) * 100

                rc1, rc2, rc3, rc4 = st.columns(4)
                for col, label, days in [
                    (rc1, "1ヶ月", 21), (rc2, "3ヶ月", 63),
                    (rc3, "6ヶ月", 126), (rc4, "1年", 252),
                ]:
                    sr = period_return(df, days)
                    ir = period_return(idx_df, days)
                    if sr is not None and ir is not None:
                        alpha = sr - ir
                        col.metric(
                            label,
                            f"{sr:+.1f}%",
                            f"超過 {alpha:+.1f}% vs {index_name}",
                            delta_color="normal",
                        )
            else:
                st.caption(f"{index_name}のデータを取得できませんでした")

        with tab2:
            st.plotly_chart(build_rsi_chart(df), width="stretch")
            st.plotly_chart(build_macd_chart(df), width="stretch")

            with st.expander("最新テクニカル値"):
                last = df.iloc[-1]
                st.markdown(f"""
| 指標 | 値 |
|------|----|
| MA20 | {last.get('ma20', float('nan')):.2f} |
| MA50 | {last.get('ma50', float('nan')):.2f} |
| MA200 | {last.get('ma200', float('nan')):.2f} |
| RSI(14) | {last.get('rsi', float('nan')):.2f} |
| MACD | {last.get('macd', float('nan')):.4f} |
| MACDシグナル | {last.get('macd_signal', float('nan')):.4f} |
| BB上限 | {last.get('bb_upper', float('nan')):.2f} |
| BB下限 | {last.get('bb_lower', float('nan')):.2f} |
""")

        with tab3:
            if info:
                display_financials(info, currency, lang)
            else:
                st.warning("財務データを取得できませんでした")

        with tab4:
            st.info("AIがテクニカル指標・価格動向・財務データを総合分析します。**投資は自己責任でお願いします。**")
            st.caption(f"使用モデル: {selected_model}")

            if st.button("🤖 AI分析を実行", type="primary", key="ai_btn"):
                placeholder = st.empty()
                full_text = ""
                with st.spinner("AIが分析中...（1〜2分かかります）"):
                    for chunk in analyze_stock_stream(df, info, signals, stats, selected_model):
                        full_text += chunk
                        placeholder.markdown(full_text)

else:
    st.markdown("""
---
### 使い方

| ステップ | 内容 |
|--------|------|
| 1️⃣ | 銘柄コードを入力して「分析」をクリック |
| 2️⃣ | ローソク足チャート・日経平均比較を確認 |
| 3️⃣ | RSI・MACDなどのインジケーターを確認 |
| 4️⃣ | 財務指標（PER・ROE・ROAなど）を確認 |
| 5️⃣ | AI分析タブでAIの見解を取得 |

### 銘柄コード例

**日本株（末尾に `.T`）**
- `7203.T` — トヨタ自動車
- `9984.T` — ソフトバンクグループ
- `6758.T` — ソニーグループ
- `8306.T` — 三菱UFJフィナンシャル

**米国株**
- `AAPL` — Apple
- `TSLA` — Tesla
- `NVDA` — NVIDIA
- `MSFT` — Microsoft
""")
