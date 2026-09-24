# -*- coding: utf-8 -*-
"""R6-7 라운드 — saju_interpreter.py:2414(시주 미상 고지문), 1894~1898(_get_base
시각값), manse.py:29106(hour_display 배지) 회귀 테스트.

R6-5-1(manse.py:15758)과 같은 패턴: "시간모름 제출 -> 체크만 해제(미제출)"
시나리오에서 in_unknown_time 라이브 플래그로 판단하던 코드가 pils[0]은 그대로
블랭크인데 플래그만 바뀌어 조용히 틀린 화면을 보여주던 결함들의 회귀 방지.

manse.py를 통째로 import하면 Streamlit 앱 실행 부작용이 커서, saju_interpreter
쪽(R6-7a/b)은 직접 import해서 검증하고 manse.py 쪽(R6-7c)은 이미 확립된
apptest_33/개별 하네스 관례를 그대로 따른다(이 파일 안에서 manse 함수를
직접 호출하는 별도 섹션으로 분리).
"""
import os
import sys
import textwrap

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # noqa: E402
from saju_interpreter import LocalSajuNarrator  # noqa: E402
from saju_engine import SajuPrecisionEngine  # noqa: E402
from saju_data import JJ_12b  # noqa: E402
from pils_fixtures import CASES  # noqa: E402

DISCLAIMER = "출생시각 미상으로"

_MANSE_PATH = os.path.join(_ROOT, "manse.py")


