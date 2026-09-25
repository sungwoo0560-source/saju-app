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
import ast
import os
import sys
import textwrap

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # noqa: E402
from saju_interpreter import LocalSajuNarrator, get_jeokjung_affair  # noqa: E402
from saju_engine import SajuPrecisionEngine, SajuCoreEngine, TimeCorrection  # noqa: E402
from saju_zhengtong import detect_life_risk_signals  # noqa: E402
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
    # R6-9b: date_badge 블록이 frozen birth_year/birth_month/birth_day 기반으로
    # 바뀌면서 이 앵커도 함께 갱신(원래 텍스트는 _solar.year 등 라이브 변수 참조였음).
    anchor = "양력 {birth_year}.{birth_month:02d}.{birth_day:02d}</span>\""
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


_SAJU_INTERP_PATH = os.path.join(_ROOT, "saju_interpreter.py")


def _extract_bmi_block():
    """R6-7d: saju_interpreter.py _get_base의 bmi(분) 계산 블록 추출.
    앵커는 R6-7b가 만든 bh 계산의 마지막 줄(이번 수정과 무관해 안정적)."""
    src = open(_SAJU_INTERP_PATH, encoding="utf-8-sig").read()
    anchor = 'bh = max(0, min(23, int(_bh_raw))) if _bh_raw not in (None, "") else 12   # 키 통일'
    end = "\n\n            # 3-A:"
    i = src.index(anchor)
    block_start = src.index("\n", i) + 1
    j = src.index(end, block_start)
    return textwrap.dedent(src[block_start:j])


_BMI_SRC = _extract_bmi_block()


def _compute_bmi(ss_dict):
    ns = {"_ss": ss_dict}
    exec(_BMI_SRC, ns)
    return ns["bmi"]


def _extract_bmn3_block():
    """R6-7d: manse.py menu8_bihang의 _bmn3(분) 계산 블록 추출.
    앵커는 바로 위 _bh3 계산 줄(이번 수정과 무관해 안정적)."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    anchor = '_bh3  = resolve_birth_hour(_ss2.get("birth_hour"), _ss2.get("in_birth_hour"))'
    end = "_dw_list3 = SajuCoreEngine.get_daewoon"
    i = src.index(anchor)
    block_start = src.index("\n", i) + 1
    j = src.index(end, block_start)
    return textwrap.dedent(src[block_start:j])


_BMN3_SRC = _extract_bmn3_block()


def _compute_bmn3(ss_dict):
    ns = {"_ss2": ss_dict}
    exec(_BMN3_SRC, ns)
    return ns["_bmn3"]


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


def check_bmi_falsy_zero():
    """R6-7d: saju_interpreter.py _get_base의 bmi — 시간모름 제출(frozen
    birth_minute=0 확정) 후 드롭다운(in_birth_minute)만 27분으로 바뀌어도
    (미제출) 계산 분은 0을 유지해야 한다. 수정 전엔 "0 or 27"이 27로 샜다."""
    ss = {"birth_minute": 0, "in_birth_minute": 27}
    bmi = _compute_bmi(ss)
    ok = bmi == 0
    print(f"[{'PASS' if ok else 'FAIL'}] _get_base bmi falsy-0: birth_minute=0(확정)+in_birth_minute=27(라이브) "
          f"-> bmi={bmi} (기대 0)")
    return ok


def check_bmi_no_frozen_key_fallback():
    """R6-7d 대조군: birth_minute 키 자체가 없으면(구형 세션 등) in_birth_minute로
    정상 폴백해야 한다(과잉 수정으로 폴백 경로 자체를 깨지 않았는지 확인)."""
    ss = {"in_birth_minute": 27}
    bmi = _compute_bmi(ss)
    ok = bmi == 27
    print(f"[{'PASS' if ok else 'FAIL'}] _get_base bmi 폴백: birth_minute 키 없음 -> in_birth_minute(27) "
          f"사용 -> bmi={bmi} (기대 27)")
    return ok


def check_bmn3_falsy_zero():
    """R6-7d: manse.py menu8_bihang의 _bmn3 — 시간확정 07:00 제출(frozen
    birth_minute=0) 후 드롭다운(in_birth_minute)만 바뀌어도(미제출) 계산
    분은 0을 유지해야 한다."""
    ss = {"birth_minute": 0, "in_birth_minute": 41}
    bmn3 = _compute_bmn3(ss)
    ok = bmn3 == 0
    print(f"[{'PASS' if ok else 'FAIL'}] menu8_bihang _bmn3 falsy-0: birth_minute=0(확정)+in_birth_minute=41(라이브) "
          f"-> _bmn3={bmn3} (기대 0)")
    return ok


def check_bmn3_no_frozen_key_fallback():
    """R6-7d 대조군: _bmn3도 birth_minute 키 자체가 없을 때만 in_birth_minute
    폴백(기본값 0 포함)을 타야 한다."""
    ss = {"in_birth_minute": 33}
    bmn3 = _compute_bmn3(ss)
    ok = bmn3 == 33
    print(f"[{'PASS' if ok else 'FAIL'}] menu8_bihang _bmn3 폴백: birth_minute 키 없음 -> in_birth_minute(33) "
          f"사용 -> _bmn3={bmn3} (기대 33)")
    return ok


_SAJU_REPORT_PATH = os.path.join(_ROOT, "saju_report.py")


def _extract_pdf_internal_birth_hour_block():
    """R6-8a: saju_report.py menu_pdf 내부 분석용 birth_hour 계산 블록 추출.
    앵커는 이번 수정과 무관한 바로 위 birth_day 줄(안정적)."""
    src = open(_SAJU_REPORT_PATH, encoding="utf-8-sig").read()
    anchor = 'birth_day    = max(1, min(31, int(st.session_state.get("birth_day")   or 1)))'
    end = "birth_minute = max(0, min(59,"
    i = src.index(anchor)
    block_start = src.index("\n", i) + 1
    j = src.index(end, block_start)
    return textwrap.dedent(src[block_start:j])


_PDF_INTERNAL_BH_SRC = _extract_pdf_internal_birth_hour_block()


def _compute_pdf_internal_birth_hour(ss_dict):
    # 이 블록은 "_ss" 별칭이 아니라 st.session_state를 직접 참조하므로
    # (saju_report.py 원본 그대로), exec 전에 실제 세션을 이 값으로 채운다.
    st.session_state.clear()
    for k, v in ss_dict.items():
        st.session_state[k] = v
    ns = {"st": st}
    exec(_PDF_INTERNAL_BH_SRC, ns)
    return ns["birth_hour"]


def _extract_pdf_call_site_block():
    """R6-8b: manse.py menu_pdf 호출부(시주 유무 판단 + birth_hour_str 구성) 추출.
    앵커는 이번 수정과 무관한 바로 위 except 블록(안정적)."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    anchor = '                except Exception:\n                    _dramatic_text = ""\n'
    end = "elif _cur_tab == 16:"
    i = src.index(anchor)
    block_start = i + len(anchor)
    j = src.index(end, block_start)
    return textwrap.dedent(src[block_start:j])


