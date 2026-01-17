import streamlit as st

from modules.admin import admin_ui
from modules.deals import deals_ui
from modules.reports_ui import reports_ui
from modules.strategy import strategy_ui
from modules.style import apply_branding, render_footer
from modules.valuation_ui import valuation_ui


def render_dashboard(user):
    logo = apply_branding("تقدير القيمة الإيجارية للعقارات الاستثمارية")

    top = st.columns([1, 6, 2])
    with top[0]:
        if logo:
            st.image(str(logo), width=86)
    with top[1]:
        st.markdown("# تقدير القيمة الإيجارية للعقارات الاستثمارية")
        st.caption(f"مستخدم: {user.get('username')} | الدور: {user.get('role')} | للاستخدام الداخلي")
    with top[2]:
        if st.button("تسجيل خروج", key="logout_btn"):
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

    render_footer()
