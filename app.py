import streamlit as st

st.set_page_config(
    page_title="株式AI分析",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_fetcher import get_stock_data, get_stock_info, get_financial_history, get_earnings_forecast, get_major_holders
from src.margin_fetcher import get_margin_trading_history
from src.holder_fetcher import get_major_shareholders_jp
from src.stock_search import search_stock
from src.technical_analysis import add_indicators, get_signals, get_summary_stats
from src.chart_builder import (
    build_price_chart, build_rsi_chart, build_macd_chart, build_comparison_chart,
    build_adx_chart, build_obv_chart, build_sparkline,
)
from src.ai_analyst import analyze_stock_stream, list_model_choices
from src.watchlist import (
    load_watchlist, save_watchlist, load_personal_watchlist, save_personal_watchlist,
    get_personal_record, verify_personal_passphrase, claim_personal_name, reset_personal_passphrase,
    load_community_watchlist, save_community_watchlist,
    get_community_record, verify_community_passphrase, claim_community_name, reset_community_passphrase,
)
from src.ui import inject_theme

inject_theme()

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

RECOMMENDATION_JA = {
    "strong_buy": "強い買い",
    "buy": "買い",
    "hold": "中立",
    "underperform": "やや売り",
    "sell": "売り",
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


def get_external_links(ticker: str, info: dict, is_japan: bool) -> list[tuple[str, str]]:
    links = []
    if is_japan:
        code = ticker[:-2]
        links.append(("四季報オンライン", f"https://shikiho.toyokeizai.net/stocks/{code}"))
        links.append(("Kabutan", f"https://kabutan.jp/stock/?code={code}"))
        links.append(("バフェット・コード", f"https://www.buffett-code.com/company/{code}"))
        links.append(("Yahoo!ファイナンス", f"https://finance.yahoo.co.jp/quote/{ticker}"))
    else:
        links.append(("Yahoo Finance", f"https://finance.yahoo.com/quote/{ticker}"))
        links.append(("StockAnalysis.com", f"https://stockanalysis.com/stocks/{ticker}"))
    website = info.get("website")
    if website:
        links.append(("公式サイト" if is_japan else "Official Site", website))
    return links


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
    if val is None or val != val:  # None or NaN
        return "N/A"
    try:
        return f"{val:{fmt}}{suffix}"
    except Exception:
        return "N/A"


def _normalize_ticker(t: str) -> str:
    t = t.strip().upper()
    if t.isdigit():
        return f"{t}.T"
    return t


def _resolve_stock(raw: str, period: str = "5d"):
    """入力値をティッカーとして解決し、価格データを取得する。
    ティッカーとして直接取得できなければ、会社名として検索して再試行する。
    戻り値: (ticker, df, info, resolved_by_name)
    """
    ticker = _normalize_ticker(raw)
    df = get_stock_data(ticker, period)
    if df is not None and not df.empty:
        return ticker, df, get_stock_info(ticker), False

    for candidate in search_stock(raw):
        cand_ticker = candidate["ticker"]
        cand_df = get_stock_data(cand_ticker, period)
        if cand_df is not None and not cand_df.empty:
            return cand_ticker, cand_df, get_stock_info(cand_ticker), True

    return ticker, None, {}, False


def _render_watchlist(wl: list, save_fn, key_prefix: str, show_added_by: bool, username: str) -> None:
    new_ticker = st.text_input("銘柄追加（例: 7203 / トヨタ）", key=f"{key_prefix}_add_input",
                               placeholder="7203 / トヨタ / AAPL")
    if st.button("追加", key=f"{key_prefix}_add_btn", use_container_width=True):
        raw = new_ticker.strip()
        if raw:
            try:
                with st.spinner("検索中..."):
                    t, _df, wl_info, _resolved = _resolve_stock(raw)
                if t is None:
                    st.warning(f"「{raw}」が見つかりませんでした。")
                elif any(w["ticker"] == t for w in wl):
                    st.info(f"「{t}」は既に追加されています。")
                else:
                    wl_name = get_display_name(wl_info, "日本語", t.endswith(".T")) if wl_info else t
                    entry = {"ticker": t, "name": wl_name or t}
                    if show_added_by:
                        entry["added_by"] = username
                    wl.append(entry)
                    save_fn(wl)
                    st.rerun()
            except Exception:
                st.warning(f"「{raw}」が見つかりませんでした。")

    st.divider()

    if wl:
        for i, wt in enumerate(wl):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                if st.button(wt["name"], key=f"{key_prefix}_sel_{i}", use_container_width=True):
                    st.session_state.current_ticker = wt["ticker"]
                    st.rerun()
                if show_added_by:
                    st.caption(f"追加: {wt.get('added_by', '匿名')}")
            with col_b:
                if st.button("✕", key=f"{key_prefix}_del_{i}", help="削除"):
                    wl.pop(i)
                    save_fn(wl)
                    st.rerun()
    else:
        st.caption("銘柄を追加してください")


@st.cache_data(show_spinner=False, ttl=300)
def _get_watchlist_quote(ticker: str) -> dict | None:
    df = get_stock_data(ticker, "1mo")
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


def _render_watchlist_dashboard(wl: list, key_prefix: str, lang: str) -> None:
    ja = lang == "日本語"
    if not wl:
        st.caption("銘柄が登録されていません。" if ja else "No stocks added yet.")
        return

    for i, wt in enumerate(wl):
        ticker = wt["ticker"]
        quote = _get_watchlist_quote(ticker)
        col_name, col_price, col_chart = st.columns([2, 2, 3])
        with col_name:
            if st.button(wt["name"], key=f"{key_prefix}_dash_sel_{i}", use_container_width=True):
                st.session_state.current_ticker = ticker
                st.rerun()
            st.caption(ticker)
        if quote is None:
            col_price.caption("データ取得失敗" if ja else "Failed to fetch data")
            col_chart.caption("—")
        else:
            currency = "JPY" if ticker.endswith(".T") else "USD"
            with col_price:
                st.metric(
                    "現在値" if ja else "Price",
                    f"{quote['current']:,.0f} {currency}",
                    f"{quote['change']:+,.0f} ({quote['change_pct']:+.2f}%)",
                )
            with col_chart:
                color = "#34d399" if quote["change"] >= 0 else "#f87171"
                fig = build_sparkline(quote["close"], color)
                st.plotly_chart(
                    fig, width="stretch", config={"displayModeBar": False},
                    key=f"{key_prefix}_spark_{i}",
                )
        st.divider()


def _render_passphrase_reset(name: str, reset_fn, key_prefix: str) -> None:
    with st.expander("🔑 合言葉を忘れた場合はこちら"):
        st.caption("名前を指定できれば誰でも合言葉を再設定できます（保存済みの銘柄は消えません）。")
        new_pw = st.text_input("新しい合言葉", type="password", key=f"{key_prefix}_reset_pw_input")
        if st.button("再設定する", key=f"{key_prefix}_reset_btn"):
            if new_pw:
                reset_fn(name, new_pw)
                st.success("合言葉を再設定しました。上の欄に新しい合言葉を入力してください。")
            else:
                st.warning("新しい合言葉を入力してください。")


def _render_gated_list(
    owner_key: str, items_key: str, name: str,
    get_record_fn, verify_fn, claim_fn, load_fn, save_fn, reset_fn,
    key_prefix: str, show_added_by: bool, username: str,
    new_name_msg: str, need_passphrase_msg: str, wrong_passphrase_msg: str,
) -> None:
    """名前/コミュニティ名 + 合言葉で保護されたリストを描画する（新規登録・照合・表示を共通化）。"""
    record = get_record_fn(name)
    passphrase = st.text_input(
        "合言葉", type="password", key=f"{key_prefix}_passphrase_input",
        help="他人が同じ名前を使えないようにするための合言葉です。初めて使うなら自由に決めてください。",
    )
    if record is None:
        if not passphrase:
            st.caption(new_name_msg)
            return
        claim_fn(name, passphrase)
        if st.session_state[owner_key] != name:
            st.session_state[items_key] = []
            st.session_state[owner_key] = name
    elif not passphrase:
        st.warning(need_passphrase_msg)
        _render_passphrase_reset(name, reset_fn, key_prefix)
        return
    elif not verify_fn(name, passphrase):
        st.error(wrong_passphrase_msg)
        _render_passphrase_reset(name, reset_fn, key_prefix)
        return
    else:
        if st.session_state[owner_key] != name:
            st.session_state[items_key] = load_fn(name)
            st.session_state[owner_key] = name

    _render_watchlist(
        st.session_state[items_key],
        lambda wl: save_fn(name, wl),
        key_prefix, show_added_by, username,
    )


def _fmt_pct(val) -> str:
    if val is None or val != val:  # None or NaN
        return "N/A"
    return f"{val * 100:.2f}%"


def _fmt_cap(val, currency: str) -> str:
    if val is None or val != val:  # None or NaN
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


def display_financials(
    info: dict, currency: str, lang: str = "日本語", fin_history=None,
    forecast=None, ticker: str = "", is_japan: bool = True, major_holders=None,
    margin_history=None,
) -> None:
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
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("売上成長率" if ja else "Revenue Growth", _fmt_pct(info.get("revenueGrowth")))
    g2.metric("利益成長率" if ja else "Earnings Growth", _fmt_pct(info.get("earningsGrowth")))
    g3.metric("流動比率" if ja else "Current Ratio", _fmt_fin(info.get("currentRatio"), ".2f"))
    g4.metric("D/Eレシオ" if ja else "D/E Ratio", _fmt_fin(info.get("debtToEquity"), ".2f"))

    g5, g6, g7 = st.columns(3)
    div = info.get("dividendYield")
    if div is not None:
        div_str = f"{div:.2f}%" if div > 0.5 else f"{div*100:.2f}%"
    else:
        div_str = "N/A"
    g5.metric("配当利回り" if ja else "Dividend Yield", div_str)
    g6.metric("配当性向" if ja else "Payout Ratio", _fmt_pct(info.get("payoutRatio")))
    latest_equity_ratio = (
        fin_history.iloc[0]["equity_ratio"]
        if fin_history is not None and not fin_history.empty else None
    )
    g7.metric("自己資本比率" if ja else "Equity Ratio", _fmt_pct(latest_equity_ratio))

    if is_japan and margin_history:
        latest = margin_history[0]
        st.markdown("#### 信用取引" if ja else "#### Margin Trading")
        m1, m2, m3 = st.columns(3)
        m1.metric("信用買残" if ja else "Margin Buy Balance", _fmt_fin(latest.get("buy_balance"), ",.1f", "千株" if ja else "K shares"))
        m2.metric("信用売残" if ja else "Margin Sell Balance", _fmt_fin(latest.get("sell_balance"), ",.1f", "千株" if ja else "K shares"))
        m3.metric("信用倍率" if ja else "Margin Ratio", _fmt_fin(latest.get("ratio"), ".2f", mult))
        st.caption(f"{'時点' if ja else 'As of'}: {latest.get('date', 'N/A')}（{'株探' if ja else 'Kabutan'}調べ）")

        if len(margin_history) > 1:
            with st.expander("直近1か月の信用取引推移" if ja else "Margin Trading (past month)"):
                header = "| 日付 | 信用買残(千株) | 信用売残(千株) | 信用倍率 |" if ja \
                    else "| Date | Buy Balance (K) | Sell Balance (K) | Ratio |"
                rows = [header, "|------|------|------|------|"]
                for h in margin_history:
                    rows.append(
                        f"| {h.get('date', 'N/A')} | {_fmt_fin(h.get('buy_balance'), ',.1f')} | "
                        f"{_fmt_fin(h.get('sell_balance'), ',.1f')} | {_fmt_fin(h.get('ratio'), '.2f')} |"
                    )
                st.markdown("\n".join(rows))

    if fin_history is not None and not fin_history.empty:
        st.markdown("#### 過去の業績推移" if ja else "#### Historical Performance")
        header = "| 年度 | 売上高 | 営業利益 | 純利益 | 自己資本比率 |" if ja \
            else "| Fiscal Year | Revenue | Operating Income | Net Income | Equity Ratio |"
        rows = [header, "|------|------|------|------|------|"]
        for _, row in fin_history.iterrows():
            year_label = f"{row['year'].year}年{row['year'].month}月期" if ja else row["year"].strftime("%Y-%m")
            rows.append(
                f"| {year_label} | {_fmt_cap(row['revenue'], currency)} | "
                f"{_fmt_cap(row['operating_income'], currency)} | {_fmt_cap(row['net_income'], currency)} | "
                f"{_fmt_pct(row['equity_ratio'])} |"
            )
        st.markdown("\n".join(rows))

    # 業績予想（アナリストコンセンサス）
    if forecast:
        earnings_est = forecast.get("earnings_estimate")
        revenue_est = forecast.get("revenue_estimate")
        if (earnings_est is not None and not earnings_est.empty) or \
                (revenue_est is not None and not revenue_est.empty):
            st.markdown("#### 業績予想（アナリスト予想）" if ja else "#### Earnings Forecast (Analyst Consensus)")
            header = "| 期 | 予想EPS | 増益率 | 予想売上高 | 増収率 | アナリスト数 |" if ja \
                else "| Period | Est. EPS | EPS Growth | Est. Revenue | Rev. Growth | # Analysts |"
            rows = [header, "|------|------|------|------|------|------|"]
            # yfinanceの revenue_estimate.growth は yearAgoRevenue が異常値になるケースがあるため、
            # 直近の実績売上高（fin_history）を基準に増収率を計算し直す。
            prev_rev_base = (
                fin_history.iloc[0]["revenue"]
                if fin_history is not None and not fin_history.empty else None
            )
            for period, period_label in [("0y", "今期" if ja else "This FY"), ("+1y", "来期" if ja else "Next FY")]:
                eps_row = earnings_est.loc[period] if earnings_est is not None and period in earnings_est.index else None
                rev_row = revenue_est.loc[period] if revenue_est is not None and period in revenue_est.index else None
                eps_avg = eps_row.get("avg") if eps_row is not None else None
                eps_growth = eps_row.get("growth") if eps_row is not None else None
                rev_avg = rev_row.get("avg") if rev_row is not None else None
                if rev_avg is not None and prev_rev_base:
                    rev_growth = (rev_avg - prev_rev_base) / prev_rev_base
                else:
                    rev_growth = rev_row.get("growth") if rev_row is not None else None
                if rev_avg is not None:
                    prev_rev_base = rev_avg
                def _safe_int(v):
                    return int(v) if v is not None and v == v else None
                n_analysts = _safe_int(eps_row.get("numberOfAnalysts")) if eps_row is not None else None
                if n_analysts is None and rev_row is not None:
                    n_analysts = _safe_int(rev_row.get("numberOfAnalysts"))
                rows.append(
                    f"| {period_label} | {_fmt_fin(eps_avg, '.2f')} | {_fmt_pct(eps_growth)} | "
                    f"{_fmt_cap(rev_avg, currency)} | {_fmt_pct(rev_growth)} | "
                    f"{n_analysts if n_analysts is not None else 'N/A'} |"
                )
            st.markdown("\n".join(rows))

        price_targets = forecast.get("price_targets")
        if price_targets:
            t1, t2, t3, t4, t5 = st.columns(5)
            t1.metric("現在株価" if ja else "Current Price", _fmt_fin(price_targets.get("current"), ",.0f"))
            t2.metric("目標株価（平均）" if ja else "Target (Mean)", _fmt_fin(price_targets.get("mean"), ",.0f"))
            t3.metric("目標株価（高値）" if ja else "Target (High)", _fmt_fin(price_targets.get("high"), ",.0f"))
            t4.metric("目標株価（安値）" if ja else "Target (Low)", _fmt_fin(price_targets.get("low"), ",.0f"))
            rec_key = info.get("recommendationKey")
            if not rec_key or rec_key == "none":
                rec_label = "N/A"
            else:
                rec_label = RECOMMENDATION_JA.get(rec_key, rec_key) if ja else rec_key
            t5.metric("アナリスト評価" if ja else "Analyst Rating", rec_label)

    # 会社概要
    summary = info.get("longBusinessSummary") or info.get("description")
    if summary:
        label = "会社概要" if ja else "Business Summary"
        with st.expander(label):
            if ja and not _has_japanese(summary):
                with st.spinner("翻訳中..."):
                    summary = translate_to_ja(summary)
            st.write(summary)

    # 役員一覧
    officers = info.get("companyOfficers")
    if officers:
        label = "役員一覧" if ja else "Company Officers"
        with st.expander(label):
            header = "| 氏名 | 役職 | 年齢 |" if ja else "| Name | Title | Age |"
            rows = [header, "|------|------|------|"]
            for o in officers[:8]:
                rows.append(f"| {o.get('name', 'N/A')} | {o.get('title', 'N/A')} | {o.get('age', 'N/A')} |")
            st.markdown("\n".join(rows))

    # 大株主一覧
    if major_holders:
        label = "大株主一覧" if ja else "Major Shareholders"
        with st.expander(label):
            header = "| 株主名 | 保有比率 | 保有株数 | 保有金額 |" if ja \
                else "| Holder | % Held | Shares | Value |"
            rows = [header, "|------|------|------|------|"]
            for h in major_holders:
                shares = h.get("shares")
                shares_str = f"{int(shares):,}" if shares is not None and shares == shares else "N/A"
                value = h.get("value")
                value_str = _fmt_cap(value, currency) if value is not None else "-"
                rows.append(
                    f"| {h.get('name', 'N/A')} | {_fmt_pct(h.get('pct'))} | "
                    f"{shares_str} | {value_str} |"
                )
            st.markdown("\n".join(rows))
            if is_japan:
                st.caption("※ 有価証券報告書等に基づく大株主情報（株探調べ）")

    # 関連リンク（四季報・株価情報サイトなど）
    links = get_external_links(ticker, info, is_japan) if ticker else []
    if links:
        label = "関連リンク" if ja else "Related Links"
        st.markdown(f"#### {label}")
        st.markdown(" 　".join(f"[{name}]({url})" for name, url in links))
        if is_japan:
            st.caption(
                "※ 四季報の詳細情報は東洋経済新報社の有料コンテンツのため、リンク先でご確認ください。"
                if ja else
                "* Shikiho content is a paid publication by Toyo Keizai — please check the linked page for details."
            )


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

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 ウォッチリスト")

    username = st.text_input("あなたの名前", key="username_input", placeholder="例: まひろ")
    username = username.strip() or "匿名"

    tab_public, tab_community, tab_personal = st.tabs(["🌐 公開", "🏘️ コミュニティ", "👤 個人"])
    with tab_public:
        st.caption("訪問者全員が見られる公開リストです。")
        _render_watchlist(st.session_state.watchlist, save_watchlist, "public", True, username)
    with tab_community:
        community_name = st.text_input(
            "コミュニティ名", key="community_name_input", placeholder="例: 投資仲間グループ",
        )
        community_name = community_name.strip()
        if not community_name:
            st.info("コミュニティ名を入力すると、合言葉を知っている仲間だけで共有できるリストが作れます。")
        else:
            _render_gated_list(
                "community_watchlist_owner", "community_watchlist", community_name,
                get_community_record, verify_community_passphrase, claim_community_name,
                load_community_watchlist, save_community_watchlist, reset_community_passphrase,
                "community", True, username,
                "🆕 新しいコミュニティ名です。合言葉を決めて入力するとメンバーで共有できます。",
                "🔒 合言葉を入力してください。",
                "合言葉が違います。コミュニティ名か合言葉を確認してください。",
            )
    with tab_personal:
        if username == "匿名":
            st.info("⬆️ 上の「あなたの名前」を入力すると、自分専用のリストを追加できるようになります。")
        else:
            _render_gated_list(
                "personal_watchlist_owner", "personal_watchlist", username,
                get_personal_record, verify_personal_passphrase, claim_personal_name,
                load_personal_watchlist, save_personal_watchlist, reset_personal_passphrase,
                "personal", False, username,
                "🆕 初めてのお名前です。合言葉を決めて入力すると個人リストが使えます。",
                "🔒 合言葉を入力してください。",
                "合言葉が違います。別のお名前をお使いください。",
            )

    st.divider()
    st.markdown("## ⚙️ 設定")

    selected_model = st.selectbox(
        "AIモデル",
        list_model_choices(),
        format_func=lambda c: f"✨ {c.name} (Gemini)" if c.provider == "gemini" else f"🦙 {c.name}",
    )

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
        placeholder="日本株: 7203 / トヨタ　米国株: AAPL / Apple",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("分析", type="primary", use_container_width=True)

ticker_raw = ticker_input.strip()
normalized_preview = _normalize_ticker(ticker_raw)

if normalized_preview and (analyze_btn or (st.session_state.current_ticker == normalized_preview and normalized_preview)):
    with st.spinner(f"「{ticker_raw}」を検索中..."):
        ticker, df, info, resolved_by_name = _resolve_stock(ticker_raw, period)
    st.session_state.current_ticker = ticker

    # 日本株か米国株かで比較インデックスを決定
    is_japan = ticker.endswith(".T")
    index_ticker = "^N225" if is_japan else "^GSPC"
    index_name = "日経平均" if is_japan else "S&P 500"

    if df is None or df.empty:
        st.error(f"「{ticker_raw}」のデータを取得できませんでした。銘柄コードまたは会社名を確認してください。")
        st.info("日本株は数字4桁のコード（例: 7203）または会社名（例: トヨタ）で検索できます。")
    else:
        if resolved_by_name:
            st.caption(f"🔍「{ticker_raw}」→ **{ticker}** の検索結果を表示しています")
        with st.spinner(f"{index_name}のデータを取得中..."):
            idx_df = get_stock_data(index_ticker, period)
        df = add_indicators(df)
        signals = get_signals(df)
        stats = get_summary_stats(df, info)

        name = get_display_name(info, lang, is_japan)
        currency = info.get("currency", "JPY" if is_japan else "USD")
        # 直近行の終値が未確定（NaN）なことがあるため、直近の有効な終値を使う
        close_valid = df["close"].dropna()
        current = close_valid.iloc[-1] if not close_valid.empty else float("nan")
        prev = close_valid.iloc[-2] if len(close_valid) > 1 else current
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
                "表示するオーバーレイ",
                ["MA20", "MA50", "MA200", "BB", "一目雲", "VWAP"],
                default=["MA20", "MA50"],
            )
            fig_price = build_price_chart(df, ticker, show_ma)
            st.plotly_chart(fig_price, width="stretch")

            st.markdown("#### テクニカルシグナル")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc5, sc6, sc7, sc8 = st.columns(4)
            for col, label, key in [
                (sc1, "MAクロス", "ma_cross"),
                (sc2, "RSI", "rsi"),
                (sc3, "MACD", "macd"),
                (sc4, "ボリンジャー", "bb"),
                (sc5, "一目均衡表", "ichimoku"),
                (sc6, "ADX", "adx"),
                (sc7, "OBV", "obv"),
                (sc8, "VWAP", "vwap"),
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
            st.plotly_chart(build_adx_chart(df), width="stretch")
            st.plotly_chart(build_obv_chart(df), width="stretch")

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
| 一目 転換線 | {last.get('ichimoku_tenkan', float('nan')):.2f} |
| 一目 基準線 | {last.get('ichimoku_kijun', float('nan')):.2f} |
| 一目 先行スパンA | {last.get('ichimoku_senkou_a', float('nan')):.2f} |
| 一目 先行スパンB | {last.get('ichimoku_senkou_b', float('nan')):.2f} |
| ADX | {last.get('adx', float('nan')):.1f} |
| +DI | {last.get('plus_di', float('nan')):.1f} |
| -DI | {last.get('minus_di', float('nan')):.1f} |
| OBV | {last.get('obv', float('nan')):,.0f} |
| VWAP(20) | {last.get('vwap', float('nan')):.2f} |
""")

        with tab3:
            if info:
                with st.spinner("過去の業績データ・業績予想を取得中..."):
                    fin_history = get_financial_history(ticker)
                    forecast = get_earnings_forecast(ticker)
                    major_holders = get_major_shareholders_jp(ticker) if is_japan else get_major_holders(ticker)
                    margin_history = get_margin_trading_history(ticker, weeks=5) if is_japan else None
                display_financials(info, currency, lang, fin_history, forecast, ticker, is_japan, major_holders, margin_history)
            else:
                st.warning("財務データを取得できませんでした")

        with tab4:
            st.info("AIがテクニカル指標・価格動向・財務データを総合分析します。**投資は自己責任でお願いします。**")
            st.caption(f"使用モデル: {selected_model.name}")

            if st.button("🤖 AI分析を実行", type="primary", key="ai_btn"):
                placeholder = st.empty()
                full_text = ""
                with st.spinner("AIが分析中...（1〜2分かかります）"):
                    for chunk in analyze_stock_stream(df, info, signals, stats, selected_model):
                        full_text += chunk
                        placeholder.markdown(full_text)

else:
    st.markdown("## 📋 ウォッチリスト一覧" if lang == "日本語" else "## 📋 Watchlist")
    tab_dash_public, tab_dash_community, tab_dash_personal = st.tabs(["🌐 公開", "🏘️ コミュニティ", "👤 個人"])
    with tab_dash_public:
        _render_watchlist_dashboard(st.session_state.watchlist, "dash_public", lang)
    with tab_dash_community:
        _render_watchlist_dashboard(st.session_state.community_watchlist, "dash_community", lang)
    with tab_dash_personal:
        _render_watchlist_dashboard(st.session_state.personal_watchlist, "dash_personal", lang)

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
