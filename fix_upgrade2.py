# fix_upgrade2.py — 신년운세 탭 추가 + 궁합 상대방 비교 강화
import re, py_compile

with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# ══════════════════════════════════════════
# 수정 1: 신년운세 전용 탭 추가
# ══════════════════════════════════════════

# 1-1: _TAB_DEFS에 신년운세 추가 (토정비결 다음)
old_tabs = '''                ("📜", "토정비결"),
                ("📄", "PDF리포트"),
                ("🌟", "개운처방"),'''

new_tabs = '''                ("📜", "토정비결"),
                ("🎊", "신년운세"),
                ("📄", "PDF리포트"),
                ("🌟", "개운처방"),'''

src = src.replace(old_tabs, new_tabs)

# 1-2: 버튼 행 2 → 9개로 변경
src = src.replace(
    '# 버튼 행 2 (7개)\n            _btn_cols2 = st.columns(7)',
    '# 버튼 행 2 (8개)\n            _btn_cols2 = st.columns(8)'
)

# 1-3: 라우팅에 신년운세 추가
old_route = '''            elif _cur_tab == 12:
                menu_tojeong(pils, name, birth_year, gender)
            elif _cur_tab == 13:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))
            elif _cur_tab == 14:
                menu_gaewoon(pils, name, birth_year, gender)'''

new_route = '''            elif _cur_tab == 12:
                menu_tojeong(pils, name, birth_year, gender)
            elif _cur_tab == 13:
                menu_yearly(pils, name, birth_year, gender)
            elif _cur_tab == 14:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))
            elif _cur_tab == 15:
                menu_gaewoon(pils, name, birth_year, gender)'''

src = src.replace(old_route, new_route)

# 1-4: PDF 탭 active_tab 인덱스 14→15로 업데이트
src = src.replace(
    'st.session_state["active_tab"] = 14  # PDF 탭으로 이동',
    'st.session_state["active_tab"] = 14  # PDF 탭으로 이동'
)

print("신년운세 탭 추가 완료")

