@echo off
REM Quick script to check if all prerequisites are installed

echo.
echo Checking MarketLens Prerequisites...
echo ====================================
echo.

REM Check Python
echo [1/3] Checking Python...
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python --version
    echo [OK] Python found
) else (
    echo [ERROR] Python not found!
    echo Please install Python 3.11+ from https://www.python.org/
)
echo.

REM Check Node.js
echo [2/3] Checking Node.js...
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    node --version
    echo [OK] Node.js found
) else (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
)
echo.

REM Check npm
echo [3/3] Checking npm...
where npm >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    npm --version
    echo [OK] npm found
) else (
    echo [ERROR] npm not found!
    echo npm should be installed with Node.js
)
echo.

echo ====================================
echo.

REM Check virtual environment
if exist "backend\venv\" (
    echo [OK] Backend virtual environment exists
) else (
    echo [SETUP] Backend virtual environment not found
    echo Run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
)
echo.

REM Check node_modules
if exist "frontend\node_modules\" (
    echo [OK] Frontend dependencies installed
) else (
    echo [SETUP] Frontend dependencies not installed
    echo Run: cd frontend ^&^& npm install
)
echo.

REM Check .env
if exist "backend\.env" (
    echo [OK] Backend .env file exists
) else (
    echo [SETUP] Backend .env file not found
    echo Create backend\.env and add your API keys
)
echo.

echo ====================================
echo Setup complete? Run: start-dev.bat
echo ====================================
echo.

pause
