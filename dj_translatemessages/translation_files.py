import re
from pathlib import Path

import polib


def parse_empty_translations(po_file_path):
    po_file = polib.pofile(po_file_path)

    empty_translations = {}
    for entry in po_file:
        if not entry.msgstr:
            empty_translations[entry.msgid] = entry.msgstr

    return empty_translations


def _split_location_comments(po_text: str) -> str:
    """
    Normalize '#:' location comments so that each file:line
    appears on its own line with exactly one space after '#:'.
    """
    out_lines = []
    i = 0
    lines = po_text.splitlines(keepends=False)

    while i < len(lines):
        line = lines[i]

        if line.startswith("#:"):
            # collect consecutive '#:' lines
            block = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("#:"):
                block.append(lines[i])
                i += 1

            # join and normalize multiple spaces
            joined = " ".join(s[2:].strip() for s in block)
            joined = re.sub(r"\s+", " ", joined)  # collapse multiple spaces

            # split into path:line tokens
            tokens = re.findall(r"\S+?:\d+", joined)

            for t in tokens:
                out_lines.append(f"#: {t}")
            continue

        out_lines.append(line)
        i += 1

    return "\n".join(out_lines) + "\n"


def fill_translations(po_file_path, translations, output_file_path):
    # Load the original po file
    po = polib.pofile(po_file_path)

    # disable wrapping so strings stay on one line / keep prior formatting
    po.wrapwidth = -1

    for entry in po:
        # If msgstr is empty and msgid is in dictionary, fill it
        if not entry.msgstr and entry.msgid in translations:
            entry.msgstr = translations[entry.msgid]

    # Save to new file
    po.save(output_file_path)

    # Then normalize '#:' lines to one occurrence per line
    p = Path(output_file_path)
    text = p.read_text(encoding=po.encoding or "utf-8")
    text = _split_location_comments(text)
    p.write_text(text, encoding=po.encoding or "utf-8")
