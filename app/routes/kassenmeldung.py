"""Kassenmeldung Endpoints."""

import logging
from pathlib import Path
from fastapi import APIRouter, Depends
from app.auth import verify_api_key
from app.models.kassenmeldung import KassenmeldungRequest
from app.models.common import SubmitResponse, ValidateResponse
from app.xml.kassenmeldung import generate_kassenmeldung_xml
from app.eric.wrapper import get_eric
from app.eric.constants import (
    ERIC_VALIDIERE,
    ERIC_VALIDIERE_UND_SENDE,
    VERFAHREN_NACHRICHT,
    DATENART_AUFZEICHNUNG146A,
    VORGANG_SEND_AUTH,
)
from app.eric.errors import EricError
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kassenmeldung", tags=["Kassenmeldung"])


@router.post("/submit", response_model=SubmitResponse)
async def submit_kassenmeldung(req: KassenmeldungRequest, _=Depends(verify_api_key)):
    """Kassenmeldung nach Paragraph 146a AO an ELSTER senden."""
    eric = get_eric()
    settings = get_settings()

    if not eric.is_available:
        return SubmitResponse(success=False, return_code=-1)

    try:
        # 1. XML erzeugen
        xml = generate_kassenmeldung_xml(
            steuernummer=req.steuerpflichtiger.steuernummer,
            bufa_nr=req.steuerpflichtiger.bufa_nr,
            firmenname=req.steuerpflichtiger.firmenname,
            strasse=req.steuerpflichtiger.strasse,
            hausnummer=req.steuerpflichtiger.hausnummer,
            plz=req.steuerpflichtiger.plz,
            ort=req.steuerpflichtiger.ort,
            bs_strasse=req.betriebsstaette.strasse,
            bs_hausnummer=req.betriebsstaette.hausnummer,
            bs_plz=req.betriebsstaette.plz,
            bs_ort=req.betriebsstaette.ort,
            kassen_hersteller=req.kasse.hersteller,
            kassen_modell=req.kasse.modell,
            kassen_seriennummer=req.kasse.seriennummer,
            kassen_software=req.kasse.software,
            kassen_software_version=req.kasse.software_version,
            tse_hersteller=req.tse.hersteller,
            tse_modell=req.tse.modell,
            tse_seriennummer=req.tse.seriennummer,
            tse_zertifikat_id=req.tse.zertifikat_id,
            anschaffungsdatum=req.kasse.anschaffungsdatum,
            inbetriebnahme=req.kasse.inbetriebnahme,
            ausserbetriebnahme=req.kasse.ausserbetriebnahme,
            meldeart=req.meldeart,
        )

        # 2. TransferHeader
        xml = eric.create_transfer_header(
            xml=xml,
            verfahren=VERFAHREN_NACHRICHT,
            datenart=DATENART_AUFZEICHNUNG146A,
            vorgang=VORGANG_SEND_AUTH,
        )

        # 3. Senden
        cert_path = str(Path(settings.cert_path) / f"{req.cert_id}.pfx")
        flags = ERIC_VALIDIERE if req.nur_validieren else ERIC_VALIDIERE_UND_SENDE

        with eric.open_certificate(cert_path) as cert_handle:
            result = eric.submit(
                xml=xml,
                datenart_version="Aufzeichnung146a_1",
                cert_handle=cert_handle,
                pin=req.cert_pin,
                flags=flags,
            )

        logger.info(
            f"Kassenmeldung ({req.meldeart}): "
            f"{'OK' if result['success'] else 'FEHLER'} "
            f"(RC={result['return_code']}, Ticket={result['transfer_ticket']})"
        )

        return SubmitResponse(**result)

    except EricError as e:
        logger.error(f"Kassenmeldung ERiC-Fehler: {e.code} - {e.message}")
        return SubmitResponse(success=False, return_code=e.code)
    except Exception as e:
        logger.exception(f"Kassenmeldung unerwarteter Fehler: {e}")
        return SubmitResponse(success=False, return_code=-1)


@router.post("/preview")
async def preview_kassenmeldung_xml(req: KassenmeldungRequest, _=Depends(verify_api_key)):
    """Kassenmeldung-XML erzeugen und zurueckgeben (ohne Senden)."""
    xml = generate_kassenmeldung_xml(
        steuernummer=req.steuerpflichtiger.steuernummer,
        bufa_nr=req.steuerpflichtiger.bufa_nr,
        firmenname=req.steuerpflichtiger.firmenname,
        strasse=req.steuerpflichtiger.strasse,
        hausnummer=req.steuerpflichtiger.hausnummer,
        plz=req.steuerpflichtiger.plz,
        ort=req.steuerpflichtiger.ort,
        bs_strasse=req.betriebsstaette.strasse,
        bs_hausnummer=req.betriebsstaette.hausnummer,
        bs_plz=req.betriebsstaette.plz,
        bs_ort=req.betriebsstaette.ort,
        kassen_hersteller=req.kasse.hersteller,
        kassen_modell=req.kasse.modell,
        kassen_seriennummer=req.kasse.seriennummer,
        kassen_software=req.kasse.software,
        kassen_software_version=req.kasse.software_version,
        tse_hersteller=req.tse.hersteller,
        tse_modell=req.tse.modell,
        tse_seriennummer=req.tse.seriennummer,
        tse_zertifikat_id=req.tse.zertifikat_id,
        anschaffungsdatum=req.kasse.anschaffungsdatum,
        inbetriebnahme=req.kasse.inbetriebnahme,
        ausserbetriebnahme=req.kasse.ausserbetriebnahme,
        meldeart=req.meldeart,
    )

    return {"xml": xml, "meldeart": req.meldeart}
