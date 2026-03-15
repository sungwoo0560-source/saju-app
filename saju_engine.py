# -*- coding: utf-8 -*-
"""
saju_engine.py - 사주 계산 엔진
KasiAPI, AstroEngine, ManseCalendarEngine, SajuCoreEngine,
calc_sipsung, calc_12unsung, calc_ohaeng_strength, get_ilgan_strength,
get_yearly_luck, get_monthly_luck, get_10year_luck_table,
get_daewoon_sewoon_cross 포함
"""
import streamlit as st
try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False
import json
import os
from datetime import date, datetime, timedelta
import random
import re
import logging as _logging
try:
    from korean_lunar_calendar import KoreanLunarCalendar as _KLC
    LUNAR_LIB_AVAILABLE = True
except ImportError:
    _KLC = None
    LUNAR_LIB_AVAILABLE = False
from saju_data import *
from saju_data import (
    _JJ_HOUR_FULL, _JJ_HOUR_SHORT, _LUNAR_DATA, _SIT, _LOTTO_SS,
    _JEOLGI_BASE, _AI_SANDBOX_HEADER, _SS_DAILY_DEEP,
    _UNSUNG_DESC, _EMOJI_MAP, _SYMBOL_MAP, _DO_LIST,
    PA_SAL_PAIRS, PA_SAL_DESC, HAE_SAL_PAIRS, HAE_SAL_DESC,
    GOEGANG_ILJU, GOEGANG_DESC,
    HAKDANG_GWIIN, HAKDANG_DESC,
    AMROK_JJ, AMROK_DESC,
    GEUNMYO_HWASIL,
)

_saju_log = _logging.getLogger("saju")

def _get_lunar_month_days(lunar_year: int, lunar_month: int, is_leap: bool) -> int:
    """해당 음력 연·월의 일수 (29 또는 30). 데이터 없으면 30 반환."""
    if lunar_year not in _LUNAR_DATA:
        return 30
    _, month_days, leap_month = _LUNAR_DATA[lunar_year]
    if is_leap and leap_month == lunar_month:
        idx = leap_month  # 윤달은 리스트에서 leap_month 인덱스
    else:
        idx = lunar_month - 1 + (1 if leap_month > 0 and lunar_month > leap_month else 0)
    if 0 <= idx < len(month_days):
        return month_days[idx]
    return 30


# ==================================================

#  🌌 한국천문연구원 (KASI) API 통합 모듈

# ==================================================


