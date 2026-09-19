# -*- coding: utf-8 -*-
"""공망 테이블 정합성 검사 — 60갑자 전수.

G1(공망 조회 SSOT화) 라운드에서 manse.py의 자체 사본 _GONGMANG_MAP을
제거하고 saju_sinsal.get_gongmang(pils) 참조로 통합했다. 남은 소스는
정본(get_sunjung_gongmang, saju_sinsal.py)과 saju_zhengtong.py의
ILJU_60GAPJA["공망"] 서술용 사본 2벌뿐이다 — 이 둘이 60갑자 전부에서
계속 일치하는지 회귀 감지하는 목적(값 자체가 다르면 순중공망 계산이나
일주 상세 데이터 중 하나가 잘못된 것).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from saju_sinsal import get_sunjung_gongmang
from saju_zhengtong import ILJU_60GAPJA

CG = list("甲乙丙丁戊己庚辛壬癸")
JJ = list("子丑寅卯辰巳午未申酉戌亥")
GAPJA60 = [(CG[i % 10], JJ[i % 12]) for i in range(60)]


def check_gongmang_table_consistency():
    mismatch = []
    missing = []
    for cg, jj in GAPJA60:
        ilju = cg + jj
        ssot = get_sunjung_gongmang(cg, jj)
        entry = ILJU_60GAPJA.get(ilju)
        if entry is None:
            missing.append(ilju)
            continue
        b_str = entry.get("공망", "")
        b = tuple(b_str) if len(b_str) == 2 else ("", "")
        if set(b) != set(ssot):
            mismatch.append((ilju, ssot, b_str))

    assert not missing, f"ILJU_60GAPJA 누락 일주: {missing}"
    assert not mismatch, f"공망 불일치: {mismatch}"
    return len(GAPJA60)


if __name__ == "__main__":
    try:
        n = check_gongmang_table_consistency()
        print(f"[PASS] 공망 테이블 정합성 — 60갑자 {n}건 전부 일치 (정본 get_sunjung_gongmang vs ILJU_60GAPJA)")
        sys.exit(0)
    except AssertionError as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
