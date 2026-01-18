import streamlit as st
from streamlit_folium import st_folium
import folium


def valuation_ui():
    st.subheader("التقييم")

    activity = st.selectbox(
        "النشاط",
        ["تجاري", "صناعي", "صحي", "تعليمي"]
    )

    area = st.number_input(
        "المساحة (م²)",
        min_value=0.0,
        step=10.0
    )

    # خريطة
    m = folium.Map(location=[24.7, 46.7], zoom_start=6)
    st_folium(m, height=300)

    # تنفيذ التقييم
    if st.button("تنفيذ التقييم"):
        recommended_value = area * 50

        st.metric(
            "القيمة الإيجارية المقترحة",
            f"{recommended_value:,.0f} ريال"
        )

        st.write("درجة الثقة: 75% (عالية)")

        # ---- (اختياري لاحقًا) حفظ التقييم ----
        # payload = {
        #     "activity": activity,
        #     "area": area,
        #     "value": recommended_value
        # }
        # save_evaluation(payload, user)
