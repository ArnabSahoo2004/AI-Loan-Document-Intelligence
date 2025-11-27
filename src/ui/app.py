import streamlit as st
import requests
import json
import os
import plotly.graph_objects as go
import pandas as pd

# Config
API_URL = "http://localhost:5000"

st.set_page_config(
    page_title="AI Loan Document Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(to bottom right, #0f172a, #1e293b);
        color: #f8fafc;
    }
    
    /* Cards */
    .metric-card {
        background-color: #334155;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 14px;
        color: #94a3b8;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Success/Error Boxes */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        border: 1px solid #22c55e;
        color: #22c55e;
    }
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score", 'font': {'size': 24, 'color': "white"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#1e293b"}, # Hide default bar, use steps
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "#22c55e"}, # Green
                {'range': [40, 70], 'color': "#eab308"}, # Yellow
                {'range': [70, 100], 'color': "#ef4444"} # Red
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Arial"})
    return fig

def display_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Main App ---

# Header
st.title("🏦 AI Loan Document Intelligence")
st.markdown("### Intelligent Analysis for BFSI")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    use_agent = st.checkbox("Use AI Agent (LangChain)", value=False, help="Enable for advanced reasoning.")
    st.info("Upload a Salary Slip (PDF/Image) to get started.")

# Layout
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.success(f"File Selected: {uploaded_file.name}")
        
        if st.button("🚀 Analyze Document", use_container_width=True):
            with st.spinner("Processing with AI..."):
                try:
                    # 1. Upload
                    files = {"file": uploaded_file.getvalue()}
                    upload_response = requests.post(f"{API_URL}/upload_document", files={"file": (uploaded_file.name, uploaded_file.getvalue())})
                    
                    if upload_response.status_code == 201:
                        file_data = upload_response.json()
                        file_path = file_data['file_path']
                        
                        # 2. Process
                        endpoint = "/process_agent" if use_agent else "/process_manual"
                        payload = {"file_path": file_path}
                        
                        process_response = requests.post(f"{API_URL}{endpoint}", json=payload)
                        
                        if process_response.status_code == 200:
                            st.session_state['result'] = process_response.json()
                            st.toast("Analysis Complete!", icon="✅")
                        else:
                            st.error(f"Processing Failed: {process_response.text}")
                    else:
                        st.error(f"Upload Failed: {upload_response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")

with col2:
    if 'result' in st.session_state:
        result = st.session_state['result']
        
        st.subheader("📊 Analysis Report")
        
        # Risk Gauge
        risk_score = result.get('risk_score', 0)
        st.plotly_chart(create_gauge_chart(risk_score), use_container_width=True)
        
        # Eligibility Banner
        eligibility = result.get('eligibility', 'Unknown')
        if eligibility == "Eligible":
            st.success(f"✅ **Status: ELIGIBLE**")
        else:
            st.error(f"❌ **Status: NOT ELIGIBLE**")
            
        # Key Metrics Cards
        data = result.get('extracted_data', {})
        c1, c2, c3 = st.columns(3)
        with c1: display_card("Net Pay", f"₹{data.get('net_pay', 0):,.0f}")
        with c2: display_card("Total Earnings", f"₹{data.get('total_earnings', 0):,.0f}")
        with c3: display_card("Deductions", f"₹{data.get('total_deductions', 0):,.0f}")
        
        st.markdown("### 📝 Detailed Insights")
        tab1, tab2, tab3 = st.tabs(["📄 Extracted Data", "⚠️ Validation", "🕵️ Fraud Check"])
        
        with tab1:
            # Convert JSON to DataFrame for better display
            flat_data = {k: v for k, v in data.items() if not isinstance(v, (list, dict))}
            # Handle lists separately if needed
            if 'names' in data: flat_data['names'] = ", ".join(data['names'])
            
            df = pd.DataFrame(list(flat_data.items()), columns=["Field", "Value"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        with tab2:
            issues = result.get('validation_issues', [])
            if issues:
                for issue in issues:
                    st.warning(f"⚠️ {issue}")
            else:
                st.info("✅ No validation issues found.")
                
        with tab3:
            fraud_status = result.get('fraud_status', 'Unknown')
            st.info(f"**Fraud Status:** {fraud_status}")
            
            fraud_reason = result.get('fraud_reason')
            if fraud_reason:
                st.error(f"**Reason:** {fraud_reason}")
                
        # Download
        st.download_button(
            label="📥 Download Full Report",
            data=json.dumps(result, indent=4),
            file_name="risk_report.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        # Placeholder when no result
        st.info("👈 Upload a document to see the analysis here.")
        st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=100) # Generic placeholder icon
