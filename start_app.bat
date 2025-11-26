@echo off
echo Starting AI Loan Document Intelligence System...

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Starting Flask API...
start "Flask API" cmd /k "python -m src.api.app"

echo Waiting for API to initialize...
timeout /t 5

echo Starting Streamlit UI...
start "Streamlit UI" cmd /k "streamlit run src/ui/app.py"

echo System Started!
echo API: http://localhost:5000
echo UI: http://localhost:8501
