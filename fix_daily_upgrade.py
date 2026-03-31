# fix_daily_upgrade.py — 일일운세 시간대별 세분화
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

old1 = '''    # -- 길한 시간 (용신 기반) ----------------

    st.markdown(
        '<div class="gold-section" style="margin-top:20px">⏰ 오늘의 길한 시간 (용신 기반)</div>',
        unsafe_allow_html=True,
    )

    ys = get_yongshin(pils)

    y_ohs = ys.get("종합_용신", [])

    OH_HOUR_MAP = {
        "木": [("3~5시", "寅"), ("5~7시", "卯")],
        "火": [("9~11시", "巳"), ("11~13시", "午")],
        "土": [("7~9시", "辰"), ("13~15시", "未")],
        "金": [("15~17시", "申"), ("17~19시", "酉")],
        "水": [("21~23시", "亥"), ("23~1시", "子")],
    }

    good_hours = []

    for oh in y_ohs:
        good_hours.extend(OH_HOUR_MAP.get(oh, []))

    if good_hours:
        tags = "".join([f"<span style='background:#f1f8e9; color:#2e7d32; padding:4px 12px; border-radius:6px; font-size:12px; margin-right:5px'>✅ {t}({jj}시)</span>" for t, jj in good_hours[:3]])

        st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)'''

