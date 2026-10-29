@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title 243 Ways Social - v2

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    echo Python 3.10 or newer was not found.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the local Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

if not exist ".venv\Scripts\streamlit.exe" (
    echo Installing dependencies. This is only needed on the first run...
    ".venv\Scripts\python.exe" -m pip install -r v2\requirements.txt
    if errorlevel 1 goto :error
)

echo Starting v2 at http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run v2\app.py
goto :end

:error
echo.
echo Startup failed. Review the message above and try again.
pause

:end
endlocal
