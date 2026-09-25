"""
check.py - 사주 프로젝트 정적 검사 스크립트

사용법:
    python check.py [파일명]        (기본값: manse.py)
    python check.py [파일명] --watch (저장 시마다 재검사)

검사 항목:
    1. 문법 검사 (py_compile, 서브프로세스)
    2. 필수 함수/클래스 정의 존재 여부 (정규식 스캔)
    3. 괄호/따옴표 짝 검사 (tokenize)
    4. import 중복/미사용 검사 (ast 정적 파싱)

주의: 대상 파일을 import하지 않는다 (Streamlit 앱이라 import 시 부작용 발생).
      텍스트 읽기 + tokenize + ast.parse 만 사용하고, py_compile은 서브프로세스로 실행한다.
"""
import ast
import io
import os
import re
import sys
import time
import tokenize
import subprocess

# 실제 grep으로 확인된 위치 기준 (2026-07-02). 파일별로 "그 파일에 실제 정의된" 심볼만 검사한다.
REQUIRED_SYMBOLS = {
    "manse.py": [
        ("def", "menu1_report"),
        ("def", "menu2_lifeline"),
        ("def", "menu3_past"),
        ("def", "menu4_future3"),
        ("def", "menu5_money"),
        ("def", "menu6_relations"),
        ("def", "menu7_ai"),
        ("def", "menu8_bihang"),
        ("def", "tab_jaemul"),
    ],
    "saju_engine.py": [
        ("class", "SajuCoreEngine"),
        ("def", "calc_sipsung"),
        ("def", "get_ilgan_strength"),
        ("def", "get_yearly_luck"),
        ("def", "get_monthly_luck"),
        ("def", "get_daewoon_sewoon_cross"),
    ],
    "saju_interpreter.py": [
        ("def", "get_yongshin_match"),
        ("def", "get_gyeokguk"),
        ("def", "get_yongshin"),
        ("def", "get_yukjin"),
        ("def", "get_special_stars"),
        ("def", "get_yongshin_multilayer"),
        ("def", "build_life_analysis"),
    ],
    "saju_sinsal.py": [
        ("def", "get_12sinsal"),
        ("def", "get_extra_sinsal"),
    ],
    "saju_data.py": [],
}


