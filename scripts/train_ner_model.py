import pandas as pd
import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import os
import logging
import sys
from tqdm import tqdm

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_FILE = "data/training_data_final.csv"
IMAGE_DIR = "data/kaggle_dataset/Salary Slip"
MODEL_DIR = "models/ner_model"

def create_training_data(df):
    ocr = OCREngine()
    TRAIN_DATA = []
    
    logger.info("Generating training data (this involves running OCR on all images)...")
    
    # Use tqdm for progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing Images", unit="img"):
        filename = row['filename']
        img_path = os.path.join(IMAGE_DIR, filename)
        
        if not os.path.exists(img_path):
            continue
            
        try:
            # Get full text
            text = ocr.extract_text(img_path)
            
            entities = []
            
            # Helper to find entity offsets
            def add_entity(value, label):
                if pd.isna(value) or value == 0 or str(value).strip() == "":
                    return
                
                val_str = str(value)
                if isinstance(value, float) and value % 1 == 0:
                    val_str = str(int(value)) # Handle 20000.0 -> 20000
                
                # Find ALL occurrences, not just the first one
                start = 0
                while True:
                    start = text.find(val_str, start)
                    if start == -1:
                        break
                    end = start + len(val_str)
                    
                    # Check for overlap with existing entities
                    is_overlap = False
                    for existing_start, existing_end, _ in entities:
                        if max(start, existing_start) < min(end, existing_end):
                            is_overlap = True
                            break
                    
                    if not is_overlap:
                        entities.append((start, end, label))
                        # We only need one instance per label ideally, but if it appears multiple times, 
                        # it's hard to know which is which without layout. 
                        # For now, let's just take the first valid non-overlapping one for this label.
                        break 
                    
                    start += 1
            
            # Add entities (Order matters: Name is usually unique, amounts might overlap)
            add_entity(row['extracted_name'], "EMPLOYEE_NAME")
            add_entity(row['salary'], "SALARY")
            add_entity(row['net_pay'], "NET_PAY")
            
            if entities:
                TRAIN_DATA.append((text, {"entities": entities}))
                
        except Exception as e:
            logger.warning(f"Skipping {filename}: {e}")
            
    return TRAIN_DATA

def train_model():
    # Enable GPU if available
    is_gpu = spacy.prefer_gpu()
    logger.info(f"GPU Enabled: {is_gpu}")

    # 1. Load Data
    if not os.path.exists(DATA_FILE):
        logger.error("Training data not found!")
        return

    df = pd.read_csv(DATA_FILE)
    # Filter out discarded rows
    df = df[~df['status'].str.contains("Discard", na=False)]
    
    logger.info(f"Training on {len(df)} verified records.")
    
    # 2. Prepare Data
    TRAIN_DATA = create_training_data(df)
    logger.info(f"Prepared {len(TRAIN_DATA)} training examples.")
    
    # 3. Initialize Model
    # We start with a blank English model or load existing
    nlp = spacy.blank("en")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
        
    # Add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
            
    # 4. Train
    optimizer = nlp.begin_training()
    
    # Training Loop
    n_iter = 20
    logger.info(f"Starting training for {n_iter} iterations...")
    
    for i in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        
        for batch in batches:
            examples = []
            for text, annots in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annots)
                examples.append(example)
            
            nlp.update(examples, drop=0.5, losses=losses, sgd=optimizer)
            
        logger.info(f"Iteration {i+1} Loss: {losses}")
        
    # 5. Save Model
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    nlp.to_disk(MODEL_DIR)
    logger.info(f"Model saved to {MODEL_DIR}")
    print("\n" + "="*40)
    print("Training Complete!")
    print(f"Model saved to: {os.path.abspath(MODEL_DIR)}")
    print("="*40)

if __name__ == "__main__":
    train_model()
