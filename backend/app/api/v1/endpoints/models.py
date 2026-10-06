from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.model_registry_service import get_model_registry, ModelRegistryService, ModelVersion

router = APIRouter()

@router.get("/production", response_model=ModelVersion, summary="Get current production model")
def get_production(registry: ModelRegistryService = Depends(get_model_registry)):
    model = registry.get_production_model()
    if not model:
        raise HTTPException(status_code=404, detail="No production model found")
    return model

@router.get("/challengers", response_model=List[ModelVersion], summary="List challenger models")
def list_challengers(registry: ModelRegistryService = Depends(get_model_registry)):
    return registry.get_challenger_models()

@router.post("/{version}/promote", response_model=ModelVersion, summary="Promote a challenger to production")
def promote_model(version: str, reviewer: str, reason: str, registry: ModelRegistryService = Depends(get_model_registry)):
    # Simple RBAC simulation
    if reviewer == "UNAUTHORIZED":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    model = registry.promote_model(version, reviewer, reason)
    if not model:
        raise HTTPException(status_code=404, detail="Challenger not found")
    return model

@router.post("/{version}/rollback", response_model=ModelVersion, summary="Rollback to a previous model")
def rollback_model(version: str, reviewer: str, reason: str, registry: ModelRegistryService = Depends(get_model_registry)):
    if reviewer == "UNAUTHORIZED":
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    model = registry.rollback_model(version, reviewer, reason)
    if not model:
        raise HTTPException(status_code=404, detail="Target version not found or not archived")
    return model
