"""
inject_css.py — Sephora Design System
Cormorant Garamond | Dark/Light | Editorial
"""


def get_css(theme: str = "dark") -> str:
    if theme == "light":
        BG          = "#F5F0EB"
        SURFACE     = "#FFFFFF"
        SURFACE2    = "#F8F4EF"
        SURFACE3    = "#F0EBE3"
        TEXT        = "#0A0A0A"
        GOLD        = "#8B6914"
        BORDER      = "#E0D8CC"
        BORDER2     = "#D4C9BB"
        MUTED       = "#888888"
        SIDEBAR_BG  = "#0A0A0A"   # sidebar RESTE sombre en mode clair
        RED         = "#B30029"
        GREEN       = "#1A7A72"
        INPUT_BG    = "#FFFFFF"
        SCROLLTHUMB = "#D4C9BB"
        NOISE_OP    = "0.02"
        SIDEBAR_AF  = "rgba(139,105,20,0.3)"
    else:
        BG          = "#000000"
        SURFACE     = "#0D0D0D"
        SURFACE2    = "#0A0A0A"
        SURFACE3    = "#050505"
        TEXT        = "#FFFFFF"
        GOLD        = "#C9A84C"
        BORDER      = "#1A1A1A"
        BORDER2     = "#333333"
        MUTED       = "#CCCCCC"
        SIDEBAR_BG  = "#050505"
        RED         = "#CC0033"
        GREEN       = "#2EC4B6"
        INPUT_BG    = "#0D0D0D"
        SCROLLTHUMB = "#1A1A1A"
        NOISE_OP    = "0.015"
        SIDEBAR_AF  = "rgba(201,168,76,0.4)"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,300;1,400&family=DM+Mono:wght@300;400;500&display=swap');

/* ── RESET & BASE ─────────────────────────────────────────────────── */
*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

/* ── STREAMLIT GLOBALS ────────────────────────────────────────────── */
.stApp {{
    background: {BG} !important;
}}
.main .block-container {{
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}}
html, body, [class*="css"] {{
    font-family: 'Jost', sans-serif !important;
    background: {BG};
    color: {TEXT};
}}

/* ── STICKY LOGO HEADER ───────────────────────────────────────────── */
.sephora-sticky-logo {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: {BG};
    border-bottom: 1px solid {BORDER};
    height: 48px;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0 0.5rem;
    margin-bottom: 1.5rem;
    animation: slideInLeft 0.4s ease forwards;
}}
.sephora-sticky-logo .logo-title {{
    font-family: 'Jost', sans-serif;
    font-weight: 300;
    font-size: 1.4rem;
    color: {TEXT};
    letter-spacing: 0.15em;
    font-style: italic;
    white-space: nowrap;
    margin: 0;
    line-height: 1;
}}
.sephora-sticky-logo .logo-sub {{
    font-family: 'DM Mono', monospace;
    font-size: 0.5rem;
    letter-spacing: 0.22em;
    color: {GOLD};
    text-transform: uppercase;
    border-left: 1px solid {BORDER2};
    padding-left: 1rem;
    white-space: nowrap;
}}
.sephora-sticky-logo .logo-jury {{
    font-family: 'DM Mono', monospace;
    font-size: 0.48rem;
    letter-spacing: 0.12em;
    color: {MUTED};
    text-transform: uppercase;
    margin-left: auto;
}}

/* ── SIDEBAR SEPHORA ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] .stRadio label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    padding: 0.6rem 1rem !important;
    border-left: 2px solid transparent !important;
    transition: all 0.3s ease !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    color: {GOLD} !important;
    border-left: 2px solid {GOLD} !important;
    background: rgba(201,168,76,0.05) !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdown"] {{
    color: {MUTED} !important;
}}
[data-testid="stSidebar"]::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 1.5rem;
    right: 1.5rem;
    height: 1px;
    background: linear-gradient(90deg, transparent, {SIDEBAR_AF}, transparent);
}}

/* ── TYPOGRAPHY ───────────────────────────────────────────────────── */
h1 {{
    font-family: 'Jost', sans-serif !important;
    font-weight: 300 !important;
    font-size: 2.8rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {TEXT} !important;
}}
h2 {{
    font-family: 'Jost', sans-serif !important;
    font-weight: 400 !important;
    font-size: 1.6rem !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    color: {TEXT} !important;
    border-bottom: 1px solid {BORDER} !important;
    padding-bottom: 0.5rem !important;
}}
h3 {{
    font-family: 'Jost', sans-serif !important;
    font-weight: 300 !important;
    font-size: 1.2rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: {TEXT} !important;
}}
h4 {{
    font-family: 'Jost', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    margin: 1.5rem 0 0.8rem !important;
}}
p {{
    font-family: 'Jost', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 300 !important;
    color: {MUTED} !important;
    line-height: 1.7 !important;
}}

