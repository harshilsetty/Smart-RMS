"""
Smart RMS - Grounding Text Utilities (Milestone 6)

Shared, deterministic helpers used by claim extraction, evidence matching and
claim verification. Keeping them in one place guarantees the claim side and the
evidence side are parsed with *identical* rules (asymmetric parsing was the
root cause of false contradictions found during the Milestone 6 audit, e.g.
"Term 6" being read as a fee of 6 rupees).
"""

import re
from typing import List, Set

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "of", "at", "by", "for",
    "with", "about", "into", "through", "during", "to", "from", "in", "on", "as",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "this", "that", "these", "those", "it", "its", "their",
    "your", "you", "we", "our", "they", "them", "his", "her", "s", "will", "shall",
    "can", "may", "must", "should", "would", "could", "per", "any", "all", "each",
    "which", "who", "whom", "such", "so", "than", "also", "via", "under", "upon",
}

NEGATION_TERMS = ("no ", "not ", "never ", "without ", "cannot ", "non-", "ineligible",
                  "prohibited", "barred", "debarred", "none ")

NUM_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fourteen": 14,
    "fifteen": 15, "twenty": 20, "thirty": 30, "forty-five": 45, "sixty": 60, "ninety": 90,
}

_UNIT_TO_HOURS = {"hour": 1, "day": 24, "week": 168, "month": 720, "year": 8760}

_NUM = r"(\d+(?:\.\d+)?|" + "|".join(sorted(NUM_WORDS, key=len, reverse=True)) + r")"
DURATION_RE = re.compile(
    _NUM + r"(?:\s*(?:to|-|–)\s*" + _NUM + r")?\s*-?\s*(?:calendar\s+|working\s+|business\s+)?"
    r"(hour|day|week|month|year)s?\b",
    re.IGNORECASE,
)
# Currency REQUIRES an explicit marker (₹ / Rs / INR / rupees). Bare numbers are never fees.
CURRENCY_RE = re.compile(
    r"(?:₹|\brs\.?|\binr)\s*(\d[\d,]*(?:\.\d+)?)|(\d[\d,]*(?:\.\d+)?)\s*(?:rupees|inr)\b",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent\b)", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def _to_num(tok: str) -> float:
    tok = tok.lower()
    if tok in NUM_WORDS:
        return float(NUM_WORDS[tok])
    return float(tok)


def split_sentences(text: str) -> List[str]:
    """Splits text into sentences; protects decimals and 'Rs.' abbreviations."""
    if not text:
        return []
    out: List[str] = []
    for line in text.split("\n"):
        line = re.sub(r"^\s*(\d+\.|\-|\*|•)\s+", "", line.strip())
        if not line:
            continue
        protected = re.sub(r"\b(Rs|rs|No|no|Dr|dr|Sec|sec|Cl|cl)\.", r"\1<DOT>", line)
        for part in re.split(r"(?<=[.!?])[\"”']?\s+(?=[\"“']?[A-Z0-9₹])", protected):
            part = part.replace("<DOT>", ".").strip()
            if part:
                out.append(part)
    return out


def tokenize(text: str) -> Set[str]:
    words = re.findall(r"[a-z0-9₹]+", (text or "").lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def containment(claim_text: str, evidence_text: str) -> float:
    """Fraction of claim content-tokens present in the evidence text (0..1)."""
    c = tokenize(claim_text)
    if not c:
        return 0.0
    return len(c & tokenize(evidence_text)) / len(c)


def jaccard(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def extract_durations_hours(text: str) -> Set[float]:
    """All durations normalised to hours. Ranges ('7 to 10 working days') yield both ends."""
    found: Set[float] = set()
    for m in DURATION_RE.finditer(text or ""):
        unit = _UNIT_TO_HOURS[m.group(3).lower()]
        found.add(_to_num(m.group(1)) * unit)
        if m.group(2):
            found.add(_to_num(m.group(2)) * unit)
    return found


def extract_currency(text: str) -> Set[float]:
    found: Set[float] = set()
    for m in CURRENCY_RE.finditer(text or ""):
        raw = (m.group(1) or m.group(2) or "").replace(",", "")
        try:
            val = float(raw)
            if val > 0:
                found.add(val)
        except ValueError:
            pass
    return found


def extract_percentages(text: str) -> Set[float]:
    return {float(m.group(1)) for m in PERCENT_RE.finditer(text or "")}


def extract_numbers(text: str) -> Set[float]:
    nums = {float(n) for n in NUMBER_RE.findall(text or "")}
    low = (text or "").lower()
    for w, v in NUM_WORDS.items():
        if re.search(rf"\b{w}\b", low):
            nums.add(float(v))
    return nums


def has_negation(text: str) -> bool:
    low = f" {(text or '').lower()} "
    return any(t in low for t in NEGATION_TERMS)
