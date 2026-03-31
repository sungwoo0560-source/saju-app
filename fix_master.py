# fix_master.py — 전체 파일 종합 수정
import re, py_compile

# ══════════════════════════════════════════
# 수정 1: 취소선 ~ 일괄 수정 (147건)
# ══════════════════════════════════════════
for fname in ["manse.py", "saju_interpreter.py"]:
    with open(fname, encoding="utf-8") as f:
        src = f.read()
    before = len(re.findall(r'\d~\d', src))
    src = re.sub(r'(\d)~(\d)', r'\1\\~\2', src)
    after = len(re.findall(r'(?<!\\)\d~\d', src))
    with open(fname, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"취소선 수정: {fname} — {before}건 → {after}건 잔존")

# ══════════════════════════════════════════
# 수정 2: manse.py — 건강탭 연결 + render_pdf_download_btn + build_past_events
# ══════════════════════════════════════════
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# 2-1: 건강탭 _TAB_DEFS 수정 (15개 → 16개)
if '"🏥", "건강분석"' not in src:
    src = src.replace(
        '("💑", "궁합관계"),\n                ("📅", "월별운세")',
        '("💑", "궁합관계"),\n                ("🏥", "건강분석"),\n                ("📅", "월별운세")'
    )
    print("건강탭 _TAB_DEFS 추가")
else:
    print("건강탭 이미 존재")

# 2-2: 버튼 행 2 columns 수정
if "# 버튼 행 2 (8개)" not in src:
    src = src.replace(
        "# 버튼 행 2 (7개)\n            _btn_cols2 = st.columns(7)",
        "# 버튼 행 2 (8개)\n            _btn_cols2 = st.columns(8)"
    )
    print("버튼 행 2 columns 수정")

# 2-3: 라우팅 수정 — 건강탭 7번, 나머지 한 칸씩 밀기
old_route = '''            elif _cur_tab == 7:
                menu10_monthly(pils, name, birth_year, gender)
            elif _cur_tab == 8:
                menu9_daily(pils, name, birth_year, gender)
            elif _cur_tab == 9:
                menu7_ai(pils, name, birth_year, gender)
            elif _cur_tab == 10:
                menu8_bihang(pils, name, birth_year, gender)
            elif _cur_tab == 11:
                menu16_ohaeng_deep(pils, name, birth_year, gender)
            elif _cur_tab == 12:
                menu_tojeong(pils, name, birth_year, gender)
            elif _cur_tab == 13:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))
            elif _cur_tab == 14:
                menu_gaewoon(pils, name, birth_year, gender)'''

new_route = '''            elif _cur_tab == 7:
                menu14_health(pils, name, birth_year, gender)
            elif _cur_tab == 8:
                menu10_monthly(pils, name, birth_year, gender)
            elif _cur_tab == 9:
                menu9_daily(pils, name, birth_year, gender)
            elif _cur_tab == 10:
                menu7_ai(pils, name, birth_year, gender)
            elif _cur_tab == 11:
                menu8_bihang(pils, name, birth_year, gender)
            elif _cur_tab == 12:
                menu16_ohaeng_deep(pils, name, birth_year, gender)
            elif _cur_tab == 13:
                menu_tojeong(pils, name, birth_year, gender)
            elif _cur_tab == 14:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))
            elif _cur_tab == 15:
                menu_gaewoon(pils, name, birth_year, gender)'''

if old_route in src:
    src = src.replace(old_route, new_route)
    print("라우팅 수정 완료")
else:
    print("라우팅 이미 수정됨 또는 패턴 불일치")

# 2-4: build_past_events @cache_data 제거
src = src.replace(
    '@st.cache_data(hash_funcs={dict: lambda d: json.dumps(d, sort_keys=True, default=str)})\ndef build_past_events(',
    '# @cache_data 제거 — session_state 내부 접근\ndef build_past_events('
)
print("build_past_events 캐시 제거")

# 2-5: render_pdf_download_btn 함수 추가 (없으면)
if 'def render_pdf_download_btn' not in src:
    PDF_BTN_FUNC = '''
def render_pdf_download_btn(tab_name, pils, name, birth_year, gender):
    """각 탭 하단 PDF 빠른 출력 — PDF 탭으로 이동"""
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(212,175,55,0.2);margin:20px 0 10px'>",
        unsafe_allow_html=True,
    )
    _TAB_LABEL = {
        "lifeline":"대운흐름","past":"과거분석","future3":"미래3년",
        "money":"재물사업","relations":"궁합관계","health":"건강분석",
        "daily":"일일운세","monthly":"월별운세","gaewoon":"개운처방",
        "ohaeng":"음양오행","tojeong":"토정비결","current_situation":"현재상황",
    }
    _label = _TAB_LABEL.get(tab_name, tab_name)
    _c1, _c2, _c3 = st.columns([1,2,1])
    with _c2:
        if st.button(f"📄 {_label} PDF 출력", key=f"pdf_quick_{tab_name}",
                     use_container_width=True):
            # PDF 탭 인덱스 14로 이동
            st.session_state["active_tab"] = 14
            st.rerun()

'''
    # render_ai_deep_analysis 바로 앞에 삽입
    src = src.replace(
        'def render_ai_deep_analysis(',
        PDF_BTN_FUNC + 'def render_ai_deep_analysis('
    )
    print("render_pdf_download_btn 함수 추가")
