# fix_menu1_upgrade.py — 종합사주 콘텐츠 강화
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# ══════════════════════════════════════════
# 수정 1: 5대 지표 뒤에 맞춤 인생 전략 카드 추가
# ══════════════════════════════════════════
old1 = '''    # ── 발동 중인 신살 강조 (세운 지지 기준) ─────────────────'''

new1 = '''    # ── 일간×격국 맞춤 인생 전략 카드 ────────────────────────
    try:
        _ilgan_s = pils[1]["cg"] if len(pils) > 1 else ""
        _ys_s = get_yongshin(pils)
        _yong_s = _ys_s.get("종합_용신",[]) if _ys_s else []
        _gisin_s = _ys_s.get("기신",[]) if _ys_s and isinstance(_ys_s.get("기신"),list) else []
        _gk_s = get_gyeokguk(pils)
        _gkn_s = _gk_s.get("격국명","") if _gk_s else ""
        _sn_s = get_ilgan_strength(_ilgan_s, pils)
        _sn_str = _sn_s.get("신강신약","중화") if _sn_s else "중화"
        _OHN_S = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}

        # 일간별 핵심 전략
        _ILGAN_STRATEGY = {
            "甲":(f"갑목(甲木) 일간인 {name}님은 타고난 선구자입니다. "
                 f"한번 목표를 정하면 끝까지 밀어붙이는 추진력이 가장 큰 무기입니다. "
                 f"단 지나친 고집이 주변과의 마찰을 만드니, "
                 f"'옳다'는 확신이 들어도 타인의 의견을 한 번 더 들어보는 여유를 가지십시오. "
                 f"용신 기운이 강할 때 과감하게 시작하고, 기신 기운일 때는 실력을 쌓으십시오."),
            "乙":(f"을목(乙木) 일간인 {name}님은 어떤 환경에서도 살아남는 불굴의 생존력이 있습니다. "
                 f"겉으로는 부드럽지만 내면은 강인한 외유내강형입니다. "
                 f"정면 돌파보다 상황에 맞게 방향을 바꾸는 유연한 전략이 성공의 열쇠입니다. "
                 f"자신의 의견을 명확하게 표현하는 연습을 꾸준히 하십시오."),
            "丙":(f"병화(丙火) 일간인 {name}님은 태양처럼 어디서든 존재감을 발휘합니다. "
                 f"열정과 추진력, 사교성이 최고의 무기입니다. "
                 f"단 에너지를 한꺼번에 쏟아붓다가 소진되는 패턴이 반복되니, "
                 f"페이스 조절이 장거리 성공의 핵심입니다."),
            "丁":(f"정화(丁火) 일간인 {name}님은 섬세하고 따뜻한 촛불의 기운입니다. "
                 f"헌신적이고 직관력이 뛰어나 주변 사람들에게 깊은 신뢰를 받습니다. "
                 f"자신의 진가를 알아주는 사람과 함께할 때 최고의 성과를 냅니다. "
                 f"자기 가치를 스스로 인정하는 자존감 훈련이 필요합니다."),
            "戊":(f"무토(戊土) 일간인 {name}님은 태산처럼 묵직하고 신뢰받는 존재입니다. "
                 f"한번 맺은 인연과 약속은 끝까지 지키는 의리파입니다. "
                 f"변화를 싫어하는 경향이 있으나, 용신 기운이 올 때 과감하게 움직이면 "
                 f"큰 결실을 얻을 수 있습니다."),
            "己":(f"기토(己土) 일간인 {name}님은 섬세하고 현실적인 판단력이 강점입니다. "
                 f"꼼꼼하고 실속을 중시하며 포용력이 넓습니다. "
                 f"스케일을 키우는 것이 다음 단계의 과제이며, "
                 f"대범한 파트너와 협력할 때 시너지가 극대화됩니다."),
            "庚":(f"경금(庚金) 일간인 {name}님은 냉철하고 결단력이 강한 강철의 기운입니다. "
                 f"한번 마음을 정하면 끝까지 가는 의지력과 원칙주의가 강점입니다. "
                 f"지나친 냉정함이 인간관계에서 '차갑다'는 인상을 줄 수 있으니, "
                 f"감정 표현을 의식적으로 늘리는 것이 대인관계의 비결입니다."),
            "辛":(f"신금(辛金) 일간인 {name}님은 날카롭고 정밀한 보석의 기운입니다. "
                 f"완벽주의적 성향과 높은 심미안이 강점이지만, "
                 f"지나친 예민함이 스스로를 옥죄는 경우가 있습니다. "
                 f"'충분히 좋은' 것을 허용하는 유연함이 삶의 여유를 만들어줍니다."),
            "壬":(f"임수(壬水) 일간인 {name}님은 깊고 지혜로운 대해의 기운입니다. "
                 f"풍부한 통찰력과 유연한 적응력이 어떤 환경에서도 살아남게 합니다. "
                 f"우유부단함이 가장 큰 약점이니, '결정하고 행동하기'를 의식적으로 훈련하십시오. "
                 f"생각을 행동으로 옮기는 속도를 높이면 잠재력이 폭발합니다."),
            "癸":(f"계수(癸水) 일간인 {name}님은 감수성이 풍부하고 적응력이 뛰어납니다. "
                 f"직관력과 공감 능력이 높아 사람들의 마음을 잘 읽습니다. "
                 f"변덕이 심해 지구력이 부족한 경우가 있으니, "
                 f"한 가지에 집중하는 루틴을 만드는 것이 성공의 핵심입니다."),
        }

        _strategy_txt = _ILGAN_STRATEGY.get(_ilgan_s, f"{_ilgan_s}일간의 기운으로 살아가고 있습니다.")
        _yong_str_s = " · ".join([_OHN_S.get(y,"") for y in _yong_s[:2]]) if _yong_s else "분석 중"
        _gisin_str_s = " · ".join([_OHN_S.get(g,"") for g in _gisin_s[:2] if isinstance(g,str)]) if _gisin_s else "없음"

        st.markdown("---")
        st.markdown(
            f"<div style='background:linear-gradient(145deg,#0d0820,#1a1035);"
            f"border-radius:16px;padding:22px 26px;border:2px solid #d4af3744;"
            f"margin-bottom:16px;'>"
            f"<div style='font-size:11px;color:#d4af37;letter-spacing:3px;"
            f"font-weight:900;margin-bottom:12px'>🎯 {name}님의 맞춤 인생 전략</div>"
            f"<div style='font-size:14px;color:#f0e6ff;line-height:2.0;'>"
            f"{_strategy_txt}</div>"
            f"<div style='display:flex;gap:20px;margin-top:14px;flex-wrap:wrap'>"
            f"<div style='background:rgba(255,255,255,0.06);border-radius:10px;"
            f"padding:8px 16px;font-size:12px;color:#7fff7f'>"
            f"✅ 용신: {_yong_str_s}</div>"
            f"<div style='background:rgba(255,255,255,0.06);border-radius:10px;"
            f"padding:8px 16px;font-size:12px;color:#ffaaaa'>"
            f"⚠️ 기신: {_gisin_str_s}</div>"
            f"<div style='background:rgba(255,255,255,0.06);border-radius:10px;"
            f"padding:8px 16px;font-size:12px;color:#aaaaff'>"
            f"📋 격국: {_gkn_s or '분석중'} / {_sn_str}</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass

    # ── 올해 월별 길흉 캘린더 ──────────────────────────────────
    try:
        _cy_cal = datetime.now().year
        _ilgan_cal = pils[1]["cg"] if len(pils) > 1 else ""
        _ys_cal = get_yongshin(pils)
        _yong_cal = _ys_cal.get("종합_용신",[]) if _ys_cal else []
        _gisin_cal= _ys_cal.get("기신",[]) if _ys_cal and isinstance(_ys_cal.get("기신"),list) else []
        _OH_CAL = {"甲":"木","乙":"木","丙":"火","丁":"Fire","戊":"土",
                   "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _OH_CAL2= {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                   "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _MON_CG_BASE = {"甲":"丙","乙":"戊","丙":"庚","丁":"壬","戊":"甲",
                        "己":"丙","庚":"戊","辛":"庚","壬":"壬","癸":"甲"}
        _CG_LIST = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
        _JJ_LIST_M = ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"]
        _start = _MON_CG_BASE.get(_ilgan_cal,"甲")
        _sidx  = _CG_LIST.index(_start) if _start in _CG_LIST else 0

        _cal_rows = []
        for _mi in range(12):
            _mcg = _CG_LIST[(_sidx + _mi) % 10]
            _mjj = _JJ_LIST_M[_mi]
            _mss = TEN_GODS_MATRIX.get(_ilgan_cal,{}).get(_mcg,"-")
            _moh = _OH_CAL2.get(_mcg,"")
            _is_y = _moh in _yong_cal
            _is_g = _moh in _gisin_cal
            _col  = "#1a3d1a" if _is_y else "#3d1a1a" if _is_g else "#1a1a2e"
            _tc   = "#7fff7f" if _is_y else "#ffaaaa" if _is_g else "#aaaaaa"
            _sig  = "🟢" if _is_y else "🔴" if _is_g else "🟡"
            _cal_rows.append(
                f"<div style='background:{_col};border-radius:8px;padding:8px 6px;"
                f"text-align:center;min-width:60px;'>"
                f"<div style='font-size:10px;color:#888;'>{_mi+1}월</div>"
                f"<div style='font-size:13px;font-weight:900;color:#fff;'>{_mcg}{_mjj}</div>"
                f"<div style='font-size:11px;color:{_tc};'>{_sig} {_mss[:2] if len(_mss)>2 else _mss}</div>"
                f"</div>"
            )

        st.markdown("---")
        st.markdown(
            f"<div style='font-size:15px;font-weight:900;color:#d4af37;"
            f"margin-bottom:8px'>📅 {_cy_cal}년 월별 길흉 캘린더</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='display:flex;flex-wrap:wrap;gap:4px;'>"
            + "".join(_cal_rows) +
            f"</div>"
            f"<div style='font-size:11px;color:#888;margin-top:6px;'>"
            f"🟢 용신월 (적극 행동) | 🔴 기신월 (수비) | 🟡 중립월 (꾸준히)</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass

    # ── 발동 중인 신살 강조 (세운 지지 기준) ─────────────────'''

