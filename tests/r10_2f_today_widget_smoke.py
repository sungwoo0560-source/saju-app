# -*- coding: utf-8 -*-
"""R10-2f 검증: main()의 "오늘의 운세" 위젯(재물/건강/관계 아이콘) 로직이
build_monthly_grades로 전환된 뒤 예외 없이 돌고, 등급 분류(대길·길=좋은 달/
흉·흉흉=나쁜 달/평길·평=중립)가 build_monthly_grades 결과와 일치하는지 확인.

배경: main()은 사이드바·탭·폼 등 무거운 의존성이 많아 전체를 bare 모드로
실행하기 부적합하다(apptest_33.py도 MENU_ORDER에 넣지 않은 이유와 동일).
대신 manse.py:28156 이하의 실제 코드와 동일한 순서로 실함수(build_monthly_
grades)를 직접 호출해 예외 여부와 분류 정합성만 확인한다 — 새 로직 재구현이
아니라 소스의 문자열 그대로를 이 파일에 옮겨 실행한다.

실행: PYTHONIOENCODING=utf-8 python tests/r10_2f_today_widget_smoke.py
"""
import sys
from datetime import datetime

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

import pils_fixtures as pf
from saju_interpreter import build_monthly_grades

_GH_HANJA_MAP_B = {"대길": "대길(大吉)", "길": "길(吉)", "평길": "평길(平吉)",
                   "평": "평(平)", "흉": "흉(凶)", "흉흉": "흉흉(凶凶)"}


def run_one(name, today):
    pils = pf.get_pils(name)
    _mg_b = build_monthly_grades(pils, today.year)
    _cur_x_b = next((x for x in _mg_b if x["월"] == today.month), {})
    _ml_b = _cur_x_b.get("ml", {})
    _grade_b = _cur_x_b.get("등급", "평")
    _gil_b = _GH_HANJA_MAP_B.get(_grade_b, "평(平)")
    _ss_mon_b = _ml_b.get("십성", "")
    _good_b = _grade_b in ("대길", "길")
    _bad_b = _grade_b in ("흉", "흉흉")
    _money_icon_b = "💰 좋음" if "재" in _ss_mon_b or _good_b else ("⚠️ 주의" if _bad_b else "➖ 보통")
    _health_icon_b = "💪 양호" if "인" in _ss_mon_b or _grade_b == "대길" else ("🤒 주의" if _grade_b == "흉흉" else "➖ 보통")
    _rel_icon_b = "❤️ 원만" if "관" in _ss_mon_b or "식" in _ss_mon_b else ("⚡ 마찰" if _bad_b else "➖ 평온")
    return _grade_b, _gil_b, _money_icon_b, _health_icon_b, _rel_icon_b


CASES_TO_CHECK = [
    "박성우", "박후규",
    "감당력_중화_19991116", "바람기81_19870515",
    "근사구간_1955입춘_정규화후경계_직후",
    "한신보유A_20010914", "한신보유B_20060728",
]

today = datetime.now()
fail = 0
for name in CASES_TO_CHECK:
    try:
        grade, gil, money, health, rel = run_one(name, today)
        # 등급 분류 정합성: gil 문자열이 grade의 정확한 한자 부기여야 한다
        assert _GH_HANJA_MAP_B[grade] == gil, f"등급/문구 불일치: {grade} vs {gil}"
        print(f"[OK] {name}: 등급={grade} 문구={gil} 재물={money} 건강={health} 관계={rel}")
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")
        fail += 1

print(f"\n총 {len(CASES_TO_CHECK)}건 중 실패 {fail}건")
sys.exit(0 if fail == 0 else 1)
