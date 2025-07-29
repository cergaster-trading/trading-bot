@echo off
cd /d "C:\Users\chris\Documents\alpaca_bot"
echo Starting ensemble optimization...

python backtest\optimize_ensemble.py --symbol TSLA --trials 25
python backtest\optimize_ensemble.py --symbol NVDA --trials 25
python backtest\optimize_ensemble.py --symbol COIN --trials 25
python backtest\optimize_ensemble.py --symbol PLTR --trials 25

echo Optimization complete.
pause