def _extract_hour_display_block():
    """manse.py의 hour_display 배지 계산 블록(R6-7c, main() 안 인라인 코드라
    resolve_birth_hour_check.py처럼 함수 단위 AST 추출이 안 됨 — 시작/끝
    마커 사이 텍스트를 그대로 잘라 exec한다. 소스가 바뀌면 이 테스트도
    최신 코드를 그대로 반영한다(라인 번호 고정 아님)."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    # 앵커는 이번 수정과 무관한(달라지지 않는) 바로 위 줄로 잡는다 — 그래야
    # git apply -R로 R6-7c만 되돌린 "수정 전" 소스에서도 추출이 안 깨진다.
    anchor = "양력 {_solar.year}.{_solar.month:02d}.{_solar.day:02d}</span>\""
    end = 'hour_badge = f"<span'
    i = src.index(anchor)
    block_start = src.index("\n", i) + 1
    j = src.index(end, block_start)
    return textwrap.dedent(src[block_start:j])


_HOUR_DISPLAY_SRC = _extract_hour_display_block()


def _compute_hour_display(pils, ss_dict):
    ns = {"_ss": ss_dict, "pils": pils, "JJ_12b": JJ_12b}
    exec(_HOUR_DISPLAY_SRC, ns)
    return ns["hour_display"]


def _make_pils(case_name, hour, minute, blank_siju):
    case = CASES[case_name]
    y, m, d, _h, _mi = case["birth"]
    gender = case["gender"]
    pils = SajuPrecisionEngine.get_pillars(y, m, d, hour, minute, gender, use_yaja_time=True, longitude=126.98)
    pils = [dict(p) for p in pils]
    if blank_siju:
        pils[0] = {"cg": "", "jj": "", "str": ""}
    return pils, y, gender


def check_2414_scenario_a():
    """R6-7a: 시간모름 제출 -> 체크만 해제(미제출). pils[0]은 여전히 블랭크인데
    disclaimer가 사라지면 안 된다(고쳐지기 전엔 사라졌음 — R6-7 진단 실측)."""
    pils, y, gender = _make_pils("박성우", 12, 0, blank_siju=True)

    st.session_state.clear()
    st.session_state["in_unknown_time"] = True
    report_submit = LocalSajuNarrator.full_report(pils, "박성우", y, gender)
    ok_submit = DISCLAIMER in report_submit

    st.session_state["in_unknown_time"] = False  # 체크만 해제, pils는 그대로(미제출)
    report_after_uncheck = LocalSajuNarrator.full_report(pils, "박성우", y, gender)
    ok_after = DISCLAIMER in report_after_uncheck  # pils[0]이 여전히 블랭크라 True여야 정상

    ok = ok_submit and ok_after
    print(f"[{'PASS' if ok else 'FAIL'}] 2414 시나리오(a): 제출시 disclaimer={ok_submit}, "
          f"체크해제후(미제출) disclaimer={ok_after} (기대 둘 다 True — pils[0] 기준이라 플래그 무관)")
    return ok


def check_2414_scenario_b():
    """R6-7a 반대 방향: 시간확정 제출 -> 체크만 켬(미제출). pils[0]은 실값 그대로라
    disclaimer가 잘못 나타나면 안 된다(과잉 노출 방지 확인)."""
    pils, y, gender = _make_pils("박성우", 7, 30, blank_siju=False)

    st.session_state.clear()
    st.session_state["in_unknown_time"] = False
    report_submit = LocalSajuNarrator.full_report(pils, "박성우", y, gender)
    ok_submit = DISCLAIMER not in report_submit

    st.session_state["in_unknown_time"] = True  # 체크만 켬, pils는 그대로(미제출, 실제 시주 있음)
    report_after_check = LocalSajuNarrator.full_report(pils, "박성우", y, gender)
    ok_after = DISCLAIMER not in report_after_check  # pils[0]에 실값 있으니 여전히 False(미노출)여야 정상

    ok = ok_submit and ok_after
    print(f"[{'PASS' if ok else 'FAIL'}] 2414 시나리오(b): 제출시 disclaimer 미노출={ok_submit}, "
          f"체크만 켠 후(미제출) disclaimer 미노출={ok_after} (기대 둘 다 True — 과잉노출 없음)")
    return ok


def check_get_base_snapshot_priority():
    """R6-7b: LocalSajuNarrator._get_base(1894~1901행)의 대운 계산용 bh가
    "_submitted_hour" 세션 스냅샷을 최우선으로 쓰는지 — R6-6b가 manse.resolve_
    birth_hour에 세운 규칙과 동일. 1957-09-14 남은 0시/12시 대운 시작나이가
    1/2로 실제로 갈리는 표본(R6-3 진단에서 N=1000 실측 확인된 값 재사용)."""
    y, m, d, gender = 1957, 9, 14, "남"
    pils = SajuPrecisionEngine.get_pillars(y, m, d, 12, 0, gender, use_yaja_time=True, longitude=126.98)

    # A) 스냅샷=12 있음 — 라이브 in_unknown_time=False·birth_hour=0(후보)이어도 무시하고 12로 계산
    st.session_state.clear()
    st.session_state["birth_month"] = m
    st.session_state["birth_day"] = d
    st.session_state["in_unknown_time"] = False
    st.session_state["birth_hour"] = 0
    st.session_state["_submitted_hour"] = 12
    b_snap = LocalSajuNarrator._get_base(pils, "테스트", y, gender)
    sa_snap = b_snap["dw_list"][0]["시작나이"]

    # B) 스냅샷 없음(구형/미제출), 라이브 birth_hour=0 — 기존 인라인 로직 그대로 폴백(0시로 계산)
    st.session_state.clear()
    st.session_state["birth_month"] = m
    st.session_state["birth_day"] = d
    st.session_state["in_unknown_time"] = False
    st.session_state["birth_hour"] = 0
    b_raw = LocalSajuNarrator._get_base(pils, "테스트", y, gender)
    sa_raw = b_raw["dw_list"][0]["시작나이"]

    ok = (sa_snap == 2) and (sa_raw == 1)
    print(f"[{'PASS' if ok else 'FAIL'}] _get_base 스냅샷 우선: 스냅샷=12일때 시작나이={sa_snap}(기대 2), "
          f"스냅샷 없음+라이브 0시일때 시작나이={sa_raw}(기대 1 — 기존 로직 폴백)")
    return ok


def check_get_base_scenario_a():
    """R6-7b 시나리오(a): 시간모름 제출(스냅샷=12 확정) -> 체크만 해제(미제출,
    라이브 birth_hour=0으로 남음). 스냅샷이 있으니 대운은 그대로 12시 기준을
    유지해야 한다(수정 전엔 라이브 0시로 흔들렸음)."""
    y, m, d, gender = 1957, 9, 14, "남"
    pils = SajuPrecisionEngine.get_pillars(y, m, d, 12, 0, gender, use_yaja_time=True, longitude=126.98)

    st.session_state.clear()
    st.session_state["birth_month"] = m
    st.session_state["birth_day"] = d
    st.session_state["in_unknown_time"] = True
    st.session_state["birth_hour"] = 0
    st.session_state["_submitted_hour"] = 12  # 제출 처리(manse.py 28687~28726행 상당)가 확정해 둔 값
    b_submit = LocalSajuNarrator._get_base(pils, "테스트", y, gender)
    sa_submit = b_submit["dw_list"][0]["시작나이"]

    st.session_state["in_unknown_time"] = False  # 체크만 해제, 미제출 — 스냅샷은 그대로 남아있음
    b_after = LocalSajuNarrator._get_base(pils, "테스트", y, gender)
    sa_after = b_after["dw_list"][0]["시작나이"]

    ok = (sa_submit == sa_after == 2)
    print(f"[{'PASS' if ok else 'FAIL'}] _get_base 시나리오(a): 제출시 시작나이={sa_submit}, "
          f"체크해제후(미제출) 시작나이={sa_after} (기대 둘 다 2 — 스냅샷이 있어 안 흔들림)")
    return ok


def check_hour_display_scenario_a():
    """R6-7c: 시간모름 제출(pils[0] 블랭크) -> 체크만 해제(미제출, 라이브
    in_birth_hour는 원시값 그대로). frozen birth_hour(R6-6a로 12 확정)와
    pils[0] 기준으로 판단하므로 "시간 모름" 배지가 안 흔들려야 한다."""
    pils, y, gender = _make_pils("박성우", 12, 0, blank_siju=True)

    ss = {"in_unknown_time": True, "birth_hour": 12, "in_birth_hour": 0}  # 제출 직후
    hd_submit = _compute_hour_display(pils, ss)

    ss["in_unknown_time"] = False  # 체크만 해제, 미제출 — birth_hour(frozen)·pils는 그대로
    hd_after = _compute_hour_display(pils, ss)

    ok = (hd_submit == "시간 모름") and (hd_after == "시간 모름")
    print(f"[{'PASS' if ok else 'FAIL'}] hour_display 시나리오(a): 제출시='{hd_submit}', "
          f"체크해제후(미제출)='{hd_after}' (기대 둘 다 '시간 모름')")
    return ok


def check_hour_display_known_time():
    """R6-7c 대조군: 시간확정(7시) 제출은 그대로 "07시(HH시)" 형식이어야 한다
    (라이브 in_birth_hour를 frozen birth_hour로 바꾼 것 때문에 회귀 없는지)."""
    pils, y, gender = _make_pils("박성우", 7, 30, blank_siju=False)
    ss = {"in_unknown_time": False, "birth_hour": 7, "in_birth_hour": 7}
    hd = _compute_hour_display(pils, ss)
    ok = hd.startswith("07시(") and hd.endswith("시)")
    print(f"[{'PASS' if ok else 'FAIL'}] hour_display 시간확정 대조군: '{hd}' (기대 '07시(...시)' 형식)")
    return ok


def run():
    results = [
        check_2414_scenario_a(),
        check_2414_scenario_b(),
        check_get_base_snapshot_priority(),
        check_get_base_scenario_a(),
        check_hour_display_scenario_a(),
        check_hour_display_known_time(),
    ]
    fail = results.count(False)
    total = len(results)
    print()
    if fail:
        print(f"[FAIL] {fail}/{total}건 실패")
        return False
    print(f"[PASS] {total}/{total}건 전부 통과")
    return True


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
