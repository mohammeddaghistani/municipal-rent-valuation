def detect_outliers(deals: list) -> dict:
    if not deals or len(deals) < 3:
        return {"warning": None}
    return {"warning": "تنبيه: قد توجد قيم شاذة ضمن الصفقات المرجعية."}
