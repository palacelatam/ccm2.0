@echo off
echo.
echo ========================================
echo  Backup Demo Data
echo ========================================
echo.

REM Create timestamp for backup
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

REM Create backups directory
if not exist "backups" mkdir backups

REM Backup current demo data
if exist "demo-data" (
    echo [INFO] Creating backup: backups\demo-data-%timestamp%
    xcopy /E /I /Q "demo-data" "backups\demo-data-%timestamp%"
    echo [INFO] Backup complete!
    echo.
    echo [INFO] Available backups:
    dir /B "backups\demo-data-*" 2>nul
) else (
    echo [ERROR] No demo-data directory found to backup.
)

echo.
pause