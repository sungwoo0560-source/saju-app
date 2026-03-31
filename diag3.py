import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, l in enumerate(lines, 1):
    if 'SajuCoreEngine' in l and ('(' in l):
        print(f'{i}: {l.strip()}')
