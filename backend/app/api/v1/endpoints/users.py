from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.rms_service import RMSService
from app.schemas.contracts import StaffUser

router = APIRouter()
rms_service = RMSService()

@router.get("", response_model=List[StaffUser], summary="List synthetic university staff users")
def list_users(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    role: Optional[str] = Query(None, description="Filter by staff role (e.g. STAFF_OPERATOR, HOD)")
):
    return rms_service.list_users(department_id=department_id, role=role)

@router.get("/{user_id}", response_model=StaffUser, summary="Get staff user details by ID")
def get_user(user_id: str):
    user = rms_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user
