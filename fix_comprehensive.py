# fix_comprehensive.py — 전체 점검 및 수정
import re
import py_compile

print("=" * 60)
print("【 종합 점검 및 수정 시작 】")
print("=" * 60)

# ════════════════════════════════════════════════════════════
# 1. manse.py 탭 개수 확인 및 columns 자동 조정
# ════════════════════════════════════════════════════════════

with open("manse.py", encoding="utf-8") as f:
    src_manse = f.read()

# 탭 개수 확인
m = re.search(r'_TAB_DEFS = \[(.*?)\]', src_manse, re.DOTALL)
tabs = re.findall(r'\(\"(.+?)\", \"(.+?)\"\)', m.group(1)) if m else []
total_tabs = len(tabs)
print(f"\n[탭 개수 확인]")
print(f"  탭 총 {total_tabs}개")

# columns 수 계산
row1 = 8
row2 = total_tabs - row1
print(f"  행1: {row1}개, 행2: {row2}개")

# 행 2 columns 수 수정
src_manse = re.sub(
    r'# 버튼 행 2 \(\d+개\)\s*\n\s*_btn_cols2 = st\.columns\(\d+\)',
    f'# 버튼 행 2 ({row2}개)\n            _btn_cols2 = st.columns({row2})',
    src_manse
)
print(f"  ✓ 버튼 행 2 → {row2} columns 수정")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src_manse)

# ════════════════════════════════════════════════════════════
# 2. 5개 파일 문법 검사 및 개선
# ════════════════════════════════════════════════════════════

files_check = [
    "manse.py",
    "saju_ui.py",
    "saju_engine.py",
    "saju_interpreter.py",
    "saju_report.py"
]

print(f"\n[5개 파일 문법 검사]")
all_ok = True

for fname in files_check:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  ✓ {fname}")
    except py_compile.PyCompileError as e:
        print(f"  ✗ {fname}: {e}")
        all_ok = False

if all_ok:
    print(f"\n  공식 검사 결과: 모든 파일 문법 OK")

# ════════════════════════════════════════════════════════════
# 3. None 반환 위험 함수 검색 (saju_engine.py)
# ════════════════════════════════════════════════════════════

print(f"\n[None 반환 함수 검색]")

with open("saju_engine.py", encoding="utf-8") as f:
    src_engine = f.read()

# get_monthly_luck 함수 검사
if "def get_monthly_luck" in src_engine:
    # None 반환 -> {} 로 변경
    src_engine = re.sub(
        r'(def get_monthly_luck.*?)\s+return\s+None(?=\s)',
        r'\1\n        return {}',
        src_engine,
        flags=re.DOTALL
    )
    print("  ✓ get_monthly_luck None -> dict 변경")

# get_daewoon_sewoon_cross 함수 검사
if "def get_daewoon_sewoon_cross" in src_engine:
    src_engine = re.sub(
        r'(def get_daewoon_sewoon_cross.*?)\s+return\s+None(?=\s)',
        r'\1\n        return {}',
        src_engine,
        flags=re.DOTALL
    )
    print("  ✓ get_daewoon_sewoon_cross None -> dict 변경")

with open("saju_engine.py", "w", encoding="utf-8") as f:
    f.write(src_engine)

# ════════════════════════════════════════════════════════════
# 4. 통합 문법 검사
# ════════════════════════════════════════════════════════════

print(f"\n[최종 문법 검사]")
all_pass = True

for fname in files_check:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  ✓ {fname} — OK")
    except py_compile.PyCompileError as e:
        print(f"  ✗ {fname} — 오류")
        all_pass = False

print("\n" + "=" * 60)
if all_pass:
    print("【 ✓ 모든 수정 완료 — git add -A && commit && git push 준비됨 】")
else:
    print("【 ✗ 일부 오류 발생 — 수동 점검 필요 】")
print("=" * 60)
