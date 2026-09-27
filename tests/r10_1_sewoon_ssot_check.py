# -*- coding: utf-8 -*-
"""R10-1 검증: PDF vs 현재상황/미래3년 세운 등급 SSOT 일치 여부 실측.

배경(R9-1 6층 진단, 2026-09-27 보고):
  get_yearly_luck()의 raw "길흉"은 십성 고정표(YEARLY_LUCK_NARRATIVE)일 뿐 개인의
  종합_용신/종합_기신과 무관하다. menu_current_situation·menu4_future3는 이걸 SSOT
  (종합_용신/종합_기신 멤버십)로 보정해서 쓰는데, saju_report.py(PDF)는 R10-1 이전엔
  raw 값을 보정 없이 그대로 판단문에 썼다 — 유효 60갑자 2,000표본(seed=42) 기준
  불일치 46.5%(완전반대 26.1%) 실측.

R10-1a: 보정 공식을 saju_interpreter.yongshin_sewoon_grade()로 추출(두 탭 공용).
R10-1b: saju_report.py 1816~1838(올해 길흉 판단)도 같은 헬퍼로 전환 + "평" 판단문 신설.

이 스크립트는 그 전후 효과를 재현·고정한다:
  - "전"(before) = get_yearly_luck raw 길흉만 사용(R10-1 이전 PDF 동작 재현)
  - "후"(after)  = yongshin_sewoon_grade() 보정 적용(R10-1 이후 PDF·화면 공용 동작)
전 vs 후 모두 "현재상황/미래3년" 기준(= yongshin_sewoon_grade 자체)과 비교해
불일치율이 46.5%/26.1% -> 0%/0%로 떨어지는지 확인한다.

추가 측정(수정 없음, R10-1 지시 항목): 월운 — menu_current_situation의 _month_grade
(십성표 base + 월지 SSOT 보정 + 충 + 공망 4단 혼합) vs menu10_monthly "이 달" 배지
(종합_용신/종합_기신 순수 멤버십, 십성표 미참조) 2026년 12개월 불일치율.

실행: PYTHONIOENCODING=utf-8 python tests/r10_1_sewoon_ssot_check.py
"""
import sys
import random
import re

sys.path.insert(0, ".")

from saju_interpreter import get_yongshin, get_ilgan_strength, yongshin_sewoon_grade
from saju_engine import get_yearly_luck, get_monthly_luck, OH

CG = list("甲乙丙丁戊己庚辛壬癸")
JJ = list("子丑寅卯辰巳午未申酉戌亥")
GAPJA = [(CG[i % 10], JJ[i % 12]) for i in range(60)]

N = 2000
YEAR = 2026


def _mk_pils(rng):
    return [{"cg": c, "jj": j} for c, j in (rng.choice(GAPJA) for _ in range(4))]


def _norm(g):
    return re.sub(r"\([^)]+\)", "", str(g)).strip()


def _bucket(g):
    if "길" in g:
        return "길"
    if "흉" in g:
        return "흉"
    return "평"


def check_yearly_pdf_vs_screen():
    rng = random.Random(42)
    total = 0
    mismatch_before = 0
    opposite_before = 0
    mismatch_after = 0
    opposite_after = 0
    dist_before = {}
    dist_after = {}
    dist_screen = {}

    for _ in range(N):
        p = _mk_pils(rng)
        ilgan = p[1]["cg"]
        sn = (get_ilgan_strength(ilgan, p) or {}).get("신강신약", "")
        ys = get_yongshin(p) or {}
        yong_ohs = ys.get("종합_용신", []) or []
        gi_ohs = ys.get("종합_기신", []) or []

        yl = get_yearly_luck(p, YEAR) or {}
        sw_oh = yl.get("오행_천간", "")
        raw_gil = _norm(yl.get("길흉", "평"))

        # 화면(현재상황/미래3년) = yongshin_sewoon_grade 자체가 정답 기준
        screen = yongshin_sewoon_grade(sw_oh, yong_ohs, gi_ohs, sn) or raw_gil
        b_screen = _bucket(screen)

        # PDF "전"(R10-1 이전, raw만 사용)
        b_before = _bucket(raw_gil)

        # PDF "후"(R10-1b 적용, 화면과 동일 헬퍼)
        after = yongshin_sewoon_grade(sw_oh, yong_ohs, gi_ohs, sn) or raw_gil
        b_after = _bucket(after)

        total += 1
        dist_before[b_before] = dist_before.get(b_before, 0) + 1
        dist_after[b_after] = dist_after.get(b_after, 0) + 1
        dist_screen[b_screen] = dist_screen.get(b_screen, 0) + 1

        if b_before != b_screen:
            mismatch_before += 1
            if {b_before, b_screen} == {"길", "흉"}:
                opposite_before += 1
        if b_after != b_screen:
            mismatch_after += 1
            if {b_after, b_screen} == {"길", "흉"}:
                opposite_after += 1

    print(f"[세운] N={total}, 기준년도={YEAR}")
    print(f"  화면(현재상황/미래3년) 분포: {dist_screen}")
    print(f"  PDF-전(raw) 분포: {dist_before}")
    print(f"  PDF-후(보정) 분포: {dist_after}")
    print(f"  PDF-전 vs 화면 불일치: {mismatch_before}건 ({mismatch_before*100.0/total:.1f}%), "
          f"완전반대: {opposite_before}건 ({opposite_before*100.0/total:.1f}%)")
    print(f"  PDF-후 vs 화면 불일치: {mismatch_after}건 ({mismatch_after*100.0/total:.1f}%), "
          f"완전반대: {opposite_after}건 ({opposite_after*100.0/total:.1f}%)")
    ok = (mismatch_after == 0 and opposite_after == 0)
    print(f"  [{'OK' if ok else 'FAIL'}] PDF-후 불일치 0건 목표")
    return ok


