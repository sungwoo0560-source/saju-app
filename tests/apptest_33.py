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
4) "박후규_시간모름_grid"(R6-2, 2026-09-24 추가) 케이스의 manse_grid 골든에는
   당시 알려진 결함 2건이 "정답"으로 그대로 구워져 있었다:
   (a) STRENGTH_DESC(saju_data.py)에 "극신강(極身强)"/"극신약(極身弱)" 키가 없어
       신강신약이 극단 판정일 때 성격 설명 줄이 빈 <div></div>로 렌더되는 결함
       — **미해결**. 고치면 이 케이스의 manse_grid 골든값이 바뀌는 게 정상이다.
   (b) render_manse_grid 자체 대운 계산(manse.py:24740)이 호출부(29093)에서
       resolve_birth_hour를 거치지 않은 raw birth_hour를 받던 결함(eb878f8의
       17곳 정리에서 누락, R6-3에서 원인 추적) — **R6-4(2026-09-24)에서 해소**.
       29093 호출부에 resolve_birth_hour(in_birth_hour, birth_hour)를 적용했고,
       이 케이스(박후규, birth_hour=12 고정)는 이미 12시라 골든값 변화 없음
       (실제 변화는 birth_hour가 0 등 다른 값일 때만 나타남 — R6-4 보고의
       Before/After 실측 참고). apptest 픽스처만으로는 이 수정을 증명할 수
       없다(--compare가 항상 0을 보고함, 아래 참고) — 실질 검증은 R6-4 보고의
       별도 하네스(resolve_birth_hour 경유 여부를 in_unknown_time=True +
       raw birth_hour=0 조합으로 직접 실측)로 수행했다.
   (a)를 나중에 고칠 때 --compare 차이는 "설명되지 않는 변경"이 아니라 "의도된
   갱신"이니 baseline 갱신 규칙(CLAUDE.md)대로 diff를 확인하고 의식적으로
   --dump한다.
5) manse.py의 raw birth_hour 관련 수정(R6-4 등)은 apptest_33으로 회귀를 증명할
   수 없다 — _run_combo(246행)가 매 콤보 전에 session_state["birth_hour"]를
   그 케이스의 실제(이미 확정된) 시각으로 세팅하므로, resolve_birth_hour를
   거치든 안 거치든 결과가 항상 같다(시간확정 케이스에서 resolve_birth_hour는
   항등함수처럼 동작 — 25b5694·R6-4 공통 설계). 이런 종류의 수정은 apptest
   --compare 차이 0건이 "정상"이며, 실제 검증은 in_unknown_time=True + raw
   birth_hour=0을 직접 세션에 주입하는 별도 스크립트로 해야 한다.
