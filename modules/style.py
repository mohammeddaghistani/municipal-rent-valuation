import base64
from pathlib import Path
from typing import Optional

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def apply_branding(page_title: str = "تقدير القيمة الإيجارية للعقارات الاستثمارية") -> Optional[Path]:
    """Apply RTL + modern brand UI and set page config safely."""

    # Derived roughly from logo palette (gold + green)
    primary = "#A88040"  # gold
    accent = "#4F9A4C"   # green
    bg = "#F7F5F0"       # warm off-white
    card = "#FFFFFF"
    text = "#1F2937"     # slate
    muted = "#6B7280"

    # Set page config once
    if "__page_config_set" not in st.session_state:
        st.set_page_config(
            page_title=page_title,
            page_icon="🧭",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
        st.session_state["__page_config_set"] = True

    logo = ASSETS_DIR / "logo.png"
    font = ASSETS_DIR / "Tajawal-Regular.ttf"

    font_css = ""
    if font.exists():
        # Inline font as base64 to avoid path issues on Streamlit Cloud
        font_b64 = _b64(font)
        font_css = f"""
        @font-face {{
            font-family: 'Tajawal';
            src: url(data:font/ttf;base64,{font_b64}) format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        """

    logo_css = ""
    if logo.exists():
        # Use the logo in login header background subtly
        try:
            logo_b64 = _b64(logo)
            logo_css = f"background-image: url('data:image/png;base64,{logo_b64}');"
        except Exception:
            logo_css = ""

    css = f"""
    <style>
      :root {{
        --primary: {primary};
        --accent: {accent};
        --bg: {bg};
        --card: {card};
        --text: {text};
        --muted: {muted};
        --radius: 18px;
      }}

      {font_css}

      html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
        direction: rtl;
        font-family: 'Tajawal', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        background: var(--bg);
        color: var(--text);
      }}

      /* Center content and keep it comfortable on mobile */
      .block-container {{
        max-width: 1180px;
        padding-top: 1.3rem;
        padding-bottom: 2.5rem;
      }}

      /* Hide Streamlit default header/footer */
      header[data-testid="stHeader"] {{ display: none; }}
      footer {{ visibility: hidden; }}

      /* Cards */
      .md-card {{
        background: var(--card);
        border-radius: var(--radius);
        border: 1px solid rgba(31,41,55,0.08);
        box-shadow: 0 6px 30px rgba(15,23,42,0.06);
        padding: 1.1rem 1.2rem;
      }}

      /* Buttons */
      .stButton > button {{
        border-radius: 14px !important;
        padding: 0.55rem 1.0rem !important;
        border: 1px solid rgba(31,41,55,0.12) !important;
      }}
      .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
        color: white !important;
        border: none !important;
      }}

      /* Inputs */
      .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 14px !important;
      }}

      /* Tabs styling */
      .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background: transparent;
        border-bottom: 1px solid rgba(31,41,55,0.12);
        padding-bottom: 6px;
      }}
      .stTabs [data-baseweb="tab"] {{
        padding: 10px 14px;
        border-radius: 14px;
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(31,41,55,0.08);
      }}
      .stTabs [aria-selected="true"] {{
        background: rgba(168,128,64,0.12);
        border: 1px solid rgba(168,128,64,0.35);
        color: var(--text);
      }}

      /* Login hero */
      .login-hero {{
        border-radius: 24px;
        padding: 26px 24px;
        border: 1px solid rgba(31,41,55,0.10);
        background: radial-gradient(1200px 400px at 10% 0%, rgba(168,128,64,0.18), transparent 55%),
                    radial-gradient(900px 380px at 90% 0%, rgba(79,154,76,0.16), transparent 55%),
                    rgba(255,255,255,0.75);
        box-shadow: 0 10px 40px rgba(15,23,42,0.08);
      }}
      .login-badge {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        color: var(--muted);
        background: rgba(31,41,55,0.04);
        border: 1px solid rgba(31,41,55,0.08);
      }}

      .brand-mark {{
        width: 82px;
        height: 82px;
        border-radius: 18px;
        background-size: cover;
        background-position: center;
        {logo_css}
        border: 1px solid rgba(31,41,55,0.08);
        box-shadow: 0 8px 26px rgba(15,23,42,0.08);
      }}

      /* Footer */
      .md-footer {{
        margin-top: 22px;
        padding-top: 14px;
        border-top: 1px solid rgba(31,41,55,0.10);
        color: var(--muted);
        font-size: 0.90rem;
      }}

      /* Better spacing on very small screens */
      @media (max-width: 640px) {{
        .block-container {{ padding-left: 0.9rem; padding-right: 0.9rem; }}
        .stTabs [data-baseweb="tab"] {{ padding: 8px 10px; }}
      }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
    return logo if logo.exists() else None


def card_open() -> None:
    st.markdown('<div class="md-card">', unsafe_allow_html=True)


def card_close() -> None:
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer(owner: str = "محمد داغستاني", year: str = "2026", initiative: str = "مبادرة تطوير الأعمال بإشراف ودعم أ.عبدالرحمن خجا") -> None:
    st.markdown(
        f"""
        <div class="md-footer">
          <div>© {owner} {year} — {initiative}</div>
          <div>للاستخدام الداخلي فقط</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
