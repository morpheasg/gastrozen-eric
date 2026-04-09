"""UStVA (Umsatzsteuervoranmeldung) XML-Generierung.

Erzeugt das Nutzdaten-XML fuer die UStVA nach aktuellem Schema.
Kennzahlen-Referenz (Restaurant-relevant):
  Kz81: Steuerpflichtige Umsaetze 19% (Getraenke)
  Kz86: Steuerpflichtige Umsaetze 7% (Speisen)
  Kz66: USt-Betrag auf Kz81
  Kz35: USt-Betrag auf Kz86
  Kz61: Vorsteuer aus Rechnungen
  Kz83: Verbleibende USt (Zahllast positiv / Erstattung negativ)
  Kz09: "74931" bei Berichtigung
  Kz10: "1" wenn Berichtigung
"""

from datetime import date
from lxml import etree
from app.xml.base import create_nutzdatenblock, create_elster_xml

USTVA_NS = "http://finkonsens.de/elster/elsteranmeldung/ustva/v2026"


def generate_ustva_xml(
    # Firmendaten
    firmenname: str,
    strasse: str,
    plz: str,
    ort: str,
    telefon: str,
    steuernummer: str,
    bufa_nr: str,
    # Zeitraum
    jahr: int,
    zeitraum: str,  # "01"-"12" monatlich, "41"-"44" quartalsweise
    # Betraege (in Euro, 2 Dezimalstellen)
    umsaetze_19: float = 0.0,      # Netto-Umsaetze 19%
    umsaetze_7: float = 0.0,       # Netto-Umsaetze 7%
    ust_19: float = 0.0,           # USt 19%
    ust_7: float = 0.0,            # USt 7%
    vorsteuer: float = 0.0,        # Vorsteuer aus Eingangsrechnungen
    # Optionen
    ist_berichtigung: bool = False,
    hersteller_id: str = "",
) -> str:
    """UStVA-XML erzeugen.

    Returns:
        Komplettes ELSTER-XML als String.
    """
    # Verbleibende USt berechnen
    zahllast = round(ust_19 + ust_7 - vorsteuer, 2)

    # Nutzdaten-Element
    ns = USTVA_NS
    anmeldung = etree.Element(
        "Anmeldungssteuern",
        nsmap={None: ns},
        version=str(jahr),
        art="UStVA",
    )

    # DatenLieferant
    dl = etree.SubElement(anmeldung, "DatenLieferant")
    _add_text(dl, "Name", firmenname)
    _add_text(dl, "Strasse", strasse)
    _add_text(dl, "PLZ", plz)
    _add_text(dl, "Ort", ort)
    _add_text(dl, "Telefon", telefon)

    # Erstellungsdatum
    _add_text(anmeldung, "Erstellungsdatum", date.today().strftime("%Y%m%d"))

    # Steuerfall
    steuerfall = etree.SubElement(anmeldung, "Steuerfall")
    ustva = etree.SubElement(steuerfall, "Umsatzsteuervoranmeldung")

    _add_text(ustva, "Jahr", str(jahr))
    _add_text(ustva, "Zeitraum", zeitraum)
    _add_text(ustva, "Steuernummer", steuernummer)

    # Berichtigung
    if ist_berichtigung:
        _add_text(ustva, "Kz09", hersteller_id or "74931")
        _add_text(ustva, "Kz10", "1")

    # Umsaetze (nur wenn > 0)
    if umsaetze_19 != 0:
        _add_text(ustva, "Kz81", _format_betrag(umsaetze_19))
    if umsaetze_7 != 0:
        _add_text(ustva, "Kz86", _format_betrag(umsaetze_7))

    # Steuerbetraege
    if ust_19 != 0:
        _add_text(ustva, "Kz66", _format_betrag(ust_19))
    if ust_7 != 0:
        _add_text(ustva, "Kz35", _format_betrag(ust_7))

    # Vorsteuer
    if vorsteuer != 0:
        _add_text(ustva, "Kz66", _format_betrag(vorsteuer))

    # Verbleibende USt
    _add_text(ustva, "Kz83", _format_betrag(zahllast))

    # In Nutzdatenblock verpacken
    block = create_nutzdatenblock(anmeldung, bufa_nr)
    return create_elster_xml(block)


def _add_text(parent: etree._Element, tag: str, text: str) -> etree._Element:
    el = etree.SubElement(parent, tag)
    el.text = text
    return el


def _format_betrag(betrag: float) -> str:
    """Betrag fuer ELSTER formatieren (gerundet, ohne Dezimalpunkt bei ganzen Zahlen)."""
    rounded = round(betrag, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.2f}"
