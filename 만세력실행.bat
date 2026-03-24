@echo off
cd /d "C:\Users\sungw\OneDrive\Desktop\Project_Saju_313"

echo Starting Saju App...

if exist "venv\Scripts\streamlit.exe" (
    venv\Scripts\streamlit.exe run manse.py --server.port 8501 --browser.gatherUsageStats false
) else (
    python -m streamlit run manse.py --server.port 8501 --browser.gatherUsageStats false
)

pause
