
import streamlit as st

def login_required():
    if "user" not in st.session_state:
        st.session_state.user = {"role": "admin", "name": "Internal User"}
    return st.session_state.user
