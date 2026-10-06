import re
from typing import List, Set, Dict

STOPWORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "to", "for", "with", "by", "of", "and",
    "or", "is", "am", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "i", "me", "my", "myself", "we", "our", "you",
    "your", "he", "him", "she", "her", "it", "its", "they", "them", "this", "that",
    "these", "those", "from", "as", "if", "so", "than", "too", "very", "s", "t",
    "can", "will", "just", "should", "now", "please", "kindly", "sir", "madam",
    "respected", "dear", "hello", "hi", "regards", "thank", "thanks"
}

DOMAIN_SYNONYMS: Dict[str, str] = {
    "hall ticket": "admit card",
    "hallticket": "admit card",
    "examination": "exam",
    "tuition fee": "fee",
    "tuition": "fee",
    "fees": "fee",
    "re-evaluation": "reevaluation",
    "re-check": "reevaluation",
    "wi-fi": "wifi",
    "continuous assessment": "ca marks",
    "marks discrepancy": "grade discrepancy",
    "marks": "grade",
    "hospitalization": "medical leave",
    "illness": "medical leave",
    "dengue": "medical leave",
    "concession": "scholarship",
    "nsp": "scholarship",
    "pms": "scholarship",
    "air conditioning": "ac unit",
    "ac repair": "ac unit",
    "leakage": "plumbing",
    "hostel room": "hostel accommodation",
    "mac address": "radius wifi"
}

def clean_text(text: str) -> str:
    """Normalizes whitespace and standardizes punctuation while preserving hyphenated identifiers."""
    if not text:
        return ""
    # Normalize multiple whitespace characters
    cleaned = re.sub(r"[\r\n\t]+", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

def normalize_text(text: str) -> str:
    """Performs clean_text, lowercasing, and canonical domain synonym substitution."""
    cleaned = clean_text(text).lower()
    for syn, canonical in DOMAIN_SYNONYMS.items():
        cleaned = cleaned.replace(syn, canonical)
    return cleaned

def tokenize(text: str, remove_stopwords: bool = False) -> List[str]:
    """Tokenizes text into words and identifier tokens (e.g. 'cse-472', 'bh-4')."""
    cleaned = clean_text(text).lower()
    # Match alphanumeric sequences optionally containing internal hyphens or slashes
    tokens = re.findall(r"[a-z0-9]+(?:[\-_/][a-z0-9]+)*", cleaned)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return tokens

def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extracts contiguous word n-grams from a token sequence."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

def preprocess_for_matching(text: str) -> Set[str]:
    """Generates an enriched token set including unigrams and bigrams for matching."""
    tokens = tokenize(text, remove_stopwords=True)
    bigrams = extract_ngrams(tokens, n=2)
    return set(tokens).union(set(bigrams))
