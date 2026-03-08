@echo off
chcp 65001 >nul
title 만세력 사주 앱

echo.
echo  ╔══════════════════════════════════╗
echo  ║     🔮 만세력 사주 앱 실행 중     ║
echo  ╚══════════════════════════════════╝
echo.

cd /d "C:\Users\sungw\OneDrive\Desktop\Project_Saju_313"

echo  📁 경로: %CD%
echo  🚀 앱을 시작합니다...
echo.

streamlit run manse.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ❌ 오류 발생! 아래 내용을 확인하세요:
    echo  - Python/Streamlit 설치 여부
    echo  - manse.py 파일 존재 여부
    echo.
    pause
)