from fastapi import APIRouter
from app.services.rms_service import RMSService
from app.schemas.rms import AnalyticsOverviewResponse, OperationsAnalytics
from app.telemetry import get_telemetry_service, OperationalMetrics

router = APIRouter()
rms_service = RMSService()
telemetry_service = get_telemetry_service()

@router.get("/overview", response_model=AnalyticsOverviewResponse, summary="Get high-level operations analytics")
def get_analytics_overview():
    return rms_service.get_analytics_overview()

@router.get("/operations", response_model=OperationsAnalytics, summary="Get comprehensive operational analytics calculated from active dataset")
def get_operations_analytics():
    return rms_service.get_operations_analytics()

@router.get("/telemetry", response_model=OperationalMetrics, summary="Get live operational telemetry metrics")
def get_telemetry_metrics():
    return telemetry_service.compute_metrics()
