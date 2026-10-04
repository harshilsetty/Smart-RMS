import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.config import settings

# Ensure workspace root is in sys.path for evaluation module
if str(settings.ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(settings.ROOT_DIR))

from evaluation.evaluator import RMSEvaluationEngine

router = APIRouter()

@router.get("/summary", summary="Retrieve actual computed evaluation metrics across benchmark RMS dataset")
async def get_evaluation_summary():
    """
    Executes benchmark evaluation dynamically across the evaluation dataset
    and returns runtime computed accuracy, F1, retrieval, and grounding metrics.
    No mock, seeded, or hardcoded values.
    """
    try:
        engine = RMSEvaluationEngine()
        results = await engine.run_evaluation()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation execution failed: {str(e)}")
