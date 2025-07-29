# trading_metrics.py
from prometheus_client import Counter, Gauge, Summary

METRIC_PNL            = Gauge('bot_portfolio_value', 'Current portfolio value in USD')
METRIC_DRAWDOWN       = Gauge('bot_drawdown_percent', 'Current drawdown percent')
METRIC_ERRORS         = Counter('bot_api_errors_total', 'Total number of API errors')
METRIC_OPEN_POSITIONS = Gauge('bot_open_positions', 'Number of open positions')
METRIC_TRADES         = Counter('bot_trades_total', 'Total number of executed trades')
METRIC_SLIPPAGE       = Summary('bot_slippage_per_share', 'Realized slippage per share')
