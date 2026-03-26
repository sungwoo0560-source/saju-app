# fix_pillars.py — 년주·시주 천간/지지 개인화 해석 추가
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()

# 삽입 위치: 월주 해석 섹션 바로 뒤
old1 = '''        lines.append("")

        # ── 3. 격국·신강신약·용신 ─'''

new1 = '''        # ── 년주·시주 천간/지지 개인화 해석 ─────────────────────
        _PILLAR_CG = {
            "甲": "갑목(甲木) — 강인한 추진력과 개척정신",
            "乙": "을목(乙木) — 유연한 적응력과 끈질긴 생명력",
            "丙": "병화(丙火) — 밝고 열정적인 태양의 기운",
            "丁": "정화(丁火) — 섬세하고 따뜻한 촛불의 기운",
            "戊": "무토(戊土) — 묵직하고 안정적인 대산의 기운",
            "己": "기토(己土) — 세심하고 현실적인 논밭의 기운",
            "庚": "경금(庚金) — 냉철하고 결단력 있는 강철의 기운",
            "辛": "신금(辛金) — 날카롭고 정밀한 보석의 기운",
            "壬": "임수(壬水) — 지혜롭고 포용적인 대해의 기운",
            "癸": "계수(癸水) — 섬세하고 직관적인 이슬의 기운",
        }
        _PILLAR_JJ = {
            "子": "자(子) — 지혜·활동·사교의 기운. 밤의 에너지로 은밀한 능력이 발달합니다.",
            "丑": "축(丑) — 인내·축적·고독의 기운. 묵묵히 쌓아가는 힘이 강합니다.",
            "寅": "인(寅) — 개척·도전·호랑이의 기운. 새벽을 여는 추진력이 있습니다.",
            "卯": "묘(卯) — 온화·예술·성장의 기운. 부드럽지만 강한 생명력이 있습니다.",
            "辰": "진(辰) — 변화·다재다능·용의 기운. 귀인 인연이 강합니다.",
            "巳": "사(巳) — 지혜·정보·뱀의 기운. 깊은 통찰력과 집중력이 있습니다.",
            "午": "오(午) — 열정·명예·말의 기운. 화려하고 활동적인 기운이 있습니다.",
            "未": "미(未) — 온화·예술·양의 기운. 예술적 감수성과 인정이 깊습니다.",
            "申": "신(申) — 변화·재치·원숭이의 기운. 임기응변과 두뇌 회전이 빠릅니다.",
            "酉": "유(酉) — 심미·완벽·닭의 기운. 날카로운 감식안과 완벽주의가 있습니다.",
            "戌": "술(戌) — 충성·고독·개의 기운. 한번 맺은 인연에 끝까지 충실합니다.",
            "亥": "해(亥) — 지혜·자유·돼지의 기운. 자유롭고 깊은 사색을 즐깁니다.",
        }
        _PILLAR_POS = {
            "년주": f"{name}님의 **년주(年柱)**는 조상·고향·어린 시절의 환경을 나타냅니다.",
            "월주": f"{name}님의 **월주(月柱)**는 부모·형제·사회적 활동기(20~40대)를 나타냅니다.",
            "일주": f"{name}님의 **일주(日柱)**는 나 자신과 배우자, 중년의 삶을 나타냅니다.",
            "시주": f"{name}님의 **시주(時柱)**는 자녀·말년·노후의 환경을 나타냅니다.",
        }

        lines.append("\\n---")
        lines.append("### 🏛️ 사주 8글자 — 기둥별 천간·지지 풀이")

        _pil_map = [
            ("년주", pils[3]["cg"] if len(pils)>3 else "", pils[3]["jj"] if len(pils)>3 else ""),
            ("월주", pils[2]["cg"] if len(pils)>2 else "", pils[2]["jj"] if len(pils)>2 else ""),
            ("일주", pils[1]["cg"] if len(pils)>1 else "", pils[1]["jj"] if len(pils)>1 else ""),
            ("시주", pils[0]["cg"] if len(pils)>0 else "", pils[0]["jj"] if len(pils)>0 else ""),
        ]
        for _pos, _cg, _jj in _pil_map:
            _pos_desc = _PILLAR_POS.get(_pos, "")
            _cg_desc  = _PILLAR_CG.get(_cg, "")
            _jj_desc  = _PILLAR_JJ.get(_jj, "")
            if _cg_desc and _jj_desc:
                lines.append(f"\\n**{_pos}({_cg}{_jj})** — {_pos_desc}")
                lines.append(f"- 천간: {_cg_desc}")
                lines.append(f"- 지지: {_jj_desc}")

        lines.append("")

        # ── 3. 격국·신강신약·용신 ─'''

src = src.replace(old1, new1)

with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 수정 완료")

import py_compile
try:
    py_compile.compile("saju_interpreter.py", doraise=True)
    print("문법 OK")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
