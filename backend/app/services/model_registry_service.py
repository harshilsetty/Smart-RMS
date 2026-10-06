import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

class ModelVersion(BaseModel):
    model_name: str
    version: str
    provider: str
    training_dataset: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    status: str = "CHALLENGER" # PRODUCTION, CHALLENGER, REJECTED, ARCHIVED
    creation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evaluation_result: Optional[str] = None

class ModelPromotionAudit(BaseModel):
    action: str # MODEL_PROMOTION_APPROVED, MODEL_PROMOTION_REJECTED, MODEL_ROLLBACK
    previous_model: str
    new_model: str
    reviewer: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evaluation_version: Optional[str] = None
    reason: str

class ModelRegistryService:
    def __init__(self, registry_dir: Optional[Path] = None):
        self.registry_dir = registry_dir or (settings.ROOT_DIR / "ml" / "registry")
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_dir / "model_registry.json"
        self.audit_file = self.registry_dir / "promotion_audit.json"
        
        self._models: List[ModelVersion] = []
        self._audit_log: List[ModelPromotionAudit] = []
        self._load_data()

    def _load_data(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    self._models = [ModelVersion(**m) for m in json.load(f)]
            except Exception as e:
                logger.warning(f"Could not load model registry: {e}")
                
        if self.audit_file.exists():
            try:
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    self._audit_log = [ModelPromotionAudit(**a) for a in json.load(f)]
            except Exception as e:
                logger.warning(f"Could not load audit log: {e}")
                
        if not self._models:
            # Seed the initial production model
            self.register_model(ModelVersion(
                model_name="tfidf_svm",
                version="v1",
                provider="sklearn",
                training_dataset="synthetic_v1",
                status="PRODUCTION",
                metrics={"macro_f1": 0.85}
            ))

    def _save_data(self):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump([m.model_dump() for m in self._models], f, indent=2)
            with open(self.audit_file, "w", encoding="utf-8") as f:
                json.dump([a.model_dump() for a in self._audit_log], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save registry data: {e}")

    def register_model(self, model: ModelVersion) -> ModelVersion:
        self._models.append(model)
        self._save_data()
        return model

    def get_production_model(self) -> Optional[ModelVersion]:
        for m in self._models:
            if m.status == "PRODUCTION":
                return m
        return None

    def get_challenger_models(self) -> List[ModelVersion]:
        return [m for m in self._models if m.status == "CHALLENGER"]

    def promote_model(self, version: str, reviewer: str, reason: str) -> Optional[ModelVersion]:
        challenger = None
        current_prod = self.get_production_model()
        
        for m in self._models:
            if m.version == version and m.status == "CHALLENGER":
                challenger = m
                break
                
        if not challenger:
            return None
            
        # Update statuses
        if current_prod:
            current_prod.status = "ARCHIVED"
        challenger.status = "PRODUCTION"
        
        # Log audit
        self._audit_log.append(ModelPromotionAudit(
            action="MODEL_PROMOTION_APPROVED",
            previous_model=current_prod.version if current_prod else "None",
            new_model=challenger.version,
            reviewer=reviewer,
            evaluation_version=challenger.evaluation_result,
            reason=reason
        ))
        
        self._save_data()
        return challenger

    def rollback_model(self, target_version: str, reviewer: str, reason: str) -> Optional[ModelVersion]:
        current_prod = self.get_production_model()
        target = None
        
        for m in self._models:
            if m.version == target_version and m.status == "ARCHIVED":
                target = m
                break
                
        if not target:
            return None
            
        if current_prod:
            current_prod.status = "ARCHIVED"
        target.status = "PRODUCTION"
        
        self._audit_log.append(ModelPromotionAudit(
            action="MODEL_ROLLBACK",
            previous_model=current_prod.version if current_prod else "None",
            new_model=target.version,
            reviewer=reviewer,
            reason=reason
        ))
        
        self._save_data()
        return target

_registry_singleton = None

def get_model_registry() -> ModelRegistryService:
    global _registry_singleton
    if _registry_singleton is None:
        _registry_singleton = ModelRegistryService()
    return _registry_singleton
