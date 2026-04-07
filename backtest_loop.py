from data_loader import df, spot_df, ce_df, pe_df
import pandas as pd
from helper import get_atm_strike, get_nearest_expiry, logger


data = pd.merge_asof(
    spot_df.rename(columns={"close": "spot"}),
    df,
    on="date"
)

trades = []

grouped = data.groupby(data["date"].dt.date)

# print(list(grouped))

for day, day_df in grouped:

    logger.info(f"Processing date: {day}")

    entry_time = day_df[day_df["date"].dt.time == pd.to_datetime("09:20").time()]
    exit_time = day_df[day_df["date"].dt.time == pd.to_datetime("15:25").time()]

    if entry_time.empty or exit_time.empty:
        logger.warning(f"No entry/exit data for {day}")
        continue

    entry_row = entry_time.iloc[0]
    exit_row = exit_time.iloc[0]

    spot_price = entry_row["spot"]
    atm = get_atm_strike(spot_price)

    expiries = df["expiry"].unique()
    expiry = get_nearest_expiry(entry_row["date"], expiries)

    # Get CE & PE at entry
    ce_entry = ce_df[
        (ce_df["date"] == entry_row["date"]) &
        (ce_df["strike"] == atm) &
        (ce_df["expiry"] == expiry)
    ]

    pe_entry = pe_df[
        (pe_df["date"] == entry_row["date"]) &
        (pe_df["strike"] == atm) &
        (pe_df["expiry"] == expiry)
    ]

    # Get exit prices
    ce_exit = ce_df[
        (ce_df["date"] == exit_row["date"]) &
        (ce_df["strike"] == atm) &
        (ce_df["expiry"] == expiry)
    ]

    pe_exit = pe_df[
        (pe_df["date"] == exit_row["date"]) &
        (pe_df["strike"] == atm) &
        (pe_df["expiry"] == expiry)
    ]

    if ce_entry.empty or pe_entry.empty or ce_exit.empty or pe_exit.empty:
        logger.warning(f"Missing entry data for {day}, skipping trade")
        continue

    ce_entry_price = ce_entry.iloc[0]["close"]
    pe_entry_price = pe_entry.iloc[0]["close"]

    ce_exit_price = ce_exit.iloc[0]["close"]
    pe_exit_price = pe_exit.iloc[0]["close"]

    lot_size = 1

    pnl = (
        (ce_exit_price - ce_entry_price) +
        (pe_exit_price - pe_entry_price)
    ) * lot_size

    trades.append({
        "date": day,
        "entry_time": entry_row["date"],
        "entry_spot_price": spot_price,
        "atm": atm,
        "expiry": expiry,
        "entry_ce": ce_entry_price,
        "entry_pe": pe_entry_price,
        "exit_time": exit_row["date"],
        "exit_spot_price": exit_row["spot"],
        "exit_ce": ce_exit_price,
        "exit_pe": pe_exit_price,
        "pnl": pnl
    })

    logger.info(f"Entry found at {entry_row['date']} | Spot: {spot_price} | ATM: {atm}")

    logger.info(
    f"TRADE | Date: {day} | ATM: {atm} | "
    f"Entry Time: {entry_row['date']} | Entry Spot: {spot_price} | "
    f"Entry CE: {ce_entry_price} | Entry PE: {pe_entry_price} | "
    f"Exit CE: {ce_exit_price} | Exit PE: {pe_exit_price} | "
    f"Exit time: {exit_row['date']} | Exit Spot: {exit_row['spot']} "
    f"PnL: {pnl}"
    )

if trades:
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv("trades.csv", index=False)
    logger.info(f"Successfully saved {len(trades)} trades to trades.csv")
else:
    logger.warning("No trades were generated, nothing to save.")

# print(trades)