new1 = '''    # ── 실시간 시간대별 운세 세분화 ────────────────────────────
    st.markdown(
        '<div class="gold-section" style="margin-top:20px">⏰ 지금 이 시간의 운기 — 12시진 실시간</div>',
        unsafe_allow_html=True,
    )
    try:
        _now_h = datetime.now().hour
        _ys_rt = get_yongshin(pils) or {}
        _yong_rt = _ys_rt.get("종합_용신",[])
        _gisin_rt= _ys_rt.get("기신",[]) if isinstance(_ys_rt.get("기신"),list) else []
        _ilgan_rt = pils[1]["cg"] if len(pils)>1 else "甲"
        _OH_RT = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _OH_RT2= {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _OH_RT3= {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}

        # 12시진 → 오행 매핑
        _SHIJIN = [
            (23, 1,  "子", "水", "자시(子時)"),
            (1,  3,  "丑", "土", "축시(丑時)"),
            (3,  5,  "寅", "木", "인시(寅時)"),
            (5,  7,  "卯", "木", "묘시(卯時)"),
            (7,  9,  "辰", "土", "진시(辰時)"),
            (9,  11, "巳", "火", "사시(巳時)"),
            (11, 13, "午", "火", "오시(午時)"),
            (13, 15, "未", "土", "미시(未時)"),
            (15, 17, "申", "金", "신시(申時)"),
            (17, 19, "酉", "金", "유시(酉時)"),
            (19, 21, "戌", "土", "술시(戌時)"),
            (21, 23, "亥", "水", "해시(亥時)"),
        ]
        _cur_shijin = None
        for _sh in _SHIJIN:
            _sh_start, _sh_end = _sh[0], _sh[1]
            if _sh_start > _sh_end:  # 자시 23~1
                if _now_h >= _sh_start or _now_h < _sh_end:
                    _cur_shijin = _sh
                    break
            else:
                if _sh_start <= _now_h < _sh_end:
                    _cur_shijin = _sh
                    break
        if not _cur_shijin:
            _cur_shijin = _SHIJIN[0]

        _cur_jj_rt, _cur_oh_rt, _cur_name_rt = _cur_shijin[2], _cur_shijin[3], _cur_shijin[4]
        _cur_ss_rt = TEN_GODS_MATRIX.get(_ilgan_rt,{}).get(_cur_jj_rt,"-")
        _is_y_rt = _cur_oh_rt in _yong_rt
        _is_g_rt = _cur_oh_rt in _gisin_rt

        # 지금 시간 신호
        if _is_y_rt:
            _rt_bg = "#1a3d1a"; _rt_tc = "#7fff7f"
            _rt_sig = "🟢 지금은 용신 시간! 중요한 행동을 지금 하십시오!"
        elif _is_g_rt:
            _rt_bg = "#3d1a1a"; _rt_tc = "#ffaaaa"
            _rt_sig = "🔴 지금은 기신 시간. 중요한 결정을 잠시 미루십시오."
        else:
            _rt_bg = "#1a1a2e"; _rt_tc = "#aaaaff"
            _rt_sig = "🟡 지금은 중립 시간. 꾸준히 나아가세요."

        # 시진별 행동 가이드
        _SHIJIN_ACTION = {
            "子": "조용한 사색·독서·내일 계획 수립에 최적. 수면 준비를 시작하세요.",
            "丑": "깊은 수면의 시간. 이 시간에 깨어있으면 내일 에너지가 떨어집니다.",
            "寅": "새벽 기도·명상·운동 시작에 최고의 시간. 하루를 여는 에너지.",
            "卯": "아침 루틴·공부 시작·중요 연락하기에 좋은 시간.",
            "辰": "집중 업무 시작·중요 회의 진행에 적합. 아침 식사 꼭 하세요.",
            "巳": "두뇌 회전 최고조. 창의적 업무·발표·영업·면접에 최적.",
            "午": "점심 식사 후 짧은 휴식이 오후 집중력을 높입니다.",
            "未": "오후 집중 업무·정산·서류 처리에 좋습니다.",
            "申": "변화와 활동의 시간. 외부 미팅·협상·수금에 유리.",
            "酉": "마무리의 시간. 오늘 업무를 정리하고 내일을 준비하세요.",
            "戌": "저녁 식사·가족·인간관계에 집중. 중요 연락 마무리.",
            "亥": "독서·학습·내일 계획·명상. 핸드폰은 내려놓고 쉬세요.",
        }
        _action_rt = _SHIJIN_ACTION.get(_cur_jj_rt,"지금 이 시간을 소중히 활용하세요.")

        # 오늘 12시간 타임라인
        _OHN_RT = {"木":"목","火":"화","土":"토","金":"금","水":"수"}
        _tl_rt = '<div style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:12px">'
        for _sh in _SHIJIN:
            _sh_oh = _sh[3]
            _sh_jj = _sh[2]
            _is_cur = (_sh == _cur_shijin)
            _is_y_sh = _sh_oh in _yong_rt
            _is_g_sh = _sh_oh in _gisin_rt
            _sh_bg = "#1a3d1a" if _is_y_sh else "#3d1a1a" if _is_g_sh else "#1a1a2e"
            _sh_tc = "#7fff7f" if _is_y_sh else "#ffaaaa" if _is_g_sh else "#888"
            _sh_border = "border:2px solid #fff !important;" if _is_cur else ""
            _sh_start_h = _sh[0] if _sh[0] < 23 else 23
            _tl_rt += (
                f"<div style='background:{_sh_bg};border-radius:6px;padding:5px 4px;"
                f"text-align:center;min-width:44px;{_sh_border}'>"
                f"<div style='font-size:9px;color:#666'>{_sh_start_h}시</div>"
                f"<div style='font-size:11px;font-weight:900;color:#fff'>{_sh_jj}</div>"
                f"<div style='font-size:9px;color:{_sh_tc}'>{_OHN_RT.get(_sh_oh,'')}</div>"
                f"{'<div style=\"font-size:8px;color:#fff;font-weight:900\">▲NOW</div>' if _is_cur else ''}"
                f"</div>"
            )
        _tl_rt += '</div>'

        st.markdown(
            f"<div style='background:{_rt_bg};border-radius:14px;padding:16px 20px;"
            f"border:2px solid {_rt_tc}55;margin-bottom:10px'>"
            f"<div style='font-size:15px;font-weight:900;color:{_rt_tc};margin-bottom:6px'>"
            f"지금 {_now_h}시 — {_cur_name_rt} [{_cur_oh_rt}/{_OHN_RT.get(_cur_oh_rt,'')}]</div>"
            f"<div style='font-size:13px;color:#fff;font-weight:700;margin-bottom:8px'>"
            f"{_rt_sig}</div>"
            f"<div style='font-size:12px;color:#ccc;'>{_action_rt}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_tl_rt, unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:11px;color:#888;margin-bottom:12px'>"
            "🟢 용신 시간 | 🔴 기신 시간 | 🟡 중립 | ▲NOW 현재 시간</div>",
            unsafe_allow_html=True,
        )

        # 오늘 남은 시간 중 용신 시간 예고
        _remain_yong = []
        for _sh in _SHIJIN:
            if _sh[3] in _yong_rt and _sh[0] > _now_h:
                _remain_yong.append(f"{_sh[0]}시({_sh[4]})")
        if _remain_yong:
            st.markdown(
                f"<div style='background:#1a3d1a;border-radius:10px;padding:10px 14px;"
                f"font-size:12px;color:#7fff7f;margin-bottom:8px'>"
                f"⏳ 오늘 남은 용신 시간: {' / '.join(_remain_yong[:3])}<br>"
                f"<span style='color:#aaa;font-size:11px'>"
                f"이 시간에 중요한 행동·결정·연락을 하십시오!</span></div>",
                unsafe_allow_html=True,
            )
    except Exception as _rt_e:
        pass

    # ── 기존 길한 시간 태그 (호환) ──────────────────────────────
    ys = get_yongshin(pils)
    y_ohs = ys.get("종합_용신", [])
    OH_HOUR_MAP = {
        "木": [("3~5시", "寅"), ("5~7시", "卯")],
        "火": [("9~11시", "巳"), ("11~13시", "午")],
        "土": [("7~9시", "辰"), ("13~15시", "未")],
        "金": [("15~17시", "申"), ("17~19시", "酉")],
        "水": [("21~23시", "亥"), ("23~1시", "子")],
    }
    good_hours = []
    for oh in y_ohs:
        good_hours.extend(OH_HOUR_MAP.get(oh, []))'''

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
