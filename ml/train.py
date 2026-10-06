"""
Smart RMS - ML Training Pipeline
Milestone 5: Train and Persist Intent Classifiers
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Ensure backend app is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.nlp.ml_classifiers import (
    TFIDFLogisticIntentModel,
    TFIDFSVMIntentModel,
    SentenceTransformerIntentModel,
    MODELS_DIR
)

ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"

def load_train_data(train_path: Path):
    with open(train_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [f"{d['subject']} {d['description']}".strip() for d in data]
    labels = [d["expected_intent"] for d in data]
    return texts, labels

def train_all_models():
    train_path = BASE_DIR / "evaluation" / "datasets" / "split_train.json"
    if not train_path.exists():
        raise FileNotFoundError(f"Training dataset not found at {train_path}. Run ml/dataset.py first.")

    texts, labels = load_train_data(train_path)
    print(f"Loaded {len(texts)} training samples across {len(set(labels))} classes.")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Any] = {}

    # 1. Model 1: TF-IDF + Logistic Regression
    print("\n--- Training Model 1: TF-IDF + Logistic Regression ---")
    t0 = time.time()
    model1 = TFIDFLogisticIntentModel(c_param=1.0, max_features=5000, random_state=42)
    model1.fit(texts, labels)
    t1 = time.time()
    train_time_1 = round(t1 - t0, 4)
    model1.save(MODELS_DIR / "tfidf_logistic.joblib")
    model1.save(ARTIFACTS_DIR / "tfidf_logistic.joblib")
    results["tfidf_logistic"] = {
        "training_time_sec": train_time_1,
        "classes": model1.classes_,
        "artifact": str(MODELS_DIR / "tfidf_logistic.joblib")
    }
    print(f"  Trained in {train_time_1}s. Saved to {MODELS_DIR / 'tfidf_logistic.joblib'}")

    # 2. Model 2: TF-IDF + Calibrated Linear SVM
    print("\n--- Training Model 2: TF-IDF + Calibrated Linear SVM ---")
    t0 = time.time()
    model2 = TFIDFSVMIntentModel(c_param=1.0, max_features=5000, random_state=42)
    model2.fit(texts, labels)
    t1 = time.time()
    train_time_2 = round(t1 - t0, 4)
    model2.save(MODELS_DIR / "tfidf_svm.joblib")
    model2.save(ARTIFACTS_DIR / "tfidf_svm.joblib")
    results["tfidf_svm"] = {
        "training_time_sec": train_time_2,
        "classes": model2.classes_,
        "artifact": str(MODELS_DIR / "tfidf_svm.joblib")
    }
    print(f"  Trained in {train_time_2}s. Saved to {MODELS_DIR / 'tfidf_svm.joblib'}")

    # 3. Model 3: Dense Embeddings + Logistic Regression
    print("\n--- Training Model 3: Dense Embeddings + Logistic Regression ---")
    t0 = time.time()
    model3 = SentenceTransformerIntentModel(random_state=42)
    print(f"  Embedding provider: {model3.embedding_type}")
    model3.fit(texts, labels)
    t1 = time.time()
    train_time_3 = round(t1 - t0, 4)
    model3.save(MODELS_DIR / "sentence_transformer.joblib")
    model3.save(ARTIFACTS_DIR / "sentence_transformer.joblib")
    results["sentence_transformer"] = {
        "training_time_sec": train_time_3,
        "embedding_type": model3.embedding_type,
        "classes": model3.classes_,
        "artifact": str(MODELS_DIR / "sentence_transformer.joblib")
    }
    print(f"  Trained in {train_time_3}s. Saved to {MODELS_DIR / 'sentence_transformer.joblib'}")

    with open(ARTIFACTS_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n=== ALL ML MODELS TRAINED & PERSISTED SUCCESSFULLY ===")
    return results

if __name__ == "__main__":
    train_all_models()
