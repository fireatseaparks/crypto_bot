from fastapi import FastAPI, HTTPException
from pathlib import Path

from src.config.config_loader import load_config
from src.db.database_handler import connect_to_database
from src.db.postgres_operations import PostgresOperations
from src.helper.interval import search_suitable_interval


api = FastAPI(openapi_tags=[
    {
        'name': 'home',
        'description': 'Basic functionality of API'
    },
    {
        'name': 'candlestick',
        'description': 'Candlestick Data. Open, High, Low, Close, Volume'
    }
])


@api.get('/check', tags=['home'])
def check_availability():
    """Check if the app is running."""
    return {"data": "success"}


@api.get("/candlesticks/{symbol}/{target_interval}", tags=['candlestick'])
def get_candlesticks(symbol: str, target_interval: str):
    psql_ops = PostgresOperations()

    conf_path = Path(__file__).resolve().parent / "config.yml"
    config = load_config(conf_path)
    conn = connect_to_database(config['postgres'])
    available_intervals = psql_ops.get_available_intervals_for_trading_pair(conn, symbol)

    chosen_interval = search_suitable_interval(available_intervals=available_intervals,
                                                target_interval=target_interval)

    data = psql_ops.get_candlestick_data(conn, symbol, target_interval, chosen_interval)

    return data
