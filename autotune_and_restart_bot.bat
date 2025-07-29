@echo off
cd /d "C:\Users\chris\Documents\alpaca_bot"

:: Step 1 – Run Auto-Tuning
"C:\Users\chris\AppData\Local\Programs\Python\Python310\python.exe" -m tools.daily_autotune

:: Step 2 – Kill Existing Bot
taskkill /f /im python.exe /fi "WINDOWTITLE eq trading_bot.py*" > nul 2>&1

:: Optional pause between kill and restart
timeout /t 5 > nul

:: Step 3 – Start Bot Fresh
start "trading_bot.py" /min "C:\Users\chris\AppData\Local\Programs\Python\Python310\python.exe" trading_bot.py
