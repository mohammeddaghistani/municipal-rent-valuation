import hashlib

import streamlit as st
from sqlalchemy.orm import Session

from modules.db import init_db, SessionLocal, User, ensure_settings
from modules.style import apply_branding, render_footer


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def ensure_admin():
    init_db()
    ensure_settings()
    admin_user = st.secrets.get("ADMIN_USERNAME", "admin")
    admin_pass = st.secrets.get("ADMIN_PASSWORD", "admin")
    db: Session = SessionLocal()
    try:
        u = db.query(User).filter(User.username == admin_user).first()
        if not u:
            db.add(User(username=admin_user, password_hash=_hash_password(admin_pass), role="admin", is_active=True))
            db.commit()
    finally:
        db.close()


def login_required():
    ensure_admin()
    if "user" in st.session_state and st.session_state.user.get("username"):
        return st.session_state.user

    apply_branding("تقدير القيمة الإيجارية للعقارات الاستثمارية")

    st.markdown(
        """
        <div class="login-hero">
          <div class="login-badge">نظام داخلي لدعم قرارات اللجان والتقدير</div>
          <div style="display:flex; align-items:center; gap:14px; margin-top:14px;">
            <div class="brand-mark"></div>
            <div>
              <div style="font-size:1.55rem; font-weight:800; color:var(--text);">تقدير القيمة الإيجارية للعقارات الاستثمارية</div>
              <div style="margin-top:4px; color:var(--muted);">سجّل الدخول للمتابعة</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    with st.form("login_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("اسم المستخدم", key="login_username")
        with c2:
            password = st.text_input("كلمة المرور", type="password", key="login_password")
        submit = st.form_submit_button("دخول", type="primary")

    if submit:
        db: Session = SessionLocal()
        try:
            u = db.query(User).filter(User.username == username, User.is_active == True).first()
            if not u or u.password_hash != _hash_password(password):
                st.error("بيانات الدخول غير صحيحة")
            else:
                st.session_state.user = {"username": u.username, "role": u.role}
                st.success("تم تسجيل الدخول")
                st.rerun()
        finally:
            db.close()

    render_footer()
    st.stop()


def require_role(allowed_roles):
    user = st.session_state.get("user", {})
    if user.get("role") not in allowed_roles:
        st.error("ليس لديك صلاحية للوصول إلى هذه الصفحة")
        st.stop()
