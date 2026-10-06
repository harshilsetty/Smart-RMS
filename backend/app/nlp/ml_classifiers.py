"""
Smart RMS - Machine Learning Intent Classifiers
Milestone 5: Modular Model Providers (TF-IDF + Logistic, TF-IDF + Linear SVM, Dense Embedding + Classifier)
"""

import os
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

from app.nlp.schemas import IntentType, IntentClassificationResult
from app.nlp.preprocessing import normalize_text, clean_text
from app.nlp.intent_classifier import BaseIntentClassifier, RuleBasedIntentClassifier

MODELS_DIR = Path(__file__).resolve().parent / "models"


class DeterministicIntentModel(RuleBasedIntentClassifier):
    """Alias/Adapter for the deterministic baseline classifier."""
    @property
    def classifier_name(self) -> str:
        return "deterministic_baseline"

    def predict(self, texts: List[str]) -> List[str]:
        return [self.classify(t).intent for t in texts]

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Approximates class probabilities from rule-based keyword weights."""
        all_intents = [
            IntentType.HOSTEL_MAINTENANCE.value,
            IntentType.FEE_PAYMENT.value,
            IntentType.EXAMINATION.value,
            IntentType.ACADEMIC.value,
            IntentType.ATTENDANCE.value,
            IntentType.SCHOLARSHIP.value,
            IntentType.IT_SUPPORT.value,
            IntentType.STUDENT_SERVICES.value,
            IntentType.GENERAL_INQUIRY.value,
            IntentType.UNKNOWN.value,
        ]
        probs = []
        for text in texts:
            res = self.classify(text)
            p_vec = np.ones(len(all_intents)) * 0.02
            if res.intent in all_intents:
                idx = all_intents.index(res.intent)
                p_vec[idx] = max(res.confidence, 0.5)
            # normalize
            p_vec = p_vec / np.sum(p_vec)
            probs.append(p_vec)
        return np.array(probs)


class TFIDFLogisticIntentModel(BaseIntentClassifier):
    """
    Model 1: TF-IDF n-grams + Multinomial Logistic Regression.
    Features: Word & Subword n-grams (1, 2), sublinear term frequency, balanced class weights.
    Provides calibrated probability outputs and explainable top feature terms.
    """

    def __init__(self, c_param: float = 1.0, max_features: int = 5000, random_state: int = 42):
        self.c_param = c_param
        self.max_features = max_features
        self.random_state = random_state
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=self.max_features,
            sublinear_tf=True,
            stop_words="english"
        )
        self.classifier = LogisticRegression(
            C=self.c_param,
            max_iter=1000,
            class_weight="balanced",
            random_state=self.random_state
        )
        self.classes_: List[str] = []
        self._is_trained = False

    @property
    def classifier_name(self) -> str:
        return "tfidf_logistic"

    def fit(self, texts: List[str], labels: List[str]):
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned_texts)
        self.classifier.fit(X, labels)
        self.classes_ = list(self.classifier.classes_)
        self._is_trained = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned_texts)
        return list(self.classifier.predict(X))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned_texts)
        return self.classifier.predict_proba(X)

    def classify(self, text: str) -> IntentClassificationResult:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned = normalize_text(text)
        X = self.vectorizer.transform([cleaned])
        probs = self.classifier.predict_proba(X)[0]
        
        sorted_indices = np.argsort(probs)[::-1]
        top_idx = sorted_indices[0]
        second_idx = sorted_indices[1] if len(sorted_indices) > 1 else top_idx

        top_intent = self.classes_[top_idx]
        second_intent = self.classes_[second_idx] if len(sorted_indices) > 1 else None
        top_prob = float(probs[top_idx])
        second_prob = float(probs[second_idx]) if len(sorted_indices) > 1 else 0.0
        margin = float(top_prob - second_prob)

        # Ambiguity detection: narrow margin or very low top probability
        is_ambiguous = (margin < 0.10) or (top_prob < 0.38) or (top_intent == IntentType.UNKNOWN.value)

        # Explainability: Extract top influential n-grams from vectorizer
        feature_names = self.vectorizer.get_feature_names_out()
        coef = self.classifier.coef_[top_idx]
        doc_vector = X.toarray()[0]
        active_indices = np.where(doc_vector > 0)[0]
        
        matched_keywords = []
        if len(active_indices) > 0:
            scores = [(feature_names[i], coef[i] * doc_vector[i]) for i in active_indices]
            scores.sort(key=lambda x: x[1], reverse=True)
            matched_keywords = [w for w, s in scores[:5] if s > 0]

        reason = (
            f"Classified by TF-IDF + Logistic Regression as {top_intent} "
            f"(P={top_prob:.2f}, margin={margin:.2f}). "
            f"Key signals: {', '.join(matched_keywords[:4]) if matched_keywords else 'distributed n-gram weights'}."
        )
        if is_ambiguous:
            reason += f" Competes with {second_intent} (P={second_prob:.2f}); staff verification required."

        return IntentClassificationResult(
            intent=top_intent,
            confidence=round(top_prob, 2),
            secondary_intent=second_intent,
            margin=round(margin, 2),
            matched_keywords=matched_keywords,
            reason=reason,
            is_ambiguous=is_ambiguous
        )

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "classes_": self.classes_,
            "c_param": self.c_param,
            "max_features": self.max_features,
            "random_state": self.random_state
        }, filepath)

    def load(self, filepath: Path):
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.classifier = data["classifier"]
        self.classes_ = data["classes_"]
        self.c_param = data.get("c_param", 1.0)
        self.max_features = data.get("max_features", 5000)
        self.random_state = data.get("random_state", 42)
        self._is_trained = True
        return self


class TFIDFSVMIntentModel(BaseIntentClassifier):
    """
    Model 2: TF-IDF n-grams + Linear SVM with CalibratedClassifierCV.
    Uses Platt scaling (sigmoid calibration) to produce authentic, calibrated posterior probabilities.
    """

    def __init__(self, c_param: float = 1.0, max_features: int = 5000, random_state: int = 42):
        self.c_param = c_param
        self.max_features = max_features
        self.random_state = random_state
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=self.max_features,
            sublinear_tf=True,
            stop_words="english"
        )
        base_svm = LinearSVC(
            C=self.c_param,
            class_weight="balanced",
            random_state=self.random_state
        )
        self.classifier = CalibratedClassifierCV(base_svm, cv=3)
        self.classes_: List[str] = []
        self._is_trained = False

    @property
    def classifier_name(self) -> str:
        return "tfidf_svm"

    def fit(self, texts: List[str], labels: List[str]):
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned_texts)
        self.classifier.fit(X, labels)
        self.classes_ = list(self.classifier.classes_)
        self._is_trained = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned_texts)
        return list(self.classifier.predict(X))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned_texts = [normalize_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned_texts)
        return self.classifier.predict_proba(X)

    def classify(self, text: str) -> IntentClassificationResult:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        cleaned = normalize_text(text)
        X = self.vectorizer.transform([cleaned])
        probs = self.classifier.predict_proba(X)[0]

        sorted_indices = np.argsort(probs)[::-1]
        top_idx = sorted_indices[0]
        second_idx = sorted_indices[1] if len(sorted_indices) > 1 else top_idx

        top_intent = self.classes_[top_idx]
        second_intent = self.classes_[second_idx] if len(sorted_indices) > 1 else None
        top_prob = float(probs[top_idx])
        second_prob = float(probs[second_idx]) if len(sorted_indices) > 1 else 0.0
        margin = float(top_prob - second_prob)

        is_ambiguous = (margin < 0.10) or (top_prob < 0.38) or (top_intent == IntentType.UNKNOWN.value)

        # Extract active words in text
        tokens = cleaned.split()
        matched_keywords = [t for t in tokens if len(t) > 3][:5]

        reason = (
            f"Classified by Calibrated Linear SVM as {top_intent} "
            f"(P={top_prob:.2f}, margin={margin:.2f})."
        )
        if is_ambiguous:
            reason += f" Closely competes with {second_intent} (P={second_prob:.2f}); staff review required."

        return IntentClassificationResult(
            intent=top_intent,
            confidence=round(top_prob, 2),
            secondary_intent=second_intent,
            margin=round(margin, 2),
            matched_keywords=matched_keywords,
            reason=reason,
            is_ambiguous=is_ambiguous
        )

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "classifier": self.classifier,
            "classes_": self.classes_,
            "c_param": self.c_param,
            "max_features": self.max_features,
            "random_state": self.random_state
        }, filepath)

    def load(self, filepath: Path):
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.classifier = data["classifier"]
        self.classes_ = data["classes_"]
        self.c_param = data.get("c_param", 1.0)
        self.max_features = data.get("max_features", 5000)
        self.random_state = data.get("random_state", 42)
        self._is_trained = True
        return self


class SentenceTransformerIntentModel(BaseIntentClassifier):
    """
    Model 3: Dense Embeddings + Multinomial Logistic Regression.
    Supports either neural SentenceTransformers ('all-MiniLM-L6-v2', 384-d)
    or local deterministic dense embedding provider fallback.
    """

    def __init__(self, embedding_type: str = "sentence_transformer", random_state: int = 42):
        self.embedding_type = embedding_type
        self.random_state = random_state
        self.embedder = None
        self._init_embedder()
        self.classifier = LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=self.random_state
        )
        self.classes_: List[str] = []
        self._is_trained = False

    def _init_embedder(self):
        try:
            from app.rag.embeddings import SentenceTransformerEmbeddingProvider
            prov = SentenceTransformerEmbeddingProvider("all-MiniLM-L6-v2")
            if prov.is_available():
                self.embedder = prov
                self.embedding_type = "sentence_transformer_all_MiniLM_L6_v2"
                return
        except Exception:
            pass

        # Fallback to local 384-d dense unit-normalized embedding provider
        from app.rag.embeddings import DeterministicLocalEmbeddingProvider
        self.embedder = DeterministicLocalEmbeddingProvider(dimension=384)
        self.embedding_type = "deterministic_dense_local_384"

    @property
    def classifier_name(self) -> str:
        return "sentence_transformer"

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        vectors = [self.embedder.embed_text(normalize_text(t)) for t in texts]
        return np.array(vectors, dtype=np.float32)

    def fit(self, texts: List[str], labels: List[str]):
        X = self._embed_batch(texts)
        self.classifier.fit(X, labels)
        self.classes_ = list(self.classifier.classes_)
        self._is_trained = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self._embed_batch(texts)
        return list(self.classifier.predict(X))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        X = self._embed_batch(texts)
        return self.classifier.predict_proba(X)

    def classify(self, text: str) -> IntentClassificationResult:
        if not self._is_trained:
            raise RuntimeError("Model is not trained. Call fit() or load() first.")
        vec = self._embed_batch([text])
        probs = self.classifier.predict_proba(vec)[0]

        sorted_indices = np.argsort(probs)[::-1]
        top_idx = sorted_indices[0]
        second_idx = sorted_indices[1] if len(sorted_indices) > 1 else top_idx

        top_intent = self.classes_[top_idx]
        second_intent = self.classes_[second_idx] if len(sorted_indices) > 1 else None
        top_prob = float(probs[top_idx])
        second_prob = float(probs[second_idx]) if len(sorted_indices) > 1 else 0.0
        margin = float(top_prob - second_prob)

        is_ambiguous = (margin < 0.10) or (top_prob < 0.38) or (top_intent == IntentType.UNKNOWN.value)

        reason = (
            f"Classified via Dense Embeddings ({self.embedding_type}) + Logistic Regression as {top_intent} "
            f"(P={top_prob:.2f}, margin={margin:.2f})."
        )
        if is_ambiguous:
            reason += f" Close competition with {second_intent} (P={second_prob:.2f}); staff review required."

        return IntentClassificationResult(
            intent=top_intent,
            confidence=round(top_prob, 2),
            secondary_intent=second_intent,
            margin=round(margin, 2),
            matched_keywords=[],
            reason=reason,
            is_ambiguous=is_ambiguous
        )

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "classifier": self.classifier,
            "classes_": self.classes_,
            "embedding_type": self.embedding_type,
            "random_state": self.random_state
        }, filepath)

    def load(self, filepath: Path):
        data = joblib.load(filepath)
        self.classifier = data["classifier"]
        self.classes_ = data["classes_"]
        self.embedding_type = data.get("embedding_type", self.embedding_type)
        self.random_state = data.get("random_state", 42)
        self._init_embedder()
        self._is_trained = True
        return self
