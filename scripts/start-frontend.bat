@echo off
cd /d "%~dp0..\frontend"
set NEXT_PUBLIC_API_URL=http://localhost:8000
if not exist "node_modules" call npm install
echo Starting frontend at http://localhost:3000
call npm run dev
