"""
Start script for loading and processing historical candlestick data (klines) from Binance.

This script is designed to load candlestick data from Binance based on configurations specified
in two YAML files: `config.yml` and `trading_pairs.yml`. The script fetches data for specified
trading pairs (e.g., BTCUSDT) at specific intervals (e.g., 1 minute, 1 hour) and stores it in
JSON files locally.

The script performs two main operations:
1. **Initial Data Load**: If no previous data exists for a trading pair, it fetches data from
   the specified start date.
2. **Incremental Data Update**: If previous data exists, it continues fetching data from the
   last recorded `close time` to avoid redundant data retrieval.

Configuration Files
-------------------
- **config.yml**: This file contains sensitive information and paths required for the script
  to operate, including:

  - **Binance API credentials** (`api_key` and `api_secret`): These are used to authenticate
    requests to the Binance API. Since these credentials are sensitive, `config.yml` is
    intentionally excluded from version control by adding it to `.gitignore`. You will need
    to create this file manually and populate it with your own Binance API credentials.

  - **Log directory path** (`log/path`): Specifies the local directory where log files will
    be stored. The logger will create this directory (if it doesn't exist) and write logs to
    a rotating log file to track the script's operations.

- **trading_pairs.yml**: This file defines the trading pairs, intervals, and start dates for
  data retrieval. Each entry in this file specifies:

  - **symbol**: The trading pair symbol (e.g., BTCUSDT).
  - **interval**: The time interval for each candlestick (e.g., "1m" for 1 minute).
  - **start_date**: The date from which to start fetching data if no previous data exists.

  The `trading_pairs.yml` file allows you to customize which trading pairs are processed and
  the granularity of the data.

Workflow
--------
1. **Setup**: The script reads `config.yml` to load API credentials and configure the logger.
   It then loads `trading_pairs.yml` to determine the trading pairs and intervals to process.
2. **Data Retrieval**: For each trading pair:
   - If no previous data exists, the script performs an **initial load** from the specified `start_date`.
   - If previous data is found, the script performs an **incremental update** starting from
     the last recorded `close time`. This approach minimizes redundant API requests by only
     fetching new data since the last recorded candlestick.
3. **Logging**: All operations are logged to a file located in the path specified by `log/path`
   in `config.yml`.

Example
-------
To run this script, make sure to create `config.yml` and `trading_pairs.yml` in the same directory.
Then execute:

"""

from pathlib import Path
from binance.client import Client
from binance.helpers import date_to_milliseconds
from typing import List, Dict

from src.helper.logger_config import setup_logger
from src.config.config_loader import load_config
from src.helper.data_processor import load_last_close_time_from_json, save_to_json
from src.data_download.api_handler import get_klines


def load_candlestick_data(client: Client, symbol: str, interval: str, start_date: str) -> List[List]:
    """
    Loads candlestick data from Binance, starting from either the last recorded close time
    or a specified start date, and returns it as a list of OHLCV data lists.

    Parameters
    ----------
    client : binance.Client
        Binance client instance for API interaction.
    symbol : str
        Name of the trading pair, e.g., "BNBBTC".
    interval : str
        Candlestick interval, e.g., "1m" for 1 minute.
    start_date : str
        Date from which to start fetching data if no previous data is recorded.

    Returns
    -------
    List[List]
        List of OHLCV data, where each inner list contains the candlestick data for a single interval.

    Notes
    -----
    - If the last close time is available in the existing JSON data, the function will start loading
      data from the next timestamp. Otherwise, it will start from the given `start_date`.
    - The function logs the start and end of the data loading process.

    Example
    -------
    ```python
    klines = load_candlestick_data(client, "BNBBTC", "1h", "1 Jan, 2021")
    ```
    """
    last_close_time = load_last_close_time_from_json(symbol, interval)
    start_ts = last_close_time + 1 if last_close_time else date_to_milliseconds(start_date)

    if last_close_time:
        logger.info(f"Trying to load new candlestick data from Binance trading pair '{symbol}' with a '{interval}' interval.")
    else:
        logger.info(f"Trying to initial load candlestick data from Binance trading pair '{symbol}' with a '{interval}' interval. Starting from {start_date}")

    klines = get_klines(client, symbol, interval, start_ts)
    logger.info(f"Loaded candlestick data from Binance for '{symbol}' with interval '{interval}' starting at {start_ts}.")
    return klines

def process_trading_pairs(pairs: List[Dict]) -> None:
    """
    Processes each trading pair from the configuration, checks the Binance system status,
    retrieves candlestick data, and saves it to JSON.

    Parameters
    ----------
    pairs : List[Dict]
        List of trading pair configurations with each dictionary containing 'symbol',
        'interval', and 'start_date' keys.

    Returns
    -------
    None

    Notes
    -----
    - The function checks the Binance system status before each data retrieval. If Binance
      is unavailable, it skips the current trading pair.
    - If the data retrieval is successful, it saves the data to a JSON file and logs the process.

    Example
    -------
    ```python
    pairs = [{'symbol': 'BNBBTC', 'interval': '1h', 'start_date': '1 Jan, 2021'}]
    process_trading_pairs(pairs)
    ```
    """
    for pair in pairs:
        symbol = pair['symbol']
        interval = pair['interval']
        start_date = pair['start_date']

        try:
            status = client.get_system_status()
            if status.get('status') == 0:
                klines = load_candlestick_data(client, symbol, interval, start_date)
                save_to_json(klines, symbol, interval)
                logger.info(f"Data for '{symbol}' with interval '{interval}' has been successfully processed.")
            else:
                logger.error(f"Binance is not available. Skipping data load for '{symbol}' with interval '{interval}'.")
        except Exception as e:
            logger.error(f"Error occurred while trying to connect to Binance. ERROR: {e}")

if __name__ == "__main__":
    conf_path = Path(__file__).resolve().parent / "config.yml"
    pairs_conf_path = Path(__file__).resolve().parent / "trading_pairs.yml"

    config = load_config(conf_path)

    log_path = Path(config['log']['path'])
    logger = setup_logger(log_path)

    api_key = config['binance']['api_key']
    api_secret = config['binance']['api_secret']
    client = Client(api_key, api_secret)

    pairs = load_config(pairs_conf_path)

    process_trading_pairs(pairs['trading_pairs'])
