# MarketLens Development Launcher (PowerShell)
# Starts both backend and frontend servers

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "            MarketLens Development Environment" -ForegroundColor Cyan
Write-Host "               AI-Powered Stock Analyst" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "→ Checking prerequisites..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "  ✓ npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ npm not found!" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "→ Checking dependencies..." -ForegroundColor Blue

if (-Not (Test-Path "backend\venv")) {
    Write-Host "  ⚠ Backend virtual environment not found!" -ForegroundColor Yellow
    Write-Host "    Run: cd backend; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ Backend virtual environment exists" -ForegroundColor Green

if (-Not (Test-Path "frontend\node_modules")) {
    Write-Host "  ⚠ Frontend node_modules not found!" -ForegroundColor Yellow
    Write-Host "    Run: cd frontend; npm install" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ Frontend node_modules exists" -ForegroundColor Green

# Check .env file
Write-Host ""
Write-Host "→ Checking configuration..." -ForegroundColor Blue

if (-Not (Test-Path "backend\.env")) {
    Write-Host "  ⚠ Backend .env file not found!" -ForegroundColor Yellow
    Write-Host "    Please create backend\.env with your API keys" -ForegroundColor Yellow

    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
} else {
    Write-Host "  ✓ Backend .env file exists" -ForegroundColor Green
}

# Start servers
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "STARTING SERVERS" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start backend in a new PowerShell window
Write-Host "→ Starting backend server..." -ForegroundColor Blue
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new PowerShell window
Write-Host "→ Starting frontend server..." -ForegroundColor Blue
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "✓ Servers started in separate windows" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the servers, close both PowerShell windows or press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Wait for user to press a key
Write-Host "Press any key to exit this launcher (servers will continue running)..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
