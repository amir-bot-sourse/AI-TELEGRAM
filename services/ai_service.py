import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-4o-mini"

URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_ai(message: str) -> str:

    if not OPENROUTER_API_KEY:
        return "❌ OPENROUTER_API_KEY تنظیم نشده است."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "AI Telegram Bot"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }

    try:

        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "⌛ زمان پاسخگویی هوش مصنوعی به پایان رسید."

    except requests.exceptions.HTTPError:
        return f"❌ خطای سرور OpenRouter:\n{response.text}"

    except Exception as e:
        return f"❌ {e}"
