from app.integrations.base import UniversitySystemAdapter
from app.integrations.mock_rms_adapter import MockRMSAdapter
from app.integrations.future_adapters import FutureUMSAdapter, FutureLMSAdapter, FutureERPAdapter

__all__ = [
    "UniversitySystemAdapter",
    "MockRMSAdapter",
    "FutureUMSAdapter",
    "FutureLMSAdapter",
    "FutureERPAdapter"
]