/* ── KPI LABELS & VALUES ─────────────────────────────────────────── */
.kpi-label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    margin-bottom: 0.4rem !important;
}}
.kpi-value {{
    font-family: 'Jost', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 300 !important;
    color: {GOLD} !important;
    line-height: 1 !important;
}}
.kpi-delta {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    color: {MUTED} !important;
    margin-top: 0.4rem !important;
    letter-spacing: 0.08em !important;
}}

/* ── KPI CARDS ───────────────────────────────────────────────────── */
.kpi-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-top: 2px solid {GOLD};
    padding: 1.5rem 1.2rem;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.6s ease forwards;
    transition: border-color 0.3s ease, transform 0.2s ease;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {GOLD}, transparent);
    animation: shimmerLine 3s infinite;
}}
.kpi-card:hover {{
    border-color: {GOLD};
    transform: translateY(-2px);
}}
.kpi-card.danger {{
    border-top-color: {RED};
}}
.kpi-card.danger .kpi-value {{
    color: {RED} !important;
}}
.kpi-card.success {{
    border-top-color: {GREEN};
}}
.kpi-card.success .kpi-value {{
    color: {GREEN} !important;
}}

/* Override existing kpi-gold class */
.kpi-gold {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-top: 2px solid {GOLD} !important;
    border-radius: 0 !important;
    padding: 1.5rem 1.2rem !important;
    position: relative !important;
    overflow: hidden !important;
    animation: fadeInUp 0.6s ease forwards !important;
    transition: border-color 0.3s ease, transform 0.2s ease !important;
}}
.kpi-gold::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {GOLD}, transparent);
    animation: shimmerLine 3s infinite;
}}
.kpi-gold:hover {{
    border-color: {GOLD} !important;
    transform: translateY(-2px) !important;
}}
.kpi-gold .kpi-label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    margin-bottom: 0.4rem !important;
}}
.kpi-gold .kpi-value {{
    font-family: 'Jost', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 300 !important;
    color: {GOLD} !important;
    line-height: 1 !important;
}}
.kpi-gold .kpi-delta {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    color: {MUTED} !important;
    margin-top: 0.4rem !important;
    letter-spacing: 0.08em !important;
}}

/* ── PAGE HEADER ─────────────────────────────────────────────────── */
.page-header {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    color: {GOLD} !important;
    border-bottom: 1px solid {BORDER} !important;
    padding-bottom: 0.6rem !important;
    margin-bottom: 1.6rem !important;
    animation: slideInLeft 0.5s ease forwards !important;
}}

/* ── ALERT COMPONENTS ────────────────────────────────────────────── */
.alert-red {{
    background: rgba(204,0,51,0.06) !important;
    border: 1px solid {BORDER} !important;
    border-left: 3px solid {RED} !important;
    border-radius: 0 !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
    animation: fadeInUp 0.4s ease forwards !important;
}}
.alert-red .alert-title {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: {RED} !important;
    text-transform: uppercase !important;
    margin-bottom: 0.3rem !important;
}}
.alert-red .alert-body {{
    font-family: 'Jost', sans-serif !important;
    font-size: 0.8rem !important;
    color: {TEXT} !important;
    line-height: 1.6 !important;
    opacity: 0.85;
}}
.alert-green {{
    background: rgba(46,196,182,0.05) !important;
    border: 1px solid {BORDER} !important;
    border-left: 3px solid {GREEN} !important;
    border-radius: 0 !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.6rem !important;
}}
.alert-green .alert-title {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    color: {GREEN} !important;
    text-transform: uppercase !important;
    margin-bottom: 0.3rem !important;
}}
.alert-green .alert-body {{
    font-family: 'Jost', sans-serif !important;
    font-size: 0.8rem !important;
    color: {TEXT} !important;
    line-height: 1.6 !important;
    opacity: 0.85;
}}

/* ── VERSUS BOX ──────────────────────────────────────────────────── */
.versus-box {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
    padding: 1.2rem 1.5rem !important;
}}
.versus-box h5 {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: {GOLD} !important;
    margin-bottom: 0.8rem !important;
    border-bottom: 1px solid {BORDER} !important;
    padding-bottom: 0.5rem !important;
}}

/* ── CRM PILL ────────────────────────────────────────────────────── */
.crm-pill {{
    display: inline-block !important;
    background: transparent !important;
    color: {GOLD} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    padding: 0.2rem 0.6rem !important;
    border: 1px solid {GOLD} !important;
    border-radius: 0 !important;
    text-transform: uppercase !important;
    margin-right: 0.4rem !important;
}}

