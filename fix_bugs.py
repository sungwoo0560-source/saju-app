# fix_bugs.py
import re

# ── manse.py 수정 ──────────────────────────────────────
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# 버그1: except Exception: + str(e) → except Exception as e:
# 대상 라인들: infer_current_worry(3곳), menu1_report, menu5_money, menu6_relations, menu7_ai
targets = [
    "[infer_current_worry]",
    "[menu1_report]",
    "[menu5_money]",
    "[menu6_relations]",
    "[menu7_ai]",
]
for tag in targets:
    src = src.replace(
        f'except Exception:\n            _saju_log.warning("{tag}',
        f'except Exception as e:\n            _saju_log.warning("{tag}'
    )
    src = src.replace(
        f'except Exception:\n        _saju_log.warning("{tag}',
        f'except Exception as e:\n        _saju_log.warning("{tag}'
    )

# 버그5: _mte3 받고 str(e) 사용
src = src.replace(
    'except Exception as _mte3:\n            _saju_log.warning("[menu4_future3] 오류: %s", str(e)[:60])',
    'except Exception as _mte3:\n            _saju_log.warning("[menu4_future3] 오류: %s", str(_mte3)[:60])'
)

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 수정 완료")

# ── saju_interpreter.py 수정 ──────────────────────────
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()

# 버그2: get_12sinsal 잘못된 인자
src = src.replace(
    'from saju_sinsal import get_12sinsal\n            _sinsal = get_12sinsal(b.get("ilgan", "甲"), pils)',
    'from saju_sinsal import get_12sinsal\n            _sinsal = get_12sinsal(pils)'
)

# 버그3: partner_ss 일지 지지 → 장간 변환 후 십성 조회
src = src.replace(
    '        partner_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(iljj, "")',
    '        _iljj_main_gan = JIJANGGAN.get(iljj, [""])[-1] if JIJANGGAN.get(iljj) else iljj\n        partner_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(_iljj_main_gan, "")'
)

# 버그4: calc_12unsung → list[str] 반환, .get() 사용 불가
src = src.replace(
    '''        unsung_list = calc_12unsung(ilgan, pils) if pils else []
        iljj_unsung = ""
        for u in unsung_list:
            if u.get("기둥") in ["일주", "일지"]:
                iljj_unsung = u.get("운성", "")
                break''',
    '''        unsung_list = calc_12unsung(ilgan, pils) if pils else []
        # calc_12unsung → list[str]: [시주운성, 일주운성, 월주운성, 년주운성]
        iljj_unsung = unsung_list[1] if len(unsung_list) > 1 else ""'''
)

with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 수정 완료")

# ── 문법 검사 ──────────────────────────────────────────
import py_compile
for fname in ["manse.py", "saju_interpreter.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"문법 OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"문법 오류 {fname}: {e}")
