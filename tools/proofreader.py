import streamlit as st
from utils.gemini_client import stream_response


def render():
    st.header("文章校正・添削")
    st.caption("文章の誤字脱字、表現の改善、文体の統一などを行います。")

    text = st.text_area("校正したい文章", placeholder="校正・添削したい文章をここに入力してください。", height=200)

    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox("校正モード", [
            "軽め（誤字脱字・明らかな間違いのみ）",
            "標準（文法・表現も含める）",
            "徹底（文体・流れ・説得力まで改善）",
        ])
        target_tone = st.selectbox("目標とする文体", [
            "現状のまま維持",
            "ビジネス・フォーマル",
            "親しみやすい・カジュアル",
            "学術・論文風",
        ])
    with col2:
        show_diff = st.checkbox("修正箇所を説明する", value=True)
        extra = st.text_input("特別な指示（任意）", placeholder="例: 敬語を統一してください")

    if st.button("校正する", type="primary", use_container_width=True):
        if not text:
            st.warning("校正したい文章を入力してください。")
            return

        diff_instruction = "修正した箇所とその理由を箇条書きで説明した後、" if show_diff else ""

        prompt = f"""あなたはプロの校正者・編集者です。以下の文章を校正・添削してください。

【原文】
{text}

【校正の条件】
- 校正モード: {mode}
- 目標文体: {target_tone}
- 特別な指示: {extra or "特になし"}

{diff_instruction}修正後の完全な文章を出力してください。"""

        with st.spinner("校正中..."):
            st.write_stream(stream_response(prompt))
