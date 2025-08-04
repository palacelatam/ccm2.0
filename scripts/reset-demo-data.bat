@echo off
echo.
echo ========================================
echo  Reset Demo Data
echo ========================================
echo.

echo [WARNING] This will delete all current demo data!
echo           Make sure Firebase emulators are stopped.
echo.
set /p confirm="Are you sure you want to reset? (y/N): "

if /i "%confirm%"=="y" (
    if exist "demo-data" (
        echo [INFO] Backing up current data before reset...
        call backup-demo-data.bat
        
        echo [INFO] Deleting current demo data...
        rmdir /S /Q "demo-data"
        echo [INFO] Demo data reset complete.
        echo [INFO] Next emulator start will be fresh.
    ) else (
        echo [INFO] No demo data found to reset.
    )
) else (
    echo [INFO] Reset cancelled.
)

echo.
pause