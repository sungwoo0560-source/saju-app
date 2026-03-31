# fix_upgrade1.py — 과거분석/대운흐름/토정비결 콘텐츠 강화
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()

# ══════════════════════════════════════════
# 수정 1: past_analysis — 실제 사건 카드 + 인생 결정적 순간 추가
# ══════════════════════════════════════════
old1 = '''        lines = []
        _cur_age_p = cur_year - birth_year + 1
        lines.append(f"## 🎯 {name}님의 인생 흐름 — 지나온 시간의 기록")
        lines.append(
            f"{name}님은 {birth_year}년에 태어나 현재 {_cur_age_p}세이십니다. "
            f"지금까지의 삶을 10년 단위 대운의 흐름으로 돌아보겠습니다. "
            f"어떤 시기가 나에게 황금기였고, 어떤 시기가 수비기였는지 "
            f"팔자 속에서 찾아보겠습니다.\\n"
        )'''

new1 = '''        lines = []
        _cur_age_p = cur_year - birth_year + 1
        lines.append(f"## 🎯 {name}님의 인생 흐름 — 지나온 시간의 기록")
        lines.append(
            f"{name}님은 {birth_year}년에 태어나 현재 {_cur_age_p}세이십니다. "
            f"지금까지의 삶을 10년 단위 대운의 흐름으로 돌아보겠습니다. "
            f"어떤 시기가 나에게 황금기였고, 어떤 시기가 수비기였는지 "
            f"팔자 속에서 찾아보겠습니다.\\n"
        )

        # ── 인생 결정적 순간 — 충/합/세운 교차 TOP 3 ──────────────────
        try:
            _JJ_CHUNG_PA = {
                "子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳",
            }
            _orig_jjs_pa = {p.get("jj","") for p in pils}
            _orig_cgs_pa = {p.get("cg","") for p in pils}
            _CG_CHUNG_PA = {
                "甲":"庚","庚":"甲","乙":"辛","辛":"乙",
                "丙":"壬","壬":"丙","丁":"癸","癸":"丁",
            }
            _SS_EVENT_PA = {
                "偏財":"💰 재물 기회·이성 인연·사업 변동",
                "正財":"💰 안정 수입·결혼·재물 정착",
                "食神":"🌟 창업·재능 개화·임신·복록",
                "傷官":"⚡ 이직·갈등·창의적 도전·구설",
                "偏官":"⚠️ 사고·건강 이상·직장 변동·관재",
                "正官":"🏆 승진·명예·결혼·공식 인정",
                "劫財":"🔴 재물 손실·배신·경쟁",
                "比肩":"💪 독립·창업 시도·이사",
                "偏印":"📚 이동·이직·학업 전환",
                "正印":"📖 자격취득·귀인 만남",
            }
            _decisive_moments = []
            for _yr_pa in range(birth_year + 10, cur_year + 1):
                try:
                    _sw_pa = get_yearly_luck(pils, _yr_pa) or {}
                    _jj_pa = _sw_pa.get("jj","")
                    _cg_pa = _sw_pa.get("세운","")[:1] if _sw_pa.get("세운") else ""
                    _ss_pa = _sw_pa.get("십성_천간","")
                    _gh_pa = _sw_pa.get("길흉","평")
                    _oh_pa = _OH.get(_cg_pa,"") if _cg_pa else ""
                    _is_y = _oh_pa in yongshin
                    _is_g = _oh_pa in gisin
                    # 충 감지
                    _ct = _JJ_CHUNG_PA.get(_jj_pa,"")
                    _has_chung = bool(_ct and _ct in _orig_jjs_pa)
                    # 천간충 감지
                    _cct = _CG_CHUNG_PA.get(_cg_pa,"")
                    _has_cg_chung = bool(_cct and _cct in _orig_cgs_pa)
                    _age_pa = _yr_pa - birth_year + 1
                    _event_hint = _SS_EVENT_PA.get(_ss_pa,"")
                    if _has_chung and _has_cg_chung:
                        _decisive_moments.append(
                            f"**{_yr_pa}년({_age_pa}세)** 💥 천간+지지 동시 충(沖) — "
                            f"인생 최대 변곡점. {_event_hint}"
                        )
                    elif _has_chung and _is_g:
                        _decisive_moments.append(
                            f"**{_yr_pa}년({_age_pa}세)** 💥 충(沖)+기신 — "
                            f"힘든 변화. {_event_hint}"
                        )
                    elif _has_chung and _is_y:
                        _decisive_moments.append(
                            f"**{_yr_pa}년({_age_pa}세)** 💥 충(沖)+용신 — "
                            f"변화 속 기회. {_event_hint}"
                        )
                    elif _is_y and _gh_pa in ("길","+"):
                        _decisive_moments.append(
                            f"**{_yr_pa}년({_age_pa}세)** 🌟 황금 세운 — {_event_hint}"
                        )
                    elif _is_g and _gh_pa in ("흉","-"):
                        _decisive_moments.append(
                            f"**{_yr_pa}년({_age_pa}세)** ⚠️ 흉 세운 — {_event_hint}"
                        )
                except Exception:
                    pass
            if _decisive_moments:
                lines.append("### 🔍 인생 결정적 순간 TOP — 사주가 가장 크게 움직인 해")
                lines.append(
                    f"아래는 {name}님의 사주 원국과 세운이 가장 강하게 충돌하거나 "
                    f"결합했던 해입니다. 이 시기에 중요한 사건이 있었는지 확인해 보십시오."
                )
                for _dm in _decisive_moments[:5]:
                    lines.append(f"- {_dm}")
                lines.append("")
        except Exception:
            pass'''

