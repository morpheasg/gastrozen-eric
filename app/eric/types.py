"""ERiC SDK C-Struct Definitionen fuer ctypes."""

import ctypes
from app.eric.constants import DRUCK_PARAMETER_VERSION, VERSCHLUESSELUNG_PARAMETER_VERSION

# === Typ-Aliase ===
EricRueckgabepufferHandle = ctypes.c_void_p
EricTransferHandle = ctypes.c_void_p
EricZertifikatHandle = ctypes.c_void_p
EricInstanzHandle = ctypes.c_void_p

# Callback-Typen
EricFortschrittCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
EricPdfCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32)


class EricDruckParameterT(ctypes.Structure):
    """Druck-Parameter fuer PDF-Erzeugung."""
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("vorschau", ctypes.c_uint32),          # 1 = Vorschau-PDF
        ("duplex_druck", ctypes.c_uint32),       # 1 = Duplex mit Rand
        ("pdf_name", ctypes.c_char_p),           # Ausgabe-Pfad
        ("fuss_text", ctypes.c_char_p),          # Fusszeile (optional)
        ("pdf_callback", EricPdfCallback),
        ("pdf_callback_benutzerdaten", ctypes.c_void_p),
    ]

    @classmethod
    def create(cls, pdf_path: str, vorschau: bool = False, fuss_text: str = "") -> "EricDruckParameterT":
        param = cls()
        param.version = DRUCK_PARAMETER_VERSION
        param.vorschau = 1 if vorschau else 0
        param.duplex_druck = 0
        param.pdf_name = pdf_path.encode("utf-8")
        param.fuss_text = fuss_text.encode("utf-8") if fuss_text else None
        param.pdf_callback = EricPdfCallback(0)
        param.pdf_callback_benutzerdaten = None
        return param


class EricVerschluesselungsParameterT(ctypes.Structure):
    """Verschluesselungs-Parameter fuer Zertifikat-basierte Sendung."""
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("zertifikat_handle", EricZertifikatHandle),
        ("pin", ctypes.c_char_p),
        ("abruf_code", ctypes.c_char_p),
    ]

    @classmethod
    def create(cls, cert_handle: EricZertifikatHandle, pin: str, abruf_code: str = "") -> "EricVerschluesselungsParameterT":
        param = cls()
        param.version = VERSCHLUESSELUNG_PARAMETER_VERSION
        param.zertifikat_handle = cert_handle
        param.pin = pin.encode("utf-8")
        param.abruf_code = abruf_code.encode("utf-8") if abruf_code else None
        return param
