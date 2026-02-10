@echo off
echo Installing PyInstaller...
pip install pyinstaller rich

echo.
echo Building executable (Ultimate Edition)...
python -m PyInstaller --onefile --clean --name "ProcessKiller_Ultimate" process_manager.py

echo.
echo Build complete!
echo The executable is located at: %~dp0dist\ProcessKiller_Ultimate.exe
pause
