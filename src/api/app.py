import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flask import Flask, request, jsonify
import uuid
from werkzeug.utils import secure_filename
from src.agent.loan_agent import LoanAgent
from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor
from src.core.validation import Validator, FraudDetector
from src.core.scoring import calculate_risk_score
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
# Note: In a real production app, the agent might be instantiated per request or via a queue
# For this demo, we'll instantiate it here, but handle the missing API key gracefully
try:
    agent = LoanAgent()
    HAS_AGENT = True
except Exception as e:
    logger.warning(f"Agent initialization failed (likely missing API key): {e}")
    HAS_AGENT = False

ocr_engine = OCREngine()
extractor = DataExtractor()
validator = Validator()
fraud_detector = FraudDetector()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/upload_document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        # Fix: Append original filename so Mock OCR can detect the type (e.g. missing_fields)
        saved_filename = f"{file_id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)
        
        return jsonify({
            "message": "File uploaded successfully",
            "file_id": file_id,
            "file_path": file_path
        }), 201

@app.route('/process_agent', methods=['POST'])
def process_with_agent():
    """
    Full end-to-end processing using the LangChain Agent.
    """
    data = request.json
    file_path = data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid file path"}), 400

    if not HAS_AGENT:
        return jsonify({"error": "Agent not available (check OPENAI_API_KEY)"}), 503

    try:
        result = agent.process_document(file_path)
        # The agent returns a string, we might need to parse it if it's JSON-like
        # For safety, we try to parse it as JSON, else return as string
        try:
            json_result = json.loads(result)
            return jsonify(json_result), 200
        except:
            return jsonify({"raw_result": result}), 200
            
    except Exception as e:
        logger.error(f"Error in agent processing: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/process_manual', methods=['POST'])
def process_manual():
    """
    Manual pipeline without the Agent (fallback).
    """
    data = request.json
    file_path = data.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid file path"}), 400

    try:
        # 1. OCR
        text = ocr_engine.extract_text(file_path)
        
        # 2. Extraction
        extracted_data = extractor.extract_entities(text)
        
        # 3. Validation
        validation_issues = validator.validate_data(extracted_data)
        
        # 4. Fraud Check (Simplified)
        # Pass the full extracted data so the detector can find components like Basic, HRA, etc.
        fraud_result = fraud_detector.check_anomaly(extracted_data)
        
        if isinstance(fraud_result, dict):
            fraud_status = fraud_result["status"]
            fraud_reason = fraud_result["reason"]
        else:
            # Fallback for legacy string response
            fraud_status = fraud_result
            fraud_reason = None
        
        # 5. Risk Logic
        risk_result = calculate_risk_score(validation_issues, fraud_status)
        risk_score = risk_result["risk_score"]
        eligibility = risk_result["eligibility"]
        
        response = {
            "extracted_data": extracted_data,
            "validation_issues": validation_issues,
            "fraud_status": fraud_status,
            "fraud_reason": fraud_reason,
            "risk_score": risk_score,
            "eligibility": eligibility,
            "summary": f"Document processed. Status: {eligibility}. Risk Score: {risk_score}"
        }
        
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in manual processing: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
