@echo off
cd /d "%~dp0"

REM Check ngrok tunnels for client demos
echo Checking ngrok tunnels...
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No ngrok tunnels detected - needed for client demos
    echo    To start tunnels: run start-ngrok-tunnels.bat
    echo    Or manually: ngrok http 8000 and ngrok http 3000
) else (
    echo ✅ Ngrok tunnels are running - ready for demos
)
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please create it first with: python -m venv venv
    pause
    exit /b 1
)

REM Authenticate with Google Cloud
REM copying out for now
REM echo Authenticating with Google Cloud...
REM gcloud auth application-default login

cd src
set PYTHONPATH=%cd%
python -m uvicorn main:app --reload