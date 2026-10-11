"""
Centralized Theme and Design System for EduRisk Modern Dark UI
Defines the authoritative color palette tokens, global CSS injection, and Plotly dark styling.
"""

# ==============================================================================
# AUTHORITATIVE COLOR PALETTE TOKENS
# ==============================================================================
COLOR_BG_MAIN = "#0B0D12"             # Matte black main canvas background
COLOR_BG_CARD = "#151922"             # Cards, panels, modal surfaces
COLOR_BG_SECONDARY = "#10151D"        # Secondary surfaces, table headers, inner wells
COLOR_ACCENT_TEAL = "#19D3C5"         # Electric teal (Primary action, active nav, focus)
COLOR_ACCENT_TEAL_HOVER = "#22F3E4"   # Slightly brighter teal on hover, retaining dark text
COLOR_ACCENT_VIOLET = "#9B8CFF"       # Soft violet (AI insights, SHAP secondary traces)
COLOR_TEXT_PRIMARY = "#F4F7FB"        # Soft white primary text
COLOR_TEXT_SECONDARY = "#AAB4C4"      # Muted secondary text
COLOR_BORDER = "#303642"              # Crisp card and container borders
COLOR_BORDER_SUBTLE = "#1E2430"       # Subtle divider lines

# Specific Button Contrast Tokens (Palette Specification)
COLOR_BTN_PRIMARY_TEXT = "#071014"    # Dark black text on primary teal buttons
COLOR_BTN_SECONDARY_BG = "#151922"    # Dark surface for secondary buttons
COLOR_BTN_SECONDARY_TEXT = "#E6EDF5"  # Crisp light text on secondary buttons
COLOR_MUTED_TEXT = "#AAB4C4"         # Muted text for captions and secondary notes

# Accessible Status & Risk Colors
COLOR_RISK_HIGH = "#FF5C5C"           # Priority Support / High Risk (Vibrant Accessible Red)
COLOR_RISK_MODERATE = "#FFB238"       # Monitoring Advised / Moderate Risk (Accessible Amber)
COLOR_RISK_LOW = "#19D3C5"            # On Track / Low Risk (Electric Teal)

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
        color: {COLOR_TEXT_PRIMARY} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Hide default left sidebar cleanly */
    section[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}

    /* Main Container Padding */
    div.block-container {{
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }}

    /* 2. Text Elements & Headings (Targeted to prevent leaking into button labels) */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 700;
    }}

    /* Normal body text inside markdown containers (excluding button descendants) */
    div[data-testid="stMarkdownContainer"]:not(button *):not([data-testid^="baseButton"] *) > p {{
        color: {COLOR_TEXT_PRIMARY};
    }}

    .stCaption, p.stCaption {{
        color: {COLOR_MUTED_TEXT} !important;
    }}

    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {{
        color: {COLOR_TEXT_PRIMARY} !important;
        font-weight: 500 !important;
    }}

    strong, b {{
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* 3. Top Navigation Bar Container */
    .edurisk-navbar-container {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 0.5rem 0.85rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
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

    /* 4. Streamlit Buttons & Controls (Targeted Precision) */
    /* PRIMARY BUTTONS: Electric Teal Background with Dark #071014 Text */
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
        font-weight: 700 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }}

    /* CRITICAL SPECIFICITY OVERRIDE: Ensure all nested elements inside primary buttons are dark #071014 */
    button[kind="primary"] *,
    button[data-testid="baseButton-primary"] *,
    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] *,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"] * {{
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        fill: {COLOR_BTN_PRIMARY_TEXT} !important;
        font-weight: 700 !important;
    }}

    /* PRIMARY BUTTONS HOVER: Slightly brighter teal, retaining readable dark #071014 text */
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-primary"]:hover {{
        background-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        border-color: {COLOR_ACCENT_TEAL_HOVER} !important;
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        box-shadow: 0 0 14px rgba(25, 211, 197, 0.45) !important;
    }}

    button[kind="primary"]:hover *,
    button[data-testid="baseButton-primary"]:hover *,
    .stButton > button[kind="primary"]:hover *,
    .stButton > button[data-testid="baseButton-primary"]:hover *,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover * {{
        color: {COLOR_BTN_PRIMARY_TEXT} !important;
        fill: {COLOR_BTN_PRIMARY_TEXT} !important;
    }}

    /* SECONDARY BUTTONS: Dark Card Surface #151922 with Light #E6EDF5 Text and Subtle #303642 Border */
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
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }}

    /* Ensure all nested elements inside secondary buttons are light #E6EDF5 */
    button[kind="secondary"] *,
    button[data-testid="baseButton-secondary"] *,
    .stButton > button[kind="secondary"] *,
    .stButton > button[data-testid="baseButton-secondary"] *,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"] *,
    div[data-testid="stFormSubmitButton"] > button[data-testid="baseButton-secondary"] * {{
        color: {COLOR_BTN_SECONDARY_TEXT} !important;
        fill: {COLOR_BTN_SECONDARY_TEXT} !important;
    }}

    /* SECONDARY BUTTONS HOVER: Dark Surface with Teal Border & Teal Text */
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"]:hover {{
        background-color: {COLOR_BG_SECONDARY} !important;
        border-color: {COLOR_ACCENT_TEAL} !important;
        color: {COLOR_ACCENT_TEAL} !important;
        box-shadow: 0 0 8px rgba(25, 211, 197, 0.25) !important;
    }}

    button[kind="secondary"]:hover *,
    button[data-testid="baseButton-secondary"]:hover *,
    .stButton > button[kind="secondary"]:hover *,
    .stButton > button[data-testid="baseButton-secondary"]:hover *,
    div[data-testid="stFormSubmitButton"] > button[kind="secondary"]:hover * {{
        color: {COLOR_ACCENT_TEAL} !important;
        fill: {COLOR_ACCENT_TEAL} !important;
    }}

    /* DISABLED BUTTON STATE: Visibly disabled but legible */
    button:disabled,
    button[disabled],
    .stButton > button:disabled,
    .stButton > button[disabled],
    div[data-testid="stFormSubmitButton"] > button:disabled {{
        opacity: 0.55 !important;
        cursor: not-allowed !important;
        border-color: {COLOR_BORDER} !important;
        box-shadow: none !important;
    }}

    button:disabled *,
    button[disabled] * {{
        opacity: 0.75 !important;
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
        color: #717D91 !important;
    }}

    input:focus, select:focus, textarea:focus {{
        border-color: {COLOR_ACCENT_TEAL} !important;
        box-shadow: 0 0 6px rgba(25, 211, 197, 0.3) !important;
    }}

    /* Select Dropdown Menu & Popover */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"] {{
        background-color: {COLOR_BG_CARD} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
    }}

    li[role="option"] {{
        background-color: {COLOR_BG_CARD} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    li[role="option"]:hover,
    li[aria-selected="true"] {{
        background-color: {COLOR_BG_SECONDARY} !important;
        color: {COLOR_ACCENT_TEAL} !important;
    }}

    /* Help tooltips and icons */
    div[data-testid="stTooltipIcon"] svg {{
        fill: {COLOR_MUTED_TEXT} !important;
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
