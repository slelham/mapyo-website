#!/usr/bin/env python3
"""Remove plain-text lists that duplicate child-nav or download-grid links."""
import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

CHILD_NAV_FILES = [
    "bible-studies.html",
    "bible-studies/genesis.html",
    "bible-studies/exodus.html",
    "bible-studies/leviticus.html",
    "bible-studies/numbers.html",
    "bible-studies/deuteronomy.html",
    "bible-studies/1-2-kings.html",
    "bible-studies/1-2-samuel.html",
    "bible-studies/joshua.html",
    "bible-studies/assurances.html",
    "bible-studies/introduction-to-the-bible.html",
    "bible-studies/st-matthew-gospel.html",
]

UL = re.compile(r'<ul class="page-content__list">.*?</ul>\s*', re.S)
FRAG_P = re.compile(r'<p>[^<]{0,40}</p>\s*')


def strip_before_child_nav(content: str) -> str:
    marker = '<div class="child-nav">'
    if marker not in content:
        return content
    before, after = content.split(marker, 1)
    # Remove the last list immediately before child-nav
    lists = list(UL.finditer(before))
    if lists:
        last = lists[-1]
        before = before[: last.start()] + before[last.end() :]
    # Remove orphan fragment paragraphs right before child-nav
    while True:
        m = re.search(r'(<p>[^<]{0,40}</p>\s*)+$', before)
        if not m:
            break
        chunk = m.group(0)
        if re.search(r'<p>(?:Week|Matthew|Seeking|St\.|Genesis|Exodus|:|\d|,\s*\d)', chunk):
            before = before[: m.start()]
        else:
            break
    return before + marker + after


def fix_bible_studies(content: str) -> str:
    content = re.sub(
        r'<ul class="page-content__list"><li>Topics</li>.*?</ul>\s*<p>St\. Matthew</p>\s*',
        "",
        content,
        flags=re.S,
    )
    return content


def fix_intro_bible(content: str) -> str:
    content = re.sub(
        r'<p>For the first three weeks of our Bible studies, we were introduced to the Bible\.</p>\s*'
        r'(?:<ul class="page-content__list"><li>We covered three main topics:</li></ul>\s*)?'
        r'<p>Who is God\?</p>\s*<p>Who is Man\?</p>\s*<p>Who is Jesus\?</p>\s*',
        "<p>For the first three weeks of our Bible studies, we were introduced to the Bible — covering who God is, who man is, and who Jesus is.</p>\n",
        content,
    )
    return content


def fix_assurances(content: str) -> str:
    content = re.sub(
        r'<ul class="page-content__list"><li>Week 4</li>.*?</ul>\s*<p>Seeking What is Important</p>\s*',
        "",
        content,
        flags=re.S,
    )
    return content


def fix_st_matthew(content: str) -> str:
    content = re.sub(
        r'<ul class="page-content__list"><li>Matthew</li><li>Week</li></ul>\s*<p>Matthew 1</p>\s*',
        "",
        content,
    )
    content = re.sub(
        r'<p>Each week&#x27;s study of the Gospel of Jesus Christ, according to the proclamation \(or preaching\) of St\.</p>',
        "<p>Each week's study of the Gospel of Jesus Christ, according to the proclamation of St. Matthew.</p>",
        content,
    )
    return content


def fix_our_bibles(content: str) -> str:
    old = re.search(
        r'<div class="page-hero.*?</div>\s*(.*?)<div class="download-grid',
        content,
        re.S,
    )
    if not old:
        return content
    replacement = """<div class="page-hero page-hero--local"><img src="../assets/images/page-banner.svg" alt="" loading="lazy" role="presentation"></div>
<h2 class="page-content__h2">The Orthodox Study Bible</h2>
<p>Starting in 2026, our Bible of choice until the last couple weeks of our Old Testament studies was the Orthodox Study Bible. You can find a PDF of it here and on the <a href="../worksheets-handouts.html">Worksheets &amp; Handouts</a> page too!</p>
<div class="download-grid page-links"><a href="https://drive.google.com/file/d/1w5WpV9_Nft38JumbBc6DE6_QMmnhvPk2/view?usp=drive_link" class="download-card" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg><span>Orthodox Study Bible PDF</span></a></div>
<p>For the Orthodox Study Bible, certain verse numbers are different from most other Bibles, especially for a book like the Psalms. The Orthodox verses are in parentheses for all pages updated in 2026 and after!</p>
<h2 class="page-content__h2">The Lamsa Bible</h2>
<p>For our Gospel readings, our Bible of choice is the Lamsa Bible, a translation of the ancient Aramaic text into English. We have physical copies available during Monday's Bible Studies or to borrow, and you can find it online.</p>
"""
    content = re.sub(
        r'<div class="page-hero page-hero--local">.*?</div>\s*.*?<div class="download-grid',
        replacement + "\n<div class=\"download-grid",
        content,
        count=1,
        flags=re.S,
    )
    # Remove trailing duplicate download grid (now empty or redundant)
    content = re.sub(
        r'<div class="download-grid page-links"><a href="https://drive\.google\.com/file/d/1w5WpV9[^<]*</a></div>\s*',
        "",
        content,
        count=1,
    )
    return content


