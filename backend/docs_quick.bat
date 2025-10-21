@echo off
REM Quick launcher for documentation - no checks, just run

echo Starting CCM 2.0 Documentation on http://localhost:8002
echo Press Ctrl+C to stop...
echo.

call venv\Scripts\activate.bat 2>nul
mkdocs serve --dev-addr 127.0.0.1:8002