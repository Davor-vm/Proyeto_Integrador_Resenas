"""
logger.py
Configuración del sistema de registro de eventos.
"""

import logging
from pathlib import Path

from config import LOG_DIR

# Crear la carpeta logs si no existe
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "scraper.log"

# Configuración principal del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ScraperMercadoLibre")