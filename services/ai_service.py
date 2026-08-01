import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-4o-mini"

URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_ai(message, history=None):

    if not API_KEY:
        return "کلید هوش مصنوعی تنظیم نشده است."

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages
    }

    try:

        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        result = r.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:

        return str(e)
