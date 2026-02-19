@echo off
title JARVIS Mark Entry Server
echo ============================================
echo   JARVIS - RMKCET Marks Dispatcher
echo   Starting local server on port 8080...
echo ============================================
echo.
echo Open in browser: http://localhost:8080/JARVIS_RMKCET.html
echo Press Ctrl+C to stop the server.
echo.
cd /d "%~dp0"
python -m http.server 8080
pause
