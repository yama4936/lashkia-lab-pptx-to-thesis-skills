"""Read slide evidence from an editable PowerPoint package without changing it."""

import argparse
import json
import posixpath
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"p": P, "a": A}


def read_xml(package, part):
    if package.getinfo(part).file_size > 32 * 1024 * 1024:
        raise ValueError(f"XML part is too large: {part}")
    return ET.fromstring(package.read(part))


def relationships(package, part):
    directory, name = posixpath.split(part)
    path = posixpath.join(directory, "_rels", name + ".rels")
    if path not in package.namelist():
        return {}
    return {node.attrib["Id"]: node.attrib for node in read_xml(package, path)}


def related_part(part, relation):
    if relation.get("TargetMode") == "External":
        raise ValueError("Expected an internal PowerPoint package part")
    target = relation["Target"]
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))


def paragraphs(node):
    result = []
    for paragraph in node.findall("./a:p", NS):
        value = "".join(
            (child.text or "") if child.tag == f"{{{A}}}t" else "\n"
            for child in paragraph.iter()
            if child.tag in (f"{{{A}}}t", f"{{{A}}}br")
        )
        if value.strip():
            result.append(value)
    return result


def read_slide(package, part, number):
    slide = read_xml(package, part)
    relations = relationships(package, part)
    blocks = []
    visual = []
    tree = slide.find("./p:cSld/p:spTree", NS)

    def table_rows(table):
        rows = []
        for row in table.findall("./a:tr", NS):
            cells = []
            for cell in row.findall("./a:tc", NS):
                body = cell.find("./a:txBody", NS)
                cells.append("\n".join(paragraphs(body)) if body is not None else "")
            rows.append(cells)
        return rows

    def read_shapes(shapes):
        for shape in shapes:
            kind = shape.tag.rsplit("}", 1)[-1]
            if kind == "grpSp":
                read_shapes(shape)
                continue

            for body in shape.findall("./p:txBody", NS):
                for text in paragraphs(body):
                    blocks.append({"text": text})

            if kind == "graphicFrame":
                table = shape.find(".//a:tbl", NS)
                if table is not None:
                    blocks.append({"table": table_rows(table)})
                else:
                    visual.append("graphicFrame (chart, SmartArt, or embedded object)")
            elif kind in ("pic", "contentPart"):
                visual.append(kind)

            for child in shape.iter():
                if child.tag.startswith("{http://schemas.openxmlformats.org/officeDocument/2006/math}"):
                    visual.append("equation")
                    break

    if tree is not None:
        read_shapes(tree)

    # A video can have a still poster image and a separate media relationship.
    embedded_media = dict.fromkeys(
        related_part(part, relation) for relation in relations.values()
        if relation["Type"].rsplit("/", 1)[-1] in ("video", "audio", "media")
        and relation.get("TargetMode") != "External"
    )

    notes = []
    all_relations = list(relations.values())
    for relation in relations.values():
        if relation["Type"].endswith("/notesSlide"):
            notes_part = related_part(part, relation)
            notes_slide = read_xml(package, notes_part)
            for shape in notes_slide.findall("./p:cSld/p:spTree/p:sp", NS):
                props = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
                body = shape.find("./p:txBody", NS)
                if props is not None and props.get("type") == "body" and body is not None:
                    notes.extend(paragraphs(body))
            all_relations.extend(relationships(package, notes_part).values())
            break

    links = dict.fromkeys(
        rel["Target"] for rel in all_relations
        if rel["Type"].endswith("/hyperlink") and rel.get("TargetMode") == "External"
    )
    return {
        "slide": number,
        "hidden": slide.get("show") in ("0", "false"),
        "blocks": blocks,
        "speaker_notes": notes,
        "external_hyperlinks": list(links),
        "embedded_media": list(embedded_media),
        "visual_review": list(dict.fromkeys(visual)),
    }


def extract(path):
    part = "ppt/presentation.xml"
    with ZipFile(path) as package:
        presentation = read_xml(package, part)
        relations = relationships(package, part)
        return [
            read_slide(package, related_part(part, relations[slide.attrib[f"{{{R}}}id"]]), number)
            for number, slide in enumerate(presentation.findall("./p:sldIdLst/p:sldId", NS), 1)
        ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    try:
        slides = extract(args.pptx)
    except (BadZipFile, ET.ParseError, OSError, KeyError, ValueError) as error:
        parser.exit(1, f"Cannot extract slides: {error}\n")
    if not slides:
        parser.exit(1, "No slides found in this PowerPoint package.\n")
    print(json.dumps(slides, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
