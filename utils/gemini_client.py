import os
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_api_key() -> str:
    # 画面入力 → Streamlit Secrets → 環境変数の順で取得
    try:
        key = st.session_state.get("gemini_api_key")
        if key:
            return key
    except Exception:
        pass
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY が設定されていません。サイドバーにAPIキーを入力してください。")
    return key


def get_client() -> genai.Client:
    # 画面入力キーが変わる可能性があるため毎回生成
    return genai.Client(api_key=_get_api_key())


def stream_response(prompt: str, model: str = "gemini-2.0-flash"):
    from google.genai import errors as genai_errors
    client = get_client()
    try:
        response = client.models.generate_content_stream(model=model, contents=prompt)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except genai_errors.ClientError as e:
        raise RuntimeError(f"Gemini API エラー (ステータス: {e.status_code}): {e.message}") from e
