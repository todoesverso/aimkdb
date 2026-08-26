#!/usr/bin/env python3
from collections import defaultdict
from pathlib import Path
import re

DB_DIR = Path("db")
OUTPUT_FILE = Path("README.md")


def parse_metadata(file_path: Path) -> dict:
    """Extract metadata from the Markdown block below a document title."""
    lines = file_path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        return {}

    metadata = {"title": lines[0][2:].strip()}
    for line in lines[1:]:
        match = re.match(r"^\*\*(Category|Subcategory|Tags|Type):\*\*\s*(.+)$", line)
        if not match:
            if metadata.keys() - {"title"}:
                break
            continue
        metadata[match.group(1).lower()] = match.group(2).strip()

    return metadata


def generate_index():
    if not DB_DIR.exists():
        print(f"Error: Directory '{DB_DIR}' does not exist.")
        return

    # Nested hierarchy: tree[category][subcategory] = [doc_info, ...]
    tree = defaultdict(lambda: defaultdict(list))

    for file_path in sorted(DB_DIR.rglob("*.md")):
        if file_path.name.lower() == "readme.md":
            continue

        fm = parse_metadata(file_path)

        category = fm.get("category", "Uncategorized")
        subcategory = fm.get("subcategory", "General")
        title = fm.get("title", file_path.stem.replace("-", " ").title())
        doc_type = fm.get("type", "note")

        tree[category][subcategory].append(
            {
                "title": title,
                "type": doc_type,
                "path": file_path.as_posix(),
            }
        )

    # Build Markdown index output
    output = [
        "# AI Knowledge Base Index\n\n",
        f"Auto-generated index of documents in `{DB_DIR}/`.\n",
    ]

    for category in sorted(tree.keys()):
        output.append(f"\n## {category}\n\n")
        for subcategory in sorted(tree[category].keys()):
            output.append(f"### {subcategory}\n\n")
            docs = sorted(tree[category][subcategory], key=lambda x: x["title"])
            for doc in docs:
                output.append(f"- [{doc['title']}]({doc['path']}) `[{doc['type']}]`\n")

    OUTPUT_FILE.write_text("".join(output), encoding="utf-8")
    print(f"Successfully generated {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_index()
