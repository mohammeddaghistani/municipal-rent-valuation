import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.db import SessionLocal, Deal
from modules.auth import require_role
from modules.utils import now_iso

def deals_ui():
    require_role(["admin", "data_entry", "committee", "valuer"])

    st.subheader("الصفقات المرجعية (CRUD)")

    with st.expander("إضافة صفقة جديدة", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            activity = st.selectbox("النشاط", [
                "تجاري","صناعي","صحي","تعليمي","رياضي وترفيهي","سياحي","زراعي وحيواني","بيئي",
                "اجتماعي","نقل","مركبات","صيانة وتعليم وتركيب","تشييد وإدارة عقارات",
                "خدمات عامة","ملبوسات ومنسوجات","مرافق عامة","مالي"
            ])
            city = st.text_input("المدينة", key="deal_city")
            district = st.text_input("الحي", key="deal_district")
        with c2:
            area_m2 = st.number_input("المساحة (م²)", min_value=0.0, key="deal_area")
            annual_rent = st.number_input("الإيجار السنوي (ريال)", min_value=0.0, key="deal_rent")
            year = st.number_input("سنة الصفقة", min_value=2000, max_value=2100, value=2024, key="deal_year")
        with c3:
            lat = st.number_input("خط العرض (اختياري)", value=0.0, format="%.6f", key="deal_lat")
            lon = st.number_input("خط الطول (اختياري)", value=0.0, format="%.6f", key="deal_lon")
            notes = st.text_input("ملاحظات", key="deal_notes")

        if st.button("حفظ الصفقة", type="primary"):
            db: Session = SessionLocal()
            try:
                db.add(Deal(
                    activity=activity,
                    city=city or None,
                    district=district or None,
                    lat=(lat if abs(lat) > 0 else None),
                    lon=(lon if abs(lon) > 0 else None),
                    area_m2=area_m2,
                    annual_rent=annual_rent,
                    year=int(year),
                    notes=notes or None,
                    created_at=now_iso(),
                    updated_at=now_iso(),
                ))
                db.commit()
                st.success("تم حفظ الصفقة")
                st.rerun()
            finally:
                db.close()

    st.divider()
    st.caption("ملاحظة: يمكنك إدخال صفقات بقيم 0 لاحقًا، ولكن يفضّل تركها 0 فقط عند الحاجة ثم تعديلها لاحقًا.")

    db: Session = SessionLocal()
    try:
        rows = db.query(Deal).order_by(Deal.year.desc(), Deal.id.desc()).all()
        data = [{
            "id": r.id, "activity": r.activity, "city": r.city, "district": r.district,
            "area_m2": r.area_m2, "annual_rent": r.annual_rent, "year": r.year,
            "lat": r.lat, "lon": r.lon, "notes": r.notes
        } for r in rows]
    finally:
        db.close()

    if not data:
        st.info("لا توجد صفقات بعد.")
        return

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("تعديل/حذف صفقة")
    selected_id = st.selectbox("اختر رقم الصفقة", df["id"].tolist())
    row = df[df["id"] == selected_id].iloc[0].to_dict()

    e1, e2, e3 = st.columns(3)
    with e1:
        e_activity = st.text_input("النشاط", value=row["activity"])
        e_city = st.text_input("المدينة", value=row["city"] or "")
        e_district = st.text_input("الحي", value=row["district"] or "")
    with e2:
        e_area = st.number_input("المساحة (م²)", min_value=0.0, value=float(row["area_m2"] or 0.0))
        e_rent = st.number_input("الإيجار السنوي (ريال)", min_value=0.0, value=float(row["annual_rent"] or 0.0))
        e_year = st.number_input("سنة الصفقة", min_value=2000, max_value=2100, value=int(row["year"] or 2024))
    with e3:
        e_lat = st.number_input("خط العرض", value=float(row["lat"] or 0.0), format="%.6f")
        e_lon = st.number_input("خط الطول", value=float(row["lon"] or 0.0), format="%.6f")
        e_notes = st.text_input("ملاحظات", value=row["notes"] or "")

    c_upd, c_del = st.columns(2)
    with c_upd:
        if st.button("تحديث الصفقة"):
            db: Session = SessionLocal()
            try:
                d = db.query(Deal).filter(Deal.id == int(selected_id)).first()
                if d:
                    d.activity = e_activity
                    d.city = e_city or None
                    d.district = e_district or None
                    d.area_m2 = float(e_area)
                    d.annual_rent = float(e_rent)
                    d.year = int(e_year)
                    d.lat = (float(e_lat) if abs(float(e_lat)) > 0 else None)
                    d.lon = (float(e_lon) if abs(float(e_lon)) > 0 else None)
                    d.notes = e_notes or None
                    d.updated_at = now_iso()
                    db.commit()
                    st.success("تم التحديث")
                    st.rerun()
            finally:
                db.close()

    with c_del:
        require_role(["admin"])
        if st.button("حذف الصفقة", type="secondary"):
            db: Session = SessionLocal()
            try:
                d = db.query(Deal).filter(Deal.id == int(selected_id)).first()
                if d:
                    db.delete(d)
                    db.commit()
                    st.success("تم الحذف")
                    st.rerun()
            finally:
                db.close()
