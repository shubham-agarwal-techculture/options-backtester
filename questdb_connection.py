import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from helper import logger
from config  import url

try: 
    
    engine = create_engine(url)


    query_options = """
    SELECT
        date,
        expiry,
        strike,
        instrument_type,
        close,
        volume,
        oi
    FROM nfo_nifty_options   
    WHERE date BETWEEN '2025-01-01T09:15:00.000000Z' and '2026-01-31T15:25:00.000000Z'
    """

    query_future = """
    SELECT date, close FROM nfo_nifty_futures 
    WHERE date BETWEEN '2025-01-01T09:15:00.000000Z' and '2026-01-31T15:25:00.000000Z'
    """

    options_df = pd.read_sql(query_options, engine)
    futures_df = pd.read_sql(query_future, engine)
    print(options_df.head())
    print(futures_df.head())

    logger.info("Connected to QuestDB successfully")

except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise

