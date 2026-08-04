from logger import logger

def parsear_json_reviews(data_json: dict, item_id: str, nombre_producto: str, product_url: str):
    """Mapea el contenido del JSON interno a la estructura estándar para reviews_raw.csv."""
    reviews_procesadas = []
    
    if not data_json:
        return reviews_procesadas

    reviews_list = data_json.get("reviews", [])
    
    for r in reviews_list:
        try:
            comment = r.get("comment", {})
            texto = comment.get("content", {}).get("text", "")
            
            # Limpieza básica de saltos de línea e espacios sobrantes
            texto_limpio = texto.replace("\n", " ").strip() if texto else ""
            
            reviews_procesadas.append({
                "reseña_id": str(r.get("id", "")),
                "producto_id": str(item_id),
                "nombre_producto": nombre_producto,
                "plataforma": "Mercado Libre",
                "rating": float(r.get("rating", 0.0)),
                "comentario": texto_limpio,
                "fecha_review": str(comment.get("date", ""))[:10],
                "url": product_url
            })
        except Exception as e:
            logger.warning(f"Error procesando una reseña individual de {item_id}: {e}")

    return reviews_procesadas