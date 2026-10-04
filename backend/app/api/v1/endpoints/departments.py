from typing import List
from fastapi import APIRouter, HTTPException
from app.services.rms_service import RMSService
from app.schemas.contracts import Department

router = APIRouter()
rms_service = RMSService()

@router.get("", response_model=List[Department], summary="List all university departments with SLA policies")
def list_departments():
    return rms_service.list_departments()

@router.get("/{department_id}", response_model=Department, summary="Get department details by ID or code")
def get_department(department_id: str):
    dept = rms_service.get_department(department_id)
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    return dept
