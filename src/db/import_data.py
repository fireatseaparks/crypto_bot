import psycopg2
import json
from datetime import datetime

# Database connection parameters
db_params = {
    "host": "localhost",
    "port": "5432",
    "dbname": "opa",
    "user": "postgres",
    "password": "password"
}

# Load JSON data from file
with open("../../sample_data/LINKUSDT_1d.json", "r") as file:
    data = json.load(file)

# Connect to the database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Create the target table "1d" if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS "1d" (
        open_time BIGINT PRIMARY KEY,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume NUMERIC,
        close_time BIGINT,
        quote_asset_volume NUMERIC,
        number_of_trades INTEGER,
        taker_buy_base_asset_volume NUMERIC,
        taker_buy_quote_asset_volume NUMERIC,
        delete SMALLINT
    );
""")
conn.commit()

# Insert JSON data into the table
for record in data:
    cur.execute("""
        INSERT INTO "1d" (open_time, open, high, low, close, volume, close_time,
                          quote_asset_volume, number_of_trades, taker_buy_base_asset_volume,
                          taker_buy_quote_asset_volume, delete)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (open_time) DO NOTHING;
    """, (
        record["open time"],
        float(record["open"]),
        float(record["high"]),
        float(record["low"]),
        float(record["close"]),
        float(record["volume"]),
        record["close time"],
        float(record["quote asset volume"]),
        int(record["number of trades"]),
        float(record["taker buy base asset volume"]),
        float(record["taker buy quote asset volume"]),
        int(record["delete"])
    ))

# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()

print("Data imported successfully!")
