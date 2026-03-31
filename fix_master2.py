# fix_master2.py — 전체 파일 종합 수정 2차
import re, py_compile

# ══════════════════════════════════════════
# 수정 1: 취소선 ~ 일괄 수정
# ══════════════════════════════════════════
for fname in ["manse.py", "saju_interpreter.py"]:
    with open(fname, encoding="utf-8") as f:
        src = f.read()
    before = len(re.findall(r'(?<!\\)\d~\d', src))
    src = re.sub(r'(\d)~(\d)', r'\1\\~\2', src)
    with open(fname, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"취소선 수정: {fname} {before}건")

# ══════════════════════════════════════════
# 수정 2: manse.py 종합 수정
# ══════════════════════════════════════════
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# 2-1: "Water" 오타 수정
src = src.replace('"Water"', '"水"')
print("Water 오타 수정")

# 2-2: build_past_events @cache_data 제거
if '@st.cache_data' in src and 'def build_past_events' in src:
    src = re.sub(
        r'@st\.cache_data\([^)]*\)\s*\ndef build_past_events\(',
        '# @cache_data 제거 — session_state 접근\ndef build_past_events(',
        src
    )
    print("build_past_events 캐시 제거")

# 2-3: _TAB_DEFS에 건강탭+신년운세탭 추가
if '"🏥", "건강분석"' not in src:
    src = src.replace(
        '("💑", "궁합관계"),\n                ("📅", "월별운세")',
        '("💑", "궁합관계"),\n                ("🏥", "건강분석"),\n                ("📅", "월별운세")'
    )
    print("건강탭 추가")

if '"🎊", "신년운세"' not in src:
    src = src.replace(
        '("📜", "토정비결"),\n                ("📄", "PDF리포트")',
        '("📜", "토정비결"),\n                ("🎊", "신년운세"),\n                ("📄", "PDF리포트")'
    )
    print("신년운세탭 추가")

# 2-4: 버튼 행 2 columns 수정
if '# 버튼 행 2 (8개)\n            _btn_cols2 = st.columns(8)' not in src:
    src = src.replace(
        '# 버튼 행 2 (7개)\n            _btn_cols2 = st.columns(7)',
        '# 버튼 행 2 (8개)\n            _btn_cols2 = st.columns(8)'
    )
    print("버튼 행 columns 수정")

# 2-5: 라우팅 전면 교체 (건강+신년운세 포함)
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
                menu_yearly(pils, name, birth_year, gender)
            elif _cur_tab == 15:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))
            elif _cur_tab == 16:
                menu_gaewoon(pils, name, birth_year, gender)'''

if old_route in src:
    src = src.replace(old_route, new_route)
    print("라우팅 수정 완료")
else:
    print("라우팅 이미 수정됨")

# 2-6: render_pdf_download_btn 함수 추가
if 'def render_pdf_download_btn' not in src:
    PDF_BTN = '''
def render_pdf_download_btn(tab_name, pils, name, birth_year, gender):
    """각 탭 하단 PDF 출력 버튼"""
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(212,175,55,0.2);margin:20px 0 10px'>",
        unsafe_allow_html=True,
    )
    _TAB_LBL = {
        "lifeline":"대운흐름","past":"과거분석","future3":"미래3년",
        "money":"재물사업","relations":"궁합관계","health":"건강분석",
        "daily":"일일운세","monthly":"월별운세","gaewoon":"개운처방",
        "ohaeng":"음양오행","tojeong":"토정비결","yearly":"신년운세",
        "current_situation":"현재상황",
    }
    _label = _TAB_LBL.get(tab_name, tab_name)
    _c1, _c2, _c3 = st.columns([1,2,1])
    with _c2:
        if st.button(f"📄 {_label} PDF 출력",
                     key=f"pdf_quick_{tab_name}",
                     use_container_width=True):
            st.session_state["active_tab"] = 15
            st.rerun()

'''
    src = src.replace(
        'def render_ai_deep_analysis(',
        PDF_BTN + 'def render_ai_deep_analysis('
    )
    print("render_pdf_download_btn 추가")

# 2-7: menu_yearly 함수 추가 (없으면)
if 'def menu_yearly' not in src:
    YEARLY_FUNC = '''
