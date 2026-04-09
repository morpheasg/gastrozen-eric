"""Health-Check Endpoint."""

from fastapi import APIRouter
from app.models.common import HealthResponse
from app.eric.wrapper import get_eric
from app.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    eric = get_eric()
    settings = get_settings()

    version = None
    if eric.is_available and eric._initialized:
        try:
            version = eric.get_version()
        except Exception:
            pass

    return HealthResponse(
        status="ok",
        eric_available=eric.is_available,
        eric_version=version,
        test_mode=settings.test_mode,
    )
