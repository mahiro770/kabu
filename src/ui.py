import streamlit as st

THEMES = {
    "dark": {
        "label": "🌙 ダーク（現在の配色）",
        "bg-a": "#1a2130", "bg-b": "#0a0d15",
        "text": "#e5e9ed", "text-muted": "#9ca3af",
        "sidebar-bg": "#0e131c", "sidebar-border": "rgba(148, 163, 184, 0.12)",
        "h1-a": "#8fb4b0", "h1-b": "#c7d1d9", "heading": "#d8dde3",
        "card-a": "#161c26", "card-b": "#0f131b",
        "card-border": "rgba(148, 163, 184, 0.16)", "card-border-hover": "rgba(111, 165, 168, 0.4)",
        "metric-label": "#9ca3af", "metric-value": "#e5e9ed",
        "btn-primary-a": "#3d6b70", "btn-primary-b": "#2c4d52", "btn-glow": "rgba(111, 165, 168, 0.4)",
        "btn-secondary-border": "rgba(148, 163, 184, 0.28)",
        "btn-secondary-hover-border": "rgba(111, 165, 168, 0.55)", "btn-secondary-glow": "rgba(111, 165, 168, 0.2)",
        "tab-selected": "#8fb4b0", "tab-hover": "#a9b6bd",
        "expander-border": "rgba(255, 255, 255, 0.08)", "expander-hover-border": "rgba(111, 165, 168, 0.3)",
        "wlcard-a": "rgba(22, 28, 38, 0.6)", "wlcard-b": "rgba(15, 19, 27, 0.6)",
        "seccard-a": "rgba(19, 25, 34, 0.55)", "seccard-b": "rgba(14, 18, 25, 0.55)",
        "seccard-border": "rgba(148, 163, 184, 0.14)",
        "input-bg": "#131a24", "input-border": "rgba(148, 163, 184, 0.25)",
        "radio-bg": "rgba(111, 165, 168, 0.06)", "radio-border": "rgba(148, 163, 184, 0.18)",
        "radio-hover-bg": "rgba(111, 165, 168, 0.14)", "radio-hover-border": "rgba(111, 165, 168, 0.5)",
        "radio-sel-a": "rgba(111, 165, 168, 0.22)", "radio-sel-b": "rgba(148, 163, 184, 0.14)",
        "radio-sel-border": "rgba(111, 165, 168, 0.55)",
        "input-focus-border": "rgba(111, 165, 168, 0.55)", "input-focus-shadow": "rgba(111, 165, 168, 0.28)",
        "hr": "rgba(255, 255, 255, 0.08)",
        "signal-buy": "#7fb69c", "signal-buy-bg": "rgba(127, 182, 156, 0.12)",
        "signal-sell": "#c98f89", "signal-sell-bg": "rgba(201, 143, 137, 0.12)",
        "signal-neutral": "#c9a76d", "signal-neutral-bg": "rgba(201, 167, 109, 0.12)",
        "scrollbar": "rgba(111, 165, 168, 0.35)",
        "code-bg": "#131a24", "code-text": "#d8dde3",
        "shadow": "rgba(0, 0, 0, 0.4)", "shadow-strong": "rgba(0, 0, 0, 0.5)",
    },
    "light_gray": {
        "label": "⚪ ホワイト・グレー",
        "bg-a": "#ffffff", "bg-b": "#eef1f3",
        "text": "#1f2933", "text-muted": "#5b6572",
        "sidebar-bg": "#f5f6f8", "sidebar-border": "rgba(15, 23, 42, 0.10)",
        "h1-a": "#3d6b70", "h1-b": "#54626c", "heading": "#1f2933",
        "card-a": "#ffffff", "card-b": "#f3f5f6",
        "card-border": "rgba(15, 23, 42, 0.10)", "card-border-hover": "rgba(61, 107, 112, 0.4)",
        "metric-label": "#5b6572", "metric-value": "#1f2933",
        "btn-primary-a": "#3d6b70", "btn-primary-b": "#2c4d52", "btn-glow": "rgba(61, 107, 112, 0.3)",
        "btn-secondary-border": "rgba(15, 23, 42, 0.18)",
        "btn-secondary-hover-border": "rgba(61, 107, 112, 0.55)", "btn-secondary-glow": "rgba(61, 107, 112, 0.18)",
        "tab-selected": "#2c4d52", "tab-hover": "#3d6b70",
        "expander-border": "rgba(15, 23, 42, 0.10)", "expander-hover-border": "rgba(61, 107, 112, 0.35)",
        "wlcard-a": "#ffffff", "wlcard-b": "#f3f5f6",
        "seccard-a": "#ffffff", "seccard-b": "#f6f7f8",
        "seccard-border": "rgba(15, 23, 42, 0.09)",
        "input-bg": "#ffffff", "input-border": "rgba(15, 23, 42, 0.18)",
        "radio-bg": "rgba(61, 107, 112, 0.05)", "radio-border": "rgba(15, 23, 42, 0.14)",
        "radio-hover-bg": "rgba(61, 107, 112, 0.12)", "radio-hover-border": "rgba(61, 107, 112, 0.5)",
        "radio-sel-a": "rgba(61, 107, 112, 0.16)", "radio-sel-b": "rgba(15, 23, 42, 0.06)",
        "radio-sel-border": "rgba(61, 107, 112, 0.55)",
        "input-focus-border": "rgba(61, 107, 112, 0.55)", "input-focus-shadow": "rgba(61, 107, 112, 0.22)",
        "hr": "rgba(15, 23, 42, 0.10)",
        "signal-buy": "#2f6a4d", "signal-buy-bg": "rgba(47, 106, 77, 0.10)",
        "signal-sell": "#9c3f34", "signal-sell-bg": "rgba(156, 63, 52, 0.10)",
        "signal-neutral": "#8a6512", "signal-neutral-bg": "rgba(138, 101, 18, 0.10)",
        "scrollbar": "rgba(61, 107, 112, 0.3)",
        "code-bg": "#eef1f3", "code-text": "#1f2933",
        "shadow": "rgba(15, 23, 42, 0.08)", "shadow-strong": "rgba(15, 23, 42, 0.14)",
    },
    "beige": {
        "label": "🟤 ベージュ",
        "bg-a": "#f7f1e6", "bg-b": "#ece1cc",
        "text": "#3a3226", "text-muted": "#7a6f5c",
        "sidebar-bg": "#f1e9d8", "sidebar-border": "rgba(90, 72, 38, 0.14)",
        "h1-a": "#7a5c3e", "h1-b": "#9c8462", "heading": "#3a3226",
        "card-a": "#fffdf8", "card-b": "#f2e9d8",
        "card-border": "rgba(90, 72, 38, 0.14)", "card-border-hover": "rgba(122, 92, 62, 0.4)",
        "metric-label": "#7a6f5c", "metric-value": "#3a3226",
        "btn-primary-a": "#7a5c3e", "btn-primary-b": "#5c4530", "btn-glow": "rgba(122, 92, 62, 0.3)",
        "btn-secondary-border": "rgba(90, 72, 38, 0.22)",
        "btn-secondary-hover-border": "rgba(122, 92, 62, 0.55)", "btn-secondary-glow": "rgba(122, 92, 62, 0.18)",
        "tab-selected": "#7a5c3e", "tab-hover": "#9c8462",
        "expander-border": "rgba(90, 72, 38, 0.14)", "expander-hover-border": "rgba(122, 92, 62, 0.35)",
        "wlcard-a": "#fffdf8", "wlcard-b": "#f2e9d8",
        "seccard-a": "#fffdf8", "seccard-b": "#f5edde",
        "seccard-border": "rgba(90, 72, 38, 0.13)",
        "input-bg": "#fffdf8", "input-border": "rgba(90, 72, 38, 0.22)",
        "radio-bg": "rgba(122, 92, 62, 0.06)", "radio-border": "rgba(90, 72, 38, 0.18)",
        "radio-hover-bg": "rgba(122, 92, 62, 0.14)", "radio-hover-border": "rgba(122, 92, 62, 0.5)",
        "radio-sel-a": "rgba(122, 92, 62, 0.20)", "radio-sel-b": "rgba(90, 72, 38, 0.08)",
        "radio-sel-border": "rgba(122, 92, 62, 0.55)",
        "input-focus-border": "rgba(122, 92, 62, 0.55)", "input-focus-shadow": "rgba(122, 92, 62, 0.22)",
        "hr": "rgba(90, 72, 38, 0.15)",
        "signal-buy": "#3f6b45", "signal-buy-bg": "rgba(63, 107, 69, 0.12)",
        "signal-sell": "#9c4b3a", "signal-sell-bg": "rgba(156, 75, 58, 0.12)",
        "signal-neutral": "#8c6a1c", "signal-neutral-bg": "rgba(140, 106, 28, 0.12)",
        "scrollbar": "rgba(122, 92, 62, 0.3)",
        "code-bg": "#f2e9d8", "code-text": "#3a3226",
        "shadow": "rgba(58, 50, 38, 0.10)", "shadow-strong": "rgba(58, 50, 38, 0.16)",
    },
}
DEFAULT_THEME = "dark"


