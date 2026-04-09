"""UStVA Endpoints."""

import logging
from pathlib import Path
from fastapi import APIRouter, Depends
from app.auth import verify_api_key
from app.models.ustva import UStVARequest
from app.models.common import SubmitResponse, ValidateResponse, ErrorResponse
from app.xml.ustva import generate_ustva_xml
from app.eric.wrapper import get_eric
from app.eric.constants import (
    ERIC_VALIDIERE,
    ERIC_VALIDIERE_UND_SENDE,
    VERFAHREN_ANMELDUNG,
    DATENART_USTVA,
    VORGANG_SEND_AUTH,
)
from app.eric.errors import EricError
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ustva", tags=["UStVA"])


@router.post("/submit", response_model=SubmitResponse)
async def submit_ustva(req: UStVARequest, _=Depends(verify_api_key)):
    """UStVA validieren und an ELSTER senden."""
    eric = get_eric()
    settings = get_settings()

    if not eric.is_available:
        return SubmitResponse(success=False, return_code=-1)

    try:
        # 1. XML erzeugen
        xml = generate_ustva_xml(
            firmenname=req.firma.firmenname,
            strasse=req.firma.strasse,
            plz=req.firma.plz,
            ort=req.firma.ort,
            telefon=req.firma.telefon,
            steuernummer=req.firma.steuernummer,
            bufa_nr=req.firma.bufa_nr,
            jahr=req.jahr,
            zeitraum=req.zeitraum,
            umsaetze_19=req.betraege.umsaetze_19,
            umsaetze_7=req.betraege.umsaetze_7,
            ust_19=req.betraege.ust_19,
            ust_7=req.betraege.ust_7,
            vorsteuer=req.betraege.vorsteuer,
            ist_berichtigung=req.ist_berichtigung,
            hersteller_id=settings.hersteller_id,
        )

        # 2. TransferHeader von ERiC erzeugen lassen
        xml = eric.create_transfer_header(
            xml=xml,
            verfahren=VERFAHREN_ANMELDUNG,
            datenart=DATENART_USTVA,
            vorgang=VORGANG_SEND_AUTH,
        )

        # 3. Zertifikat oeffnen und senden
        cert_path = str(Path(settings.cert_path) / f"{req.cert_id}.pfx")

        flags = ERIC_VALIDIERE if req.nur_validieren else ERIC_VALIDIERE_UND_SENDE
        pdf_path = None
        if req.pdf_erzeugen and not req.nur_validieren:
            pdf_path = f"/tmp/ustva_{req.jahr}_{req.zeitraum}.pdf"

        datenart_version = f"UStVA_{req.jahr}"

        with eric.open_certificate(cert_path) as cert_handle:
            result = eric.submit(
                xml=xml,
                datenart_version=datenart_version,
                cert_handle=cert_handle,
                pin=req.cert_pin,
                flags=flags,
                pdf_path=pdf_path,
            )

        logger.info(
            f"UStVA {req.jahr}/{req.zeitraum}: "
            f"{'OK' if result['success'] else 'FEHLER'} "
            f"(RC={result['return_code']}, Ticket={result['transfer_ticket']})"
        )

        return SubmitResponse(**result)

    except EricError as e:
        logger.error(f"UStVA ERiC-Fehler: {e.code} - {e.message}")
        return SubmitResponse(success=False, return_code=e.code)
    except Exception as e:
        logger.exception(f"UStVA unerwarteter Fehler: {e}")
        return SubmitResponse(success=False, return_code=-1)


@router.post("/validate", response_model=ValidateResponse)
async def validate_ustva(req: UStVARequest, _=Depends(verify_api_key)):
    """UStVA nur validieren (nicht senden)."""
    eric = get_eric()
    settings = get_settings()

    if not eric.is_available:
        return ValidateResponse(valid=False, errors="ERiC SDK nicht verfuegbar")

    try:
        xml = generate_ustva_xml(
            firmenname=req.firma.firmenname,
            strasse=req.firma.strasse,
            plz=req.firma.plz,
            ort=req.firma.ort,
            telefon=req.firma.telefon,
            steuernummer=req.firma.steuernummer,
            bufa_nr=req.firma.bufa_nr,
            jahr=req.jahr,
            zeitraum=req.zeitraum,
            umsaetze_19=req.betraege.umsaetze_19,
            umsaetze_7=req.betraege.umsaetze_7,
            ust_19=req.betraege.ust_19,
            ust_7=req.betraege.ust_7,
            vorsteuer=req.betraege.vorsteuer,
            ist_berichtigung=req.ist_berichtigung,
            hersteller_id=settings.hersteller_id,
        )

        datenart_version = f"UStVA_{req.jahr}"
        result = eric.validate_xml(xml, datenart_version)

        return ValidateResponse(**result)

    except EricError as e:
        return ValidateResponse(valid=False, errors=e.message, return_code=e.code)


@router.post("/preview")
async def preview_ustva_xml(req: UStVARequest, _=Depends(verify_api_key)):
    """UStVA-XML erzeugen und zurueckgeben (ohne Senden)."""
    settings = get_settings()

    xml = generate_ustva_xml(
        firmenname=req.firma.firmenname,
        strasse=req.firma.strasse,
        plz=req.firma.plz,
        ort=req.firma.ort,
        telefon=req.firma.telefon,
        steuernummer=req.firma.steuernummer,
        bufa_nr=req.firma.bufa_nr,
        jahr=req.jahr,
        zeitraum=req.zeitraum,
        umsaetze_19=req.betraege.umsaetze_19,
        umsaetze_7=req.betraege.umsaetze_7,
        ust_19=req.betraege.ust_19,
        ust_7=req.betraege.ust_7,
        vorsteuer=req.betraege.vorsteuer,
        ist_berichtigung=req.ist_berichtigung,
        hersteller_id=settings.hersteller_id,
    )

    # Zusammenfassung der Betraege
    zahllast = round(req.betraege.ust_19 + req.betraege.ust_7 - req.betraege.vorsteuer, 2)

    return {
        "xml": xml,
        "zusammenfassung": {
            "jahr": req.jahr,
            "zeitraum": req.zeitraum,
            "umsaetze_19_netto": req.betraege.umsaetze_19,
            "umsaetze_7_netto": req.betraege.umsaetze_7,
            "ust_19": req.betraege.ust_19,
            "ust_7": req.betraege.ust_7,
            "vorsteuer": req.betraege.vorsteuer,
            "zahllast": zahllast,
        },
    }