src = src.replace(old1, new1)

# ══════════════════════════════════════════
# 수정 2: lifeline — 대운별 스토리 서술 강화
# ══════════════════════════════════════════
old2 = '''    def lifeline(pils, name, birth_year, gender):'''

# lifeline 마지막 return 직전에 대운 스토리 추가
# lifeline 마지막 부분 찾기
import re
m = re.search(r'(    def lifeline.*?)(        return "\\\\n"\.join\(lines\))', src, re.DOTALL)
if m:
    old_return2 = '        return "\\n".join(lines)'
    new_return2 = '''        # ── 인생 전체 스토리 요약 ─────────────────────────────────
        try:
            _past_golds = [d for d in b.get("dw_list",[])
                          if _OH.get(d.get("cg",""),"") in b.get("yongshin",[])
                          and d.get("종료연도",0) < cur_year]
            _future_golds = [d for d in b.get("dw_list",[])
                            if _OH.get(d.get("cg",""),"") in b.get("yongshin",[])
                            and d.get("시작연도",9999) > cur_year]
            _cur_dw_lf = next((d for d in b.get("dw_list",[])
                              if d.get("시작연도",0) <= cur_year <= d.get("종료연도",9999)), None)
            _OHN_LF = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
            _yong_lf = b.get("yongshin",[])
            _gisin_lf = b.get("gisin",[])

            lines.append("---")
            lines.append(f"### 📖 {name}님의 인생 대서사시")

            _story_intro = (
                f"{name}님의 인생은 **{b.get('sn','중화')}** 사주로, "
                f"용신은 **{'·'.join(_OHN_LF.get(y,'') for y in _yong_lf[:2])}** 오행입니다. "
                f"이 오행이 강하게 흐르는 대운과 세운에서 {name}님의 인생이 꽃을 피웁니다.\\n"
            )
            lines.append(_story_intro)

            if _past_golds:
                _pg_str = " → ".join(f"{d.get('str','')}대운({d.get('시작연도','')}~{d.get('종료연도','')})" for d in _past_golds[-2:])
                lines.append(
                    f"**✅ 지나온 황금기**: {_pg_str}\\n"
                    f"이 시기에 시작한 일들은 지금도 {name}님의 삶을 지탱하는 자산이 되고 있습니다."
                )

            if _cur_dw_lf:
                _cur_oh_lf = _OH.get(_cur_dw_lf.get("cg",""),"")
                _cur_is_gold = _cur_oh_lf in _yong_lf
                _cur_is_bad  = _cur_oh_lf in _gisin_lf
                _remain_lf   = _cur_dw_lf.get("종료연도",0) - cur_year
                _cur_msg = (
                    f"🌟 **지금은 황금기 대운입니다!** {_remain_lf}년이 남았습니다. "
                    f"지금 움직이면 반드시 결실이 따릅니다."
                    if _cur_is_gold else
                    f"⚠️ **지금은 수비기 대운입니다.** {_remain_lf}년이 남았습니다. "
                    f"무리한 확장보다 내실을 다지는 것이 현명합니다."
                    if _cur_is_bad else
                    f"🟡 **지금은 중립 대운입니다.** {_remain_lf}년이 남았습니다. "
                    f"꾸준히 준비하면 다음 황금기에 빛을 발합니다."
                )
                lines.append(f"\\n**📍 현재 ({cur_year}년)**: {_cur_msg}")

            if _future_golds:
                _fg = _future_golds[0]
                _wait = _fg.get("시작연도",0) - cur_year
                lines.append(
                    f"\\n**🔮 다음 황금기**: {_fg.get('str','')}대운 "
                    f"({_fg.get('시작연도','')}~{_fg.get('종료연도','')}년) — "
                    f"앞으로 **{_wait}년 후** 찾아옵니다. 지금부터 준비하십시오!"
                )
            lines.append("")
        except Exception:
            pass

        return "\\n".join(lines)'''

    src = src.replace('        return "\\n".join(lines)\n\n    @staticmethod\n    def past_analysis',
                      new_return2 + '\n\n    @staticmethod\n    def past_analysis', 1)
    print("lifeline 스토리 추가")

