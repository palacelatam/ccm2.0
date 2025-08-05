@echo off
echo Starting CCM Backend API in development mode...
echo.
echo Make sure Firebase emulators are running first!
echo.
cd /d "C:\Users\bencl\Proyectos\ccm2.0\backend\src"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload