"""ERiC SDK Konstanten und Flags."""

# === Bearbeitungs-Flags (bearbeitungsFlags) ===
ERIC_VALIDIERE = 1 << 1                    # Nur validieren
ERIC_SENDE = 1 << 2                        # An ELSTER senden
ERIC_DRUCKE = 1 << 5                       # PDF erzeugen
ERIC_PRUEFE_HINWEISE = 1 << 7              # Hinweise pruefen

# Kombinationen
ERIC_VALIDIERE_UND_SENDE = ERIC_VALIDIERE | ERIC_SENDE
ERIC_ALLES = ERIC_VALIDIERE | ERIC_SENDE | ERIC_DRUCKE

# === Verfahren ===
VERFAHREN_ANMELDUNG = "ElsterAnmeldung"     # UStVA, LStA, etc.
VERFAHREN_NACHRICHT = "ElsterNachricht"      # Kassenmeldung, etc.

# === Datenarten ===
DATENART_USTVA = "UStVA"
DATENART_AUFZEICHNUNG146A = "Aufzeichnung146a"

# === Vorgaenge ===
VORGANG_SEND_AUTH = "send-Auth"              # Authentifizierte Sendung
VORGANG_SEND_NOSIG = "send-NoSig"           # Ohne Signatur (nur wenige Datenarten)

# === Testmerker ===
TESTMERKER_SOFORT_LOESCHEN = "700000004"     # Entwickler-Test
TESTMERKER_LANDESRECHENZENTRUM = "700000001"  # LRZ-Test

# === Verschluesselung ===
VERSCHLUESSELUNG_PKCS7 = "PKCS#7v1.5"
KOMPRESSION_GZIP = "GZIP"

# === Struct-Versionen ===
DRUCK_PARAMETER_VERSION = 4
VERSCHLUESSELUNG_PARAMETER_VERSION = 4

# === UStVA Kennzahlen (Restaurant-relevant) ===
# Steuerpflichtige Umsaetze
KZ_UMSAETZE_19 = "Kz81"        # Umsaetze 19% (Getraenke)
KZ_UMSAETZE_7 = "Kz86"         # Umsaetze 7% (Speisen)

# Steuerbetraege
KZ_UST_19 = "Kz66"             # USt auf Kz81
KZ_UST_7 = "Kz35"              # USt auf Kz86

# Vorsteuer
KZ_VORSTEUER = "Kz66"          # Vorsteuer aus Eingangsrechnungen
KZ_VORSTEUER_RECHNUNGEN = "Kz66"

# Ergebnis
KZ_VERBLEIBEND = "Kz83"        # Verbleibende USt (Zahllast/Erstattung)

# Berichtigung
KZ_BERICHTIGUNG = "Kz09"       # Hersteller-ID bei Berichtigung
KZ_IST_BERICHTIGUNG = "Kz10"   # "1" wenn Berichtigung

# === UStVA Zeitraeume ===
ZEITRAUM_MONATLICH = {
    1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06",
    7: "07", 8: "08", 9: "09", 10: "10", 11: "11", 12: "12"
}
ZEITRAUM_QUARTALSWEISE = {
    1: "41",  # Q1 (Jan-Mär)
    2: "42",  # Q2 (Apr-Jun)
    3: "43",  # Q3 (Jul-Sep)
    4: "44",  # Q4 (Okt-Dez)
}
