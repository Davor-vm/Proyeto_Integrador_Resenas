import duckdb

conexion = duckdb.connect("data/warehouse/reviews.db")

conexion.execute("""
CREATE TABLE IF NOT EXISTS prueba(
    id INTEGER,
    nombre VARCHAR
)
""")

conexion.execute("""
INSERT INTO prueba VALUES
(1,'Jonathan'),
(2,'Proyecto')
""")

resultado = conexion.execute("SELECT * FROM prueba").fetchall()

print(resultado)

conexion.close()