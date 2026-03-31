# fix_money_calendar.py — 금전운 타이밍 정밀 캘린더
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

old1 = '''    # ── 로컬 엔진 상세 분석 ─────────────
    try:
        _local_out = LocalSajuNarrator.money(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 재물 분석 오류: {_e}")

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")'''

new1 = '''    # ── 금전운 타이밍 정밀 캘린더 ─────────────────────────────
    st.markdown(
        '<div class="gold-section">📆 ⑤ 금전운 타이밍 정밀 캘린더</div>',
        unsafe_allow_html=True,
    )
    try:
        _cy_mc = datetime.now().year
        _cm_mc = datetime.now().month
        _ilgan_mc = pils[1]["cg"] if len(pils)>1 else "甲"
        _ys_mc = get_yongshin(pils) or {}
        _yong_mc = _ys_mc.get("종합_용신",[])
        _gisin_mc = _ys_mc.get("기신",[]) if isinstance(_ys_mc.get("기신"),list) else []
        _OH_MC = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _MONEY_SS = {"偏財","正財","食神","比肩"}  # 재물 유리 십성
        _DANGER_SS = {"劫財","偏官"}               # 재물 위험 십성

        # 월간 기반 계산 (오호둔월법)
        _MON_CG_BASE = {"甲":"丙","乙":"戊","丙":"庚","丁":"壬","戊":"甲",
                        "己":"丙","庚":"戊","辛":"庚","壬":"壬","癸":"甲"}
        _CG_LIST_MC = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
        _JJ_LIST_MC = ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"]
        _start_mc = _MON_CG_BASE.get(_ilgan_mc,"甲")
        _sidx_mc  = _CG_LIST_MC.index(_start_mc) if _start_mc in _CG_LIST_MC else 0

        # 향후 12개월 금전운 계산
        _mon_data = []
        for _mi in range(12):
            _abs_mi = (_cm_mc - 1 + _mi) % 12
            _yr_mi  = _cy_mc + (_cm_mc - 1 + _mi) // 12
            _mcg_mi = _CG_LIST_MC[(_sidx_mc + _abs_mi) % 10]
            _mjj_mi = _JJ_LIST_MC[_abs_mi]
            _mss_mi = TEN_GODS_MATRIX.get(_ilgan_mc,{}).get(_mcg_mi,"-")
            _moh_mi = _OH_MC.get(_mcg_mi,"")
            _is_y_mi = _moh_mi in _yong_mc
            _is_g_mi = _moh_mi in _gisin_mc
            _is_money_mi = _mss_mi in _MONEY_SS
            _is_danger_mi= _mss_mi in _DANGER_SS

            # 금전 점수 (0~100)
            _score_mi = 50
            if _is_y_mi:   _score_mi += 20
            if _is_g_mi:   _score_mi -= 20
            if _is_money_mi: _score_mi += 15
            if _is_danger_mi: _score_mi -= 20
            _score_mi = max(0, min(100, _score_mi))

            # 등급
            if _score_mi >= 80:
                _grade_mi = "💰💰💰 대길"
                _col_mi = "#1a3d1a"; _tc_mi = "#7fff7f"
            elif _score_mi >= 65:
                _grade_mi = "💰💰 길"
                _col_mi = "#1a3d30"; _tc_mi = "#52be80"
            elif _score_mi >= 50:
                _grade_mi = "💰 평길"
                _col_mi = "#1a1a2e"; _tc_mi = "#aaaaff"
            elif _score_mi >= 35:
                _grade_mi = "⚠️ 주의"
                _col_mi = "#2e1a1a"; _tc_mi = "#f0a080"
            else:
                _grade_mi = "🔴 위험"
                _col_mi = "#3d1a1a"; _tc_mi = "#ffaaaa"

            # 추천 행동
            _MON_ACTION_MC = {
                "偏財": "수입 기회 적극 포착. 외부 활동·영업 강화",
                "正財": "저축·정산·계약서 처리. 안전 자산 확보",
                "食神": "재능 수익화·부업 시작. 콘텐츠·강의 도전",
                "劫財": "투자·보증 절대 금지. 현금 보유 최우선",
                "偏官": "지출 최소화. 예상치 못한 비용 대비",
                "傷官": "충동 지출 자제. 계약서 꼼꼼히 확인",
                "正官": "공식 수입·급여 협상·승진 기회 포착",
                "比肩": "독립 사업·단독 행동으로 수입 창출",
                "偏印": "투자보다 학습에 집중. 큰 결정 보류",
                "正印": "귀인 활용·자격증으로 수입 향상",
            }
            _action_mi = _MON_ACTION_MC.get(_mss_mi, "흐름 읽고 꾸준히")

            _mon_data.append({
                "월": f"{_yr_mi}년 {_abs_mi+1}월" if _yr_mi != _cy_mc else f"{_abs_mi+1}월",
                "간지": f"{_mcg_mi}{_mjj_mi}",
                "십성": _mss_mi,
                "점수": _score_mi,
                "등급": _grade_mi,
                "col": _col_mi,
                "tc": _tc_mi,
                "행동": _action_mi,
                "is_cur": (_mi == 0),
            })

        # ── 캘린더 UI ────────────────────────────────────────────
        st.markdown(
            f"<div style='font-size:13px;color:#888;margin-bottom:8px'>"
            f"향후 12개월 금전운 타이밍 — 언제 움직이고 언제 지켜야 하는지</div>",
            unsafe_allow_html=True,
        )

        # 4열 그리드
        _rows_mc = [_mon_data[i:i+4] for i in range(0,12,4)]
        for _row_mc in _rows_mc:
            _cols_mc = st.columns(4)
            for _ci, _md in enumerate(_row_mc):
                with _cols_mc[_ci]:
                    _border = "border:2px solid #fff !important;" if _md["is_cur"] else ""
                    st.markdown(
                        f"<div style='background:{_md['col']};border-radius:10px;"
                        f"padding:10px 8px;text-align:center;{_border}'>"
                        f"<div style='font-size:10px;color:#888;'>"
                        f"{'📍 ' if _md['is_cur'] else ''}{_md['월']}</div>"
                        f"<div style='font-size:14px;font-weight:900;color:#fff;'>"
                        f"{_md['간지']}</div>"
                        f"<div style='font-size:11px;color:{_md['tc']};font-weight:700;'>"
                        f"{_md['등급']}</div>"
                        f"<div style='font-size:10px;color:#aaa;margin-top:3px;'>"
                        f"{_md['십성']}</div>"
                        f"<div style='font-size:10px;color:{_md['tc']};margin-top:2px;'>"
                        f"{_md['점수']}점</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        # 최고/최저 달 요약
        _best_mc  = max(_mon_data, key=lambda x: x["점수"])
        _worst_mc = min(_mon_data, key=lambda x: x["점수"])
        st.markdown(
            f"<div style='display:flex;gap:10px;margin-top:10px;flex-wrap:wrap;'>"
            f"<div style='flex:1;background:#1a3d1a;border-radius:10px;padding:12px 14px;'>"
            f"<div style='font-size:11px;color:#7fff7f;font-weight:700;'>"
            f"💰 최고 금전운 달</div>"
            f"<div style='font-size:14px;font-weight:900;color:#fff;'>"
            f"{_best_mc['월']} ({_best_mc['간지']})</div>"
            f"<div style='font-size:11px;color:#aaa;'>{_best_mc['행동']}</div>"
            f"</div>"
            f"<div style='flex:1;background:#3d1a1a;border-radius:10px;padding:12px 14px;'>"
            f"<div style='font-size:11px;color:#ffaaaa;font-weight:700;'>"
            f"⚠️ 최대 주의 달</div>"
            f"<div style='font-size:14px;font-weight:900;color:#fff;'>"
            f"{_worst_mc['월']} ({_worst_mc['간지']})</div>"
            f"<div style='font-size:11px;color:#aaa;'>지출 최소화·현금 보유</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # 이번 달 행동 지침
        _cur_mc = _mon_data[0]
        st.markdown(
            f"<div style='background:#0d1117;border:1.5px solid #d4af3744;"
            f"border-radius:10px;padding:12px 16px;margin-top:8px;'>"
            f"<div style='font-size:12px;font-weight:900;color:#d4af37;'>"
            f"📍 이번 달 ({_cur_mc['월']}) 금전 행동 지침</div>"
            f"<div style='font-size:13px;color:#fff;margin-top:6px;'>"
            f"{_cur_mc['행동']} — {_cur_mc['등급']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    except Exception as _mc_e:
        st.warning(f"⚠️ 금전운 캘린더 오류: {_mc_e}")

    # ── 로컬 엔진 상세 분석 ─────────────
    try:
        _local_out = LocalSajuNarrator.money(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 재물 분석 오류: {_e}")

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")'''

src = src.replace(old1, new1)

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("수정 완료")

import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("문법 OK")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
