#!/usr/bin/env python3
"""Inject theme-init.js into all HTML pages (before styles.css)."""
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

def inject(content: str, depth: int) -> str:
    prefix = "../" * depth
    tag = f'<script src="{prefix}js/theme-init.js"></script>\n  '
    if "theme-init.js" in content:
        return content
    needle = f'<link rel="stylesheet" href="{prefix}css/styles.css">'
    if needle not in content:
        return content
    return content.replace(needle, tag + needle)

def main():
    for path in sorted(SITE_ROOT.glob("**/*.html")):
        if ".git" in str(path):
            continue
        depth = len(path.relative_to(SITE_ROOT).parts) - 1
        content = path.read_text(encoding="utf-8")
        updated = inject(content, depth)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            print(f"  {path.relative_to(SITE_ROOT)}")

if __name__ == "__main__":
    main()