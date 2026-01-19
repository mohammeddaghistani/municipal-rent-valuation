def valuation_ui(user=None):
    st.subheader("التقييم")
    activity = st.selectbox("النشاط", ["تجاري","صناعي","صحي","تعليمي"])
    area = st.number_input("المساحة", min_value=0.0)
    m = folium.Map(location=[24.7,46.7], zoom_start=6)
    st_folium(m, height=300)
    if st.button("تنفيذ التقييم"):
        st.metric("القيمة المقترحة", f"{area*50:,.0f} ريال")
        st.write("درجة الثقة: 75% (عالية)")
