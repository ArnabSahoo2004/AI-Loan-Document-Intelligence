import sys
import os
import random
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor
from src.core.validation import Validator, FraudDetector
from src.core.scoring import calculate_risk_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_images():
    # Initialize components
    # Try easyocr first as it's more likely to be installed/working without system deps
    ocr = OCREngine(method='easyocr') 
    extractor = DataExtractor()
    validator = Validator()
    fraud_detector = FraudDetector()
    
    dataset_path = os.path.join("data", "kaggle_dataset", "Salary Slip")
    if not os.path.exists(dataset_path):
        print(f"Dataset path not found: {dataset_path}")
        return

    images = [f for f in os.listdir(dataset_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    if not images:
        print("No images found in dataset.")
        return
        
    # Pick 3 random images
    selected_images = random.sample(images, 3)
    
    print(f"Testing {len(selected_images)} real images from Kaggle dataset...\n")
    
    for img_name in selected_images:
        img_path = os.path.join(dataset_path, img_name)
        print(f"--- Processing: {img_name} ---")
        
        try:
            # 1. OCR
            print("Running OCR...")
            text = ocr.extract_text(img_path)
            if not text or "Mock text" in text: # Check if it fell back to mock
                 print("WARNING: OCR returned empty or mock text. Real OCR might not be active.")
            
            # Preview text (first 100 chars)
            print(f"Extracted Text Preview: {text[:100].replace(chr(10), ' ')}...")
            
            # 2. Extraction
            print("Extracting Entities...")
            extracted_data = extractor.extract_entities(text)
            print(f"Extracted Data: {extracted_data}")
            
            # 3. Validation
            print("Validating...")
            validation_issues = validator.validate_data(extracted_data)
            
            # 4. Fraud Check
            salary = extracted_data.get("salary", 0)
            # We don't have tax extraction yet, so passing 0s for others
            fraud_result = fraud_detector.check_anomaly([salary, 0, 0, 0])
            
            if isinstance(fraud_result, dict):
                fraud_status = fraud_result["status"]
                fraud_reason = fraud_result["reason"]
            else:
                fraud_status = fraud_result
                fraud_reason = None
                
            # 5. Scoring
            risk_result = calculate_risk_score(validation_issues, fraud_status)
            
            print("\n--- REPORT ---")
            print(f"Risk Score: {risk_result['risk_score']}/100")
            print(f"Status: {risk_result['eligibility']}")
            print(f"Fraud Status: {fraud_status}")
            if fraud_reason:
                print(f"Fraud Reason: {fraud_reason}")
            print(f"Validation Issues: {validation_issues}")
            print("--------------------------------------------------\n")
            
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

if __name__ == "__main__":
    test_real_images()
