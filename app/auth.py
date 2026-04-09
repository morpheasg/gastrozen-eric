from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    settings = get_settings()
    if not settings.api_secret_key:
        raise HTTPException(status_code=500, detail="API_SECRET_KEY nicht konfiguriert")
    if api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Ungueltiger API-Schluessel")
    return api_key
