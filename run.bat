@echo off
echo ========================================
echo Starting AI Customer Support Agent
echo ========================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting FastAPI server...
echo Open http://localhost:8000/docs for API docs
echo Open http://localhost:8000/static/index.html for web form
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
