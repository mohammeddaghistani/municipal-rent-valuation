
import streamlit as st
from modules.valuation import valuation_ui
from modules.deals import deals_ui
from modules.reports import reports_ui

def render_dashboard(user):
    st.title("نظام دعم قرار التقييم الإيجاري")
    tab1, tab2, tab3 = st.tabs(["التقييم", "الصفقات", "التقارير"])
    with tab1:
        valuation_ui()
    with tab2:
        deals_ui()
    with tab3:
        reports_ui()
