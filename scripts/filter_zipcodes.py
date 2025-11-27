import pandas as pd
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def filter_zipcodes():
    input_file = "data/training_data_repaired.csv"
    output_file = "data/training_data_final.csv"
    
    df = pd.read_csv(input_file)
    
    reverted_count = 0
    
    for index, row in df.iterrows():
        if "Auto-Repaired" in row['status']:
            salary = row['salary']
            text = str(row['raw_text_snippet']).lower()
            
            # Check if it looks like a Zip Code (6 digits, integer-like)
            if 100000 <= salary <= 999999 and salary % 1 == 0:
                # Heuristic: If text contains "pin", "mumbai", "delhi", "chennai", "road", "marg"
                # and NO "rs", "inr", "salary" near the number (hard to check in snippet, but let's try)
                
                is_suspicious = False
                
                # 1. Check for address keywords
                if any(x in text for x in ["pin", "road", "marg", "street", "box", "nagar", "pur"]):
                    is_suspicious = True
                    
                # 2. Check for specific known zip codes from previous analysis
                if salary in [302004, 6000014, 400001, 110001, 560008]: # 6000014 is 7 digits but let's be safe
                     is_suspicious = True
                     
                if is_suspicious:
                    logger.info(f"Reverting {row['filename']}: {salary} (Likely Zip Code/Address)")
                    df.at[index, 'salary'] = 0.0
                    df.at[index, 'status'] = "Review Needed (Suspected Zip Code)"
                    reverted_count += 1

    df.to_csv(output_file, index=False)
    
    print("\n" + "="*40)
    print("Zip Code Filter Complete!")
    print(f"Reverted: {reverted_count}")
    print(f"Final Ready for Training: {len(df[~df['status'].str.contains('Review')])}")
    print("="*40)

if __name__ == "__main__":
    filter_zipcodes()
