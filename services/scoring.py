from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple


# Component maxima sum to 100, so the overall score is the plain sum of the parts.
SCORE_MAXIMA = {
    "structure": 20,
    "clarity": 20,
    "impact": 20,
    "evidence": 20,
    "keywords": 20,
}

STOP_WORDS = {
    "the", "and", "for", "with", "from", "into", "your", "this", "that", "have",
    "will", "about", "their", "there", "been", "were", "using", "through", "over",
    "under", "without", "after", "before", "than", "then", "also", "more",
    "most", "some", "can", "could", "should", "would", "you", "we", "our", "they",
    "them", "his", "her", "its", "i", "me", "us", "is", "are", "was",
    "a", "an", "as", "at", "by", "on", "in", "of", "to", "or", "if", "it", "be",
    "but", "not", "no", "yes", "so", "do", "did", "does", "had", "has",
    # Filler common in job postings that says nothing about a skill.
    "need", "needs", "strong", "required", "requirements", "require", "ability", "able",
    "looking", "seeking", "plus", "preferred", "including", "etc", "must", "well", "good",
    "excellent", "knowledge", "skills", "skill", "team", "teams", "work", "working", "role",
    "candidate", "join", "what", "who", "responsibilities", "years", "year", "new", "other",
    "such", "within", "across", "based", "like", "help", "experience", "experienced",
}

# Characters allowed inside a token (c++, node.js, ci/cd) but not at its end,
# where they are sentence punctuation ("python.", "aws-").
TRAILING_PUNCTUATION = ".-/&"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z+\-/#.&]*", (text or "").lower())
    cleaned = (token.rstrip(TRAILING_PUNCTUATION) for token in tokens)
    return [token for token in cleaned if token not in STOP_WORDS and len(token) > 2]


def extract_keywords(text: str, limit: int = 12) -> List[str]:
    keyword_counts = Counter(tokenize(text))
    return [word for word, _ in keyword_counts.most_common(limit)]


def score_section_presence(sections: Dict[str, str], section_names: Iterable[str]) -> int:
    score = 0
    for name in section_names:
        if sections.get(name, "").strip():
            score += 5
    return min(score, SCORE_MAXIMA["structure"])


def calculate_resume_score(resume_text: str, sections: Dict[str, str]) -> Tuple[int, Dict[str, int], List[str]]:
    text = resume_text or ""
    words = re.findall(r"\b\w+\b", text)
    breakdown = {key: 0 for key in SCORE_MAXIMA}

    structure_score = score_section_presence(sections, ["summary", "skills", "experience", "education"])
    breakdown["structure"] = structure_score

    word_count = len(words)
    if word_count < 80:
        breakdown["clarity"] = 5
    elif word_count < 150:
        breakdown["clarity"] = 8
    elif word_count < 250:
        breakdown["clarity"] = 12
    elif word_count < 400:
        breakdown["clarity"] = 16
    elif word_count <= 800:
        breakdown["clarity"] = 20
    elif word_count <= 1200:
        breakdown["clarity"] = 16
    else:
        breakdown["clarity"] = 12

    metric_pattern = r"\d+%|\d+\s*(years|months|days)|\$\d|\b\d+\b"
    metrics = len(re.findall(metric_pattern, text.lower()))
    breakdown["impact"] = min(SCORE_MAXIMA["impact"], 5 + metrics * 3)

    experience_words = re.findall(r"\b\w+\b", sections.get("experience", ""))
    if experience_words:
        breakdown["evidence"] = min(SCORE_MAXIMA["evidence"], 5 + len(experience_words) // 12)
    else:
        breakdown["evidence"] = min(14, 4 + word_count // 50)

    # Skip the first line, which is usually the candidate's name and contact details.
    stripped = text.strip()
    body = stripped.split("\n", 1)[1] if "\n" in stripped else stripped
    keywords = extract_keywords(body, limit=SCORE_MAXIMA["keywords"])
    breakdown["keywords"] = min(SCORE_MAXIMA["keywords"], len(set(tokenize(body))))

    score = sum(breakdown.values())
    score = max(0, min(100, score))
    return score, breakdown, keywords


def calculate_match_score(resume_text: str, job_description: str) -> Tuple[int, List[str], List[str], List[str]]:
    # Compare the job's top terms against every resume term, so a skill the
    # resume mentions only once still counts as matched.
    resume_terms = set(tokenize(resume_text))
    job_terms = set(extract_keywords(job_description, limit=30))
    if not job_terms:
        return 0, [], [], []

    matched = sorted(resume_terms & job_terms)
    missing = sorted(job_terms - resume_terms)
    overlap = len(matched)
    total = max(1, len(job_terms))
    score = max(0, min(100, int((overlap / total) * 100)))
    return score, matched, missing, sorted(extract_keywords(resume_text, limit=30))
