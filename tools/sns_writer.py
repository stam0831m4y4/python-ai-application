import streamlit as st
from utils.gemini_client import stream_response


PLATFORM_INFO = {
    "Twitter/X": {"limit": "140文字以内", "style": "簡潔・インパクト重視、ハッシュタグ付き"},
    "Instagram": {"limit": "キャプション形式", "style": "感情的・共感を呼ぶ、絵文字・ハッシュタグ豊富"},
    "LinkedIn": {"limit": "ビジネスSNS", "style": "専門的・実績アピール、ビジネス向け"},
    "Facebook": {"limit": "長文可", "style": "親しみやすく・詳細に、コミュニティ意識"},
    "Threads": {"limit": "500文字以内", "style": "会話的・オープン、ハッシュタグ少なめ"},
    "note": {"limit": "ブログ形式", "style": "読み物として完結、読者との距離感近め"},
}


def render():
    st.header("SNS投稿文生成")
    st.caption("テーマや内容を入力すると、各SNSに最適化した投稿文を生成します。")

    topic = st.text_area("投稿したい内容・テーマ", placeholder="例: 新しいカフェに行ってきました。雰囲気が良くてコーヒーが絶品でした。", height=100)

    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("プラットフォーム", list(PLATFORM_INFO.keys()))
        count = st.number_input("生成するパターン数", min_value=1, max_value=5, value=3)
    with col2:
        tone = st.selectbox("投稿のトーン", ["ポジティブ・明るい", "クール・シンプル", "ユーモア・面白い", "感動的・心に響く", "情報提供・教育的"])
        use_emoji = st.checkbox("絵文字を使う", value=True)
        use_hashtag = st.checkbox("ハッシュタグを付ける", value=True)

    extra = st.text_input("その他の要望（任意）", placeholder="例: フォロワーにシェアを促す文を入れてほしい")

    if st.button("投稿文を生成", type="primary", use_container_width=True):
        if not topic:
            st.warning("投稿したい内容を入力してください。")
            return

        info = PLATFORM_INFO[platform]
        emoji_instruction = "絵文字を積極的に使ってください。" if use_emoji else "絵文字は使わないでください。"
        hashtag_instruction = "適切なハッシュタグを付けてください。" if use_hashtag else "ハッシュタグは付けないでください。"

        prompt = f"""あなたはSNSマーケティングの専門家です。以下の条件で{platform}向けの投稿文を{count}パターン作成してください。

【投稿内容】
{topic}

【条件】
- プラットフォーム: {platform}（{info["limit"]}、{info["style"]}）
- トーン: {tone}
- {emoji_instruction}
- {hashtag_instruction}
- その他: {extra or "特になし"}

各パターンに「パターン1」「パターン2」のような見出しをつけて、それぞれ独立した投稿文として出力してください。"""

        with st.spinner("投稿文を生成中..."):
            st.write_stream(stream_response(prompt))
