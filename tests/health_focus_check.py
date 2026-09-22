#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests/health_focus_check.py — get_health_focus(saju_interpreter.py) 단위 테스트 (pytest 미사용, 순수 실행 스크립트)

확정 임계값: 과다 HEALTH_OVER_PCT=40 / 피극 조건 HEALTH_WEAK_PCT=15 / 부족 HEALTH_LACK_PCT=5.

- 명식은 손으로 조립하지 않고 SajuPrecisionEngine.get_pillars(출생 입력)로 만든 실존 명식만 쓴다
  (UI와 같은 경로). 명식 표기는 전부 년월일시 순서다. get_pillars 반환은 [시, 일, 월, 년] 순서.
- T1~T5는 실측 표본(random.Random(7), N=5000)에서 고른 실제 명식과 실제 반환값을 그대로 고정한다.
  반환 순서(과다 → 피극 → 부족)까지 assert한다.
- T6~T10은 계산 로직(경계값·피극 조건·동률·인자 덮어쓰기·입력 방어)을 합성 오행 강도로 검증한다
  (calc_ohaeng_strength만 대체). 경계값은 모듈 상수에서 읽어 만든다.

사용법:
    python tests/health_focus_check.py     (리포 루트에서)
종료코드: 실패가 하나라도 있으면 1, 모두 통과하면 0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from saju_engine import SajuPrecisionEngine
import saju_interpreter as I
from pils_fixtures import CASES   # 이 import가 stdout을 UTF-8 래퍼로 바꾼다(다시 감싸지 않는다)

sys.stdout.reconfigure(encoding="utf-8")

_FAILS = []
_ROLE_RANK = {"과다": 0, "피극": 1, "부족": 2}


def _check(name, ok, detail=""):
    print(("[OK] " if ok else "[FAIL] ") + name + (" — " + detail if detail else ""))
    if not ok:
        _FAILS.append(name)


def _pils(y, m, d, h, mi, gender):
    return SajuPrecisionEngine.get_pillars(y, m, d, h, mi, gender, use_yaja_time=True, longitude=126.98)


def _ymdh(p):
    """get_pillars 반환([시,일,월,년])을 년월일시 순서 문자열 4개로."""
    return [p[3]["str"], p[2]["str"], p[1]["str"], p[0]["str"]]


def _run(p):
    return I.get_health_focus(p[1]["cg"], p)


def _row(oh, role, system, ratio):
    return {"오행": oh, "역할": role, "계통": system, "비율": ratio}


def _roles_in_order(r):
    """역할이 과다 → 피극 → 부족 순서이고 중복이 없는지."""
    ranks = [_ROLE_RANK[g["역할"]] for g in r]
    return ranks == sorted(ranks) and len(set(ranks)) == len(ranks)


def _brief(r):
    return [(g["오행"], g["역할"]) for g in r]


# ── 표본 명식 (출생 입력, 기대 명식(년월일시), 기대 반환) ─────────────────────────
def _case_from_fixture(name):
    y, m, d, h, mi = CASES[name]["birth"]
    return (y, m, d, h, mi, CASES[name]["gender"])


FIXED = [
    # (이름, 출생 입력, 기대 명식 년월일시, 기대 반환 — 순서까지 그대로)
    ("T1 박성우 — 과다·부족 모두 없음(최대 土 30.9 < 40, 최소 火 10.4 > 5)", _case_from_fixture("박성우"),
     ["己酉", "辛未", "庚寅", "丁亥"], []),
    ("T2 박후규 — 水 48.8 과다, 火 27.6은 피극 조건(≤15) 밖이라 제외, 木 4.4 부족", _case_from_fixture("박후규"),
     ["庚子", "丁亥", "丙午", "庚子"],
     [_row("水", "과다", "신장·방광·비뇨기", 48.8), _row("木", "부족", "간·담·근육·눈", 4.4)]),
    ("T3 과다+피극 — 土 41.1 과다, 水 14.4 ≤ 15 피극 채택, 최소 火 9.6 > 5라 부족 없음", (1971, 10, 9, 18, 59, "여"),
     ["辛亥", "戊戌", "丁卯", "己酉"],
     [_row("土", "과다", "소화기", 41.1), _row("水", "피극", "신장·방광·비뇨기", 14.4)]),
    ("T4 피극 오행이 곧 최부족 — 金 41.8 과다, 木 3.0(피극 채택이자 최소)이 부족으로 중복 안 들어감", (2003, 9, 6, 17, 6, "여"),
     ["癸未", "庚申", "壬午", "戊申"],
     [_row("金", "과다", "호흡기·대장·피부", 41.8), _row("木", "피극", "간·담·근육·눈", 3.0)]),
    ("T5 과다 없고 부족만 — 최대 土 29.8 < 40, 火 4.4 부족", (1935, 4, 21, 18, 7, "남"),
     ["乙亥", "庚辰", "丁卯", "己酉"],
     [_row("火", "부족", "심혈관", 4.4)]),
]