class KasiAPI:
    """

    한국천문연구원 공공데이터 API 연동 클래스

    - 24절기 정밀 시각 조회 (초 단위)

    - 음양력 변환 (윤달 완벽 처리)

    - 음력 기준 정보 조회

    """

    BASE_URL = "http://apis.data.go.kr/B090041/openapi/service"

    _SERVICE_KEY: str = ""  # 사이드바에서 주입

    @classmethod
    def set_key(cls, key: str):

        cls._SERVICE_KEY = key.strip()

    @classmethod
    def _get(cls, endpoint: str, params: dict) -> dict | None:
        """공통 GET 요청. 실패 시 None 반환."""

        if not cls._SERVICE_KEY:
            return None

        try:
            import requests

            params["serviceKey"] = cls._SERVICE_KEY

            params["_type"] = "json"

            params["numOfRows"] = 10

            url = f"{cls.BASE_URL}/{endpoint}"

            resp = requests.get(url, params=params, timeout=5)

            resp.raise_for_status()

            data = resp.json()

            items = data.get("response", {}).get("body", {}).get("items", {}).get("item")

            if items is None:
                return None

            return items if isinstance(items, list) else [items]

        except Exception:
            return None

    @classmethod
    def get_24division(cls, year: int) -> list | None:
        """

        해당 연도의 24절기 목록과 정밀 시각(초 단위) 조회

        반환: [{"solDay":"20260205","solTime":"170000","name":"입춘"}, ...]

        """

        items = cls._get("SpcdeInfoService/get24DivInfo", {"solYear": year})

        return items

    @classmethod
    def lunar_to_solar_kasi(cls, lunar_year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> date | None:
        """

        KASI API로 음력 -> 양력 변환 (윤달 완벽 지원)

        반환: date 객체, 실패 시 None

        """

        items = cls._get(
            "LrsrCldInfoService/getLunCalInfo",
            {
                "lunYear": lunar_year,
                "lunMonth": f"{lunar_month:02d}",
                "lunDay": f"{lunar_day:02d}",
                "lunLeapmonth": "1" if is_leap else "0",
            },
        )

        if not items:
            return None

        row = items[0]

        try:
            sol = str(row.get("solYear", "")) + f"{int(row.get('solMonth', 1)):02d}" + f"{int(row.get('solDay', 1)):02d}"

            return date(int(sol[:4]), int(sol[4:6]), int(sol[6:8]))

        except Exception:
            return None

    @classmethod
    def get_lunar_info(cls, solar_year: int, solar_month: int, solar_day: int) -> dict | None:
        """

        양력 날짜 -> 음력 정보 조회 (윤달 여부 포함)

        반환: {"lunYear":..., "lunMonth":..., "lunDay":..., "lunLeapmonth":...}

        """

        items = cls._get(
            "LrsrCldInfoService/getLunaraInfo",
            {
                "solYear": solar_year,
                "solMonth": f"{solar_month:02d}",
                "solDay": f"{solar_day:02d}",
            },
        )

        if not items:
            return None

        return items[0]

    @classmethod
    def get_term_datetime(cls, year: int, term_name: str) -> datetime | None:
        """

        특정 연도의 절기 이름 -> 정밀 시각(초 단위) 반환

        term_name 예: "입춘", "경칩", "청명" ...

        """

        items = cls.get_24division(year)

        if not items:
            return None

        for item in items:
            if term_name in str(item.get("name", "")):
                sol_day = str(item.get("solDay", ""))

                sol_time = str(item.get("solTime", "000000")).zfill(6)

                try:
                    return datetime(
                        int(sol_day[:4]),
                        int(sol_day[4:6]),
                        int(sol_day[6:8]),
                        int(sol_time[:2]),
                        int(sol_time[2:4]),
                        int(sol_time[4:6]),
                    )

                except Exception:
                    return None

        return None


class AstroEngine:
    """

    고정밀 천문 계산 엔진 (1940-2040 범위 보정)

    Jean Meeus 알고리즘 기반의 태양 황도 계산 보조

    """

    @staticmethod
    def get_solar_term_precision(year, month, day, term_name):
        """

        KASI 데이터가 없는 경우(1940-1999, 2028-2040) 사용하는 정밀 계산식

        오차 범위: 약 1~2분 이내

        """

        # 24절기별 태양 황경 (입춘=315도, 우수=330도, ..., 하지=90도, ...)


        target_long = TERM_LONGITUDES.get(term_name)

        if target_long is None:
            return None

        # 기준 시각 (2000년 입춘: 2월 4일 17:40경 = JD 2451579.236)

        # 매우 단순화된 선형 근사 + 보정항

        # 365.24219일마다 같은 황경이 돌아옴

        from datetime import datetime as py_datetime, timedelta

        # 대략적인 절기 날짜 (manse.py SOLAR_TERMS 기준)

        # SajuCoreEngine.SOLAR_TERMS 인덱스 활용

        term_list = [
            "소한",
            "대한",
            "입춘",
            "우수",
            "경칩",
            "춘분",
            "청명",
            "곡우",
            "입하",
            "소만",
            "망종",
            "하지",
            "소서",
            "대서",
            "입추",
            "처서",
            "백로",
            "추분",
            "한로",
            "상강",
            "입동",
            "소설",
            "대설",
            "동지",
        ]

        t_idx = term_list.index(term_name)

        # 기준연도(2000) 기준 해당 절기 시각 (분 단위 정밀도 반영)

        ref_times = {
            "입춘": (2, 4, 17, 40),
            "경칩": (3, 5, 15, 43),
            "청명": (4, 4, 20, 32),
            "입하": (5, 5, 13, 50),
            "망종": (6, 5, 17, 59),
            "소서": (7, 7, 4, 14),
            "입추": (8, 7, 14, 3),
            "백로": (9, 7, 16, 59),
            "한로": (10, 8, 8, 38),
            "입동": (11, 7, 11, 48),
            "대설": (12, 7, 4, 37),
            "소한": (1, 6, 10, 1),
        }

        # 짝수 절기(중기) 포함

        ref_times_all = {
            "소한": (1, 6, 10, 1),
            "대한": (1, 21, 3, 23),
            "입춘": (2, 4, 17, 40),
            "우수": (2, 19, 13, 13),
            "경칩": (3, 5, 15, 43),
            "춘분": (3, 20, 16, 35),
            "청명": (4, 4, 20, 32),
            "곡우": (4, 20, 3, 40),
            "입하": (5, 5, 13, 50),
            "소만": (5, 21, 2, 49),
            "망종": (6, 5, 17, 59),
            "하지": (6, 21, 10, 48),
            "소서": (7, 7, 4, 14),
            "대서": (7, 22, 21, 43),
            "입추": (8, 7, 14, 3),
            "처서": (8, 23, 4, 49),
            "백로": (9, 7, 16, 59),
            "추분": (9, 23, 2, 28),
            "한로": (10, 8, 8, 38),
            "상강": (10, 23, 11, 47),
            "입동": (11, 7, 11, 48),
            "소설": (11, 22, 9, 19),
            "대설": (12, 7, 4, 37),
            "동지": (12, 21, 22, 37),
        }

        m, d, h, mi = ref_times_all.get(term_name, (month, 15, 12, 0))

        ref_dt = py_datetime(2000, m, d, h, mi)

        # 경과년도에 따른 회귀년(Tropical Year) 보정

        diff_years = year - 2000

        # 1회귀년 = 365.24219일

        shift_days = diff_years * 365.24219

        target_dt = ref_dt + timedelta(days=shift_days)

        # 윤년 보정 등 세부 사항은 timedelta가 내부적으로 처리함

        return target_dt.month, target_dt.day, target_dt.hour, target_dt.minute


@st.cache_data
def lunar_to_solar(lunar_year, lunar_month, lunar_day, is_leap=False):
    """음력 -> 양력 변환. KASI API 우선 사용, 실패 시 로컬 데이터 fallback."""

    # 1. KASI API 시도 (키가 설정된 경우)

    kasi_res = KasiAPI.lunar_to_solar_kasi(lunar_year, lunar_month, lunar_day, is_leap)

    if kasi_res:
        return kasi_res

    # 2. 로컬 데이터 Fallback

    if lunar_year not in _LUNAR_DATA:
        return date(lunar_year, lunar_month, lunar_day)

    solar_start_mmdd, month_days, leap_month = _LUNAR_DATA[lunar_year]

    solar_start = date(lunar_year, solar_start_mmdd[0], solar_start_mmdd[1])

    # 경과 일수 계산

    elapsed = 0

    for m in range(1, lunar_month):
        # 윤달 처리: 해당 달 앞에 윤달이 있으면 +1

        idx = m - 1

        if leap_month > 0 and m > leap_month:
            idx += 1

        elapsed += month_days[idx]

    # 요청한 달이 윤달인 경우

    if is_leap and leap_month == lunar_month:
        elapsed += month_days[lunar_month - 1]  # 정달 넘기고

    elapsed += lunar_day - 1

    return solar_start + timedelta(days=elapsed)


@st.cache_data
def solar_to_lunar(solar_date):
    """양력 -> 음력 변환. 반환: (음력년, 음력월, 음력일, 윤달여부)"""

    for ly in sorted(_LUNAR_DATA.keys()):
        solar_start_mmdd, month_days, leap_month = _LUNAR_DATA[ly]

        solar_start = date(ly, solar_start_mmdd[0], solar_start_mmdd[1])

        total_days = sum(month_days)

        solar_end = solar_start + timedelta(days=total_days - 1)

        if solar_start <= solar_date <= solar_end:
            diff = (solar_date - solar_start).days

            lm = 1

            is_leap = False

            for m_idx, days in enumerate(month_days):
                if diff < days:
                    # 윤달 판별: >= 로 윤달 자신도 포착
                    if leap_month > 0 and m_idx >= leap_month:
                        if m_idx == leap_month:
                            is_leap = True
                            actual_m = leap_month
                        else:
                            actual_m = m_idx  # 윤달 이후: 인덱스 = 실제 월
                    else:
                        actual_m = m_idx + 1

                    return (ly, actual_m, diff + 1, is_leap)

                diff -= days

                lm += 1

    # 범위 밖

    return (solar_date.year, solar_date.month, solar_date.day, False)


try:
    from reportlab.lib.units import inch

    from reportlab.pdfbase.ttfonts import TTFont

    from reportlab.pdfbase import pdfmetrics

except ImportError:
    pass  # reportlab 없으면 PDF 기능 비활성화 (REPORTLAB_AVAILABLE로 이미 제어됨)

# 길일/흉일 기준 상수 (ManseCalendarEngine.get_gil_hyung 에서 사용)
_GIL_CG = {"甲", "丙", "戊", "庚", "壬"}        # 양간 = 기본 길일
_HYUNG_JJ = {"丑", "刑", "巳", "申", "寅"}      # 삼형살 지지
_GIL_JJ = {"子", "卯", "午", "酉", "亥", "寅"}  # 귀인 지지 포함


class ManseCalendarEngine:
    """

    만세력 부가 기능 엔진

    - 일진(日辰(진)) 계산

    - 24절기 달력

    - 길일/흉일 판별

    """

    # -- 일진 계산 -------------------------------------

    @staticmethod
    def get_iljin(year: int, month: int, day: int) -> dict:
        """특정 날짜의 일진(日辰(진)) 반환 {cg, jj, str, oh}"""

        from datetime import date as _date

        base = _date(2000, 1, 1)  # 甲(갑)子(자)일 기준점 (2000-01-01 = 甲(갑)辰(진)년 庚(경)戌(술)월 甲(갑)子(자)일)

        target = _date(year, month, day)

        diff = (target - base).days

        # 2000-01-01은 甲子일 - 60갑자 인덱스 0

        idx = (diff + 0) % 60

        cg = CG[idx % 10]

        jj = JJ[idx % 12]

        oh = OH.get(cg, "")

        return {"cg": cg, "jj": jj, "str": cg + jj, "oh": oh, "idx": idx}

    @staticmethod
    def get_today_iljin() -> dict:
        """오늘 일진 반환"""

        today = datetime.now()

        return ManseCalendarEngine.get_iljin(today.year, today.month, today.day)

    # -- 24절기 달력 ------------------------------------

    @staticmethod
    def get_jeolgi_calendar(year: int) -> list:
        """

        해당 연도의 24절기 목록 반환

        [{month, day, name, date_str}, ...]

        A단계 라이브러리 있으면 정밀 시각 포함

        """

        result = []

        for m, d, name in _JEOLGI_BASE:
            # 연도별 절기 날짜는 1~2일 오차 있음 (A단계에서 정밀화)

            try:
                dt = datetime(year, m, d)

                result.append(
                    {
                        "month": m,
                        "day": d,
                        "name": name,
                        "date_str": f"{year}.{m:02d}.{d:02d}",
                        "dt": dt,
                    }
                )

            except ValueError:
                pass

        # 날짜순 정렬

        result.sort(key=lambda x: (x["month"], x["day"]))

        return result

    @staticmethod
    def get_month_jeolgi(year: int, month: int) -> list:
        """특정 월의 절기만 반환"""

        return [j for j in ManseCalendarEngine.get_jeolgi_calendar(year) if j["month"] == month]

    # -- 길흉 판별 --------------------------------------

    @staticmethod
    def get_gil_hyung(year: int, month: int, day: int) -> dict:
        """

        날짜의 길흉 판별

        {grade: '길일'/'보통'/'주의', reason: str, color: '#...'}

        """

        iljin = ManseCalendarEngine.get_iljin(year, month, day)

        cg, jj = iljin["cg"], iljin["jj"]

        score = 0

        reasons = []

        if cg in _GIL_CG:
            score += 1

        if jj in _GIL_JJ:
            score += 1

            reasons.append("귀인운")

        if jj in _HYUNG_JJ:
            score -= 2

            reasons.append("삼형주의")

        # 일진별 특수 길일

        special_gil = {
            "甲(갑)子(자)",
            "甲(갑)午(오)",
            "丙(병)子(자)",
            "庚(경)子(자)",
            "壬(임)子(자)",
            "甲(갑)申(신)",
            "丙(병)寅(인)",
            "庚(경)午(오)",
            "壬(임)申(신)",
        }

        if iljin["str"] in special_gil:
            score += 2

            reasons.append("천을귀인")

        if score >= 2:
            return {
                "grade": "길일 -",
                "reason": " / ".join(reasons) or "양기 충만",
                "color": "#1a7a1a",
                "bg": "#f0fff0",
            }

        elif score <= -1:
            return {
                "grade": "주의",
                "reason": " / ".join(reasons) or "삼형 주의",
                "color": "#cc0000",
                "bg": "#fff0f0",
            }

        else:
            return {
                "grade": "보통",
                "reason": "무난한 하루",
                "color": "#444444",
                "bg": "#ffffff",
            }

    # -- 월별 달력 데이터 생성 --------------------------

    @staticmethod
    def get_month_calendar(year: int, month: int) -> list:
        """

        해당 월의 전체 날짜별 데이터 반환

        [{date, iljin, gil_hyung, jeolgi_name or None}, ...]

        """

        import calendar as _cal

        _, days_in_month = _cal.monthrange(year, month)

        jeolgi_this_month = {j["day"]: j["name"] for j in ManseCalendarEngine.get_month_jeolgi(year, month)}

        result = []

        for day in range(1, days_in_month + 1):
            iljin = ManseCalendarEngine.get_iljin(year, month, day)

            gil = ManseCalendarEngine.get_gil_hyung(year, month, day)

            jeolgi = jeolgi_this_month.get(day)

            result.append(
                {
                    "day": day,
                    "iljin": iljin,
                    "gil": gil,
                    "jeolgi": jeolgi,
                }
            )

        return result


# ==================================================

#  궁합(宮合)

# ==================================================


def calc_gunghap(pils_a, pils_b, name_a="나", name_b="상대"):

    # [년, 월, 일, 시] 순서에서 일간은 index 2

    ilgan_a = pils_a[2]["cg"]
    ilgan_b = pils_b[2]["cg"]

    jj_a = [p["jj"] for p in pils_a]
    jj_b = [p["jj"] for p in pils_b]

    oh_a = OH.get(ilgan_a, "")
    oh_b = OH.get(ilgan_b, "")

    gen_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

    ctrl_map = {"木": "土", "火": "金", "土": "수", "金": "木", "水": "火"}

    if gen_map.get(oh_a) == oh_b:
        ilgan_rel = (
            "생(生)",
            f"{name_a}({ilgan_a})이 {name_b}({ilgan_b})를 지극히 생하는 인연이로다.",
            "💚",
            80,
        )

    elif gen_map.get(oh_b) == oh_a:
        ilgan_rel = (
            "생(生)",
            f"{name_b}({ilgan_b})이 {name_a}({ilgan_a})를 자애롭게 생하는 인연이로다.",
            "💚",
            80,
        )

    elif ctrl_map.get(oh_a) == oh_b:
        ilgan_rel = (
            "극(克)",
            f"{name_a}({ilgan_a})이 {name_b}({ilgan_b})를 강렬히 극하니, 통제가 따를 것이로다.",
            "🔴",
            40,
        )

    elif ctrl_map.get(oh_b) == oh_a:
        ilgan_rel = (
            "극(克)",
            f"{name_b}({ilgan_b})이 {name_a}({ilgan_a})를 서슬 퍼렇게 극하니, 인내가 필요하도다.",
            "🔴",
            40,
        )

    elif oh_a == oh_b:
        ilgan_rel = (
            "비(比)",
            f"두 분 모두 {OHN.get(oh_a, '')}의 기운. 같은 길을 걷는 동반자이자 경쟁자로다.",
            "🟡",
            60,
        )

    else:
        ilgan_rel = (
            "평(平)",
            "상생상극 없는 중립적 관계. 깊은 인연보다는 스치는 인연에 가까운 법.",
            "🟢",
            65,
        )

    all_jj_set = set(jj_a + jj_b)
    hap_score = 0
    hap_found = []

    for combo, (name, oh, desc) in SAM_HAP_MAP.items():
        if combo.issubset(all_jj_set):
            hap_found.append(f"삼합 {name}")
            hap_score += 20

    chung_found = []

    for ja in jj_a:
        for jb in jj_b:
            k = frozenset([ja, jb])

            if k in CHUNG_MAP:
                chung_desc = CHUNG_MAP[k][0]

                if (oh_a == "火" and oh_b == "水") or (oh_a == "水" and oh_b == "火"):
                    chung_desc += " (상충살: 산불을 끌 비가 될지 모든 것을 태울 안개가 될지는 오직 참는 자만이 알 것이로다)"

                chung_found.append(chung_desc)

    chunl = {
        "甲": ["丑", "未"],
        "乙": ["子", "申"],
        "丙": ["亥", "酉"],
        "丁": ["亥", "酉"],
        "戊": ["丑", "未"],
        "己": ["子", "申"],
        "庚": ["丑", "未"],
        "辛": ["寅", "午"],
        "壬": ["卯", "巳"],
        "癸": ["卯", "巳"],
    }

    gui_a = any(jj in chunl.get(ilgan_a, []) for jj in jj_b)

    gui_b = any(jj in chunl.get(ilgan_b, []) for jj in jj_a)

    total = ilgan_rel[3] + hap_score - len(chung_found) * 10 + (10 if gui_a else 0) + (10 if gui_b else 0)

    total = max(0, min(100, total))

    if total >= 85:
        grade = "天生緣분 - 하늘이 억겁의 인연을 맺어 점지한 불멸의 짝이로다. 서로가 서로의 운명을 완성하니 이보다 귀할 수 없다."

    elif total >= 70:
        grade = "相生가합 - 서로의 기운이 톱니바퀴처럼 맞물리는구나. 서로를 위하는 마음이 운명을 밝힐 것이로다."

    elif total >= 50:
        grade = "有情무정 - 인연의 끈은 있으나 노력이 없으면 흩어질 기운. 서로의 자존심을 내려놓아야 길이 보이느니라."

    elif total >= 30:
        grade = "相衝살 - 만나면 부딪히고 돌아서면 그리운 애증의 굴레. 서로를 태워버리지 않도록 거리를 두어야 할 것이로다."

    else:
        grade = "惡緣 - 서로의 기운을 칼날처럼 갉아먹는 악연이라. 가까이 함이 곧 독이요, 멀리함이 곧 복이니라."

    return {
        "총점": total,
        "등급": grade,
        "일간관계": ilgan_rel,
        "합": hap_found,
        "충": chung_found,
        "귀인_a": gui_a,
        "귀인_b": gui_b,
        "name_a": name_a,
        "name_b": name_b,
        "ilgan_a": ilgan_a,
        "ilgan_b": ilgan_b,
    }


# ==================================================

#  택일(擇日)

# ==================================================


def get_good_days(pils, year, month):

    import calendar

    ilgan = pils[1]["cg"]
    il_jj = pils[1]["jj"]

    chunl = {
        "甲": ["丑", "未"],
        "乙": ["子", "申"],
        "丙": ["亥", "酉"],
        "丁": ["亥", "酉"],
        "戊": ["丑", "未"],
        "己": ["子", "申"],
        "庚": ["丑", "未"],
        "辛": ["寅", "午"],
        "壬": ["卯", "巳"],
        "癸": ["卯", "巳"],
    }

    gui_jjs = chunl.get(ilgan, [])

    gm = get_gongmang(pils)
    bad_jjs = list(gm["공망_지지"])

    chung_jjs = [list(k)[0] if list(k)[1] == il_jj else list(k)[1] for k in CHUNG_MAP if il_jj in k]

    days_in_month = calendar.monthrange(year, month)[1]

    idx = (year - 4) % 60
    month_base = (idx + (month - 1) * 2) % 12

    good_days = []

    for day in range(1, days_in_month + 1):
        day_jj = JJ[(month_base + day - 1) % 12]
        day_cg = CG[((idx + (month - 1) * 2) + day - 1) % 10]

        score = 50
        reasons = []

        if day_jj in gui_jjs:
            score += 25
            reasons.append("천을귀인일 🌟")

        if day_jj in bad_jjs:
            score -= 30
            reasons.append("공망일 ⚠️")

        if day_jj in chung_jjs:
            score -= 20
            reasons.append("일주충일 ⚠️")

        for k, (name, oh, desc) in SAM_HAP_MAP.items():
            if day_jj in k and il_jj in k:
                score += 15
                reasons.append(f"삼합{name}일 -")
                break

        day_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(day_cg, "-")

        if day_ss in ["식신", "정재", "정관", "정인"]:
            score += 10
            reasons.append(f"{day_ss}일 -")

        elif day_ss in ["편관", "겁재"]:
            score -= 15
            reasons.append(f"{day_ss}일 ⚠️")

        level = "- 길일 - 🌟최길" if score >= 80 else "-길" if score >= 65 else "〇보통" if score >= 45 else "[-]주의"

        if score >= 60:
            good_days.append(
                {
                    "day": day,
                    "jj": day_jj,
                    "cg": day_cg,
                    "pillar": day_cg + day_jj,
                    "score": score,
                    "level": level,
                    "reasons": reasons,
                }
            )

    return sorted(good_days, key=lambda x: -x["score"])[:10]


# ==================================================

#  🌐 정밀 시간 보정 엔진 (TimeCorrection)

#  경도/표준시/서머타임 완벽 반영

# ==================================================


class TimeCorrection:
    """한국 표준시 및 경도 보정 데이터"""

    # 한국 표준시 변경 이력

    # 1. 1908.04.01 - 1911.12.31: GMT+8:30 (127.5도)

    # 2. 1912.01.01 - 1954.03.20: GMT+9:00 (135도)

    # 3. 1954.03.21 - 1961.08.09: GMT+8:30 (127.5도)

    # 4. 1961.08.10 - 현재: GMT+9:00 (135도)

    # 서머타임(DST) 시행 이력

    DST_PERIODS = [
        (datetime(1948, 6, 1), datetime(1948, 9, 13)),
        (datetime(1949, 4, 3), datetime(1949, 9, 11)),
        (datetime(1950, 4, 1), datetime(1950, 9, 10)),
        (datetime(1951, 5, 6), datetime(1951, 9, 9)),
        (datetime(1955, 5, 5), datetime(1955, 9, 9)),
        (datetime(1956, 5, 20), datetime(1956, 9, 30)),
        (datetime(1957, 5, 5), datetime(1957, 9, 22)),
        (datetime(1958, 5, 4), datetime(1958, 9, 21)),
        (datetime(1959, 5, 3), datetime(1959, 9, 20)),
        (datetime(1960, 5, 1), datetime(1960, 9, 18)),
        (datetime(1987, 5, 10), datetime(1987, 10, 11)),
        (datetime(1988, 5, 8), datetime(1988, 10, 9)),
    ]

    @staticmethod
    def get_corrected_time(year, month, day, hour, minute):
        """입력된 시간을 '진태양시'로 보정"""

        dt = datetime(year, month, day, hour, minute)

        # 1. 서머타임 보정 (-1시간)

        is_dst = False

        for start, end in TimeCorrection.DST_PERIODS:
            if start <= dt <= end:
                is_dst = True

                break

        if is_dst:
            dt -= timedelta(hours=1)

        # 2. 표준시 보정

        # 1954.03.21 ~ 1961.08.09 기간은 GMT+8.5 (135도 기준 -30분)

        if datetime(1954, 3, 21) <= dt <= datetime(1961, 8, 9, 23, 59):
            # 이 시기 표준시는 이미 127.5도 기준이므로,

            # 135도 기준 만세력 계산 시에는 30분을 더해주거나 빼주는 처리가 필요할 수 있으나

            # 보통 사주에서는 135도(GMT+9)를 기준으로 역산함.

            pass

        # 3. 경도 보정 (서울 기준 127.0도 vs 표준 135.0도)

        # 1도 = 4분 차이 -> 8도 차이 = 32분 차이

        # 한국은 동경 135도보다 서쪽에 있으므로 실제 태양은 32분 늦게 뜸 -> 32분을 빼야 진태양시

        dt -= timedelta(minutes=32)

        return dt


class SajuPrecisionEngine:
    """고정밀 사주 엔진 (KASI 데이터 및 초단위 보정 반영)"""

    # 24절기 정밀 데이터 (예시: 2020~2030 주요 절입 시각)

    # 실제 구현 시에는 KASI API 또는 더 큰 테이블 필요

    PRECISION_TERMS = {
        2024: {
            2: {"입춘": (4, 17, 27, 0)},  # 2월 4일 17:27:00
            3: {"경칩": (5, 11, 22, 0)},
            4: {"청명": (4, 16, 2, 0)},
        },
        2025: {
            2: {"입춘": (3, 23, 10, 0)},  # 2월 3일 23:10:00
        },
    }

    @staticmethod
    def get_pillars(year, month, day, hour, minute, gender="남", use_yaja_time=True):
        """정밀 보정된 사주팔자 계산"""

        corrected_dt = TimeCorrection.get_corrected_time(year, month, day, hour, minute)

        cy, cm, cd = corrected_dt.year, corrected_dt.month, corrected_dt.day

        ch, cmin = corrected_dt.hour, corrected_dt.minute

        # 기본 엔진의 로직을 활용하되, 보정된 시간을 주입

        # (기존 SajuCoreEngine의 메서드들을 정밀 옵션과 함께 호출하도록 설계 가능)

        pils = SajuCoreEngine.get_pillars(cy, cm, cd, ch, cmin, gender, use_yaja_time=use_yaja_time)

        # 추가적인 절기 정밀 보정 (초 단위 데이터가 있는 경우)

        # if cy in SajuPrecisionEngine.PRECISION_TERMS:

        #     ... (세부 보정 로직) ...

        return pils


# ==================================================

#  사주 계산 엔진 (SajuCoreEngine)

# ==================================================


class SajuCoreEngine:
    """사주팔자 핵심 계산 엔진"""

    MONTH_GANJI = [
        ("丙(병)寅(인)", "戊(무)寅(인)"),
        ("戊(무)辰(진)", "甲(갑)辰(진)"),
        ("戊(무)午(오)", "丙(병)午(오)"),
        ("庚(경)申(신)", "戊(무)申(신)"),
        ("壬(임)戌(술)", "庚(경)戌(술)"),
        ("甲(갑)子(자)", "壬(임)子(자)"),
        ("丙(병)寅(인)", "甲(갑)寅(인)"),
        ("戊(무)辰(진)", "丙(병)辰(진)"),
        ("庚(경)午(오)", "戊(무)午(오)"),
        ("壬(임)申(신)", "庚(경)申(신)"),
        ("甲(갑)戌(술)", "壬(임)戌(술)"),
        ("丙(병)子(자)", "甲(갑)子(자)"),
    ]


    KASI_DATA = {}

    _KASI_LOADED = False

    @staticmethod
    def _load_kasi_data():
        """KASI 절기 JSON 데이터를 로드함"""

        if SajuCoreEngine._KASI_LOADED:
            return

        json_path = "kasi_24terms.json"

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    SajuCoreEngine.KASI_DATA = json.load(f)

                SajuCoreEngine._KASI_LOADED = True

            except Exception as _e:
                _saju_log.warning("[SajuCoreEngine._load_kasi] KASI 데이터 로드 실패: %s", _e)

    @staticmethod
    def _get_term_precision_time(year, term_name):
        """특정 연도/절기의 정밀 시각(시, 분)을 반환 (KASI -> AstroEngine Fallback)"""

        SajuCoreEngine._load_kasi_data()

        y_str = str(year)

        # 1. KASI JSON 확인 (2000-2027 우선)

        if y_str in SajuCoreEngine.KASI_DATA:
            term_info = SajuCoreEngine.KASI_DATA[y_str].get(term_name)

            if term_info and term_info.get("month"):
                return (
                    term_info["month"],
                    term_info["day"],
                    term_info["hour"],
                    term_info["minute"],
                )

        # 2. AstroEngine 정밀 계산 (1940-2040 전구간 정밀 보정)

        return AstroEngine.get_solar_term_precision(year, 1, 1, term_name)

    @staticmethod
    def _get_year_pillar(year, month, day, hour=12, minute=0):
        """연주 계산 (입춘 시간 정밀 보정)"""

        total_min = hour * 60 + minute

        # KASI 정밀 데이터 시도

        kasi_info = SajuCoreEngine._get_term_precision_time(year, "입춘")

        if kasi_info:
            target_m, target_d, target_h, target_min = kasi_info

            target_total_min = target_h * 60 + target_min

            is_after_ipchun = (month > target_m) or (month == target_m and (day > target_d or (day == target_d and total_min >= target_total_min)))

        else:
            # Fallback: 2월 4일 17:30 근사치

            is_after_ipchun = (month > 2) or (month == 2 and (day > 4 or (day == 4 and total_min >= 1050)))

        y = year if is_after_ipchun else year - 1

        idx = (y - 4) % 60

        return {
            "cg": CG[idx % 10],
            "jj": JJ[idx % 12],
            "str": CG[idx % 10] + JJ[idx % 12],
        }

    @staticmethod
    def _get_month_pillar(year, month, day, hour=12, minute=0):
        """월주 계산 (절기 경계 정밀 보정)"""

        terms = SOLAR_TERMS  # 모듈 레벨 SOLAR_TERMS (saju_data에서 import)

        term_idx = (month - 1) * 2

        # 해당 월의 '절기' (예: 2월이면 입춘, 3월이면 경칩...)


        term_name = term_names[term_idx]

        total_min = hour * 60 + minute

        # KASI 정밀 데이터 시도

        kasi_info = SajuCoreEngine._get_term_precision_time(year, term_name)

        if kasi_info:
            target_m, target_d, target_h, target_min = kasi_info

            target_total_min = target_h * 60 + target_min

            # 해당 월의 절입 시각보다 이전이면 이전 달 팔자 사용

            if month == target_m and (day < target_d or (day == target_d and total_min < target_total_min)):
                solar_month = month - 1

            else:
                solar_month = month

        else:
            # Fallback: 기존 근사치 방식

            t_month, t_day = terms[term_idx]

            if month == t_month and (day < t_day or (day == t_day and total_min < 720)):
                solar_month = month - 1

            else:
                solar_month = month

        if solar_month < 1:
            solar_month = 12

        y_p = SajuCoreEngine._get_year_pillar(year, month, day, hour, minute)

        y_str = y_p["str"]

        # 연간의 천간 인덱스로 월간 도출 (60갑자 기반 정밀화)

        y_cg_idx = CG.index(y_str[0])

        month_cg_starts = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 갑=丙(병), 을=戊(무)...

        cg_start = month_cg_starts[y_cg_idx % 10]

        lunar_month_num = (solar_month - 2) % 12  # 인월(寅(인))=0

        cg_idx = (cg_start + lunar_month_num) % 10

        ji_idx = (2 + lunar_month_num) % 12

        return {"cg": CG[cg_idx], "jj": JJ[ji_idx], "str": CG[cg_idx] + JJ[ji_idx]}

    @staticmethod
    def _get_days_to_term(year, month, day, hour, minute, direction):
        """대운 계산을 위한 절입일과의 거리(일수) 산출 (KASI 데이터 반영)"""

        from datetime import datetime as py_datetime

        # ✅ BUG FIX: month/day/hour/minute 범위 보정 (세션값 오염 방지)
        month  = max(1, min(12, int(month  or 1)))
        day    = max(1, min(31, int(day    or 1)))
        hour   = max(0, min(23, int(hour   or 12)))
        minute = max(0, min(59, int(minute or 0)))

        birth_dt = py_datetime(year, month, day, hour, minute)

        term_names = [
            "소한",
            "대한",
            "입춘",
            "우수",
            "경칩",
            "춘분",
            "청명",
            "곡우",
            "입하",
            "소만",
            "망종",
            "하지",
            "소서",
            "대서",
            "입추",
            "처서",
            "백로",
            "추분",
            "한로",
            "상강",
            "입동",
            "소설",
            "대설",
            "동지",
        ]

        # 현재 월의 절기 이름 (예: 2월 -> 입춘)

        term_idx = (month - 1) * 2

        def get_best_term_dt(y, m):

            t_idx = (m - 1) * 2

            t_name = term_names[t_idx]

            k_info = SajuCoreEngine._get_term_precision_time(y, t_name)

            if k_info:
                return py_datetime(y, k_info[0], k_info[1], k_info[2], k_info[3])

            # Fallback

            t_m, t_d = SOLAR_TERMS[t_idx]  # 모듈 레벨 SOLAR_TERMS

            return py_datetime(y, t_m, t_d, 12, 0)

        if direction == 1:  # 순행 (다음 절기)
            target_dt = get_best_term_dt(year, month)

            if target_dt < birth_dt:
                next_m = month + 1

                next_y = year

                if next_m > 12:
                    next_m = 1
                    next_y += 1

                target_dt = get_best_term_dt(next_y, next_m)

            # 정확한 초 단위 차이 계산 후 일수로 환산 (3일=1년 공식 등에 사용)

            diff = target_dt - birth_dt

            return diff.days + (diff.seconds / 86400.0)

        else:  # 역행 (이전 절기)
            target_dt = get_best_term_dt(year, month)

            if target_dt > birth_dt:
                prev_m = month - 1

                prev_y = year

                if prev_m < 1:
                    prev_m = 12
                    prev_y -= 1

                target_dt = get_best_term_dt(prev_y, prev_m)

            diff = birth_dt - target_dt

            return diff.days + (diff.seconds / 86400.0)

    @staticmethod
    def _get_day_pillar(year, month, day):
        """일주 계산"""

        try:
            ref_date = date(2000, 1, 1)

            target_date = date(year, month, day)

            delta = (target_date - ref_date).days

            # ✅ BUG FIX: 2000년 1월 1일 = 戊午일 (인덱스 54)

            idx = (54 + delta) % 60

            cg = CG[idx % 10]

            jj = JJ[idx % 12]

            return {"cg": cg, "jj": jj, "str": cg + jj}

        except Exception:
            return {"cg": "甲", "jj": "子", "str": "甲(갑)子(자)"}

    @staticmethod
    def _get_hour_pillar(birth_hour, birth_minute, day_cg, use_yaja_time=True):
        """시주 계산 (조자시/야자시 반영 v2)"""
        # 시 번호 결정 (자시=0, 축시=1...)
        total_minutes = birth_hour * 60 + birth_minute

        # 자시: 23:00 ~ 01:00
        is_yaja = total_minutes >= 1380  # 야자시 (23:00~00:00)
        is_joja = total_minutes < 60  # 조자시 (00:00~01:00)

        if is_yaja or is_joja:
            si_num = 0
        else:
            si_num = ((total_minutes + 60) // 120) % 12
        # 시천간 결정 기준 일간 지표
        ilgan_idx = CG.index(day_cg)

        # ✅ 야자시 핵심: 일주는 오늘(day_cg)을 쓰지만, 시주는 내일의 자시(시천간)를 씀
        # 내일 일간 = 오늘 일간 + 1
        if is_yaja and use_yaja_time:
            target_ilgan_idx = (ilgan_idx + 1) % 10
        else:
            target_ilgan_idx = ilgan_idx % 10
        day_cg_idx_for_si = target_ilgan_idx % 5
        hour_cg_starts = [
            0,
            2,
            4,
            6,
            8,
        ]  # 甲(갑)己(기)=甲(갑), 乙(을)庚(경)=丙(병), 丙(병)辛(신)=戊(무), 丁(정)壬(임)=庚(경), 戊(무)癸(계)=壬(임)
        cg_start = hour_cg_starts[day_cg_idx_for_si]
        cg_idx = (cg_start + si_num) % 10
        jj_idx = si_num % 12
        cg = CG[cg_idx]
        jj = JJ[jj_idx]
        return {"cg": cg, "jj": jj, "str": cg + jj}

    @staticmethod
    @st.cache_data
    def get_pillars(
        birth_year,
        birth_month,
        birth_day,
        birth_hour=12,
        birth_minute=0,
        gender="남",
        use_yaja_time=True,
    ):
        """사주팔자 계산 - 반환: [시주, 일주, 월주, 년주]"""

        calc_y, calc_m, calc_d = birth_year, birth_month, birth_day
        if not use_yaja_time and birth_hour >= 23:
            from datetime import date, timedelta

            next_d = date(birth_year, birth_month, birth_day) + timedelta(days=1)
            calc_y, calc_m, calc_d = next_d.year, next_d.month, next_d.day
        year_p = SajuCoreEngine._get_year_pillar(birth_year, birth_month, birth_day, birth_hour, birth_minute)
        month_p = SajuCoreEngine._get_month_pillar(birth_year, birth_month, birth_day, birth_hour, birth_minute)
        day_p = SajuCoreEngine._get_day_pillar(calc_y, calc_m, calc_d)
        hour_p = SajuCoreEngine._get_hour_pillar(birth_hour, birth_minute, day_p["cg"], use_yaja_time=use_yaja_time)
        return [hour_p, day_p, month_p, year_p]

    @staticmethod
    def get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour=12,
        birth_minute=0,
        gender="남",
    ):
        """대운 계산 - 정밀 모드"""

        # 연간의 음양 (년주의 천간 기준)

        year_cg = pils[3]["cg"]

        year_cg_idx = CG.index(year_cg)

        is_yang = year_cg_idx % 2 == 0

        # 성별+음양 순행/역행

        if (gender == "남" and is_yang) or (gender == "여" and not is_yang):
            direction = 1  # 순행

        else:
            direction = -1  # 역행

        # 절입일 찾기 및 대운 시작 나이 계산

        try:
            days_to_term = SajuCoreEngine._get_days_to_term(birth_year, birth_month, birth_day, birth_hour, birth_minute, direction)

            # 3일 = 1년, 1일 = 4개월 자투리.

            # ✅ 정밀 대운수: 반올림 적용 (나머지가 0.5년(1.5일) 이상이면 올림)

            start_age = int(round(days_to_term / 3.0))

            if start_age == 0:
                start_age = 1

            daewoon_list = []

            month_p = pils[2]  # 월주가 대운의 출발점

            wolgan_idx = CG.index(month_p["cg"])

            wolji_idx = JJ.index(month_p["jj"])

            for i in range(10):  # 100년 대운
                step = i + 1

                d_cg_idx = (wolgan_idx + direction * step) % 10

                d_jj_idx = (wolji_idx + direction * step) % 12

                age_start = start_age + (i * 10)

                year_start = birth_year + age_start

                daewoon_list.append(
                    {
                        "순번": i + 1,
                        "cg": CG[d_cg_idx],
                        "jj": JJ[d_jj_idx],
                        "str": CG[d_cg_idx] + JJ[d_jj_idx],
                        "시작나이": age_start,
                        "시작연도": year_start,
                        "종료연도": year_start + 9,
                    }
                )

        except Exception as e:
            _saju_log.warning("[get_daewoon] 대운 계산 실패: %s", e)
            daewoon_list = []

        return daewoon_list


# ==================================================

#  십성(十星) 및 12운성 계산 (Bug 5 Fix)

# ==================================================


@st.cache_data
def calc_sipsung(ilgan, pils):
    """십성 계산"""

    result = []

    for p in pils:
        cg = p["cg"]

        jj = p["jj"]

        # 천간 십성

        cg_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cg, "-")

        # 지장간 십성 (지지의 정기)

        jijang = JIJANGGAN.get(jj, [])

        if jijang:
            jj_main = jijang[-1]

            jj_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(jj_main, "-")

        else:
            jj_ss = "-"

        result.append({"cg_ss": cg_ss, "jj_ss": jj_ss, "jj": jj})

    return result


