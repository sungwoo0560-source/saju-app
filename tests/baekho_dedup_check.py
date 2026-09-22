#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests/baekho_dedup_check.py — render_pdf_download_btn(manse.py)의 "발동 신살 전체"
병합 dedup이 백호대살을 정확히 1개로 수렴시키는지 확인하는 회귀 테스트.

배경(R2/R2-1): calc_all_sinsal_extended·get_12sinsal·get_extra_sinsal 세 함수가
각자 백호대살을 판정하는데, "이름" 필드가 "백호대살(白虎大煞)"/"(白虎大殺)"/"(白虎)"로
한자 표기만 다르다. manse.py:8030-8047의 병합 dedup이 완전일치 비교였을 때는 이
표기 차이 때문에 dedup을 통과 못 해 최대 3중 리스팅됐다(균시차경계_1031 등 3건
실측 확인). Y-28 박스(manse.py:15697 부근)와 동일하게 prefix(`.split("(")[0]`)
dedup으로 교정한 뒤 재확인하는 회귀 고정용 테스트.

이 병합 로직은 render_pdf_download_btn 내부에 인라인으로만 존재하고(별도 함수로
분리돼 있지 않음), 그 경로 자체가 st.button 클릭으로만 열려 apptest_33(호출
캡처 방식)이 못 잡는다 — 12개 탭 PDF 버튼 경로 전체에서 이 테스트가 유일한
안전망이다. manse.py 소스 문자열에서 병합 블록을 그대로 추출해 실행하므로,
이 블록 자체가 나중에 바뀌면(예: 병합 순서가 바뀌거나 dedup 키가 다시 바뀌면)
이 테스트도 같이 반응한다.

사용법:
    python tests/baekho_dedup_check.py     (리포 루트에서)
종료코드: 실패가 하나라도 있으면 1, 모두 통과하면 0.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # noqa: E402  (manse import 시 필요)
import manse  # noqa: E402
from saju_sinsal import get_12sinsal, get_extra_sinsal  # noqa: E402
from saju_zhengtong import calc_all_sinsal_extended  # noqa: E402
from pils_fixtures import CASES, get_pils  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

_FAILS = []


def _check(name, ok, detail=""):
    print(("[OK] " if ok else "[FAIL] ") + name + (" — " + detail if detail else ""))
    if not ok:
        _FAILS.append(name)


# ── manse.py의 실제 병합 블록을 소스에서 그대로 추출(재구현 아님) ──
_SRC = inspect.getsource(manse.render_pdf_download_btn)
_START = "_cs_s12 = get_12sinsal(pils) or []"
_END = "_cs_all_s.append(_s)"
_start_idx = _SRC.rfind("\n", 0, _SRC.index(_START)) + 1  # 그 줄의 맨 앞(들여쓰기 포함)부터
_end_idx = _SRC.index(_END, _start_idx) + len(_END)
_BLOCK = _SRC[_start_idx:_end_idx]

import textwrap  # noqa: E402
_BLOCK_DEDENTED = textwrap.dedent(_BLOCK)


def run_merge(pils):
    """render_pdf_download_btn:8033-8047 병합+dedup 블록을 그대로 실행해
    (_cs_all_s, _cs_seen_s)를 돌려준다."""
    ns = {
        "pils": pils,
        "get_12sinsal": get_12sinsal,
        "get_extra_sinsal": get_extra_sinsal,
        "_cs_cse": calc_all_sinsal_extended,
    }
    exec(compile(_BLOCK_DEDENTED, "<render_pdf_download_btn merge block>", "exec"), ns)
    return ns["_cs_all_s"]


# ── R2 진단에서 3중 리스팅을 실측으로 재현했던 3케이스 + 대조군(박성우, 0건 기대) ──
CASES_EXPECT = {
    "균시차경계_1031": 1,
    "도화_년지만_19700403": 1,
    "지지순서_자형2종_19951109": 1,
    "박성우": 0,
}

for case_name, expect_n in CASES_EXPECT.items():
    if case_name not in CASES:
        _check(f"[{case_name}] CASES에 존재", False, "픽스처 목록에서 사라짐 — 테스트 갱신 필요")
        continue
    pils = get_pils(case_name)
    merged = run_merge(pils)
    baekho_entries = [s for s in merged if "백호" in (s.get("이름") or s.get("name") or "")]
    _check(
        f"[{case_name}] 발동 신살 목록의 백호 prefix 항목 수 == {expect_n}",
        len(baekho_entries) == expect_n,
        f"실제 {len(baekho_entries)}건: {[e.get('이름') or e.get('name') for e in baekho_entries]}",
    )
    if expect_n == 1 and len(baekho_entries) == 1:
        # 가장 정확한 설명(calc_all_sinsal_extended, 등급/아이콘/주의 필드까지 갖춘 버전)이
        # 남아야 한다 — 병합 순서(_cs_ext 먼저)상 이게 자동으로 보장되지만 회귀 고정.
        _entry = baekho_entries[0]
        _check(
            f"[{case_name}] 남은 백호 항목이 calc_all_sinsal_extended 버전(등급 필드 보유)",
            _entry.get("등급") == "강력발동" and _entry.get("아이콘") == "🐅",
            f"실제 등급={_entry.get('등급')!r} 아이콘={_entry.get('아이콘')!r}",
        )

print()
if _FAILS:
    print(f"[FAIL] {len(_FAILS)}건 실패")
    sys.exit(1)
else:
    print("[OK] 백호대살 dedup 회귀 테스트 전부 통과")
    sys.exit(0)