def test_fixed():
    for label, birth, want_ymdh, want in FIXED:
        p = _pils(*birth)
        _check(label + " · 명식(년월일시)", _ymdh(p) == want_ymdh, "실제 %s / 기대 %s" % (_ymdh(p), want_ymdh))
        got = _run(p)
        _check(label + " · 반환값(순서 포함)", got == want, "실제 %s" % ([(g["오행"], g["역할"], g["계통"], g["비율"]) for g in got]))
        _check(label + " · 역할 순서 과다→피극→부족", _roles_in_order(got))


# ── 합성 강도(계산 로직 검증) ────────────────────────────────────────────────
def _with_strength(strength, fn):
    orig = I.calc_ohaeng_strength
    I.calc_ohaeng_strength = lambda ilgan, pils: dict(strength)
    try:
        return fn()
    finally:
        I.calc_ohaeng_strength = orig


_P = [{"cg": "甲", "jj": "子", "str": "甲子"}] * 4   # 합성 테스트용 자리표시(강도는 대체 함수가 결정)


def _focus(strength, **kw):
    return _with_strength(strength, lambda: I.get_health_focus("甲", _P, **kw))


def test_synthetic():
    over, weak, lack = I.HEALTH_OVER_PCT, I.HEALTH_WEAK_PCT, I.HEALTH_LACK_PCT   # 40 / 15 / 5
    # T6 경계값: 과다 40.0 이상 / 39.9 미만, 부족 5.0 이하 / 5.1 초과, 피극 15.0 이하 채택 / 15.1 제외
    _check("T6-1 과다 경계 40.0 → 과다 발동(피극 土 12.0 ≤ 15 채택)",
           _brief(_focus({"木": over, "火": 20.0, "土": 12.0, "金": 14.0, "水": 14.0})) == [("木", "과다"), ("土", "피극")])
    _check("T6-2 과다 경계 39.9 → 과다 없음", _brief(_focus({"木": over - 0.1, "火": 20.1, "土": 12.0, "金": 14.0, "水": 14.0})) == [])
    _check("T6-3 부족 경계 5.0 → 부족 발동", _brief(_focus({"木": 25.0, "火": lack, "土": 25.0, "金": 25.0, "水": 20.0})) == [("火", "부족")])
    _check("T6-4 부족 경계 5.1 → 부족 없음", _brief(_focus({"木": 25.0, "火": lack + 0.1, "土": 25.0, "金": 25.0, "水": 19.9})) == [])
    _check("T6-5 피극 경계 15.0 → 피극 채택", _brief(_focus({"木": 45.0, "火": 20.0, "土": weak, "金": 10.0, "水": 10.0})) == [("木", "과다"), ("土", "피극")])
    _check("T6-6 피극 경계 15.1 → 피극 제외(과다만)", _brief(_focus({"木": 45.0, "火": 15.0, "土": weak + 0.1, "金": 12.9, "水": 12.0})) == [("木", "과다")])
    _check("T6-7 피극 제외 + 부족 공존(土 20 > 15 제외, 金 5.0 부족)",
           _brief(_focus({"木": 50.0, "火": 20.0, "土": 20.0, "金": 5.0, "水": 5.0})) == [("木", "과다"), ("金", "부족")],
           "최소 동률 金=水=5.0에서는 木火土金水 앞쪽인 金이 선택")
    # T7 동률: 최대 동률이면 木火土金水 앞쪽, 최소 동률이면 앞쪽
    _check("T7-1 최대 동률(木=火=40) → 木이 과다, 피극 土", _brief(_focus({"木": 40.0, "火": 40.0, "土": 5.0, "金": 10.0, "水": 5.0})) == [("木", "과다"), ("土", "피극")],
           "土 5.0은 피극으로 이미 들어가 부족(최소 동률의 앞쪽=土)으로 중복 안 됨")
    _check("T7-2 최소 동률(火=金=4) → 火가 부족", _brief(_focus({"木": 30.0, "火": 4.0, "土": 32.0, "金": 4.0, "水": 30.0})) == [("火", "부족")])
    _check("T7-3 과다가 여러 개여도 최대 1개만(木 41 · 水 41 동률 → 木)", _brief(_focus({"木": 41.0, "火": 4.0, "土": 4.0, "金": 10.0, "水": 41.0})) == [("木", "과다"), ("土", "피극"), ("火", "부족")],
           "최소 동률 火=土=4.0에서는 木火土金水 앞쪽인 火가 선택돼 부족으로 들어감")
    r = _focus({"木": 50.0, "火": 1.0, "土": 10.0, "金": 20.0, "水": 19.0})
    _check("T7-4 반환 순서·개수(과다→피극→부족, 3개)", _brief(r) == [("木", "과다"), ("土", "피극"), ("火", "부족")] and len(r) <= 3 and _roles_in_order(r))
    _check("T7-5 각 dict 키 4종(오행·역할·계통·비율), 비율은 float", all(sorted(g) == sorted(["오행", "역할", "계통", "비율"]) and isinstance(g["비율"], float) for g in r))
    # T8 입력 방어: 빈 입력은 None이 아니라 []
    _check("T8-1 pils 빈 list → []", I.get_health_focus("甲", []) == [])
    _check("T8-2 ilgan 빈 문자열 → []", I.get_health_focus("", _P) == [])
    _check("T8-3 pils None → []", I.get_health_focus("甲", None) == [])
    _check("T8-4 강도 딕셔너리가 비면 → []", _with_strength({}, lambda: I.get_health_focus("甲", _P)) == [])
    # T9 인자 덮어쓰기(측정용): 기본값은 모듈 상수, 인자를 주면 그 값이 우선
    s = {"木": 36.0, "火": 24.0, "土": 20.0, "金": 10.0, "水": 10.0}
    _check("T9-1 인자 없음 → 모듈 상수(40) 기준이라 木 36은 과다 아님", _brief(_focus(s)) == [])
    _check("T9-2 over_pct=35 덮어쓰기 → 과다 발동, 피극 土 20 > 15라 제외", _brief(_focus(s, over_pct=35)) == [("木", "과다")])
    _check("T9-3 over_pct=35, weak_pct=None(조건 없음) → 피극 土 20 채택", _brief(_focus(s, over_pct=35, weak_pct=None)) == [("木", "과다"), ("土", "피극")])
    s2 = {"木": 50.0, "火": 15.0, "土": 20.0, "金": 10.0, "水": 5.0}
    _check("T9-4 weak_pct 안 줌 → 모듈 상수(15) 적용, 土 20 제외", _brief(_focus(s2)) == [("木", "과다"), ("水", "부족")])
    _check("T9-5 weak_pct=None을 직접 줌 → 조건 없음(인자 안 준 것과 다름)", _brief(_focus(s2, weak_pct=None)) == [("木", "과다"), ("土", "피극"), ("水", "부족")])
    _check("T9-6 lack_pct=3 덮어쓰기 → 水 5.0은 부족 아님", _brief(_focus(s2, lack_pct=3)) == [("木", "과다")])
    # 모듈 상수를 바꾸면 호출 시점에 반영(측정 스크립트가 쓰는 방식) — 끝나면 원복
    orig_weak = I.HEALTH_WEAK_PCT
    I.HEALTH_WEAK_PCT = None
    try:
        _check("T9-7 모듈 상수 HEALTH_WEAK_PCT=None으로 바꾸면 인자 없는 호출에도 반영", _brief(_focus(s2)) == [("木", "과다"), ("土", "피극"), ("水", "부족")])
    finally:
        I.HEALTH_WEAK_PCT = orig_weak
    _check("T9-8 모듈 상수 원복 확인", I.HEALTH_WEAK_PCT == 15)


