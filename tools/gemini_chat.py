import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.title("💬 Gemini API チャット")
    st.caption("Gemini API に直接プロンプトを送信して応答を確認できます")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("メッセージを入力してください...")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_text = st.write_stream(stream_response(prompt))

        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    if st.session_state.chat_history:
        if st.button("履歴をクリア", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
