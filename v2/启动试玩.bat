@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 243 Ways Social

echo Starting 243 Ways Social...
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    pause
    exit /b 1
)

python -m streamlit run app.py

echo.
echo App stopped. Press any key to close.
pause >nul
