"""ERiC Fehlercodes (aus eric_fehlercodes.h)."""

# Die wichtigsten Fehlercodes - vollstaendige Liste kommt mit SDK
ERIC_OK = 0

# Allgemeine Fehler
ERIC_GLOBAL_UNKNOWN = 610001001
ERIC_GLOBAL_PRUEF_FEHLER = 610001002
ERIC_GLOBAL_HINWEISE = 610001003
ERIC_GLOBAL_NICHT_INITIALISIERT = 610001007
ERIC_GLOBAL_BEREITS_INITIALISIERT = 610001008
ERIC_GLOBAL_UNGUELTIGER_PARAMETER = 610001101

# Transfer-Fehler
ERIC_TRANSFER_COM_ERROR = 610101200
ERIC_TRANSFER_TIMEOUT = 610101210
ERIC_TRANSFER_VORGANG_NICHT_UNTERSTUETZT = 610101251

# Zertifikat-Fehler
ERIC_CRYPT_ZERTIFIKAT_NICHT_GEFUNDEN = 610301001
ERIC_CRYPT_PIN_FALSCH = 610301005
ERIC_CRYPT_PIN_GESPERRT = 610301006
ERIC_CRYPT_ZERTIFIKAT_ABGELAUFEN = 610301014

# Druck-Fehler
ERIC_PRINT_INTERNER_FEHLER = 610501001

# IO-Fehler
ERIC_IO_DATEI_NICHT_GEFUNDEN = 610601001
ERIC_IO_DATEI_NICHT_LESBAR = 610601003

ERROR_MESSAGES = {
    ERIC_OK: "Erfolgreich",
    ERIC_GLOBAL_UNKNOWN: "Unbekannter Fehler",
    ERIC_GLOBAL_PRUEF_FEHLER: "Prueffehler in den Daten",
    ERIC_GLOBAL_HINWEISE: "Hinweise vorhanden",
    ERIC_GLOBAL_NICHT_INITIALISIERT: "ERiC nicht initialisiert",
    ERIC_GLOBAL_BEREITS_INITIALISIERT: "ERiC bereits initialisiert",
    ERIC_GLOBAL_UNGUELTIGER_PARAMETER: "Ungueltiger Parameter",
    ERIC_TRANSFER_COM_ERROR: "Kommunikationsfehler mit ELSTER",
    ERIC_TRANSFER_TIMEOUT: "Timeout bei ELSTER-Kommunikation",
    ERIC_TRANSFER_VORGANG_NICHT_UNTERSTUETZT: "Vorgang nicht unterstuetzt",
    ERIC_CRYPT_ZERTIFIKAT_NICHT_GEFUNDEN: "Zertifikat nicht gefunden",
    ERIC_CRYPT_PIN_FALSCH: "PIN falsch",
    ERIC_CRYPT_PIN_GESPERRT: "PIN gesperrt",
    ERIC_CRYPT_ZERTIFIKAT_ABGELAUFEN: "Zertifikat abgelaufen",
    ERIC_PRINT_INTERNER_FEHLER: "Interner Druckfehler",
    ERIC_IO_DATEI_NICHT_GEFUNDEN: "Datei nicht gefunden",
    ERIC_IO_DATEI_NICHT_LESBAR: "Datei nicht lesbar",
}


class EricError(Exception):
    """ERiC SDK Fehler."""
    def __init__(self, code: int, message: str = ""):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, f"ERiC Fehler {code}")
        super().__init__(self.message)
