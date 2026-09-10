# -*- coding: utf-8 -*-
"""
tools/gen_solar_terms_ephem.py — 24절기(소한~동지) 시각 생성기 (ephem 기반)

★전 구간 KST(UTC+9) 고정 출력. 사용자 출생시각 입력을 앱이 언제나 KST
시계값으로 취급하는 기존 설계(saju_engine.py의 TimeCorrection — 1954~1961
GMT+8:30 구간도 의도적으로 GMT+9로 통일 처리, "pass")와 정합성을 유지하기
위함이며, 이 스크립트에는 시간대 분기가 전혀 없다.

ephem.Date에 넣는 시각은 UT로 취급되고, ephem이 내부적으로 자체
ΔT(TT-UT) 보정을 이미 적용한다(XEphem 유래 C 엔진) — 이 스크립트는
별도로 ΔT를 가산하지 않는다(이중 적용 방지).

정확도: 2000~2027년 KASI 실측 672건과 전수 대조해 평균 16.7초·최대
50.0초로 검증됨(1분 게이트 통과). astropy(별도 천체력 엔진)와도 상호
1분 이내로 일치 확인됨. 검증 근거는 이 파일이 속한 커밋 메시지·세션
기록 참고.

의존성(런타임 앱과 무관, 이 생성기 재실행 시에만 필요):
    pip install ephem

사용법 — 2041년 이후를 늘릴 때:
    python tools/gen_solar_terms_ephem.py \
        --start 2041 --end 2050 \
        --merge-with kasi_24terms.json --out kasi_24terms.json \
        --preserve-start 2000 --preserve-end 2027

--preserve-start/--preserve-end 구간의 연도는 기존 JSON 값을 그대로
보존하고(byte 단위로 건드리지 않음) 절대 생성값으로 덮지 않는다.
"""
import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta

try:
    import ephem
except ImportError:
    ephem = None


TERM_NAMES_IN_YEAR_ORDER = [
    "소한", "대한", "입춘", "우수", "경칩", "춘분", "청명", "곡우", "입하", "소만",
    "망종", "하지", "소서", "대서", "입추", "처서", "백로", "추분", "한로", "상강",
    "입동", "소설", "대설", "동지",
]

TERM_ORDER_BY_LONGITUDE = {
    "동지": 270, "소한": 285, "대한": 300, "입춘": 315, "우수": 330, "경칩": 345,
    "춘분": 0, "청명": 15, "곡우": 30, "입하": 45, "소만": 60, "망종": 75,
    "하지": 90, "소서": 105, "대서": 120, "입추": 135, "처서": 150, "백로": 165,
    "추분": 180, "한로": 195, "상강": 210, "입동": 225, "소설": 240, "대설": 255,
}

# 뉴턴법/이분법 초기 추정일(월,일) — 참값이 아니어도 됨, 근처에서 수렴만 하면 됨
_APPROX_MD = {
    "소한": (1, 6), "대한": (1, 20), "입춘": (2, 4), "우수": (2, 19), "경칩": (3, 6), "춘분": (3, 21),
    "청명": (4, 5), "곡우": (4, 20), "입하": (5, 6), "소만": (5, 21), "망종": (6, 6), "하지": (6, 21),
    "소서": (7, 7), "대서": (7, 23), "입추": (8, 8), "처서": (8, 23), "백로": (9, 8), "추분": (9, 23),
    "한로": (10, 8), "상강": (10, 23), "입동": (11, 7), "소설": (11, 22), "대설": (12, 7), "동지": (12, 22),
}


def apparent_longitude_deg(dt_ut):
    """dt_ut: python datetime(UT). 반환: 그 순간의 겉보기 지구중심 황경(도, epoch=of date)."""
    d = ephem.Date(dt_ut)
    s = ephem.Sun()
    s.compute(d)
    eq = ephem.Equatorial(s.ra, s.dec, epoch=d)
    ec = ephem.Ecliptic(eq)
    return math.degrees(ec.lon) % 360


