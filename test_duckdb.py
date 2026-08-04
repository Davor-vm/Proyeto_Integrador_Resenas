import duckdb
con = duckdb.connect("data/warehouse/reviews.db")
print(con.execute("SELECT * FROM Fact_Reviews LIMIT 5").fetchall())
con.close()