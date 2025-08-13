@echo off
cd /d "%~dp0"

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
echo Authenticating with Google Cloud...
gcloud auth application-default login

cd src
set PYTHONPATH=%cd%
python -m uvicorn main:app --reload