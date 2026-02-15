@echo off
REM Quick start script for the video generation service (Windows)

setlocal enabledelayedexpansion

echo.
echo ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! 
echo ^^! Text-to-Video Generation Service - Quick Start
echo ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! ^! 
echo.

REM Check prerequisites
echo Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Docker Compose is not installed. Please install Docker Desktop.
    exit /b 1
)

echo [OK] Docker and Docker Compose found
echo.

REM Setup .env file
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please edit .env and add your PEXELS_API_KEY
    echo          Then run this script again.
    exit /b 0
)

REM Start services
echo [*] Starting services...
docker-compose up --build -d

echo.
echo [*] Waiting for services to be ready...
timeout /t 10 /nobreak

REM Check health
echo.
echo [*] Checking service health...

setlocal enabledelayedexpansion
for /L %%i in (1,1,30) do (
    powershell -Command "try { $resp = Invoke-WebRequest -Uri 'http://localhost:8080/health' -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo [OK] API is responding
        goto :services_ready
    )
    if %%i EQU 30 (
        echo X API did not become healthy in time
        echo   Check logs with: docker-compose logs -f api
        exit /b 1
    )
    echo     Attempt %%i/30...
    timeout /t 1 /nobreak > nul
)

:services_ready
echo.
echo [OK] All services are running!
echo.
echo Services available at:
echo   API Server:     http://localhost:8080
echo   MinIO Console:  http://localhost:9001
echo   Redis:          localhost:6379
echo.
echo Quick test:
echo   - Generate video:  curl -X POST http://localhost:8080/mcp/generate -H "Content-Type: application/json" -d "{"prompt": "A sunset over the ocean", "duration_target": 30}"
echo   - Check status:    curl http://localhost:8080/mcp/status/{job_id}
echo.
echo Documentation:
echo   Getting Started: docs\GETTING_STARTED.md
echo   Architecture:    docs\ARCHITECTURE.md
echo.
echo View logs:
echo   docker-compose logs -f api
echo.
echo Stop services:
echo   docker-compose down
echo.
