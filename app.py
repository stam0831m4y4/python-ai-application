import streamlit as st
from tools import blog_writer, email_reply, summarizer, proofreader, sns_writer, style_converter, security_checker

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
    st.caption(TOOLS[st.session_state.selected_tool]["description"])

selected = st.session_state.selected_tool
TOOLS[selected]["module"].render()
