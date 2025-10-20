import os
from PIL import Image
from typing import Optional

def ocr_file(filepath: str) -> str:
    """
    MOCK: Extracts text from an image or PDF file.
    In a real app, this would use Tesseract or PaddleOCR.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        try:
            # Simulate opening the image with Pillow (to ensure file is valid/exists)
            Image.open(filepath).close()
            
            # Return mock OCR text
            return f"MOCK OCR text for image {os.path.basename(filepath)}. Keywords: document, meeting, important."
        except Exception:
            return "" # File not a valid image or does not exist
            
    elif ext == '.pdf':
        # Return mock OCR text for PDF
        return f"MOCK OCR text for PDF: {os.path.basename(filepath)}. Key content: financial report, Q3 2024."
    else:
        return ""

if __name__ == "__main__":
    print("OCR Engine Initialized (MOCK).")
    
    # Example Usage (MOCK)
    print(f"OCR result for image: {ocr_file('/data/invoice.png')}")
    print(f"OCR result for pdf: {ocr_file('/data/report.pdf')}")