# ══════════════════════════════════════════
# 수정 3: saju_interpreter.py — 토정비결 전용 메서드 추가
# ══════════════════════════════════════════
# quick_answer 뒤에 tojeong 메서드 추가
old3 = '''    @staticmethod
    def get_gongmang(pils):'''

new3 = '''    @staticmethod
    def tojeong(pils, name, birth_year, gender):
        """📜 토정비결 — 개인화 사주 기반 신년운세"""
        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)
        if not b:
            return "## ⚠️ 토정비결을 불러오지 못했습니다."

        cur_year = b.get("cur_year", datetime.now().year)
        yongshin = b.get("yongshin", [])
        gisin    = b.get("gisin",    [])
        ilgan    = b.get("ilgan",    "")
        sn       = b.get("sn",       "중화")
        gyeok    = b.get("gyeok_name","")
        OHN      = b.get("OHN",      {})
        age      = cur_year - birth_year + 1

        _OH = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
               "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}

        sw = get_yearly_luck(pils, cur_year) or {}
        sw_ss  = sw.get("십성_천간","")
        sw_gh  = sw.get("길흉","평")
        sw_gan = sw.get("세운","")
        sw_oh  = _OH.get(sw_gan[:1],"") if sw_gan else ""
        is_yong = sw_oh in yongshin
        is_gisin= sw_oh in gisin

        lines = []
        lines.append(f"## 📜 {name}님의 {cur_year}년 토정비결")
        lines.append(
            f"**{birth_year}년생 {age}세** | 일간: {ilgan} | 격국: {gyeok or '분석중'} | {sn}\\n"
        )

        # ── 총운 판정 ──────────────────────────────────────────────
        _GH_KR = {"길":"✅ 길(吉)","+":" ✅ 길(吉)","평":"⚖️ 평(平)","흉":"⚠️ 흉(凶)","-":"⚠️ 흉(凶)"}
        _sig = ("🟢 황금기 — 적극 공세의 해" if is_yong else
                "🔴 주의기 — 수비 전략의 해" if is_gisin else
                "🟡 중립 — 내실 다지기의 해")

        lines.append(f"### 🌟 {cur_year}년 총운")
        lines.append(
            f"올해 세운 **{sw_gan}({sw_ss})** | 길흉: {_GH_KR.get(sw_gh,sw_gh)} | {_sig}\\n"
        )

        _TJ_TOTAL = {
            "偏財":(f"올해는 재물과 변화의 기운이 강하게 흐르는 해입니다. "
                   f"사업·투자 기회가 찾아오고 이성 인연도 활발합니다. "
                   f"과감한 도전이 결실로 이어지지만, 충동적 투자는 반드시 피해야 합니다. "
                   f"들어오는 만큼 나가는 구조이니, 수입의 30% 이상은 반드시 지켜내십시오."),
            "正財":(f"올해는 착실히 쌓아가는 재물의 해입니다. "
                   f"성실한 노력이 실질적인 수입과 자산으로 돌아옵니다. "
                   f"투기보다 저축·부동산·안전 투자에 집중하면 연말에 뿌듯한 결실을 봅니다. "
                   f"결혼·계약 등 중요한 약속을 맺기에도 좋은 해입니다."),
            "食神":(f"올해는 재능과 복록이 꽃피는 해입니다. "
                   f"좋아하는 일을 하면 자연스럽게 수입이 따라오는 흐름입니다. "
                   f"창업·자격 취득·새 프로젝트 시작에 최적의 해이며, "
                   f"건강도 좋고 인간관계도 풍요로운 복된 해입니다."),
            "傷官":(f"올해는 창의성이 폭발하지만 마찰도 많은 해입니다. "
                   f"윗사람·상사·고객과의 언행 충돌에 각별히 주의하십시오. "
                   f"독창적인 아이디어와 기술은 빛나지만, 그 표현 방식이 관건입니다. "
                   f"계약 시 세부 조건을 꼼꼼히 확인하고 서명하십시오."),
            "偏官":(f"올해는 긴장과 변동이 따르는 해입니다. "
                   f"직장 변동·건강 이상·사고·관재 등 예상치 못한 변수가 생길 수 있습니다. "
                   f"건강 정기검진을 반드시 받고, 무리한 확장이나 새 사업 시작은 자제하십시오. "
                   f"이 시기의 고난은 다음 황금기를 위한 연단의 과정입니다."),
            "正官":(f"올해는 명예와 인정이 따르는 해입니다. "
                   f"조직 내 승진·공식 인정·수상 등 사회적 지위가 상승하는 기운입니다. "
                   f"원칙과 책임을 다하면 반드시 보답이 옵니다. "
                   f"결혼·공식 계약 등 인생의 중요한 이정표를 세우기에 좋습니다."),
            "劫財":(f"올해는 재물 손실과 경쟁이 따르는 해입니다. "
                   f"투자·보증·동업은 반드시 자제하고, 현금 보유를 늘리십시오. "
                   f"가장 믿었던 사람에게 실망하거나 배신당하는 상황이 생길 수 있으니, "
                   f"금전 거래에서 문서를 반드시 남기십시오."),
            "比肩":(f"올해는 독립심이 강해지고 경쟁이 치열해지는 해입니다. "
                   f"동업보다 단독 행동이 유리하며, 자신의 힘으로 무언가를 이루려는 의지가 강합니다. "
                   f"경쟁에서 이기려 하기보다 자신만의 길을 묵묵히 걷는 것이 현명합니다."),
            "偏印":(f"올해는 변화와 이동이 잦은 해입니다. "
                   f"이사·이직·전공 변경 등 환경의 변화가 예상됩니다. "
                   f"큰 결정은 신중하게, 새로운 분야의 학습에는 매우 유리한 해입니다. "
                   f"계획이 자주 바뀌더라도 방향성을 잃지 마십시오."),
            "正印":(f"올해는 학업과 자격 취득에 최적의 해입니다. "
                   f"시험·진학·자격증·연구 등 배움에 집중하면 반드시 결실이 옵니다. "
                   f"좋은 스승·귀인과의 만남이 기대되며, "
                   f"어머니·후원자와의 인연도 돈독해지는 해입니다."),
        }
        lines.append(_TJ_TOTAL.get(sw_ss, f"올해 {sw_ss} 기운의 해입니다. 흐름을 잘 읽고 유연하게 대응하십시오."))
        lines.append("")

        # ── 분야별 운세 ────────────────────────────────────────────
        lines.append("### 📊 분야별 운세")
        _TJ_FIELD = {
            "偏財": {"재물":"💰 큰 기회 — 적극적으로 움직이면 수입이 늘어납니다",
                     "직업":"사업·영업·무역·투자 분야 기회",
                     "연애":"이성 인연 활발 — 새로운 만남 가능성 높음",
                     "건강":"과로 주의. 움직임이 많으니 사고·교통 조심"},
            "正財": {"재물":"💰 안정 수입 — 저축과 부동산에 집중",
                     "직업":"조직 내 안정적 성과. 계약·정산 유리",
                     "연애":"결혼 인연 강화. 안정적 관계 지속",
                     "건강":"소화기·위장 건강 주의"},
            "食神": {"재물":"💰 재능이 수입으로 — 부업·창작 활성화",
                     "직업":"전문성 인정. 자격 취득 유리",
                     "연애":"자연스러운 만남. 임신·출산 기운",
                     "건강":"전반적으로 건강. 과식만 주의"},
            "傷官": {"재물":"⚠️ 수입 기복 — 충동 지출 조심",
                     "직업":"이직·전직 기운. 윗사람 마찰 주의",
                     "연애":"연애 갈등·이별 주의. 말 조심",
                     "건강":"신경계·스트레스 주의"},
            "偏官": {"재물":"⚠️ 지출 증가 — 큰 투자 금지",
                     "직업":"직장 변동·압박. 건강 이상 주의",
                     "연애":"관계 긴장. 상대방 강요·압박 주의",
                     "건강":"사고·수술·관재 주의. 정기검진 필수"},
            "正官": {"재물":"💰 안정 수입. 공식 계약 유리",
                     "직업":"승진·명예·공식 인정 기운",
                     "연애":"결혼·공식 관계 진전 기운",
                     "건강":"전반적 양호. 과로만 주의"},
            "劫財": {"재물":"🔴 손재 주의 — 투자·보증 금지",
                     "직업":"경쟁 치열. 동업 갈등 주의",
                     "연애":"제3자 개입 주의. 신뢰 위기",
                     "건강":"갑작스러운 건강 이상 주의"},
            "比肩": {"재물":"⚠️ 재물 기복 — 경쟁으로 인한 손실",
                     "직업":"독립·단독 행동 유리",
                     "연애":"자기 주장 강해져 갈등. 배려 필요",
                     "건강":"전반적 양호. 과로 주의"},
            "偏印": {"재물":"⚠️ 투자 변동 — 신중한 판단",
                     "직업":"이직·이동·학업 전환 기운",
                     "연애":"변화로 인한 관계 흔들림",
                     "건강":"신경계·불면·피로 주의"},
            "正印": {"재물":"💰 안정적 수입. 자격으로 수익 증가",
                     "직업":"학업·연구·자격증 취득 최적",
                     "연애":"인연 만남. 귀인 등장",
                     "건강":"전반적 양호. 어머니 건강 챙기기"},
        }
        _fields = _TJ_FIELD.get(sw_ss, {})
        for _fk, _fv in _fields.items():
            lines.append(f"- **{_fk}**: {_fv}")
        lines.append("")

        # ── 월별 신수 요약 ─────────────────────────────────────────
        lines.append("### 📅 월별 신수 — 12달 흐름")
        _JJ_LIST = ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"]
        _MON_NAMES = ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"]
        _ILGAN_MON_START = {
            "甲":"丙","乙":"戊","丙":"庚","丁":"壬","戊":"甲",
            "己":"丙","庚":"戊","辛":"庚","壬":"壬","癸":"甲",
        }
        _MON_CG_LIST = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
        _start_cg = _ILGAN_MON_START.get(ilgan,"甲")
        _start_idx = _MON_CG_LIST.index(_start_cg) if _start_cg in _MON_CG_LIST else 0
        _SS_SHORT = {
            "食神":"🌟 좋음","傷官":"⚡ 주의","偏財":"💰 재물","正財":"💰 안정",
            "偏官":"⚠️ 조심","正官":"🏆 명예","劫財":"🔴 손재","比肩":"💪 독립",
            "偏印":"📚 변화","正印":"📖 귀인",
        }
        for _mi, (_mon_name, _mon_jj) in enumerate(zip(_MON_NAMES, _JJ_LIST)):
            _mon_cg_idx = (_start_idx + _mi) % 10
            _mon_cg = _MON_CG_LIST[_mon_cg_idx]
            _mon_ss = TEN_GODS_MATRIX.get(ilgan,{}).get(_mon_cg,"-")
            _mon_oh = _OH.get(_mon_cg,"")
            _is_y_m = _mon_oh in yongshin
            _is_g_m = _mon_oh in gisin
            _mon_sig = "🟢" if _is_y_m else "🔴" if _is_g_m else "🟡"
            _ss_short = _SS_SHORT.get(_mon_ss, _mon_ss)
            lines.append(f"- **{_mon_name}** {_mon_sig} [{_mon_cg}{_mon_jj}] {_ss_short}")
        lines.append("")

        # ── 올해 핵심 처방 ─────────────────────────────────────────
        lines.append("### 💊 올해 핵심 처방")
        _OHN_TJ = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
        _OH_RX_TJ = {
            "木":"동쪽 방향 활용, 초록색 착용, 새벽 산책, 나무·식물 가까이 두기",
            "火":"남쪽 방향 활용, 붉은색 착용, 사교 활동 늘리기, 햇빛 쬐기",
            "土":"중앙·황토색 활용, 규칙적 생활, 황색 계열 음식, 약속 지키기",
            "金":"서쪽 방향 활용, 흰색·금속 소품, 원칙 세우기",
            "水":"북쪽 방향 활용, 검은색 착용, 독서·명상, 물가 산책",
        }
        if yongshin:
            _y1 = yongshin[0]
            lines.append(f"✅ **용신 {_OHN_TJ.get(_y1,'')} 강화**: {_OH_RX_TJ.get(_y1,'')}")
        if gisin:
            _g1 = gisin[0] if isinstance(gisin[0],str) else ""
            if _g1:
                lines.append(f"⚠️ **기신 {_OHN_TJ.get(_g1,'')} 차단**: 해당 색상·방향 과도한 사용 자제")
        lines.append("")
        lines.append(
            f"*{name}님, {cur_year}년 한 해도 사주의 흐름을 읽고 "
            f"나아갈 때와 물러설 때를 현명하게 판단하여 "
            f"뜻하는 바를 이루시기를 바랍니다.*"
        )

        return "\\n".join(lines)

    @staticmethod
    def get_gongmang(pils):'''

