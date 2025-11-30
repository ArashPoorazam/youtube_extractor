import os
import requests
import json
import time
import logging

# Import Files
from prompts import system_prompt


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

# System Instruction to define the agent's persona and rules
SYSTEM_PROMPT = system_prompt

def generate_response(user_prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        return "Error: API key not configured."

    url = f"{API_BASE_URL}{GEMINI_MODEL}:generateContent?key={api_key}"
    
    # Construct the payload
    payload = {
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
    }

    # Exponential Backoff variables
    max_retries = 5
    initial_delay = 1.0 

    for attempt in range(max_retries):
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            
            # Extract the generated text
            if result.get('candidates') and result['candidates'][0].get('content'):
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.warning(f"API response missing text content: {result}")
                return "الان نمیتونم کامل جوابتو بدم، بعدا بهم پیام بده.😓"

        except requests.exceptions.HTTPError as e:
            if response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                # Implement exponential backoff for transient errors
                delay = initial_delay * (2 ** attempt)
                # Note: We do not log retries as errors, as per instruction
                time.sleep(delay)
            else:
                logger.error(f"API Request failed with status {response.status_code}: {e}")
                return f"ارور HTTP دارم!!!"

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during API call: {e}")
            return "اینترنتم تموم شده لطفا به سازندم خبر بده. 🥲💔"
            
    return "فعلا خوابم میاد بعدا باهام چت کن. 😴"