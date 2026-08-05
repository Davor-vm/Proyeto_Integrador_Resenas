import os
import re
import duckdb
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Configuración de rutas según la arquitectura del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
RAW_DIR = ROOT_DIR / "data" / "raw"
WAREHOUSE_DIR = ROOT_DIR / "data" / "warehouse"
SQL_DIR = ROOT_DIR / "sql"

WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = WAREHOUSE_DIR / "reviews.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"

def parse_relative_date(date_str) -> datetime:
    """
    Convierte cadenas de fecha en español (absolutas o relativas como 'Hace 2 meses')
    a un objeto datetime.
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return datetime.now()
    
    date_str_clean = date_str.lower().strip()
    now = datetime.now()
    
    match = re.search(r'hace\s+(\d+)\s+(día|dias|días|mes|meses|año|años|semana|semanas|hora|horas)', date_str_clean)
    if match:
        cantidad = int(match.group(1))
        unidad = match.group(2)
        
        if 'hora' in unidad:
            return now - timedelta(hours=cantidad)
        elif 'día' in unidad or 'dia' in unidad:
            return now - timedelta(days=cantidad)
        elif 'semana' in unidad:
            return now - timedelta(weeks=cantidad)
        elif 'mes' in unidad:
            return now - timedelta(days=cantidad * 30)
        elif 'año' in unidad:
            return now - timedelta(days=cantidad * 365)
            
    # Intentar parsear si la fecha ya viene en formato estándar (ej. 2024-05-10)
    try:
        return pd.to_datetime(date_str, dayfirst=True)
    except Exception:
        return now

def clasificar_longitud_tipo(length: int) -> int:
    """Retorna el ID de Dim_ReviewType según la longitud en caracteres del comentario."""
    if length < 50:
        return 1  # Corta
    elif length <= 200:
        return 2  # Media
    else:
        return 3  # Larga

def ejecutar_etl_dw():
    print("=== [ETAPA 3] Inicio de Carga al Data Warehouse (DuckDB) ===")

    dataset_path = PROCESSED_DIR / "dataset_final.csv"
    if not dataset_path.exists():
        print(f"Error: No se encontró el dataset en {dataset_path}")
        return

    # 1. Leer dataset consolidado
    df = pd.read_csv(dataset_path)
    print(f"Reseñas procesadas cargadas para ETL: {len(df)}")

    # Conectar a la base de datos DuckDB
    con = duckdb.connect(str(DB_PATH))

    # 2. Crear las tablas ejecutando schema.sql
    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_ddl = f.read()
        con.execute(schema_ddl)
        print("Esquema Físico creado/verificado exitosamente desde schema.sql.")
    else:
        print(f"Error: No se encontró schema.sql en {SCHEMA_PATH}")
        con.close()
        return

    # Limpieza previa para garantizar idempotencia de la carga
    con.execute("DELETE FROM Fact_Reviews;")
    con.execute("DELETE FROM Dim_Product;")
    con.execute("DELETE FROM Dim_Date;")
    con.execute("DELETE FROM Dim_Sentiment;")
    con.execute("DELETE FROM Dim_ReviewType;")
    con.execute("DELETE FROM Dim_Cluster;")

    # 3. Poblado de Dim_Product
    df_product = df[[
        'producto_id', 'nombre_producto', 'marca', 'tipo_formato', 
        'precio', 'vendedor', 'tienda_oficial', 'url'
    ]].drop_duplicates(subset=['producto_id']).copy()

    df_product.columns = [
        'product_id', 'product_name', 'brand', 'format_type', 
        'price', 'seller', 'official_store', 'product_uri'
    ]
    con.register('temp_product', df_product)
    con.execute("INSERT INTO Dim_Product SELECT * FROM temp_product;")
    print(f"Dim_Product poblada ({len(df_product)} productos).")

    # 4. Poblado de Dim_Date (Ajustado para parsear texto relativo)
    df['fecha_dt'] = df['fecha_review'].apply(parse_relative_date)
    dates_unique = df['fecha_dt'].drop_duplicates().sort_values()

    df_date = pd.DataFrame({
        'date_id': dates_unique.dt.strftime('%Y%m%d').astype(int),
        'review_date': dates_unique.dt.strftime('%Y-%m-%d'),
        'year': dates_unique.dt.year,
        'quarter': dates_unique.dt.quarter,
        'month': dates_unique.dt.month,
        'day': dates_unique.dt.day
    })
    con.register('temp_date', df_date)
    con.execute("INSERT INTO Dim_Date SELECT * FROM temp_date;")
    print(f"Dim_Date poblada ({len(df_date)} fechas unicas generadas).")

    # 5. Poblado de Dim_Sentiment
    df_sentiment = pd.DataFrame([
        {'sentiment_id': 1, 'sentiment': 'Positivo', 'polarity': 0.50},
        {'sentiment_id': 2, 'sentiment': 'Neutral',  'polarity': 0.00},
        {'sentiment_id': 3, 'sentiment': 'Negativo', 'polarity': -0.50}
    ])
    con.register('temp_sentiment', df_sentiment)
    con.execute("INSERT INTO Dim_Sentiment SELECT * FROM temp_sentiment;")
    print("Dim_Sentiment poblada.")

    # 6. Poblado de Dim_ReviewType
    df_review_type = pd.DataFrame([
        {'review_type_id': 1, 'review_type': 'Corta'},
        {'review_type_id': 2, 'review_type': 'Media'},
        {'review_type_id': 3, 'review_type': 'Larga'}
    ])
    con.register('temp_review_type', df_review_type)
    con.execute("INSERT INTO Dim_ReviewType SELECT * FROM temp_review_type;")
    print("Dim_ReviewType poblada.")

    # 7. Poblado de Dim_Cluster
    cluster_mapping = {
        0: "Calidad de Sonido y ANC",
        1: "Batería y Conexión",
        2: "Comodidad y Ergonomía",
        3: "Precio y Valoración"
    }
    df_cluster = pd.DataFrame([
        {'cluster_id': cid, 'cluster_theme': theme} 
        for cid, theme in cluster_mapping.items()
    ])
    con.register('temp_cluster', df_cluster)
    con.execute("INSERT INTO Dim_Cluster SELECT * FROM temp_cluster;")
    print("Dim_Cluster poblada.")

    # 8. Poblado de Fact_Reviews
    sentiment_map = {'Positivo': 1, 'Neutral': 2, 'Negativo': 3}
    df['sentiment_id'] = df['sentimiento'].map(sentiment_map).fillna(2).astype(int)
    df['review_type_id'] = df['longitud_texto'].apply(clasificar_longitud_tipo)
    df['date_id'] = df['fecha_dt'].dt.strftime('%Y%m%d').astype(int)

    df['review_id_clean'] = pd.to_numeric(df['reseña_id'], errors='coerce')
    df['review_id_clean'] = df['review_id_clean'].fillna(pd.Series(range(1, len(df) + 1))).astype('int64')

    df_fact = df[[
        'review_id_clean', 'producto_id', 'date_id', 'sentiment_id', 
        'review_type_id', 'cluster_id', 'rating', 'longitud_texto'
    ]].copy()

    df_fact.columns = [
        'review_id', 'product_id', 'date_id', 'sentiment_id', 
        'review_type_id', 'cluster_id', 'rating', 'review_length'
    ]

    con.register('temp_fact', df_fact)
    con.execute("INSERT INTO Fact_Reviews SELECT * FROM temp_fact;")

    total_fact = con.execute("SELECT COUNT(*) FROM Fact_Reviews").fetchone()[0]
    print(f"=== ETL Concluido Exitosamente. Total registros en Fact_Reviews: {total_fact} ===")

    con.close()

if __name__ == "__main__":
    ejecutar_etl_dw()