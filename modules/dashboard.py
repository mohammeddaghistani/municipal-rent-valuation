import streamlit as st
from modules.style import apply_rtl_and_branding
from modules.deals import deals_ui
from modules.strategy import strategy_ui
from modules.admin import admin_ui
from modules.valuation_ui import valuation_ui
from modules.reports_ui import reports_ui

def render_dashboard(user):
    logo = apply_rtl_and_branding()

    header_cols = st.columns([1, 5, 2])
    with header_cols[0]:
        if logo:
            st.image(str(logo), width=80)
    with header_cols[1]:
        st.markdown("## نظام دعم قرار التقييم الإيجاري")
        st.caption(f"مستخدم: {user.get('username')} | الدور: {user.get('role')}")
    with header_cols[2]:
        if st.button("تسجيل خروج"):
            st.session_state.pop("user", None)
            st.rerun()

    tabs = st.tabs(["التقييم", "الصفقات", "التقارير", "الاستراتيجية", "الإدارة"])

    with tabs[0]:
        valuation_ui(user)
    with tabs[1]:
        deals_ui()
    with tabs[2]:
        reports_ui(user)
    with tabs[3]:
        strategy_ui()
    with tabs[4]:
        if user.get("role") == "admin":
            admin_ui()
        else:
            st.info("صفحة الإدارة متاحة للمدير فقط.")
