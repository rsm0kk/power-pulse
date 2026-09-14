@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===== 관세청 API 진단 =====
python power_pulse.py --probe > probe_log.txt 2>&1
type probe_log.txt
echo.
echo 위 내용이 probe_log.txt 로도 저장됐습니다. 그 파일을 Claude에게 올려주세요.
pause
