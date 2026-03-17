@echo off
REM GUI Sublist3r - Windows launcher
REM Double-click this file to open the GUI.

cd /d "%~dp0"

REM Try 'python' first, then 'python3', then 'py'
where python >nul 2>&1
if %errorlevel%==0 (
    python gui_sublist3r.py
    goto end
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    python3 gui_sublist3r.py
    goto end
)

where py >nul 2>&1
if %errorlevel%==0 (
    py gui_sublist3r.py
    goto end
)

echo Python not found. Please install Python 3 from https://www.python.org/
pause
:end
