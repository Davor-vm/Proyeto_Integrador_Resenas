"""
scripts/clustering/clustering.py
Módulo de Agrupamiento de Reseñas (Clustering) y Evaluación con Scikit-Learn.
"""

import pandas as pd
from pathlib import Path

# Scikit-Learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score

# Configuración de rutas
ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def ejecutar_clustering():
    print("=== [ETAPA 2] Inicio de Clustering y Segmentación de Temas ===")
    
    archivo_clean = PROCESSED_DIR / "reviews_clean.csv"
    archivo_prods = RAW_DIR / "productos_raw.csv"
    
    if not archivo_clean.exists():
        print(f"Error: Ejecute primero el preprocesamiento. No existe {archivo_clean}")
        return

    df_reviews = pd.read_csv(archivo_clean)
    
    # Vectorización TF-IDF
    vectorizador = TfidfVectorizer(max_features=300)
    matriz_tfidf = vectorizador.fit_transform(df_reviews['comentario_limpio'].fillna(''))

    # Evaluación de número óptimo de clusters (k)
    print("\nEvaluando algoritmo y número de grupos (Silhouette Score):")
    for k in [3, 4, 5]:
        kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels_km = kmeans_test.fit_predict(matriz_tfidf)
        score_km = silhouette_score(matriz_tfidf, labels_km)
        
        agg_test = AgglomerativeClustering(n_clusters=k)
        labels_agg = agg_test.fit_predict(matriz_tfidf.toarray())
        score_agg = silhouette_score(matriz_tfidf, labels_agg)
        
        print(f"  k={k} | K-Means: {score_km:.3f} | Jerárquico: {score_agg:.3f}")

    # Modelo final con K-Means (k=4)
    k_optimo = 4
    modelo_final = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
    df_reviews['cluster_id'] = modelo_final.fit_predict(matriz_tfidf)

    # Mapeo de nombres de clusters
    nombres_clusters = {
        0: "Calidad de Sonido y ANC",
        1: "Batería y Conexión",
        2: "Comodidad y Ergonomía",
        3: "Precio y Valoración"
    }
    df_reviews['tema_cluster'] = df_reviews['cluster_id'].map(nombres_clusters)

    # Consolidación final con el catálogo de productos
    if archivo_prods.exists():
        df_prods = pd.read_csv(archivo_prods)
        dataset_final = pd.merge(df_reviews, df_prods, on="producto_id", how="left", suffixes=('', '_prod'))
    else:
        dataset_final = df_reviews

    # Exportación del archivo final listo para ETL / DuckDB
    archivo_final = PROCESSED_DIR / "dataset_final.csv"
    dataset_final.to_csv(archivo_final, index=False, encoding="utf-8-sig")
    print(f"\nClustering completado. Dataset final generado en: {archivo_final}")


if __name__ == "__main__":
    ejecutar_clustering()