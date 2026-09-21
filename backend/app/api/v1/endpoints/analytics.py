from fastapi import APIRouter
from app.services.rms_service import RMSService
from app.schemas.rms import AnalyticsOverviewResponse

router = APIRouter()
rms_service = RMSService()

@router.get("/overview", response_model=AnalyticsOverviewResponse, summary="Get high-level operations analytics")
def get_analytics_overview():
    return rms_service.get_analytics_overview()
