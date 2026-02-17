@echo off
echo Starting EduTrack Backend Server...
start "" ".\.venv\Scripts\python.exe" server.py
echo.
echo Starting Web Dashboard (Vite)...
cd web
start "" npm run dev
echo.
echo App is running! 
echo 1. Dashboard: http://localhost:5173
echo 2. API Server: http://localhost:5000
echo.
echo To allow the APK to connect, ensure your phone is on the same Wi-Fi
echo and change API_BASE_URL in web/main.js to your PC's IP address.
pause
