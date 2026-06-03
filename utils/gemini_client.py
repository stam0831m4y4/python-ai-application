import os
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_api_key() -> str:
    # Streamlit Secrets → 環境変数の順で取得
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY が設定されていません。Streamlit Secrets または .env ファイルを確認してください。")
    return key


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=_get_api_key())
    return _client


def stream_response(prompt: str, model: str = "gemini-2.5-flash"):
    client = get_client()
    response = client.models.generate_content_stream(model=model, contents=prompt)
    for chunk in response:
        if chunk.text:
            yield chunk.text
