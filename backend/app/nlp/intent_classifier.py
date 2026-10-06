from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from app.nlp.schemas import IntentType, IntentClassificationResult
from app.nlp.preprocessing import tokenize, extract_ngrams, normalize_text

class BaseIntentClassifier(ABC):
    """Abstract interface for Intent Classifiers in Smart RMS."""

    @abstractmethod
    def classify(self, text: str) -> IntentClassificationResult:
        """Classifies text into an intent with confidence and explainability metadata."""
        pass

class RuleBasedIntentClassifier(BaseIntentClassifier):
    """
    Deterministic rule & keyword-based baseline intent classifier.
    Computes confidence score based on weighted token matches and margin over secondary intent.
    """

    INTENT_KEYWORDS: Dict[str, Dict[str, float]] = {
        IntentType.HOSTEL_MAINTENANCE.value: {
            "leak": 2.5, "leakage": 2.5, "ac unit": 3.0, "air conditioner": 2.5,
            "hostel": 2.0, "room": 1.5, "warden": 2.0, "bh": 2.0, "gh": 2.0,
            "electrician": 2.0, "plumber": 2.0, "switchboard": 2.0, "geyser": 2.0,
            "mess": 1.8, "water": 1.5, "fan": 1.5, "cleaning": 1.5
        },
        IntentType.FEE_PAYMENT.value: {
            "fee": 2.5, "fees": 2.5, "refund": 3.0, "deducted twice": 3.5, "debited twice": 3.5,
            "bank": 2.0, "payment": 2.0, "gateway": 2.5, "tuition": 2.0, "inr": 1.5,
            "transaction": 2.0, "ledger": 2.5, "reconciliation": 3.0, "receipt": 1.8,
            "excess": 2.0, "double payment": 3.5
        },
        IntentType.EXAMINATION.value: {
            "admit card": 3.5, "hall ticket": 3.5, "exam": 2.5, "examination": 2.5,
            "blocked": 2.0, "clearance hold": 3.0, "library clearance": 2.5, "end term": 2.5,
            "re-evaluation": 3.5, "mid term": 2.0, "seating plan": 2.0, "datesheet": 3.0,
            "detained": 2.5, "roll number": 1.8, "marksheet": 3.0, "transcript": 2.0,
            "exam center": 3.0, "seating": 2.5
        },
        IntentType.ACADEMIC.value: {
            "ca": 2.5, "ca-1": 3.0, "ca-2": 3.0, "ca-3": 3.0, "marks": 2.5, "rubric": 3.0,
            "grade": 2.5, "marks discrepancy": 3.5, "continuous assessment": 3.0,
            "course coordinator": 2.5, "syllabus": 2.5, "assignment": 2.0,
            "instructor": 2.0, "credit": 2.5, "curriculum": 2.0, "credit registration": 3.5,
            "academic mentor": 3.0, "mentor": 2.5
        },
        IntentType.ATTENDANCE.value: {
            "attendance": 3.5, "medical leave": 3.5, "hospitalization": 3.0, "dengue": 2.5,
            "condonation": 3.5, "health center": 2.5, "fitness certificate": 2.5,
            "discharge summary": 3.0, "duty leave": 3.0, "illness": 2.0, "75%": 2.5,
            "attendance drop": 2.5, "biometric": 2.5, "sports tournament": 3.0
        },
        IntentType.SCHOLARSHIP.value: {
            "scholarship": 4.0, "nsp": 3.5, "national scholarship": 3.5, "post-matric": 3.0,
            "institute verification": 3.5, "state portal": 2.5, "merit scholarship": 4.0,
            "freeship": 3.5, "disbursement": 2.5, "pms": 3.0, "nodal officer": 3.0,
            "income certificate": 3.0, "central sector": 3.5
        },
        IntentType.IT_SUPPORT.value: {
            "wi-fi": 3.5, "wifi": 3.5, "mac address": 3.5, "fortinet": 3.0, "radius": 3.0,
            "device limit": 3.0, "portal login": 2.5, "credentials": 2.5, "password reset": 3.0,
            "network": 2.5, "ums login": 3.0, "ip address": 2.0, "internet": 2.5,
            "email": 3.5, "mailbox": 3.5, "storage full": 3.5, "quota": 3.0,
            "workstation": 3.5, "computer lab": 3.0, "laboratory workstation": 3.5,
            "access point": 3.5
        },
        IntentType.STUDENT_SERVICES.value: {
            "bonafide": 3.5, "certificate": 2.5, "medium of instruction": 3.5, "moi": 3.5,
            "visa": 2.5, "exchange program": 2.5, "migration": 3.5,
            "e-document": 2.0, "student id card": 3.5, "duplicate id": 3.5,
            "character": 3.0, "conduct certificate": 3.5
        }
    }

    AMBIGUOUS_PATTERNS = [
        "issue is not solved",
        "need help with fee",
        "need help with fees",
        "something is wrong",
        "problem with portal",
        "please help me urgently",
        "status pending please check",
        "query regarding university",
        "matter is pending"
    ]

    def classify(self, text: str) -> IntentClassificationResult:
        normalized = normalize_text(text)
        tokens = tokenize(normalized, remove_stopwords=False)
        bigrams = extract_ngrams(tokens, n=2)
        n_gram_pool = set(tokens).union(set(bigrams))

        # Check for explicitly ambiguous or low-information queries
        is_generic = any(pat in normalized for pat in self.AMBIGUOUS_PATTERNS)

        scores: Dict[str, float] = {}
        matches_per_intent: Dict[str, List[str]] = {}

        for intent, kw_dict in self.INTENT_KEYWORDS.items():
            intent_score = 0.0
            matched: List[str] = []
            for kw, weight in kw_dict.items():
                if kw in normalized or kw in n_gram_pool:
                    intent_score += weight
                    matched.append(kw)
            scores[intent] = intent_score
            matches_per_intent[intent] = matched

        # Sort intents by score descending
        sorted_intents = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_intent, top_score = sorted_intents[0]
        second_intent, second_score = sorted_intents[1] if len(sorted_intents) > 1 else (None, 0.0)

        # Base case 1: Zero domain signal -> UNKNOWN
        if top_score == 0.0:
            return IntentClassificationResult(
                intent=IntentType.UNKNOWN.value,
                confidence=0.30,
                secondary_intent=None,
                margin=0.0,
                matched_keywords=[],
                reason="No recognizable domain signals detected; classified as UNKNOWN intent.",
                is_ambiguous=True
            )

        margin = top_score - second_score

        # Base case 2: Competing top intents with minimal margin or explicitly ambiguous pattern -> Ambiguity flag
        is_ambiguous = (second_score > 0 and margin < 0.5) or is_generic

        # Compute calibrated heuristic confidence: evidence weight + margin over second best
        raw_conf = 0.70 + min(top_score * 0.03, 0.20) + min(margin * 0.02, 0.08)
        if is_ambiguous:
            raw_conf -= 0.18
        confidence = round(min(max(raw_conf, 0.50), 0.98), 2)

        matched_kws = matches_per_intent.get(top_intent, [])
        reason = f"Matched {top_intent} keywords: {', '.join(matched_kws[:4])}."
        if is_generic:
            reason += " Request query is terse/ambiguous; requires student clarification or staff verification."
        elif is_ambiguous:
            reason += f" Closely competes with {second_intent} (margin: {margin:.1f}); staff verification required."

        return IntentClassificationResult(
            intent=top_intent,
            confidence=confidence,
            secondary_intent=second_intent if second_score > 0 else None,
            margin=round(margin, 2),
            matched_keywords=matched_kws,
            reason=reason,
            is_ambiguous=is_ambiguous
        )

    @property
    def classifier_name(self) -> str:
        return "deterministic_baseline"


