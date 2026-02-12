@echo off
REM MarketLens Development Launcher (Windows Batch)
REM Starts both backend and frontend servers

echo.
echo ================================================================
echo              MarketLens Development Environment
echo                 AI-Powered Stock Analyst
echo ================================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo [OK] Prerequisites found
echo.

REM Check backend virtual environment
if not exist "backend\venv\" (
    echo [WARNING] Backend virtual environment not found!
    echo Please run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check frontend node_modules
if not exist "frontend\node_modules\" (
    echo [WARNING] Frontend dependencies not found!
    echo Please run: cd frontend ^&^& npm install
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Check .env file
if not exist "backend\.env" (
    echo [WARNING] Backend .env file not found!
    echo Please create backend\.env with your API keys
    pause
)

echo.
echo ================================================================
echo Starting servers...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080
echo.
echo Press Ctrl+C to stop both servers
echo ================================================================
echo.

REM Start backend server in a new window
start "MarketLens Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window
start "MarketLens Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo [OK] Servers started in separate windows
echo.
echo To stop the servers, close both terminal windows or press Ctrl+C in each
echo.

pause
