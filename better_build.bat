@echo off
REM Batch file to build the Python script using PyInstaller

REM Set the Python script name
set SCRIPT_NAME=log_parser.py

REM Install pyinstaller if needed
pip install pyinstaller

REM Run PyInstaller with the specified options
pyinstaller --onefile --console %SCRIPT_NAME%

REM Check if the build was successful
if %ERRORLEVEL% EQU 0 (
    echo Build successful! The executable is in the "dist" folder.
) else (
    echo Build failed. Install Python 3.X and Check the output for errors.
)

REM Pause to keep the window open (optional)
pause