@echo off
cd /d "%~dp0..\backend"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
)
call .venv\Scripts\pip.exe install -q -r requirements.txt
set PYTHONPATH=%CD%
if not exist "data" mkdir data
if not defined INGESTION_URL set INGESTION_URL=http://localhost:8000/logs
echo.
echo Starting backend at http://127.0.0.1:8000
echo Loads settings from repo root .env (copy .env.example; set DATABASE_URL for MySQL)
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --port 8000
