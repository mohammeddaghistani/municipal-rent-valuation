import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.db import SessionLocal, Evaluation
from modules.reports import generate_pdf
from modules.auth import require_role

def reports_ui(user):
    require_role(["admin", "committee", "valuer"])

    st.subheader("التقارير (PDF)")

    db: Session = SessionLocal()
    try:
        rows = db.query(Evaluation).order_by(Evaluation.id.desc()).limit(50).all()
        data = [{
            "id": r.id, "activity": r.activity, "city": r.city, "district": r.district,
            "recommended": r.recommended_annual_rent,
            "confidence": f"{r.confidence_pct:.0f}% ({r.confidence_label})",
            "created_at": r.created_at,
            "created_by": r.created_by
        } for r in rows]
    finally:
        db.close()

    if not data:
        st.info("لا توجد تقييمات محفوظة بعد.")
        return

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    sel = st.selectbox("اختر تقييمًا لتوليد تقرير", df["id"].tolist(), key="rep_select_eval")
    if st.button("توليد PDF", type="primary", key="rep_gen_pdf"):
        db: Session = SessionLocal()
        try:
            r = db.query(Evaluation).filter(Evaluation.id == int(sel)).first()
        finally:
            db.close()

        if not r:
            st.error("لم يتم العثور على التقييم")
            return

        report_data = {
            "رقم التقييم": r.id,
            "النشاط": r.activity,
            "المدينة": r.city or "",
            "الحي": r.district or "",
            "المساحة (م²)": f"{r.area_m2:,.2f}",
            "الأسلوب المستخدم": r.method_used,
            "القيمة المقترحة (سنوي)": f"{r.recommended_annual_rent:,.0f} ريال",
            "النطاق": f"{r.min_annual_rent:,.0f} – {r.max_annual_rent:,.0f} ريال",
            "درجة الثقة": f"{r.confidence_pct:.0f}% ({r.confidence_label})",
            "التبرير": r.explanation or "",
            "المقيم/المستخدم": r.created_by or "",
            "التاريخ": r.created_at
        }
        pdf_bytes = generate_pdf(report_data)
        st.download_button("تحميل التقرير PDF", data=pdf_bytes, file_name=f"evaluation_{r.id}.pdf", mime="application/pdf", key="rep_dl")
