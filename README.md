# pptx to thesis｜Lashkia研究室版

Lashkia（ラシキア）研究室の過去の卒論をもとに、卒業発表のPowerPointから日本語のLaTeX原稿を作成するskills

## 導入

| 利用環境 | 手順 |
| --- | --- |
| Claude | [スキルZIP](https://github.com/yama4936/lashkia-lab-pptx-to-thesis-skills/releases/latest/download/pptx-to-thesis.zip)を「Customize → Skills」でアップロードして有効化 |
| Claude Code | 作業フォルダで `git clone https://github.com/yama4936/lashkia-lab-pptx-to-thesis-skills.git .claude/skills/pptx-to-thesis` |
| Codex・Gemini CLI | 作業フォルダで `git clone https://github.com/yama4936/lashkia-lab-pptx-to-thesis-skills.git .agents/skills/pptx-to-thesis` |
| その他のチャット | [チャット用指示書](https://github.com/yama4936/lashkia-lab-pptx-to-thesis-skills/releases/latest/download/pptx-to-thesis-chat.md)を発表資料と一緒に添付 |

## 使い方

PPTXを添付するか、作業フォルダ内のファイルを指定して依頼します。提出用テンプレートがあれば一緒に渡してください。

> pptx-to-thesis で、この卒業発表を卒論にしてください。

資料で確認できない研究条件や結果は、該当スライドを示し、利用中のチャットで質問します。回答を反映した編集用のLaTeX一式と、ビルドできた場合は確認用PDFを受け取れます。
