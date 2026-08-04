import random
import time
import requests
from config import ENDPOINT_REVIEWS, REINTENTOS, TIMEOUT, ESPERA_ENTRE_REQUESTS, obtener_headers
from logger import logger

def descargar_pagina_reviews(item_id: str, product_url: str, offset: int, limit: int = 15):
    """Realiza la petición HTTP al endpoint JSON interno de reseñas con reintentos."""
    url = ENDPOINT_REVIEWS.format(item_id=item_id)
    params = {
        "objectId": item_id,
        "siteId": "MLM",
        "isItem": "false",
        "offset": offset,
        "limit": limit
    }

    for intento in range(1, REINTENTOS + 1):
        try:
            headers = obtener_headers(product_url)
            resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
            
            if resp.status_code == 200:
                try:
                    return resp.json()
                except ValueError:
                    logger.warning(f"Respuesta no es un JSON válido para {item_id} en offset {offset}.")
                    return None

            if resp.status_code == 404:
                logger.info(f"Sin más reseñas para {item_id} (HTTP 404/Fin de catálogo).")
                return None

            if resp.status_code in (429, 500, 502, 503):
                logger.warning(f"Reintento {intento}/{REINTENTOS} por status {resp.status_code}")
                time.sleep(random.uniform(*ESPERA_ENTRE_REQUESTS) * intento * 2)
                continue

            logger.error(f"Error HTTP {resp.status_code} al consultar {item_id}: {resp.text[:150]}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red en intento {intento}/{REINTENTOS} -> {e}")
            time.sleep(random.uniform(*ESPERA_ENTRE_REQUESTS) * intento)

    logger.error(f"Fallo definitivo para {item_id} en offset={offset} tras {REINTENTOS} intentos.")
    return None