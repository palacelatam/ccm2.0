@echo off
echo.
echo ========================================
echo  Switching to Firebase Emulators
echo ========================================
echo.

echo [INFO] Configuring application to use Firebase emulators:
echo        - Project: ccm-dev-pool
echo        - Firestore: localhost:8081
echo        - Auth: localhost:9099
echo.

echo [STEP 1] Updating frontend configuration...
copy /y "frontend\.env.emulator" "frontend\.env.local" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend configured for emulators
) else (
    echo ❌ Failed to update frontend configuration
)

echo.
echo [STEP 2] Updating backend configuration...
copy /y "backend\.env.emulator" "backend\.env" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend configured for emulators
) else (
    echo ❌ Failed to update backend configuration
)

echo.
echo ========================================
echo  ✅ Emulator Configuration Active
echo ========================================
echo.
echo 🔧 Your application is now configured to use:
echo   • Firebase emulators
echo   • Local development data
echo   • Fast iteration/testing
echo.
echo ⚠️  Remember to start emulators first:
echo   firebase emulators:start --import=./demo-data --export-on-exit=./demo-data
echo.
echo 🚀 Then start your applications:
echo   • Frontend: npm start
echo   • Backend: python -m uvicorn main:app --reload
echo.
pause