#!/usr/bin/env python3
"""Generate quiz data from MAPYO page HTML content."""
import json
import random
import re
import html as htmlmod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SITE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = SITE_ROOT / "data" / "quizzes.json"

VERSE_RE = re.compile(
    r"^(?:[1-3]\s)?(?:Genesis|Exodus|Exod\.|Leviticus|Lev\.|Numbers|Num\.|"
    r"Deuteronomy|Deut\.|Joshua|Judges|Ruth|Samuel|Kings|Jonah|Matthew|Matt\.|"
    r"Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|"
    r"Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|"
    r"Jude|Revelation|Psalm|Psalms|Jeremiah|Isaiah|Daniel|Hosea|Amos|Micah|"
    r"Habakkuk|Zephaniah|Haggai|Zechariah|Malachi)\s*\d",
    re.I,
)

SKIP_PATTERNS = re.compile(
    r"^(?:\+\+\+|Topics|Discussion Questions|This Week|CONTINUATION|"
    r"Key Verses|References to|Handouts|Bible Study Worksheets|St\. Matthew|"
    r"Readings|Old Testament Study|New Testament|In This Section|"
    r"Click the drop down|Just for this week|ON THE|Efficacy)",
    re.I,
)


def clean_text(text: str) -> str:
    text = htmlmod.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate(text: str, max_len: int = 220) -> str:
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 3].rsplit(" ", 1)[0]
    return cut + "..."


def make_mcq(question: str, correct: str, pool: List[str], explanation: str) -> Optional[Dict]:
    correct = clean_text(correct)
    if not correct or len(correct) < 2:
        return None
    distractors = [d for d in pool if d != correct and len(d) > 2]
    random.shuffle(distractors)
    options = [correct]
    for d in distractors:
        if d not in options:
            options.append(d)
        if len(options) >= 4:
            break
    while len(options) < 4:
        options.append(f"None of the above ({len(options)})")
    random.shuffle(options)
    return {
        "question": question,
        "options": options,
        "correct": correct,
        "explanation": explanation,
    }


def extract_defs(content: str) -> List[Tuple[str, str]]:
    pairs = []
    for m in re.finditer(
        r'<div class="def-item"><strong>([^<]+)</strong>\s*'
        r'<span class="def-item__desc">([^<]*)</span></div>',
        content,
    ):
        term, desc = clean_text(m.group(1)), clean_text(m.group(2))
        desc = desc.strip("() ")
        if term and desc:
            pairs.append((term, desc))
    return pairs


def extract_refs(content: str) -> List[Tuple[str, str]]:
    pairs = []
    for m in re.finditer(
        r'<span class="ref-item__label">([^<]+)</span>\s*'
        r'<span class="ref-item__verse">([^<]+)</span>',
        content,
    ):
        label, verse = clean_text(m.group(1)), clean_text(m.group(2))
        if label and verse:
            pairs.append((label.rstrip("-: "), verse))
    return pairs


def extract_paragraphs(content: str) -> List[str]:
    article = re.search(
        r'<(?:article class="page-content[^"]*"|main class="page"[^>]*>\s*<div class="container")>(.*?)</(?:article|main)>',
        content,
        re.S,
    )
    if not article:
        body = re.search(r"<body[^>]*>(.*)</body>", content, re.S)
        inner = body.group(1) if body else content
    else:
        inner = article.group(1)
    inner = re.sub(r"<div class=\"(?:page-hero|video-embed|child-nav|download-grid|form-embed)[^\"]*\".*?</div>", "", inner, flags=re.S)
    paras = []
    for m in re.finditer(r"<p>([^<]*(?:<[^/p][^>]*>[^<]*)*)</p>", inner):
        text = clean_text(m.group(1))
        if text and len(text) > 8 and not SKIP_PATTERNS.match(text):
            paras.append(text)
    return paras


def extract_qa_pairs(paras: List[str]) -> List[Tuple[str, str]]:
    pairs = []
    i = 0
    while i < len(paras):
        q = paras[i]
        if q.endswith("?") and len(q) > 15:
            answer_parts = []
            j = i + 1
            while j < len(paras):
                nxt = paras[j]
                if nxt.endswith("?") and len(nxt) > 15 and not VERSE_RE.match(nxt):
                    break
                if SKIP_PATTERNS.match(nxt):
                    j += 1
                    continue
                answer_parts.append(nxt)
                if len(" ".join(answer_parts)) > 80:
                    break
                j += 1
            if answer_parts:
                pairs.append((q, truncate(" ".join(answer_parts), 300)))
            i = j
        else:
            i += 1
    return pairs


