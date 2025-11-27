import sys
import os
import pandas as pd
import re
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ocr import OCREngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

BLACKLIST = {
    "salary", "slip", "month", "year", "date", "total", "net", "pay", "bank", "account", 
    "employee", "designation", "limited", "pvt", "ltd", "marg", "road", "street", "nagar", 
    "floor", "block", "sector", "india", "govt", "department", "office", "company", "address", 
    "contact", "phone", "mobile", "email", "id", "no", "code", "number", "regime", "tax", 
    "pf", "esi", "uan", "pan", "aadhaar", "ifsc", "micr", "branch", "city", "state", "pin", 
    "zip", "zone", "circle", "division", "station", "place", "location", "site", "unit", 
    "plant", "factory", "works", "store", "shop", "mall", "plaza", "tower", "building", 
    "apartment", "flat", "house", "villa", "cottage", "bungalow", "mansion", "palace", 
    "castle", "fort", "court", "chamber", "hall", "room", "cabin", "desk", "counter", 
    "window", "gate", "door", "entrance", "exit", "lift", "elevator", "stair", "step", 
    "level", "ground", "basement", "terrace", "roof", "ceiling", "wall", "corner", "side", 
    "front", "back", "left", "right", "top", "bottom", "center", "middle", "end", "start", 
    "finish", "line", "row", "column", "grid", "table", "chart", "graph", "map", "plan", 
    "layout", "design", "draft", "copy", "print", "scan", "fax", "post", "mail", "courier", 
    "parcel", "packet", "bag", "box", "case", "crate", "bin", "bucket", "basket", "tray", 
    "plate", "dish", "bowl", "cup", "mug", "glass", "bottle", "jar", "can", "tin", "drum", 
    "barrel", "tank", "vat", "tub", "pool", "pond", "lake", "river", "sea", "ocean", "water", 
    "air", "fire", "earth", "wind", "rain", "snow", "ice", "sun", "moon", "star", "sky", 
    "cloud", "storm", "thunder", "lightning", "light", "dark", "day", "night", "morning", 
    "evening", "noon", "midnight", "time", "hour", "minute", "second", "week", "decade", 
    "century", "millennium", "era", "epoch", "age", "period", "phase", "stage", "grade", 
    "rank", "class", "group", "team", "crew", "squad", "force", "army", "navy", "airforce", 
    "police", "guard", "security", "safety", "health", "wealth", "life", "death", "birth", 
    "marriage", "divorce", "love", "hate", "war", "peace", "joy", "sorrow", "happy", "sad", 
    "good", "bad", "true", "false", "yes", "on", "off", "in", "out", "up", "down", "forward", 
    "backward", "fast", "slow", "high", "low", "big", "small", "large", "tiny", "huge", 
    "micro", "macro", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta", "kilo", 
    "hecto", "deca", "deci", "centi", "milli", "nano", "pico", "femto", "atto", "zepto", 
    "yocto", "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", 
    "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", 
    "phi", "chi", "psi", "omega", "ytd", "deductions", "earnings", "basic", "hra", "da", 
    "allowance", "bonus", "arrears", "advance", "loan", "insurance", "medical", "transport", 
    "conveyance", "special", "other", "miscellaneous", "gross", "net", "salary", "wages", 
    "stipend", "remuneration", "compensation", "benefits", "perks", "incentive", "commission", 
    "overtime", "leave", "holiday", "vacation", "sick", "casual", "earned", "privilege", 
    "maternity", "paternity", "adoption", "study", "sabbatical", "loss", "profit", "revenue", 
    "income", "expense", "cost", "price", "value", "amount", "rate", "percentage", "interest", 
    "tax", "duty", "cess", "levy", "fine", "penalty", "fee", "charge", "bill", "invoice", 
    "receipt", "voucher", "challan", "cheque", "draft", "order", "demand", "request", 
    "application", "form", "report", "statement", "sheet", "file", "document", "record", 
    "data", "info", "details", "particulars", "description", "remarks", "notes", "comments", 
    "status", "action", "result", "outcome", "output", "input", "source", "target", "destination", 
    "origin", "cause", "effect", "reason", "purpose", "goal", "objective", "target", "aim", 
    "mission", "vision", "values", "principles", "policies", "rules", "regulations", "laws", 
    "acts", "codes", "standards", "guidelines", "procedures", "processes", "methods", 
    "techniques", "tools", "systems", "software", "hardware", "network", "internet", "web", 
    "site", "page", "link", "url", "email", "address", "phone", "mobile", "fax", "telex"
}

def is_valid_name(name):
    if not name or not isinstance(name, str):
        return False
    name = name.lower().strip()
    if len(name) < 3:
        return False
    # Check if any word in the name is in the blacklist
    words = re.split(r'[\s\-_,.]+', name)
    for word in words:
        if word in BLACKLIST:
            return False
    return True

def extract_better_name(text):
    # 1. Look for "Name: [Value]" pattern
    match = re.search(r"(?:Name|Employee Name|Emp Name)[\s:_]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    if match:
        candidate = match.group(1).strip()
        if is_valid_name(candidate):
            return candidate

    # 2. Look for "Mr./Ms. [Value]" pattern
    match = re.search(r"(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    if match:
        candidate = match.group(1).strip()
        if is_valid_name(candidate):
            return candidate
            
    return ""

def repair_names():
    input_file = "data/training_data_final.csv"
    output_file = "data/training_data_final.csv" # Overwrite
    image_dir = "data/kaggle_dataset/Salary Slip"
    
    df = pd.read_csv(input_file)
    ocr = OCREngine()
    
    repaired_count = 0
    
    for index, row in df.iterrows():
        current_name = row.get('extracted_name', '')
        
        if not is_valid_name(current_name):
            filename = row['filename']
            img_path = os.path.join(image_dir, filename)
            
            logger.info(f"Repairing name for {filename} (Current: '{current_name}')...")
            
            try:
                text = ocr.extract_text(img_path)
                new_name = extract_better_name(text)
                
                if new_name:
                    df.at[index, 'extracted_name'] = new_name
                    logger.info(f"-> Found: {new_name}")
                    repaired_count += 1
                else:
                    df.at[index, 'extracted_name'] = "" # Clear invalid name
                    logger.info(f"-> Could not find better name. Cleared.")
                    
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
        else:
            # logger.info(f"Keeping valid name for {row['filename']}: {current_name}")
            pass

    df.to_csv(output_file, index=False)
    
    print("\n" + "="*40)
    print("Name Repair Complete!")
    print(f"Repaired/Cleared: {repaired_count}")
    print("="*40)

if __name__ == "__main__":
    repair_names()
