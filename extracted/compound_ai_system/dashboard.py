
import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Compound AI Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000"

# Styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc00;
        font-weight: bold;
    }
    .agent-box {
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200, response.json()
    except:
        return False, {}

def analyze_claim(claim_data):
    try:
        response = requests.post(f"{API_URL}/analyze", json=claim_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# Sidebar
st.sidebar.title("🛡️ Fraud Detection")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", ["Dashboard", "Real-time Analysis", "System Health"])

st.sidebar.markdown("---")
health_status, health_data = check_api_health()
if health_status:
    st.sidebar.success(f"System Online (Aggregated {health_data.get('agents_count', 0)} agents)")
else:
    st.sidebar.error("System Offline")

# Main Page
if page == "Dashboard":
    st.title("📊 Fraud Detection Dashboard")
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Mock data for demonstration if API is fresh
    total_analyzed = 1250
    fraud_detected = 45
    pending_review = 12
    saved_amount = 450000
    
    with col1:
        st.metric("Total Claims Analyzed", f"{total_analyzed:,}", "+25 today")
    with col2:
        st.metric("Fraud Detected", f"{fraud_detected}", "+2 today", delta_color="inverse")
    with col3:
        st.metric("Pending Review", f"{pending_review}", "-5")
    with col4:
        st.metric("Potential Savings", f"${saved_amount:,.0f}", "+$15k")

    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Risk Distribution")
        # Mock Data
        df_risk = pd.DataFrame({
            "Risk Level": ["Low", "Medium", "High", "Critical"],
            "Count": [900, 250, 80, 20]
        })
        fig = px.pie(df_risk, values='Count', names='Risk Level', 
                     color='Risk Level',
                     color_discrete_map={
                         'Low': '#2ecc71',
                         'Medium': '#f1c40f', 
                         'High': '#e67e22',
                         'Critical': '#e74c3c'
                     },
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Agent Contribution")
        # Mock Data
        df_agent = pd.DataFrame({
            "Agent": ["Statistical", "ML Pattern", "Rule Compliance", "Feature Store", "Graph"],
            "Anomaly Detection Rate": [15, 25, 40, 10, 10]
        })
        fig = px.bar(df_agent, x="Agent", y="Anomaly Detection Rate", color="Agent")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Real-time Analysis":
    st.title("🔍 Real-time Claim Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Claim Details")
        
        # Templates
        template = st.selectbox("Select Template", ["Custom", "Normal Claim", "Suspicious (High Amount)", "Fraud (Sanctioned Provider)"])
        
        if template == "Normal Claim":
            default_claim = {
                "claim_id": "CLM001", "provider_id": "PRV010", "beneficiary_id": "BEN001",
                "procedure_code": "99213", "diagnosis_code": "J06.9", "claim_amount": 120.0,
                "service_date": "2024-11-15T00:00:00", "provider_specialty": "General Practice",
                "beneficiary_age": 45, "beneficiary_state": "CA"
            }
        elif template == "Suspicious (High Amount)":
             default_claim = {
                "claim_id": "CLM002", "provider_id": "PRV001", "beneficiary_id": "BEN002",
                "procedure_code": "93306", "diagnosis_code": "M54.5", "claim_amount": 8500.0,
                "service_date": "2024-11-16T00:00:00", "provider_specialty": "Cardiology",
                "beneficiary_age": 28, "beneficiary_state": "NY"
            }
        elif template == "Fraud (Sanctioned Provider)":
             default_claim = {
                "claim_id": "CLM003", "provider_id": "PRV999", "beneficiary_id": "BEN003",
                "procedure_code": "99215", "diagnosis_code": "Z00.00", "claim_amount": 950.0,
                "service_date": "2024-11-17T00:00:00", "provider_specialty": "General Practice",
                "beneficiary_age": 70, "beneficiary_state": "FL"
            }
        else:
            default_claim = {
                "claim_id": "CLM000", "provider_id": "", "beneficiary_id": "",
                "procedure_code": "", "diagnosis_code": "", "claim_amount": 0.0,
                "service_date": "2024-11-15T00:00:00", "provider_specialty": "",
                "beneficiary_age": 0, "beneficiary_state": ""
            }

        with st.form("claim_form"):
            c_id = st.text_input("Claim ID", default_claim["claim_id"])
            p_id = st.text_input("Provider ID", default_claim["provider_id"])
            amt = st.number_input("Amount ($)", value=default_claim["claim_amount"])
            
            submitted = st.form_submit_button("🚀 Analyze Claim")
            
        if submitted:
            # Prepare Request
            claim_req = default_claim.copy()
            claim_req["claim_id"] = c_id
            claim_req["provider_id"] = p_id
            claim_req["claim_amount"] = amt
            
            with st.spinner("🤖 Coordinating Agents..."):
                # Simulate parallel agent thinking visualization
                progress_container = st.empty()
                for i in range(100):
                    time.sleep(0.01)
                    progress_container.progress(i + 1, text="Agents Analyzing...")
                
                result = analyze_claim(claim_req)
                progress_container.empty()
                
            if result:
                st.session_state['last_result'] = result

    with col2:
        st.subheader("🧠 Analysis Results")
        
        if 'last_result' in st.session_state:
            res = st.session_state['last_result']
            
            # Header
            risk_color = {
                "low": "green", "medium": "orange", "high": "red", "critical": "darkred"
            }.get(res['risk_level'], "grey")
            
            st.markdown(f"""
            <div style="background-color: {risk_color}; padding: 20px; border-radius: 10px; color: white;">
                <h2>Risk Level: {res['risk_level'].upper()}</h2>
                <h1>Score: {res['overall_risk_score']:.3f}</h1>
                <h3>Action: {res['recommended_action']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📝 Explanation")
            st.info(res['explanation'])
            
            st.markdown("### 🗝️ Key Findings")
            for finding in res['key_findings']:
                st.warning(f"• {finding}")
            
            st.markdown("---")
            st.markdown("### 🤖 Individual Agent Assessments")
            
            for agent in res['agent_results']:
                with st.expander(f"{agent['agent_name']} (Risk: {agent['risk_score']:.2f})"):
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        st.metric("Confidence", f"{agent['confidence']:.2f}")
                    with col_b:
                        for f in agent['findings']:
                            st.markdown(f"- {f}")
                        st.json(agent['evidence'])

elif page == "System Health":
    st.title("🏥 System Health")
    
    status, data = check_api_health()
    
    if status:
        st.success("System Operational")
        st.json(data)
        
        st.subheader("Active Agents")
        try:
            agents = requests.get(f"{API_URL}/agents").json()
            st.table(pd.DataFrame(agents))
        except:
            st.error("Could not fetch agents")
    else:
        st.error("System Unreachable")
        st.warning(f"Please ensure the API server is running at {API_URL}")