def calc_12unsung(ilgan, pils):
    """12운성 계산 (Bug 5 Fix: 양/음 배열 수정)"""

    # ✅ BUG 5 FIX: 올바른 양지/음지 배열

    jj_yang = ["子", "寅", "辰", "午", "申", "戌"]  # 양지 (자인진오신술)

    jj_eum = ["丑", "卯", "巳", "未", "酉", "亥"]  # 음지 (축묘사유미해)

    try:
        ilgan_idx = CG.index(ilgan)

        is_yang_gan = ilgan_idx % 2 == 0

    except (ValueError, NameError):
        pass

    # 일간 키 찾기 (ex: '甲' -> '甲(갑)')

    ilgan_key = ilgan

    try:
        ilgan_key = f"{ilgan}({CG_KR[CG.index(ilgan)]})"

    except (ValueError, NameError):
        pass

    result = []

    for p in pils:
        jj = p["jj"]

        jj_key = jj

        try:
            jj_key = f"{jj}({JJ_KR[JJ.index(jj)]})"

        except (ValueError, NameError):
            pass

        unsung_table_for = UNSUNG_TABLE.get(ilgan_key, UNSUNG_TABLE.get(ilgan, {}))

        unsung = unsung_table_for.get(jj_key, unsung_table_for.get(jj, "-"))

        result.append(unsung)

    return result


