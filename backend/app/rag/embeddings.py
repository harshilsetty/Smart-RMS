"""
Modular embedding provider architecture for Smart RMS RAG pipeline.
Supports local Sentence Transformers and deterministic offline embeddings.
"""

import math
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from app.nlp.preprocessing import tokenize, clean_text

class EmbeddingProvider(ABC):
    """Abstract base class for RAG text embedding generation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the embedding provider."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimension of generated embeddings."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates embedding for a single string."""
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of strings."""
        return [self.embed_text(t) for t in texts]


class DeterministicLocalEmbeddingProvider(EmbeddingProvider):
    """
    High-performance, deterministic, zero-dependency local embedding provider.
    Projects domain tokens, sub-word character n-grams, and semantic keywords
    into a 384-dimensional L2-normalized dense feature space.
    Guarantees reproducible offline evaluation and sub-millisecond execution.
    """

    DIM = 384

    # Domain synonyms and concept expansions
    DOMAIN_SYNONYMS = {
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
        "mac address": "radius wifi"
    }

    @property
    def name(self) -> str:
        return "deterministic-local-dense-384"

    @property
    def dimension(self) -> int:
        return self.DIM

    def _normalize(self, text: str) -> str:
        cleaned = clean_text(text).lower()
        for syn, canonical in self.DOMAIN_SYNONYMS.items():
            cleaned = cleaned.replace(syn, canonical)
        return cleaned

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            # Return zero vector with unit norm fallback
            vec = [0.0] * self.DIM
            vec[0] = 1.0
            return vec

        normalized = self._normalize(text)
        tokens = tokenize(normalized, remove_stopwords=False)
        vec = np.zeros(self.DIM, dtype=np.float32)

        # 1. Word token hashing with frequency weighting
        for token in tokens:
            # Hash to index and sign
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.DIM
            sign = 1.0 if ((h >> 16) % 2 == 0) else -1.0
            # Weight longer, informative tokens slightly higher
            weight = math.log1p(len(token))
            vec[idx] += sign * weight

        # 2. Sub-word character 3-gram hashing for morphological matching
        n = 3
        if len(normalized) >= n:
            for i in range(len(normalized) - n + 1):
                gram = normalized[i:i + n]
                h_gram = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
                idx_gram = h_gram % self.DIM
                sign_gram = 1.0 if ((h_gram >> 8) % 2 == 0) else -1.0
                vec[idx_gram] += sign_gram * 0.35

        # 3. L2 Unit Normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    Neural dense embedding provider using SentenceTransformers or HuggingFace Transformers.
    Defaults to 'sentence-transformers/all-MiniLM-L6-v2' (384-d).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            self._model = None

    @property
    def name(self) -> str:
        return f"sentence-transformers/{self.model_name}"

    @property
    def dimension(self) -> int:
        return 384

    def is_available(self) -> bool:
        return self._model is not None

    def embed_text(self, text: str) -> List[float]:
        if not self._model:
            raise RuntimeError(f"Model '{self.model_name}' is not loaded.")
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not self._model:
            raise RuntimeError(f"Model '{self.model_name}' is not loaded.")
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def get_embedding_provider(provider_type: Optional[str] = None) -> EmbeddingProvider:
    """
    Factory creating the active embedding provider.
    Gracefully falls back to DeterministicLocalEmbeddingProvider when offline or unconfigured,
    while explicitly identifying the active provider.
    """
    if provider_type == "sentence-transformers":
        st_provider = SentenceTransformerEmbeddingProvider()
        if st_provider.is_available():
            return st_provider
        # Clear notice: fallback chosen because model is not available in local environment
        print("[EmbeddingFactory] SentenceTransformer unavailable. Using deterministic local provider.")

    return DeterministicLocalEmbeddingProvider()
