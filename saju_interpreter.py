# -*- coding: utf-8 -*-
"""
saju_interpreter.py - 사주 해석 엔진
LocalSajuNarrator, detect_structure, get_gyeokguk, get_yongshin,
get_yukjin, get_special_stars, get_ohang_health_info,
get_crossing_interpretation, get_relationship_reading, get_health_reading,
HanjaSafeDict, _nar_* 함수들, build_rich_narrative 포함
"""
import streamlit as st
try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False
import json
import os
from datetime import date, datetime, timedelta
import random
import re
import logging as _logging
from saju_data import *
from saju_data import (
    _JJ_HOUR_FULL, _JJ_HOUR_SHORT, _LUNAR_DATA, _SIT, _LOTTO_SS,
    _JEOLGI_BASE, _AI_SANDBOX_HEADER, _SS_DAILY_DEEP,
    _UNSUNG_DESC, _EMOJI_MAP, _SYMBOL_MAP, _DO_LIST,
    PA_SAL_PAIRS, PA_SAL_DESC, HAE_SAL_PAIRS, HAE_SAL_DESC,
    GOEGANG_ILJU, GOEGANG_DESC,
    HAKDANG_GWIIN, HAKDANG_DESC,
    AMROK_JJ, AMROK_DESC,
    GEUNMYO_HWASIL,
)
from saju_sinsal import *
from saju_engine import *

_saju_log = _logging.getLogger("saju")


def clean_hanja(text):
    """괄호 안 한글 독음 제거 유틸 (예: '식신(食神)' → '식신')"""
    if not text:
        return ""
    return re.sub(r"\(.*?\)", "", text).strip()


def _get_yongshin_match(dw_cg_ss, yongshin_ohs, ilgan_oh):
    """대운/세운 십성이 용신 오행과 맞는지 판단 → 'yong' | 'normal'"""
    GEN   = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    CTRL  = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    BIRTH_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    SS_TO_OH = {
        "비견": ilgan_oh,         "劫財": ilgan_oh,
        "겁재": ilgan_oh,         "比肩": ilgan_oh,
        "식신": GEN.get(ilgan_oh, ""),   "食神": GEN.get(ilgan_oh, ""),
        "상관": GEN.get(ilgan_oh, ""),   "傷官": GEN.get(ilgan_oh, ""),
        "편재": CTRL.get(ilgan_oh, ""),  "偏財": CTRL.get(ilgan_oh, ""),
        "정재": CTRL.get(ilgan_oh, ""),  "正財": CTRL.get(ilgan_oh, ""),
        "편관": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "정관": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "偏官": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "正官": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "편인": BIRTH_R.get(ilgan_oh, ""), "偏印": BIRTH_R.get(ilgan_oh, ""),
        "정인": BIRTH_R.get(ilgan_oh, ""), "正印": BIRTH_R.get(ilgan_oh, ""),
    }
    dw_oh = SS_TO_OH.get(dw_cg_ss, "")
    return "yong" if dw_oh in yongshin_ohs else "normal"


# ── GYEOKGUK_NARRATIVE & STRENGTH_NARRATIVE ──
# --------------------------------------------------

# 서술형 대형 내러티브 생성기

# --------------------------------------------------


GYEOKGUK_NARRATIVE = {
    "정관격": "정관격은 사회적 규범과 질서를 중시하는 귀격(貴格)입니다. 이 격국을 가진 분은 법과 원칙 안에서 정당한 방법으로 높은 자리에 오르는 운명입니다. 성실함과 신뢰가 최대 무기이며, 꾸준히 실력을 쌓다 보면 반드시 인정받는 날이 옵니다. 직장 조직에서 빛나는 운으로, 공무원/교사/법조인/관리직이 잘 맞습니다. 다만 자신의 원칙을 지나치게 고집하면 주변과 마찰이 생기니 유연성을 함께 갖추어야 합니다.",
    "편관격": "편관격은 칠살격(七殺格)이라고도 하며, 강렬한 도전과 시련 속에서 성장하는 운명입니다. 어려움이 올수록 더욱 강해지는 역경의 강자입니다. 군인/경찰/의사/운동선수처럼 극한의 상황을 이겨내는 직업에서 탁월한 능력을 발휘합니다. 칠살이 잘 제화(制化)되면 최고의 성공을 이루는 대귀격이 됩니다. 관리되지 않은 칠살은 충동과 과격함으로 나타날 수 있으니 감정 조절이 중요합니다.",
    "정재격": "정재격은 성실하고 꾸준하게 재물을 쌓아가는 안정형 격국입니다. 한탕을 노리기보다 묵묵히 일하고 저축하여 결국 부를 이루는 타입입니다. 금융/부동산/유통/회계 분야에서 두각을 나타내며, 인생 후반에 더욱 빛나는 운명입니다. 이 격국은 배우자 인연이 좋아 가정이 안정적이며, 파트너의 내조가 큰 힘이 됩니다. 지나친 소심함으로 기회를 놓치지 않도록 용기 있는 결단이 필요한 순간도 있습니다.",
    "편재격": "편재격은 활동적이고 대담한 재물 운의 격국입니다. 사업/투자/무역처럼 움직임이 큰 분야에서 재물이 들어옵니다. 한자리에 머물기보다 넓은 세계를 돌아다니며 기회를 만드는 타입입니다. 기복이 있지만 그만큼 크게 버는 운도 있습니다. 아버지와의 인연이 인생에 큰 영향을 미칩니다. 재물이 들어온 만큼 나가기도 하므로, 수입의 일정 부분은 반드시 안전한 곳에 묶어두는 습관이 중요합니다.",
    "식신격": "식신격은 하늘이 내리신 복록의 격국입니다. 타고난 재능과 끼가 있어 그것을 표현하는 것만으로도 재물과 인복이 따라옵니다. 먹는 것을 즐기고 생활의 여유를 즐기며, 주변에 즐거움을 주는 사람입니다. 예술/요리/교육/서비스/창작 분야에서 두각을 나타냅니다. 건강하고 장수하는 운도 있습니다. 다만 너무 편안함을 추구하다 보면 도전 의식이 부족해질 수 있습니다.",
    "상관격": "상관격은 창의력과 표현 능력이 탁월한 격국입니다. 기존 질서에 얽매이지 않고 새로운 것을 만들어내는 혁신가 기질이 있습니다. 예술/문학/음악/마케팅/IT 분야에서 독보적인 능력을 발휘합니다. 직장 조직보다는 독립적인 활동이 더 잘 맞습니다. 상관견관(傷官見官)이 있으면 직장 상사나 권위자와 갈등이 생기기 쉬우니 언행에 각별히 주의해야 합니다.",
    "편인격": "편인격은 직관과 영감이 남다른 격국입니다. 특수한 기술/학문/예술에서 독보적인 경지에 오르는 운명입니다. 철학/종교/심리/의술/역학 등 남들이 쉽게 접근하지 못하는 전문 분야에서 두각을 나타냅니다. 고독을 즐기며 혼자만의 깊은 연구에서 에너지를 얻습니다. 도식(倒食)이 형성되면 직업 변동이 잦을 수 있으니 한 분야에 집중하는 것이 좋습니다.",
    "정인격": "정인격은 학문/교육/명예의 귀격입니다. 배움에 대한 열정이 넘치고, 지식을 쌓을수록 더 높은 곳으로 올라가는 운명입니다. 교수/의사/법관/연구원처럼 학문과 자격이 기반이 되는 직업에서 최고의 성과를 냅니다. 어머니와의 관계가 인생에 큰 영향을 미칩니다. 지식이 곧 재물이 되는 사주이므로 평생 배움을 멈추지 않는 것이 성공의 비결입니다.",
    "비견격": "비견격은 독립심과 자존감이 강한 격국입니다. 남 밑에서 지시받기보다 자신만의 영역을 구축하는 자영업/창업이 잘 맞습니다. 형제나 동료와의 경쟁이 인생의 주요한 테마가 되며, 이를 통해 단련됩니다. 뚝심과 의지가 강해 어떤 어려움도 정면 돌파합니다. 재물이 모이기 어려울 수 있으니 지출 관리가 특히 중요합니다.",
    "겁재격": "겁재격은 승부사 기질의 격국입니다. 경쟁을 즐기고 도전적인 상황에서 오히려 에너지가 솟습니다. 스포츠/영업/투자/법조 분야에서 강합니다. 재물의 기복이 매우 크며, 크게 벌었다가도 한순간에 잃을 수 있는 운명이므로 안전자산 확보가 필수입니다. 주변 사람들에게 베푸는 것을 좋아하지만, 그로 인해 재물이 새는 경우도 많습니다.",
}

STRENGTH_NARRATIVE = {
    "신강(身强)": """신강 사주는 일간의 기운이 강한 사주입니다. 체력과 정신력이 뛰어나고, 어떤 역경도 정면으로 돌파하는 힘이 있습니다. 그러나 기운이 너무 강하면 오히려 재물과 관운이 억눌릴 수 있습니다. 신강한 분에게는 재성(財星)과 관살(官殺) 운이 올 때 크게 성공할 기회가 생깁니다. 자신감이 넘치는 만큼 때로는 독단적으로 보일 수 있으니, 타인의 의견을 경청하는 습관을 기르는 것이 중요합니다. 신강 사주는 스스로 만들어가는 인생입니다. 남을 기다리기보다 먼저 움직여야 기회가 옵니다.""",
    "신약(身弱)": """신약 사주는 일간의 기운이 약한 사주입니다. 체력과 에너지 관리가 인생의 핵심 과제입니다. 그러나 신약이 꼭 나쁜 것은 아닙니다. 인성(印星)과 비겁(比劫) 운이 올 때 귀인의 도움을 받아 크게 도약합니다. 혼자보다 좋은 파트너나 조력자와 함께할 때 훨씬 좋은 결과를 냅니다. 건강 관리를 최우선으로 여기고, 무리한 확장보다는 내실을 다지는 전략이 맞습니다. 귀인을 만나거나 스승을 모시는 것이 신약 사주의 성공 방정식입니다.""",
    "중화(中和)": """중화 사주는 오행의 균형이 잡혀 있어 어떤 상황에서도 크게 무너지지 않는 안정성이 있습니다. 극단적인 기복보다는 꾸준하고 안정적으로 성장하는 타입입니다. 특정 용신에 편중되지 않아 다양한 분야에서 균형 잡힌 능력을 발휘합니다. 그러나 반대로 특출난 강점이 부족할 수 있으니, 자신만의 전문 분야를 하나 깊이 파는 것이 중요합니다. 중화 사주의 가장 큰 장점은 지속성입니다. 오래 달리는 경주마처럼 꾸준함이 무기입니다.""",
}




