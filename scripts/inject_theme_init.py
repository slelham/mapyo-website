#!/usr/bin/env python3
"""Inject theme-init.js into all HTML pages (before styles.css)."""
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

def inject_embed(content: str, depth: int) -> str:
    prefix = "../" * depth
    tag = f'<script src="{prefix}js/embed.js"></script>\n  '
    if "js/embed.js" in content:
        return content
    needle = f'<script src="{prefix}js/theme.js"></script>'
    if needle in content:
        return content.replace(needle, tag + needle)
    return content


def inject(content: str, depth: int) -> str:
    prefix = "../" * depth
    tag = f'<script src="{prefix}js/theme.js"></script>\n  '
    if "js/theme.js" in content:
        content = inject_embed(content, depth)
        return content
    if "theme-init.js" in content:
        content = content.replace(
            f'<script src="{prefix}js/theme-init.js"></script>\n  ',
            tag,
        )
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
        updated = inject_embed(updated, depth)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            print(f"  {path.relative_to(SITE_ROOT)}")

if __name__ == "__main__":
    main()