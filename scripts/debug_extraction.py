import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_extraction(image_path):
    ocr = OCREngine(method='easyocr')
    extractor = DataExtractor()
    
    print(f"--- Processing: {image_path} ---")
    
    # 1. OCR
    print("Running OCR...")
    text = ocr.extract_text(image_path)
    print(f"RAW OCR TEXT:\n{text}\n")
    print("-" * 50)
    
    # 2. Extraction
    print("Extracting Entities...")
    extracted_data = extractor.extract_entities(text)
    print(f"Extracted Data: {extracted_data}")

if __name__ == "__main__":
    # Use one of the Kaggle images that might be similar, or just a placeholder 
    # since we can't access the user's uploaded file directly via path yet.
    # But wait, I can ask the user to use a specific file from the dataset 
    # that looks like the one they uploaded if I can identify it.
    # For now, I will test with a known file from the dataset to see if *any* work.
    
    # Ideally, I would use the user's file. 
    # Let's try to use a file from the dataset that might be similar.
    dataset_path = os.path.join("data", "kaggle_dataset", "Salary Slip")
    if os.path.exists(dataset_path):
        # Pick a file that likely has "Basic & DA" or similar if possible, 
        # but random is fine to check general health.
        # Let's pick '37.jpg' since the user mentioned it before, 
        # or just the first one.
        target_file = os.path.join(dataset_path, "37.jpg")
        if os.path.exists(target_file):
            debug_extraction(target_file)
        else:
            print("37.jpg not found.")
    else:
        print("Dataset not found.")