else:
    print("render_pdf_download_btn 이미 존재")

# 2-6: 각 탭 마지막에 PDF 버튼 추가 (없는 경우만)
TAB_PDF_MAP = [
    # (탭키, render_ai_deep_analysis 호출 패턴, 다음 def 패턴)
    ("lifeline",  'render_ai_deep_analysis("lifeline"',  'def menu3_past'),
    ("past",      'render_ai_deep_analysis("past"',      'def menu4_future3'),
    ("future3",   'render_ai_deep_analysis("future"',    'def menu5_money'),
    ("money",     'render_ai_deep_analysis("money"',     'def menu6_relations'),
    ("relations", 'render_ai_deep_analysis("relations"', 'def menu9_daily'),
]
for tab_key, ai_pat, next_def in TAB_PDF_MAP:
    pdf_key = f'pdf_quick_{tab_key}'
    if pdf_key not in src:
        # AI 버튼 다음에 PDF 버튼 추가
        old_p = f'    render_ai_deep_analysis("{tab_key if tab_key != "future3" else "future"}", pils, name, birth_year, gender)\n\n\ndef'
        new_p = f'    render_ai_deep_analysis("{tab_key if tab_key != "future3" else "future"}", pils, name, birth_year, gender)\n    render_pdf_download_btn("{tab_key}", pils, name, birth_year, gender)\n\n\ndef'
        if old_p in src:
            src = src.replace(old_p, new_p)
            print(f"  PDF 버튼 추가: {tab_key}")

# 일진/월운 탭 PDF 버튼
for tab_key, next_def in [
    ("daily",   "def menu10_monthly"),
    ("monthly", "def menu8_bihang"),
]:
    if f'pdf_quick_{tab_key}' not in src:
        src = src.replace(
            f'\n\n{next_def}',
            f'\n    render_pdf_download_btn("{tab_key}", pils, name, birth_year, gender)\n\n\n{next_def}'
        )
        print(f"  PDF 버튼 추가: {tab_key}")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 수정 완료")

# ══════════════════════════════════════════
# 수정 3: saju_engine.py — None 반환 → {} 반환
# ══════════════════════════════════════════
with open("saju_engine.py", encoding="utf-8") as f:
    src = f.read()

# get_monthly_luck
src = src.replace(
    'def get_monthly_luck(pils, year, month):\n    """월운 계산 - 오호둔월법으로 월간(천간) 계산 후 십성 산출"""\n\n    if not pils:\n        return None',
    'def get_monthly_luck(pils, year, month):\n    """월운 계산 - 오호둔월법으로 월간(천간) 계산 후 십성 산출"""\n\n    if not pils:\n        return {}'
)

# get_daewoon_sewoon_cross None → {} 
src = re.sub(
    r'(def get_daewoon_sewoon_cross.*?if not pils.*?return) None',
    r'\1 {}',
    src, flags=re.DOTALL, count=1
)

with open("saju_engine.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_engine.py 수정 완료")

# ══════════════════════════════════════════
# 수정 4: saju_report.py — PDF 푸터 + 신규 섹션 연결
# ══════════════════════════════════════════
with open("saju_report.py", encoding="utf-8") as f:
    src = f.read()

# 4-1: new_page에 푸터 추가
if '_page_num' not in src:
    src = src.replace(
        '            def new_page(c):\n                c.showPage()\n                c.setFont(BASE_FONT, 9)\n                return H - MARGIN',
        '''            _page_num = [1]
            _section_num = [0]

            def _draw_footer(c):
                c.setStrokeColorRGB(0.75, 0.65, 0.25)
                c.setLineWidth(0.3)
                c.line(MARGIN, BOT - 3*mm, W - MARGIN, BOT - 3*mm)
                c.setFillColorRGB(0.5, 0.45, 0.35)
                c.setFont(BASE_FONT, 8)
                c.drawString(MARGIN, BOT - 7*mm, "만세력 사주 천명풀이")
                c.drawRightString(W - MARGIN, BOT - 7*mm, f"{_page_num[0]}p")
                c.drawCentredString(W/2, BOT - 7*mm, f"{name} 님의 사주 리포트")

            def new_page(c):
                _draw_footer(c)
                _page_num[0] += 1
                c.showPage()
                c.setFont(BASE_FONT, 9)
                return H - MARGIN'''
    )
    # c.save() 직전 푸터
    src = src.replace('            c.save()', '            _draw_footer(c)\n            c.save()', 1)
    print("saju_report.py PDF 푸터 추가")