def menu_yearly(pils, name, birth_year, gender):
    """🎊 신년운세 — 올해·내년 집중 분석"""
    cur_year = datetime.now().year
    st.markdown(
        f"<div style='background:linear-gradient(135deg,#0d0820,#2d1f5e);"
        f"border-radius:16px;padding:20px 24px;margin-bottom:16px;"
        f"border:2px solid #d4af3788;'>"
        f"<div style='font-size:20px;font-weight:900;color:#fff;'>"
        f"🎊 {name}님의 {cur_year}년 신년운세</div>"
        f"<div style='font-size:12px;color:#aaa;margin-top:4px;'>"
        f"{birth_year}년생 ({cur_year-birth_year+1}세)</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    try:
        _tj_out = LocalSajuNarrator.tojeong(pils, name, birth_year, gender)
        if _tj_out:
            st.markdown(_tj_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 신년운세 오류: {_e}")
    st.markdown("---")
    try:
        _ny = get_yearly_luck(pils, cur_year+1) or {}
        _ny_ss  = _ny.get("십성_천간","")
        _ny_gh  = _ny.get("길흉","평")
        _ny_gan = _ny.get("세운","")
        _ys_ny  = get_yongshin(pils)
        _yong_ny= _ys_ny.get("종합_용신",[]) if _ys_ny else []
        _OH_NY  = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                   "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _ny_oh  = _OH_NY.get(_ny_gan[:1],"") if _ny_gan else ""
        _is_y_ny= _ny_oh in _yong_ny
        _GH_KR2 = {"길":"✅ 길","+":"✅ 길","평":"⚖️ 평","흉":"⚠️ 흉","-":"⚠️ 흉"}
        _ny_sig = ("🟢 황금기 예고!" if _is_y_ny else "🟡 중립")
        st.markdown(
            f"<div style='background:#1a1a2e;border-radius:14px;padding:16px 20px;"
            f"border:1.5px solid #d4af3744;'>"
            f"<div style='font-size:14px;font-weight:900;color:#fff;margin-bottom:6px'>"
            f"🔮 {cur_year+1}년 미리보기</div>"
            f"<div style='font-size:13px;color:#e8a0f0;'>"
            f"{_ny_gan} [{_ny_ss}] {_GH_KR2.get(_ny_gh,_ny_gh)} — {_ny_sig}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass
    render_pdf_download_btn("yearly", pils, name, birth_year, gender)

'''
    src = src.replace(
        'def menu_tojeong(pils, name, birth_year, gender):',
        YEARLY_FUNC + 'def menu_tojeong(pils, name, birth_year, gender):'
    )
    print("menu_yearly 함수 추가")

# 2-8: 각 탭 PDF 버튼 추가
TAB_PDF_MAP = [
    ("lifeline",  'render_ai_deep_analysis("lifeline"', 'def menu3_past'),
    ("past",      'render_ai_deep_analysis("past"',     'def menu4_future3'),
    ("future3",   'render_ai_deep_analysis("future"',   'def menu5_money'),
    ("money",     'render_ai_deep_analysis("money"',    'def menu6_relations'),
    ("relations", 'render_ai_deep_analysis("relations"','def menu9_daily'),
]
for tab_key, ai_call, next_def in TAB_PDF_MAP:
    if f'pdf_quick_{tab_key}' not in src:
        old_p = f'    {ai_call}, pils, name, birth_year, gender)\n\n\n{next_def}'
        new_p = f'    {ai_call}, pils, name, birth_year, gender)\n    render_pdf_download_btn("{tab_key}", pils, name, birth_year, gender)\n\n\n{next_def}'
        if old_p in src:
            src = src.replace(old_p, new_p)
            print(f"  PDF 버튼: {tab_key}")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 완료")

# ══════════════════════════════════════════
# 수정 3: saju_engine.py — None → {} 반환
# ══════════════════════════════════════════
with open("saju_engine.py", encoding="utf-8") as f:
    src = f.read()

src = src.replace(
    'def get_monthly_luck(pils, year, month):\n    """월운 계산 - 오호둔월법으로 월간(천간) 계산 후 십성 산출"""\n\n    if not pils:\n        return None',
    'def get_monthly_luck(pils, year, month):\n    """월운 계산 - 오호둔월법으로 월간(천간) 계산 후 십성 산출"""\n\n    if not pils:\n        return {}'
)
src = re.sub(
    r'(def get_daewoon_sewoon_cross[^:]*:[^{]*?if not pils[^:]*:\s*)return None',
    r'\1return {}',
    src, count=1
)
with open("saju_engine.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_engine.py 완료")

# ══════════════════════════════════════════
# 수정 4: saju_report.py — PDF 푸터 + 신규 체크박스
# ══════════════════════════════════════════
with open("saju_report.py", encoding="utf-8") as f:
    src = f.read()

# 4-1: PDF 푸터
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
    src = src.replace('            c.save()', '            _draw_footer(c)\n            c.save()', 1)
    print("PDF 푸터 추가")

# 4-2: 체크박스 신규 추가
if 'include_money' not in src:
    src = src.replace(
        '        include_ohaeng = st.checkbox("☯️ 음양오행 심층 분석", value=True, key="pdf_ohaeng")',
        '''        include_ohaeng   = st.checkbox("☯️ 음양오행 심층 분석", value=True, key="pdf_ohaeng")
        include_money    = st.checkbox("💰 재물/직업 분석",        value=True, key="pdf_money")
        include_health   = st.checkbox("🏥 건강 분석",             value=True, key="pdf_health")
        include_relation = st.checkbox("💑 궁합/관계 분석",        value=True, key="pdf_relation")
        include_future3  = st.checkbox("🔮 미래 3년 분석",         value=True, key="pdf_future3")
        include_daily    = st.checkbox("☀️ 오늘의 운세",          value=True, key="pdf_daily")
        include_monthly  = st.checkbox("📅 이달의 운세",           value=True, key="pdf_monthly")
        include_nature   = st.checkbox("🧬 성격/기질 분석",        value=True, key="pdf_nature")
        include_gaewoon2 = st.checkbox("🌟 개운 처방",             value=True, key="pdf_gaewoon2")
        include_tojeong  = st.checkbox("📜 토정비결",              value=True, key="pdf_tojeong")'''
    )
    print("PDF 체크박스 10개 추가")

# 4-3: "Water" 오타 수정
src = src.replace('"Water"', '"水"')

with open("saju_report.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_report.py 완료")

# ══════════════════════════════════════════
# 수정 5: saju_interpreter.py — Water 오타 수정
# ══════════════════════════════════════════
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()
src = src.replace('"Water"', '"水"')
src = src.replace('"Fire"', '"火"')
with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 오타 수정")

# ══════════════════════════════════════════
# 전체 문법 검사
# ══════════════════════════════════════════
print("\n=== 최종 문법 검사 ===")
all_ok = True
for fname in ["manse.py","saju_engine.py","saju_interpreter.py","saju_report.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"  NG: {fname} → {str(e)[:100]}")
        all_ok = False
print("\n✅ 완료!" if all_ok else "\n❌ 오류 확인 필요!")
