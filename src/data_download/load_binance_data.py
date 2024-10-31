import json
import time
import yaml
import pandas as pd
from pathlib import Path
from binance.helpers import interval_to_milliseconds, date_to_milliseconds
from binance.client import Client

from src.helper.logger_config import setup_logger


def get_klines(symbol, interval, start_ts):
    """
    This is copy pasted get_historical_klines from the python-binance package to make small changes. 
    Aim is to make the old code work with milliseconds to append already fetched data.
    
    FROM: Get Historical Klines from Binance

    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date in milliseconds format
    :type start_str: int

    :return: list of OHLCV values
    """
    
    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts
        )
    
        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)
    return output_data


def load_last_close_time(symbol, interval):
    file_path = Path(f"{symbol}_{interval}.json")
    if file_path.exists():
        with open(file_path, "r") as file:
            data = json.load(file)
            if data:
                last_close_time = data[-1]['close time'] 
                return last_close_time
    return None


def load_candlestick_data(symbol, interval, start_date):
    last_close_time = load_last_close_time(symbol, interval)
    if last_close_time:
        start_ts = last_close_time + 1
        logger.info(f"Trying to load new candlestick data from Binance trading pair '{symbol}' with a '{interval}' interval. Data starts at {start_date}")
    else:
        start_ts = date_to_milliseconds(start_date)
        logger.info(f"Trying to initiale load candlestick data from Binance trading pair '{symbol}' with a '{interval}' interval. Data starts at {start_date}")
    
    klines = get_klines(symbol, interval, start_ts)
    logger.info(f"Loaded candlestick data from Binance trading pair '{symbol}' with a '{interval}' interval. Data starts at {start_ts}")
    return klines


def load_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


if __name__ == "__main__":
    conf_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    pairs_conf_path = Path(__file__).Path(__file__).resolve().parent.parent.parent / "trading_pairs.yaml"
    
    config = load_config(conf_path)
    log_path = config['log']['path']
    logger = setup_logger()

    api_key = config['binance']['api_key']
    api_secret = config['binance']['api_secret']
    client = Client(api_key, api_secret)

    pairs = load_config(pairs_conf_path)
    
    for pair in pairs['trading_pairs']:
        symbol = pair['symbol']
        interval = pair['interval']
        start_date = pair['start_date']

        try:
            status = client.get_system_status()
        except Exception as e:
            logger.error(f"Error occured while trying to connect to Binance. ERROR: {e}")
            
        if status.get('status') == 0:
            klines = load_candlestick_data(symbol, interval, start_date)
        else:
            logger.error(f"Could not load data from Binance for trading pair '{symbol}' with a '{interval}' interval.")

        columns = [
            'open time', 
            'open', 
            'high', 
            'low', 
            'close', 
            'volume', 
            'close time', 
            'quote asset volume', 
            'number of trades', 
            'taker buy base asset volume', 
            'taker buy quote asset volume', 
            "delete" 
        ]

        df = pd.DataFrame(klines, columns=columns)

        out_json = f"{symbol}_{interval}.json"
        df.to_json(out_json, orient="records", date_format="iso")