#!/usr/bin/env python3
"""
MarketLens Development Launcher
Starts both backend and frontend servers with a single command
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# ANSI color codes
COLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
}

def print_colored(message, color='ENDC'):
    """Print colored message"""
    if sys.platform == 'win32':
        # Windows doesn't always support ANSI colors, so just print plain text
        print(message)
    else:
        print(f"{COLORS.get(color, '')}{message}{COLORS['ENDC']}")

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              MarketLens Development Environment             ║
    ║                   AI-Powered Stock Analyst                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, 'CYAN')
    print_colored("    Starting backend and frontend servers...\n", 'YELLOW')

def check_prerequisites():
    """Check if required tools are installed"""
    print_colored("→ Checking prerequisites...", 'BLUE')

    # Check Python
    try:
        python_version = subprocess.check_output(['python', '--version'],
                                                stderr=subprocess.STDOUT).decode().strip()
        print_colored(f"  ✓ {python_version}", 'GREEN')
    except Exception:
        print_colored("  ✗ Python not found!", 'RED')
        return False

    # Check Node.js
    try:
        node_version = subprocess.check_output(['node', '--version'],
                                              stderr=subprocess.STDOUT).decode().strip()
        print_colored(f"  ✓ Node.js {node_version}", 'GREEN')
    except Exception:
        print_colored("  ✗ Node.js not found!", 'RED')
        return False

    # Check npm
    try:
        npm_version = subprocess.check_output(['npm', '--version'],
                                             stderr=subprocess.STDOUT).decode().strip()
        print_colored(f"  ✓ npm {npm_version}", 'GREEN')
    except Exception:
        print_colored("  ✗ npm not found!", 'RED')
        return False

    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print_colored("\n→ Checking dependencies...", 'BLUE')

    project_root = Path(__file__).parent
    backend_venv = project_root / 'backend' / 'venv'
    frontend_modules = project_root / 'frontend' / 'node_modules'

    # Check backend dependencies
    if not backend_venv.exists():
        print_colored("  ⚠ Backend virtual environment not found!", 'YELLOW')
        print_colored("    Run: cd backend && python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt", 'YELLOW')
        return False
    else:
        print_colored("  ✓ Backend virtual environment exists", 'GREEN')

    # Check frontend dependencies
    if not frontend_modules.exists():
        print_colored("  ⚠ Frontend node_modules not found!", 'YELLOW')
        print_colored("    Run: cd frontend && npm install", 'YELLOW')
        return False
    else:
        print_colored("  ✓ Frontend node_modules exists", 'GREEN')

    return True

def check_env_file():
    """Check if .env file exists"""
    print_colored("\n→ Checking configuration...", 'BLUE')

    project_root = Path(__file__).parent
    env_file = project_root / 'backend' / '.env'

    if not env_file.exists():
        print_colored("  ⚠ Backend .env file not found!", 'YELLOW')
        print_colored("    Please create backend/.env with your API keys", 'YELLOW')
        return False
    else:
        print_colored("  ✓ Backend .env file exists", 'GREEN')

        # Check if API keys are set
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content and 'sk-' in content:
                print_colored("  ✓ OpenAI API key configured", 'GREEN')
            else:
                print_colored("  ⚠ OpenAI API key not found in .env", 'YELLOW')

    return True

def start_backend():
    """Start the backend server"""
    print_colored("\n→ Starting backend server (port 8000)...", 'BLUE')

    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'

    # Determine Python executable
    if sys.platform == 'win32':
        python_exe = backend_dir / 'venv' / 'Scripts' / 'python.exe'
    else:
        python_exe = backend_dir / 'venv' / 'bin' / 'python'

    if not python_exe.exists():
        python_exe = 'python'  # Fallback to system python

    # Start uvicorn server
    cmd = [
        str(python_exe),
        '-m', 'uvicorn',
        'main:app',
        '--reload',
        '--host', '0.0.0.0',
        '--port', '8000'
    ]

    process = subprocess.Popen(
        cmd,
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    return process

def start_frontend():
    """Start the frontend dev server"""
    print_colored("\n→ Starting frontend server (port 8080)...", 'BLUE')

    project_root = Path(__file__).parent
    frontend_dir = project_root / 'frontend'

    # Start Vite dev server
    cmd = ['npm', 'run', 'dev']

    process = subprocess.Popen(
        cmd,
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    return process

def monitor_processes(backend_proc, frontend_proc):
    """Monitor and display output from both processes"""
    import select

    print_colored("\n" + "="*70, 'CYAN')
    print_colored("SERVERS RUNNING", 'BOLD')
    print_colored("="*70, 'CYAN')
    print_colored("Backend:  http://localhost:8000", 'GREEN')
    print_colored("Frontend: http://localhost:8080", 'GREEN')
    print_colored("\nPress Ctrl+C to stop both servers\n", 'YELLOW')
    print_colored("="*70 + "\n", 'CYAN')

    try:
        while True:
            # Read from backend
            if backend_proc.poll() is None:  # Process is running
                line = backend_proc.stdout.readline()
                if line:
                    print(f"[BACKEND]  {line.rstrip()}")

            # Read from frontend
            if frontend_proc.poll() is None:  # Process is running
                line = frontend_proc.stdout.readline()
                if line:
                    print(f"[FRONTEND] {line.rstrip()}")

            # Check if both processes have exited
            if backend_proc.poll() is not None and frontend_proc.poll() is not None:
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print_colored("\n\n→ Shutting down servers...", 'YELLOW')

        # Terminate processes gracefully
        backend_proc.terminate()
        frontend_proc.terminate()

        # Wait for processes to exit
        try:
            backend_proc.wait(timeout=5)
            frontend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if they don't exit gracefully
            backend_proc.kill()
            frontend_proc.kill()

        print_colored("✓ Servers stopped successfully\n", 'GREEN')

def main():
    """Main entry point"""
    print_banner()

    # Check prerequisites
    if not check_prerequisites():
        print_colored("\n✗ Prerequisites check failed!", 'RED')
        print_colored("Please install Python 3.11+ and Node.js 18+", 'YELLOW')
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        print_colored("\n✗ Dependencies check failed!", 'RED')
        print_colored("Please install dependencies first (see instructions above)", 'YELLOW')
        sys.exit(1)

    # Check environment
    if not check_env_file():
        print_colored("\n⚠ Configuration incomplete", 'YELLOW')
        print_colored("Please configure backend/.env with API keys", 'YELLOW')
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

    # Start servers
    try:
        backend_proc = start_backend()
        time.sleep(2)  # Wait for backend to start

        frontend_proc = start_frontend()
        time.sleep(2)  # Wait for frontend to start

        # Monitor both processes
        monitor_processes(backend_proc, frontend_proc)

    except Exception as e:
        print_colored(f"\n✗ Error: {e}", 'RED')
        sys.exit(1)

if __name__ == '__main__':
    main()
