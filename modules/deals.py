
import streamlit as st

def deals_ui():
    st.subheader("الصفقات المرجعية")
    st.number_input("قيمة الصفقة")
    st.number_input("السنة")
    st.button("حفظ")
