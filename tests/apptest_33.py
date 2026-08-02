#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests/apptest_33.py — N케이스 × 11메뉴 검증 하네스 (예외 0건 / 출력 스냅샷 / 골든값 회귀)

- 케이스는 tests/pils_fixtures.py의 CASES를 그대로 재사용한다(값 복제 금지).
  조합 수는 하드코딩하지 않고 len(CASES) × len(MENU_ORDER)로 매번 계산한다.
  지금은 박성우·박후규 2케이스 = 22조합. 윤미연 등이 CASES에 추가되면
  이 파일을 고치지 않아도 자동으로 33조합이 된다.
- manse.py 등 기존 앱 파일은 import만 하고 절대 수정하지 않는다
  (main()은 `if __name__ == "__main__"` 가드 안에 있어 import만으로는 실행되지 않음).
- st.markdown 등 텍스트 출력 함수는 런타임에만 monkeypatch로 가로채 캡처한다
  (manse.py 소스 변경 아님, 이 프로세스 안에서만 유효).

사용법:
    python tests/apptest_33.py --dump    tests/snapshots/baseline.json
    python tests/apptest_33.py --compare tests/snapshots/baseline.json
    python tests/apptest_33.py --dump    tests/snapshots/baseline.json --freeze-date 2026-08-01
    python tests/apptest_33.py --compare tests/snapshots/baseline.json  # --freeze-date 생략 시
                                                                          # baseline meta의 freeze_date
                                                                          # 자동 적용(재현성 보장)

종료코드: 예외 발생(어느 모드든) 또는 --compare에서 차이 발견 시 1, 정상 0.

━━ 비교 제외/주의가 필요한 필드 ━━
1) menu10_monthly(월별운세)의 이번 주 요약 날짜 라벨
   (manse.py 원본 L22742/L22794 부근: `d_str = ....strftime("%m/%d")`)
   — 실행한 "오늘"이 무슨 요일이냐에 따라 MM/DD 값이 매번 바뀐다.
   순수 표시용 라벨이라 회귀 판단에 의미가 없으므로 비교 시 <MMDD>로 치환해 제외한다.
   (아래 _VOLATILE_PATTERNS)
2) menu9_daily(일일운세)는 `today = datetime.now()` 기준 "오늘의 일진"을 계산하는
   메뉴 자체의 목적이 매일 다른 값을 보여주는 것이므로, 실행한 날짜가 다르면
   전체 출력이 통째로 달라지는 게 정상이다. 이 필드는 내용 자체가 매일 바뀌는 게
   설계 의도라 문자열 치환으로 제외하지 않는다 — daily 메뉴의 --compare 차이는
   "그 날짜의 일진 계산이 맞는지"를 사람이 별도로 판단해야 한다(자동 PASS/FAIL 아님).
3) 그 외 current_year/target_year 계열 값(예: "올해 2026년" 라벨)은 의도적으로
   비교 대상에 그대로 둔다 — 3-C(세운 연도 입춘 통일) 작업이 실제로 어떤 탭의
   출력을 바꾸는지 이 스냅샷으로 드러나야 하기 때문. 이 값들이 바뀌면 --compare가
   차이를 보고하는 게 정상이며, 그 경우 내용을 확인한 뒤 --dump로 베이스라인을
   의식적으로 갱신한다.
