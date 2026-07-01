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

/* Tabs */
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #22d3ee !important;
    border-bottom-color: #22d3ee !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
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
