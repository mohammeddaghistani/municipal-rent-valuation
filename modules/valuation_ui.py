import streamlit as st
from streamlit_folium import st_folium

from modules.auth import require_role
from modules.croquis import save_croquis
from modules.db import SessionLocal, Deal
from modules.evaluation import (
    DEFAULT_RATE_PER_M2,
    apply_grace_period,
    compute_confidence,
    compute_from_deals,
    fallback_from_default,
    profits_method_from_sales,
    recommend_method,
    save_evaluation,
)
from modules.maps import build_map


ACTIVITIES = [
    "تجاري",
    "صناعي",
    "صحي",
    "تعليمي",
    "رياضي وترفيهي",
    "سياحي",
    "زراعي وحيواني",
    "بيئي",
    "اجتماعي",
    "نقل",
    "مركبات",
    "صيانة وتعليم وتركيب",
    "تشييد وإدارة عقارات",
    "خدمات عامة",
    "ملبوسات ومنسوجات",
    "مرافق عامة",
    "مالي",
    "حدائق عامة",
]


def _nearby_deals(lat, lon, radius_km=15, limit=200):
    if lat is None or lon is None:
        return []
    db = SessionLocal()
    try:
        rows = db.query(Deal).filter(Deal.lat != None, Deal.lon != None).all()
    finally:
        db.close()

    pts = []
    # Compute distance in python to keep sqlite simple
    from modules.utils import haversine_km

    for d in rows:
        try:
            dist = haversine_km(lat, lon, float(d.lat), float(d.lon))
        except Exception:
            continue
        if dist <= radius_km:
            pts.append(
                {
                    "id": d.id,
                    "activity": d.activity,
                    "city": d.city,
                    "district": d.district,
                    "lat": d.lat,
                    "lon": d.lon,
                    "area_m2": d.area_m2,
                    "annual_rent": d.annual_rent,
                    "year": d.year,
                    "dist_km": dist,
                    "notes": d.notes,
                }
            )

    pts.sort(key=lambda x: x["dist_km"])
    return pts[:limit]


