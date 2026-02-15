@echo off
REM Complete System Startup Script for Windows
REM Starts all components in optimized order

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Video Generation System - Complete Startup          ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)
python --version

REM Check Node
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found
    pause
    exit /b 1
)
node --version

REM Install Python dependencies
echo [3/5] Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error installing Python dependencies
    pause
    exit /b 1
)

REM Install frontend dependencies
if not exist "ui\node_modules" (
    echo [4/5] Installing frontend dependencies...
    cd ui
    npm install --silent
    cd ..
) else (
    echo [4/5] Frontend dependencies already installed
)

REM Validation
echo [5/5] Running validation...
python validate_system.py

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  ^✓ System ready! Start services in separate terminals:║
echo ╚════════════════════════════════════════════════════════╝
echo.

echo Terminal 1 (Backend):
echo   python run_all_services.py
echo.

echo Terminal 2 (Frontend):
echo   cd ui ^&^& npm run dev
echo.

echo Terminal 3 (Testing):
echo   python test_api_comprehensive.py
echo.

echo Frontend URL: http://localhost:3000
echo API URL:     http://localhost:8080
echo WebSocket:   ws://localhost:8085
echo.

pause