def extract_label_verse_pairs(paras: List[str]) -> List[Tuple[str, str, str]]:
    """Topic label followed by verse reference and optional explanation."""
    pairs = []
    for i, p in enumerate(paras):
        if VERSE_RE.match(p):
            verse = p
            label = ""
            explanation = ""
            if i > 0 and (paras[i - 1].endswith(":") or paras[i - 1].endswith("-")):
                label = paras[i - 1].rstrip(":- ").strip()
            if i + 1 < len(paras) and not VERSE_RE.match(paras[i + 1]) and not paras[i + 1].endswith("?"):
                explanation = paras[i + 1]
            if label and len(label) > 3:
                pairs.append((label, verse, explanation or f"{label} is found in {verse}."))
    return pairs


def extract_key_facts(paras: List[str]) -> List[Tuple[str, str]]:
    facts = []
    for p in paras:
        if len(p) > 40 and not p.endswith("?") and not VERSE_RE.match(p) and "Loading form" not in p:
            if any(kw in p.lower() for kw in ("because", "means", "teaches", "shows", "ordered", "refused", "learn")):
                words = p.split()
                if len(words) >= 8:
                    snippet = " ".join(words[:6]) + "..."
                    facts.append((p, snippet))
    return facts


def generate_for_page(slug: str, content: str, title: str) -> List[Dict]:
    questions: List[Dict] = []
    seen_q = set()

    def add(q: Optional[Dict]):
        if not q:
            return
        key = q["question"][:80]
        if key in seen_q:
            return
        seen_q.add(key)
        questions.append(q)

    defs = extract_defs(content)
    refs = extract_refs(content)
    paras = extract_paragraphs(content)
    qa_pairs = extract_qa_pairs(paras)
    lv_pairs = extract_label_verse_pairs(paras)

    def_pool = [d for _, d in defs]
    ref_pool = [v for _, v in refs]
    label_pool = [l for l, _, _ in lv_pairs]
    verse_pool = [v for _, v, _ in lv_pairs]

    for term, desc in defs:
        add(make_mcq(
            f'What does "{term}" mean according to this study?',
            desc,
            def_pool + [f"Limited in power", f"Present only in heaven", f"Unknown to mankind"],
            f'On this page, {term} is defined as {desc}.',
        ))
        add(make_mcq(
            f"Which term is described as \"{desc}\"?",
            term,
            [t for t, _ in defs] + ["Messiah", "Apostle", "Disciple"],
            f'{term} means {desc}, as taught in this lesson.',
        ))

    for label, verse in refs:
        add(make_mcq(
            f'Which Bible reference is associated with "{label}" on this page?',
            verse,
            ref_pool + verse_pool + ["John 3:16", "Psalm 23:1", "Romans 8:28"],
            f'This study connects {label} with {verse}.',
        ))
        add(make_mcq(
            f'According to this page, God is described as "{label}" in which passage?',
            verse,
            ref_pool + verse_pool + ["Exodus 20:1-17", "Matthew 5:1-12"],
            f'{label} — {verse}',
        ))

    for label, verse, explanation in lv_pairs:
        add(make_mcq(
            f'Which verse relates to "{label}" in this study?',
            verse,
            verse_pool + ref_pool + ["Genesis 1:1", "John 1:1"],
            explanation,
        ))

    for question, answer in qa_pairs[:12]:
        short_answers = [truncate(a, 120) for _, a in qa_pairs]
        add(make_mcq(question, answer, short_answers + paras[:8], answer))

    # Statement-based questions from rich paragraphs
    for full, snippet in extract_key_facts(paras)[:6]:
        add(make_mcq(
            "According to this page, which statement is correct?",
            truncate(full, 120),
            [truncate(p, 120) for p in paras if p != full][:5] + [
                "This topic is not discussed on this page.",
                "The study does not provide an answer to this.",
            ],
            full,
        ))

    # Homepage: study schedule and week titles
    info_values = [clean_text(m.group(1)) for m in re.finditer(r'class="info__value">([^<]+)<', content)]
    week_titles = [clean_text(m.group(1)) for m in re.finditer(r'class="week-card__title">([^<]+)<', content)]
    team_roles = [clean_text(m.group(1)) for m in re.finditer(r'class="team-card__role">([^<]+)<', content)]

    if info_values:
        for val in info_values:
            add(make_mcq(
                "According to this page, when or where do MAPYO Bible studies take place?",
                val,
                info_values + ["Sunday mornings at 10 A.M.", "Wednesday evenings at 8 P.M.", "Friday at noon"],
                f"MAPYO Bible studies: {val}",
            ))

    if week_titles:
        for title_item in week_titles[:6]:
            add(make_mcq(
                "Which Bible study week is listed on this page?",
                title_item,
                week_titles + ["Book of Revelation", "Book of Job", "Book of Daniel"],
                f'"{title_item}" is one of the weekly studies listed on this page.',
            ))

    if team_roles:
        for role in team_roles:
            add(make_mcq(
                "Which leadership role is part of the MAPYO team on this page?",
                role,
                team_roles + ["Treasurer", "Secretary", "Choir Director"],
                f"The MAPYO leadership team includes a {role}.",
            ))

    hero_sub = re.search(r'class="hero__subtitle[^"]*">([^<]+)<', content)
    if hero_sub:
        sub = clean_text(hero_sub.group(1))
        add(make_mcq(
            "What is MAPYO's subtitle on this page?",
            sub,
            [sub, "Adult Bible Study Group", "Sunday School Program", "Choir Ministry"],
            f"MAPYO is described as: {sub}",
        ))

    # Overview pages: child-card titles
    for m in re.finditer(r'class="child-card__title">([^<]+)<', content):
        topic = clean_text(m.group(1))
        if topic:
            add(make_mcq(
                f'Which of these is a Bible study topic listed on the {title} page?',
                topic,
                [clean_text(x.group(1)) for x in re.finditer(r'class="child-card__title">([^<]+)<', content)][:8]
                + ["Book of Revelation", "Book of Job"],
                f'{topic} is listed as a study section on this page.',
            ))

    # Thin pages: use list items
    if len(questions) < 3:
        for m in re.finditer(r"<li>([^<]+)</li>", content):
            item = clean_text(m.group(1))
            if len(item) > 5 and not SKIP_PATTERNS.match(item):
                siblings = [clean_text(x.group(1)) for x in re.finditer(r"<li>([^<]+)</li>", content)]
                add(make_mcq(
                    f"Which topic is mentioned on this page?",
                    item,
                    siblings + ["Book of Ezekiel", "Book of Esther"],
                    f'"{item}" appears in the content of this page.',
                ))
                if len(questions) >= 5:
                    break

    # Form-only pages
    if slug == "structure-form":
        add(make_mcq(
            "What is the purpose of the Structure Form page?",
            "To submit the MAPYO structure form",
            ["To download worksheets", "To watch Bible study videos", "To submit prayer requests only"],
            "This page hosts the MAPYO structure form for organizational submissions.",
        ))

    if "contact" in slug and len(questions) < 3:
        add(make_mcq(
            "How can you submit anonymous questions on this page?",
            "Use the anonymous form on this page",
            ["Call the youth president only", "Email the deacon directly", "Post on social media"],
            "The page provides an anonymous Google Form for Bible study and spiritual questions.",
        ))

    random.shuffle(questions)
    return questions[:8] if len(questions) > 8 else questions


