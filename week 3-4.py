###PDF Extraction & Data Structuring###


import fitz # PyMuPDF library

def extract_full_text(pdf_path):
    """Reads a PDF and extracts all text content."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_metrics(text):
    """Simple keyword matching to find results in the paper."""
    results = {}
    keywords = ["accuracy", "dataset", "f1-score", "methods"]
    for word in keywords:
        if word in text.lower():
            results[word] = "Mentioned in text"
    return results
