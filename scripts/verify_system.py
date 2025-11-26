import unittest
import os
import json
import sys
from io import BytesIO

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'ai_loan_document_intelligence'))

from src.api.app import app

class TestLoanSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.sample_pdf = "ai_loan_document_intelligence/data/salary_slip_john.pdf"
        
        # Ensure mock data exists
        if not os.path.exists(self.sample_pdf):
            print("Generating mock data for test...")
            from scripts.generate_mock_data import generate_salary_slip
            generate_salary_slip("salary_slip_john.pdf", "John Doe", "Tech Corp", "Oct", 50000, 20000, 15000, 1800, 200)

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_upload_and_manual_process(self):
        # 1. Upload
        with open(self.sample_pdf, 'rb') as f:
            data = {
                'file': (f, 'salary_slip_john.pdf')
            }
            response = self.app.post('/upload_document', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 201)
        file_path = response.json['file_path']
        
        # 2. Process Manual
        process_response = self.app.post('/process_manual', json={'file_path': file_path})
        self.assertEqual(process_response.status_code, 200)
        
        result = process_response.json
        self.assertIn('risk_score', result)
        self.assertIn('eligibility', result)
        print(f"\nManual Process Result: {json.dumps(result, indent=2)}")

    def test_agent_process(self):
        # Skip if no API key, but we can test the endpoint handling
        if not os.getenv("OPENAI_API_KEY"):
            print("\nSkipping Agent test (No API Key)")
            return

        # 1. Upload
        with open(self.sample_pdf, 'rb') as f:
            data = {'file': (f, 'salary_slip_john.pdf')}
            response = self.app.post('/upload_document', data=data, content_type='multipart/form-data')
        
        file_path = response.json['file_path']
        
        # 2. Process Agent
        process_response = self.app.post('/process_agent', json={'file_path': file_path})
        # It might fail if API key is invalid, but let's check if it tries
        if process_response.status_code == 503:
            print("\nAgent Service Unavailable (Expected if no key)")
        else:
            print(f"\nAgent Process Result: {process_response.json}")

if __name__ == '__main__':
    unittest.main()
