
import fitz
import os
import tempfile
import docx
from fastapi import UploadFile

text = None

def extract_text(file: UploadFile) -> str:
    suffix = file.filename.split(".")[-1].lower()
    # Use delete=False for Windows compatibility in some Python versions
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    
    text = ""
    try:
        if suffix == "pdf":
            with fitz.open(tmp_path) as doc:
                text = "\n".join([page.get_text() for page in doc])
        elif suffix in ["docx", "doc"]:
            doc = docx.Document(tmp_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format. Please use PDF or DOCX.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return text

def get_context() -> str:
    if text.strip():
        return text
    return False