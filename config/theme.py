"""
Centralized Theme and Design System for EduRisk Modern White UI
Defines the authoritative color palette tokens, global CSS injection, and Plotly light styling.
"""

# ==============================================================================
# AUTHORITATIVE WHITE THEME COLOR PALETTE TOKENS
# ==============================================================================
COLOR_BG_MAIN = "#F8FAFC"             # Slate-50 canvas background
COLOR_BG_CARD = "#FFFFFF"             # Crisp white cards, panels, and surfaces
COLOR_BG_SECONDARY = "#F1F5F9"        # Slate-100 secondary surfaces, wells, table headers
COLOR_ACCENT_TEAL = "#0F9F95"         # Primary brand teal
COLOR_ACCENT_TEAL_HOVER = "#0C827A"   # Darker teal on hover
COLOR_ACCENT_TEAL_SURFACE = "#E8F8F6" # Light teal background for active states & highlights
COLOR_ACCENT_VIOLET = "#7966D8"       # Secondary accent violet (insights, tags)
COLOR_TEXT_PRIMARY = "#172033"        # Deep slate heading text
COLOR_TEXT_BODY = "#475569"           # Slate-600 body typography
COLOR_TEXT_SECONDARY = "#64748B"      # Slate-500 secondary text & captions
COLOR_TEXT_MUTED = "#94A3B8"          # Slate-400 placeholder & muted text
COLOR_BORDER = "#E2E8F0"              # Slate-200 container borders
COLOR_BORDER_SUBTLE = "#F1F5F9"       # Slate-100 divider lines

# Specific Button Contrast Tokens
COLOR_BTN_PRIMARY_BG = "#0F9F95"      # Primary teal button background
COLOR_BTN_PRIMARY_TEXT = "#FFFFFF"    # Crisp white text on primary teal buttons
COLOR_BTN_SECONDARY_BG = "#FFFFFF"    # Clean white surface for secondary buttons
COLOR_BTN_SECONDARY_TEXT = "#172033"  # Deep slate text on secondary buttons
COLOR_MUTED_TEXT = "#64748B"          # Muted text for captions

# Accessible Status & Risk Colors
COLOR_RISK_HIGH = "#DC2626"           # High Risk / Priority Support (Accessible Crimson)
COLOR_RISK_HIGH_SURFACE = "#FEE2E2"   # Light red surface
COLOR_RISK_MODERATE = "#D97706"       # Moderate Risk / Monitoring Advised (Accessible Amber)
COLOR_RISK_MODERATE_SURFACE = "#FEF3C7" # Light amber surface
COLOR_RISK_LOW = "#15803D"            # Low Risk / On Track (Accessible Forest Green)
COLOR_RISK_LOW_SURFACE = "#DCFCE7"    # Light green surface

