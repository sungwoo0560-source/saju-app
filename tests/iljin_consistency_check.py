# -*- coding: utf-8 -*-
"""R13-1 재발방지: SajuCoreEngine._get_day_pillar(A, 실제 명식 엔진) vs
ManseCalendarEngine.get_iljin(B, 만세력탭·월간 길흉일이 참조하는 달력 엔진)의
일진(日辰) 일치 여부를 전수 회귀한다.

배경(R13-0 진단, R13-1 수정):
  B는 원래 "2000-01-01 = 甲子(idx 0)"로 가정했으나, A(SajuCoreEngine._get_day_pillar,
  saju_engine.py:1408)는 이미 "2000-01-01 = 戊午(idx 54)"로 버그픽스돼 있었다
  (같은 파일 안에 같은 목적의 함수가 두 벌 있었는데 한쪽만 고쳐진 상태).
  1900-01-01~2100-12-31 전수 실측 결과 A vs B 불일치 73,414/73,414(100%),
  오프셋은 항상 정확히 54(KASI 2000~2040 구간과 그 밖 구간 동일 — 순수 상수 오프셋).
  R13-1에서 saju_engine.py:446 get_iljin의 idx 공식을 A와 동일하게 맞췄다.

이 스크립트는 그 교정이 유지되는지(회귀 여부)를 다음 두 가지로 고정한다:
  1) 1900-01-01~2100-12-31 매일 A(SajuPrecisionEngine.get_pillars, 정오·야자시
     배제 경유) vs B(ManseCalendarEngine.get_iljin) 60갑자 인덱스 완전 일치.
  2) 5개 앵커 날짜(2026-09-28·2026-10-01·2000-01-01·1969-07-14·1924-01-01)가
     정확한 값(乙巳·戊申·戊午·庚寅·己卯)과 일치.

실행: PYTHONIOENCODING=utf-8 python tests/iljin_consistency_check.py
"""
import os
import sys
import io
from datetime import date, timedelta

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_THIS_DIR)
sys.path.insert(0, _ROOT)

from saju_engine import SajuPrecisionEngine, ManseCalendarEngine, CG, JJ


def _idx_of(cg, jj):
    for i in range(60):
        if i % 10 == CG.index(cg) and i % 12 == JJ.index(jj):
            return i
    return None


def calc_A_idx(y, m, d):
    """실제 명식 엔진 경유 일주(정오 12:00 고정, 야자시 배제 — 자시 경계 무관)."""
    pils = SajuPrecisionEngine.get_pillars(y, m, d, 12, 0, "남", use_yaja_time=False, longitude=126.98)
    ilju = pils[1]  # [시,일,월,년] 순서
    return _idx_of(ilju["cg"], ilju["jj"])


def calc_B_idx(y, m, d):
    return ManseCalendarEngine.get_iljin(y, m, d)["idx"]


ANCHORS = [
    (2026, 9, 28, "乙巳"),
    (2026, 10, 1, "戊申"),
    (2000, 1, 1, "戊午"),
    (1969, 7, 14, "庚寅"),
    (1924, 1, 1, "己卯"),
]


def check_anchors():
    ok = True
    for (y, m, d, expect) in ANCHORS:
        r = ManseCalendarEngine.get_iljin(y, m, d)
        got = r["cg"] + r["jj"]
        status = "OK" if got == expect else "FAIL"
        if got != expect:
            ok = False
        print(f"  [{status}] {y}-{m:02d}-{d:02d}: get_iljin={got} 기대={expect}")
    return ok


def check_full_range():
    start = date(1900, 1, 1)
    end = date(2100, 12, 31)
    total = (end - start).days + 1
    d = start
    mismatch = 0
    first_mismatches = []
    n = 0
    while d <= end:
        a = calc_A_idx(d.year, d.month, d.day)
        b = calc_B_idx(d.year, d.month, d.day)
        if a != b:
            mismatch += 1
            if len(first_mismatches) < 5:
                first_mismatches.append((d.year, d.month, d.day, a, b))
        n += 1
        d += timedelta(days=1)
    print(f"  전체 {n}일 중 불일치 {mismatch}건")
    if first_mismatches:
        print(f"  불일치 샘플: {first_mismatches}")
    return mismatch == 0


def main():
    print("=== 1) 5개 앵커 날짜 검증 ===")
    anchors_ok = check_anchors()
    print()

    print("=== 2) 1900-01-01~2100-12-31 전수 A vs B 일치 검증(수십 초 소요) ===")
    range_ok = check_full_range()
    print()

    if anchors_ok and range_ok:
        print("[OK] 결과 요약: 일진(日辰) A/B 완전 일치 — R13-1 교정 유지됨")
        sys.exit(0)
    else:
        print("[FAIL] 결과 요약: 일진(日辰) A/B 불일치 발생 — 회귀 발생")
        sys.exit(1)


if __name__ == "__main__":
    main()
