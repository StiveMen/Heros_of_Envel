@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo ==========================================
echo   Сборка Герои Энвелла: Разлом
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Не найден Python Launcher. Установи Python 3.11/3.12 с python.org и включи Add Python to PATH.
  pause
  exit /b 1
)
py -m pip install --upgrade pip
if errorlevel 1 goto failed
py -m pip install -r requirements.txt
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Envel2D game.py
if errorlevel 1 goto failed
echo.
echo Готово! EXE находится в папке dist\Envel2D.exe
pause
exit /b 0
:failed
echo.
echo Сборка завершилась с ошибкой. Проверь интернет и установку Python.
pause
exit /b 1
