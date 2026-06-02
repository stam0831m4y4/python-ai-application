import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.header("文体変換・リライト")
    st.caption("文章のトーンや対象読者に合わせて文体を自由に変換します。")

    text = st.text_area("変換したい文章", placeholder="変換・リライトしたい文章を入力してください。", height=180)

    col1, col2 = st.columns(2)
    with col1:
        from_style = st.selectbox("現在の文体（任意）", [
            "自動判定",
            "カジュアル",
            "フォーマル・ビジネス",
            "学術・論文風",
            "話し言葉",
        ])
        to_style = st.selectbox("変換後の文体", [
            "フォーマル・ビジネス",
            "カジュアル・親しみやすい",
            "子供向け・わかりやすい",
            "専門家向け・技術的",
            "文学的・詩的",
            "ユーモア・面白い",
            "プレスリリース風",
            "FAQ・Q&A形式",
        ])
    with col2:
        target_reader = st.text_input("ターゲット読者（任意）", placeholder="例: 60代の主婦、大学生")
        preserve = st.text_input("変えずに保持したい要素（任意）", placeholder="例: 数字・固有名詞・専門用語")

    extra = st.text_area("その他の変換指示", placeholder="例: より行動を促す表現にしてください", height=60)

    if st.button("文体を変換", type="primary", use_container_width=True):
        if not text:
            st.warning("変換したい文章を入力してください。")
            return

        prompt = f"""あなたはプロのコピーライターです。以下の文章を指定された文体に変換・リライトしてください。

【元の文章】
{text}

【変換条件】
- 元の文体: {from_style}
- 変換後の文体: {to_style}
- ターゲット読者: {target_reader or "特定しない"}
- 保持する要素: {preserve or "特になし"}
- その他の指示: {extra or "特になし"}

意味・情報量を変えずに、指定された文体に自然に変換した文章を出力してください。"""

        with st.spinner("文体を変換中..."):
            st.write_stream(stream_response(prompt))