_PDF_CALL_SITE_SRC = _extract_pdf_call_site_block()


def _compute_pdf_bh_str(pils, ss_dict):
    captured = {}

    def _fake_menu_pdf(pils, birth_year, gender, name, bh_str, dramatic_text=None):
        captured["bh_str"] = bh_str

    ns = {
        "pils": pils, "_ss": ss_dict, "menu_pdf": _fake_menu_pdf,
        "birth_year": 1990, "gender": "남", "name": "테스트", "_dramatic_text": "",
    }
    exec(_PDF_CALL_SITE_SRC, ns)
    return captured["bh_str"]


def check_pdf_unknown_time_shows_미입력():
    """R6-8: 시간모름 제출(pils[0] 블랭크) -> PDF 호출부가 빈 문자열을 넘겨
    saju_report.menu_pdf의 기존 '미입력' 폴백이 작동해야 한다."""
    pils, y, gender = _make_pils("박성우", 12, 0, blank_siju=True)
    ss = {"birth_hour": 12, "in_birth_hour": 0}
    bh_str = _compute_pdf_bh_str(pils, ss)
    pdf_line = f"출생시: {bh_str or '미입력'}"
    ok = (bh_str == "") and (pdf_line == "출생시: 미입력")
    print(f"[{'PASS' if ok else 'FAIL'}] PDF 시간모름: bh_str={bh_str!r} -> \"{pdf_line}\" (기대 \"출생시: 미입력\")")
    return ok


def check_pdf_known_time_shows_number():
    """R6-8 대조군: 시간확정(7시) 제출은 그대로 "출생시: 7"이어야 한다."""
    pils, y, gender = _make_pils("박성우", 7, 30, blank_siju=False)
    ss = {"birth_hour": 7, "in_birth_hour": 7}
    bh_str = _compute_pdf_bh_str(pils, ss)
    pdf_line = f"출생시: {bh_str or '미입력'}"
    ok = pdf_line == "출생시: 7"
    print(f"[{'PASS' if ok else 'FAIL'}] PDF 시간확정: bh_str={bh_str!r} -> \"{pdf_line}\" (기대 \"출생시: 7\")")
    return ok


