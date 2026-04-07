# options-backtester
simple back testing the option strategy 


# 1. Project Setup
- Create a virtual environment: python -m venv .venv
- Activate it: .venv\Scripts\activate
- Install dependencies: pip install -r requirements.txt

# 2. Database Connection
- Copy config_example.py to config.py
- Fill in your QuestDB connection details
- Run: python questdb_connection.py

# 3. Backtest Execution
- Run: python backtest_loop.py

# 4. Results
- Check backtest.log for logs
- Run: python results_and_metrics.py to see PnL and win rate

