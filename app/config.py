from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API-Authentifizierung
    api_secret_key: str = ""

    # ERiC SDK
    eric_lib_path: str = "/app/eric_lib"
    eric_log_path: str = "/app/logs"

    # ELSTER
    hersteller_id: str = ""
    daten_lieferant: str = "GastroZen UG"

    # Test-Modus
    test_mode: bool = True

    # Zertifikate
    cert_path: str = "/app/certs"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"

    @property
    def testmerker(self) -> str | None:
        return "700000004" if self.test_mode else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