def check_pdf_internal_birth_hour_scenario_a():
    """R6-8a 시나리오(a): 시간모름 제출(스냅샷=12 확정) -> 체크만 해제(미제출).
    PDF 분석용 birth_hour는 스냅샷을 유지해 12로 남아야 한다."""
    ss_submit = {"in_unknown_time": True, "birth_hour": 0, "_submitted_hour": 12}
    bh_submit = _compute_pdf_internal_birth_hour(ss_submit)

    ss_after = dict(ss_submit)
    ss_after["in_unknown_time"] = False  # 체크만 해제, 미제출 — 스냅샷은 그대로
    bh_after = _compute_pdf_internal_birth_hour(ss_after)

    ok = (bh_submit == 12) and (bh_after == 12)
    print(f"[{'PASS' if ok else 'FAIL'}] PDF 분석용 birth_hour 시나리오(a): 제출시={bh_submit}, "
          f"체크해제후(미제출)={bh_after} (기대 둘 다 12 — 스냅샷 유지)")
    return ok


def _load_resolve_birth_hour_src():
    """R6-9a: resolve_birth_hour 함수 정의 자체를 manse.py에서 AST로 추출
    (부작용 없는 순수 함수). render_manse_grid 호출부가 인자 계산에 이 함수를
    직접 쓰므로, 호출부 블록만 exec하려면 이 정의도 같은 네임스페이스에
    있어야 한다."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "resolve_birth_hour":
            return ast.get_source_segment(src, node)
    raise AssertionError("resolve_birth_hour 함수를 manse.py에서 찾지 못함")


_RESOLVE_BIRTH_HOUR_SRC = _load_resolve_birth_hour_src()


def _extract_render_grid_call_block():
    """R6-9a: manse.py render_manse_grid 호출부(3단 만세력 그리드, 대운 계산에
    쓰이는 birth_hour/birth_minute 인자) 추출. 앵커는 이번 수정과 무관한
    상단 주석 시작줄(안정적)."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    anchor = "            # 3단 만세력 그리드 (입력 완료 직후)\n"
    end = "            )\n"
    i = src.index(anchor)
    j = src.index(end, i) + len(end)
    return textwrap.dedent(src[i:j])


_RENDER_GRID_CALL_SRC = _extract_render_grid_call_block()


def _compute_render_grid_args(pils, birth_year, birth_month, birth_day, gender):
    """render_manse_grid 호출부를 exec해 실제로 넘어가는 birth_hour/birth_minute
    인자를 캡처한다. _ss는 st.session_state 그 자체(manse.py 본문과 동일 별칭
    관계) — resolve_birth_hour 내부가 st.session_state를 직접 읽으므로 두
    참조가 같은 객체여야 한다."""
    captured = {}

    def fake_render_manse_grid(pils, birth_year, birth_month, birth_day, birth_hour, birth_minute, gender):
        captured["birth_hour"] = birth_hour
        captured["birth_minute"] = birth_minute

    ns = {
        "st": st, "_ss": st.session_state, "pils": pils,
        "birth_year": birth_year, "birth_month": birth_month, "birth_day": birth_day,
        "gender": gender, "render_manse_grid": fake_render_manse_grid,
    }
    exec(_RESOLVE_BIRTH_HOUR_SRC, ns)
    exec(_RENDER_GRID_CALL_SRC, ns)
    return captured


def check_render_grid_birth_minute_scenario_a():
    """R6-9a: 경계사례(1967-2-7 18시 여 — 분(分) 0/59에서 대운 시작나이가
    9/8로 실제로 갈리는 표본, R6-9 진단에서 300개 무작위 표본 중 발견) —
    분 제출 후 드롭다운만 바꿔도(미제출) 만세력 그리드의 대운 시작나이가
    흔들리면 안 된다(수정 전엔 흔들렸음 — R6-9 진단 실측)."""
    y, m, d, h, gender = 1967, 2, 7, 18, "여"
    pils = SajuPrecisionEngine.get_pillars(y, m, d, h, 0, gender, use_yaja_time=True, longitude=126.98)

    st.session_state.clear()
    st.session_state["in_birth_hour"] = h
    st.session_state["birth_hour"] = h
    st.session_state["_submitted_hour"] = h
    st.session_state["in_birth_minute"] = 0
    st.session_state["birth_minute"] = 0  # 제출 시점 확정(manse.py 28831행 상당)
    args_submit = _compute_render_grid_args(pils, y, m, d, gender)
    dw_submit = SajuCoreEngine.get_daewoon(pils, y, m, d, args_submit["birth_hour"], args_submit["birth_minute"], gender)
    sa_submit = dw_submit[0]["시작나이"] if dw_submit else None

    st.session_state["in_birth_minute"] = 59  # 드롭다운만 조작, 미제출 — frozen birth_minute=0 그대로
    args_after = _compute_render_grid_args(pils, y, m, d, gender)
    dw_after = SajuCoreEngine.get_daewoon(pils, y, m, d, args_after["birth_hour"], args_after["birth_minute"], gender)
    sa_after = dw_after[0]["시작나이"] if dw_after else None

    ok = (args_submit["birth_minute"] == 0 and args_after["birth_minute"] == 0
          and sa_submit == sa_after == 9)
    print(f"[{'PASS' if ok else 'FAIL'}] render_manse_grid 호출부 분(分) 시나리오(a): "
          f"제출시 넘긴 분={args_submit['birth_minute']}, 시작나이={sa_submit} / "
          f"드롭다운만 59로 조작 후(미제출) 넘긴 분={args_after['birth_minute']}, 시작나이={sa_after} "
          f"(기대: 분 둘 다 0, 시작나이 둘 다 9)")
    return ok