def check_syntax(filepath):
    """py_compile을 서브프로세스로 실행해 문법 오류를 잡는다."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", filepath],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return True, "문법 검사 통과"
    return False, result.stderr.strip()


def check_required_symbols(filepath, text):
    """파일명에 매핑된 필수 def/class 심볼이 실제로 정의됐는지 확인."""
    basename = os.path.basename(filepath)
    symbols = REQUIRED_SYMBOLS.get(basename)
    if symbols is None:
        return True, [f"(등록되지 않은 파일 — 심볼 검사 생략: {basename})"]
    if not symbols:
        return True, ["(검사 대상 필수 심볼 없음)"]

    missing = []
    found = 0
    for kind, name in symbols:
        pattern = re.compile(rf"^{kind}\s+{re.escape(name)}\b", re.MULTILINE)
        if pattern.search(text):
            found += 1
        else:
            missing.append(f"{kind} {name}")
    ok = not missing
    msg = [f"필수 심볼 {found}/{len(symbols)} 발견"]
    if missing:
        msg.append("누락: " + ", ".join(missing))
    return ok, msg


def check_brackets(filepath):
    """tokenize로 괄호 짝을 검사한다 (문자열/주석은 tokenize가 알아서 구분)."""
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set(pairs.values())
    closes = set(pairs.keys())
    stack = []
    problems = []
    try:
        with open(filepath, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for tok in tokens:
                if tok.type != tokenize.OP:
                    continue
                s = tok.string
                if s in opens:
                    stack.append((s, tok.start[0]))
                elif s in closes:
                    if not stack or stack[-1][0] != pairs[s]:
                        problems.append(f"line {tok.start[0]}: '{s}' 짝이 맞지 않음")
                    else:
                        stack.pop()
    except (tokenize.TokenizeError, IndentationError, SyntaxError) as e:
        return False, [f"tokenize 실패 (문법 오류 가능성): {e}"]
    except Exception as e:
        return False, [f"tokenize 실패: {e}"]

    for s, line in stack:
        problems.append(f"line {line}: '{s}' 가 닫히지 않음")

    ok = not problems
    return ok, problems if problems else ["괄호 짝 이상 없음"]


def check_imports(filepath, text):
    """ast로 최상위 import문만 정적 파싱해 중복/미사용을 가볍게 리포트한다."""
    try:
        tree = ast.parse(text, filename=filepath)
    except SyntaxError as e:
        return False, [f"import 검사 생략 (구문 오류로 파싱 불가): {e}"]

    seen = {}
    dup = []
    imported_names = []  # (name, lineno)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                key = alias.asname or alias.name
                local_name = key.split(".")[0]
                imported_names.append((local_name, node.lineno))
                if key in seen:
                    dup.append(f"line {node.lineno}: '{key}' 중복 import (line {seen[key]}와 동일)")
                else:
                    seen[key] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                key = alias.asname or alias.name
                imported_names.append((key, node.lineno))
                sig = f"{node.module}.{key}"
                if sig in seen:
                    dup.append(f"line {node.lineno}: '{key}' 중복 import (from {node.module})")
                else:
                    seen[sig] = node.lineno

    lines = text.splitlines()
    unused = []
    for name, lineno in imported_names:
        count = 0
        pattern = re.compile(rf"\b{re.escape(name)}\b")
        for i, line in enumerate(lines, start=1):
            if i == lineno:
                continue
            if pattern.search(line):
                count += 1
                break
        if count == 0:
            unused.append(f"line {lineno}: '{name}' 미사용 가능성")

    msgs = []
    if dup:
        msgs.append(f"중복 import {len(dup)}건")
        msgs.extend(dup[:10])
    if unused:
        msgs.append(f"미사용 가능 import {len(unused)}건 (참고용, from-import * 은 검사 제외)")
        msgs.extend(unused[:10])
    if not dup and not unused:
        msgs.append("중복/미사용 import 없음")
    ok = True  # import 검사는 경고성이라 전체 결과에 FAIL을 유발하지 않음
    return ok, msgs


# --- R6 재발 방지: 입력폼 블록 밖 in_* 위젯 키 직접 읽기 WARN ---
# (근거: CLAUDE.md 작업 규칙 — 결과 화면·계산 경로에서 in_* 위젯 키 직접
#  읽기 금지, 명식 입력값은 frozen 키·_submitted_hour·pils[0] 사용)

IN_STAR_PREFIXES = [
    "in_birth", "in_unknown_time", "in_cal_type", "in_solar",
    "in_lunar", "in_is_leap", "in_birth_region", "in_use_yaja",
]
IN_STAR_PATTERN = re.compile(
    r"""\.get\(\s*["'](%s)""" % "|".join(re.escape(p) for p in IN_STAR_PREFIXES)
)

# 정당한 폴백 패턴 — 함수명이 아니라 '같은 줄의 텍스트 형태'로 판정한다.
# 1) frozen 키 get()이 in_* get()보다 그 줄에서 먼저 나오는 폴백 형태
#    예: _ss.get("birth_region", _ss.get("in_birth_region", "서울"))
# 2) resolve_birth_hour( 호출의 인자로 넘기는 in_* 읽기 — 그 헬퍼 내부가
#    _submitted_hour를 항상 최우선으로 보므로 안전하다.
# 그 외(함수명과 무관하게) 이 두 형태에 안 걸리면 전부 WARN 대상이다.
FROZEN_GET_BEFORE_RE = re.compile(r"""\.get\(\s*["'](?!in_)[A-Za-z_]""")


def _find_input_form_block(text):
    """'st.expander(...사주 정보 입력...)' with 블록의 (시작줄, 끝줄)을
    tokenize INDENT/DEDENT로 동적 계산한다(줄번호 하드코딩 금지 — 파일이
    바뀌어도 다시 계산됨). 못 찾으면 None."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except Exception:
        return None

    start_idx = None
    for idx, tok in enumerate(tokens):
        if tok.type == tokenize.NAME and tok.string == "with":
            line = tok.line
            if "st.expander(" in line and "사주 정보 입력" in line:
                start_idx = idx
                break
    if start_idx is None:
        return None

    start_line = tokens[start_idx].start[0]
    depth = 0
    entered = False
    end_line = None
    for tok in tokens[start_idx:]:
        if tok.type == tokenize.INDENT:
            depth += 1
            entered = True
        elif tok.type == tokenize.DEDENT:
            if entered:
                depth -= 1
                if depth == 0:
                    end_line = tok.start[0]
                    break
    if end_line is None:
        return None
    return start_line, end_line - 1


def _build_func_ranges(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    ranges = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            ranges.append((node.name, node.lineno, end))
    return ranges


def _enclosing_func(ranges, lineno):
    best = None
    for name, s, e in ranges:
        if s <= lineno <= e:
            if best is None or (e - s) < (best[2] - best[1]):
                best = (name, s, e)
    return best[0] if best else None


def check_in_star_direct_read(filepath, text):
    """입력폼 블록(st.expander 사주 정보 입력) 밖에서 in_* 위젯 키를 .get()으로
    직접 읽는 지점을 WARN. 함수명이 아니라 같은 줄의 텍스트 패턴으로 판정한다:
    frozen 키 get()이 in_* get()보다 먼저 나오는 폴백 형태, 또는
    resolve_birth_hour( 호출의 인자 내부는 정당한 폴백으로 보고 제외."""
    basename = os.path.basename(filepath)
    if basename != "manse.py":
        return True, ["(manse.py 전용 검사 — 대상 아님)"]

    block = _find_input_form_block(text)
    if block is None:
        return True, ["(입력폼 블록(st.expander 사주 정보 입력)을 찾지 못함 — 검사 생략)"]
    block_start, block_end = block

    func_ranges = _build_func_ranges(text)  # WARN 메시지에 함수명 표시용(필터링에는 미사용)
    lines = text.splitlines()

    warnings = []
    for i, line in enumerate(lines, start=1):
        if block_start <= i <= block_end:
            continue
        m = IN_STAR_PATTERN.search(line)
        if not m:
            continue
        prefix = line[: m.start()]
        if FROZEN_GET_BEFORE_RE.search(prefix):
            continue  # 같은 줄에서 frozen 키 get()이 먼저 나오는 폴백 형태
        if "resolve_birth_hour(" in prefix:
            continue  # resolve_birth_hour( 인자 내부 읽기
        fn = _enclosing_func(func_ranges, i)
        warnings.append(f"line {i} [{fn or '모듈 최상위'}]: {line.strip()[:100]}")

    msg = [f"입력폼 블록: line {block_start}-{block_end}"]
    if warnings:
        msg.append(f"WARN {len(warnings)}건 (결과 화면·계산 경로 in_* 직접 읽기 의심)")
        msg.extend(warnings)
    else:
        msg.append("WARN 없음")
    return True, msg  # 경고성 — 전체 결과 FAIL 유발하지 않음


def run_check(filepath):
    print(f"=== check.py : {filepath} ===")
    overall_ok = True

    if not os.path.isfile(filepath):
        print(f"[FAIL] 파일을 찾을 수 없음: {filepath}")
        return False

    syn_ok, syn_msg = check_syntax(filepath)
    print(f"[{'OK' if syn_ok else 'FAIL'}] 문법(py_compile): {syn_msg if syn_ok else ''}")
    if not syn_ok:
        print(syn_msg)
        overall_ok = False
        # 문법이 깨지면 이후 검사(tokenize/ast)는 신뢰할 수 없으므로 여기서 중단
        print(f"=== 결과: [FAIL] {filepath} ===")
        return False

    with open(filepath, "r", encoding="utf-8-sig") as f:
        text = f.read()

    sym_ok, sym_msgs = check_required_symbols(filepath, text)
    print(f"[{'OK' if sym_ok else 'FAIL'}] 필수 함수/클래스:")
    for m in sym_msgs:
        print(f"    {m}")
    overall_ok &= sym_ok

    br_ok, br_msgs = check_brackets(filepath)
    print(f"[{'OK' if br_ok else 'FAIL'}] 괄호 짝:")
    for m in br_msgs:
        print(f"    {m}")
    overall_ok &= br_ok

    imp_ok, imp_msgs = check_imports(filepath, text)
    print(f"[INFO] import 검사(참고용):")
    for m in imp_msgs:
        print(f"    {m}")

    warn_ok, warn_msgs = check_in_star_direct_read(filepath, text)
    print(f"[INFO] in_* 위젯 키 직접 읽기(R6 재발방지, 참고용):")
    for m in warn_msgs:
        print(f"    {m}")

    print(f"=== 결과: [{'OK' if overall_ok else 'FAIL'}] {filepath} ===")
    return overall_ok


def main():
    args = [a for a in sys.argv[1:] if a != "--watch"]
    watch = "--watch" in sys.argv[1:]
    filepath = args[0] if args else "manse.py"

    if not watch:
        ok = run_check(filepath)
        sys.exit(0 if ok else 1)

    print(f"--watch 모드: {filepath} 저장 감지 중... (Ctrl+C로 종료)")
    last_mtime = None
    try:
        while True:
            if os.path.isfile(filepath):
                mtime = os.path.getmtime(filepath)
                if mtime != last_mtime:
                    last_mtime = mtime
                    os.system("cls" if os.name == "nt" else "clear")
                    run_check(filepath)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n감시 종료")


if __name__ == "__main__":
    main()
