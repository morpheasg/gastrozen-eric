"""ERiC SDK Wrapper - ctypes Anbindung an libericapi.so.

Nutzt die Singlethread-API (EricInitialisiere/EricBeende).
Die .so-Dateien muessen im eric_lib/ Verzeichnis liegen.
"""

import ctypes
import logging
import os
from pathlib import Path
from contextlib import contextmanager

from app.eric.types import (
    EricRueckgabepufferHandle,
    EricZertifikatHandle,
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
    """Wrapper fuer ERiC SDK (Singlethread-API)."""

    def __init__(self):
        self._lib: ctypes.CDLL | None = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        settings = get_settings()
        lib_path = Path(settings.eric_lib_path) / "libericapi.so"
        return lib_path.exists()

    def initialize(self) -> None:
        if self._initialized:
            return

        settings = get_settings()
        lib_path = Path(settings.eric_lib_path) / "libericapi.so"

        if not lib_path.exists():
            raise EricError(0, f"ERiC Library nicht gefunden: {lib_path}")

        self._lib = ctypes.CDLL(str(lib_path))
        self._setup_function_signatures()

        plugin_path = str(Path(settings.eric_lib_path) / "plugins").encode("utf-8")
        log_path = settings.eric_log_path.encode("utf-8")

        rc = self._lib.EricInitialisiere(plugin_path, log_path)
        if rc != ERIC_OK:
            raise EricError(rc, "EricInitialisiere fehlgeschlagen")

        self._initialized = True
        logger.info("ERiC SDK initialisiert")

    def shutdown(self) -> None:
        if not self._initialized or not self._lib:
            return
        self._lib.EricBeende()
        self._initialized = False
        logger.info("ERiC SDK beendet")

    def _setup_function_signatures(self) -> None:
        lib = self._lib

        # Init/Shutdown
        lib.EricInitialisiere.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.EricInitialisiere.restype = ctypes.c_int

        lib.EricBeende.argtypes = []
        lib.EricBeende.restype = ctypes.c_int

        # Rueckgabepuffer
        lib.EricRueckgabepufferErzeugen.argtypes = []
        lib.EricRueckgabepufferErzeugen.restype = EricRueckgabepufferHandle

        lib.EricRueckgabepufferInhalt.argtypes = [EricRueckgabepufferHandle]
        lib.EricRueckgabepufferInhalt.restype = ctypes.c_char_p

        lib.EricRueckgabepufferFreigeben.argtypes = [EricRueckgabepufferHandle]
        lib.EricRueckgabepufferFreigeben.restype = ctypes.c_int

        # Hauptfunktion
        lib.EricBearbeiteVorgang.argtypes = [
            ctypes.c_char_p,                                    # datenpuffer (XML)
            ctypes.c_char_p,                                    # datenartVersion
            ctypes.c_uint32,                                    # bearbeitungsFlags
            ctypes.POINTER(EricDruckParameterT),                # druckParameter
            ctypes.POINTER(EricVerschluesselungsParameterT),    # cryptoParameter
            ctypes.c_void_p,                                    # transferHandle
            EricRueckgabepufferHandle,                          # rueckgabeXmlPuffer
            EricRueckgabepufferHandle,                          # serverantwortXmlPuffer
        ]
        lib.EricBearbeiteVorgang.restype = ctypes.c_int

        # Zertifikate
        lib.EricGetHandleToCertificate.argtypes = [
            ctypes.POINTER(EricZertifikatHandle),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_char_p,
        ]
        lib.EricGetHandleToCertificate.restype = ctypes.c_int

        lib.EricCloseHandleToCertificate.argtypes = [EricZertifikatHandle]
        lib.EricCloseHandleToCertificate.restype = ctypes.c_int

        lib.EricHoleZertifikatEigenschaften.argtypes = [
            EricZertifikatHandle, ctypes.c_char_p, EricRueckgabepufferHandle,
        ]
        lib.EricHoleZertifikatEigenschaften.restype = ctypes.c_int

        # Validierung
        lib.EricCheckXML.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, EricRueckgabepufferHandle
        ]
        lib.EricCheckXML.restype = ctypes.c_int

        lib.EricPruefeSteuernummer.argtypes = [ctypes.c_char_p]
        lib.EricPruefeSteuernummer.restype = ctypes.c_int

        lib.EricPruefeBuFaNummer.argtypes = [ctypes.c_char_p]
        lib.EricPruefeBuFaNummer.restype = ctypes.c_int

        # Hilfsfunktionen
        lib.EricHoleFehlerText.argtypes = [ctypes.c_int, EricRueckgabepufferHandle]
        lib.EricHoleFehlerText.restype = ctypes.c_int

        lib.EricVersion.argtypes = [EricRueckgabepufferHandle]
        lib.EricVersion.restype = ctypes.c_int

        lib.EricHoleFinanzaemter.argtypes = [ctypes.c_char_p, EricRueckgabepufferHandle]
        lib.EricHoleFinanzaemter.restype = ctypes.c_int

    # === Puffer-Hilfsfunktionen ===

    def _create_buffer(self) -> EricRueckgabepufferHandle:
        return self._lib.EricRueckgabepufferErzeugen()

    def _read_buffer(self, handle: EricRueckgabepufferHandle) -> str:
        content = self._lib.EricRueckgabepufferInhalt(handle)
        return content.decode("utf-8") if content else ""

    def _free_buffer(self, handle: EricRueckgabepufferHandle) -> None:
        self._lib.EricRueckgabepufferFreigeben(handle)

    @contextmanager
    def _buffer(self):
        buf = self._create_buffer()
        try:
            yield buf
        finally:
            self._free_buffer(buf)

    def _check_rc(self, rc: int, operation: str) -> None:
        if rc == ERIC_OK or rc == ERIC_GLOBAL_HINWEISE:
            return
        msg = ""
        with self._buffer() as buf:
            self._lib.EricHoleFehlerText(rc, buf)
            msg = self._read_buffer(buf)
        raise EricError(rc, f"{operation}: {msg}" if msg else operation)

    # === Oeffentliche API ===

    def get_version(self) -> str:
        self._ensure_initialized()
        with self._buffer() as buf:
            rc = self._lib.EricVersion(buf)
            self._check_rc(rc, "EricVersion")
            return self._read_buffer(buf)

    def validate_xml(self, xml: str, datenart_version: str) -> dict:
        self._ensure_initialized()
        with self._buffer() as error_buf:
            rc = self._lib.EricCheckXML(
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
        self._ensure_initialized()
        rc = self._lib.EricPruefeSteuernummer(steuernummer.encode("utf-8"))
        return rc == ERIC_OK

    def validate_bufa_nummer(self, bufa: str) -> bool:
        self._ensure_initialized()
        rc = self._lib.EricPruefeBuFaNummer(bufa.encode("utf-8"))
        return rc == ERIC_OK

    @contextmanager
    def open_certificate(self, cert_path: str):
        self._ensure_initialized()
        handle = EricZertifikatHandle()
        pin_support = ctypes.c_uint32()
        rc = self._lib.EricGetHandleToCertificate(
            ctypes.byref(handle),
            ctypes.byref(pin_support),
            cert_path.encode("utf-8"),
        )
        self._check_rc(rc, "Zertifikat oeffnen")
        try:
            yield handle
        finally:
            self._lib.EricCloseHandleToCertificate(handle)

    def get_certificate_info(self, cert_path: str, pin: str) -> str:
        self._ensure_initialized()
        with self.open_certificate(cert_path) as handle:
            with self._buffer() as buf:
                rc = self._lib.EricHoleZertifikatEigenschaften(
                    handle, pin.encode("utf-8"), buf
                )
                self._check_rc(rc, "Zertifikat-Eigenschaften")
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
        self._ensure_initialized()

        druck_param = None
        if pdf_path:
            flags |= ERIC_DRUCKE
            druck_param = EricDruckParameterT.create(pdf_path)

        crypto_param = EricVerschluesselungsParameterT.create(cert_handle, pin)

        with self._buffer() as result_buf, self._buffer() as server_buf:
            rc = self._lib.EricBearbeiteVorgang(
                xml.encode("utf-8"),
                datenart_version.encode("utf-8"),
                ctypes.c_uint32(flags),
                ctypes.byref(druck_param) if druck_param else None,
                ctypes.byref(crypto_param),
                None,
                result_buf,
                server_buf,
            )
            result_xml = self._read_buffer(result_buf)
            server_response = self._read_buffer(server_buf)

        transfer_ticket = self._extract_transfer_ticket(server_response)
        success = rc == ERIC_OK or rc == ERIC_GLOBAL_HINWEISE

        if not success:
            error_msg = ""
            with self._buffer() as err_buf:
                self._lib.EricHoleFehlerText(rc, err_buf)
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
        self._ensure_initialized()
        with self._buffer() as buf:
            rc = self._lib.EricHoleFinanzaemter(bundesland_nr.encode("utf-8"), buf)
            self._check_rc(rc, "Finanzaemter abfragen")
            return self._read_buffer(buf)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise EricError(0, "ERiC SDK nicht initialisiert. Rufe initialize() auf.")

    @staticmethod
    def _extract_transfer_ticket(server_response: str) -> str:
        if not server_response:
            return ""
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
