import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display

def _ar(text: str) -> str:
    # تشكيل عربي بسيط
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(text))

def generate_pdf(report_data: dict) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    font_path = Path("assets/Tajawal-Regular.ttf")
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("Tajawal", str(font_path)))
        c.setFont("Tajawal", 14)
    else:
        c.setFont("Helvetica", 12)

    y = height - 60
    c.drawString(40, y, _ar("تقرير تقييم إيجاري (داخلي)"))
    y -= 30

    for k, v in report_data.items():
        line = f"{k}: {v}"
        c.drawString(40, y, _ar(line))
        y -= 22
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont(c._fontname, c._fontsize)

    c.showPage()
    c.save()
    return buf.getvalue()
