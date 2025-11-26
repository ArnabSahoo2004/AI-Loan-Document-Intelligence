import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os
import random

def generate_synthetic_data(n_samples=100):
    """
    Generate synthetic salary data.
    Features: [Basic, HRA, Special, Deductions]
    """
    data = []
    
    # 1. Generate Normal Data (90%)
    n_normal = int(n_samples * 0.9)
    for _ in range(n_normal):
        basic = random.randint(20000, 100000)
        hra = int(basic * 0.4) # HRA is usually 40-50% of basic
        special = random.randint(5000, 20000)
        
        gross = basic + hra + special
        # Tax/Deductions is usually 10-30% of gross
        deductions = int(gross * random.uniform(0.1, 0.3))
        
        data.append([basic, hra, special, deductions])
        
    # 2. Generate Fraud/Anomaly Data (10%)
    n_fraud = n_samples - n_normal
    for _ in range(n_fraud):
        case_type = random.choice(['zero_tax', 'negative', 'random'])
        
        if case_type == 'zero_tax':
            # High income, Zero tax
            basic = random.randint(150000, 300000)
            hra = int(basic * 0.4)
            special = random.randint(20000, 50000)
            deductions = 0 # Suspicious!
            data.append([basic, hra, special, deductions])
            
        elif case_type == 'negative':
            # Negative values
            data.append([50000, -2000, 10000, 500])
            
        elif case_type == 'random':
            # Random noise
            data.append([100, 100, 100, 100])

    return np.array(data)

def train_model():
    print("Generating synthetic data...")
    X_train = generate_synthetic_data(100)
    
    print(f"Training Isolation Forest on {len(X_train)} samples...")
    # contamination=0.1 means we expect ~10% outliers
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    
    model_path = 'models/anomaly_model.pkl'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    # Quick Test
    test_fraud = [[200000, 80000, 40000, 0]] # Should be -1 (Anomaly)
    test_normal = [[50000, 20000, 10000, 8000]] # Should be 1 (Normal)
    
    print(f"Test Fraud Prediction: {model.predict(test_fraud)[0]} (Expected -1)")
    print(f"Test Normal Prediction: {model.predict(test_normal)[0]} (Expected 1)")

if __name__ == "__main__":
    train_model()
