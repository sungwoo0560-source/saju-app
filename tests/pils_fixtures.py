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
    # 주의: 丙子는 정답이 아니라 경도보정만 적용한 값 — GUI에서 분(Min) 위젯이
    # 실제로 반영되지 않아도(0분 취급) 그대로 재현되니 기대값으로 오인 금지.
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
    # 주의: 위 값은 정답이 아니라 f81b288 이전의 버그 값이다 — 기대값으로 오인
    # 절대 금지. 같은 값이 GUI에서 분(Min)이 0으로 미입력돼도 그대로 재현되니 혼동 주의.
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
    # 자정역전 경계 픽스처(M-T2 라운드) — 조자시(00:00~00:59)는 당일 일주라는
    # 원칙과 진태양시(경도+균시차) 보정이 자정을 역전시켜 일주를 전일로 미는
    # 동작이 충돌했던 버그의 회귀 기준선. 표준 크로싱(EoT≈0) 케이스.
    # 수정 전(버그, 일주가 전일로 밀림): ['壬子','丁丑','丁卯','甲辰']
    # 수정 후(원시각 날짜 사용, 현재): ['壬子','戊寅','丁卯','甲辰']
    "자정역전_20240315": {
        "birth": (2024, 3, 15, 0, 20),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬子", "戊寅", "丁卯", "甲辰"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["火", "土", "水", "金"],
            "공망": "申酉",
        },
    },
    # 자정역전 경계 픽스처 2 — EoT가 연중 최대 음수(2월 중순)라 역전 폭이
    # 가장 넓어지는 케이스(00:00~00:49대까지 전일로 역전됨, §2 실측 참고).
    # 수정 전(버그, 일주가 전일로 밀림): ['甲子','戊申','丙寅','甲辰']
    # 수정 후(원시각 날짜 사용, 현재): ['甲子','己酉','丙寅','甲辰']
    "자정역전_EoT최대_20240215": {
        "birth": (2024, 2, 15, 0, 10),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲子", "己酉", "丙寅", "甲辰"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "正官(정관)格",
            "종합_용신": ["火", "土", "木"],
            "공망": "寅卯",
        },
    },
    # 양인 정의 통일(L 라운드) 회귀 픽스처 — saju_zhengtong.py의 로컬 10천간
    # yangin_map(음간까지 포함)을 YANGIN_MAP(정통 양간 5개 전용) 단일 소스로
    # 교체했을 때, 이 차이가 baseline diff로 실제로 잡히는 유일한 조합.
    # 일간=乙(음간)이고 원국에 辰이 있어 구(舊) 10천간 정의에서만 활성돼
    # 사고수/바람기/큰병 점수에 "양인살" 가산이 붙었다 — 정통 통일 후에는
    # 비활성이 정답(음간은 양인 성립 안 함).
    "음간양인_보유_19640705": {
        "birth": (1964, 7, 5, 10, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["辛巳", "乙卯", "庚午", "甲辰"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["水", "金", "木"],
            "공망": "子丑",
        },
    },
    # 대조군 — 일간=乙(음간)이지만 원국에 辰이 없어, 구 정의·정통 정의
    # 둘 다 애초에 비활성인 경우. 위 케이스와 짝을 이뤄 "음간이라서
    # 항상 달라지는 게 아니라 辰 보유 여부에 따라 갈린다"를 확인한다.
    "음간양인_미보유_19660705": {
        "birth": (1966, 7, 5, 10, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["辛巳", "乙丑", "甲午", "丙午"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "傷官(상관)格",
            "종합_용신": ["水", "金", "木"],
            "공망": "戌亥",
        },
    },
    # 도화 관법 통일(P 라운드, c안: 년지OR일지 + 삼합국 목욕지) 회귀 픽스처 3건.
    # 년지만 성립 / 일지만 성립 / 둘 다 성립 각각을 재현해, 통일 전(일부
    # 지점은 년지만·일부는 일지만·일부는 사왕지 상호였던 상태)과 통일 후
    # (get_dohwa 단일 소스, 년지OR일지+목욕지)가 실제로 갈리는지 baseline이
    # 검증할 수 있게 한다.
    "도화_년지만_19700403": {
        "birth": (1970, 4, 3, 9, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙辰", "癸丑", "己卯", "庚戌"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["金", "水", "火"],
            "공망": "寅卯",
        },
    },
    "도화_일지만_19701003": {
        "birth": (1970, 10, 3, 9, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬辰", "丙辰", "乙酉", "庚戌"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏財(편재)格",
            "종합_용신": ["木", "火"],
            "공망": "子丑",
        },
    },
    "도화_년일지둘다_19701213": {
        "birth": (1970, 12, 13, 9, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲辰", "丁卯", "戊子", "庚戌"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["火", "土", "木"],
            "공망": "戌亥",
        },
    },
    # 배우자성 감당력 축(관계운 R 라운드) 회귀 픽스처 4건 — get_gamdang_pattern
    # 6패턴 중 Q6 진단에서 커버리지가 0건이던 4종을 채운다.
    "감당력_남약왕무근_19780520": {
        "birth": (1978, 5, 20, 6, 16),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["癸卯", "壬午", "丁巳", "戊午"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["水", "金"],
            "공망": "申酉",
        },
    },
    "감당력_남강성왕_19981009": {
        "birth": (1998, 10, 9, 17, 34),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["癸酉", "己丑", "壬戌", "戊寅"],
        "baseline": {
            "신강신약": "신강",
            "격국명": "月劫格",
            "종합_용신": ["木", "水", "火"],
            "공망": "午未",
        },
    },
    "감당력_여강성무_20001028": {
        "birth": (2000, 10, 28, 15, 23),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬申", "己未", "丙戌", "庚辰"],
        "baseline": {
            "신강신약": "극신강",
            "격국명": "月劫格",
            "종합_용신": ["木", "水", "火"],
            "공망": "子丑",
        },
    },
    "감당력_중화_19991116": {
        "birth": (1999, 11, 16, 13, 55),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丁未", "壬申", "乙亥", "己卯"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "建祿格",
            "종합_용신": ["木", "火", "土"],
            "공망": "戌亥",
        },
    },
    # 효신탈식(梟神奪食) 회귀 픽스처 2건(식신생재 정밀화 라운드) — 기존
    # 15건은 전부 raw 인접 성립+효신 인접+통근 조건을 동시에 만족하는
    # 케이스가 없어(효신탈식 실제 발동 0건), 대조쌍을 새로 추가한다.
    "효신탈식_발동_19981226": {
        # 丁일간, 식신(己, 일지未)이 재성(辛, 시간)과 인접(거리1)하지만
        # 인성(甲, 월간+년지寅 통근)이 식신(未)과도 인접(거리1)하고
        # 통근까지 있어 효신탈식 발동 — 식신생재 불성립이 기대값.
        "birth": (1998, 12, 26, 22, 37),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["辛亥", "丁未", "甲子", "戊寅"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["火", "土", "木"],
            "공망": "寅卯",
        },
    },
    "효신탈식_불발동_20060404": {
        # 辛일간, 식신·재성 인접 성립 + 인성도 식신과 인접하지만 통근이
        # 없어(뜬 인성) 효신탈식 불발동 — 식신생재 성립 유지가 기대값.
        # 위 발동 케이스와 "인접은 같은데 통근만 다른" 대조쌍.
        "birth": (2006, 4, 4, 20, 11),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬戌", "癸亥", "辛卯", "丙戌"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["金", "水", "火"],
            "공망": "子丑",
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
