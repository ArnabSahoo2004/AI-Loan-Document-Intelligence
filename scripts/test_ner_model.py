import spacy
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

import spacy
import sys
import os
import pandas as pd
import random

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

MODEL_DIR = "models/ner_model"
DATA_FILE = "data/training_data_final.csv"
IMAGE_DIR = "data/kaggle_dataset/Salary Slip"

def test_model():
    if not os.path.exists(MODEL_DIR):
        print("Model not found.")
        return

    print("Loading model...")
    nlp = spacy.load(MODEL_DIR)
    ocr = OCREngine()
    
    # Load verified data to pick samples
    df = pd.read_csv(DATA_FILE)
    verified_df = df[~df['status'].str.contains("Discard", na=False)]
    
    # Pick 3 random samples
    samples = verified_df.sample(3)
    
    for index, row in samples.iterrows():
        filename = row['filename']
        img_path = os.path.join(IMAGE_DIR, filename)
        
        print(f"\n{'='*40}")
        print(f"Testing {filename}...")
        print(f"Expected: Salary={row['salary']}, Net={row['net_pay']}, Name={row['extracted_name']}")
        
        try:
            text = ocr.extract_text(img_path)
            doc = nlp(text)
            
            print("Extracted Entities:")
            found_any = False
            for ent in doc.ents:
                print(f" - {ent.label_}: {ent.text}")
                found_any = True
            
            if not found_any:
                print(" - No entities found.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
