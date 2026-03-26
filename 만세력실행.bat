@echo off
cd /d "C:\Users\sungw\OneDrive\Desktop\Project_Saju_313"
start "" cmd /c "timeout /t 3 >nul && start http://localhost:8501"
python -m streamlit run manse.py --server.port 8501 --browser.gatherUsageStats false
pause
