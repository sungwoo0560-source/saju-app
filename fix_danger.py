with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 렌더링 시작 직전에 위험신호 분석 블록 삽입
old = '''    lines = []
    lines.append(f"## 🎯 {name}님, 지금 무엇 때문에 힘드신가요?")'''

new = '''    # ── 위험 신호 분석 ─────────────────────────────────────
    _danger_signals = []

    try:
        from saju_interpreter import get_12sinsal, get_yearly_luck
        _sinsal_list = get_12sinsal(pils)
        _yl = get_yearly_luck(pils, cur_year)
        _jj_cur = _yl.get("jj", "")   # 세운 지지
        _oh_cg  = _yl.get("오행_천간", "")
        _oh_jj  = _yl.get("오행_지지", "")

        # 충(沖) 판단 — 일지 vs 세운지지
        _CHUNG_MAP = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅","卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
        _il_jj = pils[1].get("jj","")
        _yl_jj_raw = _jj_cur

        if _CHUNG_MAP.get(_il_jj,"") == _yl_jj_raw:
            _danger_signals.append(("💥 이동수·사고수 주의", f"올해 일지({_il_jj})와 세운지지({_yl_jj_raw})가 충(沖)을 이룹니다. 갑작스러운 이동, 교통사고, 수술, 이사, 이직 등 큰 변화가 터질 수 있습니다. 특히 상반기 중 조심하십시오."))

        # 년주·월주 충 → 이혼수
        _year_jj = pils[0].get("jj","") if len(pils)>0 else ""
        if _CHUNG_MAP.get(_year_jj,"") == _yl_jj_raw:
            _danger_signals.append(("💔 부부·가족 갈등 수", f"올해 년주({_year_jj})와 세운이 충돌합니다. 배우자 또는 가족과의 심각한 갈등, 별거, 이혼 논의가 생길 수 있습니다. 감정이 격해지는 시기에 큰 결정을 미루십시오."))

        # 신살 기반 경고
        for _s in _sinsal_list:
            _nm = _s.get("이름","")
            _tp = _s.get("type","")

            if "도화" in _nm:
                _danger_signals.append(("🌸 이성 문제·외도 가능성", f"도화살이 강하게 작용하는 시기입니다. 배우자 있는 분은 외부 이성과의 불필요한 접촉을 삼가십시오. 미혼이라면 연애운은 좋으나 상대의 진심을 잘 살펴야 합니다. 감각적 유혹에 흔들리기 쉬운 해입니다."))

            if "망신" in _nm:
                _danger_signals.append(("🌀 구설수·스캔들 주의", f"망신살이 세운과 맞물립니다. 말 한마디가 큰 화를 부를 수 있으니 SNS·술자리·직장에서 언행을 극도로 조심하십시오. 비밀이 드러나거나 남의 일에 엮이는 수가 있습니다."))

            if "겁재" in _nm or "양인" in _nm:
                _danger_signals.append(("⚔️ 재물 손실·다툼 수", f"겁재·양인살 기운이 강합니다. 투자 손실, 보증, 동업 분쟁이 생길 수 있습니다. 큰 돈이 오가는 결정은 올해를 피하십시오."))

            if "역마" in _nm:
                _danger_signals.append(("🚗 이동·교통사고 주의", f"역마살이 활성화되어 있습니다. 장거리 이동 시 각별히 조심하고, 운전 중 핸드폰 사용은 금물입니다."))

            if "관재" in _nm or "백호" in _nm:
                _danger_signals.append(("⚖️ 법적 분쟁·관재 수", f"관재수가 보입니다. 계약서·법적 서류를 꼼꼼히 확인하고, 보증·연대책임은 절대 서지 마십시오."))

        # 세운 오행 火火 겹침 → 건강(심장·혈압)
        if _oh_cg == "火" and _oh_jj == "火":
            _danger_signals.append(("🏥 건강 적신호 — 심장·혈압·눈", f"올해 천간·지지 모두 火 기운으로 과열 상태입니다. 심장 두근거림, 혈압 상승, 눈 충혈, 불면증이 생기기 쉽습니다. 정기 건강검진을 꼭 받으십시오. 무더운 여름철 특히 조심하십시오."))

        # 세운 십성 편관 → 사고수·직장 위기
        _sw_ss_raw = cross.get("sw_ss","")
        if "편관" in _sw_ss_raw:
            _danger_signals.append(("⚡ 직장·법적 압박 수", f"편관 세운은 상사나 권력자로부터 압박을 받거나, 직장에서 갑작스러운 위기가 올 수 있습니다. 규칙을 철저히 지키고 튀는 행동을 삼가십시오."))

        # 세운 십성 상관 → 이혼·구설
        if "상관" in _sw_ss_raw:
            _danger_signals.append(("💬 이혼·구설·직장 충돌", f"상관 세운은 윗사람과의 충돌, 배우자와의 갈등이 폭발하는 시기입니다. 기혼자는 이혼 위기가 올 수 있고, 직장인은 상사와 크게 부딪힐 수 있습니다."))

    except Exception:
        pass

    lines = []
    lines.append(f"## 🎯 {name}님, 지금 무엇 때문에 힘드신가요?")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ 위험신호 섹션 삽입 완료")
else:
    print("❌ 패턴 없음 — 확인 필요")

# 위험신호 렌더링 — 기존 렌더링 직후 삽입
old2 = '''    # 1. 공감 질문
    lines.append(f"### 💬 {hard_q}")'''

new2 = '''    # 0. 위험 신호 카드 (있을 때만)
    if _danger_signals:
        lines.append("### 🚨 지금 당신의 사주에서 보이는 위험 신호")
        lines.append("")
        for _title, _body in _danger_signals:
            lines.append(f"**{_title}**")
            lines.append(_body)
            lines.append("")
        lines.append("---")
        lines.append("")

    # 1. 공감 질문
    lines.append(f"### 💬 {hard_q}")'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ 위험신호 렌더링 삽입 완료")
else:
    print("❌ 렌더링 패턴 없음")

with open('manse.py', 'w', encoding='utf-8') as f:
    f.write(content)