_RANK_M = {"대길": 5, "길": 4, "평길": 3, "평": 2, "흉": 1, "흉흉": 0}


def _month_grade_replica(ml, yong_list, orig_jjs, gi_list, gm_list, JJCHUNG):
    """manse.py _month_grade(16197)의 재구현 — 새 판정 아님, 기존 공식 그대로 복제."""
    base = ml["길흉"]
    oh_cg = ml["_오행_천간"]
    is_yong = oh_cg in yong_list
    is_chung = JJCHUNG.get(ml["지"], "") in orig_jjs
    RANK = _RANK_M
    RANK_REV = {v: k for k, v in RANK.items()}

    if is_yong:
        if is_chung:
            grade = "평길"
        elif base in ("대길", "길"):
            grade = "대길"
        else:
            grade = "길"
    else:
        if is_chung and base in ("흉", "흉흉"):
            grade = "흉"
        elif is_chung:
            grade = "평"
        else:
            grade = "길" if base == "대길" else base

    wolji_oh = ml["_오행_지지"]
    r = RANK.get(grade, 2)
    if wolji_oh and wolji_oh in yong_list:
        if r < 5:
            r += 1
            grade = RANK_REV.get(r, grade)
    elif gi_list and wolji_oh and wolji_oh in gi_list:
        if r > 0:
            r -= 1
            grade = RANK_REV.get(r, grade)

    if gm_list and ml.get("지", "") in gm_list:
        r = RANK.get(grade, 2)
        if r >= 4:
            grade = RANK_REV.get(r - 1, grade)
        elif r <= 1:
            grade = RANK_REV.get(r + 1, grade)

    return grade


def check_monthly_screen_vs_badge():
    """menu_current_situation의 _month_grade(십성+SSOT+충+공망 혼합) vs
    menu10_monthly "이 달" 배지(순수 SSOT 멤버십) — 2026년 12개월 불일치율.
    공망은 여기선 0건 취급(무관 변수 배제, 두 방식의 SSOT/십성 혼합 차이만 본다)."""
    from saju_data import JIJANGGAN
    _JJCHUNG_L = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
                  "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
    rng = random.Random(42)
    total = 0
    mismatch = 0
    opposite = 0

    for _ in range(N):
        p = _mk_pils(rng)
        ilgan = p[1]["cg"]
        ys = get_yongshin(p) or {}
        yong_ohs = ys.get("종합_용신", []) or []
        gi_ohs = ys.get("종합_기신", []) or []
        orig_jjs = {pp["jj"] for pp in p}

        for month in range(1, 13):
            ml = get_monthly_luck(p, YEAR, month) or {}
            if not ml:
                continue
            oh_cg = OH.get(ml.get("간", ""), "")
            oh_jj = OH.get(ml.get("지", ""), "")
            ml2 = dict(ml)
            ml2["_오행_천간"] = oh_cg
            ml2["_오행_지지"] = oh_jj

            grade_screen = _month_grade_replica(ml2, yong_ohs, orig_jjs, gi_ohs, [], _JJCHUNG_L)
            b_screen = "길" if grade_screen in ("대길", "길", "평길") else ("흉" if grade_screen in ("흉", "흉흉") else "평")

            # menu10_monthly "이 달" 배지: 순수 SSOT 멤버십(십성표 미참조), 충만 별도 반영
            is_yong_badge = oh_cg in yong_ohs
            is_gisin_badge = oh_cg in gi_ohs
            has_chung_badge = bool(_JJCHUNG_L.get(ml.get("지", ""), "") in orig_jjs)
            if is_yong_badge and not has_chung_badge:
                b_badge = "길"
            elif is_gisin_badge or has_chung_badge:
                b_badge = "흉"
            else:
                b_badge = "평"

            total += 1
            if b_screen != b_badge:
                mismatch += 1
                if {b_screen, b_badge} == {"길", "흉"}:
                    opposite += 1

    print(f"\n[월운] N={total}(표본 {N} x 12개월), 기준년도={YEAR}")
    print(f"  현재상황(_month_grade 혼합) vs menu10_monthly(이 달 배지, 순수 SSOT) 불일치: "
          f"{mismatch}건 ({mismatch*100.0/total:.1f}%)")
    print(f"  완전반대: {opposite}건 ({opposite*100.0/total:.1f}%)")


if __name__ == "__main__":
    ok = check_yearly_pdf_vs_screen()
    check_monthly_screen_vs_badge()
    sys.exit(0 if ok else 1)