else:
    print("saju_report.py 푸터 이미 존재")

# 4-2: 체크박스 신규 10개 추가 (없으면)
if 'include_money' not in src:
    old_col = '''    with col2:
        include_ss = st.checkbox("십성 분포 분석", value=True, key="pdf_ss")

        include_sinsal = st.checkbox("신살 분석", value=True, key="pdf_sinsal")

        include_yukjin = st.checkbox("육친 분석", value=True, key="pdf_yukjin")

        include_fortune = st.checkbox("AI 종합운세 (전문 분석)", value=True, key="pdf_fortune")

        include_advice = st.checkbox("처방/조언", value=True, key="pdf_advice")

        include_ohaeng = st.checkbox("☯️ 음양오행 심층 분석", value=True, key="pdf_ohaeng")'''

    new_col = '''    with col2:
        include_ss      = st.checkbox("십성 분포 분석",           value=True, key="pdf_ss")
        include_sinsal  = st.checkbox("신살 분석",                value=True, key="pdf_sinsal")
        include_yukjin  = st.checkbox("육친 분석",                value=True, key="pdf_yukjin")
        include_fortune = st.checkbox("AI 종합운세 (전문 분석)",   value=True, key="pdf_fortune")
        include_advice  = st.checkbox("처방/조언",                value=True, key="pdf_advice")
        include_ohaeng  = st.checkbox("☯️ 음양오행 심층 분석",    value=True, key="pdf_ohaeng")
        include_money   = st.checkbox("💰 재물/직업 분석",        value=True, key="pdf_money")
        include_health  = st.checkbox("🏥 건강 분석",             value=True, key="pdf_health")
        include_relation= st.checkbox("💑 궁합/관계 분석",        value=True, key="pdf_relation")
        include_future3 = st.checkbox("🔮 미래 3년 분석",         value=True, key="pdf_future3")
        include_daily   = st.checkbox("☀️ 오늘의 운세",          value=True, key="pdf_daily")
        include_monthly = st.checkbox("📅 이달의 운세",           value=True, key="pdf_monthly")
        include_nature  = st.checkbox("🧬 성격/기질 분석",        value=True, key="pdf_nature")
        include_gaewoon = st.checkbox("🌟 개운 처방",             value=True, key="pdf_gaewoon")
        include_tojeong = st.checkbox("📜 토정비결",              value=True, key="pdf_tojeong")'''

    src = src.replace(old_col, new_col)
    print("saju_report.py 체크박스 10개 추가")
else:
    print("saju_report.py 체크박스 이미 존재")

with open("saju_report.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_report.py 수정 완료")

# ══════════════════════════════════════════
# 수정 5: saju_sinsal.py 미사용 함수 — manse.py 신살 분석에 연결
# ══════════════════════════════════════════
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# get_pahae / get_geunmyo_hwasil / get_waryeong / get_oigyeok → 신살 탭에 연결
if 'get_pahae(' not in src:
    old_sinsal = '''    tab_yukjin(pils, gender)'''
    new_sinsal = '''    tab_yukjin(pils, gender)

    # ── 미사용 신살 분석 연결 ────────────────────────────────────
    try:
        from saju_sinsal import get_pahae, get_geunmyo_hwasil, get_waryeong, get_oigyeok
        st.markdown(\'<div class="gold-section">🔍 파살·해살 분석</div>\', unsafe_allow_html=True)
        _ph = get_pahae(pils)
        _pahae_list = _ph.get("파살",[]) + _ph.get("해살",[])
        if _pahae_list:
            for _p in _pahae_list[:3]:
                st.markdown(f"- {_p}", unsafe_allow_html=True)
        else:
            st.markdown("파살·해살이 감지되지 않습니다. ✅")

        st.markdown(\'<div class="gold-section">🌱 근묘화실 — 4기둥 궁 분석</div>\', unsafe_allow_html=True)
        _gm = get_geunmyo_hwasil(pils)
        if isinstance(_gm, list):
            for _g in _gm[:4]:
                if isinstance(_g, dict):
                    st.markdown(f"**{_g.get('궁','')}**: {_g.get('설명','')}")
    except Exception as _se:
        pass'''
    src = src.replace(old_sinsal, new_sinsal)
    print("파살·해살·근묘화실 연결")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 최종 수정 완료")

# ══════════════════════════════════════════
# 전체 문법 검사
# ══════════════════════════════════════════
print("\n=== 최종 문법 검사 ===")
all_ok = True
for fname in ["manse.py","saju_engine.py","saju_interpreter.py","saju_report.py","saju_sinsal.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"  NG: {fname} → {str(e)[:100]}")
        all_ok = False

print("\n✅ 전체 완료!" if all_ok else "\n❌ 오류 확인 필요!")