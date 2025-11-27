import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.extraction import DataExtractor
from src.core.ocr import OCREngine

TEST_IMAGE = "data/kaggle_dataset/Salary Slip/10.jpg"

def verify_integration():
    print("Initializing DataExtractor...")
    extractor = DataExtractor()
    
    if extractor.ner_model:
        print("SUCCESS: NER model loaded.")
    else:
        print("FAILURE: NER model NOT loaded.")
        return

    print(f"\nExtracting from {TEST_IMAGE}...")
    ocr = OCREngine()
    text = ocr.extract_text(TEST_IMAGE)
    
    data = extractor.extract_entities(text)
    
    print("\nExtracted Data:")
    print(f" - Salary: {data.get('salary')}")
    print(f" - Net Pay: {data.get('net_pay')}")
    print(f" - Total Earnings: {data.get('total_earnings')}")
    print(f" - Names: {data.get('names')}")
    
    # Check if NER values are present (we know 10.jpg has Wayne Doorprize)
    if "Wayne Doorprize" in data.get('names', []):
        print("\nSUCCESS: NER extracted correct name.")
    else:
        print("\nWARNING: NER did not extract expected name.")

if __name__ == "__main__":
    verify_integration()
