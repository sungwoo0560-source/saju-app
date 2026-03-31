with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    lines = []
    _dw_label = f"{dw_kr} 대운" if dw_kr else "대운 미산출"'''

new = '''    # ── 위험 신호 분석 ─────────────────────────────────────
    _danger_signals = []
    try:
        from saju_interpreter import get_12sinsal, get_yearly_luck
        _sinsal_list = get_12sinsal(pils)
        _yl = get_yearly_luck(pils, cur_year)
        _jj_cur = _yl.get("jj", "")
        _oh_cg  = _yl.get("오행_천간", "")
        _oh_jj  = _yl.get("오행_지지", "")
        _CHUNG_MAP = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                      "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
        _il_jj   = pils[1].get("jj","")
        _year_jj = pils[0].get("jj","") if len(pils)>0 else ""
        if _CHUNG_MAP.get(_il_jj,"") == _jj_cur:
            _danger_signals.append(("💥 이동수·사고수 주의",
                f"올해 일지({_il_jj})와 세운지지({_jj_cur})가 충(沖)입니다. "
                f"교통사고, 수술, 갑작스러운 이사·이직 등 큰 변화가 터질 수 있습니다. "
                f"상반기 중 각별히 조심하십시오."))
        if _CHUNG_MAP.get(_year_jj,"") == _jj_cur:
            _danger_signals.append(("💔 부부·가족 갈등수",
                f"년주({_year_jj})와 세운이 충돌합니다. "
                f"배우자·가족과 심각한 갈등, 별거, 이혼 논의가 생길 수 있습니다. "
                f"감정이 격해지는 시기에 큰 결정을 미루십시오."))
        for _s in _sinsal_list:
            _nm = _s.get("이름","")
            if "도화" in _nm:
                _danger_signals.append(("🌸 이성 문제·외도 가능성",
                    "도화살이 강하게 작용하는 시기입니다. "
                    "배우자 있는 분은 외부 이성과의 접촉을 삼가십시오. "
                    "감각적 유혹에 흔들리기 쉬운 해입니다."))
            if "망신" in _nm:
                _danger_signals.append(("🌀 구설수·스캔들 주의",
                    "망신살이 세운과 맞물립니다. "
                    "SNS·술자리·직장에서 언행을 극도로 조심하십시오. "
                    "비밀이 드러나거나 남의 일에 엮이는 수가 있습니다."))
            if "역마" in _nm:
                _danger_signals.append(("🚗 이동·교통사고 주의",
                    "역마살이 활성화되어 있습니다. "
                    "장거리 이동 시 각별히 조심하고 운전 중 핸드폰은 금물입니다."))
            if "관재" in _nm or "백호" in _nm:
                _danger_signals.append(("⚖️ 법적 분쟁·관재수",
                    "관재수가 보입니다. 계약서·법적 서류를 꼼꼼히 확인하고 "
                    "보증·연대책임은 절대 서지 마십시오."))
        if _oh_cg == "火" and _oh_jj == "火":
            _danger_signals.append(("🏥 건강 적신호 — 심장·혈압·눈",
                "올해 천간·지지 모두 火 기운으로 과열 상태입니다. "
                "심장 두근거림, 혈압 상승, 눈 충혈, 불면증이 생기기 쉽습니다. "
                "정기 건강검진을 꼭 받으십시오."))
        _sw_ss_raw = cross.get("sw_ss","")
        if "편관" in _sw_ss_raw:
            _danger_signals.append(("⚡ 직장·권력자 압박수",
                "편관 세운은 상사나 권력자로부터 압박을 받거나 "
                "직장에서 갑작스러운 위기가 올 수 있습니다. "
                "규칙을 철저히 지키고 튀는 행동을 삼가십시오."))
        if "상관" in _sw_ss_raw:
            _danger_signals.append(("💬 이혼·구설·직장 충돌",
                "상관 세운은 윗사람과의 충돌, 배우자와의 갈등이 폭발하는 시기입니다. "
                "기혼자는 이혼 위기, 직장인은 상사와 크게 부딪힐 수 있습니다."))
    except Exception:
        pass

    lines = []
    _dw_label = f"{dw_kr} 대운" if dw_kr else "대운 미산출"'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ 위험신호 분석 블록 삽입 완료")
else:
    print("❌ 패턴 없음")

with open('manse.py', 'w', encoding='utf-8') as f:
    f.write(content)
