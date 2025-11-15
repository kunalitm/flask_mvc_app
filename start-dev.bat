@echo off
echo Starting Flask MVC Application...
echo.

REM Start backend in new window
echo Starting backend server...
start "Flask Backend" cmd /k "python run.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo Starting frontend server...
start "React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Login with:
echo Username: admin
echo Password: admin123
echo.
pause
