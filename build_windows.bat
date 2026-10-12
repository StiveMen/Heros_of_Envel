@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   Envel2D Windows build
echo ==========================================
echo.

where py >nul 2>nul
if not errorlevel 1 goto use_py

where python >nul 2>nul
if not errorlevel 1 goto use_python

echo ERROR: Python was not found.
echo Install Python 3.11 or 3.12 from https://www.python.org/downloads/
echo During installation, enable "Add Python to PATH".
pause
exit /b 1

:use_py
py -m pip install --upgrade pip
if errorlevel 1 goto failed
py -m pip install -r requirements.txt
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Envel2D game.py
if errorlevel 1 goto failed
goto success

:use_python
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Envel2D game.py
if errorlevel 1 goto failed
goto success

:success
echo.
echo BUILD SUCCESSFUL.
echo Your game is here: dist\Envel2D.exe
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Read the error messages above.
echo Check your internet connection and Python installation.
pause
exit /b 1
