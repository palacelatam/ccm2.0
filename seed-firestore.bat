@echo off
echo.
echo ========================================
echo  Seeding Firestore Demo Data
echo ========================================
echo.

echo [INFO] Make sure Firebase emulators are running before proceeding!
echo        Run: firebase emulators:start --import=./demo-data --export-on-exit=./demo-data
echo.

set /p confirm="Are Firebase emulators running? (y/N): "

if /i "%confirm%"=="y" (
    echo.
    echo [STEP 1] Getting Firebase Auth UIDs...
    cd scripts
    node get-auth-uids.js
    
    echo.
    echo [STEP 2] Seeding Firestore demo data...
    node seed-demo-data.js
    
    echo.
    echo [INFO] Demo data seeding complete!
    echo [INFO] View data in Emulator UI: http://127.0.0.1:4000/firestore
    
    cd ..
) else (
    echo [INFO] Please start Firebase emulators first, then run this script again.
)

echo.
pause