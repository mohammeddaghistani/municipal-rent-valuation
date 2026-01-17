import io
from pathlib import Path
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

def _ar(text: str) -> str:
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(str(text)))

class PDF(FPDF):
    pass

def generate_pdf(report_data: dict) -> bytes:
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    font_path = Path("assets/Tajawal-Regular.ttf")
    if font_path.exists():
        pdf.add_font("Tajawal", "", str(font_path), uni=True)
        pdf.set_font("Tajawal", size=14)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.cell(0, 10, _ar("تقرير تقييم إيجاري (داخلي)"), ln=True)
    pdf.ln(2)

    if font_path.exists():
        pdf.set_font("Tajawal", size=11)
    else:
        pdf.set_font("Helvetica", size=10)

    for k, v in report_data.items():
        line = f"{k}: {v}"
        pdf.multi_cell(0, 7, _ar(line))

    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()
