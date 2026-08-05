import duckdb
from pathlib import Path

# ==========================================================
# Configuración de rutas
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "warehouse" / "reviews.db"

EXPORT_DIR = ROOT_DIR / "dashboard"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Conexión
# ==========================================================

con = duckdb.connect(str(DB_PATH))

tablas = [
    "Dim_Product",
    "Dim_Date",
    "Dim_Sentiment",
    "Dim_ReviewType",
    "Dim_Cluster",
    "Fact_Reviews"
]

print("=" * 60)
print("EXPORTACIÓN PARA POWER BI")
print("=" * 60)

for tabla in tablas:

    archivo = EXPORT_DIR / f"{tabla}.csv"

    df = con.execute(f"SELECT * FROM {tabla}").fetchdf()

    df.to_csv(archivo, index=False, encoding="utf-8-sig")

    print(f"{tabla:<20} -> {len(df)} registros exportados")

print("\nExportación finalizada correctamente.")

con.close()