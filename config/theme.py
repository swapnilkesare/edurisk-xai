"""
Centralized Theme and Design System for EduRisk Modern Dark UI
Defines the authoritative color palette tokens, global CSS injection, and Plotly dark styling.
"""

# ==============================================================================
# AUTHORITATIVE COLOR PALETTE TOKENS
# ==============================================================================
COLOR_BG_MAIN = "#0B0D12"         # Matte black main background
COLOR_BG_CARD = "#151922"         # Cards, panels, modal surfaces
COLOR_BG_SECONDARY = "#10151D"    # Secondary surfaces, table headers, inner wells
COLOR_ACCENT_TEAL = "#19D3C5"     # Electric teal (Primary action, active nav, focus)
COLOR_ACCENT_TEAL_HOVER = "#15B5A8"
COLOR_ACCENT_VIOLET = "#9B8CFF"   # Soft violet (AI insights, SHAP secondary traces)
COLOR_TEXT_PRIMARY = "#F4F7FB"    # Soft white primary text
COLOR_TEXT_SECONDARY = "#AAB4C4"  # Muted secondary text
COLOR_BORDER = "#303642"          # Crisp card and container borders
COLOR_BORDER_SUBTLE = "#1E2430"   # Subtle divider lines

# Accessible Status & Risk Colors
COLOR_RISK_HIGH = "#FF5C5C"       # Priority Support / High Risk (Vibrant Accessible Red)
COLOR_RISK_MODERATE = "#FFB238"   # Monitoring Advised / Moderate Risk (Accessible Amber)
COLOR_RISK_LOW = "#19D3C5"        # On Track / Low Risk (Electric Teal)

# ==============================================================================
# GLOBAL STREAMLIT CSS INJECTION
# ==============================================================================
DARK_THEME_CSS = f"""
<style>
    /* 1. Global App Canvas & Core CSS Variables */
    :root {{
        --color-bg-main: {COLOR_BG_MAIN};
        --color-bg-card: {COLOR_BG_CARD};
        --color-bg-secondary: {COLOR_BG_SECONDARY};
        --color-accent-teal: {COLOR_ACCENT_TEAL};
        --color-accent-teal-hover: {COLOR_ACCENT_TEAL_HOVER};
        --color-accent-violet: {COLOR_ACCENT_VIOLET};
        --color-text-primary: {COLOR_TEXT_PRIMARY};
        --color-text-secondary: {COLOR_TEXT_SECONDARY};
        --color-border: {COLOR_BORDER};
        --color-border-subtle: {COLOR_BORDER_SUBTLE};
        --color-risk-high: {COLOR_RISK_HIGH};
        --color-risk-mod: {COLOR_RISK_MODERATE};
        --color-risk-low: {COLOR_RISK_LOW};
    }}

    /* Global Background and Typography */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {COLOR_BG_MAIN} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Hide default left sidebar cleanly */
    section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}

    /* Main Container Padding */
    div.block-container {{
        padding-top: 1.25rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1400px;
    }}

    /* 2. Text Elements & Headings */
    h1, h2, h3, h4, h5, h6, .stMarkdown p {{
        color: {COLOR_TEXT_PRIMARY} !important;
    }}
    .stMarkdown p, .stCaption, span, label {{
        color: {COLOR_TEXT_SECONDARY} !important;
    }}
    strong, b {{
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    /* 3. Top Navigation Bar Polish */
    .edurisk-navbar-container {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }}

    /* 4. Streamlit Buttons */
    /* Primary buttons: Electric Teal */
    .stButton>button[kind="primary"] {{
        background-color: {COLOR_ACCENT_TEAL} !important;
        color: #0B0D12 !important;
        border: 1px solid {COLOR_ACCENT_TEAL} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton>button[kind="primary"]:hover {{
        background-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        border-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        box-shadow: 0 0 12px rgba(25, 211, 197, 0.35) !important;
    }}

    /* Secondary buttons: Dark Card with Border */
    .stButton>button[kind="secondary"] {{
        background-color: {COLOR_BG_CARD} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton>button[kind="secondary"]:hover {{
        background-color: {COLOR_BG_SECONDARY} !important;
        border-color: {COLOR_ACCENT_TEAL} !important;
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    /* Active Nav Button Highlight */
    .nav-btn-active button {{
        background-color: {COLOR_BG_SECONDARY} !important;
        border: 1px solid {COLOR_ACCENT_TEAL} !important;
        color: {COLOR_ACCENT_TEAL} !important;
        font-weight: 700 !important;
        box-shadow: 0 0 8px rgba(25, 211, 197, 0.25) !important;
    }}

    /* 5. Inputs, Selectboxes, Number Inputs & Sliders */
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextInput>div>div, .stNumberInput>div>div {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}
    input, select, textarea {{
        color: {COLOR_TEXT_PRIMARY} !important;
        background-color: transparent !important;
    }}
    input:focus, select:focus, textarea:focus {{
        border-color: {COLOR_ACCENT_TEAL} !important;
        box-shadow: 0 0 6px rgba(25, 211, 197, 0.3) !important;
    }}
    div[data-baseweb="popover"], div[data-baseweb="menu"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
    }}
    li[role="option"] {{
        background-color: {COLOR_BG_CARD} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: {COLOR_BG_SECONDARY} !important;
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    /* 6. Expanders & Containers */
    div[data-testid="stExpander"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        background-color: {COLOR_BG_CARD} !important;
    }}
    div[data-testid="stExpander"] summary:hover {{
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    /* 7. Metrics & DataFrames */
    div[data-testid="stMetricValue"] {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {COLOR_TEXT_SECONDARY} !important;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        background-color: {COLOR_BG_CARD} !important;
    }}

    /* 8. Alerts & Info Banners */
    div[data-testid="stAlert"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        border-radius: 8px !important;
    }}

    /* Custom Reusable Component Classes */
    .edurisk-card {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    .edurisk-card-interactive:hover {{
        border-color: {COLOR_ACCENT_TEAL};
        box-shadow: 0 4px 16px rgba(25, 211, 197, 0.15);
    }}
</style>
"""

def inject_custom_theme():
    """Returns the CSS markup to inject into the Streamlit session."""
    return DARK_THEME_CSS

def apply_dark_theme_to_plotly(fig):
    """
    Applies the matte black / electric teal / soft violet palette to Plotly figures.
    """
    fig.update_layout(
        paper_bgcolor=COLOR_BG_CARD,
        plot_bgcolor=COLOR_BG_CARD,
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color=COLOR_TEXT_PRIMARY,
            size=12
        ),
        xaxis=dict(
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
            tickcolor=COLOR_BORDER,
            tickfont=dict(color=COLOR_TEXT_SECONDARY),
            titlefont=dict(color=COLOR_TEXT_PRIMARY)
        ),
        yaxis=dict(
            gridcolor=COLOR_BORDER,
            linecolor=COLOR_BORDER,
            tickcolor=COLOR_BORDER,
            tickfont=dict(color=COLOR_TEXT_SECONDARY),
            titlefont=dict(color=COLOR_TEXT_PRIMARY)
        ),
        legend=dict(
            font=dict(color=COLOR_TEXT_PRIMARY),
            bgcolor=COLOR_BG_SECONDARY,
            bordercolor=COLOR_BORDER,
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig
