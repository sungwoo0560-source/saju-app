
# ======================================================
# 🤖 AI WORK ENGINE (No Saju Logic)
# Integrated Automation + Prompt Control + Error Recovery
# ======================================================
#
# Purpose:
# - Stable AI task execution
# - Auto error detection & recovery
# - Prompt standardization
# - Feedback learning system
# - Developer workflow assistant
#
# ======================================================

import json
import datetime
import traceback
from typing import Any, Dict

# ======================================================
# 1️⃣ Prompt Engine (Stable AI Instructions)
# ======================================================

BASE_PROMPT = """
You are an elite senior software engineer AI.

Rules:
1. Fix errors automatically when detected.
2. Always return runnable code.
3. Prefer minimal changes over rewrites.
4. Explain briefly, then provide corrected code.
5. Never leave unfinished logic.
"""

def build_prompt(task_description: str, code_context: str = "") -> str:
    return f"""
{BASE_PROMPT}

TASK:
{task_description}

CODE CONTEXT:
{code_context}
"""

# ======================================================
# 2️⃣ Safe Execution Layer (Prevents Crash Loops)
# ======================================================

def safe_execute(func, *args, **kwargs):
    try:
        return {
            "success": True,
            "result": func(*args, **kwargs)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }

# ======================================================
# 3️⃣ Error Analyzer (Auto Debug Helper)
# ======================================================

def analyze_error(trace: str) -> Dict[str, Any]:
    if "IndentationError" in trace:
        issue = "Indentation problem detected"
    elif "KeyError" in trace:
        issue = "Missing dictionary key"
    elif "TypeError" in trace:
        issue = "Type mismatch"
    else:
        issue = "Unknown runtime error"

    return {
        "diagnosis": issue,
        "recommendation": "Review recent code changes near error location."
    }

# ======================================================
# 4️⃣ Feedback Learning System
# ======================================================

FEEDBACK_DB = "ai_feedback.json"

def save_feedback(user_id: str, rating: int, comment: str):
    data = []
    try:
        with open(FEEDBACK_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        pass

    data.append({
        "user": user_id,
        "rating": rating,
        "comment": comment,
        "time": str(datetime.datetime.now())
    })

    with open(FEEDBACK_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def average_rating():
    try:
        with open(FEEDBACK_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sum(d["rating"] for d in data) / len(data)
    except:
        return 0

# ======================================================
# 5️⃣ AI Workflow Pipeline
# ======================================================

def run_ai_task(user_id: str, task: str, code_context: str = ""):
    prompt = build_prompt(task, code_context)

    # Placeholder for real LLM API call
    ai_output = f"""
[SIMULATED AI OUTPUT]

Task understood.
Generated stable solution based on rules.

Prompt Length: {len(prompt)} characters
"""

    return {
        "prompt": prompt,
        "output": ai_output
    }

# ======================================================
# 6️⃣ Streamlit Interface Example
# ======================================================

def streamlit_app():
    import streamlit as st

    st.title("🤖 AI Work Engine")

    task = st.text_area("작업 설명")
    context = st.text_area("코드 컨텍스트 (선택)")

    if st.button("AI 실행"):
        result = run_ai_task("demo_user", task, context)
        st.text(result["output"])

        rating = st.slider("결과 만족도", 1, 5, 3)
        comment = st.text_input("피드백")

        if st.button("피드백 저장"):
            save_feedback("demo_user", rating, comment)
            st.success("저장 완료")

# ======================================================
# Test Run
# ======================================================

if __name__ == "__main__":
    print(run_ai_task("test_user", "Fix python error"))
