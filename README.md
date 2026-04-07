# 🚀 Options Strategy Backtester

A high-performance intra-day options backtesting engine designed for precision and speed. This system monitors portfolio-level metrics minute-by-minute, enabling sophisticated risk management strategies like automated Stop Loss (SL) triggers.

---

## ✨ Key Features

- **⚡ High-Performance Engine**: Optimized to process ~25 million rows of intra-day data in approximately 11 minutes using advanced indexing and localized filtering.
- **🛡️ Portfolio Stop Loss (SL)**: Built-in functionality to trigger early exits if the combined CE/PE premium drops by 3% (configurable).
- **⏱️ Minute-by-Minute Monitoring**: Strategic exits are evaluated every 60 seconds between entry (09:15) and scheduled exit.
- **📊 Premium Analytics Dashboard**: Interactive Streamlit interface with equity curves, drawdown analysis, and detailed trade history.
- **🗄️ QuestDB Integration**: Uses QuestDB for reliable, fast storage and retrieval of time-series market data.

---

## 🛠️ Project Structure

- `backtest_loop.py`: The core simulation engine with SL monitoring logic.
- `dashboard.py`: Streamlit-based visualization tool for backtest results.
- `data_loader.py`: Handles data retrieval from QuestDB.
- `results_and_metrics.py`: Computes statistical performance indicators (Win Rate, PnL, etc.).
- `config.py`: Management of database credentials and strategy parameters.

---

## 🚀 Getting Started

### 1. Project Setup
Prerequisites: Python 3.8+ and an active QuestDB instance.

```bash
# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
1. Copy `config_example.py` to `config.py`.
2. Update the QuestDB connection details (host, port, user, password).
3. Test the connection:
   ```bash
   python questdb_connection.py
   ```

### 3. Running a Backtest
Execute the main backtest loop to generate results:
```bash
python backtest_loop.py
```
*Results will be saved to `backtest_results.csv` and detailed events logged in `backtest.log`.*

### 4. Launching the Analytics Dashboard
Visualize your strategy's performance with a premium UI:
```bash
streamlit run dashboard.py
```

---

## 📈 Analyzing Results

The system provides multiple layers of feedback:
- **`backtest_results.csv`**: Tabular data for each trade, including entry/exit times, prices, and `exit_reason` (Target vs SL).
- **`backtest.log`**: Detailed execution logs showing minute-by-minute calculations and trigger events.
- **Analytics Dashboard**: Interactive charts to evaluate risk-reward ratios and equity progression.

---

## 📝 Recent Implementation: Portfolio SL
The latest update introduces a 3% portfolio-level stop loss. On volatile days, the system identifies premium drops within minutes of entry, preserving capital by exiting before the scheduled target time.

> [!TIP]
> You can adjust the `STOP_LOSS_PCT` in `backtest_loop.py` to tune the strategy's risk profile.
