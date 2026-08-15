@echo off
REM start_sender.bat - Batch script to run music_sender.py

echo Starting ArcadeMatrix Music Sender...
echo.

python "%~dp0music_sender.py" --port 8085

echo.
echo Music sender stopped.
pause