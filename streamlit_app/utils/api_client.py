import requests

API_BASE_URL = "http://localhost:8000"  # Update if deployed elsewhere


def login_user(patient_id: str):
    response = requests.post(f"{API_BASE_URL}/login", json={"patient_id": patient_id})
    return response.json()


def send_message_to_bot(message: str, patient_id: str):
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json={"message": message, "patient_id": patient_id}
    )
    return response.json()


def check_symptoms(symptoms: str):
    response = requests.post(
        f"{API_BASE_URL}/check_symptoms",
        json={"symptoms": symptoms}
    )
    return response.json()


def get_drug_info(drug_name: str):
    response = requests.get(f"{API_BASE_URL}/drug_info", params={"name": drug_name})
    return response.json()


def get_chat_history(patient_id: str):
    response = requests.get(f"{API_BASE_URL}/chat_history", params={"patient_id": patient_id})
    return response.json()