def test_constants():
    _check("상수 HEALTH_OVER_PCT == 40", I.HEALTH_OVER_PCT == 40)
    _check("상수 HEALTH_WEAK_PCT == 15", I.HEALTH_WEAK_PCT == 15)
    _check("상수 HEALTH_LACK_PCT == 5", I.HEALTH_LACK_PCT == 5)
    _check("계통 매핑 원문", I._HEALTH_SYSTEM == {"木": "간·담·근육·눈", "火": "심혈관", "土": "소화기", "金": "호흡기·대장·피부", "水": "신장·방광·비뇨기"})
    _check("극 관계(木→土, 火→金, 土→水, 金→木, 水→火)", I._HEALTH_GEUK == {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"})
    p = _pils(*_case_from_fixture("박후규"))
    a = _run(p)
    b = _run(p)
    _check("같은 입력을 두 번 호출해도 결과 동일(부작용 없음)", a == b)


def test_role_text_and_jeokjung():
    """R1-b-3a: HEALTH_ROLE_TEXT(틀 3개) 정합 + get_jeokjung_health가 focus·신살을 따르는지."""
    T = I.HEALTH_ROLE_TEXT
    OHS = "木火土金水"
    _check("HEALTH_ROLE_TEXT 원문(틀 3개)", T == {
        "과다": "{오행} 기운이 강한 편이라 {계통} 쪽을 평소에 살펴주면 좋습니다.",
        "피극": "{극하는오행} 기운에 눌려 {오행} 기운이 약해지기 쉬워, {계통} 쪽 관리가 필요합니다.",
        "부족": "{오행} 기운이 적은 편이라 {계통} 쪽을 꾸준히 챙겨주면 좋습니다.",
    })
    geuk_by = {v: k for k, v in I._HEALTH_GEUK.items()}   # 피극 오행 → 극하는 오행
    bad, texts = [], []
    for r in T:
        for o in OHS:
            row = _row(o, r, I._HEALTH_SYSTEM[o], 12.3)
            try:
                t = T[r].format(**row, 극하는오행=geuk_by[o])
            except Exception as e:
                bad.append((r, o, repr(e))); continue
            texts.append(t)
            if I._HEALTH_SYSTEM[o] not in t or "{" in t or "}" in t or (r == "피극" and not t.startswith("%s 기운에 눌려 %s 기운이" % (geuk_by[o], o))):
                bad.append((r, o, t))
    _check("format(**focus행, 극하는오행=): 계통·오행 치환, 잔여 중괄호 없음, 피극 극하는오행 = _HEALTH_GEUK 역방향", not bad, str(bad[:2]))
    _check("문구에 % 와 숫자 미노출(비율은 넣지 않는다)", all("%" not in t and not any(c.isdigit() for c in t) for t in texts) and "%" not in "".join(T.values()))
    words = ("반드시", "무조건", "위험", "집착", "터집니다", "질환", "병", "수술", "사고", "급성", "절대", "100%")
    hit = [(r, w) for r in T for w in words if w in T[r]]
    _check("문구 틀에 금지어 없음", not hit, str(hit[:3]))

    def box(name, sinsal=()):
        p = _pils(*_case_from_fixture(name))
        return _run(p), I.get_jeokjung_health({}, p, list(sinsal))
    def fmt(f, over):
        return T[f["역할"]].format(**f, 극하는오행=over)
    f, b = box("박성우")
    _check("get_jeokjung_health: focus [] → 기존 균형 분기(신살 없음이면 line3도 기존 문구)", f == [] and "고른 편" in b["line1"] and "피로 누적" in b["title"] and b["line3"] == "피로 누적·번아웃 쪽을 관리 포인트로 봅니다.", str(b))
    _, b = box("박성우", ["양인살"])
    _check("균형 분기에도 양인 줄이 붙는다", b["line3"].startswith("⚠️ 양인까지") and "고른 편" in b["line1"], b["line3"])
    _, b = box("박성우", ["백호살"])
    _check("균형 분기에도 백호 줄이 붙는다", b["line3"].startswith("⚠️ 백호살까지 겹쳐 있어"), b["line3"])
    _check("백호 줄 문구 고정(균형 분기, 원문 전체 일치)", b["line3"] == "⚠️ 백호살까지 겹쳐 있어 — 다치거나 수술할 일이 없도록 조심하는 게 좋습니다. 검진도 미루지 않는 게 좋습니다.", b["line3"])
    f, b = box("박후규")
    over = f[0]["오행"]
    ok = len(f) == 2 and f[0]["계통"] in b["title"] and b["line1"] == fmt(f[0], over) and b["line2"] == fmt(f[1], over)
    _check("get_jeokjung_health: 박후규 main·sub가 focus 문구", ok, str(b))
    _, b = box("박후규", ["백호살"])
    _check("get_jeokjung_health: 백호 줄 순화 문구 고정(원문 전체 일치)", b["line3"] == "⚠️ 백호살까지 겹쳐 있어 — 다치거나 수술할 일이 없도록 조심하는 게 좋습니다. 검진도 미루지 않는 게 좋습니다.", b["line3"])
    _, b = box("박후규", ["양인살"])
    _check("get_jeokjung_health: 양인 줄(신살) 그대로", b["line3"].startswith("⚠️ 양인까지"), b["line3"])
    _, b = box("박후규")
    _check("get_jeokjung_health: 신살 없으면 순화된 검진 줄", b["line3"] == "검진 한 번 받아보시길 권합니다. 미루지 않는 게 좋습니다.", b["line3"])
    # 피극 행이 있는 명식(T3: 土과다·水피극)에서 극하는오행 = 과다 오행
    p = _pils(1971, 10, 9, 18, 59, "여")
    f = _run(p); bx = I.get_jeokjung_health({}, p, [])
    _check("피극 문구: 극하는오행이 같은 focus의 과다 오행", [x["역할"] for x in f][:2] == ["과다", "피극"] and bx["line2"] == "土 기운에 눌려 水 기운이 약해지기 쉬워, 신장·방광·비뇨기 쪽 관리가 필요합니다.", bx["line2"])
    # 박스 4줄 어디에도 % / 숫자 / 금지어가 없다(5명식 × 신살 3종)
    allbox = []
    for nm in ("박성우", "박후규"):
        for sn in ([], ["백호살"], ["양인살"]):
            _, bx2 = box(nm, sn); allbox += [bx2["title"], bx2["line1"], bx2["line2"]]
    _check("① 박스 title·line1·line2에 % 미노출·금지어 없음", all("%" not in t and "터집니다" not in t and "반드시" not in t and "위험" not in t and "집착" not in t for t in allbox))


def test_diag_weak_health_sentence_guard():
    """R1-b-3c-1 가드: _DIAG_WEAK_HEALTH_SENTENCE의 발췌 문장이 _DIAG_WEAK_DETAIL[같은 오행]
    원문에 정확히 1회 부분문자열로 들어있는지 확인한다. full_report가 str.replace로 이 문장을
    찾아 교체·삭제하므로, 원문 문구가 나중에 손질되면 replace가 무음으로 실패(0회 치환)해
    건강 줄이 그대로 남거나 사라지는 모습이 안 보이는 회귀가 생길 수 있다 — 그걸 여기서 잡는다."""
    S = I._DIAG_WEAK_HEALTH_SENTENCE
    D = I._DIAG_WEAK_DETAIL
    _check("_DIAG_WEAK_HEALTH_SENTENCE 대상 오행 = 火土金水(木 제외)", set(S) == {"火", "土", "金", "水"})
    for oh, sentence in S.items():
        _check(
            "_DIAG_WEAK_HEALTH_SENTENCE[%s]가 _DIAG_WEAK_DETAIL[%s] 원문에 정확히 1회 존재" % (oh, oh),
            oh in D and D[oh].count(sentence) == 1,
            "count=%d" % (D.get(oh, "").count(sentence) if oh in D else -1),
        )


def main():
    print("=== tests/health_focus_check.py ===")
    test_fixed()
    test_synthetic()
    test_constants()
    test_role_text_and_jeokjung()
    test_diag_weak_health_sentence_guard()
    print()
    if _FAILS:
        print("[FAIL] 실패 %d건: %s" % (len(_FAILS), _FAILS))
        sys.exit(1)
    print("[OK] 결과 요약: get_health_focus 단위 테스트 전부 통과")
    sys.exit(0)


if __name__ == "__main__":
    main()
