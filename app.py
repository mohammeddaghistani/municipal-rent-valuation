
import streamlit as st
from streamlit_folium import st_folium
import folium
import sqlite3
import os

st.set_page_config(page_title="نظام دعم قرار التقييم الإيجاري", layout="wide")

# ---------- Paths ----------
DB_PATH = "data/app.db"
UPLOAD_DIR = "data/uploads"
os.makedirs("data", exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- DB ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT,
        city TEXT,
        value REAL,
        year INTEGER
    )""")
    conn.commit()
    conn.close()

init_db()

# ---------- UI ----------
st.title("نظام دعم قرار التقييم الإيجاري")
st.caption("استخدام داخلي – دعم لجان المنافسات والتخطيط الاستراتيجي")

activity = st.selectbox("نوع النشاط", [
    "تجاري","صناعي","صحي","تعليمي","رياضي","سياحي","زراعي","بيئي","اجتماعي",
    "نقل","مركبات","صيانة","تشييد","خدمات عامة","ملبوسات","مرافق عامة","مالي"
])

city = st.text_input("المدينة")
area = st.number_input("المساحة (م²)", min_value=0.0)

st.subheader("تحديد الموقع")
m = folium.Map(location=[24.7,46.7], zoom_start=6)
map_data = st_folium(m, height=400)

lat, lon = None, None
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"تم اختيار الموقع: {lat:.5f}, {lon:.5f}")

st.subheader("رفع كروكي الموقع")
st.file_uploader("PDF أو صورة", type=["pdf","png","jpg","jpeg"])

st.subheader("إدخال صفقة مرجعية")
deal_value = st.number_input("قيمة الصفقة", min_value=0.0)
deal_year = st.number_input("سنة الصفقة", min_value=2000, value=2023)

if st.button("حفظ الصفقة"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO deals (activity, city, value, year) VALUES (?,?,?,?)",
              (activity, city, deal_value, deal_year))
    conn.commit()
    conn.close()
    st.success("تم حفظ الصفقة")

st.subheader("نتيجة التقييم المبدئي")
if st.button("تنفيذ التقييم"):
    if area > 0 and lat:
        recommended = area * 50
        st.metric("القيمة الإيجارية السنوية المقترحة", f"{recommended:,.0f} ريال")
        st.write("درجة الثقة: 65% (متوسطة)")
    else:
        st.warning("يرجى إدخال المساحة وتحديد الموقع")
