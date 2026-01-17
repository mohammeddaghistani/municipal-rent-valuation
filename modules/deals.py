import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session

from modules.auth import require_role
from modules.db import SessionLocal, Deal
from modules.maps import build_map
from modules.utils import now_iso
from streamlit_folium import st_folium

ACTIVITIES = [
    "تجاري","صناعي","صحي","تعليمي","رياضي وترفيهي","سياحي","زراعي وحيواني","بيئي",
    "اجتماعي","نقل","مركبات","صيانة وتعليم وتركيب","تشييد وإدارة عقارات",
    "خدمات عامة","ملبوسات ومنسوجات","مرافق عامة","مالي","حدائق عامة"
]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Accept Arabic/English columns
    col_map = {
        "activity": "activity",
        "النشاط": "activity",
        "city": "city",
        "المدينة": "city",
        "district": "district",
        "الحي": "district",
        "area_m2": "area_m2",
        "المساحة": "area_m2",
        "المساحة (م2)": "area_m2",
        "annual_rent": "annual_rent",
        "الإيجار": "annual_rent",
        "الإيجار السنوي": "annual_rent",
        "year": "year",
        "السنة": "year",
        "lat": "lat",
        "longitude": "lon",
        "lon": "lon",
        "خط العرض": "lat",
        "خط الطول": "lon",
        "notes": "notes",
        "ملاحظات": "notes",
    }

    df = df.copy()
    new_cols = {}
    for c in df.columns:
        cc = str(c).strip()
        new_cols[c] = col_map.get(cc, cc)
    df = df.rename(columns=new_cols)
    return df


