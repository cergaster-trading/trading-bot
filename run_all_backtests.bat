@echo off
setlocal

set SYMBOLS=TSLA NVDA PLTR COIN
set CASH=17500

echo Running ensemble backtests for all symbols...
echo.

for %%S in (%SYMBOLS%) do (
    echo 🔄 Running backtest for %%S with $%CASH% starting cash...
    python -m backtest.backtest_daily --symbol %%S --initial-cash %CASH%
    echo --------------------------------------------------------
    echo.
)

echo ✅ All backtests complete.
pause
