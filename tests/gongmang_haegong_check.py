# -*- coding: utf-8 -*-
"""get_haegong(saju_sinsal.py) 단위 테스트 — 8케이스.

G2 재작성 라운드: 전실/충공/합공은 "공망 쌍 전체"가 아니라 "원국의
시지·월지·년지 중 실제로 공망 글자인 대상"만 기준으로 판정해야 한다.
공망 쌍의 나머지 한 글자가 원국에 없으면 그 글자는 판정 대상이 아니다
(세운·대운이 그 글자 자체이거나 그 글자를 충/합해도 무관 처리 —
"세운 공망(허)" 영역이지 해공이 아님). 길흉 해석은 검증 범위 밖.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from saju_sinsal import get_haegong
from pils_fixtures import get_pils

# 박성우: pils=[시,일,월,년]=丁亥/庚寅/辛未/己酉, 일주庚寅 → 공망(午,未).
# 원국 시지=亥(공망 아님)/월지=未(공망 O)/년지=酉(공망 아님)
# → 대상 글자는 未 하나뿐(午는 공망 쌍이지만 원국에 실재하지 않아 대상 제외).
PARK = get_pils("박성우")

CASES = []

# 1) 세운 午 / 대운 丑 → 午는 대상(未) 자체도 아니고 未의 충(丑)도 육합(午)
#    조건 예외(운지지가 공망쌍 멤버라 합공 불인정)에도 걸려 "없음".
#    丑은 未의 충(丑未沖) → 대운 충공(2). 세운 0 + 대운 2 → 겹침 없음(세운 0), 종합 2.
CASES.append({
    "name": "1. 박성우 세운 午 / 대운 丑",
    "pils": PARK, "sewoon_jj": "午", "daewoon_jj": "丑",
    "expect": {"세운_등급": 0, "대운_등급": 2, "종합_등급": 2, "겹침": False},
})

# 2) 세운 未(대상 글자 자체) → 전실(3). 대운 丑(未의 충) → 충공(2). 둘다>0 → 겹침, 종합 3.
CASES.append({
    "name": "2. 박성우 세운 未 / 대운 丑",
    "pils": PARK, "sewoon_jj": "未", "daewoon_jj": "丑",
    "expect": {"세운_등급": 3, "대운_등급": 2, "종합_등급": 3, "겹침": True},
})

# 3) 세운 丑 / 대운 丑 — 둘 다 未의 충 → 각각 충공(2), 겹침 → 종합 min(3, 2+1)=3.
CASES.append({
    "name": "3. 박성우 세운 丑 / 대운 丑",
    "pils": PARK, "sewoon_jj": "丑", "daewoon_jj": "丑",
    "expect": {"세운_등급": 2, "대운_등급": 2, "종합_등급": 3, "겹침": True},
})

# 4) 세운 未(전실 3) / 대운 寅(未와 무관: 충도 합도 아님) → 대운 0, 겹침 없음, 종합 3.
CASES.append({
    "name": "4. 박성우 세운 未 / 대운 寅",
    "pils": PARK, "sewoon_jj": "未", "daewoon_jj": "寅",
    "expect": {"세운_등급": 3, "대운_등급": 0, "종합_등급": 3, "겹침": False},
})

# 5) 세운 子 / 대운 없음 — 子는 午를 충하지만 午는 원국에 없는 공망 글자(대상 제외).
#    대상(未)과 子는 전실·충·합 어느 것도 아님 → 빈 결과(등급0).
CASES.append({
    "name": "5. 박성우 세운 子 / 대운 없음 (子는 午를 충하나 午는 원국에 없음)",
    "pils": PARK, "sewoon_jj": "子", "daewoon_jj": "",
    "expect": {"세운_등급": 0, "대운_등급": 0, "종합_등급": 0, "겹침": False},
})

# 6) 정상 합공 — 甲子旬(공망 戌亥), 원국에 戌이 실제로 존재하는 명식.
#    8글자(년/월/일/시): 甲子年 丙子月 甲子日 甲戌時 → pils=[시,일,월,년]
#    = [甲戌, 甲子, 丙子, 甲子]. 시지=戌(공망 O, 대상) / 월지=子·년지=子(공망 아님).
#    세운 卯 → 卯는 대상(戌)의 육합(HAP_MAP[戌]="卯") 이고 卯는 공망쌍(戌,亥) 멤버가
#    아니므로 합공(1) 성립.
GAPJA_HAP = [
    {"cg": "甲", "jj": "戌"},  # 시주
    {"cg": "甲", "jj": "子"},  # 일주
    {"cg": "丙", "jj": "子"},  # 월주
    {"cg": "甲", "jj": "子"},  # 년주
]
CASES.append({
    "name": "6. 정상 합공 (甲子旬, 시지 戌 실재, 세운 卯)",
    "pils": GAPJA_HAP, "sewoon_jj": "卯", "daewoon_jj": "",
    "expect": {"세운_등급": 1, "대운_등급": 0, "종합_등급": 1, "겹침": False},
})

# 7) 원국에 공망 글자가 하나도 없는 명식 — 甲子日(공망 戌亥)인데 시지/월지/년지가
#    각각 子/丑/寅으로 戌·亥 어느 것도 아님.
#    8글자(년/월/일/시): 丙寅年 辛丑月 甲子日 甲子時 → pils=[시,일,월,년]
#    = [甲子, 甲子, 辛丑, 丙寅]. 세운은 아무거나(子)로 둬도 대상 자체가 없어 빈 결과.
GAPJA_NONE = [
    {"cg": "甲", "jj": "子"},  # 시주
    {"cg": "甲", "jj": "子"},  # 일주
    {"cg": "辛", "jj": "丑"},  # 월주
    {"cg": "丙", "jj": "寅"},  # 년주
]
CASES.append({
    "name": "7. 원국에 공망 글자 없음 (甲子日, 시/월/년지=子/丑/寅)",
    "pils": GAPJA_NONE, "sewoon_jj": "子", "daewoon_jj": "",
    "expect": {"세운_등급": 0, "대운_등급": 0, "종합_등급": 0, "겹침": False},
})

# 8) 세운 寅 / 대운 없음 — 寅은 대상(未)과 전실·충·합 어느 것도 아닌 무관한 지지.
CASES.append({
    "name": "8. 박성우 세운 寅 / 대운 없음 (관련 없는 운 지지)",
    "pils": PARK, "sewoon_jj": "寅", "daewoon_jj": "",
    "expect": {"세운_등급": 0, "대운_등급": 0, "종합_등급": 0, "겹침": False},
})


def run():
    fail = 0
    for c in CASES:
        r = get_haegong(c["pils"], sewoon_jj=c["sewoon_jj"], daewoon_jj=c["daewoon_jj"])
        e = c["expect"]
        ok = (
            r["세운_판정"]["등급"] == e["세운_등급"]
            and r["대운_판정"]["등급"] == e["대운_등급"]
            and r["종합"]["등급"] == e["종합_등급"]
            and r["종합"]["겹침"] == e["겹침"]
        )
        status = "PASS" if ok else "FAIL"
        if not ok:
            fail += 1
        print(f"[{status}] {c['name']}")
        print(f"  입력: sewoon_jj={c['sewoon_jj']!r} daewoon_jj={c['daewoon_jj']!r}")
        print(f"  기대: {e}")
        print(f"  실제: {r}")
        print()

    if fail:
        print(f"[FAIL] {fail}/{len(CASES)}건 실패")
        return False
    print(f"[PASS] {len(CASES)}/{len(CASES)}건 전부 통과")
    return True


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