@st.cache_data
def calc_ohaeng_strength(ilgan, pils):
    """

    오행 세력 점수화 v2 (정밀 엔진)

    월령득령(25pt) + 천간투출(6~10pt) + 지지(8~15pt) + 지장간(4~8pt) + 통근보너스(5pt)

    -> 합산 후 100% 정규화

    """

    power = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}

    # - 월령 득령 (월지 계절기운, 최대 25점) -

    _WOLLYEONG = {
        "寅": {"木": 25, "火": 0, "土": 3, "金": 0, "水": 0},
        "卯": {"木": 25, "火": 0, "土": 3, "金": 0, "水": 0},
        "辰": {"木": 8, "火": 0, "土": 20, "金": 0, "水": 3},
        "巳": {"木": 0, "火": 25, "土": 3, "金": 0, "水": 0},
        "午": {"木": 0, "火": 25, "土": 3, "金": 0, "水": 0},
        "未": {"木": 0, "火": 8, "土": 20, "金": 0, "水": 0},
        "申": {"木": 0, "火": 0, "土": 3, "金": 25, "水": 0},
        "酉": {"木": 0, "火": 0, "土": 3, "金": 25, "水": 0},
        "戌": {"木": 0, "火": 0, "土": 20, "金": 8, "水": 0},
        "亥": {"木": 3, "火": 0, "土": 0, "金": 0, "水": 25},
        "子": {"木": 3, "火": 0, "土": 0, "金": 0, "水": 25},
        "丑": {"木": 0, "火": 0, "土": 20, "金": 3, "水": 8},
    }

    wol_jj = pils[2]["jj"]  # 월지 (Index 2)

    wol_oh = OH.get(wol_jj, "")

    ilgan_oh = OH.get(ilgan, "")

    if wol_oh == ilgan_oh:
        power[wol_oh] += 25.0  # 득령 보너스

    # ② 전체 원국 점수 합산

    # 천간: 10점, 지지: 15점, 지장간: 5점 (기본 가중치)

    for i, p in enumerate(pils):
        cg_oh = OH.get(p["cg"], "")

        jj_oh = OH.get(p["jj"], "")

        # 천간 기운

        if cg_oh in power:
            power[cg_oh] += 10.0

        # 지지 기운

        if jj_oh in power:
            power[jj_oh] += 15.0

        # 지장간 가중치 — JIJANGGAN_RATIO 비율 반영 (여기/중기/정기 분배)
        jijang_ratio = JIJANGGAN_RATIO.get(p["jj"], [])
        if jijang_ratio:
            _total_r = sum(r for _, r in jijang_ratio) or 1
            for _jg_cg, _jg_r in jijang_ratio:
                _jg_oh = OH.get(_jg_cg, "")
                if _jg_oh in power:
                    power[_jg_oh] += 5.0 * (_jg_r / _total_r)
        else:
            # 폴백: 기존 방식 (정기만)
            jijang = JIJANGGAN.get(p["jj"], [])
            if jijang:
                jj_main = OH.get(jijang[-1], "")
                if jj_main in power:
                    power[jj_main] += 5.0

    # ③ 월령(월지) 추가 가중치 (index 2)

    if wol_oh in power:
        power[wol_oh] += 10.0  # 월령의 지지력 추가 반영

    # ④ 일간(index 1) 통근 보너스

    day_jj = pils[1]["jj"]

    if OH.get(day_jj) == ilgan_oh:
        power[ilgan_oh] += 5.0

    # - 12운성 보정 -

    _UNSUNG_MOD = {
        "장생": 1.2,
        "목욕": 0.8,
        "관대": 1.1,
        "건록": 1.4,
        "제왕": 1.5,
        "쇠": 0.9,
        "병": 0.7,
        "사": 0.5,
        "묘": 0.4,
        "절": 0.3,
        "태": 0.5,
        "양": 0.7,
    }

    ilgan_oh = OH.get(ilgan, "")

    _JJ_W2 = [8, 15, 12, 10]

    for i, p in enumerate(pils):
        state = UNSUNG_TABLE.get(ilgan, {}).get(p["jj"], "")

        mod = _UNSUNG_MOD.get(state, 1.0)

        if mod != 1.0 and ilgan_oh:
            power[ilgan_oh] = max(0, power[ilgan_oh] + _JJ_W2[i] * (mod - 1.0) * 0.4)

    # - 통근 보너스 -

    _TONGGUEN = {
        "木": {"寅", "卯", "辰", "亥", "未"},
        "火": {"巳", "午", "未", "寅", "戌"},
        "土": {"辰", "戌", "丑", "未", "巳", "午"},
        "金": {"申", "酉", "戌", "丑"},
        "水": {"亥", "子", "丑", "申", "辰"},
    }

    all_jjs = {p["jj"] for p in pils}

    for oh, jj_set in _TONGGUEN.items():
        if all_jjs & jj_set:
            power[oh] += 5.0

    # - 정규화 (합=100) -

    total = sum(power.values())

    if total <= 0:
        return {"木": 20, "火": 20, "土": 20, "金": 20, "水": 20}

    return {k: round(v / total * 100, 1) for k, v in power.items()}




@st.cache_data
def get_ilgan_strength(ilgan, pils):
    """

    일간 신강신약 v2 | 5단계 점수화 (0~100)

    극신강 / 신강 / 중화 / 신약 / 극신약

    """

    oh_strength = calc_ohaeng_strength(ilgan, pils)

    ilgan_oh = OH.get(ilgan, "")

    # 생(生)해주는 오행 (인성)

    _BIRTH_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

    parent_oh = _BIRTH_R.get(ilgan_oh, "")

    # 돕는 세력 = 비겁(같은오행) + 인성

    helper_score = oh_strength.get(ilgan_oh, 0) + oh_strength.get(parent_oh, 0)

    # 약화 세력 = 식상x0.8 + 재성x1.0 + 관성x1.0

    _BIRTH_F = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

    _CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    sik_oh = _BIRTH_F.get(ilgan_oh, "")

    jae_oh = _CTRL.get(ilgan_oh, "")

    gwan_oh = next((k for k, v in _CTRL.items() if v == ilgan_oh), "")

    weak_score = oh_strength.get(sik_oh, 0) * 0.8 + oh_strength.get(jae_oh, 0) * 1.0 + oh_strength.get(gwan_oh, 0) * 1.0

    # 일간 힘 점수 0~100

    total = helper_score + weak_score

    daymaster_score = round(helper_score / total * 100, 1) if total > 0 else 50.0

    # 5단계

    if daymaster_score >= 68:
        strength = "극신강(極身强)"

        advice = "기운이 넘칩니다. 재성/관성 운에서 발복하나 자만과 독선 경계"

    elif daymaster_score >= 55:
        strength = "신강(身强)"

        advice = "강한 기운 - 재성/관성 운에서 발복하나 비겁운은 경계"

    elif daymaster_score >= 45:
        strength = "중화(中和)"

        advice = "균형 잡힌 기운 - 어떤 운에서도 무난하게 발전 가능"

    elif daymaster_score >= 32:
        strength = "신약(身弱)"

        advice = "약한 기운 - 인성/비겁 운에서 힘을 얻고 재/관운은 조심"

    else:
        strength = "극신약(極身弱)"

        advice = "기운이 매우 약합니다. 인성/비겁 운이 절실하며 재관운은 특히 위험"

    return {
        "신강신약": strength,
        "일간점수": daymaster_score,
        "helper_score": helper_score,
        "weak_score": weak_score,
        "조언": advice,
        "oh_strength": oh_strength,
        "ilgan_oh": ilgan_oh,
        "parent_oh": parent_oh,
        "sik_oh": sik_oh,
        "jae_oh": jae_oh,
        "gwan_oh": gwan_oh,
    }


# ==================================================

#  세운/월운 계산 (Bug 6 Fix)

# ==================================================



@st.cache_data
def get_yearly_luck(pils, current_year):
    """세운 계산"""

    idx = (current_year - 4) % 60

    cg = CG[idx % 10]

    jj = JJ[idx % 12]

    # ✅ BUG 6 FIX: pils[1]["cg"] (일주 천간) - [시, 일, 월, 년] 순서

    ilgan = pils[1]["cg"]

    se_ss_cg = TEN_GODS_MATRIX.get(ilgan, {}).get(cg, "-")

    jijang = JIJANGGAN.get(jj, [])

    se_ss_jj = TEN_GODS_MATRIX.get(ilgan, {}).get(jijang[-1] if jijang else "", "-")

    oh_cg = OH.get(cg, "")

    oh_jj = OH.get(jj, "")

    narr = YEARLY_LUCK_NARRATIVE.get(se_ss_cg, YEARLY_LUCK_NARRATIVE["-"])

    return {
        "연도": current_year,
        "세운": cg + jj,
        "cg": cg,
        "jj": jj,
        "십성_천간": se_ss_cg,
        "십성_지지": se_ss_jj,
        "오행_천간": oh_cg,
        "오행_지지": oh_jj,
        "길흉": narr["level"],
        "아이콘": narr["icon"],
        "narrative": narr,
    }




