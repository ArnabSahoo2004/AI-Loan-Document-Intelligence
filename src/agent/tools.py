from langchain.tools import Tool
from src.core.ocr import OCREngine
from src.core.extraction import DataExtractor
from src.core.validation import Validator, FraudDetector
import json

# Initialize Core Modules
ocr_engine = OCREngine()
extractor = DataExtractor()
validator = Validator()
fraud_detector = FraudDetector()

def ocr_tool_func(file_path):
    """Reads text from a document (PDF/Image)."""
    return ocr_engine.extract_text(file_path)

def extraction_tool_func(text):
    """Extracts structured fields (PAN, Name, Salary) from text."""
    data = extractor.extract_entities(text)
    return json.dumps(data)

def validation_tool_func(json_data):
    """Checks for missing fields and invalid formats."""
    data = json.loads(json_data)
    issues = validator.validate_data(data)
    return json.dumps({"issues": issues, "status": "Valid" if not issues else "Invalid"})

def fraud_check_tool_func(json_data):
    """Detects anomalies in salary patterns."""
    data = json.loads(json_data)
    salary = data.get("salary", 0)
    # Simplified: In a real scenario, we'd extract components. 
    # Here we just check if salary is present for the anomaly model or use a dummy check.
    # For the mock model we created, we need 4 components. 
    # Let's assume we extracted them or default to 0.
    components = [salary, 0, 0, 0] 
    result = fraud_detector.check_anomaly(components)
    return result

# Define LangChain Tools
tools = [
    Tool(
        name="OCR_Document",
        func=ocr_tool_func,
        description="Useful for reading text from a loan document file path."
    ),
    Tool(
        name="Extract_Data",
        func=extraction_tool_func,
        description="Useful for extracting structured data (JSON) from raw text."
    ),
    Tool(
        name="Validate_Data",
        func=validation_tool_func,
        description="Useful for validating extracted data for missing fields or errors. Input should be JSON string."
    ),
    Tool(
        name="Fraud_Check",
        func=fraud_check_tool_func,
        description="Useful for detecting fraud or anomalies in the data. Input should be JSON string."
    )
]
