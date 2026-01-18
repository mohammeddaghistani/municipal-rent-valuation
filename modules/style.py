import streamlit as st
from pathlib import Path

def apply_rtl_and_branding():
    # Tajawal + RTL (إذا كانت الملفات موجودة في assets)
    tajawal = Path("assets/Tajawal-Regular.ttf")
    logo = Path("assets/logo.png")

    css = """
    <style>
      html, body, [class*="css"] { direction: rtl; }
      .block-container { padding-top: 1.2rem; }
    </style>
    """

    if tajawal.exists():
        css += f"""
        <style>
        @font-face {{
            font-family: 'Tajawal';
            src: url('{tajawal.as_posix()}');
        }}
        html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; }}
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)

    return logo if logo.exists() else None
