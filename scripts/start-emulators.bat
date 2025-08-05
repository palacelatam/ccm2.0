@echo off
echo.
echo ========================================
echo  Firebase Emulators with Persistent Data
echo ========================================
echo.

REM Create demo-data directory if it doesn't exist
if not exist "demo-data" mkdir demo-data

REM Check if demo data exists
if exist "demo-data\auth_export\accounts.json" (
    echo [INFO] Loading existing demo data...
    echo        - Demo users: admin@xyz.cl, usuario@xyz.cl, admin@bancoabc.cl
    echo        - Password for all users: demo123
) else (
    echo [INFO] No existing demo data found. Starting fresh...
)

echo.
echo [INFO] Starting Firebase Emulators...
echo        - Auth Emulator: http://127.0.0.1:9099
echo        - Firestore Emulator: http://127.0.0.1:8081  
echo        - Emulator UI: http://127.0.0.1:4000
echo.
echo [INFO] Data will be automatically saved on exit.
echo        Press Ctrl+C to stop emulators and save data.
echo.

REM Start emulators with data import/export
firebase emulators:start --import=./demo-data --export-on-exit=./demo-data

echo.
echo [INFO] Emulators stopped. Demo data saved to ./demo-data/
echo [INFO] Next time you run this script, your demo users will be restored.