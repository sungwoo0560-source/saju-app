import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
from datetime import datetime

try:
    from saju_engine import SajuCoreEngine
    engine = SajuCoreEngine(1990, 3, 15, 10, '남')
    pils = engine.get_pillar()

    from saju_interpreter import get_crossing_interpretation, get_ilgan_strength, get_yongshin
    cur_year = datetime.now().year
    cross = get_crossing_interpretation(pils, cur_year)

    print('=== cross 키 목록 ===')
    print(list(cross.keys()))
    print('dw_ss:', cross.get('dw_ss', '없음'))
    print('sw_ss:', cross.get('sw_ss', '없음'))
    print('sw_gil:', cross.get('sw_gil', '없음'))
    print('대운_천간십성:', cross.get('대운_천간십성', '없음'))
    print('세운_천간십성:', cross.get('세운_천간십성', '없음'))

    ilgan = pils[1]['cg']
    sn_info = get_ilgan_strength(ilgan, pils)
    print('신강신약:', sn_info.get('신강신약', '없음'))
    ys_info = get_yongshin(pils)
    print('종합_용신:', ys_info.get('종합_용신', '없음'))
    print('기신:', ys_info.get('기신', '없음'))
except Exception as e:
    import traceback
    traceback.print_exc()
