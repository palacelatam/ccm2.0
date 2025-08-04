@echo off
echo Exporting current emulator data...

REM Export current emulator state
firebase emulators:export ./demo-data --force

echo Demo data exported to ./demo-data/
echo You can now commit this data to Git for team sharing.