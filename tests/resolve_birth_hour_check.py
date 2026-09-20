# -*- coding: utf-8 -*-
"""manse.py의 resolve_birth_hour 헬퍼 단위 테스트.

E1 라운드: 출생 시(hour) "or 12" 폴백이 0시(자시 전반) 출생자를 조용히
정오로 덮어쓰던 문제를 고치기 위해 도입한 헬퍼. manse.py 전체를 임포트하면
Streamlit 앱 실행 부작용이 커서, 소스에서 함수 정의만 추출해 독립 실행한다.
"""
import ast
import os
import sys

MANSE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manse.py")


class _FakeSessionState(dict):
    """st.session_state 대역 — resolve_birth_hour가 in_unknown_time만 조회한다."""
    pass


class _FakeSt:
    session_state = _FakeSessionState()


def _load_resolve_birth_hour():
    src = open(MANSE_PATH, encoding="utf-8-sig").read()
    tree = ast.parse(src)
    func_src = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "resolve_birth_hour":
            func_src = ast.get_source_segment(src, node)
            break
    assert func_src, "resolve_birth_hour 함수를 manse.py에서 찾지 못함"
    ns = {"st": _FakeSt()}
    exec(func_src, ns)
    return ns["resolve_birth_hour"]


resolve_birth_hour = _load_resolve_birth_hour()

# (후보 튜플, in_unknown_time, 기대값, 설명)
CASES = [
    ((0,), False, 0, "정상 0시"),
    ((None, 0), False, 0, "첫 후보 None, 둘째 0"),
    (("", 5), False, 5, "첫 후보 빈문자열, 둘째 5"),
    ((None, None), False, 12, "전부 없음 -> 기본값 12"),
    ((23,), False, 23, "최대값 23"),
    ((30,), False, 23, "범위초과 -> clamp 23"),
    ((-5,), False, 0, "음수 -> clamp 0"),
    (("7",), False, 7, "문자열 숫자"),
    (("abc",), False, 12, "변환불가 문자열 -> 기본값"),
    # E1 추가: 시간 모름이면 후보와 무관하게 항상 12
    ((0,), True, 12, "시간모름=True + 후보 0 -> 12"),
    ((23,), True, 12, "시간모름=True + 후보 23 -> 12"),
    ((None,), True, 12, "시간모름=True + 후보 None -> 12"),
]


def run():
    fail = 0
    for args, unknown, expect, desc in CASES:
        _FakeSt.session_state = _FakeSessionState(in_unknown_time=unknown)
        got = resolve_birth_hour(*args)
        ok = got == expect
        if not ok:
            fail += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {desc}: resolve_birth_hour{args} (in_unknown_time={unknown}) = {got} (기대 {expect})")

    print()
    if fail:
        print(f"[FAIL] {fail}/{len(CASES)}건 실패")
        return False
    print(f"[PASS] {len(CASES)}/{len(CASES)}건 전부 통과")
    return True


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
