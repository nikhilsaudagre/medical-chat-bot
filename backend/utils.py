import requests
import uuid
import re
from backend.config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {
    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def get_ai_response(messages, max_tokens=500, temperature=0.7, model=None):
    payload = {
        "model": model or settings.GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(GROQ_API_URL, headers=GROQ_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq API Error:", e)
        return "⚠️ Sorry, the AI assistant is currently unavailable. Please try again later."

def analyze_symptoms(symptoms: list, severity: str, duration: str, additional_info: str):
    prompt = f"""
    Analyze the following symptoms reported by a patient:
    Symptoms: {", ".join(symptoms)}
    Severity: {severity}
    Duration: {duration}
    Additional info: {additional_info or "None"}
    
    Provide:
    1. 2-3 possible conditions (with likelihood percentages)
    2. Recommended next steps
    3. Red flags to watch for
    4. When to seek immediate care

    Structure as a conversational response. Remember:
    - NEVER diagnose
    - Always recommend professional consultation
    - Use simple language
    - Include disclaimer
    """

    messages = [
        {"role": "system", "content": "You are a professional medical assistant."},
        {"role": "user", "content": prompt}
    ]

    return get_ai_response(messages, temperature=0.2)

def get_drug_info(drug_name: str):
    prompt = f"""
    Provide detailed information about the drug: {drug_name}
    Include:
    - Description
    - Common usage
    - Side effects (list 5-7)
    - Important interactions (list 3-5)

    Format the response as:
    Description: [text]
    Usage: [text]
    Side Effects:
    - [effect1]
    - [effect2]
    Interactions:
    - [interaction1]
    - [interaction2]
    """

    messages = [
        {"role": "system", "content": "You are a professional pharmacist."},
        {"role": "user", "content": prompt}
    ]

    response = get_ai_response(messages, temperature=0.1)

    # Parse the response
    result = {
        "name": drug_name,
        "description": "",
        "usage": "",
        "side_effects": [],
        "interactions": []
    }

    sections = {
        "Description": "description",
        "Usage": "usage",
        "Side Effects": "side_effects",
        "Interactions": "interactions"
    }

    current_section = None
    for line in response.split("\n"):
        line = line.strip()
        if not line:
            continue

        section_found = False
        for section, key in sections.items():
            if line.startswith(section + ":"):
                current_section = key
                section_found = True
                content = line[len(section)+1:].strip()
                if content and key in ["description", "usage"]:
                    result[key] = content
                break

        if section_found:
            continue

        if current_section and line.startswith("-"):
            content = line[1:].strip()
            if current_section in ["side_effects", "interactions"]:
                result[current_section].append(content)
            elif current_section in ["description", "usage"]:
                result[current_section] += " " + content
        elif current_section and current_section in ["description", "usage"]:
            result[current_section] += " " + line

    return result
