import streamlit as st
from tools import blog_writer, email_reply, summarizer, proofreader, sns_writer, style_converter, security_checker, gemini_chat

st.set_page_config(
    page_title="AI ライティングツール",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOOLS = {
    "ブログ記事執筆": {
        "icon": "📝",
        "module": blog_writer,
        "description": "テーマを入力するだけでブログ記事を自動生成",
    },
    "メール返信文生成": {
        "icon": "📧",
        "module": email_reply,
        "description": "受信メールに対する返信文を作成",
    },
    "文章要約": {
        "icon": "📋",
        "module": summarizer,
        "description": "長文を指定スタイルで簡潔にまとめる",
    },
    "文章校正・添削": {
        "icon": "🔍",
        "module": proofreader,
        "description": "誤字脱字・表現・文体を修正",
    },
    "SNS投稿文生成": {
        "icon": "📱",
        "module": sns_writer,
        "description": "各SNSに最適化した投稿文を複数パターン生成",
    },
    "文体変換・リライト": {
        "icon": "🔄",
        "module": style_converter,
        "description": "文章のトーンや対象読者に合わせて文体を変換",
    },
    "セキュリティチェッカー": {
        "icon": "🛡️",
        "module": security_checker,
        "description": "Streamlit + LLM API アプリのセキュリティを診断しレポートを生成",
    },
    "Gemini API チャット": {
        "icon": "💬",
        "module": gemini_chat,
        "description": "Gemini API に直接プロンプトを送信して応答を確認",
    },
}

with st.sidebar:
    st.title("✍️ AI ライティングツール")
    st.divider()
    st.subheader("ツールを選択")

    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = list(TOOLS.keys())[0]

    for name, info in TOOLS.items():
        is_active = st.session_state.selected_tool == name
        if st.button(
            f"{info['icon']} {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.selected_tool = name
            st.rerun()

    st.divider()
    st.subheader("🔑 API キー設定")
    api_key_input = st.text_input(
        "Gemini API キー",
        value=st.session_state.get("gemini_api_key", ""),
        type="password",
        placeholder="AIzaSy...",
        label_visibility="collapsed",
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        st.success("APIキーを設定しました", icon="✅")
    else:
        st.session_state.gemini_api_key = ""
        st.caption("APIキーを入力してください")

    st.divider()
    st.caption(TOOLS[st.session_state.selected_tool]["description"])
    st.markdown(
        """
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #1a73e8, #0d47a1);
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
        ">⚡ Powered by Gemini API</div>
        """,
        unsafe_allow_html=True,
    )

selected = st.session_state.selected_tool
TOOLS[selected]["module"].render()
