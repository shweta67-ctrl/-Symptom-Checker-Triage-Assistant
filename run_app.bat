@echo off
echo Starting AI Symptom Checker ^& Triage Assistant...
echo.
cd /d "%~dp0"
streamlit run app.py
pause
