import requests

OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # or "mistral", "phi", etc.

def ollama_infer(prompt: str, model: str = OLLAMA_MODEL):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_BASE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"Ollama error: {str(e)}"


# Optional wrapper for basic summarization
def summarize_content(text: str):
    prompt = f"Summarize this:\n{text}"
    return ollama_infer(prompt)
