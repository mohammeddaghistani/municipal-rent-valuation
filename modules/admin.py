import hashlib

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from modules.auth import require_role
from modules.db import AppSettings, SessionLocal, User, get_settings
from modules.utils import now_iso


def _hash(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def _settings_ui():
    st.subheader("إعدادات التقييم (Admin)")
    s = get_settings()

    with st.expander("معايير عامة", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            yield_rate_pct = st.number_input("نسبة العائد (%)", min_value=0.1, max_value=50.0, value=float(s.yield_rate_pct), step=0.1, key="set_yield")
        with c2:
            grace_period_years = st.number_input("فترة السماح (بالسنوات)", min_value=0.0, max_value=10.0, value=float(s.grace_period_years), step=0.5, key="set_grace")
        with c3:
            rent_to_sale_pct = st.number_input("نسبة الإيجار من قيمة البيع (%)", min_value=0.0, max_value=100.0, value=float(s.rent_to_sale_pct), step=0.1, key="set_rent_to_sale")

        if st.button("حفظ الإعدادات", type="primary", key="settings_save"):
            db: Session = SessionLocal()
            try:
                row = db.query(AppSettings).filter(AppSettings.id == 1).first()
                row.yield_rate_pct = float(yield_rate_pct)
                row.grace_period_years = float(grace_period_years)
                row.rent_to_sale_pct = float(rent_to_sale_pct)
                row.updated_at = now_iso()
                db.commit()
                st.success("تم حفظ الإعدادات")
                st.rerun()
            finally:
                db.close()


def admin_ui():
    require_role(["admin"])

    tabs = st.tabs(["المستخدمون", "إعدادات التقييم"])

    with tabs[0]:
        st.subheader("إدارة المستخدمين")

        with st.expander("إضافة مستخدم", expanded=True):
            u = st.text_input("اسم المستخدم الجديد", key="admin_add_user")
            pw = st.text_input("كلمة المرور", type="password", key="admin_add_pw")
            role = st.selectbox("الدور", ["admin", "committee", "valuer", "data_entry"], key="admin_add_role")
            if st.button("إنشاء المستخدم", type="primary", key="admin_create_user"):
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
            sel = st.selectbox("اختر المستخدم", df["username"].tolist(), key="admin_select_user")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("تعطيل", key="admin_disable"):
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
                if st.button("تفعيل", key="admin_enable"):
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
        else:
            st.info("لا يوجد مستخدمون بعد.")

    with tabs[1]:
        _settings_ui()
