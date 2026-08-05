import duckdb

con = duckdb.connect("data/warehouse/reviews.db")

consulta = """
SELECT
    fr.review_id,
    dp.product_name,
    ds.sentiment,
    dr.review_type,
    dc.cluster_theme,
    fr.rating
FROM Fact_Reviews fr
JOIN Dim_Product dp
ON fr.product_id = dp.product_id

JOIN Dim_Sentiment ds
ON fr.sentiment_id = ds.sentiment_id

JOIN Dim_ReviewType dr
ON fr.review_type_id = dr.review_type_id

JOIN Dim_Cluster dc
ON fr.cluster_id = dc.cluster_id

LIMIT 15;
"""

resultado = con.execute(consulta).fetchdf()

print(resultado)

con.close()