/* ── PERSONAS ────────────────────────────────────────────────────── */
.persona-avatar {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    animation: personaFloat 3s ease-in-out infinite;
    margin: 0 auto 1rem;
}}
.persona-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s ease;
    animation: fadeInUp 0.6s ease forwards;
    position: relative;
    overflow: hidden;
}}
.persona-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--persona-color), transparent);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}}
.persona-card:hover::after {{
    transform: scaleX(1);
}}
.persona-card:hover {{
    border-color: var(--persona-color);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}}
.persona-name {{
    font-family: 'Jost', sans-serif;
    font-size: 1.1rem;
    font-style: italic;
    color: {TEXT};
    margin-bottom: 0.3rem;
}}
.persona-tag {{
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--persona-color);
}}

/* ── BUTTONS ─────────────────────────────────────────────────────── */
.stButton button {{
    background: transparent !important;
    border: 1px solid {GOLD} !important;
    color: {GOLD} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    transition: all 0.3s ease !important;
}}
.stButton button:hover {{
    background: {GOLD} !important;
    color: {BG} !important;
}}
.stButton button:active {{
    transform: scale(0.98) !important;
}}

/* ── TABLES & DATAFRAMES ─────────────────────────────────────────── */
.stDataFrame {{
    border: 1px solid {BORDER} !important;
}}
.stDataFrame thead th {{
    background: {SURFACE} !important;
    color: {MUTED} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid {GOLD} !important;
}}
.stDataFrame tbody tr:nth-child(even) {{
    background: {SURFACE2} !important;
}}
.stDataFrame tbody tr:nth-child(odd) {{
    background: {SURFACE} !important;
}}
.stDataFrame tbody tr:hover {{
    background: {SURFACE3} !important;
}}
.stDataFrame tbody td {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {TEXT} !important;
    border-color: {BORDER} !important;
    opacity: 0.9;
}}

/* ── SLIDERS ─────────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] {{
    padding: 0 !important;
}}
.stSlider [data-baseweb="thumb"] {{
    background: {GOLD} !important;
    border: none !important;
    width: 18px !important;
    height: 18px !important;
    border-radius: 0 !important;
}}
.stSlider [data-baseweb="track-background"] {{
    background: {BORDER} !important;
    height: 2px !important;
}}
.stSlider [data-baseweb="track-foreground"] {{
    background: {GOLD} !important;
}}
.stSlider label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    color: {MUTED} !important;
    text-transform: uppercase !important;
}}

/* ── SELECTBOX & INPUTS ──────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] {{
    background: {INPUT_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}}
.stSelectbox label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
}}
.stTextInput input {{
    background: {INPUT_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
    color: {TEXT} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}}
.stTextInput input:focus {{
    border-color: {GOLD} !important;
    box-shadow: 0 0 0 1px {GOLD} !important;
}}
.stTextInput label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
}}

/* ── STREAMLIT METRICS OVERRIDE ──────────────────────────────────── */
[data-testid="stMetricValue"] {{
    font-family: 'Jost', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 300 !important;
    color: {GOLD} !important;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
}}
div[data-testid="metric-container"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-top: 2px solid {GOLD} !important;
    border-radius: 0 !important;
    padding: 1rem 1.2rem !important;
}}
.stMetric {{
    background: {SURFACE} !important;
    border-radius: 0 !important;
    padding: 0.7rem !important;
}}

/* ── DIVIDERS ────────────────────────────────────────────────────── */
hr, .stDivider {{
    border-color: {BORDER} !important;
    opacity: 1 !important;
}}

/* ── EXPANDER ────────────────────────────────────────────────────── */
.streamlit-expanderHeader {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
}}
.streamlit-expanderContent {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-top: none !important;
    border-radius: 0 !important;
}}

/* ── INFO / WARNING / ERROR BOXES ────────────────────────────────── */
.stAlert {{
    background: {SURFACE} !important;
    border-radius: 0 !important;
    border: 1px solid {BORDER} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}}

/* ── SCROLLBAR ───────────────────────────────────────────────────── */
::-webkit-scrollbar {{
    width: 4px;
    height: 4px;
}}
::-webkit-scrollbar-track {{
    background: {SURFACE3};
}}
::-webkit-scrollbar-thumb {{
    background: {SCROLLTHUMB};
    border-radius: 0;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {GOLD};
}}