"""
import sys
import os
import re
import json
import argparse
import difflib
import subprocess
import random
import tempfile
from datetime import date, datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_THIS_DIR)
sys.path.insert(0, _ROOT)      # manse, saju_engine, saju_interpreter, saju_sinsal
sys.path.insert(0, _THIS_DIR)  # pils_fixtures

import streamlit as st  # noqa: E402
import manse  # noqa: E402  (import만 함 — main()은 __main__ 가드 안이라 실행되지 않음)
# R3-4: menu7_ai 편입 준비 — UsageTracker가 프로젝트 루트 usage_stats.json(로컬
# 실사용 카운터, git 비추적)에 실제로 읽고/쓰는 걸 런타임 몽키패치로 완전히
# 차단한다(manse.py 소스 무수정). 이게 없으면 menu7_ai가 세션당 최초 1회
# chat_history를 채울 때 UsageTracker.increment()가 그 실파일을 덮어쓴다.
manse.UsageTracker.check_limit = staticmethod(lambda: True)
manse.UsageTracker.increment = staticmethod(lambda: None)
import saju_interpreter  # noqa: E402  (freeze 대상 — .datetime 이름 교체용, 모듈 자체 참조 필요)
from pils_fixtures import CASES, get_pils  # noqa: E402  (값 재사용, 복제 금지)
from saju_engine import calc_sipsung, SajuCoreEngine  # noqa: E402
from saju_interpreter import get_jeokjung_guiin  # noqa: E402
from saju_sinsal import get_gongmang  # noqa: E402


# 11메뉴 — 그동안 33조합 검증에 쓰던 목록 그대로
# health(menu14_health)는 R1-b-3b-0(2026-09-22)에서 추가 — 기존 11메뉴 골든은 불변,
# health만 baseline에 신규 조합으로 붙는다.
# report_narr는 R1-c-0''(2026-09-23)에서 추가 — build_rich_narrative(section="report")
# 반환 문자열을 직접 캡처(menu7_ai UI 경로는 안 탐, 아래 _call_menu 주석 참고).
# 이것도 기존 12메뉴 골든은 건드리지 않고 baseline에 신규 조합으로만 붙는다.
# ohaeng_deep(menu16_ohaeng_deep)은 R2-2(2026-09-23)에서 추가 — R2 진단에서
# 백호대살 로컬 리터럴(manse.py:31113)이 이 메뉴에만 있고 apptest 밖이라 사각지대였음.
# 이것도 기존 13메뉴 골든은 건드리지 않고 baseline에 신규 조합으로만 붙는다.
# bihang(menu8_bihang)·gaewoon(menu_gaewoon)은 R3-2(2026-09-23)에서 추가 — main()
# 탭 dispatch에 실제로 연결돼 있는데 apptest_33 밖이라 사각지대였음(R3 진단).
# 다른 12메뉴와 동일 시그니처(pils, name, birth_year, gender)라 직접호출 가능,
# 2케이스 사전 probe로 케이스 간 오염·예외 없음 확인 후 추가. 기존 15메뉴
# 골든은 건드리지 않고 baseline에 신규 조합으로만 붙는다.
# menu7_ai(ai)는 R3-2에서 검토 중 tab_ai_chat의 st.session_state.chat_history가
# 케이스별로 격리되지 않는 전역 키라 apptest_33처럼 한 프로세스에서 여러 "가상
# 세션"(케이스)을 순서대로 도는 하네스에서는 두 번째 케이스부터 첫 케이스의 stale
# 채팅 인트로를 그대로 재노출하는 문제(R3-2 진단 확인)와, 그 인트로 생성 시
# UsageTracker.increment()가 프로젝트 루트 usage_stats.json(로컬 실사용 카운터,
# git 비추적)에 실제로 쓰는 문제(R3-3 진단 확인)가 있어 보류됐다. R3-4에서
# manse.py 무수정으로 해결: (1) _run_combo가 매 콤보 전에 chat_history를
# 비워 케이스 간 오염 차단, (2) import manse 직후 UsageTracker.check_limit/
# increment를 몽키패치해 실파일 접근 자체를 차단. 이 2줄만 넣은 상태로
# --compare 차이 0건 확인 후 menu7_ai를 추가(R3-4 결정론 검증: 박성우→박후규
# 순서와 박후규 단독 실행의 menu7_ai 캡처가 바이트 동일 — 오염 해소 확인).
# manse_grid(render_manse_grid)는 R5-2(2026-09-24)에서 추가 — R5 진단에서 이 함수가
# main() 안 입력완료 직후 1회만 렌더되는 독립 경로라 17메뉴 dispatch 어디에도 안 걸려
# 사각지대였음이 확인됨(get_special_stars를 부르는 다른 두 호출부와 달리 top-5/top-3
# 슬라이싱 + 신강신약·오행분포·용신기신·세운·대운·월운을 한 화면에 조합하는 로직은
# 이 함수에만 있음 — 중복 캡처 아님). main()의 session_state 읽기 경로(_ss.get("in_
# birth_hour", ...) 등, 세션 키 접두사가 다름)를 그대로 재현하지 않고, 다른 17메뉴와
# 동일하게 함수를 직접 호출한다 — birth_month/day/hour/minute은 _run_combo가 매 콤보
# 전에 이미 st.session_state에 세팅해 두므로 _call_menu에서 그대로 꺼내 쓴다(아래 참고).
# 이것도 기존 17메뉴 골든은 건드리지 않고 baseline에 신규 조합으로만 붙는다.
MENU_ORDER = [
    "menu1_report", "current_situation", "lifeline", "past", "future3",
    "money", "relations", "daily", "monthly", "yearly", "tojeong", "health",
    "report_narr", "money_narr", "relations_narr", "future_narr", "lifeline_narr", "past_narr",
    "ohaeng_deep", "bihang", "gaewoon", "ai", "manse_grid",
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
    elif menu_key == "health":
        manse.menu14_health(pils, case_name, birth_year, gender)
    elif menu_key == "report_narr":
        # menu7_ai는 build_rich_narrative(section="report") 호출부(manse.py:23374)가
        # `if False:` 죽은 코드 안에 있어 UI 경로로는 절대 도달 못 함(R1-c-0' 실측).
        # PDF(menu_pdf, saju_report.py:2131)가 유일한 실사용 경로인데 버튼 트리거
        # 하네스가 따로 필요해 무거우므로, 함수를 직접 호출해 반환 문자열을 캡처하는
        # 이 경로로 _nar_ch8_flow(5대 지표/건강점수 포함) 로직만 정밀 감시한다.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="report")
    elif menu_key == "money_narr":
        # R8-5: build_rich_narrative(section="money") — 실사용 경로는
        # render_ai_deep_analysis()의 "💰 재물/사업운 심층 리포트 보기" 버튼
        # (여러 탭 하단, 클릭 트리거 하네스 없이는 apptest가 못 탐). report_narr와
        # 동일하게 함수 직접 호출로 _nar_wealth(GYEOKGUK_DETAIL 재물/직업/주의/
        # 처방 포함) 로직을 감시한다.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="money")
    elif menu_key == "relations_narr":
        # R8-5: build_rich_narrative(section="relations") — 실사용 경로는
        # render_ai_deep_analysis()의 "💑 인연/인간관계 심층 리포트 보기" 버튼.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="relations")
    elif menu_key == "future_narr":
        # R8-5: build_rich_narrative(section="future") — 실사용 경로는
        # render_ai_deep_analysis()의 "🔮 미래 3년 집중 예언 보기" 버튼.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="future")
    elif menu_key == "lifeline_narr":
        # R8-5: build_rich_narrative(section="lifeline") — 실사용 경로는
        # render_ai_deep_analysis()의 "🌊 대운 100년 정밀 풀이 보기" 버튼.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="lifeline")
    elif menu_key == "past_narr":
        # R8-5: build_rich_narrative(section="past") — 실사용 경로는
        # render_ai_deep_analysis()의 "🎯 과거 사건 복기 풀이 보기" 버튼.
        return manse.build_rich_narrative(pils, birth_year, gender, case_name, section="past")
    elif menu_key == "ohaeng_deep":
        manse.menu16_ohaeng_deep(pils, case_name, birth_year, gender)
    elif menu_key == "bihang":
        manse.menu8_bihang(pils, case_name, birth_year, gender)
    elif menu_key == "gaewoon":
        manse.menu_gaewoon(pils, case_name, birth_year, gender)
    elif menu_key == "ai":
        manse.menu7_ai(pils, case_name, birth_year, gender)
    elif menu_key == "manse_grid":
        # render_manse_grid는 다른 12메뉴와 달리 birth_month/day/hour/minute을
        # 직접 인자로 받는다(name 인자는 없음). _run_combo가 매 콤보 전에
        # st.session_state["birth_month"/"birth_day"/"birth_hour"/"birth_minute"]을
        # 이미 그 콤보 값으로 세팅해 두므로(위 _run_combo 정의 참고) 여기서 그대로
        # 꺼내 쓴다 — main()의 "in_birth_hour"/"in_birth_minute" 세션 키 경로는
        # 재현하지 않는다(R5 진단: 접두사가 달라 apptest 세션과 안 맞음).
        #
        # R6-2: CASES[case_name]["unknown_time"]이 참이면 시간모름 화면을
        # 재현한다 — pils_fixtures.py의 check_yangin_unknown_time과 동일한
        # 관용구(get_pils 결과를 복사해 pils[0]만 블랭크)로 pils[0]을 비우고,
        # 그 직전 값을 _est_hour_pillar에 담아 main():28699와 동일하게
        # 세션에 넣는다(R6-1 이후 render_manse_grid는 이 세션키+pils[0] 상태만
        # 보고 판단하므로 in_unknown_time 플래그는 여기서도 세팅하지 않는다).
        # 원본 pils는 복사본이라 무변경 — 다른 17개 분기(이 케이스도 시간확정
        # 처럼 그대로 도는 나머지 메뉴)에 영향 없음.
        #
        # ★알려진 결함(R6-2 진단 확인) — 고칠 때 이 케이스 골든도 의도적으로 갱신할 것:
        #  1) STRENGTH_DESC(saju_data.py)에 "극신강(極身强)"/"극신약(極身弱)" 키가
        #     없어, 이 케이스처럼 시주가 빠지며 신강신약이 극단으로 밀리면 24933행
        #     성격 설명 줄이 빈 <div></div>로 렌더됨(값이 틀리진 않음, 정상 침묵이나
        #     불완전) — 미해결.
        #  2) render_manse_grid 자체 대운 계산(24740행)이 호출부(29093행)에서
        #     resolve_birth_hour를 거치지 않은 raw birth_hour를 받던 결함(eb878f8의
        #     17곳 정리에서 빠진 지점, R6-3 원인 추적) — R6-4(2026-09-24)에서 해소.
        #     이 케이스는 birth_hour=12 고정이라 골든값 변화는 없었다(무영향 케이스).
        if CASES[case_name].get("unknown_time"):
            _pils_ut = [dict(p) for p in pils]
            st.session_state["_est_hour_pillar"] = {
                "cg": _pils_ut[0].get("cg", ""), "jj": _pils_ut[0].get("jj", ""),
            }
            _pils_ut[0] = {"cg": "", "jj": "", "str": ""}
            manse.render_manse_grid(
                _pils_ut, birth_year,
                st.session_state.get("birth_month"), st.session_state.get("birth_day"),
                st.session_state.get("birth_hour"), st.session_state.get("birth_minute"),
                gender,
            )
        else:
            manse.render_manse_grid(
                pils, birth_year,
                st.session_state.get("birth_month"), st.session_state.get("birth_day"),
                st.session_state.get("birth_hour"), st.session_state.get("birth_minute"),
                gender,
            )
    else:
        raise ValueError(f"알 수 없는 menu_key: {menu_key}")
    return None


def _run_combo(menu_key, pils, case_name, birth_year, m, d, h, mi, gender):
    st.session_state["birth_month"] = m
    st.session_state["birth_day"] = d
    st.session_state["birth_hour"] = h
    st.session_state["birth_minute"] = mi
    st.session_state["marriage_status"] = "미혼"
    st.session_state["in_marriage"] = "미혼"
    st.session_state["partner_pils"] = None
    # R3-4: menu7_ai(tab_ai_chat)의 chat_history가 케이스별로 격리되지 않는
    # 전역 세션 키라 — 매 콤보 시작 전에 비워서 이전 케이스의 stale 인트로가
    # 다음 케이스로 새는 걸 막는다(R3-3 진단에서 오염 실측 확인).
    st.session_state["chat_history"] = []

    exc_msg = None
    cap = _Capturer()
    with cap:
        try:
            _ret = _call_menu(menu_key, pils, case_name, birth_year, gender)
            if _ret:
                # 기존 12메뉴는 _call_menu가 항상 None을 반환하므로 이 분기는
                # report_narr에서만 타고, 나머지 메뉴의 캡처 내용·순서는 무변경.
                cap.buf.append(f"return|{_ret!r}")
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


def _diff_two_dump_files(path_a, path_b, label_a, label_b):
    """이미 저장된 dump 파일 2개를 (재실행 없이) 그대로 비교한다.
    compare()의 정규화·diff 출력 로직을 파일 대 파일 비교용으로 재사용."""
    with open(path_a, "r", encoding="utf-8") as f:
        da = json.load(f)
    with open(path_b, "r", encoding="utf-8") as f:
        db = json.load(f)
    ra, rb = da.get("results", {}), db.get("results", {})
    diff_count = 0
    for case_name in sorted(set(ra) | set(rb)):
        ma, mb = ra.get(case_name, {}), rb.get(case_name, {})
        for menu_key in sorted(set(ma) | set(mb)):
            a, b = ma.get(menu_key), mb.get(menu_key)
            if a is None or b is None:
                print(f"[DIFF] {case_name}/{menu_key} — 한쪽에만 존재({label_a if a is None else label_b}에 없음)")
                diff_count += 1
                continue
            if bool(a.get("exception")) != bool(b.get("exception")):
                print(f"[DIFF] {case_name}/{menu_key} — 예외 상태가 시드마다 다름: "
                      f"{label_a}={a.get('exception')!r} / {label_b}={b.get('exception')!r}")
                diff_count += 1
                continue
            an = [_normalize(x) for x in a.get("output", [])]
            bn = [_normalize(x) for x in b.get("output", [])]
            if an != bn:
                diff_count += 1
                print(f"[DIFF] {case_name}/{menu_key} — {label_a} vs {label_b} 비결정 출력 발견")
                udiff = list(difflib.unified_diff(an, bn, lineterm="", n=0,
                                                   fromfile=label_a, tofile=label_b))
                for line in udiff[:10]:
                    print("    " + line)
                if len(udiff) > 10:
                    print(f"    ... ({len(udiff) - 10}줄 더 있음)")
    return diff_count


def determinism_check(freeze_date):
    """PYTHONHASHSEED는 프로세스 시작 시에만 고정 가능하므로, 서로 다른 두 값으로
    이 스크립트를 서브프로세스로 두 번 --dump 실행해 결과를 비교한다. 시드는
    매번 무작위로 고른다(특정 시드 하나에 고정해 그 시드에서만 우연히 통과하는
    걸 피하기 위함 — R8-6). --freeze-date는 필수(시각 드리프트와 해시 순서
    드리프트를 분리해서 봐야 하므로)."""
    if not freeze_date:
        print("[FAIL] --determinism에는 --freeze-date가 필요합니다(시각 드리프트와 "
              "해시 순서 문제를 분리하기 위함).")
        return 1

    seed_a = random.randint(1, 2**31 - 1)
    seed_b = random.randint(1, 2**31 - 1)
    while seed_b == seed_a:
        seed_b = random.randint(1, 2**31 - 1)

    with tempfile.TemporaryDirectory() as tmpdir:
        path_a = os.path.join(tmpdir, "seed_a.json")
        path_b = os.path.join(tmpdir, "seed_b.json")
        for seed, path in ((seed_a, path_a), (seed_b, path_b)):
            env = dict(os.environ)
            env["PYTHONHASHSEED"] = str(seed)
            env["PYTHONIOENCODING"] = "utf-8"
            proc = subprocess.run(
                [sys.executable, os.path.abspath(__file__),
                 "--dump", path, "--freeze-date", freeze_date],
                env=env, capture_output=True, text=True, encoding="utf-8",
            )
            if proc.returncode != 0 or not os.path.exists(path):
                print(f"[FAIL] PYTHONHASHSEED={seed} 실행 실패(returncode={proc.returncode})")
                print(proc.stdout[-2000:])
                print(proc.stderr[-2000:])
                return 1

        print(f"[DETERMINISM] PYTHONHASHSEED={seed_a} vs {seed_b} (freeze_date={freeze_date}) 비교")
        diff_count = _diff_two_dump_files(path_a, path_b, f"seed{seed_a}", f"seed{seed_b}")

    if diff_count == 0:
        print(f"[OK] 비결정 지점 0건 (시드 {seed_a}/{seed_b})")
        return 0
    else:
        print(f"[FAIL] 비결정 출력 {diff_count}건 발견 (시드 {seed_a}/{seed_b})")
        return 1


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
    group.add_argument(
        "--determinism", action="store_true",
        help="서로 다른 두 PYTHONHASHSEED(매번 무작위 선택)로 --dump를 두 번 서브프로세스 "
             "실행해 결과를 비교한다(R8-6). set/frozenset 순회 비결정성 재발 감시용 — "
             "특정 시드 하나에 고정하지 않는다. --freeze-date 필수.",
    )
    parser.add_argument(
        "--freeze-date", metavar="YYYY-MM-DD", default=None,
        help="현재 시각을 이 날짜로 고정하고 실행(daily/monthly/money/④대운시제 노이즈 제거용). "
             "미지정 시 실제 현재 시각 사용(현행 동작과 동일, 하위호환). --compare에서 미지정 시 "
             "baseline meta의 freeze_date를 자동으로 읽어 재현한다. --determinism에는 필수.",
    )
    args = parser.parse_args()

    if args.determinism:
        sys.exit(determinism_check(args.freeze_date))

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
