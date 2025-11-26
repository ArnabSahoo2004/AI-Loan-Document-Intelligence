import streamlit as st
import requests
import json
import os

# Configuration
API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="AI Loan Document Intelligence",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Loan Document Intelligence System")
st.markdown("---")

# Sidebar
st.sidebar.header("Configuration")
use_agent = st.sidebar.checkbox("Use AI Agent (LangChain)", value=False, help="Enable to use the full ReAct agent workflow. Requires OpenAI API Key.")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Document")
    uploaded_file = st.file_uploader("Choose a file (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.info(f"File uploaded: {uploaded_file.name}")
        
        # Upload to Backend
        if st.button("Process Document"):
            with st.spinner("Uploading and Processing..."):
                try:
                    # 1. Upload
                    files = {"file": uploaded_file.getvalue()}
                    upload_response = requests.post(f"{API_URL}/upload_document", files={"file": (uploaded_file.name, uploaded_file.getvalue())})
                    
                    if upload_response.status_code == 201:
                        file_data = upload_response.json()
                        file_path = file_data['file_path']
                        st.success("Upload Successful!")
                        
                        # 2. Process
                        endpoint = "/process_agent" if use_agent else "/process_manual"
                        payload = {"file_path": file_path}
                        
                        process_response = requests.post(f"{API_URL}{endpoint}", json=payload)
                        
                        if process_response.status_code == 200:
                            result = process_response.json()
                            st.session_state['result'] = result
                        else:
                            st.error(f"Processing Failed: {process_response.text}")
                    else:
                        st.error(f"Upload Failed: {upload_response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")

with col2:
    st.subheader("2. Analysis Report")
    
    if 'result' in st.session_state:
        result = st.session_state['result']
        
        # Display Risk Score
        risk_score = result.get('risk_score', 0)
        st.metric("Risk Score", f"{risk_score}/100", delta="High Risk" if risk_score >= 40 else "-Low Risk", delta_color="inverse")
        
        # Display Eligibility
        eligibility = result.get('eligibility', 'Unknown')
        if eligibility == "Eligible":
            st.success(f"✅ Status: {eligibility}")
        else:
            st.error(f"❌ Status: {eligibility}")
            
        # Tabs for details
        tab1, tab2, tab3 = st.tabs(["Extracted Data", "Validation Issues", "Fraud Check"])
        
        with tab1:
            st.json(result.get('extracted_data', {}))
            
        with tab2:
            issues = result.get('validation_issues', [])
            if issues:
                for issue in issues:
                    st.warning(issue)
            else:
                st.info("No validation issues found.")
                
        with tab3:
            fraud_status = result.get('fraud_status', 'Unknown')
            st.info(f"Fraud Status: {fraud_status}")
            
            fraud_reason = result.get('fraud_reason')
            if fraud_reason:
                st.error(f"Reason: {fraud_reason}")
            
        # Download Report
        st.download_button(
            label="Download Report JSON",
            data=json.dumps(result, indent=4),
            file_name="risk_report.json",
            mime="application/json"
        )