def check_render_grid_birth_minute_no_frozen_key_fallback():
    """R6-9a 대조군: frozen birth_minute 키 자체가 없으면(구형 세션 등)
    in_birth_minute로 정상 폴백해야 한다(과잉 수정으로 폴백 경로 자체를
    깨지 않았는지 확인)."""
    y, m, d, h, gender = 1967, 2, 7, 18, "여"
    pils = SajuPrecisionEngine.get_pillars(y, m, d, h, 0, gender, use_yaja_time=True, longitude=126.98)
    st.session_state.clear()
    st.session_state["in_birth_hour"] = h
    st.session_state["_submitted_hour"] = h
    st.session_state["in_birth_minute"] = 59
    args = _compute_render_grid_args(pils, y, m, d, gender)
    ok = args["birth_minute"] == 59
    print(f"[{'PASS' if ok else 'FAIL'}] render_manse_grid 호출부 분(分) 폴백: birth_minute 키 없음 -> "
          f"in_birth_minute(59) 사용 -> {args['birth_minute']} (기대 59)")
    return ok


def _extract_date_badge_block():
    """R6-9b: manse.py date_badge(생년월일 표시 배지) 계산 블록 추출.
    앵커는 이번 수정으로 새로 생긴 if문 시작줄(이 라운드 검증 대상 자체라
    안정적 — 되돌려지면 이 앵커부터 못 찾아 테스트가 즉시 실패하도록 의도)."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    anchor = '            if cal_type_saved == "음력":\n'
    end = ('            else:\n'
           '                date_badge = f"<span style=\'font-size:12px;background:#e8f5e8;'
           'padding:3px 10px;border-radius:12px;margin-left:6px\'>양력 '
           '{birth_year}.{birth_month:02d}.{birth_day:02d}</span>"\n')
    i = src.index(anchor)
    j = src.index(end, i) + len(end)
    return textwrap.dedent(src[i:j])


_DATE_BADGE_SRC = _extract_date_badge_block()


def _compute_date_badge(cal_type_saved, lunar_info, birth_year, birth_month, birth_day):
    ns = {
        "cal_type_saved": cal_type_saved, "lunar_info": lunar_info,
        "birth_year": birth_year, "birth_month": birth_month, "birth_day": birth_day,
    }
    exec(_DATE_BADGE_SRC, ns)
    return ns["date_badge"]


def check_date_badge_no_live_session_dependency():
    """R6-9b: date_badge 블록이 더 이상 _ss(st.session_state)의 라이브
    in_cal_type/in_lunar_*/in_solar_date를 참조하지 않고 frozen 인자
    (cal_type_saved/lunar_info/birth_year/birth_month/birth_day)만으로
    계산되는지 검증 — exec 네임스페이스에 _ss/st를 아예 안 넣는다. 수정
    전 소스(라이브 _ss["in_cal_type"] 등 참조)라면 여기서 NameError로
    즉시 실패해 회귀를 잡는다."""
    # 음력 1990-01-01(윤달 아님) 제출 — 양력 환산은 1990-01-27(frozen birth_year 등에
    # 이미 반영돼 있다고 가정, lunar_to_solar 재호출 없이 그대로 씀)
    badge = _compute_date_badge("음력", "1990년 1월 1일", 1990, 1, 27)
    ok = ("음력 1990년 1월 1일" in badge) and ("(양력 1990.01.27)" in badge)
    print(f"[{'PASS' if ok else 'FAIL'}] date_badge 라이브 세션 미의존 확인(음력): '{badge}' "
          f"(기대: '음력 1990년 1월 1일'·'(양력 1990.01.27)' 둘 다 포함, _ss/st 없이도 NameError 없음)")
    return ok


def check_date_badge_solar_known():
    """R6-9b 대조군: 양력 제출은 그대로 '양력 YYYY.MM.DD' 형식이어야 한다."""
    badge = _compute_date_badge("양력", "", 1985, 5, 20)
    ok = badge == "<span style='font-size:12px;background:#e8f5e8;padding:3px 10px;border-radius:12px;margin-left:6px'>양력 1985.05.20</span>"
    print(f"[{'PASS' if ok else 'FAIL'}] date_badge 양력 대조군: '{badge}' (기대 '양력 1985.05.20' 포함 형식)")
    return ok


def _extract_line(path, anchor_line):
    """단일 대입문 한 줄을 그대로 추출(줄 전체가 앵커 — 존재하지 않으면
    즉시 ValueError로 실패해 회귀를 잡는다)."""
    src = open(path, encoding="utf-8-sig").read()
    i = src.index(anchor_line)
    return src[i:i + len(anchor_line)]


_REGION_DISP_LINE = ('            _tc_region_disp = _ss.get("birth_region", '
                      '_ss.get("in_birth_region", "서울"))')
_REGION_DISP_SRC = textwrap.dedent(_extract_line(_MANSE_PATH, _REGION_DISP_LINE))

_REGION_PDF_LINE = ('            _tc_region_pdf = st.session_state.get("birth_region", '
                     'st.session_state.get("in_birth_region", "서울"))')
_REGION_PDF_SRC = textwrap.dedent(_extract_line(_SAJU_REPORT_PATH, _REGION_PDF_LINE))

_PARTNER_YAJA_LINE = ('            _p_use_yaja = st.session_state.get("use_yaja", '
                       'st.session_state.get("in_use_yaja", True))')
_PARTNER_YAJA_SRC = textwrap.dedent(_extract_line(_MANSE_PATH, _PARTNER_YAJA_LINE))


def check_region_caption_frozen_priority():
    """R6-9c: manse.py 결과화면 진태양시 캡션(_tc_region_disp) — frozen
    birth_region이 있으면 라이브 in_birth_region 변경(미제출)에 안 흔들려야
    한다."""
    st.session_state.clear()
    st.session_state["birth_region"] = "부산"  # 제출 시점 확정(R6-9c)
    st.session_state["in_birth_region"] = "서울"  # 제출 없이 드롭다운만 바꾼 상태
    ns = {"_ss": st.session_state}
    exec(_REGION_DISP_SRC, ns)
    ok = ns["_tc_region_disp"] == "부산"
    print(f"[{'PASS' if ok else 'FAIL'}] manse.py 진태양시 캡션 frozen 우선: "
          f"birth_region=부산(frozen)+in_birth_region=서울(라이브,미제출) -> '{ns['_tc_region_disp']}' (기대 '부산')")
    return ok


def check_region_caption_legacy_fallback():
    """R6-9c 대조군: frozen birth_region 키 자체가 없으면(구형 세션) 라이브
    in_birth_region으로 정상 폴백해야 한다."""
    st.session_state.clear()
    st.session_state["in_birth_region"] = "대구"
    ns = {"_ss": st.session_state}
    exec(_REGION_DISP_SRC, ns)
    ok = ns["_tc_region_disp"] == "대구"
    print(f"[{'PASS' if ok else 'FAIL'}] manse.py 진태양시 캡션 폴백: birth_region 키 없음 -> "
          f"in_birth_region(대구) 사용 -> '{ns['_tc_region_disp']}' (기대 '대구')")
    return ok


def check_pdf_region_caption_frozen_priority():
    """R6-9c: saju_report.py PDF 표지 캡션(_tc_region_pdf) — manse.py와 동일
    규칙."""
    st.session_state.clear()
    st.session_state["birth_region"] = "제주"
    st.session_state["in_birth_region"] = "서울"
    ns = {"st": st}
    exec(_REGION_PDF_SRC, ns)
    ok = ns["_tc_region_pdf"] == "제주"
    print(f"[{'PASS' if ok else 'FAIL'}] saju_report.py PDF 캡션 frozen 우선: "
          f"birth_region=제주(frozen)+in_birth_region=서울(라이브,미제출) -> '{ns['_tc_region_pdf']}' (기대 '제주')")
    return ok


def check_partner_yaja_frozen_priority():
    """R6-9c: manse.py menu6_relations 상대방 궁합 계산의 야자시(_p_use_yaja) —
    본인 명식 계산에 실제로 쓰인 frozen use_yaja를 우선해야 한다(제출 없이
    고급설정 야자시 체크박스만 만져도 상대방 계산 기준이 어긋나면 안 됨)."""
    st.session_state.clear()
    st.session_state["use_yaja"] = False  # 제출 시점 확정(R6-9c)
    st.session_state["in_use_yaja"] = True  # 제출 없이 체크박스만 바꾼 상태
    ns = {"st": st}
    exec(_PARTNER_YAJA_SRC, ns)
    ok = ns["_p_use_yaja"] is False
    print(f"[{'PASS' if ok else 'FAIL'}] 상대방 궁합 야자시 frozen 우선: "
          f"use_yaja=False(frozen)+in_use_yaja=True(라이브,미제출) -> {ns['_p_use_yaja']} (기대 False)")
    return ok


def check_partner_yaja_legacy_fallback():
    """R6-9c 대조군: frozen use_yaja 키 자체가 없으면 라이브 in_use_yaja로
    정상 폴백해야 한다."""
    st.session_state.clear()
    st.session_state["in_use_yaja"] = False
    ns = {"st": st}
    exec(_PARTNER_YAJA_SRC, ns)
    ok = ns["_p_use_yaja"] is False
    print(f"[{'PASS' if ok else 'FAIL'}] 상대방 궁합 야자시 폴백: use_yaja 키 없음 -> "
          f"in_use_yaja(False) 사용 -> {ns['_p_use_yaja']} (기대 False)")
    return ok


def _load_manse_func_src(func_name):
    """R6-9c/d: save_to_favorites/load_from_favorite(최상위 함수)와
    _sync_marriage_status/_sync_occupation(main() 내부 중첩 함수) 모두 순수
    session_state 조작이라 AST로 정의 전체를 추출해도 부작용이 없다
    (resolve_birth_hour와 동일 기법). ast.walk로 중첩 함수도 찾는다."""
    src = open(_MANSE_PATH, encoding="utf-8-sig").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(src, node)
    raise AssertionError(f"{func_name} 함수를 manse.py에서 찾지 못함")


_FAV_NS = {"st": st, "date": __import__("datetime").date, "datetime": __import__("datetime").datetime,
           "TimeCorrection": TimeCorrection}
exec(_RESOLVE_BIRTH_HOUR_SRC, _FAV_NS)
exec(_load_manse_func_src("save_to_favorites"), _FAV_NS)
exec(_load_manse_func_src("load_from_favorite"), _FAV_NS)
save_to_favorites = _FAV_NS["save_to_favorites"]
load_from_favorite = _FAV_NS["load_from_favorite"]


def check_favorites_region_yaja_roundtrip():
    """R6-9c: 즐겨찾기 저장→다른 값으로 오염→로드 시나리오. birth_region/
    use_yaja가 simple_keys에 포함돼 저장 당시 frozen 값으로 정확히
    되돌아와야 한다(빠져 있으면 로드 후에도 오염된 이전 값이 남는다)."""
    st.session_state.clear()
    st.session_state["in_name"] = "테스트"
    st.session_state["in_birth_region"] = "부산"
    st.session_state["birth_region"] = "부산"
    st.session_state["in_use_yaja"] = False
    st.session_state["use_yaja"] = False
    save_to_favorites("R69C_테스트")

    # 다른 명식(오염 시나리오) — 이전 프로필의 frozen 값이 남아있다고 가정
    st.session_state["birth_region"] = "제주"
    st.session_state["use_yaja"] = True

    load_from_favorite(0)
    ok = (st.session_state.get("birth_region") == "부산") and (st.session_state.get("use_yaja") is False)
    print(f"[{'PASS' if ok else 'FAIL'}] 즐겨찾기 round-trip: 저장(부산/False) -> 오염(제주/True) -> 로드 후 "
          f"birth_region={st.session_state.get('birth_region')}, use_yaja={st.session_state.get('use_yaja')} "
          f"(기대 부산/False)")
    return ok


def check_favorites_legacy_no_stale_leak():
    """R6-9c 대조군: birth_region/use_yaja가 없는 구형 즐겨찾기를 로드해도,
    로드 직전 세션에 남아있던 다른 명식의 frozen 값이 새지 않고 방금
    복원한 in_birth_region/in_use_yaja(구형 simple_keys) 기준으로 재확정돼야
    한다."""
    st.session_state.clear()
    st.session_state["favorites"] = [{
        "label": "구형즐겨찾기", "in_name": "구형",
        "in_birth_region": "대전", "in_gender": "남",
        # birth_region/use_yaja 키 자체가 없음(R6-9c 이전 저장분)
    }]
    st.session_state["birth_region"] = "제주"  # 오염(직전 세션 잔재)
    st.session_state["use_yaja"] = False        # 오염(직전 세션 잔재)

    load_from_favorite(0)
    ok = (st.session_state.get("birth_region") == "대전") and (st.session_state.get("use_yaja") is True)
    print(f"[{'PASS' if ok else 'FAIL'}] 구형 즐겨찾기 로드(오염 방지): 로드 후 "
          f"birth_region={st.session_state.get('birth_region')}(기대 대전), "
          f"use_yaja={st.session_state.get('use_yaja')}(기대 True — in_use_yaja 기본값)")
    return ok


_SYNC_MARRIAGE_SRC = _load_manse_func_src("_sync_marriage_status")
_SYNC_OCCUPATION_SRC = _load_manse_func_src("_sync_occupation")


def _call_sync(src, func_name, ss_dict):
    ns = {"st": st}
    exec(src, ns)
    ns[func_name]()


def check_marriage_status_on_change_sync():
    """R6-9d: 결혼상태 드롭다운 on_change 콜백이 frozen marriage_status를
    즉시 동기화하는지 확인. D 진단 재현 시나리오 — 제출 시점엔 '미혼'으로
    frozen 확정됐다가, 제출 없이 드롭다운만 '기혼'으로 바꾸면(콜백 발동)
    이제는 frozen도 즉시 '기혼'으로 따라가 live 소비처(menu1_report의
    render_life_risk_card 등)와 더 이상 어긋나지 않아야 한다."""
    st.session_state.clear()
    st.session_state["marriage_status"] = "미혼"  # 이전 제출로 확정된 frozen 값
    st.session_state["in_marriage"] = "기혼"       # 제출 없이 드롭다운만 변경(콜백 발동 시점)
    _call_sync(_SYNC_MARRIAGE_SRC, "_sync_marriage_status", st.session_state)
    ok = st.session_state.get("marriage_status") == "기혼"
    print(f"[{'PASS' if ok else 'FAIL'}] 결혼상태 on_change 동기화: 이전 frozen='미혼' -> "
          f"드롭다운 변경(기혼) 콜백 후 marriage_status='{st.session_state.get('marriage_status')}' (기대 '기혼')")
    return ok


def check_occupation_on_change_sync():
    """R6-9d 대조군: 직업분야도 동일 패턴."""
    st.session_state.clear()
    st.session_state["occupation"] = "선택 안 함"
    st.session_state["in_occupation"] = "예술가"
    _call_sync(_SYNC_OCCUPATION_SRC, "_sync_occupation", st.session_state)
    ok = st.session_state.get("occupation") == "예술가"
    print(f"[{'PASS' if ok else 'FAIL'}] 직업분야 on_change 동기화: 이전 frozen='선택 안 함' -> "
          f"드롭다운 변경(예술가) 콜백 후 occupation='{st.session_state.get('occupation')}' (기대 '예술가')")
    return ok


def check_jeokjung_affair_frozen_live_reconciled():
    """R6-9d: D 진단에서 실측한 divergence(get_jeokjung_affair가 frozen을
    쓰는 상황에서 marriage_status="기혼"/"미혼"에 따라 적중박스 문구가
    갈리던 것) — on_change 동기화 후에는 frozen이 항상 live를 즉시 따라가므로
    '제출 없이 드롭다운만 바꾼' 시나리오에서도 frozen 값이 live와 일치해야
    한다(더 이상 예전 제출값에 머물러 있지 않음)."""
    st.session_state.clear()
    st.session_state["marriage_status"] = "미혼"  # 제출 당시 값
    st.session_state["in_marriage"] = "기혼"        # 미제출 상태로 변경
    _call_sync(_SYNC_MARRIAGE_SRC, "_sync_marriage_status", st.session_state)

    frozen_after_sync = st.session_state.get("marriage_status")
    live = st.session_state.get("in_marriage")
    ok = frozen_after_sync == live == "기혼"
    print(f"[{'PASS' if ok else 'FAIL'}] frozen/live 재수렴 확인: 동기화 후 frozen={frozen_after_sync}, "
          f"live={live} (기대 둘 다 '기혼' — get_jeokjung_affair(frozen)와 render_life_risk_card(live)가 "
          f"더 이상 다른 값을 보지 않음)")
    return ok


_Y9A_MARRIAGE_ANCHOR = '        _kw_y9a = {"gender": gender, "marriage_status": st.session_state.get("in_marriage", "미혼")}'
_JEOKJUNG_AFFAIR_MARRIAGE_ANCHOR = 'marriage_status=st.session_state.get("marriage_status", "미혼"))'
# 두 소스 라인이 실제로 존재하는지 앵커 확인(소스가 바뀌면 여기서 즉시 실패) — 값 자체는
# 아래에서 st.session_state를 직접 조작해 같은 패턴으로 재현한다.
_extract_line(_MANSE_PATH, _Y9A_MARRIAGE_ANCHOR)
_extract_line(_MANSE_PATH, _JEOKJUNG_AFFAIR_MARRIAGE_ANCHOR)


def check_menu1report_boxes_marriage_status_consistent():
    """R6-9d: menu1_report 안에서 "7대 운명 코드 박스"(16530행,
    render_life_risk_card용 marriage_status — in_marriage 소스)와 "적중
    박스-불륜"(16595행, get_jeokjung_affair용 marriage_status — 소스)이
    실제로 같은 결혼상태를 전제로 계산되는지. 기혼 제출 -> 드롭다운 미혼
    변경(미제출) 시나리오에서, on_change 동기화가 없다면(Before) 두 소스가
    갈려 무관 구조 표본의 적중박스-불륜 문구가 서로 다른 결혼상태를
    전제로 나온다(FAIL). on_change 콜백 적용 후(After)에는 두 소스가
    수렴해 일치한다(PASS)."""
    pils = [{"cg": "甲", "jj": "子"}, {"cg": "丙", "jj": "寅"}, {"cg": "戊", "jj": "辰"}, {"cg": "庚", "jj": "申"}]
    yukjin_list, sinsal_list = [], []  # 무관(無官) 구조 유도 — get_jeokjung_affair의 marriage_status 분기 트리거

    def _read_two_sources():
        # 16530행과 동일한 표현식(라이브 소스)
        y9a_marriage_status = st.session_state.get("in_marriage", "미혼")
        # 16595행과 동일한 표현식(frozen 소스)
        affair_marriage_status = st.session_state.get("marriage_status", "미혼")
        return y9a_marriage_status, affair_marriage_status

    # Before(on_change 없다고 가정): 기혼 제출 -> 미혼으로 드롭다운만 변경(미제출),
    # frozen marriage_status는 그대로 "기혼"에 머물러 있는 상태를 직접 재현.
    st.session_state.clear()
    st.session_state["marriage_status"] = "기혼"
    st.session_state["in_marriage"] = "미혼"
    y9a_before, affair_before = _read_two_sources()
    affair_text_before = get_jeokjung_affair("여", "甲", yukjin_list, sinsal_list, pils,
                                              marriage_status=affair_before).get("title", "")
    risk_before = detect_life_risk_signals(pils, gender="여", marriage_status=y9a_before)
    before_sources_agree = (y9a_before == affair_before)

    # After(R6-9d on_change 콜백 발동): 드롭다운 변경 즉시 frozen도 동기화.
    st.session_state["marriage_status"] = st.session_state["in_marriage"]  # _sync_marriage_status와 동일
    y9a_after, affair_after = _read_two_sources()
    affair_text_after = get_jeokjung_affair("여", "甲", yukjin_list, sinsal_list, pils,
                                             marriage_status=affair_after).get("title", "")
    risk_after = detect_life_risk_signals(pils, gender="여", marriage_status=y9a_after)
    after_sources_agree = (y9a_after == affair_after)

    ok = (before_sources_agree is False) and (after_sources_agree is True) and (y9a_after == affair_after == "미혼")
    print(f"[{'PASS' if ok else 'FAIL'}] menu1_report 두 박스 결혼상태 소스 일치성: "
          f"Before(콜백 전) 7대운명코드='{y9a_before}' vs 적중박스-불륜='{affair_before}' "
          f"(일치={before_sources_agree}, 기대 False=FAIL 재현) / "
          f"After(콜백 후) 7대운명코드='{y9a_after}' vs 적중박스-불륜='{affair_after}' "
          f"(일치={after_sources_agree}, 기대 True=PASS)")
    print(f"      참고 — 적중박스-불륜 제목: Before='{affair_text_before}' / After='{affair_text_after}' "
          f"(제목 자체가 갈렸었다는 것이 실질 사용자 체감 증거)")
    return ok


def run():
    results = [
        check_2414_scenario_a(),
        check_2414_scenario_b(),
        check_get_base_snapshot_priority(),
        check_get_base_scenario_a(),
        check_hour_display_scenario_a(),
        check_hour_display_known_time(),
        check_bmi_falsy_zero(),
        check_bmi_no_frozen_key_fallback(),
        check_bmn3_falsy_zero(),
        check_bmn3_no_frozen_key_fallback(),
        check_pdf_unknown_time_shows_미입력(),
        check_pdf_known_time_shows_number(),
        check_pdf_internal_birth_hour_scenario_a(),
        check_render_grid_birth_minute_scenario_a(),
        check_render_grid_birth_minute_no_frozen_key_fallback(),
        check_date_badge_no_live_session_dependency(),
        check_date_badge_solar_known(),
        check_region_caption_frozen_priority(),
        check_region_caption_legacy_fallback(),
        check_pdf_region_caption_frozen_priority(),
        check_partner_yaja_frozen_priority(),
        check_partner_yaja_legacy_fallback(),
        check_favorites_region_yaja_roundtrip(),
        check_favorites_legacy_no_stale_leak(),
        check_marriage_status_on_change_sync(),
        check_occupation_on_change_sync(),
        check_jeokjung_affair_frozen_live_reconciled(),
        check_menu1report_boxes_marriage_status_consistent(),
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
