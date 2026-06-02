import re
import streamlit as st
from datetime import datetime
from pathlib import Path


# =====================
# チェックパターン定義
# =====================

PROMPT_INJECTION_PATTERNS = [
    (r"ignore\s+(previous|all|above|prior)\s+instruction", "前の指示を無視させる試み"),
    (r"you\s+are\s+now\s+(a|an|the)", "AIのロール変更の試み"),
    (r"forget\s+(everything|all|your|the)\s+(previous|instructions|rules)", "指示リセットの試み"),
    (r"(system|assistant|user)\s*:", "システムロールの偽装"),
    (r"<\s*(system|instruction|prompt)\s*>", "タグによるロール偽装"),
    (r"act\s+as\s+(if|a|an|though)", "キャラクター偽装の試み"),
    (r"(DAN|jailbreak|jail\s*break)", "ジェイルブレイク試み"),
    (r"(override|bypass|disable)\s+(safety|filter|restriction|guideline)", "安全制約の回避試み"),
    (r"(reveal|show|print|output)\s+(your\s+)?(system\s+prompt|instruction|api\s+key|secret)", "システム情報の漏洩誘導"),
    (r"```[\s\S]{50,}```", "大型コードブロックの埋め込み"),
]

PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "メールアドレス"),
    (r"\b\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b", "電話番号の可能性"),
    (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "クレジットカード番号の可能性"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN（米国社会保障番号）の可能性"),
    (r"(パスワード|password|passwd|pwd)\s*[:=]\s*\S+", "パスワードの平文記載"),
]

