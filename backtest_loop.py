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

STOP_LOSS_PCT = 0.02  # 3% Stop Loss
ENTRY_TIME_STR = "09:15"
EXIT_TIME_STR = "09:25"

# Set indices for high-performance lookups
ce_df = ce_df.set_index("date").sort_index()
pe_df = pe_df.set_index("date").sort_index()

# trading loop 
for day, day_df in grouped:

    logger.info(f"Processing date: {day}")

    # 1. Find Entry data
    entry_time = pd.to_datetime(f"{day} {ENTRY_TIME_STR}")
    
    try:
        # Check if entry time exists in spot data
        entry_records = day_df[day_df["date"] == entry_time]
        if entry_records.empty:
            logger.warning(f"No entry data at {ENTRY_TIME_STR} for {day}")
            continue

        entry_row = entry_records.iloc[0]
        spot_price = entry_row["spot"]
        atm = get_atm_strike(spot_price)

        expiries = df["expiry"].unique()
        expiry = get_nearest_expiry(entry_row["date"], expiries)

        ce_strike = atm + 100
        pe_strike = atm - 100

        # Get CE & PE at entry using indexed lookup
        ce_entry_price = ce_df.loc[
            (ce_df.index == entry_time) & (ce_df["strike"] == ce_strike) & (ce_df["expiry"] == expiry), 
            "close"
        ]
        pe_entry_price = pe_df.loc[
            (pe_df.index == entry_time) & (pe_df["strike"] == pe_strike) & (pe_df["expiry"] == expiry), 
            "close"
        ]

        if ce_entry_price.empty or pe_entry_price.empty:
            logger.warning(f"Missing entry prices for {day} | Strike CE: {ce_strike}, PE: {pe_strike}")
            continue

        ce_entry_val = ce_entry_price.iloc[0]
        pe_entry_val = pe_entry_price.iloc[0]
        total_entry_premium = ce_entry_val + pe_entry_val

        # 2. OPTIMIZATION: Get all bars for the trade window for these specific strikes using fast indexing
        # Filter by index (date) first, then by columns
        ce_day_data = ce_df.loc[str(day)]
        ce_day_data = ce_day_data[
            (ce_day_data["strike"] == ce_strike) & (ce_day_data["expiry"] == expiry)
        ][["close"]].rename(columns={"close": "ce_close"})

        pe_day_data = pe_df.loc[str(day)]
        pe_day_data = pe_day_data[
            (pe_day_data["strike"] == pe_strike) & (pe_day_data["expiry"] == expiry)
        ][["close"]].rename(columns={"close": "pe_close"})

        # Identify trade period bars
        trade_period_df = day_df[
            (day_df["date"].dt.time >= pd.to_datetime(ENTRY_TIME_STR).time()) &
            (day_df["date"].dt.time <= pd.to_datetime(EXIT_TIME_STR).time())
        ].sort_values("date")

        # Merge local day data
        trade_period_df = pd.merge(trade_period_df, ce_day_data, left_on="date", right_index=True, how="left")
        trade_period_df = pd.merge(trade_period_df, pe_day_data, left_on="date", right_index=True, how="left")

        exit_row = None
        exit_ce_price = None
        exit_pe_price = None
        exit_reason = "Target"

        for _, bar in trade_period_df.iterrows():
            if pd.isna(bar["ce_close"]) or pd.isna(bar["pe_close"]):
                continue

            curr_ce_price = bar["ce_close"]
            curr_pe_price = bar["pe_close"]
            total_curr_premium = curr_ce_price + curr_pe_price
            
            # Calculate PnL %
            pnl_pct = (total_curr_premium - total_entry_premium) / total_entry_premium

            # Check Stop Loss
            if pnl_pct <= -STOP_LOSS_PCT:
                exit_row = bar
                exit_ce_price = curr_ce_price
                exit_pe_price = curr_pe_price
                exit_reason = "SL"
                logger.info(f"SL HIT at {bar['date']} | PnL%: {pnl_pct:.2%}")
                break
            
            # Default exit at target time
            if bar["date"].time() == pd.to_datetime(EXIT_TIME_STR).time():
                exit_row = bar
                exit_ce_price = curr_ce_price
                exit_pe_price = curr_pe_price
                exit_reason = "Target"

        if exit_row is None:
            logger.warning(f"Could not find exit data for {day}")
            continue

        lot_size = 1
        pnl = ((exit_ce_price - ce_entry_val) + (exit_pe_price - pe_entry_val)) * lot_size

        trades.append({
            "date": day,
            "entry_time": entry_row["date"],
            "spot_price": spot_price,
            "atm": atm,
            "ce_strike": ce_strike,
            "pe_strike": pe_strike,
            "expiry": expiry,
            "entry_ce": ce_entry_val,
            "entry_pe": pe_entry_val,
            "exit_time": exit_row["date"],
            "exit_spot_price": exit_row["spot"],
            "exit_ce": exit_ce_price,
            "exit_pe": exit_pe_price,
            "exit_reason": exit_reason,
            "pnl": pnl
        })

        logger.info(f"Entry: {entry_row['date']} ({total_entry_premium:.2f}) | Exit: {exit_row['date']} ({exit_ce_price + exit_pe_price:.2f}) | Reason: {exit_reason} | PnL: {pnl:.2f}")

    except Exception as e:
        logger.error(f"Error processing {day}: {e}")
        continue

if trades:
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv("backtest_results.csv", index=False)
    logger.info(f"Backtest completed. {len(trades)} trades saved to backtest_results.csv")
else:
    logger.warning("No trades were generated during the backtest.")

# print(trades)