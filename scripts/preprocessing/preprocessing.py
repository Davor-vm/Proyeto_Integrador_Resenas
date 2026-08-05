"""
scripts/preprocessing/preprocessing.py
Módulo de Limpieza de Texto y Análisis de Sentimiento (NLP) Optimizado Localmente.
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

# Palabras clave en español para refuerzo léxico local
PALABRAS_POSITIVAS = {
    'excelente', 'bueno', 'buena', 'buen', 'perfecto', 'perfecta', 'genial', 
    'encanta', 'me gusto', 'gusto', 'recomiendo', 'calidad', 'rapido', 'original',
    'satisfecho', 'increible', 'maravilla', 'top', 'funciona', 'comodo', 'duradero'
}

PALABRAS_NEGATIVAS = {
    'malo', 'mala', 'pesimo', 'pesima', 'defectuoso', 'horrible', 'no sirve', 
    'roto', 'basura', 'decepcion', 'fatal', 'lento', 'caro', 'falso', 'debil',
    'problema', 'fallo', 'chafa', 'devuelvo', 'devolucion', 'ruido'
}


def limpiar_texto(texto: str) -> str:
    """Aplica minúsculas, elimina puntuación, números y stop words."""
    if not isinstance(texto, str):
        return ""
    
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    palabras = [p for p in texto.split() if p not in STOP_WORDS_ES and len(p) > 2]
    return " ".join(palabras)


def calcular_sentimiento_local(texto_original: str, rating: float = None) -> tuple:
    """
    Calcula polaridad y categoría mediante evaluación léxica en español + rating,
    evitando peticiones HTTP externas.
    """
    if not isinstance(texto_original, str) or not texto_original.strip():
        return 0.0, "Neutral"
    
    texto_clean = texto_original.lower()
    
    # 1. Score por léxico en español
    pos_count = sum(1 for p in PALABRAS_POSITIVAS if p in texto_clean)
    neg_count = sum(1 for p in PALABRAS_NEGATIVAS if p in texto_clean)
    
    lexicon_score = 0.0
    if (pos_count + neg_count) > 0:
        lexicon_score = (pos_count - neg_count) / (pos_count + neg_count)

    # 2. TextBlob / VADER basico
    blob_score = TextBlob(texto_original).sentiment.polarity
    vader_score = vader_analyzer.polarity_scores(texto_original)['compound']
    
    # Combinación de scores locales
    polaridad_calculada = (lexicon_score * 0.5) + (vader_score * 0.3) + (blob_score * 0.2)
    
    # 3. Calibración con el Rating de estrellas (Si existe)
    if rating is not None and pd.notna(rating):
        rating = float(rating)
        if rating >= 4.0:
            # Si el usuario puso 4 o 5 estrellas, el sentimiento debe ser al menos levemente positivo
            polaridad_calculada = max(0.10, polaridad_calculada)
        elif rating <= 2.0:
            # Si el usuario puso 1 o 2 estrellas, debe ser negativo
            polaridad_calculada = min(-0.10, -abs(polaridad_calculada))

    polaridad_final = round(polaridad_calculada, 3)

    # Clasificación final
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

    # Identificar columna de rating si existe
    col_rating = 'rating' if 'rating' in df_reviews.columns else ('calificacion' if 'calificacion' in df_reviews.columns else None)

    # Calcular polaridad y etiqueta usando evaluación local rápida
    if col_rating:
        resultados = df_reviews.apply(
            lambda r: calcular_sentimiento_local(r['comentario'], r[col_rating]), axis=1
        )
    else:
        resultados = df_reviews['comentario'].apply(calcular_sentimiento_local)

    df_reviews['polaridad'] = [r[0] for r in resultados]
    df_reviews['sentimiento'] = [r[1] for r in resultados]

    # Guardar en la capa PROCESSED
    archivo_salida = PROCESSED_DIR / "reviews_clean.csv"
    df_reviews.to_csv(archivo_salida, index=False, encoding="utf-8-sig")
    print(f"Preprocesamiento finalizado. Resultado guardado en: {archivo_salida}")


if __name__ == "__main__":
    ejecutar_preprocesamiento()