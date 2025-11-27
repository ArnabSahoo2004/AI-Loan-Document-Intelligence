import sys
import os
import pandas as pd
import re
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def smart_repair():
    input_file = "data/training_data_draft.csv"
    output_file = "data/training_data_repaired.csv"
    image_dir = "data/kaggle_dataset/Salary Slip"
    
    if not os.path.exists(input_file):
        print("Draft dataset not found.")
        return

    df = pd.read_csv(input_file)
    ocr = OCREngine()
    
    repaired_count = 0
    
    for index, row in df.iterrows():
        if "Review Needed" in row['status']:
            filename = row['filename']
            img_path = os.path.join(image_dir, filename)
            
            logger.info(f"Attempting repair for {filename}...")
            
            try:
                # Re-run OCR to get full text (snippet in CSV might be truncated)
                text = ocr.extract_text(img_path)
                
                # Heuristic 1: Find all numbers > 3000 (likely monthly salary)
                # Ignore years (1990-2025)
                numbers = re.findall(r"[\d,]+(?:\.\d{2})?", text)
                candidates = []
                for num_str in numbers:
                    try:
                        val = float(num_str.replace(',', ''))
                        if 3000 <= val <= 1000000: # Reasonable salary range
                            if 1990 <= val <= 2025: # Exclude years
                                continue
                            candidates.append(val)
                    except ValueError:
                        continue
                
                if candidates:
                    # Heuristic 2: Pick the largest value (likely Gross or Net)
                    # If there are multiple, the largest is usually Total Earnings
                    best_guess = max(candidates)
                    
                    df.at[index, 'salary'] = best_guess
                    df.at[index, 'status'] = "Auto-Repaired (Heuristic)"
                    df.at[index, 'raw_text_snippet'] = text[:100].replace('\n', ' ')
                    repaired_count += 1
                    logger.info(f"-> Repaired {filename}: Found {best_guess}")
                else:
                    logger.warning(f"-> Failed to repair {filename}: No candidates found.")
                    
            except Exception as e:
                logger.error(f"Error repairing {filename}: {e}")

    # Save
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*40)
    print("Smart Repair Complete!")
    print(f"Original Review Needed: {len(df[df['status'].str.contains('Review')]) + repaired_count}")
    print(f"Successfully Repaired: {repaired_count}")
    print(f"Remaining Review Needed: {len(df[df['status'].str.contains('Review')])}")
    print("="*40)

if __name__ == "__main__":
    smart_repair()
