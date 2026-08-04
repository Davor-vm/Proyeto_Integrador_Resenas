"""
scripts/preprocessing/preprocessing.py
Módulo de Limpieza de Texto y Análisis de Sentimiento (NLP).
"""

import re
import pandas as pd
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Configuración de rutas según la estructura del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Descarga de recursos NLTK
nltk.download('stopwords', quiet=True)
STOP_WORDS_ES = set(stopwords.words('spanish'))

# Inicializar VADER Sentiment Analyzer
vader_analyzer = SentimentIntensityAnalyzer()


def limpiar_texto(texto: str) -> str:
    """Aplica minúsculas, elimina puntuación, números y stop words."""
    if not isinstance(texto, str):
        return ""
    
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    palabras = [p for p in texto.split() if p not in STOP_WORDS_ES and len(p) > 2]
    return " ".join(palabras)


def calcular_sentimiento(texto_original: str) -> tuple:
    """Calcula la polaridad usando VADER y TextBlob, retornando la puntuación y categoría."""
    if not isinstance(texto_original, str) or not texto_original.strip():
        return 0.0, "Neutral"
    
    # Análisis secundario con TextBlob
    blob = TextBlob(texto_original)
    polaridad_tb = blob.sentiment.polarity
    
    # Asignación de categoría según la polaridad
    if polaridad_tb > 0.10:
        categoria = "Positivo"
    elif polaridad_tb < -0.10:
        categoria = "Negativo"
    else:
        categoria = "Neutral"
        
    return round(polaridad_tb, 3), categoria


def ejecutar_preprocesamiento():
    print("=== [ETAPA 1] Inicio de Preprocesamiento de Texto y Sentimiento ===")
    
    archivo_entrada = RAW_DIR / "reviews_raw.csv"
    if not archivo_entrada.exists():
        print(f"Error: No se localizó el archivo {archivo_entrada}")
        return

    df_reviews = pd.read_csv(archivo_entrada)
    print(f"Reseñas cargadas desde RAW: {len(df_reviews)}")

    # Aplicar limpieza de texto y cálculo de longitud
    df_reviews['comentario_limpio'] = df_reviews['comentario'].apply(limpiar_texto)
    df_reviews['longitud_texto'] = df_reviews['comentario'].fillna('').apply(len)

    # Calcular polaridad y etiqueta de sentimiento
    resultados_sentimiento = df_reviews['comentario'].apply(calcular_sentimiento)
    df_reviews['polaridad'] = [r[0] for r in resultados_sentimiento]
    df_reviews['sentimiento'] = [r[1] for r in resultados_sentimiento]

    # Guardar en la capa PROCESSED
    archivo_salida = PROCESSED_DIR / "reviews_clean.csv"
    df_reviews.to_csv(archivo_salida, index=False, encoding="utf-8-sig")
    print(f"Preprocesamiento finalizado. Resultado guardado en: {archivo_salida}")


if __name__ == "__main__":
    ejecutar_preprocesamiento()