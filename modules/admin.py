import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.db import SessionLocal, User
from modules.auth import require_role
import hashlib

def _hash(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def admin_ui():
    require_role(["admin"])
    st.subheader("إدارة المستخدمين (Admin)")

    with st.expander("إضافة مستخدم", expanded=True):
        u = st.text_input("اسم المستخدم الجديد")
        pw = st.text_input("كلمة المرور", type="password")
        role = st.selectbox("الدور", ["admin","committee","valuer","data_entry"])
        if st.button("إنشاء المستخدم", type="primary"):
            if not u or not pw:
                st.warning("الرجاء إدخال اسم المستخدم وكلمة المرور")
            else:
                db: Session = SessionLocal()
                try:
                    exists = db.query(User).filter(User.username == u).first()
                    if exists:
                        st.error("اسم المستخدم موجود مسبقًا")
                    else:
                        db.add(User(username=u, password_hash=_hash(pw), role=role, is_active=True))
                        db.commit()
                        st.success("تم إنشاء المستخدم")
                        st.rerun()
                finally:
                    db.close()

    db: Session = SessionLocal()
    try:
        users = db.query(User).order_by(User.id.desc()).all()
        data = [{"id": x.id, "username": x.username, "role": x.role, "is_active": x.is_active} for x in users]
    finally:
        db.close()

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("تفعيل/تعطيل مستخدم")
        sel = st.selectbox("اختر المستخدم", df["username"].tolist())
        col1, col2 = st.columns(2)
        with col1:
            if st.button("تعطيل"):
                db: Session = SessionLocal()
                try:
                    x = db.query(User).filter(User.username == sel).first()
                    if x and x.username != st.secrets.get("ADMIN_USERNAME", "admin"):
                        x.is_active = False
                        db.commit()
                        st.success("تم التعطيل")
                        st.rerun()
                finally:
                    db.close()
        with col2:
            if st.button("تفعيل"):
                db: Session = SessionLocal()
                try:
                    x = db.query(User).filter(User.username == sel).first()
                    if x:
                        x.is_active = True
                        db.commit()
                        st.success("تم التفعيل")
                        st.rerun()
                finally:
                    db.close()
