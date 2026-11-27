"""Build Claude's skill ZIP and a self-contained prompt for ordinary chats."""

import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ("references/writing-patterns.md", "references/academic-writing.md", "references/sources.md")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=True)

    with ZipFile(out / "pptx-to-thesis.zip", "w", ZIP_DEFLATED) as archive:
        for name in ("SKILL.md", *GUIDES, "scripts/read_pptx.py", "scripts/ciinii.py"):
            archive.write(ROOT / name, "pptx-to-thesis/" + name)

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[2]
    patterns, writing, sources = [(ROOT / name).read_text(encoding="utf-8") for name in GUIDES]
    # Plain chats receive the guides inline and do not have the optional database CLI.
    sources = sources.split("## 任意で学内文献を利用する場合", 1)[0]
    intro = ("この指示書と提出者の資料を使って以下の手順を実行する。"
             "参照先の執筆指針と文献案内はこの指示書の後半に収録している。"
             "同梱スクリプトが手元にない場合は、添付ファイルを読める範囲で扱う。")
    text = "\n\n".join(part.strip() for part in (skill, patterns, writing, sources))
    text = re.sub(r"\[([^\]]+)\]\((?:references/)?[\w-]+\.md(?:#[^)]*)?\)", r"\1", text)
    (out / "pptx-to-thesis-chat.md").write_text(intro + "\n\n" + text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