def page_slug_from_path(path: Path) -> str:
    rel = path.relative_to(SITE_ROOT)
    if rel.name == "index.html":
        return "index"
    return str(rel.with_suffix("")).replace("\\", "/")


def inject_quiz_script(content: str, depth: int) -> str:
    prefix = "../" * depth
    main_script = f'<script src="{prefix}js/main.js"></script>'
    quiz_script = f'<script src="{prefix}js/quiz.js"></script>'
    if "js/quiz.js" in content:
        return content
    return content.replace(main_script, f"{quiz_script}\n{main_script}")


def main():
    random.seed(42)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    quizzes = {}
    html_files = sorted(SITE_ROOT.glob("**/*.html"))

    for path in html_files:
        if ".git" in str(path):
            continue
        slug = page_slug_from_path(path)
        content = path.read_text(encoding="utf-8")
        title_m = re.search(r"<title>([^<]+)</title>", content)
        title = clean_text(title_m.group(1).split("—")[0].strip()) if title_m else slug

        questions = generate_for_page(slug, content, title)
        if questions:
            quizzes[slug] = {"title": title, "questions": questions}
            print(f"  {slug}: {len(questions)} questions")

        depth = len(path.relative_to(SITE_ROOT).parts) - 1
        updated = inject_quiz_script(content, depth)
        if updated != content:
            path.write_text(updated, encoding="utf-8")

    OUTPUT.write_text(json.dumps(quizzes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(quizzes)} quizzes to {OUTPUT}")


if __name__ == "__main__":
    main()