def get_intent_classifier(provider_name: Optional[str] = None) -> BaseIntentClassifier:
    """
    Factory function to instantiate configured intent classifier.
    Supports:
      - 'deterministic': Fast rule-based baseline
      - 'tfidf_logistic': TF-IDF + Logistic Regression
      - 'tfidf_svm': TF-IDF + Linear SVM (calibrated)
      - 'sentence_transformer': Dense Embeddings + Classifier
    Gracefully falls back to RuleBasedIntentClassifier if model artifacts are not found or loading fails.
    """
    from app.config import settings
    selected = provider_name or getattr(settings, "NLP_MODEL_PROVIDER", "deterministic")
    selected = str(selected).lower().strip()

    if selected == "deterministic":
        return RuleBasedIntentClassifier()

    try:
        from app.nlp.ml_classifiers import (
            TFIDFLogisticIntentModel,
            TFIDFSVMIntentModel,
            SentenceTransformerIntentModel,
            MODELS_DIR
        )

        if selected == "tfidf_logistic":
            model_path = MODELS_DIR / "tfidf_logistic.joblib"
            if model_path.exists():
                return TFIDFLogisticIntentModel().load(model_path)
            # Return fresh untrained model or fallback
            return RuleBasedIntentClassifier()

        elif selected == "tfidf_svm":
            model_path = MODELS_DIR / "tfidf_svm.joblib"
            if model_path.exists():
                return TFIDFSVMIntentModel().load(model_path)
            return RuleBasedIntentClassifier()

        elif selected in ["sentence_transformer", "dense_embedding"]:
            model_path = MODELS_DIR / "sentence_transformer.joblib"
            if model_path.exists():
                return SentenceTransformerIntentModel().load(model_path)
            return RuleBasedIntentClassifier()

    except Exception:
        pass

    return RuleBasedIntentClassifier()