src = src.replace(old3, new3)

with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 수정 완료")

# ── 토정비결 탭 연결 ──
with open("manse.py", encoding="utf-8") as f:
    src_m = f.read()

old_tj = '''def menu_tojeong(pils, name, birth_year, gender):'''
# menu_tojeong 시작 후 LocalSajuNarrator.tojeong 호출 추가
import re
m_tj = re.search(r'def menu_tojeong\(pils, name, birth_year, gender\):.*?(?=\ndef )', src_m, re.DOTALL)
if m_tj:
    old_tj_body = m_tj.group()
    if 'LocalSajuNarrator.tojeong' not in old_tj_body:
        # 기존 내용 앞에 tojeong 메서드 출력 추가
        new_tj_insert = '''def menu_tojeong(pils, name, birth_year, gender):
    """📜 토정비결 — 개인화 신년운세"""
    # ── 개인화 토정비결 ──────────────────────────────────────
    try:
        _tj_out = LocalSajuNarrator.tojeong(pils, name, birth_year, gender)
        if _tj_out:
            st.markdown(_tj_out, unsafe_allow_html=True)
    except Exception as _te:
        st.warning(f"⚠️ 토정비결 오류: {_te}")
    st.markdown("---")
'''
        src_m = src_m.replace('def menu_tojeong(pils, name, birth_year, gender):\n', new_tj_insert)
        print("토정비결 탭 LocalSajuNarrator.tojeong 연결")

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src_m)
print("manse.py 수정 완료")

# ── 문법 검사 ──
import py_compile
print("\n=== 최종 문법 검사 ===")
for fname in ["saju_interpreter.py","manse.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"  NG: {fname} → {str(e)[:100]}")