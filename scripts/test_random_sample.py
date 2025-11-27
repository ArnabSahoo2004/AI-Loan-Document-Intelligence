import sys
import os
import random
import glob

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor

def test_random_sample(n=10):
    # 1. Find all images
    image_dir = "data/kaggle_dataset/Salary Slip"
    images = glob.glob(os.path.join(image_dir, "*.jpg")) + glob.glob(os.path.join(image_dir, "*.png"))
    
    if not images:
        print(f"No images found in {image_dir}")
        return

    # 2. Select random sample
    sample_images = random.sample(images, min(n, len(images)))
    
    print(f"Testing on {len(sample_images)} random images...\n")
    
    ocr = OCREngine()
    extractor = DataExtractor()
    
    results = []
    
    for img_path in sample_images:
        filename = os.path.basename(img_path)
        print(f"Processing: {filename}...")
        
        try:
            # Run OCR
            text = ocr.extract_text(img_path)
            
            # Run Extraction
            data = extractor.extract_entities(text)
            
            # Store result
            result = {
                "file": filename,
                "salary": data.get("salary", 0.0),
                "net_pay": data.get("net_pay", 0.0),
                "total_earnings": data.get("total_earnings", 0.0),
                "basic": data.get("basic_salary", 0.0)
            }
            results.append(result)
            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")
            results.append({"file": filename, "error": str(e)})

    # 3. Print Summary
    print("\n" + "="*60)
    print(f"{'Filename':<20} | {'Salary':<10} | {'Net Pay':<10} | {'Earnings':<10}")
    print("-" * 60)
    
    for res in results:
        if "error" in res:
             print(f"{res['file']:<20} | ERROR: {res['error']}")
        else:
            print(f"{res['file']:<20} | {res['salary']:<10} | {res['net_pay']:<10} | {res['total_earnings']:<10}")
    print("="*60)

if __name__ == "__main__":
    test_random_sample(10)
