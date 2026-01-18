import streamlit as st


def apply_branding(app_title: str = ""):
    """
    Branding فقط (CSS/RTL/خط/شعار/تذييل).
    ممنوع وضع st.set_page_config هنا.
    """

    # RTL + خطوط + تحسين الواجهة
    st.markdown(
        """
        <style>
          html, body, [class*="css"]  {
            direction: rtl;
            text-align: right;
            font-family: "Tajawal", "IBM Plex Sans Arabic", "Cairo", sans-serif;
          }

          /* تحسين التباعد العام */
          .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
          }

          /* تحسين التبويبات */
          div[data-baseweb="tab-list"] {
            gap: .5rem;
            justify-content: flex-start;
          }
          button[data-baseweb="tab"] {
            border-radius: 12px !important;
            padding: .55rem .9rem !important;
            font-weight: 700 !important;
          }

          /* كروت */
          .mdg-card {
            border-radius: 18px;
            padding: 16px 18px;
            border: 1px solid rgba(255,255,255,.08);
            background: rgba(255,255,255,.04);
            backdrop-filter: blur(10px);
          }

          /* فوتر */
          .mdg-footer {
            margin-top: 28px;
            padding: 14px 16px;
            border-top: 1px solid rgba(255,255,255,.10);
            opacity: .9;
            font-size: .92rem;
            line-height: 1.7;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # عنوان أعلى الصفحة (اختياري)
    if app_title:
        st.markdown(
            f"""
            <div class="mdg-card" style="margin-bottom: 14px;">
              <div style="font-size:1.35rem;font-weight:900;">{app_title}</div>
              <div style="opacity:.85;margin-top:6px;">
                للاستخدام الداخلي – غير مخصص للنشر
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_footer():
    st.markdown(
        """
        <div class="mdg-footer">
          <div><b>© محمد داغستاني 2026</b></div>
          <div>مبادرة تطوير الأعمال بإشراف ودعم أ. عبدالرحمن خجا</div>
          <div>للاستخدام الداخلي – غير مخصص للنشر</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
