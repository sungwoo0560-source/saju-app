# fix_region.py
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# ── 수정 1: 고급 설정에 출생지 선택 UI 추가 ──
old1 = '''        with st.expander("⚙️ 고급 설정 (야자시)", expanded=False):
            st.checkbox(
                "🌙 야자시 적용",
                value=True,
                key="in_use_yaja",
                help="23:00~00:00 사이 출생 시 다음날의 일진을 적용합니다.",
            )'''

new1 = '''        with st.expander("⚙️ 고급 설정 (야자시 · 지방시)", expanded=False):
            st.checkbox(
                "🌙 야자시 적용",
                value=True,
                key="in_use_yaja",
                help="23:00~00:00 사이 출생 시 다음날의 일진을 적용합니다.",
            )
            st.markdown("---")
            st.markdown("**🌐 출생지 (지방시 보정)**")
            _region_list = ["서울","부산","인천","대구","대전","광주","울산","세종",
                           "수원","고양","용인","부천","성남","안산","안양","평택",
                           "춘천","원주","강릉","속초","청주","충주","전주","군산",
                           "목포","여수","순천","포항","경주","구미","안동","창원",
                           "진주","거제","제주","서귀포"]
            _cur_region = _ss.get("in_birth_region", "서울")
            _cur_idx = _region_list.index(_cur_region) if _cur_region in _region_list else 0
            st.selectbox(
                "출생지",
                options=_region_list,
                index=_cur_idx,
                key="in_birth_region",
                help="출생지 경도 기준으로 진태양시를 자동 보정합니다.",
                label_visibility="collapsed",
            )
            _lon = TimeCorrection.REGION_LONGITUDE.get(_ss.get("in_birth_region","서울"), 126.98)
            _offset = round((_lon - 135.0) * 4)
            st.caption(f"📍 경도 {_lon}° → 표준시 대비 {_offset:+d}분 보정")'''

src = src.replace(old1, new1)

# ── 수정 2: SajuPrecisionEngine 호출에 longitude 전달 ──
old2 = '''                pils = SajuPrecisionEngine.get_pillars(
                    b_year,
                    b_month,
                    b_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    _ss["in_gender"],
                    use_yaja_time=_ss.get("in_use_yaja", True),
                )'''

new2 = '''                _region_lon = TimeCorrection.REGION_LONGITUDE.get(
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

src = src.replace(old2, new2)

# ── 수정 3: session_state 초기값 추가 ──
old3 = '    if "form_expanded" not in _ss:'
new3 = '''    if "in_birth_region" not in _ss:
        _ss["in_birth_region"] = "서울"
    if "form_expanded" not in _ss:'''

src = src.replace(old3, new3)

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 수정 완료")

import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("문법 OK: manse.py")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
