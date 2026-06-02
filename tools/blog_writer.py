import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.header("ブログ記事執筆")
    st.caption("テーマや条件を入力すると、ブログ記事を自動生成します。")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("記事のテーマ・タイトル", placeholder="例: 初心者向けPythonの始め方")
        target = st.text_input("ターゲット読者", placeholder="例: プログラミング初心者")
    with col2:
        tone = st.selectbox("文体・トーン", ["親しみやすい・カジュアル", "丁寧・フォーマル", "専門的・技術的", "エンタメ・ユーモア"])
        length = st.selectbox("記事の長さ", ["短め（500字程度）", "標準（1000〜1500字）", "長め（2000字以上）"])

    keywords = st.text_input("含めたいキーワード（カンマ区切り）", placeholder="例: Python, 入門, 環境構築")
    extra = st.text_area("その他の要望・補足情報", placeholder="例: SEOを意識した構成にしてください", height=80)

    if st.button("記事を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("テーマを入力してください。")
            return

        prompt = f"""あなたはプロのブログライターです。以下の条件でブログ記事を執筆してください。

テーマ: {topic}
ターゲット読者: {target or "一般読者"}
文体・トーン: {tone}
記事の長さ: {length}
含めるキーワード: {keywords or "特になし"}
その他要望: {extra or "特になし"}

記事は以下の構成で書いてください：
- 魅力的な導入文（読者を引き込む）
- 複数の見出し（## を使用）と本文
- まとめ・結論

Markdownで記述してください。"""

        with st.spinner("記事を生成中..."):
            st.write_stream(stream_response(prompt))
