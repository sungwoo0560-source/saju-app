# -*- coding: utf-8 -*-
"""R10-2c 검증: render_pdf_download_btn(탭 전용 즉시 PDF, future3/yearly)의
월별 길흉 섹션을 build_monthly_grades로 전환한 뒤 실제로 예외 없이 도는지 확인.

배경: 두 지점(구 8380/8465) 모두 get_monthly_luck(pils, year)를 month 인자 없이
불러 항상 TypeError가 나고 try/except로 조용히 폴백 문구로 빠지던 죽은 코드였다
(R10-2 진단, 2026-09-27 실측 확인). apptest_33.py는 이 함수를 MENU_ORDER에 넣지
않고(st.button 게이트라 bare 모드에서 항상 False), 다른 22개 메뉴처럼 st.*
캡처만으로는 이 분기를 통과시킬 수 없다 — st.button만 True로 임시 monkeypatch해
실제 버튼 클릭을 재현한다.

실행: PYTHONIOENCODING=utf-8 python tests/r10_2c_pdf_monthly_smoke.py
"""
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

import streamlit as st
import manse
import pils_fixtures as pf

# render_pdf_download_btn은 "if st.button(...):" 안에서만 PDF를 생성한다 —
# bare 모드에서는 항상 False라 실제 클릭을 흉내내야 그 분기를 통과한다.
_orig_button = st.button
st.button = lambda *a, **k: True
manse.st.button = st.button


def run_one(name, tab_name):
    pils = pf.get_pils(name)
    cfg = pf.CASES[name]
    try:
        manse.render_pdf_download_btn(tab_name, pils, name, cfg["birth"][0], cfg["gender"])
        return True, None
    except Exception as e:
        return False, e


CASES_TO_CHECK = [
    "박성우", "박후규",
    "감당력_중화_19991116", "바람기81_19870515",       # R9-1a 극한월 순수중화
    "근사구간_1955입춘_정규화후경계_직후",                 # 춘추월 순수중화
    "한신보유A_20010914", "한신보유B_20060728",           # 신강 표본
]

ok_count = 0
fail_count = 0
for name in CASES_TO_CHECK:
    for tab in ("future3", "yearly"):
        ok, err = run_one(name, tab)
        status = "[OK]" if ok else "[FAIL]"
        print(f"{status} {name} / {tab}" + (f" — {type(err).__name__}: {err}" if err else ""))
        if ok:
            ok_count += 1
        else:
            fail_count += 1

print(f"\n총 {ok_count + fail_count}건 중 성공 {ok_count}건, 실패 {fail_count}건")

st.button = _orig_button
sys.exit(0 if fail_count == 0 else 1)
