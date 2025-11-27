import logging
from sklearn.ensemble import IsolationForest
import numpy as np
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Validator:
    def __init__(self):
        pass

    def validate_data(self, data):
        """
        Validate extracted data against rules.
        """
        issues = []
        
        # Rule 1: Mandatory Fields
        mandatory = ["pan", "names"]
        for field in mandatory:
            value = data.get(field)
            # Check if None or Empty List
            if not value or (isinstance(value, list) and len(value) == 0):
                if field == "pan":
                    issues.append(f"Missing field: {field}") # Downgrade to warning
                else:
                    issues.append(f"Missing mandatory field: {field}")
            # Check if List contains only empty strings
            elif isinstance(value, list) and all(isinstance(s, str) and s.strip() == "" for s in value):
                issues.append(f"Missing mandatory field: {field} (Found empty)")

        # Rule 2: PAN Format (Double check)
        if data.get("pan") and len(data["pan"]) != 10:
             issues.append(f"Invalid PAN format: {data['pan']}")

        # Rule 3: Salary Check
        if data.get("salary", 0) < 1000:
            issues.append(f"Suspiciously low salary detected: {data.get('salary')}")

        return issues

class FraudDetector:
    def __init__(self, model_path='models/anomaly_model.pkl'):
        self.model_path = model_path
        self.model = self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        else:
            logger.warning(f"Model not found at {self.model_path}. Please run scripts/train_model.py")
            # Return a dummy object that always predicts Normal to avoid crash
            class DummyModel:
                def predict(self, X): return [1] * len(X)
            return DummyModel()

    def check_anomaly(self, salary_input):
        """
        Check if the salary components look anomalous.
        Input can be a list [Basic, HRA, Special, Deductions] OR a dict of components.
        """
        features = [0, 0, 0, 0] # Default [Basic, HRA, Special, Deductions]
        
        if isinstance(salary_input, dict):
            # Map extracted components to model features
            basic = salary_input.get("basic_salary", 0)
            hra = salary_input.get("hra", 0)
            deductions = salary_input.get("total_deductions", 0)
            # Special allowance is often the rest
            total = salary_input.get("total_earnings", 0)
            special = max(0, total - (basic + hra))
            
            features = [basic, hra, special, deductions]
        elif isinstance(salary_input, list) and len(salary_input) == 4:
            features = salary_input
        else:
            return "Skipped (Insufficient Data)"
        
        # Ensure input is 2D array
        prediction = self.model.predict([features])
        
        # IsolationForest returns -1 for anomalies, 1 for normal
        is_anomaly = prediction[0] == -1
        
        if is_anomaly:
            reason = self._explain_anomaly(features)
            return {"status": "Anomaly Detected", "reason": reason}
        else:
            return {"status": "Normal", "reason": None}

    def _explain_anomaly(self, features):
        """
        Heuristic to explain why the model might have flagged this.
        features: [Basic, HRA, Special, Deductions]
        """
        basic, hra, special, deductions = features
        
        if basic > 100000 and deductions == 0:
            return "High Income with Zero Tax/Deductions"
        
        if any(x < 0 for x in features):
            return "Negative values detected in salary components"
            
        if basic < 1000 and basic > 0: # Only flag if non-zero but low
            return "Extremely low Basic Salary"
            
        return "Statistical Outlier (Unusual combination of values)"
