import streamlit as st
from streamlit_folium import st_folium
from modules.maps import build_map
from modules.croquis import save_croquis
from modules.evaluation import compute_from_deals, compute_confidence, recommend_method, DEFAULT_RATE_PER_M2, save_evaluation
from modules.auth import require_role

def valuation_ui(user):
    require_role(["admin", "committee", "valuer", "data_entry"])

    st.subheader("التقييم")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        activity = st.selectbox(
            "النشاط",
            [
                "تجاري","صناعي","صحي","تعليمي","رياضي وترفيهي","سياحي","زراعي وحيواني","بيئي",
                "اجتماعي","نقل","مركبات","صيانة وتعليم وتركيب","تشييد وإدارة عقارات",
                "خدمات عامة","ملبوسات ومنسوجات","مرافق عامة","مالي"
            ],
            key="eval_activity"
        )
    with c2:
        city = st.text_input("المدينة", key="eval_city")
    with c3:
        district = st.text_input("الحي", key="eval_district")
    with c4:
        contract_years = st.number_input("مدة العقد (سنة)", min_value=1, value=10, key="eval_contract_years")

    area_m2 = st.number_input("المساحة (م²)", min_value=0.0, value=0.0, key="eval_area")

    st.markdown("### تحديد الموقع")
    if "clicked" not in st.session_state:
        st.session_state.clicked = None

    center_lat, center_lon, zoom = 24.7136, 46.6753, 6
    clicked = st.session_state.clicked

    m = build_map(center_lat, center_lon, zoom, clicked=clicked, deal_points=None)
    map_data = st_folium(m, height=420, width=None, key="eval_map")

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.session_state.clicked = (lat, lon)
        st.success(f"تم اختيار الموقع: خط العرض {lat:.6f} ، خط الطول {lon:.6f}")
        clicked = st.session_state.clicked

    st.markdown("### رفع كروكي الموقع (اختياري)")
    uploaded = st.file_uploader("PDF أو صورة", type=["pdf","png","jpg","jpeg"], key="eval_croquis_upload")
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

        rec, mn, mx, comps = (None, None, None, [])
        if inputs_complete:
            rec, mn, mx, comps = compute_from_deals(activity, area_m2, lat, lon, city=city or None, radius_km=15)

        if rec is None:
            rate = DEFAULT_RATE_PER_M2.get(activity, 40)
            rec = rate * area_m2
            mn, mx = rec * 0.80, rec * 1.20
            explanation = f"تم استخدام قيمة استرشادية احتياطية ({rate} ريال/م²) لعدم توفر صفقات كافية قريبة ومشابهة."
        else:
            explanation = f"تم الاعتماد على صفقات مرجعية قريبة ومشابهة ضمن نطاق 15 كم (عدد المقارنات: {len(comps)})."

        conf_pct, conf_label = compute_confidence(comps, inputs_complete)

        st.metric("القيمة الإيجارية السنوية المقترحة", f"{rec:,.0f} ريال")
        st.write(f"**نطاق القيمة:** {mn:,.0f} – {mx:,.0f} ريال")
        st.write(f"**درجة الثقة:** {conf_pct:.0f}% ({conf_label})")
        st.write(f"**التبرير:** {explanation}")


        # --- زر التحليل الذكي (اختياري) ---
        with st.expander("تحليل ذكي (اختياري – لا يؤثر على الحسابات)", expanded=False):
            col_ai1, col_ai2 = st.columns([1,2])
            with col_ai1:
                run_ai = st.button("تشغيل التحليل الذكي", key="ai_run")
            with col_ai2:
                st.caption("يولّد تبريرًا لغويًا، وتحذير القيم الشاذة، ومقارنة سيناريوهات لدعم قرار اللجنة دون تغيير النتائج.")
            if run_ai:
                try:
                    from ai.explainable import generate_explanation
                    from ai.outliers import detect_outliers
                    from ai.scenarios import compare_scenarios

                    ai_context = {
                        "activity": activity,
                        "city": city,
                        "district": district,
                        "area_m2": area_m2,
                        "recommended_annual_rent": rec,
                        "constraints": {
                            "setup_max_pct": 10,
                            "parks_invest_max_pct": 25
                        }
                    }
                    st.markdown("#### التبرير الذكي")
                    st.write(generate_explanation(ai_context))

                    st.markdown("#### فحص القيم الشاذة")
                    out = detect_outliers([])  # يمكن ربطها لاحقًا بصفقات المقارنة الفعلية
                    if out.get("warning"):
                        st.warning(out["warning"])
                    else:
                        st.success("لا توجد إشارات شذوذ كافية للعرض (تحتاج 3 صفقات على الأقل).")

                    st.markdown("#### مقارنة سيناريوهات")
                    sc = compare_scenarios(float(rec))
                    st.write({
                        "الأساس": sc["base"],
                        "سيناريو أعلى (+15%)": sc["scenario_up"],
                        "سيناريو أقل (-10%)": sc["scenario_down"],
                        "ملاحظة": sc["note"]
                    })
                except Exception as e:
                    st.error(f"تعذر تشغيل التحليل الذكي: {e}")

payload = dict(
            activity=activity,
            city=city or None,
            district=district or None,
            lat=lat, lon=lon,
            area_m2=float(area_m2),
            contract_years=int(contract_years),
            method_used=method_suggested,
            recommended_annual_rent=float(rec),
            min_annual_rent=float(mn),
            max_annual_rent=float(mx),
            confidence_pct=float(conf_pct),
            confidence_label=conf_label,
            explanation=explanation,
            croquis_path=croquis_path
        )
        save_evaluation(payload, user.get("username"))
        st.success("تم حفظ التقييم في قاعدة البيانات.")
