import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.validation import Validator
from src.core.scoring import calculate_risk_score

def test_missing_fields_score():
    validator = Validator()
    
    # Simulate extracted data with missing name
    extracted_data = {
        "names": [], # Empty list
        "pan": "ABCDE1234F",
        "salary": 50000
    }
    
    validation_issues = validator.validate_data(extracted_data)
    print(f"Validation Issues: {validation_issues}")
    
    # Use the new scoring function
    result = calculate_risk_score(validation_issues, "Normal")
    risk_score = result["risk_score"]
    eligibility = result["eligibility"]
    
    print(f"Risk Score: {risk_score}")
    print(f"Eligibility: {eligibility}")
    
    if risk_score == 100 and eligibility == "Rejected":
        print("PASS: Risk Score is 100 and Rejected as expected.")
    else:
        print(f"FAIL: Expected Score 100/Rejected, got {risk_score}/{eligibility}")

if __name__ == "__main__":
    test_missing_fields_score()
