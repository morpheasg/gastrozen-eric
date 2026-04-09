"""ELSTER Basis-XML Struktur.

Erzeugt das aeussere XML-Geruest das fuer alle Datenarten gleich ist.
Der TransferHeader wird spaeter von ERiC via EricCreateTH befuellt.
"""

from lxml import etree

ELSTER_NS = "http://www.elster.de/elsterxml/schema/v11"
NSMAP = {None: ELSTER_NS}


def create_nutzdatenblock(
    nutzdaten_xml: etree._Element,
    empfaenger_id: str,
    nutzdaten_ticket: str = "1",
) -> etree._Element:
    """Nutzdatenblock mit Header erzeugen.

    Args:
        nutzdaten_xml: Das Nutzdaten-Element (UStVA, Aufzeichnung146a, etc.)
        empfaenger_id: 4-stellige BuFa-Nummer
        nutzdaten_ticket: Ticket-Nummer (bei Sammeldaten hochzaehlen)
    """
    block = etree.Element("Nutzdatenblock")

    # NutzdatenHeader
    header = etree.SubElement(block, "NutzdatenHeader", version="11")
    ticket = etree.SubElement(header, "NutzdatenTicket")
    ticket.text = nutzdaten_ticket
    empf = etree.SubElement(header, "Empfaenger", id="F")
    empf.text = empfaenger_id

    # Nutzdaten
    nd = etree.SubElement(block, "Nutzdaten")
    nd.append(nutzdaten_xml)

    return block


def create_elster_xml(nutzdatenblock: etree._Element) -> str:
    """Komplettes ELSTER-XML erzeugen (ohne TransferHeader - wird von ERiC befuellt).

    Args:
        nutzdatenblock: Ein oder mehrere Nutzdatenblock-Elemente

    Returns:
        XML-String (UTF-8)
    """
    root = etree.Element("Elster", nsmap=NSMAP)
    root.set("xmlns", ELSTER_NS)

    # TransferHeader (Platzhalter - wird von EricCreateTH ersetzt)
    th = etree.SubElement(root, "TransferHeader", version="11")
    etree.SubElement(th, "Verfahren")
    etree.SubElement(th, "DatenArt")
    etree.SubElement(th, "Vorgang")
    empf = etree.SubElement(th, "Empfaenger", id="F")
    empf.text = ""
    etree.SubElement(th, "HerstellerID")
    etree.SubElement(th, "DatenLieferant")

    # DatenTeil
    datenteil = etree.SubElement(root, "DatenTeil")
    datenteil.append(nutzdatenblock)

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True).decode("utf-8")
