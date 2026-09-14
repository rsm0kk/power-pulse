@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo  Power Equipment Pulse - 대시보드 빌드
echo ============================================
python power_pulse.py
if errorlevel 1 (
  echo.
  echo [오류] python 명령을 못 찾았거나 실행에 실패했습니다.
  echo python.org 에서 Python 설치 시 "Add to PATH" 체크했는지 확인하세요.
)
echo.
echo out 폴더의 HTML 파일을 열거나 공유하세요.
pause
