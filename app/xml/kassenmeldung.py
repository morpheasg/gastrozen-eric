"""Kassenmeldung (Aufzeichnung146a) XML-Generierung.

Meldepflicht nach Paragraph 146a Abs. 4 AO:
Jedes elektronische Aufzeichnungssystem und jede TSE muss
beim zustaendigen Finanzamt gemeldet werden.

Meldeanlaesse:
- Anschaffung/Inbetriebnahme einer Kasse
- Ausserbetriennahme einer Kasse
- TSE-Wechsel
- Aenderung der Betriebsstaette
"""

from datetime import date
from lxml import etree
from app.xml.base import create_nutzdatenblock, create_elster_xml

AUFZEICHNUNG_NS = "http://finkonsens.de/elster/elsternachricht/aufzeichnung146a/v1"


def generate_kassenmeldung_xml(
    # Steuerpflichtiger
    steuernummer: str,
    bufa_nr: str,
    firmenname: str,
    strasse: str,
    hausnummer: str,
    plz: str,
    ort: str,
    # Betriebsstaette (kann abweichen von Firmensitz)
    bs_strasse: str = "",
    bs_hausnummer: str = "",
    bs_plz: str = "",
    bs_ort: str = "",
    # Kassen-System
    kassen_hersteller: str = "GastroZen",
    kassen_modell: str = "GastroZen POS",
    kassen_seriennummer: str = "",
    kassen_software: str = "GastroZen",
    kassen_software_version: str = "1.0",
    # TSE
    tse_hersteller: str = "",
    tse_modell: str = "",
    tse_seriennummer: str = "",
    tse_zertifikat_id: str = "",
    # Daten
    anschaffungsdatum: str = "",   # YYYY-MM-DD
    inbetriebnahme: str = "",      # YYYY-MM-DD
    ausserbetriebnahme: str = "",  # YYYY-MM-DD (leer wenn aktiv)
    # Art der Meldung
    meldeart: str = "anmeldung",   # anmeldung | abmeldung | aenderung
) -> str:
    """Kassenmeldung XML erzeugen.

    Returns:
        Komplettes ELSTER-XML als String.
    """
    # Betriebsstaetten-Adresse (Fallback: Firmenadresse)
    bs_strasse = bs_strasse or strasse
    bs_hausnummer = bs_hausnummer or hausnummer
    bs_plz = bs_plz or plz
    bs_ort = bs_ort or ort

    # Aufzeichnung146a Element
    root = etree.Element(
        "Aufzeichnung146a",
        nsmap={None: AUFZEICHNUNG_NS},
        version="1",
    )

    # Steuerpflichtiger
    stpfl = etree.SubElement(root, "Steuerpflichtiger")
    _add_text(stpfl, "Name", firmenname)
    _add_text(stpfl, "Steuernummer", steuernummer)

    anschrift = etree.SubElement(stpfl, "Anschrift")
    _add_text(anschrift, "Strasse", strasse)
    _add_text(anschrift, "Hausnummer", hausnummer)
    _add_text(anschrift, "PLZ", plz)
    _add_text(anschrift, "Ort", ort)

    # Betriebsstaette
    bs = etree.SubElement(root, "Betriebsstaette")
    bs_anschrift = etree.SubElement(bs, "Anschrift")
    _add_text(bs_anschrift, "Strasse", bs_strasse)
    _add_text(bs_anschrift, "Hausnummer", bs_hausnummer)
    _add_text(bs_anschrift, "PLZ", bs_plz)
    _add_text(bs_anschrift, "Ort", bs_ort)

    # Aufzeichnungssystem (Kasse)
    system = etree.SubElement(root, "Aufzeichnungssystem")
    _add_text(system, "Art", "EAS")  # Elektronisches Aufzeichnungssystem
    _add_text(system, "Hersteller", kassen_hersteller)
    _add_text(system, "Modell", kassen_modell)
    _add_text(system, "Seriennummer", kassen_seriennummer)

    software = etree.SubElement(system, "Software")
    _add_text(software, "Name", kassen_software)
    _add_text(software, "Version", kassen_software_version)

    if anschaffungsdatum:
        _add_text(system, "Anschaffungsdatum", _format_date(anschaffungsdatum))
    if inbetriebnahme:
        _add_text(system, "Inbetriebnahme", _format_date(inbetriebnahme))
    if ausserbetriebnahme:
        _add_text(system, "Ausserbetriebnahme", _format_date(ausserbetriebnahme))

    # TSE (Technische Sicherheitseinrichtung)
    if tse_hersteller:
        tse = etree.SubElement(root, "TSE")
        _add_text(tse, "Hersteller", tse_hersteller)
        _add_text(tse, "Modell", tse_modell)
        _add_text(tse, "Seriennummer", tse_seriennummer)
        if tse_zertifikat_id:
            _add_text(tse, "ZertifikatID", tse_zertifikat_id)

    # Meldeart
    _add_text(root, "Meldeart", meldeart)
    _add_text(root, "Erstellungsdatum", date.today().strftime("%Y%m%d"))

    # In Nutzdatenblock verpacken
    block = create_nutzdatenblock(root, bufa_nr)
    return create_elster_xml(block)


def _add_text(parent: etree._Element, tag: str, text: str) -> etree._Element:
    el = etree.SubElement(parent, tag)
    el.text = text
    return el


def _format_date(d: str) -> str:
    """Datum von YYYY-MM-DD nach YYYYMMDD konvertieren."""
    return d.replace("-", "")
