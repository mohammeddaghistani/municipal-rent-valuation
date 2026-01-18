import streamlit as st

# يجب أن يكون هذا أول نداء لـ Streamlit بعد الاستيراد مباشرة
st.set_page_config(
    page_title="تقدير القيمة الإيجارية للعقارات الاستثمارية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.db import init_db
from modules.auth import login_required
from modules.dashboard import render_dashboard


def main():
    init_db()
    user = login_required()
    render_dashboard(user)


if __name__ == "__main__":
    main()
