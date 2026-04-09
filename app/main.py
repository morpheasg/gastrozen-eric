"""GastroZen ERiC Microservice - ELSTER Anbindung.

REST API die ERiC (ELSTER Rich Client) kapselt.
Ermoeglicht UStVA-Einreichung und Kassenmeldung fuer GastroZen-Restaurants.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.eric.wrapper import get_eric
from app.routes import health, ustva, kassenmeldung, certificate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/Shutdown: ERiC initialisieren und herunterfahren."""
    eric = get_eric()
    if eric.is_available:
        try:
            eric.initialize()
            logger.info(f"ERiC Version: {eric.get_version()}")
        except Exception as e:
            logger.warning(f"ERiC Initialisierung fehlgeschlagen: {e}")
            logger.info("Server laeuft ohne ERiC (nur XML-Preview verfuegbar)")
    else:
        logger.info("ERiC SDK nicht gefunden - Server laeuft im Preview-Modus")

    yield

    if eric._initialized:
        eric.shutdown()


app = FastAPI(
    title="GastroZen ERiC Microservice",
    description="ELSTER-Anbindung fuer UStVA und Kassenmeldung",
    version="1.0.0",
    lifespan=lifespan,
)

# Routes registrieren
app.include_router(health.router)
app.include_router(ustva.router)
app.include_router(kassenmeldung.router)
app.include_router(certificate.router)
