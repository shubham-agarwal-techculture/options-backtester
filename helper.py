import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(f"./backtest.log"),
        logging.StreamHandler()  # prints to console
    ]
)

logger = logging.getLogger(__name__)


def get_atm_strike(spot_price, step=50):
    return round(spot_price / step) * step

def get_nearest_expiry(current_date, expiries):
    future_expiries = [e for e in expiries if e >= current_date]
    return min(future_expiries) if future_expiries else None