"""
import sys
import os
import re
import json
import argparse
import difflib
from datetime import date, datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_THIS_DIR)
sys.path.insert(0, _ROOT)      # manse, saju_engine, saju_interpreter, saju_sinsal
sys.path.insert(0, _THIS_DIR)  # pils_fixtures

import streamlit as st  # noqa: E402
import manse  # noqa: E402  (import만 함 — main()은 __main__ 가드 안이라 실행되지 않음)
import saju_interpreter  # noqa: E402  (freeze 대상 — .datetime 이름 교체용, 모듈 자체 참조 필요)
from pils_fixtures import CASES, get_pils  # noqa: E402  (값 재사용, 복제 금지)
from saju_engine import calc_sipsung, SajuCoreEngine  # noqa: E402
from saju_interpreter import get_jeokjung_guiin  # noqa: E402
from saju_sinsal import get_gongmang  # noqa: E402


# 11메뉴 — 그동안 33조합 검증에 쓰던 목록 그대로
MENU_ORDER = [
    "menu1_report", "current_situation", "lifeline", "past", "future3",
    "money", "relations", "daily", "monthly", "yearly", "tojeong",
]

# 텍스트 출력 계열 st.* 함수 — 캡처 대상(런타임 monkeypatch, 소스 수정 아님)
_CAPTURE_FUNCS = [
    "markdown", "write", "error", "warning", "info", "success",
    "subheader", "header", "title", "caption", "text", "code",
    "metric", "json", "toast",
]

# 매번 바뀌어 비교가 항상 실패하는 순수 표시용 필드 — 위 docstring 1) 참고
_VOLATILE_PATTERNS = [
    (re.compile(r"\b\d{1,2}/\d{1,2}\b"), "<MMDD>"),
]


# ── freeze-time 인프라 ───────────────────────────────────────────────────
# daily/monthly/money/④대운시제(build_saju_tongbyeon)가 "오늘"을 읽는 경로는
# manse.py·saju_interpreter.py 모듈레벨 datetime/date 이름(둘 다 `from datetime
# import date, datetime`) 두 개로 수렴한다. datetime만 패치했을 때 daily·monthly가
# LocalSajuNarrator.daily()/monthly()(saju_interpreter.py) 안의 별도 `date.today()`
# 호출을 못 잡아 실제 오늘 날짜가 새는 버그가 실측으로 드러나서(재생성 baseline의
# daily 헤더가 freeze-date가 아니라 진짜 오늘로 찍힘), datetime과 date를 둘 다
# 패치하도록 고쳤다. manse.py/saju_interpreter.py 소스는 무수정 — import된 모듈
# 네임스페이스의 이름만 이 테스트 프로세스 안에서 갈아끼운다(다른 프로세스인 실제
# 앱 런타임은 영향 없음).
_REAL_DATETIME = datetime
_REAL_DATE = date


class FrozenDatetime(_REAL_DATETIME):
    """now()/today()만 고정 시각을 반환. 그 외는 datetime.datetime 그대로 상속되어
    strftime·비교·timedelta 연산 등 정상 동작(freeze 프로토타입에서 검증됨)."""
    _frozen = None

    @classmethod
    def now(cls, tz=None):
        return cls._frozen if tz is None else cls._frozen.astimezone(tz)

    @classmethod
    def today(cls):
        return cls._frozen


class FrozenDate(_REAL_DATE):
    """date.today()만 고정 날짜 반환. LocalSajuNarrator.daily()/monthly()가 쓰는
    `date.today()` 경로 전용(datetime과는 별개 클래스라 따로 패치 필요)."""
    _frozen = None

    @classmethod
    def today(cls):
        return cls._frozen


def freeze(freeze_date):
    """freeze_date: 'YYYY-MM-DD' 문자열. manse.datetime/date·saju_interpreter.
    datetime/date를 FrozenDatetime/FrozenDate로 교체한다."""
    y, m, d = (int(x) for x in freeze_date.split("-"))
    FrozenDatetime._frozen = _REAL_DATETIME(y, m, d, 12, 0, 0)
    FrozenDate._frozen = _REAL_DATE(y, m, d)
    manse.datetime = FrozenDatetime
    manse.date = FrozenDate
    saju_interpreter.datetime = FrozenDatetime
    saju_interpreter.date = FrozenDate


def unfreeze():
    """freeze() 이전 상태(실제 datetime.datetime/date)로 복원."""
    manse.datetime = _REAL_DATETIME
    manse.date = _REAL_DATE
    saju_interpreter.datetime = _REAL_DATETIME
    saju_interpreter.date = _REAL_DATE


class _Capturer:
    """st.markdown 등을 일시적으로 감싸 호출 인자를 기록한다. __exit__에서 원복."""

    def __init__(self):
        self.buf = []
        self._originals = {}

    def __enter__(self):
        for fn_name in _CAPTURE_FUNCS:
            orig = getattr(st, fn_name)
            self._originals[fn_name] = orig
            self._wrap(fn_name, orig)
        return self

    def _wrap(self, fn_name, orig):
        def wrapper(*args, **kwargs):
            self.buf.append(f"{fn_name}|{args!r}|{sorted(kwargs.items())!r}")
            try:
                return orig(*args, **kwargs)
            except Exception:
                return None
        setattr(st, fn_name, wrapper)

    def __exit__(self, exc_type, exc, tb):
        for fn_name, orig in self._originals.items():
            setattr(st, fn_name, orig)
        return False


def _call_menu(menu_key, pils, case_name, birth_year, gender):
    if menu_key == "menu1_report":
        manse.menu1_report(pils, case_name, birth_year, gender, "선택 안 함")
    elif menu_key == "current_situation":
        manse.menu_current_situation(pils, case_name, birth_year, gender, "미혼")
    elif menu_key == "lifeline":
        manse.menu2_lifeline(pils, birth_year, gender, case_name)
    elif menu_key == "past":
        manse.menu3_past(pils, birth_year, gender, case_name)
    elif menu_key == "future3":
        manse.menu4_future3(pils, birth_year, gender, "미혼", case_name)
    elif menu_key == "money":
        manse.menu5_money(pils, birth_year, gender, case_name)
    elif menu_key == "relations":
        manse.menu6_relations(pils, case_name, birth_year, gender, "미혼")
    elif menu_key == "daily":
        manse.menu9_daily(pils, case_name, birth_year, gender)
    elif menu_key == "monthly":
        manse.menu10_monthly(pils, case_name, birth_year, gender)
    elif menu_key == "yearly":
        manse.menu_yearly(pils, case_name, birth_year, gender)
    elif menu_key == "tojeong":
        manse.menu_tojeong(pils, case_name, birth_year, gender)
    else:
        raise ValueError(f"알 수 없는 menu_key: {menu_key}")


def _run_combo(menu_key, pils, case_name, birth_year, m, d, h, mi, gender):
    st.session_state["birth_month"] = m
    st.session_state["birth_day"] = d
    st.session_state["birth_hour"] = h
    st.session_state["birth_minute"] = mi
    st.session_state["marriage_status"] = "미혼"
    st.session_state["in_marriage"] = "미혼"
    st.session_state["partner_pils"] = None

    exc_msg = None
    cap = _Capturer()
    with cap:
        try:
            _call_menu(menu_key, pils, case_name, birth_year, gender)
        except Exception as e:
            exc_msg = f"{type(e).__name__}: {e}"
    return cap.buf, exc_msg


def run_all():
    """CASES × MENU_ORDER 전 조합 실행. (results dict, 예외 발생 건수) 반환."""
    results = {}
    exc_count = 0
    for case_name in CASES:
        case = CASES[case_name]
        y, m, d, h, mi = case["birth"]
        gender = case["gender"]
        pils = get_pils(case_name)
        results[case_name] = {}
        for menu_key in MENU_ORDER:
            output, exc = _run_combo(menu_key, pils, case_name, y, m, d, h, mi, gender)
            if exc:
                exc_count += 1
            results[case_name][menu_key] = {"output": output, "exception": exc}
    return results, exc_count


def _normalize(entry):
    for pat, repl in _VOLATILE_PATTERNS:
        entry = pat.sub(repl, entry)
    return entry


def dump(path, freeze_date=None):
    if freeze_date:
        freeze(freeze_date)
    try:
        results, exc_count = run_all()
    finally:
        if freeze_date:
            unfreeze()
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    payload = {
        "meta": {
            "case_count": len(CASES),
            "menu_count": len(MENU_ORDER),
            "combo_count": len(CASES) * len(MENU_ORDER),
            "cases": list(CASES.keys()),
            "menus": MENU_ORDER,
            "freeze_date": freeze_date,  # None이면 미고정 실행(현행 동작과 동일)
        },
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"[DUMP] 저장 완료: {path}" + (f" (freeze_date={freeze_date})" if freeze_date else " (freeze 미적용)"))
    if exc_count:
        print(f"[FAIL] 예외 {exc_count}건 발생")
    else:
        print("[OK] 예외 0건")
    return exc_count


def compare(path, freeze_date=None):
    with open(path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    baseline_freeze = baseline.get("meta", {}).get("freeze_date")
    if freeze_date and baseline_freeze and freeze_date != baseline_freeze:
        print(f"[WARN] --freeze-date({freeze_date})가 baseline meta의 freeze_date({baseline_freeze})와 "
              f"다릅니다 — CLI 값({freeze_date})을 우선 적용합니다.")
    effective_freeze = freeze_date or baseline_freeze
    if effective_freeze:
        print(f"[FREEZE] {effective_freeze} 기준으로 고정 실행"
              + (" (baseline meta에서 자동 적용)" if not freeze_date else ""))
        freeze(effective_freeze)
    try:
        current, exc_count = run_all()
    finally:
        if effective_freeze:
            unfreeze()

    base_results = baseline.get("results", {})
    diff_count = 0
    all_cases = sorted(set(base_results) | set(current))
    for case_name in all_cases:
        base_menus = base_results.get(case_name, {})
        cur_menus = current.get(case_name, {})
        all_menus = sorted(set(base_menus) | set(cur_menus))
        for menu_key in all_menus:
            b = base_menus.get(menu_key)
            c = cur_menus.get(menu_key)
            if b is None:
                print(f"[NEW] {case_name}/{menu_key} — baseline에 없는 신규 조합 (--dump로 갱신 필요)")
                diff_count += 1
                continue
            if c is None:
                print(f"[MISSING] {case_name}/{menu_key} — 이번 실행에 없음")
                diff_count += 1
                continue
            if bool(b.get("exception")) != bool(c.get("exception")):
                print(f"[DIFF] {case_name}/{menu_key} — 예외 상태 변경: "
                      f"{b.get('exception')!r} -> {c.get('exception')!r}")
                diff_count += 1
                continue
            b_norm = [_normalize(x) for x in b.get("output", [])]
            c_norm = [_normalize(x) for x in c.get("output", [])]
            if b_norm != c_norm:
                diff_count += 1
                print(f"[DIFF] {case_name}/{menu_key} — 출력 차이 발견")
                udiff = list(difflib.unified_diff(b_norm, c_norm, lineterm="", n=0))
                for line in udiff[:10]:
                    print("    " + line)
                if len(udiff) > 10:
                    print(f"    ... ({len(udiff) - 10}줄 더 있음)")

    if exc_count:
        print(f"[FAIL] 예외 {exc_count}건 발생")
    else:
        print("[OK] 예외 0건")

    if diff_count == 0:
        print("[OK] 차이 0건")
    else:
        print(f"[FAIL] 차이 {diff_count}건 발견")

    return diff_count, exc_count


def _classify_line2(pils, ilgan, cur_year):
    """get_jeokjung_guiin의 line2를 live(內藏)/sealed(공망 봉인)/external로 3분기."""
    yukjin_raw = calc_sipsung(ilgan, pils)
    yukjin_list = []
    for s in yukjin_raw:
        if s.get("cg_ss", "-") != "-":
            yukjin_list.append({"관계": s["cg_ss"]})
        if s.get("jj_ss", "-") != "-":
            yukjin_list.append({"관계": s["jj_ss"]})
    gm = get_gongmang(pils).get("공망_지지") or ()
    result = get_jeokjung_guiin(ilgan, pils, yukjin_list, cur_year, gm)
    line2 = result.get("line2", "")
    if "內藏" in line2:
        return "live"
    if "잠들어" in line2:
        return "sealed"
    return "external"


def _golden_checks():
    """케이스별 골든값 회귀 체크. CASES에 없는 케이스의 항목은 자동 skip(에러 아님)."""
    out = []

    def _add(name, ok, detail):
        out.append((name, ok, detail))

    if "박성우" in CASES:
        case = CASES["박성우"]
        y, m, d, h, mi = case["birth"]
        gender = case["gender"]
        pils = get_pils("박성우")
        ilgan = pils[1]["cg"]

        dw = SajuCoreEngine.get_daewoon(pils, y, m, d, h, mi, gender=gender)
        dw_years = [x.get("시작연도") for x in dw[:3]]
        _add("[박성우] 대운 시작연도", dw_years == [1971, 1981, 1991],
             f"실제={dw_years} 기대=[1971, 1981, 1991]")

        golden_luck = {2019: 95, 2023: 75, 2025: 85, 2026: 60, 2027: 95, 2030: 85}
        for ty, expect in golden_luck.items():
            actual = manse.calc_luck_score(pils, y, gender, bm=m, bd=d, bh=h, bmi=mi, target_year=ty)
            _add(f"[박성우] calc_luck_score({ty})", actual == expect, f"실제={actual} 기대={expect}")

        gm_str = "".join(get_gongmang(pils).get("공망_지지", ("", "")))
        _add("[박성우] 공망", gm_str == "午未", f"실제={gm_str} 기대=午未")
        _add("[박성우] 일간", ilgan == "庚", f"실제={ilgan} 기대=庚")

        cls = _classify_line2(pils, ilgan, y)
        _add("[박성우] line2 분기", cls == "sealed", f"실제={cls} 기대=sealed")
    else:
        out.append(("[박성우] 전체", None, "CASES에 없어 skip"))

    if "박후규" in CASES:
        case = CASES["박후규"]
        y, m, d, h, mi = case["birth"]
        pils = get_pils("박후규")
        ilgan = pils[1]["cg"]

        cls = _classify_line2(pils, ilgan, y)
        _add("[박후규] line2 분기", cls == "live", f"실제={cls} 기대=live(內藏)")

        gm_str = "".join(get_gongmang(pils).get("공망_지지", ("", "")))
        _add("[박후규] 공망", gm_str == "寅卯", f"실제={gm_str} 기대=寅卯")
    else:
        out.append(("[박후규] 전체", None, "CASES에 없어 skip"))

    # ---- 윤미연: 생일 미확정(tests/pils_fixtures.py TODO) — CASES에 확정 추가되면 주석 해제 ----
    # if "윤미연" in CASES:
    #     case = CASES["윤미연"]
    #     y, m, d, h, mi = case["birth"]
    #     pils = get_pils("윤미연")
    #     ilgan = pils[1]["cg"]
    #     cls = _classify_line2(pils, ilgan, y)
    #     _add("[윤미연] line2 분기", cls == "live", f"실제={cls} 기대=live(內藏)")

    return out


def main():
    print(f"{len(CASES)}케이스 × {len(MENU_ORDER)}메뉴 = {len(CASES) * len(MENU_ORDER)}조합")

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dump", metavar="PATH")
    group.add_argument("--compare", metavar="PATH")
    parser.add_argument(
        "--freeze-date", metavar="YYYY-MM-DD", default=None,
        help="현재 시각을 이 날짜로 고정하고 실행(daily/monthly/money/④대운시제 노이즈 제거용). "
             "미지정 시 실제 현재 시각 사용(현행 동작과 동일, 하위호환). --compare에서 미지정 시 "
             "baseline meta의 freeze_date를 자동으로 읽어 재현한다.",
    )
    args = parser.parse_args()

    exit_code = 0

    if args.dump:
        exc_count = dump(args.dump, freeze_date=args.freeze_date)
        if exc_count:
            exit_code = 1
    else:
        diff_count, exc_count = compare(args.compare, freeze_date=args.freeze_date)
        if exc_count or diff_count:
            exit_code = 1

    print("\n=== 골든값 회귀 검사 ===")
    golden_fail = 0
    golden_skip = 0
    for name, ok, detail in _golden_checks():
        if ok is None:
            golden_skip += 1
            print(f"[SKIP] {name}: {detail}")
            continue
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not ok:
            golden_fail += 1
    if golden_fail:
        print(f"[FAIL] 골든값 {golden_fail}건 불일치")
        exit_code = 1
    else:
        print(f"[OK] 골든값 전부 통과 (skip {golden_skip}건)")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
