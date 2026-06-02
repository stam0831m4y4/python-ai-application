import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.header("メール返信文生成")
    st.caption("受信したメールを貼り付けると、適切な返信文を生成します。")

    received = st.text_area("受信メールの内容", placeholder="返信したいメールの本文をここに貼り付けてください。", height=180)

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("返信のトーン", ["丁寧・ビジネス", "フレンドリー・カジュアル", "簡潔・要点のみ", "謝罪・お詫び", "断り・辞退"])
        sender_name = st.text_input("差出人の名前（任意）", placeholder="例: 田中様")
    with col2:
        your_name = st.text_input("自分の名前（署名用）", placeholder="例: 山田太郎")
        language = st.selectbox("返信言語", ["日本語", "英語", "日英両方"])

    intent = st.text_area("返信で伝えたい内容・意図", placeholder="例: 来週の会議に参加できること、日程調整を依頼したいこと", height=80)

    if st.button("返信文を生成", type="primary", use_container_width=True):
        if not received:
            st.warning("受信メールの内容を入力してください。")
            return

        prompt = f"""あなたはプロのビジネスライターです。以下の受信メールに対する返信文を作成してください。

【受信メール】
{received}

【返信の条件】
- トーン: {tone}
- 差出人: {sender_name or "相手"}
- 署名名: {your_name or "（名前）"}
- 返信言語: {language}
- 伝えたい内容: {intent or "適切に返信してください"}

件名（Re:〜）と本文を含めた完全なメール文を作成してください。"""

        with st.spinner("返信文を生成中..."):
            st.write_stream(stream_response(prompt))
