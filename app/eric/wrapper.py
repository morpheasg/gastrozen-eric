"""ERiC SDK Wrapper - ctypes Anbindung an libericapi.so.

Dieser Wrapper bildet alle relevanten ERiC-Funktionen ab.
Die eigentlichen .so-Dateien muessen im eric_lib/ Verzeichnis liegen.
"""

import ctypes
import logging
import os
from pathlib import Path
from contextlib import contextmanager

from app.eric.types import (
    EricRueckgabepufferHandle,
    EricZertifikatHandle,
    EricInstanzHandle,
    EricDruckParameterT,
    EricVerschluesselungsParameterT,
)
from app.eric.errors import ERIC_OK, ERIC_GLOBAL_HINWEISE, EricError
from app.eric.constants import (
    ERIC_VALIDIERE,
    ERIC_SENDE,
    ERIC_DRUCKE,
    ERIC_VALIDIERE_UND_SENDE,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class EricWrapper:
    """Wrapper fuer ERiC SDK (Multithreading-API)."""

    def __init__(self):
        self._lib: ctypes.CDLL | None = None
        self._instanz: EricInstanzHandle | None = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Prueft ob ERiC SDK vorhanden ist."""
        settings = get_settings()
        lib_path = Path(settings.eric_lib_path) / "libericapi.so"
        return lib_path.exists()

    def initialize(self) -> None:
        """ERiC SDK laden und initialisieren."""
        if self._initialized:
            return

        settings = get_settings()
        lib_path = Path(settings.eric_lib_path) / "libericapi.so"

        if not lib_path.exists():
            raise EricError(0, f"ERiC Library nicht gefunden: {lib_path}")

        # Library laden
        self._lib = ctypes.CDLL(str(lib_path))
        self._setup_function_signatures()

        # Plugin-Pfad (Verzeichnis mit commonData.so, checkUStVA_*.so, etc.)
        plugin_path = str(Path(settings.eric_lib_path) / "plugins").encode("utf-8")
        log_path = settings.eric_log_path.encode("utf-8")

        # Multithreading-Instanz erzeugen
        instanz = EricInstanzHandle()
        rc = self._lib.EricMtInstanzErzeugen(plugin_path, log_path, ctypes.byref(instanz))
        if rc != ERIC_OK:
            raise EricError(rc, "EricMtInstanzErzeugen fehlgeschlagen")

        self._instanz = instanz
        self._initialized = True
        logger.info("ERiC SDK initialisiert")

    def shutdown(self) -> None:
        """ERiC SDK herunterfahren."""
        if not self._initialized or not self._lib:
            return

        if self._instanz:
            self._lib.EricMtInstanzFreigeben(self._instanz)
            self._instanz = None

        self._initialized = False
        logger.info("ERiC SDK beendet")

    def _setup_function_signatures(self) -> None:
        """C-Funktionssignaturen definieren."""
        lib = self._lib

        # --- Instanz-Verwaltung ---
        lib.EricMtInstanzErzeugen.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(EricInstanzHandle)]
        lib.EricMtInstanzErzeugen.restype = ctypes.c_int

        lib.EricMtInstanzFreigeben.argtypes = [EricInstanzHandle]
        lib.EricMtInstanzFreigeben.restype = ctypes.c_int

        # --- Rueckgabepuffer ---
        lib.EricMtRueckgabepufferErzeugen.argtypes = [EricInstanzHandle]
        lib.EricMtRueckgabepufferErzeugen.restype = EricRueckgabepufferHandle

        lib.EricMtRueckgabepufferInhalt.argtypes = [EricInstanzHandle, EricRueckgabepufferHandle]
        lib.EricMtRueckgabepufferInhalt.restype = ctypes.c_char_p

        lib.EricMtRueckgabepufferLaenge.argtypes = [EricInstanzHandle, EricRueckgabepufferHandle]
        lib.EricMtRueckgabepufferLaenge.restype = ctypes.c_uint32

        lib.EricMtRueckgabepufferFreigeben.argtypes = [EricInstanzHandle, EricRueckgabepufferHandle]
        lib.EricMtRueckgabepufferFreigeben.restype = ctypes.c_int

        # --- Hauptfunktion ---
        lib.EricMtBearbeiteVorgang.argtypes = [
            EricInstanzHandle,                                             # instanz
            ctypes.c_char_p,                                               # datenpuffer (XML)
            ctypes.c_char_p,                                               # datenartVersion
            ctypes.c_uint32,                                               # bearbeitungsFlags
            ctypes.POINTER(EricDruckParameterT),                           # druckParameter
            ctypes.POINTER(EricVerschluesselungsParameterT),               # cryptoParameter
            ctypes.c_void_p,                                               # transferHandle
            EricRueckgabepufferHandle,                                     # rueckgabeXmlPuffer
            EricRueckgabepufferHandle,                                     # serverantwortXmlPuffer
        ]
        lib.EricMtBearbeiteVorgang.restype = ctypes.c_int

        # --- TransferHeader ---
        lib.EricMtCreateTH.argtypes = [
            EricInstanzHandle,
            ctypes.c_char_p,    # xml
            ctypes.c_char_p,    # verfahren
            ctypes.c_char_p,    # datenart
            ctypes.c_char_p,    # vorgang
            ctypes.c_char_p,    # testmerker
            ctypes.c_char_p,    # herstellerId
            ctypes.c_char_p,    # datenLieferant
            ctypes.c_char_p,    # versionClient
            ctypes.c_char_p,    # publicKey
            EricRueckgabepufferHandle,
        ]
        lib.EricMtCreateTH.restype = ctypes.c_int

        # --- Zertifikate ---
        lib.EricMtGetHandleToCertificate.argtypes = [
            EricInstanzHandle,
            ctypes.POINTER(EricZertifikatHandle),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
        ]
        lib.EricMtGetHandleToCertificate.restype = ctypes.c_int

        lib.EricMtCloseHandleToCertificate.argtypes = [EricInstanzHandle, EricZertifikatHandle]
        lib.EricMtCloseHandleToCertificate.restype = ctypes.c_int

        lib.EricMtHoleZertifikatEigenschaften.argtypes = [
            EricInstanzHandle,
            EricZertifikatHandle,
            ctypes.c_char_p,
            EricRueckgabepufferHandle,
        ]
        lib.EricMtHoleZertifikatEigenschaften.restype = ctypes.c_int

        # --- Validierung ---
        lib.EricMtCheckXML.argtypes = [
            EricInstanzHandle, ctypes.c_char_p, ctypes.c_char_p, EricRueckgabepufferHandle
        ]
        lib.EricMtCheckXML.restype = ctypes.c_int

        lib.EricMtPruefeSteuernummer.argtypes = [EricInstanzHandle, ctypes.c_char_p]
        lib.EricMtPruefeSteuernummer.restype = ctypes.c_int

        lib.EricMtPruefeBuFaNummer.argtypes = [EricInstanzHandle, ctypes.c_char_p]
        lib.EricMtPruefeBuFaNummer.restype = ctypes.c_int

        # --- Hilfsfunktionen ---
        lib.EricMtHoleFehlerText.argtypes = [EricInstanzHandle, ctypes.c_int, EricRueckgabepufferHandle]
        lib.EricMtHoleFehlerText.restype = ctypes.c_int

        lib.EricMtVersion.argtypes = [EricInstanzHandle, EricRueckgabepufferHandle]
        lib.EricMtVersion.restype = ctypes.c_int

        lib.EricMtEinstellungSetzen.argtypes = [EricInstanzHandle, ctypes.c_char_p, ctypes.c_char_p]
        lib.EricMtEinstellungSetzen.restype = ctypes.c_int

        lib.EricMtHoleFinanzaemter.argtypes = [
            EricInstanzHandle, ctypes.c_char_p, EricRueckgabepufferHandle
        ]
        lib.EricMtHoleFinanzaemter.restype = ctypes.c_int

    # === Puffer-Hilfsfunktionen ===

    def _create_buffer(self) -> EricRueckgabepufferHandle:
        return self._lib.EricMtRueckgabepufferErzeugen(self._instanz)

    def _read_buffer(self, handle: EricRueckgabepufferHandle) -> str:
        content = self._lib.EricMtRueckgabepufferInhalt(self._instanz, handle)
        return content.decode("utf-8") if content else ""

    def _free_buffer(self, handle: EricRueckgabepufferHandle) -> None:
        self._lib.EricMtRueckgabepufferFreigeben(self._instanz, handle)

    @contextmanager
    def _buffer(self):
        """Context Manager fuer Rueckgabepuffer."""
        buf = self._create_buffer()
        try:
            yield buf
        finally:
            self._free_buffer(buf)

    def _check_rc(self, rc: int, operation: str) -> None:
        """Return Code pruefen und ggf. Exception werfen."""
        if rc == ERIC_OK or rc == ERIC_GLOBAL_HINWEISE:
            return
        # Fehlertext holen
        msg = ""
        with self._buffer() as buf:
            self._lib.EricMtHoleFehlerText(self._instanz, rc, buf)
            msg = self._read_buffer(buf)
        raise EricError(rc, f"{operation}: {msg}" if msg else operation)

    # === Oeffentliche API ===

    def get_version(self) -> str:
        """ERiC SDK Version abfragen."""
        self._ensure_initialized()
        with self._buffer() as buf:
            rc = self._lib.EricMtVersion(self._instanz, buf)
            self._check_rc(rc, "EricMtVersion")
            return self._read_buffer(buf)

    def validate_xml(self, xml: str, datenart_version: str) -> dict:
        """XML gegen ERiC Schema validieren.

        Returns:
            {"valid": True/False, "errors": str, "warnings": str}
        """
        self._ensure_initialized()
        with self._buffer() as error_buf:
            rc = self._lib.EricMtCheckXML(
                self._instanz,
                xml.encode("utf-8"),
                datenart_version.encode("utf-8"),
                error_buf,
            )
            errors = self._read_buffer(error_buf)

        return {
            "valid": rc == ERIC_OK,
            "return_code": rc,
            "errors": errors if rc != ERIC_OK else "",
            "has_warnings": rc == ERIC_GLOBAL_HINWEISE,
        }

    def validate_steuernummer(self, steuernummer: str) -> bool:
        """Steuernummer pruefen."""
        self._ensure_initialized()
        rc = self._lib.EricMtPruefeSteuernummer(self._instanz, steuernummer.encode("utf-8"))
        return rc == ERIC_OK

    def validate_bufa_nummer(self, bufa: str) -> bool:
        """Bundesfinanzamtsnummer pruefen."""
        self._ensure_initialized()
        rc = self._lib.EricMtPruefeBuFaNummer(self._instanz, bufa.encode("utf-8"))
        return rc == ERIC_OK

    @contextmanager
    def open_certificate(self, cert_path: str):
        """Zertifikat oeffnen (Context Manager).

        Usage:
            with eric.open_certificate("/path/to/cert.pfx") as cert_handle:
                eric.submit_ustva(xml, cert_handle, pin)
        """
        self._ensure_initialized()
        handle = EricZertifikatHandle()
        pin_support = ctypes.c_uint32()

        rc = self._lib.EricMtGetHandleToCertificate(
            self._instanz,
            ctypes.byref(handle),
            ctypes.byref(pin_support),
            cert_path.encode("utf-8"),
        )
        self._check_rc(rc, "Zertifikat oeffnen")

        try:
            yield handle
        finally:
            self._lib.EricMtCloseHandleToCertificate(self._instanz, handle)

    def get_certificate_info(self, cert_path: str, pin: str) -> str:
        """Zertifikat-Eigenschaften abfragen."""
        self._ensure_initialized()
        with self.open_certificate(cert_path) as handle:
            with self._buffer() as buf:
                rc = self._lib.EricMtHoleZertifikatEigenschaften(
                    self._instanz, handle, pin.encode("utf-8"), buf
                )
                self._check_rc(rc, "Zertifikat-Eigenschaften")
                return self._read_buffer(buf)

    def create_transfer_header(
        self,
        xml: str,
        verfahren: str,
        datenart: str,
        vorgang: str = "send-Auth",
    ) -> str:
        """TransferHeader erzeugen (wird von ERiC korrekt befuellt)."""
        self._ensure_initialized()
        settings = get_settings()

        with self._buffer() as buf:
            rc = self._lib.EricMtCreateTH(
                self._instanz,
                xml.encode("utf-8"),
                verfahren.encode("utf-8"),
                datenart.encode("utf-8"),
                vorgang.encode("utf-8"),
                settings.testmerker.encode("utf-8") if settings.testmerker else None,
                settings.hersteller_id.encode("utf-8"),
                settings.daten_lieferant.encode("utf-8"),
                b"GastroZen 1.0",
                None,  # publicKey
                buf,
            )
            self._check_rc(rc, "TransferHeader erzeugen")
            return self._read_buffer(buf)

    def submit(
        self,
        xml: str,
        datenart_version: str,
        cert_handle: EricZertifikatHandle,
        pin: str,
        flags: int = ERIC_VALIDIERE_UND_SENDE,
        pdf_path: str | None = None,
    ) -> dict:
        """Daten validieren und an ELSTER senden.

        Returns:
            {
                "success": bool,
                "return_code": int,
                "server_response": str,
                "result_xml": str,
                "transfer_ticket": str,
                "pdf_generated": bool,
            }
        """
        self._ensure_initialized()

        # Druck-Parameter (optional)
        druck_param = None
        if pdf_path:
            flags |= ERIC_DRUCKE
            druck_param = EricDruckParameterT.create(pdf_path)

        # Verschluesselungs-Parameter
        crypto_param = EricVerschluesselungsParameterT.create(cert_handle, pin)

        with self._buffer() as result_buf, self._buffer() as server_buf:
            rc = self._lib.EricMtBearbeiteVorgang(
                self._instanz,
                xml.encode("utf-8"),
                datenart_version.encode("utf-8"),
                ctypes.c_uint32(flags),
                ctypes.byref(druck_param) if druck_param else None,
                ctypes.byref(crypto_param),
                None,  # transferHandle
                result_buf,
                server_buf,
            )

            result_xml = self._read_buffer(result_buf)
            server_response = self._read_buffer(server_buf)

        # Transfer-Ticket aus Server-Antwort extrahieren
        transfer_ticket = self._extract_transfer_ticket(server_response)

        success = rc == ERIC_OK or rc == ERIC_GLOBAL_HINWEISE

        if not success:
            error_msg = ""
            with self._buffer() as err_buf:
                self._lib.EricMtHoleFehlerText(self._instanz, rc, err_buf)
                error_msg = self._read_buffer(err_buf)
            logger.error(f"ELSTER Einreichung fehlgeschlagen: {rc} - {error_msg}")

        return {
            "success": success,
            "return_code": rc,
            "server_response": server_response,
            "result_xml": result_xml,
            "transfer_ticket": transfer_ticket,
            "pdf_generated": pdf_path is not None and success,
        }

    def get_finanzaemter(self, bundesland_nr: str) -> str:
        """Finanzaemter eines Bundeslandes abfragen."""
        self._ensure_initialized()
        with self._buffer() as buf:
            rc = self._lib.EricMtHoleFinanzaemter(
                self._instanz, bundesland_nr.encode("utf-8"), buf
            )
            self._check_rc(rc, "Finanzaemter abfragen")
            return self._read_buffer(buf)

    # === Interne Hilfsfunktionen ===

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise EricError(0, "ERiC SDK nicht initialisiert. Rufe initialize() auf.")

    @staticmethod
    def _extract_transfer_ticket(server_response: str) -> str:
        """Transfer-Ticket aus der ELSTER Server-Antwort extrahieren."""
        if not server_response:
            return ""
        # <TransferTicket>...</TransferTicket>
        start = server_response.find("<TransferTicket>")
        end = server_response.find("</TransferTicket>")
        if start != -1 and end != -1:
            return server_response[start + 16:end]
        return ""


# Singleton
_eric: EricWrapper | None = None


def get_eric() -> EricWrapper:
    global _eric
    if _eric is None:
        _eric = EricWrapper()
    return _eric
