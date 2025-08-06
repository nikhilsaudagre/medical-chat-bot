import streamlit as st
import requests
import uuid
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Page config
st.set_page_config(page_title="MedAssistant", page_icon="🤖", layout="wide")

# Initialize session
if "session_id" not in st.session_state:
    response = requests.post(f"{BACKEND_URL}/sessions/")
    if response.status_code == 200:
        st.session_state.session_id = response.json()["session_id"]
    else:
        st.error("❌ Failed to create session")
        st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm MedAssistant, your AI healthcare companion. How can I help you today?"
    })

# Initialize symptom reports
if "symptom_reports" not in st.session_state:
    st.session_state.symptom_reports = []

# Sidebar
with st.sidebar:
    st.header("🛠️ MedAssistant Tools")
    st.caption(f"Session ID: `{st.session_state.session_id}`")
    st.divider()

    # Symptom Checker
    with st.expander("🔍 Symptom Checker"):
        symptoms = st.multiselect(
            "Select symptoms",
            ["Headache", "Fever", "Cough", "Nausea", "Dizziness", 
             "Fatigue", "Pain", "Rash", "Vomiting", "Diarrhea"]
        )
        severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
        duration = st.selectbox("Duration", ["< 24 hours", "1–3 days", "4–7 days", "Over a week"])
        additional_info = st.text_area("Additional information")

        if st.button("Analyze Symptoms"):
            if not symptoms:
                st.error("Please select at least one symptom.")
            else:
                report_data = {
                    "session_id": st.session_state.session_id,
                    "symptoms": symptoms,
                    "severity": severity,
                    "duration": duration,
                    "additional_info": additional_info
                }
                response = requests.post(f"{BACKEND_URL}/symptom-check/", json=report_data)
                if response.status_code == 200:
                    report = response.json()
                    st.session_state.symptom_reports.append(report)
                    st.success("✅ Symptom analysis completed!")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"I've analyzed your symptoms:\n\n{report['analysis_result']}"
                    })
                else:
                    st.error(f"Failed: {response.text}")

    # Drug Info
    with st.expander("💊 Drug Information"):
        drug_name = st.text_input("Enter drug name")
        if st.button("Get Drug Info"):
            if drug_name:
                response = requests.post(f"{BACKEND_URL}/drug-info/", json={"drug_name": drug_name})
                if response.status_code == 200:
                    drug_info = response.json()
                    info_text = (
                        f"**{drug_info['name']}**\n\n"
                        f"**Description:** {drug_info['description']}\n\n"
                        f"**Usage:** {drug_info['usage']}\n\n"
                        f"**Side Effects:**\n"
                        + "\n".join([f"- {eff}" for eff in drug_info['side_effects']]) + "\n\n"
                        f"**Interactions:**\n"
                        + "\n".join([f"- {intr}" for intr in drug_info['interactions']])
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": info_text
                    })
                else:
                    st.error(f"Failed: {response.text}")
            else:
                st.error("Please enter a drug name.")

    # Chat history
    st.divider()
    st.subheader("🗑️ Chat History")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Chat history cleared. How can I help you today?"
        })

    # Symptom Reports
    if st.session_state.symptom_reports:
        st.subheader("📋 Symptom Reports")
        for i, report in enumerate(st.session_state.symptom_reports):
            with st.expander(f"Report #{i+1} - {report['created_at']}"):
                st.write(f"**Symptoms:** {', '.join(report['symptoms'])}")
                st.write(f"**Severity:** {report['severity']}")
                st.write(f"**Duration:** {report['duration']}")
                st.write(f"**Analysis:** {report['analysis_result']}")

# Main Chat Interface
st.title("🤖 MedAssistant")
st.caption("Ask anything about your health, symptoms, or medications.")

# Show messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a medical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to backend
    chat_data = {
        "session_id": st.session_state.session_id,
        "message": prompt
    }
    response = requests.post(f"{BACKEND_URL}/chat/", json=chat_data)

    if response.status_code == 200:
        ai_response = response.json()["response"]
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
    else:
        error_msg = f"❌ Error: {response.status_code} - {response.text}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.error(error_msg)
