import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

.stApp {
    background: #1b1e21;
}

.block-container { padding-top: 2.2rem; padding-bottom: 3rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #17191c;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
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
    color: #eae7e0 !important;
}
h3, h4 {
    font-family: 'Shippori Mincho', serif !important;
    font-weight: 600 !important;
    color: #eae7e0 !important;
    margin-top: 0.4rem;
    margin-bottom: 1rem;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #212529;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-1px);
    border-color: rgba(138, 173, 148, 0.45);
}
[data-testid="stMetricLabel"] { color: #97958d; }
[data-testid="stMetricValue"] { color: #eae7e0; }
/* Long values (e.g. "33.51兆円", "-59 (-2.04%)") wrap onto a second line
   instead of truncating with an ellipsis — never hide the actual number.
   The truncation styles are set on the innermost <p>, not on stMetricValue
   or stMarkdownContainer themselves, so all three levels must be overridden. */
[data-testid="stMetricValue"], [data-testid="stMetricDelta"],
[data-testid="stMetricValue"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricDelta"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricValue"] p, [data-testid="stMetricDelta"] p {
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
    background: #3a4a3d !important;
    border: 1px solid rgba(138, 173, 148, 0.4) !important;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.02rem;
    box-shadow: none;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 0 0 3px rgba(138, 173, 148, 0.18);
    transform: translateY(-1px);
}

/* Secondary / default buttons */
[data-testid="stBaseButton-secondary"] {
    border-radius: 10px;
    padding: 0.5rem 1.1rem;
    transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}
[data-testid="stBaseButton-secondary"]:hover {
    border-color: rgba(138, 173, 148, 0.5);
    box-shadow: 0 0 0 3px rgba(138, 173, 148, 0.12);
    transform: translateY(-1px);
}

/* Tabs */
[data-testid="stTabs"] button {
    font-weight: 600;
    transition: color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #8aad94 !important;
    border-bottom-color: #8aad94 !important;
}
[data-testid="stTabs"] button[aria-selected="false"]:hover {
    color: #b7b4ac !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    transition: border-color 0.15s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(138, 173, 148, 0.35);
}

/* Bordered containers used as cards (e.g. watchlist rows).
   Streamlit adds a "st-key-<key>" class to containers created with an explicit
   key= — used here instead of internal testids, which vary between versions. */
[class*="st-key-wlcard_"] {
    border-radius: 12px !important;
    margin-bottom: 0.9rem;
    background: #212529 !important;
    transition: border-color 0.15s ease, transform 0.15s ease;
}
[class*="st-key-wlcard_"]:hover {
    transform: translateY(-1px);
    border-color: rgba(138, 173, 148, 0.4) !important;
}

/* Static section cards — used to group related content (financial metric
   groups, AI report output, usage guides) into visually distinct blocks.
   Unlike wlcard, these aren't clickable, so no hover lift. */
[class*="st-key-seccard_"] {
    border-radius: 14px !important;
    padding: 1.3rem 1.5rem !important;
    margin-bottom: 1.6rem;
    background: #212529 !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

/* Small per-indicator cards (technical signal grid). Same visual language
   as seccard but tighter padding, since these sit 4-up in a column grid. */
[class*="st-key-sigcard_"] {
    border-radius: 12px !important;
    padding: 0.8rem 0.9rem !important;
    margin: 0 0.6rem 0.9rem 0 !important;
    background: #212529 !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
    transition: border-color 0.15s ease;
}
[class*="st-key-sigcard_"]:hover {
    border-color: rgba(138, 173, 148, 0.35) !important;
}

/* Radio groups styled as pill chips (period / folder selectors).
   Streamlit has changed the internal radio-option markup across versions
   (BaseWeb "label[data-baseweb=radio]" in older releases, the "stRadioOption"
   testid in newer ones) — both selectors are kept so this works either way. */
[data-testid="stRadio"] label[data-baseweb="radio"],
[data-testid="stRadioOption"] {
    background: rgba(138, 173, 148, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-right: 0.3rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
[data-testid="stRadioOption"]:hover {
    background: rgba(138, 173, 148, 0.12);
    border-color: rgba(138, 173, 148, 0.5);
    transform: translateY(-1px);
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadioOption"][data-selected="true"] {
    background: rgba(138, 173, 148, 0.2);
    border-color: rgba(138, 173, 148, 0.55);
}

/* Text inputs / text areas */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: rgba(138, 173, 148, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(138, 173, 148, 0.28);
}

hr { border-color: rgba(255, 255, 255, 0.08); }

/* Signal badges */
.signal-buy, .signal-sell, .signal-neutral {
    display: inline-block;
    padding: 0.15rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
}
.signal-buy { color: #8aad94; background: rgba(138, 173, 148, 0.12); }
.signal-sell { color: #b98a7d; background: rgba(185, 138, 125, 0.12); }
.signal-neutral { color: #c2a873; background: rgba(194, 168, 115, 0.12); }

.fin-label { font-size: 0.8rem; color: #97958d; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(138, 173, 148, 0.35); border-radius: 8px; }
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
