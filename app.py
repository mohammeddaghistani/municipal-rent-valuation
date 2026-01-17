
# Production App Entry
import streamlit as st
from modules.auth import login_required
from modules.dashboard import render_dashboard

st.set_page_config(page_title="نظام دعم قرار التقييم الإيجاري", layout="wide")

user = login_required()
render_dashboard(user)
