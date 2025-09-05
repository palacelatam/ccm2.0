@echo off
cd /d "%~dp0"

REM Check ngrok tunnels for client demos and set CLOUD_RUN_URL for Cloud Tasks
echo Checking ngrok tunnels...
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No ngrok tunnels detected - needed for client demos and Cloud Tasks
    echo    To start tunnels: run start-ngrok-tunnels.bat
    echo    Or manually: ngrok http 8000 and ngrok http 3000
    echo    Warning: Cloud Tasks will use localhost:8000 without ngrok
    set CLOUD_RUN_URL=http://localhost:8000
) else (
    echo ✅ Ngrok tunnels are running - detecting backend URL for Cloud Tasks...
    
    REM Get ngrok tunnel URL for port 8000 and set CLOUD_RUN_URL
    for /f "tokens=*" %%i in ('curl -s http://localhost:4040/api/tunnels ^| python -c "import sys, json; data=json.load(sys.stdin); tunnels=[t for t in data.get('tunnels', []) if t.get('config', {}).get('addr') == 'http://localhost:8000']; print(tunnels[0]['public_url'] if tunnels and tunnels[0].get('public_url', '').startswith('https://') else 'http://localhost:8000')"') do (
        set CLOUD_RUN_URL=%%i
    )
    
    if "%CLOUD_RUN_URL%"=="http://localhost:8000" (
        echo ⚠️  Could not detect ngrok HTTPS URL for port 8000
        echo    Using fallback: http://localhost:8000
    ) else (
        echo ✅ Cloud Tasks will use: %CLOUD_RUN_URL%
    )
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

REM Display Cloud Tasks configuration
echo.
echo 🌐 Cloud Tasks Configuration:
echo    CLOUD_RUN_URL: %CLOUD_RUN_URL%
echo.
echo Starting FastAPI server...

python -m uvicorn main:app --reload