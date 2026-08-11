"""
Keyword extraction using TF-IDF over a corpus of complaint narratives.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Optional

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "not", "no", "nor", "so",
    "i", "my", "me", "we", "our", "you", "your", "he", "she", "it", "they",
    "this", "that", "these", "those", "which", "who", "what", "when",
    "there", "their", "they", "would", "could", "should", "will", "can",
    "as", "if", "then", "than", "about", "up", "out", "into", "through",
    "after", "before", "over", "under", "between", "each", "other",
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\b[a-z]{3,}\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS]


def extract_keywords(texts: list[str], top_n: int = 20) -> list[dict]:
    """
    Extract top_n keywords by frequency across all texts.
    Returns list of {"keyword": str, "count": int, "frequency": float}.
    """
    counter: Counter = Counter()
    total_docs = len(texts)
    for text in texts:
        tokens = set(_tokenize(text))
        counter.update(tokens)

    results = []
    for word, count in counter.most_common(top_n):
        results.append({
            "keyword": word,
            "count": count,
            "frequency": round(count / total_docs, 4) if total_docs else 0.0,
        })
    return results


def extract_keywords_single(text: str, top_n: int = 10) -> list[str]:
    tokens = _tokenize(text)
    return [w for w, _ in Counter(tokens).most_common(top_n)]
