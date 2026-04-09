"""Zertifikat-Verwaltung Endpoints."""

import logging
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File
from app.auth import verify_api_key
from app.eric.wrapper import get_eric
from app.eric.errors import EricError
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/certificate", tags=["Zertifikate"])


@router.post("/upload")
async def upload_certificate(
    cert_id: str,
    file: UploadFile = File(...),
    _=Depends(verify_api_key),
):
    """Zertifikat (.pfx) hochladen.

    cert_id: Eindeutige ID (z.B. subscription_id des Restaurants)
    """
    settings = get_settings()
    cert_dir = Path(settings.cert_path)
    cert_dir.mkdir(parents=True, exist_ok=True)

    dest = cert_dir / f"{cert_id}.pfx"

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    logger.info(f"Zertifikat hochgeladen: {cert_id}")
    return {"success": True, "cert_id": cert_id}


@router.get("/info")
async def get_certificate_info(
    cert_id: str,
    pin: str,
    _=Depends(verify_api_key),
):
    """Zertifikat-Eigenschaften abfragen (Name, Ablaufdatum, etc.)."""
    eric = get_eric()
    settings = get_settings()

    cert_path = str(Path(settings.cert_path) / f"{cert_id}.pfx")

    if not Path(cert_path).exists():
        return {"success": False, "error": "Zertifikat nicht gefunden"}

    if not eric.is_available:
        return {"success": False, "error": "ERiC SDK nicht verfuegbar"}

    try:
        info = eric.get_certificate_info(cert_path, pin)
        return {"success": True, "info": info}
    except EricError as e:
        return {"success": False, "error": e.message, "error_code": e.code}


@router.delete("/{cert_id}")
async def delete_certificate(cert_id: str, _=Depends(verify_api_key)):
    """Zertifikat loeschen."""
    settings = get_settings()
    cert_path = Path(settings.cert_path) / f"{cert_id}.pfx"

    if not cert_path.exists():
        return {"success": False, "error": "Zertifikat nicht gefunden"}

    cert_path.unlink()
    logger.info(f"Zertifikat geloescht: {cert_id}")
    return {"success": True}


@router.get("/list")
async def list_certificates(_=Depends(verify_api_key)):
    """Vorhandene Zertifikate auflisten (nur IDs, keine Inhalte)."""
    settings = get_settings()
    cert_dir = Path(settings.cert_path)

    if not cert_dir.exists():
        return {"certificates": []}

    certs = [p.stem for p in cert_dir.glob("*.pfx")]
    return {"certificates": certs}
