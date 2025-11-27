import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.extraction import DataExtractor

def test_reconciliation():
    extractor = DataExtractor()
    
    # Test Case 1: Missing Deductions
    data1 = {"net_pay": 2850.0, "total_earnings": 2900.0, "total_deductions": 0.0}
    result1 = extractor._reconcile_data(data1)
    print(f"Test 1 (Missing Deductions): {result1['total_deductions']} (Expected: 50.0)")
    
    # Test Case 2: Missing Net Pay
    data2 = {"net_pay": 0.0, "total_earnings": 50000.0, "total_deductions": 5000.0}
    result2 = extractor._reconcile_data(data2)
    print(f"Test 2 (Missing Net Pay): {result2['net_pay']} (Expected: 45000.0)")
    
    # Test Case 3: All Present (Should not change)
    data3 = {"net_pay": 100.0, "total_earnings": 200.0, "total_deductions": 100.0}
    result3 = extractor._reconcile_data(data3)
    print(f"Test 3 (All Present): {result3['total_deductions']} (Expected: 100.0)")

if __name__ == "__main__":
    test_reconciliation()