HARDCODED_SECRET_PATTERNS = [
    (r'(api[_-]?key|apikey)\s*=\s*["\']([^"\']{10,})["\']', "ハードコードされたAPIキー"),
    (r'(secret|password|passwd|token)\s*=\s*["\']([^"\']{6,})["\']', "ハードコードされたシークレット"),
    (r'(GEMINI|OPENAI|ANTHROPIC|AZURE)[_A-Z]*\s*=\s*["\']([A-Za-z0-9_\-]{10,})["\']', "ハードコードされたLLM APIキー"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI形式のAPIキー"),
    (r'AIza[A-Za-z0-9_\-]{35}', "Google APIキー"),
]

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_LABEL = {
    "critical": "🔴 重大",
    "high": "🟠 高",
    "medium": "🟡 中",
    "low": "🔵 低",
    "info": "⚪ 情報",
}


# =====================
# 入力テキストチェック
# =====================

def check_prompt_injection(text: str) -> list:
    findings = []
    for pattern, description in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append({
                "severity": "high",
                "category": "プロンプトインジェクション",
                "description": description,
                "detail": f"検出パターン: `{pattern}`",
            })
    return findings


def check_pii(text: str) -> list:
    findings = []
    for pattern, description in PII_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            findings.append({
                "severity": "medium",
                "category": "個人情報（PII）検出",
                "description": f"{description}が含まれている可能性があります",
                "detail": f"{len(matches)} 件検出。LLMへ送信する前に削除または匿名化を検討してください。",
            })
    return findings


def check_input_length(text: str, max_chars: int) -> list:
    if len(text) > max_chars:
        return [{
            "severity": "medium",
            "category": "入力長チェック",
            "description": f"入力が最大許容文字数（{max_chars:,}文字）を超過しています",
            "detail": f"現在: {len(text):,}文字。超過分はAPIコスト増大やDoS攻撃に悪用される可能性があります。",
        }]
    return []


# =====================
# プロジェクト静的解析
# =====================

def scan_secrets(project_root: Path) -> list:
    findings = []
    py_files = [
        f for f in project_root.rglob("*.py")
        if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]
    for file_path in py_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for pattern, description in HARDCODED_SECRET_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append({
                        "severity": "critical",
                        "category": "ハードコードシークレット",
                        "description": description,
                        "detail": f"ファイル: `{file_path.relative_to(project_root)}`。環境変数（.env）に移行してください。",
                    })
        except Exception:
            pass
    if not findings:
        findings.append({
            "severity": "info",
            "category": "ハードコードシークレット",
            "description": "ハードコードされたシークレットは検出されませんでした",
            "detail": f"スキャン対象: {len(py_files)} ファイル",
        })
    return findings


def check_env_security(project_root: Path) -> list:
    findings = []
    env_file = project_root / ".env"
    gitignore = project_root / ".gitignore"

    if env_file.exists():
        findings.append({
            "severity": "info",
            "category": "環境設定",
            "description": ".env ファイルが存在します（APIキーが適切に管理されています）",
            "detail": "環境変数での管理は良好なプラクティスです。",
        })
        if gitignore.exists():
            gi_content = gitignore.read_text(encoding="utf-8", errors="ignore")
            if ".env" in gi_content:
                findings.append({
                    "severity": "info",
                    "category": "Gitセキュリティ",
                    "description": ".env は .gitignore で除外されています",
                    "detail": "誤ってリポジトリに含まれるリスクがありません（良好）。",
                })
            else:
                findings.append({
                    "severity": "critical",
                    "category": "Gitセキュリティ",
                    "description": ".env が .gitignore に含まれていません",
                    "detail": ".gitignore に `.env` を追加してください。このままではAPIキーがリポジトリに混入する危険があります。",
                })
        else:
            findings.append({
                "severity": "high",
                "category": "Gitセキュリティ",
                "description": ".gitignore ファイルが見つかりません",
                "detail": ".gitignore を作成し、`.env` を除外してください。",
            })
    else:
        findings.append({
            "severity": "high",
            "category": "環境設定",
            "description": ".env ファイルが見つかりません",
            "detail": ".env.example を参考に .env を作成し、APIキーを設定してください。",
        })

    return findings


def check_input_validation(project_root: Path) -> list:
    findings = []
    tools_dir = project_root / "tools"
    if not tools_dir.exists():
        return findings

    py_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]
    insufficient = []
    for f in py_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"(st\.warning|st\.error|if not |len\(|\.strip\(\))", content):
            insufficient.append(f.name)

    if insufficient:
        findings.append({
            "severity": "medium",
            "category": "入力バリデーション",
            "description": "入力検証が不十分な可能性があるファイルがあります",
            "detail": ", ".join(insufficient) + " — 空入力チェック等の追加を検討してください。",
        })
    else:
        findings.append({
            "severity": "info",
            "category": "入力バリデーション",
            "description": "全ツールで入力バリデーションが実装されています",
            "detail": f"{len(py_files)} ファイルで確認済み。",
        })
    return findings


def check_rate_limiting(project_root: Path) -> list:
    all_py = [f for f in project_root.rglob("*.py") if "__pycache__" not in str(f)]
    for f in all_py:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(rate.?limit|throttl|time\.sleep|RateLimiter)", content, re.IGNORECASE):
            return [{
                "severity": "info",
                "category": "レートリミット",
                "description": "レートリミットの実装が確認されました",
                "detail": "APIの過剰使用・悪用が抑制されています（良好）。",
            }]
    return [{
        "severity": "medium",
        "category": "レートリミット",
        "description": "APIへのレートリミットが実装されていません",
        "detail": "API使用量の急増・コスト爆発・DoS攻撃に対して脆弱です。リクエスト間隔制御や使用量上限の実装を推奨します。",
    }]


def check_streamlit_config(project_root: Path) -> list:
    findings = []
    config_path = project_root / ".streamlit" / "config.toml"

    if config_path.exists():
        content = config_path.read_text(encoding="utf-8", errors="ignore")
        findings.append({
            "severity": "info",
            "category": "Streamlit設定",
            "description": ".streamlit/config.toml が存在します",
            "detail": "セキュリティ設定が明示的に管理されています。",
        })
        if re.search(r"enableXsrfProtection\s*=\s*false", content, re.IGNORECASE):
            findings.append({
                "severity": "high",
                "category": "CSRF保護",
                "description": "CSRF保護（enableXsrfProtection）が無効化されています",
                "detail": "`enableXsrfProtection = true` に変更してください。",
            })
    else:
        findings.append({
            "severity": "low",
            "category": "Streamlit設定",
            "description": ".streamlit/config.toml が見つかりません",
            "detail": "セキュリティ設定を明示管理するため config.toml の作成を推奨します（CSRF保護はデフォルトで有効）。",
        })
    return findings