def valuation_ui(user):
    require_role(["admin", "committee", "valuer", "data_entry"])

    st.subheader("التقييم")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        activity = st.selectbox("النشاط", ACTIVITIES, key="eval_activity")
    with c2:
        city = st.text_input("المدينة", key="eval_city")
    with c3:
        district = st.text_input("الحي", key="eval_district")
    with c4:
        contract_years = st.number_input("مدة العقد (سنة)", min_value=1, value=10, key="eval_contract_years")

    area_m2 = st.number_input("المساحة (م²)", min_value=0.0, value=0.0, key="eval_area")

    # Special inputs for public parks (profits method)
    annual_sales = None
    if activity == "حدائق عامة":
        st.info("للحدائق العامة: يتم استخدام **طريقة الأرباح** (مبسطة) كنسبة من قيمة البيع/المبيعات السنوية، وفق ما ورد في الدليل.")
        annual_sales = st.number_input(
            "قيمة البيع/المبيعات السنوية التقديرية (ريال)",
            min_value=0.0,
            value=0.0,
            key="parks_sales",
        )

    st.markdown("### تحديد الموقع")
    if "clicked" not in st.session_state:
        st.session_state.clicked = None

    clicked = st.session_state.clicked
    center_lat, center_lon, zoom = 24.7136, 46.6753, 6

    # nearby deals markers (read-only)
    deal_points = []
    if clicked:
        deal_points = _nearby_deals(clicked[0], clicked[1], radius_km=20)

    m = build_map(center_lat, center_lon, zoom, clicked=clicked, deal_points=deal_points)
    map_data = st_folium(m, height=420, width=None, key="eval_map")

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.session_state.clicked = (lat, lon)
        clicked = st.session_state.clicked
        st.success(f"تم اختيار الموقع: خط العرض {lat:.6f} ، خط الطول {lon:.6f}")

    if clicked and deal_points:
        with st.expander("عرض الصفقات القريبة على الخريطة", expanded=False):
            st.caption("الخريطة غير قابلة للتعديل. يتم فقط عرض الصفقات المسجلة بالقرب من موقع التقييم.")
            st.dataframe(
                [{
                    "المسافة (كم)": round(d["dist_km"], 2),
                    "النشاط": d["activity"],
                    "الإيجار السنوي": d["annual_rent"],
                    "المساحة": d["area_m2"],
                    "السنة": d["year"],
                    "الموقع": f"{d['lat']:.5f},{d['lon']:.5f}",
                } for d in deal_points],
                use_container_width=True,
                hide_index=True,
            )

    st.markdown("### رفع كروكي الموقع (اختياري)")
    uploaded = st.file_uploader("PDF أو صورة", type=["pdf", "png", "jpg", "jpeg"], key="eval_croquis_upload")
    croquis_path, croquis_text = save_croquis(uploaded)
    if croquis_path:
        st.info(f"تم حفظ الكروكي: {croquis_path}")
        if croquis_text:
            with st.expander("نص مستخرج من PDF (إن وجد)"):
                st.write(croquis_text[:2000])

    st.divider()
    st.markdown("### تنفيذ التقييم")

    method_suggested = recommend_method(activity)
    st.write(f"**الأسلوب المقترح:** {method_suggested}")

    if st.button("تنفيذ التقييم", type="primary", key="eval_run"):
        inputs_complete = bool(area_m2 > 0 and clicked is not None)
        lat, lon = (clicked[0], clicked[1]) if clicked else (None, None)

        rec = mn = mx = None
        comps = []
        explanation_parts = []

        if activity == "حدائق عامة":
            rec = profits_method_from_sales(float(annual_sales or 0.0))
            mn, mx = rec * 0.85, rec * 1.15
            explanation_parts.append("تم احتساب الإيجار كنسبة من قيمة البيع/المبيعات السنوية (طريقة الأرباح المبسطة).")
        else:
            if inputs_complete:
                rec, mn, mx, comps = compute_from_deals(activity, area_m2, lat, lon, city=city or None, radius_km=15)

            if rec is None:
                rec, mn, mx = fallback_from_default(activity, float(area_m2))
                rate = DEFAULT_RATE_PER_M2.get(activity, 35)
                explanation_parts.append(f"تم استخدام قيمة استرشادية احتياطية ({rate} ريال/م²) لعدم توفر صفقات كافية قريبة ومشابهة.")
            else:
                explanation_parts.append(f"تم الاعتماد على صفقات مرجعية قريبة ومشابهة ضمن نطاق 15 كم (عدد المقارنات: {len(comps)}).")

        conf_pct, conf_label = compute_confidence(comps, inputs_complete)

        grace_info = apply_grace_period(float(rec), int(contract_years))

        st.metric("القيمة الإيجارية السنوية المقترحة", f"{rec:,.0f} ريال")
        st.write(f"**نطاق القيمة:** {mn:,.0f} – {mx:,.0f} ريال")
        st.write(f"**درجة الثقة:** {conf_pct:.0f}% ({conf_label})")

        if grace_info.get("grace_years", 0) > 0:
            st.info(
                f"فترة السماح: {grace_info['grace_years']} سنة. متوسط الإيجار السنوي على كامل مدة العقد ≈ {grace_info['avg_annual_rent']:,.0f} ريال."
            )

        explanation = " ".join(explanation_parts)
        st.write(f"**التبرير:** {explanation}")

        payload = dict(
            activity=activity,
            city=city or None,
            district=district or None,
            lat=lat,
            lon=lon,
            area_m2=float(area_m2),
            contract_years=int(contract_years),
            method_used=method_suggested,
            recommended_annual_rent=float(rec),
            min_annual_rent=float(mn),
            max_annual_rent=float(mx),
            confidence_pct=float(conf_pct),
            confidence_label=conf_label,
            explanation=explanation,
            croquis_path=croquis_path,
        )
        save_evaluation(payload, user.get("username"))
        st.success("تم حفظ التقييم في قاعدة البيانات.")
