import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from a Streamlit-uploaded PDF file."""
    uploaded_file.seek(0)
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        return "".join(page.get_text() for page in doc)