def solve_term_time_kst(target_deg, initial_guess_ut):
    """이분법. target_deg 부근에서 단조증가 구간을 잡아 좁혀간다. 반환: KST datetime."""
    lo = initial_guess_ut - timedelta(days=3)
    hi = initial_guess_ut + timedelta(days=3)

    def f(dt):
        lam = apparent_longitude_deg(dt)
        diff = ((lam - target_deg + 180) % 360) - 180
        return diff

    flo, fhi = f(lo), f(hi)
    if flo > 0 or fhi < 0:
        lo = initial_guess_ut - timedelta(days=10)
        hi = initial_guess_ut + timedelta(days=10)

    for _ in range(60):
        mid = lo + (hi - lo) / 2
        fm = f(mid)
        if abs(fm) < 1e-8:
            lo = hi = mid
            break
        if fm < 0:
            lo = mid
        else:
            hi = mid
        if (hi - lo) < timedelta(microseconds=1):
            break

    result_ut = lo + (hi - lo) / 2
    return result_ut + timedelta(hours=9)  # KST 고정


def gen_year(year):
    """해당 연도 24절기(KST datetime) dict 반환. {절기명: datetime}"""
    if ephem is None:
        raise ImportError("ephem이 설치돼 있지 않습니다. 'pip install ephem' 후 재실행하세요.")
    out = {}
    for name, (m, d) in _APPROX_MD.items():
        target_deg = TERM_ORDER_BY_LONGITUDE[name]
        guess = datetime(year, m, d, 12, 0, 0)
        out[name] = solve_term_time_kst(target_deg, guess)
    return out


def gen_year_as_json_entries(year):
    """gen_year 결과를 kasi_24terms.json 절기 항목 스키마(dict of dict)로 변환.
    src 표식을 포함한다. 초는 버림(분 단위)."""
    terms = gen_year(year)
    result = {}
    for name in TERM_NAMES_IN_YEAR_ORDER:
        dt = terms[name]
        result[name] = {
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "src": "computed-ephem",
        }
    return result


def _parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", type=int, required=True, help="생성 시작 연도(포함)")
    p.add_argument("--end", type=int, required=True, help="생성 종료 연도(포함)")
    p.add_argument("--merge-with", type=str, default=None, help="병합할 기존 JSON 경로(없으면 새로 생성)")
    p.add_argument("--out", type=str, required=True, help="출력 JSON 경로")
    p.add_argument("--preserve-start", type=int, default=2000, help="보존 구간 시작(이 구간은 절대 덮어쓰지 않음)")
    p.add_argument("--preserve-end", type=int, default=2027, help="보존 구간 끝(이 구간은 절대 덮어쓰지 않음)")
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv or sys.argv[1:])

    if args.merge_with and os.path.exists(args.merge_with):
        with open(args.merge_with, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    generated = 0
    skipped_preserved = 0
    for year in range(args.start, args.end + 1):
        if args.preserve_start <= year <= args.preserve_end:
            # ★보존 구간 — 기존 값이 있으면 절대 건드리지 않는다(생성 자체를 스킵)
            if str(year) in data and data[str(year)]:
                skipped_preserved += 1
                continue
        data[str(year)] = gen_year_as_json_entries(year)
        generated += 1
        print(f"  {year} 생성 완료", file=sys.stderr)

    # ★기존 kasi_24terms.json과 바이트 단위로 맞추기 위해 CRLF·trailing
    # newline 없음을 그대로 재현한다(원본 파일 자체가 CRLF, 말미 개행 없음).
    text = json.dumps(data, indent=2, ensure_ascii=False)
    with open(args.out, "wb") as f:
        f.write(text.replace("\n", "\r\n").encode("utf-8"))

    print(f"완료: {generated}개 연도 생성, {skipped_preserved}개 연도 보존(스킵). 출력: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
