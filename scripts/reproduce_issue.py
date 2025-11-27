import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor

def test_extraction(image_path):
    print(f"Testing extraction on: {image_path}")
    
    # 1. Run OCR
    ocr = OCREngine()
    text = ocr.extract_text(image_path)
    
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("\n--- RAW OCR TEXT START ---\n")
        for line in text.split('\n'):
            f.write(f"LINE: {line}\n")
        f.write("--- RAW OCR TEXT END ---\n\n")
        
        # Debug: Find all numbers
        import re
        numbers = re.findall(r"[\d,]+(?:\.\d{2})?", text)
        f.write(f"DEBUG: All numbers found: {numbers}\n")
    
    # 2. Run Extraction
    extractor = DataExtractor()
    data = extractor.extract_entities(text)
    with open("debug_output.txt", "a", encoding="utf-8") as f:
        f.write(f"\nEXTRACTED DATA: {data}\n")
    print("\n--- EXTRACTED DATA ---")
    print(data)

if __name__ == "__main__":
    # Use one of the kaggle images
    test_image = "data/kaggle_dataset/Salary Slip/10.jpg"
    if os.path.exists(test_image):
        test_extraction(test_image)
    else:
        print(f"File not found: {test_image}")
