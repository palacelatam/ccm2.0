@echo off
REM ============================================
REM CCM 2.0 Backend Documentation Launcher (Clean)
REM Suppresses warnings for a cleaner output
REM ============================================

echo.
echo ====================================================
echo         CCM 2.0 Backend Documentation
echo ====================================================
echo.

REM Check if we're in the backend directory
if not exist "mkdocs.yml" (
    echo ERROR: mkdocs.yml not found!
    echo Please run this script from the backend directory.
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if MkDocs is installed
python -c "import mkdocs" 2>nul
if errorlevel 1 (
    echo.
    echo MkDocs not found. Installing documentation dependencies...
    echo This may take a few minutes on first run...
    echo.
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt >nul 2>&1
    echo.
    echo Documentation dependencies installed successfully!
    echo.
)

REM Start MkDocs server with warning suppression
echo.
echo Starting documentation server on port 8002...
echo.
echo ====================================================
echo.
echo   Documentation will be available at:
echo   http://localhost:8002
echo.
echo   Press Ctrl+C to stop the server
echo.
echo ====================================================
echo.
echo Note: Some warnings about missing files are expected
echo as the documentation is still being developed.
echo.

REM Set environment variable to suppress Pydantic warnings
set PYTHONWARNINGS=ignore::DeprecationWarning

REM Launch MkDocs with cleaner output (warnings go to nul)
mkdocs serve --dev-addr 127.0.0.1:8002 2>&1 | findstr /V "WARNING"

REM When user stops the server
echo.
echo Documentation server stopped.
echo.
pause