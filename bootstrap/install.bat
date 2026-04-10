@echo off
setlocal

python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

echo.
echo [OK] Environment siap.
endlocal
