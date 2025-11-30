#!/usr/bin/env python3
import os
from pathlib import Path

def build_tree(root: Path) -> list[str]:
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if rel == Path("."):
            # Skip the root folder itself
            indent = ""
        else:
            indent = "    " * len(rel.parts)
            lines.append(f"{indent}{rel.name}/")

        subindent = indent + "    "
        for f in sorted(filenames):
            if rel == Path("."):
                # Files directly in root
                lines.append(f"    {f}")
            else:
                lines.append(f"{subindent}{f}")

    return lines


def main():
    root = Path(__file__).resolve().parent
    out_file = root / "folder_structure.txt"

    tree_lines = build_tree(root)
    out_file.write_text("\n".join(tree_lines), encoding="utf-8")

    print(f"✔ Folder snapshot saved to: {out_file}")


if __name__ == "__main__":
    main()
