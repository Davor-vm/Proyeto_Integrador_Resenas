import sys
from pathlib import Path

# Vincular los módulos del proyecto al PATH
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR / "scripts" / "scraping"))
sys.path.append(str(ROOT_DIR / "scripts" / "preprocessing"))
sys.path.append(str(ROOT_DIR / "scripts" / "clustering"))
sys.path.append(str(ROOT_DIR / "scripts" / "etl"))

from main_scraper import main as ejecutar_scraping
from preprocessing import ejecutar_preprocesamiento
from clustering import ejecutar_clustering
from load_dw import ejecutar_etl_dw

def main():
    print("==========================================================")
    print(" PLATAFORMA ANALÍTICA: MINERÍA DE DATOS & DATA WAREHOUSE ")
    print("==========================================================")
    
    # 1. Minería Web (Scraping)
    print("\n---> [Fase 1/4] Ejecutando Minería Web...")
    try:
        ejecutar_scraping()
    except Exception as e:
        print(f"Error en Fase 1: {e}")
        return

    # 2. Preprocesamiento NLP y Sentimiento
    print("\n---> [Fase 2/4] Ejecutando NLP y Análisis de Sentimiento...")
    try:
        ejecutar_preprocesamiento()
    except Exception as e:
        print(f"Error en Fase 2: {e}")
        return

    # 3. Clustering (Agrupamiento de Temas)
    print("\n---> [Fase 3/4] Ejecutando Clustering de Reseñas...")
    try:
        ejecutar_clustering()
    except Exception as e:
        print(f"Error en Fase 3: {e}")
        return

    # 4. Carga de Datos al Data Warehouse (DuckDB)
    print("\n---> [Fase 4/4] Ejecutando Proceso ETL hacia DuckDB...")
    try:
        ejecutar_etl_dw()
    except Exception as e:
        print(f"Error en Fase 4: {e}")
        return

    print("\n==========================================================")
    print("   ¡PROCESO FINALIZADO EXITOSAMENTE!")
    print("   Base de datos generada en: data/warehouse/reviews.db")
    print("==========================================================")

if __name__ == "__main__":
    main()