class LocalSajuNarrator:
    """만세력 계산 결과를 받아 사람의 언어로 풀어주는 완전 로컬 해석 엔진"""

    # ── 60갑자 풀이 테이블 ─────────────────────────────────────


    # ── 십성별 10년 대운 특성 ────────────────────────────────

    DW_SS_MEANING = {
        "食神": "복록과 표현의 시기. 하고 싶은 일에 도전하면 성과가 따른다. 창업·기술 습득·콘텐츠 창작에 유리하고, 건강과 인복이 함께 좋아진다. 재능을 아낌없이 펼치는 것이 이 대운의 핵심이다.",
        "傷官": "재능과 갈등이 동시에 따르는 시기. 기존 틀을 깨는 혁신적 성취를 거두나 윗사람과의 마찰·구설을 극도로 조심해야 한다. 창의적 분야(예술·기술·컨설팅)에서 명성을 날릴 수 있다.",
        "偏財": "활동적 재물의 시기. 사업 확장·재테크·이성 인연이 풍부하다. 분산 투자와 인맥 활동이 뜻밖의 기회를 열어준다. 과욕보다 유연한 전략으로 넓게 씨를 뿌리는 대운이다.",
        "正財": "성실함이 쌓이는 안정 수입의 시기. 꾸준한 노력이 결실을 맺는다. 저축·부동산·신뢰 관계 구축이 핵심이다. 급하지 않고 원칙대로 나아갈 때 탄탄한 경제 기반이 완성된다.",
        "偏官": "도전과 변동의 시기. 강한 압박이 따르나 버텨내면 권위와 큰 성장이 온다. 건강(혈압·관절)·법적 문제에 유의하라. 위기 극복 경험이 이 대운의 가장 값진 자산이다.",
        "正官": "명예와 책임의 시기. 승진·임용·사회적 평가가 비약적으로 높아진다. 체계적이고 성실한 노력이 공식적으로 인정받는다. 규율과 원칙을 지키면 인생의 정점이 이 대운에서 온다.",
        "偏印": "변화·이동·전문성 확장의 시기. 자격증·이직·이사·해외와 인연이 깊다. 독창적 분야에서 독보적 전문가로 자리잡기 좋다. 고정관념을 깨고 새 정보를 흡수하는 것이 핵심 전략이다.",
        "正印": "학습과 귀인의 시기. 스승·후원자가 나타나 인생을 인도한다. 자격증·학위·문서 관련 일에서 뜻밖의 기회가 열린다. 조급함을 버리고 배움과 내공을 쌓으면 든든한 귀인이 따른다.",
        "比肩": "독립과 자립의 시기. 주도적으로 개척하는 기운이 강하다. 경쟁이 치열해지나 자력으로 이루는 성취가 가장 값지다. 협력보다 자기 실력을 믿고 정면 돌파하는 것이 이 대운의 정답이다.",
        "劫財": "경쟁·손재·변혁의 시기. 투자·보증·동업을 반드시 피해야 한다. 지출을 줄이고 수비 전략이 최선이다. 경쟁에서 정정당당히 임하고 재물 관리를 철저히 하면 위기 속에서 도약한다.",
    }

    # ── 오행별 직업/성향 요약 ───────────────────────────────

    OH_JOB = {
        "木": "교육·출판·법률·의료·환경 분야에 적합하다. 인의(仁義)를 중시하며 성장과 발전을 추구한다. 창의적이고 진보적인 사고로 사람을 이끄는 리더형 기질이 있으며, 장기 프로젝트에 강하다.",
        "火": "언론·예술·IT·식품·방송 분야에 적합하다. 열정과 표현력으로 사람들의 마음을 움직인다. 활발한 소통과 화려한 존재감으로 주목받으며, 무대 위에서 빛나는 기질이 있다.",
        "土": "부동산·건설·농업·금융·행정 분야에 적합하다. 신의(信義)가 강하며 안정과 실속을 추구한다. 중재자 역할에 뛰어나고 신중한 판단으로 주변의 신뢰를 한 몸에 받는 기질이다.",
        "金": "금융·법·군경·의료·제조 분야에 적합하다. 의리와 원칙을 중시하며 전문성이 강점이다. 정확하고 날카로운 판단력으로 전문가 최고 자리에 오르며, 불의에 타협하지 않는다.",
        "水": "유통·무역·IT·연구·철학 분야에 적합하다. 지혜롭고 유연하며 변화에 강한 적응력이 있다. 뛰어난 통찰력과 전략적 사고로 흐름을 읽고 선제적으로 기회를 잡는 기질이다.",
    }

    # ── 월지 계절별 특성 ────────────────────────────────────

    MONTH_JJ_SEASON = {
        "寅": "인월(寅月)은 木기운이 솟구치는 봄의 출발점입니다. 새 계획과 도전을 실행하기에 최상의 시기로, 진취적 활동이 빠르게 결실을 맺습니다. 새 인연과 확장의 기운이 충만한 달입니다.",
        "卯": "묘월(卯月)은 木기운이 절정에 달하며 성장과 확산이 가속되는 시기입니다. 사교·협업 활동이 빛나며 인간관계가 풍성해집니다. 재능을 드러내고 새 인연을 맺기에 가장 좋은 달입니다.",
        "辰": "진월(辰月)은 木·土기운이 교차하는 환절기의 달입니다. 봄의 성과를 정리하고 실속을 챙기는 전환점으로, 변화가 크지만 준비된 자에게는 도약의 기회가 열리는 달입니다.",
        "巳": "사월(巳月)은 火기운이 본격적으로 솟아오르는 열정의 달입니다. 표현력과 홍보 효과가 극대화되어 적극적인 활동과 자기 드러내기가 빛을 발합니다. 네트워크 확장과 영업에 최적입니다.",
        "午": "오월(午月)은 火기운이 절정에 달하는 뜨거운 결단의 달입니다. 과감한 도전이 결실을 맺고 리더십이 빛나는 시기입니다. 중요한 결정을 내리기에 좋으나 지나친 욕심은 삼가야 합니다.",
        "未": "미월(未月)은 火·土기운이 교차하는 조정과 내실의 달입니다. 여름 성과를 갈무리하고 과도한 확장보다 알찬 결실에 집중해야 합니다. 체력 안배와 건강 관리가 이 달의 핵심입니다.",
        "申": "신월(申月)은 金기운이 강해지며 결단과 수확의 계절이 열립니다. 중요한 결정을 내리고 불필요한 것을 정리해 핵심에 집중할 때입니다. 냉철한 분석이 이 달의 최고 무기입니다.",
        "酉": "유월(酉月)은 金기운이 절정에 달하는 완성과 전문성의 달입니다. 자신의 분야를 더욱 연마하고 완성도를 높이십시오. 꾸준한 노력이 공식적인 인정을 받으며 결실을 수확하는 달입니다.",
        "戌": "술월(戌月)은 가을에서 겨울로 전환하는 土기운의 달입니다. 한 해의 성과를 갈무리하고 내년을 준비하는 저장의 시기입니다. 냉정한 점검과 다음 도약을 위한 계획 수립이 핵심입니다.",
        "亥": "해월(亥月)은 水기운이 시작되는 지혜와 통찰의 달입니다. 외부 활동보다 내면 탐구와 학습에 집중하십시오. 깊은 계획이 빛나는 시기로, 다음 봄 도약을 위한 씨앗을 심는 달입니다.",
        "子": "자월(子月)은 水기운이 최강인 잠재력 응축의 달입니다. 조용히 실력을 쌓고 미래를 설계하십시오. 지금의 내공이 봄이 오면 폭발적 성장 에너지로 전환되는 귀중한 씨앗의 달입니다.",
        "丑": "축월(丑月)은 겨울과 봄 사이 인내와 성실의 달입니다. 눈에 보이는 성과보다 기초를 다지고 준비하는 데 집중하십시오. 묵묵한 노력이 봄이 오면 빛나는 결실로 터져 나옵니다.",
    }

    @staticmethod
    def _get_base(pils, name, birth_year, gender):
        """공통 기초 데이터 추출"""

        try:
            ilgan = pils[1]["cg"] if len(pils) > 1 else "?"

            gyeok = get_gyeokguk(pils) or {}

            gyeok_name = gyeok.get("격국명", "")

            str_info = get_ilgan_strength(ilgan, pils) or {}

            sn = str_info.get("신강신약", "")

            ys_data = get_yongshin(pils) or {}

            yongshin = ys_data.get("종합_용신", [])

            gisin = ys_data.get("기신", [])

            ss_list = calc_sipsung(ilgan, pils) or []

            o_s = calc_ohaeng_strength(ilgan, pils) or {}

            # 일주 (년주[0]=시, 년주[1]=일, 년주[2]=월, 년주[3]=년)

            pil_labels = ["시주", "일주", "월주", "년주"]

            pillars = {}

            for idx, label in enumerate(pil_labels):
                if idx < len(pils):
                    pillars[label] = f"{pils[idx].get('cg', '?')}{pils[idx].get('jj', '?')}"

            # 일주 60갑자

            ilju_key = pils[1].get("cg", "") + pils[1].get("jj", "") if len(pils) > 1 else ""

            ilju_desc = GJ60.get(ilju_key, ("", ""))[1]

            # 오행 최강·최약

            oh_max = max(o_s, key=o_s.get) if o_s else ""

            oh_min = min(o_s, key=o_s.get) if o_s else ""

            OHN = {
                "木": "목(木)",
                "火": "화(火)",
                "土": "토(土)",
                "金": "금(金)",
                "水": "수(水)",
            }

            # 현재 대운

            _ss = st.session_state

            bm = _ss.get("birth_month", 1)

            bd = _ss.get("birth_day", 1)

            bh = _ss.get("in_birth_hour", 12)

            bmi = _ss.get("in_birth_minute", 0)

            cur_year = datetime.now().year

            dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender) or []

            cur_dw = next(
                (d for d in dw_list if d.get("시작연도", 0) <= cur_year <= d.get("종료연도", 9999)),
                None,
            )

            sw = get_yearly_luck(pils, cur_year) or {}

            return dict(
                ilgan=ilgan,
                gyeok_name=gyeok_name,
                sn=sn,
                yongshin=yongshin,
                gisin=gisin,
                ss_list=ss_list,
                o_s=o_s,
                pillars=pillars,
                ilju_key=ilju_key,
                ilju_desc=ilju_desc,
                oh_max=oh_max,
                oh_min=oh_min,
                OHN=OHN,
                dw_list=dw_list,
                cur_dw=cur_dw,
                sw=sw,
                cur_year=cur_year,
                bm=bm,
                bd=bd,
            )

        except Exception as e:
            return {}

    @staticmethod
    def full_report(pils, name, birth_year, gender):
        """📊 종합운세 — 사주 전체 구조를 풀어 현재까지의 삶을 해석 (대폭 보강)"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        age = b["cur_year"] - birth_year + 1

        g_str = "남성" if gender == "남" else "여성"

        lines = []

        # ── 1. 사주 구조 소개 ─

        lines.append(f"## 🌟 {name}님의 사주 종합 리포트")

        lines.append(
            f"**{birth_year}년생 {age}세 {g_str}** — {b['pillars'].get('년주', '?')}년 {b['pillars'].get('월주', '?')}월 {b['pillars'].get('일주', '?')}일 {b['pillars'].get('시주', '?')}시 생\n"
        )

        lines.append("### 📋 사주 원국 (네 기둥의 힘)")

        lines.append("사주는 태어난 연, 월, 일, 시를 바탕으로 그려진 인생의 바코드이자 에너지 명세서입니다.")

        for label in ["년주", "월주", "일주", "시주"]:
            p = b["pillars"].get(label, "?")

            gj_info = GJ60.get(p, (p, ""))

            lines.append(f"- **{label}**: {p} ({gj_info[0] if gj_info[0] else p})")

            if gj_info[1]:
                lines.append(f"  - 📖 {gj_info[1]}")

        lines.append("")

        # ── 2. 일간 및 일주 기질 (본질) ─

        lines.append("### 🔥 타고난 본성과 기질 (일간/일주)")

        ilgan = b["ilgan"]

        OH_NATURE = {
            "甲": "갑목(甲木): 하늘로 곧게 뻗어 오르려는 큰 직립수. 리더십이 강하고 불의와 타협하지 않는 곧은 성품입니다.",
            "乙": "을목(乙木): 끈질긴 생명력을 지닌 덩굴 식물. 환경 적응력이 타의 추종을 불허하며 부드럽지만 외유내강입니다.",
            "丙": "병화(丙火): 만물을 비추는 태양. 숨기는 것이 없고 매우 다정다감하며 명랑하고 화려한 성향입니다.",
            "丁": "정화(丁火): 어둠을 밝히는 등대나 촛불. 희생정신이 뛰어나고 내면의 열정과 끈기가 대단한 외유내강형입니다.",
            "戊": "무토(戊土): 든든하고 스케일이 큰 거대한 산. 중재자 역할을 잘하며 신용과 무게감이 인생의 무기입니다.",
            "己": "기토(己土): 만물을 길러내는 비옥한 논밭. 현실 감각이 매우 탁월하며 실속 있고 자상한 기질입니다.",
            "庚": "경금(庚金): 가공되지 않은 바위나 무쇠. 한 번 결정한 것은 끝까지 밀어붙이는 의리와 승부욕이 빛납니다.",
            "辛": "신금(辛金): 세공이 끝난 빛나는 보석. 완벽주의 성향과 예리한 통찰력을 가졌으며 자존심이 매우 강합니다.",
            "壬": "임수(壬水): 모든 것을 포용하는 넓은 바다 혹은 큰 강. 두뇌 회전이 대단히 빠르고 포용력과 유연성이 좋습니다.",
            "癸": "계수(癸水): 만물을 적시는 이슬비나 샘물. 지혜롭고 섬세하며 상황 파악 능력이 탁월한 기획자 타입입니다.",
        }

        lines.append(f"**[{ilgan} 일간의 본성]**\n{OH_NATURE.get(ilgan, f'{ilgan} 일간 — 고유한 기질을 지니고 있습니다.')}")

        ilju_key = b["ilju_key"]

        ilju_desc = b["ilju_desc"]

        if ilju_desc:
            lines.append(f"\n**[{ilju_key} 일주의 특성]**\n나를 직접적으로 나타내는 기둥인 일주(日柱)의 특성입니다. {ilju_desc}")

        lines.append("")

        # ── 3. 격국·신강신약·용신 ─

        lines.append("### ⚖️ 사주의 뼈대와 균형 (격국과 용신)")

        if b["gyeok_name"]:
            lines.append(f"- **격국(사주의 사회적 역할)**: {b['gyeok_name']}")

        if b["sn"]:
            sn_desc = {
                "신강": "일간의 힘이 든든한 신강 사주입니다. 주체성이 강하여 스스로 개척하려는 성향이 짙습니다. 독단에 빠지지 않도록 유연함을 기르십시오.",
                "신약": "일간의 힘이 조화로운 신약 사주입니다. 타인과의 협력, 귀인의 도움이 큰 힘이 됩니다. 좋은 멘토와 파트너를 만나는 것이 인생의 핵심입니다.",
            }.get(b["sn"], b["sn"])

            lines.append(f"- **신강/신약(주도력)**: {sn_desc}")

        if b["yongshin"]:
            ys_str = "·".join(b["yongshin"][:3])

            lines.append(f"- **용신(도력 오행)**: {ys_str} — 이 기운이 들어오는 해, 이 색상이나 방향이 삶에 긍정적인 반전을 가져다줍니다.")

        if b["gisin"]:
            gs_str = "·".join(b["gisin"][:2])

            lines.append(f"- **기신(주의 오행)**: {gs_str} — 이 기운의 시기에는 수비적인 자세로 내실을 다지는 것이 좋습니다.")

        lines.append("")

        # ── 4. 오행 분포 ─

        if b["o_s"]:
            lines.append("### 🌊 오행 분포와 성향의 기울기")

            OHN = b["OHN"]

            oh_sorted = sorted(b["o_s"].items(), key=lambda x: -x[1])

            for oh, sc in oh_sorted:
                bar = "█" * min(int(sc * 2), 10)

                lines.append(f"- **{OHN.get(oh, oh)}**: {bar} ({sc:.1f})")

            omax = OHN.get(b["oh_max"], b["oh_max"])

            omin = OHN.get(b["oh_min"], b["oh_min"])

            lines.append(f"\n**가장 강한 에너지**: {omax} | **가장 약한 에너지**: {omin}")

            job_desc = LocalSajuNarrator.OH_JOB.get(b["oh_max"], "")

            if job_desc:
                lines.append(f"- **직업 성향 풀이**: {job_desc}")

            lines.append("")

        # ── 5. 주요 십성 구조와 사회적 활용 ─

        if b["ss_list"]:
            lines.append("### 🧠 사회적 성향과 무기 (십성 분석)")

            ss_names = []

            for d in b["ss_list"]:
                if isinstance(d, dict):
                    if d.get("cg_ss") and d.get("cg_ss") != "-":
                        ss_names.append(d["cg_ss"])

                    if d.get("jj_ss") and d.get("jj_ss") != "-":
                        ss_names.append(d["jj_ss"])

                elif isinstance(d, str) and d != "-":
                    ss_names.append(d)

            ss_str = " / ".join(list(set(ss_names))) if ss_names else "알 수 없음"

            lines.append(f"내 사주에 주로 포진된 사회적 무기는 **[{ss_str}]** 입니다.")

            # Simple interpretation of prevalent Sipsung

            if "식신" in ss_str or "상관" in ss_str:
                lines.append("- **식상(재능, 표현력)**: 본인만의 기술이나 예술적 감각, 언변 등 표현하는 능력을 생업으로 삼을 때 유리합니다.")

            if "편재" in ss_str or "정재" in ss_str:
                lines.append("- **재성(재물, 결과)**: 현실 감각이 뛰어나며, 결과를 만들어내고 금전을 굴리는 이재술에 밝습니다.")

            if "편관" in ss_str or "정관" in ss_str:
                lines.append("- **관성(명예, 조직)**: 조직 활동, 공직, 대기업 등 체계가 있는 곳에서 인정받으며 원칙을 중시합니다.")

            if "편인" in ss_str or "정인" in ss_str:
                lines.append("- **인성(자격, 학문)**: 지적 자산, 부동산, 전문 자격증, 끊임없는 학구열이 성공의 발판이 됩니다.")

            if "비견" in ss_str or "겁재" in ss_str:
                lines.append("- **비겁(주체, 경쟁)**: 강한 자신감과 승부욕을 바탕으로 독립적 인 궤도를 그립니다. 사람 사이의 협력이 관건입니다.")

            lines.append("")

        # ── 6. 올해 세운 + 현재 대운 ─

        lines.append("### 🌀 현재 운세와 환경의 흐름")

        sw = b["sw"]

        sw_ss = sw.get("십성_천간", "")

        sw_gan = sw.get("세운", "")

        sw_gh = sw.get("길흉", "평")

        if sw_gan:
            dw_meaning = LocalSajuNarrator.DW_SS_MEANING.get(sw_ss, "")

            lines.append(f"**올해(2026년) 세운**: {sw_gan} [{sw_ss}] — 길흉: **{sw_gh}**")

            if dw_meaning:
                lines.append(f"  - 💡 {dw_meaning}")

        cur_dw = b["cur_dw"]

        if cur_dw:
            dw_gan = cur_dw.get("str", "") or cur_dw.get("대운", "")
            dw_ss = cur_dw.get("십성_천간", "") or (TEN_GODS_MATRIX.get(b.get("ilgan"), {}).get(cur_dw.get("cg", ""), "") if cur_dw.get("cg") else "")

            dw_start = cur_dw.get("시작연도", 0)

            dw_end = cur_dw.get("종료연도", 9999)

            age_s = dw_start - birth_year + 1

            age_e = dw_end - birth_year + 1

            lines.append(f"\n**현재 대운**: {dw_gan} [{dw_ss}] ({dw_start} ~ {dw_end}년 / {age_s} ~ {age_e}세)")

            lines.append("  - 흐름을 잘 살피고, 길몽이라면 박차를 가하며 흉운이라면 내실을 다져야 하는 시기입니다.")

        lines.append("")

        # ── 6.5. 신살·공망 (로컬 엔진 강화) ─

        try:
            _sinsal_list = get_12sinsal(pils)
            _gongmang = get_gongmang(pils)
            _has_sinsal = _sinsal_list and len(_sinsal_list) > 0
            _gm_cols = _gongmang.get("해당_기둥", []) if isinstance(_gongmang, dict) else []
            if _has_sinsal or _gm_cols:
                lines.append("### ✨ 특별한 기운 (신살·공망)")
                if _has_sinsal:
                    _names = [s.get("이름") or s.get("name", "") for s in _sinsal_list[:6] if isinstance(s, dict)]
                    if _names:
                        lines.append(f"- **신살**: {', '.join(_names)} — 사주에 특별한 기운이 자리해 해당하는 재능과 주의할 점이 있습니다.")
                if _gm_cols:
                    _gm_names = [g.get("기둥", "") for g in _gm_cols if isinstance(g, dict)]
                    if _gm_names:
                        lines.append(f"- **공망**: {', '.join(_gm_names)}에 공망이 있어, 해당 영역은 때로 헛되이 느껴질 수 있으나 집착을 내려놓을 때 균형이 잡힙니다.")
                lines.append("")
        except Exception as _e:
            _saju_log.debug("[silent except] %s", _e)

        # ── 7. 종합 가이드 ─

        lines.append("### 💡 인생 종합 액션 플랜")

        lines.append("사주는 정해진 운명이라기보다 **내가 가진 패와 날씨의 달력**입니다. 강점은 키우고 약점은 보완하는 지혜를 발휘하십시오.")

        lines.append("다가오는 10년의 구체적인 전술은 아래 **시기별 행동 지침**을 참고하여 나아갈 때와 물러설 때를 구별하시기 바랍니다.")

        lines.append("")

        lines.append(LocalSajuNarrator._timing_advice(pils, birth_year, b["yongshin"], b["gisin"], b["cur_year"]))

        return "\n".join(lines)

    @staticmethod
    def lifeline(pils, name, birth_year, gender):
        """🔄 대운 전생애 서사 — 과거에서 미래까지 10년 단위로"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        cur_year = b["cur_year"]

        age_now = cur_year - birth_year + 1

        lines = []

        lines.append(f"## 🔄 {name}님의 대운(大運) 100년 생애 흐름")

        lines.append(f"*{birth_year}년생 현재 {age_now}세 — 대운은 10년마다 바뀌는 삶의 큰 물줄기입니다.*\n")

        dw_list = b["dw_list"]

        for dw in dw_list:
            lines.append(LocalSajuNarrator._dw_detail(dw, birth_year, pils, cur_year, b["yongshin"], b["gisin"]))

        lines.append("---")

        lines.append("### 📌 전생애 흐름 요약")

        lines.append("어려운 대운에는 내실을 다지고 기다리는 지혜가 필요합니다.")

        return "\n".join(lines)

    @staticmethod
    def past_analysis(pils, name, birth_year, gender):
        """🎯 과거 적중 — 지나온 대운별 '그 시절' 서술"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        cur_year = b["cur_year"]

        lines = []

        lines.append(f"## 🎯 {name}님의 과거 사주 적중 분석")

        lines.append(f"*지나온 대운의 흐름 속에서 어떤 일들이 있었는지 사주로 살펴봅니다.*\n")

        past_dws = [d for d in b["dw_list"] if d.get("종료연도", 0) < cur_year]

        if not past_dws:
            lines.append("분석할 과거 대운 데이터가 없습니다.")

            return "\n".join(lines)

        for dw in past_dws:
            dw_start = dw.get("시작연도", 0)

            dw_end = dw.get("종료연도", 9999)

            dw_gan = dw.get("str", "") or dw.get("대운", "")

            dw_ss = dw.get("십성_천간", "")

            age_s = dw_start - birth_year + 1

            age_e = dw_end - birth_year + 1

            lines.append(f"### 📜 {dw_gan} 대운 ({dw_start} ~ {dw_end}년 | {age_s} ~ {age_e}세)")

            # 시기별 생애 맥락

            if age_s <= 7:
                lines.append(f"**유아기**: 태어나 세상을 인식하기 시작한 시절입니다.")

                lines.append(f"부모와 가정 환경이 이 시기를 결정하며, {dw_ss} 기운이 성장 환경을 만들었습니다.")

            elif age_s <= 15:
                lines.append(f"**청소년 초기**: 학교 생활이 중심이 된 시절입니다.")

                if dw_ss in ["正印", "偏印"]:
                    lines.append("학업에서 좋은 성과를 거뒀을 가능성이 높습니다. 선생님이나 멘토의 영향을 받았을 것입니다.")

                elif dw_ss in ["比肩", "劫財"]:
                    lines.append("또래 친구들과의 관계가 중심이었습니다. 경쟁 의식도 강했을 시기입니다.")

                elif dw_ss in ["食神", "傷官"]:
                    lines.append("재능이 표출되기 시작한 시기입니다. 특기나 관심 분야가 생겼을 것입니다.")

            elif age_s <= 25:
                lines.append(f"**청년기**: 진로와 자아 정체성을 찾아가던 시절입니다.")

                if dw_ss in ["正官", "偏官"]:
                    lines.append("사회적 규범과 의무가 강조되던 시기. 직장 진출, 군대, 책임감이 컸을 것입니다.")

                elif dw_ss in ["偏財", "正財"]:
                    lines.append("경제적 독립을 향해 첫발을 내딛던 시기. 재물에 대한 욕구가 강해졌을 것입니다.")

                elif dw_ss in ["正印", "偏印"]:
                    lines.append("공부와 자기 계발에 집중했던 시기. 자격증·학위·전문성을 쌓았을 것입니다.")

            elif age_s <= 40:
                lines.append(f"**중청년기**: 직업, 결혼, 경제적 기반이 완성되어 가던 시절입니다.")

                if dw_ss in ["正財", "偏財"]:
                    lines.append("재물·사업 기운이 강했던 시기. 경제적으로 가장 활발하게 움직였을 것입니다.")

                elif dw_ss in ["正官", "偏官"]:
                    lines.append("직장에서의 책임과 사회적 지위가 높아졌던 시기입니다.")

                elif dw_ss in ["食神", "傷官"]:
                    lines.append("창의적인 활동과 자기 표현이 활발했던 시기입니다.")

            else:
                lines.append(f"**중년기**: 삶의 결실과 안정을 찾아가던 시절입니다.")

                gl = dw.get("길흉", "평")

                if gl in ["길", "+"]:
                    lines.append(f"{dw_gan} 대운은 길한 기운이었습니다. 이 시기에 삶의 주요 성취가 이루어졌을 것입니다.")

                elif gl in ["흉", "-"]:
                    lines.append(f"{dw_gan} 대운은 도전적인 기운이었습니다. 시련이 있었으나 그것이 성장의 밑거름이 되었을 것입니다.")

            # 세운 하이라이트 (그 시기 중 특별한 해)

            highlight_years = []

            for yr in range(dw_start, min(dw_end + 1, cur_year)):
                try:
                    sw_yr = get_yearly_luck(pils, yr)

                    sw_gh = sw_yr.get("길흉", "평")

                    sw_ss = sw_yr.get("십성_천간", "")

                    if sw_gh in ["길", "+"]:
                        highlight_years.append(f"  - **{yr}년** ({yr - birth_year + 1}세): {sw_yr.get('세운', '')} [{sw_ss}] — 좋은 기운이 흘렀습니다.")

                    elif sw_gh in ["흉", "-"] and len(highlight_years) < 2:
                        highlight_years.append(f"  - **{yr}년** ({yr - birth_year + 1}세): {sw_yr.get('세운', '')} [{sw_ss}] — 조심이 필요했던 해.")

                except Exception as _e:
                    _saju_log.debug("[silent except] %s", _e)

            if highlight_years:
                lines.append("\n**주목할 해:**")

                for hy in highlight_years[:3]:
                    lines.append(hy)

            lines.append("")

        lines.append("---")

        lines.append("*사주는 과거를 되짚어 현재와 미래의 방향을 찾는 지도입니다.*")

        return "\n".join(lines)

    @staticmethod
    def _timing_advice(pils, birth_year, yongshin, gisin, cur_year):
        """향후 10년 시기별 행동 지침 생성 (산문 형식)"""

        OH = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        }

        # 십성별 (산문 설명, 추천, 주의, 핵심 전략)
        SS_PROSE = {
            "食神": (
                "먹고 즐기는 기운이 활성화되는 해로, 창의력과 표현력이 최고조에 달합니다. "
                "새로운 아이디어가 풍성하게 솟아오르고 사람들과의 소통이 자연스럽게 이루어집니다. "
                "다만 풍족함에 취해 과로하거나 건강을 소홀히 하지 않도록 주의하십시오.",
                "새 사업·부업·강의·창작 활동·요식업·콘텐츠 제작",
                "과로로 인한 건강 악화, 지나친 소비와 향락",
                "재능을 세상에 드러낼 적기입니다. 좋아하는 일을 사업화하는 방향을 모색하십시오.",
            ),
            "傷官": (
                "기존의 틀을 깨려는 충동이 강하게 일어나는 해입니다. "
                "창의적 에너지와 반항 기질이 함께 올라오므로, 그 에너지를 혁신과 기술 향상에 쏟으면 "
                "큰 성과를 거둘 수 있습니다. 단, 윗사람과의 언행 충돌에 각별히 주의하십시오.",
                "기술 연마·자격증 취득·혁신적 아이디어 실행·전문직 도전",
                "윗사람과의 마찰, 계약 분쟁, 충동적 이직·결정",
                "실력을 쌓되 드러내는 시기는 조금 기다리십시오. 말보다 결과물로 증명하십시오.",
            ),
            "偏財": (
                "활동적인 재물 기운이 넘치는 해로, 사업 확장과 적극적 영업에 유리한 시기입니다. "
                "여러 곳에서 기회가 동시에 찾아오지만, 그만큼 분산 투자의 위험도 높아집니다. "
                "재물이 빠르게 들어오고 빠르게 나가는 흐름이니 자금 관리를 철저히 하십시오.",
                "사업 확장·적극적 영업·투자·네트워킹·해외 거래",
                "무분별한 투자, 타인 보증 서기, 충동적 지출",
                "들어오는 돈의 절반은 반드시 저축하거나 안전 자산에 묶어두십시오.",
            ),
            "正財": (
                "안정적이고 꾸준한 재물 기운이 흐르는 해입니다. "
                "급격한 변화보다는 착실히 쌓아가는 전략이 빛을 발하며, "
                "부동산·저축·정기적 수입원 확보에 최적의 시기입니다.",
                "저축·부동산 매입·꾸준한 수입원 확보·재정 계획 수립",
                "과도한 소비, 도박성 투자, 지나친 인색함으로 인한 기회 손실",
                "눈앞의 작은 이익보다 장기적 안정을 선택하십시오. 꾸준함이 최고의 전략입니다.",
            ),
            "偏官": (
                "강렬한 도전과 경쟁의 기운이 몰아치는 해입니다. "
                "자신을 강하게 몰아붙이는 외부 압력이 생기지만, "
                "그것을 성장의 연료로 삼으면 비약적 도약이 가능합니다. "
                "건강과 안전에 각별히 주의하십시오.",
                "도전적 목표 설정·군경·운동·강도 높은 훈련·경쟁에서의 승부",
                "과로·사고·법적 분쟁·충동적 대결",
                "적을 만들지 마십시오. 경쟁에서 이기되 상대를 존중하는 태도가 장기적 승리를 가져옵니다.",
            ),
            "正官": (
                "질서와 책임의 기운이 강해지는 해로, 조직 안에서의 신뢰가 쌓이고 승진·인정을 받을 수 있습니다. "
                "다만 과도한 책임감이 스트레스로 쌓이지 않도록 적절한 휴식과 경계 설정이 필요합니다.",
                "승진·자격 취득·직장 안정·사회적 신뢰 구축·공직 도전",
                "스트레스 누적, 과도한 책임 부담, 유연성 부족",
                "규칙을 지키되 자신의 건강도 규칙처럼 지키십시오. 번아웃을 조심하십시오.",
            ),
            "偏印": (
                "변화와 이동의 기운이 강한 해입니다. "
                "새로운 기술·학문·영성에 관심이 높아지고, 이직·이사·해외 진출 등 큰 변화가 생길 수 있습니다. "
                "직관이 날카로워지는 시기이지만, 허황된 말에 현혹되기도 쉬운 해입니다.",
                "자격증·이직·이사·해외 도전·영적 성장·다양한 분야 학습",
                "감언이설에 속기, 과도한 변동, 집중력 분산",
                "변화를 두려워하지 마십시오. 다만 한 가지에 깊이 파고드는 집중력을 잃지 마십시오.",
            ),
            "正印": (
                "배움과 지혜의 기운이 충만한 해입니다. "
                "학문·공부·자격증에 집중하면 큰 성과를 거둘 수 있으며, "
                "좋은 스승이나 귀인의 도움을 받을 수 있는 시기입니다. "
                "다만 행동력이 약해지고 의존심이 강해지지 않도록 주의하십시오.",
                "공부·자격·스승 찾기·문서 작업·계획 수립",
                "의존심 과다, 행동력 부족, 결정을 미루는 습관",
                "아는 것에서 멈추지 말고 반드시 실행하십시오. 지식은 행동할 때 비로소 가치가 생깁니다.",
            ),
            "比肩": (
                "자립과 독립의 기운이 강해지는 해입니다. "
                "자신만의 길을 개척하려는 욕구가 강해지고, 창업·자기 브랜딩에 유리한 시기입니다. "
                "단, 경쟁 심리가 과해지거나 협력을 거부하면 고립될 수 있습니다.",
                "독립·창업·자기 브랜딩·네트워크 확장·리더십 발휘",
                "고집 강화, 과도한 경쟁, 협력 거부로 인한 고립",
                "혼자 잘하는 것보다 함께 잘하는 것이 더 큰 성과를 만들어 냅니다. 팀을 만드십시오.",
            ),
            "劫財": (
                "재물이 흔들리고 인간관계에서 변동이 생기는 해입니다. "
                "예상치 못한 지출이나 손해가 발생하기 쉬우며, "
                "타인과의 금전 거래에서 분쟁이 일어날 수 있습니다. "
                "현금 확보와 부채 감축에 집중하는 한 해로 삼으십시오.",
                "현금 확보·부채 감축·비상금 마련·내실 다지기",
                "투자·보증·동업·충동 지출·과도한 신용",
                "이 해는 지키는 것이 버는 것입니다. 수비를 전략으로 삼으십시오.",
            ),
        }

        SS_DEFAULT = (
            "운의 흐름이 중립적인 해입니다. 과도한 욕심 없이 현재 자리를 잘 지키면서 "
            "다음 기회를 준비하는 시기로 활용하십시오.",
            "현 상황 유지·내실 다지기·자기 계발",
            "무리한 변화, 충동적 결정",
            "지금은 씨앗을 심는 시기입니다. 조급해하지 마십시오.",
        )

        GH_KR = {"길": "길운(吉)", "+": "길운(吉)", "평": "평운(平)", "흉": "주의운(凶)", "-": "주의운(凶)"}

        lines = []
        lines.append("### 📅 향후 10년 시기별 행동 지침\n")

        for yr in range(cur_year, cur_year + 10):
            try:
                sw = get_yearly_luck(pils, yr)
                ss = sw.get("십성_천간", "")
                gh = sw.get("길흉", "평")
                gan = sw.get("세운", "")
                age = yr - birth_year + 1
                yr_oh = OH.get(gan[:1], "") if gan else ""

                is_ys = any(yr_oh == y or yr_oh in y for y in (yongshin or []))
                is_gs = any(yr_oh == g or yr_oh in g for g in (gisin or []))

                ys_badge = " ✨ **[용신년 — 적극 활용하십시오]**" if is_ys else (
                    " 🔴 **[기신년 — 신중하게 행동하십시오]**" if is_gs else ""
                )

                gh_kr = GH_KR.get(gh, gh)
                narr, action, caution, strategy = SS_PROSE.get(ss, SS_DEFAULT)

                lines.append(
                    f"---\n"
                    f"▶ **{yr}년 ({age}세) — {gan}년 [{ss}] {gh_kr}**{ys_badge}\n\n"
                    f"{narr}\n\n"
                    f"✅ **추천:** {action}  \n"
                    f"⚠️ **주의:** {caution}  \n"
                    f"💡 **핵심 전략:** {strategy}\n"
                )

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

        return "\n".join(lines)

    @staticmethod
    def _dw_detail(dw, birth_year, pils, cur_year, yongshin, gisin):
        """대운 1개의 상세 서술 생성 (버그 완벽 수정 및 풍성한 만신 서사 적용)"""

        OH = {
            "甲": "木",
            "乙": "木",
            "丙": "火",
            "丁": "火",
            "戊": "土",
            "己": "土",
            "庚": "金",
            "辛": "金",
            "壬": "水",
            "癸": "水",
        }

        dw_start = dw.get("시작연도", 0)

        dw_end = dw.get("종료연도", 9999)

        # 🚨 버그 1 원인 수정: "대운" 키가 아니라 "str"로 가져와야 간지(글자)가 나옴!

        dw_gan = dw.get("str", "")

        dw_ss = dw.get("십성_천간", "")

        dw_ss_j = dw.get("십성_지지", "")

        age_s = dw_start - birth_year + 1

        age_e = dw_end - birth_year + 1

        is_cur = dw_start <= cur_year <= dw_end

        is_past = dw_end < cur_year

        gj_key = dw_gan[:2] if len(dw_gan) >= 2 else dw_gan

        gj = GJ60.get(gj_key, ("", ""))

        oh = OH.get(dw_gan[:1], "")

        # 🚨 버그 2 원인 수정: oh가 빈값("")일 때 무조건 True가 나오는 파이썬 버그 방어 (bool(oh) 추가)

        is_ys = bool(oh) and any(oh == y for y in (yongshin or []))

        is_gs = bool(oh) and any(oh == g for g in (gisin or []))

        lines = []

        icon = "⭐" if is_cur else ("📜" if is_past else "🔮")

        cur_mark = " **[현재 대운]**" if is_cur else ""

        ys_mark = " ✨【용신 대운 — 황금기】" if is_ys else (" ⚠️【기신 대운 — 조심】" if is_gs else "")

        # 이제 대운 글자(간지)가 제대로 찍힙니다.

        lines.append(f"\n{icon} **{dw_gan} 대운 ({dw_start} ~ {dw_end}년 / {age_s} ~ {age_e}세)**{cur_mark}{ys_mark}")

        # 🚨 버그 3 원인 수정: 뻔한 텍스트 대신, 이미 만들어두신 '만신 풍성한 해석 함수' 연동!

        try:
            nar_icon, nar_title, nar_text = get_daewoon_narrative(dw_ss, dw_ss_j, dw_gan, age_s)

            lines.append(f"> **{nar_icon} {nar_title}**")

            # HTML 줄바꿈을 마크다운 줄바꿈으로 깔끔하게 치환

            lines.append(nar_text.replace("<br>", "\n"))

        except Exception:
            m = LocalSajuNarrator.DW_SS_MEANING.get(dw_ss, "")

            if m:
                lines.append(f"**{dw_ss}({dw_ss_j}) 기운**: {m}")

        gj_desc = gj[1] if gj[1] else ""

        if gj_desc:
            gj_desc_short = gj_desc[:120] + "…" if len(gj_desc) > 120 else gj_desc
            lines.append(f"**간지 풀이**: {gj_desc_short}")

        # 현재 대운이면 세운 + 조합 분석

        if is_cur:
            lines.append("\n**이 대운 안의 세운 흐름:**")

            for yr in range(max(dw_start, cur_year - 2), min(dw_end + 1, cur_year + 5)):
                try:
                    sw = get_yearly_luck(pils, yr)

                    sw_ss = sw.get("십성_천간", "")

                    sw_gh = sw.get("길흉", "평")

                    sw_gan = sw.get("세운", "")

                    yr_oh = OH.get(sw_gan[:1], "") if sw_gan else ""

                    is_ys2 = bool(yr_oh) and any(yr_oh == y for y in (yongshin or []))

                    is_gs2 = bool(yr_oh) and any(yr_oh == g for g in (gisin or []))

                    ys2 = "✨" if is_ys2 else ("🔴" if is_gs2 else "")

                    gh_icon = "🌟" if sw_gh in ["길", "+"] else ("⚠️" if sw_gh in ["흉", "-"] else "⚖️")

                    cur_mark2 = " ◀ **올해**" if yr == cur_year else ""

                    lines.append(f"  - **{yr}년** ({yr - birth_year + 1}세): {sw_gan}[{sw_ss}] {gh_icon}{ys2}{cur_mark2}")

                except Exception as _e:
                    _saju_log.debug("[silent except] %s", _e)

        return "\n".join(lines)

    @staticmethod
    def future3(pils, name, birth_year, gender, marriage="미혼"):
        """🔮 미래 3년 ― 세운+대운 조합 상세 예측"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        cur_year = b["cur_year"]

        lines = []

        lines.append(f"## 🔮 {name}님의 미래 3년 심층 예측 ({cur_year}~{cur_year + 2}년)")

        dw_gan = (b["cur_dw"].get("str", "") or b["cur_dw"].get("대운", "")) if b["cur_dw"] else "?"

        lines.append(f"*현재 {dw_gan} 대운의 큰 흐름 속에서 다가올 3년의 구체적인 행동 지침을 분석합니다.*\n")

        ys_list = b["yongshin"]

        gisin = b["gisin"]

        OH = {
            "甲": "木",
            "乙": "木",
            "丙": "火",
            "丁": "火",
            "戊": "土",
            "己": "土",
            "庚": "金",
            "辛": "金",
            "壬": "水",
            "癸": "水",
        }

        OHN = b["OHN"]

        for yr in [cur_year, cur_year + 1, cur_year + 2]:
            try:
                sw = get_yearly_luck(pils, yr)

            except Exception:
                sw = {}

            sw_ss = sw.get("십성_천간", "")

            sw_ss_j = sw.get("십성_지지", "")

            sw_gan = sw.get("세운", "")

            sw_gh = sw.get("길흉", "평")

            age_yr = yr - birth_year + 1

            yr_oh = OH.get(sw_gan[:1], "") if sw_gan else ""

            label = "📌 **올해**" if yr == cur_year else ("📅 **내년**" if yr == cur_year + 1 else "🔭 **내후년**")

            lines.append(f"### {label} {yr}년 ({age_yr}세) — {sw_gan} [{sw_ss}/{sw_ss_j}]")

            gh_icon = "🌟" if sw_gh in ["길", "+"] else ("⚠️" if sw_gh in ["흉", "-"] else "⚖️")

            lines.append(f"**{gh_icon} 세운 총평**: {sw_gh}")

            if yr_oh and ys_list:
                is_ys = any(yr_oh in y for y in ys_list)

                is_gs = any(yr_oh in g for g in gisin)

                if is_ys:
                    lines.append(f"✨ **용신(행운)의 해입니다.** 주저하지 말고 판을 키우거나 새로운 도전을 시작하십시오!")

                elif is_gs:
                    lines.append(f"🔴 **기신(주의)의 해입니다.** 새로운 시도보다는 현재 위치를 방어하고 내실을 다지는 수비 전략이 필수입니다.")

            # 십성별 상세 행동 지침 (언제 좋고 언제 조심)


            if sw_ss in guides:
                lines.append(f"- **이 해에 집중할 것**: {guides[sw_ss][0]}")

                lines.append(f"- **이 해에 조심할 것**: {guides[sw_ss][1]}")

            lines.append("")

        lines.append("---")

        lines.append("### 🏆 향후 3년 승부처와 휴식처")

        lines.append("다가올 3년 중, **강하게 밀어붙여야 할 타이밍**과 **움츠리고 방어해야 할 타이밍**을 종합적으로 구분합니다.\n")

        try:
            gh_list = []

            for yr in [cur_year, cur_year + 1, cur_year + 2]:
                sw = get_yearly_luck(pils, yr)

                gh_list.append((yr, sw.get("길흉", "평"), sw.get("세운", "")))

            best = [f"{y}년({g[2]})" for y, g1, g in gh_list if g1 in ["길", "+"]]

            worst = [f"{y}년({g[2]})" for y, g1, g in gh_list if g1 in ["흉", "-"]]

            if best:
                lines.append(f"✅ **승부를 띄워야 할 황금기 (적극적 행동 추천)**: {', '.join(best)}")

                lines.append("이 시기에는 이직, 사업 확장, 결혼, 매매 등 인생의 중요한 결정을 과감하게 내리는 것이 유리합니다.")

            if worst:
                lines.append(f"🛡️ **돌다리도 두드려야 할 수비기 (현상 유지 필수)**: {', '.join(worst)}")

                lines.append("이 시기에는 확장이나 큰 변동을 피하고 현금 보유를 늘리며, 건강 관리에 힘쓰고 계약을 보류하는 것이 좋습니다.")

        except Exception as _e:
            _saju_log.debug("[silent except] %s", _e)

        return "\n".join(lines)

    @staticmethod
    def money(pils, name, birth_year, gender):
        """💰 재물/사업 분석 ― 언제 벌고 언제 조심하나"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        lines = []

        lines.append(f"## 💰 {name}님의 평생 재물 및 사업 분석")

        lines.append(f"*재물은 형태(어떤 방식으로 버는가)와 타이밍(언제 벌고 언제 조심하는가)을 아는 것이 중요합니다.*\n")

        ilgan = b["ilgan"]

        ss_list = b["ss_list"]

        # 1. 십성 분석

        lines.append("### 🏦 내게 맞는 재물의 형태 (십성 구조)")

        jaesung = [s for s in ss_list if s.get("cg_ss") in ["偏財", "正財"] or s.get("jj_ss") in ["偏財", "正財"]]

        siksung = [s for s in ss_list if s.get("cg_ss") in ["食神", "傷官"] or s.get("jj_ss") in ["食神", "傷官"]]

        if jaesung:
            lines.append(f"사주 원국에 재성(결과물, 돈)이 **{len(jaesung)}개** 있습니다.")

            has_pj = any(s.get("cg_ss") == "偏財" or s.get("jj_ss") == "偏財" for s in jaesung)

            has_jj = any(s.get("cg_ss") == "正財" or s.get("jj_ss") == "正財" for s in jaesung)

            if has_pj:
                lines.append(
                    "- **편재(큰 돈/사업재물)**의 기운이 있습니다. 통이 크고 금전의 융통 규모가 크며, 고정 급여보다는 인센티브나 사업, 유통, 무역을 통해 돈을 불리는 재주가 탁월합니다. 하지만 지출 통제가 안 될 수 있으니 번 돈을 부동산이나 고정 자산으로 바로 묶어두는 지혜가 필요합니다."
                )

            if has_jj:
                lines.append(
                    "- **정재(월급/고정수입)**의 기운이 있습니다. 차곡차곡 모으는 저축형 재정에 능합니다. 안정적인 월급이나 임대 수익이 맞으며, 불확실한 주식이나 도박성 투자보다는 안정적인 부동산, 채권 등에 투자하는 것이 평생 재물을 지키는 길입니다."
                )

        else:
            lines.append("✨ 사주 원국에 직접적인 '재성'(뚜렷하게 눈에 보이는 돈) 자체는 적게 나타나는 무재(無財) 성향을 띠거나 재물이 숨어 있습니다.")

            if siksung:
                lines.append(
                    "하지만 식상(재능/표현력)이 있어 굶어 죽지 않는 팔자입니다. 직접 돈을 좇기보다는 **내 기술과 재능(자격증, 전문성)을 닦으면 그것이 자연스럽게 재물로 환산**되는 구조입니다. 눈앞의 수익보다 명예와 이름값을 올리는 데 집중하십시오."
                )

            else:
                lines.append(
                    "자신만의 독보적인 기술, 전문직 자격, 혹은 안정적인 거대 조직(공기업/대기업)에 소속되어 재정을 의탁하는 것이 가장 안전합니다. 자기 사업이나 장사보다는 '내 분야의 마스터'가 되어 월급이나 컨설팅 비용을 받는 것이 최고의 전략입니다."
                )

        # 2. 오행 추천

        lines.append("\n### 💡 유리한 직종과 투자처 (오행)")

        lines.append(LocalSajuNarrator.OH_JOB.get(b["oh_max"], ""))

        if b["yongshin"]:
            lines.append(f"특히 용신 오행인 **{' · '.join(b['yongshin'][:2])}** 관련 사업(색상, 방향, 취급 품목 등)을 취급할 때 재물 운이 상승합니다.")

        # 3. 타이밍! 언제 좋고 언제 조심?

        lines.append("\n### ⏰ 시기별 투자/사업 행동 지침")

        # 최근 10년의 재성/겁재 해

        lines.append("**✅ 크게 움직이고 투자해야 할 때 (기회가 오는 해)**")

        lines.append("- 사주에서 **편재/정재/식신** 운이 들어오는 해입니다.")

        lines.append("- 이때는 대출을 일으키거나 투자를 공격적으로 늘려도 결과가 돌아옵니다.")

        lines.append("\n**⚠️ 다 멈추고 현금을 쥐고 있어야 할 때 (손재수가 오는 해)**")

        lines.append("- 사주에서 **겁재/편관** 운이 들어오는 해입니다. 특히 '**겁재**' 해에는 친구, 친척의 달콤한 동업 제안, 확실해 보이는 투자처가 사실은 내 돈을 뺏어가는 덫입니다.")

        lines.append("- 이때는 보증 절대 금지, 동업 금지, 주식 등 변동성 자산을 처분하고 예/적금으로 현금을 묶어두십시오.")

        sw = b["sw"]

        sw_ss = sw.get("십성_천간", "")

        lines.append(f"\n👉 **그래서 올해({b['cur_year']}년)는 어떤가?**")

        lines.append(f"올해는 **{sw.get('세운', '')} [{sw_ss}]** 의 기운입니다.")

        cur_money_guide = {
            "偏財": "🔥 **투자 적기입니다.** 자본을 굴리거나 사업을 확장하십시오. 다만 쓸 데 없는 과소비만 조심하십시오.",
            "正財": "✅ **안정적인 수확기입니다.** 하던 일을 꾸준히 하며 차곡차곡 수익을 내십시오. 투기만 안 하면 쌓이는 해입니다.",
            "劫財": "🛑 **위험 경보!** 내 재물을 누가 탐내는 해입니다. 신규 투자, 동업, 금전 대여를 모두 거절해야 돈을 지킵니다.",
            "比肩": "💪 **내가 직접 뛰어야 버는 해입니다.** 남에게 맡기지 말고, 내 힘과 아이디어로 승부하십시오.",
            "食神": "🌱 **새로운 파이프라인(부업/창업)을 열기 좋은 해입니다.** 하고 싶었던 아이템이 있다면 소규모로 시작해보십시오.",
            "傷官": "⚠️ **직장 그만두고 사업하고 싶은 충동이 강해지는 해입니다.** 철저한 준비 없이 욱하는 마음으로 움직이면 돈이 묶입니다.",
            "偏官": "💼 **재물보다는 일 자체가 고되고 힘든 해입니다.** 돈을 벌기 위해 건강을 잃을 수 있으니 무리한 목표는 낮추십시오.",
            "正官": "🏢 **직장 운이 좋고 명예가 오릅니다.** 승진이나 연봉 협상에서 유리한 위치를 점할 수 있습니다.",
            "正印": "📚 **부동산 취득이나 문서 계약, 내 자격을 업그레이드하여 가치를 높이기에 최적의 해입니다.**",
            "偏印": "❓ **판단 착오를 조심하십시오.** 남의 말만 믿고 재테크나 코인 등에 손을 대면 묶이기 쉬운 답답한 시기입니다.",
        }

        lines.append(cur_money_guide.get(sw_ss, "무난한 시기입니다. 하던 대로 꾸준함을 유지하십시오."))

        return "\n".join(lines)

    @staticmethod
    def relations(pils, name, birth_year, gender, marriage="미혼"):
        """💑 궁합/결혼/관계 분석 ― 나와 맞는 인연은 어떤 모습일까?"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "사주 데이터를 불러오지 못했습니다."

        lines = []

        lines.append(f"## 💑 {name}님의 평생 인연과 관계 분석")

        lines.append(f"*사주에서 인연은 나에게 부족한 기운을 채워주는 사람, 혹은 내 기운이 자연스럽게 흘러가는 사람을 의미합니다.*\n")

        ilgan = b["ilgan"]

        ilju_key = b["ilju_key"]

        ss_list = b["ss_list"]

        try:
            from manse import ILJJ_SPOUSE

            spouse_desc = ILJJ_SPOUSE.get(ilju_key, "")

        except Exception:
            spouse_desc = ""

        # 1. 일주로 보는 타고난 배우자 자리

        lines.append("### 🏡 내가 무의식적으로 끌리는 배우자상 (일주론)")

        if spouse_desc:
            lines.append(spouse_desc)

        else:
            lines.append("부부 궁(일지)의 기운을 보았을 때, 서로의 영역을 존중하면서도 정신적인 교류가 될 수 있는 인연이 좋습니다.")

        lines.append("\n**[일간(나의 본질)별 조언]**")

        spouse_by_ilgan = {
            "甲": "곧고 강직한 성품 탓에 부러지기 쉽습니다. 나를 유연하게 만들어주고 편안하게 품어주는 사람(수/토 기운)이 좋습니다.",
            "乙": "섬세하고 감성적입니다. 의지할 수 있는 단단하고 든든한 사람(금/토 기운) 혹은 나를 밝게 이끌어주는 사람(화 기운)이 맞습니다.",
            "丙": "열정적이고 확산하는 기질입니다. 내 불같은 에너지를 차분하게 식혀주고 통제해 줄 수 있는 지혜로운 사람(수 기운)이 필요합니다.",
            "丁": "자상하고 섬세한 촛불 같습니다. 묵묵히 내 가치를 알아주고 땔감이 되어줄 든든하고 우직한 사람(목 기운)이 최고입니다.",
            "戊": "큰 산처럼 우직합니다. 답답할 수 있는 나를 활기차게 흔들어주고 생기를 불어넣어 줄 다이나믹한 사람(수/목 기운)이 좋습니다.",
            "己": "실속을 챙기고 포용력이 좋습니다. 때로는 내 스케일을 키워줄 수 있는 대범하고 밝은 사람(화/금 기운)과 시너지가 납니다.",
            "庚": "의리가 강하고 한번 믿으면 끝까지 갑니다. 너무 예리한 나를 부드럽게 녹여줄 온화하고 다정한 사람(화/수 기운)을 만나야 합니다.",
            "辛": "예민하고 완벽주의 성향이 있습니다. 내 까다로움을 너그럽게 받아주고 씻어주는 스케일 큰 사람(수 기운)이 천생연분입니다.",
            "壬": "속을 알 수 없이 깊고 지혜롭습니다. 내 안의 우울함이나 정체를 막아주고 끊임없이 대화가 통하는 재치있는 사람(목/화 기운)이 좋습니다.",
            "癸": "감수성이 뛰어나고 적응력이 좋습니다. 변덕스러운 내 마음을 굳건히 잡아줄 변함없는 사람(금/토 기운)과 인연이 닿습니다.",
        }

        lines.append(spouse_by_ilgan.get(ilgan, ""))

        # 2. 십성 구조로 보는 연애 스타일

        lines.append("\n### 💞 연애와 결혼 타이밍 (십성 분석)")

        gwan = [s for s in ss_list if s.get("cg_ss") in ["偏官", "正官"] or s.get("jj_ss") in ["偏官", "正官"]]

        jae = [s for s in ss_list if s.get("cg_ss") in ["偏財", "正財"] or s.get("jj_ss") in ["偏財", "正財"]]

        if gender == "여":
            if gwan:
                lines.append(f"사주에 남자를 의미하는 관성(官星)이 **{len(gwan)}개** 있습니다.")

                if any(s.get("cg_ss") == "偏官" or s.get("jj_ss") == "偏官" for s in gwan):
                    lines.append(
                        "- **편관(나쁜 남자/카리스마/연하/외국인)**: 안정적인 공무원 스타일보다는 카리스마 있고 리더십 강한 스타일, 혹은 직업이 뚜렷하게(군경/의료/사업) 센 사람과 인연이 많습니다. 드라마틱한 연애를 자주 합니다."
                    )

                if any(s.get("cg_ss") == "正官" or s.get("jj_ss") == "正官" for s in gwan):
                    lines.append("- **정관(바른 사나이/안정/신뢰)**: 책임감이 강하고 직장이 번듯하며 가정적인 남성과 연이 좋습니다. 짜릿함보다는 안정감을 주는 만남이 지속됩니다.")

            else:
                lines.append(
                    "원국에 관성(남편성)이 겉으로 드러나지 않아, 조건을 따지기보다는 '코드와 대화가 통하는 사람'을 만나야 합니다. 연애보다 내 전문성과 경력이 먼저인 무관(無官) 사주 성향입니다."
                )

        else:  # 남성
            if jae:
                lines.append(f"사주에 여자를 의미하는 재성(財星)이 **{len(jae)}개** 있습니다.")

                if any(s.get("cg_ss") == "偏財" or s.get("jj_ss") == "偏財" for s in jae):
                    lines.append("- **편재(화려함/능력자/애인)**: 스케일이 크고 활동적이며, 연애 경험 자체를 즐기는 성향입니다. 개방적이고 화려한 스타일의 파트너와 인연이 많습니다.")

                if any(s.get("cg_ss") == "正財" or s.get("jj_ss") == "正財" for s in jae):
                    lines.append("- **정재(현모양처/알뜰함/보수적)**: 가정적이고 알뜰하며 나를 착실하게 내조해줄 수 있는 파트너상입니다. 연애가 길어지면 자연스레 결혼으로 넘어갑니다.")

            else:
                lines.append(
                    "원국에 재성(아내성)이 드러나지 않아, 이성에 대한 집착이 상대적으로 덜하거나 혼기를 놓칠 수 있습니다. 소개팅이나 중매보다는 일하다가 다가오는 인연, 동호회 등 자연스런 만남이 유리합니다."
                )

        sw = b["sw"]

        sw_ss = sw.get("십성_천간", "")

        if sw_ss in ["偏財", "正財", "正官", "偏官", "食神"] and marriage in [
            "미혼",
            "싱글",
        ]:
            lines.append(f"\n👉 **올해({b['cur_year']}년)는 새로운 좋은 인연이 들어올 가능성이 매우 높은 핵심 시기입니다.** 만남의 자리를 주저하지 마십시오!")

        return "\n".join(lines)

    @staticmethod
    def daily(pils, name, birth_year, gender):
        """☀️ 일일 운세 ― 오늘 뭐 하면 좋을까?"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "데이터를 불러오지 못했습니다."

        today = date.today()

        sw = b["sw"]

        sw_ss = sw.get("십성_천간", "")

        sw_gh = sw.get("길흉", "평")

        sw_gan = sw.get("세운", "")

        lines = []

        lines.append(f"## ☀️ {today.month}월 {today.day}일 일진(日辰) 분석 가이드")

        lines.append(f"*{b['cur_year']}년 {sw_gan}[{sw_ss}] 세운의 흐름 아래에서, 오늘 하루의 미세한 기운을 읽어냅니다.*\n")

        gh_msg = {
            "길": "✨ **상승 기류**: 중요한 결정을 내리거나, 계약, 오디션, 고백 등 미뤘던 용기를 내기 가장 좋은 날입니다. 결과가 유리하게 흘러갑니다.",
            "+": "✨ **상승 기류**: 중요한 결정을 내리거나, 미뤘던 일을 처리하면 속도가 붙고 좋은 소식을 들을 수 있는 날입니다.",
            "평": "⚖️ **평온 유지**: 어제와 다름없는 무난한 하루입니다. 새로운 무리수보다는 하던 일을 성실히 마무리하는 데 에너지를 쓰십시오.",
            "흉": "🛡️ **수비 모드**: 평소 안 하던 실수가 나오거나 타인과 감정싸움이 날 수 있습니다. 한 템포 쉬어가고 일찍 귀가하는 것이 상책입니다.",
            "-": "🛡️ **수비 모드**: 계획이 틀어질 수 있습니다. 운전 조심, 말조심, 그리고 중요한 결정사항은 내일로 미루십시오.",
        }

        lines.append(f"### 📍 오늘의 총평: {gh_msg.get(sw_gh, '평온한 기운이 흐릅니다.')}\n")

        lines.append("### 📋 오늘의 3분 분야별 지침")


        if sw_ss in ss_advice:
            for adv in ss_advice[sw_ss]:
                lines.append(adv)

        else:
            lines.append("차분하게 평범한 일상을 성실하게 수행하는 것이 최선의 액운막이입니다.")

        return "\n".join(lines)

    @staticmethod
    def monthly(pils, name, birth_year, gender):
        """📆 월별 운세 ― 6개월 심층 흐름"""

        b = LocalSajuNarrator._get_base(pils, name, birth_year, gender)

        if not b:
            return "월별 운세 데이터를 불러오지 못했습니다."

        today = date.today()

        cur_year = b["cur_year"]

        lines = []

        lines.append(f"## 📆 {name}님의 향후 6개월 정밀 다이어리")

        MONTH_JJ = [
            "",
            "寅",
            "卯",
            "辰",
            "巳",
            "午",
            "未",
            "申",
            "酉",
            "戌",
            "亥",
            "子",
            "丑",
        ]

        for i in range(6):
            m = today.month + i

            yr = cur_year + (m - 1) // 12

            m = ((m - 1) % 12) + 1

            jj = MONTH_JJ[m] if m < len(MONTH_JJ) else ""

            is_current = i == 0

            label = "📌 **이번 달**" if is_current else f"📅 **{yr}년 {m}월**"

            lines.append(f"### {label} — {jj}월(月)")

            # 월지 고유의 행동 지침

            m_guide = {
                "寅": "새 판을 짜고 출발을 선언하기 좋습니다. 고민을 멈추고 액션(결제, 시작)을 취하십시오.",
                "卯": "네트워킹. 사람을 많이 만나고 정보를 교환해야 좋은 기회가 찾아옵니다.",
                "辰": "일이 꼬이거나 지연될 수 있습니다. 벌린 일을 수습하고 중간 점검을 철저히 하십시오.",
                "巳": "열정이 끓어오릅니다. 나를 홍보하고 드러내며, 영업활동에 최적화된 달입니다.",
                "午": "결과가 눈에 보이는 달. 속도전이 승패를 가릅니다. 질질 끌지 말고 쇼부를 보십시오.",
                "未": "휴식과 재조정의 달. 체력이 방전되기 쉬우니 큰 결정은 미루고 건강검진 등을 챙기십시오.",
                "申": "과감한 커트라인. 내게 손해를 끼치는 인연이나 적자 나는 프로젝트를 가차 없이 끊어내십시오.",
                "酉": "완성도. 하던 일의 디테일을 높이고 마무리를 지어 성과급/결제 대금을 청구할 타이밍입니다.",
                "戌": "수비 방어선 구축. 쓸데없는 지출을 막고 다음 단계(내년/겨울)를 위한 비상금을 비축하십시오.",
                "亥": "지식 습득과 전략 수립. 새로운 트렌드를 공부하거나 중요한 문서를 작성하기에 최고입니다.",
                "子": "잠재 능력 극대화. 겉으로 나서기보다 스펙업, 어학, 자격증 공부에 집중하면 결과가 압도적입니다.",
                "丑": "인생의 추운 고비점. 변화를 주면 실패하기 쉽습니다. 지금의 자리를 묵묵히 지키고 인내하십시오.",
            }

            lines.append(f"> **월의 테마**: {LocalSajuNarrator.MONTH_JJ_SEASON.get(jj, '')}")

            lines.append(f"- **행동 지침**: {m_guide.get(jj, '흐름에 맡기며 유연하게 대처하십시오.')}")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def yearly(pils, name, birth_year, gender):
        """🎊 신년운세 ― 올해 전체 다이어리 (추가 확장 안함, 이미 future3에 자세히 넣었음)"""

        # yearly는 기존 1/2부에서 만든 방식+future3과 겹치므로 깔끔하게 처리

        cur_year = datetime.now().year
        return LocalSajuNarrator.future3(pils, name, birth_year, gender, "미혼").replace("미래 3년 심층 예측", f"{cur_year}년 신년 심층 리포트")

        # 주의: 여기엔 b가 없으니 예외처리 필요. 간단히 기존 1/2부로 된 yearly 사용.

    @staticmethod
    def quick_answer(question: str, pils: list, birth_year: int, gender: str) -> str:
        """빠른 질문에 대한 로컬 엔진 즉시 답변"""
        try:
            ilgan = pils[1]["cg"]
            ilp = ILGAN_PROFILE.get(ilgan, {})
            cur_year = datetime.now().year
            sw = get_yearly_luck(pils, cur_year)
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "보통")
            ys = get_yongshin(pils)
            yong = ys.get("종합_용신", [])
            gy = get_gyeokguk(pils)
            gname = gy.get("격국명", "") if gy else ""

            _Q_MAP = {
                "직장": (f"올해 {sw_ss} 세운이 흐릅니다. {sw_gh} 기운으로 직장 안정도는 "
                         f"{'높습니다. 승진·인정의 기운이 강합니다.' if sw_gh == '길' else '변화 가능성이 있습니다. 무리한 행동을 자제하세요.'}"),
                "재물": (f"{ilp.get('재물','재물 운이 꾸준히 흐르고 있습니다.')} "
                         f"올해 {sw_ss} 세운으로 재물 흐름은 {sw_gh}입니다."),
                "인연": (f"올해 {sw_ss} 기운이 인연 운에 영향을 줍니다. "
                         f"{ilp.get('연애','인연은 준비된 자에게 찾아옵니다.')}"),
                "건강": (f"{ilp.get('건강','건강 관리에 유의하세요.')} "
                         f"용신 오행({', '.join(yong)})을 강화하는 생활 습관이 중요합니다."),
                "사업": (f"{gname} 격국으로 사업 성향을 분석하면: {ilp.get('재물','')} "
                         f"올해 {sw_ss} 세운은 사업 기운이 {sw_gh}입니다."),
                "이사": (f"올해 {sw_ss} 세운이 이동·변화 기운과 연관됩니다. "
                         f"{'이동·이사에 좋은 시기입니다.' if sw_ss in ('偏印','偏財','傷官') else '신중하게 결정하십시오.'}"),
                "가족": (f"일간 {ilgan}({ilp.get('한글','')})의 가족 관계 기운: "
                         f"올해는 {sw_gh} 기운으로 가족과의 소통이 {'원활합니다.' if sw_gh == '길' else '주의가 필요합니다.'}"),
                "적성": (f"천직·적성: {ilp.get('직업','다양한 분야에서 능력을 발휘합니다.')} "
                         f"{gname} 격국으로 {ilp.get('본질','')[:30]}의 성향을 가지고 있습니다."),
                "조심": (f"올해 {sw_ss}({sw_gh}) 세운에서 가장 주의할 것: "
                         f"{'재물 지출과 인간관계 마찰' if '흉' in sw_gh else '과도한 확장과 무리한 투자'}입니다."),
            }
            for key, answer in _Q_MAP.items():
                if key in question:
                    return answer
            return f"일간 {ilgan}({ilp.get('한글','')}) 기준으로 분석하면: {ilp.get('본질','')} 올해({cur_year}) {sw_ss} 세운은 {sw_gh}입니다."
        except Exception:
            return ""


def detect_structure(ilgan, wolji_jj):

    jijang = JIJANGGAN.get(wolji_jj, [])

    if not jijang:
        return "일반격"

    junggi = jijang[-1]

    structure_type = TEN_GODS_MATRIX.get(ilgan, {}).get(junggi, "기타")

    return f"{structure_type}格"



# * BUG2 FIX: 일간=pils[1]["cg"], 월지=pils[2]["jj"] (pillar order: [시(0),일(1),월(2),년(3)])


@st.cache_data
def get_gyeokguk(pils):

    if len(pils) < 4:
        return None

    ilgan = pils[1]["cg"]  # ✅ 일간 (day stem)
    ilgan_oh = OH.get(ilgan, "")

    wolji = pils[2]["jj"]  # ✅ 월지 (month branch)

    jijang = JIJANGGAN.get(wolji, [])

    if not jijang:
        return None

    jeongi = jijang[-1]

    sipsung = TEN_GODS_MATRIX.get(ilgan, {}).get(jeongi, "기타")

    gyeok_name = f"{sipsung}格"

    cgs_all = [p["cg"] for p in pils]
    jjs_all = [p["jj"] for p in pils]

    is_toucht = jeongi in cgs_all

    if is_toucht:
        grade = "純格 - 월지 정기가 천간에 투출하여 격이 매우 청명하다!"

        grade_score = 95

    elif len(jijang) > 1 and jijang[-2] in cgs_all:
        grade = "雜格 - 중기가 투출, 격이 복잡하나 쓸모가 있다."

        grade_score = 70

    else:
        grade = "暗格 - 지장간에 숨어있어 격의 힘이 약하다."

        grade_score = 50

    # 외격 판단 — 종격(從格): 일간과 같은 오행 + 생해주는 오행이 없을 때
    _BIRTH_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    parent_oh = _BIRTH_R.get(ilgan_oh, "")
    _all_ohs = set(OH.get(c, "") for c in cgs_all + list(jijang) if OH.get(c))
    _support_absent = ilgan_oh not in _all_ohs and parent_oh not in _all_ohs
    if _support_absent:
        # 종강격(일간과 같은 오행 지배) 또는 종살격(관살이 지배)
        _ctrl_oh = next((k for k, v in {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}.items() if v == ilgan_oh), "")
        _dom = max(_all_ohs, key=lambda o: cgs_all.count(next((c for c in cgs_all if OH.get(c) == o), "X"))) if _all_ohs else ""
        if _dom == ilgan_oh:
            gyeok_name = "從强格(종강격)"
            grade = "外格 - 일간의 기운이 넘쳐 같은 오행에 종하는 특수격"
            grade_score = 88
        elif _dom == _ctrl_oh:
            gyeok_name = "從殺格(종살격)"
            grade = "外格 - 관살이 압도적으로 강해 일간이 종하는 특수격"
            grade_score = 85

    desc_data = GYEOKGUK_DESC.get(
        gyeok_name,
        {
            "summary": f"{gyeok_name}으로 독자적인 인생 노선을 개척하는 격이로다.",
            "lucky_career": "자유업/개인 사업",
            "caution": "잡기를 경계하라.",
            "god_rank": "용신과의 조화를 이룰 때 빛난다",
        },
    )

    return {
        "격국명": gyeok_name,
        "격의_등급": grade,
        "격의_순수도": grade_score,
        "월지": wolji,
        "정기": jeongi,
        "투출여부": is_toucht,
        "격국_해설": desc_data["summary"],
        "적합_진로": desc_data["lucky_career"],
        "경계사항": desc_data["caution"],
        "신급_판정": desc_data["god_rank"],
        "narrative": (
            f"🏛️ **격국 판별**: {gyeok_name}!\n"
            f"  월지 {wolji}의 정기 {jeongi}로 {'투출된 청명한 ' if is_toucht else '숨은 '}{gyeok_name}을 이루었도다.\n"
            f"  등급: {grade}\n  {desc_data['summary']}\n"
            f"  적합 분야: {desc_data['lucky_career']}\n  경계: {desc_data['caution']}"
        ),
    }


# 삼합/반합/방합

SAM_HAP_MAP = {
    frozenset(["寅", "午", "戌"]): ("火局", "火", "寅午戌 三合"),
    frozenset(["申", "子", "辰"]): ("水局", "水", "申子辰 三합"),
    frozenset(["巳", "酉", "丑"]): ("金局", "金", "巳酉丑 三合"),
    frozenset(["亥", "卯", "未"]): ("木局", "木", "亥卯未 三合"),
}

BAN_HAP_MAP = {
    frozenset(["寅", "午"]): ("寅午 半合(火)", "火", "半合"),
    frozenset(["午", "戌"]): ("午戌 半合(火)", "火", "半合"),
    frozenset(["申", "子"]): ("申子 半合(水)", "水", "반합"),
    frozenset(["子", "辰"]): ("子辰 半合(水)", "水", "반합"),
    frozenset(["巳", "酉"]): ("巳酉 半合(金)", "金", "반합"),
    frozenset(["酉", "丑"]): ("酉丑 半合(金)", "金", "반합"),
    frozenset(["亥", "卯"]): ("亥卯 半合(木)", "木", "반합"),
    frozenset(["卯", "未"]): ("卯未 半合(木)", "木", "반합"),
}

BANG_HAP_MAP = {
    frozenset(["寅", "卯", "辰"]): ("東方 木局", "木", "方合"),
    frozenset(["巳", "午", "未"]): ("南方 火局", "火", "方合"),
    frozenset(["申", "酉", "戌"]): ("西方 金局", "金", "方合"),
    frozenset(["亥", "子", "丑"]): ("北方 水局", "水", "方合"),
}


def get_yongshin(pils):
    """용신(用神) 종합 분석 - 억부+조후+통관"""

    ilgan = pils[1]["cg"]

    wol_jj = pils[2]["jj"]

    strength_info = get_ilgan_strength(ilgan, pils)

    oh_strength = strength_info["oh_strength"]

    sn = strength_info["신강신약"]

    ilgan_oh = OH.get(ilgan, "")

    BIRTH_MAP_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

    CONTROL_MAP = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    if sn == "신강(身强)":
        ok_관 = next((k for k, v in CONTROL_MAP.items() if v == ilgan_oh), "")

        ok_재 = CONTROL_MAP.get(ilgan_oh, "")

        eokbu_yong = [ok_관, ok_재]

        eokbu_base = "신강(身强) -> 억(抑) 용신 필요"

        eokbu_desc = f"강한 일간을 억제하는 관성({ok_관}기운)과 재성({ok_재}기운)이 용신입니다."

        kihwa = "인성/비겁 대운은 기신(忌神) - 더 강해져 흉작용"

    elif sn == "신약(身弱)":
        ok_인 = BIRTH_MAP_R.get(ilgan_oh, "")

        eokbu_yong = [ok_인, ilgan_oh]

        eokbu_base = "신약(身弱) -> 부(扶) 용신 필요"

        eokbu_desc = f"약한 일간을 도와주는 인성({ok_인}기운)과 비겁({ilgan_oh}기운)이 용신입니다."

        kihwa = "재성/관성 대운은 기신(忌神) - 약한 일간이 더 눌림"

    else:
        eokbu_yong = []

        eokbu_base = "중화(中和) -> 균형 유지"

        eokbu_desc = "오행이 균형 잡혀 특정 용신보다 전체 균형 유지가 중요합니다."

        kihwa = "어느 쪽으로도 과도하게 치우치는 운이 기신"

    jokhu = YONGSHIN_JOKHU.get(wol_jj, {})

    # 통관용신

    oh_list = sorted(oh_strength.items(), key=lambda x: -x[1])

    tongkwan_yong = None

    tongkwan_desc = ""

    if len(oh_list) >= 2:
        t1, v1 = oh_list[0]
        t2, v2 = oh_list[1]

        if v1 >= 35 and v2 >= 25:
            if CONTROL_MAP.get(t1) == t2 or CONTROL_MAP.get(t2) == t1:
                gen_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

                tongkwan_yong = gen_map.get(t1, "")

                tongkwan_desc = f"{t1}({OHN.get(t1, '')})와 {t2}({OHN.get(t2, '')})가 충돌. {tongkwan_yong}({OHN.get(tongkwan_yong, '')}) 통관용신 필요."

    all_yong = list(dict.fromkeys(eokbu_yong + [OH.get(c, "") for c in jokhu.get("need", [])] + ([tongkwan_yong] if tongkwan_yong else [])))

    all_yong = [o for o in all_yong if o]

    # 병약용신(病藥用神): 가장 강한 오행이 병(病)이면 그것을 제어하는 오행이 약(藥)
    byeong_yong = None
    byeong_desc = ""
    if oh_list:
        strongest_oh, strongest_val = oh_list[0]
        if strongest_val >= 40:  # 한 오행이 40% 이상 독점 → 병(病)으로 판단
            # 병(病)을 극하는 오행 = 약(藥)
            byeong_yong = CONTROL_MAP.get(strongest_oh, "")
            byeong_desc = (
                f"{strongest_oh}({OHN.get(strongest_oh, '')}) 기운이 과도({strongest_val:.0f}%)하여 병(病)을 이룸. "
                f"이를 제어하는 {byeong_yong}({OHN.get(byeong_yong, '')}) 기운이 병약용신(病藥用神)입니다."
            )
            if byeong_yong and byeong_yong not in all_yong:
                all_yong.append(byeong_yong)

    return {
        "억부_base": eokbu_base,
        "억부_desc": eokbu_desc,
        "억부_용신": eokbu_yong,
        "조후_desc": jokhu.get("desc", ""),
        "조후_need": jokhu.get("need", []),
        "조후_avoid": jokhu.get("avoid", []),
        "통관_yong": tongkwan_yong,
        "통관_desc": tongkwan_desc,
        "병약_yong": byeong_yong,
        "병약_desc": byeong_desc,
        "기신": kihwa,
        "종합_용신": all_yong,
        "월지": wol_jj,
    }


# ==================================================

#  충(沖)/형(刑)/파(破)/해(害)/천간합

# ==================================================

# CHUNG_MAP is updated above

HYUNG_MAP = {
    frozenset(["寅", "巳", "申"]): ("寅巳申 三刑", "無恩之刑", "법적 문제, 관재, 배신"),
    frozenset(["丑", "戌", "未"]): (
        "丑戌未 三刑",
        "持勢之刑",
        "권력 다툼, 재물 분쟁, 고집의 화",
    ),
    frozenset(["子", "卯"]): ("子卯 相刑", "無禮之刑", "무례한 인간관계, 배신"),
}

SELF_HYUNG = ["辰", "午", "酉", "亥"]

PA_MAP = {
    frozenset(["子", "酉"]): ("子酉破", "감정 상처, 이별"),
    frozenset(["丑", "辰"]): ("丑辰破", "재물 파손, 직업 변동"),
    frozenset(["寅", "亥"]): ("寅亥破", "계획 차질, 예상 밖 변수"),
    frozenset(["卯", "午"]): ("卯午破", "감정 충돌, 혼인 불화"),
    frozenset(["申", "巳"]): ("申사파(申巳破)", "사고 위험, 계획 좌절"),
    frozenset(["戌", "未"]): ("戌未破", "재물 분실, 고집 충돌"),
}

HAE_MAP = {
    frozenset(["子", "未"]): ("자미 육해(六害)", "원망과 불신 (怨望/不信)"),
    frozenset(["丑", "午"]): ("축오 육해(六害)", "성급함과 갈등 (性急/葛藤)"),
    frozenset(["寅", "巳"]): ("인사 육해(六害)", "시기심과 상처 (猜忌/傷處)"),
    frozenset(["卯", "辰"]): ("묘진 육해(六害)", "오해와 불화 (誤解/不和)"),
    frozenset(["申", "亥"]): ("신해 육해(六害)", "단절과 고립 (斷絶/孤立)"),
    frozenset(["酉", "戌"]): ("유술 육해(六害)", "신뢰 상실과 피해 (信賴 喪失)"),
}

TG_HAP_MAP = {
    frozenset(["甲", "己"]): ("甲己合", "土", "中正之合"),
    frozenset(["乙", "庚"]): ("乙庚合", "金", "仁義之合"),
    frozenset(["丙", "辛"]): ("丙辛合", "水", "威制之合"),
    frozenset(["丁", "壬"]): ("丁壬合", "木", "淫匿之合"),
    frozenset(["戊", "癸"]): ("戊癸合", "火", "無情之合"),
}


def get_yukjin(ilgan, pils, gender="남"):


    ss_to_family = {
        '比肩': '형제·자매·친구',
        '劫財': '형제·자매·경쟁자',
        '食神': '자녀·제자',
        '傷官': '자녀·제자',
        '偏財': '아버지·애인',
        '正財': '아버지·배우자',
        '偏官': '자녀(남)·직장상사',
        '正官': '남편·직장',
        '偏印': '어머니·이모',
        '正印': '어머니·윗사람',
    }

    sipsung_data = calc_sipsung(ilgan, pils)

    found = {}

    for i, ss_info in enumerate(sipsung_data):
        label = ["시주", "일주", "월주", "년주"][i]

        p = pils[i]

        for ss in [ss_info.get("cg_ss", "-"), ss_info.get("jj_ss", "-")]:
            fam = ss_to_family.get(ss)

            if fam:
                if fam not in found:
                    found[fam] = []

                found[fam].append(f"{label}({p['str']})")

    result = []

    checks = [
        (
            "어머니(正印)",
            "정인",
            "인성이 있어 어머니의 음덕(蔭德)이 큽니다.",
            "정인(어머니 기운)이 약합니다. 어머니와의 인연이 엷거나 일찍 독립하는 기운입니다.",
        ),
        (
            "아버지(偏財)",
            "편재",
            "편재(아버지 기운)가 있습니다. 아버지의 재물적 도움이 있거나 부친 덕이 있습니다.",
            "편재(아버지 기운)가 약합니다. 부친과의 인연이 엷거나 일찍 독립하는 기운입니다.",
        ),
    ]

    if gender == "남":
        checks += [
            (
                "아내(正財)",
                "정재",
                "정재(아내 기운)가 있습니다. 배우자 인연이 있고 가정적인 아내를 만날 기운입니다.",
                "정재(아내 기운)가 약합니다. 결혼이 늦거나 대운에서 재성운이 올 때 인연이 찾아옵니다.",
            ),
            (
                "아들(偏官)/딸(正官)",
                "편관",
                "관살이 있습니다. 자녀 인연이 있으며 자녀로 인한 기쁨이 있습니다.",
                "관살이 약합니다. 자녀와의 인연이 엷거나 늦게 생길 수 있습니다.",
            ),
        ]

    else:
        checks += [
            (
                "남편(正官)",
                "정관",
                "정관(남편 기운)이 있습니다. 안정적이고 믿음직한 남편 인연이 있습니다.",
                "정관(남편 기운)이 없거나 약합니다. 결혼이 늦거나 편관으로 대체될 수 있습니다.",
            ),
            (
                "아들(食神)/딸(傷官)",
                "식신",
                "식상이 있습니다. 자녀 인연이 있으며 자녀로 인한 기쁨이 있습니다.",
                "식상이 약합니다. 자녀와의 인연이 엷거나 늦을 수 있습니다.",
            ),
        ]

    checks.append(
        (
            "형제(比肩)",
            "비견",
            "비겁이 있습니다. 형제자매 또는 동료/친구와의 인연이 깊습니다.",
            "비겁이 약합니다. 형제자매 인연이 엷거나 자립심이 강한 독립적인 기질입니다.",
        )
    )

    sipsung_all = [ss for si in sipsung_data for ss in [si.get("cg_ss", "-"), si.get("jj_ss", "-")]]

    for fam_label, ss_key, yes_msg, no_msg in checks:
        has = ss_key in sipsung_all

        where = ", ".join(found.get(fam_label, []))

        result.append(
            {
                "관계": fam_label,
                "위치": where if where else "없음",
                "present": has,
                "desc": yes_msg if has else no_msg,
            }
        )

    return result


# ==================================================

#  추가 신살 (원진/귀문관/백호/양인/화개)

# ==================================================



def get_special_stars(pils):
    """신살 계산 (tab_special_stars에서 분리)"""

    ilgan = pils[1]["cg"]

    pil_jjs = [p["jj"] for p in pils]

    result = []

    # 천을귀인

    chunl = {
        "甲": ["丑", "未"],
        "乙": ["子", "申"],
        "丙": ["亥", "酉"],
        "丁": ["亥", "酉"],
        "戊": ["丑", "未"],
        "己": ["子", "申"],
        "庚": ["丑", "未"],
        "辛": ["寅", "午"],
        "壬": ["卯", "巳"],
        "癸": ["卯", "巳"],
    }

    if any(jj in chunl.get(ilgan, []) for jj in pil_jjs):
        found = [jj for jj in pil_jjs if jj in chunl.get(ilgan, [])]

        result.append(
            {
                "name": f"천을귀인(天乙(을)貴人) [{','.join(found)}]",
                "desc": "하늘이 내리신 최고의 귀인성. 위기 때마다 귀인이 나타나 도와줍니다.",
            }
        )

    # 역마살

    yeokma = {
        "寅": "申",
        "午": "申",
        "戌": "申",
        "申": "寅",
        "子": "寅",
        "辰": "寅",
        "巳": "亥",
        "酉": "亥",
        "丑": "亥",
        "亥": "巳",
        "卯": "巳",
        "未": "巳",
    }

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    if wol_jj and yeokma.get(wol_jj, "") in pil_jjs:
        result.append({"name": "역마살(驛馬殺)", "desc": "평생 이동/여행/해외와 인연이 깊습니다."})

    # 도화살

    dohwa = {
        "寅": "卯",
        "午": "卯",
        "戌": "卯",
        "申": "酉",
        "子": "酉",
        "辰": "酉",
        "亥": "子",
        "卯": "子",
        "未": "子",
        "巳": "午",
        "酉": "午",
        "丑": "午",
    }

    if wol_jj and dohwa.get(wol_jj, "") in pil_jjs:
        result.append(
            {
                "name": "도화살(桃花殺)",
                "desc": "이성의 인기를 한몸에 받는 매력의 신살입니다.",
            }
        )

    # 문창귀인(文昌貴人) — 일간 기준 학문·총명의 귀인
    mc_jj = MUNCHANG_MAP.get(ilgan, "")
    if mc_jj and mc_jj in pil_jjs:
        result.append({
            "name": f"문창귀인(文昌貴人) [{mc_jj}]",
            "desc": "총명함과 학문적 재능을 나타내는 귀인성. 글·말·학업에서 두각을 나타냅니다.",
        })

    # 겁살(劫殺) — 년지/일지 기준 삼합국 → 겁살지지가 사주에 있는지
    _nyon_jj = pils[3]["jj"] if len(pils) > 3 else ""
    _il_jj = pils[1]["jj"] if len(pils) > 1 else ""
    for _ref_jj in [_nyon_jj, _il_jj]:
        _geop_jj = GEOP_MAP.get(_ref_jj, "")
        if _geop_jj and _geop_jj in pil_jjs:
            result.append({
                "name": f"겁살(劫殺) [{_geop_jj}]",
                "desc": "외부의 갑작스러운 충격·강탈·사고 기운. 투자·보증·동업을 각별히 조심하십시오.",
            })
            break

    # 망신살(亡身殺) — 구설·배신·체면 손상
    for _ref_jj in [_nyon_jj, _il_jj]:
        _ms_jj = MANGSHIN_MAP.get(_ref_jj, "")
        if _ms_jj and _ms_jj in pil_jjs:
            result.append({
                "name": f"망신살(亡身殺) [{_ms_jj}]",
                "desc": "구설수·스캔들·배신의 기운. 언행을 조심하고 비밀 관리를 철저히 하십시오.",
            })
            break

    # 화개살(華蓋殺) — 예술·종교·고독의 기운 (HWAGAE_MAP 기준 보강)
    _hg_found = []
    for _ref_jj in [_nyon_jj, _il_jj, wol_jj]:
        _hg_jj = HWAGAE_MAP.get(_ref_jj, "")
        if _hg_jj and _hg_jj in pil_jjs and _hg_jj not in _hg_found:
            _hg_found.append(_hg_jj)
    if _hg_found:
        result.append({
            "name": f"화개살(華蓋殺) [{','.join(_hg_found)}]",
            "desc": "예술적 재능과 종교·철학적 심성이 깊은 기운. 고독을 즐기며 내면을 다지면 크게 빛납니다.",
        })

    return result


def get_ohang_health_info(ilgan, pils):
    """오행 신체 건강 분석 — 부족/과다 오행 기준 취약 장기 반환"""
    try:
        oh_strength = calc_ohaeng_strength(ilgan, pils)
    except Exception:
        return []

    results = []
    for oh, pct in oh_strength.items():
        body = OHANG_BODY.get(oh)
        if not body:
            continue
        if pct <= 10:
            results.append({
                "오행": oh,
                "상태": "부족",
                "점수": pct,
                "장기": body["장기"],
                "증상": body["증상"],
                "음식": body["음식"],
                "주의": body["주의"],
                "desc": f"【{oh} 기운 부족 — {pct:.0f}%】 {body['장기']} 취약. 보완 음식: {body['음식']}",
            })
        elif pct >= 40:
            results.append({
                "오행": oh,
                "상태": "과다",
                "점수": pct,
                "장기": body["장기"],
                "증상": body["증상"],
                "음식": body["음식"],
                "주의": body["주의"],
                "desc": f"【{oh} 기운 과다 — {pct:.0f}%】 {body['증상']} 주의. {body['주의']}",
            })

    results.sort(key=lambda x: abs(x["점수"] - 25), reverse=True)
    return results


def get_crossing_interpretation(pils, cur_year):
    """세운×대운 교차 해석 — 대운 십성과 세운 십성의 조합으로 핵심 키워드 반환"""
    try:
        ilgan = pils[1]["cg"]
        birth_year = pils[0]["year"] if pils[0] and "year" in pils[0] else 1980
        birth_month = 1
        birth_day = 1
        birth_hour = 12
        birth_minute = 0
        daewoon = SajuCoreEngine.get_daewoon(
            pils, birth_year, birth_month, birth_day,
            birth_hour, birth_minute, gender="남"
        )
        cur_dw = next((d for d in daewoon if d["시작연도"] <= cur_year <= d["종료연도"]), None)
        sw = get_yearly_luck(pils, cur_year)

        if not cur_dw or not sw:
            return {"summary": "", "finance": "", "career": "", "health": "", "relation": ""}

        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw.get("cg", ""), "")
        sw_ss = sw.get("십성_천간", "")
        sw_gil = sw.get("길흉", "평")

        # 대운·세운 십성 조합 매핑
        _CROSS_MAP = {
            ("正官", "正官"): {"summary": "명예와 승진이 겹치는 최고의 출세 운", "career": "승진·이직·공직 도전에 최적"},
            ("正官", "偏官"): {"summary": "조직 내 긴장과 경쟁 심화", "career": "직장 내 경쟁 심화, 실력으로 돌파"},
            ("偏官", "偏官"): {"summary": "강렬한 도전과 변화의 시기", "career": "과감한 이직·창업 도전 가능"},
            ("食神", "偏財"): {"summary": "재능이 돈으로 직결되는 황금 조합", "finance": "사업·부업 확장 시도"},
            ("食神", "正財"): {"summary": "꾸준한 노력이 안정적 수입으로 연결", "finance": "저축·투자 계획 실행"},
            ("偏財", "食神"): {"summary": "창의적 아이디어가 큰 수익으로", "finance": "신사업·신상품 출시 적기"},
            ("正財", "正財"): {"summary": "가장 안정적인 재물 운", "finance": "부동산·장기 투자 검토"},
            ("偏印", "食神"): {"summary": "창작 에너지가 절정, 단 결실 주의", "career": "창작·연구·개발에 집중"},
            ("正印", "正官"): {"summary": "학문과 명예가 합치는 귀인 대운", "career": "자격증·시험·관직 도전"},
            ("比肩", "劫財"): {"summary": "경쟁과 변동이 극심한 시기", "finance": "동업·보증 절대 금지"},
            ("劫財", "比肩"): {"summary": "독립 도전과 경쟁의 시기", "career": "창업 또는 독립 선언"},
        }

        cross_key = (dw_ss, sw_ss)
        cross_info = _CROSS_MAP.get(cross_key, {})

        # 기본 요약 생성
        _GIL_MAP = {
            "대길": "매우 좋은 운기",
            "길": "좋은 운기",
            "평": "평범한 운기",
            "흉": "주의가 필요한 운기",
            "대흉": "각별히 조심해야 할 운기",
        }
        gil_desc = _GIL_MAP.get(sw_gil, "")

        summary = cross_info.get("summary", f"{dw_ss} 대운에 {sw_ss} 세운 — {gil_desc}")
        finance = cross_info.get("finance", f"재물: {sw_gil} 운기. 과도한 지출 자제하고 안전 자산 유지.")
        career = cross_info.get("career", f"직업: {sw_ss} 기운 활용. 현재 위치를 최대한 활용하는 전략 유효.")
        health = f"건강: {'활동적 시기이므로 과로와 스트레스 주의.' if sw_gil in ['길','대길'] else '기운이 약한 시기. 무리한 계획보다 건강 우선.'}"
        relation = f"인간관계: {'귀인 만남 가능성 높음. 새로운 인연을 적극적으로 받아들일 것.' if sw_gil in ['길','대길'] else '갈등 조심. 감정적 충돌보다 이성적 대화를 선택.'}"

        return {
            "dw_ss": dw_ss, "sw_ss": sw_ss, "sw_gil": sw_gil,
            "summary": summary, "finance": finance,
            "career": career, "health": health, "relation": relation,
        }
    except Exception as _e:
        _saju_log.debug("[crossing_interp] %s", _e)
        return {"summary": "", "finance": "", "career": "", "health": "", "relation": ""}


def get_relationship_reading(pils, gender="남", marriage_status="미혼"):
    """결혼/연애운 해석 — 일주·십성·신살 기반 종합 연애·결혼 분석"""
    try:
        ilgan = pils[1]["cg"] if len(pils) > 1 else ""
        iljj = pils[1]["jj"] if len(pils) > 1 else ""
        ilgan_oh = OH.get(ilgan, "")

        # 배우자 자리(일지) 십성
        partner_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(iljj, "")

        _SS_KR = {
            "食神": "식신", "傷官": "상관", "偏財": "편재", "正財": "정재",
            "偏官": "편관", "正官": "정관", "偏印": "편인", "正印": "정인",
            "比肩": "비견", "劫財": "겁재",
        }
        partner_ss_kr = _SS_KR.get(partner_ss, partner_ss)

        # 일지 십성별 배우자 기질
        _ILJJ_SS_PARTNER = {
            "食神":  "여유롭고 배려 깊은 배우자. 가정적이며 먹복·자녀복 있음.",
            "傷官":  "재능 있고 개성 강한 배우자. 이성미 넘치나 관계 유지에 노력 필요.",
            "偏財":  "활동적이고 사업 수완 있는 배우자. 다정하나 이성 인연 조심.",
            "正財":  "성실하고 검소한 배우자. 가정에 충실하며 재물 관리 능력 우수.",
            "偏官":  "강하고 카리스마 있는 배우자. 열정적이나 갈등도 잦을 수 있음.",
            "正官":  "책임감 강하고 신뢰할 수 있는 배우자. 사회적으로 인정받는 사람.",
            "偏印":  "자유로운 영혼의 배우자. 다재다능하나 정착이 어려울 수 있음.",
            "正印":  "학식 있고 지적인 배우자. 배우자 덕이 강하고 어머니 역할에 충실.",
            "比肩":  "비슷한 성향의 배우자. 경쟁적 관계가 될 수 있어 역할 분담 중요.",
            "劫財":  "활동적이고 승부욕 강한 배우자. 재물 기복 있으니 경제 관리 필요.",
        }
        partner_desc = _ILJJ_SS_PARTNER.get(partner_ss, f"{partner_ss_kr} 기운의 배우자 자리. 이 기운에 맞는 인연이 자연스럽게 온다.")

        # 오행별 이상형/결합 방식
        _OH_LOVE = {
            "木": "이상적이고 원칙적인 이성을 선호. 공감보다 존중을 원하는 타입.",
            "火": "열정적이고 활동적인 이성에게 끌림. 감정 표현이 화끈해 첫 만남이 강렬.",
            "土": "안정적이고 신뢰할 수 있는 이성을 원함. 오래 알고 난 후 사귀는 경향.",
            "金": "원칙과 격식이 있는 이성을 좋아함. 완벽주의적 이상형 기준이 높음.",
            "水": "지적이고 감성 깊은 이성에게 끌림. 감정적 교감을 가장 중시.",
        }
        love_style = _OH_LOVE.get(ilgan_oh, "")

        # 신살 체크 (도화살, 홍염살 등 연애 신살)
        sinsal = get_12sinsal(pils) if pils else []
        love_sinsal = []
        for s in sinsal:
            n = s.get("이름") or s.get("name") or ""
            if any(k in n for k in ["도화", "홍염", "천을귀인", "월덕귀인"]):
                love_sinsal.append(n)

        # 결혼 시기 힌트 (일지 12운성 기반)
        unsung_list = calc_12unsung(ilgan, pils) if pils else []
        iljj_unsung = ""
        for u in unsung_list:
            if u.get("기둥") in ["일주", "일지"]:
                iljj_unsung = u.get("운성", "")
                break

        _UNSUNG_MARRY = {
            "長生": "결혼운이 밝고 배우자 복이 있음.",
            "건록": "자립 후 결혼이 안정적. 독립 기반 마련 후 인연.",
            "제왕": "강한 파트너와 인연. 서로 주도권 조율이 중요.",
            "衰": "늦은 인연이 오래감. 서두르지 말 것.",
            "病": "건강한 배우자 선택이 중요. 건강 체크 후 결혼 결정.",
            "死": "재혼 인연이 있거나 특별한 운명적 만남.",
            "묘": "숨겨진 인연. 예상치 못한 곳에서 만남.",
            "절": "자유로운 연애 후 늦은 결혼. 이동이 많은 파트너와 인연.",
        }
        marry_hint = _UNSUNG_MARRY.get(iljj_unsung, "")

        is_married = marriage_status == "기혼"
        status_label = "배우자" if is_married else "연인·배우자"

        result = {
            "파트너_십성": partner_ss_kr,
            "파트너_기질": partner_desc,
            "연애_스타일": love_style,
            "결혼_힌트": marry_hint,
            "연애_신살": love_sinsal,
            "기혼여부": is_married,
            "status_label": status_label,
        }
        return result
    except Exception as _e:
        _saju_log.debug("[relationship_reading] %s", _e)
        return {}


def get_health_reading(pils):
    """건강운 종합 해석 — 오행 불균형·일간·대운 기반 신체 분석"""
    try:
        ilgan = pils[1]["cg"] if len(pils) > 1 else ""
        ilgan_oh = OH.get(ilgan, "")

        oh_strength = calc_ohaeng_strength(ilgan, pils) or {}
        health_info = get_ohang_health_info(ilgan, pils) or []

        # 오행별 건강 요약
        weak_items = [h for h in health_info if h.get("상태") == "부족"]
        over_items = [h for h in health_info if h.get("상태") == "과다"]

        # 일간 오행 기반 선천적 취약 장기
        _ILGAN_HEALTH = {
            "甲": "간·담낭·눈·신경계가 선천적으로 주의 포인트. 과로와 음주를 피하고 눈 건강을 정기적으로 체크.",
            "乙": "간·담낭·척추·관절이 취약. 스트레칭과 충분한 수면으로 신경계 보호.",
            "丙": "심장·혈관·혈압이 선천적 주의 포인트. 격한 감정 변화와 과식을 피하고 정기 심혈관 검진 권장.",
            "丁": "심장·소장·혀·신경계 주의. 과도한 사색과 스트레스가 심장에 부담. 명상과 충분한 수면 필수.",
            "戊": "비장·위장·췌장·관절 취약. 불규칙한 식사와 과식이 직접 건강을 해침.",
            "己": "위장·비장·췌장·소화기 주의. 걱정과 스트레스가 위장에 바로 영향. 소화기 정기 검진.",
            "庚": "폐·대장·기관지·코·피부 취약. 호흡기 건강 관리와 금연이 핵심.",
            "辛": "폐·기관지·피부·코 주의. 건조한 환경과 감기에 약함. 충분한 수분 섭취 필수.",
            "壬": "신장·방광·생식기·허리 취약. 냉증에 약하므로 체온 유지가 건강 관리의 핵심.",
            "癸": "신장·방광·허리·골 주의. 냉증과 부종 조심. 따뜻한 음식과 충분한 숙면 권장.",
        }
        ilgan_health = _ILGAN_HEALTH.get(ilgan, "")

        # 세부 처방 생성
        prescriptions = []
        for h in health_info[:2]:  # 최대 2개
            oh = h.get("오행", "")
            state = h.get("상태", "")
            food = h.get("음식", "")
            note = h.get("주의", "")
            if state == "부족":
                prescriptions.append(f"{oh} 기운 보강: {food}을 꾸준히 섭취. {note}")
            elif state == "과다":
                prescriptions.append(f"{oh} 기운 조절 필요: {note}에 주의. 제어 오행 음식으로 균형.")

        return {
            "일간_건강": ilgan_health,
            "부족_오행": weak_items,
            "과다_오행": over_items,
            "처방": prescriptions,
            "health_info": health_info,
        }
    except Exception as _e:
        _saju_log.debug("[health_reading] %s", _e)
        return {}


class HanjaSafeDict(dict):
    def get(self, key, default=None):
        if not isinstance(key, str):
            return super().get(key, default)

        clean_k = re.sub(r"\(.*?\)", "", key).strip()

        if key in self:
            return self[key]
        if clean_k in self:
            return self[clean_k]

        for k in self.keys():
            if isinstance(k, str) and re.sub(r"\(.*?\)", "", k).strip() == clean_k:
                return self[k]

        return default


def make_hanja_safe(d):
    if not isinstance(d, dict):
        return d
    new_d = HanjaSafeDict()
    for k, v in d.items():
        new_d[k] = make_hanja_safe(v)
    return new_d


# Apply to all relevant global dictionaries
OH = make_hanja_safe(OH)
TEN_GODS_MATRIX = make_hanja_safe(TEN_GODS_MATRIX)
ILGAN_CHAR_DESC = make_hanja_safe(ILGAN_CHAR_DESC)
HEALTH_OH = make_hanja_safe(HEALTH_OH)
GYEOKGUK_DESC = make_hanja_safe(GYEOKGUK_DESC)
STRENGTH_NARRATIVE = make_hanja_safe(STRENGTH_NARRATIVE)
CAREER_MATRIX = make_hanja_safe(CAREER_MATRIX)


# ----------------- HANJA SAFE INJECT END -----------------
def _nar_ch1_ilgan(ctx):
    """1~5장: 일간 기질 + 신강신약 + 인생흐름 + 나이대분석 + 올해메시지 + 만신한마디"""

    ilgan = ctx.get("ilgan", "")
    ilgan_kr = ctx.get("ilgan_kr", "")
    iljj = ctx.get("iljj", "")
    iljj_kr = ctx.get("iljj_kr", "")
    display_name = ctx.get("display_name", "내담자")
    birth_year = ctx.get("birth_year", 1980)
    sn = ctx.get("sn", "")
    strength_info = ctx.get("strength_info", {})
    char = ctx.get("char", {})
    sn_narr = ctx.get("sn_narr", "")
    current_age = ctx.get("current_age", 40)
    current_year = ctx.get("current_year", 2026)
    sw_now = ctx.get("sw_now", {}) or {}
    cur_dw = ctx.get("cur_dw", {}) or {}
    daewoon = ctx.get("daewoon", []) or []

    ilp = ILGAN_PROFILE.get(ilgan, {})
    profile_bonzil = ilp.get("본질", char.get("성격_핵심", ""))
    profile_jangjeom = ilp.get("장점", char.get("장점", ""))
    profile_daknjeom = ilp.get("단점", char.get("단점", ""))
    profile_jikup = ilp.get("직업", "")
    profile_jaemul = ilp.get("재물", "")
    profile_yeonae = ilp.get("연애", "")
    profile_geongang = ilp.get("건강", "")
    profile_chobang = ilp.get("처방", "")

    jangjeom_list = [j.strip() for j in profile_jangjeom.split(",") if j.strip()][:3]
    daknjeom_list = [d.strip() for d in profile_daknjeom.split(".") if d.strip()][:3]

    sn_advice = (
        "신강한 사주는 직접 움직여야 기회가 옵니다. 수동적으로 기다리면 아무것도 이루지 못합니다."
        if "신강" in sn else
        "신약한 사주는 귀인과 함께할 때 가장 강합니다. 좋은 파트너와 스승이 운명을 바꾸는 열쇠입니다."
        if "신약" in sn else
        "중화 사주는 꾸준함이 가장 큰 무기입니다. 한 분야를 깊이 파고드는 전략이 가장 효과적입니다."
    )

    # 현재 나이대 분석
    if current_age < 30:
        age_stage, age_msg = "청년기 초반", (
            f"지금은 기반을 닦는 가장 중요한 시기입니다. {ilgan_kr} 일간의 강점을 살려 방향을 확실히 잡아야 합니다. "
            f"이 시기의 선택이 앞으로 20년의 궤도를 결정합니다. 재능을 아낌없이 펼치십시오. "
            f"실패를 두려워 말고, 지금의 경험이 곧 자산임을 기억하십시오."
        )
    elif current_age < 40:
        age_stage, age_msg = "청년기", (
            f"인생에서 가장 역동적인 30대입니다. {ilgan_kr}의 기운이 본격적인 전성기를 맞이하고 있습니다. "
            f"도전과 확장의 시기이나, 무리한 욕심은 금물입니다. 실력을 쌓으면서 기회를 잡으십시오. "
            f"지금 맺는 인연과 쌓는 신뢰가 40대 이후의 가장 큰 자산이 됩니다."
        )
    elif current_age < 50:
        age_stage, age_msg = "중년기", (
            f"40대는 사주의 모든 에너지가 결실을 맺는 황금기입니다. {ilgan_kr}의 본성이 가장 강하게 발휘됩니다. "
            f"지금까지 쌓아온 것들이 실제 열매로 맺히는 시기. 큰 그림을 그리되 내실을 더욱 단단히 하십시오. "
            f"건강 관리를 시작하지 않으면 50대에 대가를 치릅니다. 지금이 바꿀 수 있는 마지막 기회입니다."
        )
    elif current_age < 60:
        age_stage, age_msg = "중년기 후반", (
            f"50대는 수확과 전환의 시기입니다. {ilgan_kr} 일간의 기운이 내면으로 깊어지는 때입니다. "
            f"지나온 길을 돌아보고 남은 길을 재정비하십시오. 욕심을 줄이고 핵심에만 집중하는 것이 지혜입니다. "
            f"건강 관리를 최우선 과제로 삼고, 가족과의 시간을 늘리십시오."
        )
    else:
        age_stage, age_msg = "장년기", (
            f"장년기는 지혜로 빛나는 시기입니다. {ilgan_kr}의 기운이 원숙함으로 완성되고 있습니다. "
            f"후학을 이끌고 경험을 나누는 것이 이 시기의 가장 큰 복입니다. "
            f"욕심보다 감사를, 경쟁보다 조화를 추구할 때 진정한 행복이 찾아옵니다."
        )

    # 인생 대운 흐름
    def _dw_at(age):
        for dw in daewoon:
            s = dw.get("시작나이", 0)
            if s <= age < s + 10:
                return dw.get("str", "?")
        return "?"

    # 올해 세운 메시지
    sw_ss = sw_now.get("십성_천간", "")
    sw_gilhyung = sw_now.get("길흉", "보통")
    _SW_MSG = {
        "正官": f"{current_year}년 정관(正官) 세운 — 명예와 직위가 오르는 해. 조직 내 신뢰가 높아집니다.",
        "偏官": f"{current_year}년 편관(偏官) 세운 — 도전과 극복의 해. 강인하게 버티면 크게 성장합니다.",
        "正財": f"{current_year}년 정재(正財) 세운 — 안정적 수입이 늘어나는 해. 성실한 노력이 결실을 맺습니다.",
        "偏財": f"{current_year}년 편재(偏財) 세운 — 예상치 못한 수입과 기회의 해. 적극적으로 움직이십시오.",
        "食神": f"{current_year}년 식신(食神) 세운 — 표현력과 창의성이 빛나는 해. 부업·새 분야 도전에 좋습니다.",
        "傷官": f"{current_year}년 상관(傷官) 세운 — 변화와 혁신의 에너지. 기존 틀을 깨는 도전이 성과를 냅니다.",
        "比肩": f"{current_year}년 비견(比肩) 세운 — 독립과 자립의 해. 경쟁이 심해지나 자신감으로 돌파 가능합니다.",
        "劫財": f"{current_year}년 겁재(劫財) 세운 — 재물 기복 주의. 충동적 지출과 투자를 자제하십시오.",
        "偏印": f"{current_year}년 편인(偏印) 세운 — 이동과 변화의 해. 학습·이직·이사 기운이 강합니다.",
        "正印": f"{current_year}년 정인(正印) 세운 — 학문과 귀인의 해. 배움과 자격증이 운명을 바꿉니다.",
    }
    sw_msg1 = _SW_MSG.get(sw_ss, f"{current_year}년은 {sw_gilhyung}의 기운이 흐르는 한 해입니다.")
    sw_msg2 = (
        "길(吉)한 기운이 강하니 상반기에 중요한 결정을 내리십시오."
        if "길" in sw_gilhyung else
        "흉(凶) 기운이 있으니 무리한 변화보다 내실을 다지는 한 해로 삼으십시오."
        if "흉" in sw_gilhyung else
        "평온하게 흐르는 한 해. 꾸준함이 가장 큰 무기입니다."
    )

    # 만신의 한마디
    _MANSHIN = {
        "甲": f"곧게 뻗은 나무가 아름답지만, 폭풍에는 휘는 대나무가 오래 삽니다. 유연함을 기르십시오.",
        "乙": f"덩굴은 어디든 뿌리를 내립니다. 지금 있는 자리에서 최선을 다하면 반드시 꽃피웁니다.",
        "丙": f"태양은 매일 뜨지만 소모되지 않습니다. 충전 없는 빛은 꺼집니다. 쉬는 것도 실력입니다.",
        "丁": f"촛불은 어둠을 밝히다 자신을 태웁니다. 감정을 표현하고 속을 비워야 더 오래 빛납니다.",
        "戊": f"산은 움직이지 않아도 세상 모든 것이 찾아옵니다. 변화를 두려워 말고 중심을 지키십시오.",
        "己": f"비옥한 땅은 심은 것을 모두 키워냅니다. 걱정을 줄이고 씨앗 심는 데 집중하십시오.",
        "庚": f"쇠는 불에 달구어야 날카로워집니다. 지금의 시련이 당신을 더욱 빛나게 하고 있습니다.",
        "辛": f"완벽한 보석도 땅속에서는 빛나지 않습니다. 80%의 완성으로 세상에 나오십시오.",
        "壬": f"큰 강은 모든 것을 받아들이지만 방향을 잃지 않습니다. 깊이 없는 넓음은 진흙이 됩니다.",
        "癸": f"이슬 한 방울이 메마른 땅을 촉촉이 적십니다. 당신의 섬세함이 곧 천재성입니다.",
    }
    manshin = _MANSHIN.get(ilgan, f"당신의 운명은 선택으로 완성됩니다. 지금 이 순간이 가장 중요합니다.")

    lines = [
        f"",
        f"    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"      {display_name}님의 사주 종합 리포트",
        f"      {birth_year}년생 | {ilgan_kr}({ilgan}) 일간 | {sn}",
        f"    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"    ┌ 제1장 | 일간(日干) — 타고난 기질과 본성 ┐",
        f"",
        f"일간(日干)은 '나 자신'을 나타내는 사주의 핵심. {display_name}님의 일간은 {ilgan}({ilgan_kr})입니다.",
        f"",
        f"  {profile_bonzil}",
        f"",
        f"  일간 {ilgan_kr}이(가) {iljj_kr}(日支) 위에 앉아 있습니다.",
        f"  {iljj_kr}의 기운이 현실적 행동 패턴과 배우자 자리에 깊숙이 관여합니다.",
        f"",
        f"  ▶ 타고난 장점 TOP 3",
    ]
    for j in jangjeom_list:
        lines.append(f"    ✓ {j}")
    lines += [f"", f"  ▶ 주의해야 할 단점 TOP 3"]
    for d in daknjeom_list:
        if d:
            lines.append(f"    △ {d}")
    lines.append(f"")
    if profile_jikup:
        lines.append(f"  [천직·적성] {profile_jikup}")
    if profile_jaemul:
        lines.append(f"  [재물 그릇] {profile_jaemul}")
    if profile_yeonae:
        lines.append(f"  [연애 스타일] {profile_yeonae}")
    if profile_geongang:
        lines.append(f"  [건강 주의] {profile_geongang}")
    if profile_chobang:
        lines += [f"", f"  ◆ 핵심 처방: {profile_chobang}"]
    lines += [
        f"",
        f"    ┌ 제2장 | 신강신약(身强弱) — 기운의 세기 ┐",
        f"",
        f"  {sn_narr}",
        f"  체력 점수: {strength_info.get('helper_score', 50)}점",
        f"  → {sn_advice}",
        f"",
        f"    ┌ 제3장 | 인생 전체 흐름 — 대운의 파도 ┐",
        f"",
        f"  [유년기~20대] {_dw_at(10)} 대운",
        f"    기질이 형성되는 시기. 가정과 학업 환경이 성격의 틀을 잡습니다.",
        f"    {ilgan_kr}의 씨앗이 심어지고 자라는 출발점.",
        f"",
        f"  [청년기~30대] {_dw_at(28)} 대운",
        f"    사회로 나아가 자신을 증명하는 시기. 도전과 실패가 모두 자양분.",
        f"    이 시기의 경험이 중년 이후의 내공을 결정합니다.",
        f"",
        f"  [중년기~40대] {_dw_at(45)} 대운",
        f"    인생의 수확기. 쌓아온 것들이 현실로 결실을 맺습니다.",
        f"    가장 강한 에너지가 흐르는 황금기. 큰 결정을 내리기에 최적의 시기.",
        f"",
        f"  [장년기~60대] {_dw_at(65)} 대운",
        f"    완성과 전달의 시기. 지혜가 빛을 발하고 후학이 모여듭니다.",
        f"    건강과 관계를 최우선으로. 욕심보다 여유가 복을 부릅니다.",
        f"",
        f"    ┌ 제4장 | 현재 나이대 집중 분석 ({current_age}세 / {age_stage}) ┐",
        f"",
        f"  {age_msg}",
        f"  현재 {cur_dw.get('str', '?')} 대운이 흐르고 있습니다.",
        f"  이 대운의 기운을 최대로 활용하는 것이 지금 가장 중요한 과제입니다.",
        f"",
        f"    ┌ 제5장 | 올해({current_year}년) 세운 핵심 메시지 ┐",
        f"",
        f"  {sw_msg1}",
        f"  {sw_msg2}",
        f"",
        f"    ━━━━━ 🔮 만신의 한마디 ━━━━━",
        f"",
        f"  「 {display_name}님, {manshin} 」",
        f"",
    ]
    return "\n".join(lines)


def _nar_ch3_gyeokguk(ctx):
    """3~4장: 격국 + 용신 (GYEOKGUK_DETAIL 강화)"""

    display_name = ctx.get("display_name", "내담자")
    gname = ctx.get("gname", "")
    gnarr = ctx.get("gnarr", "")
    yongshin_ohs = ctx.get("yongshin_ohs", [])
    yong_kr = ctx.get("yong_kr", "")

    # GYEOKGUK_DETAIL 데이터 우선 활용
    gd = GYEOKGUK_DETAIL.get(gname, {})
    gd_heksim = gd.get("핵심", "")
    gd_jikup = gd.get("직업", "")
    gd_jaemul = gd.get("재물", "")
    gd_yeonae = gd.get("연애", "")
    gd_juui = gd.get("주의", "")
    gd_chobang = gd.get("처방", "")

    lines = [
        f"[ 제3장 | 격국(格局) - 타고난 인생 설계도 ]",
        f"",
        f"  {gnarr}" if gnarr else f"  {display_name}님의 격국: {gname}",
        f"",
    ]
    if gd_heksim:
        lines.append(f"  핵심 의미: {gd_heksim}")
        lines.append(f"")
    if gd_jikup:
        lines.append(f"  [적성·직업]: {gd_jikup}")
    if gd_jaemul:
        lines.append(f"  [재물 운]: {gd_jaemul}")
    if gd_yeonae:
        lines.append(f"  [연애·결혼]: {gd_yeonae}")
    if gd_juui:
        lines.append(f"  [주의사항]: {gd_juui}")
    if gd_chobang:
        lines.append(f"  [처방]: {gd_chobang}")
    if not gd:
        lines += [
            f"  격국은 사주의 큰 그림, 인생의 방향성을 나타냅니다.",
            f"  {gname}을 가진 분이 성공하는 공통점:",
            f"  첫째, 타고난 격국에 맞는 분야에서 최대 능력 발휘.",
            f"  둘째, 격국의 장점을 살리며 단점을 보완하는 운을 활용.",
            f"  셋째, 용신 오행이 강한 시기에 결정적 도전.",
        ]
    lines += [
        f"",
        f"[ 제4장 | 용신(用神) - 내 인생의 보물 오행 ]",
        f"",
        f"  용신은 내 사주에 가장 필요한 오행. 이 기운이 강화될 때 건강·재물·명예 모두 좋아집니다.",
        f"",
        f"  {display_name}님의 용신: {yong_kr}",
        f"",
        f"  용신 강화 방법:",
        f"  * 용신 색상의 옷/소품 활용",
        f"  * 용신 방위에 중요한 공간 배치",
        f"  * 용신 오행에 해당하는 음식 자주 섭취",
        f"  * 용신이 강한 해에 큰 결정 실행",
        f"",
        f"  기신(忌神) 운에서는 무리한 투자·이동·결정을 자제하고 내실을 다지십시오.",
        f"",
    ]
    return "\n".join(lines)


def _nar_ch5_sipsong(ctx):
    """5장: 십성(十星) 조합 — 당신만의 인생 코드 (SIPSONG_DETAIL 강화)"""
    display_name = ctx.get("display_name", "내담자")
    top_ss = ctx.get("top_ss", [])
    ss_dist = ctx.get("ss_dist", {})
    combos = ctx.get("combos", [])

    lines = [
        f"[ 제5장 | 십성(十星) 조합 - {display_name}님의 인생 코드 ]",
        f"",
        f"  사주 원국에서 가장 강한 십성은 세상을 바라보는 방식이자 가장 자연스럽게 발휘하는 능력입니다.",
        f"",
    ]
    if top_ss:
        lines.append(f"  주도 십성: {' / '.join(top_ss)}")
        lines.append(f"")
        for ss in top_ss[:2]:
            sd = SIPSONG_DETAIL.get(ss, {})
            if sd:
                lines.append(f"  ■ {ss}({sd.get('한글', '')}) — {sd.get('핵심', '')}")
                if sd.get("직업"):
                    lines.append(f"    [적성]: {sd['직업']}")
                if sd.get("재물"):
                    lines.append(f"    [재물]: {sd['재물']}")
                if sd.get("연애"):
                    lines.append(f"    [연애]: {sd['연애']}")
                if sd.get("처방"):
                    lines.append(f"    [처방]: {sd['처방']}")
                lines.append(f"")
            else:
                lines.append(f"  * {ss}: 이 기운이 삶을 이끄는 주된 에너지입니다.")
                lines.append(f"")
    if ss_dist:
        strong = [k for k, v in ss_dist.items() if isinstance(v, (int, float)) and v >= 2]
        if strong:
            lines.append(f"  집중 십성(2개 이상): {', '.join(strong)}")
            lines.append(f"  → 이 기운들이 {display_name}님의 삶을 가장 강하게 끌어당깁니다.")
            lines.append(f"")
    if combos:
        lines.append(f"  주요 십성 조합:")
        for c in combos[:3]:
            if isinstance(c, str):
                lines.append(f"  * {c}")
        lines.append(f"")
    lines.append(f"  황금률: 강한 십성을 살리되, 부족한 십성이 요구하는 영역을 의식적으로 보완하면 균형 잡힌 인생이 열립니다.")
    lines.append(f"")
    return "\n".join(lines)


def _nar_ch6_daewoon(ctx):
    """6장: 대운 흐름 + 세운 예측 — 인생의 타임라인 (DAEWOON_INTERP 강화)"""
    display_name = ctx.get("display_name", "내담자")
    birth_year = ctx.get("birth_year", 1980)
    current_year = ctx.get("current_year", datetime.now().year)
    cur_dw = ctx.get("cur_dw", {})
    cur_dw_ss = ctx.get("cur_dw_ss", "")
    sw_now = ctx.get("sw_now", {})
    sw_next = ctx.get("sw_next", {})
    daewoon = ctx.get("daewoon", [])
    yongshin_ohs = ctx.get("yongshin_ohs", [])
    ilgan_oh = ctx.get("ilgan_oh", "")
    pils = ctx.get("pils", [])

    DW_SS_MEANING = {
        "比肩": "독립·자립의 10년. 스스로 개척할 때 기회가 옴.",
        "劫財": "경쟁·변동의 10년. 재물 기복이 크고 승부욕이 강해짐.",
        "食神": "표현·창작·부업의 10년. 먹고살 복이 충만한 시기.",
        "傷官": "혁신·기술·충돌의 10년. 기존 틀을 깨는 창조적 에너지.",
        "偏財": "사업·투자·인맥의 10년. 적극적 확장이 기회를 만듦.",
        "正財": "저축·안정·성실의 10년. 꾸준히 쌓아야 빛나는 시기.",
        "偏官": "도전·극기·변화의 10년. 강인한 의지로 장벽을 돌파.",
        "正官": "명예·승진·안정의 10년. 사회적 신뢰가 쌓이는 시기.",
        "偏印": "이동·학습·변화의 10년. 이직·이사·유학 가능성 증가.",
        "正印": "학문·자격·보호의 10년. 배움과 귀인의 도움이 뒤따름.",
    }

    is_yong_dw = cur_dw and _get_yongshin_match(cur_dw_ss, yongshin_ohs, ilgan_oh) == "yong"

    # 세운×대운 교차 해석
    cross = {}
    try:
        cross = get_crossing_interpretation(pils, current_year) if pils else {}
    except Exception:
        pass

    # 현재 대운 천간·지지 DAEWOON_INTERP 해석
    dw_cg_interp = DAEWOON_INTERP.get(cur_dw.get("cg", ""), "") if cur_dw else ""
    dw_jj_interp = DAEWOON_INTERP.get(cur_dw.get("jj", ""), "") if cur_dw else ""

    lines = [
        f"[ 제6장 | 대운(大運)·세운(歲運) 흐름 - {display_name}님의 인생 타임라인 ]",
        f"",
        f"  대운은 10년 단위의 운의 물결. 세운은 그 위에 부는 1년짜리 바람입니다.",
        f"",
        f"  ▸ 현재 대운: {cur_dw.get('str', '-')} ({cur_dw_ss})",
        f"    {DW_SS_MEANING.get(cur_dw_ss, '현재 대운 기운에 순응하며 흐름을 타십시오.')}",
        f"    기간: {cur_dw.get('시작연도', '-')}년 ~ {cur_dw.get('종료연도', '-')}년",
        f"    {'[용신 대운] 황금기입니다. 과감하게 도전하십시오.' if is_yong_dw else '[주의 대운] 무리한 확장보다 내실을 다지는 10년으로 활용하십시오.'}",
        f"",
    ]
    if dw_cg_interp:
        lines.append(f"  천간 해석: {dw_cg_interp}")
    if dw_jj_interp:
        lines.append(f"  지지 해석: {dw_jj_interp}")
    if dw_cg_interp or dw_jj_interp:
        lines.append(f"")
    lines += [
        f"  ▸ 올해 세운: {sw_now.get('세운', '-')} ({sw_now.get('십성_천간', '-')}) — {sw_now.get('길흉', '-')}",
        f"  ▸ 내년 세운: {sw_next.get('세운', '-')} ({sw_next.get('십성_천간', '-')}) — {sw_next.get('길흉', '-')}",
        f"",
    ]
    if cross.get("summary"):
        lines += [
            f"  [세운×대운 교차 분석]",
            f"  {cross['summary']}",
            f"  {cross.get('career', '')}",
            f"  {cross.get('finance', '')}",
            f"",
        ]
    if daewoon:
        future_dws = [dw for dw in daewoon if dw.get("종료연도", 0) >= current_year][:3]
        if future_dws:
            lines.append(f"  향후 대운 예고:")
            for dw in future_dws:
                dw_yong = _get_yongshin_match(dw.get("십성_천간", ""), yongshin_ohs, ilgan_oh) == "yong"
                mark = "[용신]" if dw_yong else ""
                dw_cg_hint = DAEWOON_INTERP.get(dw.get("cg", ""), "")[:30]
                lines.append(
                    f"  * {dw['str']} 대운 ({dw['시작연도']}~{dw['종료연도']}) "
                    f"[{dw.get('십성_천간', '-')}] {mark} {dw_cg_hint}"
                )
            lines.append(f"")
    lines.append(
        f"  용신이 겹치는 해는 최고의 기회, 기신이 겹치는 해는 최대의 위험. 두 방향이 같을 때 기운이 극대화됩니다."
    )

    # 이 10년의 키워드 3개
    _DW_KEYWORDS = {
        "比肩": ["독립", "자립", "경쟁"],
        "劫財": ["변동", "재물기복", "승부"],
        "食神": ["창작", "복록", "표현"],
        "傷官": ["혁신", "충돌", "기술"],
        "偏財": ["사업", "확장", "인맥"],
        "正財": ["안정", "성실", "저축"],
        "偏官": ["도전", "극복", "단련"],
        "正官": ["명예", "신뢰", "승진"],
        "偏印": ["이동", "변화", "학습"],
        "正印": ["학문", "귀인", "보호"],
    }
    kws = _DW_KEYWORDS.get(cur_dw_ss, ["성장", "변화", "결실"])
    lines += [
        f"",
        f"  ▶ 이 10년의 핵심 키워드: #{kws[0]}  #{kws[1]}  #{kws[2]}",
        f"",
    ]

    # 연도별 흐름 요약 (현재~5년후)
    lines.append(f"  ▶ 향후 5년 연도별 흐름 요약")
    for offset in range(6):
        y = current_year + offset
        try:
            yl = get_yearly_luck(pils, y) if pils else {}
            y_ss = yl.get("십성_천간", "-")
            y_gh = yl.get("길흉", "보통")
            y_sw = yl.get("세운", str(y))
            _Y_HINT = {
                "正官": "명예·승진 기운",  "偏官": "도전·극복 기운",
                "正財": "수입 증가 기운",  "偏財": "기회·확장 기운",
                "食神": "창의·복록 기운",  "傷官": "변화·혁신 기운",
                "比肩": "자립·경쟁 기운",  "劫財": "재물 기복 기운",
                "偏印": "이동·학습 기운",  "正印": "귀인·학문 기운",
            }
            hint = _Y_HINT.get(y_ss, "흐름 유지")
            lines.append(f"    {y}년 [{y_sw}] {y_ss} — {hint} ({y_gh})")
        except Exception:
            lines.append(f"    {y}년 — 계산 중")
    lines.append(f"")

    # 이 대운에서 반드시 해야 할 것 / 하지 말아야 할 것
    _DW_DO = {
        "比肩": ("독립 사업 또는 부업 시작, 자기 브랜드 구축", "타인에게 지나치게 의존하거나 경쟁을 회피"),
        "劫財": ("적극적 사업 도전, 협업 파트너 확보", "충동적 투자·투기, 보증·연대"),
        "食神": ("창의적 표현 활동, 부업·취미 사업화", "재능을 혼자 묻어두는 것, 과한 식음주"),
        "傷官": ("새 기술·자격증 취득, 창업 준비", "윗사람과의 충돌, 법적 분쟁"),
        "偏財": ("인맥 확장, 사업 투자, 이성 인연 적극 추구", "도박성 투자, 다수와의 금전 거래"),
        "正財": ("저축·안정 자산 확보, 착실한 실력 축적", "무리한 확장, 큰 투기성 투자"),
        "偏官": ("건강 관리, 체력 단련, 도전 과제 설정", "감정적 충돌, 무리한 과로"),
        "正官": ("경력 개발, 자격증, 대외 신뢰도 구축", "원칙 어기기, 불필요한 이직·변동"),
        "偏印": ("이사·이직·유학 등 큰 변화 실행", "한 자리에 고착, 변화 거부"),
        "正印": ("학업·자격증·연구, 귀인 관계 돈독히", "독선적 행동, 스승·멘토 무시"),
    }
    do_txt, dont_txt = _DW_DO.get(cur_dw_ss, ("현재 기운에 집중", "무리한 변화 자제"))
    lines += [
        f"  ▶ 이 대운에서 반드시 해야 할 것",
        f"    ✓ {do_txt}",
        f"",
        f"  ▶ 이 대운에서 하지 말아야 할 것",
        f"    ✗ {dont_txt}",
        f"",
    ]
    return "\n".join(lines)


def _nar_ch7_health(ctx):
    """7장: 건강운 — 오행 불균형 진단 (get_health_reading 강화)"""
    display_name = ctx.get("display_name", "내담자")
    ilgan = ctx.get("ilgan", "")
    ilgan_oh = ctx.get("ilgan_oh", "")
    oh_strength = ctx.get("oh_strength", {})
    OH_KR_MAP = ctx.get("OH_KR_MAP", {"木": "목(木)", "火": "화(火)", "土": "토(土)", "金": "금(金)", "水": "수(水)"})
    pils = ctx.get("pils", [])

    # get_health_reading 활용
    hr = {}
    try:
        hr = get_health_reading(pils) if pils else {}
    except Exception:
        pass

    lines = [
        f"[ 제7장 | 건강운 - 오행 불균형 진단 ]",
        f"",
        f"  사주의 오행 강약은 신체 특정 부위의 선천적 강·약점과 연결됩니다.",
        f"",
    ]

    # 일간 기반 선천 취약 부위
    ilgan_health = hr.get("일간_건강", "")
    if ilgan_health:
        lines.append(f"  [일간 {ilgan} 선천 취약 부위]")
        lines.append(f"  {ilgan_health}")
        lines.append(f"")

    # 오행 불균형 상세 진단
    health_info = hr.get("health_info", [])
    if health_info:
        for h in health_info[:3]:
            oh = h.get("오행", "")
            state = h.get("상태", "")
            pct = h.get("점수", 0)
            organ = h.get("장기", "")
            symptom = h.get("증상", "")
            food = h.get("음식", "")
            note = h.get("주의", "")
            oh_kr = OH_KR_MAP.get(oh, oh)
            if state == "부족":
                lines.append(f"  ■ {oh_kr} 기운 부족 ({pct:.0f}%) — 취약 부위: {organ}")
                lines.append(f"    주의 증상: {symptom}")
                lines.append(f"    보완 음식: {food}")
            elif state == "과다":
                lines.append(f"  ■ {oh_kr} 기운 과다 ({pct:.0f}%) — 해당 부위 과부하 주의: {organ}")
                lines.append(f"    주의사항: {note}")
            lines.append(f"")
    elif oh_strength and isinstance(oh_strength, dict):
        # 폴백: 기존 방식
        oh_sorted = sorted([(k, v) for k, v in oh_strength.items() if isinstance(v, (int, float))], key=lambda x: x[1])
        if oh_sorted:
            weakest = oh_sorted[0][0]
            w_kr = OH_KR_MAP.get(weakest, weakest)
            lines.append(f"  가장 약한 오행: {w_kr} — 해당 장기 건강 주의")
            lines.append(f"")

    # 처방
    prescriptions = hr.get("처방", [])
    lines.append(f"  [건강 처방]")
    for p in prescriptions:
        lines.append(f"  * {p}")
    lines += [
        f"  * 약한 오행 계절(봄=木, 여름=火, 환절기=土, 가을=金, 겨울=水)에 활동량 조절",
        f"  * 정기 검진은 위 지목 장기 위주로 시행",
        f"  * 과로와 스트레스가 가장 약한 오행을 더욱 손상시킴 — 충분한 숙면 필수",
        f"",
    ]
    return "\n".join(lines)


def _nar_ch8_flow(ctx):
    """8장: 현재 운기 + 내년 세운 전망"""

    current_year = ctx.get("current_year", datetime.now().year)

    cur_dw = ctx.get("cur_dw", {})

    cur_dw_ss = ctx.get("cur_dw_ss", "")

    sw_now = ctx.get("sw_now", {})

    sw_next = ctx.get("sw_next", {})

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    ilgan_oh = ctx.get("ilgan_oh", "")

    return (
        "\n".join(
            [
                f"",
                f"",
                f"[ 제8장 | 현재 운기(Flow) - {current_year}년 상황 ]",
                f"",
                f"현재 {cur_dw['str'] if cur_dw else '-'} 대운이 진행 중입니다.",
                f"    ({cur_dw_ss} 십성 대운 | {cur_dw['시작연도'] if cur_dw else '-'}년부터 {cur_dw['종료연도'] if cur_dw else '-'}년까지)",
                f"",
                f"올해 {sw_now.get('세운', '')} 세운 ({sw_now.get('십성_천간', '')} / {sw_now.get('길흉', '')})",
                f"",
                f"{'이 시기는 용신 대운이 들어오는 황금기입니다. 적극적으로 움직이고 도전하십시오. 지금 준비하면 반드시 결실이 옵니다.' if cur_dw and _get_yongshin_match(cur_dw_ss, yongshin_ohs, ilgan_oh) == 'yong' else '이 시기는 주의가 필요한 대운입니다. 무리한 확장보다 내실을 다지고 건강 관리에 집중하십시오. 지금의 인내가 다음 황금기를 준비하는 것입니다.'}",
                f"",
                f"",
            ]
        )
        + f"    내년 {sw_next.get('세운', '')} 세운 전망: {sw_next.get('십성_천간', '')} 십성 | {sw_next.get('길흉', '')}\n"
    )


def _nar_ch20_prescription(ctx):
    """20장: 맞춤 인생 처방전"""

    display_name = ctx.get("display_name", "내담자")

    current_year = ctx.get("current_year", datetime.now().year)

    gname = ctx.get("gname", "")

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    yong_kr = ctx.get("yong_kr", "")

    top_ss = ctx.get("top_ss", [])

    sw_next = ctx.get("sw_next", {})

    ilgan = ctx.get("ilgan", "")
    ilp = ILGAN_PROFILE.get(ilgan, {})
    ilp_rx   = ilp.get("처방", "")
    gd = GYEOKGUK_DETAIL.get(gname, {})
    gd_rx    = gd.get("처방", "")

    return "\n".join(
        [
            f"",
            f"",
            f"[ 제20장 | {display_name}님에게만 드리는 맞춤 인생 처방전 ]",
            f"",
            f"20개 장의 분석을 종합한 최종 처방입니다.",
            f"",
            f"[지금 당장 해야 할 것 (Yongshin 강화)]",
            f"",
            f"색상 처방:",
            chr(10).join(filter(None, [
                f'* 목(木) 용신: 청색, 녹색 계열' if '木' in yongshin_ohs else '',
                f'* 화(火) 용신: 적색, 주황색 계열' if '火' in yongshin_ohs else '',
                f'* 토(土) 용신: 황색, 베이지, 갈색 계열' if '土' in yongshin_ohs else '',
                f'* 금(金) 용신: 백색, 은색, 금색 계열' if '金' in yongshin_ohs else '',
                f'* 수(水) 용신: 흘색, 남색, 회색 계열' if '水' in yongshin_ohs else '',
            ])),
            f"",
            f"방위 처방:",
            chr(10).join(filter(None, [
                f'* 목(木): 동쪽' if '木' in yongshin_ohs else '',
                f'* 화(火): 남쪽' if '火' in yongshin_ohs else '',
                f'* 토(土): 중앙, 북동, 북서' if '土' in yongshin_ohs else '',
                f'* 금(金): 서쪽' if '金' in yongshin_ohs else '',
                f'* 수(水): 북쪽' if '水' in yongshin_ohs else '',
            ])),
            f"",
            f"시간 처방:",
            chr(10).join(filter(None, [
                f'* 목(木): 새벽 3~7시(인묘시)' if '木' in yongshin_ohs else '',
                f'* 화(火): 오전 9~13시(사오시)' if '火' in yongshin_ohs else '',
                f'* 토(土): 진술축미시' if '土' in yongshin_ohs else '',
                f'* 금(金): 오후 3~7시(신유시)' if '金' in yongshin_ohs else '',
                f'* 수(水): 저녁 9~새벽 1시(해자시)' if '水' in yongshin_ohs else '',
            ])),
            f"",
            f"[일간 처방]",
            f"* {ilp_rx}" if ilp_rx else "",
            f"",
            f"[격국 처방]",
            f"* {gd_rx}" if gd_rx else f"* {gname}의 본래 기운을 따르는 것이 가장 빠른 길입니다.",
            f"",
            f"[절대 하면 안 되는 것 (Gishin 주의)]",
            f"",
            f"* 기신 운이 강한 해에 큰 투자, 이사, 창업, 결혼 서두르지 않기",
            f"* {gname}에 맞지 않는 사업 방향 피하기",
            f"* {'보증, 연대책임 절대 금지' if '겁재' in str(top_ss) or '비견' in str(top_ss) else '감정적 충동 결정 자제'}",
            f"* 건강 경고 신호 무시하지 않기",
            f"",
            f"[ {current_year + 1}년 행동 계획 ]",
            f"",
            f"내년 세운: {sw_next.get('세운', '')} ({sw_next.get('십성_천간', '')} / {sw_next.get('길흉', '')})",
            f"{'[확인] 적극적으로 움직여야 할 해. 준비한 것을 실행하고 귀인의 도움을 요청하십시오.' if sw_next.get('길흉', '') in ['길', '대길'] else '[주의] 신중하게 내실을 다지는 해. 현재를 안정화하는 데 집중하십시오.'}",
            f"",
            f'"운명은 사주가 정하지만, 운명을 만드는 것은 당신입니다."',
            f"",
            f"",
        ]
    )


def _nar_report(ctx):
    pils, birth_year, gender, name = (
        ctx["pils"],
        ctx["birth_year"],
        ctx["gender"],
        ctx["name"],
    )

    # 1. 추출 및 데이터 변환 (형님 엔진 데이터)
    display_name = name
    ilgan = clean_hanja(pils[1]["cg"]) if pils[1] else ""
    char_desc = ILGAN_CHAR_DESC.get(ilgan, {})
    ilgan_kr = char_desc.get("상징", "")

    strength_info = get_ilgan_strength(pils[1]["cg"], pils)
    sn = strength_info.get("신강신약", "중화")

    gyeokguk = get_gyeokguk(pils)
    gname = clean_hanja(gyeokguk.get("격국명", "")) if gyeokguk else "미정격"

    ys = get_yongshin(pils)
    yong_list = ys.get("종합_용신", [])
    yong_kr = clean_hanja(yong_list[0]) if isinstance(yong_list, list) and yong_list else "木"

    # 상위 십성 추출
    ss_counts = {}
    for p in pils:
        if p:
            if p.get("cg_ss"):
                ss_counts[p.get("cg_ss")] = ss_counts.get(p.get("cg_ss"), 0) + 1
            if p.get("jj_ss"):
                ss_counts[p.get("jj_ss")] = ss_counts.get(p.get("jj_ss"), 0) + 1
    top_ss = [item[0] for item in sorted(ss_counts.items(), key=lambda x: -x[1])][:2]

    # 안전장치 (십성이 부족할 때)
    top1 = top_ss[0] if len(top_ss) > 0 else "비견"
    top2 = top_ss[1] if len(top_ss) > 1 else "식신"

    # 운세 흐름 (대운/세운)
    cur_year = datetime.now().year
    try:
        this_year_flow = get_yearly_luck(pils, cur_year)
    except Exception:
        this_year_flow = {}

    daewoons = SajuCoreEngine.get_daewoon(pils, birth_year, 1, 1, 12, 0, gender=gender)
    current_dw = next((dw for dw in daewoons if dw["시작연도"] <= cur_year <= dw["종료연도"]), None)

    cur_dw_str = current_dw["str"] if current_dw else "알 수 없는"
    sw_now_str = this_year_flow.get("세운", "") if this_year_flow else "알 수 없는"
    # 세운 해석은 천간 기준 십성을 사용 (지지 기준이 아님)
    sw_now_ss = clean_hanja(this_year_flow.get("십성_천간", "") or "알 수 없는 기운")
    # 신강신약별 행동 패턴
    sn_action = (
        "남의 밑에서 지시를 받기보다는 스스로의 길을 개척해야 직성이 풀리는 강인한 분"
        if "신강" in sn
        else "혼자보다는 귀인이나 좋은 파트너와 함께할 때 그 잠재력이 폭발하는 섬세한 분"
        if "신약" in sn
        else "어떤 상황에서도 무너지지 않는 끈기와 밸런스를 갖춘 분"
    )

    # 로컬 엔진 강화: 일주·오행·신살·공망 풍부한 서술
    oh_strength = ctx.get("oh_strength", {})
    sinsal_list = ctx.get("sinsal_list", [])
    gongmang = ctx.get("gongmang", {})
    ilju_desc = ctx.get("ilju_desc", "")
    OH_KR_MAP = ctx.get("OH_KR_MAP", {"木": "목(木)", "火": "화(火)", "土": "토(土)", "金": "금(金)", "水": "수(水)"})

    ilju_block = ""
    if ilju_desc:
        ilju_block = f"당신의 <b>일주(日柱)</b>는 {ilju_desc}<br><br>"

    oh_block = ""
    if oh_strength and isinstance(oh_strength, dict):
        try:
            oh_sorted = sorted([(k, v) for k, v in oh_strength.items() if isinstance(v, (int, float))], key=lambda x: -x[1])
            if oh_sorted:
                strongest_kr = OH_KR_MAP.get(oh_sorted[0][0], oh_sorted[0][0])
                weakest_kr = OH_KR_MAP.get(oh_sorted[-1][0], oh_sorted[-1][0]) if len(oh_sorted) > 1 else ""
                oh_block = f"<b>오행(五行)</b>으로 보면 {strongest_kr} 기운이 가장 강하고, {weakest_kr}가 상대적으로 약합니다. 강한 기운을 살리되 약한 쪽은 용신으로 보강하면 좋습니다.<br><br>"
        except Exception as _e:
            _saju_log.debug("[silent except] %s", _e)

    sinsal_block = ""
    if sinsal_list and isinstance(sinsal_list, list):
        names = []
        for s in sinsal_list[:5]:
            n = s.get("이름") or s.get("name") or ""
            if n:
                names.append(n)
        if names:
            sinsal_block = f"<b>신살(神殺)</b>로는 {', '.join(names)} 등이 자리해, 그에 맞는 재능과 주의할 점이 있습니다.<br><br>"

    gongmang_block = ""
    gm_cols = gongmang.get("해당_기둥", []) if isinstance(gongmang, dict) else []
    if gm_cols:
        gm_names = [g.get("기둥", "") for g in gm_cols if isinstance(g, dict)]
        if gm_names:
            gongmang_block = f"<b>공망(空亡)</b>이 {', '.join(gm_names)}에 있어 해당 부분은 때로 헛되이 느껴질 수 있으나, 그곳에 집착하지 않을 때 오히려 균형이 잡힙니다.<br><br>"

    pahae = ctx.get("pahae", {})
    pahae_block = ""
    pahae_items = pahae.get("items", []) if isinstance(pahae, dict) else []
    if pahae_items:
        pahae_parts = []
        for item in pahae_items:
            t = item.get("type", "")
            pair = "·".join(item.get("pair", []))
            desc = item.get("desc", "")
            pahae_parts.append(f"{t}({pair}): {desc}")
        pahae_block = f"<b>파·해살(破害殺)</b> — {' / '.join(pahae_parts)}<br><br>"

    geunmyo = ctx.get("geunmyo", [])
    geunmyo_block = ""
    if geunmyo and isinstance(geunmyo, list):
        parts = [f"{g['궁']} {g['pillar']}({g['간지']}, {g['천간십성']})" for g in geunmyo if g.get("궁")]
        if parts:
            geunmyo_block = f"<b>근묘화실(根苗花實)</b> — {' | '.join(parts)}<br><br>"

    extra_section = ""
    if ilju_block or oh_block or sinsal_block or gongmang_block or pahae_block or geunmyo_block:
        extra_section = f"""
