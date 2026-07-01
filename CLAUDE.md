# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Streamlit multipage app for AI-assisted Japanese/US stock analysis: candlestick charts with a wide set of technical indicators, financial metrics, an LLM-generated analyst report, and a separate news-driven stock screening page — all in Japanese by default with an English toggle on the main page.

## Running

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

On Windows, `起動.bat` does the same (checks if port 8501 is already serving, otherwise launches Streamlit and opens the browser once ready). There are no tests, lint config, or CI in this repo.

AI features require a local Ollama server (`ollama serve`) with at least one model pulled; model dropdowns list whatever `ollama.list()` returns (falls back to a hardcoded name if Ollama isn't reachable). Both AI call sites (`analyze_stock_stream`, `screen_stocks_stream_with_timeout`) stream token-by-token and degrade to an inline error message rather than raising if Ollama is unreachable or the model doesn't respond.

## Architecture

Streamlit's file-based multipage routing is used: `app.py` is the main/default page, and `pages/1_注目銘柄スクリーニング.py` is a second page auto-added to the sidebar nav. Each page is its own script run (own `st.set_page_config` + theme injection); `st.session_state` is the only thing shared between them.

- `app.py` — main page UI: sidebar (watchlist + settings), ticker analysis layout, and all Streamlit rendering/formatting/translation logic for the single-stock view.
- `pages/1_注目銘柄スクリーニング.py` — fetches news headlines and asks one or more local Ollama models to rank stocks likely to move next session, with a per-model response timeout.
- `src/data_fetcher.py` — wraps `yfinance` (`get_stock_data` for OHLCV history, `get_stock_info` for fundamentals, `get_financial_history` for a multi-year revenue/operating income/net income/equity-ratio table built from `.financials` + `.balance_sheet`). Returns `None`/`{}` on failure rather than raising, so callers must check for that.
- `src/technical_analysis.py` — pure pandas/numpy functions, no I/O:
  - `add_indicators(df)` adds MA20/50/200, Bollinger Bands, RSI(14), MACD, Ichimoku Cloud (`ichimoku_*`), ADX/+DI/-DI, OBV(+EMA20), and a 20-day rolling VWAP to the OHLCV dataframe.
  - `get_signals(df)` derives per-indicator 買い/売り/中立 (buy/sell/neutral) signals from the last row for each key in `DIRECTIONAL_SIGNAL_KEYS`, then an `overall` signal by ratio vote (≥75% buy/sell → 買い/売り, plain majority → やや買い/やや売り, else 中立). When adding a new directional indicator, add its signal key to `DIRECTIONAL_SIGNAL_KEYS` so it's automatically folded into `overall`.
  - `get_summary_stats(df, info)` computes 52-week high/low, period returns, volume averages, and annualized volatility.
- `src/chart_builder.py` — builds Plotly figures (candlestick+volume with optional MA/BB/Ichimoku-cloud/VWAP overlays, RSI, MACD, ADX, OBV, normalized stock-vs-index comparison). Pure functions taking the indicator dataframe, no side effects. The Ichimoku cloud is the one exception to "no date extension beyond `df`": it projects Senkou Span A/B 26 sessions into the future using `pd.bdate_range`, purely for that chart trace — the core dataframe/signals are never extended.
- `src/ai_analyst.py` — builds a long structured Japanese prompt from the dataframe/info/signals/stats and streams a response from a local Ollama model (`analyze_stock_stream`); also exposes `list_ollama_models()`, shared by both pages.
- `src/news_fetcher.py` — scrapes 日経 markets/stocks headlines (requests + BeautifulSoup, matching `a[href^="/article/"]`) and parses the Yahoo!ニュース経済 RSS feed (stdlib `xml.etree`). Both return `[]` on any failure.
- `src/stock_screener.py` — builds the screening prompt from fetched headlines and streams a ranked-stock report; `screen_stocks_stream_with_timeout` wraps the stream in a background thread + `queue.Queue`, yielding a timeout message if no chunk arrives within the configured seconds (so a stuck/slow local model can't hang the UI forever).
- `src/watchlist.py` — `load_watchlist`/`save_watchlist` against `watchlist.json`, used by `app.py`'s sidebar.
- `src/ui.py` — `inject_theme()`, the shared CSS (dark, purple/cyan-accented) injected via `st.markdown` at the top of every page. Theme base colors also live in `.streamlit/config.toml`.

Data flow through `app.py`: `data_fetcher` → `technical_analysis.add_indicators` → `technical_analysis.get_signals`/`get_summary_stats` → rendered via `chart_builder` (tabs 1-2) and `ai_analyst` (tab 4). Financial metrics (tab 3) come directly from `get_stock_info`.

## Conventions specific to this repo

- All user-facing strings are Japanese by default; the `lang` radio ("日本語"/"English") toggles English labels inline via `... if ja else ...` — there's no i18n framework. When adding UI text, follow this same inline-ternary pattern rather than introducing one.
- Ticker convention: Japanese stocks use the `.T` suffix (e.g. `7203.T`); anything without `.T` is treated as a US stock, which determines the comparison index (`^N225` vs `^GSPC`) and default currency.
- Company names/business summaries are translated to Japanese on demand via `deep_translator.GoogleTranslator`, cached with `@st.cache_data` (24h for names, 1h for summaries) and best-effort (falls back to the original text on any exception — never raises).
- `watchlist.json` is local, gitignored user state (list of ticker strings). It is not committed.
- Signal badges use fixed CSS classes (`signal-buy`/`signal-sell`/`signal-neutral`, styled as pill chips in `src/ui.py`) — keep new signal-like UI consistent with these classes.
- News scraping (`src/news_fetcher.py`) targets public headline listings only, never paywalled article bodies — keep it that way if extending to new sources.
