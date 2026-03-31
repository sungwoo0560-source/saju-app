import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
from saju_engine import SajuCoreEngine
from saju_interpreter import get_12sinsal, get_extra_sinsal, get_yearly_luck
from datetime import datetime

pils = SajuCoreEngine.get_pillars(1990, 3, 15, 10)
cur_year = datetime.now().year

print('=== get_12sinsal ===')
try:
    ss = get_12sinsal(pils)
    print(type(ss))
    print(str(ss)[:500])
except Exception as e:
    print('오류:', e)

print()
print('=== get_extra_sinsal ===')
try:
    es = get_extra_sinsal(pils)
    print(type(es))
    print(str(es)[:500])
except Exception as e:
    print('오류:', e)

print()
print('=== get_yearly_luck ===')
try:
    yl = get_yearly_luck(pils, cur_year)
    print(type(yl))
    print(str(yl)[:500])
except Exception as e:
    print('오류:', e)

print()
print('=== cross 전체 내용 ===')
try:
    from saju_interpreter import get_crossing_interpretation
    cross = get_crossing_interpretation(pils, cur_year)
    for k, v in cross.items():
        print(f'{k}: {str(v)[:100]}')
except Exception as e:
    print('오류:', e)
