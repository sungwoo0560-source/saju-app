#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from datetime import datetime

# 테스트용 샘플 사주 (임의)
try:
    from saju_engine import SajuCoreEngine
    # 샘플 사주: 1990년 3월 15일 오전 10시 남성
    pils = SajuCoreEngine.get_pillars(1990, 3, 15, 10)
    cur_year = datetime.now().year
    cur_age = cur_year - 1990 + 1

    print(f'현재연도: {cur_year}')
    print(f'현재나이: {cur_age}')
    print(f'pils 타입: {type(pils)}')
    print(f'pils 길이: {len(pils)}')
    
    # pils 구조 파악
    print(f'\npils 전체 구조:')
    for idx, p in enumerate(pils):
        print(f'  pils[{idx}] = {p}')
    
    print(f'\n일간(cg): {pils[1].get("cg", "?") if isinstance(pils[1], dict) else pils[1]}')

    print()

    from saju_interpreter import get_ilgan_strength, get_yongshin, get_crossing_interpretation
    sn = get_ilgan_strength(pils[1]['cg'], pils)
    print(f'신강신약 결과: {sn}')
    print(f'신강신약: {sn.get("신강신약", "?")}')
    
    ys = get_yongshin(pils)
    print(f'용신 결과 키: {list(ys.keys())}')
    print(f'용신: {ys.get("종합_용신", [])}')
    print(f'기신: {ys.get("기신", [])}')
    print()

    cross = get_crossing_interpretation(pils, cur_year)
    print(f'cross 결과 키: {list(cross.keys())}')
    print(f'dw_ss: {cross.get("dw_ss","없음")}')
    print(f'sw_ss: {cross.get("sw_ss","없음")}')
    print(f'sw_gil: {cross.get("sw_gil","없음")}')
    
except Exception as e:
    print(f'오류: {e}')
    import traceback
    traceback.print_exc()
