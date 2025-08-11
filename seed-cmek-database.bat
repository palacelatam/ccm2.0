@echo off
echo.
echo ========================================
echo  Seeding CMEK Firestore Database
echo ========================================
echo.

echo [INFO] This will populate your CMEK-enabled Firestore database:
echo        - Project: ccm-dev-pool
echo        - Database: ccm-development
echo        - Location: southamerica-west1
echo        - Encryption: Customer-Managed Keys
echo.

set /p confirm="Continue with CMEK database seeding? (y/N): "

if /i "%confirm%"=="y" (
    echo.
    echo [STEP 1] Setting up environment...
    cd scripts
    
    echo.
    echo [STEP 2] Seeding CMEK Firestore database...
    echo [INFO] This may take 30-60 seconds...
    node seed-cmek-database.js
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo  ✅ CMEK Database Setup Complete!
        echo ========================================
        echo.
        echo 🎯 Database Summary:
        echo   • Project: ccm-dev-pool
        echo   • Database: ccm-development ^(CMEK^)
        echo   • Location: Santiago, Chile
        echo.
        echo 📊 Collections Created:
        echo   • roles ^(3 user roles^)
        echo   • banks ^(1 bank + subcollections^)
        echo   • clients ^(1 client + subcollections^)
        echo   • users ^(3 user profiles^)
        echo   • systemSettings ^(global config^)
        echo.
        echo 🎛️  Client Dashboard Collections:
        echo   • unmatchedTrades ^(2 sample trades^)
        echo   • matchedTrades ^(1 matched trade^)
        echo   • emailMatches ^(1 email confirmation^)
        echo   • dashboardMetadata ^(statistics^)
        echo.
        echo 🌐 View Database:
        echo   Firebase Console: https://console.firebase.google.com/project/ccm-dev-pool/firestore
        echo.
    ) else (
        echo.
        echo ❌ Seeding failed! Check the error messages above.
    )
    
    cd ..
) else (
    echo [INFO] CMEK database seeding cancelled.
)

echo.
pause