def check_dependencies(project_root: Path) -> list:
    findings = []
    req_file = project_root / "requirements.txt"

    if not req_file.exists():
        return [{
            "severity": "medium",
            "category": "依存パッケージ",
            "description": "requirements.txt が見つかりません",
            "detail": "依存パッケージをバージョン固定で管理してください。",
        }]

    lines = [
        l.strip() for l in req_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        if l.strip() and not l.startswith("#")
    ]
    loose = [l for l in lines if re.search(r">=", l) and "==" not in l]
    unpinned = [l for l in lines if not re.search(r"[=<>!~]", l)]

    if unpinned:
        findings.append({
            "severity": "low",
            "category": "依存パッケージ",
            "description": "バージョン未指定のパッケージがあります",
            "detail": ", ".join(unpinned) + " — サプライチェーン攻撃への対策としてバージョン固定を推奨します。",
        })
    if loose:
        findings.append({
            "severity": "info",
            "category": "依存パッケージ",
            "description": "最低バージョンのみ指定のパッケージがあります",
            "detail": ", ".join(loose) + " — 再現性のため `==` による固定を推奨します。",
        })
    if not unpinned and not loose:
        findings.append({
            "severity": "info",
            "category": "依存パッケージ",
            "description": "全パッケージがバージョン管理されています",
            "detail": f"{len(lines)} パッケージ確認済み（良好）。",
        })
    return findings


# =====================
# レポート描画
# =====================

def _build_text_report(findings: list, title: str, target: str, now: str, counts: dict, overall: str) -> str:
    sev_ja = {"critical": "重大", "high": "高", "medium": "中", "low": "低", "info": "情報"}
    lines = [
        "=" * 64,
        f"  {title}",
        "=" * 64,
        f"生成日時 : {now}",
        f"対象     : {target}",
        f"総合評価 : {overall}",
        "",
        "[ サマリー ]",
        f"  重大 (Critical) : {counts['critical']}",
        f"  高   (High)     : {counts['high']}",
        f"  中   (Medium)   : {counts['medium']}",
        f"  低   (Low)      : {counts['low']}",
        f"  情報 (Info)     : {counts['info']}",
        "",
        "[ 詳細チェック結果 ]",
    ]
    for i, f in enumerate(sorted(findings, key=lambda x: SEVERITY_ORDER[x["severity"]]), 1):
        lines += [
            "",
            f"  [{i}] {f['category']}",
            f"      重大度 : {sev_ja[f['severity']]}",
            f"      内容   : {f['description']}",
            f"      詳細   : {f['detail']}",
        ]
    lines += ["", "=" * 64]
    return "\n".join(lines)


def render_report(findings: list, title: str, target: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_ORDER}
    issues = counts["critical"] + counts["high"] + counts["medium"] + counts["low"]

    if issues == 0:
        overall = "✅ 問題なし"
    elif counts["critical"] > 0:
        overall = "🔴 重大な問題あり"
    elif counts["high"] > 0:
        overall = "🟠 高リスクの問題あり"
    elif counts["medium"] > 0:
        overall = "🟡 中程度のリスクあり"
    else:
        overall = "🔵 軽微な問題のみ"

    st.markdown(f"## {title}")
    st.caption(f"生成日時: {now}　|　対象: {target}")
    st.divider()

    st.markdown("### 総合評価")
    st.markdown(f"**{overall}**")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔴 重大", counts["critical"])
    c2.metric("🟠 高", counts["high"])
    c3.metric("🟡 中", counts["medium"])
    c4.metric("🔵 低", counts["low"])
    c5.metric("⚪ 情報", counts["info"])

    st.divider()
    st.markdown("### 詳細チェック結果")

    for f in sorted(findings, key=lambda x: SEVERITY_ORDER[x["severity"]]):
        label = SEVERITY_LABEL[f["severity"]]
        expanded = f["severity"] in ("critical", "high")
        with st.expander(f"{label}　{f['category']}：{f['description']}", expanded=expanded):
            st.markdown(f"**カテゴリ:** {f['category']}")
            st.markdown(f"**重大度:** {label}")
            st.markdown(f"**詳細:** {f['detail']}")

    st.divider()
    report_text = _build_text_report(findings, title, target, now, counts, overall)
    st.download_button(
        label="📄 レポートをダウンロード（テキスト）",
        data=report_text,
        file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True,
    )


