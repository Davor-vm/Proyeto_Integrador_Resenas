import duckdb

con = duckdb.connect("data/warehouse/reviews.db")

print("=" * 60)
print("TABLAS DEL DATA WAREHOUSE")
print("=" * 60)

print(con.execute("SHOW TABLES").fetchall())

print("\n")

print("=" * 60)
print("REGISTROS EN FACT_REVIEWS")
print("=" * 60)

print(
    con.execute("""
        SELECT COUNT(*)
        FROM Fact_Reviews
    """).fetchall()
)

print("\n")

print("=" * 60)
print("PRODUCTOS")
print("=" * 60)

print(
    con.execute("""
        SELECT nombre_producto
        FROM Dim_Product
    """).fetchall()
)

con.close()