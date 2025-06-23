import duckdb

db = duckdb.connect('twitter_data.db')

db.execute("select * from tweets")

