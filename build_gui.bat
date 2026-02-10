@echo off
echo Installing Dependencies...
pip install customtkinter psutil packaging pillow

echo.
echo.
echo Building GUI Executable...
:: We use --noconsole to hide the terminal window
:: --collect-all customtkinter ensures all theme files are included
:: --icon=icon.ico sets the exe icon
:: --add-data "icon.ico;." ensures the icon is available at runtime
pyinstaller --noconsole --onefile --clean --name "ProcessKiller_GUI" --collect-all customtkinter --icon=icon.ico --add-data "icon.ico;." process_manager_gui.py

echo.
echo Build complete!
echo The App is located at: %~dp0dist\ProcessKiller_GUI.exe
pause
