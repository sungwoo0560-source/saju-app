import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
from saju_engine import SajuCoreEngine
from saju_interpreter import get_yongshin

pils = SajuCoreEngine.get_pillars(1990, 3, 15, 10)
ys = get_yongshin(pils)
print('get_yongshin 전체 키:', list(ys.keys()))
print('종합_용신:', ys.get('종합_용신'))
print('기신:', ys.get('기신'))
print('기신 타입:', type(ys.get('기신')))

with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# _GIL_COMMENT 키 확인
for i, l in enumerate(lines, 1):
    if '_GIL_COMMENT' in l and '{' in l:
        print(f'GIL 시작라인 {i}:', l.strip())
        for j in range(i, i+10):
            print(f'  {j+1}:', lines[j].strip())
        break

# _YONG_RX 키 확인
for i, l in enumerate(lines, 1):
    if '_YONG_RX' in l and '=' in l and '{' in l:
        print(f'YONG_RX 시작라인 {i}:', l.strip())
        for j in range(i, i+10):
            print(f'  {j+1}:', lines[j].strip())
        break
