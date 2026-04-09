"""UStVA Pydantic-Models."""

from pydantic import BaseModel, Field


class UStVAFirmendaten(BaseModel):
    """Firmendaten des Steuerpflichtigen."""
    firmenname: str = Field(..., description="Name des Unternehmens")
    strasse: str = Field(..., description="Strasse inkl. Hausnummer")
    plz: str = Field(..., description="Postleitzahl")
    ort: str = Field(..., description="Ort")
    telefon: str = Field("", description="Telefonnummer")
    steuernummer: str = Field(..., description="13-stellige Steuernummer")
    bufa_nr: str = Field(..., description="4-stellige Bundesfinanzamtsnummer")


class UStVABetraege(BaseModel):
    """Steuerbetraege fuer die UStVA.

    Alle Betraege in Euro (Netto).
    """
    umsaetze_19: float = Field(0.0, description="Netto-Umsaetze 19% (Getraenke)")
    umsaetze_7: float = Field(0.0, description="Netto-Umsaetze 7% (Speisen)")
    ust_19: float = Field(0.0, description="USt-Betrag 19%")
    ust_7: float = Field(0.0, description="USt-Betrag 7%")
    vorsteuer: float = Field(0.0, description="Vorsteuer aus Eingangsrechnungen")


class UStVARequest(BaseModel):
    """Komplette UStVA-Anfrage."""
    firma: UStVAFirmendaten
    betraege: UStVABetraege
    jahr: int = Field(..., description="Steuerjahr", ge=2024, le=2030)
    zeitraum: str = Field(..., description="01-12 (monatlich) oder 41-44 (quartalsweise)")
    ist_berichtigung: bool = Field(False, description="Berichtigte Meldung")
    # Zertifikat
    cert_id: str = Field(..., description="ID des Zertifikats (Dateiname ohne .pfx)")
    cert_pin: str = Field(..., description="PIN des Zertifikats")
    # Optionen
    nur_validieren: bool = Field(False, description="Nur validieren, nicht senden")
    pdf_erzeugen: bool = Field(False, description="Zusaetzlich PDF erzeugen")