def _css_vars(theme: str) -> str:
    tokens = THEMES.get(theme, THEMES[DEFAULT_THEME])
    lines = [f"--{k}: {v};" for k, v in tokens.items() if k != "label"]
    return "\n".join(lines)


def _build_css(theme: str) -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap');

:root {{
{_css_vars(theme)}
}}

html, body, [class*="css"] {{
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 15% -10%, var(--bg-a) 0%, var(--bg-b) 45%) fixed;
    color: var(--text);
}}
[data-testid="stCaptionContainer"], .fin-label {{ color: var(--text-muted) !important; }}
/* Widget labels (e.g. "AIモデル", "表示言語") and help/alert text default to
   Streamlit's own dark-theme palette regardless of our theme — force them
   to follow the selected theme too so they stay legible on light grounds. */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
label, [data-testid="stAlertContentInfo"], [data-testid="stAlertContentWarning"],
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentError"] {{
    color: var(--text) !important;
}}

.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
}}

/* Headings */
h1 {{
    font-weight: 700;
    font-size: 2.6rem;
    letter-spacing: -0.01em;
    background: linear-gradient(90deg, var(--h1-a), var(--h1-b));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    width: fit-content;
}}
h3, h4 {{ color: var(--heading); margin-top: 0.4rem; margin-bottom: 1rem; }}

