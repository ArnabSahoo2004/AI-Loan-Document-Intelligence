# AI Loan Document Intelligence System

An end-to-end AI system for extracting, validating, and analyzing loan documents (Salary Slips, KYC) using OCR, NLP, and Agentic Workflows.

## Features
- **OCR Extraction**: Supports Images and PDFs using Tesseract/EasyOCR.
- **NLP Parsing**: Extracts key fields (Name, PAN, Income) using Regex/SpaCy.
- **Fraud Detection**: Validates data consistency and detects anomalies in salary patterns.
- **Agentic Workflow**: Uses LangChain agents to orchestrate the extraction and validation process.
- **Risk Reporting**: Generates a comprehensive risk summary with eligibility checks.
- **UI/API**: Streamlit frontend and Flask REST API.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR**
   - Windows: Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
   - Add Tesseract to your system PATH.

3. **Download SpaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the Application**
   - **API**: `python src/api/app.py`
   - **Frontend**: `streamlit run src/ui/app.py`

## Directory Structure
- `src/core`: Core logic for OCR, Extraction, and Validation.
- `src/agent`: LangChain agent definitions.
- `src/api`: Flask backend.
- `src/ui`: Streamlit frontend.
- `scripts`: Helper scripts (e.g., mock data generation).