# ══════════════════════════════════════════
# 수정 2: 신년운세 메뉴 함수 추가
# ══════════════════════════════════════════
YEARLY_FUNC = '''

def menu_yearly(pils, name, birth_year, gender):
    """🎊 신년운세 — 올해·내년 집중 분석"""

    cur_year = datetime.now().year

    st.markdown(
        f"<div style='background:linear-gradient(135deg,#0d0820,#1a1035,#2d1f5e);"
        f"border-radius:16px;padding:22px 26px;margin-bottom:20px;"
        f"border:2px solid #d4af3788;'>"
        f"<div style='font-size:11px;color:#d4af37;letter-spacing:4px;"
        f"font-weight:900;margin-bottom:6px'>🎊 신년운세</div>"
        f"<div style='font-size:20px;font-weight:900;color:#fff;margin-bottom:4px'>"
        f"{name}님의 {cur_year}년 · {cur_year+1}년 집중 분석</div>"
        f"<div style='font-size:12px;color:#aaa;'>"
        f"{birth_year}년생 ({cur_year-birth_year+1}세) | "
        f"올해와 내년 운세를 사주 기반으로 분석합니다</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── 올해 토정비결 (개인화) ──────────────────────────────────
    try:
        _tj_out = LocalSajuNarrator.tojeong(pils, name, birth_year, gender)
        if _tj_out:
            st.markdown(_tj_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 신년운세 오류: {_e}")

    st.markdown("---")

    # ── 내년 미리 보기 ──────────────────────────────────────────
    st.markdown(
        f'<div class="gold-section">🔮 {cur_year+1}년 미리 보기</div>',
        unsafe_allow_html=True,
    )
    try:
        _ny = get_yearly_luck(pils, cur_year+1) or {}
        _ny_ss  = _ny.get("십성_천간","")
        _ny_gh  = _ny.get("길흉","평")
        _ny_gan = _ny.get("세운","")
        _ys_ny  = get_yongshin(pils)
        _yong_ny= _ys_ny.get("종합_용신",[]) if _ys_ny else []
        _gisin_ny=_ys_ny.get("기신",[]) if _ys_ny and isinstance(_ys_ny.get("기신"),list) else []
        _OH_NY  = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                   "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _ny_oh  = _OH_NY.get(_ny_gan[:1],"") if _ny_gan else ""
        _is_y_ny= _ny_oh in _yong_ny
        _is_g_ny= _ny_oh in _gisin_ny
        _ny_sig = ("🟢 황금기 예고 — 지금부터 준비하십시오!" if _is_y_ny else
                   "🔴 주의기 예고 — 안전 자산 미리 확보하십시오" if _is_g_ny else
                   "🟡 중립 — 꾸준히 내실 다지기")
        _GH_KR  = {"길":"✅ 길","+":" ✅ 길","평":"⚖️ 평","흉":"⚠️ 흉","-":"⚠️ 흉"}
        _NY_SS_DESC = {
            "偏財":f"재물 기회·이성 인연·사업 변동의 해. 지금부터 사업 계획을 세우십시오.",
            "正財":f"안정 수입·결혼 인연·자산 정착의 해. 저축과 부동산을 준비하십시오.",
            "食神":f"재능·복록·창업의 해. 하고 싶은 일의 준비를 지금부터 시작하십시오.",
            "傷官":f"창의·이직·갈등의 해. 말조심과 계약서 확인을 철저히 하십시오.",
            "偏官":f"긴장·변동·건강 주의의 해. 정기검진과 안전에 미리 대비하십시오.",
            "正官":f"명예·승진·결혼의 해. 지금부터 실력을 쌓아 기회를 잡으십시오.",
            "劫財":f"손재·경쟁의 해. 투자·보증을 미리 정리하고 현금을 확보하십시오.",
            "比肩":f"독립·경쟁의 해. 단독 추진 계획을 지금부터 세우십시오.",
            "偏印":f"변화·이동·학업의 해. 이사·이직 계획을 미리 검토하십시오.",
            "正印":f"학습·자격·귀인의 해. 시험·자격증 준비를 지금부터 시작하십시오.",
        }
        st.markdown(
            f"<div style='background:#1a1a2e;border-radius:14px;padding:18px 22px;"
            f"border:1.5px solid #d4af3744;'>"
            f"<div style='font-size:16px;font-weight:900;color:#fff;margin-bottom:10px'>"
            f"{cur_year+1}년 {_ny_gan} [{_ny_ss}] — {_GH_KR.get(_ny_gh,_ny_gh)}</div>"
            f"<div style='font-size:14px;color:#e8a0f0;font-weight:700;"
            f"margin-bottom:8px'>{_ny_sig}</div>"
            f"<div style='font-size:13px;color:#ccc;line-height:1.8'>"
            f"{_NY_SS_DESC.get(_ny_ss, f'{cur_year+1}년 {_ny_ss} 기운의 해입니다.')}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    except Exception as _nye:
        st.warning(f"⚠️ 내년 미리보기 오류: {_nye}")

    render_pdf_download_btn("yearly", pils, name, birth_year, gender)

'''

# menu_tojeong 앞에 삽입
src = src.replace('def menu_tojeong(pils, name, birth_year, gender):', YEARLY_FUNC + 'def menu_tojeong(pils, name, birth_year, gender):')
print("menu_yearly 함수 추가 완료")

# ══════════════════════════════════════════
# 수정 3: 궁합 상대방 비교 강화
# ══════════════════════════════════════════
# 기존 partner_pils 비교 결과에 월별 궁합 타이밍 + 일주 상세 분석 추가
old_partner = '''    st.markdown("---")

    # ── 로컬 엔진 항상 먼저 출력 ─────────────
    try:
        _marriage_v2 = st.session_state.get("in_marriage", "미혼")
        _local_out = LocalSajuNarrator.relations(pils, name, birth_year, gender, _marriage_v2)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 관계 분석 오류: {_e}")'''

