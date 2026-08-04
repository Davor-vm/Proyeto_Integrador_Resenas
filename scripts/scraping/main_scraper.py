import random
import time
import pandas as pd
from config import PRODUCTOS_OBJETIVO, MAX_PAGINAS_PER_PROD, LIMIT_POR_PAGINA, ESPERA_ENTRE_REQUESTS, RAW_DIR
from extractor import descargar_pagina_reviews
from parser import parsear_json_reviews
from logger import logger

def main():
    logger.info("=== Inicio de Scraping Enfocado: Audífonos Sony & Apple (Over-Ear vs In-Ear) ===")
    
    productos_lista = []
    todas_las_reviews = []
    
    for prod_idx, prod in enumerate(PRODUCTOS_OBJETIVO, 1):
        item_id = prod["item_id"]
        product_url = prod["url"]
        nombre = prod["nombre"]
        marca = prod["marca"]
        tipo = prod["tipo"]
        
        logger.info(f"Procesando [{prod_idx}/{len(PRODUCTOS_OBJETIVO)}]: {nombre} ({tipo}) - ID: {item_id}")
        
        # Registrar catálogo
        productos_lista.append({
            "producto_id": item_id,
            "nombre": nombre,
            "marca": marca,
            "tipo_formato": tipo,
            "precio": prod["precio"],
            "vendedor": prod["vendedor"],
            "tienda_oficial": True,
            "url": product_url,
            "plataforma": "Mercado Libre"
        })
        
        # Extracción de opiniones vía endpoint JSON
        offset = 0
        reviews_producto = 0
        
        for pagina in range(1, MAX_PAGINAS_PER_PROD + 1):
            data = descargar_pagina_reviews(item_id, product_url, offset, LIMIT_POR_PAGINA)
            
            if not data:
                break
                
            reviews_pagina = parsear_json_reviews(data, item_id, nombre, product_url)
            
            if not reviews_pagina:
                logger.info(f"Página {pagina}: Sin más reseñas disponibles para este modelo.")
                break
            
            # Enriquecer cada reseña con tipo y marca para facilitar NLP posterior
            for r in reviews_pagina:
                r["marca"] = marca
                r["tipo_formato"] = tipo
                
            todas_las_reviews.extend(reviews_pagina)
            reviews_producto += len(reviews_pagina)
            
            if len(reviews_pagina) < LIMIT_POR_PAGINA:
                break
                
            offset += LIMIT_POR_PAGINA
            time.sleep(random.uniform(*ESPERA_ENTRE_REQUESTS))
            
        logger.info(f"Total de reseñas capturadas para '{nombre}': {reviews_producto}")

    # Guardar Catálogo de Productos
    df_prods = pd.DataFrame(productos_lista)
    df_prods.to_csv(RAW_DIR / "productos_raw.csv", index=False, encoding="utf-8-sig")
    logger.info(f"Guardados {len(df_prods)} productos en {RAW_DIR / 'productos_raw.csv'}")

    # Guardar Reseñas Extraídas
    df_reviews = pd.DataFrame(todas_las_reviews)
    if not df_reviews.empty:
        df_reviews.to_csv(RAW_DIR / "reviews_raw.csv", index=False, encoding="utf-8-sig")
        logger.info(f"Guardadas {len(df_reviews)} reseñas REALES en {RAW_DIR / 'reviews_raw.csv'}")
    else:
        logger.warning("No se obtuvieron reseñas.")

    logger.info("=== Scraping Finalizado Exitosamente ===")

if __name__ == "__main__":
    main()