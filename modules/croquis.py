import streamlit as st
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader
from PIL import Image

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_croquis(uploaded_file):
    if not uploaded_file:
        return None, None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = Path(uploaded_file.name).suffix.lower()
    safe_name = f"croquis_{ts}{suffix}"
    out_path = UPLOAD_DIR / safe_name

    with open(out_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    extracted_text = None
    try:
        if suffix == ".pdf":
            reader = PdfReader(str(out_path))
            extracted_text = "\n".join([p.extract_text() or "" for p in reader.pages]).strip() or None
    except Exception:
        extracted_text = None

    return str(out_path), extracted_text
