import duckdb

DB_PATH = "data/warehouse/reviews.db"

con = duckdb.connect(DB_PATH)

print("=" * 70)
print("VALIDACIÓN DEL DATA WAREHOUSE")
print("=" * 70)

# ---------------------------------------------------
# TABLAS
# ---------------------------------------------------
print("\n[1] Tablas creadas:\n")

tablas = con.execute("SHOW TABLES").fetchall()

for tabla in tablas:
    print(f"- {tabla[0]}")

# ---------------------------------------------------
# REGISTROS
# ---------------------------------------------------
print("\n[2] Número de registros por tabla:\n")

consultas = {
    "Dim_Product": "SELECT COUNT(*) FROM Dim_Product",
    "Dim_Date": "SELECT COUNT(*) FROM Dim_Date",
    "Dim_Sentiment": "SELECT COUNT(*) FROM Dim_Sentiment",
    "Dim_ReviewType": "SELECT COUNT(*) FROM Dim_ReviewType",
    "Dim_Cluster": "SELECT COUNT(*) FROM Dim_Cluster",
    "Fact_Reviews": "SELECT COUNT(*) FROM Fact_Reviews"
}

for nombre, consulta in consultas.items():
    total = con.execute(consulta).fetchone()[0]
    print(f"{nombre:<20}: {total}")

# ---------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------
print("\n[3] Productos cargados:\n")

productos = con.execute("""
SELECT product_name
FROM Dim_Product
""").fetchall()

for producto in productos:
    print(f"- {producto[0]}")

# ---------------------------------------------------
# RATING PROMEDIO
# ---------------------------------------------------
print("\n[4] Rating promedio por producto:\n")

resultado = con.execute("""
SELECT
    dp.product_name,
    ROUND(AVG(fr.rating),2) AS promedio
FROM Fact_Reviews fr
JOIN Dim_Product dp
ON fr.product_id = dp.product_id
GROUP BY dp.product_name
ORDER BY promedio DESC
""").fetchall()

for fila in resultado:
    print(f"{fila[0]} -> {fila[1]}")

print("\nVALIDACIÓN FINALIZADA CORRECTAMENTE")

con.close()