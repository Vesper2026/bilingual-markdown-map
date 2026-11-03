"""Compare the structure of two Markdown files, not translation quality."""
from __future__ import annotations
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re

HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
TARGET = re.compile(r"(!?)\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))(?:\s+\"[^\"\n]*\")?\s*\)")


def section(index, title, level, line):
    return dict(index=index, title=title, level=level, line=line, code_languages=[], math_blocks=0, images=[], links=[])


def parse_markdown(source):
    """Supported subset: ATX headings, fenced code, standalone $$, direct inline links."""
    sections = [section(0, "(preamble)", 0, 1)]
    current = sections[0]
    fence_char, fence_length, in_math = None, 0, False
    preamble_has_text = False
    for line_number, line in enumerate(source.splitlines(), 1):
        if current["index"] == 0 and line.strip() and (fence_char or in_math or not HEADING.match(line)):
            preamble_has_text = True
        if fence_char:
            if re.fullmatch(r" {0,3}" + re.escape(fence_char) + "{" + str(fence_length) + r",}[ \t]*", line):
                fence_char = None
            continue
        if line.strip() == "$$":
            if not in_math:
                current["math_blocks"] += 1
            in_math = not in_math
            continue
        if in_math:
            continue
        fence = FENCE.match(line)
        if fence:
            marker, info = fence.groups()
            fence_char, fence_length = marker[0], len(marker)
            current["code_languages"].append(info.strip().split()[0] if info.strip() else "(unspecified)")
            continue
        heading = HEADING.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(2) or "").strip()
            current = section(len(sections), title, len(heading.group(1)), line_number)
            sections.append(current)
        # Ignore inline code spans before collecting the limited direct-link syntax.
        visible = re.sub(r"(`+).*?\1", "", line)
        for match in TARGET.finditer(visible):
            target = match.group(2) or match.group(3)
            current["images" if match.group(1) else "links"].append(target)
    if not preamble_has_text:
        sections = sections[1:]
    return sections


def compare(left, right, mapping=None):
    left_by = {item["index"]: item for item in left}
    right_by = {item["index"]: item for item in right}
    if mapping is None:
        pairs = list(zip([i for i in left_by if i != 0], [i for i in right_by if i != 0]))
        if 0 in left_by and 0 in right_by:
            pairs.insert(0, (0, 0))
    else:
        if not isinstance(mapping, list):
            raise ValueError("Mapping must be a JSON array of [source_index, target_index] pairs.")
        pairs = []
        for pair in mapping:
            if not isinstance(pair, list) or len(pair) != 2 or any(type(i) is not int for i in pair):
                raise ValueError("Each mapping pair must contain two integer section indices.")
            a, b = pair
            if a not in left_by or b not in right_by:
                raise ValueError(f"Mapping references an unknown section: {pair}")
            pairs.append((a, b))
        if len({a for a, _ in pairs}) != len(pairs) or len({b for _, b in pairs}) != len(pairs):
            raise ValueError("Mapping must be one-to-one; repeated section indices are not allowed.")
    matches = []
    for a, b in pairs:
        source, target = left_by[a], right_by[b]
        changes = []
        for field in ("level", "math_blocks", "code_languages", "images", "links"):
            equal = Counter(source[field]) == Counter(target[field]) if isinstance(source[field], list) else source[field] == target[field]
            if not equal:
                changes.append({"field": field, "source": source[field], "target": target[field]})
        matches.append({"source": source, "target": target, "review_items": changes})
    return dict(
        notice="Structural review only, not a semantic or translation-quality assessment. Order-based pairing can misalign after omissions; use an explicit index map.",
        mode="explicit" if mapping is not None else "order",
        pairs=matches,
        source_unpaired=[item for item in left if item["index"] not in {a for a, _ in pairs}],
        target_unpaired=[item for item in right if item["index"] not in {b for _, b in pairs}],
    )


def escape(value):
    return html.escape(str(value), quote=False).replace("|", "\\|").replace("\n", " ")


def render(report):
    lines = ["# Bilingual Markdown map", "", report["notice"], "", f"Mode: {report['mode']}", "",
             "| Source index / title | Target index / title | Review fields |", "|---|---|---|"]
    for pair in report["pairs"]:
        a, b = pair["source"], pair["target"]
        fields = ", ".join(change["field"] for change in pair["review_items"]) or "No structural differences"
        lines.append(f"| {a['index']}: {escape(a['title'] or '(untitled)')} | {b['index']}: {escape(b['title'] or '(untitled)')} | {fields} |")
    for name in ("source_unpaired", "target_unpaired"):
        lines += ["", f"## {name.replace('_', ' ')}", ""]
        for item in report[name]:
            lines.append(f"- {item['index']}: {escape(item['title'] or '(untitled)')} (line {item['line']})")
        if not report[name]:
            lines.append("None.")
    lines += ["", "## Difference details", ""]
    for pair in report["pairs"]:
        for change in pair["review_items"]:
            lines.append(f"- {pair['source']['index']} ↔ {pair['target']['index']} / {change['field']}: {escape(json.dumps(change['source'], ensure_ascii=False))} → {escape(json.dumps(change['target'], ensure_ascii=False))}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--map", type=Path, help="JSON array of one-to-one integer index pairs")
    parser.add_argument("--output", type=Path, default=Path("comparison"))
    args = parser.parse_args()
    try:
        left = parse_markdown(args.source.read_text(encoding="utf-8-sig"))
        right = parse_markdown(args.target.read_text(encoding="utf-8-sig"))
        mapping = json.loads(args.map.read_text(encoding="utf-8-sig")) if args.map else None
        result = compare(left, right, mapping)
        destinations = [args.output / "comparison.json", args.output / "comparison.md"]
        if {args.source.resolve(), args.target.resolve()} & {path.resolve() for path in destinations}:
            raise ValueError("Output must not overwrite an input document.")
        args.output.mkdir(parents=True, exist_ok=True)
        destinations[0].write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        destinations[1].write_text(render(result), encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"{len(result['pairs'])} section pairs; {len(result['source_unpaired'])} source / {len(result['target_unpaired'])} target unpaired. No semantic scoring.")


if __name__ == "__main__":
    main()
