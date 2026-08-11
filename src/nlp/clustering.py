"""
Topic clustering using KMeans on TF-IDF vectors.
"""
from __future__ import annotations

import re
from typing import Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from src.nlp.keywords import _tokenize, STOP_WORDS


def cluster_complaints(
    texts: list[str],
    n_clusters: int = 8,
    top_keywords_per_cluster: int = 10,
) -> tuple[list[dict], list[int]]:
    """
    Cluster complaint narratives and return cluster metadata.
    Returns list of {"cluster_id": int, "label": str, "top_keywords": list[str], "size": int}.
    """
    if len(texts) < n_clusters:
        n_clusters = max(1, len(texts))

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    X = vectorizer.fit_transform(texts)
    feature_names = np.array(vectorizer.get_feature_names_out())

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    clusters = []
    for cid in range(n_clusters):
        center = km.cluster_centers_[cid]
        top_idx = center.argsort()[::-1][:top_keywords_per_cluster]
        keywords = feature_names[top_idx].tolist()
        size = int(np.sum(labels == cid))
        clusters.append({
            "cluster_id": cid,
            "label": f"Topic {cid + 1}: {keywords[0]}",
            "top_keywords": keywords,
            "size": size,
        })

    # Sort by size descending
    clusters.sort(key=lambda c: c["size"], reverse=True)
    return clusters, labels.tolist()