src = src.replace(old1, new1)

# ══════════════════════════════════════════
# 수정 2: 귀인 타이밍 + 주의 시기 추가
# ══════════════════════════════════════════
old2 = '''    except Exception as e:
        _saju_log.warning("[menu1_report] 오류: %s", str(e)[:60])

    # if not api_key and not groq_key:

    # return  # API 없으면 로컬만 출력 후 종료

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    try:'''

new2 = '''    except Exception as e:
        _saju_log.warning("[menu1_report] 오류: %s", str(e)[:60])

    # ── 귀인 타이밍 + 올해 주의 시기 ───────────────────────────
    try:
        _cy_g = datetime.now().year
        _ilgan_g = pils[1]["cg"] if len(pils) > 1 else ""
        _ys_g = get_yongshin(pils)
        _yong_g = _ys_g.get("종합_용신",[]) if _ys_g else []
        _OH_G2 = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _OH_G = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                 "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        # 천을귀인 테이블
        _GUIIN_MAP = {
            "甲":["丑","未"],"乙":["子","申"],"丙":["亥","酉"],
            "丁":["亥","酉"],"戊":["丑","未"],"己":["子","申"],
            "庚":["丑","未"],"辛":["寅","午"],"壬":["卯","巳"],"癸":["卯","巳"],
        }
        _guiin_jjs = _GUIIN_MAP.get(_ilgan_g,[])
        _JJ_MON_MAP = {
            "子":11,"丑":12,"寅":1,"卯":2,"辰":3,"巳":4,
            "午":5,"未":6,"申":7,"酉":8,"戌":9,"亥":10
        }
        _guiin_months = [f"{_JJ_MON_MAP.get(j,0)}월" for j in _guiin_jjs if j in _JJ_MON_MAP]

        # 올해 가장 주의할 달 (기신 + 세운 지지 충)
        _orig_jjs_g = {p.get("jj","") for p in pils}
        _CHUNG_G = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                    "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
        _JJ_LIST_G = ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"]
        _danger_months = []
        _good_months = []
        _CG_LIST_G = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
        _start_g = {"甲":"丙","乙":"戊","丙":"庚","丁":"壬","戊":"甲",
                    "己":"丙","庚":"戊","辛":"庚","壬":"壬","癸":"甲"}.get(_ilgan_g,"甲")
        _sidx_g = _CG_LIST_G.index(_start_g) if _start_g in _CG_LIST_G else 0

        for _mi_g in range(12):
            _mcg_g = _CG_LIST_G[(_sidx_g + _mi_g) % 10]
            _mjj_g = _JJ_LIST_G[_mi_g]
            _moh_g = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                      "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}.get(_mcg_g,"")
            _chung_g = _CHUNG_G.get(_mjj_g,"")
            _has_chung_g = bool(_chung_g and _chung_g in _orig_jjs_g)
            _is_g_g = _moh_g in (_ys_g.get("기신",[]) if _ys_g and isinstance(_ys_g.get("기신"),list) else [])
            _is_y_g = _moh_g in _yong_g
            if _has_chung_g and _is_g_g:
                _danger_months.append(f"**{_mi_g+1}월** (충+기신)")
            elif _is_y_g:
                _good_months.append(f"**{_mi_g+1}월**")

        st.markdown(
            f"<div style='background:#0d1117;border:1.5px solid #d4af3744;"
            f"border-radius:14px;padding:18px 22px;margin:16px 0;'>"
            f"<div style='font-size:13px;font-weight:900;color:#d4af37;"
            f"margin-bottom:12px'>🌟 귀인 타이밍 & 주의 시기</div>"
            f"<div style='display:flex;gap:20px;flex-wrap:wrap;font-size:13px;'>"
            f"<div>"
            f"<div style='color:#7fff7f;font-weight:700;margin-bottom:4px'>"
            f"👼 천을귀인 활성 달</div>"
            f"<div style='color:#ccc;'>{' · '.join(_guiin_months) if _guiin_months else '확인 중'}</div>"
            f"<div style='color:#888;font-size:11px;margin-top:2px'>"
            f"이 달에 만나는 귀인이 인생을 바꿉니다</div>"
            f"</div>"
            f"<div>"
            f"<div style='color:#7fff7f;font-weight:700;margin-bottom:4px'>"
            f"🌟 용신 활성 달</div>"
            f"<div style='color:#ccc;'>{' · '.join(_good_months[:4]) if _good_months else '없음'}</div>"
            f"<div style='color:#888;font-size:11px;margin-top:2px'>"
            f"중요한 일은 이 달에 시작하세요</div>"
            f"</div>"
            f"<div>"
            f"<div style='color:#ffaaaa;font-weight:700;margin-bottom:4px'>"
            f"⚠️ 최대 주의 달</div>"
            f"<div style='color:#ccc;'>{' · '.join(_danger_months[:3]) if _danger_months else '없음'}</div>"
            f"<div style='color:#888;font-size:11px;margin-top:2px'>"
            f"이 달엔 중요 결정 보류하세요</div>"
            f"</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    except Exception:
        pass

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    try:'''

if old1 in src:
    print("✅ 수정 1: 맞춤 인생 전략 카드 추가 완료")
else:
    print("⚠️ 수정 1: 이미 적용되었거나 패턴이 없음")

if old2 in src:
    src = src.replace(old2, new2)
    print("✅ 수정 2: 귀인 타이밍 추가 완료")
else:
    print("⚠️ 수정 2: 이미 적용되었거나 패턴이 없음")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("✅ manse.py 저장 완료")

import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("✅ 문법 검사: OK")
except py_compile.PyCompileError as e:
    print(f"❌ 문법 오류: {e}")