new_partner = '''    # ── 두 사주 월별 궁합 타이밍 ─────────────────────────────────
    _p_pils2 = st.session_state.get("partner_pils")
    if _p_pils2:
        st.markdown(
            '<div class="gold-section">📅 두 사람의 궁합 최적 타이밍</div>',
            unsafe_allow_html=True,
        )
        try:
            _cur_yr_rel = datetime.now().year
            _OH_REL = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                       "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
            _my_ys2  = get_yongshin(pils)
            _p_ys2   = get_yongshin(_p_pils2)
            _my_yong2= _my_ys2.get("종합_용신",[]) if _my_ys2 else []
            _p_yong2 = _p_ys2.get("종합_용신",[]) if _p_ys2 else []
            # 두 사람 모두에게 좋은 해 찾기
            _good_yrs = []
            _bad_yrs  = []
            for _yr_r in range(_cur_yr_rel, _cur_yr_rel+5):
                _sw_r = get_yearly_luck(pils, _yr_r) or {}
                _sw_r2= get_yearly_luck(_p_pils2, _yr_r) or {}
                _oh_r1= _OH_REL.get(_sw_r.get("세운","")[:1],"")
                _oh_r2= _OH_REL.get(_sw_r2.get("세운","")[:1],"")
                _both_good = _oh_r1 in _my_yong2 and _oh_r2 in _p_yong2
                _both_bad  = _oh_r1 in (_my_ys2.get("기신",[]) if _my_ys2 else []) and \
                             _oh_r2 in (_p_ys2.get("기신",[]) if _p_ys2 else [])
                _age_r = _yr_r - birth_year + 1
                if _both_good:
                    _good_yrs.append(f"**{_yr_r}년**({_age_r}세) 🌟 두 사람 모두 용신운 — 최고의 해")
                elif _both_bad:
                    _bad_yrs.append(f"{_yr_r}년({_age_r}세) ⚠️ 두 사람 모두 기신운 — 중요 결정 자제")
                elif _oh_r1 in _my_yong2 or _oh_r2 in _p_yong2:
                    _good_yrs.append(f"{_yr_r}년({_age_r}세) ✅ 한 사람에게 유리한 해")

            _timing_html = "<div style='font-size:13px;color:#3d2800;line-height:2'>"
            if _good_yrs:
                _timing_html += "<b>💑 함께 움직이기 좋은 해:</b><br>"
                _timing_html += "<br>".join(f"  {g}" for g in _good_yrs[:3])
            if _bad_yrs:
                _timing_html += "<br><b>⚠️ 조심해야 할 해:</b><br>"
                _timing_html += "<br>".join(f"  {b}" for b in _bad_yrs[:2])
            _timing_html += "</div>"
            st.markdown(
                f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);"
                f"border:1px solid #c9a84c;border-radius:14px;padding:18px;"
                f"margin:10px 0'>{_timing_html}</div>",
                unsafe_allow_html=True,
            )
        except Exception as _re3:
            pass

    st.markdown("---")

    # ── 로컬 엔진 항상 먼저 출력 ─────────────
    try:
        _marriage_v2 = st.session_state.get("in_marriage", "미혼")
        _local_out = LocalSajuNarrator.relations(pils, name, birth_year, gender, _marriage_v2)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 관계 분석 오류: {_e}")'''

src = src.replace(old_partner, new_partner)
print("궁합 타이밍 분석 추가 완료")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("manse.py 수정 완료")

# ── 문법 검사 ──
print("\n=== 문법 검사 ===")
all_ok = True
for fname in ["manse.py", "saju_interpreter.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"  NG: {fname} → {str(e)[:100]}")
        all_ok = False

if all_ok:
    print("\n✅ 완료!")
else:
    print("\n❌ 오류 확인 필요!")