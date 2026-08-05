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
from deep_translator import GoogleTranslator

# Configuración de rutas según la estructura del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Descarga de recursos NLTK
nltk.download('stopwords', quiet=True)
STOP_WORDS_ES = set(stopwords.words('spanish'))

# Inicializar VADER Sentiment Analyzer y Traductor
vader_analyzer = SentimentIntensityAnalyzer()
translator = GoogleTranslator(source='auto', target='en')


def traducir_a_ingles(texto: str) -> str:
    """
    Traduce texto en español a inglés para optimizar el análisis de VADER/TextBlob.
    Retorna el texto original si falla la conexión a internet.
    """
    if not texto or not isinstance(texto, str) or len(texto.strip()) < 3:
        return ""
    try:
        # Se limita la longitud a 400 caracteres para agilizar el procesamiento
        return translator.translate(texto[:400])
    except Exception:
        return texto


def limpiar_texto(texto: str) -> str:
    """Aplica minúsculas, elimina puntuación, números y stop words."""
    if not isinstance(texto, str):
        return ""
    
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    palabras = [p for p in texto.split() if p not in STOP_WORDS_ES and len(p) > 2]
    return " ".join(palabras)


def calcular_sentimiento(texto_original: str, rating: float = None) -> tuple:
    """
    Calcula la polaridad combinando VADER y TextBlob, retornando la puntuación y categoría.
    Aplica ajuste según el rating de la reseña si está disponible.
    """
    if not isinstance(texto_original, str) or not texto_original.strip():
        return 0.0, "Neutral"
    
    # Traducir temporalmente para que VADER y TextBlob evalúen correctamente el español
    texto_en = traducir_a_ingles(texto_original)
    texto_evaluar = texto_en if texto_en else texto_original

    # 1. Análisis con TextBlob
    blob = TextBlob(texto_evaluar)
    polaridad_tb = blob.sentiment.polarity

    # 2. Análisis con VADER
    vader_scores = vader_analyzer.polarity_scores(texto_evaluar)
    vader_compound = vader_scores['compound']

    # Ponderación híbrida: 70% VADER + 30% TextBlob
    polaridad_combinada = (vader_compound * 0.7) + (polaridad_tb * 0.3)
    polaridad_final = round(polaridad_combinada, 3)

    # Ajuste por inconsistencias (evita clasificar 5 estrellas como negativo)
    if rating is not None and pd.notna(rating):
        if rating >= 4.0 and polaridad_final < 0:
            polaridad_final = max(0.15, abs(polaridad_final))
        elif rating <= 2.0 and polaridad_final > 0:
            polaridad_final = min(-0.15, -abs(polaridad_final))

    # Asignación de categoría
    if polaridad_final >= 0.05:
        categoria = "Positivo"
    elif polaridad_final <= -0.05:
        categoria = "Negativo"
    else:
        categoria = "Neutral"
        
    return polaridad_final, categoria


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

    # Identificar columna de rating/calificación en el CSV de origen si existe
    col_rating = 'rating' if 'rating' in df_reviews.columns else ('calificacion' if 'calificacion' in df_reviews.columns else None)

    # Calcular polaridad y etiqueta de sentimiento usando el enfoque híbrido VADER + TextBlob
    if col_rating:
        resultados_sentimiento = df_reviews.apply(
            lambda r: calcular_sentimiento(r['comentario'], r[col_rating]), axis=1
        )
    else:
        resultados_sentimiento = df_reviews['comentario'].apply(calcular_sentimiento)

    df_reviews['polaridad'] = [r[0] for r in resultados_sentimiento]
    df_reviews['sentimiento'] = [r[1] for r in resultados_sentimiento]

    # Guardar en la capa PROCESSED
    archivo_salida = PROCESSED_DIR / "reviews_clean.csv"
    df_reviews.to_csv(archivo_salida, index=False, encoding="utf-8-sig")
    print(f"Preprocesamiento finalizado. Resultado guardado en: {archivo_salida}")


if __name__ == "__main__":
    ejecutar_preprocesamiento()