#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests/pils_fixtures.py — 검증용 사주 픽스처 (pytest 미사용, 순수 실행 스크립트)

- pils는 손으로 조립하지 않고 SajuPrecisionEngine.get_pillars() 계산 결과를 그대로 쓴다
  (UI(main())가 쓰는 것과 동일한 경로 — SajuCoreEngine 직접 호출 아님).
- manse.py는 import하지 않는다 (Streamlit 앱이라 import 시 부작용 발생 — check.py와 동일한 원칙).
  saju_engine / saju_interpreter / saju_sinsal 만 사용한다.

사용법:
    python tests/pils_fixtures.py     (리포 루트에서)
    python pils_fixtures.py           (tests/ 안에서)
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from saju_engine import SajuPrecisionEngine, get_ilgan_strength
from saju_interpreter import get_yongshin, get_gyeokguk
from saju_sinsal import get_gongmang


# pils 순서: [시주, 일주, 월주, 년주] (SajuPrecisionEngine.get_pillars 반환 그대로)
# baseline = 현재 판정 로직의 회귀 기준선.
# 8글자와 달리 절대 정답이 아니며, 명리 정합성 개선으로
# 정당하게 바뀔 수 있음. 그래서 불일치는 WARN만 발생.
# 값을 고칠 때는 반드시 근거를 확인할 것.
CASES = {
    "박성우": {
        "birth": (1969, 7, 14, 22, 30),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丁亥", "庚寅", "辛未", "己酉"],
        "baseline": {
            "신강신약": "신강",
            "격국명": "正印(정인)格",
            "종합_용신": ["水", "木", "火"],
            "공망": "午未",
        },
    },
    "박후규": {
        "birth": (1960, 11, 14, 23, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["己亥", "丙午", "丁亥", "庚子"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["木", "火", "土"],
        },
    },
    # 균시차(EoT) 경계 픽스처(F-EoT 라운드2) — 10/31(EoT 최댓값 +16.5분 근접)
    # 01:20생, 경도만 보정하면 자시(丙子)인데 균시차까지 더하면 축시(丁丑)로
    # 시주 자체가 바뀐다(일·월·년주는 불변) — 균시차 편입이 실제로 8글자를
    # 바꾸는 걸 보여주는 유일한 회귀 기준선(박성우·박후규는 경계에서 멀어
    # 무영향이라 이 케이스가 없으면 균시차 효과를 검증할 수 없다).
    "균시차경계_1031": {
        "birth": (1995, 10, 31, 1, 20),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丁丑", "乙未", "丙戌", "乙亥"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["木", "火", "水"],
            "공망": "辰巳",
        },
    },
    # 절입 기준분리 경계 픽스처(F-절입 라운드2) — 2024년 입춘(2/4 17:27 KST)과
    # "시계로" 똑같은 순간에 서울에서 태어난 경우. 진태양시(경도+균시차)로
    # 보정하면 16:41이라 아직 입춘 전(乙丑월/癸卯년)처럼 보이지만, 절입은
    # 위치 무관의 전지구적 순간이라 원시각(KST) 그대로 비교해야 한다 — 이번
    # 수정 전엔 월주뿐 아니라 연주까지 잘못됐었다(전년도 癸卯로 계산됨).
    # 수정 전(버그): ['庚申','戊戌','乙丑','癸卯']
    # 수정 후(원시각 비교, 현재): ['庚申','戊戌','丙寅','甲辰']
    "절입경계_20240204": {
        "birth": (2024, 2, 4, 17, 27),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["庚申", "戊戌", "丙寅", "甲辰"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["火", "土", "木"],
            "공망": "辰巳",
        },
    },
}

# TODO 윤미연: 1967년 甲戌 일주, 女.
# 후보 6개 — 1967-01-10 / 03-11 / 05-10 /
#            07-09 / 09-07 / 11-06
# 월(月) 확인되면 확정 후 추가


def get_pils(name):
    """CASES[name] 값으로 SajuPrecisionEngine.get_pillars()를 호출해 pils를 반환한다.
    반드시 SajuPrecisionEngine 경유(UI와 동일 경로) — SajuCoreEngine 직접 호출 금지."""
    case = CASES[name]
    y, m, d, h, mi = case["birth"]
    return SajuPrecisionEngine.get_pillars(
        y, m, d, h, mi,
        case["gender"],
        use_yaja_time=case["use_yaja_time"],
        longitude=case["longitude"],
    )


def assert_pillars(name):
    """반환 pils의 str 값 4개를 expect_pillars와 대조. 불일치 시 [FAIL] 출력 후 False."""
    case = CASES[name]
    pils = get_pils(name)
    actual = [p.get("str", "") for p in pils]
    expected = case["expect_pillars"]
    if actual == expected:
        print(f"[OK] {name} 8글자 일치: {actual}")
        return True
    print(f"[FAIL] {name} 8글자 불일치")
    print(f"    기대: {expected}")
    print(f"    실제: {actual}")
    return False


def check_baseline(name):
    """get_yongshin/get_ilgan_strength/get_gyeokguk/get_gongmang을 호출해 baseline과 대조.
    불일치는 [FAIL]이 아니라 [WARN]으로만 출력하고 종료코드에는 영향을 주지 않는다
    (판정 로직이 정당하게 개선될 수 있으므로)."""
    case = CASES[name]
    baseline = case.get("baseline", {})
    if not baseline:
        print(f"[INFO] {name}: baseline 없음, 건너뜀")
        return

    pils = get_pils(name)
    ilgan = pils[1].get("cg", "")

    if "신강신약" in baseline:
        strength = get_ilgan_strength(ilgan, pils) or {}
        actual = strength.get("신강신약", "")
        expected = baseline["신강신약"]
        if expected in actual:
            print(f"[OK] {name} 신강신약: {actual}")
        else:
            print(f"[WARN] {name} 신강신약 불일치 — 기대:{expected} 실제:{actual}")

    if "격국명" in baseline:
        gyeok = get_gyeokguk(pils) or {}
        actual = gyeok.get("격국명", "")
        expected = baseline["격국명"]
        if expected == actual:
            print(f"[OK] {name} 격국: {actual}")
        else:
            print(f"[WARN] {name} 격국 불일치 — 기대:{expected} 실제:{actual}")

    if "종합_용신" in baseline:
        ys = get_yongshin(pils) or {}
        actual = ys.get("종합_용신", [])
        expected = baseline["종합_용신"]
        if actual == expected:
            print(f"[OK] {name} 용신: {actual}")
        else:
            print(f"[WARN] {name} 용신 불일치 — 기대:{expected} 실제:{actual}")

    if "공망" in baseline:
        gm = get_gongmang(pils) or {}
        pair = gm.get("공망_지지", ("", ""))
        actual = "".join(pair)
        expected = baseline["공망"]
        if actual == expected:
            print(f"[OK] {name} 공망: {actual}")
        else:
            print(f"[WARN] {name} 공망 불일치 — 기대:{expected} 실제:{actual}")


def main():
    print("=== tests/pils_fixtures.py ===")
    all_pillars_ok = True
    for name in CASES:
        ok = assert_pillars(name)
        all_pillars_ok = all_pillars_ok and ok
        check_baseline(name)
        print()

    if all_pillars_ok:
        print("[OK] 결과 요약: 전체 픽스처 8글자 일치")
        sys.exit(0)
    else:
        print("[FAIL] 결과 요약: 8글자 불일치 픽스처 있음")
        sys.exit(1)


if __name__ == "__main__":
    main()
