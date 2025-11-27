import sys
import os
import glob
import pandas as pd
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_dataset():
    image_dir = "data/kaggle_dataset/Salary Slip"
    output_file = "data/training_data_draft.csv"
    
    # Find all images
    images = glob.glob(os.path.join(image_dir, "*.jpg")) + glob.glob(os.path.join(image_dir, "*.png"))
    logger.info(f"Found {len(images)} images in {image_dir}")
    
    ocr = OCREngine()
    extractor = DataExtractor()
    
    records = []
    
    for i, img_path in enumerate(images):
        filename = os.path.basename(img_path)
        logger.info(f"[{i+1}/{len(images)}] Processing {filename}...")
        
        try:
            # 1. OCR
            text = ocr.extract_text(img_path)
            
            # 2. Extraction
            data = extractor.extract_entities(text)
            
            # 3. Prepare Record
            salary = data.get("salary", 0.0)
            
            # Determine Status
            status = "Auto-Labeled"
            if salary < 1000:
                status = "Review Needed (Low Salary)"
            elif salary == 0:
                status = "Review Needed (Zero)"
            
            record = {
                "filename": filename,
                "salary": salary,
                "net_pay": data.get("net_pay", 0.0),
                "total_earnings": data.get("total_earnings", 0.0),
                "basic_salary": data.get("basic_salary", 0.0),
                "hra": data.get("hra", 0.0),
                "extracted_name": data.get("names", [""])[0] if data.get("names") else "",
                "status": status,
                "raw_text_snippet": text[:100].replace('\n', ' ') # Save snippet for quick context
            }
            records.append(record)
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}")
            records.append({
                "filename": filename,
                "status": f"Error: {str(e)}"
            })
            
    # Save to CSV
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    logger.info(f"Dataset saved to {output_file}")
    
    # Print Summary
    print("\n" + "="*40)
    print("Processing Complete!")
    print(f"Total Images: {len(images)}")
    print(f"Auto-Labeled: {len(df[df['status'] == 'Auto-Labeled'])}")
    print(f"Needs Review: {len(df[df['status'].str.contains('Review')])}")
    print("="*40)

if __name__ == "__main__":
    generate_dataset()
