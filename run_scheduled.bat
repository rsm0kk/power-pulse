@echo off
chcp 65001 >nul
cd /d "%~dp0"
"C:\Python314\python.exe" power_pulse.py >> "%~dp0build_log.txt" 2>&1