# =====================
# メインrender
# =====================

def render():
    st.header("セキュリティチェッカー")
    st.caption("Streamlit + LLM API アプリのセキュリティを診断し、レポートを生成します。")

    tab1, tab2 = st.tabs(["🔍 入力テキスト診断", "🏗️ プロジェクトスキャン"])

    with tab1:
        st.markdown("#### ユーザー入力のセキュリティ診断")
        st.caption(
            "LLM に送信する前にユーザー入力を検査します。"
            "プロンプトインジェクション・個人情報（PII）・入力長の3軸でチェックします。"
        )

        input_text = st.text_area(
            "検査するテキスト",
            placeholder="診断したいユーザー入力やプロンプトをここに貼り付けてください...",
            height=200,
        )
        max_chars = st.slider("最大許容文字数", min_value=500, max_value=50000, value=10000, step=500)

        if st.button("入力テキストを診断", type="primary", use_container_width=True):
            if not input_text.strip():
                st.warning("テキストを入力してください。")
            else:
                findings = (
                    check_prompt_injection(input_text)
                    + check_pii(input_text)
                    + check_input_length(input_text, max_chars)
                )
                if not findings:
                    findings.append({
                        "severity": "info",
                        "category": "診断結果",
                        "description": "検出されたリスクはありません",
                        "detail": "プロンプトインジェクション・PII・入力長の全チェックをパスしました。",
                    })
                render_report(
                    findings,
                    "入力テキスト セキュリティレポート",
                    f"{len(input_text):,} 文字のテキスト",
                )

    with tab2:
        st.markdown("#### プロジェクト静的解析")
        st.caption("ファイル構成・設定・ソースコードを静的解析し、セキュリティリスクを洗い出します。")

        default_path = str(Path(__file__).parent.parent)
        project_path = st.text_input("プロジェクトルートパス", value=default_path)

        all_checks = [
            "ハードコードシークレットスキャン",
            "環境設定・Gitセキュリティ",
            "入力バリデーション確認",
            "レートリミット確認",
            "Streamlit設定確認",
            "依存パッケージ確認",
        ]
        selected_checks = st.multiselect("実行するチェック項目", options=all_checks, default=all_checks)

        if st.button("プロジェクトをスキャン", type="primary", use_container_width=True):
            root = Path(project_path)
            if not root.exists():
                st.error(f"パスが存在しません: {project_path}")
            else:
                findings = []
                with st.spinner("スキャン中..."):
                    if "ハードコードシークレットスキャン" in selected_checks:
                        findings += scan_secrets(root)
                    if "環境設定・Gitセキュリティ" in selected_checks:
                        findings += check_env_security(root)
                    if "入力バリデーション確認" in selected_checks:
                        findings += check_input_validation(root)
                    if "レートリミット確認" in selected_checks:
                        findings += check_rate_limiting(root)
                    if "Streamlit設定確認" in selected_checks:
                        findings += check_streamlit_config(root)
                    if "依存パッケージ確認" in selected_checks:
                        findings += check_dependencies(root)

                if not findings:
                    findings.append({
                        "severity": "info",
                        "category": "診断結果",
                        "description": "選択したチェック項目で問題は検出されませんでした",
                        "detail": "全チェックをパスしました。",
                    })

                render_report(findings, "プロジェクト セキュリティレポート", str(root))