/* ── ANIMATIONS ──────────────────────────────────────────────────── */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes shimmerLine {{
    0%   {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}
@keyframes pulseGold {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(201,168,76,0.4); }}
    50%       {{ box-shadow: 0 0 0 8px rgba(201,168,76,0); }}
}}
@keyframes blinkRed {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0.5; }}
}}
@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-30px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes personaFloat {{
    0%, 100% {{ transform: translateY(0px); }}
    50%       {{ transform: translateY(-8px); }}
}}
@keyframes productReveal {{
    from {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
    to   {{ opacity: 1; clip-path: inset(0 0% 0 0); }}
}}
@keyframes glowPulse {{
    0%   {{ filter: drop-shadow(0 0 4px rgba(201,168,76,0.3)); }}
    50%  {{ filter: drop-shadow(0 0 12px rgba(201,168,76,0.7)); }}
    100% {{ filter: drop-shadow(0 0 4px rgba(201,168,76,0.3)); }}
}}

/* ── STAGGER ANIMATIONS ──────────────────────────────────────────── */
[data-testid="column"]:nth-child(1) .kpi-gold,
[data-testid="column"]:nth-child(1) .kpi-card {{
    animation-delay: 0.05s;
}}
[data-testid="column"]:nth-child(2) .kpi-gold,
[data-testid="column"]:nth-child(2) .kpi-card {{
    animation-delay: 0.1s;
}}
[data-testid="column"]:nth-child(3) .kpi-gold,
[data-testid="column"]:nth-child(3) .kpi-card {{
    animation-delay: 0.15s;
}}
[data-testid="column"]:nth-child(4) .kpi-gold,
[data-testid="column"]:nth-child(4) .kpi-card {{
    animation-delay: 0.2s;
}}

/* ── NOISE TEXTURE ───────────────────────────────────────────────── */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9998;
    opacity: {NOISE_OP};
}}

/* ── RADIO BUTTONS ───────────────────────────────────────────────── */
[data-testid="stRadio"] label {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
}}
[data-testid="stRadio"] label:hover {{
    color: {GOLD} !important;
}}

/* ── IMAGES ──────────────────────────────────────────────────────── */
[data-testid="stImage"] img {{
    border: 1px solid {BORDER} !important;
    animation: productReveal 0.8s ease forwards !important;
}}

/* ── LIGHT MODE — MAIN CONTENT ───────────────────────────────────── */
{"" if theme != "light" else """
.stApp { background: #F5F0EB !important; }
header[data-testid="stHeader"] {
    background: #F5F0EB !important;
    border-bottom: 1px solid #E0D8CC !important;
}
.main .block-container { background: transparent !important; }
h1, h2, h3, h4 { color: #0A0A0A !important; }

/* LIGHT — KPI cards */
.kpi-gold {
    background: #FFFFFF !important;
    border: 1px solid #E0D8CC !important;
    border-top: 2px solid #8B6914 !important;
}
.kpi-gold .kpi-value { color: #8B6914 !important; }
.kpi-gold .kpi-label { color: #888888 !important; }

/* LIGHT — metrics */
[data-testid="stMetricValue"] { color: #8B6914 !important; }
[data-testid="stMetricLabel"] { color: #555555 !important; }
div[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E0D8CC !important;
    border-top: 2px solid #8B6914 !important;
}

/* LIGHT — selectbox/input */
.stSelectbox [data-baseweb="select"] {
    background: #FFFFFF !important;
    border: 1px solid #E0D8CC !important;
    color: #0A0A0A !important;
}
.stTextInput input {
    background: #FFFFFF !important;
    border: 1px solid #E0D8CC !important;
    color: #0A0A0A !important;
}

/* LIGHT — dataframe */
.stDataFrame thead th {
    background: #F0EBE3 !important;
    color: #555555 !important;
    border-bottom: 1px solid #8B6914 !important;
}
.stDataFrame tbody tr:nth-child(even) { background: #FAF7F4 !important; }
.stDataFrame tbody tr:nth-child(odd)  { background: #FFFFFF !important; }
.stDataFrame tbody td { color: #0A0A0A !important; }

/* LIGHT — alerts */
.alert-danger  { background: #FFF0F0 !important; }
.alert-success { background: #F0FBF9 !important; }

/* LIGHT — sliders */
[data-baseweb="thumb"]            { background: #8B6914 !important; }
[data-baseweb="track-foreground"] { background: #8B6914 !important; }
"""}

/* ── LIGHT MODE — SIDEBAR RESTE SOMBRE ──────────────────────────── */
{"" if theme != "light" else """
[data-testid="stSidebar"] {
    background: #0A0A0A !important;
    border-right: 1px solid #1A1A1A !important;
}
[data-testid="stSidebar"] * {
    color: #F5F0EB !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #888888 !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #C9A84C !important;
}
[data-testid="stSidebar"] .stButton button {
    border-color: #C9A84C !important;
    color: #C9A84C !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #C9A84C !important;
    color: #000000 !important;
}
"""}
</style>
"""
