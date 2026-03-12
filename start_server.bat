@echo off
echo =========================================
echo Starting AI Customer Support Agent
echo =========================================
echo.
echo Server starting on: http://localhost:8000
echo UI: http://localhost:8000/
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo =========================================
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
