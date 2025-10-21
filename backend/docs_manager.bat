@echo off
REM ============================================
REM CCM 2.0 Documentation Manager
REM ============================================

setlocal enabledelayedexpansion

:MENU
cls
echo.
echo ========================================================
echo           CCM 2.0 Documentation Manager
echo ========================================================
echo.
echo   1. Launch Documentation Server (port 8002)
echo   2. Build Static Documentation
echo   3. Check Docstring Coverage
echo   4. Analyze ClientService Docstrings
echo   5. Install/Update Documentation Dependencies
echo   6. Open Documentation in Browser
echo   7. Exit
echo.
echo ========================================================
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto LAUNCH
if "%choice%"=="2" goto BUILD
if "%choice%"=="3" goto COVERAGE
if "%choice%"=="4" goto ANALYZE
if "%choice%"=="5" goto INSTALL
if "%choice%"=="6" goto BROWSER
if "%choice%"=="7" goto END

echo Invalid choice. Please try again.
pause
goto MENU

:LAUNCH
cls
echo.
echo Starting documentation server on port 8002...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if MkDocs is installed
python -c "import mkdocs" 2>nul
if errorlevel 1 (
    echo Installing MkDocs...
    pip install -r requirements.txt
)

echo.
echo ====================================================
echo   Documentation available at: http://localhost:8002
echo   Press Ctrl+C to stop the server
echo ====================================================
echo.

mkdocs serve --dev-addr 127.0.0.1:8002

echo.
echo Server stopped.
pause
goto MENU

:BUILD
cls
echo.
echo Building static documentation...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Build documentation
mkdocs build --clean

echo.
echo ====================================================
echo   Documentation built successfully!
echo   Output location: site/
echo ====================================================
echo.
pause
goto MENU

:COVERAGE
cls
echo.
echo Checking docstring coverage...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if interrogate is installed
python -c "import interrogate" 2>nul
if errorlevel 1 (
    echo Installing interrogate...
    pip install interrogate
)

echo.
echo ====================================================
echo         Docstring Coverage Report
echo ====================================================
echo.

REM Run interrogate on source code
interrogate -v src/ --exclude "*/test_*.py" --fail-under 0

echo.
echo ====================================================
pause
goto MENU

:ANALYZE
cls
echo.
echo Analyzing ClientService docstrings...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if the analysis script exists
if exist "improve_docstrings.py" (
    python improve_docstrings.py
) else (
    echo.
    echo Analysis script not found!
    echo Running basic analysis...
    echo.

    REM Basic analysis with interrogate
    interrogate -v src/services/client_service.py --fail-under 0
)

echo.
pause
goto MENU

:INSTALL
cls
echo.
echo Installing/Updating documentation dependencies...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing documentation packages...
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-autorefs
pip install pymdown-extensions mkdocs-git-revision-date-localized-plugin
pip install interrogate pydocstyle black mike

echo.
echo ====================================================
echo   Documentation dependencies installed successfully!
echo ====================================================
echo.
pause
goto MENU

:BROWSER
cls
echo.
echo Opening documentation in browser...
echo.

REM Check if documentation is running
curl -s -o nul -w "%%{http_code}" http://localhost:8002 | findstr /C:"200" >nul
if errorlevel 1 (
    echo Documentation server is not running!
    echo Please start the server first (Option 1).
    pause
    goto MENU
)

REM Open in default browser
start http://localhost:8002

echo Browser launched!
timeout /t 2 >nul
goto MENU

:END
echo.
echo Thank you for using CCM Documentation Manager!
echo.
exit /b 0