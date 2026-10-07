@echo off
setlocal
cd /d "%~dp0"
set "PORT=8000"
where py >nul 2>nul
if not errorlevel 1 goto run_py
where python >nul 2>nul
if not errorlevel 1 goto run_python

echo Python was not found. Opening the static Ahangban brand preview directly instead.
start "" "%~dp0index.html"
echo You can still open index.html manually. To use localhost, install Python 3 and run this file again.
exit /b 0

:run_py
start "Ahangban localhost server" py -m http.server %PORT% --bind 127.0.0.1
goto open_preview

:run_python
start "Ahangban localhost server" python -m http.server %PORT% --bind 127.0.0.1

:open_preview
timeout /t 2 /nobreak >nul
start "" "http://localhost:%PORT%/index.html"
echo The server is running in its separate console window. Keep that window open.
echo Press Ctrl+C in the server window (or close it) to stop the preview.
exit /b 0
