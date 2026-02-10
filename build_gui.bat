@echo off
echo Installing Dependencies...
pip install -r requirements.txt

echo.
echo.
echo Building Process Manager Elite...
:: --noconsole: Hide terminal
:: --collect-all customtkinter: Include CTK theme files
:: --icon: Set exe icon
:: --add-data: Include assets folder
:: --name: Output filename
pyinstaller --noconsole --onefile --clean --name "ProcessKiller" --collect-all customtkinter --icon="assets/icon.ico" --add-data "assets;assets" main.py

echo.
echo Build complete!
echo The App is located at: %~dp0dist\ProcessKiller.exe
pause
