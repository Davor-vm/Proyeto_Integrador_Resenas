"""
exporter.py
Exporta los datos obtenidos a CSV.
"""

import pandas as pd

from config import RAW_DIR
from logger import logger


def guardar_productos(productos):

    archivo = RAW_DIR / "productos_raw.csv"

    df = pd.DataFrame(productos)

    df.to_csv(
        archivo,
        index=False,
        encoding="utf-8-sig"
    )

    logger.info(f"Archivo generado: {archivo}")