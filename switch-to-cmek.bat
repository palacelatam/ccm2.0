@echo off
echo.
echo ========================================
echo  Switching to CMEK Database
echo ========================================
echo.

echo [INFO] Configuring application to use CMEK-enabled Firestore database:
echo        - Project: ccm-dev-pool
echo        - Database: ccm-development (CMEK-encrypted)
echo        - Location: southamerica-west1
echo.

echo [STEP 1] Updating frontend configuration...
copy /y "frontend\.env.development" "frontend\.env.local" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend configured for CMEK database
) else (
    echo ❌ Failed to update frontend configuration
)

echo.
echo [STEP 2] Updating backend configuration...
copy /y "backend\.env.development" "backend\.env" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend configured for CMEK database
) else (
    echo ❌ Failed to update backend configuration
)

echo.
echo ========================================
echo  ✅ CMEK Configuration Active
echo ========================================
echo.
echo 🔐 Your application is now configured to use:
echo   • CMEK-encrypted Firestore database
echo   • Persistent data storage
echo   • Production-like security
echo.
echo 🚀 Next steps:
echo   • Frontend: npm start
echo   • Backend: python -m uvicorn main:app --reload
echo.
pause