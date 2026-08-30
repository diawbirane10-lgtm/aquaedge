from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(slots=True)
class Document:
    doc_id: str
    text: str
    source: str = ""


class TfidfRetriever:
    """Small offline baseline retriever.

    This is deliberately simple. It gives the project a measurable baseline
    before introducing embedding APIs or local embedding models.
    """

    def __init__(self, documents: list[Document]) -> None:
        if not documents:
            raise ValueError("At least one document is required")
        self.documents = documents
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.matrix = self.vectorizer.fit_transform([d.text for d in documents])

    def search(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        order = scores.argsort()[::-1][:k]
        return [(self.documents[i], float(scores[i])) for i in order]