<b>6️⃣ [일주·오행·특별기운]</b><br>
        {ilju_block}{oh_block}{sinsal_block}{gongmang_block}{pahae_block}{geunmyo_block}
"""

    # 2. 만신 화법 f-string 조립 (5단계 + 강화된 6단계)
    report = f"""
<div style="background:#ffffff; border:2px solid #d4af37; border-radius:16px; padding:25px; margin-top:20px; box-shadow:0 8px 20px rgba(212,175,55,0.15)">
<div style="font-size:22px; font-weight:900; color:#b38728; text-align:center; margin-bottom:20px; letter-spacing:1px;">
        📜 {display_name}님을 위한 만신의 천명(天命) 풀이
</div>
<div style="font-size:15px; color:#222; line-height:2.1; letter-spacing:-0.3px;">
<b>1️⃣ [천기의 낙인]</b><br>
        {display_name}님의 사주는 한마디로 <b>[{top1}]</b>과 <b>[{top2}]</b>의 기운이 강력하게 이끄는 운명입니다! 남들과는 다른 자신만의 뚜렷한 궤도를 도는 팔자를 지니셨습니다.<br><br>
<b>2️⃣ [나의 본질]</b><br>
        당신은 <b>{ilgan_kr}({ilgan})</b>의 기운을 품고 태어났습니다. 게다가 그 기운이 <b>{sn}</b>으로 자리 잡았으니, {sn_action}입니다. 겉으로 보이는 모습 이면에 숨겨진 단단한 심지를 무기로 삼으십시오.<br><br>
