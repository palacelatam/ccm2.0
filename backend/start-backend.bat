@echo off
cd /d "%~dp0\src"
set PYTHONPATH=%cd%
python -m uvicorn main:app --reload