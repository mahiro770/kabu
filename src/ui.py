import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 15% -10%, #1a2130 0%, #0a0d15 45%) fixed;
}

.block-container { padding-top: 1.5rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0e131c;
    border-right: 1px solid rgba(148, 163, 184, 0.12);
}

/* Headings */
h1 {
    font-weight: 700;
    background: linear-gradient(90deg, #8fb4b0, #c7d1d9);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    width: fit-content;
}
h3, h4 { color: #d8dde3; }

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, #161c26, #0f131b);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    border-color: rgba(111, 165, 168, 0.4);
}
[data-testid="stMetricLabel"] { color: #9ca3af; }
[data-testid="stMetricValue"] { color: #e5e9ed; }

/* Primary buttons */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #3d6b70, #2c4d52);
    border: none;
    box-shadow: 0 0 0 rgba(111, 165, 168, 0);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 0 14px rgba(111, 165, 168, 0.4);
    transform: translateY(-1px);
}

/* Secondary / default buttons */
[data-testid="stBaseButton-secondary"] {
    transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}
[data-testid="stBaseButton-secondary"]:hover {
    border-color: rgba(111, 165, 168, 0.55);
    box-shadow: 0 0 10px rgba(111, 165, 168, 0.2);
    transform: translateY(-1px);
}

/* Tabs */
[data-testid="stTabs"] button {
    transition: color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #8fb4b0 !important;
    border-bottom-color: #8fb4b0 !important;
}
[data-testid="stTabs"] button[aria-selected="false"]:hover {
    color: #a9b6bd !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    transition: border-color 0.15s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(111, 165, 168, 0.3);
}

/* Bordered containers used as cards (e.g. watchlist rows).
   Streamlit adds a "st-key-<key>" class to containers created with an explicit
   key= — used here instead of internal testids, which vary between versions. */
[class*="st-key-wlcard_"] {
    border-radius: 14px !important;
    margin-bottom: 0.9rem;
    background: linear-gradient(160deg, rgba(22, 28, 38, 0.6), rgba(15, 19, 27, 0.6)) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
[class*="st-key-wlcard_"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
    border-color: rgba(111, 165, 168, 0.4) !important;
}

/* Radio groups styled as pill chips (period / folder selectors).
   Streamlit has changed the internal radio-option markup across versions
   (BaseWeb "label[data-baseweb=radio]" in older releases, the "stRadioOption"
   testid in newer ones) — both selectors are kept so this works either way. */
[data-testid="stRadio"] label[data-baseweb="radio"],
[data-testid="stRadioOption"] {
    background: rgba(111, 165, 168, 0.06);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-right: 0.3rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
[data-testid="stRadioOption"]:hover {
    background: rgba(111, 165, 168, 0.14);
    border-color: rgba(111, 165, 168, 0.5);
    transform: translateY(-1px);
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadioOption"][data-selected="true"] {
    background: linear-gradient(90deg, rgba(111, 165, 168, 0.22), rgba(148, 163, 184, 0.14));
    border-color: rgba(111, 165, 168, 0.55);
}

/* Text inputs / text areas */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: rgba(111, 165, 168, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(111, 165, 168, 0.28);
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
.signal-buy { color: #7fb69c; background: rgba(127, 182, 156, 0.12); }
.signal-sell { color: #c98f89; background: rgba(201, 143, 137, 0.12); }
.signal-neutral { color: #c9a76d; background: rgba(201, 167, 109, 0.12); }

.fin-label { font-size: 0.8rem; color: #9ca3af; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(111, 165, 168, 0.35); border-radius: 8px; }
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