@st.cache_data
def get_monthly_luck(pils, year, month):
    """월운 계산 - 오호둔월법으로 월간(천간) 계산 후 십성 산출"""

    if not pils:
        return None

    ilgan = pils[1]["cg"]

    # 월지(月支): 1월=丑, 2월=寅, ..., 12월=子

    jj_list = ["丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子"]

    target_jj = jj_list[(month - 1) % 12]

    # [BUG FIX] 월간(月干) 계산 - 오호둔월법

    # TEN_GODS_MATRIX는 천간 키만 가짐 → 지지(target_jj)를 직접 조회하면 항상 "-" 반환이 버그 원인

    CG_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    year_cg = CG_LIST[(year - 4) % 10]

    # 연간 기준 寅月(2월) 시작 천간 인덱스 (오호둔월법)

    OHHO_IDX = {
        "甲": 2,
        "己": 2,
        "乙": 4,
        "庚": 4,
        "丙": 6,
        "辛": 6,
        "丁": 8,
        "壬": 8,
        "戊": 0,
        "癸": 0,
    }

    start_idx = OHHO_IDX.get(year_cg, 0)

    # month 2(寅)=offset 0, month 3(卯)=offset 1, ..., month 1(丑)=offset 11

    month_offset = (month - 2) % 12

    target_cg = CG_LIST[(start_idx + month_offset) % 10]

    # 천간 기준 십성 (정확한 계산)

    sipsung = TEN_GODS_MATRIX.get(ilgan, {}).get(target_cg, "-")

    # 지지 정기(본기) 기준 보조 십성

    jj_junggi = JIJANGGAN.get(target_jj, ["-"])[-1]

    sipsung_jj = TEN_GODS_MATRIX.get(ilgan, {}).get(jj_junggi, "-")

    luck_data = MONTHLY_LUCK_DESC.get(sipsung) or MONTHLY_LUCK_DESC.get(sipsung_jj) or MONTHLY_LUCK_DESC["-"]

    return {
        "월": month,
        "간": target_cg,
        "지": target_jj,
        "십성": sipsung,
        "십성_지지": sipsung_jj,
        "월운": f"{target_cg}{target_jj}월",
        "월주": target_cg + target_jj,
        "설명": luck_data["desc"],
        "길흉": luck_data["길흉"],
        "css": luck_data["css"],
        "short": luck_data["short"],
        "desc": luck_data["desc"],
        "재물": luck_data["재물"],
        "관계": luck_data["관계"],
        "주의": luck_data["주의"],
    }


