@echo off
cd /d "%~dp0"

echo Starting Blackwater Ledger...
python desktop_app.py

if errorlevel 1 (
    echo.
    echo Something went wrong starting the app - see the error above.
    pause
)
