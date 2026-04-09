"""Kassenmeldung Pydantic-Models."""

from pydantic import BaseModel, Field


class KassenSteuerpflichtiger(BaseModel):
    """Steuerpflichtiger (Restaurant-Inhaber)."""
    firmenname: str
    steuernummer: str = Field(..., description="13-stellige Steuernummer")
    bufa_nr: str = Field(..., description="4-stellige BuFa-Nummer")
    strasse: str
    hausnummer: str
    plz: str
    ort: str


class KassenBetriebsstaette(BaseModel):
    """Betriebsstaette (Restaurant-Standort, kann vom Firmensitz abweichen)."""
    strasse: str = ""
    hausnummer: str = ""
    plz: str = ""
    ort: str = ""


class KassenSystem(BaseModel):
    """Elektronisches Aufzeichnungssystem (Kasse)."""
    hersteller: str = "GastroZen"
    modell: str = "GastroZen POS"
    seriennummer: str = Field(..., description="Eindeutige Seriennummer der Kasse")
    software: str = "GastroZen"
    software_version: str = "1.0"
    anschaffungsdatum: str = Field("", description="YYYY-MM-DD")
    inbetriebnahme: str = Field("", description="YYYY-MM-DD")
    ausserbetriebnahme: str = Field("", description="YYYY-MM-DD (leer wenn aktiv)")


class KassenTSE(BaseModel):
    """Technische Sicherheitseinrichtung."""
    hersteller: str = Field(..., description="z.B. fiskaltrust, Swissbit, Epson")
    modell: str = ""
    seriennummer: str = Field(..., description="TSE Seriennummer")
    zertifikat_id: str = Field("", description="TSE Zertifikats-ID")


class KassenmeldungRequest(BaseModel):
    """Komplette Kassenmeldung-Anfrage."""
    steuerpflichtiger: KassenSteuerpflichtiger
    betriebsstaette: KassenBetriebsstaette = KassenBetriebsstaette()
    kasse: KassenSystem
    tse: KassenTSE
    meldeart: str = Field("anmeldung", description="anmeldung | abmeldung | aenderung")
    # Zertifikat
    cert_id: str = Field(..., description="ID des Zertifikats")
    cert_pin: str = Field(..., description="PIN des Zertifikats")
    nur_validieren: bool = False
