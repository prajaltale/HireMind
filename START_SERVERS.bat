@echo off
REM ===================================================
REM HireMind - Startup Script
REM Starts both FastAPI and Django servers
REM ===================================================

cd /d "e:\Cusrsor\Hire MInd"

echo.
echo ╔════════════════════════════════════════════════╗
echo ║      HireMind Application Startup              ║
echo ╚════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI Server (Port 8000)...
echo       Application URL: http://localhost:8000
echo       Restart: Auto-reload enabled
start cmd /k "E:/Cusrsor/.venv/Scripts/python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak

echo.
echo [2/2] Starting Django Admin Panel (Port 8001)...
echo       Admin URL: http://localhost:8001/admin/
echo       Username: admin
echo       Password: admin123
start cmd /k "E:/Cusrsor/.venv/Scripts/python.exe manage.py runserver 8001"

echo.
echo ╔════════════════════════════════════════════════╗
echo ║      ✓ Both servers starting...                ║
echo ║                                                ║
echo ║  FastAPI:     http://localhost:8000           ║
echo ║  Django Admin: http://localhost:8001/admin/   ║
echo ║                                                ║
echo ║  Press Ctrl+C in each window to stop          ║
echo ╚════════════════════════════════════════════════╝
echo.

pause
