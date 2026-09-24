# -*- coding: utf-8 -*-
"""manse.py의 resolve_birth_hour 헬퍼 단위 테스트.

E1 라운드: 출생 시(hour) "or 12" 폴백이 0시(자시 전반) 출생자를 조용히
정오로 덮어쓰던 문제를 고치기 위해 도입한 헬퍼. manse.py 전체를 임포트하면
Streamlit 앱 실행 부작용이 커서, 소스에서 함수 정의만 추출해 독립 실행한다.

R6-6b 라운드: 제출 시점 스냅샷("_submitted_hour") 최우선 반환 분기 추가 —
체크박스·시(時) 드롭다운을 제출 없이 만져도(라이브 값) 이미 확정된 명식의
대운 계산 기준 시각이 안 바뀌게 하는 게 목적. 스냅샷 유무에 따른 케이스와,
"재제출"·"즐겨찾기 로드" 시나리오(스냅샷을 지웠다 다시 채우는 순서)를 추가.
"""
import ast
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MANSE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manse.py")


class _FakeSessionState(dict):
    """st.session_state 대역 — resolve_birth_hour가 in_unknown_time·_submitted_hour만 조회한다."""
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

_NO_SNAPSHOT = object()  # "_submitted_hour" 키 자체가 세션에 없는 상태(구형/미제출)를 뜻하는 sentinel

# (후보 튜플, in_unknown_time, 스냅샷값(_NO_SNAPSHOT이면 키 없음), 기대값, 설명)
CASES = [
    # ── 기존 E1 케이스(스냅샷 없음 — 이 라운드 이전과 동일 동작이어야 함) ──
    ((0,), False, _NO_SNAPSHOT, 0, "정상 0시"),
    ((None, 0), False, _NO_SNAPSHOT, 0, "첫 후보 None, 둘째 0"),
    (("", 5), False, _NO_SNAPSHOT, 5, "첫 후보 빈문자열, 둘째 5"),
    ((None, None), False, _NO_SNAPSHOT, 12, "전부 없음 -> 기본값 12"),
    ((23,), False, _NO_SNAPSHOT, 23, "최대값 23"),
    ((30,), False, _NO_SNAPSHOT, 23, "범위초과 -> clamp 23"),
    ((-5,), False, _NO_SNAPSHOT, 0, "음수 -> clamp 0"),
    (("7",), False, _NO_SNAPSHOT, 7, "문자열 숫자"),
    (("abc",), False, _NO_SNAPSHOT, 12, "변환불가 문자열 -> 기본값"),
    ((0,), True, _NO_SNAPSHOT, 12, "시간모름=True + 후보 0 -> 12"),
    ((23,), True, _NO_SNAPSHOT, 12, "시간모름=True + 후보 23 -> 12"),
    ((None,), True, _NO_SNAPSHOT, 12, "시간모름=True + 후보 None -> 12"),

    # ── R6-6b: 스냅샷 우선 반환 ──
    ((0,), False, 7, 7, "스냅샷=7 있으면 후보(0)와 무관하게 7 반환"),
    ((23,), True, 3, 3, "스냅샷=3 있으면 in_unknown_time=True(후보 23)여도 3 — 라이브 플래그보다 스냅샷 우선"),
    ((None,), False, 0, 0, "스냅샷=0(0시)도 그대로 반환 — falsy라고 무시하지 않음(0은 유효값)"),
    ((15,), True, 15, 15, "스냅샷과 라이브 판정이 우연히 같은 값이어도 스냅샷 경로로 반환"),
]


def _fmt_snapshot(snap):
    return "(없음)" if snap is _NO_SNAPSHOT else snap


def run_flat_cases():
    fail = 0
    for args, unknown, snap, expect, desc in CASES:
        state = _FakeSessionState(in_unknown_time=unknown)
        if snap is not _NO_SNAPSHOT:
            state["_submitted_hour"] = snap
        _FakeSt.session_state = state
        got = resolve_birth_hour(*args)
        ok = got == expect
        if not ok:
            fail += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {desc}: resolve_birth_hour{args} "
              f"(in_unknown_time={unknown}, 스냅샷={_fmt_snapshot(snap)}) = {got} (기대 {expect})")
    return fail, len(CASES)


