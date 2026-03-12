@echo off
echo ========================================
echo AI Customer Support Agent - Setup Script
echo ========================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python is installed and in PATH
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Copying environment file...
if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file with your credentials
    echo Especially DATABASE_URL and API keys
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Edit .env file with your database URL and API keys
echo 2. Create PostgreSQL database: customer_support
echo 3. Run: python app/main.py
echo 4. Open: http://localhost:8000/docs
echo.
pause
