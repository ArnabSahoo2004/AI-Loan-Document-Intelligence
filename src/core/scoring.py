def calculate_risk_score(validation_issues, fraud_status):
    """
    Calculate the risk score based on validation issues and fraud status.
    
    Rules:
    - Base Score: 0
    - Critical Penalty: Missing mandatory fields -> 100 (Max Risk)
    - Standard Penalty: Other validation issues -> +20 points each
    - Fraud Penalty: Anomaly Detected -> +50 points
    
    Returns:
        dict: {
            "risk_score": int (0-100),
            "eligibility": str ("Eligible" or "Rejected")
        }
    """
    risk_score = 0
    
    # Check for critical issues first
    critical_issues = [issue for issue in validation_issues if "Missing mandatory field" in issue]
    if critical_issues:
        return {
            "risk_score": 100,
            "eligibility": "Rejected"
        }
        
    # Standard penalties
    if validation_issues:
        risk_score += 20 * len(validation_issues)
        
    # Fraud penalty
    if fraud_status == "Anomaly Detected":
        risk_score += 50
        
    # Cap score at 100
    risk_score = min(risk_score, 100)
    
    # Determine eligibility (Threshold: 40)
    eligibility = "Eligible" if risk_score < 40 else "Rejected"
    
    return {
        "risk_score": risk_score,
        "eligibility": eligibility
    }
