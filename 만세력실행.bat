@echo off
chcp 65001 > nul
title 만세력 사주 앱

cd /d "C:\Users\sungw\OneDrive\Desktop\Project_Saju_313"

echo.
echo  ==========================================
echo   만세력 사주 앱 시작 중...
echo  ==========================================
echo.

REM venv Python 우선, 없으면 시스템 Python 사용
if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
    set STREAMLIT=venv\Scripts\streamlit.exe
) else (
    set PYTHON=python
    set STREAMLIT=python -m streamlit
)

REM streamlit.exe 없으면 -m 방식으로 fallback
if not exist "venv\Scripts\streamlit.exe" (
    set STREAMLIT=%PYTHON% -m streamlit
)

echo  Python: %PYTHON%
echo.

REM 브라우저 자동 오픈 포함
%STREAMLIT% run manse.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

if errorlevel 1 (
    echo.
    echo  [오류] 앱 실행에 실패했습니다.
    echo  venv가 없는 경우: python -m pip install streamlit 실행 후 다시 시도하세요.
    pause
)
