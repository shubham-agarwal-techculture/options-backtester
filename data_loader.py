import pandas as pd
from questdb_connection import options_df, futures_df
from helper import logger

logger.info("Fetching options data...")

try:
    df = options_df
    df = df.sort_values("date")

    # Separate CE & PE
    ce_df = df[df["instrument_type"] == "CE"]
    pe_df = df[df["instrument_type"] == "PE"]

    # print(df.head())

    spot_df = futures_df
    spot_df = spot_df.sort_values("date")

    # print(spot_df.head())
    logger.info(f"Options ce data fetched: {len(ce_df)} rows")
    logger.info(f"Options pe data fetched: {len(pe_df)} rows")
    logger.info(f"Spot data fetched: {len(spot_df)} rows")

except Exception as e:
    logger.error(f"Error fetching options data: {e}")

# Spot data (you must have this)
# spot_df = pd.read_csv("spot.csv", parse_dates=["date"])
# spot_df = spot_df.sort_values("date")