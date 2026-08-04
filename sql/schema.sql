-- ============================================================
-- ESQUEMA FÍSICO DEL DATA WAREHOUSE (MODELO ESTRELLA - DAMA)
-- Base de Datos: DuckDB (data/warehouse/reviews.db)
-- ============================================================

-- 1. Dimensión Producto
CREATE TABLE IF NOT EXISTS Dim_Product (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    brand VARCHAR NOT NULL,
    format_type VARCHAR NOT NULL,
    price DECIMAL(10, 2),
    seller VARCHAR,
    official_store BOOLEAN,
    product_uri TEXT
);

-- 2. Dimensión Tiempo/Fecha
CREATE TABLE IF NOT EXISTS Dim_Date (
    date_id INT PRIMARY KEY, -- Formato YYYYMMDD
    review_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL
);

-- 3. Dimensión Sentimiento
CREATE TABLE IF NOT EXISTS Dim_Sentiment (
    sentiment_id INT PRIMARY KEY,
    sentiment VARCHAR NOT NULL, -- Positivo, Neutral, Negativo
    polarity FLOAT
);

-- 4. Dimensión Tipo de Reseña (Clasificación por Longitud)
CREATE TABLE IF NOT EXISTS Dim_ReviewType (
    review_type_id INT PRIMARY KEY,
    review_type VARCHAR NOT NULL -- Corta, Media, Larga
);

-- 5. Dimensión Clúster (Temáticas de Minería de Datos)
CREATE TABLE IF NOT EXISTS Dim_Cluster (
    cluster_id INT PRIMARY KEY,
    cluster_theme VARCHAR NOT NULL
);

-- 6. Tabla de Hechos: Reseñas (Fact_Reviews)
CREATE TABLE IF NOT EXISTS Fact_Reviews (
    review_id BIGINT PRIMARY KEY,
    product_id VARCHAR NOT NULL REFERENCES Dim_Product(product_id),
    date_id INT NOT NULL REFERENCES Dim_Date(date_id),
    sentiment_id INT NOT NULL REFERENCES Dim_Sentiment(sentiment_id),
    review_type_id INT NOT NULL REFERENCES Dim_ReviewType(review_type_id),
    cluster_id INT NOT NULL REFERENCES Dim_Cluster(cluster_id),
    rating FLOAT NOT NULL,
    review_length INT NOT NULL
);