# ==============================================================================
# GLOBAL STREAMLIT CSS INJECTION (WHITE THEME)
# ==============================================================================
WHITE_THEME_CSS = f"""
<style>
    /* 1. Global App Canvas & Core CSS Variables */
    :root {{
        --color-bg-main: {COLOR_BG_MAIN};
        --color-bg-card: {COLOR_BG_CARD};
        --color-bg-secondary: {COLOR_BG_SECONDARY};
        --color-accent-teal: {COLOR_ACCENT_TEAL};
        --color-accent-teal-hover: {COLOR_ACCENT_TEAL_HOVER};
        --color-accent-teal-surface: {COLOR_ACCENT_TEAL_SURFACE};
        --color-accent-violet: {COLOR_ACCENT_VIOLET};
        --color-text-primary: {COLOR_TEXT_PRIMARY};
        --color-text-body: {COLOR_TEXT_BODY};
        --color-text-secondary: {COLOR_TEXT_SECONDARY};
        --color-border: {COLOR_BORDER};
        --color-border-subtle: {COLOR_BORDER_SUBTLE};
        --color-btn-primary-text: {COLOR_BTN_PRIMARY_TEXT};
        --color-btn-secondary-bg: {COLOR_BTN_SECONDARY_BG};
        --color-btn-secondary-text: {COLOR_BTN_SECONDARY_TEXT};
        --color-muted-text: {COLOR_MUTED_TEXT};
        --color-risk-high: {COLOR_RISK_HIGH};
        --color-risk-mod: {COLOR_RISK_MODERATE};
        --color-risk-low: {COLOR_RISK_LOW};
    }}

    /* Global Background and Typography */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: {COLOR_BG_MAIN} !important;
        color: {COLOR_TEXT_BODY} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Hide default left sidebar cleanly */
    section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}

    /* Main Container Padding & Uncompressed Width */
    div.block-container {{
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }}

    /* 2. Text Elements & Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    /* Normal body text inside markdown containers (excluding button descendants) */
    div[data-testid="stMarkdownContainer"]:not(button *):not([data-testid^="baseButton"] *) > p {{
        color: {COLOR_TEXT_BODY};
        line-height: 1.55;
    }}

    .stCaption, p.stCaption {{
        color: {COLOR_TEXT_SECONDARY} !important;
    }}

    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    strong, b {{
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* 3. Top Navigation Bar Container */
    .edurisk-navbar-container {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    /* Responsive adjustments for navbar */
    @media (max-width: 992px) {{
        .edurisk-navbar-container {{
            padding: 0.4rem 0.5rem;
        }}
        .edurisk-navbar-container .stButton button {{
            font-size: 0.82rem !important;
            padding: 0.25rem 0.35rem !important;
        }}
    }}

    /* 4. Streamlit Buttons & Controls */
    /* PRIMARY BUTTONS: Brand Teal Background with Crisp White Text */
    button[kind="primary"],
    button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"] {{
        background-color: {COLOR_ACCENT_TEAL} !important;
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        border: 1px solid {COLOR_ACCENT_TEAL} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.18s ease-in-out !important;
        box-shadow: 0 1px 2px rgba(15, 159, 149, 0.2) !important;
    }}

    button[kind="primary"] *,
    button[data-testid="baseButton-primary"] *,
    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] *,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"] * {{
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        fill: {COLOR_BTN_PRIMARY_TEXT} !important;
        font-weight: 600 !important;
    }}

    /* PRIMARY BUTTONS HOVER */
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"]:hover {{
        background-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        border-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        box-shadow: 0 2px 6px rgba(15, 159, 149, 0.3) !important;
    }}

    /* SECONDARY BUTTONS: Clean White Card Surface with Deep Slate Text and Border */
    button[kind="secondary"],
    button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"],
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-secondary"] {{
        background-color: {COLOR_BTN_SECONDARY_BG} !important;
        color: {COLOR_BTN_SECONDARY_TEXT} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.18s ease-in-out !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    }}

    button[kind="secondary"] *,
    button[data-testid="baseButton-secondary"] *,
    .stButton > button[kind="secondary"] *,
    .stButton > button[data-testid="baseButton-secondary"] *,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"] *,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-secondary"] * {{
        color: {COLOR_BTN_SECONDARY_TEXT} !important;
        fill: {COLOR_BTN_SECONDARY_TEXT} !important;
    }}

    /* SECONDARY BUTTONS HOVER: Light Teal Surface & Teal Border */
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"]:hover {{
        background-color: {COLOR_ACCENT_TEAL_SURFACE} !important;
        border-color: {COLOR_ACCENT_TEAL} !important;
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    button[kind="secondary"]:hover *,
    button[data-testid="baseButton-secondary"]:hover *,
    .stButton > button[kind="secondary"]:hover *,
    .stButton > button[data-testid="baseButton-secondary"]:hover *,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"]:hover * {{
        color: {COLOR_ACCENT_TEAL} !important;
        fill: {COLOR_ACCENT_TEAL} !important;
    }}

    /* 5. Inputs, Selectboxes, Number Inputs & Sliders */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stNumberInput > div > div {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    input, select, textarea {{
        color: {COLOR_TEXT_PRIMARY} !important;
        background-color: transparent !important;
    }}

    input::placeholder, textarea::placeholder {{
        color: {COLOR_TEXT_MUTED} !important;
    }}

    input:focus, select:focus, textarea:focus {{
        border-color: {COLOR_ACCENT_TEAL} !important;
        box-shadow: 0 0 0 3px rgba(15, 159, 149, 0.15) !important;
    }}

    /* Select Dropdown Menu & Popover */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08) !important;
    }}

    li[role="option"] {{
        background-color: {COLOR_BG_CARD} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    li[role="option"]:hover,
    li[aria-selected="true"] {{
        background-color: {COLOR_ACCENT_TEAL_SURFACE} !important;
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    /* 6. Expanders & Containers */
    div[data-testid="stExpander"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
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
        font-weight: 500 !important;
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
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }}
    .edurisk-card-interactive:hover {{
        border-color: {COLOR_ACCENT_TEAL};
        box-shadow: 0 4px 12px rgba(15, 159, 149, 0.1);
    }}
</style>
"""

def inject_custom_theme():
    """Returns the white theme CSS markup to inject into the Streamlit session."""
    return WHITE_THEME_CSS

def apply_dark_theme_to_plotly(fig):
    """
    Applies the clean white theme palette to Plotly figures.
    (Kept name for backward compatibility across existing report pages).
    """
    fig.update_layout(
        paper_bgcolor=COLOR_BG_CARD,
        plot_bgcolor=COLOR_BG_CARD,
        font=dict(
            family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            color=COLOR_TEXT_PRIMARY,
            size=12
        ),
        xaxis=dict(
            gridcolor=COLOR_BORDER_SUBTLE,
            linecolor=COLOR_BORDER,
            tickcolor=COLOR_BORDER,
            tickfont=dict(color=COLOR_TEXT_SECONDARY),
            titlefont=dict(color=COLOR_TEXT_PRIMARY)
        ),
        yaxis=dict(
            gridcolor=COLOR_BORDER_SUBTLE,
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