/* Metric cards */
[data-testid="stMetric"] {{
    background: linear-gradient(160deg, var(--card-a), var(--card-b));
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    box-shadow: 0 4px 16px var(--shadow);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px var(--shadow-strong);
    border-color: var(--card-border-hover);
}}
[data-testid="stMetricLabel"] {{ color: var(--metric-label); }}
[data-testid="stMetricValue"] {{ color: var(--metric-value); }}
/* Long values (e.g. "33.51兆円", "-59 (-2.04%)") wrap onto a second line
   instead of truncating with an ellipsis — never hide the actual number.
   The truncation styles are set on the innermost <p>, not on stMetricValue
   or stMarkdownContainer themselves, so all three levels must be overridden. */
[data-testid="stMetricValue"], [data-testid="stMetricDelta"],
[data-testid="stMetricValue"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricDelta"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricValue"] p, [data-testid="stMetricDelta"] p {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: break-word;
    line-height: 1.2;
}}

/* Primary buttons */
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(90deg, var(--btn-primary-a), var(--btn-primary-b));
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-size: 1.02rem;
    color: #f3f6f6;
    box-shadow: 0 0 0 rgba(0, 0, 0, 0);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}}
[data-testid="stBaseButton-primary"]:hover {{
    box-shadow: 0 0 14px var(--btn-glow);
    transform: translateY(-1px);
}}

/* Secondary / default buttons */
[data-testid="stBaseButton-secondary"] {{
    border-radius: 10px;
    padding: 0.5rem 1.1rem;
    background: var(--card-a) !important;
    color: var(--text) !important;
    border-color: var(--btn-secondary-border) !important;
    transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}}
[data-testid="stBaseButton-secondary"]:hover {{
    border-color: var(--btn-secondary-hover-border);
    box-shadow: 0 0 10px var(--btn-secondary-glow);
    transform: translateY(-1px);
}}

/* Tabs */
[data-testid="stTabs"] button {{
    transition: color 0.15s ease, border-color 0.15s ease;
    color: var(--text-muted);
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: var(--tab-selected) !important;
    border-bottom-color: var(--tab-selected) !important;
}}
[data-testid="stTabs"] button[aria-selected="false"]:hover {{
    color: var(--tab-hover) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    border: 1px solid var(--expander-border);
    border-radius: 10px;
    transition: border-color 0.15s ease;
}}
[data-testid="stExpander"]:hover {{
    border-color: var(--expander-hover-border);
}}

/* Bordered containers used as cards (e.g. watchlist rows).
   Streamlit adds a "st-key-<key>" class to containers created with an explicit
   key= — used here instead of internal testids, which vary between versions. */
