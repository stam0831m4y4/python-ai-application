import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。")
        _client = genai.Client(api_key=api_key)
    return _client


def stream_response(prompt: str, model: str = "gemini-2.5-flash"):
    client = get_client()
    response = client.models.generate_content_stream(model=model, contents=prompt)
    for chunk in response:
        if chunk.text:
            yield chunk.text
