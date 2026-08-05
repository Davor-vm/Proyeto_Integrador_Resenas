-- ============================================================
-- VALIDACIÓN DEL DATA WAREHOUSE
-- Proyecto Integrador - Minería de Datos
-- ============================================================

---------------------------------------------------------------
-- 1. Mostrar las tablas creadas
---------------------------------------------------------------

SHOW TABLES;

---------------------------------------------------------------
-- 2. Cantidad de registros por tabla
---------------------------------------------------------------

SELECT 'Dim_Product' AS tabla, COUNT(*) AS registros
FROM Dim_Product

UNION ALL

SELECT 'Dim_Date', COUNT(*)
FROM Dim_Date

UNION ALL

SELECT 'Dim_Sentiment', COUNT(*)
FROM Dim_Sentiment

UNION ALL

SELECT 'Dim_ReviewType', COUNT(*)
FROM Dim_ReviewType

UNION ALL

SELECT 'Dim_Cluster', COUNT(*)
FROM Dim_Cluster

UNION ALL

SELECT 'Fact_Reviews', COUNT(*)
FROM Fact_Reviews;

---------------------------------------------------------------
-- 3. Primeros registros de la tabla de hechos
---------------------------------------------------------------

SELECT *
FROM Fact_Reviews
LIMIT 10;

---------------------------------------------------------------
-- 4. Productos almacenados
---------------------------------------------------------------

SELECT *
FROM Dim_Product;

---------------------------------------------------------------
-- 5. Distribución de sentimientos
---------------------------------------------------------------

SELECT
    ds.sentiment,
    COUNT(*) AS total_reseñas
FROM Fact_Reviews fr
JOIN Dim_Sentiment ds
    ON fr.sentiment_id = ds.sentiment_id
GROUP BY ds.sentiment
ORDER BY total_reseñas DESC;

---------------------------------------------------------------
-- 6. Distribución de tipos de reseña
---------------------------------------------------------------

SELECT
    dr.review_type,
    COUNT(*) AS total
FROM Fact_Reviews fr
JOIN Dim_ReviewType dr
    ON fr.review_type_id = dr.review_type_id
GROUP BY dr.review_type
ORDER BY total DESC;

---------------------------------------------------------------
-- 7. Distribución de clusters
---------------------------------------------------------------

SELECT
    dc.cluster_theme,
    COUNT(*) AS total
FROM Fact_Reviews fr
JOIN Dim_Cluster dc
    ON fr.cluster_id = dc.cluster_id
GROUP BY dc.cluster_theme
ORDER BY total DESC;

---------------------------------------------------------------
-- 8. Rating promedio por producto
---------------------------------------------------------------

SELECT
    dp.product_name,
    ROUND(AVG(fr.rating),2) AS rating_promedio,
    COUNT(*) AS total_reseñas
FROM Fact_Reviews fr
JOIN Dim_Product dp
    ON fr.product_id = dp.product_id
GROUP BY dp.product_name
ORDER BY rating_promedio DESC;

---------------------------------------------------------------
-- 9. Longitud promedio de reseñas por producto
---------------------------------------------------------------

SELECT
    dp.product_name,
    ROUND(AVG(fr.review_length),2) AS longitud_promedio
FROM Fact_Reviews fr
JOIN Dim_Product dp
    ON fr.product_id = dp.product_id
GROUP BY dp.product_name
ORDER BY longitud_promedio DESC;