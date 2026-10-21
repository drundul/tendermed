@echo off
chcp 65001 > nul
echo ============================================================
echo   Запуск TenderMed SaaS (FastAPI + Next.js 15)
echo ============================================================
echo.
python run_saas.py
pause