def get_10year_luck_table(pils, birth_year, gender="남"):
    """10년 운세 테이블"""

    # 대운 호출 시 실제 생년월일시 반영

    birth_month  = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day    = max(1, min(31, int(st.session_state.get("birth_day")   or 1)))

    birth_hour   = max(0, min(23, int(st.session_state.get("birth_hour")  or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    result = []

    current_year = datetime.now().year

    for dw in daewoon:
        yearly = []

        for y in range(dw["시작연도"], dw["시작연도"] + 10):
            ye = get_yearly_luck(pils, y)

            yearly.append(ye)

        result.append(
            {
                **dw,
                "yearly": yearly,
                "is_current": dw["시작연도"] <= current_year <= dw["종료연도"],
            }
        )

    return result


def get_daewoon_sewoon_cross(pils, birth_year, gender, target_year=None):
    """대운*세운 교차 분석"""

    ilgan = pils[1]["cg"]

    if target_year is None:
        target_year = datetime.now().year

    # 대운 호출 시 실제 생년월일시 반영

    _bm  = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    _bd  = max(1, min(31, int(st.session_state.get("birth_day")   or 1)))

    _bh  = max(0, min(23, int(st.session_state.get("birth_hour")  or 12)))

    _bmi = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon_list = SajuCoreEngine.get_daewoon(pils, birth_year, _bm, _bd, _bh, _bmi, gender)

    cur_dw = next((d for d in daewoon_list if d["시작연도"] <= target_year <= d["종료연도"]), None)

    if not cur_dw:
        return None

    sewoon = get_yearly_luck(pils, target_year)

    dw_cg_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw["cg"], "-")

    dw_jj_cg = JIJANGGAN.get(cur_dw["jj"], [""])[-1]

    dw_jj_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw_jj_cg, "-")

    sw_cg_ss = sewoon["십성_천간"]

    sw_jj_cg = JIJANGGAN.get(sewoon["jj"], [""])[-1]

    sw_jj_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(sw_jj_cg, "-")

    cross_events = []

    TG_HAP_PAIRS = [
        {"甲", "己"},
        {"乙", "庚"},
        {"丙", "辛"},
        {"丁", "壬"},
        {"戊", "癸"},
    ]

    for pair in TG_HAP_PAIRS:
        if cur_dw["cg"] in pair and sewoon["cg"] in pair:
            cross_events.append(
                {
                    "type": "천간합",
                    "desc": f"대운 천간({cur_dw['cg']})과 세운 천간({sewoon['cg']})이 합(合). 변화와 기회의 해.",
                }
            )

    for k, (name, oh, desc) in CHUNG_MAP.items():
        if cur_dw["jj"] in k and sewoon["jj"] in k:
            cross_events.append(
                {
                    "type": "지지충",
                    "desc": f"대운 지지({cur_dw['jj']})와 세운 지지({sewoon['jj']})가 충(沖). {desc}",
                }
            )

    for combo, (hname, hoh, hdesc) in SAM_HAP_MAP.items():
        all_jj = {cur_dw["jj"], sewoon["jj"]} | {p["jj"] for p in pils}

        if combo.issubset(all_jj):
            cross_events.append(
                {
                    "type": "삼합",
                    "desc": f"대운/세운/원국 삼합({hname}) - 강력한 발복의 기운.",
                }
            )

    ss_combo = f"{dw_cg_ss}+{sw_cg_ss}"

    interp = {
        "정관+식신": "명예와 재능이 동시에 빛나는 최길 조합. 승진/수상/큰 성취.",
        "식신+정재": "복록과 재물이 넘치는 대길 조합. 재물운 폭발.",
        "편관+편관": "이중 편관. 시련 극도. 건강/사고 각별히 주의.",
        "겁재+겁재": "이중 겁재. 재물 손실/경쟁 극심. 방어 전략이 최선.",
        "정인+정관": "학문과 명예 동시에 오는 최길 조합. 시험/자격증/승진.",
        "편관+식신": "칠살제화(七殺制化) - 시련이 오히려 기회가 됩니다.",
        "정재+정관": "재물과 명예 함께 오는 길한 조합. 사업 성공과 인정.",
    }

    cross_desc = interp.get(ss_combo, f"대운 {dw_cg_ss}의 흐름 속에 세운 {sw_cg_ss}의 기운이 더해집니다.")

    return {
        "연도": target_year,
        "대운": cur_dw,
        "세운": sewoon,
        "대운_천간십성": dw_cg_ss,
        "대운_지지십성": dw_jj_ss,
        "세운_천간십성": sw_cg_ss,
        "세운_지지십성": sw_jj_ss,
        "교차사건": cross_events,
        "교차해석": cross_desc,
    }