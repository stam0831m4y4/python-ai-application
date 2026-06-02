import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.header("文章要約")
    st.caption("長い文章をAIが自動的に要約します。")

    text = st.text_area("要約したい文章", placeholder="要約したい文章をここに貼り付けてください。", height=200)

    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("要約スタイル", [
            "箇条書き（ポイント整理）",
            "短文まとめ（1〜3文）",
            "詳細まとめ（段落形式）",
            "TLDR（超要約・一言）",
        ])
        ratio = st.selectbox("要約の割合", ["元の10%程度", "元の20〜30%程度", "元の50%程度"])
    with col2:
        focus = st.text_input("重点的にまとめたいポイント（任意）", placeholder="例: 結論・数字・リスク")
        output_lang = st.selectbox("出力言語", ["入力と同じ言語", "日本語", "英語"])

    if st.button("要約する", type="primary", use_container_width=True):
        if not text:
            st.warning("要約したい文章を入力してください。")
            return

        prompt = f"""あなたは優秀な編集者です。以下の文章を要約してください。

【原文】
{text}

【要約の条件】
- スタイル: {style}
- 要約の割合: {ratio}
- 重点ポイント: {focus or "特になし"}
- 出力言語: {output_lang}

重要な情報を漏らさず、簡潔かつ正確にまとめてください。"""

        with st.spinner("要約中..."):
            st.write_stream(stream_response(prompt))