<b>3️⃣ [사회적 무기]</b><br>
        세상을 살아가는 가장 큰 무기는 바로 <b>'{gname}'</b>입니다. 사주 전반에 포진된 {", ".join(top_ss)}의 기운을 보건대, 가만히 머물기보다는 이 무기를 빼어 들고 세상에 부딪힐 때 재물과 명예가 자연스럽게 따라붙게 됩니다.<br><br>
<b>4️⃣ [현재의 날씨]</b><br>
        지금 당신의 배는 <b>{cur_dw_str} 대운</b>의 바다를 관통하고 있으며, 올해는 <b>{sw_now_str}년({sw_now_ss})</b>이라는 바람을 맞이했습니다. 대운의 큰 물결 속에 {sw_now_ss}의 기운이 들어왔으니, 무리한 요행을 바라기보다는 다가오는 변화의 파도를 유연하게 타는 지혜가 필요합니다.<br><br>
<b>5️⃣ [만신의 처방]</b><br>
        당신의 막힌 기운을 뚫어줄 평생의 용신(用神)은 <b>'{yong_kr}'</b>입니다. 중요한 결정을 내릴 때는 이 용신의 방향을 향하시고, 일상에서도 용신의 색상을 가까이하십시오. 운명은 정해져 있으나, 그것을 뚫고 나가는 것은 온전히 {display_name}님의 의지입니다.<br><br>
        {extra_section}