def _import_excel(file) -> tuple[int, list[str]]:
    df = pd.read_excel(file)
    df = _normalize_columns(df)

    required = {"activity", "area_m2", "annual_rent", "year"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        return 0, [f"عمود مفقود: {m}" for m in missing]

    inserted = 0
    errors = []
    db: Session = SessionLocal()
    try:
        for i, r in df.iterrows():
            try:
                activity = str(r.get("activity", "")).strip()
                if not activity:
                    continue
                db.add(
                    Deal(
                        activity=activity,
                        city=(str(r.get("city", "")).strip() or None),
                        district=(str(r.get("district", "")).strip() or None),
                        lat=(float(r.get("lat")) if pd.notna(r.get("lat")) else None),
                        lon=(float(r.get("lon")) if pd.notna(r.get("lon")) else None),
                        area_m2=float(r.get("area_m2") or 0.0),
                        annual_rent=float(r.get("annual_rent") or 0.0),
                        year=int(r.get("year") or 2024),
                        notes=(str(r.get("notes", "")).strip() or None),
                        created_at=now_iso(),
                        updated_at=now_iso(),
                    )
                )
                inserted += 1
            except Exception as e:
                errors.append(f"صف {i+2}: {e}")
        db.commit()
    finally:
        db.close()

    return inserted, errors


def deals_ui():
    require_role(["admin", "data_entry", "committee", "valuer"])

    st.subheader("الصفقات المرجعية")

    with st.expander("استيراد صفقات من ملف Excel", expanded=False):
        st.caption("يدعم أعمدة: activity/النشاط, city/المدينة, district/الحي, area_m2/المساحة, annual_rent/الإيجار السنوي, year/السنة, lat, lon, notes")
        up = st.file_uploader("رفع ملف Excel", type=["xlsx"], key="deals_import_xlsx")
        if up is not None:
            if st.button("استيراد", type="primary", key="deals_import_btn"):
                n, errs = _import_excel(up)
                if errs:
                    st.warning("تم الاستيراد مع ملاحظات:")
                    st.write(errs[:20])
                st.success(f"تم إدخال {n} صفقة")
                st.rerun()

    with st.expander("إضافة صفقة جديدة", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            activity = st.selectbox("النشاط", ACTIVITIES, key="deal_add_activity")
            city = st.text_input("المدينة", key="deal_add_city")
            district = st.text_input("الحي", key="deal_add_district")
        with c2:
            area_m2 = st.number_input("المساحة (م²)", min_value=0.0, key="deal_add_area")
            annual_rent = st.number_input("الإيجار السنوي (ريال)", min_value=0.0, key="deal_add_rent")
            year = st.number_input("سنة الصفقة", min_value=2000, max_value=2100, value=2024, key="deal_add_year")
        with c3:
            lat = st.number_input("خط العرض (اختياري)", value=0.0, format="%.6f", key="deal_add_lat")
            lon = st.number_input("خط الطول (اختياري)", value=0.0, format="%.6f", key="deal_add_lon")
            notes = st.text_input("ملاحظات", key="deal_add_notes")

        if st.button("حفظ الصفقة", type="primary", key="deal_add_save"):
            db: Session = SessionLocal()
            try:
                db.add(
                    Deal(
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
                    )
                )
                db.commit()
                st.success("تم حفظ الصفقة")
                st.rerun()
            finally:
                db.close()

    st.divider()
    st.caption("ملاحظة: يمكنك إدخال صفقات بقيم 0 لاحقًا، ثم تعديلها عند توفر البيانات.")

    db: Session = SessionLocal()
    try:
        rows = db.query(Deal).order_by(Deal.year.desc(), Deal.id.desc()).all()
        data = [
            {
                "id": r.id,
                "activity": r.activity,
                "city": r.city,
                "district": r.district,
                "area_m2": r.area_m2,
                "annual_rent": r.annual_rent,
                "year": r.year,
                "lat": r.lat,
                "lon": r.lon,
                "notes": r.notes,
            }
            for r in rows
        ]
    finally:
        db.close()

    if not data:
        st.info("لا توجد صفقات بعد.")
        return

    df = pd.DataFrame(data)

    # Map (read-only) showing all deals with coordinates
    with st.expander("خريطة الصفقات (عرض فقط)", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            f_activity = st.selectbox("تصفية بالنشاط", ["الكل"] + ACTIVITIES, key="deals_map_activity")
        with f2:
            f_city = st.text_input("تصفية بالمدينة (اختياري)", key="deals_map_city")

        view_df = df.copy()
        if f_activity != "الكل":
            view_df = view_df[view_df["activity"] == f_activity]
        if f_city.strip():
            view_df = view_df[view_df["city"].fillna("") == f_city.strip()]

        pts = view_df.dropna(subset=["lat", "lon"]).to_dict(orient="records")
        m = build_map(24.7136, 46.6753, 6, clicked=None, deal_points=pts)
        st_folium(m, height=420, key="deals_map")
        st.caption("الخريطة للعرض فقط، ويتم إظهار قيم الصفقات (الإيجار/المساحة/السنة) عند تمرير المؤشر على النقاط.")

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("تعديل/حذف صفقة")
    selected_id = st.selectbox("اختر رقم الصفقة", df["id"].tolist(), key="deal_edit_select_id")
    row = df[df["id"] == selected_id].iloc[0].to_dict()

    e1, e2, e3 = st.columns(3)
    with e1:
        e_activity = st.selectbox("النشاط", ACTIVITIES, index=max(0, ACTIVITIES.index(row["activity"]) if row["activity"] in ACTIVITIES else 0), key="deal_edit_activity")
        e_city = st.text_input("المدينة", value=row["city"] or "", key="deal_edit_city")
        e_district = st.text_input("الحي", value=row["district"] or "", key="deal_edit_district")
    with e2:
        e_area = st.number_input("المساحة (م²)", min_value=0.0, value=float(row["area_m2"] or 0.0), key="deal_edit_area")
        e_rent = st.number_input("الإيجار السنوي (ريال)", min_value=0.0, value=float(row["annual_rent"] or 0.0), key="deal_edit_rent")
        e_year = st.number_input("سنة الصفقة", min_value=2000, max_value=2100, value=int(row["year"] or 2024), key="deal_edit_year")
    with e3:
        e_lat = st.number_input("خط العرض", value=float(row["lat"] or 0.0), format="%.6f", key="deal_edit_lat")
        e_lon = st.number_input("خط الطول", value=float(row["lon"] or 0.0), format="%.6f", key="deal_edit_lon")
        e_notes = st.text_input("ملاحظات", value=row["notes"] or "", key="deal_edit_notes")

    c_upd, c_del = st.columns(2)
    with c_upd:
        if st.button("تحديث الصفقة", key="deal_edit_update"):
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
        if st.button("حذف الصفقة", type="secondary", key="deal_edit_delete"):
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
