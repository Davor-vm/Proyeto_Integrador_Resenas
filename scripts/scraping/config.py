import random
from pathlib import Path

# ==============================================================================
# CONFIGURACIÓN DEL ENDPOINT Y PARÁMETROS DE SCRAPING
# ==============================================================================
ENDPOINT_REVIEWS = "https://www.mercadolibre.com.mx/noindex/catalog/reviews/{item_id}/search"
LIMIT_POR_PAGINA = 15
MAX_PAGINAS_PER_PROD = 20    # Extrae hasta 300 reseñas por modelo (hasta 1,200 en total)
TIMEOUT = 10
REINTENTOS = 3
ESPERA_ENTRE_REQUESTS = (2.0, 4.0)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

# RUTAS DEL PROYECTO
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
LOG_DIR = ROOT_DIR / "logs"

# ==============================================================================
# PRODUCTOS OBJETIVO (ENLACES DIRECTOS PROPORCIONADOS)
# ==============================================================================
PRODUCTOS_OBJETIVO = [
    {
        "item_id": "MLM1066705967",
        "marca": "Apple",
        "nombre": "Apple AirPods Max 2",
        "tipo": "Over-Ear",
        "precio": 11999.00,
        "vendedor": "Distribuidor Autorizado Apple",
        "url": "https://www.mercadolibre.com.mx/airpods-max-2-azul-distribuidor-autorizado/p/MLM1066705967"
    },
    {
        "item_id": "MLM42305910",
        "marca": "Sony",
        "nombre": "Sony WH-1000XM5 Over-Ear",
        "tipo": "Over-Ear",
        "precio": 6499.00,
        "vendedor": "Sony Official Store",
        "url": "https://www.mercadolibre.com.mx/auriculares-bluetooth-sony-inalambricos-wh-1000xm5-rosa/p/MLM42305910"
    },
    {
        "item_id": "MLM26578383",
        "marca": "Sony",
        "nombre": "Sony WF-1000XM5 In-Ear",
        "tipo": "In-Ear",
        "precio": 4299.00,
        "vendedor": "Sony Official Store",
        "url": "https://www.mercadolibre.com.mx/audifonos-true-wireless-con-noise-cancelling-wf-1000xm5-color-negro/p/MLM26578383"
    },
    {
        "item_id": "MLM1054106888",
        "marca": "Apple",
        "nombre": "Apple AirPods Pro In-Ear",
        "tipo": "In-Ear",
        "precio": 4499.00,
        "vendedor": "Distribuidor Autorizado Apple",
        "url": "https://www.mercadolibre.com.mx/apple-airpods-pro-3-color-blanco-con-cancelacion-de-ruido-distribuidor-autorizado/p/MLM1054106888"
    }
]

def obtener_headers(referer_url: str):
    """Genera encabezados dinámicos con Referer explícito para evitar bloqueos."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Accept-Language": "es-MX,es;q=0.9",
        "Referer": referer_url
    }