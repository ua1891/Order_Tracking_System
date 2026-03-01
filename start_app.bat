@echo off
echo =========================================
echo    Starting Order Tracking System...
echo =========================================
echo.
echo Launching the server and opening browser...
echo Please do not close this window while using the app.

:: Open the browser
start http://localhost:5000

:: Run the Flask application
python main\app.py

pause
