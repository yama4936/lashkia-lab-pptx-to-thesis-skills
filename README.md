# 卒業発表から卒論へ

卒業発表のPPTXから日本語のLaTeX原稿を作るスキルです。過去の卒論20本を調べ、発表資料もある10組から、スライドの内容をどの章でどう詳しく書くかを整理しました。CiiiiNiiiiiiiiのアカウントは不要です。[発表から本文への対応表](references/writing-patterns.md)

## Claude・Codex・Geminiで使う

卒論の作業フォルダを開き、利用するツールに合わせて導入します。

| 利用環境 | 導入 | 呼び出し方 |
| --- | --- | --- |
| Claude（Web・アプリのカスタムスキル対応環境） | [スキルZIP](https://github.com/yama4936/pptx-to-thesis/releases/latest/download/pptx-to-thesis.zip)をダウンロードし、Claudeの「Customize → Skills」でアップロードして有効化 | 新しいチャットに発表資料を添付し、下の依頼例を送る |
| Claude Code | `git clone https://github.com/yama4936/pptx-to-thesis.git .claude/skills/pptx-to-thesis` | 同じフォルダで `/pptx-to-thesis` とPPTXのパスを入力 |
| Gemini CLI | `git clone https://github.com/yama4936/pptx-to-thesis.git .agents/skills/pptx-to-thesis` | 同じフォルダでスキル名とPPTXのパスを指定して依頼 |
| Codex | Gemini CLIと同じ配置先を使う | `$pptx-to-thesis` とPPTXを指定して依頼 |

ユーザー単位で導入するときは、Claude Codeなら `~/.claude/skills/pptx-to-thesis`、Codex・Gemini CLIなら `~/.agents/skills/pptx-to-thesis` にクローンします。Gitバンドルを使うときはURLをバンドルのパスに置き換えます。[Claudeのアップロード手順](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) ／ [Claude Code](https://code.claude.com/docs/en/skills) ／ [Gemini CLI](https://geminicli.com/docs/cli/skills/) ／ [Codex](https://learn.chatgpt.com/docs/build-skills)

## スキルを追加できないチャットで使う

[チャット用の指示書](https://github.com/yama4936/pptx-to-thesis/releases/latest/download/pptx-to-thesis-chat.md)と発表PPTXを同じ会話に添付します。指示書は全文を貼り付けても使えます。執筆指針・質問例・文献の扱いを1ファイルに収録しています。PPTXを読めない環境には、スライド番号が分かるPDFまたは画像と、発表者ノートのテキストを渡してください。

> pptx-to-thesis の手順で、この卒業発表を日本語の卒論にしてください。根拠が足りない箇所はスライド番号付きで質問し、私の回答を原稿に反映してください。

通常は編集可能なTeX一式と、ビルドできた場合は確認用PDFを受け取れます。チャットがファイル作成に対応していない場合は、保存するファイル名とソース本文が返ります。提出テンプレートやWord指定があれば最初に渡してください。PPTX抽出用の補助スクリプトはPython 3.9以降の標準ライブラリで動きます。

## 配布物を作る

リポジトリ内で `python3 scripts/package_skill.py /path/to/output` を実行すると、同じ執筆ルールからアップロード用ZIPとチャット用Markdownを生成します。