</div>
</div>
"""
    # 상세 챕터 분석 추가 (1·3·4·5·6·7·8·20장)
    try:
        ch1 = _nar_ch1_ilgan(ctx)
        ch3 = _nar_ch3_gyeokguk(ctx)
        ch5 = _nar_ch5_sipsong(ctx)
        ch6 = _nar_ch6_daewoon(ctx)
        ch7 = _nar_ch7_health(ctx)
        ch8 = _nar_ch8_flow(ctx)
        ch20 = _nar_ch20_prescription(ctx)
        chapter_text = "\n\n".join([ch1, ch3, ch5, ch6, ch7, ch8, ch20])
        report += f"""<div style="background:#f9f5e8; border:1px solid #d4af37; border-radius:12px; padding:20px; margin-top:16px; font-size:13px; line-height:1.9; white-space:pre-wrap; color:#333; font-family:'Nanum Gothic',sans-serif;">
{chapter_text}
</div>
"""
    except Exception as _e:
        _saju_log.debug("[silent except] %s", _e)
    return report


def _nar_future(ctx):
    """미래 운세 섹션 (future / lifeline)"""

    ilgan = ctx.get("ilgan", "")

    ilgan_kr = ctx.get("ilgan_kr", "")

    iljj = ctx.get("iljj", "")

    iljj_kr = ctx.get("iljj_kr", "")

    ilgan_oh = ctx.get("ilgan_oh", "")

    current_year = ctx.get("current_year", datetime.now().year)

    current_age = ctx.get("current_age", 40)

    display_name = ctx.get("display_name", "내담자")

    birth_year = ctx.get("birth_year", 1980)

    gender = ctx.get("gender", "남")

    pils = ctx.get("pils", [(0, {}), (0, {})])

    sn = ctx.get("sn", "")

    strength_info = ctx.get("strength_info", {})

    gname = ctx.get("gname", "")

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    yong_kr = ctx.get("yong_kr", "")

    char = ctx.get("char", {})

    sn_narr = ctx.get("sn_narr", "")

    gnarr = ctx.get("gnarr", "")

    top_ss = ctx.get("top_ss", [])

    combos = ctx.get("combos", [])

    ss_dist = ctx.get("ss_dist", {})

    cur_dw = ctx.get("cur_dw", {})

    cur_dw_ss = ctx.get("cur_dw_ss", "")

    sw_now = ctx.get("sw_now", {})

    sw_next = ctx.get("sw_next", {})

    daewoon = ctx.get("daewoon", [])

    if ctx.get("section", "") == "lifeline":
        result = []

        result.append(
            "\n".join(
                [
                    f"大運(大運)은 10년 단위로 흐르는 인생의 큰 물결입니다. 세운(歲運)이 1년 단위의 파도라면, 大運은 10년을 휘감는 조류(潮流)입니다. 아무리 좋은 세운이 와도 大運이 나쁘면 크게 발현되지 않으며, 반대로 힘든 세운도 좋은 大運 아래서는 그 피해가 줄어듭니다.",
                    f"",
                    f"{display_name}님의 用神은 {yong_kr}입니다. 이 오행의 大運이 오는 시기가 인생의 황금기가 됩니다.",
                ]
            )
        )

        for dw in daewoon[:9]:
            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            dw_oh = OH.get(dw["cg"], "")

            is_yong = _get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong"

            is_cur = dw["시작연도"] <= current_year <= dw["종료연도"]

            cur_mark = " ◀ 현재 大運" if is_cur else ""

            DW_SS_DESC = {
                "食神": f"食神 大運은 재능이 꽃피고 복록이 따르는 풍요의 시기입니다. 창작/교육/서비스 분야에서 두각을 나타냅니다.",
                "傷官": f"傷官 大運은 창의력이 폭발하지만 언행에 주의해야 하는 시기입니다. 예술/창업/자유업에서 빛나며 기존 틀을 깨는 성취를 거둡니다.",
                "偏財": f"偏財 大運은 사업/투자/이동이 활발한 도전의 시기입니다. 기복이 크므로 관리 능력이 성패를 가릅니다.",
                "正財": f"正財 大運은 성실한 노력이 재물로 축적되는 안정기입니다. 가정의 화목과 자산 형성에 최적의 시기입니다.",
                "偏官": f"偏官 大運은 시련과 도전이 교차하는 변곡점입니다. 강한 리더십으로 돌파하면 큰 권위를 얻게 됩니다.",
                "正官": f"正官 大運은 사회적 지위와 명예가 상승하는 시기입니다. 승진/자격 취득 등 공적 인정이 따릅니다.",
                "偏印": f"偏印 大運은 직관과 전문성이 강해지는 시기입니다. 특수 분야에서 독보적 역량을 쌓기에 좋습니다.",
                "正印": f"正印 大運은 귀인의 도움과 학문적 성취가 깃드는 시기입니다. 시험/자격증에서 좋은 결과를 냅니다.",
                "比肩": f"比肩 大運은 독립심과 경쟁이 강해지는 시기입니다. 지출 관리에 유의하며 자신만의 길을 개척해야 합니다.",
                "劫財": f"劫財 大運은 재물의 기복이 심한 시기입니다. 투기/보증/동업을 피하고 현상 유지에 집중하십시오.",
            }

            desc = DW_SS_DESC.get(dw_ss, f"{dw_ss} 十星 大運으로 {dw['str']}의 기운이 10년간 흐릅니다.")

            # DAEWOON_INTERP 천간·지지 해석
            dw_cg_interp = DAEWOON_INTERP.get(dw.get("cg", ""), "")
            dw_jj_interp = DAEWOON_INTERP.get(dw.get("jj", ""), "")

            interp_lines = []
            if dw_cg_interp:
                interp_lines.append(f"  천간 {dw.get('cg', '')}: {dw_cg_interp}")
            if dw_jj_interp:
                interp_lines.append(f"  지지 {dw.get('jj', '')}: {dw_jj_interp}")

            result.append(
                "\n".join(
                    [
                        f"-> {dw['시작나이']}세 ~ {dw['시작나이'] + 9}세 | {dw['str']} 大運 ({dw_ss}){cur_mark}",
                        f"({dw['시작연도']}년 ~ {dw['종료연도']}년)",
                        f"{'* 用神 大運 - 인생의 황금기' if is_yong else ''}",
                        f"{desc}",
                    ] + interp_lines + [
                        f"{'지금이 바로 큰 결정을 내려야 할 때입니다.' if is_yong and is_cur else '지금은 내실을 다지는 준비 기간입니다.' if not is_yong and is_cur else ''}",
                        f"",
                    ]
                )
            )

        result.append(
            "\n".join(
                [
                    "-> [ 인생 전체 흐름 요약 ]",
                    f"{display_name}님의 인생에서 가장 중요한 大運은 用神 {yong_kr} 오행이 들어오는 시기입니다. 이 시기에 큰 결정을 내리고 적극적으로 움직여야 합니다.",
                    f"현재 {current_age}세의 {display_name}님은 {'지금이 바로 황금기입니다. 두려워하지 말고 전진하십시오!' if cur_dw and _get_yongshin_match(cur_dw_ss, yongshin_ohs, ilgan_oh) == 'yong' else '지금은 준비 기간입니다. 다음 用神 大運을 위해 체력과 실력을 비축하십시오.'}",
                    "인생의 좋은 大運에 최대한 활동하고, 나쁜 大運에 최소한으로 노출되는 것 - 이것이 사주 활용의 핵심 전략입니다.",
                ]
            )
        )

        # -- 나이 단계별 분야 포커스 사전 ------------------------------


        DEFAULT_DOMAIN = {
            "초": {
                "학업": "학업에 성실히 임하고 진로를 탐색하십시오.",
                "부모": "가족과의 유대를 소중히 하십시오.",
                "활동": "다양한 경험이 자신을 성장시킵니다.",
            },
            "청장": {
                "재물": "운기를 주시하며 재물을 지키십시오.",
                "직업": "변화에 유연하게 대비하십시오.",
                "인연": "인연에 열린 자세를 유지하십시오.",
            },
            "말": {
                "건강": "건강 관리를 최우선으로 삼으십시오.",
                "명예": "그간의 삶을 되돌아보고 마음을 정리하십시오.",
                "안정": "가까운 사람들과의 따뜻한 시간을 소중히 하십시오.",
            },
        }

        for dw in daewoon[:9]:
            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            is_cur = dw["시작연도"] <= current_year <= dw["종료연도"]

            cur_mark = " [현재]" if is_cur else ""

            dw_age = int(dw.get("시작나이", 0))

            if dw_age < 20:
                d_stage, d_label = "초", "🌱 초년기"

                d_keys = ["학업", "부모", "활동"]

            elif dw_age < 60:
                d_stage, d_label = "청장", "🌿 청장년기"

                d_keys = ["재물", "직업", "인연"]

            else:
                d_stage, d_label = "말", "🍂 말년기"

                d_keys = ["건강", "명예", "안정"]

            stage_detail = DW_DOMAIN_STAGE.get(dw_ss, DEFAULT_DOMAIN).get(d_stage, DEFAULT_DOMAIN.get(d_stage, {}))

            lines_out = [f"[{k}]: {stage_detail.get(k, '운기를 살피십시오.')}" for k in d_keys]

            result.append(
                "\n".join(
                    [
                        "",
                        "",
                        f"-> {dw['시작나이']}~{dw['시작나이'] + 9}세 {dw['str']} ({dw_ss}大運){cur_mark} | {d_label}",
                    ]
                    + lines_out
                    + ["", ""]
                )
            )

        golden = [
            (dw["시작나이"], dw["str"])
            for dw in daewoon
            if _get_yongshin_match(
                TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-"),
                yongshin_ohs,
                ilgan_oh,
            )
            == "yong"
        ]

        crisis = [
            (dw["시작나이"], dw["str"])
            for dw in daewoon
            if TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-") in ["偏官", "劫財"]
            and _get_yongshin_match(
                TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-"),
                yongshin_ohs,
                ilgan_oh,
            )
            != "yong"
        ]

        golden_str = " / ".join([f"{a}세 {s}" for a, s in golden[:4]]) if golden else "꾸준한 노력이 황금기를 만듭니다"

        crisis_str = " / ".join([f"{a}세 {s}" for a, s in crisis[:3]]) if crisis else "없음"

        result.append(
            "\n".join(
                [
                    "",
                    "",
                    "-> [ 인생 황금기 vs 위기 구간 최종 정리 ]",
                    "",
                    f"[*] 황금기 구간: {golden_str}",
                    f"⚠️ 주의 구간: {crisis_str}",
                    "",
                    "황금기에는 적극 활동하고, 주의 구간에는 내실을 다지며 30%를 비축하십시오.",
                ]
            )
        )

        return "".join(result)

    else:  # "future"
        result = []

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"    -----------------------------------------------------",
                    f"      {display_name}님의 미래 3년 집중 분석",
                    f"    -----------------------------------------------------",
                    f"",
                    f"향후 3년은 {display_name}님 인생에서 중요한 변곡점이 될 수 있습니다. 각 해의 세운(歲運)을 분야별로 집중 분석합니다.",
                    f"",
                    f"",
                    f"",
                ]
            )
        )

        for y in range(current_year, current_year + 3):
            sw = get_yearly_luck(pils, y)

            dw = next((d for d in daewoon if d["시작연도"] <= y <= d["종료연도"]), None)

            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-") if dw else "-"

            sw_ss = sw.get("십성_천간", "-")

            sw_jj_ss = sw.get("지지십성", "-") if "지지십성" in sw else "-"

            age = y - birth_year + 1

            is_yong_sw = _get_yongshin_match(sw_ss, yongshin_ohs, ilgan_oh) == "yong"

            gilhyung = sw.get("길흉", "")

            # 길흉 마커

            gh_mark = "[길]" if gilhyung in ["길", "대길"] else "[평]" if gilhyung == "평" else "[의]"

            result.append(f"### {y}년 차트 ({age}세) | {sw['세운']} ({sw_ss}) {gh_mark}\n")

            if is_yong_sw:
                result.append(f"* [용신운] 올해는 하늘의 도움이 따르는 해입니다.\n")

            # 세운×대운 교차 분석 (연도별)
            try:
                cross_y = get_crossing_interpretation(pils, y) if pils else {}
                if cross_y.get("summary"):
                    result.append(f"  [교차분석] {cross_y['summary']}\n")
            except Exception:
                pass

            yd = YEAR_SS_DETAIL.get(
                sw_ss,
                {
                    "총평": f"{y}년 {sw.get('세운', '')} 세운이 흐릅니다.",
                    "돈": "재물 흐름을 주시하십시오.",
                    "직장": "직업적 변화에 유의하십시오.",
                    "연애": "인연에 관심을 기울이십시오.",
                    "건강": "건강 관리에 신경 쓰십시오.",
                    "조언": "차분히 흐름을 따르십시오.",
                },
            )

            star = "[*] " if is_yong_sw else "⚠️ " if sw_ss in ["편관", "겁재"] else "+ "

            result.append(
                "\n".join(
                    [
                        f"",
                        f"",
                        f"-----------------------------------------------------",
                        f"{star}{y}년 ({age}세) | {sw.get('세운', '')} 세운 | {sw_ss} / {gilhyung}",
                        f"-----------------------------------------------------",
                        f"",
                        f"{yd['총평']}",
                        f"",
                        f"[재물/돈]: {yd['돈']}",
                        f"",
                        f"[직장/사업]: {yd['직장']}",
                        f"",
                        f"[연애/관계]: {yd['연애']}",
                        f"",
                        f"[건강]: {yd['건강']}",
                        f"",
                        f"[핵심 조언]: {yd['조언']}",
                        f"",
                        f"",
                    ]
                )
            )

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"[ 3년 종합 전략 ]",
                    f"",
                    f"향후 3년 동안 {display_name}님이 가장 중점을 두어야 할 사항:",
                    f"",
                    f"1. 용신 {yong_kr} 강화 | 용신 오행의 색상, 음식, 방위를 일상에서 꾸준히 활용하십시오",
                    f"2. 기신 차단 | 기신 오행의 요소를 생활 공간에서 최소화하십시오",
                    f"3. {'적극적 투자와 도전 | 지금이 황금기의 연속입니다' if all(_get_yongshin_match(get_yearly_luck(pils, y).get('십성_천간', '-'), yongshin_ohs, ilgan_oh) == 'yong' for y in range(current_year, current_year + 2)) else '내실 다지기 | 지금은 준비 기간이니 실력 향상에 집중하십시오'}",
                    f"4. 건강 관리 | 사주의 취약한 오행 관련 기관을 정기적으로 점검하십시오",
                    f"5. 인맥 관리 | {'귀인을 만날 운기이니 새로운 사람들과의 교류에 적극적으로 나서십시오' if '정인' in [get_yearly_luck(pils, y).get('십성_천간') for y in range(current_year, current_year + 3)] else '신뢰 관계를 꾸준히 유지하고 새로운 파트너를 신중하게 선택하십시오'}",
                    f"",
                    f"",
                ]
            )
        )

        # 확장 - 월별 핵심 시기 분석

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"[ 올해 월별 운기 핵심 포인트 ]",
                    f"",
                    f"월별 세운(月運)을 통해 어느 달에 집중하고, 어느 달에 쉬어야 하는지 파악합니다.",
                    f"",
                    f"",
                ]
            )
        )

        try:
            month_data = []

            for m in range(1, 13):
                ml = get_monthly_luck(pils, current_year, m) if "get_monthly_luck" in dir() else None

                if ml:
                    m_ss = ml.get("십성", "")

                    m_str = ml.get("월주", "")

                    is_m_yong = _get_yongshin_match(m_ss, yongshin_ohs, ilgan_oh) == "yong"

                    mark = "*" if is_m_yong else "!" if m_ss in ["편관", "겁재"] else "o"

                    month_data.append(f"  {m:2d}월 {m_str:6s} ({m_ss:4s}) {mark}")

            if month_data:
                result.append("\n".join(month_data))

                result.append(
                    "\n".join(
                        [
                            f"",
                            f"",
                            f"",
                            f"* 별표 달: 이 달에 중요한 미팅, 계약, 투자 결정을 하십시오",
                            f"! 경고 달: 이 달에는 큰 결정을 피하고 수비 전략을 쓰십시오",
                            f"o 보통 달: 꾸준히 계획대로 진행하십시오",
                            f"",
                            f"",
                        ]
                    )
                )

        except Exception as e:
            _saju_log.debug(str(e))

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"[ 3년 분야별 최적 타이밍 ]",
                    f"",
                    f"[돈] 재물, 투자 최적 시기:",
                    f"{'* ' + str(current_year) + '년이 3년 중 재물 최고 시기입니다. 이 해에 투자, 계약을 집중하십시오.' if _get_yongshin_match(sw_now.get('십성_천간', ''), yongshin_ohs, ilgan_oh) == 'yong' else '* ' + str(current_year + 1) + '년에 재물 운이 더 강해질 것으로 예상됩니다.'}",
                    f"",
                    f"[직업] 직업, 사업 최적 시기:",
                    f"* 정관, 편관, 정인이 오는 해에 승진, 자격, 계약 기회를 노리십시오",
                    f"* {'지금이 새 사업을 시작하기에 좋은 흐름입니다.' if _get_yongshin_match(sw_now.get('십성_천간', ''), yongshin_ohs, ilgan_oh) == 'yong' else '새 사업은 다음 용신 세운이 올 때까지 기다리십시오.'}",
                    f"",
                    f"[연애] 연애, 결혼 최적 시기:",
                    f"* {'재성(남성) / 관성(여성) 세운이 오는 해가 결혼, 인연의 최적 시기입니다.' if gender == '남' else ''}",
                    f"* {'이 3년 중 ' + str(current_year) + '년이 이성 인연에 가장 활성화된 해입니다.' if (sw_now.get('십성_천간', '') in (['정재', '편재'] if gender == '남' else ['정관', '편관'])) else '적극적인 활동을 통해 인연의 기회를 만드십시오.'}",
                    f"",
                    f"[건강] 건강 주의 시기:",
                    f"* 편관, 겁재 세운은 건강 이상이 생기기 쉬운 시기입니다",
                    f"* 매년 정기 건강검진을 받고, 용신 오행 관련 기관을 특히 점검하십시오",
                    f"",
                    f"[ 3년 후 미래 | 지금의 선택이 만드는 5년 후 ]",
                    f"",
                    f"향후 3년을 어떻게 보내느냐에 따라 5년 후의 삶이 완전히 달라집니다.",
                    f"",
                    f"{'용신 대운이 진행 중인 지금, 이 황금기를 제대로 활용한다면 5년 후에는 재물/명예/건강 모두 크게 향상될 것입니다.' if cur_dw and _get_yongshin_match(cur_dw_ss, yongshin_ohs, ilgan_oh) == 'yong' else '지금의 준비 기간을 어떻게 보내느냐에 따라 다음 황금기의 높이가 결정됩니다. 지금 실력을 갈고닦으십시오.'}",
                    f"",
                    f"{display_name}님에게 드리는 3년 최종 처방:",
                    f'"지금 당장 할 수 있는 한 가지를 시작하십시오. 완벽한 타이밍을 기다리다 인생이 지나갑니다."',
                    f"",
                    f"",
                ]
            )
        )

        return "".join(result)


def _nar_wealth(ctx):
    """재물/사업 섹션 (money)"""

    ilgan = ctx.get("ilgan", "")

    ilgan_kr = ctx.get("ilgan_kr", "")

    iljj = ctx.get("iljj", "")

    iljj_kr = ctx.get("iljj_kr", "")

    ilgan_oh = ctx.get("ilgan_oh", "")

    current_year = ctx.get("current_year", datetime.now().year)

    current_age = ctx.get("current_age", 40)

    display_name = ctx.get("display_name", "내담자")

    birth_year = ctx.get("birth_year", 1980)

    gender = ctx.get("gender", "남")

    pils = ctx.get("pils", [(0, {}), (0, {})])

    sn = ctx.get("sn", "")

    strength_info = ctx.get("strength_info", {})

    gname = ctx.get("gname", "")

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    yong_kr = ctx.get("yong_kr", "")

    char = ctx.get("char", {})

    sn_narr = ctx.get("sn_narr", "")

    gnarr = ctx.get("gnarr", "")

    top_ss = ctx.get("top_ss", [])

    combos = ctx.get("combos", [])

    ss_dist = ctx.get("ss_dist", {})

    cur_dw = ctx.get("cur_dw", {})

    cur_dw_ss = ctx.get("cur_dw_ss", "")

    sw_now = ctx.get("sw_now", {})

    sw_next = ctx.get("sw_next", {})

    daewoon = ctx.get("daewoon", [])

    # ── ILGAN_PROFILE / GYEOKGUK_DETAIL / SIPSONG_DETAIL 재물 데이터 ──
    ilp = ILGAN_PROFILE.get(ilgan, {})
    ilp_money = ilp.get("재물", "")
    gd = GYEOKGUK_DETAIL.get(gname, {})
    gd_money = gd.get("재물", "")
    gd_job   = gd.get("직업", "")
    gd_note  = gd.get("주의", "")
    gd_rx    = gd.get("처방", "")

    # 세운×대운 교차 해석 (재물 섹션용)
    cross_money = {}
    try:
        cross_money = get_crossing_interpretation(pils, current_year) if pils else {}
    except Exception:
        pass

    if True:
        result = []

        # ── 제1장: 재물 기질 완전 분석 ──
        ss_money_lines = []
        for ss in top_ss[:2]:
            sd = SIPSONG_DETAIL.get(ss, {})
            if sd.get("재물"):
                ss_money_lines.append(f"  ■ {ss}({sd.get('한글','')}) 십성의 재물 스타일: {sd['재물']}")

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"    -----------------------------------------------------",
                    f"      {display_name}님의 재물, 사업 특화 완전 분석",
                    f"    -----------------------------------------------------",
                    f"",
                    f"재물(財物)은 사주에서 재성(財星)과 용신(用神)의 관계로 파악합니다. 얼마나 버느냐보다 어떤 방식으로 버는지, 어떤 시기에 돈이 모이는지를 아는 것이 진짜 재물 분석입니다.",
                    f"",
                    f"[ 제1장 | 재물 기질 완전 분석 ]",
                    f"",
                    f"  {display_name}님의 재물 버는 방식 — 일간 {ilgan_kr} + {sn} + 주도 십성 {', '.join(top_ss[:3])}",
                    f"",
                    f"  [일간 {ilgan_kr}의 재물 그릇]",
                    f"  {ilp_money}" if ilp_money else "",
                    f"",
                    f"  [격국({gname})의 재물 운]",
                    f"  {gd_money}" if gd_money else f"  격국에 맞는 방식으로 재물을 쌓아가십시오.",
                    f"  적성 분야: {gd_job}" if gd_job else "",
                    f"",
                ] + ss_money_lines + [
                    f"",
                    f"  [재물 주의사항]",
                    f"  {gd_note}" if gd_note else "  기신 오행이 강해지는 해에 무리한 투자를 자제하십시오.",
                    f"  [재물 처방]",
                    f"  {gd_rx}" if gd_rx else "  용신 오행이 강한 시기에 핵심 결정을 집중하십시오.",
                    f"",
                    f"",
                ]
            )
        )

        for key, combo in combos[:3]:
            result.append(
                "\n".join(
                    [
                        f"",
                        f"",
                        f"* [{' x '.join(key)}] 재물 조합",
                        f"",
                        f"{combo.get('요약', '')}",
                        f"",
                        f"재물 버는 방식: {combo.get('재물', '')}",
                        f"맞는 사업/직업: {combo.get('직업', '')}",
                        f"재물 주의사항: {combo.get('주의', '')}",
                        f"",
                        f"",
                    ]
                )
            )

        # ── 세운×대운 교차 재물 분석 ──
        if cross_money.get("summary") or cross_money.get("finance"):
            result.append(
                "\n".join([
                    f"",
                    f"[ 세운×대운 교차 재물 분석 ]",
                    f"",
                    f"  {cross_money.get('summary', '')}",
                    f"  {cross_money.get('finance', '')}",
                    f"  {cross_money.get('career', '')}",
                    f"",
                ])
            )

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"[ 제2장 | 재물 운기 분석 | 돈이 모이는 시기와 새는 시기 ]",
                    f"",
                    f"사주에서 재물은 대운과 세운의 조합으로 결정됩니다. 용신 오행이 들어오는 해에 재물이 모이고, 기신 오행이 강해지는 해에 재물이 나갑니다.",
                    f"",
                    f"현재 {cur_dw['str'] if cur_dw else '-'} 대운 ({cur_dw_ss})",
                    f"{'> 이 대운은 용신 대운으로, 재물이 모이기 좋은 10년입니다. 적극적으로 투자하고 수익 구조를 만들어가십시오.' if cur_dw and _get_yongshin_match(cur_dw_ss, yongshin_ohs, ilgan_oh) == 'yong' else '> 이 대운은 재물 관리에 신중해야 하는 시기입니다. 무리한 투자보다 기존 자산을 지키는 전략이 중요합니다.'}",
                    f"",
                    f"올해 {sw_now.get('세운', '')} 세운 ({sw_now.get('십성_천간', '')} / {sw_now.get('길흉', '')})",
                    f"{'> 올해는 재물 운이 활성화되는 해입니다. 새로운 수입원을 만들거나 투자를 시작하기 좋습니다.' if _get_yongshin_match(sw_now.get('십성_천간', ''), yongshin_ohs, ilgan_oh) == 'yong' else '> 올해는 재물 지출에 주의해야 합니다. 불필요한 지출을 줄이고 저축에 집중하십시오.'}",
                    f"",
                    f"[ 제3장 | 투자 유형 분석 ]",
                    f"",
                    f"{display_name}님의 사주에서 가장 잘 맞는 투자 유형:",
                    f"",
                    f"{'[v] 부동산 투자 | 토(土) 기운과 관련된 투자로 장기적으로 안정적인 수익을 줍니다.' if '土' in yongshin_ohs else ''}",
                    f"{'[v] 금융, 주식 투자 | 금(金) 기운과 관련된 투자로 결단력 있게 움직이면 수익이 납니다.' if '金' in yongshin_ohs else ''}",
                    f"{'[v] 무역, 유통 투자 | 수(水) 기운과 관련된 투자로 흐름을 잘 타면 큰 수익을 냅니다.' if '水' in yongshin_ohs else ''}",
                    f"{'[v] 성장주, 벤처 투자 | 목(木) 기운과 관련된 투자로 초기 단계 투자에서 강합니다.' if '木' in yongshin_ohs else ''}",
                    f"{'[v] 에너지, 문화 투자 | 화(火) 기운과 관련된 투자로 사람과 콘텐츠에서 수익이 납니다.' if '火' in yongshin_ohs else ''}",
                    f"",
                    f"! 피해야 할 투자 유형 (기신 오행 관련):",
                    f"{'기신 오행의 산업/자산에는 투자를 자제하십시오. 아무리 좋아 보여도 이 분의 사주에서는 기신 오행 투자가 손실로 이어지는 경우가 많습니다.'}",
                    f"",
                    f"[ 제4장 | 사업 적합성 분석 ]",
                    f"",
                    f"{display_name}님의 사주가 독립사업과 직장 중 어느 쪽이 더 맞는지:",
                    f"",
                    f"{'비견/겁재가 강한 이 사주는 독립사업/자영업이 더 맞습니다. 남 밑에서 지시받기보다 자신만의 영역에서 일할 때 재물이 쌓입니다.' if any(ss in top_ss for ss in ['비견', '겁재']) else ''}",
                    f"{'식신/상관이 강한 이 사주는 창의적인 사업 또는 프리랜서 활동이 맞습니다. 재능을 상품화하는 방식이 가장 효율적인 재물 창출입니다.' if any(ss in top_ss for ss in ['식신', '상관']) else ''}",
                    f"{'정관/정재가 강한 이 사주는 안정적인 직장에서 꾸준히 성장하는 방식이 맞습니다. 조직 내에서 신뢰를 쌓는 것이 재물로 이어집니다.' if any(ss in top_ss for ss in ['정관', '정재']) else ''}",
                    f"{'편재/편관이 강한 이 사주는 역동적인 사업 환경에서 강합니다. 위험을 감수하고 크게 움직이는 것을 두려워하지 마십시오.' if any(ss in top_ss for ss in ['편재', '편관']) else ''}",
                    f"",
                    f"[ 제5장 | 재물 새는 구멍과 막는 법 ]",
                    f"",
                    f"이 사주에서 재물이 새는 주요 원인:",
                    f"",
                    f"{'1. 겁재가 강해 주변 사람들에게 베풀다가 재물이 분산됩니다. 감정적 지출을 줄이십시오.' if '겁재' in ss_dist else ''}",
                    f"{'2. 상관이 강해 충동적인 소비나 불필요한 지출이 생깁니다. 구매 전 하루 생각하는 습관을 들이십시오.' if '상관' in ss_dist else ''}",
                    f"{'3. 편재가 강해 투자 욕구가 넘쳐 무리하게 확장하다 손실이 납니다. 수익의 30%는 반드시 안전 자산으로 보관하십시오.' if '편재' in ss_dist else ''}",
                    f"{'4. 편인이 강해 직업 변동이 잦아 안정적인 수입 구조를 만들기 어렵습니다. 한 분야에 집중하는 것이 재물 관리의 핵심입니다.' if '편인' in ss_dist else ''}",
                    f"",
                    f"재물을 지키는 가장 좋은 방법:",
                    f"* 용신 {yong_kr} 색상의 지갑 사용",
                    f"* 수입의 20~30% 자동 저축 설정",
                    f"* 기신 오행이 강한 해에는 큰 재물 결정 미루기",
                    f"* 용신 오행이 강한 해에 투자 및 사업 확장",
                    f"",
                    f"[ 제6장 | 재물 황금기 완전 예측 ]",
                    f"",
                    f"{display_name}님의 인생에서 재물 황금기가 오는 시기:",
                    f"",
                    f"",
                ]
            )
        )

        # 향후 대운 중 용신 대운 찾기

        peak_years = []

        for dw in daewoon:
            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            if _get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong":
                age_mid = dw["시작나이"] + 5

                year_mid = birth_year + age_mid - 1

                peak_years.append(f"* {dw['시작나이']}~{dw['시작나이'] + 9}세 ({dw['시작연도']}~{dw['종료연도']}년): {dw['str']} 용신 대운 | 이 10년이 {display_name}님의 재물 황금기입니다")

        result.append("\n".join(peak_years[:3]) if peak_years else "* 꾸준한 노력이 재물 황금기를 만듭니다")

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"",
                    f"재물 황금기를 최대로 활용하는 전략:",
                    f"1. 황금기 대운이 시작되기 2~3년 전부터 준비하십시오",
                    f"2. 황금기에는 두려움 없이 과감하게 투자하십시오",
                    f"3. 황금기의 수익은 다음 어려운 시기를 위해 30% 이상 비축하십시오",
                    f"4. 사업을 시작한다면 황금기 대운 초반에 시작하는 것이 가장 좋습니다",
                    f"",
                    f"[ 제7장 | 재물 관리의 황금 원칙 | 이 사주에만 해당하는 처방 ]",
                    f"",
                    f"일간 {ilgan_kr} + {gname} + {sn} 조합의 재물 관리 황금 원칙:",
                    f"",
                    f"원칙 1. {'크게 벌고 크게 쓰는 패턴을 끊어야 합니다. 수입이 생기면 즉시 30%를 자동이체로 저축하십시오.' if any(ss in ss_dist for ss in ['겁재', '편재']) else '안정적으로 쌓아가는 것이 이 사주의 재물 방식입니다. 투기성 투자에 유혹받지 마십시오.'}",
                    f"",
                    f"원칙 2. {'창의력과 재능이 돈이 됩니다. 자신의 전문성을 상품화하는 방법을 끊임없이 고민하십시오.' if any(ss in ss_dist for ss in ['식신', '상관']) else '안정적 수입 구조를 먼저 만들고 투자를 시작하십시오.'}",
                    f"",
                    f"원칙 3. 용신 {yong_kr} 오행이 강해지는 해에 큰 재물 결정을 집중하고, 기신이 강해지는 해에는 지키는 전략을 쓰십시오.",
                    f"",
                    f"원칙 4. {'부동산은 이 사주에 중장기적으로 좋은 자산입니다.' if '土' in yongshin_ohs else '금융 자산과 현금 유동성을 충분히 유지하십시오.' if '水' in yongshin_ohs or '金' in yongshin_ohs else '성장하는 분야에 일찍 진입하는 것이 이 사주의 재물 전략입니다.' if '木' in yongshin_ohs else '콘텐츠/사람/브랜드에 투자하는 것이 이 사주의 재물 방식입니다.'}",
                    f"",
                    f"원칙 5. 보증/동업에서 재물을 잃는 경우가 많습니다. 계약서 없는 재물 거래는 절대 하지 마십시오.",
                    f"",
                    f"[ 제8장 | 직업별 예상 소득 패턴 분석 ]",
                    f"",
                    f"{display_name}님의 사주에서 각 직업 유형별 예상 소득 패턴:",
                    f"",
                    f"* 직장인: 꾸준하고 안정적이지만 {'가파른 성장은 어렵습니다. 전문성을 쌓아 희소 인재가 되어야 합니다.' if '신강' in sn else '귀인의 도움으로 예상보다 빠른 성장이 가능합니다.'}",
                    f"",
                    f"* 프리랜서/자영업: {'이 사주에 가장 잘 맞는 방식입니다. 초기 기반을 잡는 데 3~5년이 필요하지만, 그 후에는 직장보다 훨씬 큰 수익을 낼 수 있습니다.' if any(ss in ss_dist for ss in ['비견', '식신', '상관']) else '안정적인 수입이 보장되지 않는 방식이라 이 사주에는 주의가 필요합니다.'}",
                    f"",
                    f"* 투자/사업: {'편재가 강해 사업 확장 기질이 있습니다. 단, 리스크 관리가 생존의 핵심입니다.' if '편재' in ss_dist else '안정적인 사업 기반을 만든 후 확장하는 보수적 전략이 맞습니다.'}",
                    f"",
                    f"[ 제9장 | 나이별 재물 타이밍 완전 분석 ]",
                    f"",
                    f"인생의 각 10년 구간에서 재물 운의 흐름:",
                    f"",
                    f"",
                ]
            )
        )

        for dw in daewoon[:8]:
            dw_ss_hanja = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            # 한자 → 한글 변환 (TEN_GODS_MATRIX는 한자 반환)

            _SS_KR = {
                "食神": "식신",
                "傷官": "상관",
                "偏財": "편재",
                "正財": "정재",
                "偏官": "편관",
                "正官": "정관",
                "偏印": "편인",
                "正印": "정인",
                "比肩": "비견",
                "劫財": "겁재",
            }

            dw_ss = _SS_KR.get(dw_ss_hanja, dw_ss_hanja)

            is_yong = _get_yongshin_match(dw_ss_hanja, yongshin_ohs, ilgan_oh) == "yong"

            money_advice = {
                "식신": "재능 소득·창작 수익이 들어오는 시기",
                "상관": "혁신적 방식으로 새 수익원 개척 시기",
                "편재": "⭐ 투자·사업으로 크게 버는 시기 (기복 주의)",
                "정재": "안정적 저축·자산 축적 최적 시기",
                "편관": "⚠️ 재물 보호·손실 방어가 우선인 시기",
                "정관": "직장·명예를 통한 합법적 소득 증가 시기",
                "편인": "전문성 투자 시기 (미래 재물의 씨앗)",
                "정인": "귀인을 통한 재물 기회 시기",
                "비견": "재물 분산 주의·독립 수익 도전 시기",
                "겁재": "❌ 재물 손실 위험·투기 절대 금지 시기",
            }.get(dw_ss, f"{dw_ss_hanja} 기운의 운기")

            yong_mark = " ★[용신 황금기]" if is_yong else ""

            result.append(f"  {dw['시작나이']}~{dw['시작나이'] + 9}세 ({dw_ss_hanja}/{dw_ss}): {money_advice}{yong_mark}\n")

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"",
                    f"[ 제10장 | 만신의 재물 최종 처방 ]",
                    f"",
                    f"{display_name}님의 재물 운을 한마디로 요약하면:",
                    f'"{combos[0][1].get("재물", "타고난 방식으로 꾸준히 쌓아가는 재물") if combos else "성실함과 전문성으로 재물을 쌓아가는 사주"}"',
                    f"",
                    f'이 사주에서 재물이 들어오는 문은 "{", ".join(top_ss[:2])}"이(가) 열어줍니다.',
                    f"이 문이 활성화되는 운기에 최대로 움직이고, 닫히는 운기에는 지키십시오.",
                    f"",
                    f"재물은 복이지만 집착하면 독이 됩니다. {display_name}님만의 방식으로 재물을 이루어 나가십시오.",
                    f"",
                    f"",
                ]
            )
        )

        return "".join(result)


def _nar_health(ctx):
    """인간관계/육친 섹션 (relations)"""

    ilgan = ctx.get("ilgan", "")

    ilgan_kr = ctx.get("ilgan_kr", "")

    iljj = ctx.get("iljj", "")

    iljj_kr = ctx.get("iljj_kr", "")

    ilgan_oh = ctx.get("ilgan_oh", "")

    current_year = ctx.get("current_year", datetime.now().year)

    current_age = ctx.get("current_age", 40)

    display_name = ctx.get("display_name", "내담자")

    birth_year = ctx.get("birth_year", 1980)

    gender = ctx.get("gender", "남")

    pils = ctx.get("pils", [(0, {}), (0, {})])

    sn = ctx.get("sn", "")

    strength_info = ctx.get("strength_info", {})

    gname = ctx.get("gname", "")

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    yong_kr = ctx.get("yong_kr", "")

    char = ctx.get("char", {})

    sn_narr = ctx.get("sn_narr", "")

    gnarr = ctx.get("gnarr", "")

    top_ss = ctx.get("top_ss", [])

    combos = ctx.get("combos", [])

    ss_dist = ctx.get("ss_dist", {})

    cur_dw = ctx.get("cur_dw", {})

    cur_dw_ss = ctx.get("cur_dw_ss", "")

    sw_now = ctx.get("sw_now", {})

    sw_next = ctx.get("sw_next", {})

    daewoon = ctx.get("daewoon", [])

    # ── get_relationship_reading() 연동 ──
    rr = {}
    try:
        rr = get_relationship_reading(pils, gender) if pils else {}
    except Exception:
        pass

    if True:
        result = []

        yk = get_yukjin(ilgan, pils, gender)

        sipsung_data = calc_sipsung(ilgan, pils)

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"    -----------------------------------------------------",
                    f"      {display_name}님의 인간관계, 육친 완전 분석",
                    f"    -----------------------------------------------------",
                    f"",
                    f"인간관계는 사주에서 십성(十星)과 육친(六親)을 통해 분석합니다. 어떤 사람과 인연이 깊은지, 어떤 사람과 갈등이 생기는지를 사주는 미리 알려줍니다.",
                    f"",
                    f"[ 제1장 | 일간의 대인관계 패턴 ]",
                    f"",
                    f"{display_name}님은 일간 {ilgan_kr} + {sn}의 조합으로 다음과 같은 대인관계 패턴을 가집니다:",
                    f"",
                    f"{'* 신강하여 자기주장이 강합니다. 타인의 의견을 경청하는 연습이 관계 개선의 핵심입니다.' if '신강' in sn else '* 신약하여 타인의 영향을 많이 받습니다. 자신의 의견을 분명히 표현하는 연습이 필요합니다.' if '신약' in sn else '* 중화 사주로 균형 잡힌 대인관계를 유지합니다. 극단적인 관계보다 안정적인 인간관계를 선호합니다.'}",
                    f"",
                    f"{'* 비견, 겁재가 강해 경쟁적인 관계에서 에너지를 발산합니다.' if any(ss in ss_dist for ss in ['비견', '겁재']) else ''}",
                    f"{'* 식신, 상관이 강해 자신을 잘 표현하고 주변에 즐거움을 줍니다.' if any(ss in ss_dist for ss in ['식신', '상관']) else ''}",
                    f"{'* 정관, 편관이 강해 조직과 권위를 의식하며 사회적 관계에 민감합니다.' if any(ss in ss_dist for ss in ['정관', '편관']) else ''}",
                    f"{'* 정인, 편인이 강해 스승과 선배로부터 배우고 지식을 나누는 관계를 중요시합니다.' if any(ss in ss_dist for ss in ['정인', '편인']) else ''}",
                    f"",
                    f"[ 제2장 | 육친 상세 분석 ]",
                    f"",
                    f"",
                ]
            )
        )

        YUKJIN_DEEP = {
            "어머니(正印)": f"정인은 어머니의 자리입니다. {display_name}님과 어머니의 관계는 사주에서 매우 중요한 영향을 미칩니다. 정인이 있다면 어머니의 음덕(蔭德)이 크며, 어머니로부터 정서적/물질적 도움을 받는 운입니다. 학문과 귀인을 상징하는 정인이 강하면 교육열이 높고 스승의 인연이 좋습니다.",
            "계모(偏印)": f"편인은 계모/이모/외조모 등 어머니 외의 여성 윗사람을 상징합니다. 편인이 강하면 독특한 재능과 직관이 있으며, 특수 분야에서 독보적인 능력을 발휘합니다. 단, 식신을 억제하면 도식이 형성되어 복이 꺾이는 작용이 있습니다.",
            "아버지(偏財)": f"편재는 아버지의 자리입니다. {display_name}님과 아버지의 관계가 이 사주에 큰 영향을 줍니다. 편재가 있다면 아버지로부터 재물적 도움이나 사업적 조언을 받을 수 있습니다. 편재는 활동적이고 외향적인 아버지의 기운으로, 아버지가 사업가이거나 활발한 분인 경우가 많습니다.",
            "아내(正財)": f"정재는 남성에게 아내의 자리입니다. 정재가 있으면 성실하고 현모양처형 배우자를 만나는 운입니다. 정재가 강하면 안정적인 가정생활을 영위하며, 배우자의 내조가 큰 힘이 됩니다. 다만 정재가 너무 강하면 돈과 배우자에 집착하는 경향이 생길 수 있습니다.",
            "남편(正官)": f"정관은 여성에게 남편의 자리입니다. 정관이 있으면 점잖고 안정적인 남편 인연이 있습니다. 사회적으로 인정받는 남성을 만나는 운이며, 결혼 후 안정적인 가정생활을 할 가능성이 높습니다.",
            "아들(偏官)": f"편관(칠살)은 남성에게 아들, 여성에게는 정부(情夫)를 상징합니다. 편관이 있으면 자녀로 인한 기쁨과 함께 자녀 교육에 많은 에너지를 쏟습니다. 칠살이 제화(制化)되면 자녀가 사회적으로 성공하는 운입니다.",
            "딸(正官)": f"정관은 남성에게 딸을 상징합니다. 딸과의 관계가 따뜻하고 격식 있습니다. 자녀가 안정적이고 사회적으로 인정받는 삶을 사는 운입니다.",
            "형제(比肩)": f"비견은 형제/자매/친구/동료를 상징합니다. 비견이 강하면 형제자매나 친구와의 인연이 깊습니다. 서로 경쟁하면서도 성장하는 관계이며, 동업이나 협업을 통해 시너지를 낼 수 있습니다.",
            "이복형제(劫財)": f"겁재는 이복 형제/경쟁자/라이벌을 상징합니다. 겁재가 강하면 주변에 경쟁자가 많고, 재물이 분산될 수 있습니다. 그러나 건강한 경쟁 의식으로 발전시키면 강한 추진력이 됩니다.",
        }

        for item in yk:
            fam = item.get("관계", "")

            has = item.get("present", False)

            where = item.get("위치", "없음")

            deep_desc = YUKJIN_DEEP.get(fam, item.get("desc", ""))

            result.append(
                "\n".join(
                    [
                        f"",
                        f"",
                        f"* {fam}",
                        f"   위치: {where if where != '없음' else '원국에 직접 없음'}",
                        f"   인연 강도: {'강함 | 이 인연이 인생에 크게 영향을 미칩니다' if has else '약함 | 인연이 엷거나 독립적인 관계'}",
                        f"",
                        f"   {deep_desc}",
                        f"",
                        f"   {'이 육친과의 관계가 이 분의 운명에 핵심적인 역할을 합니다. 이 관계를 잘 가꾸십시오.' if has else '이 육친과의 관계에서 독립적인 성향이 강합니다. 의식적으로 관계를 돌보는 노력이 필요합니다.'}",
                        f"",
                        f"",
                    ]
                )
            )

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"[ 제3장 | 이성 인연, 배우자 분석 ]",
                    f"",
                    f"일지(日支) {iljj_kr}({iljj})는 배우자 자리입니다. 이 자리의 기운이 배우자의 성품과 부부 관계의 방향을 결정합니다.",
                    f"",
                    f"{display_name}님의 배우자 자리 분석:",
                    f"* {iljj_kr}({iljj}) 일지 | {'안정과 포용력을 가진 배우자' if iljj in ['丑(축)', '辰(진)', '戌(술)', '未(미)'] else '열정적이고 활기찬 배우자' if iljj in ['午(오)', '巳(사)', '寅(인)'] else '논리적이고 실력 있는 배우자' if iljj in ['申(신)', '酉(유)', '亥(해)', '子(자)'] else '성장하는 에너지를 가진 배우자' if iljj in ['卯(묘)'] else '포용력 있는 배우자'}를 만나는 운입니다.",
                    f"",
                    f"이성 인연이 강해지는 시기:",
                    f"* {'재성(財星) 세운 | 편재, 정재 세운이 올 때 이성 인연이 활성화됩니다.' if gender == '남' else '* 관성(官星) 세운 | 정관, 편관 세운이 올 때 이성 인연이 활성화됩니다.'}",
                    f"* 현재 대운 {cur_dw['str'] if cur_dw else '-'} | {'이성 인연이 활성화되는 대운입니다' if cur_dw_ss in (['정재', '편재'] if gender == '남' else ['정관', '편관']) else '배우자 운보다 다른 분야가 강조되는 대운입니다'}",
                    f"",
                    f"이상적인 파트너의 특징:",
                    f"* 용신 {yong_kr} 오행을 가진 사람과 궁합이 잘 맞습니다",
                    f"* {'불, 에너지가 강한 사람' if '火' in yongshin_ohs else ''}{'땅처럼 안정적인 사람' if '土' in yongshin_ohs else ''}{'물처럼 지혜로운 사람' if '水' in yongshin_ohs else ''}{'나무처럼 성장하는 사람' if '木' in yongshin_ohs else ''}{'금처럼 결단력 있는 사람' if '金' in yongshin_ohs else ''}이(가) 이상적인 파트너입니다",
                    f"",
                    f"[ 제4장 | 사회적 인간관계 조언 ]",
                    f"",
                    f"{display_name}님이 만나야 할 귀인(貴人)의 특징:",
                    f"* 용신 오행이 강한 분야(직업, 전공)에 있는 사람이 귀인입니다",
                    f"* {'수학, 금융, 법, 의료, 공학 분야의 전문가' if '金' in yongshin_ohs or '水' in yongshin_ohs else '교육, 예술, 봉사, 문화 분야의 전문가' if '木' in yongshin_ohs or '火' in yongshin_ohs else '부동산, 건설, 농업, 토지 관련 분야의 전문가' if '土' in yongshin_ohs else '다양한 분야의 전문가'}와의 인연을 소중히 하십시오",
                    f"",
                    f"조심해야 할 인연:",
                    f"* 기신 오행이 강한 사람과는 재물 거래나 동업을 피하십시오",
                    f"* 겁재가 강하게 들어오는 해에 만나는 사업 파트너는 신중히 검토하십시오",
                    f"* 겉으로는 화려해 보이지만 실속이 없는 관계에 에너지를 낭비하지 마십시오",
                    f"",
                    f"인간관계에서 {display_name}님만의 강점:",
                    f"{char.get('장점', '타고난 성품으로 주변 사람들에게 신뢰를 줍니다')}",
                    f"",
                    f"이 강점을 살려 인간관계를 넓혀가면, 그 관계가 결국 재물과 명예로 돌아오는 운명입니다.",
                    f"",
                    f"[ 제5장 | 연애, 결혼 심층 분석 ]",
                    f"",
                    f"{'남성' if gender == '남' else '여성'} {ilgan_kr} 일간의 연애 스타일:",
                    f"* {ILGAN_PROFILE.get(ilgan, {}).get('연애', char.get('연애_남', '') if gender == '남' else char.get('연애_여', ''))}",
                    f"",
                    f"배우자 자리 {iljj_kr}({iljj}) 심층 해석:",
                    f"  일지 십성: {rr.get('파트너_십성', '')} — {rr.get('파트너_기질', iljj_kr + '이(가) 배우자 자리에 있습니다.')}",
                    f"",
                    f"오행별 연애 스타일:",
                    f"  {rr.get('연애_스타일', ILGAN_PROFILE.get(ilgan, {}).get('연애', ''))}",
                    f"",
                    f"이상적인 배우자의 오행:",
                    f"* 용신 {yong_kr} 오행이 강한 사람 — 이 분과 함께하면 삶이 더 풍요로워집니다",
                    f"* {ILGAN_PROFILE.get(ilgan, {}).get('처방', '자신의 부족한 점을 채워주는 파트너가 이상적입니다.')}",
                    f"",
                ] + ([
                    f"  연애 관련 신살: {', '.join(rr['연애_신살'])}",
                    f"  → 신살의 기운이 이성 인연을 강하게 활성화합니다. 적극적으로 나서십시오.",
                    f"",
                ] if rr.get("연애_신살") else []) + [
                    f"  결혼 시기 힌트: {rr.get('결혼_힌트', '')}",
                    f"",
                    f"결혼 운기 분석:",
                    f"현재 {current_age}세 기준:",
                    f"* {'재성 대운 — 결혼 에너지가 활성화되어 있습니다.' if cur_dw and cur_dw_ss in (['정재', '편재'] if gender == '남' else ['정관', '편관']) else '관성 대운 — 결혼 에너지가 활성화되어 있습니다.' if cur_dw and cur_dw_ss in (['정관', '편관'] if gender == '남' else ['정재', '편재']) else '지금은 자기 개발에 집중하는 시기. 준비가 되면 인연이 옵니다.'}",
                    f"* 가장 강한 결혼 기회가 오는 세운: {'정재·편재 세운' if gender == '남' else '정관·편관 세운'}",
                    f"",
                    f"[ 제6장 | 직장 내 인간관계 전략 ]",
                    f"",
                    f"{gname}을 가진 분의 직장 인간관계 패턴:",
                    f"* {'정관격은 상사와 원칙적이고 예의 바른 관계를 형성합니다. 규칙을 잘 지키고 성실한 모습이 신뢰를 얻습니다.' if '정관' in gname else '편관격은 직장에서 경쟁이 치열하고 상사와 갈등이 생기기 쉽습니다. 실력으로 인정받는 것이 최선입니다.' if '편관' in gname else '격국의 기운이 직장 내 관계에 영향을 줍니다.'}",
                    f"",
                    f"동료와의 관계:",
                    f"* {'비견이 강해 동료 간 경쟁이 활발합니다. 협력을 통해 함께 성장하는 방식이 더 유리합니다.' if '비견' in ss_dist or '겁재' in ss_dist else '식신, 상관이 강해 동료들에게 재미와 영감을 주는 존재입니다. 분위기 메이커 역할이 강점입니다.' if '식신' in ss_dist or '상관' in ss_dist else '정관, 정인이 강해 조직 내에서 신뢰받는 전문가로 인식됩니다.' if '정관' in ss_dist or '정인' in ss_dist else '독특한 개성으로 직장 내 독보적인 존재감을 가집니다.'}",
                    f"",
                    f"직장에서 조심해야 할 사람:",
                    f"* 기신 오행이 강한 상사나 동료와는 재물 거래를 피하십시오",
                    f"* 자신을 이용하려는 person을 빨리 알아채는 직관을 기르십시오",
                    f"",
                    f"[ 제7장 | 인간관계 운기별 전략 ]",
                    f"",
                    f"현재 {cur_dw['str'] if cur_dw else '-'} 대운에서의 인간관계:",
                    f"{'* 인성 대운: 스승, 어른의 도움이 큰 시기입니다. 배움의 인연을 소중히 하십시오.' if cur_dw_ss in ['정인', '편인'] else '* 재성 대운: 이성 인연과 사업 파트너 운이 강합니다.' if cur_dw_ss in ['정재', '편재'] else '* 관성 대운: 사회적 관계와 권위자와의 인연이 중요해집니다.' if cur_dw_ss in ['정관', '편관'] else '* 비겁 대운: 동료, 친구, 경쟁자와의 관계가 인생의 중심이 됩니다.' if cur_dw_ss in ['비견', '겁재'] else '* 식상 대운: 자기표현과 인기가 중심이 되는 시기입니다.'}",
                    f"",
                    f"올해 {sw_now.get('세운', '')} 세운에서의 인간관계:",
                    f"{'* 새로운 귀인을 만날 운기입니다. 모임, 행사에 적극적으로 참여하십시오.' if _get_yongshin_match(sw_now.get('십성_천간', ''), yongshin_ohs, ilgan_oh) == 'yong' else '* 인간관계에서 신중함이 요구되는 해입니다. 새로운 동업이나 큰 부탁은 자제하십시오.'}",
                    f"",
                    f"[ 제8장 | 만신의 인간관계 최종 처방 ]",
                    f"",
                    f"{display_name}님의 인간관계 핵심 비결:",
                    f"",
                    f"1. {char.get('장점', '타고난 성품')}을(를) 인간관계에서 최대로 발휘하십시오",
                    f"2. {char.get('단점', '약점')}을(를) 의식적으로 보완하는 노력을 하십시오",
                    f"3. 용신 {yong_kr} 오행이 강한 분야의 사람들과 더 많이 교류하십시오",
                    f"4. 인간관계에 투자한 시간과 에너지는 결국 재물과 명예로 돌아옵니다",
                    f"",
                    f'    "Good relationships create good luck, and good luck creates a good life."',
                    f"",
                    f"",
                ]
            )
        )

        return "".join(result)


def _nar_past(ctx):
    """과거 적중 섹션 (past)"""

    ilgan = ctx.get("ilgan", "")

    ilgan_kr = ctx.get("ilgan_kr", "")

    iljj = ctx.get("iljj", "")

    iljj_kr = ctx.get("iljj_kr", "")

    ilgan_oh = ctx.get("ilgan_oh", "")

    current_year = ctx.get("current_year", datetime.now().year)

    current_age = ctx.get("current_age", 40)

    display_name = ctx.get("display_name", "내담자")

    birth_year = ctx.get("birth_year", 1980)

    gender = ctx.get("gender", "남")

    pils = ctx.get("pils", [(0, {}), (0, {})])

    sn = ctx.get("sn", "")

    strength_info = ctx.get("strength_info", {})

    gname = ctx.get("gname", "")

    yongshin_ohs = ctx.get("yongshin_ohs", [])

    yong_kr = ctx.get("yong_kr", "")

    char = ctx.get("char", {})

    sn_narr = ctx.get("sn_narr", "")

    gnarr = ctx.get("gnarr", "")

    top_ss = ctx.get("top_ss", [])

    combos = ctx.get("combos", [])

    ss_dist = ctx.get("ss_dist", {})

    cur_dw = ctx.get("cur_dw", {})

    cur_dw_ss = ctx.get("cur_dw_ss", "")

    sw_now = ctx.get("sw_now", {})

    sw_next = ctx.get("sw_next", {})

    daewoon = ctx.get("daewoon", [])

    if True:
        result = []

        result.append(
            "\n".join(
                [
                    f"",
                    f"",
                    f"    -----------------------------------------------------",
                    f"      {display_name}님의 과거 적중 타임라인 분석",
                    f"    -----------------------------------------------------",
                    f"",
                    f"과거의 사건들을 사주 엔진으로 분석한 결과입니다. 특정 시기에 발생한 강한 기운의 변화(충, 합)가 실제 삶에서 어떻게 나타났는지 확인해 보십시오.",
                    f"",
                    f"",
                    f"",
                ]
            )
        )

        try:
            highlights = generate_engine_highlights(pils, birth_year, gender)
        except (NameError, Exception):
            highlights = {"past_events": []}

        for event in highlights.get("past_events", []):
            result.append(f"### {event.get('age')}세 ({event.get('year')}년) | {event.get('title')}\n")

            result.append(f"{event.get('desc')}\n\n")

        result.append("""