DOWNLOAD_CARD = (
    '<div class="download-grid page-links">'
    '<a href="{url}" class="download-card" target="_blank" rel="noopener">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
    '<path d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>'
    "<span>{label}</span></a></div>"
)


def fix_exodus_week6(content: str) -> str:
    card = DOWNLOAD_CARD.format(
        url="https://drive.google.com/file/d/17dxXPSURk6spYQt7AAdnW9WcINZ9CzRG/view?usp=sharing",
        label="Exodus Graphics — Week 6",
    )
    content = re.sub(
        r'<p>\+\+\+Please see the “Exodus Graphics- Week 6” pdf handout</p>\s*'
        r'<ul class="page-content__list"><li>here</li></ul>\s*'
        r"<p>to use alongside this weeks’ readings\.</p>\s*",
        f"<p>Please see the Exodus Graphics — Week 6 pdf handout to use alongside this week's readings.</p>\n{card}\n",
        content,
    )
    content = re.sub(
        r'\n<div class="download-grid page-links"><a href="https://drive\.google\.com/file/d/17dxXPSURk6spYQt7AAdnW9WcINZ9CzRG[^<]*</a></div>\s*(?=</article>)',
        "\n",
        content,
    )
    return content


def fix_genesis_week3(content: str) -> str:
    card = DOWNLOAD_CARD.format(
        url="https://drive.google.com/file/d/1ACiMfh3E8enxnggQEmvJOtc6KjQ9Osim/view?usp=drive_link",
        label="Circumcision &amp; Baptism Infographic",
    )
    content = re.sub(
        r"<p>Another major parallel from the Old Testament scriptures to the New is that of circumcision and baptism\. For brevity[’']s sake, please refer to</p>\s*"
        r'<ul class="page-content__list"><li>this infographic</li></ul>\s*'
        r"<p>to read about those parallels, as well as the discussion questions below\.</p>\s*",
        f"<p>Another major parallel from the Old Testament scriptures to the New is that of circumcision and baptism. For brevity's sake, please refer to the infographic below to read about those parallels, as well as the discussion questions below.</p>\n{card}\n",
        content,
    )
    # Remove only a trailing duplicate grid at end of article (not inline grids)
    content = re.sub(
        r'(\s*<div class="download-grid page-links"><a href="https://drive\.google\.com/file/d/1ACiMfh3)[^<]*</a>(?:<a[^<]*</a>)*</div>)\s*(</article>)',
        r"\2",
        content,
        count=1,
    )
    return content


def fix_numbers_week4(content: str) -> str:
    card = DOWNLOAD_CARD.format(
        url="https://drive.google.com/file/d/1isMKJOCY_wCn71LueTaYHs8owYVkqiC8/view?usp=drive_link",
        label="Israelite Encampment Graphic",
    )
    content = re.sub(
        r'<ul class="page-content__list"><li>Reference Graphic below at end of booklet</li></ul>\s*'
        r"<p>How did the Israelite encampment look\?</p>\s*"
        r'<ul class="page-content__list"><li>They had to encamp in</li></ul>\s*'
        r"<p>this fashion</p>\s*",
        f"<p>How did the Israelite encampment look? They had to encamp in this fashion:</p>\n{card}\n",
        content,
    )
    content = re.sub(
        r'\n<div class="download-grid page-links"><a href="https://drive\.google\.com/file/d/1isMKJOCY[^<]*</a></div>\s*(?=</article>)',
        "\n",
        content,
    )
    return content


SPECIAL = {
    "bible-studies.html": fix_bible_studies,
    "bible-studies/introduction-to-the-bible.html": fix_intro_bible,
    "bible-studies/assurances.html": fix_assurances,
    "bible-studies/st-matthew-gospel.html": fix_st_matthew,
    "bible-studies/our-bibles.html": fix_our_bibles,
    "bible-studies/exodus/week-6.html": fix_exodus_week6,
    "bible-studies/genesis/week-3.html": fix_genesis_week3,
    "bible-studies/numbers/week-4.html": fix_numbers_week4,
}


def main():
    changed = []
    for rel in CHILD_NAV_FILES:
        path = SITE_ROOT / rel
        content = path.read_text(encoding="utf-8")
        updated = strip_before_child_nav(content)
        if rel in SPECIAL:
            updated = SPECIAL[rel](updated)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            changed.append(rel)

    for rel, fn in SPECIAL.items():
        if rel in CHILD_NAV_FILES:
            continue
        path = SITE_ROOT / rel
        content = path.read_text(encoding="utf-8")
        updated = fn(content)
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            changed.append(rel)

    for rel in sorted(set(changed)):
        print(f"  fixed: {rel}")
    print(f"\nUpdated {len(changed)} files")


if __name__ == "__main__":
    main()