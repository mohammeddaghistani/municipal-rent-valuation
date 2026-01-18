import streamlit as st
from modules.db import init_db
from modules.auth import login_required
from modules.dashboard import render_dashboard

def main():
    st.set_page_config(page_title="نظام دعم قرار التقييم الإيجاري", page_icon="📌", layout="wide")
    init_db()
    user = login_required()
    render_dashboard(user)

if __name__ == "__main__":
    main()
