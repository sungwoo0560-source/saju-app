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

from saju_engine import SajuPrecisionEngine, get_ilgan_strength, get_pillars_12beol, format_12beol_display
from saju_interpreter import get_yongshin, get_gyeokguk, build_saju_tongbyeon, get_yongshin_multilayer
from saju_sinsal import get_gongmang, get_yangin, get_extra_sinsal, HONGYEOM_MAP
from saju_zhengtong import render_jonghap_pyongron, render_four_pillars_card, calc_all_sinsal_extended


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
        # ★2026-09-10 GMT+8:30 4주 공통 정규화(TimeCorrection._normalize_local_clock)
        # 적용으로 값 갱신 — 1960년은 GMT+8:30 구간(1954-03-21~1961-08-10 00:30) 안이라
        # +30분 정규화 영향을 받는다(시주 己亥->庚子로 변경, 나머지 3주 무변).
        "birth": (1960, 11, 14, 23, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["庚子", "丙午", "丁亥", "庚子"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["木", "火", "土"],
            "공망": "寅卯",
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
    # 근사구간(AstroEngine, KASI 데이터 없음) 입춘 4시간 기준시각 교정 회귀 픽스처 3건.
    # saju_engine.py의 AstroEngine ref_times/ref_times_all(298·317행)이 kasi_24terms.json의
    # 2000년 입춘 사본인데, f81b288(2000년 KASI 데이터 결손 수정, 2/4 21:40 확정)때 이
    # 사본 갱신이 누락돼 "입춘": (2, 4, 17, 40) 상태로 4시간 틀린 채 남아 있었다 — 이 오차가
    # diff_years*365.24219 선형 외삽의 기준시각이라 1940-1999·2028-2040 전 구간(근사구간)
    # 입춘 계산에 그대로 전파됐다. 아래 3건은 그 4시간 창(교정전 목표시각~교정후 목표시각)
    # 안에서 태어나 연주·월주가 통째로 바뀌는 실제 사례다(각 케이스 옆 "교정 전(버그)"
    # 연주 참고 — 정답이 아니라 회귀 대조용).
    "근사구간_입춘4시간교정_19700204": {
        # 교정 전(버그) 연주: 庚戌(1970년 취급) — 실제 입춘(15:17)보다 이른 13:00생인데
        # 옛 기준시각(11:17)만 지나 "이미 입춘 지남"으로 오판정됐었다.
        "birth": (1970, 2, 4, 13, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬午", "乙卯", "丁丑", "己酉"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏財(편재)格",
            "종합_용신": ["火", "木", "水"],
            "공망": "子丑",
        },
    },
    "근사구간_입춘4시간교정_19800204": {
        # 교정 전(버그) 연주: 庚申(1980년 취급), 자정을 넘나드는 케이스(교정전 목표
        # 21:24~교정후 목표 01:23(익일)가 4시간 창 — 절입 오차가 날짜 경계까지 흔든다).
        "birth": (1980, 2, 4, 23, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["辛亥", "丁未", "丁丑", "己未"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["火", "木"],
            "공망": "寅卯",
        },
    },
    "근사구간_입춘4시간교정_19990204": {
        # 교정 전(버그) 연주: 己卯(1999년 취급).
        "birth": (1999, 2, 4, 13, 30),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙午", "丁亥", "乙丑", "戊寅"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "食神(식신)格",
            "종합_용신": ["火", "木"],
            "공망": "午未",
        },
    },
    # AstroEngine→정밀계산(ephem) 교체 회귀 픽스처 3쌍(2026-09-10) — kasi_24terms.json이
    # 1940~2040 전 구간을 실측/정밀계산으로 커버하게 된 뒤, 이전엔 AstroEngine 선형
    # 외삽이 자정 부근에서 날짜를 밀리게 만들었던 지점(17건 날짜갈림 목록 중 3개)을
    # "절입 직전 1분/직후 1분"으로 고정해 8글자가 실제로 갈리는지(또는 안 갈리는지)
    # 검증한다. 값은 tools/gen_solar_terms_ephem.py 기반 kasi_24terms.json에서 나옴.
    "근사구간_1955입춘_정규화후경계_직전": {
        # ★2026-09-10 재설계 — GMT+8:30 +30분 정규화를 반영해 원시각(그 시절
        # 시계값)을 역산했다. 절입(1955-02-04 23:17 KST) 1분 전이 되도록
        # 정규화 후 23:16이 나오게: 원시각 22:46(+30분=23:16). 아직 갑오년/축월.
        "birth": (1955, 2, 4, 22, 46),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["己亥", "丙申", "丁丑", "甲午"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "傷官(상관)格",
            "종합_용신": ["火", "木"],
            "공망": "辰巳",
        },
    },
    "근사구간_1955입춘_정규화후경계_직후": {
        # 원시각 22:48(+30분=23:18, 절입 1분 후) — 을미년/인월로 전환. ★입춘은
        # 연주·월주 경계 동시 담당이라 위 케이스와 짝지어 연주까지 바뀌는 걸
        # 실증하는 유일한 픽스처(정규화 후 시각 기준으로 재역산 완료).
        "birth": (1955, 2, 4, 22, 48),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["己亥", "丙申", "戊寅", "乙未"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "미정격",
            "종합_용신": ["火", "木"],
            "공망": "辰巳",
        },
    },
    "근사구간_1948입추_정규화후경계_직전": {
        # ★2026-09-10 재설계 — DST -1시간 정규화를 반영해 원시각을 역산했다.
        # 절입(1948-08-08 00:26 KST) 1분 전이 되도록: 원시각 01:25(-1h=00:25).
        # 아직 己未월.
        "birth": (1948, 8, 8, 1, 25),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙子", "乙丑", "己未", "戊子"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "偏財(편재)格",
            "종합_용신": ["水", "木", "金"],
            "공망": "戌亥",
        },
    },
    "근사구간_1948입추_정규화후경계_직후": {
        # 원시각 01:27(-1h=00:27, 절입 1분 후) — 庚申월로 전환. 입추는 연주
        # 경계가 아니라 연주(戊子)는 불변, 월주만 갈리는 걸 보여주는 대조
        # 케이스(위 입춘 쌍과 구분, 정규화 후 시각 기준으로 재역산 완료).
        "birth": (1948, 8, 8, 1, 27),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙子", "乙丑", "庚申", "戊子"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "正官(정관)格",
            "종합_용신": ["水", "木", "土", "火"],
            "공망": "戌亥",
        },
    },
    "근사구간_1959동지_직전_중기무변": {
        # ★동지는 中氣(월주 경계가 아닌 節 사이 절기)라 절입 시각이 앞뒤로 1440분(하루)
        # 가까이 틀려도 8글자에 전혀 영향이 없다 — 절입 직전/직후 쌍의 값이 완전히
        # 동일한 것이 정상(연주·월주 경계 절기인 위 두 쌍과 대비되는 대조군).
        # 값은 2026-09-10 4주 공통 정규화 반영 갱신(1959년은 GMT+8:30 구간).
        "birth": (1959, 12, 22, 23, 33),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲子", "己卯", "丙子", "己亥"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏財(편재)格",
            "종합_용신": ["火", "土"],
            "공망": "申酉",
        },
    },
    "근사구간_1959동지_직후_중기무변": {
        "birth": (1959, 12, 22, 23, 35),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲子", "己卯", "丙子", "己亥"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏財(편재)格",
            "종합_용신": ["火", "土"],
            "공망": "申酉",
        },
    },
    # GMT+8:30 표준시·DST 4주 공통 정규화(TimeCorrection._normalize_gmt830) 회귀
    # 픽스처 9건(2026-09-10) — 1954-03-21~1961-08-09 구간에 한해 원본 출생시각을
    # +30분(DST 겹침이면 순서상 -1h 후 +30분=최종 -30분)으로 정규화해 오늘날
    # KST로 환산한 뒤, 이 값을 get_corrected_time() 입력과 term_*(월주·연주·일주가
    # 보는 원시각) 양쪽에 동일하게 먹인다.
    "경계시작_직전_19540320": {
        # 1954-03-21 00:00 경계 바로 전(구간 밖) — 정규화 미적용, 무변경.
        "birth": (1954, 3, 20, 23, 59),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊子", "乙亥", "丁卯", "甲午"],
        "baseline": {
            "신강신약": "극신강",
            "격국명": "建祿格",
            "종합_용신": ["金", "土", "火", "水"],
            "공망": "申酉",
        },
    },
    "경계시작_직후_19540321": {
        # 경계 시작 정각 — +30분 적용(00:00->00:30). 시주(자시->축시)·일간 모두
        # 바뀌어 위 케이스와 짝을 이룬다.
        "birth": (1954, 3, 21, 0, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊子", "丙子", "丁卯", "甲午"],
        "baseline": {
            "신강신약": "신강",
            "격국명": "偏印(편인)格",
            "종합_용신": ["水", "金", "火"],
            "공망": "申酉",
        },
    },
    "경계끝_직전_롤오버_19610809": {
        # ★일주 flip 실증: 23:50에 +30분이 더해져 00:20(익일 1961-08-10)로
        # 날짜가 넘어간다 — 정규화 전(구코드 pass) 일주는 甲戌이었으나
        # 정규화 후 乙亥(8/10 기준)로 확정된다.
        "birth": (1961, 8, 9, 23, 50),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙子", "乙亥", "丙申", "辛丑"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "正官(정관)格",
            "종합_용신": ["土", "火"],
            "공망": "申酉",
        },
    },
    "경계확장_1961년0810_0010_구간안8글자무변": {
        # ★2026-09-10 tzdata 정밀대조로 GMT+8:30 종료 경계가 1961-08-09 23:59
        # -> 1961-08-10 00:30(exclusive)으로 30분 확장됨에 따라, 이 시각
        # (00:10)은 이제 "구간 밖 대조군"이 아니라 "구간 안"이다(+30분 정규화
        # 대상, 00:10->00:40). 다만 00:10과 00:40이 둘 다 같은 子시(23:00~
        # 00:59)·같은 날짜(8/10) 안이라 8글자는 우연히 불변 — 5분 간격 전수
        # 스윕(00:00~00:25)으로 이 창 전체가 불변임을 실측 확인했다.
        # 경계값이 다시 틀어지면(예: 00:30을 넘는 값으로 잘못 확장되면) 이
        # 픽스처가 잡아준다.
        "birth": (1961, 8, 10, 0, 10),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙子", "乙亥", "丙申", "辛丑"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "正官(정관)格",
            "종합_용신": ["土", "火"],
            "공망": "申酉",
        },
    },
    "구간밖_19530615": {
        # 구간(1954-03-21~1961-08-09) 훨씬 이전 — 무변경 고정.
        "birth": (1953, 6, 15, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙午", "丁酉", "戊午", "癸巳"],
        "baseline": {
            "신강신약": "극신강",
            "격국명": "建祿格",
            "종합_용신": ["水", "金"],
            "공망": "辰巳",
        },
    },
    "구간밖_19620615": {
        # 구간 훨씬 이후 — 무변경 고정.
        "birth": (1962, 6, 15, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["庚午", "甲申", "丙午", "壬寅"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "食神(식신)格",
            "종합_용신": ["水", "金", "木"],
            "공망": "午未",
        },
    },
    "1955입춘_연주월주flip_2300": {
        # 1955-02-04 23:00(원시각) +30분=23:30 — 절입(23:17 KST) 이후로 넘어가
        # 연주·월주가 동시에 flip된다(정규화 없었다면 절입 전이라 甲午년/丁丑월).
        "birth": (1955, 2, 4, 23, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["己亥", "丙申", "戊寅", "乙未"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "미정격",
            "종합_용신": ["火", "木"],
            "공망": "辰巳",
        },
    },
    "DST겹침_1958여름": {
        # DST 기간(1958-05-04~09-21) + GMT+8:30 구간 겹침 — 순서상 -1h(DST)
        # 후 +30분(표준시)=최종 -30분(12:00->11:30).
        "birth": (1958, 7, 15, 12, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丁巳", "癸巳", "己未", "戊戌"],
        "baseline": {
            "신강신약": "극신약",
            "격국명": "偏官(편관)格",
            "종합_용신": ["水", "木", "金"],
            "공망": "午未",
        },
    },
    "DST없음_GMT830_1954봄": {
        # GMT+8:30 구간이지만 DST 비대상(1954년은 DST_PERIODS에 없음) — 표준시
        # +30분만 적용(12:00->12:30). 위 DST 겹침 케이스와 부호 대조.
        "birth": (1954, 4, 15, 12, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲午", "辛丑", "戊辰", "甲午"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "正印(정인)格",
            "종합_용신": ["木", "火", "水"],
            "공망": "辰巳",
        },
    },
    # 1987~1988 DST 회귀 픽스처 3건(2026-09-10) — GMT+8:30 구간(1954~1961) 밖이지만
    # DST_PERIODS에는 속해 이번 4주 공통 정규화의 영향을 처음 받는 시대. 현재
    # 주력 사용자층(40대 전후) 출생 구간이라 별도로 고정한다.
    "DST1987_시작전_0510_0030_구간밖": {
        # ★2026-09-10 tzdata 정정으로 1987 DST 시작이 05-10 00:00->03:00으로
        # 바뀌어, 00:30은 더 이상 DST 구간이 아니다(정정 전엔 이미 시작했다고
        # 오판정했었다 — 정정 후 미적용 확정, 정규화 없음 그대로).
        "birth": (1987, 5, 10, 0, 30),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲子", "己未", "乙巳", "丁卯"],
        "baseline": {
            "신강신약": "중화",
            "격국명": "正印(정인)格",
            "종합_용신": ["水", "金"],
            "공망": "子丑",
        },
    },
    "DST1987_종료직전_1010_2330": {
        # DST 종료(1987-10-11 00:00) 직전 — -1시간 적용(23:30->22:30, 일주가
        # 전일 기준으로 바뀜). 구코드는 壬子壬辰庚戌丁卯(일주 壬子)였다.
        "birth": (1987, 10, 10, 23, 30),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["辛亥", "壬辰", "庚戌", "丁卯"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "正財(정재)格",
            "종합_용신": ["金", "水", "木", "火"],
            "공망": "午未",
        },
    },
    "DST1987_밖_대조군_겨울": {
        # DST 기간(5/10~10/11) 밖(1월, 겨울철) — 정규화 미적용, 무변경 대조군.
        "birth": (1987, 1, 15, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["庚午", "甲子", "辛丑", "丙寅"],
        "baseline": {
            "신강신약": "신약",
            "격국명": "正官(정관)格",
            "종합_용신": ["火", "木", "水"],
            "공망": "戌亥",
        },
    },
    # ── 양인 sentinel 충돌 회귀(2026-09-10) ──────────────────────────────
    # get_yangin()/detect_life_risk_signals()가 "양인 없음"(음간 일간)과
    # "시간미상이라 시주 없음"(manse.py:29345-29346)을 둘 다 빈 문자열로
    # 표시해 서로 매칭되던 결함의 고정 기준선. birth의 시(時)는 임의값(12:00)
    # — 아래 check_yangin_unknown_time()이 pils[0]을 직접 블랭크 처리해
    # manse.py의 시간미상 분기를 재현하므로 실제로는 쓰이지 않는다.
    "박후규_1969_계사일_시간미상": {
        "birth": (1969, 11, 14, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊午", "癸巳", "乙亥", "己酉"],
    },
    "음간양인_시간미상_乙": {
        "birth": (1990, 1, 10, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬午", "乙亥", "丁丑", "己巳"],
    },
    "음간양인_시간미상_丁": {
        "birth": (1990, 1, 2, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙午", "丁卯", "丙子", "己巳"],
    },
    "음간양인_시간미상_己": {
        "birth": (1990, 1, 4, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["庚午", "己巳", "丙子", "己巳"],
    },
    "음간양인_시간미상_辛": {
        "birth": (1990, 1, 6, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲午", "辛未", "丁丑", "己巳"],
    },
    "음간양인_시간미상_癸": {
        "birth": (1990, 1, 8, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊午", "癸酉", "丁丑", "己巳"],
    },
    # 양간 대조군 — 일지·년지(시주와 무관한 자리)에 양인이 실재해, 시간미상
    # 처리로 시주가 블랭크돼도 존재=True가 유지돼야 한다(과교정 방지 확인용).
    "양간대조_시간미상_丙": {
        "birth": (1990, 2, 10, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲午", "丙午", "戊寅", "庚午"],
    },
    # 12벌 수렴도 표시 회귀(2026-09-11) — 수렴 높음/중간/낮음 3단계.
    # birth의 시(時)는 임의값(12:00) — check_12beol_convergence()가 pils[0]을
    # 직접 블랭크하고 get_pillars_12beol()로 12벌을 따로 산출하므로 실제로는
    # 안 쓰인다(다른 시간미상 픽스처들과 동일 관례).
    "12벌_수렴높음_박후규": {
        "birth": (1960, 11, 14, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["甲午", "丙午", "丁亥", "庚子"],
    },
    "12벌_수렴중간_19301020": {
        "birth": (1930, 10, 20, 12, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊午", "癸卯", "丙戌", "庚午"],
    },
    "12벌_수렴낮음_19301009": {
        "birth": (1930, 10, 9, 12, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丙午", "壬辰", "丙戌", "庚午"],
    },
    # 홍염살 SSOT 통일 회귀(2026-09-12) — 乙일간은 기존 saju_sinsal(申)과
    # zhengtong(午)이 갈리던 유일한 간이었다. HONGYEOM_MAP 통일 후 甲과
    # 같은 午로 확정 — 이 픽스처는 乙일간+午 실보유 케이스로 두 함수의
    # 판정 일치(회귀 방지)를 고정한다.
    "홍염_乙일간_午보유": {
        "birth": (1997, 4, 13, 12, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["壬午", "乙酉", "甲辰", "丁丑"],
    },
    # 대조군 — 乙일간이지만 원국에 午가 없어 홍염살이 뜨면 안 되는 케이스.
    "홍염_乙일간_午미보유": {
        "birth": (1973, 2, 18, 22, 0),
        "gender": "남",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["丁亥", "乙酉", "甲寅", "癸丑"],
    },
    # set 정렬 없는 순회 결정성 회귀(2026-09-12) — manse.py:2628-2630
    # (_local_saju_engine 기신/용신 세운 문구). 기신 2종(火·土) 보유 케이스 —
    # PYTHONHASHSEED에 따라 '火, 土'/'土, 火'로 갈리던 것을 오행 표준순서
    # (木火土金水)로 고정했는지 확인.
    "오행순서_기신2종_20020516": {
        "birth": (2002, 5, 16, 19, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["癸酉", "甲申", "乙巳", "壬午"],
    },
    # set 정렬 없는 순회 결정성 회귀(2026-09-12) — manse.py:15328-15341
    # (menu_current_situation 자형 위험카드). 辰辰亥亥 — 자형이 2종 동시 발동하는
    # 케이스. PYTHONHASHSEED에 따라 ['辰','亥']/['亥','辰']로 갈리던 것을
    # 12지지 표준순서(子丑寅卯辰巳午未申酉戌亥)로 고정했는지 확인.
    "지지순서_자형2종_19951109": {
        "birth": (1995, 11, 9, 8, 0),
        "gender": "여",
        "longitude": 126.98,
        "use_yaja_time": True,
        "expect_pillars": ["戊辰", "甲辰", "丁亥", "乙亥"],
    },
}

# 위 "시간미상" 픽스처들의 get_yangin() 기대값 — (존재 여부, 위치 목록).
# 위치는 blanking 후 pils 순서([시주,일주,월주,년주]) 기준 라벨.
YANGIN_UNKNOWN_TIME_EXPECT = {
    "박후규_1969_계사일_시간미상": (False, []),
    "음간양인_시간미상_乙": (False, []),
    "음간양인_시간미상_丁": (False, []),
    "음간양인_시간미상_己": (False, []),
    "음간양인_시간미상_辛": (False, []),
    "음간양인_시간미상_癸": (False, []),
    "양간대조_시간미상_丙": (True, ["일주", "년주"]),
}

# render_jonghap_pyongron·render_four_pillars_card의 "시주 빈 괄호 ()" 회귀(2026-09-11).
# 기존 픽스처 재사용 — 시간미상 1건 + 시간확정 대조군 1건.
SIJU_DISPLAY_EXPECT = {
    "박후규_1969_계사일_시간미상": True,   # 시간미상 — "시간 미상" 문구, () 미노출 기대
    "박후규": False,                        # 시간확정 대조군 — 실제 간지 노출, "시간 미상" 미노출 기대
}

# 12벌 수렴도 표시 회귀(2026-09-11) — saju_engine.get_pillars_12beol() +
# format_12beol_display()의 실제 산출값을 고정한다. "격국"/"주용신"은
# item_type="general", "신강약"은 엄격 기준, "대운수"는 원시 오프셋(대운수)
# 기준(get_crossing_interpretation의 "현재 대운 블록 보정"은 이 픽스처의
# 범위 밖 — build_saju_tongbyeon/get_pillars_12beol 자체의 회귀만 고정).
TWELVE_BEOL_EXPECT = {
    "12벌_수렴높음_박후규": {
        "격국": "偏官(편관)格 (시간 미상 — 12벌 중 10벌 기준)",
        "신강약": "신약 또는 중화",
        "주용신": "木 (시간 미상 — 12벌 중 11벌 기준)",
        "대운수": "7세",
    },
    "12벌_수렴중간_19301020": {
        "격국": "正官(정관)格 (시간 미상 — 12벌 중 10벌 기준)",
        "신강약": "극신약(極身弱) 또는 신약(身弱)",
        "주용신": "金",
        "대운수": "3세",
    },
    "12벌_수렴낮음_19301009": {
        "격국": "偏官(편관)格 또는 偏印(편인)格",
        "신강약": "신약 또는 중화",
        "주용신": "⚠️ 金 (7/12 — 시간에 따라 달라질 수 있음)",
        "대운수": "1세 (시간에 따라 3가지)",
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


def check_yangin_unknown_time(name):
    """manse.py:29345-29346의 '시간미상 시 pils[0] 블랭크' 분기를 재현해
    get_yangin()의 sentinel 충돌 회귀를 고정한다. [FAIL] 시 False 반환."""
    expected_exists, expected_loc = YANGIN_UNKNOWN_TIME_EXPECT[name]
    pils = get_pils(name)
    pils_unknown = [dict(p) for p in pils]
    pils_unknown[0] = {"cg": "", "jj": "", "str": ""}

    result = get_yangin(pils_unknown)
    actual_exists = result.get("존재", False)
    actual_loc = result.get("위치", [])

    if actual_exists == expected_exists and actual_loc == expected_loc:
        print(f"[OK] {name} 양인(시간미상) 존재={actual_exists} 위치={actual_loc}")
        return True
    print(f"[FAIL] {name} 양인(시간미상) 불일치")
    print(f"    기대: 존재={expected_exists} 위치={expected_loc}")
    print(f"    실제: 존재={actual_exists} 위치={actual_loc}")
    return False


def check_siju_unknown_display(name, expect_unknown):
    """render_jonghap_pyongron·render_four_pillars_card의 시주 표시 회귀(2026-09-11).
    시간미상이면 '시간 미상' 문구가 나오고 빈 괄호 '()'가 남지 않아야 하며,
    시간확정 대조군은 실제 간지가 그대로 나오고 '시간 미상'이 섞이면 안 된다."""
    case = CASES[name]
    pils = get_pils(name)
    if expect_unknown:
        pils = [dict(p) for p in pils]
        pils[0] = {"cg": "", "jj": "", "str": ""}

    birth_year = case["birth"][0]
    gender = case["gender"]

    html1 = render_jonghap_pyongron(pils, name, birth_year, gender, marriage_status="미혼", cur_year=2026)
    html2 = render_four_pillars_card(pils, name)

    ok = True
    if expect_unknown:
        if "()" in html1 or "()" in html2:
            print(f"[FAIL] {name} 시주표시(시간미상): 빈 괄호 '()' 잔존")
            ok = False
        if "시간 미상" not in html1 or "시간 미상" not in html2:
            print(f"[FAIL] {name} 시주표시(시간미상): '시간 미상' 문구 누락")
            ok = False
    else:
        siju_str = pils[0]["str"]
        siju_cg, siju_jj = pils[0]["cg"], pils[0]["jj"]
        # html1(년/월/일/시 인접 텍스트)은 문자열 그대로, html2(카드)는
        # cg/jj 사이에 <span> 태그가 끼어 "간지" 연속 문자열이 안 나오므로 개별 확인.
        if siju_str not in html1:
            print(f"[FAIL] {name} 시주표시(시간확정): render_jonghap_pyongron에 실제 간지({siju_str}) 미노출")
            ok = False
        if siju_cg not in html2 or siju_jj not in html2:
            print(f"[FAIL] {name} 시주표시(시간확정): render_four_pillars_card에 실제 간지({siju_cg}{siju_jj}) 미노출")
            ok = False
        if "시간 미상" in html1 or "시간 미상" in html2:
            print(f"[FAIL] {name} 시주표시(시간확정): '시간 미상' 과잉 노출")
            ok = False

    if ok:
        print(f"[OK] {name} 시주표시 정상 (시간미상={expect_unknown})")
    return ok


def check_12beol_convergence(name):
    """12벌 수렴도 표시 회귀(2026-09-11). get_pillars_12beol() + format_12beol_display()
    실제 산출값을 고정하고, build_saju_tongbyeon()이 twelve_beol을 받아도
    크래시 없이 본문을 만드는지(형식 유지) 함께 확인한다."""
    case = CASES[name]
    y, m, d, _h, _mi = case["birth"]
    gender = case["gender"]
    expect = TWELVE_BEOL_EXPECT[name]

    twelve_beol = get_pillars_12beol(y, m, d, gender, case["longitude"], case["use_yaja_time"])

    actual = {
        "격국": format_12beol_display([v["격국"] for v in twelve_beol], "general"),
        "신강약": format_12beol_display([v["신강약"] for v in twelve_beol], "신강약"),
        "주용신": format_12beol_display([v["주용신"] for v in twelve_beol], "general"),
        "대운수": format_12beol_display([v["대운수"] for v in twelve_beol], "대운시작나이"),
    }

    ok = True
    for key in expect:
        if actual[key] != expect[key]:
            print(f"[FAIL] {name} 12벌표시[{key}] 불일치 — 기대:{expect[key]!r} 실제:{actual[key]!r}")
            ok = False

    # 통합 스모크 — twelve_beol을 실제로 넘겨도 build_saju_tongbyeon이 크래시 없이
    # 비어있지 않은 본문을 만드는지만 확인(문장 전문은 위 값 4개로 이미 고정됨).
    pils = get_pils(name)
    pils = [dict(p) for p in pils]
    pils[0] = {"cg": "", "jj": "", "str": ""}
    try:
        body = build_saju_tongbyeon(pils, daewoon=None, birth_year=y, twelve_beol=twelve_beol)
    except Exception as e:
        print(f"[FAIL] {name} build_saju_tongbyeon 크래시: {type(e).__name__}:{e}")
        ok = False
        body = ""
    if not body:
        print(f"[FAIL] {name} build_saju_tongbyeon이 시간미상+twelve_beol에서 빈 본문 반환")
        ok = False

    if ok:
        print(f"[OK] {name} 12벌표시 정상 — {actual}")
    return ok


# 홍염살 SSOT 통일 회귀(2026-09-12) — get_extra_sinsal(saju_sinsal)과
# calc_all_sinsal_extended(zhengtong)이 같은 HONGYEOM_MAP을 참조해
# 판정이 항상 일치해야 한다(과거 乙에서만 갈렸음).
HONGYEOM_EXPECT = {
    "홍염_乙일간_午보유": True,
    "홍염_乙일간_午미보유": False,
}


def check_hongyeom_ssot(name):
    """saju_sinsal.get_extra_sinsal와 saju_zhengtong.calc_all_sinsal_extended의
    홍염살 판정이 HONGYEOM_MAP 단일 소스로 일치하는지 고정한다."""
    expect_fire = HONGYEOM_EXPECT[name]
    pils = get_pils(name)
    ilgan = pils[1]["cg"]

    fires_sinsal = any(s.get("name", "").startswith("홍염살") for s in get_extra_sinsal(pils))
    fires_zt = any(s.get("이름", "").startswith("홍염살") for s in calc_all_sinsal_extended(pils))

    ok = True
    if fires_sinsal != fires_zt:
        print(f"[FAIL] {name} 홍염살 두 함수 불일치 — get_extra_sinsal={fires_sinsal} / calc_all_sinsal_extended={fires_zt}")
        ok = False
    if fires_sinsal != expect_fire:
        print(f"[FAIL] {name} 홍염살 발동 기대 불일치 — 기대:{expect_fire} 실제:{fires_sinsal} (일간:{ilgan}, HONGYEOM_MAP:{HONGYEOM_MAP.get(ilgan)})")
        ok = False
    if ok:
        print(f"[OK] {name} 홍염살 SSOT 일치 — 발동={fires_sinsal} (일간:{ilgan})")
    return ok


# set 정렬 없는 순회 결정성 회귀(2026-09-12) — manse.py:2628-2630.
# PYTHONHASHSEED가 프로세스마다 바뀌면 set() 그대로 join한 결과의 순서도
# 바뀌던 것을, 오행 표준순서(木火土金水) 정렬로 고정했는지 확인한다.
_OH_ORDER_EXPECT = ["木", "火", "土", "金", "水"]
OH_ORDER_EXPECT = {
    "오행순서_기신2종_20020516": {"기신": ["火", "土"], "용신": []},
}


def check_oh_order_determinism(name):
    """get_yongshin_multilayer()의 기신/용신을 manse.py:2628-2630과 동일하게
    set() 후 오행순서로 정렬해, 순서가 고정값과 일치하는지 확인한다."""
    case = CASES[name]
    y, m, d, bh, bmi = case["birth"]
    gender = case["gender"]
    expect = OH_ORDER_EXPECT[name]

    ys_f = get_yongshin_multilayer(get_pils(name), y, gender, m, d, bh, bmi, 2026)
    gisin_f = sorted(set(ys_f.get("기신", [])), key=_OH_ORDER_EXPECT.index)
    yong_f = sorted(set(ys_f.get("용신", [])), key=_OH_ORDER_EXPECT.index)

    ok = True
    if gisin_f != expect["기신"]:
        print(f"[FAIL] {name} 기신 오행순서 불일치 — 기대:{expect['기신']} 실제:{gisin_f}")
        ok = False
    if yong_f != expect["용신"]:
        print(f"[FAIL] {name} 용신 오행순서 불일치 — 기대:{expect['용신']} 실제:{yong_f}")
        ok = False
    if ok:
        print(f"[OK] {name} 기신/용신 오행순서 정렬 정상 — 기신={gisin_f} 용신={yong_f}")
    return ok


# set 정렬 없는 순회 결정성 회귀(2026-09-12) — manse.py:15328-15341
# (menu_current_situation 자형 위험카드). _HYUNG_SELF가 set 리터럴이던 것을
# 12지지 표준순서 tuple로 바꿔 카드 등장 순서를 고정했는지, manse.py를
# import하지 않는 이 파일의 원칙에 맞춰 동일 알고리즘을 그대로 재현해 확인한다
# (manse.py 실제 렌더 경로의 교차프로세스 결정성 실증은 이번 라운드 보고에 별도 기록).
_HYUNG_SELF_EXPECT = ("辰", "午", "酉", "亥")
HYUNG_SELF_ORDER_EXPECT = {
    "지지순서_자형2종_19951109": ["辰", "亥"],
}


def check_hyung_self_order(name):
    """manse.py:15328-15341의 자형(自刑) 판정 알고리즘을 그대로 재현해,
    12지지 표준순서로 카드가 나열되는지 확인한다."""
    pils = get_pils(name)
    all_jj = [p.get("jj", "") for p in pils]
    found = [jj for jj in _HYUNG_SELF_EXPECT if all_jj.count(jj) >= 2]
    expect = HYUNG_SELF_ORDER_EXPECT[name]
    if found != expect:
        print(f"[FAIL] {name} 자형 순서 불일치 — 기대:{expect} 실제:{found}")
        return False
    print(f"[OK] {name} 자형 순서 정상 — {found}")
    return True


def main():
    print("=== tests/pils_fixtures.py ===")
    all_pillars_ok = True
    for name in CASES:
        ok = assert_pillars(name)
        all_pillars_ok = all_pillars_ok and ok
        check_baseline(name)
        print()

    print("=== 양인 sentinel 충돌 회귀(시간미상) ===")
    all_yangin_ok = True
    for name in YANGIN_UNKNOWN_TIME_EXPECT:
        ok = check_yangin_unknown_time(name)
        all_yangin_ok = all_yangin_ok and ok
    print()
    all_pillars_ok = all_pillars_ok and all_yangin_ok

    print("=== 시주 빈 괄호 회귀(render_jonghap_pyongron·render_four_pillars_card) ===")
    all_siju_disp_ok = True
    for name, expect_unknown in SIJU_DISPLAY_EXPECT.items():
        ok = check_siju_unknown_display(name, expect_unknown)
        all_siju_disp_ok = all_siju_disp_ok and ok
    print()
    all_pillars_ok = all_pillars_ok and all_siju_disp_ok

    print("=== 12벌 수렴도 표시 회귀(주용신·격국·신강약·대운수) ===")
    all_12beol_ok = True
    for name in TWELVE_BEOL_EXPECT:
        ok = check_12beol_convergence(name)
        all_12beol_ok = all_12beol_ok and ok
    print()
    all_pillars_ok = all_pillars_ok and all_12beol_ok

    print("=== 홍염살 SSOT 통일 회귀(get_extra_sinsal vs calc_all_sinsal_extended) ===")
    all_hongyeom_ok = True
    for name in HONGYEOM_EXPECT:
        ok = check_hongyeom_ssot(name)
        all_hongyeom_ok = all_hongyeom_ok and ok
    print()
    all_pillars_ok = all_pillars_ok and all_hongyeom_ok

    print("=== set 정렬 없는 순회 결정성 회귀(오행순서·지지순서) ===")
    all_order_ok = True
    for name in OH_ORDER_EXPECT:
        ok = check_oh_order_determinism(name)
        all_order_ok = all_order_ok and ok
    for name in HYUNG_SELF_ORDER_EXPECT:
        ok = check_hyung_self_order(name)
        all_order_ok = all_order_ok and ok
    print()
    all_pillars_ok = all_pillars_ok and all_order_ok

    if all_pillars_ok:
        print("[OK] 결과 요약: 전체 픽스처 8글자 일치")
        sys.exit(0)
    else:
        print("[FAIL] 결과 요약: 8글자 불일치 픽스처 있음")
        sys.exit(1)


if __name__ == "__main__":
    main()
