@echo off
chcp 65001 >nul
title Project_Saju_313 정리

cd /d "C:\Users\sungw\OneDrive\Desktop\Project_Saju_313"

echo.
echo  ╔══════════════════════════════════════╗
echo  ║     🗑️  Project_Saju_313 정리 시작   ║
echo  ╚══════════════════════════════════════╝
echo.
echo  아래 항목들을 삭제합니다:
echo  - __pycache__  (파이썬 캐시 폴더)
echo  - .ruff_cache  (린터 캐시 폴더)
echo  - _font_test.pdf
echo  - _font_test2.pdf
echo  - app_sim_055527.pdf
echo  - debug_saju.py
echo  - pyflakes_err.txt
echo  - saju_cache.json
echo  - saju_memory_cache.json
echo.
echo  ⚠️  계속하시겠습니까? (Y/N)
set /p confirm=  입력: 

if /i "%confirm%" NEQ "Y" (
    echo  취소되었습니다.
    pause
    exit
)

echo.
echo  🔄 정리 중...

:: 캐시 폴더
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo  ✅ __pycache__ 삭제
)
if exist ".ruff_cache" (
    rmdir /s /q ".ruff_cache"
    echo  ✅ .ruff_cache 삭제
)

:: 테스트 PDF
if exist "_font_test.pdf"      del /q "_font_test.pdf"      && echo  ✅ _font_test.pdf 삭제
if exist "_font_test2.pdf"     del /q "_font_test2.pdf"     && echo  ✅ _font_test2.pdf 삭제
if exist "app_sim_055527.pdf"  del /q "app_sim_055527.pdf"  && echo  ✅ app_sim_055527.pdf 삭제

:: 디버그/오류 파일
if exist "debug_saju.py"       del /q "debug_saju.py"       && echo  ✅ debug_saju.py 삭제
if exist "pyflakes_err.txt"    del /q "pyflakes_err.txt"    && echo  ✅ pyflakes_err.txt 삭제

:: 캐시 JSON
if exist "saju_cache.json"        del /q "saju_cache.json"        && echo  ✅ saju_cache.json 삭제
if exist "saju_memory_cache.json" del /q "saju_memory_cache.json" && echo  ✅ saju_memory_cache.json 삭제

echo.
echo  ✅ 정리 완료!
echo.
echo  📌 유지된 중요 파일:
echo  - manse.py, saju_data.py (메인 소스)
echo  - customer_db.db, saju_consultations.db (DB)
echo  - history_memory.json, saju_feedback.json (데이터)
echo  - kasi_24terms.json, html_blocks.json (엔진 데이터)
echo  - NanumMyeongjo.ttf (폰트)
echo  - .claude, .streamlit, venv (설정/환경)
echo.
pause