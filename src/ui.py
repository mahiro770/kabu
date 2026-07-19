import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');

:root {
    --paper: #121212;
    --paper-soft: #1B1B19;
    --paper-soft-2: #232320;
    --ink: #EDEAE0;
    --ink-soft: #A6A399;
    --up: #4E9A79;
    --down: #C05B3F;
    --gold: #D2AE5C;
    --hairline: rgba(237, 234, 224, 0.14);
    --hairline-strong: rgba(237, 234, 224, 0.28);
    --font-mono: ui-monospace, "SF Mono", "Roboto Mono", Consolas, monospace;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

.stApp {
    background: var(--paper);
}

.block-container { padding-top: 2.2rem; padding-bottom: 3rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0e0e0c;
    border-right: 1px solid var(--hairline);
}

/* Headings — mincho serif for a calmer, more grown-up tone.
   !important is required here: Streamlit emits its own class-scoped heading
   rule (e.g. ".st-emotion-cache-XXXX h1") which outranks a bare "h1" selector
   on specificity regardless of source order. */
h1 {
    font-family: 'Shippori Mincho', serif !important;
    font-weight: 600 !important;
    font-size: 2.3rem !important;
    letter-spacing: 0.01em;
    color: var(--ink) !important;
}
h3, h4 {
    font-family: 'Shippori Mincho', serif !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    margin-top: 0.4rem;
    margin-bottom: 1rem;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--paper-soft);
    border: 1px solid var(--hairline);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-1px);
    border-color: rgba(210, 174, 92, 0.45);
}
[data-testid="stMetricLabel"] { color: var(--ink-soft); }
[data-testid="stMetricValue"] {
    color: var(--ink);
    font-family: var(--font-mono);
    font-variant-numeric: tabular-nums;
}
[data-testid="stMetricDelta"] {
    font-family: var(--font-mono);
    font-variant-numeric: tabular-nums;
}
/* Long values/labels (e.g. "33.51兆円", "-59 (-2.04%)", "コミュニケーション・サービス")
   wrap onto a second line instead of truncating with an ellipsis — never hide
   the actual number or name. The truncation styles are set on the innermost
   <p>, not on stMetricValue/stMetricLabel/stMarkdownContainer themselves, so
   all three levels must be overridden. */
[data-testid="stMetricValue"], [data-testid="stMetricDelta"], [data-testid="stMetricLabel"],
[data-testid="stMetricValue"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricDelta"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricValue"] p, [data-testid="stMetricDelta"] p, [data-testid="stMetricLabel"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: break-word;
    line-height: 1.2;
}

/* Primary buttons.
   !important on background/border: Streamlit re-injects its own themed
   button rule (using the config.toml primaryColor) on every script rerun,
   and that fresh rule can land later in the stylesheet than ours, winning
   the cascade at equal specificity — same root cause as the h1 override above. */
[data-testid="stBaseButton-primary"] {
    background: #3a3221 !important;
    border: 1px solid rgba(210, 174, 92, 0.4) !important;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.02rem;
    box-shadow: none;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 0 0 3px rgba(210, 174, 92, 0.18);
    transform: translateY(-1px);
}

/* Secondary / default buttons */
[data-testid="stBaseButton-secondary"] {
    border-radius: 10px;
    padding: 0.5rem 1.1rem;
    transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}
[data-testid="stBaseButton-secondary"]:hover {
    border-color: rgba(210, 174, 92, 0.5);
    box-shadow: 0 0 0 3px rgba(210, 174, 92, 0.12);
    transform: translateY(-1px);
}

/* Tabs */
[data-testid="stTabs"] button {
    font-weight: 600;
    transition: color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}
[data-testid="stTabs"] button[aria-selected="false"]:hover {
    color: var(--ink-soft) !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid var(--hairline);
    border-radius: 10px;
    transition: border-color 0.15s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(210, 174, 92, 0.35);
}

/* Bordered containers used as cards (e.g. watchlist rows).
   Streamlit adds a "st-key-<key>" class to containers created with an explicit
   key= — used here instead of internal testids, which vary between versions. */
