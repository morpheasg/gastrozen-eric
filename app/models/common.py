"""Gemeinsame Pydantic-Models."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    eric_available: bool
    eric_version: str | None = None
    test_mode: bool


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: int | None = None


class SubmitResponse(BaseModel):
    success: bool
    transfer_ticket: str = ""
    server_response: str = ""
    result_xml: str = ""
    return_code: int = 0
    pdf_generated: bool = False


class ValidateResponse(BaseModel):
    valid: bool
    errors: str = ""
    has_warnings: bool = False
    return_code: int = 0
