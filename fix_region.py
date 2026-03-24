# fix_region.py
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# ── 수정 1: SajuPrecisionEngine 호출에 longitude 추가 ──
old = '''                pils = SajuPrecisionEngine.get_pillars(
                    b_year,
                    b_month,
                    b_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    _ss["in_gender"],
                    use_yaja_time=_ss.get("in_use_yaja", True),
                )'''

new = '''                _region_lon = TimeCorrection.REGION_LONGITUDE.get(
                    _ss.get("in_birth_region", "서울"), 126.98
                )
                pils = SajuPrecisionEngine.get_pillars(
                    b_year,
                    b_month,
                    b_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    _ss["in_gender"],
                    use_yaja_time=_ss.get("in_use_yaja", True),
                    longitude=_region_lon,
                )'''

src = src.replace(old, new)

# ── 수정 2: 출생지 선택 UI — 프리미엄 보정 체크박스 바로 아래에 삽입 ──
old2 = '''    if "in_premium_correction" not in _ss:
        _ss["in_premium_correction"] = True'''

new2 = '''    if "in_premium_correction" not in _ss:
        _ss["in_premium_correction"] = True
    if "in_birth_region" not in _ss:
        _ss["in_birth_region"] = "서울"'''

src = src.replace(old2, new2)

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 수정 완료")

# ── 문법 검사 ──
import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("문법 OK: manse.py")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