def run_scenarios():
    """단발 (입력→출력) 케이스로는 못 담는 '순서가 있는' 시나리오 —
    manse.py 실제 호출부(제출 처리·load_from_favorite)가 구현해야 하는
    pop→계산→쓰기 순서를 이 헬퍼 레벨에서 그대로 재현해 검증한다."""
    fail = 0
    total = 0

    # 시나리오 1: 재제출 — 이전 스냅샷(0시)이 남은 채로 사용자가 시(時)를
    # 7시로 바꿔 다시 "계산하기"를 누르면, 호출부가 반드시 pop 먼저 해야
    # 새 값(7)이 반영된다. pop을 안 하면 스냅샷이 이겨서 옛 값(0)이 남는다
    # — manse.py:28687 부근의 실제 순서(pop → resolve → 스냅샷 쓰기)가 왜
    # 필요한지 이 대조로 보여준다.
    total += 1
    state = _FakeSessionState(in_unknown_time=False, _submitted_hour=0)
    _FakeSt.session_state = state
    got_without_pop = resolve_birth_hour(7)  # pop 안 하면 스냅샷(0)이 이김
    ok1 = got_without_pop == 0
    if not ok1:
        fail += 1
    print(f"[{'PASS' if ok1 else 'FAIL'}] 재제출 시나리오 A(pop 누락): "
          f"이전 스냅샷 0 남은 채 새 후보 7 넘겨도 resolve={got_without_pop} (기대 0 — 이래서 pop이 필수)")

    total += 1
    state.pop("_submitted_hour", None)  # 호출부가 해야 하는 pop
    got_after_pop = resolve_birth_hour(7)
    ok2 = got_after_pop == 7
    if not ok2:
        fail += 1
    print(f"[{'PASS' if ok2 else 'FAIL'}] 재제출 시나리오 B(pop 후 재계산): "
          f"pop 후 resolve(7)={got_after_pop} (기대 7 — 새 제출값 반영)")

    # 시나리오 2: 즐겨찾기 로드 — 저장 당시 명식의 확정 시각(예: 3시)이
    # _submitted_hour로 복원되면, 로드 시점의 라이브 in_unknown_time·드롭다운
    # 값이 무엇이든 그 저장 당시 시각이 그대로 쓰여야 한다.
    total += 1
    state2 = _FakeSessionState(in_unknown_time=True)  # 로드 시점에 체크박스가 우연히 켜져 있어도
    state2["_submitted_hour"] = 3                      # 불러온 스냅샷(저장 당시 3시 확정)이 이겨야 함
    _FakeSt.session_state = state2
    got_loaded = resolve_birth_hour(0)
    ok3 = got_loaded == 3
    if not ok3:
        fail += 1
    print(f"[{'PASS' if ok3 else 'FAIL'}] 즐겨찾기 로드 시나리오: 저장 당시 확정 시각(3)이 "
          f"로드 시점 라이브 상태(in_unknown_time=True)와 무관하게 유지 -> resolve={got_loaded} (기대 3)")

    # 시나리오 3: 구형 즐겨찾기 폴백 — _submitted_hour가 저장 안 된 옛
    # 스냅샷을 불러오면(즉 이 세션에 그 키가 없으면), load_from_favorite이
    # 복원한 in_unknown_time·birth_hour로 즉석 재계산한 값이 그대로 쓰여야
    # 한다 — 이 재계산 자체도 resolve_birth_hour 호출이므로, 스냅샷이 없는
    # 상태에서 기존 로직(라이브 판정)으로 정확히 폴백하는지 확인.
    total += 1
    state3 = _FakeSessionState(in_unknown_time=True)  # 구형 즐겨찾기가 in_unknown_time=True로 저장됐던 경우
    _FakeSt.session_state = state3  # _submitted_hour 키 자체가 없음(구형)
    got_legacy = resolve_birth_hour(5)  # birth_hour 후보가 뭐든 in_unknown_time이 이김(기존 로직)
    ok4 = got_legacy == 12
    if not ok4:
        fail += 1
    print(f"[{'PASS' if ok4 else 'FAIL'}] 구형 즐겨찾기 폴백 시나리오: 스냅샷 없음 + "
          f"복원된 in_unknown_time=True -> resolve={got_legacy} (기대 12 — 기존 로직 그대로 폴백)")

    # 시나리오 4(R6-6 보완): 구형 시간모름 즐겨찾기 로드 후 frozen birth_hour/
    # birth_minute 정렬 — load_from_favorite 호환 블록(manse.py 10383~10391)의
    # 순서를 그대로 재현한다. R6-6a 이전에 저장된 구형 즐겨찾기는
    # in_unknown_time=True인데도 frozen birth_hour/birth_minute에 원시
    # 드롭다운값(예: 3시 27분)이 그대로 남아있을 수 있는데, 호환 블록이
    # _submitted_hour/_minute 재계산과 함께 frozen 값도 12/0으로 덮어써야
    # R6-6a가 세운 "frozen == 실제 계산값" 불변식이 구형 로드 후에도 유지된다.
    total += 1
    state4 = _FakeSessionState(
        in_unknown_time=True,
        in_birth_hour=3, birth_hour=3,          # 구형: 시간모름인데도 frozen이 원시값
        in_birth_minute=27, birth_minute=27,    # 구형: 마찬가지로 원시값
    )
    _FakeSt.session_state = state4
    state4.pop("_submitted_hour", None)
    state4.pop("_submitted_minute", None)
    state4["_submitted_hour"] = resolve_birth_hour(state4.get("in_birth_hour"), state4.get("birth_hour"))
    state4["_submitted_minute"] = 0 if state4.get("in_unknown_time") else state4.get("in_birth_minute", state4.get("birth_minute", 0))
    state4["birth_hour"] = state4["_submitted_hour"]
    state4["birth_minute"] = state4["_submitted_minute"]
    ok5 = state4["birth_hour"] == 12 and state4["birth_minute"] == 0
    if not ok5:
        fail += 1
    print(f"[{'PASS' if ok5 else 'FAIL'}] 구형 시간모름 즐겨찾기 로드 후 frozen 정렬: "
          f"birth_hour={state4['birth_hour']}(기대 12), birth_minute={state4['birth_minute']}(기대 0)")

    return fail, total


def run():
    fail1, total1 = run_flat_cases()
    print()
    fail2, total2 = run_scenarios()
    print()
    fail = fail1 + fail2
    total = total1 + total2
    if fail:
        print(f"[FAIL] {fail}/{total}건 실패")
        return False
    print(f"[PASS] {total}/{total}건 전부 통과")
    return True


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
