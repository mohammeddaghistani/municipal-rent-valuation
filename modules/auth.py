import streamlit as st
import hashlib
from sqlalchemy.orm import Session
from modules.db import init_db, SessionLocal, User

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def ensure_admin():
    init_db()
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

    st.title("تسجيل الدخول")
    st.caption("استخدام داخلي – الرجاء إدخال بيانات الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    login = st.button("دخول")

    if login:
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

    st.stop()

def require_role(allowed_roles):
    user = st.session_state.get("user", {})
    if user.get("role") not in allowed_roles:
        st.error("ليس لديك صلاحية للوصول إلى هذه الصفحة")
        st.stop()
