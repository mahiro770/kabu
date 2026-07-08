import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 15% -10%, #1b2140 0%, #0b0f19 45%) fixed;
}

.block-container { padding-top: 1.5rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #10141f;
    border-right: 1px solid rgba(139, 92, 246, 0.15);
}

/* Headings */
h1 {
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    width: fit-content;
}
h3, h4 { color: #e5e7eb; }

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, #171d30, #10131f);
    border: 1px solid rgba(139, 92, 246, 0.18);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
    border-color: rgba(139, 92, 246, 0.4);
}
[data-testid="stMetricLabel"] { color: #9ca3af; }
[data-testid="stMetricValue"] { color: #f3f4f6; }

/* Primary buttons */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #8b5cf6, #6366f1);
    border: none;
    box-shadow: 0 0 0 rgba(139, 92, 246, 0);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 0 18px rgba(139, 92, 246, 0.55);
    transform: translateY(-1px);
}

/* Secondary / default buttons */
[data-testid="stBaseButton-secondary"] {
    transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}
[data-testid="stBaseButton-secondary"]:hover {
    border-color: rgba(34, 211, 238, 0.6);
    box-shadow: 0 0 12px rgba(34, 211, 238, 0.25);
    transform: translateY(-1px);
}

/* Tabs */
[data-testid="stTabs"] button {
    transition: color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #22d3ee !important;
    border-bottom-color: #22d3ee !important;
}
[data-testid="stTabs"] button[aria-selected="false"]:hover {
    color: #a78bfa !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    transition: border-color 0.15s ease;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(139, 92, 246, 0.3);
}

/* Bordered containers used as cards (e.g. watchlist rows).
   Streamlit adds a "st-key-<key>" class to containers created with an explicit
   key= — used here instead of internal testids, which vary between versions. */
[class*="st-key-wlcard_"] {
    border-radius: 14px !important;
    margin-bottom: 0.9rem;
    background: linear-gradient(160deg, rgba(23, 29, 48, 0.6), rgba(16, 19, 31, 0.6)) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
[class*="st-key-wlcard_"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4);
    border-color: rgba(139, 92, 246, 0.45) !important;
}

/* Radio groups styled as pill chips (period / folder selectors).
   Streamlit has changed the internal radio-option markup across versions
   (BaseWeb "label[data-baseweb=radio]" in older releases, the "stRadioOption"
   testid in newer ones) — both selectors are kept so this works either way. */
[data-testid="stRadio"] label[data-baseweb="radio"],
[data-testid="stRadioOption"] {
    background: rgba(139, 92, 246, 0.06);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-right: 0.3rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
[data-testid="stRadioOption"]:hover {
    background: rgba(139, 92, 246, 0.16);
    border-color: rgba(139, 92, 246, 0.55);
    transform: translateY(-1px);
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadioOption"][data-selected="true"] {
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.25), rgba(34, 211, 238, 0.18));
    border-color: rgba(34, 211, 238, 0.6);
}

/* Text inputs / text areas */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: rgba(34, 211, 238, 0.6) !important;
    box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.3);
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
.signal-buy { color: #34d399; background: rgba(52, 211, 153, 0.12); }
.signal-sell { color: #f87171; background: rgba(248, 113, 113, 0.12); }
.signal-neutral { color: #fbbf24; background: rgba(251, 191, 36, 0.12); }

.fin-label { font-size: 0.8rem; color: #9ca3af; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.4); border-radius: 8px; }
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
