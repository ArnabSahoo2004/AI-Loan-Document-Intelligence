import sys
import os
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.validation import FraudDetector

def debug_fraud():
    detector = FraudDetector()
    
    # Case 1: The case that failed (High Salary, Zeros)
    # In app.py: fraud_detector.check_anomaly([salary, 0, 0, 0])
    features_failed = [200000, 0, 0, 0]
    print(f"Testing Features {features_failed}...")
    result = detector.check_anomaly(features_failed)
    print(f"Result: {result}")
    
    # Case 2: Normal case (approximate to training data)
    features_normal = [50000, 20000, 15000, 2000]
    print(f"Testing Features {features_normal}...")
    result = detector.check_anomaly(features_normal)
    print(f"Result: {result}")

    # Case 3: Extreme outlier
    features_extreme = [10000000, 0, 0, 0]
    print(f"Testing Features {features_extreme}...")
    result = detector.check_anomaly(features_extreme)
    print(f"Result: {result}")

if __name__ == "__main__":
    debug_fraud()
