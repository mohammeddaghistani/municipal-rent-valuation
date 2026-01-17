import streamlit as st
import numpy as np
from sqlalchemy.orm import Session
from modules.db import SessionLocal, Deal, Evaluation
from modules.utils import haversine_km, now_iso

DEFAULT_RATE_PER_M2 = {
    "تجاري": 50, "صناعي": 35, "صحي": 55, "تعليمي": 40, "رياضي وترفيهي": 35, "سياحي": 60,
    "زراعي وحيواني": 15, "بيئي": 20, "اجتماعي": 20, "نقل": 45, "مركبات": 40,
    "صيانة وتعليم وتركيب": 35, "تشييد وإدارة عقارات": 45, "خدمات عامة": 25,
    "ملبوسات ومنسوجات": 45, "مرافق عامة": 25, "مالي": 65
}

def confidence_label(pct: float) -> str:
    if pct >= 70:
        return "عالية"
    if pct >= 40:
        return "متوسطة"
    return "منخفضة"

def recommend_method(activity: str) -> str:
    # مبسّط: معظم الأنشطة الاستثمارية تميل لأسلوب الدخل، مع السوق عند وفرة المقارنات
    market_like = {"تجاري","مركبات","ملبوسات ومنسوجات","صيانة وتعليم وتركيب"}
    if activity in market_like:
        return "السوق + الدخل"
    return "الدخل"

def compute_from_deals(activity, area_m2, lat, lon, city=None, radius_km=10):
    db: Session = SessionLocal()
    try:
        q = db.query(Deal).filter(Deal.activity == activity)
        if city:
            q = q.filter(Deal.city == city)
        deals = q.all()
    finally:
        db.close()

    comps = []
    for d in deals:
        if d.area_m2 and d.annual_rent and d.area_m2 > 0 and d.annual_rent > 0:
            dist = None
            if lat is not None and lon is not None and d.lat is not None and d.lon is not None:
                dist = haversine_km(lat, lon, d.lat, d.lon)
            # إذا لا توجد إحداثيات للصفقة، نعتبرها ضمن نفس المدينة (إذا تم إدخال المدينة)
            if dist is None and city and d.city == city:
                dist = radius_km * 0.7
            if dist is not None and dist <= radius_km:
                rate = d.annual_rent / d.area_m2
                comps.append((rate, dist, d.year))

    if len(comps) >= 2:
        rates = np.array([c[0] for c in comps], dtype=float)
        med = float(np.median(rates))
        # نطاق: 15% حول الوسيط (مبدئي)
        rec = med * area_m2
        return rec, rec*0.85, rec*1.15, comps
    return None, None, None, comps

def compute_confidence(comps, inputs_complete: bool):
    # مبدئي: يعتمد على عدد المقارنات + قربها
    n = len(comps)
    if n == 0:
        base = 20
    elif n == 1:
        base = 35
    elif n <= 3:
        base = 55
    elif n <= 7:
        base = 75
    else:
        base = 85

    if n > 0:
        avg_dist = float(np.mean([c[1] for c in comps]))
        # كلما زادت المسافة تقل الثقة
        base -= min(25, avg_dist * 1.5)

    if not inputs_complete:
        base -= 15

    base = max(5, min(95, base))
    return float(base), confidence_label(float(base))

def save_evaluation(payload: dict, username: str):
    db: Session = SessionLocal()
    try:
        db.add(Evaluation(created_by=username, **payload))
        db.commit()
    finally:
        db.close()
