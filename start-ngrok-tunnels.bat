@echo off
setlocal enabledelayedexpansion
color 0B

echo.
echo ========================================
echo   Starting Ngrok Tunnels for CCM2.0
echo ========================================
echo.

:: Check if ngrok is installed
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: ngrok is not installed or not in PATH
    echo Please see ngrok.md for installation instructions.
    pause
    exit /b 1
)

:: Check if tunnels are already running
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Ngrok tunnels may already be running.
    echo    Check http://localhost:4040 for active tunnels.
    echo.
    choice /c YN /m "Continue anyway (Y/N)"
    if errorlevel 2 exit /b 0
)

echo Starting ngrok tunnels...
echo.
echo This will open two command windows:
echo   1. Backend tunnel (port 8000)
echo   2. Frontend tunnel (port 3000)  
echo.
echo ⚠️  Keep both windows open during your demo!
echo ⚠️  Access ngrok dashboard at: http://localhost:4040
echo.

pause

:: Start backend tunnel in new window
echo Starting backend tunnel...
start "CCM2.0 Backend Tunnel" cmd /k "echo Backend API Tunnel (Port 8000) && echo. && ngrok http 8000 --log=stdout"

:: Wait a moment for first tunnel to initialize
timeout /t 3 /nobreak >nul

:: Start frontend tunnel in new window  
echo Starting frontend tunnel...
start "CCM2.0 Frontend Tunnel" cmd /k "echo Frontend Tunnel (Port 3000) && echo. && ngrok http 3000 --log=stdout"

:: Wait for tunnels to initialize
echo.
echo Waiting for tunnels to initialize...
timeout /t 5 /nobreak >nul

:: Try to display tunnel URLs
echo.
echo ========================================
echo   Tunnel Status
echo ========================================
echo.

curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Cannot connect to ngrok dashboard yet.
    echo    Wait a moment and check http://localhost:4040
) else (
    echo ✅ Ngrok dashboard accessible at: http://localhost:4040
    echo.
    echo Your tunnel URLs will appear shortly at:
    echo   http://localhost:4040
)

echo.
echo ========================================
echo   Demo Preparation Complete
echo ========================================
echo.
echo Next steps for client demo:
echo   1. Ensure backend server is running (localhost:8000)
echo   2. Ensure frontend server is running (localhost:3000)  
echo   3. Test your application via the ngrok HTTPS URLs
echo   4. Share the ngrok URLs with your client
echo.
echo Important:
echo   - Keep ngrok terminal windows open during demo
echo   - Monitor requests at http://localhost:4040
echo   - Close tunnels after demo for security
echo.

pause