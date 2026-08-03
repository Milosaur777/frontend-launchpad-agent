@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install "remove-ai-watermarks[gpu]"
echo.
echo Starting AI Image Cleaner...
cd src
python main.py
pause
