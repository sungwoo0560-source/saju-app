import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open('manse.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines[11880:11915], start=11881):
    print(f'{i}:{l}', end='')
