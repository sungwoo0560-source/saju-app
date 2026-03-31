# fix_tab_cols.py — 탭 버튼 columns 수 정합성 수정
import re
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# 현재 TAB_DEFS 개수 확인
m = re.search(r'_TAB_DEFS = \[(.*?)\]', src, re.DOTALL)
tabs = re.findall(r'\(\"(.+?)\", \"(.+?)\"\)', m.group(1)) if m else []
total = len(tabs)
row1 = 8
row2 = total - row1
print(f"탭 총 {total}개 — 행1: {row1}개, 행2: {row2}개")

# 행 2 columns 수 수정
import re
src = re.sub(
    r'# 버튼 행 2 \(\d+개\)\s*\n\s*_btn_cols2 = st\.columns\(\d+\)',
    f'# 버튼 행 2 ({row2}개)\n            _btn_cols2 = st.columns({row2})',
    src
)
print(f"버튼 행 2 → {row2} columns 수정")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)

import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("문법 OK")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
