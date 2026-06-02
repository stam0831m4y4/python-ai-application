# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# アプリ起動
streamlit run app.py

# 依存パッケージインストール
pip install -r requirements.txt
```

## Architecture

Streamlit のシングルページアプリ。サイドバーのナビゲーションで `st.session_state.selected_tool` を切り替え、選択されたツールモジュールの `render()` を呼び出す構成。

### ツール追加の手順

1. `tools/` に新しいモジュールを作成し、`render()` 関数を実装する
2. `app.py` の `TOOLS` 辞書にエントリを追加する（`icon`, `module`, `description`）
3. `app.py` の import 文に追加する

### Gemini API

`utils/gemini_client.py` の `stream_response(prompt)` がジェネレーターを返す。Streamlit 側では `st.write_stream()` に渡してストリーミング表示する。モデルはデフォルト `gemini-2.0-flash`。APIキーは `.env` の `GEMINI_API_KEY` から読み込む（`python-dotenv` 使用）。

使用パッケージは `google-generativeai` ではなく **`google-genai`**（`from google import genai`）。前者は非推奨のため絶対に使わない。

## 注意事項

- **ストリーミング表示は `st.write_stream()` を使う。** `st.write()` に渡してもストリーミングにならない。
- **各ツールモジュールは必ず `render()` 関数を公開する。** `app.py` はこの関数だけを呼び出す。
- **Streamlit はボタンを押すたびにスクリプト全体を再実行する。** ツール間の状態保持が必要な場合は `st.session_state` を使う。
- **`get_client()` はシングルトン。** `_client` をモジュールレベルでキャッシュしており、毎回 API クライアントを生成しない設計になっている。
- **プロンプトは各ツールモジュール内に直書きする。** 共通化・抽象化はしない。

## ツール一覧と対応ファイル

| ツール名 | ファイル |
|---------|---------|
| ブログ記事執筆 | `tools/blog_writer.py` |
| メール返信文生成 | `tools/email_reply.py` |
| 文章要約 | `tools/summarizer.py` |
| 文章校正・添削 | `tools/proofreader.py` |
| SNS投稿文生成 | `tools/sns_writer.py` |
| 文体変換・リライト | `tools/style_converter.py` |
