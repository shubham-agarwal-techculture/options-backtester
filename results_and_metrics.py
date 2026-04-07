from backtest_loop import trades
import pandas as pd
from helper import logger

trades_df = pd.DataFrame(trades)

total_pnl = trades_df["pnl"].sum()
win_rate = (trades_df["pnl"] > 0).mean()

print("Total PnL:", total_pnl)
print("Win Rate:", win_rate)

logger.info("Backtest completed")

logger.info(f"Total Trades: {len(trades_df)}")
logger.info(f"Total PnL: {total_pnl}")
logger.info(f"Win Rate: {win_rate:.2f}")