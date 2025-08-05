@echo off
echo.
echo ========================================
echo  Cleaning up all running processes
echo ========================================
echo.

echo [INFO] Stopping Firebase emulators...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9099') do (
    echo Killing process on port 9099: %%a
    taskkill /PID %%a /F > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081') do (
    echo Killing process on port 8081: %%a
    taskkill /PID %%a /F > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :4000') do (
    echo Killing process on port 4000: %%a
    taskkill /PID %%a /F > nul 2>&1
)

echo [INFO] Stopping Node.js processes...
taskkill /F /IM node.exe > nul 2>&1

echo [INFO] Stopping Java processes...
taskkill /F /IM java.exe > nul 2>&1

echo [INFO] Stopping Python processes...
taskkill /F /IM python.exe > nul 2>&1

echo.
echo [INFO] Waiting for processes to fully terminate...
timeout /t 3 > nul

echo.
echo ✅ Cleanup complete! All ports should now be free.
echo.