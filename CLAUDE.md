# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Streamlit single-page app (`app.py`) for AI-assisted Japanese/US stock analysis: candlestick charts, technical indicators, financial metrics, and an LLM-generated analyst report, all in Japanese by default with an English toggle.

## Running

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

On Windows, `起動.bat` does the same (checks if port 8501 is already serving, otherwise launches Streamlit and opens the browser once ready). There are no tests, lint config, or CI in this repo.

AI analysis requires a local Ollama server (`ollama serve`) with at least one model pulled; the model dropdown in the sidebar lists whatever `ollama.list()` returns (falls back to a hardcoded name if Ollama isn't reachable).

## Architecture

- `app.py` — the entire UI: sidebar (watchlist + settings), main layout, and all Streamlit rendering/formatting/translation logic. This is intentionally a monolith; there's no routing or multi-page structure.
- `src/data_fetcher.py` — wraps `yfinance` (`get_stock_data` for OHLCV history, `get_stock_info` for fundamentals). Returns `None`/`{}` on failure rather than raising, so callers must check for that.
- `src/technical_analysis.py` — pure pandas/numpy functions, no I/O:
  - `add_indicators(df)` adds MA20/50/200, Bollinger Bands, RSI(14), MACD columns to the OHLCV dataframe.
  - `get_signals(df)` derives per-indicator 買い/売り/中立 (buy/sell/neutral) signals from the last row, then a majority-vote `overall` signal (≥3 buy/sell signals → 買い/売り, else やや買い/やや売り/中立).
  - `get_summary_stats(df, info)` computes 52-week high/low, period returns, volume averages, and annualized volatility.
- `src/chart_builder.py` — builds Plotly figures (candlestick+volume, RSI, MACD, normalized stock-vs-index comparison). Pure functions taking the indicator dataframe, no side effects.
- `src/ai_analyst.py` — builds a long structured Japanese prompt from the dataframe/info/signals/stats and streams a response from a local Ollama model (`analyze_stock_stream`). On failure it yields an inline error message telling the user to check that Ollama is running, rather than raising.

Data flow through `app.py`: `data_fetcher` → `technical_analysis.add_indicators` → `technical_analysis.get_signals`/`get_summary_stats` → rendered via `chart_builder` (tabs 1-2) and `ai_analyst` (tab 4). Financial metrics (tab 3) come directly from `get_stock_info`.

## Conventions specific to this repo

- All user-facing strings are Japanese by default; the `lang` radio ("日本語"/"English") toggles English labels inline via `... if ja else ...` — there's no i18n framework. When adding UI text, follow this same inline-ternary pattern rather than introducing one.
- Ticker convention: Japanese stocks use the `.T` suffix (e.g. `7203.T`); anything without `.T` is treated as a US stock, which determines the comparison index (`^N225` vs `^GSPC`) and default currency.
- Company names/business summaries are translated to Japanese on demand via `deep_translator.GoogleTranslator`, cached with `@st.cache_data` (24h for names, 1h for summaries) and best-effort (falls back to the original text on any exception — never raises).
- `watchlist.json` is local, gitignored user state (list of ticker strings), read/written directly by `app.py` via `load_watchlist`/`save_watchlist`. It is not committed.
- Signal badges use fixed CSS classes (`signal-buy`/`signal-sell`/`signal-neutral`) defined inline in `app.py`'s `st.markdown` block at the top of the file — keep new signal-like UI consistent with these classes.