[ 과거 분석의 의미 ]

과거를 분석하는 것은 미래를 대비하기 위함입니다. 어떤 운기에 어떤 사건이 일어났는지 패턴을 파악하면, 다가올 운기에서 최선의 선택을 할 수 있습니다.

""")

        return "".join(result)


def build_life_analysis(pils, gender):
    """십성 2-조합으로 인생 전체를 읽는 핵심 엔진"""
    ilgan = pils[1]["cg"]
    ss_count = {}
    for p in pils:
        cg_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(p["cg"], "")
        jjg = JIJANGGAN.get(p["jj"], [])
        jj_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(jjg[-1] if jjg else "", "")
        for ss in [cg_ss, jj_ss]:
            if ss and ss not in ("-", ""):
                ss_count[ss] = ss_count.get(ss, 0) + 1
    top_ss = sorted(ss_count, key=ss_count.get, reverse=True)
    matched = []
    checked = set()
    for i, a in enumerate(top_ss[:5]):
        for b in top_ss[i + 1:5]:
            k = frozenset([a, b])
            if k in SIPSUNG_COMBO_LIFE and k not in checked:
                matched.append((k, SIPSUNG_COMBO_LIFE[k]))
                checked.add(k)
    strength_info = get_ilgan_strength(ilgan, pils)
    sn = strength_info["신강신약"]
    return {
        "조합_결과": matched[:2],
        "전체_십성": ss_count,
        "주요_십성": top_ss[:4],
        "신강신약": sn,
        "일간": ilgan,
    }


def build_rich_narrative(pils, birth_year, gender, name, section="report"):
    """각 메뉴별 5000~10000자 서술형 내러티브 생성"""

    try:
        ilgan = pils[1]["cg"]

        ilgan_idx = CG.index(ilgan) if ilgan in CG else 0

        ilgan_kr = CG_KR[ilgan_idx]

        iljj = pils[1]["jj"]

        iljj_idx = JJ.index(iljj) if iljj in JJ else 0

        iljj_kr = JJ_KR[iljj_idx]

        current_year = datetime.now().year

        current_age = current_year - birth_year + 1

        display_name = name if name else "내담자"

        strength_info = get_ilgan_strength(ilgan, pils)

        sn = strength_info.get("신강신약", "중화(中和)")

        gyeokguk = get_gyeokguk(pils)

        gname = gyeokguk.get("격국명", "") if gyeokguk else ""

        ys = get_yongshin(pils)

        yongshin_ohs = ys.get("종합_용신", [])

        if not isinstance(yongshin_ohs, list):
            yongshin_ohs = []

        ilgan_oh = OH.get(ilgan, "")

        life = build_life_analysis(pils, gender)

        ss_dist = life.get("전체_십성", {})

        top_ss = [k for k, v in sorted(ss_dist.items(), key=lambda x: -x[1])][:3]

        combos = life.get("조합_결과", [])

        birth_month = st.session_state.get("birth_month", 1)

        birth_day = st.session_state.get("birth_day", 1)

        birth_hour = st.session_state.get("birth_hour", 12)

        birth_minute = st.session_state.get("birth_minute", 0)

        daewoon = SajuCoreEngine.get_daewoon(
            pils,
            birth_year,
            birth_month,
            birth_day,
            birth_hour,
            birth_minute,
            gender=gender,
        )

        cur_dw = next((d for d in daewoon if d["시작연도"] <= current_year <= d["종료연도"]), None)

        # 일간 한자 → '甲(갑)' 형식 변환 (ILGAN_CHAR_DESC 키 형식)

        _CG_KR_MAP = {
            "甲": "갑",
            "乙": "을",
            "丙": "병",
            "丁": "정",
            "戊": "무",
            "己": "기",
            "庚": "경",
            "辛": "신",
            "壬": "임",
            "癸": "계",
        }

        ilgan_char_key = f"{ilgan}({_CG_KR_MAP.get(ilgan, '')})" if ilgan in _CG_KR_MAP else ilgan

        char = ILGAN_CHAR_DESC.get(ilgan_char_key, ILGAN_CHAR_DESC.get(ilgan, {}))

        # 십성 한자 → 한글 변환

        _SS_KR_MAP = {
            "食神": "식신",
            "傷官": "상관",
            "偏財": "편재",
            "正財": "정재",
            "偏官": "편관",
            "正官": "정관",
            "偏印": "편인",
            "正印": "정인",
            "比肩": "비견",
            "劫財": "겁재",
        }

        cur_dw_ss_hanja = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw["cg"], "-") if cur_dw else "-"

        cur_dw_ss = _SS_KR_MAP.get(cur_dw_ss_hanja, cur_dw_ss_hanja)

        sn_narr = STRENGTH_NARRATIVE.get(sn, STRENGTH_NARRATIVE.get(sn.split("(")[0], ""))

        gnarr = GYEOKGUK_NARRATIVE.get(gname, f"{gname}은 독특한 개성과 능력을 가진 격국입니다.")

        sw_now = get_yearly_luck(pils, current_year)

        sw_next = get_yearly_luck(pils, current_year + 1)

        OH_KR_MAP = {
            "木": "목(木)",
            "火": "화(火)",
            "土": "토(土)",
            "金": "금(金)",
            "水": "수(水)",
        }

        yong_kr = " - ".join([OH_KR_MAP.get(o, o) for o in yongshin_ohs])

        # 로컬 엔진 강화: 오행·신살·공망·12운성·일주 데이터 (풍부한 서술용)
        oh_strength = calc_ohaeng_strength(ilgan, pils) or {}
        sinsal_list = get_12sinsal(pils) if pils else []
        gongmang = get_gongmang(pils) if pils else {}
        unsung_list = calc_12unsung(ilgan, pils) if pils else []
        ilju_key = (pils[1]["cg"] + pils[1]["jj"]) if len(pils) > 1 else ""
        ilju_desc = (GJ60.get(ilju_key, ("", ""))[1]) if ilju_key else ""
        pahae = get_pahae(pils) if pils else {"파살": [], "해살": [], "items": []}
        geunmyo = get_geunmyo_hwasil(pils) if pils else []

        # ctx 딕셔너리 조립 - 모든 섹션 함수 공통 전달
        ctx = {
            "pils": pils, "birth_year": birth_year, "gender": gender, "name": name,
            "display_name": display_name, "ilgan": ilgan, "ilgan_kr": ilgan_kr,
            "iljj": iljj, "iljj_kr": iljj_kr, "ilgan_oh": ilgan_oh,
            "current_year": current_year, "current_age": current_age,
            "sn": sn, "strength_info": strength_info, "sn_narr": sn_narr,
            "gname": gname, "gnarr": gnarr, "char": char,
            "yongshin_ohs": yongshin_ohs, "yong_kr": yong_kr,
            "top_ss": top_ss, "combos": combos, "ss_dist": ss_dist,
            "cur_dw": cur_dw, "cur_dw_ss": cur_dw_ss,
            "sw_now": sw_now, "sw_next": sw_next, "daewoon": daewoon,
            "oh_strength": oh_strength, "sinsal_list": sinsal_list,
            "gongmang": gongmang, "unsung_list": unsung_list,
            "ilju_desc": ilju_desc, "OH_KR_MAP": OH_KR_MAP, "section": section,
            "pahae": pahae, "geunmyo": geunmyo,
            "ilgan_profile": ILGAN_PROFILE.get(ilgan, {}),
        }

        if section == "report":
            return _nar_report(ctx)

        elif section in ("future", "lifeline"):
            return _nar_future(ctx)

        elif section == "money":
            return _nar_wealth(ctx)

        elif section == "relations":
            return _nar_health(ctx)

        elif section == "past":
            return _nar_past(ctx)

        return ""

    except Exception as e:
        return f"Error in narrative generation: {e}"


# tab_ai_chat_prophet: 제거됨 - tab_ai_chat 으로 통합

# --------------------------------------------------

#  UI Menu Functions

# --------------------------------------------------


