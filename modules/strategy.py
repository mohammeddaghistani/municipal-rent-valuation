import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from modules.db import SessionLocal, Deal
import numpy as np

def strategy_ui():
    st.subheader("التخطيط الاستراتيجي (داخلي)")
    st.caption("تحليلات مبنية على الصفقات التاريخية لدعم التخطيط والاستدامة.")

    db: Session = SessionLocal()
    try:
        rows = db.query(Deal).all()
        data = [{
            "activity": r.activity, "city": r.city, "year": r.year,
            "annual_rent": r.annual_rent, "area_m2": r.area_m2
        } for r in rows if r.area_m2 and r.area_m2 > 0 and r.annual_rent and r.annual_rent > 0]
    finally:
        db.close()

    if not data:
        st.info("أدخل صفقات كافية لعرض التحليلات.")
        return

    df = pd.DataFrame(data)
    df["rate_per_m2"] = df["annual_rent"] / df["area_m2"]

    # مؤشرات بسيطة
    grp = df.groupby("activity")["rate_per_m2"]
    summary = pd.DataFrame({
        "متوسط (ريال/م²)": grp.mean().round(2),
        "انحراف معياري": grp.std().fillna(0).round(2),
        "عدد الصفقات": grp.count()
    }).reset_index()

    # مؤشر استدامة بسيط: أعلى = عدد أكبر + تذبذب أقل
    summary["مؤشر الاستدامة (0-100)"] = (
        (summary["عدد الصفقات"] / summary["عدد الصفقات"].max()) * 60 +
        (1 - (summary["انحراف معياري"] / (summary["انحراف معياري"].max() + 1e-6))) * 40
    ).clip(0, 100).round(0)

    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.bar_chart(summary.set_index("activity")["مؤشر الاستدامة (0-100)"])
