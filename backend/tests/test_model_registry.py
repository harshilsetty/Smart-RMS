import pytest
from app.services.model_registry_service import ModelRegistryService, ModelVersion
from pathlib import Path

@pytest.fixture
def temp_registry_dir(tmp_path):
    return tmp_path / "registry_test"

def test_initial_production_model(temp_registry_dir):
    service = ModelRegistryService(registry_dir=temp_registry_dir)
    prod = service.get_production_model()
    assert prod is not None
    assert prod.status == "PRODUCTION"
    assert prod.version == "v1"

def test_register_and_list_challenger(temp_registry_dir):
    service = ModelRegistryService(registry_dir=temp_registry_dir)
    service.register_model(ModelVersion(
        model_name="tfidf_svm",
        version="v2",
        provider="sklearn",
        status="CHALLENGER"
    ))
    
    challengers = service.get_challenger_models()
    assert len(challengers) == 1
    assert challengers[0].version == "v2"

def test_promotion_workflow(temp_registry_dir):
    service = ModelRegistryService(registry_dir=temp_registry_dir)
    service.register_model(ModelVersion(
        model_name="tfidf_svm",
        version="v2",
        provider="sklearn",
        status="CHALLENGER"
    ))
    
    promoted = service.promote_model("v2", reviewer="ADMIN-01", reason="Passed safety gates")
    assert promoted is not None
    assert promoted.status == "PRODUCTION"
    
    prod = service.get_production_model()
    assert prod.version == "v2"
    
    # Check that v1 is archived
    v1 = next((m for m in service._models if m.version == "v1"), None)
    assert v1.status == "ARCHIVED"

def test_rollback_workflow(temp_registry_dir):
    service = ModelRegistryService(registry_dir=temp_registry_dir)
    service.register_model(ModelVersion(
        model_name="tfidf_svm",
        version="v2",
        provider="sklearn",
        status="CHALLENGER"
    ))
    service.promote_model("v2", reviewer="ADMIN-01", reason="Passed")
    
    # Rollback to v1
    rolled_back = service.rollback_model("v1", reviewer="ADMIN-02", reason="Latency issues")
    assert rolled_back is not None
    assert rolled_back.status == "PRODUCTION"
    
    prod = service.get_production_model()
    assert prod.version == "v1"
