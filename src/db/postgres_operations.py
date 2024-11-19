from io import StringIO


class PostgresOperations:
    def __init__(self, logger):
        """
        Initialize the PostgresOperations class.

        Args:
            logger: Logger instance for logging.
        """
        self.logger = logger

    def copy_import_candlestick_data(self, connection, df_klines, table_name="candlesticks"):
        """
        Uses PostgreSQL COPY to efficiently load candlestick data from a DataFrame into the database.

        Args:
            connection: psycopg2 database connection object.
            df_klines: Pandas DataFrame containing the candlestick data.
            table_name: Target table name in the database.
        """
        try:
            self.logger.info(f"Start import of {len(df_klines)} rows into {table_name}.")

            # Prepare the DataFrame for COPY by converting it to CSV in memory
            output = StringIO()
            df_klines.to_csv(output, index=False, header=False)  # Exclude index and headers
            output.seek(0)  # Move cursor to the beginning of the StringIO object

            # Execute the COPY command
            with connection.cursor() as cursor:
                cursor.copy_expert(
                    f"""
                    COPY {table_name} (
                        trading_pair_id, timestamp, open_time, open, high, low, close, volume, close_time, number_of_trades
                    ) FROM STDIN WITH CSV;
                    """,
                    output,
                )
            connection.commit()
            self.logger.info(f"Successfully copied {len(df_klines)} rows into {table_name}.")
        except Exception as e:
            self.logger.error(f"Error copying data to PostgreSQL: {e}")
            connection.rollback()

    def get_source_id(self, connection, source_name):
        """
        Fetches the source_id for a given source name.

        Args:
            connection: psycopg2 database connection object.
            source_name: Name of the source (e.g., 'Binance').
        """
        query = "SELECT id FROM sources WHERE name = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (source_name,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    self.logger.warning(f"Source {source_name} not found.")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching source ID: {e}")
            return None

    def get_or_create_trading_pair_id(self, connection, symbol: str, source_name: str,
                                      source_type: str = "exchange") -> int:
        """
        Fetches the trading_pair_id for a given trading pair symbol and source.
        If the trading pair or source does not exist, it will be created.

        Parameters
        ----------
        connection : psycopg2 connection
            Database connection object.
        symbol : str
            Trading pair symbol (e.g., 'BTCUSDT').
        source_name : str
            Name of the source (e.g., 'Binance').
        source_type : str, optional
            Type of the source (default is 'exchange').

        Returns
        -------
        int
            The trading_pair_id for the given symbol and source.
        """
        try:
            # Check if the source exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM sources WHERE name = %s", (source_name,))
                source_result = cursor.fetchone()

                if source_result:
                    source_id = source_result[0]
                else:
                    # Insert the source if it doesn't exist
                    cursor.execute(
                        "INSERT INTO sources (name, type) VALUES (%s, %s) RETURNING id",
                        (source_name, source_type),
                    )
                    source_id = cursor.fetchone()[0]
                    self.logger.info(f"Created new source '{source_name}' with ID {source_id}.")

                # Check if the trading pair exists for the source
                cursor.execute(
                    "SELECT id FROM trading_pairs WHERE symbol = %s AND source_id = %s",
                    (symbol, source_id),
                )
                trading_pair_result = cursor.fetchone()

                if trading_pair_result:
                    trading_pair_id = trading_pair_result[0]
                else:
                    # Insert the trading pair if it doesn't exist
                    cursor.execute(
                        """
                        INSERT INTO trading_pairs (symbol, source_id, type)
                        VALUES (%s, %s, %s) RETURNING id
                        """,
                        (symbol, source_id, "crypto"),
                    )
                    trading_pair_id = cursor.fetchone()[0]
                    self.logger.info(f"Created new trading pair '{symbol}' with ID {trading_pair_id}.")

                connection.commit()
                return trading_pair_id

        except Exception as e:
            self.logger.error(f"Error fetching or creating trading pair '{symbol}': {e}")
            connection.rollback()
            raise

    def get_last_close_time(self, connection, trading_pair_id: int) -> int:
        """
        Fetches the last recorded close time for a trading pair from the database.

        Parameters
        ----------
        connection : psycopg2 connection
            Database connection object.
        trading_pair_id : int
            ID of the trading pair.

        Returns
        -------
        int
            The last recorded close time in milliseconds, or None if no records exist.
        """
        query = """
            SELECT MAX(close_time) AS last_close_time
            FROM candlesticks
            WHERE trading_pair_id = %s;
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (trading_pair_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    self.logger.info(f"Last close time for trading pair {trading_pair_id}: {result[0]}")
                    return result[0]
                else:
                    self.logger.info(f"No candlestick data found for trading pair {trading_pair_id}.")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching last close time for trading pair {trading_pair_id}: {e}")
            raise