[class*="st-key-wlcard_"] {{
    border-radius: 14px !important;
    margin-bottom: 0.9rem;
    background: linear-gradient(160deg, var(--wlcard-a), var(--wlcard-b)) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}}
[class*="st-key-wlcard_"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 28px var(--shadow-strong);
    border-color: var(--card-border-hover) !important;
}}

/* Static section cards — used to group related content (financial metric
   groups, AI report output, usage guides) into visually distinct blocks.
   Unlike wlcard, these aren't clickable, so no hover lift. */
[class*="st-key-seccard_"] {{
    border-radius: 16px !important;
    padding: 1.3rem 1.5rem !important;
    margin-bottom: 1.6rem;
    background: linear-gradient(160deg, var(--seccard-a), var(--seccard-b)) !important;
    border-color: var(--seccard-border) !important;
}}

/* Radio groups styled as pill chips (period / folder selectors).
   Streamlit has changed the internal radio-option markup across versions
   (BaseWeb "label[data-baseweb=radio]" in older releases, the "stRadioOption"
   testid in newer ones) — both selectors are kept so this works either way. */
[data-testid="stRadio"] label[data-baseweb="radio"],
[data-testid="stRadioOption"] {{
    background: var(--radio-bg);
    border: 1px solid var(--radio-border);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-right: 0.3rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
[data-testid="stRadioOption"]:hover {{
    background: var(--radio-hover-bg);
    border-color: var(--radio-hover-border);
    transform: translateY(-1px);
}}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
[data-testid="stRadioOption"][data-selected="true"] {{
    background: linear-gradient(90deg, var(--radio-sel-a), var(--radio-sel-b));
    border-color: var(--radio-sel-border);
}}
/* The dot indicator's innermost fill hardcodes Streamlit's own base
   background color (meant to be invisible against Streamlit's own dark
   theme) — it stays visible as a stray dark circle on our light themes,
   so it's forced transparent (or accent-colored when selected) instead. */
[data-testid="stRadioOption"] > div > div > div > div {{
    background: transparent !important;
}}
[data-testid="stRadioOption"][data-selected="true"] > div > div > div > div {{
    background: var(--radio-sel-border) !important;
}}

/* Text inputs / text areas / select boxes / multiselect / sliders */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
    background: var(--input-bg) !important;
    border-color: var(--input-border) !important;
    color: var(--text) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {{
    border-color: var(--input-focus-border) !important;
    box-shadow: 0 0 0 1px var(--input-focus-shadow);
}}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{ background: var(--radio-border) !important; }}

hr {{ border-color: var(--hr); }}

/* Signal badges */
.signal-buy, .signal-sell, .signal-neutral {{
    display: inline-block;
    padding: 0.15rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
}}
.signal-buy {{ color: var(--signal-buy); background: var(--signal-buy-bg); }}
.signal-sell {{ color: var(--signal-sell); background: var(--signal-sell-bg); }}
.signal-neutral {{ color: var(--signal-neutral); background: var(--signal-neutral-bg); }}

code {{ background: var(--code-bg) !important; color: var(--code-text) !important; }}

::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-thumb {{ background: var(--scrollbar); border-radius: 8px; }}
</style>
"""


def get_current_theme() -> str:
    # ウィジェット自身のkey（"app_theme_widget"）はクリック直後の同一スクリプト内
    # でも最新値になっているため、まずそれを優先して読む（切り替えた瞬間に反映
    # させるため）。ページ遷移でそのウィジェットがまだ描画されていない場合は
    # 存在しないので、current_tickerと同じ明示代入パターンの"theme_choice"に
    # フォールバックする。
    if "app_theme_widget" in st.session_state:
        return st.session_state["app_theme_widget"]
    return st.session_state.get("theme_choice", DEFAULT_THEME)


def inject_theme(theme: str | None = None) -> None:
    st.markdown(_build_css(theme or get_current_theme()), unsafe_allow_html=True)


def render_theme_switcher() -> None:
    """サイドバーに背景テーマの切り替えUIを表示する。選択は全ページで共有される。"""
    keys = list(THEMES.keys())
    current = get_current_theme()
    current_index = keys.index(current) if current in keys else 0
    selected = st.selectbox(
        "背景テーマ", keys, index=current_index, key="app_theme_widget",
        format_func=lambda t: THEMES[t]["label"],
    )
    st.session_state.theme_choice = selected
