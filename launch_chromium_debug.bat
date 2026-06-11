@echo off
echo Killing any existing Chrome/Chromium processes...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromium.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo Launching Chromium with remote debugging on port 9222...
start "" "C:\Users\Admin\AppData\Local\Chromium\chrome-win\chrome.exe" --remote-debugging-port=9222 "--user-data-dir=%~dp0.chrome-debug-profile" --no-first-run --disable-session-crashed-bubble


echo Waiting for Chromium to bind to port 9222...
timeout /t 3 /nobreak >nul

echo Verify at: http://127.0.0.1:9222/json
pause