[class*="st-key-wlcard_"] {
    border-radius: 12px !important;
    margin-bottom: 0.9rem;
    background: var(--paper-soft) !important;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
[class*="st-key-wlcard_"]:hover {
    transform: translateY(-1px);
    border-color: rgba(210, 174, 92, 0.4) !important;
}

/* Static section cards — used to group related content (financial metric
   groups, AI report output, usage guides) into visually distinct blocks.
   Unlike wlcard, these aren't clickable, so no hover lift. */
[class*="st-key-seccard_"] {
    border-radius: 14px !important;
    padding: 1.3rem 1.5rem !important;
    margin-bottom: 1.6rem;
    background: var(--paper-soft) !important;
    border-color: var(--hairline) !important;
}

/* Small per-indicator cards (technical signal grid). Same visual language
   as seccard but tighter padding, since these sit 4-up in a column grid. */
[class*="st-key-sigcard_"] {
    border-radius: 12px !important;
    padding: 0.8rem 0.9rem !important;
    margin: 0 0.6rem 0.9rem 0 !important;
    background: var(--paper-soft) !important;
    border-color: var(--hairline) !important;
    transition: border-color 0.15s ease;
}
[class*="st-key-sigcard_"]:hover {
    border-color: rgba(210, 174, 92, 0.35) !important;
}

/* Radio groups styled as pill chips (period / folder selectors).
   Streamlit has changed the internal radio-option markup across versions
   (BaseWeb "label[data-baseweb=radio]" in older releases, the "stRadioOption"
   testid in newer ones) — both selectors are kept so this works either way. */
[data-testid="stRadio"] label[data-baseweb="radio"],
[data-testid="stRadioOption"] {
    background: rgba(210, 174, 92, 0.05);
    border: 1px solid var(--hairline);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-right: 0.3rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
[data-testid="stRadioOption"]:hover {
    background: rgba(210, 174, 92, 0.12);
    border-color: rgba(210, 174, 92, 0.5);
    transform: translateY(-1px);
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadioOption"][data-selected="true"] {
    background: rgba(210, 174, 92, 0.2);
    border-color: rgba(210, 174, 92, 0.55);
}

/* Text inputs / text areas */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: rgba(210, 174, 92, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(210, 174, 92, 0.28);
}

/* Number inputs (e.g. screening filter min/max fields) */
[data-testid="stNumberInputContainer"] {
    border: 1px solid var(--hairline-strong) !important;
    border-radius: 10px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stNumberInputContainer"]:focus-within {
    border-color: rgba(210, 174, 92, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(210, 174, 92, 0.28);
}

hr { border-color: var(--hairline); }

/* Markdown tables (使い方 page, financial history tables, etc.) — replace the
   browser-default grid-of-boxes look with hairline row dividers and a small
   letter-spaced header, matching the rest of the editorial chrome. */
[data-testid="stMarkdownContainer"] table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.4rem 0 0.6rem;
    font-size: 0.96rem;
}
[data-testid="stMarkdownContainer"] table th {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
    color: var(--ink-soft);
    text-align: left;
    padding: 0.5rem 1rem;
    border-bottom: 2px solid var(--hairline-strong);
    white-space: nowrap;
}
[data-testid="stMarkdownContainer"] table td {
    padding: 0.85rem 1rem;
    border-bottom: 1.5px solid var(--hairline);
    color: var(--ink);
    vertical-align: top;
}
[data-testid="stMarkdownContainer"] table tr:last-child td { border-bottom: 2px solid var(--hairline-strong); }
[data-testid="stMarkdownContainer"] table tr:hover td { background: rgba(210, 174, 92, 0.05); }
[data-testid="stMarkdownContainer"] table td:first-child {
    font-weight: 600;
    white-space: nowrap;
}

/* Signal badges. Buy/sell use the semantic up/down hues; neutral uses a
   muted bronze — a desaturated relative of the accent gold rather than a
   fourth unrelated hue, so the badge trio still reads as one family. */
.signal-buy, .signal-sell, .signal-neutral {
    display: inline-block;
    padding: 0.15rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
    font-family: var(--font-mono);
}
.signal-buy { color: var(--up); background: rgba(78, 154, 121, 0.14); }
.signal-sell { color: var(--down); background: rgba(192, 91, 63, 0.14); }
.signal-neutral { color: #B79A5C; background: rgba(183, 154, 92, 0.14); }

.fin-label { font-size: 0.8rem; color: var(--ink-soft); }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(210, 174, 92, 0.35); border-radius: 8px; }
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
