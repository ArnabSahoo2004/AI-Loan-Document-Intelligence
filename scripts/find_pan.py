import sys
import os
import pandas as pd
import re

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

DATA_FILE = "data/training_data_final.csv"
IMAGE_DIR = "data/kaggle_dataset/Salary Slip"

def find_pan_images():
    df = pd.read_csv(DATA_FILE)
    verified_df = df[~df['status'].str.contains("Discard", na=False)]
    
    ocr = OCREngine()
    pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    
    print("Scanning for PANs...")
    
    for index, row in verified_df.iterrows():
        filename = row['filename']
        img_path = os.path.join(IMAGE_DIR, filename)
        
        try:
            text = ocr.extract_text(img_path)
            match = re.search(pan_pattern, text)
            if match:
                print(f"FOUND PAN in {filename}: {match.group(0)}")
                return # Found one!
        except Exception:
            pass
            
    print("No PANs found in verified set.")

if __name__ == "__main__":
    find_pan_images()
