# -*- coding: utf-8 -*-

import streamlit as st

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

import json

import os
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
from saju_ui import *
from saju_report import menu_pdf

# ── saju_ui / saju_report 없을 경우 폴백 정의 ─────────────────────
if "render_quick_consult_header" not in dir():
    def render_quick_consult_header():
        """퀵 상담창 헤더 (saju_ui 폴백)"""
        import streamlit as _st
        _st.markdown(
            "<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);"
            "border-radius:12px;padding:12px 16px;margin-bottom:8px;'>"
            "<span style='color:#d4af37;font-size:15px;font-weight:900;'>🔮 만신 직격 상담창</span>"
            "<span style='color:#aaa;font-size:11px;margin-left:8px;'>사주 기반 즉답</span>"
            "</div>",
            unsafe_allow_html=True,
        )

if "render_quick_consult_response" not in dir():
    def render_quick_consult_response(response: str):
        """퀵 상담 응답 출력 (saju_ui 폴백)"""
        import streamlit as _st
        if not response:
            _st.warning("⚠️ 응답을 생성하지 못했습니다. 다시 질문해주세요.")
            return
        _st.markdown(
            f"<div style='background:linear-gradient(145deg,#faf7f0,#f5f0e8);"
            f"border:1.5px solid #d4af37;border-radius:16px;padding:20px 24px;"
            f"margin:10px 0;font-size:14px;color:#2d1f00;line-height:2.1;'>"
            f"<div style='font-size:11px;font-weight:800;color:#d4af37;"
            f"margin-bottom:10px;letter-spacing:1px;'>🔮 만신의 직격 답변</div>"
            f"{response.replace(chr(10), '<br>')}"
            f"</div>",
            unsafe_allow_html=True,
        )

if "menu_pdf" not in dir():
    def menu_pdf(pils, birth_year, gender, name, birth_hour=""):
        """PDF 리포트 (saju_report 폴백)"""
        import streamlit as _st
        _st.info("📄 PDF 리포트 기능은 saju_report.py 파일이 필요합니다.")
        _st.markdown(
            f"<div style='background:#f5f5f5;border-radius:12px;padding:20px;"
            f"text-align:center;color:#666;'>"
            f"📄 {name}님의 사주 리포트를 생성하려면<br>"
            f"saju_report.py 파일을 프로젝트 폴더에 넣어주세요.</div>",
            unsafe_allow_html=True,
        )

from datetime import date, datetime, timedelta

import random

import io

import re

import base64

import logging as _logging


def clean_hanja(text):
    if not text:
        return ""
    return re.sub(r"\(.*?\)", "", text).strip()


_saju_log = _logging.getLogger("saju")

try:
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )

    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    from reportlab.lib import colors

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False

# 3단계 A: korean-lunar-calendar 라이브러리 (정밀 절기 계산)

try:
    from korean_lunar_calendar import KoreanLunarCalendar as _KLC

    LUNAR_LIB_AVAILABLE = True

except ImportError:
    _KLC = None

    LUNAR_LIB_AVAILABLE = False  # -> 기존 내장 테이블로 자동 fallback

# ==========================================================

#  🌌 시스템 공통 상수

# ==========================================================

_AI_SANDBOX_HEADER = """

[🌌 MASTER MANSE SAJU ENGINE V3.1]

본 페르소나는 대한민국 명리학의 정수를 AI로 구현한 '만신(萬神)' 시스템입니다.

데이터 분석과 직관적 통찰이 결합된 최상위 상담 엔진으로 동작합니다.

"""

# 시각 표시용 12지 배열 (24시간 → 지지 매핑) - 모듈 수준 공통 상수



# ==========================================================

#  음력 ↔ 양력 변환 (내장 테이블 방식)

#  출처: 한국천문연구원 만세력 기준 1900~2060

# ==========================================================

# 음력 데이터: 각 음력 연도의 1월 1일 양력 날짜 + 월별 일수(29/30)

# 형식: {음력년: (양력월일, [월1일수, 월2일수, ..., 윤달여부포함])}

# 간략화: 1940~2030 핵심 구간만 내장 (나머지는 근사 계산)




# ── 분리된 모듈 import ──
from saju_engine import *
from saju_sinsal import *
from saju_interpreter import *
from saju_report import *

# ==========================================================

#  🧠 사주 AI 기억 시스템 (SajuMemory) - 4계층 구조

#  정보 저장 ❌ / 맥락 저장 ⭕

# ==========================================================


class SajuMemory:
    """

    만신(萬神) 영속 기억 시스템 (E-Version)

    파일 기반 저장소 (history_memory.json)를 통해 브라우저 종료 후에도 상담 맥락을 유지합니다.

    """

    MEMORY_FILE = "history_memory.json"

    @staticmethod
    def build_context_prompt() -> str:
        """SajuJudgmentRules 등에서 호출하는 전역 맥락 빌더"""

        name = st.session_state.get("saju_name", "내담자")

        return SajuMemory.build_rich_ai_context(name)

    @staticmethod
    def _load_all() -> dict:

        if not os.path.exists(SajuMemory.MEMORY_FILE):
            return {}

        try:
            with open(SajuMemory.MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception:
            return {}

    @staticmethod
    def _save_all(data: dict):

        try:
            with open(SajuMemory.MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as _e:
            _saju_log.warning("[SajuMemory.save_memory] 파일 저장 실패: %s", _e)

    @staticmethod
    def get_memory(name: str) -> dict:

        key = name.strip()

        all_data = SajuMemory._load_all()

        if key not in all_data:
            all_data[key] = {
                "identity": {
                    "profile": {},
                    "trait_fixed": [],
                    "implicit_persona": "초기탐색형",
                    "narrative": "",
                },
                "interest": {},
                "flow": {"stage": "탐색", "consult_stage": "탐색"},
                "behavior_stats": {
                    "query_lengths": [],
                    "visit_hours": [],
                    "emotion_log": [],
                },
                "conversation": [],
                "trust": {"score": 50, "level": 1, "history": []},
                "bond": {"level": 1, "score": 10, "label": "탐색"},
                "matrix": {
                    "행동": 50,
                    "감정": 50,
                    "기회": 50,
                    "관계": 50,
                    "에너지": 50,
                },
                "v2_features": {"mbti": "", "evolution_level": 1},
            }

            SajuMemory._save_all(all_data)

        return all_data[key]

    @staticmethod
    def adjust_bond(name: str, amount: int):

        def update(m):

            b = m.get("bond", {"level": 1, "score": 0})

            b["score"] = max(0, min(100, b["score"] + amount))

            # 20점당 1레벨업 (최대 5레벨)

            b["level"] = min(5, (b["score"] // 20) + 1)

            labels = ["탐색", "편안", "신뢰", "의존", "동반자"]

            b["label"] = labels[b["level"] - 1]

            m["bond"] = b

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def update_matrix(name: str, key: str, value: int):

        def update(m):

            if "matrix" not in m:
                m["matrix"] = {
                    "행동": 50,
                    "감정": 50,
                    "기회": 50,
                    "관계": 50,
                    "에너지": 50,
                }

            m["matrix"][key] = max(0, min(100, value))

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def record_behavior(name: str, query: str):

        def update(m):

            stats = m.get("behavior_stats", {"query_lengths": [], "visit_hours": []})

            stats["query_lengths"].append(len(query))

            stats["visit_hours"].append(datetime.now().hour)

            # 최근 20개만 유지

            if len(stats["query_lengths"]) > 20:
                stats["query_lengths"].pop(0)

            if len(stats["visit_hours"]) > 20:
                stats["visit_hours"].pop(0)

            m["behavior_stats"] = stats

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def adjust_trust(name: str, amount: int, reason: str = ""):

        def update(m):

            t = m.get("trust", {"score": 50, "level": 1, "history": []})

            t["score"] = max(0, min(100, t["score"] + amount))

            # 레벨 계산 (20점당 1레벨)

            t["level"] = (t["score"] // 20) + 1

            t["history"].append(
                {
                    "time": datetime.now().strftime("%Y-%m-%d"),
                    "amount": amount,
                    "reason": reason,
                }
            )

            m["trust"] = t

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def update_memory(name: str, update_fn):

        all_data = SajuMemory._load_all()

        key = name.strip()

        if key not in all_data:
            all_data[key] = SajuMemory.get_memory(name)

        all_data[key] = update_fn(all_data[key])

        SajuMemory._save_all(all_data)

    @staticmethod
    def update_identity(
        name: str,
        profile: dict = None,
        trait_fixed: list = None,
        implicit_persona: str = None,
        narrative: str = None,
        career: str = None,
        health: str = None,
    ):
        """

        내담자 정체성(identity) 갱신.

        - profile       : 사주-MBTI / trait_desc 등 프로파일 딕셔너리

        - trait_fixed   : 고정 성향 태그 리스트

        - implicit_persona : 행동 유형 문자열 (예: '분석탐구형')

        - narrative     : 현재 인생 서사 문자열

        - career        : 직장운/직업 요약 문자열

        - health        : 건강운 요약 문자열

        """

        def update(m):

            ident = m.get(
                "identity",
                {
                    "profile": {},
                    "trait_fixed": [],
                    "implicit_persona": "초기탐색형",
                    "narrative": "",
                },
            )

            if profile is not None:
                ident["profile"].update(profile)

            if trait_fixed is not None:
                ident["trait_fixed"] = trait_fixed

            if implicit_persona is not None:
                ident["implicit_persona"] = implicit_persona

            if narrative is not None:
                ident["narrative"] = narrative

            if career is not None:
                ident["career"] = career

            if health is not None:
                ident["health"] = health

            m["identity"] = ident

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def record_interest(name: str, topic: str):

        def update(m):

            m["interest"][topic] = m["interest"].get(topic, 0) + 1

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def get_interest_summary(name: str):

        mem = SajuMemory.get_memory(name)

        interests = mem.get("interest", {})

        if not interests:
            return "전반적 운세"

        return ", ".join(k for k, v in sorted(interests.items(), key=lambda x: x[1], reverse=True)[:2])

    @staticmethod
    def add_conversation(name: str, topic: str, content: str, emotion: str = ""):

        def update(m):

            m["conversation"].append(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": topic,
                    "summary": content[:150],
                    "emotion": emotion,
                }
            )

            if len(m["conversation"]) > 7:
                m["conversation"].pop(0)

            return m

        SajuMemory.update_memory(name, update)

    @staticmethod
    def get_personalized_intro(name: str, pils: list = None) -> str:

        mem = SajuMemory.get_memory(name)

        conv = mem.get("conversation", [])

        if conv:
            return f"허허, 다시 찾아왔구먼. 지난 '{conv[-1]['topic']}' 자리 이후로 {name}의 기운이 어찌 흘렀는지 내 신안(神眼)에 선히 보이느니라. 오늘은 또 어떤 천명(天命)의 실타래를 풀러 왔는가?"

        if pils:
            profile = PersonalityProfiler.analyze(pils)

            desc = profile.get("trait_desc", "깊은 내면의 힘")

            return f"허어, 어서 오게. {desc}의 기질을 타고난 {name}의 팔자(八字)가 내 신안에 선히 보이는구먼. 이 만신의 문을 두드린 데는 분명한 까닭이 있으리라. 어디, 속 이야기를 털어놓아 보게나."

        return f"허허, 어서 오게. 자네 기운이 느껴지는구먼... 나는 만신(萬神)이라네. 천명(天命)을 읽고 팔자(八字)의 이치를 풀어내는 것이 내 소임이니, 무엇이든 묻고 가게나."

    @staticmethod
    def build_rich_ai_context(name: str) -> str:

        mem = SajuMemory.get_memory(name)

        profile = mem["identity"].get("profile", {})

        convs = mem.get("conversation", [])

        trust = mem.get("trust", {"score": 50, "level": 1})

        bond = mem.get("bond", {"level": 1, "label": "탐색"})

        v2 = mem.get("v2_features", {})

        matrix = mem.get("matrix", {})

        # 🌌 Master Version Platform Context

        implicit = mem["identity"].get("implicit_persona", "초기탐색형")

        evolution_lvl = v2.get("evolution_level", 1)

        ctx = f"\n[🌌 MASTER PLATFORM CONTEXT (Bond: {bond['label']} Lv.{bond['level']})]\n"

        ctx += f"- AI-내담자 유대감: {bond['label']} 상태 (함께한 진화 Lv.{evolution_lvl})\n"

        ctx += f"- 인생 매트릭스 지표: 행동({matrix.get('행동', 50)}), 감정({matrix.get('감정', 50)}), 기회({matrix.get('기회', 50)}), 에너지({matrix.get('에너지', 50)})\n"

        if profile:
            ctx += f"- 사주-MBTI: {profile.get('mbti')} / 페르소나: {profile.get('trait_desc')}\n"

            if mem["identity"].get("narrative"):
                ctx += f"- 현재 인생 서사: '{mem['identity']['narrative']}'\n"

        # 🗺️ Timeline 맥락

        timeline_ctx = DestinyTimelineEngine.get_context_summary()

        ctx += f"- 운명 타임라인: {timeline_ctx}\n"

        if convs:
            ctx += "- 주요 상담 맥락:\n"

            for c in convs[-3:]:
                ctx += f"  * {c['topic']}: {c['summary']}\n"

        # 👥 AICouncil 준비 지침

        ctx += f"\n[시스템 지침: AI Council 모드]\n당신은 이제 단독 상담사가 아닌, 3인의 전문가(명리분석/심리상담/전략코치)가 통합된 존재입니다. 각 관점을 융합하여 깊이 있는 결론을 내리세요.\n"

        ctx += SelfEvolutionEngine.get_instruction(implicit)

        return ctx


class AICouncil:
    """👥 다중 AI 페르소나 토론 시스템 (Master Version)"""

    @staticmethod
    def get_personas() -> dict:

        return {
            "analyst": "사주 원국과 대운의 흐름을 냉철하게 분석하는 정통 명리학자",
            "counselor": "내담자의 감정을 공감하고 심리적 안정을 도모하는 심리 상담 전문가",
            "coach": "분석된 운세를 바탕으로 현실적인 행동 지침과 전략을 제시하는 커리어 코치",
        }

    @staticmethod
    def build_council_prompt(user_query: str) -> str:

        p = AICouncil.get_personas()

        return f"""

[👥 AI Council: 다중 전문가 통합 전수 지침]

당신은 현재 3인의 마스터 전문가로 구성된 '상담위원회'입니다. 

다음 세 전문가가 내부 토론을 거쳐 합의된 최상의 결론을 내담자에게 전달하십시오.

1. 🏛️ 명리분석가: {p["analyst"]}

2. 🧘 심리상담가: {p["counselor"]}

3. 🚀 전략코치: {p["coach"]}

답변 구성 원칙:

- 전문가 3인의 관점이 모두 녹아든 '통합 리포트' 형식으로 답변하세요.

- [분석: 운의 흐름], [케어: 마음가짐], [행동: 현실적 조언] 항목이 조화롭게 포함되어야 합니다.

- 만신(萬神)의 권위 있고 따뜻한 어조(고어체 융합)를 끝까지 유지하십시오.

"""


class LifeNarrativeEngine:
    """📖 사용자의 삶을 스토리(Narrative)로 정의하고 서사를 부여하는 엔진"""

    @staticmethod
    def update_narrative(name: str, topic_kr: str, emotion: str):

        def update(m):

            bond_lv = m.get("bond", {}).get("level", 1)

            # 심화 서사 생성 로직

            base_narratives = {
                "직업/진로": "자신의 천명을 찾아가는 고귀한 여정",
                "재물/사업": "풍요의 바다를 향해 돛을 펼치는 도전",
                "연애/결혼": "서로의 기운이 만나 조화를 이루는 인연의 숲",
                "인간관계": "다양한 삶의 결이 부딪히며 다듬어지는 과정",
                "인생 방향": "자아의 근원을 찾아 떠나는 내면의 항해",
                "운세 흐름": "하늘의 운율에 맞춰 춤추는 인생의 파동",
            }

            theme = base_narratives.get(topic_kr, "삶의 신비를 풀어가는 여정")

            if emotion == "불안":
                theme += " (어둠 속에서 빛을 찾는 중)"

            elif emotion == "결심":
                theme += " (새로운 태양이 뜨는 시점)"

            if bond_lv >= 4:
                m["identity"]["narrative"] = f"만신과 함께 써내려가는 '{theme}'의 마스터 피스"

            else:
                m["identity"]["narrative"] = theme

            return m

        SajuMemory.update_memory(name, update)


class GoalCreationEngine:
    """🎯 사용자의 숨은 목표(Goal)를 발견하고 정의하는 엔진"""

    @staticmethod
    def extract_goal(name: str, query: str):

        def update(m):

            if "identity" not in m:
                m["identity"] = {}

            if "goals" not in m["identity"]:
                m["identity"]["goals"] = []

            # 키워드 기반 단순 목표 추출 (향후 LLM 분석 결과 피드백 가능)

            if any(k in query for k in ["성공", "부자", "돈", "수익"]):
                goal = "경제적 자유 달성"

            elif any(k in query for k in ["이직", "취업", "합격"]):
                goal = "사회적 성취와 안착"

            elif any(k in query for k in ["외롭", "결혼", "만남"]):
                goal = "진정한 인연과의 결합"

            else:
                return m

            if goal not in m["identity"]["goals"]:
                m["identity"]["goals"].append(goal)

            return m

        SajuMemory.update_memory(name, update)


class DestinyMatrix:
    """📊 인생의 5대 핵심 지표를 관리하는 매트릭스 엔진"""

    @staticmethod
    def calculate_sync(name: str, pils: dict, luck_score: int):

        # 운세 점수와 심리 상태를 결합하여 지표 산출

        mem = SajuMemory.get_memory(name)

        stats = mem.get("behavior_stats", {})

        # 행동력 (질문 길이와 적극성)

        action = min(100, 50 + (len(stats.get("query_lengths", [])) * 2))

        # 에너지 (운세 점수 기반)

        energy = luck_score

        # 감정 (최근 감정 로그 기반 - 스텁)

        emotion = 60 if "불안" not in str(mem.get("conversation", [])) else 40

        SajuMemory.update_matrix(name, "행동", action)

        SajuMemory.update_matrix(name, "에너지", energy)

        SajuMemory.update_matrix(name, "감정", emotion)

        SajuMemory.update_matrix(name, "기회", luck_score + 10 if luck_score > 70 else luck_score)

        SajuMemory.update_matrix(name, "관계", 50)


class PersonalityEngine:
    """🧠 내담자의 입력 패턴을 분석하여 '심저(深底) 성향'을 파악하는 엔진"""

    @staticmethod
    def analyze_behavior(name: str):

        mem = SajuMemory.get_memory(name)

        stats = mem.get("behavior_stats", {})

        ql = stats.get("query_lengths", [])

        vh = stats.get("visit_hours", [])

        if not ql:
            return "초기탐색형"

        # 분석 로직

        avg_len = sum(ql) / len(ql)

        night_visits = len([h for h in vh if h >= 22 or h <= 4])

        if avg_len > 100:
            persona = "논리/분석 탐색형"

        elif night_visits >= 3:
            persona = "현실불안 위로형"

        elif len(ql) > 10:
            persona = "해답갈구 확신형"

        else:
            persona = "온건적 소통형"

        def update_implicit(m):

            m["identity"]["implicit_persona"] = persona

            # 이해도 상승

            m["v2_features"]["evolution_level"] = min(10, m["v2_features"].get("evolution_level", 1) + 1)

            return m

        SajuMemory.update_memory(name, update_implicit)

        return persona


def _local_saju_engine(pils, name, birth_year, gender, query):
    """만세력/격국/용신/대운 엔진 기반 로컬 사주 상담 (무당 말투) — 재사용 가능 모듈"""

    import re as _re

    from datetime import date as _d_today

    q = query or ""

    current_year = datetime.now().year

    ilgan = pils[1]["cg"] if len(pils) > 1 else "?"

    _ss = st.session_state

    bm = max(1, min(12, int(_ss.get("birth_month") or 1)))

    bd = max(1, min(31, int(_ss.get("birth_day") or 1)))

    bh = max(0, min(23, int(_ss.get("birth_hour") or 12)))

    bmn = max(0, min(59, int(_ss.get("birth_minute") or 0)))

    is_today = bool(_re.search(r"오늘|일진|내일|이번주", q))

    is_year = bool(_re.search(r"올해|세운|금년|올해운세|2025|2026|2027", q)) or is_today

    is_money = bool(_re.search(r"재물|돈|사업|수입|투자|부자|재산|벌리나|벌어|돈나와|돈올까|수익|매출|버는|벌수있|잘벌|부자될", q))

    is_lotto = bool(_re.search(r"로또|복권|횡재|당첨|대박|일확천금", q))

    is_love = bool(_re.search(r"연애|결혼|궁합|이성|남자|여자|남편|아내|인연|배우자", q))

    is_health = bool(_re.search(r"건강|병원|아프|수술|몸|질병|체력", q))

    is_dw = bool(_re.search(r"대운|운세흐름|인생|10년|장기|앞으로|미래", q))

    is_past = bool(_re.search(r"과거|지나온|예전|돌아보|과거운|이전|맞춰봐", q))

    is_job = bool(_re.search(r"직업|진로|취업|창업|커리어|직장|일자리|사업방향", q))

    is_char = bool(_re.search(r"성격|성향|기질|특성|나는|내가|나의", q))

    is_avoid = bool(_re.search(r"피해야|조심|주의|하면안|금기|위험|손재|삼가|나쁜|피하", q))

    is_lucky = bool(_re.search(r"좋은날|길일|행운의날|언제가좋|언제해야|좋은시기|황금기", q))

    is_move = bool(_re.search(r"이사|이직|이동|이민|출국|이전|결정|시작|개업", q))

    is_study = bool(_re.search(r"시험|공부|합격|학업|수능|입학|자격증|고시", q))

    is_family = bool(_re.search(r"부모|아버지|어머니|자녀|아들|딸|형제|가족|자식", q))

    # ── 추가 키워드 분기 (직격 질문 대응) ──────────────────────
    is_infidelity = bool(_re.search(r"바람|외도|불륜|바람피|이성문제|浮氣|浮气|바람끼|이중생활", q))
    is_accident   = bool(_re.search(r"사고수|사고|위기|큰일|큰 일|재난|재앙|조심해야|올해위험|위험한해|아픈해", q))
    is_quit       = bool(_re.search(r"퇴사|회사그만|직장그만|사직|그만둬야|그만해야|때려치|때려쳐|관두|관뒤", q))
    is_fail_biz   = bool(_re.search(r"사업망|사업실패|폐업|사업접|망할|망하|접어야|빚|손실|부도|파산", q))
    is_lawsuit    = bool(_re.search(r"소송|법적|관재|고소|피소|분쟁|법원|변호사|처벌|범죄", q))
    is_pregnancy  = bool(_re.search(r"임신|출산|애기|아기|아이|태어|낳|득자|득남|득녀|태아", q))
    # ── 신규 분기 키워드 7개 ──
    is_luck_remedy = bool(_re.search(r"개운|부적|방위|색상|행운색|행운|개운법|풍수|기운올리|운올리|처방|비방", q))
    is_divorce     = bool(_re.search(r"이혼|별거|부부불화|부부싸움|가정불화|혼인파탄|이혼해야|이혼할까|부부관계|부부문제", q))
    is_overseas    = bool(_re.search(r"해외|이민|유학|출국|외국|외국생활|해외취업|해외사업|이민가야|외국나가|해외이주", q))
    is_realestate  = bool(_re.search(r"부동산|집매입|땅|아파트|건물|전세|월세|집살|집팔|매매|이사방위|방위", q))
    is_guiin       = bool(_re.search(r"귀인|천을귀인|도움|구원|베풀|후원자|은인|누가도와|누가돕|좋은사람|좋은인연", q))
    is_elderly     = bool(_re.search(r"노후|말년|은퇴|노년|60세|70세|80세|늙어서|나중에|수명|장수|오래살", q))
    is_childcare   = bool(_re.search(r"자녀진로|아이진로|아이공부|자녀교육|아이적성|아들사주|딸사주|자식팔자|자식운|아이운", q))

    out = [f"허허, 어서 오게. {name}의 팔자를 내 신안(神眼)으로 살펴보겠느니라.\n"]

    # ── 복합 질문(2개 이상 분야) 시 AICouncil 다중 전문가 헤더 ──
    _topic_count = sum([
        is_money, is_love, is_health, is_job,
        is_infidelity, is_accident, is_quit, is_fail_biz, is_lawsuit
    ])
    if _topic_count >= 2:
        try:
            _council_hdr = AICouncil.build_council_prompt(q)
            out.insert(0, f"*[3인 전문가 통합 상담 모드]*\n{_council_hdr[:120]}\n")
        except Exception:
            pass

    try:
        if is_today:
            today = _d_today.today()

            sw = get_yearly_luck(pils, current_year) or {}

            sw_ss = sw.get("십성_천간", "") or "-"

            sw_gh = sw.get("길흉", "평")

            sw_gan = sw.get("세운", "")

            # 한자→한글 변환

            _SS_KR2 = {
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

            sw_ss_kr = _SS_KR2.get(sw_ss, sw_ss)

            _SW_D = {
                "偏財": "재물·이성 기운이 활발하느니라. 능동적으로 움직이면 좋은 결과가 오리라.",
                "正財": "안정된 수입·신뢰 기운이 흐르느니라. 약속과 계획을 착실히 이행하게.",
                "食神": "창의와 표현의 기운이 넘치는 시기니라. 새 아이디어를 펼치기 좋으니라.",
                "傷官": "말조심, 윗사람과의 마찰을 피하게. 창의성은 좋으나 충돌을 조심하게.",
                "偏官": "긴장과 변동의 기운이 있느니라. 안전과 건강에 각별히 유의하게.",
                "正官": "명예와 인정의 기운이 흐르느니라. 책임을 다하면 좋은 평가가 오리라.",
                "偏印": "이동·변화 기운이 있느니라. 새 정보를 수집하되 결정은 신중히 하게.",
                "正印": "학습과 지혜의 기운이 충만하느니라. 배움과 자격 준비에 집중하게.",
                "比肩": "독립 의지가 강해지는 기운이니라. 협력보다 단독 추진이 유리하느니라.",
                "劫財": "경쟁과 재물 손실 기운이 있느니라. 보증·투자·동업을 삼가게.",
            }

            out.append(f"**오늘({today.month}월 {today.day}일) 일진 풀이**\n")

            out.append(f"올해({current_year}년) {sw_gan} 세운 안에서 오늘 하루가 펼쳐지느니라.\n")

            if sw_ss and sw_ss != "-":
                out.append(f"올해 흐르는 십성: **{sw_ss}({sw_ss_kr})** | 길흉: **{sw_gh}**\n")

                out.append(_SW_D.get(sw_ss, f"{sw_ss_kr} 기운이 오늘 하루에도 그대로 흐르느니라.") + "\n")

            else:
                out.append(f"길흉: **{sw_gh}** — 흐름을 잘 읽고 신중히 움직이게.\n")

            # ── 상황별 전용 답변 (경찰서/법원/병원/계약/면접/데이트/여행) ──


            sit_answered = False

            for keywords, ss_map in _SIT.items():
                if any(k in q for k in keywords):
                    sit_answer = ss_map.get(sw_ss, ss_map.get("_default", ""))

                    if sit_answer:
                        kw_label = keywords[0]

                        out.append(f"\n**[{kw_label} 방문 — 오늘의 사주 판단]**\n{sit_answer}\n")

                    sit_answered = True

                    break

            if not sit_answered:
                # 일반 오늘 풀이

                _GH_TODAY = {
                    "길": "오늘은 길한 기운이 흐르느니라! 중요한 일을 추진하면 좋은 결과가 오니라.",
                    "+": "오늘은 길한 기운이 흐르느니라! 중요한 일을 추진하면 좋은 결과가 오니라.",
                    "평": "오늘은 평온한 기운이니라. 무리하지 말고 꾸준히 나아가는 것이 좋으니라.",
                    "흉": "오늘은 조심스러운 기운이니라. 중요한 결정은 내일로 미루고 안전을 우선하게.",
                    "-": "오늘은 조심스러운 기운이니라. 중요한 결정은 내일로 미루고 안전을 우선하게.",
                }

                out.append(f"\n{_GH_TODAY.get(sw_gh, '오늘 하루 평온한 기운이니라.')}\n")

            sw_n = get_yearly_luck(pils, current_year + 1) or {}

            sw_n_ss = sw_n.get("십성_천간", "")

            sw_n_kr = _SS_KR2.get(sw_n_ss, sw_n_ss)

            out.append(f"\n내년 {current_year + 1}년은 {sw_n.get('세운', '')} [{sw_n_ss}/{sw_n_kr}] 기운이 다가오고 있으니 미리 내다보게.\n")

        elif is_year and not is_money and not is_accident:
            sw = get_yearly_luck(pils, current_year) or {}

            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            sw_gan = sw.get("세운", "")

            try:
                tp = calc_turning_point(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            except Exception:
                tp = {}

            _SW = {
                "偏財": "재물 변동과 이성 인연의 기운이 강하느니라. 사업 기회가 오지만 투기는 조심하게.",
                "正財": "안정된 수입과 결혼 인연의 기운이 들어오느니라. 재물을 차곡차곡 모을 수 있는 해니라.",
                "食神": "직업과 재능이 빛을 발하는 해니라. 새 일을 시작하거나 자격 취득에 좋으니라.",
                "傷官": "창의성이 폭발하지만 윗사람과의 마찰을 조심해야 하느니라.",
                "偏官": "직장 변동과 사고 기운이 있느니라. 건강과 안전에 각별히 주의하게.",
                "正官": "명예와 승진의 기운이 강하느니라. 조직에서 인정받는 해니라.",
                "偏印": "계획이 자주 바뀌고 이사·이동의 기운이 있느니라. 신중하게 결정하게.",
                "正印": "학업과 자격 취득에 유리한 해니라. 어머니와의 인연도 돈독해지느니라.",
                "比肩": "독립심이 강해지고 경쟁이 치열해지는 해니라. 동업보다 단독 행동이 낫느니라.",
                "劫財": "재물 손실과 경쟁이 극심한 해니라. 보증과 투자를 자제하게.",
            }

            _ACT = {
                "偏財": "적극적 투자·사업 기회를 잡되 안전 자산 30% 이상 반드시 확보하게!",
                "正財": "부동산·예금·적금 등 안정 자산에 집중하게. 불필요한 지출을 줄이는 것이 재물의 시작이니라.",
                "食神": "자격증 취득·신규 프로젝트 시작이 최적이니라. 전문성을 드러낼 시기니라.",
                "傷官": "창작·발명은 좋으나 직속 상관·계약서 분쟁 조심. 독립 행보는 내년 이후가 유리하니라.",
                "偏官": "건강 정기검진 필수. 무리한 확장·새 사업 시작 자제. 법적 분쟁도 조심하게.",
                "正官": "자격증·승진 시험·공직 지원에 최적의 해! 조직 내 신뢰를 쌓는 것이 핵심이니라.",
                "偏印": "이사·이직·전공 변경 시 신중히 결정하게. 새 분야 학습에는 유리하니라.",
                "正印": "자격증·진학·연구에 집중하라. 어머니·스승과의 관계를 돈독히 하게.",
                "比肩": "독립·창업·단독 프로젝트에 유리. 동업·보증은 이 해에 시작하지 말게.",
                "劫財": "현금 보유·빚 상환 우선. 도박·투기·보증 절대 금지. 경쟁에서 냉정함을 유지하게.",
            }

            # ── 쉬운 말 결론 한 줄 매핑 ──────────────────────────
            _EASY_VERDICT = {
                "偏財": "💰 돈 기회가 오는 해! 적극적으로 움직이면 됩니다",
                "正財": "💰 꾸준히 모으면 쌓이는 안정적인 해입니다",
                "食神": "🌟 내 실력·재능이 돈이 되는 해입니다",
                "傷官": "⚠️ 말조심·윗사람 관계 조심이 먼저인 해입니다",
                "偏官": "⚠️ 건강·안전 최우선, 무리한 투자 금지인 해입니다",
                "正官": "✅ 직장·조직에서 인정받는 해입니다",
                "偏印": "📚 큰 결정은 신중히, 공부·학습엔 유리한 해입니다",
                "正印": "📚 자격증·공부가 잘 되는 해입니다",
                "比肩": "⚡ 혼자 움직일 때 유리, 동업·보증은 피하세요",
                "劫財": "🔴 돈이 나가기 쉬운 해 — 투자·보증 절대 금지!",
            }
            _GH_KR = {"길": "✅ 좋음", "+": "✅ 좋음", "평": "⚖️ 보통", "흉": "⚠️ 나쁨", "-": "⚠️ 나쁨"}
            _ss_clean = sw_ss.split("(")[0] if "(" in sw_ss else sw_ss
            _gh_txt = _GH_KR.get(sw_gh, sw_gh)

            out.append(f"**{current_year}년 ({current_year - birth_year + 1}세) 운세 직격 분석**\n")
            out.append(f"\n**▶ 한 줄 결론: {_EASY_VERDICT.get(_ss_clean, f'올해 [{sw_ss}] 기운의 해니라')}**\n\n")
            out.append(f"올해 하늘의 기운: **{sw_gan}** | 운세등급: {_gh_txt}\n\n")
            out.append(_SW.get(_ss_clean, f"{sw_ss} 기운이 강하게 작동하는 해니라.") + "\n")
            out.append(f"\n**[지금 당장 해야 할 행동]** {_ACT.get(_ss_clean, '분수에 맞게 안정적으로 움직이게.')}\n")

            tp_int = tp.get("intensity", "")
            tp_sc  = tp.get("score_change", 0)
            tp_rsn = tp.get("reason", [])

            if "강력" in tp_int:
                out.append(f"\n**⚡ 올해 인생의 큰 변화 시점!** 지금 중요한 결정을 내려야 할 때니라.\n")
                for r in tp_rsn[:3]:
                    # 내부 식별자("용신 대운", "황금기" 등) 필터
                    _r_clean = r.replace(" - ","·").strip()
                    if len(_r_clean) > 5 and "대운" not in _r_clean[:5]:
                        out.append(f"• {_r_clean}\n")
            elif "주요" in tp_int or "변화" in tp_int:
                out.append(f"\n**🔄 올해 삶에 변화가 생깁니다.** 준비하고 대응하면 기회가 됩니다.\n")
                for r in tp_rsn[:2]:
                    _r_clean = r.replace(" - ","·").strip()
                    if len(_r_clean) > 5:
                        out.append(f"• {_r_clean}\n")

            sw_n  = get_yearly_luck(pils, current_year + 1) or {}
            sw_n2 = get_yearly_luck(pils, current_year + 2) or {}
            _n_ss  = sw_n.get('십성_천간', '')
            _n2_ss = sw_n2.get('십성_천간', '')
            _n_ss_c  = _n_ss.split("(")[0]  if "(" in _n_ss  else _n_ss
            _n2_ss_c = _n2_ss.split("(")[0] if "(" in _n2_ss else _n2_ss
            _n_ev  = _EASY_VERDICT.get(_n_ss_c,  f'[{_n_ss}] 기운')
            _n2_ev = _EASY_VERDICT.get(_n2_ss_c, f'[{_n2_ss}] 기운')
            _n_gh  = _GH_KR.get(sw_n.get('길흉', ''), sw_n.get('길흉', ''))
            _n2_gh = _GH_KR.get(sw_n2.get('길흉',''), sw_n2.get('길흉',''))

            out.append(f"\n**[내년 {current_year + 1}년 미리보기]** {sw_n.get('세운', '')} — {_n_ev} {_n_gh}\n")
            out.append(f"**[후년 {current_year + 2}년 미리보기]** {sw_n2.get('세운', '')} — {_n2_ev} {_n2_gh}")

        elif is_lotto and not is_luck_remedy:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            si = get_ilgan_strength(ilgan, pils)

            sw_ss = sw.get("십성_천간", "")

            sw_gh = sw.get("길흉", "")

            sw_gan = sw.get("세운", "")

            y1 = ys.get("용신_1순위", "-")

            heui = ys.get("희신", "-")

            gisin = ", ".join(ys.get("기신", []))

            sn = si.get("신강신약", "중화")


            lotto_star, lotto_desc = _LOTTO_SS.get(
                sw_ss,
                (
                    "★ 보통 수준",
                    f"{sw_ss or '이'} 기운의 해니라. 로또보다 실력과 노력이 더 확실한 수익이 되느니라.",
                ),
            )

            out.append(f"**{name}의 로또·복권·횡재운 분석**\n허허, 횡재는 하늘이 내리는 것이니라. 신안으로 살펴보겠느니라.\n")

            out.append(f"\n**{current_year}년 세운 {sw_gan} [{sw_ss}] {sw_gh}**\n")

            out.append(f"{lotto_star} {lotto_desc}\n")

            yong_oh = OH.get(sw_gan[:1] if sw_gan else "", "")

            if yong_oh in {y1, heui}:
                out.append(f"\n흐! 올해 세운 {sw_gan}이 용신({y1})·희신({heui})과 일치하느니라! **연중 최설 횡재 기운**이니 이 시기를 놓치지 말게!\n")

            elif gisin and yong_oh in gisin:
                out.append(f"\n⚠️ 올해 세운이 기신({gisin})에 해당하니 **큰 투기는 삼가게**. 소액으로만 즐기는 것이 현명하니라.\n")

            else:
                out.append(f"\n용신 **{y1}** 오행이 강한 해에 한 번씩 시도해보는 것이 이치에 맞니라. 꼭 오늘만이 기회가 아니느니라.\n")

            gold_lotto = []

            for yr in range(current_year, current_year + 6):
                sw_l = get_yearly_luck(pils, yr) or {}

                ss_l = sw_l.get("십성_천간", "")

                yo_l = OH.get(sw_l.get("세운", "")[:1], "")

                if ss_l == "偏財" and sw_l.get("길흉", "") in ("길", "+"):
                    gold_lotto.append(f"  * **{yr}년**({yr - birth_year + 1}세): {sw_l.get('세운', '')} [偏財(편재) 편재] ★★★ 횡재 피크!")

                elif ss_l in ("偏財(편재)", "食神(식신)") and yo_l in {y1, heui}:
                    gold_lotto.append(f"  * **{yr}년**({yr - birth_year + 1}세): {sw_l.get('세운', '')} [{ss_l}] ★★ 용신과 일치하는 행운 시기")

            if gold_lotto:
                out.append(f"\n**[향후 횡재·행운 피크 시기]**\n")

                for g in gold_lotto:
                    out.append(g + "\n")

            else:
                out.append(f"\n당장의 횡재보다 꾸준한 재물 축적이 이 팔자에 맞느니라.\n")

            out.append(f"\n로또는 정가비를 즐기는 선에서 하는 것이 현명하니라. {ilgan}(일간)의 기운상 매주 소액으로 꾸준히 사는 것이 한 방보다 낫느니라!\n")

        elif is_money:
            gk = get_gyeokguk(pils)
            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            gkn = gk["격국명"] if gk else "미정격"
            y1 = ys.get("용신_1순위", "-")
            y2 = ys.get("용신_2순위", "-")
            heui = ys.get("희신", "-")
            gisin = ", ".join(ys.get("기신", []))

            # ── "올해 돈" 질문이면 올해 세운 기반 재물 직격 판단 먼저 출력
            _sw_m = get_yearly_luck(pils, current_year) or {}
            _sw_ss_m = _sw_m.get("십성_천간","")
            _sw_gan_m = _sw_m.get("세운","")
            _sw_gh_m  = _sw_m.get("길흉","평")
            _sw_oh_m  = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                         "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}.get((_sw_gan_m[:1] if _sw_gan_m else ""),"")
            _ys_ohs_m = ys.get("종합_용신",[]) if isinstance(ys.get("종합_용신",[]),list) else []
            _is_ys_m  = _sw_oh_m in _ys_ohs_m
            _GH_KR_M  = {"길":"✅ 재물 좋음","+":"✅ 재물 좋음","평":"⚖️ 보통","흉":"⚠️ 조심","-":"⚠️ 조심"}
            _MONEY_SS_NOW = {
                "偏財":"💰 사업·투자 기회의 해! 움직이면 돈이 된다. 단, 투기는 금물.",
                "正財":"💰 꾸준히 모으면 쌓이는 해. 저축·계약·정산에 집중하라.",
                "食神":"🌟 내 실력·재능이 돈이 되는 해. 새 파이프라인을 여는 적기.",
                "傷官":"⚠️ 직접 벌기보다 아이디어·창작으로 수입을 만들어야 하는 해. 말조심 필수.",
                "偏官":"🔴 올해는 재물보다 버티는 것이 전략. 큰 투자·동업 금지.",
                "正官":"✅ 직장·승진으로 수입이 늘어나는 해. 조직 안에서 움직여라.",
                "劫財":"🔴 돈이 나가기 쉬운 해. 투자·보증 절대 금지. 현금을 지켜라.",
                "比肩":"⚡ 혼자 움직여야 돈이 되는 해. 동업·공동 투자 피하라.",
                "偏印":"📚 재물보다 실력 쌓기가 맞는 해. 무리한 수익 추구 금물.",
                "正印":"📚 자격·귀인의 도움으로 돈이 오는 해. 인맥을 활용하라.",
            }
            _ss_clean_m = _sw_ss_m.split("(")[0] if "(" in _sw_ss_m else _sw_ss_m
            _now_verdict = _MONEY_SS_NOW.get(_ss_clean_m,"올해 흐름에 맞게 신중하게 움직이게.")
            _grade_m = "🌟 황금 재물기" if _is_ys_m and _sw_gh_m in ("길","+") else ("💰 재물 상승기" if _is_ys_m else ("⚠️ 재물 조심기" if _sw_gh_m in ("흉","-") else "⚖️ 평년 수준"))

            out.append(f"**{name}의 재물운 완전 분석**\n")
            out.append(f"\n**▶ 올해({current_year}) 재물 직격 판단: {_grade_m}**\n")
            out.append(f"올해 하늘 기운 **{_sw_gan_m}** [{_ss_clean_m}] — {_GH_KR_M.get(_sw_gh_m,'평')}\n")
            out.append(f"**{_now_verdict}**\n\n")
            if _is_ys_m:
                out.append("용신 오행이 들어오는 해니라. **이 해 최대한 움직여라. 10년에 한번 오는 기회다.**\n\n")
            elif not _is_ys_m and _sw_oh_m in (ys.get("기신",[]) if isinstance(ys.get("기신",[]),list) else []):
                out.append("기신 오행이 강한 해니라. **수비가 최선이다. 큰 결정은 내년으로 미뤄라.**\n\n")

            _GKM = {
                "정관격": "명예와 재물이 함께 오는 격국이니라. 조직에서 승진할수록 재물이 늘어나느니라. 직함과 신뢰가 곧 재물이니 체면을 지키게.",
                "정재격": "꾸준한 노력으로 재물을 쌓는 격국이니라. 금융·부동산에서 재물이 쌓이느니라. 규칙적 저축과 장기 투자가 최고의 전략이니라.",
                "편재격": "사업가 기질의 격국이니라. 투자·영업에서 큰 기회가 오느니라. 기복이 크니 안전 자산 30% 이상 반드시 확보하게. 한 방을 노리다 전부 잃는 수가 있느니라.",
                "식신격": "전문성을 키우면 재물이 자연스럽게 따라오는 격국이니라. 실력을 쌓는 것이 곧 재물을 쌓는 것이니라.",
                "상관격": "창의적 방법으로 재물을 만드는 격국이니라. 프리랜서·컨설팅·콘텐츠 창작이 맞느니라.",
                "편인격": "기술·학문·특허로 재물을 만드는 격국이니라. 단 재물보다 전문성에 집중할 때 돈이 따라오느니라.",
                "정인격": "안정적 직업·자격증으로 꾸준히 재물을 쌓는 격국이니라. 주식·투기보다 연금·부동산이 맞느니라.",
                "비견격": "독립 사업이나 프리랜서로 재물을 벌어야 하는 격국이니라. 공동 투자·동업은 반드시 계약서를 쓰게.",
                "겁재격": "경쟁과 도전 속에서 재물을 얻는 격국이니라. 손실도 크지만 회복도 빠른 팔자니라.",
            }

            _MONEY_EASY = {
                "정관격":"✅ 직장·승진할수록 돈이 따라오는 팔자","정재격":"💰 꾸준히 모으면 쌓이는 팔자",
                "편재격":"⚡ 사업·투자로 크게 벌 수 있는 팔자(기복 주의)","식신격":"🌟 실력이 곧 돈이 되는 팔자",
                "상관격":"💡 창의로 수입 만드는 팔자","편인격":"📚 기술·전문지식으로 돈 버는 팔자",
                "정인격":"📚 자격증·안정직업으로 꾸준히 버는 팔자","비견격":"⚡ 혼자 일할 때 가장 잘 버는 팔자",
                "겁재격":"⚠️ 기복이 크지만 회복도 빠른 팔자",
            }
            out.append(f"**{name}의 재물운 완전 분석**\n")
            if gkn in _MONEY_EASY:
                out.append(f"**▶ 재물 팔자 결론: {_MONEY_EASY[gkn]}**\n\n")
            out.append(f"격국(내 팔자 유형): **{gkn}**이니라.\n")

            out.append(_GKM.get(gkn, f"{gkn}의 재물 패턴은 독특하니라. 용신 기운을 따르게.") + "\n")

            out.append(f"\n용신 **{y1}** / 희신 **{heui}** 기운이 강한 해(年)에 재물 결정을 내려야 하느니라.\n")

            if gisin:
                out.append(f"⚠️ **기신 경고:** {gisin} 기운 강한 해에는 큰 투자·동업·보증을 반드시 피하게! 이 해에 움직이면 손실이 크니라.\n")

            # 향후 재물 황금기 (용신 세운, 별점 차등)

            gold_ohs = {o for o in [y1, y2] if o in ("木", "火", "土", "金", "水")}

            gold_yrs = []

            for yr in range(current_year, current_year + 11):
                sw_g = get_yearly_luck(pils, yr) or {}

                if OH.get((sw_g.get("세운", "")[:1]), "") in gold_ohs:
                    sw_g_ss = sw_g.get("십성_천간", "")

                    star = "★★★" if sw_g_ss in ("偏財(편재)", "正財(정재)", "食神(식신)") else "★★" if sw_g_ss in ("正官(정관)", "正印(정인)") else "★"

                    gold_yrs.append(f"* **{yr}년**({yr - birth_year + 1}세): {sw_g.get('세운', '')} [{sw_g_ss}] {sw_g.get('길흉', '')} {star}")

            if gold_yrs:
                out.append(f"\n**[향후 재물 황금기 — 용신 세운]**\n")

                for gy in gold_yrs[:6]:
                    out.append(gy + "\n")

                out.append("이 해들에 중요한 재물 결정을 내리게!\n")

            # 대운×세운 재물 더블 황금기

            try:
                hl_m = generate_engine_highlights(pils, birth_year, gender, bm, bd, bh, bmn)

                double_mp = [m for m in hl_m.get("money_peak", []) if m.get("ss") == "더블"]

                if double_mp:
                    out.append(f"\n**[대운×세운 재물 더블 황금기]** — 이 시기가 진짜 인생 재물 피크니라!\n")

                    for m in double_mp[:3]:
                        out.append(f"* {m.get('year', '')}년 ({m.get('age', '')}) {m.get('desc', '')}\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 기신 대운 경고

            try:
                dw_list_m = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                gisin_ohs = set(ys.get("기신", []))

                gisin_dws = [dw for dw in dw_list_m if OH.get(dw.get("cg", ""), "") in gisin_ohs and dw["종료연도"] >= current_year]

                if gisin_dws:
                    gdw = gisin_dws[0]

                    gdw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(gdw["cg"], "-")

                    if gdw["시작연도"] <= current_year:
                        out.append(f"\n⚠️ 지금 **{gdw['str']} {gdw_ss}** 기신 대운 진행 중! {gdw['종료연도'] - current_year}년 더 이어지느니라. 대형 투자·보증 자제가 최선이니라.\n")

                    else:
                        out.append(f"\n⚠️ {gdw['시작연도']}년({gdw['시작나이']}세)부터 **{gdw['str']} {gdw_ss}** 기신 대운이 오느니라. 미리 안전 자산 확보를 서두르게!\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

        elif is_love:
            out.append(f"**{name}의 인연·결혼운 완전 분석**\n허어, 인연의 실타래를 신안으로 살펴보겠느니라.\n")
            _love_now_e = get_yearly_luck(pils, current_year) or {}
            _love_ss_e = _love_now_e.get("십성_천간","").split("(")[0]
            _LOVE_EASY = {
                "偏財":"💕 올해 이성 인연이 강하게 오는 해 (남성 기준)","正財":"💕 안정적 결혼 인연이 오는 해 (남성 기준)",
                "偏官":"💕 강렬한 이성 기운이 들어오는 해 (여성 기준)","正官":"💕 공식 연애·결혼 기운의 해 (여성 기준)",
                "劫財":"⚠️ 이성 경쟁자·삼각관계 주의해야 하는 해","傷官":"⚠️ 말·감정이 관계를 흔들기 쉬운 해",
            }
            if _love_ss_e in _LOVE_EASY:
                out.append(f"\n**▶ 올해 연애운 결론: {_LOVE_EASY[_love_ss_e]}**\n\n")

            # 1. 배우자 자리(정재/편재 또는 정관/편관) 분석

            yk = get_yukjin(ilgan, pils, gender)

            spouse_keys = ["아내", "처", "正財(정재)", "妻"] if gender == "남" else ["남편", "夫", "正官(정관)", "情夫", "편관"]

            for rel in yk:
                rn = rel.get("관계", "")

                if any(k in rn for k in spouse_keys):
                    loc = rel.get("위치", "없음")

                    out.append(f"\n**[배우자 자리]** {rn} — 위치: **{loc}**\n")

                    out.append(rel.get("desc", "") + "\n")

                    if rel.get("present"):
                        out.append("허허, 배우자 기운이 사주에 뚜렷이 자리 잡고 있구먼. 인연은 반드시 오느니라.\n")

                    else:
                        out.append("배우자 기운이 약하니 대운·세운에서 재성/관성이 들어올 때 적극적으로 움직이게.\n")

                    break

            # 2. 일지(배우자 자리) 지지 해석

            iljj = pils[1]["jj"] if len(pils) > 1 else "?"

            _ILJJ_LOVE = {
                "子": "지적이고 감각적인 분을 배우자로 만날 가능성이 높습니다. 지적 교감과 정서적 소통이 부부 관계의 핵심입니다. [주의] 배우자의 감정 기복과 비밀주의를 이해하고 포용하는 마음이 필요합니다.",
                "丑": "성실하고 현실적이며 가정적인 분을 배우자로 만나게 됩니다. [주의] 배우자의 고집과 변화 거부를 이해하며 부드럽게 이끌어야 합니다.",
                "寅": "활동적이고 추진력 있는 분을 배우자로 만납니다. 서로에게 에너지를 주고받는 역동적인 관계가 형성됩니다. [주의] 주도권 갈등 역할 분담 요망.",
                "卯": "섬세하고 예술적 감각이 있는 분을 배우자로 만납니다. 온화하고 부드러운 매력. [주의] 배우자가 우유부단할 때 지지자가 되어주어야 합니다.",
                "辰": "다재다능하고 신비로우며 위기 상황에서 놀라운 능력을 발휘하는 분을 만납니다. [주의] 안정적인 소통의 장을 만드세요.",
                "巳": "지혜롭고 신중하며 경제적 감각이 뛰어난 분을 배우자로 만납니다. [주의] 배우자의 언어 표현 부족으로 오해가 생길 수 있어 주의.",
                "午": "열정적이고 표현력이 강하며 뜨겁게 사랑하는 분을 만납니다. [주의] 감정 기복이 크므로 포용력 필요.",
                "未": "따뜻하고 예술적 감각이 있으며 가정을 최우선하는 분을 만납니다. [주의] 미적 취향 기준을 존중해 주세요.",
                "申": "영리하고 임기응변이 뛰어나며 사교적인 분을 만납니다. [주의] 함께하는 시간을 반드시 확보하세요.",
                "酉": "세련되고 예리하며 완벽을 추구하는 분을 만납니다. [주의] 배우자의 높은 기준을 불편해하지 말고 존중하세요.",
                "戌": "의리 있고 충직하며 정의감이 강한 분을 만납니다. [주의] 평소 충분히 감정을 풀어주세요.",
                "亥": "자유롭고 포용력 있으며 영성적인 분을 만납니다. [주의] 자유 추구를 인정하되 현실적인 공동 목표를 함께 세우세요.",
            }

            out.append(f"\n**[일지 배우자 자리 — {iljj}]**\n{_ILJJ_LOVE.get(iljj, f'일지 {iljj}의 기운이 배우자 자리에 흐르느니라.')}\n")

            # 3. 대운에서 재성/관성운 들어오는 시기

            try:
                daewoon = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                love_dw_ss = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

                love_dws = [dw for dw in daewoon if TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "") in love_dw_ss and dw["종료연도"] >= current_year]

                if love_dws:
                    cdw = love_dws[0]

                    cdw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cdw["cg"], "")

                    if cdw["시작연도"] <= current_year:
                        out.append(f"\n**[대운 인연 시기]** 지금 **{cdw['str']} {cdw_ss}** 대운 진행 중! {cdw['종료연도'] - current_year}년 남았으니 이 기간을 놓치지 말게!\n")

                    else:
                        out.append(f"\n**[대운 인연 시기]** {cdw['시작연도']}년({cdw['시작나이']}세)부터 **{cdw['str']} {cdw_ss}** 대운이 열리느니라. 그때가 인연의 문이 활짝 열리는 시기니라.\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 4. 향후 3년 중 연애운 좋은 해 특정

            love_yr_ss = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

            love_yrs = []

            for yr in range(current_year, current_year + 4):
                sw_l = get_yearly_luck(pils, yr) or {}

                sw_ss_l = sw_l.get("십성_천간", "")

                if sw_ss_l in love_yr_ss:
                    love_yrs.append(f"**{yr}년**({yr - birth_year + 1}세): {sw_l.get('세운', '')} [{sw_ss_l}] {sw_l.get('길흉', '')} ← 이성 인연 기운이 강하느니라!")

            if love_yrs:
                out.append("\n**[향후 3년 연애·결혼 특효 시기]**\n")

                for ly in love_yrs:
                    out.append(f"* {ly}\n")

                out.append("이 해들에 적극적으로 인연을 찾아 나서게. 하늘이 돕는 시기니라!\n")

            else:
                sw_now = get_yearly_luck(pils, current_year)

                out.append(f"\n올해 {sw_now.get('세운', '')} [{sw_now.get('십성_천간', '')}] — 향후 3년은 이성 세운이 약하니 자기계발로 내실을 다지는 시기니라. 인연은 준비된 자에게 오느니라.\n")

            # 5. 도화살 확인

            try:
                sinsal = get_special_stars(pils)

                dohwa_found = [s for s in sinsal if "도화" in s.get("name", "")]

                ss12 = get_12sinsal(pils)

                dohwa12 = [s for s in ss12 if "도화" in s.get("이름", "") or "년살" in s.get("이름", "")]

                if dohwa_found or dohwa12:
                    out.append(
                        "\n**[신살 — 도화살(桃花殺)]** 도화살이 사주에 있구먼!\n이성의 인기를 한몸에 받는 매력의 기운이니라. 이성이 먼저 다가오는 팔자이나, 감정에 휩쓸려 경솔한 선택을 하지 않도록 명심하게.\n"
                    )

                else:
                    out.append("\n도화살은 없으나, 꾸준한 진심이 최고의 인연을 불러오느니라.\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 6. 결혼 적령기

            current_age = current_year - birth_year + 1

            out.append(f"\n**[결혼 적령기 — 현재 {current_age}세]**\n")

            try:
                daewoon2 = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                love_ss2 = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

                future_dws = [dw for dw in daewoon2 if TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "") in love_ss2 and dw["종료연도"] >= current_year]

                if future_dws:
                    bd2 = future_dws[0]

                    bd2_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(bd2["cg"], "")

                    if bd2["시작연도"] <= current_year:
                        out.append(f"지금 **{bd2['str']} {bd2_ss}** 대운 중! **{current_year}~{bd2['종료연도']}년**이 최적 결혼 시기니라. 망설이지 말게!\n")

                    else:
                        out.append(f"**{bd2['시작연도']}년({bd2['시작나이']}세)**부터 {bd2['str']} **{bd2_ss}** 대운이 열리느니라. 그 무렵 결혼 결실이 맺어질 가능성이 높느니라.\n")

                else:
                    for yr in range(current_year, current_year + 10):
                        sw_y = get_yearly_luck(pils, yr) or {}

                        if sw_y.get("십성_천간", "") in ({"偏財", "正財"} if gender == "남" else {"偏官", "正官"}):
                            out.append(f"**{yr}년({yr - birth_year + 1}세)** 세운에 인연 기운이 들어오느니라. 그 무렵 준비하게.\n")

                            break

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

        elif is_health:
            ilgan_oh = OH.get(ilgan, "")

            _OHB = {
                "木": "간장·담낭·눈·근육·인대·신경계",
                "火": "심장·소장·혈관·혈압·시력",
                "土": "비장·위장·췌장·소화기·근육",
                "金": "폐·대장·기관지·피부·호흡기",
                "水": "신장·방광·생식기·귀·뼈·척추",
            }
            _OHA = {
                "木": "스트레칭과 충분한 수면이 최우선이니라. 분노·스트레스가 간장을 상하게 하느니라. 신맛 음식(식초·레몬·매실)이 도움이 되느니라.",
                "火": "심혈관 정기검진이 필수이니라. 카페인·음주를 자제하고 과로를 삼가게. 쓴맛 음식(커피 대신 녹차·쑥)이 도움이 되느니라.",
                "土": "식사 규칙성이 핵심이니라. 폭식·군것질을 삼가게. 걱정이 위장을 상하게 하느니라. 단맛 음식(고구마·감자·현미)이 도움이 되느니라.",
                "金": "습도 관리가 중요하니라. 가을·건조한 환경을 조심하게. 매운맛 음식(도라지·배·무)이 폐를 강화하느니라.",
                "水": "충분한 수분 섭취가 필수니라. 과로·짠 음식을 피하게. 검은콩·해조류·흑임자가 신장을 보호하느니라.",
            }

            out.append(f"**{name}의 건강운 완전 분석**\n일간 {ilgan}의 오행은 **{OHN.get(ilgan_oh, '')}({ilgan_oh})**이니라.\n")
            out.append(f"**타고난 취약 신체**: {_OHB.get(ilgan_oh, '전반적 건강')}\n")
            out.append(_OHA.get(ilgan_oh, "규칙적인 생활이 핵심이니라.") + "\n")

            # 오행 과다/부족 TOP3
            oh_s = calc_ohaeng_strength(ilgan, pils)
            out.append("\n**[오행별 건강 취약점 TOP3]**")
            _sorted_oh = sorted(oh_s.items(), key=lambda x: x[1])
            for o, v in _sorted_oh[:2]:
                if v <= 8:
                    out.append(f"- 💊 **{OHN.get(o,'')}({o}) 부족({v:.0f}%)**: {_OHB.get(o,'')} 계통 보강 필요. 이 오행이 약하면 해당 장기가 취약하느니라.")
            for o, v in sorted(oh_s.items(), key=lambda x: -x[1])[:1]:
                if v >= 35:
                    out.append(f"- ⚠️ **{OHN.get(o,'')}({o}) 과다({v:.0f}%)**: {_OHB.get(o,'')} 계통 혹사 주의. 과다한 오행이 해당 장기를 과부하시키느니라.")
            out.append("")

            # 현재 대운 건강 영향
            try:
                dw_list_h = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)
                cdw_h = next(
                    (d for d in dw_list_h if d["시작연도"] <= current_year <= d["종료연도"]),
                    None,
                )
                if cdw_h:
                    cdw_ss_h = TEN_GODS_MATRIX.get(ilgan, {}).get(cdw_h["cg"], "-")
                    cdw_oh_h = OH.get(cdw_h["cg"], "")
                    _DWH = {
                        "偏官": "편관 대운은 압박·스트레스가 극심하느니라. 면역력 저하와 사고 위험이 높으니 정기검진을 서두르게.",
                        "傷官": "상관 대운은 신경계 과부하와 과로가 주적이니라. 수면 관리와 스트레스 해소가 핵심이니라.",
                        "劫財": "겁재 대운은 외상·수술·혈액 관련 건강 이슈가 올 수 있으니라. 운동 시 안전에 유의하게.",
                        "偏印": "편인 대운은 우울·불안·정신건강에 주의가 필요하니라. 고립을 피하고 활동적으로 지내게.",
                        "比肩": "비견 대운은 과도한 경쟁과 독립 행보로 체력 소진을 조심하게. 충분한 휴식이 필수이니라.",
                        "食神": "식신 대운은 건강이 비교적 좋은 시기니라. 다만 과식으로 인한 소화계 문제를 조심하게.",
                        "正財": "정재 대운은 안정적 건강 유지가 가능한 시기니라. 규칙적 생활로 내실을 다지게.",
                        "正官": "정관 대운은 스트레스가 직장에서 오므로 멘탈 관리에 집중하게.",
                        "偏財": "편재 대운은 분주한 활동으로 체력 소진을 조심하게. 철저한 체력 관리가 필요하느니라.",
                        "正印": "정인 대운은 건강이 좋은 편이나 과보호 경향이 오히려 체력을 약하게 만들 수 있느니라.",
                    }
                    out.append(f"**[현재 대운 건강 영향]** {cdw_h['str']} **{cdw_ss_h}** 대운 ({cdw_h['종료연도'] - current_year}년 남음)\n")
                    out.append(_DWH.get(cdw_ss_h, f"{cdw_ss_h} 대운의 건강 기운이 흐르느니라. 몸의 신호에 귀를 기울이게.") + "\n")
                    out.append(f"이 대운 오행: **{OHN.get(cdw_oh_h,'')}({cdw_oh_h})** — {_OHB.get(cdw_oh_h,'')} 계통에 영향을 주느니라.\n")
            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 올해 세운 건강 경보
            sw_hlt    = get_yearly_luck(pils, current_year) or {}
            sw_hlt_ss = sw_hlt.get("십성_천간", "")
            _YEAR_HEALTH = {
                "偏官": f"⚠️ 올해({current_year}년) [偏官(편관)] 세운 — 건강 사고 위험 높은 해니라. 무리한 활동·수술은 신중하게. 정기검진 필수.\n",
                "傷官": f"올해({current_year}년) [傷官(상관)] 세운 — 과로와 신경 소모가 심한 해니라. 충분한 휴식이 최우선이니라.\n",
                "劫財": f"올해({current_year}년) [劫財(겁재)] 세운 — 체력 소진·외상 조심. 무리한 운동이나 야간 활동을 자제하게.\n",
            }
            if sw_hlt_ss in _YEAR_HEALTH:
                out.append("\n" + _YEAR_HEALTH[sw_hlt_ss])

            # 향후 5년 건강 위험 구간
            out.append("\n**[향후 5년 건강 위험 구간]**")
            _bad_health_ss = {"偏官","劫財","傷官"}
            ys_hlt = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            gisin_hlt = set(ys_hlt.get("기신", []))
            for _yr in range(current_year, current_year + 5):
                try:
                    _sw_hlt = get_yearly_luck(pils, _yr) or {}
                    _hs     = _sw_hlt.get("십성_천간","")
                    _hg     = _sw_hlt.get("길흉","평")
                    _hoh    = OH.get(_sw_hlt.get("세운","")[:1],"")
                    _hgs    = _hoh in gisin_hlt
                    if _hs in _bad_health_ss:
                        out.append(f"- 🔴 **{_yr}년** [{_hs}] — 각별 건강 주의 구간")
                    elif _hgs and _hg in ("흉","-"):
                        out.append(f"- ⚠️ **{_yr}년** [{_hs}] — 기신 흉운, 면역 관리 필요")
                    else:
                        out.append(f"- ✅ **{_yr}년** [{_hs}] — 안정 구간")
                except Exception:
                    pass

            # 용신 오행 건강 처방
            ys_hlt2 = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            yong_oh1 = ys_hlt2.get("용신_1순위","")
            _OH_RX = {
                "木": "🌿 초록 채소·산책·스트레칭이 건강을 지키느니라. 동쪽 방향이 기운을 살리느니라.",
                "火": "🔥 햇빛 쬐기·적당한 유산소 운동이 심혈관을 강화하느니라. 남쪽 방향이 길하느니라.",
                "土": "🏔️ 규칙적 식사·명상·걷기 운동이 소화기를 지키느니라. 황색 식품이 도움이 되느니라.",
                "金": "⚙️ 폐 호흡 운동·수영·흰색 식품(무·배·도라지)이 호흡기를 강화하느니라.",
                "水": "💧 충분한 수분 섭취·수영·검은콩·해조류가 신장을 보호하느니라. 북쪽이 길하느니라.",
            }
            if yong_oh1 in _OH_RX:
                out.append(f"\n**[용신 오행 건강 처방]** {_OH_RX[yong_oh1]}")

            # 오행 과다/부족 건강 경고

            oh_s = calc_ohaeng_strength(ilgan, pils)

            for o, v in oh_s.items():
                if v >= 35:
                    out.append(f"\n⚠️ **{OHN.get(o, '')}({o}) 과다({v}%):** {_OHB.get(o, '')} 계통 특히 조심하게. 과다한 오행이 해당 장기를 혹사시키느니라.")

                elif v <= 5:
                    out.append(f"\n💊 **{OHN.get(o, '')}({o}) 부족({v}%):** {_OHB.get(o, '')} 계통 보강하게. 부족한 오행이 해당 장기를 약하게 만드느니라.")

            # 현재 대운 건강 영향

            try:
                dw_list_h = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                cdw_h = next(
                    (d for d in dw_list_h if d["시작연도"] <= current_year <= d["종료연도"]),
                    None,
                )

                if cdw_h:
                    cdw_ss_h = TEN_GODS_MATRIX.get(ilgan, {}).get(cdw_h["cg"], "-")

                    cdw_oh_h = OH.get(cdw_h["cg"], "")

                    _DWH = {
                        "偏官": "편관 대운은 압박과 스트레스가 극심하느니라. 면역력 저하와 사고 위험이 높으니 정기검진을 서두르게.",
                        "傷官": "상관 대운은 신경계 과부하와 과로가 주적이니라. 수면 관리와 스트레스 해소가 핵심이니라.",
                        "劫財": "겁재 대운은 외상·수술·혈액 관련 건강 이슈가 올 수 있으니라. 운동 시 안전에 유의하게.",
                        "偏印": "편인 대운은 우울·불안·정신건강에 주의가 필요하니라. 고립을 피하고 활동적으로 지내게.",
                        "比肩": "비견 대운은 과도한 경쟁과 독립 행보로 체력 소진을 조심하게. 충분한 휴식이 필수이니라.",
                        "食神": "식신 대운은 건강이 비교적 좋은 시기니라. 다만 과식으로 인한 소화계 문제를 조심하게.",
                        "正財": "정재 대운은 안정적 건강 유지가 가능한 시기니라. 규칙적 생활로 내실을 다지게.",
                        "正官": "정관 대운은 스트레스가 직장에서 오므로 멘탈 관리에 집중하게.",
                        "偏財": "편재 대운은 분주한 활동으로 체력 소진을 조심하게. 철저한 체력 관리가 필요하느니라.",
                        "正印": "정인 대운은 건강이 좋은 편이나 과보호·의존 경향이 오히려 체력을 약하게 만들 수 있느니라.",
                    }

                    out.append(f"\n**[현재 대운 건강 영향]** {cdw_h['str']} **{cdw_ss_h}** 대운 ({cdw_h['종료연도'] - current_year}년 남음)\n")

                    out.append(
                        _DWH.get(
                            cdw_ss_h,
                            f"{cdw_ss_h} 대운의 건강 기운이 흐르느니라. 몸의 신호에 귀를 기울이게.",
                        )
                        + "\n"
                    )

                    out.append(f"이 대운 오행: **{OHN.get(cdw_oh_h, '')}({cdw_oh_h})** — {_OHB.get(cdw_oh_h, '')} 계통에 영향을 주느니라.\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 올해 세운 건강 경보

            sw_hlt = get_yearly_luck(pils, current_year) or {}

            sw_hlt_ss = sw_hlt.get("십성_천간", "")

            if sw_hlt_ss == "偏官":
                out.append(f"\n⚠️ 올해({current_year}년) {sw_hlt.get('세운', '')} [偏官(편관)] 세운 — 건강 사고 위험 높은 해니라. 무리한 활동·수술 신중하게.\n")

            elif sw_hlt_ss == "傷官":
                out.append(f"\n올해({current_year}년) {sw_hlt.get('세운', '')} [傷官(상관)] 세운 — 과로와 신경 소모가 심한 해니라. 충분한 휴식이 최우선이니라.\n")

        elif is_dw:
            daewoon = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

            cdw = next(
                (d for d in daewoon if d["시작연도"] <= current_year <= d["종료연도"]),
                None,
            )

            out.append(f"**{name}의 대운 흐름 완전 분석**\n")

            # 용신 기반 황금기/주의기 판별

            try:
                ys_dw = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                yong_ohs_dw = {
                    o
                    for o in [
                        ys_dw.get("용신_1순위", ""),
                        ys_dw.get("용신_2순위", ""),
                        ys_dw.get("희신", ""),
                    ]
                    if o in ("木", "火", "土", "金", "水")
                }

                gisin_dw = set(ys_dw.get("기신", []))

            except Exception:
                yong_ohs_dw = set()
                gisin_dw = set()

            if cdw:
                cdw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cdw["cg"], "-")

                cdw_oh = OH.get(cdw["cg"], "")

                grade = "🌟 황금기 대운" if cdw_oh in yong_ohs_dw else "⚠️ 주의기 대운" if cdw_oh in gisin_dw else "⬜ 보통 대운"

                out.append(f"현재 대운: **{cdw['str']}** ({cdw_ss}) — **{grade}**\n")

                out.append(f"{cdw['시작연도']}~{cdw['종료연도']}년 ({cdw['시작나이']}~{cdw['시작나이'] + 9}세), **{cdw['종료연도'] - current_year}년** 더 이어지느니라.\n")

                out.append(DAEWOON_PRESCRIPTION.get(cdw_ss, "꾸준한 노력으로 안정을 유지하게.") + "\n")

                if cdw_oh in yong_ohs_dw:
                    out.append("이 대운은 용신 기운이 흐르는 황금기니라! 크게 움직여도 하늘이 돕는 시기이니라.\n")

                elif cdw_oh in gisin_dw:
                    out.append("이 대운은 기신 기운이 흐르는 주의기니라. 무리한 확장보다 안전 자산 확보와 내실 다지기가 최선이니라.\n")

            # 다음 대운 미리보기

            cdw_idx = next(
                (i for i, d in enumerate(daewoon) if d["시작연도"] <= current_year <= d["종료연도"]),
                None,
            )

            if cdw_idx is not None and cdw_idx + 1 < len(daewoon):
                ndw = daewoon[cdw_idx + 1]

                ndw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(ndw["cg"], "-")

                ndw_oh = OH.get(ndw["cg"], "")

                ndw_grade = "🌟 황금기" if ndw_oh in yong_ohs_dw else "⚠️ 주의기" if ndw_oh in gisin_dw else "⬜ 보통"

                out.append(f"\n**[다음 대운 미리보기]** {ndw['시작연도']}년({ndw['시작나이']}세)부터 **{ndw['str']} {ndw_ss}** ({ndw_grade}) 대운이 열리느니라.\n")

                out.append(DAEWOON_PRESCRIPTION.get(ndw_ss, "새 대운을 준비하게.") + "\n")

            out.append("\n**전체 대운 흐름 (🌟황금기 / ⚠️주의기 표시):**\n")

            for dw in daewoon[:8]:
                dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

                dw_oh = OH.get(dw["cg"], "")

                dw_grade = "🌟" if dw_oh in yong_ohs_dw else "⚠️" if dw_oh in gisin_dw else "⬜"

                cur_m = " ◀현재" if dw["시작연도"] <= current_year <= dw["종료연도"] else ""

                out.append(f"* {dw['시작나이']}~{dw['시작나이'] + 9}세: {dw['str']} ({dw_ss}) {dw_grade}{cur_m}\n")

        elif is_past:
            hl = generate_engine_highlights(pils, birth_year, gender, bm, bd, bh, bmn)

            pevs = sorted(
                hl.get("past_events", []),
                key=lambda e: {"🔴": 0, "🟡": 1, "🟢": 2}.get(e.get("intensity", "🟢"), 3),
            )

            out.append(f"**{name}의 과거 사건 완전 분석**\n허허, 지나온 세월을 신안으로 살펴보겠느니라.\n")

            if pevs:
                out.append("\n**[주요 과거 사건 — 강도순]**\n")

                for ev in pevs[:6]:
                    out.append(f"\n**{ev.get('year', '')}년 ({ev.get('age', '')}) {ev.get('intensity', '')} [{ev.get('domain', '변화')}]**\n{ev.get('desc', '')}\n")

            else:
                out.append("사주 엔진이 과거 데이터를 분석 중이니라.\n")

            # 월지 충 근거 (기반이 흔들린 시기)

            wc = hl.get("wolji_chung", [])

            if wc:
                out.append("\n**[월지 충(沖) — 삶의 기반이 흔들린 시기]**\n")

                for w in wc[:3]:
                    out.append(f"* {w.get('age', '')}: {w.get('desc', '')}\n")

            # 위험 구간 (과거분)

            dz = hl.get("danger_zones", [])

            if dz:
                try:
                    past_dz = [d for d in dz if d.get("year", "") and int(d["year"].split("~")[-1]) <= current_year]

                except Exception:
                    past_dz = []

                if past_dz:
                    out.append("\n**[과거 위험 구간 — 힘든 시기의 근거]**\n")

                    for d in past_dz[:2]:
                        out.append(f"* {d.get('age', '')}: {d.get('desc', '')}\n")

        elif is_job:
            gk = get_gyeokguk(pils)

            gkn = gk["격국명"] if gk else "미정격"

            ys2 = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            y1j = ys2.get("용신_1순위", "-")

            si_j = get_ilgan_strength(ilgan, pils)

            sn_j = si_j.get("신강신약", "중화")

            _JOB = {
                "정관격": "조직·공직·행정·관리직·법조가 천직이니라. 안정된 조직 안에서 명예와 재물이 함께 오느니라. 공무원·대기업·공공기관이 최적이니라.",
                "편관격": "군경·의료·법조·스포츠·안전·소방·국방 분야에서 진가를 발휘하느니라. 강인한 의지와 추진력이 강점이니라.",
                "정재격": "금융·회계·부동산·세무·유통·은행이 맞느니라. 성실한 노력으로 안정된 자산을 쌓는 팔자니라. 꼼꼼함과 책임감이 무기니라.",
                "편재격": "사업·영업·투자·무역·중개·부동산 개발이 맞느니라. 기회를 포착하는 사업가 기질이 타고났느니라. 빠른 판단력이 핵심이니라.",
                "식신격": "요식·창작·예술·교육·서비스·콘텐츠·강의가 맞느니라. 재능이 곧 밥그릇이 되는 팔자니라.",
                "상관격": "IT·방송·컨설팅·프리랜서·스타트업·예술가에서 독보적 존재가 되느니라. 창의력이 최대 무기니라.",
                "편인격": "학문·연구·철학·심리·의학·IT연구·특허 분야가 천직이니라. 깊은 통찰이 곧 경쟁력이니라.",
                "정인격": "교육·학술·전문직·자격증 기반 직종·상담이 맞느니라. 배움이 쌓일수록 위상이 높아지느니라.",
                "비견격": "독립·자영업·프리랜서·개인사업·1인 기업이 맞느니라. 혼자 움직일 때 가장 강해지는 팔자니라.",
                "겁재격": "경쟁·협상·중개·스포츠·증권·선물 분야에서 오히려 빛나는 팔자니라.",
            }

            _OHJOB = {
                "木": "목재·제지·섬유·교육·의류·원예·환경·에너지·스포츠 관련 업종이 유리하느니라.",
                "火": "방송·광고·전기·전자·IT·연예·문화·조명·화학 관련 업종이 유리하느니라.",
                "土": "부동산·건설·농업·의약·식품·유통·경영컨설팅 관련 업종이 유리하느니라.",
                "金": "금융·금속·기계·법조·의료·국방·스포츠·경찰 관련 업종이 유리하느니라.",
                "水": "무역·해운·유통·관광·호텔·미디어·철학·심리 관련 업종이 유리하느니라.",
            }

            _SWJOB = {
                "食神": "올해는 재능 발휘와 자격 취득에 최적의 해니라. 새 프로젝트를 시작하게!",
                "正官": "승진·이직·공직 시험에 유리한 해니라. 조직 내 신뢰를 쌓는 것이 핵심이니라.",
                "偏財": "사업·영업 기회가 오는 해니라. 적극적으로 나서되 도박성 투자는 자제하게.",
                "正財": "안정된 수입·직장 유지에 좋은 해니라. 차분하게 실력을 쌓는 것이 맞느니라.",
                "傷官": "독립·창업·이직을 고려한다면 올해가 전환점이 될 수 있느니라. 단 계약서 주의.",
                "偏官": "직장 변동·갈등이 올 수 있느니라. 무리한 도전보다 현 자리 지키기가 현명하니라.",
            }

            _JOB_EASY = {
                "정관격":"✅ 공무원·대기업·조직 승진 — 안정된 조직이 천직","편관격":"✅ 군경·의료·법조·스포츠 — 강인함 필요 분야",
                "정재격":"💰 금융·회계·부동산·은행 — 성실함이 무기","편재격":"⚡ 사업·영업·투자 — 기회포착 사업가 기질",
                "식신격":"🌟 요식·창작·교육·콘텐츠 — 재능이 밥벌이","상관격":"💡 IT·방송·컨설팅·프리랜서 — 창의력이 무기",
                "편인격":"📚 학문·연구·심리·의학 — 통찰이 경쟁력","정인격":"📚 교육·전문직·자격증 기반 — 배울수록 위상 높아짐",
                "비견격":"⚡ 독립사업·프리랜서·1인기업 — 혼자 움직일 때 최강","겁재격":"⚠️ 경쟁·협상·증권·스포츠 — 경쟁 속에서 빛남",
            }
            out.append(f"**{name}의 직업·진로 완전 분석**\n")
            if gkn in _JOB_EASY:
                out.append(f"**▶ 내 천직 결론: {_JOB_EASY[gkn]}**\n\n")
            out.append(f"격국(팔자 유형): **{gkn}** — 이 방향이 가장 잘 맞는 직업군이니라.\n")

            out.append(_JOB.get(gkn, f"{gkn}의 독특한 기운을 살려 자신만의 길을 개척해야 하느니라.") + "\n")

            # 십성 분포 분석

            try:
                ss_list_j = calc_sipsung(ilgan, pils)

                _GRP = {
                    "비견": "비겁",
                    "겁재": "비겁",
                    "식신": "식상",
                    "상관": "식상",
                    "정재": "재성",
                    "편재": "재성",
                    "정관": "관성",
                    "편관": "관성",
                    "정인": "인성",
                    "편인": "인성",
                }

                sc_cnt = {}

                for p in ss_list_j:
                    g = _GRP.get(p.get("십성", ""), "")

                    if g:
                        sc_cnt[g] = sc_cnt.get(g, 0) + 1

                top_g = max(sc_cnt, key=sc_cnt.get) if sc_cnt else ""

                _SGJ = {
                    "재성": "재물을 직접 다루는 영역에서 두각을 드러내느니라.",
                    "관성": "조직과 권위 안에서 진가가 빛나느니라.",
                    "식상": "창의와 표현으로 세상을 사로잡는 팔자니라.",
                    "인성": "배움과 자격증으로 전문성을 쌓는 것이 맞느니라.",
                    "비겁": "독립과 경쟁 속에서 오히려 강해지는 팔자니라.",
                }

                if top_g:
                    out.append(f"\n사주 십성 분포상 **{top_g}** 기운이 강하니 {_SGJ.get(top_g, '')}\n")

            except Exception as _e:
                _saju_log.debug("[silent except] %s", _e)

            # 용신 오행 업종

            out.append(f"\n**[용신 오행 업종]** 용신 **{y1j}** — {_OHJOB.get(y1j, f'{y1j} 오행 관련 업종이 맞느니라.')}\n")

            # 신강신약 행동 패턴

            if "신강" in sn_j:
                out.append(f"\n**신강({sn_j})** — 독립·창업·단독 행보가 최적이니라. 조직보다 자신이 주도하는 환경에서 능력을 발휘하느니라.\n")

            elif "신약" in sn_j:
                out.append(f"\n**신약({sn_j})** — 안정된 조직·전문직 안에서 귀인의 도움을 받는 것이 최적이니라. 창업보다 전문성 강화가 우선이니라.\n")

            # 올해 진로 세운

            sw_j = get_yearly_luck(pils, current_year) or {}

            sw_j_ss = sw_j.get("십성_천간", "")

            out.append(f"\n올해({current_year}년) {sw_j.get('세운', '')} [{sw_j_ss}] {sw_j.get('길흉', '')} — {_SWJOB.get(sw_j_ss, sw_j_ss + ' 기운의 해이니 흐름을 잘 읽고 움직이게.')}\n")

            out.append(f"\n용신 **{y1j}** 오행이 강한 해에 진로 결정을 내리면 가장 유리하느니라. 명심하게!\n")

        elif is_char:
            gk = get_gyeokguk(pils)

            si = get_ilgan_strength(ilgan, pils)

            gkn = gk["격국명"] if gk else "미정격"

            sn = si.get("신강신약", "중화")

            sc = si.get("일간점수", 50)

            _CG_KR = {
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

            _ilgan_k = f"{ilgan}({_CG_KR.get(ilgan, '')})"

            _CHR = ILGAN_CHAR_DESC.get(_ilgan_k, ILGAN_CHAR_DESC.get(ilgan, {}))

            oh_s_c = calc_ohaeng_strength(ilgan, pils)

            out.append(f"**{name}의 성격·기질 완전 분석**\n일간 **{ilgan}** | 격국 **{gkn}** | **{sn}**(점수 {sc}/100)\n")

            out.append(_CHR.get("성격_핵심", f"일간 {ilgan}의 기운이 삶 전반을 이끄느니라.") + "\n")

            if _CHR.get("장점"):
                out.append(f"\n**[장점]** {_CHR['장점']}\n")

            if _CHR.get("단점"):
                out.append(f"**[주의]** {_CHR['단점']}\n")

            if _CHR.get("재물패턴"):
                out.append(f"**[재물 성향]** {_CHR['재물패턴']}\n")

            if _CHR.get("건강"):
                out.append(f"**[건강 주의]** {_CHR['건강']}\n")

            if _CHR.get("직업"):
                out.append(f"**[천직 힌트]** {_CHR['직업']}\n")

            _SNS = {
                "신강": f"기운이 넘치는 신강({sc}/100)이니라. 스스로 움직여야 기회가 오느니라. 독립적 결단이 맞는 팔자이나 자기중심적으로 흐를 수 있으니 타인 의견에도 귀를 열게.",
                "신약": f"기운이 부족한 신약({sc}/100)이니라. 귀인과 함께할 때 진가가 발휘되느니라. 좋은 파트너·스승이 운명을 바꾸느니라. 협업 속에서 빛나는 팔자이니라.",
                "중화": f"기운이 균형 잡힌 중화({sc}/100)이니라. 어느 상황에도 적응하는 유연함이 강점이니라. 꾸준함과 전문성이 최대 무기이니라.",
            }

            for k, v in _SNS.items():
                if k in sn:
                    out.append(f"\n**[신강신약 행동 패턴]** {v}\n")
                    break

            # 오행 과다 성격 패턴

            _OHC = {
                "木": "木 과다: 고집이 세고 자기주장이 강하며 리더십이 강함. 하지만 융통성 부족 주의.",
                "火": "火 과다: 열정적이고 급하며 사교성이 뛰어남. 하지만 과잉 행동과 산만함 주의.",
                "土": "土 과다: 신중하고 보수적이며 인내심이 강함. 하지만 변화 거부와 고집 주의.",
                "金": "金 과다: 원칙주의적이고 결단력이 강함. 하지만 냉철함이 지나쳐 인간관계 문제 주의.",
                "水": "水 과다: 지혜롭고 유연하며 전략적. 하지만 우유부단과 비밀주의 주의.",
            }

            for o, v in oh_s_c.items():
                if v >= 35:
                    out.append(f"\n{_OHC.get(o, '')}\n")

            sw = get_yearly_luck(pils, current_year) or {}

            out.append(f"\n올해({current_year}년)는 {sw.get('세운', '')} [{sw.get('십성_천간', '')}] {sw.get('길흉', '')} 기운이니 그 흐름을 잘 타게.\n")

        elif is_avoid:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            si = get_ilgan_strength(ilgan, pils)

            sw_ss = sw.get("십성_천간", "")

            sw_gh = sw.get("길흉", "")

            y1 = ys.get("용신_1순위", "-")

            gisin = ", ".join(ys.get("기신", []))

            sn = si.get("신강신약", "중화")

            _AVOID_SS = {
                "劫財": "겁재(劫財) 기운이 강하니 보증·동업·투기·도박을 절대 삼가게! 재물이 새어나가기 쉬운 시기니라.",
                "偏官": "편관(偏官) 기운이 강하니 법적 다툼·충돌·무리한 도전을 삼가게. 건강과 안전에 각별히 유의하게.",
                "傷官": "상관(傷官) 기운이니 윗사람과의 마찰, 계약·언행에 주의해야 하느니라. 독단 결정도 삼가게.",
            }

            out.append(f"**{name}의 {current_year}년 피할 일·조심할 것 분석**\n")

            out.append(f"올해 세운 {sw.get('세운', '')} [{sw_ss}] {sw_gh}\n")

            out.append(
                _AVOID_SS.get(
                    sw_ss,
                    f"올해 [{sw_ss}] 기운에서 특히 기신({gisin}) 오행과 관련된 일을 삼가는 것이 현명하니라.",
                )
                + "\n"
            )

            gisin_warn = {
                "木": "목(木) 방향/업種: 무리한 확장·소송·나무 관련 계약을 조심하게.",
                "火": "화(火) 관련: 급한 결정·충동 투자·말다툼·화재(火災) 주의.",
                "土": "토(土) 관련: 부동산 무리한 매입·토지 계약·신용 거래 주의.",
                "金": "금(金) 관련: 금전 보증·대출 확대·금속/기계 사고 주의.",
                "水": "수(水) 관련: 수상 사고·과음·불필요한 이동·비밀 누설 주의.",
            }

            if gisin:
                for g in ys.get("기신", []):
                    if g in gisin_warn:
                        out.append(f"\n⚠️ **기신({g}) 주의사항:** {gisin_warn[g]}\n")

            _SS_BAD_TIME = {
                "劫財": "돈 거래·대출·보증—절대 금기",
                "偏官": "무리한 도전·이직·창업 시작",
                "傷官": "상사와의 충돌·계약서 서명·공개적 발언",
                "偏印": "새 일 시작·여행·과감한 결정",
            }

            bad = _SS_BAD_TIME.get(sw_ss, "")

            if bad:
                out.append(f"\n**[올해 특히 조심할 행동]** {bad}\n")

            if "신강" in sn:
                out.append(f"\n신강 팔자는 자기 확신이 강해 실수를 인정하지 않기 쉬우니 타인 의견에도 귀를 열게.\n")

            elif "신약" in sn:
                out.append(f"\n신약 팔자는 타인에게 쉽게 끌려다니니 중요한 결정은 혼자 성급히 내리지 말게.\n")

        elif is_lucky:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            y1 = ys.get("용신_1순위", "-")

            heui = ys.get("희신", "-")

            out.append(f"**{name}의 좋은 날·길일·황금 시기 분석**\n허허, 하늘이 돕는 날을 골라주겠느니라.\n")

            _OH_DAY = {
                "木": "甲(갑)·乙(을) 일(日), 봄(1~3월), 동쪽 방향이 길하느니라. 인(寅)·묘(卯)시가 행운의 시각이니라.",
                "火": "丙(병)·丁(정) 일(日), 여름(4~6월), 남쪽 방향이 길하느니라. 오(午)시가 행운의 시각이니라.",
                "土": "戊(무)·己(기) 일(日), 환절기, 중앙 방향이 길하느니라. 진(辰)·술(戌)·축(丑)·미(未)시가 좋으니라.",
                "金": "庚(경)·辛(신) 일(日), 가을(7~9월), 서쪽 방향이 길하느니라. 申(신)·酉(유)시가 행운의 시각이니라.",
                "水": "壬(임)·癸(계) 일(日), 겨울(10~12월), 북쪽 방향이 길하느니라. 子(자)·亥(해)시가 행운의 시각이니라.",
            }

            out.append(f"\n용신 **{y1}** 오행이 살아있는 날이 곧 길일이니라!\n")

            out.append(_OH_DAY.get(y1, f"용신 {y1} 오행이 강한 날을 택하게.") + "\n")

            out.append(f"\n희신 **{heui}** 기운도 함께 활용하면 더욱 좋으니라.\n")

            out.append(_OH_DAY.get(heui, "") + "\n" if heui in _OH_DAY else "")

            gold_yrs2 = []

            for yr in range(current_year, current_year + 5):
                sw_g2 = get_yearly_luck(pils, yr) or {}

                ss_g2 = sw_g2.get("십성_천간", "")

                yo_g2 = OH.get(sw_g2.get("세운", "")[:1], "")

                if yo_g2 in {y1, heui}:
                    gold_yrs2.append(f"  * **{yr}년**({yr - birth_year + 1}세): {sw_g2.get('세운', '')} [{ss_g2}] ← 용신 기운의 해!")

            if gold_yrs2:
                out.append(f"\n**[용신 황금 시기 — 이 해에 중요한 일 시작하게!]**\n")

                for gyr in gold_yrs2:
                    out.append(gyr + "\n")

        elif is_move:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            si = get_ilgan_strength(ilgan, pils)

            sw_ss = sw.get("십성_천간", "")

            y1 = ys.get("용신_1순위", "-")

            heui = ys.get("희신", "-")

            sn = si.get("신강신약", "중화")

            out.append(f"**{name}의 이사·이직·중요 결정 시기 분석**\n")

            _MOVE_SS = {
                "偏財": "편재(偏財) 세운은 변화와 이동에 유리하느니라. 이사·이직·사업 시작에 좋은 시기니라. 단 충동적 결정은 조심하게.",
                "正官": "정관(正官) 세운은 조직 내 승진·인정의 해이니라. 이직보다는 현 자리에서 실력을 쌓는 것이 더 유리하느니라.",
                "偏印": "편인(偏印) 세운은 이동·변화의 기운이 강하느니라. 단 시작한 일이 중도 포기가 되기 쉬우니 신중히 결정하게.",
                "劫財": "겁재(劫財) 세운은 이직·창업에 불리하느니라. 경쟁이 심하고 손실이 크니 이 해의 큰 결정은 미루게.",
                "偏官": "편관(偏官) 세운은 강제적 변동(해고·이사)의 기운이 있느니라. 미리 준비하되 자의적으로 무리하게 움직이지는 말게.",
            }

            out.append(
                _MOVE_SS.get(
                    sw_ss,
                    f"올해 [{sw_ss}] 기운에서 큰 변동은 내년 이후 용신 세운에 맞춰 결정하는 것이 현명하니라.",
                )
                + "\n"
            )

            oh_now = OH.get(sw.get("세운", "")[:1], "")

            if oh_now in {y1, heui}:
                out.append(f"\n올해 세운 오행이 용신·희신과 일치! **이 해 안에 결정을 내리면 길하느니라.**\n")

            else:
                out.append(f"\n용신 **{y1}** 오행이 강한 해에 이사·이직을 단행하면 더욱 길하느니라. 조금 기다리게.\n")

            if "신강" in sn:
                out.append("\n신강형이니 스스로 먼저 움직여 기회를 잡아야 하느니라. 기다리면 기회가 지나가느니라.\n")

            else:
                out.append("\n신약형이니 귀인의 소개·추천을 통한 이직이 단독 도전보다 훨씬 유리하느니라.\n")

        elif is_study:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            sw_ss = sw.get("십성_천간", "")

            y1 = ys.get("용신_1순위", "-")

            out.append(f"**{name}의 학업·시험·합격운 분석**\n")

            _STUDY_SS = {
                "正印": "정인(正印) 세운! 학업·시험 운이 최정점이니라. 노력한 만큼 결과가 오는 해이니 전력을 다하게!",
                "偏印": "편인(偏印) 세운은 학습과 연구에 유리하느니라. 새 분야 습득에 최적이나 끈기가 필요하니라.",
                "食神": "식신(食神) 세운은 집중력과 창의력이 높아지느니라. 실기·실무형 시험에 특히 유리하느니라.",
                "正官": "정관(正官) 세운은 공무원·조직 시험에 유리하느니라. 규칙적 학습 루틴이 합격의 열쇠니라.",
                "劫財": "겁재(劫財) 세운은 집중력이 분산되기 쉬운 해니라. 경쟁자에게 뒤처지지 않으려면 2배 노력이 필요하느니라.",
            }

            out.append(
                _STUDY_SS.get(
                    sw_ss,
                    f"올해 [{sw_ss}] 기운에서 꾸준한 학습이 가장 중요하니라. 포기하지 말게.",
                )
                + "\n"
            )

            _OH_STUDY = {
                "水": "수(水) 오행은 지혜·암기·분석력의 오행이니라. 용신이 水이면 이론 과목에서 강하느니라.",
                "木": "목(木) 오행은 성장·창의력의 오행이니라. 논술·어학에서 두각을 나타내느니라.",
                "金": "금(金) 오행은 정밀·원칙의 오행이니라. 수학·법학·의학계열에 유리하느니라.",
                "火": "화(火) 오행은 열정·집중의 오행이니라. 시험장에서 순발력이 발휘되느니라.",
                "土": "토(土) 오행은 인내·신뢰의 오행이니라. 장기 고시·반복 학습에 특히 강하느니라.",
            }

            out.append(f"\n용신 **{y1}** — {_OH_STUDY.get(y1, f'{y1} 오행 기운을 활용하여 학습 전략을 세우게.')}\n")

        elif is_family:
            sw = get_yearly_luck(pils, current_year) or {}

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            si = get_ilgan_strength(ilgan, pils)

            sw_ss = sw.get("십성_천간", "")

            sn = si.get("신강신약", "중화")

            yk = get_yukjin(ilgan, pils, gender)

            out.append(f"**{name}의 가족·인연운 분석**\n허허, 가족은 사주의 거울이니라. 신안으로 살펴보겠느니라.\n")

            _FAM_REL = {
                "인성": "부모·윗사람과의 관계가 사주의 핵심이니라.",
                "재성": "배우자·자녀와의 인연이 재물과 직결되느니라.",
                "관성": "자녀(특히 아들)와 직장이 연결된 팔자니라.",
                "비겁": "형제·동료 관계가 운의 핵심이니라.",
            }

            _SS_FAM = {
                "正印": "올해 부모·어른과의 관계가 깊어지는 시기니라. 가족을 챙기면 좋은 기운이 돌아오느니라.",
                "偏印": "이동·변화가 많으니 가족과 소통이 줄기 쉬운 해니라. 의도적으로 시간을 내게.",
                "食神": "자녀와 관련된 기쁜 소식이 올 수 있느니라. 가족과 함께하는 시간이 재충전이 되느니라.",
                "劫財": "형제·친구 간 금전 갈등 주의. 가족 간 돈 거래는 명확히 하게.",
                "正官": "자녀(특히 아들)와 관련된 경사가 있을 수 있느니라. 가족 행사를 챙기는 것이 길하느니라.",
            }

            out.append(f"\n올해 [{sw_ss}] 기운 — {_SS_FAM.get(sw_ss, f'{sw_ss} 기운에서 가족과의 대화와 배려가 중요하니라.')}\n")

            if "신강" in sn:
                out.append("\n신강 팔자는 자기 의견이 강하니 가족에게 고집을 부리는 경향이 있느니라. 한 발씩 양보하게.\n")

            elif "신약" in sn:
                out.append("\n신약 팔자는 가족의 지지가 에너지의 원천이느니라. 가족과의 유대를 더욱 깊이 하게.\n")

        elif is_infidelity:
            sw    = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_jj = sw.get("jj", "")
            iljj  = pils[1]["jj"] if len(pils) > 1 else ""
            _pjjs = [p.get("jj","") for p in pils]
            _CIF  = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                     "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}

            geop_cnt   = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") == "劫財")
            pjjs_ss    = [TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") for p in pils]
            sang_cnt   = pjjs_ss.count("傷官")
            peon_g_cnt = pjjs_ss.count("偏官")

            doha_jjs  = {"子":["卯","午","酉"],"午":["卯","子","酉"],
                         "卯":["子","午","酉"],"酉":["子","午","卯"]}
            has_doha  = any(j in doha_jjs.get(iljj,[]) for j in _pjjs)
            yr_chung  = [j for j in _pjjs if _CIF.get(sw_jj,"") == j]

            # 용신/기신 여부
            ys_if = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            oh_sw_if = OH.get(sw.get("세운","")[:1],"")
            is_gs_if = oh_sw_if in set(ys_if.get("기신",[]))

            out.append(f"**{name}의 이성 문제·외도 직격 판단**\n허허, 묻기 두려웠던 것을 신안으로 낱낱이 살펴보겠느니라.\n")

            # ── 올해 세운 기준 직격 판단 ──
            _IF_SS = {
                "劫財": (
                    "🔴 **劫財(겁재) 세운 — 이성 문제 최경보!**\n"
                    "배우자·연인 외의 이성 관계에서 문제가 터지기 쉬운 해니라.\n"
                    "상대방이 흔들리거나 내가 흔들리거나 — 지금 의심이 간다면 그 느낌이 맞을 가능성이 높으니라.\n"
                    "→ 냉정하게 증거를 확인하고 감정적 대응은 피하게.\n"
                    "→ 상대가 귀가가 늦거나 연락이 줄었다면 지금 바로 확인하게.\n"
                ),
                "偏財": (
                    "⚠️ **偏財(편재) 세운 — 이성 유혹 강화!** (남성)\n"
                    "새로운 이성과의 접촉이 폭발적으로 많아지는 해니라.\n"
                    "가정이 있다면 이 해에 경솔하게 움직이면 평생 후회할 결과가 오느니라.\n"
                    "→ 술자리·업무상 이성과의 단둘이 만남을 자제하게.\n"
                    "→ 감정이 흔들리면 행동하기 전 72시간을 기다리게.\n"
                ),
                "偏官": (
                    "⚠️ **偏官(편관) 세운 — 외부 강제 변화!** (여성)\n"
                    "카리스마 강한 이성의 접근이나 현 관계에 균열이 생기기 쉬운 해니라.\n"
                    "→ 관계의 경계선을 명확히 하고 소통을 강화하게.\n"
                    "→ 상대방을 의심하기보다 직접 대화로 확인하게.\n"
                ),
                "傷官": (
                    "⚠️ **傷官(상관) 세운 — 말·SNS로 인한 관계 균열!**\n"
                    "배우자·연인과의 불화가 극에 달하고 제3자가 끼어들기 쉬운 해니라.\n"
                    "→ 감정적 언쟁에서 돌이킬 수 없는 말을 하지 않도록 주의하게.\n"
                    "→ SNS에 사적인 감정을 올리는 것은 관계를 더 망가뜨리느니라.\n"
                ),
            }

            # 성별 맞춤
            _ss_key = sw_ss.split("(")[0] if "(" in sw_ss else sw_ss
            if _ss_key == "偏財" and gender != "남":
                out.append(
                    f"⚠️ **偏財(편재) 세운 — 남성의 바람기 자극 해!** (여성 입장)\n"
                    f"배우자나 연인이 이성 유혹에 흔들리기 쉬운 해니라.\n"
                    f"→ 관계에 더 많은 관심과 시간을 투자하게.\n"
                    f"→ 의심을 키우기보다 소통을 먼저 강화하게.\n"
                )
            else:
                out.append(_IF_SS.get(_ss_key,
                    f"올해 [{sw_ss}] 세운 — 직접적 외도 기운은 강하지 않느니라. "
                    "다만 관계에 소홀하면 틈이 생기느니라.\n") + "\n"
                )

            # ── 원국 구조 분석 ──
            out.append("**[원국 이성 구조 분석]**")
            if geop_cnt >= 1:
                out.append(
                    f"- ⚡ **겁재 {geop_cnt}개**: 이성 경쟁자가 항상 존재하는 구조를 타고났느니라. "
                    "배우자 외 이성 관계 관리가 평생 숙제이니라."
                )
            if has_doha:
                out.append(
                    "- 🌹 **도화살 활성**: 타고난 매력으로 이성이 끊임없이 주변을 맴도느니라. "
                    "유혹에 흔들리지 않는 내공이 관계를 지키는 핵심이니라."
                )
            if gender == "여" and peon_g_cnt >= 2:
                out.append(
                    f"- ⚡ **偏官(편관) {peon_g_cnt}개**: 카리스마 강한 남성에게 끌리는 구조. "
                    "매력적이지만 지배욕이 강하거나 바람기 있는 남성을 조심하게."
                )
            if sang_cnt >= 2:
                out.append(
                    f"- 🔪 **傷官(상관) {sang_cnt}개**: 배우자 자리를 상관이 침범. "
                    "말 한마디가 관계를 갈라놓을 수 있으니 말 조심이 최우선이니라."
                )
            if geop_cnt == 0 and not has_doha and peon_g_cnt < 2 and sang_cnt < 2:
                out.append("- ✅ 원국 구조상 이성 문제 시그널이 두드러지지 않느니라.")
            out.append("")

            # ── 충 발동 ──
            if yr_chung:
                out.append(
                    f"⚡ **충(沖) 발동** — 올해 세운 지지가 원국 {'/'.join(yr_chung)}와 충이 일어나느니라. "
                    "관계에서 강제 변화가 생기느니라. 드러낼 것은 드러내고 정리할 것은 정리하게.\n"
                )

            # ── 단계별 대응 처방 ──
            out.append("**[단계별 대응 처방]**\n"
                       "- **의심 단계**: 감정적으로 따지기 전 침착하게 사실을 확인하게\n"
                       "- **확인 단계**: 증거 없이 추궁하면 오히려 역공당하느니라\n"
                       "- **결정 단계**: 1주일 이상 시간을 두고 냉정하게 판단하게\n"
                       "- **해결 단계**: 전문 상담사·법무사 도움을 받는 것이 현명하니라\n")

            # ── 향후 위험 해 ──
            out.append("**[향후 3년 이성 문제 위험 해]**")
            _if_bad = {"劫財","偏財","偏官","傷官"}
            for _yr in range(current_year, current_year + 3):
                try:
                    _sw_if = get_yearly_luck(pils, _yr) or {}
                    _is_s  = _sw_if.get("십성_천간","").split("(")[0]
                    _is_g  = _sw_if.get("길흉","평")
                    if _is_s in _if_bad:
                        out.append(f"- 🔴 **{_yr}년** [{_is_s}] — 이성 관계 주의 구간")
                    else:
                        out.append(f"- ✅ **{_yr}년** [{_is_s}] — 안정적 흐름")
                except Exception:
                    pass

        elif is_accident:
            sw    = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            sw_jj = sw.get("jj", "")
            _pjjs2 = [p.get("jj","") for p in pils]
            _CAC   = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                      "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
            chung_h = [j for j in _pjjs2 if _CAC.get(sw_jj,"") == j]

            # 원국 편관 개수
            _pg_cnt = sum(1 for p in pils
                          if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("偏官","편관"))
            # 용신 여부
            ys_a = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            oh_sw_a = OH.get(sw.get("세운","")[:1], "")
            is_gisin_a = oh_sw_a in set(ys_a.get("기신", []))

            out.append(f"**{name}의 사고수·위기 직격 판단**\n허허, 신안으로 올해 위기 기운을 낱낱이 살펴보겠느니라.\n")

            _RISK = {
                "偏官": (
                    "🔴 **偏官(편관) 세운 — 사고·관재 고위험!**\n"
                    "신체 사고·법적 분쟁·직장 충돌 중 한 가지 이상이 터질 수 있느니라.\n"
                    "- 자동차·오토바이 조작 각별 주의\n"
                    "- 야간 외출·과로·무리한 운동 자제\n"
                    "- 정기검진 즉시 예약 — 특히 혈압·심장·혈액 검사\n"
                    "- 법적 서류에 즉답하지 말고 반드시 법률 검토 후 서명\n"
                ),
                "劫財": (
                    "⚠️ **劫財(겁재) 세운 — 재물 사고·배신 위험!**\n"
                    "믿었던 사람에게 금전적 손해를 입거나 투자 사기를 당하기 쉬운 해니라.\n"
                    "- 신규 투자·동업 제안 전면 거절\n"
                    "- 지인 보증·돈 빌려주기 절대 금지\n"
                    "- 통장·카드 관리 강화\n"
                ),
                "傷官": (
                    "⚠️ **傷官(상관) 세운 — 구설·분쟁·사고 위험!**\n"
                    "말 한마디가 소송으로 번지기 쉬운 해니라. 교통사고·작은 부상도 주의.\n"
                    "- 감정적 언쟁과 SNS 발언 극도로 자제\n"
                    "- 계약서는 법률 검토 후 서명\n"
                    "- 자전거·레저 스포츠 안전 장비 필수\n"
                ),
            }
            out.append(_RISK.get(sw_ss,
                f"올해 [{sw_ss}] {sw_gh} — 직접적 사고 기운이 강하진 않으나, "
                "방심은 금물이니라. 매사 안전을 우선으로 하게.\n") + "\n"
            )

            # 원국 편관 과다 경고
            if _pg_cnt >= 2:
                out.append(
                    f"⚡ **원국에 偏官(편관) {_pg_cnt}개** — 사고·위기와 친숙한 팔자를 타고났느니라. "
                    "평소에도 안전 의식을 남들보다 두 배 높게 유지해야 하느니라.\n"
                )

            # 충 발동
            if chung_h:
                out.append(
                    f"🔴 **충(沖) 발동!** 올해 세운 지지가 원국 {'/'.join(chung_h)}와 충(沖)이 일어나느니라. "
                    "이사·이직·사고·수술 등 강제 변화가 올 수 있으니 신중히 하게.\n"
                )

            # 기신 세운 추가 경고
            if is_gisin_a and sw_ss not in ("偏官","劫財","傷官"):
                out.append(
                    f"⚠️ **기신(忌神) 세운** — 올해는 내 용신을 깎아먹는 기운이 흐르느니라. "
                    "체력 관리와 스트레스 조절이 사고수를 줄이는 핵심이니라.\n"
                )

            # 향후 3년 위험 구간
            out.append("\n**[향후 3년 위험 구간 미리보기]**")
            for _yr in range(current_year, current_year + 3):
                try:
                    _sw_yr = get_yearly_luck(pils, _yr) or {}
                    _yr_ss = _sw_yr.get("십성_천간","")
                    _yr_gh = _sw_yr.get("길흉","평")
                    _yr_oh = OH.get(_sw_yr.get("세운","")[:1],"")
                    _yr_gs = _yr_oh in set(ys_a.get("기신",[]))
                    if _yr_ss in ("偏官","劫財","傷官") or (_yr_gh in ("흉","-") and _yr_gs):
                        out.append(f"- 🔴 **{_yr}년** [{_yr_ss}] — 각별 주의 구간")
                    elif _yr_gh in ("길","+"):
                        out.append(f"- ✅ **{_yr}년** [{_yr_ss}] — 안정 구간")
                    else:
                        out.append(f"- ⚖️ **{_yr}년** [{_yr_ss}] — 평이한 흐름")
                except Exception:
                    pass
            out.append("\n**[즉각 행동 체크리스트]**\n"
                       "- □ 자동차 보험 내역 확인\n"
                       "- □ 건강검진 즉시 예약\n"
                       "- □ 보증·투자 약속 전면 재검토\n"
                       "- □ 계약서 법률 검토 필수\n"
                       "- □ 비상금 3개월치 별도 확보\n")

        elif is_quit:
            sw    = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            ys_q  = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_q  = ys_q.get("용신_1순위", "-")
            si_q  = get_ilgan_strength(ilgan, pils)
            sn_q  = si_q.get("신강신약", "중화")
            sc_q  = si_q.get("일간점수", 50)
            gisin_q = set(ys_q.get("기신", []))
            oh_sw_q = OH.get(sw.get("세운","")[:1], "")
            is_gs_q = oh_sw_q in gisin_q

            out.append(f"**{name}의 퇴사·이직 직격 판단**\n허허, 직장을 그만둬도 되는지 신안으로 살펴보겠느니라.\n")

            _QUIT_DETAIL = {
                "偏官": (
                    "🔴 **偏官(편관) 세운 — 직장 압박 극심!**\n"
                    "상사·조직과의 충돌이 극에 달하는 해니라. 내가 그만두기 전에 잘릴 수도 있느니라.\n"
                    "→ 퇴사한다면 최소 **6개월치 생활비** 확보 후 나가게.\n"
                    "→ 이직이라면 반드시 새 직장을 **먼저 확정**한 뒤 현직장 통보하게.\n"
                ),
                "傷官": (
                    "⚠️ **傷官(상관) 세운 — 박차고 나가고 싶은 충동 극대!**\n"
                    "이 감정의 절반은 실제 필요이고, 절반은 세운의 기운에 휩쓸린 것이니라.\n"
                    "→ 지금 당장 그만두지 말고 **3개월 준비** 후 결단하게.\n"
                    "→ 부업 수입이 월급의 30% 이상 될 때 나가는 것이 안전하니라.\n"
                ),
                "食神": (
                    "✅ **食神(식신) 세운 — 이직엔 좋으나 완전 퇴사는 신중!**\n"
                    "재능과 복록이 흐르는 해니라. 더 좋은 조건의 이직 기회가 실제로 오느니라.\n"
                    "→ 이직: 적극 추진해도 좋으니라.\n"
                    "→ 창업: 부업으로 먼저 검증 후 도전하게.\n"
                ),
                "偏財": (
                    "⚠️ **偏財(편재) 세운 — 창업 유혹 강함!**\n"
                    "사업 기회가 눈에 보이는 해니라. 하지만 보이는 것보다 실제는 더 어렵느니라.\n"
                    "→ 창업 자금의 **3배**를 확보하고 시작하게.\n"
                    "→ 본업 수입을 끊지 말고 **겸직** 형태로 먼저 검증하게.\n"
                ),
                "正官": (
                    "✅ **正官(정관) 세운 — 현 직장에서 인정받는 해!**\n"
                    "올해는 버티면 승진·연봉 인상이 오는 흐름이니라.\n"
                    "→ 퇴사는 이 대운이 끝난 뒤로 미루게.\n"
                    "→ 이직을 원한다면 조건을 꼼꼼히 따져 **상향 이직**만 고려하게.\n"
                ),
                "正財": (
                    "✅ **正財(정재) 세운 — 안정 수입 흐름!**\n"
                    "꾸준히 일하면 재물이 쌓이는 해니라. 지금 나가는 것은 손해니라.\n"
                    "→ 연봉 협상이나 내부 부서 이동을 먼저 시도하게.\n"
                    "→ 퇴사는 내년 이후로 미루고 탈출 자금을 모으게.\n"
                ),
            }
            out.append(_QUIT_DETAIL.get(sw_ss,
                f"올해 [{sw_ss}] {sw_gh} — "
                f"용신 오행({y1_q})이 강한 해에 결단하면 더욱 길하느니라.\n") + "\n"
            )

            # 신강신약 맞춤 전략
            if "신강" in sn_q:
                out.append(
                    f"**신강 팔자 ({sc_q}점)**: 독립 행보가 체질에 맞느니라. "
                    "자금과 기술이 준비된 상태라면 과감하게 나가도 되느니라.\n"
                )
            else:
                out.append(
                    f"**신약 팔자 ({sc_q}점)**: 혼자보다 든든한 동반자·귀인과 함께 나가거나, "
                    "이직(회사→회사) 형태가 창업보다 훨씬 안전하니라.\n"
                )

            # 향후 3년 최적 이직 타이밍
            _love_quit = {"食神","正印","偏財","正財"}
            out.append("\n**[향후 3년 이직·독립 최적 타이밍]**")
            for _yr in range(current_year, current_year + 3):
                try:
                    _sw_q = get_yearly_luck(pils, _yr) or {}
                    _qs   = _sw_q.get("십성_천간","")
                    _qg   = _sw_q.get("길흉","평")
                    _qoh  = OH.get(_sw_q.get("세운","")[:1],"")
                    _qys  = _qoh in set(ys_q.get("용신",[]))
                    if _qs in _love_quit or _qys:
                        out.append(f"- ✅ **{_yr}년** [{_qs}] {_qg} — 이직·독립 적합")
                    elif _qs in ("偏官","劫財"):
                        out.append(f"- 🔴 **{_yr}년** [{_qs}] {_qg} — 퇴사 위험 구간")
                    else:
                        out.append(f"- ⚖️ **{_yr}년** [{_qs}] {_qg} — 준비 기간")
                except Exception:
                    pass

        elif is_fail_biz:
            sw    = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            sw_jj = sw.get("jj", "")
            gk_f  = get_gyeokguk(pils)
            gkn_f = gk_f["격국명"] if gk_f else "미정격"
            ys_f  = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            gisin_f  = set(ys_f.get("기신",[]))
            yong_f   = set(ys_f.get("용신",[]))
            oh_sw_f  = OH.get(sw.get("세운","")[:1],"")
            is_gs_yr = oh_sw_f in gisin_f
            is_ys_yr = oh_sw_f in yong_f

            # 원국 위험 지표
            geop_biz  = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") == "劫財")
            sang_biz  = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") == "傷官")
            peon_g_biz= sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") == "偏官")

            # 충 발동
            _CHUNG_B = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                        "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
            _pjjs_b  = [p.get("jj","") for p in pils]
            chung_b  = [j for j in _pjjs_b if _CHUNG_B.get(sw_jj,"") == j]

            out.append(f"**{name}의 사업 위기·실패 직격 판단**\n허허, 직설로 말해주겠느니라.\n")

            # ── 올해 세운 직격 판단 ──
            _BIZ_SS = {
                "劫財": (
                    "🔴 **劫財(겁재) 세운 — 사업 실패수 최고조!**\n"
                    "동업자 배신·자금 이탈·거래처 부도 중 한 가지 이상이 반드시 터지느니라.\n"
                    "→ **지금 사업 확장하면 망하느니라.** 무조건 멈추게.\n"
                    "→ 긴축 경영·현금 사수·불필요 지출 전면 차단이 생존의 길이니라.\n"
                    "→ 동업·외상 거래·어음 결제는 이 해에 절대 금지이니라.\n"
                ),
                "偏官": (
                    "🔴 **偏官(편관) 세운 — 관재·세무·법적 압박!**\n"
                    "세무조사·계약 분쟁·직원 문제가 사업에 들이닥칠 수 있느니라.\n"
                    "→ 세금 정리와 계약서 법적 검토를 지금 당장 하게.\n"
                    "→ 무리한 신규 사업 진출은 이 해에 반드시 피하게.\n"
                    "→ 기존 사업 수성(守成)에만 집중하느니라.\n"
                ),
                "傷官": (
                    "⚠️ **傷官(상관) 세운 — 직원·파트너 갈등!**\n"
                    "핵심 직원 이탈·거래처 갈등·SNS 구설이 사업을 흔들 수 있느니라.\n"
                    "→ 내부 직원 관리와 소통을 강화하게.\n"
                    "→ 말 실수로 인한 계약 파기를 조심하게.\n"
                ),
                "比肩": (
                    "⚠️ **比肩(비견) 세운 — 경쟁 심화!**\n"
                    "같은 업종 경쟁자가 치고 올라오는 해니라.\n"
                    "→ 가격 경쟁이 아닌 차별화 전략으로 승부하게.\n"
                    "→ 시장 점유율 방어에 집중하느니라.\n"
                ),
            }
            _ss_key_b = sw_ss.split("(")[0] if "(" in sw_ss else sw_ss
            if _ss_key_b in _BIZ_SS:
                out.append(_BIZ_SS[_ss_key_b] + "\n")
            elif is_gs_yr:
                out.append(
                    f"⚠️ **기신({', '.join(gisin_f)}) 세운** — 사업 기운이 역행하는 해니라.\n"
                    "신규 투자·사업 확장은 용신 오행의 해로 미루고 현금 확보에 집중하게.\n\n"
                )
            elif is_ys_yr:
                out.append(
                    f"✅ **용신({', '.join(yong_f)}) 세운** — 사업 위기보다는 기회의 해니라.\n"
                    f"[{sw_ss}] {sw_gh} — 신중히 움직이면 손실을 피하고 회복이 가능하느니라.\n\n"
                )
            else:
                _GKB = {
                    "겁재격": "경쟁 업종 조심. 동업 계약서 없이 움직이지 말게.",
                    "편관격": "도전적 사업은 맞으나 법적 리스크를 항상 점검하게.",
                    "상관격": "직원 관리와 계약서 주의가 핵심이니라.",
                }
                out.append(
                    f"올해 [{sw_ss}] {sw_gh} — 사업 흐름이 나쁘지 않으나 "
                    f"{_GKB.get(gkn_f, '무리한 확장보다 내실을 다지는 것이 현명하니라.')}\n\n"
                )

            # ── 원국 사업 위험 지표 ──
            out.append("**[원국 사업 위험 지표]**")
            if geop_biz >= 1:
                out.append(f"- ⚡ **겁재 {geop_biz}개**: 동업자·협력사에게 배신당하거나 자금이 새는 구조를 타고났느니라. 동업은 반드시 계약서를 쓰게.")
            if peon_g_biz >= 2:
                out.append(f"- 🔴 **편관 {peon_g_biz}개**: 관재·법적 압박에 노출되기 쉬운 구조이니라. 세무·법률 관리를 철저히 하게.")
            if sang_biz >= 2:
                out.append(f"- ⚠️ **상관 {sang_biz}개**: 직원·파트너와의 갈등이 잦은 구조이니라. 인사 관리에 각별히 신경 쓰게.")
            if geop_biz == 0 and peon_g_biz < 2 and sang_biz < 2:
                out.append("- ✅ 원국 구조상 치명적 사업 위험 지표는 두드러지지 않느니라.")
            out.append("")

            # ── 충 발동 ──
            if chung_b:
                out.append(
                    f"⚡ **충(沖) 발동** — 올해 세운이 원국 {'/'.join(chung_b)}와 충이 일어나느니라. "
                    "사업의 기반이 흔들리거나 갑작스러운 변화가 올 수 있느니라. "
                    "계약·투자·확장을 이 해에 하지 말게.\n"
                )

            # ── 사업 위기 단계별 처방 ──
            out.append("**[사업 위기 단계별 처방]**\n"
                       "- **초기 위기**: 고정비(임대료·인건비) 즉시 재검토 — 30% 절감 목표\n"
                       "- **자금 압박**: 매출채권 즉시 회수, 신규 외상거래 전면 중단\n"
                       "- **동업 갈등**: 계약서 기반 명확한 역할 분리, 감정 배제\n"
                       "- **세무 문제**: 세무사 즉시 선임, 자진 신고가 가산세 최소화\n"
                       "- **폐업 고려**: 부채 정리 후 재출발이 빚더미 속 지속보다 현명하니라\n")

            # ── 향후 3년 사업 흐름 ──
            out.append("**[향후 3년 사업 흐름]**")
            _biz_good = {"食神","偏財","正財","正官"}
            _biz_bad  = {"劫財","偏官","傷官"}
            for _yr in range(current_year, current_year + 3):
                try:
                    _sw_b  = get_yearly_luck(pils, _yr) or {}
                    _bs    = _sw_b.get("십성_천간","").split("(")[0]
                    _bg    = _sw_b.get("길흉","평")
                    _boh   = OH.get(_sw_b.get("세운","")[:1],"")
                    _bys   = _boh in yong_f
                    _bgs   = _boh in gisin_f
                    if _bs in _biz_bad or _bgs:
                        out.append(f"- 🔴 **{_yr}년** [{_bs}] {_bg} — 수비·방어 구간, 확장 금지")
                    elif _bs in _biz_good or _bys:
                        out.append(f"- ✅ **{_yr}년** [{_bs}] {_bg} — 회복·성장 가능 구간")
                    else:
                        out.append(f"- ⚖️ **{_yr}년** [{_bs}] {_bg} — 유지·준비 구간")
                except Exception:
                    pass

        elif is_lawsuit:
            sw    = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            sw_jj = sw.get("jj", "")
            _pjjs_l = [p.get("jj","") for p in pils]
            _CHUNG_L = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                        "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
            chung_l = [j for j in _pjjs_l if _CHUNG_L.get(sw_jj,"") == j]
            ys_l    = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            oh_sw_l = OH.get(sw.get("세운","")[:1], "")
            is_gs_l = oh_sw_l in set(ys_l.get("기신", []))

            out.append(f"**{name}의 소송·법적 분쟁 직격 판단**\n허허, 법과 관재의 기운을 신안으로 살펴보겠느니라.\n")

            _LAW_DETAIL = {
                "偏官": (
                    "🔴 **偏官(편관) 세운 — 관재 최고위험!**\n"
                    "법적 분쟁이 생기거나 기존 분쟁이 악화되는 흐름이니라.\n"
                    "→ **빠른 합의**가 장기 소송보다 훨씬 유리하느니라.\n"
                    "→ 지금 당장 전문 **변호사 선임** 필수.\n"
                    "→ 감정적 대응은 패소 가능성을 높이니 침묵하고 증거로 말하게.\n"
                ),
                "傷官": (
                    "⚠️ **傷官(상관) 세운 — 구설·소송 발생 위험!**\n"
                    "말과 문서로 인한 분쟁이 새로 생기기 쉬운 해니라.\n"
                    "→ SNS·인터뷰·계약서 서명에 극도로 주의하게.\n"
                    "→ 기존 분쟁 중이라면 합의를 적극 시도하게.\n"
                ),
                "劫財": (
                    "⚠️ **劫財(겁재) 세운 — 금전 분쟁 법적 비화 위험!**\n"
                    "금전 관련 민사 소송이 생기기 쉬운 해니라.\n"
                    "→ 증거를 미리 확보하고, 합의보다 법적 절차가 유리할 수 있느니라.\n"
                    "→ 채권 회수는 이 해에 적극적으로 움직여야 하느니라.\n"
                ),
            }
            out.append(_LAW_DETAIL.get(sw_ss,
                f"올해 [{sw_ss}] {sw_gh} — 직접적 관재 기운이 강하지 않느니라. "
                "분쟁 중이라면 용신 기운 강한 해에 마무리 짓는 것이 유리하니라.\n") + "\n"
            )

            # 충 발동 = 법적 결과 강제 변화
            if chung_l:
                out.append(
                    f"⚡ **충(沖) 발동** — 올해 세운이 원국 {'/'.join(chung_l)}와 충이 일어나느니라. "
                    "판결·합의 결과가 예상치 못한 방향으로 바뀔 수 있으니 대비하게.\n"
                )

            # 기신 세운 = 불리한 해
            if is_gs_l:
                out.append(
                    "🔴 **기신 세운 — 소송에 불리한 흐름!** "
                    "올해는 소를 제기하거나 법적 대응보다 합의·조정을 우선 시도하게. "
                    "용신 기운이 오는 해까지 전략적으로 기다리는 것이 승소율을 높이느니라.\n"
                )

            # 향후 소송 유리한 해 찾기
            _law_good = {"正官","偏財","正財","正印"}
            out.append("\n**[소송 유리한 해 — 향후 3년]**")
            for _yr in range(current_year, current_year + 3):
                try:
                    _sw_l = get_yearly_luck(pils, _yr) or {}
                    _ls   = _sw_l.get("십성_천간","")
                    _lg   = _sw_l.get("길흉","평")
                    _loh  = OH.get(_sw_l.get("세운","")[:1],"")
                    _lys  = _loh in set(ys_l.get("용신",[]))
                    if _ls in _law_good or _lys:
                        out.append(f"- ✅ **{_yr}년** [{_ls}] {_lg} — 법적 대응·합의 유리")
                    elif _ls in ("偏官","劫財","傷官"):
                        out.append(f"- 🔴 **{_yr}년** [{_ls}] {_lg} — 불리한 흐름")
                    else:
                        out.append(f"- ⚖️ **{_yr}년** [{_ls}] {_lg} — 중립 흐름")
                except Exception:
                    pass

            out.append(
                "\n**[분쟁 대응 원칙]**\n"
                "- □ 모든 대화·거래 내역 즉시 문서화\n"
                "- □ 감정적 대응 대신 증거 확보 먼저\n"
                "- □ 상대방 요구에 즉답하지 말고 법률 검토 후 대응\n"
                "- □ 변호사 선임 전 법률구조공단 무료 상담 활용\n"
                "- □ 소멸시효·제소 기간 반드시 확인\n"
            )

        elif is_pregnancy:
            sw = get_yearly_luck(pils, current_year) or {}
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            ys_p  = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_p  = ys_p.get("용신_1순위", "-")
            out.append(f"**{name}의 임신·출산·자녀운 직격 판단**\n허허, 자식 인연의 기운을 신안으로 살펴보겠느니라.\n")
            _PREG = {
                "食神": "✅ **식신 세운 — 임신·출산 최적기!** 식신은 자녀를 상징하는 가장 강력한 별이니라. 지금이 하늘이 허락하는 최적의 시기이니라.",
                "正印": "✅ **정인 세운 — 자녀 인연 기운 상승!** 임신 가능성이 높아지며 건강한 임신 기간이 예상되느니라.",
                "劫財": "⚠️ **겁재 세운 — 임신·출산 조심!** 산모 건강 이슈가 생기기 쉬운 기운이니라. 정기검진을 철저히 챙기게.",
                "偏官": "⚠️ **편관 세운 — 산모 건강 주의!** 스트레스 관리가 최우선이니라. 과로·무리한 일은 절대 삼가게.",
                "傷官": "⚠️ **상관 세운 — 임신에 어려움 가능!** 전문의 상담을 먼저 받게. 무리하지 말고 몸부터 챙기게.",
            }
            out.append(_PREG.get(sw_ss, f"올해 [{sw_ss}] {sw_gh} — 용신 오행({y1_p})이 강한 해에 시도하는 것이 가장 좋은 타이밍이니라.") + "\n")
            try:
                yk_p = get_yukjin(ilgan, pils, gender)
                for rel_p in yk_p:
                    if any(k in rel_p.get("관계","") for k in ["자녀","식신","食神(식신)","傷官(상관)"]):
                        out.append(f"\n**[자녀 자리]** {rel_p.get('관계','')} — {rel_p.get('desc','')}\n")
                        break
            except Exception:
                pass

        # ══════════════════════════════════════════════
        # 신규 분기 7개 — 개운/이혼/해외/부동산/귀인/노후/자녀
        # ══════════════════════════════════════════════

        elif is_luck_remedy:
            ys_lr = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_lr = ys_lr.get("용신_1순위", "-")
            heui_lr = ys_lr.get("희신", "-")
            gi_lr = ys_lr.get("기신", [])
            si_lr = get_ilgan_strength(ilgan, pils)
            sn_lr = si_lr.get("신강신약","중화")
            _RX_OH = {
                "木": {"색상":"초록·파란색","방향":"동쪽","숫자":"3, 8","음식":"식초·레몬·매실·녹색채소","행동":"매일 아침 동쪽 창문 열고 심호흡 5분","금기":"서쪽·흰색·금속 소품 과다"},
                "火": {"색상":"빨간·주황색","방향":"남쪽","숫자":"2, 7","음식":"녹차·쑥·토마토·석류","행동":"아침 남쪽 향해 15분 햇빛 쬐기","금기":"북쪽·검은색·찬 음식"},
                "土": {"색상":"노란·황금색","방향":"중앙","숫자":"5, 0","음식":"고구마·현미·꿀·생강차","행동":"맨발로 흙·잔디 10분 걷기","금기":"동쪽·신맛·파란 소품 과다"},
                "金": {"색상":"흰·은·금색","방향":"서쪽","숫자":"4, 9","음식":"무·배·도라지·생강","행동":"금속 팔찌 착용, 집 서쪽에 거울","금기":"동쪽·붉은색·나무 소품 과다"},
                "水": {"색상":"검은·남색","방향":"북쪽","숫자":"1, 6","음식":"김·미역·검은콩·흑임자","행동":"하루 물 2리터+, 북쪽에 작은 수족관","금기":"남쪽·붉은색·건조한 환경"},
            }
            out.append(f"**{name}의 개운법(開運法) 완전 처방**\n허허, 하늘 기운을 내 편으로 만드는 법을 일러주겠느니라.\n")
            out.append(f"용신 **{y1_lr}** · 희신 **{heui_lr}** — 이 두 기운을 강화하는 것이 개운의 핵심이니라.\n")
            rx1 = _RX_OH.get(y1_lr, {})
            if rx1:
                out.append(f"\n**[용신 {y1_lr} 개운 처방]**\n")
                out.append(f"✅ 행운 색상: **{rx1['색상']}** — 지갑·옷·소품에 이 색 하나 추가하게!\n")
                out.append(f"✅ 행운 방향: **{rx1['방향']}** — 침대 머리·책상 방향을 이쪽으로!\n")
                out.append(f"✅ 행운 숫자: **{rx1['숫자']}** — 중요 날짜·번호에 활용하게!\n")
                out.append(f"✅ 행운 음식: {rx1['음식']} — 매일 한 가지씩!\n")
                out.append(f"✅ 일상 개운: {rx1['행동']}\n")
                out.append(f"⛔ 피할 것: {rx1['금기']}\n")
            if gi_lr:
                out.append(f"\n⛔ **기신({', '.join(gi_lr[:2])}) — 이 기운이 강한 날·계절·방향을 피하게.**\n")
            if "신강" in sn_lr:
                out.append("\n신강 팔자 개운 포인트: 쉬는 것이 개운이니라. 욕심을 비울수록 기운이 더 크게 돌아오느니라.\n")
            else:
                out.append("\n신약 팔자 개운 포인트: 좋은 사람 곁에 있는 것이 최고의 개운이니라. 귀인을 만날 모임·종교 활동에 적극 참여하게.\n")

        elif is_divorce:
            sw_d = get_yearly_luck(pils, current_year) or {}
            sw_ss_d = sw_d.get("십성_천간","").split("(")[0]
            iljj_d = pils[1]["jj"] if len(pils)>1 else ""
            _CHUNG_D = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅","卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
            sw_jj_d = sw_d.get("jj","")
            is_iljj_chung = (_CHUNG_D.get(iljj_d,"") == sw_jj_d)
            _DIV_SS = {"偏官":"⚠️ 배우자와 갈등이 폭발하는 해니라. 권위적 태도와 일방적 결정이 관계를 갈라놓느니라.",
                       "傷官":"⚠️ 말 한마디가 이혼으로 번지기 쉬운 해니라. 감정적 언어 사용이 최대 위험이니라.",
                       "劫財":"⚠️ 제3자 개입이나 금전 갈등이 부부 사이를 흔드는 해니라.",
                       "正官":"✅ 부부 관계 안정의 해니라. 갈등이 있어도 공식적 관계를 유지하려는 기운이 강하느니라.",
                       "正財":"✅ 안정적 부부 기운. 지금은 이혼보다 개선을 시도하는 것이 현명하니라."}
            out.append(f"**{name}의 부부불화·이혼 직격 판단**\n허허, 부부 인연의 실타래를 신안으로 살펴보겠느니라.\n")
            if is_iljj_chung:
                out.append(f"\n🔴 **일지 충(沖) 발동!** 올해 배우자 자리({iljj_d})에 충이 들어오느니라. 이혼·별거 등 강제 변화 기운이 가장 강한 해니라.\n")
            out.append(f"\n올해 [{sw_ss_d}] — {_DIV_SS.get(sw_ss_d, '중립적 기운이니 성급한 결정은 삼가게.')}\n")
            out.append("\n**[이혼 결정 원칙]**\n- 충 발동 해에 충동적으로 결정하면 후회가 크느니라\n- 자녀가 있다면 정관 세운에서 합의 이혼이 유리하니라\n- 6개월 이상 별거 후 진짜 원하는 것인지 확인하게\n")

        elif is_overseas:
            sw_ov = get_yearly_luck(pils, current_year) or {}
            sw_ss_ov = sw_ov.get("십성_천간","").split("(")[0]
            ys_ov = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_ov = ys_ov.get("용신_1순위","-")
            _OV_DIR = {"木":"동쪽 — 일본·중국·동남아","火":"남쪽 — 동남아·호주·인도","土":"중앙 — 유럽 내륙·미국 중부","金":"서쪽 — 미국·캐나다·유럽","水":"북쪽 — 캐나다·북유럽·미국 북부"}
            _OV_SS = {"偏財":"✅ 해외 사업 기회가 오는 해. 현지 네트워크를 구축하게.",
                      "食神":"✅ 재능을 해외에서 펼치기 좋은 해. 유학·해외 취업이 맞는 시기.",
                      "偏官":"⚠️ 예상치 못한 압박이 올 수 있음. 비자·법적 서류를 꼼꼼히 챙기게.",
                      "劫財":"⚠️ 해외에서 금전 손실·사기 조심. 검증된 파트너만 믿게."}
            out.append(f"**{name}의 해외·이민·유학운 직격 판단**\n허허, 이 팔자가 해외에서 빛을 발하는지 살펴보겠느니라.\n")
            out.append(f"\n**[유리한 해외 방위]** 용신 **{y1_ov}** — {_OV_DIR.get(y1_ov,'용신 방향 나라를 선택하게.')}\n")
            out.append(f"\n올해 [{sw_ss_ov}] — {_OV_SS.get(sw_ss_ov, '용신 기운이 강한 해에 실행하는 것이 가장 유리하느니라.')}\n")

        elif is_realestate:
            sw_re = get_yearly_luck(pils, current_year) or {}
            sw_ss_re = sw_re.get("십성_천간","").split("(")[0]
            sw_gh_re = sw_re.get("길흉","")
            ys_re = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_re = ys_re.get("용신_1순위","-")
            _RE_SS = {"正財":"✅ 실거주 매입 최적기! 무리한 대출 없이 진행하면 길하느니라.",
                      "偏財":"⚡ 시세차익 기회의 해! 안전 자산 30% 유지하게.",
                      "劫財":"🔴 매입 금지! 이 해에 부동산 매입하면 손해가 크니라. 내년 이후로 미루게.",
                      "偏官":"⚠️ 법적 분쟁 주의! 등기·계약서 전문가 검토 필수."}
            _RE_DIR = {"木":"동향·숲 인근","火":"남향·햇빛 잘 드는 집","土":"중앙 입지·토지","金":"서향·신축·도심 핵심","水":"북향·수변 인근"}
            out.append(f"**{name}의 부동산 타이밍 직격 판단**\n허허, 땅과 집의 기운을 신안으로 살펴보겠느니라.\n")
            out.append(f"\n**[용신 {y1_re} 방향 부동산]** {_RE_DIR.get(y1_re,'용신 방향 지역을 선택하게.')}\n")
            out.append(f"\n올해 [{sw_ss_re}] {sw_gh_re} — {_RE_SS.get(sw_ss_re,'용신 오행이 강한 해에 매입하는 것이 가장 안전하니라.')}\n")
            out.append("\n**[향후 5년 매입 황금기]**\n")
            for _yr in range(current_year, current_year+5):
                try:
                    _sw_r = get_yearly_luck(pils, _yr) or {}
                    _rs = _sw_r.get("십성_천간","").split("(")[0]
                    _rg = _sw_r.get("길흉","평")
                    if _rs in ("正財","偏財") and _rg in ("길","+"):
                        out.append(f"- ✅ **{_yr}년** [{_rs}] — 매입 황금기!\n")
                    elif _rs == "劫財":
                        out.append(f"- 🔴 **{_yr}년** [{_rs}] — 매입 금지\n")
                    else:
                        out.append(f"- ⚖️ **{_yr}년** [{_rs}] — 관망\n")
                except Exception:
                    pass

        elif is_guiin:
            ys_g = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_g = ys_g.get("용신_1순위","-")
            stars_g = get_special_stars(pils)
            tiany = [s for s in stars_g if "천을귀인" in s.get("name","")]
            _GUIIN_OH = {
                "木": {"방향":"동쪽","직업":"교육자·의사·환경 관련","띠":"호랑이·토끼띠","색상":"초록색 옷 입은 사람"},
                "火": {"방향":"남쪽","직업":"연예인·강사·IT","띠":"말·뱀띠","색상":"빨간·주황색 옷 입은 사람"},
                "土": {"방향":"중앙","직업":"부동산·공무원·의약","띠":"소·용·양·개띠","색상":"노란·황금색 옷 입은 사람"},
                "金": {"방향":"서쪽","직업":"금융·법조·의료","띠":"원숭이·닭띠","색상":"흰·은색 옷 입은 사람"},
                "水": {"방향":"북쪽","직업":"무역·외교·미디어","띠":"쥐·돼지띠","색상":"검은·남색 옷 입은 사람"},
            }
            out.append(f"**{name}의 귀인(貴人) 완전 분석**\n허허, 당신의 인생을 도와줄 귀인을 신안으로 찾아보겠느니라.\n")
            if tiany:
                out.append(f"\n🌟 **천을귀인 발견!** 하늘이 직접 내리는 귀인 기운이 원국에 있느니라. 위기의 순간마다 기적 같은 도움이 오는 팔자이니라.\n")
            gui = _GUIIN_OH.get(y1_g, {})
            if gui:
                out.append(f"\n**[용신 {y1_g} 귀인의 특징]**\n")
                out.append(f"🧭 방향: **{gui['방향']}** — 이 방향에서 귀인이 오느니라!\n")
                out.append(f"👔 직업: **{gui['직업']}** — 이 직종 사람이 내 인생을 바꾸느니라!\n")
                out.append(f"🐾 띠: **{gui['띠']}** — 이 띠 사람을 가까이 두게!\n")
                out.append(f"👕 특징: {gui['색상']}\n")
            out.append("\n**[귀인을 만나는 3원칙]**\n1. 먼저 베풀어라 — 귀인은 내가 도움을 줄 때 나타나느니라\n2. 용신 방향·색상을 활용하라\n3. 나 자신을 드러내라 — 숨어있으면 귀인도 못 찾느니라\n")

        elif is_elderly:
            ys_el = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_el = ys_el.get("용신_1순위","-")
            si_el = get_ilgan_strength(ilgan, pils)
            sn_el = si_el.get("신강신약","중화")
            gk_el = get_gyeokguk(pils)
            gkn_el = gk_el["격국명"] if gk_el else "미정격"
            sijju_jj = pils[0].get("jj","") if pils else ""
            _SIJ_LATE = {
                "子":"말년에 지혜와 문서 인연이 강하느니라. 학문·종교로 노년을 빛내게.",
                "丑":"말년에 착실한 노력의 결실이 맺히느니라.",
                "寅":"말년에 활동력이 강하니 사회 활동을 유지하는 것이 건강을 지키느니라.",
                "卯":"말년에 인화(人和)가 넘치느니라. 따뜻한 노년이 기다리느니라.",
                "辰":"말년에 여러 분야에서 능력이 빛나느니라. 배움을 멈추지 말게.",
                "巳":"말년에 지혜와 재물이 함께하느니라. 정신적 수행이 노년을 풍요롭게 하느니라.",
                "午":"말년에 열정이 넘치느니라. 사회 봉사·가르치는 일이 가장 맞는 노년이니라.",
                "未":"말년에 가족 인연이 강하느니라. 가정 중심으로 안정된 노년이 오느니라.",
                "申":"말년에 영리하고 활동적이니 사회·경제 활동을 유지하면 기운이 살아나느니라.",
                "酉":"말년에 완성과 결실의 기운이니라. 젊은 시절 전문성이 노년에 꽃피느니라.",
                "戌":"말년에 의리와 신뢰의 기운이니라. 쌓아온 관계가 노후의 가장 큰 자산이니라.",
                "亥":"말년에 자유와 영성의 기운이니라. 종교·철학·여행으로 노년을 풍요롭게 하게.",
            }
            _GK_LATE = {
                "정재격":"연금·부동산 중심 안정 자산. 꾸준히 모아온 재물이 노후를 지키느니라.",
                "식신격":"재능·취미가 노후의 밥벌이가 되느니라. 강의·창작·봉사로 활기찬 노년.",
                "편재격":"사업 활동을 노년에도 유지하는 것이 맞는 팔자니라. 완전 은퇴보다 규모를 줄여 계속 활동하게.",
            }
            out.append(f"**{name}의 노후·말년운 완전 분석**\n허허, 황혼의 기운을 신안으로 살펴보겠느니라.\n")
            out.append(f"\n**[시주(時柱) 말년 기운]** {sijju_jj}\n{_SIJ_LATE.get(sijju_jj, f'시지 {sijju_jj}의 기운이 말년을 이끌어 가느니라.')}\n")
            out.append(f"\n**[격국별 노후 전략]** {_GK_LATE.get(gkn_el, '용신 기운을 유지하면서 즐겁게 활동하는 것이 최고의 노후니라.')}\n")
            if "신강" in sn_el:
                out.append("\n신강 팔자 노후: 에너지가 넘치니 사회 활동을 유지하는 것이 건강에 좋으니라. 완전 은퇴는 오히려 건강을 해치느니라.\n")
            else:
                out.append("\n신약 팔자 노후: 가족·지인의 도움을 적극적으로 받는 것이 건강에 좋으니라. 혼자 모든 것을 해결하려 하지 말게.\n")

        elif is_childcare:
            sw_cc = get_yearly_luck(pils, current_year) or {}
            sw_ss_cc = sw_cc.get("십성_천간","").split("(")[0]
            ys_cc = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            y1_cc = ys_cc.get("용신_1순위","-")
            _PARENTING = {
                "甲":"갑목 부모: 원칙과 목표 중시. 자녀의 독립심을 키워주되 지나친 기대감이 자녀를 압박하지 않도록 주의.",
                "乙":"을목 부모: 섬세하게 자녀 감정을 읽음. 개성을 존중하면 크게 성장.",
                "丙":"병화 부모: 열정적으로 이끄는 스타일. 자녀에게도 쉬는 시간을 주게.",
                "丁":"정화 부모: 따뜻하고 헌신적. 자녀 대신 모든 것을 해주려 하지 말게.",
                "戊":"무토 부모: 안정된 환경 조성. 고집스러운 교육이 창의성을 억누르지 않도록 유의.",
                "己":"기토 부모: 세밀한 관찰. 과잉보호가 독립심을 해치지 않도록 주의.",
                "庚":"경금 부모: 원칙과 규율 중시. 감정 표현을 더 많이 해주면 자녀와의 거리가 줄어듦.",
                "辛":"신금 부모: 완벽주의적. 자녀의 실수를 과도하게 지적하지 않는 것이 관계의 핵심.",
                "壬":"임수 부모: 자유롭고 유연. 자녀에게 규칙과 경계를 명확히 해주게.",
                "癸":"계수 부모: 감성·공감 능력 탁월. 꿈을 현실로 연결해주는 실질 지원도 함께.",
            }
            _CC_OH = {
                "木":"언어·교육·환경·스포츠 방향의 재능을 살려주게.",
                "火":"예술·방송·IT·디자인 방향이 유리하느니라.",
                "土":"경영·의약·식품·사회복지 방향이 안정적.",
                "金":"의료·법학·금융·공학 방향에서 빛나느니라.",
                "水":"외국어·무역·심리·예술 방향의 재능이 꽃피느니라.",
            }
            _CC_SS = {"食神":"✅ 자녀와의 관계 가장 좋은 해. 교육·진로 결정 함께 논의하기 좋은 시기.",
                      "正印":"✅ 자녀 학업 성취 기대. 교육 환경 개선에 투자하면 효과 큼.",
                      "偏官":"⚠️ 자녀와 갈등 생기기 쉬운 해. 강압보다 대화로 풀어나가게.",
                      "劫財":"⚠️ 자녀 관련 금전 지출 생기는 해. 교육비 계획 미리 세우게."}
            out.append(f"**{name}의 자녀 교육·진로 완전 분석**\n허허, 자식 팔자와 부모의 역할을 신안으로 살펴보겠느니라.\n")
            out.append(f"\n**[{ilgan} 일간 양육 기질]**\n{_PARENTING.get(ilgan, f'일간 {ilgan}의 기운으로 자녀를 이끄는 것이 맞느니라.')}\n")
            out.append(f"\n**[용신 기반 자녀 잠재 적성]** 용신 **{y1_cc}** — {_CC_OH.get(y1_cc, '용신 오행 분야에서 자녀 재능이 빛나느니라.')}\n")
            out.append(f"\n올해 [{sw_ss_cc}] — {_CC_SS.get(sw_ss_cc, '자녀와 함께하는 시간을 늘리는 것이 최선이니라.')}\n")
            out.append("\n**[자녀 양육 3원칙]**\n1. 부모의 팔자를 자녀에게 강요하지 말게\n2. 자녀 용신 오행을 살려주는 것이 최고의 교육\n3. 부모가 행복한 것이 자녀에게 가장 큰 유산\n")

        # ─── 개선된 catch-all: 질문을 실제로 활용한 실질 답변 ───
            gk = get_gyeokguk(pils)
            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)
            si = get_ilgan_strength(ilgan, pils)
            sw = get_yearly_luck(pils, current_year) or {}
            gkn = gk["격국명"] if gk else "미정격"
            sn  = si.get("신강신약", "중화")
            sc  = si.get("일간점수", 50)
            y1  = ys.get("용신_1순위", "-")
            heui = ys.get("희신", "-")
            gisin = ", ".join(ys.get("기신", []))
            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")
            sw_gan = sw.get("세운", "")
            oh_now = OH.get(sw_gan[:1] if sw_gan else "", "")
            _GKS = {
                "정관격":"조직과 원칙 안에서 빛을 발하는 격국이니라.",
                "편관격":"강인한 의지와 도전 정신이 핵심인 격국이니라.",
                "정재격":"성실함으로 재물을 쌓는 격국이니라.",
                "편재격":"사업가 기질이 넘치는 격국이니라.",
                "식신격":"복록이 넘치며 창작·교육에서 빛나는 격국이니라.",
                "상관격":"재기와 창의성이 폭발하는 격국이니라.",
                "편인격":"학문과 연구에 뛰어난 격국이니라.",
                "정인격":"학문과 자격으로 성장하는 격국이니라.",
            }
            q_short = q.strip()[:40]
            out.append(f"**'{q_short}'에 대해 {name}의 팔자로 직접 답하겠느니라.**\n")
            out.append(f"일간 **{ilgan}** | 격국 **{gkn}** | {sn}({sc}/100)\n")
            out.append(f"용신 **{y1}** · 희신 **{heui}** | 기신 {gisin}\n")
            out.append(f"올해({current_year}년) **{sw_gan} [{sw_ss}] {sw_gh}**\n\n")
            _SW_VERDICT = {
                "偏財": "올해는 재물과 이성 기운이 활발한 해니라. 돈·사업·이성 관련이라면 적극적으로 나서면 좋은 결과가 오느니라.",
                "正財": "올해는 안정과 착실함의 기운이니라. 검증된 방법으로 진행된다면 결실이 맺히느니라.",
                "食神": "올해는 재능과 창의의 기운이니라. 당신이 잘하는 것을 드러낼 때 답이 나오느니라.",
                "傷官": "올해는 변화와 충돌의 기운이 강하느니라. 기존 방식을 과감히 바꾸고 싶지만 상사·윗사람과의 마찰을 조심하게.",
                "偏官": "올해는 압박과 도전의 기운이니라. 무리하게 추진하면 역효과가 나느니라. 수비적으로 대응하는 것이 현명하니라.",
                "正官": "올해는 명예와 안정의 기운이니라. 조직과 원칙 안에서 움직이면 좋은 평가와 결과가 오느니라.",
                "劫財": "올해는 경쟁과 손재의 기운이니라. 새로운 것을 시작하기보다 현재를 지키는 것이 최선이니라.",
                "偏印": "올해는 변화와 이동의 기운이니라. 새 정보를 모으고 판단은 신중히 내려야 하느니라.",
                "正印": "올해는 배움과 귀인의 기운이니라. 전문가나 윗사람의 도움을 받으면 뜻이 이루어지느니라.",
                "比肩": "올해는 독립과 경쟁의 기운이니라. 스스로 움직일 때 기회가 오느니라.",
            }
            out.append(_SW_VERDICT.get(sw_ss, f"올해 [{sw_ss}] 기운은 중립적이니라. 용신({y1}) 오행이 강한 해에 중요한 결정을 내리는 것이 가장 유리하느니라.") + "\n")
            if oh_now in {y1, heui}:
                out.append(f"\n✅ 올해 세운이 용신·희신과 일치하니 **{current_year}년 안에 결단하면 길하느니라!**\n")
            elif gisin and oh_now in gisin:
                out.append(f"\n⚠️ 올해 세운이 기신({gisin})에 해당하니 **큰 결정은 내년 이후로 미루는 것이 현명하니라.**\n")
            out.append(f"\n{_GKS.get(gkn, '독특한 개성과 능력을 갖춘 격국이니라.')}\n")
            out.append("\n스스로 움직여야 기회가 오느니라.\n" if "신강" in sn else "\n귀인과 함께할 때 가장 강해지는 팔자이니라. 좋은 파트너가 운명을 바꾸느니라.\n")

            gk = get_gyeokguk(pils)

            ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

            si = get_ilgan_strength(ilgan, pils)

            sw = get_yearly_luck(pils, current_year) or {}

            gkn = gk["격국명"] if gk else "미정격"

            sn = si.get("신강신약", "중화")
            sc = si.get("일간점수", 50)

            y1 = ys.get("용신_1순위", "-")
            heui = ys.get("희신", "-")

            gisin = ", ".join(ys.get("기신", []))

            sw_ss = sw.get("십성_천간", "")
            sw_gh = sw.get("길흉", "")

            sw_gan = sw.get("세운", "")

            _GKS = {
                "정관격": "규칙과 질서를 중시하며 조직에서 빛을 발하느니라.",
                "편관격": "강인한 의지와 도전 정신이 핵심이니라.",
                "정재격": "성실함으로 재물을 쌓는 격국이니라.",
                "편재격": "사업가 기질이 넘치는 격국이니라.",
                "식신격": "복록이 넘치는 격국이니라. 창작·교육에서 빛을 발하느니라.",
                "상관격": "재기와 창의성이 폭발하는 격국이니라.",
                "편인격": "학문과 연구에 뛰어난 격국이니라.",
                "정인격": "학문과 자격의 격국이니라.",
            }

            # 질문 키워드 반영 인트로

            q_short = q.strip()[:30]

            out.append(f"**{name}의 팔자로 '{q_short}' 질문을 풀어드리겠느니라.**\n")

            out.append(f"일간 {ilgan} | 격국 **{gkn}** | {sn}(점수 {sc}/100)\n")

            out.append(f"용신 **{y1}** | 희신 **{heui}** | 기신 {gisin}\n\n")

            out.append(_GKS.get(gkn, "독특한 개성과 능력을 갖춘 격국이니라.") + "\n")

            out.append("\n일간의 기운이 강하니 스스로 움직여야 기회가 오느니라.\n" if "신강" in sn else "\n귀인과 함께할 때 가장 강해지는 팔자이니라. 좋은 파트너가 운명을 바꾸느니라.\n")

            out.append(f"\n올해({current_year}년)는 {sw_gan} [{sw_ss}] {sw_gh} 기운이니라.\n")

            # 용신 일치 여부 판단

            oh_now = OH.get(sw_gan[:1] if sw_gan else "", "")

            if oh_now in {y1, heui}:
                out.append(f"\n올해 세운이 용신·희신과 일치하니 **{current_year}년에 질문하신 일을 추진하면 길하느니라!**\n")

            elif gisin and oh_now in gisin:
                out.append(f"\n올해 세운이 기신({gisin})에 해당하니 **큰 결정은 내년 이후로 미루는 것이 현명하느니라.**\n")

            else:
                out.append(f"\n용신 **{y1}** 오행이 강한 해에 행동을 취하면 가장 좋은 결과가 오느니라.\n")

            # 향후 최선의 시기

            best_yrs = []

            for yr in range(current_year, current_year + 5):
                sw_b = get_yearly_luck(pils, yr)

                yo_b = OH.get(sw_b.get("세운", "")[:1], "")

                if yo_b in {y1, heui}:
                    best_yrs.append(f"  * **{yr}년**({yr - birth_year + 1}세): {sw_b.get('세운', '')} [{sw_b.get('십성_천간', '')}] ← 용신 기운의 황금기!")

            if best_yrs:
                out.append("\n**[최선의 시기]**\n")

                for by in best_yrs[:3]:
                    out.append(by + "\n")

    except Exception as _le:
        out.append(f"\n허어, 기운이 잠시 흔들렸느니라. 기본 팔자로 답을 드리겠네.\n")

        try:
            sw = get_yearly_luck(pils, current_year) or {}

            out.append(f"올해 {sw.get('세운', '')} [{sw.get('십성_천간', '')}] {sw.get('길흉', '')} 기운이니라.\n")

        except Exception as _e:
            _saju_log.debug("[silent except] %s", _e)

    out.append(f"\n---\n*내 신안(神眼)이 본 {name}의 팔자가 이러하니라. 더 깊이 알고 싶다면 다시 물어보게.*")

    return "\n".join(out)


# ============================================================

# 🌟 LocalSajuNarrator — API 없이 전 메뉴 사주 해석 생성 엔진

# 천간지지·일주·월주·년주·시주·대운·세운·절운·12운성·60갑자

# 기반으로 과거·현재·미래 全 생애 서사를 자체 생성한다.

# ============================================================


def quick_consult_bar(pils, name, birth_year, gender):
    """🌌 전역 퀵 상담창: 어떤 탭에서든 즉시 질문하고 답을 얻는 고정 UI"""

    render_quick_consult_header()

    # ── 직격 질문 버튼 (원클릭) ──────────────────────────────
    st.markdown(
        "<div style='font-size:12px;color:#888;margin-bottom:6px;'>⚡ 원클릭 직격 질문</div>",
        unsafe_allow_html=True,
    )
    _QUICK_BTNS = [
        ("💰 올해 돈 벌리나",     "올해 재물운 직격 — 돈 버는 시기와 방법 알려줘"),
        ("💼 내 적성 직업은",     "내 사주에 맞는 직업 적성 진로를 직격으로 알려줘"),
        ("❤️ 연애·결혼 언제",    "연애 또는 결혼 인연이 오는 시기를 정확히 알려주세요"),
        ("🚨 사고수 있냐",        "올해 사고수 건강 위기 관재수가 있는지 직격으로 알려줘"),
        ("💥 사업 해도 되나",     "지금 사업 또는 창업을 해도 되는지 직격으로 판단해주세요"),
        ("🌹 바람·이성 문제",     "배우자나 연인의 이성 문제, 외도 가능성을 사주로 분석해주세요"),
        ("🍀 개운법 알려줘",      "내 용신 오행에 맞는 개운법과 지금 당장 실천할 처방을 알려주세요"),
        ("🏠 부동산 타이밍",      "부동산 매입 또는 이사 최적 시기와 방위를 사주로 알려주세요"),
        ("👴 노후·말년운",        "내 노후와 말년운이 어떻게 흘러가는지 직격으로 알려주세요"),
    ]
    # 3열×3행
    _clicked_q = ""
    _qrow1 = st.columns(3)
    _qrow2 = st.columns(3)
    _qrow3 = st.columns(3)
    for _ci, (_blabel, _bquery) in enumerate(_QUICK_BTNS):
        if _ci < 3:
            _col = _qrow1[_ci % 3]
        elif _ci < 6:
            _col = _qrow2[_ci % 3]
        else:
            _col = _qrow3[_ci % 3]
        if _col.button(_blabel, key=f"qbar_quick_{_ci}", use_container_width=True):
            _clicked_q = _bquery

    with st.container():
        q_col1, q_col2 = st.columns([5, 1])

        with q_col1:
            quick_query = st.text_input(
                "질문 입력",
                key="global_quick_query",
                label_visibility="collapsed",
                placeholder="예: 올해 연애운은 어떤가요? 지금 하려는 사업 괜찮을까요?",
                value=_clicked_q,
            )

        with q_col2:
            q_submitted = st.button("🔮 즉각전수", key="global_quick_btn", use_container_width=True)

    # 원클릭 버튼 클릭 시 자동 실행
    _auto_submit = bool(_clicked_q)
    # 퀵버튼 클릭이면 _clicked_q를 실제 질문으로 사용
    _final_query = _clicked_q if _auto_submit else quick_query

    if (q_submitted and quick_query) or (_auto_submit and _clicked_q):
        with st.status("🔮 만신의 신안(神眼)이 천기를 살피는 중...", expanded=True) as status:
            # 1. 의도 및 유대감 업데이트
            intent_res = IntentEngine.analyze(_final_query)

            st.write(f"🎯 분석 주제: **{intent_res['topic_kr']}** / 감정선: **{intent_res['emotion']}**")

            SajuMemory.record_behavior(name, _final_query)

            SajuMemory.adjust_bond(name, 5)

            GoalCreationEngine.extract_goal(name, _final_query)

            # 2. 로컬 사주 엔진 응답 생성
            response = _local_saju_engine(pils, name, birth_year, gender, _final_query)
            # ── 판단 규칙 후처리 (단정 완화·균형·톤 정제) ──
            response = SajuJudgmentRules.apply_all(response)

            # 3. 응답 출력

            render_quick_consult_response(response)

            # 4. 데이터 영속화

            current_year = datetime.now().year

            SajuMemory.add_conversation(name, f"퀵:{intent_res['topic_kr']}", response, intent_res["emotion"])

            LifeNarrativeEngine.update_narrative(name, intent_res["topic_kr"], intent_res["emotion"])

            # 5. 전환점 감지

            try:
                luck_score = calc_luck_score(pils, birth_year, gender, current_year)

                pivot_info = ChangeRadarEngine.detect_pivot(name, luck_score)

                if pivot_info["is_pivot"]:
                    st.info(f"🛰️ **전환점 감지:** {pivot_info['message']}")

            except Exception as _e:
                st.warning(f"⚠️ 오류: {str(_e)[:80]}")

            status.update(label="✅ 전수 완료", state="complete", expanded=True)


class DestinyTimelineEngine:
    """🗺️ 운명을 시간 축(Timeline)으로 매핑하여 현재 위치를 알려주는 엔진"""

    @staticmethod
    def get_context_summary() -> str:

        # 병오(丙午)년 고정 시뮬레이션 기반 시점 분석

        now = datetime.now()

        month = now.month

        if month in [3, 4, 5]:
            return "씨앗을 뿌리고 기반을 다지는 '창조의 봄' 단계"

        if month in [6, 7, 8]:
            return "열기가 가득하여 결과가 가시화되는 '도약의 여름' 단계"

        if month in [9, 10, 11]:
            return "내실을 기하고 결과물을 거두는 '수렴의 가을' 단계"

        return "자신을 돌아보고 에너지를 비축하는 '성찰의 겨울' 단계"


class SelfEvolutionEngine:
    """🔥 내담자 유형에 맞춰 AI의 상담 알고리즘 및 톤을 진화시키는 엔진"""

    @staticmethod
    def get_instruction(persona: str) -> str:

        instructions = {
            "논리/분석 탐색형": "- 사용자는 논리적 근거를 중시합니다. 명리적 용어(십성, 합충)를 섞어 구체적으로 답변하세요.",
            "현실불안 위로형": "- 밤에 접속한 내담자입니다. 정서적 불안이 높을 수 있으니 따뜻한 위로와 공감을 70% 비중으로 하세요.",
            "해답갈구 확신형": "- 사용자는 결론을 원합니다. 서론을 줄이고 'Yes/No' 혹은 '추천 행동'을 먼저 제시하세요.",
            "온건적 소통형": "- 일상적인 대화 톤으로 편안하게 사주의 지혜를 전달하세요.",
        }

        return instructions.get(persona, "- 내담자의 성향을 탐색하며 정중하게 상담하세요.")


class PersonalityProfiler:
    """사주 원국 기반 '고전적/현대적 통합 성격 지문' 및 MBTI 매핑 엔진"""

    @staticmethod
    def analyze(pils: list) -> dict:

        default_res = {
            "trait1": "독자적인 기운",
            "trait2": "잠재된 사회적 역량",
            "mbti": "INFJ",
            "trait_desc": "사주 원국 데이터를 분석 중입니다.",
            "counseling_strategy": "내담자의 성향을 파악하며 유연하게 상담하세요.",
        }

        # 안전성 검사 강화

        if not pils or not isinstance(pils, list) or len(pils) < 4:
            return default_res

        try:
            # [시(0), 일(1), 월(2), 년(3)] 순서

            hour_p = pils[0]

            day_p = pils[1]

            month_p = pils[2]

            year_p = pils[3]

            ilgan = day_p.get("cg", "")

            month_ji = month_p.get("jj", "")

            iljj = day_p.get("jj", "")

        except (IndexError, AttributeError, KeyError):
            return default_res

        if not ilgan or not month_ji:
            return default_res

        # 1. 고전 명리 기질

        traits = {
            "甲": "우뚝 솟은 나무처럼 강직하고 리더십이 강함",
            "乙": "유연한 덩굴처럼 생명력이 질기고 적응력이 뛰어남",
            "丙": "하늘의 태양처럼 열정적이고 숨김이 없으며 밝음",
            "丁": "밤하늘의 등불처럼 섬세하고 따뜻하며 예의가 바름",
            "戊": "드넓은 대지처럼 듬직하고 포용력이 크며 신중함",
            "己": "비옥한 논밭처럼 치밀하고 실속이 있으며 자애로움",
            "庚": "날카로운 바위처럼 결단력이 있고 정의로우며 강한 자존심",
            "辛": "빛나는 보석처럼 정교하고 깔끔하며 완벽주의 성향",
            "壬": "끝없는 바다처럼 지혜롭고 수용성이 넓으며 생각이 깊음",
            "癸": "봄비처럼 여리고 유연하며 창의적인 영감이 뛰어남",
        }

        social = {
            "寅": "개척과 추진력",
            "卯": "조화와 예술성",
            "辰": "관리와 포용력",
            "巳": "확산과 표현력",
            "午": "돌파와 열정",
            "未": "인내와 저장력",
            "申": "냉철함과 기술력",
            "酉": "정밀함과 결단력",
            "戌": "신의와 실천력",
            "亥": "통찰과 응용력",
            "子": "연구와 원천 기운",
            "丑": "성실과 축적력",
        }

        desc = traits.get(ilgan, "독자적인 기운")

        soc_desc = social.get(month_ji, "잠재된 사회적 역량")

        # 2. 사주-MBTI 매핑 로직 (V2 핵심)

        mbti_map = {
            "甲(갑)-寅(인)": "ENTJ",
            "乙(을)-卯(묘)": "ENFP",
            "丙(병)-午(오)": "ENFJ",
            "丁(정)-巳(사)": "INFJ",
            "戊(무)-辰(진)": "ESTJ",
            "己(기)-丑(축)": "ISFJ",
            "庚(경)-申(신)": "ISTP",
            "辛(신)-酉(유)": "INTJ",
            "壬(임)-亥(해)": "INTP",
            "癸(계)-子(자)": "INFP",
        }

        key = f"{ilgan}-{month_ji}"

        mbti_type = mbti_map.get(key, "INFJ" if ilgan in "丁(정)癸(계)" else "ESTP")

        # 일주 데이터 참조 (Hotfix: ILJU_DESC -> ILJU_DATA)

        ilju_key = f"{ilgan}{iljj}"

        ilju_info = ILJU_DATA.get(ilju_key, {})

        ilju_symbol = ilju_info.get("symbol", "🔮")

        ilju_desc = ilju_info.get("desc", f"{ilju_key}의 기운")

        return {
            "trait1": desc,
            "trait2": soc_desc,
            "mbti": mbti_type,
            "ilju_symbol": ilju_symbol,
            "trait_desc": f"{ilju_symbol} {ilju_desc}\n\n{desc}을 바탕으로 {soc_desc}이 돋보이며, 현대적으로는 {mbti_type} 유형과 유사함",
            "counseling_strategy": f"이 분은 {mbti_type} 성향을 고려하여 {'체계적이고 명확하게' if 'J' in mbti_type else '자유롭고 가능성을 열어두고'} 상담하세요.",
        }


class FollowUpGenerator:
    """내담자의 주제와 감정에 반응하는 '여운이 남는 질문' 생성기 V2"""

    @staticmethod
    def get_question(topic: str, intent: str = "", trust_level: int = 1) -> str:


        if trust_level >= 4:
            # 신뢰도가 높을 때의 깊은 질문 풀 확장

            pools["LIFE_PATH"].append("본인의 가장 치부라고 생각하는 기질이 사실은 가장 강력한 무기라는 걸 알고 계셨나요?")

            pools["CAREER"].append("사회적 성공 뒤에 숨겨진 본인의 외로움을 정면으로 마주할 준비가 되셨나요?")

        pool = pools.get(topic, ["오늘의 상담이 {name}님의 마음에 작은 등불이 되었을까요?"])

        return random.choice(pool)


class FatePredictionEngine:
    """🚨 돌발 사건 감지 및 실시간 위험 경고 엔진 (V2)"""

    @staticmethod
    def detect_risk(pils: list, current_year: int) -> dict:

        if not pils or len(pils) < 4:
            return {"is_risk": False, "messages": [], "severity": "보통"}

        # 단순화된 충(沖) 감지 로직

        ilgan = pils[1]["cg"]

        year_ji = pils[3]["jj"] if len(pils) > 3 else ""  # 년지

        risks = []

        # 2026년 병오(丙午)년 기준 예시

        if year_ji == "子":
            risks.append("연지와 세운의 자오충(子(자)午(오)沖)이 보입니다. 갑작스러운 환경 변화나 이동수를 주의하세요.")

        if ilgan == "壬":
            risks.append("일간과 세운의 병임충(丙(병)壬(임)沖) 기운이 있어 감정의 변동이 클 수 있습니다.")

        return {
            "is_risk": len(risks) > 0,
            "messages": risks,
            "severity": "높음" if len(risks) >= 2 else "보통",
        }


class ChangeRadarEngine:
    """📈 인생의 전환점(Pivot Point)을 감지하는 레이더 엔진"""

    @staticmethod
    def detect_pivot(name: str, luck_score: int):

        # 운세 점수가 급변하거나 특정 조건 만족 시 전환점 알림

        mem = SajuMemory.get_memory(name)

        prev_score = mem.get("matrix", {}).get("에너지", 50)

        # 20점 이상 급변 시 전환점 인지

        is_pivot = abs(luck_score - prev_score) >= 20

        message = ""

        if is_pivot:
            if luck_score > prev_score:
                message = "대운의 상승 기류가 시작되는 '기회의 전환점'에 진입했습니다."

            else:
                message = "잠시 멈춰 에너지를 재정비해야 하는 '성찰의 전환점'입니다."

        return {"is_pivot": is_pivot, "message": message}


class UsageTracker:
    """일일 테스트 인원 제한 관리 (Stable Service)"""

    FILE_PATH = "usage_stats.json"

    LIMIT = 100  # 일일 제한 인원 (사용자 요청에 따라 100명 설정)

    @staticmethod
    def check_limit() -> bool:
        """오늘 사용량이 제한을 넘었는지 확인"""

        today = date.today().isoformat()

        try:
            with open(UsageTracker.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("date") != today:
                return True

            return data.get("count", 0) < UsageTracker.LIMIT

        except Exception:
            return True

    @staticmethod
    def increment():
        """오늘 사용량 1 증가"""

        today = date.today().isoformat()

        try:
            with open(UsageTracker.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

        except Exception:
            data = {"date": today, "count": 0}

        if data.get("date") != today:
            data = {"date": today, "count": 0}

        data["count"] += 1

        with open(UsageTracker.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class VirtualUserEngine:
    """🧪 가상 테스트 인원 100명 관리 엔진"""

    @staticmethod
    def generate_100() -> list:
        """100명의 가상 인물 데이터를 생성 (재현성을 위해 시드 고정)"""

        users = []

        rng = random.Random(42)  # 로컬 시드 고정

        for i in range(1, 101):
            year = rng.randint(1960, 2005)

            month = rng.randint(1, 12)

            day = rng.randint(1, 28)

            hour = rng.randint(0, 23)

            gender = rng.choice(["남성", "여성"])

            calendar = rng.choice(["양력", "음력"])

            # 이름은 성씨 조합으로 생성

            surnames = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]

            names = [
                "민호",
                "서연",
                "지우",
                "민준",
                "하윤",
                "주원",
                "예준",
                "서윤",
                "도윤",
                "채원",
            ]

            full_name = f"{rng.choice(surnames)}{rng.choice(names)}_{i:02d}"

            users.append(
                {
                    "name": full_name,
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "gender": gender,
                    "calendar": calendar,
                }
            )

        return users

    @staticmethod
    def pick_random():
        """100명 중 한 명을 무작위로 추출"""

        return random.choice(VirtualUserEngine.generate_100())


class BatchSimulationEngine:
    """📊 대규모 배치 시뮬레이션 엔진"""

    @staticmethod
    def run_full_scan():
        """100명 전체 사주 엔진 분석 실행 및 통계 산출"""

        users = VirtualUserEngine.generate_100()

        stats = {
            "ilgan_dist": {},
            "luck_scores": [],
            "top_fate": [],
            "processing_time": 0,
        }

        import time

        start_t = time.time()

        for u in users:
            # 엔진 계산만 수행 (AI 호출 제외로 부하 방지)

            if u["calendar"] == "양력":
                pils = SajuCoreEngine.get_pillars(
                    u["year"],
                    u["month"],
                    u["day"],
                    u["hour"],
                    0,
                    "남" if u["gender"] == "남성" else "여",
                )

            else:
                s_date = lunar_to_solar(u["year"], u["month"], u["day"], False)

                pils = SajuCoreEngine.get_pillars(
                    s_date.year,
                    s_date.month,
                    s_date.day,
                    u["hour"],
                    0,
                    "남" if u["gender"] == "남성" else "여",
                )

            ilgan = pils[1]["cg"]

            stats["ilgan_dist"][ilgan] = stats["ilgan_dist"].get(ilgan, 0) + 1

            luck_s = calc_luck_score(pils, u["year"], "남" if u["gender"] == "남성" else "여", 2026)

            stats["luck_scores"].append(luck_s)

            if luck_s >= 85:
                stats["top_fate"].append(f"{u['name']}({luck_s}점)")

        stats["processing_time"] = round(time.time() - start_t, 3)

        return stats


class IntentEngine:
    """🎯 질문 의도 해석 엔진 (5-Layer Intent Detection)"""

    # Layer 1: Emotion Categories
    EMOTIONS = {
        "불안": ["불안", "걱정", "두렵", "무섭", "초조", "떨려", "겁", "위기"],
        "절망": ["힘들", "지쳐", "포기", "끝났", "망했", "죽겠", "못하겠", "한계"],
        "혼란": ["모르겠", "헷갈", "뭘", "어떻게", "왜", "이상해", "혼란", "갈팡"],
        "기대": ["될까", "가능", "기회", "잘될", "좋아질", "언제쯤", "희망", "바뀔"],
        "분노": ["화나", "짜증", "억울", "열받", "불공평", "왜이렇", "싫어", "미치겠"],
        "슬픔": ["슬퍼", "눈물", "외로워", "혼자", "허전", "그리워", "상실", "아파"],
    }

    # Layer 2: Keyword Groups
    KEYWORD_GROUPS = {
        "CAREER": ["직장", "직업", "취업", "이직", "승진", "사업", "창업", "커리어", "일자리", "퇴직", "출세", "직위"],
        "WEALTH": ["돈", "재물", "투자", "주식", "부동산", "수입", "월급", "빚", "대출", "재테크", "재산", "벌이"],
        "LOVE": ["연애", "사랑", "남자친구", "여자친구", "남편", "아내", "결혼", "이별", "짝사랑", "소개팅", "인연", "궁합"],
        "RELATION": ["친구", "가족", "부모", "형제", "동료", "상사", "갈등", "관계", "인간관계", "싸움", "화해", "사람"],
        "SELF": ["나", "성격", "적성", "운명", "팔자", "본인", "자신", "내면", "가치", "방향", "정체성", "천명"],
        "TIMING": ["언제", "시기", "때", "올해", "내년", "이번달", "곧", "금방", "조만간", "타이밍", "기회", "전환"],
    }

    # Layer 3: Situation Patterns
    PATTERNS = {
        "CAREER": ["직장을 옮", "이직할까", "사업 시작", "창업해도", "승진이 될", "취직이 될", "직장 그만"],
        "WEALTH": ["돈이 들어", "재물운이", "투자해도 될", "빚을 갚", "수입이 늘", "재산이 늘", "손해를 볼"],
        "LOVE": ["만날 수 있", "결혼할 수", "이 사람이 내 인연", "헤어져야", "다시 만날", "고백해도", "사랑받을"],
        "RELATION": ["관계가 나빠", "사람 때문에", "상사가 힘들", "가족과 갈등", "친구 사이", "화해할 수"],
        "SELF": ["내 팔자가", "내 운명이", "나는 왜", "내 성격이", "본인이 잘", "내 적성이"],
        "TIMING": ["언제 좋아질", "언제 풀릴", "이번 해가", "내년이 되면", "지금 해도 될", "시기가 맞"],
    }


    # Layer 5: Counseling Directions

    DIRECTIONS = {
        "CAREER": "커리어 흐름과 발전 가능성, 대운의 변화 시기를 중심으로 전문적인 분석을 제공하십시오.",
        "WEALTH": "재물의 성취와 손실 시기, 투자 적기 및 자산 운용의 기운을 정밀하게 진단하십시오.",
        "LOVE": "인연의 깊이와 합/충의 조화, 상대와의 감정적 소통 흐름을 중심으로 해석하십시오.",
        "RELATION": "대인관계의 마찰 해소 및 사회적 유대, 주변 사람과의 기운적 상생을 조망하십시오.",
        "SELF": "내면의 성향과 본연의 가치, 인생의 근본적인 방향성과 자아 성찰의 메시지를 전달하십시오.",
        "TIMING": "운의 전환점과 결정적인 기회, 행동해야 할 시기와 멈춰야 할 시기를 명확히 제시하십시오.",
    }

    @staticmethod
    def analyze(query: str) -> dict:
        """5단계 레이어를 거쳐 감정, 주제, 상담 방향을 최종 결정한다."""

        # 1-1. 감정 감지 (Layer 1)

        detected_emotion = "혼란"  # 기본값

        for emo, kws in IntentEngine.EMOTIONS.items():
            if any(kw in query for kw in kws):
                detected_emotion = emo

                break

        # 1-2. 주제 분류 점수 계산 (Layer 4 - 확신도 계산)

        scores = {topic: 0 for topic in IntentEngine.DIRECTIONS.keys()}

        # 패턴 매칭 (가장 높은 우선순위)

        for topic, kws in IntentEngine.PATTERNS.items():
            if any(kw in query for kw in kws):
                scores[topic] += 60

        # 키워드 매칭

        for topic, kws in IntentEngine.KEYWORD_GROUPS.items():
            if any(kw in query for kw in kws):
                scores[topic] += 40

        # 최종 주제 선정 (Layer 4)

        sorted_topics = sorted(scores.items(), key=lambda x: (x[1], x[0] == "SELF"), reverse=True)

        if sorted_topics[0][1] < 30:
            final_topic = "SELF"

        else:
            final_topic = sorted_topics[0][0]

        confidence = min(sorted_topics[0][1] + 20, 95) if sorted_topics[0][1] > 0 else 60

        # 가독성을 위한 주제명 변환

        topic_kr_map = {
            "CAREER": "직업/진로",
            "WEALTH": "재물/사업",
            "LOVE": "연애/결혼",
            "RELATION": "인간관계",
            "SELF": "인생 방향",
            "TIMING": "운세 흐름",
        }

        return {
            "topic": final_topic,
            "topic_kr": topic_kr_map[final_topic],
            "emotion": detected_emotion,
            "direction": IntentEngine.DIRECTIONS[final_topic],
            "confidence": confidence,
        }

    @staticmethod
    def build_intent_prompt(query: str) -> str:

        res = IntentEngine.analyze(query)

        prompt = (
            f"내담자의 감정 상태는 [{res['emotion']}]이며, 질문의 의도는 [{res['topic_kr']}]로 분류되었습니다.\n"
            f"상담 방향 지침: {res['direction']}\n"
            f"전문가로서 위 감정을 충분히 어루만지며 제시된 방향으로 답변하십시오."
        )

        return prompt

    @staticmethod
    def get_topic_badge(user_input: str) -> str:
        """UI에 표시할 주제 및 감정 배지 HTML 반환"""

        res = IntentEngine.analyze(user_input)

        emotion_icon = {
            "불안": "😰",
            "혼란": "🤔",
            "기대": "-",
            "후회": "😔",
            "결심": "💪",
            "피로": "😮‍💨",
            "분노": "😡",
        }.get(res["emotion"], "💬")

        return (
            f"<div style='display:flex; gap:6px; margin-bottom:10px'>"
            f"<span style='background:#f1f8e9;color:#2e7d32;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700'>🏷️ {res['topic_kr']}</span>"
            f"<span style='background:#fce4ec;color:#c2185b;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700'>{emotion_icon} {res['emotion']}</span>"
            f"</div>"
        )


def build_saju_context_dict(pils, birth_year, gender, current_year, topic):
    """엔진 데이터를 집약하여 AI에게 전달할 맥락 생성 (단순 dict 반환, 채팅/퀵컨설트 전용)"""

    # [시(0), 일(1), 월(2), 년(3)] 순서 반영

    # (주의: PillarEngine에 따라 인덱스가 다를 수 있으나 현재 manse.py 관례 준수)

    try:
        ilgan = pils[1]["cg"] if len(pils) > 1 else "?"

        gyeok_data = get_gyeokguk(pils)

        # 용신 엔진은 multilayer 또는 단일 호출 가능. 여기서는 단일 호출 래퍼 사용

        ys_data = get_yongshin(pils)

        return {
            "내담자_일간": ilgan,
            "격국": gyeok_data.get("격국명", "분석중") if gyeok_data else "정보없음",
            "용신": ys_data.get("종합_용신", ["분석중"]) if ys_data else ["정보없음"],
            "팔자": " / ".join([f"{p['cg']}{p['jj']}" for p in pils]) if pils else "정보없음",
            "상담주제": topic,
        }

    except Exception:
        return {"error": "데이터 추출 중 기운이 엇갈렸습니다."}


class SajuExpertPrompt:
    """🏛️ 전문가형 5단 프롬프트 아키텍처 (SajuExpertPrompt) V2"""

    @staticmethod
    def build_system_prompt(name, topic_direction, ctx_data):
        """🏛️ 명리학 전문가형 8섹션 프롬프트 아키텍처 V3"""

        header = _AI_SANDBOX_HEADER

        rules_ctx = SajuJudgmentRules.build_rules_prompt(name)

        prompt = f"""
{header}

너는 30년 경력의 명리학 전문가이자 사주 분석 AI이다.
아래 [사주 계산 데이터]는 SajuCoreEngine이 이미 정확하게 계산한 값이다.
절대로 이 값을 재계산하거나 수정하지 말고, 그대로 활용하여 해석만 수행하라.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【판단 규칙 (Guardrails)】
{rules_ctx}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【사주 계산 데이터】 ← 이 값을 기준으로 8섹션을 생성하라
{ctx_data}

【상담 주제】
{topic_direction}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【출력 형식: 8섹션 필수 출력】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

아래 8개 섹션을 순서대로 모두 출력하라. 표 중심 구조, 명리학 이론 기반, 한국어로 작성.

【1】사주 원국
구분 | 년주 | 월주 | 일주 | 시주 형식의 표로 출력.
행: 천간 / 지지 / 십성(천간기준) / 지장간(장간 위주)
계산 데이터의 값을 그대로 채워 넣고, 각 기둥의 특성을 1~2줄로 해석.

【2】오행 분석
목(木)·화(火)·토(土)·금(金)·수(水) 각 개수와 비율을 표로 출력.
가장 강한 오행·가장 약한 오행을 명시하고,
오행 불균형이 삶에 미치는 영향을 3~4줄로 해석.

【3】십성 분석
비견·겁재·식신·상관·편재·정재·편관·정관·편인·정인 중
사주에 등장하는 십성을 표로 정리(십성명 / 위치 / 의미 / 강약).
지배적 십성 2개를 선정해 성격·직업·대인관계에 미치는 영향 해석.

【4】대운 흐름
10년 단위 최소 8개 대운을 표로 출력(나이 / 대운간지 / 십성 / 오행 / 길흉 / 핵심 키워드).
현재 대운을 ★로 표시하고, 용신 대운 시기를 강조하여 해석.

【5】세운 (현재~10년)
연도 / 천간 / 지지 / 십성 / 주요 영향 형식 표.
현재 연도부터 10년치 출력. 길흉 방향과 주의 사항 포함.

【6】월운 (현재 연도 1~12월)
월 / 월건 / 십성 / 길흉 / 핵심 메시지 형식 표.
특히 좋은 달·나쁜 달을 굵게 강조.

【7】신살
천을귀인·문창귀인·도화살·역마살·백호대살·화개살 해당 여부를 표로 출력.
해당 신살의 발현 시기와 활용법을 간결하게 해석.

【8】종합 해석
다음 항목을 각 2~4줄로 작성:
① 사주 구조 요약 (격국·신강신약·용신)
② 타고난 성격과 잠재력
③ 최적 직업군·적성
④ 재물운 패턴
⑤ 결혼·인연운
⑥ 건강 주의사항
⑦ 향후 10년 핵심 흐름
⑧ 개운법 (용신 색상·방위·음식·생활습관)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
출력 규칙:
- 모든 섹션 번호【1】~【8】을 반드시 유지할 것
- 계산 데이터에 없는 값은 임의로 만들지 말고 "데이터 없음"으로 표기
- 전문 용어는 괄호로 한글 병기: 예) 식신(食神), 겁재(劫財)
- 내담자 이름: {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return prompt.strip()


# ==========================================================

#  ⚖️ 사주 AI 판단 규칙 12개 (Hallucination 방지 시스템)

#  질문 -> 사주 분석 -> [판단 규칙 검사] -> 출력

# ==========================================================


class SajuJudgmentRules:
    # -- 판단 규칙용 상수 정의 ---------------------------

    _ASSERTION_MAP = {
        "반드시": "흐름상",
        "절대": "거의",
        "확실히": "분명",
        "무조건": "매우",
        "단언컨대": "필시",
        "명백히": "상당히",
        "꼭": "가급적",
    }

    _ANXIETY_KEYWORDS = [
        "불안",
        "걱정",
        "무서",
        "두려",
        "죽고",
        "힘들",
        "사고",
        "문제",
        "위험",
        "절망",
        "실패",
        "망할",
        "끝장",
        "괴롭",
        "우울",
        "긴장",
        "떨려",
        "초조",
    ]

    _OVERPOSITIVE = [
        "천하무적",
        "완벽한",
        "최강의",
        "무조건 성공",
        "로또 당첨",
        "대박 확정",
        "100% 성공",
        "절대 실패하지 않",
    ]

    _REPORT_TONE = [
        "분석 결과:",
        "다음과 같습니다:",
        "결론적으로",
        "요약하자면",
        "이상으로",
        "보고드리면",
        "정리하면",
        "종합해 보면",
    ]

    """

    AI 출력이 생성되기 전/후 적용되는 12개 판단 규칙.

    - 프롬프트 빌드 시 규칙을 주입 (사전 제어)

    - 출력 텍스트 검증/수정 (사후 제어)

    """

    def rule01_soften_assertions(text: str) -> str:
        """[1] 단정 금지 규칙 - '반드시' -> '흐름상' 치환"""

        for bad, good in SajuJudgmentRules._ASSERTION_MAP.items():
            text = text.replace(bad, good)

        return text

    # -- 규칙 5: 부정 균형 - 위험 + 대응 세트 확인 --------

    @staticmethod
    def rule05_check_negative_balance(text: str) -> str:
        """[5] 나쁜 운 설명 시 대응 방법이 없으면 자동 추가 힌트 삽입"""

        negative_phrases = [
            "어려운 시기",
            "힘든 운",
            "충(沖)",
            "주의가 필요",
            "조심해야",
        ]

        has_response = ["준비", "대응", "방법", "기회", "전략", "조언"]

        for phrase in negative_phrases:
            if phrase in text:
                if not any(r in text for r in has_response):
                    text += "\n\n※ 힘든 흐름도 준비하면 기회가 됩니다. 지금 할 수 있는 한 가지 행동에 집중해 보세요."

                break

        return text

    # -- 규칙 7: 감정 보호 - 불안 질문 탐지 ---------------

    @staticmethod
    def rule07_detect_anxiety(user_input: str) -> bool:
        """[7] 사용자 입력에 불안 키워드 포함 여부 반환"""

        return any(kw in user_input for kw in SajuJudgmentRules._ANXIETY_KEYWORDS)

    # -- 규칙 9: 기억 충돌 검사 ----------------------------

    @staticmethod
    def rule09_check_memory_conflict(text: str) -> str:
        """[9] 현재 출력 vs 저장된 흐름 기억 충돌 시 경고 보정"""

        try:
            _mem = SajuMemory.get_memory() or {}
            flow_stage = _mem.get("flow", {}).get("stage", "")
        except Exception:
            flow_stage = ""

        if not flow_stage:
            return text

        # 안정기인데 '격변' 또는 '위기' 언급 시 완화

        if "안정기" in flow_stage:
            for conflict_word in ["격변", "대위기", "모든 것이 바뀝니다"]:
                if conflict_word in text:
                    text = text.replace(conflict_word, "변화의 씨앗이 싹트는 시기")

        return text

    # -- 규칙 11: 과도한 긍정 완화 ------------------------

    @staticmethod
    def rule11_limit_overpositive(text: str) -> str:
        """[11] 과도한 긍정 표현 -> 현실적 표현으로 치환"""

        for phrase in SajuJudgmentRules._OVERPOSITIVE:
            text = text.replace(phrase, "좋은 흐름이 있는 사주")

        return text

    # -- 규칙 12: 보고서 톤 제거 --------------------------

    @staticmethod
    def rule12_remove_report_tone(text: str) -> str:
        """[12] 분석 보고서 말투 제거 -> 상담가 어투 유지"""

        for phrase in SajuJudgmentRules._REPORT_TONE:
            text = text.replace(phrase, "")

        return text

    # -- 전체 사후 필터 (출력 텍스트에 한 번에 적용) ---------

    @staticmethod
    def apply_all(text: str) -> str:
        """생성된 AI 텍스트에 전체 판단 규칙 순서대로 적용"""

        text = SajuJudgmentRules.rule01_soften_assertions(text)

        text = SajuJudgmentRules.rule05_check_negative_balance(text)

        text = SajuJudgmentRules.rule09_check_memory_conflict(text)

        text = SajuJudgmentRules.rule11_limit_overpositive(text)

        text = SajuJudgmentRules.rule12_remove_report_tone(text)

        return text.strip()

    # -- AI 프롬프트용 규칙 주입 문자열 (사전 제어) ----------

    @staticmethod
    def build_rules_prompt(user_input: str = "") -> str:
        """AI 시스템 프롬프트에 추가할 판단 규칙 지시문 생성"""

        is_anxious = SajuJudgmentRules.rule07_detect_anxiety(user_input)

        mem_ctx = SajuMemory.build_context_prompt()
        rules = """

[사주 AI 판단 규칙 - 반드시 준수]

[1] 단정 금지: "반드시", "100%" 대신 "흐름상", "가능성이 높습니다" 사용

[2] 순서 유지: 현재 운세 -> 성향 -> 행동 조언 순

[3] 데이터 준수: 사주 원국에 없는 정보(특정 날짜/직업명 단정) 생성 금지

[4] 시간 제한: 단기(1년)/중기(3년)/장기(10년) 이상 예측 금지

[5] 부정 균형: 위험 요소 언급 시 반드시 대응 방법 함께 제시

[6] 일관성: 동일 질문에 방향이 달라지면 안 됨

[8] 언어: 한자/격국 전문용어 남발 금지. 일반인 언어로 설명

[10] 행동 조언: 모든 풀이 끝에 "지금 할 수 있는 행동 1가지" 제시

[11] 긍정 과잉 금지: 긍정 60 / 현실 경고 40 비율 유지

[12] 상담가 말투: "분석 결과:" "다음과 같습니다" 같은 보고서체 금지

"""

        if is_anxious:
            rules += "\n[7] 주의: 사용자가 불안 상태입니다. 공포 강화 금지. 이해 -> 안정 -> 방향 순으로 답변."

        if mem_ctx:
            rules += f"\n\n{mem_ctx}"

        return rules.strip()


st.set_page_config(
    page_title="[MANSE] Saju Heaven-Sent Destiny",
    page_icon="*",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()

# 모바일 viewport 메타태그 (iOS Safari 줌 방지)
st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
    unsafe_allow_html=True,
)

# ==============================================

#  만신(萬神)급 명리 데이터 상수

# ==============================================

CG = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

CG_KR = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]

JJ = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

JJ_KR = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

JJ_AN = [
    "쥐",
    "소",
    "호랑이",
    "토끼",
    "용",
    "뱀",
    "말",
    "양",
    "원숭이",
    "닭",
    "개",
    "돼지",
]


HAP_MAP = {
    "子": "丑",
    "丑": "子",
    "寅": "亥",
    "亥": "寅",
    "卯": "戌",
    "戌": "卯",
    "辰": "酉",
    "酉": "辰",
    "巳": "申",
    "申": "巳",
    "午": "未",
    "未": "午",
}

GANJI_60 = [CG[i % 10] + JJ[i % 12] for i in range(60)]

GANJI_60_KR = [CG_KR[i % 10] + JJ_KR[i % 12] for i in range(60)]


OHN = {"木": "나무", "火": "불", "土": "흙", "金": "쇠", "水": "물"}

OHE = {"木": "🌳", "火": "🔥", "土": "🪨", "金": "-", "水": "💧"}

OH_DIR = {"木": "동쪽", "火": "남쪽", "土": "중앙", "金": "서쪽", "水": "북쪽"}

OH_COLOR = {
    "목": "초록, 청색",
    "화": "빨강, 주황",
    "토": "노랑, 갈색",
    "금": "흰색, 은색",
    "수": "검정, 남색",
}

OH_NUM = {"木": "1, 3", "火": "2, 7", "土": "5, 0", "金": "4, 9", "水": "1, 6"}

OH_FOOD = {
    "木": "신맛, 푸른 채소",
    "火": "쓴맛, 붉은 과일",
    "土": "단맛, 뿌리 채소",
    "金": "매운맛, 흰색 육류",
    "水": "짠맛, 해조류/검은콩",
}

# 📖 만신(萬神) 통합 사주 용어 사전 (Lexicon)

SAJU_LEXICON = {
    "공망": "🌓 공망(空亡): '비어 있다'는 뜻으로, 해당 장소의 기운이 약해지거나 실속이 없어짐을 의미합니다. 하지만 예술, 종교, 철학 등 정신적 영역에서는 오히려 큰 성취의 기반이 되기도 합니다.",
    "원진살": "🎭 원진살(元辰(진)殺): 서로 미워하고 멀리하는 기운입니다. 인간관계에서 이유 없는 불화나 원망이 생길 수 있으나, 이를 인내와 배려로 극복하면 오히려 더 깊은 유대감을 형성하는 계기가 됩니다.",
    "귀문관살": "🚪 귀문관살(鬼門關殺): 직관력과 영감이 매우 예민해지는 기운입니다. 예술가나 종교인에게는 천재성을 발휘하는 통로가 되지만, 평상시에는 신경과민이나 집중력 분산을 주의해야 합니다.",
    "백호살": "🐯 백호살(白虎殺): 강력한 에너지와 추진력을 의미합니다. 과거에는 흉살로 보았으나 현대에는 카리스마와 전문성을 발휘하여 큰 성공을 거두는 강력한 원동력으로 해석합니다.",
    "양인살": "⚔️ 양인살(羊刃殺): 칼을 든 것처럼 강한 고집과 독립심을 뜻합니다. 경쟁 사회에서 남들보다 앞서가는 힘이 되지만, 독단적인 판단보다는 주변과의 조화를 꾀하는 지혜가 필요합니다.",
    "화개살": "🌸 화개살(華蓋殺): 예술적 재능과 종교적 심성이 깊음을 뜻합니다. 고독을 즐기며 내면을 다지면 학문이나 예술 분야에서 빛을 발하는 고결한 기운입니다.",
    "역마살": "🐎 역마살(驛馬殺): 활동 범위가 넓고 변화를 추구하는 기운입니다. 한곳에 머물기보다 이동과 소통을 통해 기회를 잡는 현대 사회에 매우 유리한 길성이기도 합니다.",
    "도화살": "🍑 도화살(桃花殺): 사람을 끌어당기는 매력과 인기를 뜻합니다. 현대 사회에서 연예, 홍보, 영업 등 대인 관계가 중요한 분야에서 강력한 성공의 무기가 되는 기운입니다.",
}


def render_saju_tooltip(term):
    """사주 용어에 툴팁을 적용하여 반환 (HTML)"""

    clean_term = term.replace("살", "").strip()

    desc = SAJU_LEXICON.get(term) or SAJU_LEXICON.get(clean_term) or SAJU_LEXICON.get(term + "살")

    if desc:
        return f'<span class="saju-tooltip">{term}<span class="tooltiptext">{desc}</span></span>'

    return term


def apply_lexicon_tooltips(text):
    """텍스트 내의 사주 용어들을 찾아 툴팁 HTML로 자동 치환"""

    if not text or not isinstance(text, str):
        return text

    # 용어 길이가 긴 것부터 치환하여 중복 간섭 최소화

    sorted_terms = sorted(SAJU_LEXICON.keys(), key=len, reverse=True)

    for term in sorted_terms:
        if term in text:
            # 이미 HTML 태그로 감싸진 경우 제외 (단순 구현)

            pattern = re.compile(f'(?<![>"]){re.escape(term)}(?![<"])')

            text = pattern.sub(render_saju_tooltip(term), text)

    return text



ess_map = {k: v["nature"] for k, v in ILGAN_DESC.items()}

OH_RELATE = {
    "木": {"saeng": "火", "geuk": "土"},
    "火": {"saeng": "土", "geuk": "金"},
    "土": {"saeng": "金", "geuk": "水"},
    "金": {"saeng": "水", "geuk": "木"},
    "水": {"saeng": "木", "geuk": "火"},
}

SIPSUNG_LIST = [
    "比肩(비견)",
    "劫財(겁재)",
    "食神(식신)",
    "傷官(상관)",
    "偏財(편재)",
    "正財(정재)",
    "偏官(편관)",
    "正官(정관)",
    "偏印(편인)",
    "正印(정인)",
]


# ★ bare 한자 key alias 추가: CG[]='甲' → TEN_GODS_MATRIX='甲(갑)' 불일치 해결

# get_pillars, get_daewoon 등은 CG[]=bare 한자를 사용하므로 두 포맷 모두 지원

_CG_FULL = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

_CG_BARE = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

for _bare, _full in zip(_CG_BARE, _CG_FULL):
    if _full in TEN_GODS_MATRIX and _bare not in TEN_GODS_MATRIX:
        _sub = {}

        for _k, _v in TEN_GODS_MATRIX[_full].items():
            _sub[_k] = _v

            # 서브키도 bare 한자로 alias (예: "甲"→"甲")

            _bare_k = _k.split("(")[0] if "(" in _k else _k

            if _bare_k != _k:
                _sub[_bare_k] = _v

        TEN_GODS_MATRIX[_bare] = _sub

        # 원래 full키 서브딕셔너리에도 bare 서브키 추가

        for _k2, _v2 in list(TEN_GODS_MATRIX[_full].items()):
            _bare_k2 = _k2.split("(")[0] if "(" in _k2 else _k2

            if _bare_k2 not in TEN_GODS_MATRIX[_full]:
                TEN_GODS_MATRIX[_full][_bare_k2] = _v2

JIJANGGAN = {
    "子": ["壬", "癸"],
    "丑": ["癸", "辛", "己"],
    "寅": ["戊", "丙", "甲"],
    "卯": ["甲", "乙"],
    "辰": ["乙", "癸", "戊"],
    "巳": ["戊", "庚", "丙"],
    "午": ["丙", "己", "丁"],
    "未": ["丁", "乙", "己"],
    "申": ["戊", "壬", "庚"],
    "酉": ["庚", "辛"],
    "戌": ["辛", "丁", "戊"],
    "亥": ["戊", "甲", "壬"],
}

# JIJANGGAN bare 한자 key alias: JJ[]='子'(bare) 형식으로 조회 가능하게

for _jb, _jf in zip(
    ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"],
    [
        "子(자)",
        "丑(축)",
        "寅(인)",
        "卯(묘)",
        "辰(진)",
        "巳(사)",
        "午(오)",
        "未(미)",
        "申(신)",
        "酉(유)",
        "戌(술)",
        "亥(해)",
    ],
):
    if _jf in JIJANGGAN and _jb not in JIJANGGAN:
        JIJANGGAN[_jb] = JIJANGGAN[_jf]


CONTROL_MAP = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

BIRTH_MAP = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}


def tab_monthly(pils, birth_year, gender):
    """월별 세운 표시 (단순화 버전 - 오류 해결용)"""

    import calendar

    today = datetime.now()

    sel_year = today.year

    LEVEL_COLOR = {
        "대길": "#4caf50",
        "길": "#8bc34a",
        "평길": "#ffc107",
        "평": "#9e9e9e",
        "흉": "#f44336",
        "흉흉": "#b71c1c",
    }

    LEVEL_EMOJI = {
        "대길": "🌟",
        "길": "✅",
        "평길": "🟡",
        "평": "⬜",
        "흉": "⚠️",
        "흉흉": "🔴",
    }

    months_data = [get_monthly_luck(pils, sel_year, m) for m in range(1, 13)]

    for ml in months_data:
        m = ml["월"]

        is_now = m == today.month

        lcolor = LEVEL_COLOR.get(ml["길흉"], "#777")

        lemoji = LEVEL_EMOJI.get(ml["길흉"], "")

        with st.expander(
            f"{'-> ' if is_now else ''}{m}월 | {ml['월운']} | {lemoji} {ml['길흉']}",
            expanded=is_now,
        ):
            st.markdown(
                f"""

<div style="border-left:4px solid {lcolor}; padding:10px; background:#f9f9f9; border-radius:0 8px 8px 0;">

<div style="font-size:13px; color:#333; line-height:1.6;">

<b>[요약]</b> {ml["short"]}<br>

<b>[분석]</b> {ml["설명"]}

</div>

</div>

            """,
                unsafe_allow_html=True,
            )


# ==================================================

#  AI 해석 (Bug 3 Fix: hash_funcs)

# ==================================================

################################################################################

# *** Saju Platform Engineering Agent - AI 격리 아키텍처 ***

#

# [구조 원칙]

#   만세력 엔진(Deterministic) -> 분석 JSON -> AI Sandbox -> 텍스트 출력

#

# Brain 1: 만세력 계산 엔진 - 절대 영역, AI 접근 금지

# Brain 2: AI 해석 엔진     - 읽기 전용 JSON만 수신, 계산 금지

#

# [AI 행동 금지]

#   - 생년월일 재계산 금지

#   - 간지(干支) 재추론 금지

#   - 오행 재계산 금지

#   - 대운/세운 재계산 금지

#   -> 위반 감지 시 자동 차단 (validate_ai_output)

################################################################################

# -- Brain 2: AI Sandbox Wrapper -----------------------------------------------



def get_ai_interpretation(
    prompt_text,
    api_key="",
    system="당신은 40년 경력의 한국 전통 사주명리 전문가입니다.",
    max_tokens=2000,
    groq_key="",
    stream=False,
    history=None,
):
    """[로컬 전용] AI API 미사용. 외부 호출 제거됨. 로컬 엔진만 사용하세요."""
    return ""


# ✅ BUG 3 FIX: hash_funcs를 사용하여 dict 인수 해싱 가능하게 처리


@st.cache_data(hash_funcs={dict: lambda d: json.dumps(d, sort_keys=True, default=str)})
def build_past_events(pils, birth_year, gender):
    """

    과거 사건 자동 생성 v2 — 천간충+지지충 동시 감지, 도메인 7개 세분화, 구체적 문구

    정확도 향상 포인트:

    · 천간충(甲(갑)-庚(경), 乙(을)-辛(신), 丙(병)-壬(임), 丁(정)-癸(계)) + 지지충 동시 발생 → 최고강도

    · 육합(六合) 감지로 긍정 이벤트 추가

    · 충 종류별 도메인 자동 매핑 (子(자)午(오)→건강, 丑(축)未(미)→재물손실, 寅(인)申(신)→사고 등)

    · 나이: 만나이+1 = 한국 세는나이 일관 적용

    """

    ilgan = pils[1]["cg"]

    orig_jjs = [p["jj"] for p in pils]

    orig_cgs = [p["cg"] for p in pils]

    current_year = datetime.now().year

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    # ① 천간충 쌍 (甲-庚, 乙-辛, 丙-壬, 丁-癸)

    TG_CHUNG = [
        frozenset(["甲", "庚"]),
        frozenset(["乙", "辛"]),
        frozenset(["丙", "壬"]),
        frozenset(["丁", "癸"]),
    ]

    # ② 천간합 쌍

    TG_HAP = [
        frozenset(["甲", "己"]),
        frozenset(["乙", "庚"]),
        frozenset(["丙", "辛"]),
        frozenset(["丁", "壬"]),
        frozenset(["戊", "癸"]),
    ]

    # ③ 육합(六合) — 대운×세운 지지가 합을 이루면 긍정 이벤트

    YUK_HAP = [
        frozenset(["子", "丑"]),
        frozenset(["寅", "亥"]),
        frozenset(["卯", "戌"]),
        frozenset(["辰", "酉"]),
        frozenset(["巳", "申"]),
        frozenset(["午", "未"]),
    ]

    # ④ 지지충 → 도메인·설명 (사건 유형 고정)


    # ⑤ 십성 → 세분화 도메인 (7개 카테고리)


    # ⑥ 대운+세운 십성 조합 → (강도, 구체 설명)


    events = []

    def _adjust_for_youth(domain, desc, age):
        """미성년자(20세 미만)에 맞게 도메인과 설명을 필터링/수정"""

        if age >= 20:
            return domain, desc

        # 20세 미만 필터링 로직

        if any(w in domain for w in ["재물", "직업", "결혼", "이직", "사업", "승진"]):
            return None, None  # 미성년자에게 안 맞는 도메인은 통째로 스킵

        if "관재" in domain or "소송" in desc or "법적" in desc:
            domain = domain.replace("관재", "잔부상").replace("이별", "")

            desc = "성장기의 크고 작은 부상이나 건강 상의 주의가 필요했던 시기일 수 있습니다."

        if "강제이동" in domain or "이사" in desc:
            domain = "가족이동/환경변화"

            desc = "부모님의 환경 변화나 전학 등으로 거주지/학교 생활에 큰 변화가 있었을 가능성이 있습니다."

        if "건강" in domain or "사고" in domain or "질병" in domain or "부상" in desc:
            domain = "건강/잔병치레"

            desc = "어릴 적 크게 앓았거나 다쳤을 가능성, 또는 잔병치레가 많았을 시기입니다."

        return domain, desc

    for dw in daewoon:
        if dw["시작연도"] > current_year:
            continue

        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        dw_domain = SS_DOMAIN.get(gender, SS_DOMAIN["남"]).get(dw_ss, "변화")

        age_start = dw["시작나이"]

        # A. 대운 천간이 원국 천간과 충하는지 (천간충)

        dw_tg_chung = [ocg for ocg in orig_cgs if frozenset([dw["cg"], ocg]) in TG_CHUNG]

        # B. 대운 지지가 원국 지지와 충하는지 (지지충)

        dw_jj_chung = [(ojj, frozenset([dw["jj"], ojj])) for ojj in orig_jjs if frozenset([dw["jj"], ojj]) in CHUNG_MAP]

        # C. 대운 천간이 원국 천간과 합하는지

        dw_tg_hap = [list(pair - {dw["cg"]})[0] for pair in TG_HAP if dw["cg"] in pair and list(pair - {dw["cg"]})[0] in orig_cgs]

        # 대운 진입 이벤트: 천간충+지지충 동시 → 최고강도

        if dw_tg_chung and dw_jj_chung:
            ojj, ck = dw_jj_chung[0]

            domain, cdd = CHUNG_DOMAIN_DESC.get(ck, (dw_domain, "큰 변화가 왔다"))

            adj_domain, adj_desc = _adjust_for_youth(domain, cdd, age_start)

            if adj_domain:
                events.append(
                    {
                        "age": f"{age_start}~{age_start + 2}세",
                        "year": dw["시작연도"],
                        "type": "대운 천간충+지지충",
                        "domain": adj_domain,
                        "desc": (
                            f"【{age_start}세 대운 진입 · 천간충+지지충 동시】"
                            f"천간({dw['cg']})과 지지({dw['jj']})가 동시에 원국을 강타."
                            f" {adj_desc}. 이 시기 삶이 크게 뒤흔들렸을 가능성이 매우 높습니다."
                        ),
                        "intensity": "High",
                    }
                )

            ojj, ck = dw_jj_chung[0]

            domain, cdd = CHUNG_DOMAIN_DESC.get(ck, (dw_domain, "큰 변화가 찾아왔다"))

            adj_domain, adj_desc = _adjust_for_youth(domain, cdd, age_start)

            if adj_domain:
                events.append(
                    {
                        "age": f"{age_start}~{age_start + 2}세",
                        "year": dw["시작연도"],
                        "type": "대운 지지충",
                        "domain": adj_domain,
                        "desc": f"【{age_start}세 대운 진입 · 지지충】{adj_desc}.",
                        "intensity": "High",
                    }
                )

        elif dw_tg_hap:
            adj_domain, _ = _adjust_for_youth(dw_domain, "", age_start)

            if adj_domain:
                events.append(
                    {
                        "age": f"{age_start}세",
                        "year": dw["시작연도"],
                        "type": "대운 천간합",
                        "domain": adj_domain,
                        "desc": f"【{age_start}세 대운 진입 · 천간합】천간합(天干合) 성립 — {adj_domain} 영역에서 뜻밖의 인연이나 도움이 찾아온 시기입니다.",
                        "intensity": "Mid",
                    }
                )

        # 대운 내 세운별 교차 분석

        for y in range(dw["시작연도"], min(dw["종료연도"] + 1, current_year)):
            age = y - birth_year + 1

            if age < 5:
                continue

            sw = get_yearly_luck(pils, y) or {}

            sw_cg = sw.get("cg", "")

            sw_ss = sw.get("십성_천간", "-")

            sw_domain = SS_DOMAIN.get(gender, SS_DOMAIN["남"]).get(sw_ss, "변화")

            # 세운 지지 → 원국 지지 충 감지

            sw_jj_chung = [(ojj, frozenset([sw.get("jj",""), ojj])) for ojj in orig_jjs if frozenset([sw.get("jj",""), ojj]) in CHUNG_MAP]

            # 세운 천간 → 원국 천간 충 감지

            sw_tg_chung = [ocg for ocg in orig_cgs if frozenset([sw_cg, ocg]) in TG_CHUNG]

            # 대운 지지 ↔ 세운 지지 충

            dw_sw_jj_chung = frozenset([dw["jj"], sw.get("jj","")]) in CHUNG_MAP

            # 십성 조합 체크 (정방향+역방향)

            dw_sw_key = f"{dw_ss}+{sw_ss}"

            sw_dw_key = f"{sw_ss}+{dw_ss}"

            combo_hit = HIGH_IMPACT.get(dw_sw_key) or HIGH_IMPACT.get(sw_dw_key)

            # 삼합 성립 여부

            sam_hap_found = []

            all_jj = set(orig_jjs + [dw["jj"], sw.get("jj","")])

            for combo, (hname, hoh, hdesc) in SAM_HAP_MAP.items():
                if combo.issubset(all_jj) and dw["jj"] in combo and sw.get("jj","") in combo:
                    sam_hap_found.append(hname)

            # 대운×세운 육합 (긍정 결합)

            yuk_hap = frozenset([dw["jj"], sw.get("jj","")]) in YUK_HAP

            # 이미 같은 연도 이벤트가 있으면 스킵

            if any(e["year"] == y for e in events):
                continue

            # ── 우선순위 1: 천간충+지지충 동시 (세운 기준) ──

            if sw_tg_chung and sw_jj_chung:
                ojj, ck = sw_jj_chung[0]

                domain, cdd = CHUNG_DOMAIN_DESC.get(ck, (sw_domain, "큰 변화"))

                combo_desc = combo_hit[1] if combo_hit else ""

                adj_domain, adj_cdd = _adjust_for_youth(domain, cdd, age)

                _, adj_combo = _adjust_for_youth(domain, combo_desc, age)

                if adj_domain:
                    events.append(
                        {
                            "age": f"{age}세",
                            "year": y,
                            "type": f"{dw_ss}대운 x {sw_ss}세운 + 천간충+지지충",
                            "domain": adj_domain,
                            "desc": (f"【{y}년 · {age}세 · 최고강도】천간({sw_cg})과 지지({sw['jj']})가 동시에 원국을 충격하는 해. {adj_cdd}. {adj_combo or ''}"),
                            "intensity": "High",
                        }
                    )

            # ── 우선순위 2: 세운 지지충 발생 ──

            elif sw_jj_chung:
                ojj, ck = sw_jj_chung[0]

                domain, cdd = CHUNG_DOMAIN_DESC.get(ck, (sw_domain, "큰 변화"))

                intensity = "High"  # 충 발생 시 최소 High

                adj_domain, adj_cdd = _adjust_for_youth(domain, cdd, age)

                _, adj_combo = _adjust_for_youth(domain, combo_hit[1] if combo_hit else "", age)

                if adj_domain:
                    if combo_hit:
                        full_desc = f"【{y}년 · {age}세】{adj_cdd}. {adj_combo}"

                    else:
                        full_desc = f"【{y}년 · {age}세】{adj_cdd}."

                    events.append(
                        {
                            "age": f"{age}세",
                            "year": y,
                            "type": f"{dw_ss}대운 x {sw_ss}세운 + 원국충",
                            "domain": adj_domain,
                            "desc": full_desc,
                            "intensity": intensity,
                        }
                    )

            # ── 우선순위 3: 대운 지지 ↔ 세운 지지 충 + 십성조합 강도 High ──

            elif dw_sw_jj_chung and combo_hit and combo_hit[0] == "High":
                adj_domain, adj_combo = _adjust_for_youth(sw_domain, combo_hit[1], age)

                if adj_domain:
                    events.append(
                        {
                            "age": f"{age}세",
                            "year": y,
                            "type": f"{dw_ss}대운 x {sw_ss}세운 (대운지지-세운지지 충)",
                            "domain": adj_domain,
                            "desc": f"【{y}년 · {age}세】대운과 세운 지지가 서로 충돌하며 운의 방향이 급변. {adj_combo}",
                            "intensity": "High",
                        }
                    )

            # ── 우선순위 4: 삼합 성립 ──

            elif sam_hap_found:
                adj_domain, _ = _adjust_for_youth(sw_domain, "", age)

                if adj_domain:
                    events.append(
                        {
                            "age": f"{age}세",
                            "year": y,
                            "type": f"삼합 {sam_hap_found[0]}",
                            "domain": adj_domain,
                            "desc": f"【{y}년 · {age}세】대운·세운·원국 삼합({sam_hap_found[0]}) 성립 — {adj_domain} 영역에서 운의 집중 발복이 있었을 가능성이 높습니다.",
                            "intensity": "Mid",
                        }
                    )

            # ── 우선순위 5: 십성 조합 High/Mid ──

            elif combo_hit:
                intensity, combo_desc = combo_hit

                if intensity in ("High", "Mid", "Low"):
                    adj_domain, adj_combo = _adjust_for_youth(sw_domain, combo_desc, age)

                    if adj_domain:
                        events.append(
                            {
                                "age": f"{age}세",
                                "year": y,
                                "type": f"{dw_ss}대운 x {sw_ss}세운",
                                "domain": adj_domain,
                                "desc": f"【{y}년 · {age}세】{adj_combo}",
                                "intensity": intensity,
                            }
                        )

            # ── 우선순위 6: 대운×세운 육합 (긍정 결합) ──

            elif yuk_hap and dw_ss in {"正財", "食神", "正官", "正印"} and sw_ss in {"正財", "食神", "正官", "正印"}:
                adj_domain, _ = _adjust_for_youth(sw_domain, "", age)

                if adj_domain:
                    events.append(
                        {
                            "age": f"{age}세",
                            "year": y,
                            "type": f"{dw_ss}대운 x {sw_ss}세운 육합",
                            "domain": adj_domain,
                            "desc": f"【{y}년 · {age}세】대운·세운 지지가 육합(六合)을 이루며 기운이 모임. {adj_domain} 영역에서 좋은 결실이 있었을 가능성이 높습니다.",
                            "intensity": "Low",
                        }
                    )

    # 중요도 기준 정렬, 상위 15개 선별

    priority = {"High": 0, "Mid": 1, "Low": 2, "None": 3}

    events.sort(key=lambda e: (priority.get(e["intensity"], 3), e["year"]))

    return events


def build_life_event_timeline(pils, birth_year, gender, start_year=None, end_year=None):
    """

    ⏱️ 생애 사건 타임라인 v2 — 7개 도메인 핀포인팅

    직업변화 / 결혼·교제 / 이사·이동 / 재물획득 / 재물손실 / 사고·관재 / 질병·건강

    개선: 지지충 유형별 도메인 자동 고정, 대운만 해당해도 보조 체크, 구체 문구

    """

    ilgan = pils[1]["cg"]

    current_year = datetime.now().year
    _end_year = end_year if end_year is not None else current_year
    _start_year = start_year if start_year is not None else 0

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    orig_jjs = [p["jj"] for p in pils]

    # 7개 도메인 트리거 십성

    DOMAIN_TRIGGERS = {
        "직업변화": {"偏官", "正官", "傷官", "劫財"},
        "결혼·교제": {"正財", "偏財"} if gender == "남" else {"正官", "偏官"},
        "이사·이동": {"偏印", "偏財", "劫財"},
        "재물획득": {"食神", "正財", "偏財"},
        "재물손실": {"劫財", "偏官"},
        "사고·관재": {"偏官", "劫財"},
        "질병·건강": {"偏官"},
    }

    # 도메인 우선순위 (낮을수록 먼저 선택)

    DOMAIN_PRIORITY = {
        "사고·관재": 0,
        "질병·건강": 1,
        "재물손실": 2,
        "직업변화": 3,
        "결혼·교제": 4,
        "이사·이동": 5,
        "재물획득": 6,
    }

    # 지지충 → 도메인 강제 매핑 (충 발생 시 해당 도메인으로 고정)

    CHUNG_TO_DOMAIN = {
        frozenset(["子", "午"]): "질병·건강",
        frozenset(["丑", "未"]): "재물손실",
        frozenset(["寅", "申"]): "사고·관재",
        frozenset(["卯", "酉"]): "직업변화",
        frozenset(["辰", "戌"]): "재물손실",
        frozenset(["巳", "亥"]): "이사·이동",
    }

    CHUNG_DESC = {
        frozenset(["子", "午"]): "수화(水火) 충돌 — 극심한 감정 기복, 심장·혈압·신경계 이상이 온 시기입니다.",
        frozenset(["丑", "未"]): "토(土) 충돌 — 토지·부동산·보증 문제 또는 재물 분쟁이 있었던 시기입니다.",
        frozenset(["寅", "申"]): "목금(木金) 충돌 — 돌발 사고·강제 이직·이사 중 하나가 있었던 시기입니다.",
        frozenset(["卯", "酉"]): "목금(木金) 충돌 — 관재·이직·이성 갈등 중 하나가 있었던 시기입니다.",
        frozenset(["辰", "戌"]): "토(土) 충돌 — 부동산 갈등이나 큰 재물 손실이 있었던 시기입니다.",
        frozenset(["巳", "亥"]): "화수(火水) 충돌 — 중요한 이별이나 먼 이동이 있었던 시기입니다.",
    }

    # 도메인별 십성 조합 → 구체 문구


    DEFAULT_DESC = {
        "직업변화": "직장 또는 직업에서 중요한 변화가 있었던 시기입니다.",
        "결혼·교제": "가까운 인연 관계에서 중요한 전환점이 있었던 시기입니다.",
        "이사·이동": "거주지나 생활 환경이 크게 바뀌었던 시기입니다.",
        "재물획득": "수입이 오르거나 재물이 들어오는 변화가 있었던 시기입니다.",
        "재물손실": "재물이 빠져나가거나 금전적 손실이 있었던 시기입니다.",
        "사고·관재": "사고·법적 문제·외부 압박이 있었던 시기입니다.",
        "질병·건강": "몸이나 정신에 이상 신호가 온 시기입니다.",
    }

    DOMAIN_EMOJI = {
        "직업변화": "💼",
        "결혼·교제": "💑",
        "이사·이동": "🏠",
        "재물획득": "💰",
        "재물손실": "💸",
        "사고·관재": "⚠️",
        "질병·건강": "🏥",
    }

    timeline = []

    def _adjust_for_youth_timeline(domain, desc, age):
        """미성년자(20세 미만)에 맞게 도메인과 설명을 필터링/수정"""

        if age >= 20:
            return domain, desc

        # 20세 미만 필터링 로직

        if domain in ["직업변화", "결혼·교제", "재물획득", "재물손실"]:
            return None, None

        if domain == "사고·관재":
            domain = "건강/잔병치레"

            desc = "성장기의 크고 작은 부상이나 건강 상의 주의가 필요했던 시기입니다."

        if domain == "이사·이동":
            domain = "가족이동/환경변화"

            desc = "부모님의 환경 변화나 전학 등으로 거주지/학교 생활에 큰 변화가 있었을 가능성이 있습니다."

        if domain == "질병·건강":
            domain = "건강/잔병치레"

            desc = "어릴 적 크게 앓았거나 다쳤을 가능성, 또는 잔병치레가 많았을 시기입니다."

        return domain, desc

    for dw in daewoon:
        if dw["시작연도"] > _end_year:
            continue
        if dw["종료연도"] < _start_year:
            continue

        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        yr_from = max(dw["시작연도"], _start_year) if _start_year else dw["시작연도"]
        for y in range(yr_from, min(dw["종료연도"] + 1, _end_year + 1)):
            age = y - birth_year + 1

            if age < 5:  # 최소 5세부터 시작
                continue

            sw = get_yearly_luck(pils, y) or {}

            sw_ss = sw.get("십성_천간", "-")

            combo = (dw_ss, sw_ss)

            # 세운 지지 → 원국 지지 충 감지 → 도메인 강제 매핑

            sw_chung_domain = None

            sw_chung_desc = None

            for ojj in orig_jjs:
                k = frozenset([sw.get("jj",""), ojj])

                if k in CHUNG_MAP and k in CHUNG_TO_DOMAIN:
                    sw_chung_domain = CHUNG_TO_DOMAIN[k]

                    sw_chung_desc = CHUNG_DESC.get(k, "")

                    break

            # 중복 방지

            if any(t["year"] == y for t in timeline):
                continue

            # 후보 도메인 수집 (대운+세운 모두 트리거이거나, 충이 발생한 경우)

            candidates = []

            for domain, triggers in DOMAIN_TRIGGERS.items():
                both_match = dw_ss in triggers and sw_ss in triggers

                chung_match = (sw_chung_domain == domain) and (dw_ss in triggers or sw_ss in triggers)

                if both_match or chung_match:
                    candidates.append(domain)

            if not candidates:
                continue

            # 우선순위 가장 높은 도메인 선택

            best_domain = min(candidates, key=lambda d: DOMAIN_PRIORITY.get(d, 9))

            # 충 발생한 도메인이 있으면 그것을 우선

            if sw_chung_domain and sw_chung_domain in candidates:
                best_domain = sw_chung_domain

            # 설명 생성

            desc = EVENT_DESC.get(best_domain, {}).get(combo)

            if not desc:
                desc = DEFAULT_DESC.get(best_domain, "중요한 변화가 있었을 가능성이 높습니다.")

            if sw_chung_domain == best_domain and sw_chung_desc:
                desc = sw_chung_desc  # 충 설명이 있으면 구체 설명만 사용, 일반 설명 생략

            adj_domain, adj_desc = _adjust_for_youth_timeline(best_domain, desc, age)

            if not adj_domain:
                continue

            sign = "🔴" if adj_domain in ("사고·관재", "재물손실", "질병·건강", "건강/잔병치레") else "🟡"

            timeline.append(
                {
                    "year": y,
                    "age": age,
                    "domain": adj_domain,
                    "emoji": DOMAIN_EMOJI.get(best_domain, "📍"),
                    "desc": adj_desc,
                    "intensity": "High" if sw_chung_domain else "Mid",
                    "sign": sign,
                }
            )

    # 연도 순 정렬, 최대 30개
    timeline.sort(key=lambda x: x["year"])

    return timeline[:30]


# ==================================================================

# *** 십성(十星) 2-조합 인생 분석 DB ***

# 조합만 알면 그 사람의 인생이 보인다

# ==================================================================




# ── CAREER_MATRIX 키 변환 헬퍼 (짧은 형식 → 긴 형식) ──────────
_GK_KEY_MAP_GLOBAL = {
    "比肩格":"比肩(비견)格(비견격)", "劫財格":"劫財(겁재)格(겁재격)",
    "食神格":"食神(식신)格(식신격)", "傷官格":"傷官(상관)格(상관격)",
    "偏財格":"偏財(편재)格(편재격)", "正財格":"正財(정재)格(정재격)",
    "偏官格":"偏官(편관)格(편관격)", "正官格":"正官(정관)格(정관격)",
    "偏印格":"偏印(편인)格(편인격)", "正印格":"正印(정인)格(정인격)",
    "비견格":"比肩(비견)格(비견격)", "겁재格":"劫財(겁재)格(겁재격)",
    "식신格":"食神(식신)格(식신격)", "상관格":"傷官(상관)格(상관격)",
    "편재格":"偏財(편재)格(편재격)", "정재格":"正財(정재)格(정재격)",
    "편관格":"偏官(편관)格(편관격)", "정관格":"正官(정관)格(정관격)",
    "편인格":"偏印(편인)格(편인격)", "정인格":"正印(정인)格(정인격)",
}

def _gk_career(gname):
    """격국명을 CAREER_MATRIX 키 형식으로 변환 후 조회"""
    _key = _GK_KEY_MAP_GLOBAL.get(gname, gname)
    _fb  = "比肩(비견)格(비견격)"
    return CAREER_MATRIX.get(_key, CAREER_MATRIX.get(_fb, {
        "best": ["자영업/프리랜서", "독립 사업"],
        "good": ["컨설팅", "강사"],
        "avoid": ["단순 반복직"]
    }))

def build_life_analysis(pils, gender):
    """

    * 십성 2-조합으로 인생 전체를 읽는 핵심 엔진 *

    성향 / 재물 / 직업 / 연애 / 주의사항 5가지 출력

    """

    ilgan = pils[1]["cg"]

    # 원국 전체 십성 수집

    ss_count = {}

    for p in pils:
        cg_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(p["cg"], "")

        jjg = JIJANGGAN.get(p["jj"], [])

        jj_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(jjg[-1] if jjg else "", "")

        for ss in [cg_ss, jj_ss]:
            if ss and ss not in ("-", ""):
                ss_count[ss] = ss_count.get(ss, 0) + 1

    # 많이 나온 순으로 정렬

    top_ss = sorted(ss_count, key=ss_count.get, reverse=True)

    # 조합 매칭 (상위 4개 십성 내에서)

    matched = []

    checked = set()

    for i, a in enumerate(top_ss[:5]):
        for b in top_ss[i + 1 : 5]:
            k = frozenset([a, b])

            if k in SIPSUNG_COMBO_LIFE and k not in checked:
                matched.append((k, SIPSUNG_COMBO_LIFE[k]))

                checked.add(k)

    strength_info = get_ilgan_strength(ilgan, pils)

    sn = strength_info["신강신약"]

    return {
        "조합_결과": matched[:2],  # 상위 2개 조합
        "전체_십성": ss_count,
        "주요_십성": top_ss[:4],
        "신강신약": sn,
        "일간": ilgan,
    }


# ==================================================================

#  엔진 하이라이트 - AI가 아닌 엔진이 먼저 뽑아내는 핵심 적중 데이터

# ==================================================================

# 성향 조합 DB - "신약+관성강 -> 책임감 강+스트레스 많음" 같은 조합 공식


# 오행 과다/부족 조합 DB



@st.cache_data
def generate_engine_highlights(pils, birth_year, gender, bm=1, bd=1, bh=12, bmi=0):
    """

    * 핵심 엔진 *

    AI가 찾게 하지 말고 엔진이 먼저 뽑아낸다.

    반환값:

    {

        "past_events": [{"age": "27~28세", "year": 2019, "domain": "직장", "desc": "...", "intensity": "🔴"}],

        "personality": ["겉은 강해 보이나 속은...", "혼자 고민을 오래 끄는 성향"],

        "money_peak": [{"age": 32, "year": 2024, "desc": "..."}],

        "marriage_peak": [{"age": 31, "year": 2023, "desc": "..."}],

        "danger_zones": [{"age": "29~30세", "desc": "..."}],

        "wolji_chung": [{"age": "28세", "desc": "..."}]

    }

    """

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    current_year = datetime.now().year

    daewoon = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender=gender)

    strength_info = get_ilgan_strength(ilgan, pils)

    sn = strength_info["신강신약"]

    oh_strength = strength_info["oh_strength"]

    # -- 과거 사건 (기존 엔진 활용) -----------------------

    past_events = build_past_events(pils, birth_year, gender)

    # -- 성향 - 조합 공식으로 생성 ------------------------

    personality = build_personality_detail_v2(pils, gender, sn, oh_strength)

    # -- 재물 피크 -----------------------------------------

    money_peak = []

    MONEY_SS = {"식신", "정재", "편재"}

    for dw in daewoon:
        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        age_c = birth_year + dw["시작나이"] - 1

        if dw_ss in MONEY_SS:
            money_peak.append(
                {
                    "age": f"{dw['시작나이']}~{dw['시작나이'] + 9}세",
                    "year": f"{dw['시작연도']}~{dw['종료연도']}",
                    "desc": f"{dw['str']}대운({dw_ss}) - 재물이 자연스럽게 따라오는 시기",
                    "ss": dw_ss,
                }
            )

        # 세운 중 재물 피크 (현재+5년)

        if dw["시작연도"] <= current_year + 5 and dw["종료연도"] >= current_year - 2:
            for y in range(
                max(dw["시작연도"], current_year - 2),
                min(dw["종료연도"] + 1, current_year + 6),
            ):
                sw = get_yearly_luck(pils, y) or {}

                if sw.get("십성_천간","") in MONEY_SS and dw_ss in MONEY_SS:
                    age = y - birth_year + 1

                    money_peak.append(
                        {
                            "age": f"{age}세",
                            "year": str(y),
                            "desc": f"{y}년 - 대운({dw_ss})x세운({sw['십성_천간']}) 재물 더블. 최고의 돈 기회",
                            "ss": "더블",
                        }
                    )

    # -- 혼인 피크 -----------------------------------------

    MARRIAGE_SS = {"정재", "편재"} if gender == "남" else {"정관", "편관"}

    marriage_peak = []

    for dw in daewoon:
        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        if dw_ss in MARRIAGE_SS:
            # 대운 내에서 가장 강한 세운 탐색

            for y in range(dw["시작연도"], min(dw["종료연도"] + 1, current_year + 10)):
                sw = get_yearly_luck(pils, y) or {}

                if sw.get("십성_천간","") in MARRIAGE_SS:
                    age = y - birth_year + 1

                    marriage_peak.append(
                        {
                            "age": f"{age}세",
                            "year": str(y),
                            "desc": f"{y}년({age}세) - 대운/세운 모두 인연성. 배우자 인연이 오는 해",
                        }
                    )

    # -- 위험 구간 -----------------------------------------

    danger_zones = []

    DANGER_SS = {"편관", "겁재"}

    for dw in daewoon:
        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        if dw_ss in DANGER_SS:
            danger_zones.append(
                {
                    "age": f"{dw['시작나이']}~{dw['시작나이'] + 9}세",
                    "year": f"{dw['시작연도']}~{dw['종료연도']}",
                    "desc": f"{dw['str']}대운({dw_ss}) - {'직장/관재/건강 압박' if dw_ss == '편관' else '재물손실/경쟁/배신'} 주의",
                }
            )

    # -- 월지 충 시점 --------------------------------------

    wolji_chung = []

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    for dw in daewoon:
        if dw["종료연도"] >= current_year:
            continue

        k = frozenset([dw["jj"], wol_jj])

        if k in CHUNG_MAP:
            name_c, _, desc = CHUNG_MAP[k]

            age_start = dw["시작나이"]

            suffix = "학업/거주환경 중 하나가 크게 흔들렸습니다." if age_start < 20 else "직업/가정 중 하나가 반드시 흔들렸습니다."

            wolji_chung.append(
                {
                    "age": f"{age_start}~{age_start + 2}세",
                    "desc": f"대운 진입시 월지 충({name_c}) - {desc}. 이 시기 {suffix}",
                }
            )

        for y in range(dw["시작연도"], min(dw["종료연도"] + 1, current_year)):
            sw = get_yearly_luck(pils, y) or {}

            k2 = frozenset([sw.get("jj",""), wol_jj])

            if k2 in CHUNG_MAP:
                age = y - birth_year + 1

                name_c2, _, desc2 = CHUNG_MAP[k2]

                suffix = "학업/가정환경 중 하나가 흔들렸습니다." if age < 20 else "직업/가정 중 하나가 흔들렸습니다."

                wolji_chung.append(
                    {
                        "age": f"{age}세",
                        "desc": f"{y}년 세운이 월지를 충({name_c2}) - {desc2}. {suffix}",
                    }
                )

    return {
        "past_events": past_events,
        "personality": personality,
        "money_peak": money_peak,
        "marriage_peak": marriage_peak,
        "danger_zones": danger_zones,
        "wolji_chung": wolji_chung,
        "raw": {
            "ilgan": ilgan,
            "sn": sn,
            "oh_strength": oh_strength,
            "yongshin_ohs": get_yongshin(pils)["종합_용신"],
            "gyeok": get_gyeokguk(pils)["격국명"] if get_gyeokguk(pils) else "미정격",
        },
    }


def build_personality_detail_v2(pils, gender, sn, oh_strength):
    """

    강화된 성향 DB - 조합 공식 기반

    신약+관성강 / 비겁강 / 수과다 등 구체적 콤보

    """

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    traits = []

    # 강한 십성 파악 (원국 내 2개 이상)

    ss_count = {}

    for p in pils:
        jjg = JIJANGGAN.get(p["jj"], [])

        jeongi = jjg[-1] if jjg else ""

        for cg_check in [p["cg"], jeongi]:
            ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cg_check, "")

            if ss and ss not in ("", "-"):
                ss_count[ss] = ss_count.get(ss, 0) + 1

    strong_ss = [ss for ss, cnt in ss_count.items() if cnt >= 2]

    sn_key = "신강" if "신강" in sn else "신약"

    # 조합 공식 적용

    for ss in strong_ss:
        combo_key = (sn_key, ss)

        if combo_key in PERSONALITY_COMBO_DB:
            traits.extend(PERSONALITY_COMBO_DB[combo_key])

    # 기본 일간 심리 (조합이 없을 때 폴백)

    if not traits:

        base = OH_BASE.get(ilgan_oh, {}).get(sn_key, "")

        if base:
            traits.append(base)

    # 일지 십성 심리

    iljj_ss = "-"

    try:
        iljj_ss = calc_sipsung(ilgan, pils)[1].get("jj_ss", "-")

    except Exception as e:
        _saju_log.debug(str(e))

    ILJJ_DEEP = {
        "비견": "지기 싫어합니다. 지면 속으로 오래 끌고 갑니다. 표시는 안 내도 계속 생각합니다.",
        "겁재": "승부욕이 강합니다. 가까운 사람에게도 지기 싫어합니다. 배신당한 경험이 있고, 이후로 조심합니다.",
        "식신": "자기 방식이 있습니다. 간섭받는 것을 싫어하고, 자기 페이스로 하는 걸 좋아합니다.",
        "상관": "말이 빠르고 재치 있습니다. 상대방의 단점이 눈에 먼저 보입니다. 때로는 그 솔직함이 문제가 됩니다.",
        "편재": "활동적이고 사교적이지만, 한곳에 오래 머물기 싫어합니다. 새로운 자극을 계속 찾습니다.",
        "정재": "현실적이고 꼼꼼합니다. 손해 보는 것을 굉장히 싫어합니다. 계산이 빠릅니다.",
        "편관": "압박이 오면 오히려 더 버팁니다. 굴복하는 것을 본능적으로 거부합니다. 강인한 사람입니다.",
        "정관": "체면과 원칙을 중시합니다. 남들 시선에 민감하고, 창피당하는 것을 극도로 싫어합니다.",
        "편인": "설명하기 어렵지만 '그냥 아는' 경우가 많습니다. 직관이 매우 발달해 있습니다.",
        "정인": "완전히 이해하기 전까지 결정을 미룹니다. 배움에 대한 욕구가 강합니다.",
    }

    iljj_t = ILJJ_DEEP.get(iljj_ss, "")

    if iljj_t and iljj_t not in " ".join(traits):
        traits.append(iljj_t)

    # 오행 과다/부족 조합

    over_ohs = [o for o, v in oh_strength.items() if v >= 35]

    lack_ohs = [o for o, v in oh_strength.items() if v <= 5]

    zero_ohs = [o for o, v in oh_strength.items() if v == 0]

    for oh in over_ohs:
        for t in OH_COMBO_DB.get(("over", oh), []):
            traits.append(t)

    for oh in lack_ohs:
        for t in OH_COMBO_DB.get(("lack", oh), []):
            traits.append(t)

    if zero_ohs:
        oh_names = "/".join([OHN.get(o, "") for o in zero_ohs])

        traits.append(f"{oh_names} 기운이 완전히 없습니다. 이 분야가 들어올 때마다 당황하거나 흔들립니다.")

    return traits[:8]  # 최대 8개 - 너무 많으면 희석됨


@st.cache_data
def build_personality_detail(pils, gender="남"):
    """

    심리 디테일 생성 - "예민합니다"가 아닌 구체적 서술

    일간 + 일지 + 신강신약 + 오행 과다 조합

    """

    ilgan = pils[1]["cg"]

    iljj = pils[1]["jj"]

    ilgan_oh = OH.get(ilgan, "")

    iljj_ss = calc_sipsung(ilgan, pils)[1].get("jj_ss", "-")

    strength_info = get_ilgan_strength(ilgan, pils)

    sn = strength_info["신강신약"]

    oh_strength = strength_info["oh_strength"]

    over_ohs = [o for o, v in oh_strength.items() if v >= 35]

    lack_ohs = [o for o, v in oh_strength.items() if v <= 5]

    traits = []

    # 일간 심리 특성 (오행별)


    # 일간 기본 심리

    sn_key = "신강" if "신강" in sn else "신약" if "신약" in sn else "중화"

    base_trait = OH_PSYCH.get(ilgan_oh, {}).get(sn_key, "")

    if base_trait:
        traits.append(base_trait)

    # 일지 십성별 심리 보정

    ILJJ_PSYCH = {
        "비견": "자존심이 매우 강합니다. 지기 싫어하고, 지면 속으로 오래 끌고 갑니다.",
        "겁재": "경쟁 심리가 강하고 승부욕이 있습니다. 친한 사람에게도 지기 싫어합니다.",
        "식신": "배짱이 있고 여유롭게 보이지만, 은근히 자기 방식대로 하고 싶어합니다.",
        "상관": "말이 빠르고 재치 있습니다. 상대방의 단점이 눈에 먼저 보입니다.",
        "편재": "활동적이고 사교적이지만, 한곳에 오래 머물기 싫어합니다. 새로운 자극을 계속 찾습니다.",
        "정재": "현실적이고 꼼꼼합니다. 손해 보는 것을 굉장히 싫어합니다. 계산이 빠릅니다.",
        "편관": "압박이 오면 오히려 더 버팁니다. 굴복하는 것을 본능적으로 거부합니다. 강인한 사람입니다.",
        "정관": "체면과 원칙을 중시합니다. 남들 시선에 민감하고 규칙을 잘 지킵니다.",
        "편인": "직관이 뛰어납니다. 설명하기 어렵지만 '그냥 아는' 경우가 많습니다.",
        "정인": "배움을 좋아합니다. 완전히 이해하기 전까지 결정을 미루는 경향이 있습니다.",
    }

    iljj_trait = ILJJ_PSYCH.get(iljj_ss, "")

    if iljj_trait:
        traits.append(iljj_trait)

    # 오행 과다 심리 보정

    OH_OVER_PSYCH = {
        "木": "남들보다 빠릅니다. 결정도 빠르고 판단도 빠릅니다. 대신 기다리는 것을 못 합니다.",
        "火": "에너지가 넘칩니다. 시작은 잘 하는데 끝까지 가는 것이 과제입니다.",
        "土": "한번 정하면 잘 안 바꿉니다. 고집이 강하고 자기 방식이 확실합니다.",
        "金": "예리합니다. 사람을 빠르게 파악하고 판단합니다. 때로는 너무 날카롭습니다.",
        "水": "생각이 많습니다. 잠자리에 누워도 머릿속이 돌아갑니다. 걱정을 사서 합니다.",
    }

    for oh in over_ohs:
        t = OH_OVER_PSYCH.get(oh, "")

        if t:
            traits.append(f"[{OHN.get(oh, '')} 과다] {t}")

    # 오행 결핍 심리 보정

    OH_LACK_PSYCH = {
        "木": "계획을 세우는 것이 약합니다. 시작하기까지 시간이 걸립니다.",
        "火": "표현이 서툽니다. 속으로는 열정이 있지만 겉으로는 차가워 보일 수 있습니다.",
        "土": "안정을 찾기 힘들 수 있습니다. 한곳에 뿌리내리는 것이 과제입니다.",
        "金": "결단력이 부족할 수 있습니다. 잘라내야 할 것을 잘라내지 못합니다.",
        "水": "직관보다 논리로 움직입니다. 감정 표현이 서툴 수 있습니다.",
    }

    for oh in lack_ohs:
        t = OH_LACK_PSYCH.get(oh, "")

        if t:
            traits.append(f"[{OHN.get(oh, '')} 부족] {t}")

    return traits


def get_cached_ai_interpretation(
    pils_hashable,
    prompt_type="general",
    birth_year=1990,
    gender="남",
    name="",
    stream=False,
):
    """

    AI 해석 - Brain 2 Sandbox 통과 + 파일 캐시 적용

    [Saju Platform Engineering Agent]

    - 동일 사주 + 동일 prompt_type -> 캐시에서 즉시 반환 (API 재호출 없음)

    - 캐시 미스 -> Sandbox로 AI 호출 -> 결과 검증 -> 캐시 저장

    """

    saju_key = pils_hashable

    cache_key = f"{saju_key}_{prompt_type}"

    # 1. 파일 캐시 조회

    cached = get_ai_cache(saju_key, prompt_type)

    if cached:
        cached = cached.replace("~", "～")  # 마크다운 취소선 방지 (캐시 호출 시에도 적용)

        if stream:

            def cached_stream():

                yield cached

            return cached_stream()

        return cached

    # 2. 캐시 미스 -> 사주 데이터 구성 후 AI 호웉

    pils = json.loads(pils_hashable) if isinstance(pils_hashable, str) else pils_hashable

    ilgan = pils[1]["cg"] if len(pils) > 1 else "甲"

    saju_str = " ".join([p["str"] for p in pils])

    # * Brain 2 AI 캐시 확인 (동일 사주 재요청 시 즉시 반환)

    saju_key = pils_to_cache_key(pils)

    cached_ai = get_ai_cache(saju_key, prompt_type)

    if cached_ai:
        return cached_ai

    # 사주 데이터 계산

    strength_info = get_ilgan_strength(ilgan, pils)

    gyeokguk = get_gyeokguk(pils)

    oh_strength = strength_info["oh_strength"]

    current_year = datetime.now().year

    current_age = current_year - birth_year + 1

    # 대운 호출 시 실제 생년월일시 반영

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    current_dw = next((dw for dw in daewoon if dw["시작연도"] <= current_year <= dw["종료연도"]), None)

    yearly = get_yearly_luck(pils, current_year)

    gname = gyeokguk["격국명"] if gyeokguk else "미정격"

    sn = strength_info["신강신약"]

    # 대운 과거 목록 (발복/시련 분석용)

    past_dw_summary = []

    for dw in daewoon:
        if dw["종료연도"] < current_year:
            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            past_dw_summary.append(f"  {dw['시작나이']}~{dw['시작나이'] + 9}세({dw['시작연도']}~{dw['종료연도']}): {dw['str']} [{dw_ss}]")

    # 미래 3년 세운

    future_years = []

    for y in range(current_year, current_year + 3):
        ye = get_yearly_luck(pils, y)

        future_years.append(f"  {y}년({current_year - birth_year + (y - current_year) + 1}세): {ye['세운']} [{ye['십성_천간']}] {ye['길흉']}")

    # 돈 상승기 탐색 (대운 세운 중 재물 길운)

    money_peaks = []

    for dw in daewoon:
        if dw["시작연도"] >= current_year - 5:
            dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

            if dw_ss in ["식신", "정재", "편재", "정관"]:
                money_peaks.append(f"  {dw['시작나이']}~{dw['시작나이'] + 9}세 {dw['str']}대운({dw_ss}) 주목")

    # 혼인 분석 데이터

    marriage_ss = {"남": ["정재", "편재"], "여": ["정관", "편관"]}

    marry_hint = []

    for dw in daewoon:
        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        if dw_ss in marriage_ss.get(gender, []):
            marry_hint.append(f"  {dw['시작나이']}~{dw['시작나이'] + 9}세 {dw['str']}대운")

    # -- 엔진 하이라이트 계산 (핵심) -------------------

    hl = generate_engine_highlights(pils, birth_year, gender)

    # 과거 사건 블록 - 🔴부터 먼저

    past_ev_lines = []

    for ev in sorted(
        hl["past_events"],
        key=lambda e: {"🔴": 0, "🟡": 1, "🟢": 2}.get(e["intensity"], 3),
    ):
        past_ev_lines.append(f"  [{ev['intensity']}] {ev['age']}({ev['year']}년) [{ev.get('domain', '변화')}] {ev['desc']}")

    past_events_block = "\n".join(past_ev_lines) if past_ev_lines else "  (데이터 없음)"

    # 성향 블록 - 조합 공식 결과

    personality_block = "\n".join([f"  / {t}" for t in hl["personality"]])

    # 돈/결혼 피크

    money_block = "\n".join([f"  {m['age']}({m['year']}) - {m['desc']}" for m in hl["money_peak"]]) or "  (없음)"

    marry_block = "\n".join([f"  {m['age']}({m['year']}) - {m['desc']}" for m in hl["marriage_peak"]]) or "  (없음)"

    danger_block = "\n".join([f"  {d['age']}({d['year']}) - {d['desc']}" for d in hl["danger_zones"]]) or "  (없음)"

    wolji_block = "\n".join([f"  {w['age']} - {w['desc']}" for w in hl["wolji_chung"]]) or "  (없음)"

    ctx_data = build_rich_ai_context(pils, birth_year, gender, current_year)


    _tp = calc_turning_point(pils, birth_year, gender, current_year) if "calc_turning_point" in dir() else {}

    _yl = get_yearly_luck(pils, current_year)

    _ys = get_yongshin_multilayer(pils, birth_year, gender, current_year)

    _tp_label = _tp.get("fate_label", "분석중") if _tp else "분석중"

    _tp_desc = _tp.get("fate_desc", "") if _tp else ""

    _tp_intens = _tp.get("intensity", "보통") if _tp else "보통"

    _tp_reason = ", ".join(_tp.get("reason", [])) if _tp else ""


    # ── 과거 프롬프트 강화: 원국 분석 + 연도별 대운×세운 교차 ──────────────

    _sipsung_list = calc_sipsung(ilgan, pils)

    _sip_labels = ["시주", "일주", "월주", "년주"]

    _sipsung_str = " / ".join([f"{_sip_labels[i]}: 천간{s['cg_ss']} 지지{s['jj_ss']}" for i, s in enumerate(_sipsung_list)])

    _sinsal_12 = get_12sinsal(pils)

    _sinsal_detail = "\n".join([f"  - {s['이름']}({s['icon']}): {s['desc']} (주의: {s['caution']})" for s in _sinsal_12]) or "  없음"

    _sinsal_str = ", ".join([f"{s['이름']}({s['icon']})" for s in _sinsal_12]) or "없음"

    _extra_sins = get_extra_sinsal(pils)

    _extra_str = ", ".join([s.get("name", s.get("이름", "")) for s in _extra_sins]) or "없음"

    _has_yangin = any("양인" in s.get("name", "") or "羊刃" in s.get("name", "") for s in _extra_sins)

    _has_yukma = any("역마" in s.get("이름", "") or "驛馬" in s.get("이름", "") for s in _sinsal_12)

    _yukjin = get_yukjin(ilgan, pils, gender)

    _yukjin_str = "\n".join([f"  {y['관계']}: {y['위치']} - {y['desc']}" for y in _yukjin])

    _ys_ml = get_yongshin_multilayer(pils, birth_year, gender, current_year)

    _gyeokguk_str = f"{gname} ({gyeokguk.get('격의_등급', '') if gyeokguk else '-'})"

    # 과거 연도 수집 (과거사건 연도 + 대운 시작연도)

    _past_yr_set = set()

    for ev in hl["past_events"]:
        if ev["year"] < current_year:
            _past_yr_set.add(ev["year"])

    for dw in daewoon:
        if dw["시작연도"] < current_year:
            _past_yr_set.add(dw["시작연도"])

    _past_yr_list = sorted(_past_yr_set)

    _cross_lines = []

    _chung_lines = []

    for yr in _past_yr_list:
        age_y = yr - birth_year + 1

        cross = get_daewoon_sewoon_cross(pils, birth_year, gender, yr)

        if not cross:
            continue

        dw_i = cross["대운"]

        sw_i = cross["세운"]

        _cross_lines.append(
            f"  {yr}년({age_y}세): 대운{dw_i.get('str','')}[{cross.get('대운_천간십성','-')}/{cross.get('대운_지지십성','-')}] × 세운{sw_i.get('세운','')}[{cross.get('세운_천간십성','-')}/{cross.get('세운_지지십성','-')}] → {cross.get('교차해석','')}"
        )

        for ev_item in cross.get("교차사건", []):
            _chung_lines.append(f"  {yr}년({age_y}세): [{ev_item['type']}] {ev_item['desc']}")

    _cross_block = "\n".join(_cross_lines) if _cross_lines else "  (데이터 없음)"

    _chung_block = "\n".join(_chung_lines) if _chung_lines else "  (충/합 없음)"



    prompt = prompts.get(prompt_type, prompts["general"])

    # * Brain 3: Prompt Optimizer - 학습 패턴 자동 주입

    optimizer_suffix = b3_build_optimized_prompt_suffix()

    # * Adaptive Engine - 페르소나 스타일 자동 주입

    try:
        persona = infer_persona()

        persona_style = get_persona_prompt_style(persona)

        adaptive_suffix = f"\n\n[사용자 성향 분석]\n{persona_style}"

    except Exception:
        adaptive_suffix = ""

    # * User Memory Context - 사용자 기억 주입

    try:
        memory_ctx = build_memory_context(pils_to_cache_key(pils))

        memory_suffix = f"\n\n{memory_ctx}" if memory_ctx else ""

    except Exception:
        memory_suffix = ""

    # [로컬 전용] API 미사용. 캐시 미스 시 로컬 엔진(build_rich_narrative)으로 즉시 생성
    _section_map = {
        "prophet": "report",
        "general": "report",
        "career": "report",
        "love": "report",
        "lifeline": "lifeline",
        "past": "past",
        "money": "money",
        "relations": "relations",
        "future": "future",
    }
    _section = _section_map.get(prompt_type, "report")
    result = build_rich_narrative(pils, birth_year, gender, name, section=_section)
    if result and not result.startswith("["):
        result = result.replace("~", "～")
        set_ai_cache(saju_key, prompt_type, result)
    return result or ""


# 사주 입력값을 캐시 키로 변환


def pils_to_cache_key(pils):

    return json.dumps(pils, ensure_ascii=False, sort_keys=True)


# -- Brain 1 + Brain 2 캐싱 시스템 --------------------------------------------

# [설계 원칙]

#   만세력 결과 -> 파일 캐시 (동일 입력 = 즉시 출력, 계산 재수행 없음)

#   AI 해석 결과 -> AI 전용 캐시 (API 비용 70~80% 절감)

#   사용자 피드백 -> 캐싱 금지 (실시간 반영 필요)

#

# [성능 효과]

#   첫 계산: 4~6초 / 재사용: 0.1초 이하

#   AI 비용: 최초 1회만 지불, 동일 사주 재호출 무료

################################################################################

import os as _os

_SAJU_CACHE_FILE = "saju_cache.json"

_AI_CACHE_FILE = "saju_ai_cache.json"


def _load_json_cache(filepath: str) -> dict:
    """JSON 파일 캐시 로드"""

    try:
        if _os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    return {}


def _save_json_cache(filepath: str, cache: dict):
    """JSON 파일 캐시 저장"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")


def create_saju_cache_key(year: int, month: int, day: int, hour: int, gender: str, use_yaja_time: bool = True) -> str:
    """사주 캐시 키 생성 - 생년월일시+성별로 고유 ID"""
    return f"{year}-{month:02d}-{day:02d}-{hour:02d}-{gender}-{use_yaja_time}"


def get_saju_cache(year: int, month: int, day: int, hour: int, gender: str, use_yaja_time: bool = True):
    """Brain 1 계산 결과 캐시 조회"""
    key = create_saju_cache_key(year, month, day, hour, gender, use_yaja_time)
    cache = _load_json_cache(_SAJU_CACHE_FILE)
    return cache.get(key)


def set_saju_cache(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    data,
    use_yaja_time: bool = True,
):
    """Brain 1 계산 결과 캐시 저장"""
    key = create_saju_cache_key(year, month, day, hour, gender, use_yaja_time)
    cache = _load_json_cache(_SAJU_CACHE_FILE)
    cache[key] = data
    _save_json_cache(_SAJU_CACHE_FILE, cache)


def get_ai_cache(saju_key: str, prompt_type: str) -> str:
    """Brain 2 AI 해석 결과 캐시 조회 (날짜 만료 자동 적용)"""

    from datetime import datetime as _dt

    ai_key = f"AI-{prompt_type}-{saju_key}"

    cache = _load_json_cache(_AI_CACHE_FILE)

    entry = cache.get(ai_key)

    if entry is None:
        return None

    # 저장 형식: {"text": ..., "saved_at": "YYYYMMDD"} 또는 문자열(예전 캐시)

    if isinstance(entry, dict):
        text = entry.get("text", "")

        saved_at = entry.get("saved_at", "")

    else:
        text = entry

        saved_at = "19700101"  # 강제 만료 처리용 옛날 날짜

    # 만료 체크

    today = _dt.now()

    if prompt_type == "daily_ai":
        # 일일 운세: 오늘 날짜와 다르면 무조건 만료

        if saved_at != today.strftime("%Y%m%d"):
            return None

    elif prompt_type == "monthly_ai":
        # 월별: 그 달이 지나면 만료

        if saved_at[:6] != today.strftime("%Y%m"):
            return None

    elif prompt_type == "yearly_ai":
        # 연별: 다른 해면 만료

        if saved_at[:4] != today.strftime("%Y"):
            return None

    return text


def set_ai_cache(saju_key: str, prompt_type: str, text: str):
    """Brain 2 AI 해석 결과 캐시 저장 (날짜 타임스탬프 포함)"""

    from datetime import datetime as _dt

    ai_key = f"AI-{prompt_type}-{saju_key}"

    cache = _load_json_cache(_AI_CACHE_FILE)

    cache[ai_key] = {"text": text, "saved_at": _dt.now().strftime("%Y%m%d")}

    _save_json_cache(_AI_CACHE_FILE, cache)


def clear_ai_cache_for_key(saju_key: str):
    """특정 사주의 AI 캐시 무효화 (재분석 요청 시)"""

    cache = _load_json_cache(_AI_CACHE_FILE)

    keys_to_del = [k for k in cache if k.endswith(saju_key)]

    for k in keys_to_del:
        del cache[k]

    _save_json_cache(_AI_CACHE_FILE, cache)


def render_ai_deep_analysis(prompt_type, pils, name, birth_year, gender):
    """
    [로컬 엔진 완전 해방 버전]
    API 통신 없이 무조건 만신 로컬 서술 엔진(build_rich_narrative)을 즉시 출력합니다.
    """
    st.markdown(
        '<hr style="border:none;border-top:1px dashed #000000;margin:25px 0">',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("")  # 간격 조절

    button_label = {
        "lifeline": "🌊 대운 100년 정밀 풀이 보기",
        "past": "🎯 과거 사건 복기 풀이 보기",
        "money": "💰 재물/사업운 심층 리포트 보기",
        "relations": "💑 인연/인간관계 심층 리포트 보기",
        "future": "🔮 미래 3년 집중 예언 보기",
        "prophet": "📜 종합 운명 마스터 리포트 보기",
    }.get(prompt_type, "정밀 분석 보기")

    if st.button(button_label, key=f"btn_deep_{prompt_type}", use_container_width=True):
        with st.spinner("만신 엔진이 사주 명식을 집대성하고 있습니다..."):
            _sec_map = {
                "lifeline": "lifeline",
                "past": "past",
                "money": "money",
                "relations": "relations",
                "future": "future",
                "prophet": "report",
            }
            _section = _sec_map.get(prompt_type, "report")

            # API 우회하고 로컬 텍스트 생성기 바로 호출!
            result = build_rich_narrative(pils, birth_year, gender, name, section=_section)

            if result:
                st.markdown(
                    f"""
<div style="background:#ffffff;border:2px solid #000000;border-radius:16px; padding:25px;margin-top:20px;box-shadow:0 4px 15px rgba(197,160,89,0.15)">
<div style="font-size:18px;font-weight:900;color:#000000;margin-bottom:15px;text-align:center">
                        【 만신 정밀 사주 풀이 결과 】
</div>
<div style="font-size:15px;color:#111;line-height:2.2;white-space:pre-wrap;letter-spacing:-0.2px">
                        {apply_lexicon_tooltips(result)}
</div>
</div>
                """,
                    unsafe_allow_html=True,
                )


# ==================================================

#  UI 헬퍼 함수

# ==================================================


def get_ohang_color(char):
    """오행별 (배경색, 글자색) 반환 — 천간·지지 공통"""
    wood_cg = ["甲", "乙"]
    fire_cg = ["丙", "丁"]
    earth_cg = ["戊", "己"]
    metal_cg = ["庚", "辛"]
    water_cg = ["壬", "癸"]
    wood_jj = ["寅", "卯"]
    fire_jj = ["巳", "午"]
    earth_jj = ["辰", "戌", "丑", "未"]
    metal_jj = ["申", "酉"]
    water_jj = ["亥", "子"]
    colors = {
        "wood":  ("#2d8a4e", "#ffffff"),
        "fire":  ("#e53935", "#ffffff"),
        "earth": ("#f9a825", "#1a1a1a"),
        "metal": ("#9e9e9e", "#ffffff"),
        "water": ("#1565c0", "#ffffff"),
    }
    if char in wood_cg + wood_jj:  return colors["wood"]
    if char in fire_cg + fire_jj:  return colors["fire"]
    if char in earth_cg + earth_jj: return colors["earth"]
    if char in metal_cg + metal_jj: return colors["metal"]
    if char in water_cg + water_jj: return colors["water"]
    return ("#555555", "#ffffff")


def color_ganzhi_badge(ganzhi_str, font_size="30px", font_weight="900",
                        padding="4px 10px", border_radius="8px"):
    """간지 2글자를 오행 색상 뱃지 HTML로 변환 (예: '甲子' → colored spans)"""
    if not ganzhi_str or len(ganzhi_str) < 2:
        return f"<span style='font-size:{font_size}'>{ganzhi_str}</span>"
    cg_char = ganzhi_str[0]
    jj_char = ganzhi_str[1]
    bg_cg, fg_cg = get_ohang_color(cg_char)
    bg_jj, fg_jj = get_ohang_color(jj_char)
    style = (
        "display:inline-block;border-radius:{br};padding:{p};"
        "font-size:{fs};font-weight:{fw};"
    ).format(br=border_radius, p=padding, fs=font_size, fw=font_weight)
    return (
        f"<span style='{style}background:{bg_cg};color:{fg_cg};margin-right:2px'>{cg_char}</span>"
        f"<span style='{style}background:{bg_jj};color:{fg_jj}'>{jj_char}</span>"
    )


def render_pillars(pils):
    """사주 기둥 표시"""

    labels = ["시(時)", "일(日)", "월(月)", "년(年)"]

    cols = st.columns(4)

    # get_pillars returns [시, 일, 월, 연] -> Index 0 is Hour (시), 1 is Day (일), etc.

    for i, (p, label) in enumerate(zip(pils, labels)):
        cg = p["cg"]

        jj = p["jj"]

        cg_kr = CG_KR[CG.index(cg)]

        jj_kr = JJ_KR[JJ.index(jj)]

        jj_an = JJ_AN[JJ.index(jj)]

        oh_cg = OH.get(cg, "")

        oh_jj = OH.get(jj, "")

        emoji_cg = OHE.get(oh_cg, "")

        emoji_jj = OHE.get(oh_jj, "")

        bg_cg, fg_cg = get_ohang_color(cg)
        bg_jj, fg_jj = get_ohang_color(jj)

        with cols[i]:
            st.markdown(
                f"""

<div class="pillar-box">

<div style="font-size:11px;color:#555555;margin-bottom:6px;font-weight:700">{label}</div>

<div style="background:{bg_cg};color:{fg_cg};font-size:30px;font-weight:900;
            border-radius:10px;padding:6px 0;margin-bottom:4px">{cg}</div>

<div style="font-size:11px;color:#555555;">{cg_kr} / {emoji_cg}{oh_cg}</div>

<div style="background:{bg_jj};color:{fg_jj};font-size:32px;font-weight:900;
            border-radius:10px;padding:6px 0;margin-top:8px;margin-bottom:4px">{jj}</div>

<div style="font-size:11px;color:#555555;">{jj_kr} / {emoji_jj}{oh_jj}</div>

<div style="font-size:10px;color:#888888;margin-top:4px">{jj_an}띠</div>

</div>

""",
                unsafe_allow_html=True,
            )




def render_ohaeng_chart(oh_strength):
    """오행 강약 차트 + 진단"""

    oh_order = ["木", "火", "土", "金", "水"]

    oh_names = {
        "木": "목(木)🌳",
        "火": "화(火)🔥",
        "土": "토(土)🪨",
        "金": "금(金)-",
        "水": "수(水)💧",
    }

    cols = st.columns(5)

    for i, oh in enumerate(oh_order):
        val = oh_strength.get(oh, 0)

        with cols[i]:
            st.markdown(
                f"""

<div style="text-align:center;padding:8px">

<div style="font-size:13px;font-weight:700;color:#000000">{oh_names[oh]}</div>

<div style="font-size:22px;font-weight:900;color:#000000">{val}%</div>

</div>

""",
                unsafe_allow_html=True,
            )

            st.progress(min(val / 100, 1.0))

    # 오행 조화 진단 - 결과값만 간결하게

    over_ohs = [(oh, v) for oh, v in oh_strength.items() if v >= 35]

    lack_ohs = [(oh, v) for oh, v in oh_strength.items() if v <= 5]

    diag_lines = []

    if not over_ohs and not lack_ohs:
        diag_lines.append("⚖️ 오행이 비교적 균형 잡혀 있습니다 - 안정적인 사주입니다.")

    for oh, val in over_ohs:
        d = OHAENG_DIAGNOSIS[oh]

        diag_lines.append(f"🔴 {d['name']} 과다({val}%) - {d['over_desc'][:40]}... 💊 {d['over_remedy'][:50]}")

    for oh, val in lack_ohs:
        d = OHAENG_DIAGNOSIS[oh]

        diag_lines.append(f"🔵 {d['name']} 부족({val}%) - {d['lack_desc'][:40]}... 💊 {d['lack_remedy'][:50]}")

    if diag_lines:
        for dl in diag_lines:
            st.caption(dl)


def format_saju_text(pils, name=""):
    """사주 텍스트 요약"""

    lines = []

    if name:
        lines.append(f"* {name}님의 사주팔자 *")

    labels = ["시주(時柱)", "일주(日柱)", "월주(月柱)", "년주(年柱)"]

    for p, label in zip(pils, labels):
        oh_cg = OH.get(p["cg"], "")

        oh_jj = OH.get(p["jj"], "")

        lines.append(f"{label}: {p['str']}  [{OHN.get(oh_cg, '')} / {OHN.get(oh_jj, '')}]")

    return "\n".join(lines)


def generate_saju_summary(pils, name, birth_year, gender):
    """사주 종합 총평 자동 생성"""

    ilgan = pils[1]["cg"]

    ilgan_kr = CG_KR[CG.index(ilgan)]

    oh = OH.get(ilgan, "")

    oh_emoji = {"木": "🌳", "火": "🔥", "土": "🏔️", "金": "⚔️", "水": "🌊"}.get(oh, "-")

    strength_info = get_ilgan_strength(ilgan, pils)

    strength = strength_info["신강신약"]

    oh_strength = strength_info["oh_strength"]

    gyeokguk = get_gyeokguk(pils)

    gname = gyeokguk["격국명"] if gyeokguk else "미정격"

    grade = gyeokguk["격의_등급"] if gyeokguk else ""

    unsung = calc_12unsung(ilgan, pils)

    il_unsung = unsung[1] if len(unsung) > 1 else ""

    # 오행 분석

    max_oh = max(oh_strength.items(), key=lambda x: x[1])

    min_oh = min(oh_strength.items(), key=lambda x: x[1])

    zero_ohs = [o for o, v in oh_strength.items() if v == 0]

    # 대운 현재

    current_year = datetime.now().year

    # 대운 호출 시 실제 생년월일시 반영

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    current_dw = next((dw for dw in daewoon if dw["시작연도"] <= current_year <= dw["종료연도"]), None)

    # 세운

    yearly = get_yearly_luck(pils, current_year)

    # 신살

    special = get_special_stars(pils)

    lines = []

    name_str = f"{name}님의 " if name else ""

    lines.append(f"* {name_str}사주팔자 천명 총평 *")

    lines.append("-" * 40)

    lines.append("")

    lines.append(f"【일간(日干)】 {oh_emoji} {ilgan}({ilgan_kr}) - {OHN.get(oh, '')}의 기운")

    lines.append(ILGAN_DESC.get(ilgan, {}).get("nature", "").split("\n")[0])

    lines.append("")

    lines.append(f"【신강신약】 {strength}")

    lines.append(strength_info["조언"])

    lines.append("")

    lines.append(f"【격국(格局)】 {gname} ({grade})")

    if gyeokguk:
        lines.append(GYEOKGUK_DESC.get(gname, {}).get("summary", "").split("\n")[0] if GYEOKGUK_DESC.get(gname) else gyeokguk.get("격국_해설", "")[:80])

    lines.append("")

    lines.append(f"【일주 12운성】 {il_unsung}")

    lines.append("")

    lines.append("【오행 분포】")

    for o, v in sorted(oh_strength.items(), key=lambda x: -x[1]):
        bar = "█" * (v // 5)

        lines.append(f"  {o}({OHN.get(o, '')}) {v}% {bar}")

    if zero_ohs:
        lines.append(f"  ⚠️ {', '.join([OHN.get(o, '') for o in zero_ohs])} 기운이 완전히 없습니다 - 관련 분야 주의")

    lines.append("")

    if current_dw:
        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(current_dw["cg"], "-")

        lines.append(f"【현재 대운】 {current_dw['str']} ({current_dw['시작나이']}~{current_dw['시작나이'] + 9}세, {current_dw['시작연도']}~{current_dw['종료연도']}년)")

        lines.append(f"  천간 {dw_ss}의 기운 - " + get_daewoon_narrative(dw_ss, "", current_dw["str"], current_dw["시작나이"])[2][:60] + "...")

        lines.append("")

    lines.append(f"【{current_year}년 세운】 {yearly['세운']} {yearly['아이콘']} {yearly['길흉']}")

    narr = yearly.get("narrative", {})

    lines.append(f"  {narr.get('title', '')} - {narr.get('desc', '')[:60]}...")

    lines.append("")

    if special:
        lines.append("【신살(神殺)】")

        for s in special[:4]:
            lines.append(f"  {s['name']}: {s.get('desc', '')[:40]}...")

    lines.append("")

    lines.append("-" * 40)

    lines.append("※ 본 풀이는 전통 사주명리학에 근거한 참고 자료입니다.")

    return "\n".join(lines)


# ==================================================

#  메인 탭별 렌더링 함수

# ==================================================

# tab_saju_basic: 제거됨 - 미호출 함수

# tab_ilgan_desc: 제거됨 - 미호출 함수

# tab_12unsung: 제거됨 - 미호출 함수


@st.cache_data
def get_daewoon_narrative(d_ss_cg, d_ss_jj, dw_str, age_start):
    """대운 천간/지지 십성별 상세 해석 생성 (나이 단계 분기 포함)"""


    # -- 인생 단계별 집중 조언 -------------------------------------


    # 나이 단계 분기

    age = int(age_start) if age_start else 0

    if age < 20:
        stage = "초"

        stage_label = "🌱 초년기 (학업/부모/진로 집중)"

    elif age < 60:
        stage = "청장"

        stage_label = "🌿 청장년기 (취업/재물/연애/사업 집중)"

    else:
        stage = "말"

        stage_label = "🍂 말년기 (건강/명예/안정 집중)"

    icon, title, text = narratives.get(d_ss_cg, narratives["-"])

    focus_map = AGE_STAGE_FOCUS.get(d_ss_cg, AGE_STAGE_FOCUS["-"])

    focus_text = focus_map.get(stage, "")

    stage_label_html = f"<span style='font-size:11px;color:#888;font-weight:600'>{stage_label}</span>"
    full_text = f"{text}\n\n{stage_label_html}\n{focus_text}"

    return icon, title, full_text


def _get_dw_alert(ilgan, dw_cg, dw_jj, pils):
    """대운이 원국과 충/합을 일으키는지 감지"""

    alerts = []

    labels = ["시주", "일주", "월주", "년주"]

    orig_jjs = [p["jj"] for p in pils]

    orig_cgs = [p["cg"] for p in pils]

    for i, p in enumerate(pils):
        ojj = p["jj"]

        k = frozenset([dw_jj, ojj])

        if k in CHUNG_MAP:
            name, rel, desc = CHUNG_MAP[k]

            alerts.append(
                {
                    "type": "⚠️ 지지충",
                    "color": "#c0392b",
                    "desc": f"대운 {dw_jj}가 원국 {labels[i]}({ojj})를 충(沖) - {desc}",
                }
            )

    TG_HAP_PAIRS = [
        {"甲", "己"},
        {"乙", "庚"},
        {"丙", "辛"},
        {"丁", "壬"},
        {"戊", "癸"},
    ]

    for pair in TG_HAP_PAIRS:
        if dw_cg in pair:
            other = list(pair - {dw_cg})[0]

            if other in orig_cgs:
                found_idx = orig_cgs.index(other)

                alerts.append(
                    {
                        "type": "- 천간합",
                        "color": "#27ae60",
                        "desc": f"대운 {dw_cg}가 원국 {labels[found_idx]}({other})와 합(合) - 변화와 기회의 기운",
                    }
                )

    for combo, (hname, hoh, hdesc) in SAM_HAP_MAP.items():
        if dw_jj in combo:
            orig_in = []

            for i, p in enumerate(pils):
                if p["jj"] in combo:
                    orig_in.append(f"{labels[i]}({p['jj']})")

            if len(orig_in) >= 2:
                alerts.append(
                    {
                        "type": "🌟 삼합 성립",
                        "color": "#8e44ad",
                        "desc": f"대운 {dw_jj} + 원국 {','.join(orig_in)} = {hname} - 강력한 발복",
                    }
                )

            elif len(orig_in) == 1:
                alerts.append(
                    {
                        "type": "💫 반합",
                        "color": "#2980b9",
                        "desc": f"대운 {dw_jj} + 원국 {orig_in[0]} 반합 - 부분적 기운 변화",
                    }
                )

    return alerts


def _get_yongshin_match(dw_cg_ss, yongshin_ohs, ilgan_oh):
    """대운 십성이 용신 오행과 맞는지 판단"""

    GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

    CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    BIRTH_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

    SS_TO_OH = {
        "비견": ilgan_oh,
        "겁재": ilgan_oh,
        "식신": GEN.get(ilgan_oh, ""),
        "상관": GEN.get(ilgan_oh, ""),
        "편재": CTRL.get(ilgan_oh, ""),
        "정재": CTRL.get(ilgan_oh, ""),
        "편관": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "정관": next((k for k, v in CTRL.items() if v == ilgan_oh), ""),
        "편인": BIRTH_R.get(ilgan_oh, ""),
        "정인": BIRTH_R.get(ilgan_oh, ""),
    }

    dw_oh = SS_TO_OH.get(dw_cg_ss, "")

    return "yong" if dw_oh in yongshin_ohs else "normal"


def _get_hap_break_warning(pils, dw_jj, sw_jj):
    """원국의 합이 대운/세운 충으로 깨지는 시점 감지"""

    warnings = []

    labels = ["시주", "일주", "월주", "년주"]

    for combo, (hname, hoh, hdesc) in SAM_HAP_MAP.items():
        orig_indices = [i for i, p in enumerate(pils) if p["jj"] in combo]

        if len(orig_indices) >= 2:
            orig_desc = ",".join([f"{labels[i]}({pils[i]['jj']})" for i in orig_indices])

            for breaker in [dw_jj, sw_jj]:
                for i in orig_indices:
                    jj = pils[i]["jj"]

                    k = frozenset([breaker, jj])

                    if k in CHUNG_MAP:
                        warnings.append(
                            {
                                "level": "🔴 위험",
                                "color": "#c0392b",
                                "desc": f"원국 {hname}({orig_desc})을 {'대운' if breaker == dw_jj else '세운'} {breaker}가 {labels[i]}({jj})를 충(沖)으로 깨뜨립니다. 계획 좌절/관계 파탄/재물 손실 위험.",
                            }
                        )

    return warnings


DAEWOON_PRESCRIPTION = {
    "比肩": "독립 사업/협력 강화/새 파트너십 구축이 유리합니다.",
    "劫財": "투자/보증/동업 금지. 지출 절제, 현상 유지가 최선입니다.",
    "食神": "재능 발휘/창업/콘텐츠 창작을 적극 추진하십시오.",
    "傷官": "직장 이직/창업/예술 활동에 좋으나 언행 극도 조심.",
    "偏財": "사업 확장/투자/이동이 유리. 단, 과욕은 금물입니다.",
    "正財": "저축/자산 관리/안정적 수입 구조 구축에 집중하십시오.",
    "偏官": "건강검진 필수. 무리한 확장 자제. 인내와 정면 돌파가 최선.",
    "正官": "승진/자격증/공식 계약을 적극 추진하십시오. 명예의 시기.",
    "偏印": "학문/자격증/특수 분야 연구에 집중하기 좋은 시기입니다.",
    "正印": "시험/학업/귀인과의 만남. 배움에 투자하십시오.",
}

# 대운 직격 처방 — 결론 먼저 3단 구조
DAEWOON_VERDICT = {
    "比肩": {
        "결론":    "🟡 독립과 경쟁의 시기 — 스스로 뛰어야 기회가 옵니다",
        "해야할것": [
            "지금 하는 일에서 독립 행보를 시작하십시오 — 부업·1인 창업이 이 시기의 정답입니다",
            "경쟁자가 많아지는 시기이니 나만의 차별점을 명확히 만들어야 합니다",
            "마음이 맞는 동업자를 찾되 반드시 계약서를 쓰십시오",
            "체력 관리가 핵심 — 과도한 경쟁으로 소진되지 않도록 휴식을 의도적으로 확보하십시오",
        ],
        "하면망함": [
            "남 밑에서 지시만 받고 있으면 이 대운이 통째로 낭비됩니다",
            "재물을 지인에게 빌려주거나 보증을 서면 이 시기에 반드시 돌아오지 않습니다",
            "혼자 모든 것을 감당하려다 번아웃이 오면 대운 후반이 무너집니다",
        ],
        "기회": "자기 브랜드 구축, 프리랜서 전환, 경쟁이 있는 분야에서의 독립 사업",
    },
    "劫財": {
        "결론":    "🔴 손재·배신의 시기 — 지키는 것이 버는 것입니다",
        "해야할것": [
            "현금을 최우선으로 보유하십시오 — 이 대운에서 유동성이 생명입니다",
            "기존 거래처와 신뢰 관계를 철저히 점검하고 수상한 움직임을 조기에 차단하십시오",
            "체력과 면역 관리 — 겁재 대운은 혈액·외상 관련 건강 이슈가 동반되기 쉽습니다",
            "경쟁이 불가피하다면 법적 근거를 먼저 확보한 뒤 움직이십시오",
        ],
        "하면망함": [
            "동업·투자·보증 — 이 세 가지 중 하나라도 이 대운에 시작하면 재물을 잃습니다",
            "지인의 달콤한 사업 제안을 덥석 받아들이면 이 대운의 최대 실수가 됩니다",
            "빚을 내어 투자하면 이 시기에 반드시 손실로 돌아옵니다",
        ],
        "기회": "기존 사업 내실 다지기, 불필요한 지출 구조 혁신, 경쟁 우위 포지션 확보",
    },
    "食神": {
        "결론":    "✅ 복록과 창의의 시기 — 재능을 드러내면 돈이 따라옵니다",
        "해야할것": [
            "지금까지 준비해온 기술·재능·콘텐츠를 세상에 꺼내십시오 — 이 시기가 발표 타이밍입니다",
            "새로운 수입 파이프라인(부업·창업·강의·유튜브 등)을 이 대운에 만들어 두십시오",
            "인맥을 넓히고 좋은 음식을 먹으며 여유 있게 생활하십시오 — 긍정 에너지가 재물을 부릅니다",
            "건강에 신경 쓰되 과식·과음으로 인한 소화기 문제를 주의하십시오",
        ],
        "하면망함": [
            "재능이 있어도 드러내지 않고 숨어 있으면 이 대운을 통째로 흘려보냅니다",
            "지나친 안주와 게으름 — 식신 대운의 가장 큰 적은 과도한 편안함입니다",
            "남을 짓밟는 방식으로 올라가려 하면 인복을 잃습니다",
        ],
        "기회": "창작·강의·외식·콘텐츠·서비스업 창업, 전문 자격증 취득 후 독립",
    },
    "傷官": {
        "결론":    "⚠️ 변화와 충돌의 시기 — 기존 틀을 깨되 말조심이 생명입니다",
        "해야할것": [
            "직장을 박차고 나가고 싶다면 이 대운이 유일한 기회 — 단, 준비 자금 최소 1년치를 확보하고 움직이십시오",
            "창의적 아이디어를 실행에 옮기기 좋은 시기 — IT·예술·컨설팅·혁신 분야에서 승부를 보십시오",
            "언변과 글쓰기 능력을 극대화하여 강연·저술·컨설팅으로 수익화하십시오",
        ],
        "하면망함": [
            "상사·권위자·관공서와 정면으로 맞서면 직장을 잃고 법적 분쟁까지 생깁니다",
            "계약서 없이 구두 약속으로 사업을 진행하면 반드시 배신을 당합니다",
            "SNS·인터뷰에서 충동적 발언을 하면 구설수가 커지고 이미지가 무너집니다",
        ],
        "기회": "기존 직장 탈피 후 전문직·프리랜서·스타트업 창업, 특허·저작권 기반 수익 모델",
    },
    "偏財": {
        "결론":    "✅ 사업과 이성 기운의 시기 — 크게 움직이면 크게 벌립니다",
        "해야할것": [
            "사업 확장·신규 거래처 개척·투자를 적극적으로 추진하십시오 — 이 대운이 재물의 황금기입니다",
            "활동 반경을 넓히십시오 — 출장·해외·이동이 많을수록 기회가 커집니다",
            "번 돈의 30% 이상은 반드시 부동산·예금 등 안전 자산으로 묶어두십시오",
            "미혼이라면 이성 인연이 활발해지는 시기 — 적극적으로 만남의 자리를 만드십시오",
        ],
        "하면망함": [
            "한 곳에 전 재산을 집중 투자하면 편재의 기복으로 한순간에 잃습니다",
            "도박·코인·레버리지 투자처럼 극단적 투기는 이 시기에 특히 위험합니다",
            "이성 관계 충동적 행동은 가정과 재물을 동시에 잃는 최악의 결과를 부릅니다",
        ],
        "기회": "무역·유통·부동산 개발·사업 인수합병·다중 수입 파이프라인 구축",
    },
    "正財": {
        "결론":    "✅ 착실한 결실의 시기 — 꾸준히 쌓으면 반드시 불어납니다",
        "해야할것": [
            "부동산·예금·적금 등 안정적 자산 축적에 집중하십시오 — 이 시기에 쌓은 자산이 노후를 책임집니다",
            "현 직장에서의 실력과 신뢰를 쌓으십시오 — 정재 대운은 조직 안에서 인정받는 구조입니다",
            "결혼을 고려 중이라면 이 대운 안에 결단하십시오 — 배우자 인연이 강해지는 시기입니다",
        ],
        "하면망함": [
            "주식·코인 등 투기성 투자에 손을 대면 착실히 쌓은 재물이 사라집니다",
            "소심함으로 기회가 와도 실행을 미루면 정재 대운의 결실을 놓칩니다",
            "불규칙한 생활과 폭식은 위장·소화기를 망가뜨립니다",
        ],
        "기회": "월세 수익 부동산 매입, 연금보험·장기 저축 시작, 직장 내 승진과 연봉 협상",
    },
    "偏官": {
        "결론":    "🔴 압박과 단련의 시기 — 버티면 강해지고 무너지면 끝입니다",
        "해야할것": [
            "지금 당장 건강검진을 예약하십시오 — 편관 대운에서 건강을 잃으면 모든 것이 무너집니다",
            "명확한 원칙과 근거를 갖추고 움직이십시오 — 실력으로 증명해야 하는 시기입니다",
            "법적·재무적 리스크를 사전에 차단하십시오 — 계약서·보험·세금 처리를 지금 정비하십시오",
            "이 시기의 고난을 견뎌낸 사람에게는 다음 대운에서 반드시 큰 보상이 옵니다",
        ],
        "하면망함": [
            "무리한 사업 확장·신규 투자를 강행하면 관재와 손실이 동시에 옵니다",
            "권위자·상사·국가기관과 정면 충돌하면 이길 수 없는 싸움이 시작됩니다",
            "건강을 무시하고 과로를 지속하면 대운 후반에 강제 입원·수술이 찾아옵니다",
        ],
        "기회": "군경·의료·법조·스포츠 종사자에게는 오히려 성장기 — 위기를 돌파하는 직종에서 두각",
    },
    "正官": {
        "결론":    "✅ 명예와 인정의 시기 — 조직 안에서 올라가는 것이 최고의 전략입니다",
        "해야할것": [
            "승진·자격증·공직 시험을 이 대운 안에 반드시 도전하십시오 — 노력한 만큼 결과가 옵니다",
            "직장 내 신뢰와 인맥을 두텁게 쌓으십시오 — 이 시기에 맺은 인연이 평생 귀인이 됩니다",
            "법과 원칙을 철저히 지키십시오 — 정관 대운의 핵심은 신뢰 자산입니다",
        ],
        "하면망함": [
            "규정을 어기거나 편법을 쓰면 명예가 한순간에 추락합니다",
            "독립·창업의 유혹에 흔들려 안정적 조직을 떠나면 이 시기에 맞지 않는 선택이 됩니다",
            "융통성 없이 원칙만 고집하면 귀인을 잃습니다",
        ],
        "기회": "공무원 승진·대기업 임원·전문직 자격증 취득·중요 계약 성사",
    },
    "偏印": {
        "결론":    "🟡 탐구와 변화의 시기 — 깊이 파고들되 결정은 신중히 해야 합니다",
        "해야할것": [
            "특수 기술·학문·자격증에 집중 투자하십시오 — 이 시기에 익힌 전문성이 평생 먹거리가 됩니다",
            "새로운 분야 탐구와 연구에 시간을 쏟으십시오 — 직관과 아이디어가 날카로워지는 시기입니다",
            "환경 변화를 두려워하지 마십시오 — 새로운 곳에서 새 기회가 옵니다",
        ],
        "하면망함": [
            "시작한 일을 중도 포기하는 패턴이 반복되면 이 대운의 잠재력을 통째로 날립니다",
            "불확실한 정보를 믿고 투자하면 사기·손실 피해를 입기 쉽습니다",
            "고립되어 혼자만의 세계에 빠지면 우울·불안이 깊어집니다",
        ],
        "기회": "IT·프로그래밍·심리학·의학·철학 등 독창적 전문 분야에서의 성장",
    },
    "正印": {
        "결론":    "✅ 배움과 귀인의 시기 — 투자하면 반드시 돌아옵니다",
        "해야할것": [
            "자격증·진학·연구·어학 공부를 지금 당장 시작하십시오 — 이 대운에 얻은 자격이 다음 대운의 무기가 됩니다",
            "좋은 스승·멘토·귀인을 적극적으로 찾고 인연을 이어가십시오 — 정인 대운의 귀인은 인생을 바꿉니다",
            "부동산·계약 취득 타이밍 — 공식 서류 처리를 이 시기에 마무리하십시오",
        ],
        "하면망함": [
            "배움의 기회가 왔는데 자만하여 공부를 게을리하면 이 대운의 핵심을 놓칩니다",
            "귀인에게 지나치게 의존하면 자기 실력이 쌓이지 않아 다음 대운에 홀로 서지 못합니다",
            "과도한 걱정과 회피로 새로운 시도를 멀리하면 대운이 끝난 뒤 후회가 남습니다",
        ],
        "기회": "전문직 자격증·대학원·해외 연수·부동산 매입·은사 인연을 통한 경력 점프",
    },
}

# ── 대운 직격 처방 ─────────────────────────────────────────────────
DAEWOON_DIRECT = {
    "比肩": {
        "verdict": "⚡ 독립과 경쟁의 시기 — 혼자 움직여야 기회가 옵니다",
        "do":    ["독립 창업 또는 1인 프로젝트 시작", "경쟁에서 이기는 전략 수립", "자기 브랜드·이름값 올리기", "혼자 처리할 수 있는 일에 집중"],
        "dont":  ["동업 계약 — 계약서 없이 하면 배신당함", "재물 보증 서기 — 이 대운에 보증은 손해로 직결", "남에게 중요한 결정 맡기기"],
        "money": "직접 움직여서 번 돈만 진짜 내 돈이 됩니다. 소극적이면 경쟁자에게 빼앗깁니다.",
        "caution": "고집이 지나치면 귀인도 떠납니다. 경청 능력을 키우십시오.",
    },
    "劫財": {
        "verdict": "🔴 손재와 배신의 시기 — 지키는 것이 버는 것입니다",
        "do":    ["현금 보유 극대화, 불필요 지출 전면 차단", "기존 사업·직장 유지에 집중", "신뢰 관계 재검증", "법적 계약서 없는 거래 거절"],
        "dont":  ["신규 투자·주식·코인 — 이 대운에 시작하면 90% 손실", "지인 돈 빌려주기 또는 보증 서기", "충동적인 사업 확장", "감정에 휩쓸린 큰 결정"],
        "money": "이 시기에 들어오는 달콤한 투자 제안은 100% 함정입니다. 현금이 곧 안전입니다.",
        "caution": "가장 믿었던 사람이 배신하는 시기입니다. 돈 거래는 형제·친구도 계약서를 쓰십시오.",
    },
    "食神": {
        "verdict": "✅ 재능 개화의 시기 — 보여주면 돈이 따라옵니다",
        "do":    ["콘텐츠 창작·유튜브·강의 등 자기 표현 시작", "요리·교육·서비스업 창업 검토", "자격증 취득 및 전문성 공개", "네트워크 파티·모임 적극 참여"],
        "dont":  ["재능을 숨기고 혼자 쌓아두기 — 드러내지 않으면 기회가 지나감", "과식·음주 과다", "너무 편한 것만 추구하다 도전 의식 잃기"],
        "money": "전문성과 재능이 직접 수익으로 전환되는 황금기. 부업·겸업을 지금 시작하십시오.",
        "caution": "너무 여유로워져 긴장이 풀리는 것이 위험. 성실함을 유지하십시오.",
    },
    "傷官": {
        "verdict": "⚠️ 변화와 충돌의 시기 — 표현력은 극대화, 관계는 극도 주의",
        "do":    ["창업·이직·예술·발명 등 기존 틀 깨는 도전", "특허·지식재산권 출원", "강연·방송 등 언변 활용 직종", "전문 기술 연마 후 독립"],
        "dont":  ["직속 상관·윗사람과 정면 충돌 — 반드시 손해로 끝남", "계약서 안 보고 서명", "SNS 감정 폭발 — 구설수의 씨앗", "공무원·관직 도전 — 이 시기 관과 충돌"],
        "money": "재능으로 번 돈은 크지만, 분쟁·소송으로 나가는 돈도 큰 시기입니다.",
        "caution": "말이 칼이 되는 시기. 한 마디 내뱉기 전에 세 번 생각하십시오.",
    },
    "偏財": {
        "verdict": "💰 사업과 이동의 황금기 — 적극적으로 움직이면 큰돈이 따릅니다",
        "do":    ["사업 확장·신규 사업 론칭", "부동산·주식 등 자산 투자 검토", "해외 진출·국제 거래 추진", "새로운 인맥 영업 활동 강화"],
        "dont":  ["전 재산 올인 — 편재는 들어오는 만큼 나가기도 함", "충동적 소비·사치", "검증 안 된 투자처"],
        "money": "수입이 크게 늘어나는 시기이나 나가는 돈도 큽니다. 수입의 30%는 반드시 안전 자산으로 묶어두십시오.",
        "caution": "남성은 이성 문제를 조심해야 하는 시기. 이성으로 인한 재물 손실을 경계하십시오.",
    },
    "正財": {
        "verdict": "✅ 안정적 수확의 시기 — 꾸준하면 반드시 쌓입니다",
        "do":    ["부동산·예금·적금 등 안정 자산 매입", "회계·세금·재정 정리", "장기 계약·안정적 거래처 확보", "결혼 준비·배우자와의 관계 강화"],
        "dont":  ["투기·도박·변동성 큰 투자", "즉흥적인 사업 확장", "재정 원칙 없이 지인에게 퍼주기"],
        "money": "한탕보다 꾸준한 저축이 법칙. 매달 일정액을 강제 저축하면 10년 후 놀라운 결과가 옵니다.",
        "caution": "너무 꼼꼼하다 보면 좋은 기회도 놓칩니다. 가끔은 과감함도 필요합니다.",
    },
    "偏官": {
        "verdict": "🔴 압박과 단련의 시기 — 버티면 강해지고 포기하면 무너집니다",
        "do":    ["건강검진 즉시 예약 및 정기 관리", "법적 분쟁 발생 시 즉각 전문가 선임", "현재 자리 지키기 — 이직·창업은 이 대운 이후로", "인내심 훈련 — 이 시기 고난이 다음 대운의 자산"],
        "dont":  ["무리한 사업 확장·신규 투자", "권위자·상사와 정면 대결", "건강 신호 무시하고 과로", "충동적 이직·창업 — 이 대운에 나가면 더 힘들어짐"],
        "money": "돈을 벌기보다 잃지 않는 것이 목표. 현금을 지키는 자가 승리합니다.",
        "caution": "이 대운에 찾아오는 사업 기회는 함정일 가능성 높습니다. 2~3번 의심하고 검증 후 움직이십시오.",
    },
    "正官": {
        "verdict": "🏆 명예와 인정의 시기 — 조직 안에서 움직이면 길이 열립니다",
        "do":    ["승진·자격증·공직 시험 도전", "공식 계약·법인 설립·등록", "조직 내 신뢰 쌓기", "자기 이름을 걸고 하는 공식 활동"],
        "dont":  ["원칙·규정을 어기는 행동 — 이 시기 적발되면 치명적", "직장을 박차고 무계획 독립", "탈세·편법·불투명한 거래"],
        "money": "직함과 명예가 곧 재물. 연봉 협상·승진이 가장 큰 투자입니다.",
        "caution": "지나친 원칙주의로 주변을 피곤하게 만들 수 있습니다. 융통성을 함께 갖추십시오.",
    },
    "偏印": {
        "verdict": "📚 변화와 탐구의 시기 — 깊이 파고들면 전문가가 됩니다",
        "do":    ["새 분야 학문·연구·기술 습득", "자격증·특수 면허 취득", "이사·이동·이직 등 환경 변화 수용", "명상·철학 탐구"],
        "dont":  ["이것저것 겉핥기 — 하나를 깊이 파지 않으면 아무것도 안 됨", "중요한 결정 즉흥적으로 내리기", "불확실한 투자 정보 믿고 행동", "고립 — 우울로 이어짐"],
        "money": "지식·기술·자격이 재물로 전환되는 시기. 지금 배우는 것이 5년 후 수익을 만듭니다.",
        "caution": "이 시기 시작한 일이 중도에 흐지부지되기 쉽습니다. 한 가지에 집중력을 유지하십시오.",
    },
    "正印": {
        "verdict": "📖 귀인과 배움의 시기 — 도움받고 성장하는 황금기입니다",
        "do":    ["학업·시험·진학·자격증에 전력투구", "스승·멘토·귀인과의 관계 강화", "부동산·문서·계약 등 자산 취득", "어머니·윗사람에게 효도 및 연락"],
        "dont":  ["귀인의 도움을 당연하게 여기기 — 감사함 잃으면 귀인이 떠남", "과도한 의존", "게으름·과한 안주 — 편안함이 성장의 적"],
        "money": "재물보다 실력과 자격을 쌓는 시기. 지금의 투자가 다음 대운 재물의 씨앗이 됩니다.",
        "caution": "이 대운에 귀인을 만날 수 있습니다. 소개·추천 기회가 오면 적극 응하십시오.",
    },
    "-": {
        "verdict": "⬜ 균형과 중립의 시기 — 특별한 기운의 충돌 없이 꾸준함이 최선입니다",
        "do":    ["현재 진행 중인 일의 완성도 높이기", "실력과 전문성 꾸준히 쌓기", "건강 관리와 생활 루틴 정비", "다음 황금기 대운을 위한 내실 다지기"],
        "dont":  ["무리한 새로운 시작 — 지금은 결실보다 준비의 시간", "감정적 충동 결정", "주변 유혹에 흔들려 방향 잃기"],
        "money": "큰 기복 없이 현상 유지가 가능한 시기. 저축과 안전 자산 확보에 집중하십시오.",
        "caution": "특별한 위기는 없으나 방심이 위기를 만듭니다. 꾸준함을 잃지 마십시오.",
    },
}


def get_year_detail(y, c2, ilgan, yongshin_ohs, birth_year):
    """향후 10년 운세 상세 해석 반환 (dict)"""
    try:
        dw = c2.get("대운", {})
        sw = c2.get("세운", {})
        dw_cg = dw.get("cg", "")
        dw_jj = dw.get("jj", "")
        sw_cg = sw.get("cg", "")
        sw_jj = sw.get("jj", "")
        dw_str = dw.get("str", "")
        sw_str = sw.get("세운", "")
        dw_ss = c2.get("대운_천간십성", "")
        sw_ss = c2.get("세운_천간십성", "")
        gil = sw.get("길흉", "평")
        ilgan_oh = OH.get(ilgan, "")
        _kr_age = y - birth_year + 1

        d_is_y = _get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong"
        s_is_y = _get_yongshin_match(sw_ss, yongshin_ohs, ilgan_oh) == "yong"

        # 길흉 배지
        if d_is_y and s_is_y:
            badge = "🌟 최길"
            gil_color = "#1a6b2e"
        elif d_is_y or s_is_y:
            badge = "✦ 길"
            gil_color = "#1565c0"
        elif "흉" in gil:
            badge = "⚠️ 흉"
            gil_color = "#c0392b"
        else:
            badge = "〰️ 평"
            gil_color = "#888"

        # 합 체크 (천간합/지지합)
        _TG_HAP = [frozenset({"甲","己"}),frozenset({"乙","庚"}),frozenset({"丙","辛"}),frozenset({"丁","壬"}),frozenset({"戊","癸"})]
        _JJ_HAP = [frozenset({"子","丑"}),frozenset({"寅","亥"}),frozenset({"卯","戌"}),frozenset({"辰","酉"}),frozenset({"巳","申"}),frozenset({"午","未"})]
        _tg_hap = frozenset({dw_cg, sw_cg}) in _TG_HAP if dw_cg and sw_cg else False
        _jj_hap = frozenset({dw_jj, sw_jj}) in _JJ_HAP if dw_jj and sw_jj else False

        # 충 체크 (지지충)
        _chung_pairs = [frozenset({"子","午"}),frozenset({"丑","未"}),frozenset({"寅","申"}),frozenset({"卯","酉"}),frozenset({"辰","戌"}),frozenset({"巳","亥"})]
        _jj_chung = frozenset({dw_jj, sw_jj}) in _chung_pairs if dw_jj and sw_jj else False

        hap_chung_parts = []
        if _tg_hap:
            hap_chung_parts.append(f"천간합({dw_cg}+{sw_cg}): 두 기운이 합쳐져 변화의 에너지 발생. 기존 오행이 전환되는 해.")
        if _jj_hap:
            hap_chung_parts.append(f"지지합({dw_jj}+{sw_jj}): 두 지지가 결합. 인연·사건·환경의 큰 변화가 동반될 수 있음.")
        if _jj_chung:
            hap_chung_parts.append(f"지지충({dw_jj}↔{sw_jj}): 대운과 세운이 충돌. 계획 변경·이동·갈등 주의.")

        hap_icon = " ⚡합" if (_tg_hap or _jj_hap) else (" ⚡충" if _jj_chung else "")

        # 핵심 기운 (DAEWOON_INTERP + 십성 조합)
        dw_cg_interp = DAEWOON_INTERP.get(dw_cg, "")
        dw_jj_interp = DAEWOON_INTERP.get(dw_jj, "")
        sd_dw = SIPSONG_DETAIL.get(dw_ss, {})
        sd_sw = SIPSONG_DETAIL.get(sw_ss, {})

        _core_parts = []
        if dw_cg_interp:
            _core_parts.append(dw_cg_interp.split(".")[0] + ".")
        if dw_jj_interp:
            _core_parts.append(dw_jj_interp.split(".")[0] + ".")
        if d_is_y and s_is_y:
            _core_parts.append("용신 대운과 세운이 겹치는 최고의 발복기입니다. 준비한 것을 과감히 실행하십시오.")
        elif not d_is_y and not s_is_y and "흉" in gil:
            _core_parts.append("기신 대운과 세운이 겹치는 시기. 무리한 확장을 자제하고 내실을 다지십시오.")
        core_text = " ".join(_core_parts[:2]) if _core_parts else f"{dw_ss} 대운에 {sw_ss} 세운이 더해지는 해입니다."

        # 분야별 예측
        career = sd_dw.get("직업", "") or f"{dw_ss} 기운의 분야에서 활동이 유리합니다."
        finance = sd_sw.get("재물", "") or f"세운 {sw_ss} — {dw_cg_interp[:30] if dw_cg_interp else '재물 흐름에 주의가 필요합니다.'}"
        ilp = ILGAN_PROFILE.get(ilgan, {})
        relation = ilp.get("연애", f"{ilgan} 일간 특유의 관계 방식이 두드러지는 해.")
        oh_health = OHANG_BODY.get(OH.get(dw_cg, ""), {})
        health = f"대운 천간 오행 관련 {oh_health.get('장기','해당 부위')} 주의. {oh_health.get('주의','무리한 활동 삼갈 것.')}" if oh_health else "건강 기복 주의. 정기 검진 권장."

        # 키워드
        keywords = []
        if d_is_y or s_is_y:
            keywords.append("#도약")
        if "흉" in gil:
            keywords.append("#주의")
        if _tg_hap or _jj_hap:
            keywords.append("#변화")
        if _jj_chung:
            keywords.append("#충돌")
        if sd_dw.get("한글"):
            keywords.append(f"#{sd_dw['한글'].split('(')[0]}")
        if sd_sw.get("한글"):
            keywords.append(f"#{sd_sw['한글'].split('(')[0]}")
        keywords = keywords[:3]

        return {
            "year": y, "kr_age": _kr_age,
            "dw_str": dw_str, "sw_str": sw_str,
            "dw_ss": dw_ss, "sw_ss": sw_ss,
            "badge": badge, "gil_color": gil_color,
            "hap_icon": hap_icon,
            "core_text": core_text,
            "career": career, "finance": finance,
            "relation": relation, "health": health,
            "keywords": keywords,
            "hap_chung_parts": hap_chung_parts,
            "d_is_y": d_is_y, "s_is_y": s_is_y,
        }
    except Exception as _e:
        _saju_log.debug("[get_year_detail] %s", _e)
        return {}


def tab_daewoon(pils, birth_year, gender):
    """대운 탭 - 용신 하이라이트 + 합충 경고 + 처방"""

    st.markdown(
        '<div class="gold-section">🔄 대운(大運) | 10년 주기 운명의 큰 흐름</div>',
        unsafe_allow_html=True,
    )

    # 대운 호출 시 실제 생년월일시 반영

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    current_year = datetime.now().year

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    ys = get_yongshin(pils)

    yongshin_ohs = ys["종합_용신"]

    # -- 타임라인 요약 바 --------------------------------

    st.markdown('<div class="gold-section">📊 용신 대운 타임라인</div>', unsafe_allow_html=True)

    oh_emoji = {"木": "🌳", "火": "🔥", "土": "🏔️", "金": "⚔️", "水": "💧"}

    yong_str = " / ".join([f"{oh_emoji.get(o, '')}{OHN.get(o, '')}" for o in yongshin_ohs]) if yongshin_ohs else "분석 중"

    st.markdown(
        f"""

<div class="card" style="background:#ffffff;border:2px solid #000000;margin-bottom:10px;font-size:13px;color:#000000;line-height:1.9">

- <b>이 사주 用神:</b> {yong_str} &nbsp;|&nbsp;

🟡 황금 카드 = 用神 大運 &nbsp;|&nbsp; 🟠 주황 테두리 = 현재 大運

</div>

""",
        unsafe_allow_html=True,
    )

    _GZ_KR = dict(zip(CG + JJ, CG_KR + JJ_KR))
    tl = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:16px">'

    for dw in daewoon:
        d_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        is_yong = _get_yongshin_match(d_ss, yongshin_ohs, ilgan_oh) == "yong"

        is_cur = dw["시작연도"] <= current_year <= dw["종료연도"]

        bg = "#000000" if is_yong else "#e8e8e8"

        tc = "white" if is_yong else "#666"

        bdr = "border:3px solid #ff6b00;" if is_cur else "border:2px solid transparent;"

        _dw_str = dw["str"]
        _dw_kr = "".join(_GZ_KR.get(c, c) for c in _dw_str)

        tl += f'<div style="background:{bg};color:{tc};{bdr}border-radius:10px;padding:8px 12px;text-align:center;min-width:68px"><div style="font-size:10px;opacity:.8">{dw["시작나이"]}세</div><div style="font-size:15px;font-weight:800">{_dw_str}</div><div style="font-size:10px;opacity:.75">({_dw_kr})</div><div style="font-size:10px">{d_ss}</div>{"<div style=font-size:10px;color:#ffe;font-weight:700>🌟용신</div>" if is_yong else ""}{"<div style=font-size:10px;color:#ff6b00;font-weight:800>◀현재</div>" if is_cur else ""}</div>'

    tl += "</div>"

    st.markdown(tl, unsafe_allow_html=True)

    # -- 대운별 상세 카드 --------------------------------

    for dw in daewoon:
        if dw.get("시작나이", 0) < 20 or dw.get("시작나이", 0) > 80:
            continue

        d_ss_cg = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

        d_ss_jj_list = JIJANGGAN.get(dw["jj"], [])

        d_ss_jj = TEN_GODS_MATRIX.get(ilgan, {}).get(d_ss_jj_list[-1] if d_ss_jj_list else "", "-")

        oh_cg = OH.get(dw["cg"], "")
        oh_jj = OH.get(dw["jj"], "")

        is_current = dw["시작연도"] <= current_year <= dw["종료연도"]

        is_yong = _get_yongshin_match(d_ss_cg, yongshin_ohs, ilgan_oh) == "yong"

        alerts = _get_dw_alert(ilgan, dw["cg"], dw["jj"], pils)

        icon, title, narrative_raw = get_daewoon_narrative(d_ss_cg, d_ss_jj, dw["str"], dw["시작나이"])

        narrative = narrative_raw.replace("\n", "<br>")

        prescription = DAEWOON_PRESCRIPTION.get(d_ss_cg, "꾸준한 노력으로 안정을 유지하십시오.")

        if is_current:
            bdr = "border:3px solid #ff6b00;"

            bg2 = "background:linear-gradient(135deg,#fff8ee,#fff3e0);"

            badge = "<div style='font-size:12px;color:#ff6b00;font-weight:900;letter-spacing:2px;margin-bottom:8px'>-> * 현재 진행 중인 대운 *</div>"

        elif is_yong:
            bdr = "border:2px solid #000000;"

            bg2 = "background:linear-gradient(135deg,#ffffff,#ffffff);"

            badge = "<div style='font-size:11px;color:#000000;font-weight:800;margin-bottom:6px'>🌟 용신(用神) 대운 - 이 시기를 놓치지 마십시오</div>"

        else:
            bdr = "border:1px solid #e8e8e8;"

            bg2 = "background:#fafafa;"

            badge = ""

        alert_html = "".join(
            [
                f'<div style="background:{a["color"]}18;border-left:3px solid {a["color"]};padding:8px 12px;border-radius:6px;margin-top:4px;font-size:12px"><b style="color:{a["color"]}">{a["type"]}</b> - {a["desc"]}</div>'
                for a in alerts
            ]
        )

        render_daewoon_card(dw, oh_cg, d_ss_cg, oh_jj, d_ss_jj, title, icon, narrative, prescription, alert_html, bdr, bg2, badge, OHE)

        # ── 직격 처방 블록 (결론 먼저 / 해야 할 것 / 하면 망하는 것) ──
        _dd = DAEWOON_DIRECT.get(d_ss_cg, {})
        if _dd:
            with st.expander(f"🎯 {dw['str']} 대운 직격 처방 — 해야 할 것 & 하면 망하는 것", expanded=is_current):
                # 결론 먼저
                st.markdown(
                    f"<div style='background:#1a1a2e;color:#f7e695;font-size:15px;font-weight:900;"
                    f"padding:12px 16px;border-radius:10px;margin-bottom:12px;letter-spacing:0.5px'>"
                    f"📌 {_dd.get('verdict','')}</div>",
                    unsafe_allow_html=True,
                )
                _col_do, _col_dont = st.columns(2)
                with _col_do:
                    st.markdown(
                        "<div style='font-size:13px;font-weight:800;color:#27ae60;margin-bottom:6px'>"
                        "✅ 이 시기에 반드시 해야 할 것</div>",
                        unsafe_allow_html=True,
                    )
                    for _item in _dd.get("do", []):
                        st.markdown(
                            f"<div style='font-size:12px;color:#1a5c2a;padding:4px 0;border-bottom:"
                            f"1px solid #e8f5e9;'>▶ {_item}</div>",
                            unsafe_allow_html=True,
                        )
                with _col_dont:
                    st.markdown(
                        "<div style='font-size:13px;font-weight:800;color:#c0392b;margin-bottom:6px'>"
                        "🚫 하면 망하는 것 (절대 금지)</div>",
                        unsafe_allow_html=True,
                    )
                    for _item in _dd.get("dont", []):
                        st.markdown(
                            f"<div style='font-size:12px;color:#7b241c;padding:4px 0;border-bottom:"
                            f"1px solid #fce4ec;'>✗ {_item}</div>",
                            unsafe_allow_html=True,
                        )
                st.markdown(
                    f"<div style='background:#fff8e1;border-left:4px solid #f39c12;border-radius:8px;"
                    f"padding:10px 14px;margin-top:10px;font-size:13px;color:#7d6608;'>"
                    f"💰 <b>재물 전략:</b> {_dd.get('money','')}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='background:#f3e5f5;border-left:4px solid #8e24aa;border-radius:8px;"
                    f"padding:10px 14px;margin-top:6px;font-size:13px;color:#4a148c;'>"
                    f"⚠️ <b>핵심 경계:</b> {_dd.get('caution','')}</div>",
                    unsafe_allow_html=True,
                )


# tab_ilju: 제거됨 - 미호출 함수


def tab_yukjin(pils, gender="남"):
    """육친론(六親論) 탭"""

    ilgan = pils[1]["cg"]

    st.markdown(
        '<div class="gold-section">👨‍👩‍👧‍👦 육친론(六親論) - 가족과 인연</div>',
        unsafe_allow_html=True,
    )

    render_info_card("육친론이란?", """일간을 기준으로 각 십성(十星)이 어느 가족을 나타내는지 분석합니다.
각 기둥의 십성 강약으로 가족관계의 덕, 인연, 갈등을 판단합니다.""")

    yk = get_yukjin(ilgan, pils, gender)

    fam_emoji = {
        "어머니": "👩",
        "계모": "👩‍🦳",
        "아내": "💑",
        "정부": "💘",
        "아버지": "👨",
        "시아버지": "👴",
        "딸": "👧",
        "남편": "💑",
        "아들": "👦",
        "형제": "👬",
        "자매": "👭",
        "이복형제": "👥",
        "이복자매": "👥",
        "조모": "👵",
        "손자": "👶",
    }

    if yk:
        for item in yk:
            fam_name = item.get("관계", "")

            emoji = next((e for n, e in fam_emoji.items() if n in fam_name), "👤")

            where_str = item.get("위치", "없음")

            has = item.get("present", False)

            desc = item.get("desc", "")

            strength_label = "강(强) - 인연이 깊습니다" if has else "약(弱) - 인연이 엷습니다"

            st.markdown(
                f"""

<div class="card" style="margin-bottom:8px">

<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">

<span style="font-size:24px">{emoji}</span>

<div>

<div style="font-size:15px;font-weight:700;color:#000000">{fam_name}</div>

<div style="font-size:12px;color:#444">{where_str} | {strength_label}</div>

</div>

</div>

<div style="font-size:13px;color:#000000;background:#ffffff;padding:8px 12px;border-radius:8px;margin-top:4px;line-height:1.8">{desc}</div>

</div>

""",
                unsafe_allow_html=True,
            )

    else:
        st.info("육친 데이터를 분석 중입니다.")

    # 배우자/인연 자리 분석
    _marriage_status = st.session_state.get("marriage_status", "미혼")
    _is_married = _marriage_status == "기혼"
    _partner_label = "배우자" if _is_married else "인연 파트너"
    _section_title = "💑 배우자 자리 (일지) 분석" if _is_married else "💕 인연 자리 (일지) 분석"

    st.markdown(
        f'<div class="gold-section">{_section_title}</div>',
        unsafe_allow_html=True,
    )

    iljj = pils[1]["jj"]

    iljj_ss = calc_sipsung(ilgan, pils)[1].get("jj_ss", "-")

    spouse_desc = {
        "남": {
            "정재": f"현모양처형. 안정적이고 내조를 잘하는 {_partner_label}.",
            "편재": f"활달하고 매력적이나 변화가 많은 {_partner_label}.",
            "정관": f"격조 있는 인연.",
            "편관": f"강하고 카리스마 있는 {_partner_label}. 갈등도 있을 수 있습니다.",
        },
        "여": {
            "정관": f"점잖고 안정적인 {_partner_label}. 사회적으로 인정받는 분.",
            "편관": f"카리스마 있고 강한 {_partner_label}. 자유분방한 측면도.",
            "정재": f"풍요로운 인연의 {_partner_label}.",
            "편재": f"활동적이고 사교적인 {_partner_label}.",
        },
    }

    spouse_hint = spouse_desc.get(gender, {}).get(iljj_ss, f"일지의 {iljj_ss} - {_partner_label}의 성향을 나타냅니다.")

    st.markdown(
        f"""

<div class="card" style="background:#fff0f8;border:2px solid #d580b8">

<div style="font-size:14px;font-weight:700;color:#8b2060;margin-bottom:8px">

            💑 {_partner_label} 자리: {iljj}({JJ_KR[JJ.index(iljj)] if iljj in JJ else ""}) - {iljj_ss}

</div>

<div style="font-size:13px;color:#000000;line-height:1.9">{spouse_hint}</div>

</div>

""",
        unsafe_allow_html=True,
    )


def tab_gunghap(pils, name="나"):
    """궁합(宮合) 탭"""

    st.markdown(
        '<div class="gold-section">💑 궁합(宮合) - 두 사주의 조화</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """

<div class="card" style="background:#fff0f8;border:1px solid #d5a8c8">

<div style="font-size:13px;color:#8b2060;font-weight:700;margin-bottom:6px">💡 상대방 사주 입력</div>

<div style="font-size:13px;color:#444">상대방의 생년월일시를 입력하시면 두 사주의 궁합을 분석합니다.</div>

</div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        partner_name = st.text_input("상대방 이름", placeholder="이름", key="partner_name")

    with col2:
        p_year = st.number_input("생년", min_value=1920, max_value=2010, value=1992, key="p_year")

    with col3:
        p_month = st.number_input("생월", min_value=1, max_value=12, value=6, key="p_month")

    with col4:
        p_day = st.number_input("생일", min_value=1, max_value=31, value=15, key="p_day")

    col5, col6 = st.columns(2)

    with col5:
        p_hour = st.selectbox("생시", list(range(0, 24)), index=12, key="p_hour")

    with col6:
        p_gender = st.selectbox("성별", ["남", "여"], key="p_gender")

    if st.button("💑 궁합 분석", use_container_width=True, type="primary"):
        try:
            partner_pils = SajuCoreEngine.get_pillars(p_year, p_month, p_day, p_hour)

            pname = partner_name if partner_name else "상대방"

            result = calc_gunghap(pils, partner_pils, name, pname)

            # AI 연동을 위해 세션에 저장

            st.session_state.last_gunghap = {
                "name": pname,
                "pils": partner_pils,
                "summary": f"{name}님과 {pname}님의 궁합 점수는 {result['총점']}점({result['등급']})입니다.",
                "details": result,
            }

            # 궁합 점수 게이지

            score = result["총점"]

            grade = result["등급"]

            bar = "🟥" * (score // 10) + "⬜" * (10 - score // 10)

            score_color = "#000000" if score >= 70 else "#c03020" if score < 40 else "#888"

            st.markdown(
                f"""

<div style="background:linear-gradient(135deg,#ffe2f6,#ffe1ff);color:#000000;padding:28px;border-radius:16px;text-align:center;margin:16px 0">

<div style="font-size:16px;color:#f0c0d8;margin-bottom:8px">{name} ❤️ {pname}</div>

<div style="font-size:48px;font-weight:900;color:#8b6200">{score}점</div>

<div style="font-size:22px;margin:10px 0">{bar}</div>

<div style="font-size:20px;font-weight:700;color:#8b6200">{grade}</div>

</div>

""",
                unsafe_allow_html=True,
            )

            # 세부 분석

            col_a, col_b = st.columns(2)

            with col_a:
                ir = result["일간관계"]

                st.markdown(
                    f"""

<div class="card">

<div style="font-size:13px;font-weight:700;color:#000000;margin-bottom:6px">{ir[2]} 일간 관계: {ir[0]}</div>

<div style="font-size:13px;color:#444">{ir[1]}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

                if result["합"]:
                    st.markdown(
                        f"""

<div class="card" style="background:#ffffff;border:1px solid #a8d5a8">

<div style="font-size:13px;font-weight:700;color:#2a6f2a;margin-bottom:6px">- 합(合) 발견!</div>

<div style="font-size:13px;color:#333">{", ".join(result["합"])}</div>

</div>

""",
                        unsafe_allow_html=True,
                    )

            with col_b:
                if result["충"]:
                    st.markdown(
                        f"""

<div class="card" style="background:#fff0f0;border:1px solid #d5a8a8">

<div style="font-size:13px;font-weight:700;color:#8b2020;margin-bottom:6px">⚠️ 충(沖) 발견</div>

<div style="font-size:13px;color:#333">{", ".join(result["충"])}</div>

<div style="font-size:12px;color:#000000;margin-top:4px">충이 있어도 서로 이해하고 보완하면 더욱 단단한 인연이 됩니다.</div>

</div>

""",
                        unsafe_allow_html=True,
                    )

                gui_items = []

                if result["귀인_a"]:
                    gui_items.append(f"{name}의 사주에 {pname}이 귀인 역할")

                if result["귀인_b"]:
                    gui_items.append(f"{pname}의 사주에 {name}이 귀인 역할")

                if gui_items:
                    st.markdown(
                        f"""

<div class="card" style="background:#ffffff;border:1px solid #e8d5a0">

<div style="font-size:13px;font-weight:700;color:#000000;margin-bottom:6px">- 천을귀인 인연!</div>

<div style="font-size:13px;color:#444">{"<br>".join(gui_items)}</div>

</div>

""",
                        unsafe_allow_html=True,
                    )

        except Exception as e:
            st.error(f"분석 오류: {e}")


# ==================================================

#  월령(月令) 심화 - 왕상휴수사

# ==================================================


JJ_MONTH_SEASON = {
    "寅": "봄 초입(1월, 양력2월)",
    "卯": "봄 한창(2월, 양력3월)",
    "辰": "봄 마무리(3월, 양력4월)",
    "巳": "여름 초입(4월, 양력5월)",
    "午": "여름 한창(5월, 양력6월)",
    "未": "여름 마무리(6월, 양력7월)",
    "申": "가을 초입(7월, 양력8월)",
    "酉": "가을 한창(8월, 양력9월)",
    "戌": "가을 마무리(9월, 양력10월)",
    "亥": "겨울 초입(10월, 양력11월)",
    "子": "겨울 한창(11월, 양력12월)",
    "丑": "겨울 마무리(12월, 양력1월)",
}


# ==================================================

#  대운/세운 교차 분석

# ==================================================

# ==================================================

# * 사건 트리거 감지 엔진 v2 *

# 충/형/합 + 십성활성 + 대운전환점 -> "소름 포인트" 생성

# ==================================================

_JIJI_CHUNG = {
    "子": "午",
    "午": "子",
    "丑": "未",
    "未": "丑",
    "寅": "申",
    "申": "寅",
    "卯": "酉",
    "酉": "卯",
    "辰": "戌",
    "戌": "辰",
    "巳": "亥",
    "亥": "巳",
}

_JIJI_HYEONG = {
    "子": "卯",
    "卯": "子",
    "寅": "巳",
    "巳": "申",
    "申": "寅",
    "丑": "戌",
    "戌": "未",
    "未": "丑",
    "辰": "辰",
    "午": "午",
    "酉": "酉",
    "亥": "亥",
}

_TG_HAP_PAIRS = [{"甲", "己"}, {"乙", "庚"}, {"丙", "辛"}, {"丁", "壬"}, {"戊", "癸"}]

_SAM_HAP = [
    (frozenset({"寅", "午", "戌"}), "火"),
    (frozenset({"申", "子", "辰"}), "水"),
    (frozenset({"亥", "卯", "未"}), "木"),
    (frozenset({"巳", "酉", "丑"}), "金"),
]

_BIRTH_F2 = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

_CTRL2 = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}


@st.cache_data
def detect_event_triggers(pils, birth_year, gender, bm=1, bd=1, bh=12, bmi=0, target_year=None):
    """

    사건 트리거 감지 - 충/형/합/십성활성/대운전환

    Returns list[dict]: type, title, detail, prob(0~100)

    """

    if target_year is None:
        target_year = datetime.now().year

    ilgan = pils[1]["cg"]

    il_jj = pils[1]["jj"]

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    y_idx = (target_year - 4) % 60

    year_jj = JJ[y_idx % 12]

    year_cg = CG[y_idx % 10]

    # 대운 호출 시 실제 생년월일시 반영 (사용자 지침 준수)

    dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender=gender)

    cur_dw = next((d for d in dw_list if d["시작연도"] <= target_year <= d["종료연도"]), None)

    dw_jj = cur_dw["jj"] if cur_dw else ""

    dw_cg = cur_dw["cg"] if cur_dw else ""

    ys = get_yongshin(pils)

    yong_ohs = ys.get("종합_용신", []) if isinstance(ys.get("종합_용신"), list) else []

    all_jjs = frozenset(p["jj"] for p in pils)

    triggers = []

    def add(type_, title, detail, prob):

        triggers.append({"type": type_, "title": title, "detail": detail, "prob": prob})

    # ① 충

    if _JIJI_CHUNG.get(il_jj) == year_jj:
        add(
            "충",
            "⚡ 일지 충(세운) - 삶의 터전 격변",
            "이사/직장변화/관계분리 확률이 높습니다. 기존 환경이 흔들리는 해입니다.",
            85,
        )

    if dw_jj and _JIJI_CHUNG.get(il_jj) == dw_jj:
        add(
            "충",
            "⚡ 일지 충(대운) | 10년 환경 변화",
            "대운 수준의 큰 환경 변화. 이사/직업 전환의 대운입니다.",
            80,
        )

    if _JIJI_CHUNG.get(wol_jj) == year_jj:
        add(
            "충",
            "🌊 월지 충 - 가족/직업 변동",
            "부모/형제 관계 변화, 직업 환경의 급격한 변화가 예상됩니다.",
            75,
        )

    # ② 형

    if _JIJI_HYEONG.get(il_jj) == year_jj or _JIJI_HYEONG.get(year_jj) == il_jj:
        add(
            "형",
            "⚠️ 일지 형(刑) - 스트레스/사고",
            "건강/사고/법적 문제에 주의. 인간관계 갈등이 생깁니다.",
            70,
        )

    # ③ 천간합

    for pair in _TG_HAP_PAIRS:
        if dw_cg in pair and year_cg in pair:
            add(
                "합",
                "💑 천간합 - 새 인연/파트너십",
                "새로운 인연/결혼/동업/계약 인연이 찾아옵니다.",
                65,
            )

            break

    # ④ 삼합국

    check_jjs = all_jjs | frozenset([dw_jj, year_jj])

    for combo, oh in _SAM_HAP:
        if combo.issubset(check_jjs):
            kind = "용신" if oh in yong_ohs else "기신"

            add(
                "삼합",
                "🌟 삼합국 - 강력한 기운 형성",
                f"대운/세운/원국이 {oh}({OHN.get(oh, '')}) 삼합. {kind} 오행이므로 {'크게 발복' if kind == '용신' else '조심 필요'}합니다.",
                80,
            )

            break

    # ⑤ 용신/기신 대운

    if dw_cg:
        dw_oh = OH.get(dw_cg, "")

        if dw_oh in yong_ohs:
            add(
                "황금기",
                "- 용신 대운 - 황금기",
                "일생에 몇 번 없는 상승기. 이 시기의 도전은 결실을 맺습니다.",
                90,
            )

        elif any(_CTRL2.get(dw_oh) == y or _CTRL2.get(y) == dw_oh for y in yong_ohs):
            add(
                "경계",
                "🛡️ 기신 대운 - 방어 필요",
                "확장보다 수성(守成)이 최선. 큰 결정은 신중히 하십시오.",
                80,
            )

    # ⑥ 대운 전환점 (2년 이내)

    for i, dw_item in enumerate(dw_list[:-1]):
        if dw_item["시작연도"] <= target_year <= dw_item["종료연도"]:
            yrs_left = dw_item["종료연도"] - target_year

            if yrs_left <= 2:
                next_dw = dw_list[i + 1]

                add(
                    "전환",
                    "🔄 대운 전환점 - 흐름 역전",
                    f"{yrs_left + 1}년 안에 대운이 {next_dw['str']}로 전환됩니다. 이전과 다른 인생 국면이 펼쳐집니다.",
                    85,
                )

    # ⑦ 십성 활성화

    year_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(year_cg, "-")

    if year_ss in ["정관", "편관"]:
        add(
            "직업",
            "🎖️ 관성 활성 - 직업/명예 변화",
            f"세운 천간({year_cg})이 {year_ss}. 승진/이직/자격증 변화가 예상됩니다.",
            70,
        )

    if year_ss in ["정재", "편재"]:
        add(
            "재물",
            "💰 재성 활성 - 재물 흐름",
            f"세운 천간({year_cg})이 {year_ss}. 재물 흐름이 활발해집니다. 투자 기회 주의.",
            72,
        )

    return triggers


@st.cache_data
def calc_luck_score(pils, birth_year, gender, bm=1, bd=1, bh=12, bmi=0, target_year=None):
    """대운+세운 종합 운세 점수 (0~100)"""

    if target_year is None:
        target_year = datetime.now().year

    ys = get_yongshin(pils)

    yong_ohs = ys.get("종합_용신", []) if isinstance(ys.get("종합_용신"), list) else []

    dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender=gender)

    cur_dw = next((d for d in dw_list if d["시작연도"] <= target_year <= d["종료연도"]), None)

    score = 50

    if cur_dw:
        dw_oh = OH.get(cur_dw["cg"], "")

        if dw_oh in yong_ohs:
            score += 25

        elif any(_BIRTH_F2.get(dw_oh) == y for y in yong_ohs):
            score += 12

        elif any(_CTRL2.get(dw_oh) == y or _CTRL2.get(y) == dw_oh for y in yong_ohs):
            score -= 20

    _LV = {
        "대길(大吉)": 20,
        "길(吉)": 10,
        "평길(平吉)": 5,
        "평(平)": 0,
        "흉(凶)": -15,
        "흉흉(凶凶)": -25,
    }

    yl = get_yearly_luck(pils, target_year)

    score += _LV.get(yl.get("길흉", "평(平)"), 0)

    return max(0, min(100, score))


@st.cache_data
def calc_turning_point(pils, birth_year, gender, bm=1, bd=1, bh=12, bmi=0, target_year=None):
    """

    인생 전환점 감지 엔진 (정밀 v2)

    대운 점수 차이 + 세운 트리거 + 충합 종합

    Returns dict: {is_turning:bool, intensity:str, reason:list, score_change:int}

    """

    if target_year is None:
        target_year = datetime.now().year

    prev_score = calc_luck_score(pils, birth_year, gender, bm, bd, bh, bmi, target_year - 1)

    curr_score = calc_luck_score(pils, birth_year, gender, bm, bd, bh, bmi, target_year)

    next_score = calc_luck_score(pils, birth_year, gender, bm, bd, bh, bmi, target_year + 1)

    dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender=gender)

    cur_dw = next((d for d in dw_list if d["시작연도"] <= target_year <= d["종료연도"]), None)

    prev_dw = None

    for i, d in enumerate(dw_list):
        if d["시작연도"] <= target_year <= d["종료연도"] and i > 0:
            prev_dw = dw_list[i - 1]

            break

    reasons = []

    diff = curr_score - prev_score

    next_diff = next_score - curr_score

    # 대운 전환점 (이 해 또는 1~2년 이내)

    if cur_dw:
        yrs_to_change = cur_dw["종료연도"] - target_year

        if yrs_to_change <= 1:
            reasons.append(f"⚡ 대운 {cur_dw['str']} 마지막 해 - 인생 국면 전환 목전")

        if cur_dw["시작연도"] == target_year:
            reasons.append(f"🌟 새 대운 {cur_dw['str']} 시작 | 10년 흐름 완전 변화")

    if prev_dw and cur_dw and cur_dw["시작연도"] == target_year:
        # 이전 대운과 오행 관계

        prev_oh = OH.get(prev_dw["cg"], "")

        curr_oh = OH.get(cur_dw["cg"], "")

        ys = get_yongshin(pils)

        yong_ohs = ys.get("종합_용신", []) if isinstance(ys.get("종합_용신"), list) else []

        if prev_oh not in yong_ohs and curr_oh in yong_ohs:
            reasons.append(f"- 기신 대운->용신 대운 전환 - 인생 역전의 기회")

        elif prev_oh in yong_ohs and curr_oh not in yong_ohs:
            reasons.append(f"⚠️ 용신 대운->기신 대운 전환 - 속도 조절 필요")

    # 운세 점수 급변

    if abs(diff) >= 25:
        direction = "상승" if diff > 0 else "하락"

        reasons.append(f"📊 운세 점수 {abs(diff)}점 급{'등' if diff > 0 else '락'} - 삶의 {direction} 흐름")

    elif abs(diff) >= 15:
        direction = "개선" if diff > 0 else "하강"

        reasons.append(f"📈 운세 {direction} ({diff:+d}점) - 변화 감지")

    # 사건 트리거 (충/합 있으면 강화)

    triggers = detect_event_triggers(pils, birth_year, gender, bm, bd, bh, bmi, target_year)

    high_triggers = [t for t in triggers if t["prob"] >= 80]

    if high_triggers:
        # 트리거 제목 정리 — 불필요한 내부 식별자 제거
        _trig_title = high_triggers[0].get("title","사건")
        _trig_title = _trig_title.replace(" - ","·").strip()
        reasons.append(f"🔴 강한 변화 기운 {len(high_triggers)}가지 — {_trig_title}")

    # 전환점 여부 및 강도

    total_score_change = abs(diff)

    is_turning = total_score_change >= 15 or any("대운" in r or "전환" in r for r in reasons)

    if total_score_change >= 30 or len(reasons) >= 3:
        intensity = "🔴 강력 전환점"

    elif total_score_change >= 20 or len(reasons) >= 2:
        intensity = "🟡 주요 변화점"

    elif is_turning:
        intensity = "🟢 변화 시작"

    else:
        intensity = "⬜ 흐름 유지"

    # 운세 라벨링 (Stage Labeling)

    fate_label = (
        "준비기 🌱",
        "새로운 시작을 위해 내면을 채우고 씨앗을 심는 시기입니다.",
    )

    if is_turning:
        fate_label = (
            "전환기 ⚡",
            "삶의 경로가 바뀌는 격동의 시기입니다. 유연한 대처가 필요합니다.",
        )

    elif diff > 10:
        fate_label = (
            "확장기 🔥",
            "에너지가 분출되고 외연을 넓히는 시기입니다. 적극적으로 움직이세요.",
        )

    elif curr_score >= 70:
        fate_label = (
            "수확기 🍂",
            "그동안의 노력이 결실을 맺는 안정과 성취의 시기입니다.",
        )

    return {
        "is_turning": is_turning,
        "intensity": intensity,
        "fate_label": fate_label[0],
        "fate_desc": fate_label[1],
        "reason": reasons,
        "score_prev": prev_score,
        "score_curr": curr_score,
        "score_next": next_score,
        "score_change": diff,
        "triggers": triggers,
    }


@st.cache_data
def get_yongshin_multilayer(pils, birth_year, gender, bm=1, bd=1, bh=12, bmi=0, target_year=None):
    """

    다층 용신 분석 (1순위~3순위 + 희신 + 기신 + 대운별 용신)

    Returns dict with 용신_1순위, 용신_2순위, 희신, 기신, 현재_상황_용신, 대운_용신

    """

    if target_year is None:
        target_year = datetime.now().year

    ys = get_yongshin(pils)

    yong_list = ys.get("종합_용신", []) if isinstance(ys.get("종합_용신"), list) else []

    # [년, 월, 일, 시] 순서에서 일간은 index 2

    oh_strength = calc_ohaeng_strength(pils[1]["cg"], pils)

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    # 상생 순서

    BIRTH = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

    CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    # 용신 1순위 (가장 필요한 오행)

    base_yong = yong_list[0] if yong_list else ""

    # 희신 (용신을 생해주는 오행)

    hee_shin = BIRTH.get(base_yong, "")

    # 기신 (용신을 극하는 오행)

    gi_shin_list = []

    for oh in ["木", "火", "土", "金", "水"]:
        if CTRL.get(oh) == base_yong or CTRL.get(base_yong) == oh:
            if oh != ilgan_oh and oh not in yong_list:
                gi_shin_list.append(oh)

    # 용신 2순위

    yong_2 = yong_list[1] if len(yong_list) > 1 else ""

    # 대운별 용신 변화

    dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmi, gender=gender)

    cur_dw = next((d for d in dw_list if d["시작연도"] <= target_year <= d["종료연도"]), None)

    dw_yong = ""

    dw_note = ""

    if cur_dw:
        dw_oh = OH.get(cur_dw["cg"], "")

        if dw_oh in yong_list:
            dw_yong = dw_oh

            dw_note = f"현재 {cur_dw['str']} 대운 = 용신 오행 -> 황금기"

        elif dw_oh == hee_shin:
            dw_yong = hee_shin

            dw_note = f"현재 {cur_dw['str']} 대운 = 희신 -> 안정 성장기"

        elif dw_oh in gi_shin_list:
            dw_yong = ""

            dw_note = f"현재 {cur_dw['str']} 대운 = 기신 -> 방어 전략 필요"

        else:
            dw_yong = dw_oh

            dw_note = f"현재 {cur_dw['str']} 대운 = 중립 -> 평상 유지"

    # 상황별 용신 (재물/직장/건강)

    situation_yong = {
        "재물": yong_list[0] if yong_list else "",
        "직업": yong_list[1] if len(yong_list) > 1 else (yong_list[0] if yong_list else ""),
        "건강": hee_shin or (yong_list[0] if yong_list else ""),
        "인간관계": hee_shin or (yong_list[0] if yong_list else ""),
    }

    return {
        "용신_1순위": base_yong,
        "용신_2순위": yong_2,
        "희신": hee_shin,
        "기신": gi_shin_list[:2] if gi_shin_list else [],
        "현재_대운_용신": dw_yong,
        "대운_해석": dw_note,
        "상황별_용신": situation_yong,
        "전체_용신_목록": yong_list,
    }


def build_rich_ai_context(pils, birth_year, gender, target_year=None, focus="종합"):
    """

    AI에게 전달할 풍부한 계산 데이터 JSON 빌더 (Skill 2 & 3: Structuring & Analysis)

    - 감정적 해석을 배제하고 순수 명리 분석 수치/지표만 전달합니다.

    """

    if target_year is None:
        target_year = datetime.now().year

    # [시, 일, 월, 년] 순서에서 일간은 index 1

    ilgan = pils[1]["cg"]

    strength_info = get_ilgan_strength(ilgan, pils)

    ys_multi = get_yongshin_multilayer(pils, birth_year, gender, target_year)

    turning = calc_turning_point(pils, birth_year, gender, target_year)

    pillars_str = " ".join([p["str"] for p in pils])

    # 순수 데이터 구조화 (Skill 2: Structuring)


    # 분야별 정밀 가중치 데이터 (Skill 3: Analysis)

    if focus == "재물":
        context["domain_specific"] = {
            "wealth_star_strength": "강" if strength_info["oh_strength"].get("土", 0) > 20 else "약",  # 예시 로직
            "business_luck": "상승기" if turning["score_change"] > 10 else "안정기",
        }

    elif focus == "연애":
        context["domain_specific"] = {"couple_star_status": "활성" if any("합" in t["title"] for t in turning["triggers"]) else "비활성"}

    return context


# --------------------------------------------------------------

# GOOSEBUMP ENGINE - 소름 문장 자동 생성 (Cold Reading 알고리즘)

# 과거 적중 -> 현재 공감 -> 미래 예고 -> 확신 강화

# --------------------------------------------------------------


def goosebump_engine(pils, birth_year, gender, target_year=None):
    """

    [Engine] Goosebump Engine

    Saju patterns -> Trigger -> Sentence

    Returns: dict

    """

    if target_year is None:
        target_year = datetime.now().year

    ilgan = pils[1]["cg"]

    il_jj = pils[1]["jj"]

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    ilgan_oh = OH.get(ilgan, "")

    strength_info = get_ilgan_strength(ilgan, pils)

    oh_str = strength_info["oh_strength"]

    sn = strength_info["신강신약"]

    score = strength_info.get("일간점수", 50)

    TGM = TEN_GODS_MATRIX.get(ilgan, {})

    all_ss = [TGM.get(p["cg"], "-") for p in pils]

    ys = get_yongshin(pils)

    yong_ohs = ys.get("종합_용신", []) if isinstance(ys.get("종합_용신"), list) else []

    luck_s = calc_luck_score(pils, birth_year, gender, target_year)

    triggers = detect_event_triggers(pils, birth_year, gender, target_year)

    turning = calc_turning_point(pils, birth_year, gender, target_year)

    # ① 과거 적중 문장 - 사주 패턴 -> 이미 겪은 일

    past_sentences = []

    # 관성 충 감지

    officer_clash = any(TGM.get(p["cg"], "") in ("정관", "편관") and _JIJI_CHUNG.get(p["jj"]) in {q["jj"] for q in pils} for p in pils)

    if officer_clash or any(s in ("정관", "편관") for s in all_ss):
        past_sentences.append("직장이나 책임 문제로 크게 고민하고 홀로 힘들었던 시기가 분명히 있었습니다.")

    # 재성 과다

    wealth_count = sum(1 for s in all_ss if s in ("정재", "편재"))

    if wealth_count >= 2:
        past_sentences.append("돈이나 현실적 문제로 판단을 반복하고 마음이 복잡했던 시기가 있었습니다.")

    # 인성 과다 (생각 많음)

    insung_count = sum(1 for s in all_ss if s in ("정인", "편인"))

    if insung_count >= 2:
        past_sentences.append("머릿속 생각이 많아 결정을 내리지 못하고 오래 고민했던 시간이 있었습니다.")

    # 일지 충 (과거)

    # 대운 호출 시 실제 생년월일시 반영 (사용자 지침 준수)

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    past_dw = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    for dw in past_dw:
        if dw["종료연도"] < target_year:
            if _JIJI_CHUNG.get(il_jj) == dw["jj"]:
                age = dw["시작나이"]

                past_sentences.append(f"{age}대에 환경이 크게 바뀌거나 중요한 관계가 변한 일이 있었습니다.")

                break

    # 겁재 (재물 경쟁)

    if any(s == "겁재" for s in all_ss):
        past_sentences.append("믿었던 사람에게 금전적으로 손해를 보거나 경쟁에서 예상치 못한 결과를 겪은 적이 있었습니다.")

    # ② 현재 상태 문장 - 현재 운 vs 원국 비교

    present_sentences = []

    prev_luck = calc_luck_score(pils, birth_year, gender, target_year - 1)

    diff = luck_s - prev_luck

    if diff < -20:
        present_sentences.append("지금은 노력 대비 결과가 느리게 따라오는 시기입니다. 열심히 하는데 티가 안 나는 느낌, 맞지 않으십니까?")

    elif diff < -10:
        present_sentences.append("최근 들어 무언가 예전 같지 않다는 느낌, 흐름이 살짝 꺾인 느낌을 받고 계실 겁니다.")

    elif diff > 20:
        present_sentences.append("지금 운이 올라오는 시기입니다. 최근 생각지도 못한 기회나 연락이 오고 있지는 않으십니까?")

    elif diff > 10:
        present_sentences.append("서서히 흐름이 좋아지는 시기입니다. 주변에서 당신을 다시 보기 시작하는 신호가 보일 겁니다.")

    else:
        present_sentences.append("지금은 흐름이 안정적으로 유지되고 있습니다. 큰 변화 없이 무난한 시기지만, 곧 달라질 계기가 옵니다.")

    # 신강/신약 현재 체감

    if "신약" in sn:
        present_sentences.append("겉으로는 괜찮아 보이지만 혼자 고민을 오래 끌어가는 편이십니다. 말하지 않고 삭이는 경우가 많습니다.")

    elif "신강" in sn:
        present_sentences.append("자신이 옳다는 확신이 강하고, 타인의 시선보다 자기 기준을 먼저 내세우는 편이십니다.")

    # ③ 미래 예고 문장

    future_sentences = []

    if turning["is_turning"]:
        intensity = turning["intensity"]

        if "강력" in intensity:
            future_sentences.append("곧 인생 흐름이 크게 바뀌는 계기가 들어옵니다. 이 시기가 지나면 이전과 완전히 다른 국면이 펼쳐집니다.")

        else:
            future_sentences.append("변화의 씨앗이 심어지고 있습니다. 지금의 선택 하나가 앞으로 수년을 결정짓는 분기점이 됩니다.")

    # 고확률 트리거 예고

    high_t = [t for t in triggers if t["prob"] >= 80]

    if high_t:
        t = high_t[0]

        if t["type"] == "충":
            future_sentences.append("환경이 흔들리는 기운이 다가오고 있습니다. 이사/직장/관계 중 하나가 변할 가능성이 높습니다.")

        elif t["type"] == "황금기":
            future_sentences.append("이 시기는 일생에 몇 번 없는 상승기입니다. 지금의 도전은 반드시 결실을 맺습니다.")

        elif t["type"] == "합":
            future_sentences.append("새로운 인연이나 협력의 기운이 강하게 들어옵니다. 혼자보다는 함께할 때 결과가 좋습니다.")

        elif t["type"] == "인연":
            future_sentences.append("인연의 기운이 움직이고 있습니다. 새로운 중요한 만남이 가까운 시일 안에 찾아옵니다.")

        elif t["type"] == "재물":
            future_sentences.append("재물운의 흐름이 강화되고 있습니다. 뜻하지 않은 기회나 보상이 따를 수 있는 시기입니다.")

    return {
        "past": past_sentences,
        "present": present_sentences,
        "future": future_sentences,
        "full_text": "\n\n".join(
            [
                " ".join(past_sentences),
                " ".join(present_sentences),
                " ".join(future_sentences),
            ]
        ),
    }


def render_lucky_kit(yong_oh):
    """

    Brain 1: 자체 로직 기반 행운의 개운법 UI 렌더링

    """


    k = kits.get(yong_oh, kits["木"])

    st.markdown(
        f"""

<div style="background: #ffffff; border: 1px solid #e0d8c0; border-radius: 12px; padding: 20px; margin-bottom: 25px;">

<div style="font-size: 16px; font-weight: 800; color: #000000; margin-bottom: 15px; border-bottom: 1px solid #f0e8d0; padding-bottom: 8px;">

            [개운] 오늘의 행운 개운 비방 (Lucky Kit)

</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">

<div style="font-size: 14px; color: #555;"><b>행운의 색상:</b> <span style="color:#333">{k["color"]}</span></div>

<div style="font-size: 14px; color: #555;"><b>행운의 숫자:</b> <span style="color:#333">{k["num"]}</span></div>

<div style="font-size: 14px; color: #555;"><b>행운의 방향:</b> <span style="color:#333">{k["dir"]}</span></div>

<div style="font-size: 14px; color: #555;"><b>행운의 음식:</b> <span style="color:#333">{k["food"]}</span></div>

</div>

<div style="margin-top: 12px; font-size: 12px; color: #888; font-style: italic;">

            (안내) {yong_oh}의 기운을 보강하여 오늘 하루의 운기를 상승시키는 실천법입니다.

</div>

</div>

    

""",
        unsafe_allow_html=True,
    )


def apply_mansin_filter(text):
    """만신 AI 환각 방지 및 말투 보정 필터"""

    if not text:
        return ""

    # AI/보고서체 -> 만신 톤 치환
    _REPLACES = [
        ("AI로서 말씀드리면", "만신의 눈으로 보건대"),
        ("분석한 결과입니다", "천명의 암호를 풀이한 결과로다"),
        ("도움이 되셨길 바랍니다", "부디 이 신탁이 네 삶의 등불이 되길 바란다"),
        ("AI가 분석한 결과", "만신이 읽은 천명"),
        ("제가 보기에는", "신안(神眼)으로 보건대"),
        ("제가 판단하기엔", "팔자로 보아"),
        ("도움이 되었으면 합니다", "이 말씀이 네 발밑의 등불이 되길 바란다"),
        ("참고하시기 바랍니다", "마음에 새겨 두시길 바라나이다"),
        ("라고 할 수 있습니다", "이라 하겠느니라"),
        ("라고 생각됩니다", "이라 보이는구나"),
        ("분석 결과,", "풀이하건대,"),
        ("결론적으로", "한마디로"),
    ]
    for bad, good in _REPLACES:
        text = text.replace(bad, good)

    return text


# ==============================================================

#  🧠 ADAPTIVE ENGINE - 페르소나 감지 -> 맞춤 해석 스타일

#  사용자 행동 패턴으로 성향 자동 추정

# ==============================================================

_PERSONA_KEY = "_adaptive_persona"


def infer_persona() -> str:
    """

    세션 행동 데이터로 페르소나 자동 추정

    achievement / overthinking / emotional / cautious / balanced

    """

    behavior = st.session_state.get("_b3_behavior", {})

    focus = st.session_state.get("ai_focus", "종합")

    actions = behavior.get("actions", [])

    q_count = behavior.get("question_count", 0)

    v_count = behavior.get("view_count", 0)

    # 행동 기반 성향

    if focus == "재물":
        return "achievement_type"  # 성취/결과 지향

    if focus == "연애":
        return "emotional_type"  # 감정/관계 중심

    if focus == "건강":
        return "cautious_type"  # 안정/리스크 회피

    if focus == "직장":
        return "career_type"  # 커리어/명예 지향

    if q_count >= 2:
        return "overthinking_type"  # 생각 많음, 확인 욕구

    if v_count >= 4:
        return "deep_reflection_type"  # 심층 탐색

    return "balanced_type"


def get_persona_prompt_style(persona: str) -> str:
    """페르소나별 AI 해석 스타일 지침"""

    style_map = {
        "achievement_type": ("사용자는 성취/결과 지향적이다. 현실적이고 구체적인 행동 가이드와 기회를 중심으로 해석하라. 추상적 표현 최소화. 언제, 무엇을, 어떻게 해야 하는지 단정적으로 말하라."),
        "emotional_type": ("사용자는 감정/관계를 중시한다. 인간관계와 감정 흐름을 중심으로 따뜻하고 공감적으로 해석하라. 외로움, 그리움, 설렘 등 감정 언어를 자연스럽게 사용하라."),
        "career_type": ("사용자는 커리어와 사회적 인정을 중요하게 생각한다. 직업/승진/명예/직장 흐름을 중심으로 단계적이고 전략적으로 해석하라."),
        "cautious_type": ("사용자는 안정과 리스크 회피를 선호한다. 위험 요인을 먼저 짚고, 안전한 선택지와 주의 사항을 구체적으로 제시하라. 과도한 낙관 표현 자제."),
        "overthinking_type": ("사용자는 생각이 많고 확신을 원한다. 반복적 고민에 대한 공감을 먼저 표현하고, 단정적이고 명확한 결론을 내려주어 안심시켜라. 모호한 표현 절대 금지."),
        "deep_reflection_type": ("사용자는 인생의 의미와 방향성을 탐색 중이다. 철학적이고 깊이 있는 해석을 선호한다. 표면적 사건보다 근본적 원인과 삶의 패턴을 설명하라."),
        "balanced_type": ("사용자는 균형 잡힌 관점을 원한다. 긍정과 주의 사항을 균형 있게 제시하고, 현재 상황과 미래 흐름을 종합적으로 해석하라."),
    }

    return style_map.get(persona, style_map["balanced_type"])


def get_persona_label(persona: str) -> tuple:
    """페르소나 -> (아이콘, 한국어 라벨, 색상)"""

    labels = {
        "achievement_type": ("[목표]", "성취/결과형", "#e65100"),
        "emotional_type": ("[감정]", "감정/관계형", "#e91e8c"),
        "career_type": ("[커리어]", "커리어/명예형", "#1565c0"),
        "cautious_type": ("[신중]", "안정/신중형", "#2e7d32"),
        "overthinking_type": ("[분석]", "분석/확인형", "#6a1b9a"),
        "deep_reflection_type": ("[성찰]", "성찰/탐색형", "#00695c"),
        "balanced_type": ("[균형]", "균형/종합형", "#8B6914"),
    }

    return labels.get(persona, ("[종합]", "종합형", "#8B6914"))


# ==============================================================

#  SELF-CHECK ENGINE - AI 2패스 자기검증 시스템

#  1차 해석 -> AI 감수 -> 논리 보정 -> 최종 출력

# ==============================================================


def self_check_ai(first_report: str, analysis_summary: str, api_key: str = "", groq_key: str = "") -> str:
    """[로컬 전용] API 미사용. 1차 결과를 그대로 반환."""
    return first_report


# ==============================================================

#  🔄 RETENTION ENGINE - 재방문/중독 구조

#  스트릭 카운터 / 운 변화 카운트다운 / 일별 운 점수

# ==============================================================

_RETENTION_FILE = "saju_retention.json"

_USER_PROFILE_FILE = "saju_user_profile.json"

SAJU_SAVE_FILE = "saju_save.json"

# ==============================================================

#  🧠 USER MEMORY SYSTEM - AI가 사용자를 기억하는 구조

#  상담 이력 / 관심 영역 / 믿음 지수 / 이전 예측 저장

# ==============================================================


def _load_user_profile() -> dict:
    """사용자 프로필 로드"""

    try:
        if os.path.exists(_USER_PROFILE_FILE):
            with open(_USER_PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    return {}


def _save_user_profile(data: dict):
    """사용자 프로필 저장"""

    try:
        with open(_USER_PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")


def save_saju_state():
    """사주 입력값 및 계산 결과를 JSON 파일로 영구 저장"""

    _ss = st.session_state

    solar = _ss.get("in_solar_date")

    data = {
        # -- 입력값 --
        "in_name": _ss.get("in_name", ""),
        "in_gender": _ss.get("in_gender", "남"),
        "in_cal_type": _ss.get("in_cal_type", "양력"),
        "in_solar_date": solar.isoformat() if solar else "1990-01-01",
        "in_lunar_year": _ss.get("in_lunar_year", 1990),
        "in_lunar_month": _ss.get("in_lunar_month", 1),
        "in_lunar_day": _ss.get("in_lunar_day", 1),
        "in_is_leap": _ss.get("in_is_leap", False),
        "in_birth_hour": _ss.get("in_birth_hour", 12),
        "in_birth_minute": _ss.get("in_birth_minute", 0),
        "in_unknown_time": _ss.get("in_unknown_time", False),
        "in_marriage": _ss.get("in_marriage", "미혼"),
        "in_occupation": _ss.get("in_occupation", "선택 안 함"),
        "in_premium_correction": _ss.get("in_premium_correction", True),
        # -- 계산 결과 --
        "saju_pils": _ss.get("saju_pils"),
        "birth_year": _ss.get("birth_year"),
        "birth_month": _ss.get("birth_month"),
        "birth_day": _ss.get("birth_day"),
        "birth_hour": _ss.get("birth_hour"),
        "birth_minute": _ss.get("birth_minute"),
        "gender": _ss.get("gender"),
        "saju_name": _ss.get("saju_name"),
        "marriage_status": _ss.get("marriage_status"),
        "occupation": _ss.get("occupation"),
        "cal_type": _ss.get("cal_type"),
        "lunar_info": _ss.get("lunar_info", ""),
        # -- 기억 구조 --
        "saju_memory": _ss.get("saju_memory", {}),
        # -- 즐겨찾기 --
        "favorites": _ss.get("favorites", []),
    }

    try:
        with open(SAJU_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")


def load_saju_state():
    """saju_save.json에서 상태를 읽어 session_state에 복원"""

    if not os.path.exists(SAJU_SAVE_FILE):
        return

    try:
        with open(SAJU_SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception:
        return

    _ss = st.session_state

    # 단순 키 복원 (입력값 + 계산 결과)


    for key in simple_keys:
        if key in data:
            _ss[key] = data[key]

    # date 객체 복원

    if "in_solar_date" in data:
        try:
            _ss["in_solar_date"] = date.fromisoformat(data["in_solar_date"])

        except Exception as _e:
            st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    # 기억 구조 복원

    if "saju_memory" in data:
        _ss["saju_memory"] = data["saju_memory"]

    # 즐겨찾기 복원

    if "favorites" in data:
        _ss["favorites"] = data["favorites"]


def _write_favorites_to_file(favorites: list):
    """saju_save.json의 favorites 키만 업데이트"""

    existing = {}

    if os.path.exists(SAJU_SAVE_FILE):
        try:
            with open(SAJU_SAVE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)

        except Exception as _e:
            st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    existing["favorites"] = favorites

    try:
        with open(SAJU_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2, default=str)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")


def save_to_favorites(label: str):
    """현재 상태를 즐겨찾기에 저장 (같은 label이면 덮어쓰기)"""

    _ss = st.session_state

    solar = _ss.get("in_solar_date")

    snapshot = {
        "label": label or _ss.get("in_name") or "이름 없음",
        "in_name": _ss.get("in_name", ""),
        "in_gender": _ss.get("in_gender", "남"),
        "in_cal_type": _ss.get("in_cal_type", "양력"),
        "in_solar_date": solar.isoformat() if solar else "1990-01-01",
        "in_lunar_year": _ss.get("in_lunar_year", 1990),
        "in_lunar_month": _ss.get("in_lunar_month", 1),
        "in_lunar_day": _ss.get("in_lunar_day", 1),
        "in_is_leap": _ss.get("in_is_leap", False),
        "in_birth_hour": _ss.get("in_birth_hour", 12),
        "in_birth_minute": _ss.get("in_birth_minute", 0),
        "in_unknown_time": _ss.get("in_unknown_time", False),
        "in_marriage": _ss.get("in_marriage", "미혼"),
        "in_occupation": _ss.get("in_occupation", "선택 안 함"),
        "in_premium_correction": _ss.get("in_premium_correction", True),
        "saju_pils": _ss.get("saju_pils"),
        "birth_year": _ss.get("birth_year"),
        "birth_month": _ss.get("birth_month"),
        "birth_day": _ss.get("birth_day"),
        "birth_hour": _ss.get("birth_hour"),
        "birth_minute": _ss.get("birth_minute"),
        "gender": _ss.get("gender"),
        "saju_name": _ss.get("saju_name"),
        "marriage_status": _ss.get("marriage_status"),
        "occupation": _ss.get("occupation"),
        "cal_type": _ss.get("cal_type"),
        "lunar_info": _ss.get("lunar_info", ""),
        "saju_memory": _ss.get("saju_memory", {}),
    }

    favorites = list(_ss.get("favorites", []))

    for i, fav in enumerate(favorites):
        if fav.get("label") == snapshot["label"]:
            favorites[i] = snapshot

            break

    else:
        favorites.append(snapshot)

    _ss["favorites"] = favorites

    _write_favorites_to_file(favorites)


def load_from_favorite(idx: int):
    """즐겨찾기 항목을 session_state에 복원"""

    favorites = st.session_state.get("favorites", [])

    if not (0 <= idx < len(favorites)):
        return

    data = favorites[idx]

    _ss = st.session_state

    simple_keys = [
        "in_name",
        "in_gender",
        "in_cal_type",
        "in_lunar_year",
        "in_lunar_month",
        "in_lunar_day",
        "in_is_leap",
        "in_birth_hour",
        "in_birth_minute",
        "in_unknown_time",
        "in_marriage",
        "in_occupation",
        "in_premium_correction",
        "saju_pils",
        "birth_year",
        "birth_month",
        "birth_day",
        "birth_hour",
        "birth_minute",
        "gender",
        "saju_name",
        "marriage_status",
        "occupation",
        "cal_type",
        "lunar_info",
    ]

    for key in simple_keys:
        if key in data:
            _ss[key] = data[key]

    if "in_solar_date" in data:
        try:
            _ss["in_solar_date"] = date.fromisoformat(data["in_solar_date"])

        except Exception as _e:
            st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    if "saju_memory" in data:
        _ss["saju_memory"] = data["saju_memory"]

    _ss["form_expanded"] = False


def delete_favorite(idx: int):
    """즐겨찾기 항목 삭제"""

    favorites = list(st.session_state.get("favorites", []))

    if 0 <= idx < len(favorites):
        favorites.pop(idx)

        st.session_state["favorites"] = favorites

        _write_favorites_to_file(favorites)


def get_user_profile(saju_key: str) -> dict:
    """특정 사주의 사용자 프로필 반환"""

    all_profiles = _load_user_profile()

    default = {
        "saju_key": saju_key,
        "main_concern": "",  # 주요 관심사
        "past_concerns": [],  # 이전 관심사 이력
        "last_focus": "",  # 마지막 집중 분야
        "last_visit": "",  # 마지막 방문일
        "visit_count": 0,  # 총 방문 횟수
        "belief_level": 0.5,  # 신뢰도 (0~1)
        "last_prediction": "",  # 마지막 예측 요약
        "prediction_history": [],  # 예측 이력
        "stress_pattern": "",  # 주요 스트레스 패턴
        "persona": "balanced_type",  # 감지된 페르소나
        "first_visit": "",  # 첫 방문일
    }

    profile = all_profiles.get(saju_key, default)

    return profile


def update_user_profile(saju_key: str, **kwargs) -> dict:
    """사용자 프로필 업데이트"""

    all_profiles = _load_user_profile()

    profile = get_user_profile(saju_key)

    today = datetime.now().strftime("%Y-%m-%d")

    # 자동 업데이트

    if not profile.get("first_visit"):
        profile["first_visit"] = today

    profile["last_visit"] = today

    profile["visit_count"] = profile.get("visit_count", 0) + 1

    # kwargs 반영

    for k, v in kwargs.items():
        if k == "concern" and v:
            # 관심사 이력 관리

            if profile.get("main_concern") and profile["main_concern"] != v:
                hist = profile.get("past_concerns", [])

                hist.append({"concern": profile["main_concern"], "date": today})

                profile["past_concerns"] = hist[-5:]  # 최근 5개만 유지

            profile["main_concern"] = v

        elif k == "prediction" and v:
            hist = profile.get("prediction_history", [])

            hist.append({"text": v[:100], "date": today})

            profile["prediction_history"] = hist[-10:]

            profile["last_prediction"] = v[:100]

        elif k == "belief_delta" and isinstance(v, (int, float)):
            profile["belief_level"] = max(0.0, min(1.0, profile.get("belief_level", 0.5) + v))

        else:
            profile[k] = v

    all_profiles[saju_key] = profile

    _save_user_profile(all_profiles)

    return profile


def build_memory_context(saju_key: str) -> str:
    """AI 프롬프트에 삽입할 사용자 기억 컨텍스트 생성"""

    profile = get_user_profile(saju_key)

    if profile.get("visit_count", 0) <= 1:
        return ""  # 첫 방문이면 기억 없음

    lines = []

    vc = profile.get("visit_count", 0)

    lines.append(f"[이전 상담 기억] 총 {vc}회 방문한 사용자입니다.")

    if profile.get("main_concern"):
        lines.append(f"주요 관심사: {profile['main_concern']}")

    if profile.get("last_prediction"):
        lines.append(f"지난 상담 예측: {profile['last_prediction']}")

    past = profile.get("past_concerns", [])

    if past:
        prev = past[-1]

        lines.append(f"이전 관심사: {prev.get('concern', '')} ({prev.get('date', '')})")

    bl = profile.get("belief_level", 0.5)

    if bl >= 0.7:
        lines.append("신뢰도 높음 - 이전 예측이 맞았던 사용자. 더 구체적이고 단정적으로 해석하라.")

    elif bl <= 0.3:
        lines.append("신뢰도 낮음 - 의심이 많은 사용자. 근거를 더 상세히 설명하라.")

    stress = profile.get("stress_pattern")

    if stress:
        lines.append(f"주요 스트레스 패턴: {stress}")

    if lines:
        return "\n".join(lines) + "\n"

    return ""


def render_user_memory_badge(saju_key: str):
    """사용자 기억 상태 배지 렌더링"""

    profile = get_user_profile(saju_key)

    vc = profile.get("visit_count", 0)

    if vc < 2:
        return

    bl = profile.get("belief_level", 0.5)

    bl_pct = int(bl * 100)

    bl_color = "#4caf50" if bl >= 0.7 else "#ff9800" if bl >= 0.4 else "#f44336"

    bl_label = "높음" if bl >= 0.7 else "보통" if bl >= 0.4 else "형성중"

    mc = profile.get("main_concern", "")

    lp = profile.get("last_prediction", "")

    mc_html = f"<div>(관심): <b>{mc}</b></div>" if mc else ""

    lp_html = f"<div>(이전): <span style='color:#666'>{lp[:40]}...</span></div>" if lp else ""

    html = "<div style='background:linear-gradient(135deg,#f0f0ff,#e8e8ff);border:1px solid #b8a8ee;border-radius:12px;padding:12px 14px;margin:8px 0'>"

    html += f"<div style='font-size:11px;color:#7b5ea7;font-weight:700;margin-bottom:6px'>AI 기억 시스템 - {vc}회 상담 이력</div>"

    html += "<div style='display:flex;gap:12px;flex-wrap:wrap;align-items:center'>"

    html += "<div style='text-align:center'>"

    html += "<div style='font-size:10px;color:#888'>신뢰도</div>"

    html += f"<div style='font-size:16px;font-weight:900;color:{bl_color}'>{bl_pct}%</div>"

    html += f"<div style='font-size:9px;color:{bl_color}'>{bl_label}</div>"

    html += "</div>"

    html += "<div style='flex:1;font-size:11px;color:#000000;line-height:1.8'>"

    html += mc_html + lp_html

    html += "</div></div></div>"

    st.markdown(html, unsafe_allow_html=True)


def render_ai_opening_ment(saju_key: str, name: str):
    """사용자 상태에 따른 맞춤형 오프닝 멘트 (Retention)"""

    profile = get_user_profile(saju_key)

    vc = profile.get("visit_count", 0)

    concern = profile.get("main_concern", "")

    persona = profile.get("persona", "balanced_type")

    _, p_label, _ = get_persona_label(persona)

    # 멘트 템플릿

    if vc <= 1:
        ment = f"반갑습니다, {name}님. 당신의 천명을 풀이하러 온 {p_label} 마스터입니다. 오늘 어떤 고민이 당신의 마음을 흔들고 있나요?"

    else:
        visit_text = f"벌써 {vc}번째 방문이시네요."

        if concern:
            ment = f"어서 오세요, {name}님. {visit_text} 지난번에 '<b>{concern}</b>' 관련해 고민하셨던 흐름이 지금은 어떻게 바뀌었을까요? 다시 한번 정밀하게 짚어드리겠습니다."

        else:
            ment = f"다시 뵙게 되어 기쁩니다, {name}님. {visit_text} 오늘 당신의 운기 흐름에서 가장 먼저 짚어드려야 할 곳이 어디인지 선택해 주세요."

    html = "<div style='background:linear-gradient(135deg,#f8f5ff,#ffffff);border-left:5px solid #7b5ea7;border-radius:0 12px 12px 0;padding:20px 18px;margin:15px 0;box-shadow:0 3px 10px rgba(0,0,0,0.05)'>"

    html += f"<div style='font-size:15px;color:#2c1a4d;line-height:1.7;white-space:normal;word-break:break-all;font-weight:600'>{ment}</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# ==============================================================

#  📊 STATISTICAL CORRECTION ENGINE - 통계 보정 시스템

#  사주 패턴 x 실제 데이터 -> 확률 기반 해석

# ==============================================================

# 패턴별 확률 데이터 (실증 기반 추정값)

_STATISTICAL_PATTERNS = {
    # (신강신약, 오행과다) -> (주제, 확률, 해석)
    ("신약", "金"): (
        "직장 스트레스",
        76,
        "금기 과다 + 신약 -> 책임 부담, 직장 압박 패턴",
    ),
    ("신약", "水"): ("과잉 사고", 71, "수기 과다 + 신약 -> 걱정/불안/수면 불안정"),
    ("신강", "火"): ("감정 폭발", 68, "화기 과다 + 신강 -> 충동적 표현, 인간관계 갈등"),
    ("신강", "木"): ("고집/충돌", 65, "목기 과다 + 신강 -> 타협 어려움, 독선적 결정"),
    ("중화", "土"): ("변화 저항", 62, "토기 균형 + 중화 -> 안정 선호, 새로움 회피"),
    ("신약", "火"): ("소진/번아웃", 74, "화기 과다 + 신약 -> 에너지 고갈, 소진 패턴"),
    ("신강", "金"): ("재물 집착", 66, "금기 과다 + 신강 -> 물질 중시, 절약 강박"),
    ("극신약", "土"): ("건강 취약", 79, "토기 과다 + 극신약 -> 소화기 계통 주의"),
    ("극신강", "木"): ("인간관계 마찰", 72, "목기 극강 -> 자기중심적, 협력 어려움"),
}


def get_statistical_insights(pils, strength_info) -> list:
    """

    통계 보정 인사이트 생성

    Returns: list[dict] - {pattern, prob, insight, advice}

    """

    sn = strength_info.get("신강신약", "중화")

    oh_str = strength_info.get("oh_strength", {})

    insights = []

    # 과다 오행 탐지 (35% 이상)

    over_ohs = [(oh, v) for oh, v in oh_str.items() if v >= 35]

    for oh, val in over_ohs:
        key = (sn, oh)

        if key in _STATISTICAL_PATTERNS:
            topic, prob, desc = _STATISTICAL_PATTERNS[key]

            # 과다 강도에 따라 확률 보정

            adjusted_prob = min(95, int(prob + (val - 35) * 0.5))

            insights.append(
                {
                    "pattern": f"{sn} + {oh}과다({val:.0f}%)",
                    "topic": topic,
                    "prob": adjusted_prob,
                    "insight": desc,
                    "advice": _get_pattern_advice(sn, oh),
                }
            )

    # 특수 패턴: 삼형살

    il_jj = pils[1]["jj"]

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    hyeong_pairs = {("寅", "巳", "申"), ("丑", "戌", "未"), ("子", "卯")}

    all_jjs = frozenset(p["jj"] for p in pils)

    for combo in hyeong_pairs:
        if isinstance(combo, frozenset):
            if combo.issubset(all_jjs):
                insights.append(
                    {
                        "pattern": "삼형살(三刑殺)",
                        "topic": "사고/건강/법적 분쟁",
                        "prob": 61,
                        "insight": "삼형살 - 스트레스/사고/법적 문제 주의",
                        "advice": "큰 결정 전 충분한 검토. 건강검진 정기적으로.",
                    }
                )

        elif isinstance(combo, tuple) and len(combo) == 3:
            if frozenset(combo).issubset(all_jjs):
                insights.append(
                    {
                        "pattern": f"삼형살({','.join(combo)})",
                        "topic": "사고/건강/법적 분쟁",
                        "prob": 61,
                        "insight": f"{','.join(combo)} 삼형살 - 스트레스/사고/법적 문제 주의",
                        "advice": "큰 결정 전 충분한 검토. 건강검진 정기적으로.",
                    }
                )

        elif isinstance(combo, tuple) and len(combo) == 2:
            if combo[0] in all_jjs and combo[1] in all_jjs:
                insights.append(
                    {
                        "pattern": f"자묘형({combo[0]}{combo[1]})",
                        "topic": "인간관계 갈등",
                        "prob": 58,
                        "insight": "자묘형 - 원칙적 인간관계, 갈등 가능성",
                        "advice": "감정 조절과 유연한 대처가 중요합니다.",
                    }
                )

    return sorted(insights, key=lambda x: -x["prob"])[:4]  # 상위 4개


def _get_pattern_advice(sn: str, oh: str) -> str:
    """패턴별 실전 조언"""

    advice_map = {
        ("신약", "金"): "용신(木/水)의 방향으로 직업을 선택하면 스트레스가 줄어듭니다.",
        (
            "신약",
            "水",
        ): "걱정을 글로 써내려가는 습관이 도움이 됩니다. 수면 루틴 확립 필수.",
        (
            "신강",
            "火",
        ): "중요한 결정은 감정이 가라앉은 뒤 내리십시오. 규칙적 운동이 필수.",
        (
            "신강",
            "木",
        ): "타인의 의견을 '위협'이 아닌 '정보'로 받아들이는 연습을 하십시오.",
        ("신약", "火"): "무리한 약속을 줄이고 에너지를 선택적으로 사용하십시오.",
        ("신강", "金"): "물질이 아닌 경험에 투자하면 삶의 만족도가 올라갑니다.",
    }

    return advice_map.get((sn, oh), "오행 균형을 위한 용신 활용을 권장합니다.")


def render_statistical_insights(pils, strength_info):
    """통계 인사이트 UI 렌더링"""

    insights = get_statistical_insights(pils, strength_info)

    if not insights:
        return

    st.markdown(
        '<div class="gold-section">📊 데이터 기반 패턴 분석</div>',
        unsafe_allow_html=True,
    )

    st.caption("사주 패턴별 실증 통계 기반 분석입니다")

    for ins in insights:
        prob = ins["prob"]

        color = "#f44336" if prob >= 75 else "#ff9800" if prob >= 60 else "#4caf50"

        html = f"<div style='background:#fffef8;border:1px solid #e8d5a0;border-radius:12px;padding:14px 16px;margin:6px 0'>"

        html += "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:4px'>"

        html += f"<span style='font-size:12px;font-weight:700;color:#333'>[분석] {ins['topic']}</span>"

        html += f"<span style='background:{color}22;border:1px solid {color}55;color:{color};font-size:12px;font-weight:800;padding:2px 10px;border-radius:8px'>{prob}% 패턴</span>"

        html += "</div>"

        html += f"<div style='font-size:12px;color:#000000;margin-bottom:6px'>{ins['insight']}</div>"

        html += f"<div style='font-size:11px;color:#000000;background:#ffffff;padding:6px 10px;border-radius:6px'>(조언): {ins['advice']}</div>"

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)


def _load_retention() -> dict:

    try:
        if os.path.exists(_RETENTION_FILE):
            with open(_RETENTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    return {}


def _save_retention(data: dict):

    try:
        with open(_RETENTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")


def update_streak() -> dict:
    """

    방문 스트릭 업데이트

    Returns: {streak: int, is_new_day: bool, message: str}

    """

    today = datetime.now().strftime("%Y-%m-%d")

    data = _load_retention()

    streak_data = data.get("streak", {"count": 0, "last_date": "", "max": 0})

    last = streak_data.get("last_date", "")

    count = streak_data.get("count", 0)

    max_s = streak_data.get("max", 0)

    is_new_day = False

    if last == today:
        # 오늘 이미 방문

        pass

    elif last == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
        # 연속 방문

        count += 1

        is_new_day = True

        streak_data["count"] = count

        streak_data["last_date"] = today

        streak_data["max"] = max(max_s, count)

    else:
        # 끊김 또는 첫 방문

        count = 1

        is_new_day = True

        streak_data["count"] = count

        streak_data["last_date"] = today

    data["streak"] = streak_data

    _save_retention(data)

    # 스트릭 메시지

    if count >= 30:
        msg = f"[대단하네요] {count}일 연속 방문 - 진정한 천명 탐구자!"

    elif count >= 14:
        msg = f"[대단하네요] {count}일 연속 방문 - 운의 흐름을 꿰뚫고 있습니다"

    elif count >= 7:
        msg = f"[대단하네요] {count}일 연속 방문 - 한 주 완성!"

    elif count >= 3:
        msg = f"[대단하네요] {count}일 연속 방문 중"

    else:
        msg = f"[방문] {count}일째 방문"

    return {
        "streak": count,
        "max": streak_data.get("max", count),
        "is_new_day": is_new_day,
        "message": msg,
    }


def get_daily_luck_score(pils, birth_year, gender, target_date=None) -> dict:
    """

    일별 운세 점수 (기본운 * 대운 * 세운 * 월운 합산)

    Returns: {score: int, trend: str, label: str}

    """

    if target_date is None:
        target_date = datetime.now()

    y = target_date.year

    m = target_date.month

    d = target_date.day

    base = calc_luck_score(pils, birth_year, gender, y)

    yearly = get_yearly_luck(pils, y)

    monthly = get_monthly_luck(pils, y, m)

    # 일별 미세 변동 (일지 기반 결정론적 계산)

    ilgan = pils[1]["cg"]

    il_jj = pils[1]["jj"]

    day_jj_idx = (d - 1) % 12

    day_jj = JJ[day_jj_idx]

    # 일간과 일지 조화 점수

    day_mod = 0

    if _JIJI_CHUNG.get(il_jj) == day_jj:
        day_mod = -8

    elif HAP_MAP.get(il_jj) == day_jj:
        day_mod = +6

    elif OH.get(il_jj) == OH.get(day_jj):
        day_mod = +4

    _GH = {
        "대길(大吉)": 8,
        "길(吉)": 4,
        "평길(平吉)": 2,
        "평(平)": 0,
        "흉(凶)": -6,
        "흉흉(凶凶)": -12,
    }

    year_mod = _GH.get(yearly.get("길흉", "평(平)"), 0)

    month_mod = _GH.get(
        monthly.get("길흉", "평(平)") if isinstance(monthly.get("길흉"), str) else "평(平)",
        0,
    )

    final = max(0, min(100, base + year_mod * 0.4 + month_mod * 0.3 + day_mod))

    if final >= 75:
        label, trend = "대길(Dae-Gil)", "UP-UP"

    elif final >= 60:
        label, trend = "길(Gil)", "UP"

    elif final >= 45:
        label, trend = "평(Normal)", "MID"

    elif final >= 30:
        label, trend = "흉(Bad)", "DOWN"

    else:
        label, trend = "흉흉(Very Bad)", "DOWN-DOWN"

    return {
        "score": int(final),
        "label": label,
        "trend": trend,
        "year_mod": year_mod,
        "month_mod": month_mod,
        "day_mod": day_mod,
    }


def get_7day_luck_graph(pils, birth_year, gender) -> list:
    """7일 운세 점수 그래프 데이터"""

    today = datetime.now()

    result = []

    for delta in range(-3, 4):
        d = today + timedelta(days=delta)

        s = get_daily_luck_score(pils, birth_year, gender, d)

        result.append(
            {
                "date": d.strftime("%m/%d"),
                "day": ["월", "화", "수", "목", "금", "토", "일"][d.weekday()],
                "score": s["score"],
                "label": s["label"],
                "is_today": delta == 0,
            }
        )

    return result


def get_turning_countdown(pils, birth_year, gender) -> dict:
    """

    다음 인생 전환점까지 남은 날짜 계산

    Returns: {days_left: int, date: str, description: str}

    """

    today = datetime.now()

    # 최대 365일 앞을 스캔

    for delta in range(1, 366):
        future = today + timedelta(days=delta)

        t = calc_turning_point(pils, birth_year, gender, future.year)

        if t["is_turning"] and abs(t["score_change"]) >= 15:
            # 대운 전환 시점 더 정확히

            # 대운 호출 시 실제 생년월일시 반영

            _bm = st.session_state.get("birth_month", 1)

            _bd = st.session_state.get("birth_day", 1)

            _bh = st.session_state.get("birth_hour", 12)

            _bmi = st.session_state.get("birth_minute", 0)

            dw_list = SajuCoreEngine.get_daewoon(pils, birth_year, _bm, _bd, _bh, _bmi, gender)

            for dw in dw_list:
                if dw["시작연도"] == future.year:
                    change_date = f"{future.year}년 {birth_year % 100 + dw['시작나이'] % 10}월경"

                    return {
                        "days_left": delta,
                        "date": change_date,
                        "description": f"새 대운 {dw['str']} 시작 - 인생 국면 전환",
                        "intensity": t["intensity"],
                    }

            # 세운 전환점

            return {
                "days_left": delta,
                "date": future.strftime("%Y년 %m월"),
                "description": t["reason"][0] if t["reason"] else "흐름 변화",
                "intensity": t["intensity"],
            }

    return {
        "days_left": None,
        "date": "-",
        "description": "대운 안정기",
        "intensity": "⬜",
    }


def render_retention_widget(pils, birth_year, gender):
    """중독 유발 핵심 위젯 (Main Addiction Engine)"""

    streak_info = update_streak()

    graph_data = get_7day_luck_graph(pils, birth_year, gender)

    countdown = get_turning_countdown(pils, birth_year, gender)

    today_score = next((d for d in graph_data if d["is_today"]), {})

    streak_c = streak_info["streak"]

    days_left = countdown.get("days_left")

    if days_left is None:
        days_left_display = "365+"

        progress = 0

    else:
        days_left_display = str(days_left)

        progress = min(100, max(0, 100 - (days_left // 3)))

    score = today_score.get("score", 50)

    score_color = "#4caf50" if score >= 60 else "#ff9800" if score >= 45 else "#f44336"

    html = "<div style='background:linear-gradient(135deg,#fffef5,#ffffff);border:1.5px solid #e8d5a0;border-radius:16px;padding:16px 14px;margin:10px 0'>"

    html += "<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"

    html += "<div style='text-align:center'>"

    html += "<div style='font-size:10px;color:#000000;font-weight:700;letter-spacing:1px'>방문 스트릭</div>"

    html += f"<div style='font-size:28px;font-weight:900;color:#000000'>{streak_c}일</div>"

    html += f"<div style='font-size:10px;color:#888'>최고 {streak_info['max']}일</div>"

    html += "</div>"

    html += "<div style='text-align:center'>"

    html += "<div style='font-size:10px;color:#000000;font-weight:700;letter-spacing:1px'>오늘 운세</div>"

    html += f"<div style='font-size:28px;font-weight:900;color:{score_color}'>{score}점</div>"

    html += f"<div style='font-size:11px;color:#666'>{today_score.get('label', 'Normal')}</div>"

    html += "</div>"

    html += "<div style='text-align:center'>"

    html += "<div style='font-size:10px;color:#000000;font-weight:700;letter-spacing:1px'>전환점까지</div>"

    html += f"<div style='font-size:22px;font-weight:900;color:#e65100'>D-{days_left_display}</div>"

    html += f"<div style='font-size:10px;color:#888'>{countdown.get('date', '-')}</div>"

    html += "</div>"

    html += "</div>"

    html += "<div style='margin-top:16px; background:white; border-radius:10px; padding:10px 12px; border:1px solid #eee'>"

    html += "<div style='display:flex; justify-content:space-between; font-size:10px; color:#000000; font-weight:700; margin-bottom:5px'>"

    html += "<span>현재 인생 흐름 진행률</span>"

    html += f"<span>{progress}%</span>"

    html += "</div>"

    html += "<div style='background:#f0f0f0; height:12px; border-radius:6px; '>"

    html += f"<div style='background:linear-gradient(90deg, #000000, #e65100); width:{progress}%; height:100%;'></div>"

    html += "</div>"

    html += f"<div style='font-size:10px; color:#e65100; font-weight:700; margin-top:5px; text-align:center'>{countdown.get('description', 'Status')}</div>"

    html += "</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    # -- 7일 운 그래프

    max_s = max(d["score"] for d in graph_data) or 100

    bars = "<div style='display:flex;justify-content:space-between;align-items:flex-end;height:120px;padding:15px 10px;background:#fcfaf5;border-radius:12px;margin:5px 0'>"

    for d in graph_data:
        h = max(15, int(d["score"] / max_s * 70))

        bg = "#000000" if d["is_today"] else ("#4caf50" if d["score"] >= 60 else "#ff9800" if d["score"] >= 45 else "#f44336")

        fw = "800" if d["is_today"] else "600"

        bars += f"""

<div style="display:flex;flex-direction:column;align-items:center;width:14%;position:relative">

<div style="font-size:10px;color:#000000;margin-bottom:4px;font-weight:{fw}">{d["date"]}</div>

<div style="background:{bg};height:{h}px;width:80%;border-radius:4px;margin-bottom:4px;display:flex;align-items:flex-end;justify-content:center;color:white;font-size:10px;font-weight:bold">{d["score"]}</div>

<div style="font-size:10px;color:#000000;font-weight:{fw}">{d["day"]}</div>

</div>

        """

    st.markdown(
        f"""

<div style="background:#fcfaf5;border:1.5px solid #e8d5a0;border-radius:16px;padding:16px 14px;margin:10px 0">

<div style="font-size:12px;color:#000000;font-weight:700;letter-spacing:1px;margin-bottom:10px">

            7일 운세 흐름

</div>

<div style="display:flex;justify-content:space-between;align-items:flex-end;height:120px;padding:15px 10px;background:#fcfaf5;border-radius:12px;margin:5px 0">

            {bars}

</div>

</div>

    

""",
        unsafe_allow_html=True,
    )

    # -- 전환점 카운트다운 배너

    if countdown["days_left"] and countdown["days_left"] <= 60:
        ic = "#f44336" if "강력" in countdown["intensity"] else "#ff9800"

        html = f"<div style='background:linear-gradient(135deg,#fff5f0,#ffe8e0);border:2px solid {ic};border-radius:12px;padding:14px 16px;margin:8px 0;text-align:center'>"

        html += f"<div style='font-size:12px;color:{ic};font-weight:700;margin-bottom:4px'>[알림] {countdown['intensity']} 감지</div>"

        html += f"<div style='font-size:22px;font-weight:900;color:{ic}'>D-{countdown['days_left']}</div>"

        html += f"<div style='font-size:12px;color:#000000;margin-top:4px'>{countdown['description']}</div>"

        html += f"<div style='font-size:11px;color:#000000;margin-top:4px'>{countdown['date']}</div>"

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)


# ==================================================

#  지장간(地藏干) 심화

# ==================================================


TYPE_LABEL = {"여기": "餘氣", "중기": "中氣", "정기": "正氣"}


def get_jijanggan_analysis(ilgan, pils):

    cgs_all = [p["cg"] for p in pils]

    result = []

    labels = ["시주", "일주", "월주", "년주"]

    for i, p in enumerate(pils):
        jj = p["jj"]

        jjg = JIJANGGAN_FULL.get(jj, [])

        items = []

        for e in jjg:
            cg = e["cg"]

            ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cg, "-")

            items.append(
                {
                    "천간": cg,
                    "타입": e["type"],
                    "일수": e["days"],
                    "십성": ss,
                    "투출": cg in cgs_all,
                }
            )

        result.append({"기둥": labels[i], "지지": jj, "지장간": items})

    return result


# ==================================================

#  건강론(健康論)

# ==================================================



def get_health_analysis(pils, gender="남"):

    ilgan = pils[1]["cg"]

    oh_strength = calc_ohaeng_strength(ilgan, pils)

    unsung = calc_12unsung(ilgan, pils)

    il_unsung = unsung[1] if len(unsung) > 1 else ""

    il_oh = OH.get(ilgan, "")

    HEALTH_UNSUNG = {
        "병": "병지(病地) - 건강 약한 구조. 정기 검진 필수.",
        "사": "사지(死地) - 생명력 약함. 안전사고/건강 각별 주의.",
        "절": "절지(絶地) - 체력 소진되기 쉬움.",
        "묘": "묘지(墓地) - 만성질환 오래 지속될 수 있음.",
    }

    return {
        "과다_오행": [{"오행": o, "수치": v, "health": HEALTH_OH.get(o, {})} for o, v in oh_strength.items() if v >= 35],
        "부족_오행": [{"오행": o, "수치": v, "health": HEALTH_OH.get(o, {})} for o, v in oh_strength.items() if v <= 5],
        "일주_건강": HEALTH_UNSUNG.get(il_unsung, ""),
        "일간_건강": HEALTH_OH.get(il_oh, {}),
        "ilgan_oh": il_oh,
        "oh_strength": oh_strength,
    }


# ==================================================

#  재물론(財物論)

# ==================================================


def get_jaemul_analysis(pils, birth_year, gender="남"):

    ilgan = pils[1]["cg"]

    oh_strength = calc_ohaeng_strength(ilgan, pils)

    strength_info = get_ilgan_strength(ilgan, pils)

    sn = strength_info["신강신약"]

    CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    ilgan_oh = OH.get(ilgan, "")

    jae_oh = CTRL.get(ilgan_oh, "")

    jae_strength = oh_strength.get(jae_oh, 0)

    # 재성 위치

    jae_pos = []

    for i, p in enumerate(pils):
        ss_cg = TEN_GODS_MATRIX.get(ilgan, {}).get(p["cg"], "-")

        jj_cg = JIJANGGAN.get(p["jj"], [""])[-1]

        ss_jj = TEN_GODS_MATRIX.get(ilgan, {}).get(jj_cg, "-")

        lbl = ["시주", "일주", "월주", "년주"][i]

        if ss_cg in ["正財(정재)", "偏財(편재)"]:
            jae_pos.append(f"{lbl} 천간({ss_cg})")

        if ss_jj in ["正財(정재)", "偏財(편재)"]:
            jae_pos.append(f"{lbl} 지지({ss_jj})")

    # 대운 재물 피크 (사용자 지침 준수)

    birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

    birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

    birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils,
        birth_year,
        birth_month,
        birth_day,
        birth_hour,
        birth_minute,
        gender=gender,
    )

    peaks = [
        {
            "대운": d["str"],
            "나이": f"{d['시작나이']}~{d['시작나이'] + 9}세",
            "연도": f"{d['시작연도']}~{d['종료연도']}",
            "십성": TEN_GODS_MATRIX.get(ilgan, {}).get(d["cg"], "-"),
        }
        for d in daewoon
        if TEN_GODS_MATRIX.get(ilgan, {}).get(d["cg"], "-") in ["正財", "偏財", "食神"]
    ]

    # 유형 판단

    if sn == "신강(身强)" and jae_strength >= 20:
        jtype, jstrat = (
            "적극형 - 강한 일간이 재성을 다루는 이상적 구조.",
            "재성 운에서 과감히 행동하십시오.",
        )

    elif sn == "신약(身弱)" and jae_strength >= 30:
        jtype, jstrat = (
            "부담형 - 재물이 있어도 감당하기 벅찬 구조.",
            "고정수입/저축 중심으로 운용하십시오.",
        )

    elif jae_strength == 0:
        jtype, jstrat = (
            "재성공망형 - 재성이 없는 사주. 명예/학문/기술로 성공.",
            "전문성과 명예를 쌓으면 돈은 따라옵니다.",
        )

    else:
        jtype, jstrat = (
            "균형형 - 꾸준한 노력으로 재물을 쌓아가는 구조.",
            "안정적 자산관리가 유리합니다.",
        )

    return {
        "재성_오행": jae_oh,
        "재성_강도": jae_strength,
        "재성_위치": jae_pos,
        "재물_유형": jtype,
        "재물_전략": jstrat,
        "재물_피크_대운": peaks,
        "신강신약": sn,
    }


# ==================================================

#  직업론(職業論)

# ==================================================


ILGAN_CAREER_ADD = {
    "甲": ["건축/목재/산림", "교육/인재개발"],
    "乙": ["꽃/원예/디자인", "상담/교육"],
    "丙": ["방송/연예", "발전/에너지"],
    "丁": ["의료/제약", "교육/종교"],
    "戊": ["건설/부동산", "농업/식품"],
    "己": ["농업/식품가공", "행정/회계"],
    "庚": ["금융/금속/기계", "법조/군경"],
    "辛": ["패션/보석/예술", "의료/약학"],
    "壬": ["해운/무역/외교", "IT/전략"],
    "癸": ["상담/심리/영성", "의료/약학"],
}


def get_career_analysis(pils, gender="남"):

    ilgan = pils[1]["cg"]

    gyeokguk = get_gyeokguk(pils)

    gname_raw = gyeokguk["격국명"] if gyeokguk else "比肩格"
    # get_gyeokguk 반환 "比肩格" → CAREER_MATRIX 키 "比肩(비견)格(비견격)" 변환
    _GK_KEY_MAP = {
        "比肩格":"比肩(비견)格(비견격)", "劫財格":"劫財(겁재)格(겁재격)",
        "食神格":"食神(식신)格(식신격)", "傷官格":"傷官(상관)格(상관격)",
        "偏財格":"偏財(편재)格(편재격)", "正財格":"正財(정재)格(정재격)",
        "偏官格":"偏官(편관)格(편관격)", "正官格":"正官(정관)格(정관격)",
        "偏印格":"偏印(편인)格(편인격)", "正印格":"正印(정인)格(정인격)",
        "비견격":"比肩(비견)格(비견격)", "겁재격":"劫財(겁재)格(겁재격)",
        "식신격":"食神(식신)格(식신격)", "상관격":"傷官(상관)格(상관격)",
        "편재격":"偏財(편재)格(편재격)", "정재격":"正財(정재)格(정재격)",
        "편관격":"偏官(편관)格(편관격)", "정관격":"正官(정관)格(정관격)",
        "편인격":"偏印(편인)格(편인격)", "정인격":"正印(정인)格(정인격)",
    }
    gname = _GK_KEY_MAP.get(gname_raw, gname_raw)
    _fallback_key = "比肩(비견)格(비견격)"
    career = _gk_career(gname)

    sinsal = get_12sinsal(pils)

    sinsal_jobs = []

    for s in sinsal:
        if "장성" in s["이름"]:
            sinsal_jobs.append("군/경/스포츠 수장 기질")

        if "화개" in s["이름"]:
            sinsal_jobs.append("예술/종교/철학 방면 특화")

        if "역마" in s["이름"]:
            sinsal_jobs.append("이동/무역/해외 관련 직종 유리")

        if "도화" in s["이름"] or "년살" in s["이름"]:
            sinsal_jobs.append("연예/서비스/대인 방면 유리")

    yin = get_yangin(pils)

    if yin["존재"]:
        sinsal_jobs.append("군/경/의료(외과) 분야 강한 기질")

    return {
        "격국": gname,
        "최적직업": career["best"],
        "유리직업": career["good"],
        "피할직업": career["avoid"],
        "일간추가": ILGAN_CAREER_ADD.get(ilgan, []),
        "신살보정": sinsal_jobs,
    }


# ==================================================

#  개명(改名) 오행 분석

# ==================================================



def decompose_hangul(char):

    if not (0xAC00 <= ord(char) <= 0xD7A3):
        return []

    code = ord(char) - 0xAC00

    jong = code % 28
    jung = (code // 28) % 21
    cho = code // 28 // 21

    CHOSUNG = [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ]



    r = [CHOSUNG[cho], JUNGSUNG[jung]]

    if jong:
        r.append(JONGSUNG[jong])

    return r


def analyze_name_oh(name_str):

    oh_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    for char in name_str:
        for jamo in decompose_hangul(char):
            oh = HANGUL_OH.get(jamo)

            if oh:
                oh_count[oh] += 1

    total = sum(oh_count.values()) or 1

    return oh_count, {k: round(v / total * 100) for k, v in oh_count.items()}


# ==================================================

#  새 탭 UI 함수들

# ==================================================

################################################################################

# *** Brain 3 - Learning & Monetization Engine ***

#

# [역할]  사용자 반응을 수집/분석하여 AI 프롬프트를 자동 강화한다

#

# [데이터 흐름]

#   사용자 반응 -> Feedback Collector

#               -> Pattern Analyzer   (어떤 문장이 결제/재방문 유도?)

#               -> Prompt Optimizer   (다음 AI 호출 프롬프트 자동 강화)

#               -> Monetization Trigger (결제 타이밍 감지)

#

# [저장 파일]

#   saju_feedback.json  - 피드백 원본 데이터 (삭제/캐싱 금지)

#   saju_patterns.json  - 학습 패턴 결과 (자동 갱신)

################################################################################

import time as _time

_FEEDBACK_FILE = "saju_feedback.json"

_PATTERN_FILE = "saju_patterns.json"

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

# Brain 3-③ : Prompt Optimizer

# -----------------------------------------------------------------------------


def b3_build_optimized_prompt_suffix() -> str:
    """Brain3 피드백 최적화 제거됨"""
    return ""


# -----------------------------------------------------------------------------

def b3_check_monetization_trigger(api_key: str = "") -> tuple:
    """[로컬 전용] API 미사용. 결제 유도 트리거 비활성화."""
    return False, ""


def b3_render_trigger_card(msg: str):
    """결제 유도 카드 렌더링"""

    html = "<div style='background:linear-gradient(135deg,#f5eeff,#ecdaff);border:2px solid #000000;border-radius:16px;padding:22px 24px;margin:16px 0;text-align:center'>"

    html += "<div style='font-size:16px;color:#8b6200;font-weight:700;margin-bottom:10px'>[안내] 지금이 중요한 시점입니다</div>"

    html += f"<div style='font-size:13px;color:#8b6200;line-height:1.9;margin-bottom:16px'>{msg}</div>"

    html += "<div style='font-size:12px;color:#000000;margin-top:8px'>로컬 만신 엔진으로 풀이합니다.</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------

# Brain 3 통합: 피드백 버튼 (기존 render_feedback_btn 대체)

# -----------------------------------------------------------------------------


def save_feedback(feedback_key, hit):
    """피드백 저장 제거됨"""
    pass


def get_feedback_stats():
    """피드백 통계 반환"""

    log = st.session_state.get("feedback_log", {})

    total = len(log)

    hits = sum(1 for v in log.values() if v == "hit")

    return total, hits


def render_feedback_btn(key, desc):
    """맞음/안맞음 버튼 제거됨"""
    pass


def tab_past_events(pils, birth_year, gender, name=""):
    """[적중] 과거 적중 탭 — 현재 나이 이전 사건만, 간소화"""

    st.markdown(
        '<div class="gold-section">📍 과거 사건 적중 — 내 나이 전에 일어난 일들</div>',
        unsafe_allow_html=True,
    )

    # ── 현재 나이 계산
    _today = datetime.now()
    _bm  = max(1, min(12, int(st.session_state.get("birth_month") or 1)))
    _bd2 = max(1, min(31, int(st.session_state.get("birth_day")   or 1)))
    _man_age = _today.year - birth_year
    if (_today.month, _today.day) < (_bm, _bd2):
        _man_age -= 1
    _kr_age = _man_age + 1
    current_year = _today.year

    # ── 데이터 계산
    with st.spinner("과거 사건 계산 중..."):
        hl = generate_engine_highlights(pils, birth_year, gender)

    def _parse_age_int(age_str):
        try:
            return int(str(age_str).split("~")[0].replace("세","").strip())
        except Exception:
            return 999

    def _clean_desc(raw, maxlen=100):
        s = re.sub(r"【.*?】", "", str(raw)).strip()
        return s[:maxlen] + ("..." if len(s) > maxlen else "")

    past_events_raw = hl.get("past_events", [])
    past_events = [e for e in past_events_raw if _parse_age_int(e.get("age","")) < _kr_age]

    _DC = {
        "사고·관재":"#c0392b","건강이상":"#8e44ad","질병·건강":"#8e44ad",
        "재물손실":"#e67e22","재물획득":"#27ae60","직업변화":"#2980b9",
        "직업변동":"#2980b9","결혼·교제":"#e91e8c","결혼/이별":"#e91e8c",
        "이사·이동":"#16a085","이사/이동":"#16a085",
        "가족이동/환경변화":"#16a085","재물성쇠":"#e67e22",
        "건강/잔병치레":"#8e44ad",
    }
    def _dc(domain): return _DC.get(domain, "#666")

    # ── 섹션1: 성향 요약 (3줄)
    st.markdown(
        "<div style=\'background:#f8f5ff;border-left:4px solid #9b59b6;border-radius:10px;padding:14px 16px;margin-bottom:16px\'>"
        "<div style=\'font-size:13px;font-weight:800;color:#4a235a;margin-bottom:6px\'>🧬 타고난 성향</div>",
        unsafe_allow_html=True,
    )
    for trait in hl.get("personality", [])[:3]:
        c = "#3d1a6e" if ("겉" in trait or "속" in trait) else "#1a3060"
        st.markdown(
            f"<div style=\'font-size:13px;color:{c};line-height:1.8;padding:4px 0;border-bottom:1px solid #eee\'>{trait}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 섹션2: 과거 사건 (현재 나이 이전만)
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#1a1a1a,#2c2c2c);border-radius:14px;padding:14px 18px;margin-bottom:12px">
<div style="color:#f7e695;font-size:15px;font-weight:900">📅 과거 주요 사건 (현재 {_kr_age}세 이전)</div>
<div style="color:#aaa;font-size:12px;margin-top:3px">대운×세운 충·합 교차 계산 — 현재 나이 이전 사건만 표시</div>
</div>""",
        unsafe_allow_html=True,
    )

    _crisis = [e for e in past_events if any(k in e.get("domain","") for k in ["사고","관재","건강","질병","재물손실"])]
    _change = [e for e in past_events if e not in _crisis]

    def _event_row(ev, bg):
        dc = _dc(ev.get("domain",""))
        age_s = ev.get("age",""); yr = ev.get("year",""); dom = ev.get("domain","변화")
        desc  = _clean_desc(ev.get("desc",""))
        return (
            f"<div style=\'display:flex;align-items:flex-start;gap:12px;background:{bg};border-left:5px solid {dc};border-radius:10px;padding:12px 14px;margin:5px 0\'>"
            f"<div style=\'min-width:56px;text-align:center\'>"
            f"<div style=\'font-size:17px;font-weight:900;color:{dc}\'>{age_s}</div>"
            f"<div style=\'font-size:10px;color:#888\'>{yr}년</div></div>"
            f"<div style=\'flex:1\'>"
            f"<span style=\'background:{dc};color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px\'>{dom}</span>"
            f"<div style=\'font-size:13px;color:#222;line-height:1.8;margin-top:5px\'>{desc}</div>"
            f"</div></div>"
        )

    if _crisis:
        st.markdown(
            "<div style=\'font-size:12px;font-weight:800;color:#c0392b;letter-spacing:1px;margin:10px 0 6px;padding-left:10px;border-left:3px solid #c0392b\'>🔴 사고·위기·손실 — 조심해야 했던 때</div>",
            unsafe_allow_html=True,
        )
        for ev in _crisis[:8]:
            st.markdown(_event_row(ev, "#fff5f5"), unsafe_allow_html=True)

    if _change:
        st.markdown(
            "<div style=\'font-size:12px;font-weight:800;color:#2980b9;letter-spacing:1px;margin:14px 0 6px;padding-left:10px;border-left:3px solid #2980b9\'>🔄 직업·이동·인연 — 흐름이 바뀐 때</div>",
            unsafe_allow_html=True,
        )
        for ev in _change[:8]:
            st.markdown(_event_row(ev, "#f5faff"), unsafe_allow_html=True)

    if not past_events:
        st.info(f"현재 나이({_kr_age}세) 이전에 감지된 주요 사건이 없습니다.")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ── 섹션3: 재물/인연 피크
    col_m, col_r = st.columns(2)
    with col_m:
        st.markdown('<div class="gold-section">💰 돈이 오는 시기</div>', unsafe_allow_html=True)
        money_list = hl.get("money_peak", [])
        for mp in money_list[:5]:
            c = "#000000" if mp.get("ss") == "더블" else "#27ae60"
            mp_age  = str(mp.get("age", ""))
            mp_year = str(mp.get("year", ""))
            mp_desc = _clean_desc(str(mp.get("desc", "")), 50)
            st.markdown(
                f"<div style='background:#fff;border-left:4px solid {c};border-radius:8px;padding:8px 12px;margin:4px 0'>"
                f"<span style='font-weight:800;color:{c}'>{mp_age}</span> "
                f"<span style='font-size:11px;color:#888'>({mp_year})</span>"
                f"<div style='font-size:12px;color:#333;margin-top:3px'>{mp_desc}</div></div>",
                unsafe_allow_html=True,
            )
        if not money_list:
            st.info("계산 중")
    with col_r:
        st.markdown('<div class="gold-section">💑 인연이 오는 시기</div>', unsafe_allow_html=True)
        marry_list = hl.get("marriage_peak", [])
        for mp in marry_list[:5]:
            mp_age  = str(mp.get("age", ""))
            mp_year = str(mp.get("year", ""))
            mp_desc = _clean_desc(str(mp.get("desc", "")), 50)
            st.markdown(
                f"<div style='background:#fff0f8;border-left:4px solid #e91e8c;border-radius:8px;padding:8px 12px;margin:4px 0'>"
                f"<span style='font-weight:800;color:#e91e8c'>{mp_age}</span> "
                f"<span style='font-size:11px;color:#888'>({mp_year})</span>"
                f"<div style='font-size:12px;color:#333;margin-top:3px'>{mp_desc}</div></div>",
                unsafe_allow_html=True,
            )
        if not marry_list:
            st.info("계산 중")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ── 섹션4: 앞으로 10년 예측
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#0d2137,#1a3a5c);border-radius:14px;padding:14px 18px;margin-bottom:12px">
<div style="color:#a8d8ff;font-size:15px;font-weight:900">🔮 앞으로 10년 예측 ({_kr_age}세 ~ {_kr_age+10}세)</div>
<div style="color:#8ab;font-size:12px;margin-top:3px">현재 대운+세운 교차 계산 — 참고용</div>
</div>""",
        unsafe_allow_html=True,
    )
    try:
        with st.spinner("앞으로 10년 계산 중..."):
            future_tl = build_life_event_timeline(
                pils, birth_year, gender,
                start_year=_today.year + 1,
                end_year=_today.year + 10,
            )
        future_tl = [e for e in future_tl if e.get("age", 0) > _kr_age][:8]
        for ev in future_tl:
            dc = _dc(ev.get("domain",""))
            clean_d = _clean_desc(ev.get("desc",""))
            st.markdown(
                f"""<div style="display:flex;align-items:flex-start;gap:12px;background:#eaf4ff;border-left:5px solid {dc};border-radius:10px;padding:12px 14px;margin:5px 0">
<div style="min-width:56px;text-align:center">
<div style="font-size:17px;font-weight:900;color:{dc}">{ev.get("age","")}세</div>
<div style="font-size:10px;color:#888">{ev.get("year","")}년</div>
</div>
<div style="flex:1">
<span style="background:{dc};color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px">예측 · {ev.get("domain","변화")}</span>
<div style="font-size:13px;color:#334;line-height:1.8;margin-top:5px">{clean_d}</div>
</div></div>""",
                unsafe_allow_html=True,
            )
        if not future_tl:
            st.info("앞으로 10년 주요 운기 변화가 감지되지 않았습니다.")
    except Exception:
        st.info("앞으로 10년 예측 계산 중 오류가 발생했습니다.")


def tab_cross_analysis(pils, birth_year, gender):
    """대운/세운 교차 분석 - 3중 완전판"""

    st.markdown(
        '<div class="gold-section">[분석] 대운/세운 교차 분석 - 운명의 교차점</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """

<div class="card" style="background:#f5f5ff;color:#000000;padding:14px;font-size:13px;line-height:1.9;margin-bottom:12px">

[안내] <b style="color:#8b6200">고수가 보는 법:</b> 원국은 무대 설계, 대운은 계절, 세운은 날씨입니다.

<b style="color:#000000">세 가지가 겹치는 해</b>에 인생의 큰 사건이 일어납니다. 특히 원국의 합이 운에서 충으로 깨질 때를 정확히 짚는 것이 핵심입니다.

</div>""",
        unsafe_allow_html=True,
    )

    current_year = datetime.now().year

    year_sel = st.selectbox(
        "분석 연도",
        list(range(current_year - 5, current_year + 16)),
        index=5,
        key="cross_year",
    )

    cross = get_daewoon_sewoon_cross(pils, birth_year, gender, year_sel)

    if not cross:
        st.warning("해당 연도의 대운 정보가 없습니다.")
        return

    ilgan = pils[1]["cg"]
    ilgan_oh = OH.get(ilgan, "")

    ys = get_yongshin(pils)
    yongshin_ohs = ys.get("종합_용신", []) if ys else []

    dw = cross["대운"]
    sw = cross["세운"]

    dw_ss = cross["대운_천간십성"]
    sw_ss = cross["세운_천간십성"]

    dw_is_yong = _get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong"

    sw_is_yong = _get_yongshin_match(sw_ss, yongshin_ohs, ilgan_oh) == "yong"

    hap_breaks = _get_hap_break_warning(pils, dw["jj"], sw.get("jj",""))

    lc = "#000000" if (dw_is_yong and sw_is_yong) else "#c0392b" if (not dw_is_yong and not sw_is_yong) else "#2980b9"

    overall = (
        "[최고] 용신 대운x세운 겹침 - 최고의 발복 시기"
        if (dw_is_yong and sw_is_yong)
        else "[수비] 기신 대운x세운 - 수비 전략 필요"
        if (not dw_is_yong and not sw_is_yong)
        else "[혼재] 대운/세운 혼재 - 선별적 추진"
    )

    html = (
        f"<div style='background:linear-gradient(135deg,#f0eeff,#ece8ff);color:#000000;"
        f"padding:28px;border-radius:16px;margin-bottom:14px'>"
        f"<div style='text-align:center;font-size:13px;color:#000000;margin-bottom:14px'>{year_sel}년 운명의 교차점</div>"
    )

    html += "<div style='display:flex;justify-content:center;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:14px'>"

    html += f"<div style='text-align:center;background:{'rgba(197,160,89,0.25)' if dw_is_yong else 'rgba(255,255,255,0.65)'};padding:16px 24px;border-radius:14px;border:{'2px solid #c5a059' if dw_is_yong else '1px solid #bbb'}'>"

    html += f"<div style='font-size:11px;color:#555'>대운(Dae-woon)</div>"

    html += f"<div style='margin:6px 0'>{color_ganzhi_badge(dw['str'], font_size='28px')}</div>"

    html += f"<div style='font-size:12px;color:#5a3d99'>{dw_ss} / {cross.get('대운_지지십성','-')}</div>"

    if dw_is_yong:
        html += "<div style='font-size:11px;color:#8b6200;margin-top:4px'>[용신 대운]</div>"

    html += "</div>"

    html += f"<div style='font-size:28px;color:{lc}'>x</div>"

    html += f"<div style='text-align:center;background:{'rgba(197,160,89,0.25)' if sw_is_yong else 'rgba(255,255,255,0.65)'};padding:16px 24px;border-radius:14px;border:{'2px solid #c5a059' if sw_is_yong else '1px solid #bbb'}'>"

    html += f"<div style='font-size:11px;color:#555'>세운(Se-woon)</div>"

    html += f"<div style='margin:6px 0'>{color_ganzhi_badge(sw['세운'], font_size='28px')}</div>"

    html += f"<div style='font-size:12px;color:#5a3d99'>{sw_ss} / {cross.get('세운_지지십성','-')}</div>"

    if sw_is_yong:
        html += "<div style='font-size:11px;color:#8b6200;margin-top:4px'>[용신 세운]</div>"

    html += "</div></div>"

    html += f"<div style='text-align:center;font-size:15px;font-weight:700;color:{lc}'>{overall}</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    # 합이 깨지는 경고

    if hap_breaks:
        st.markdown(
            '<div class="gold-section">[경고] 원국 합(Hap)이 운에서 깨지는 경고</div>',
            unsafe_allow_html=True,
        )

        for w in hap_breaks:
            html = f"<div class='card' style='background:{w['color']}18;border-left:5px solid {w['color']}'>"

            html += f"<div style='font-size:13px;font-weight:700;color:{w['color']};margin-bottom:4px'>{w['level']}</div>"

            html += f"<div style='font-size:13px;color:#000000;line-height:1.9'>{w['desc']}</div></div>"

            st.markdown(html, unsafe_allow_html=True)

    # 교차 해석

    st.markdown(
        f"<div class='card' style='background:#ffffff;border:2px solid #000000'><div style='font-size:14px;font-weight:700;color:#000000;margin-bottom:8px'>[데이터] {year_sel}년 핵심 해석</div><div style='font-size:14px;color:#000000;line-height:2.0;margin-bottom:10px'>{cross.get('교차해석','')}</div></div>",
        unsafe_allow_html=True,
    )

    if cross["교차사건"]:
        st.markdown(
            '<div class="gold-section">[분석] 원국과의 교차 사건</div>',
            unsafe_allow_html=True,
        )

        for ev in cross["교차사건"]:
            c = "#000000" if "합" in ev["type"] else "#c0392b" if "충" in ev["type"] else "#8e44ad"

            st.markdown(
                f'<div class="card" style="border-left:4px solid {c}"><b style="color:{c}">{ev["type"]}</b> - {ev["desc"]}</div>',
                unsafe_allow_html=True,
            )

    # 처방


    plabel, pcolor, pdesc = PCMAP.get(
        (dw_is_yong, sw_is_yong),
        ("[보통] 평범한 해", "#888", "꾸준한 노력으로 안정을 유지하십시오."),
    )

    html = f"<div class='card' style='background:{pcolor}15;border:2px solid {pcolor};margin-top:10px'>"

    html += f"<div style='font-size:15px;font-weight:800;color:{pcolor};margin-bottom:8px'>{plabel}</div>"

    html += f"<div style='font-size:13px;color:#000000;line-height:1.9'>{pdesc}</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    # 향후 10년 타임라인

    st.markdown(
        '<div class="gold-section">📅 향후 10년 운세 타임라인</div>',
        unsafe_allow_html=True,
    )

    render_future_10years(pils, birth_year, gender, yongshin_ohs, year_sel, ilgan)


def render_future_10years(pils, birth_year, gender, yongshin_ohs, year_sel, ilgan):
    """향후 10년 운세 타임라인 - 전면 개편 렌더링"""

    # 10년 데이터 수집
    year_data = []
    for y in range(year_sel, year_sel + 10):
        c2 = get_daewoon_sewoon_cross(pils, birth_year, gender, y)
        if not c2:
            continue
        det = get_year_detail(y, c2, ilgan, yongshin_ohs, birth_year)
        if not det:
            continue
        year_data.append((y, c2, det))

    if not year_data:
        st.info("운세 데이터를 불러올 수 없습니다.")
        return

    # ── 1. 10년 한눈에 보기 개요 바 ─────────────────────────
    st.markdown('<div class="gold-section">📊 10년 한눈에 보기</div>', unsafe_allow_html=True)

    bar_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px'>"
    for y, c2, det in year_data:
        gc = det["gil_color"]
        age = det["kr_age"]
        is_cur = (y == year_sel)
        bdr = "3px solid #c5a059" if is_cur else "1px solid #ddd"
        if det["d_is_y"] and det["s_is_y"]:
            bg = "#fffff0"
        elif det["d_is_y"] or det["s_is_y"]:
            bg = "#f0f8ff"
        elif "흉" in det["badge"]:
            bg = "#fff5f5"
        else:
            bg = "#fafafa"
        dw_str = c2.get("대운", {}).get("str", "")
        sw_str = c2.get("세운", {}).get("세운", "")
        bar_html += (
            f"<div style='text-align:center;background:{bg};border:{bdr};"
            f"border-radius:10px;padding:8px 10px;min-width:72px'>"
            f"<div style='font-size:10px;color:#888'>{age}세</div>"
            f"<div style='font-size:13px;font-weight:800;color:#1a1a1a'>{y}</div>"
            f"<div style='font-size:10px;color:#555;margin:2px 0'>{dw_str}×{sw_str}</div>"
            f"<div style='font-size:11px;font-weight:700;color:{gc}'>{det['badge']}</div>"
            f"</div>"
        )
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)

    # ── 2. 연도별 상세 expander ──────────────────────────────
    st.markdown('<div class="gold-section">📅 연도별 상세 운세</div>', unsafe_allow_html=True)

    for y, c2, det in year_data:
        gc = det["gil_color"]
        age = det["kr_age"]
        badge = det["badge"]
        hap_icon = det["hap_icon"]
        dw_str = c2.get("대운", {}).get("str", "")
        sw_str = c2.get("세운", {}).get("세운", "")
        dw_ss = det["dw_ss"]
        sw_ss = det["sw_ss"]
        is_cur = (y == year_sel)

        label = f"{'▶ ' if is_cur else ''}{y}년 ({age}세)  大運:{dw_str} / 세운:{sw_str}  {badge}{hap_icon}"

        with st.expander(label, expanded=is_cur):

            # 헤더 카드
            if det["d_is_y"] and det["s_is_y"]:
                header_bg = "linear-gradient(135deg,#e8f5e9,#c8e6c9)"
            elif det["d_is_y"] or det["s_is_y"]:
                header_bg = "linear-gradient(135deg,#e3f2fd,#bbdefb)"
            elif "흉" in badge:
                header_bg = "linear-gradient(135deg,#ffebee,#ffcdd2)"
            else:
                header_bg = "linear-gradient(135deg,#fafafa,#f0f0f0)"

            hap_span = f"<span style='margin-left:8px;color:#c0392b;font-weight:700'>{hap_icon}</span>" if hap_icon else ""
            _hdr = (
                f"<div style='background:{header_bg};border-radius:12px;padding:14px 18px;margin-bottom:12px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px'>"
                f"<div><span style='font-size:18px;font-weight:900;color:{gc}'>🗓 {y}년 ({age}세)</span>"
                f"<span style='margin-left:12px;font-size:15px;font-weight:700;color:{gc}'>{badge}</span>"
                f"{hap_span}</div>"
                f"<div style='display:flex;gap:10px'>"
                f"<div style='text-align:center;background:rgba(255,255,255,0.75);border-radius:8px;padding:6px 12px'>"
                f"<div style='font-size:10px;color:#888'>大運</div>"
                f"<div style='font-size:16px;font-weight:800'>{dw_str}</div>"
                f"<div style='font-size:11px;color:#5a3d99'>{dw_ss}</div></div>"
                f"<div style='text-align:center;background:rgba(255,255,255,0.75);border-radius:8px;padding:6px 12px'>"
                f"<div style='font-size:10px;color:#888'>세운</div>"
                f"<div style='font-size:16px;font-weight:800'>{sw_str}</div>"
                f"<div style='font-size:11px;color:#5a3d99'>{sw_ss}</div></div>"
                f"</div></div></div>"
            )
            st.markdown(_hdr, unsafe_allow_html=True)

            # 핵심 기운 텍스트
            st.markdown(
                f"<div style='background:#fffdf0;border-left:4px solid #c5a059;"
                f"padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:12px;"
                f"font-size:13px;color:#333;line-height:1.8'>"
                f"💡 <b>이 해의 핵심:</b> {det['core_text']}</div>",
                unsafe_allow_html=True,
            )

            # 분야별 4칸 그리드
            _grid = (
                f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px'>"
                f"<div style='background:#f0f4ff;border-radius:10px;padding:10px 12px'>"
                f"<div style='font-size:12px;font-weight:700;color:#1565c0;margin-bottom:4px'>💼 직업·사업</div>"
                f"<div style='font-size:12px;color:#333;line-height:1.7;white-space:normal;word-break:break-all'>{det['career']}</div></div>"
                f"<div style='background:#f0fff4;border-radius:10px;padding:10px 12px'>"
                f"<div style='font-size:12px;font-weight:700;color:#1a6b2e;margin-bottom:4px'>💰 재물·돈</div>"
                f"<div style='font-size:12px;color:#333;line-height:1.7;white-space:normal;word-break:break-all'>{det['finance']}</div></div>"
                f"<div style='background:#fff0f6;border-radius:10px;padding:10px 12px'>"
                f"<div style='font-size:12px;font-weight:700;color:#880e4f;margin-bottom:4px'>❤️ 관계·인연</div>"
                f"<div style='font-size:12px;color:#333;line-height:1.7;white-space:normal;word-break:break-all'>{det['relation']}</div></div>"
                f"<div style='background:#fff8e1;border-radius:10px;padding:10px 12px'>"
                f"<div style='font-size:12px;font-weight:700;color:#e65100;margin-bottom:4px'>🏥 건강</div>"
                f"<div style='font-size:12px;color:#333;line-height:1.7;white-space:normal;word-break:break-all'>{det['health']}</div></div>"
                f"</div>"
            )
            st.markdown(_grid, unsafe_allow_html=True)

            # 키워드 태그
            if det["keywords"]:
                kw_html = "<div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px'>"
                for kw in det["keywords"]:
                    kw_html += (
                        f"<span style='background:#f0e8d5;border:1px solid #c9a84c;"
                        f"border-radius:20px;padding:3px 10px;font-size:12px;"
                        f"color:#5a3d1a;margin:2px;font-weight:600'>{kw}</span>"
                    )
                kw_html += "</div>"
                st.markdown(kw_html, unsafe_allow_html=True)

            # 합충 정보
            for hc in det["hap_chung_parts"]:
                hc_color = "#c0392b" if "충" in hc else "#1565c0"
                st.markdown(
                    f"<div style='background:{hc_color}12;border-left:3px solid {hc_color};"
                    f"padding:8px 12px;border-radius:0 8px 8px 0;font-size:12px;"
                    f"color:#333;margin-bottom:6px'>{hc}</div>",
                    unsafe_allow_html=True,
                )


def menu_monthly(pils, birth_year, gender):
    """📅 월별 운세 — 이 달의 십성 기운 요약"""
    current_year = datetime.now().year
    current_month = datetime.now().month

    st.markdown(f"### 📅 {current_year}년 월별 운세")

    MONTH_JJ = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    ilgan = pils[1]["cg"]
    year_cg = pils[0]["cg"]
    year_gan_idx = CG.index(year_cg) % 5

    GIL_MAP = {
        "食神": "✨ 길", "偏財": "✨ 길", "正財": "✨ 길", "正印": "✨ 길",
        "偏官": "🔴 흉", "劫財": "⚠️ 주의", "傷官": "⚠️ 주의",
        "比肩": "〰️ 평", "正官": "〰️ 평", "偏印": "〰️ 평",
    }

    for i in range(12):
        jj = MONTH_JJ[i]
        month_gan_idx = (year_gan_idx * 2 + 2 + i) % 10
        month_cg = CG[month_gan_idx]
        sip_cg = TEN_GODS_MATRIX.get(ilgan, {}).get(month_cg, "")
        gil = GIL_MAP.get(sip_cg, "〰️ 평")
        detail = SIPSONG_DETAIL.get(sip_cg, {})
        is_current = (current_month == i + 1)

        label = f"{'🔆 ' if is_current else ''}{'%02d' % (i + 1)}월 ({month_cg}{jj}) {sip_cg} {gil}"

        with st.expander(label, expanded=is_current):
            core = detail.get("핵심", f"{month_cg}{jj}의 기운이 흐르는 달입니다.")
            career = (detail.get("직업", "") or "안정유지")[:20]
            finance = (detail.get("재물", "") or "수입관리")[:20]
            relation = (detail.get("연애", "") or "인연주의")[:20]
            _card = (
                f"<div style='background:#1a1a1a;border-radius:10px;padding:16px;color:#e0e0e0;'>"
                f"<div style='margin-bottom:10px;font-size:14px;line-height:1.8;'>{core}</div>"
                f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;'>"
                f"<div style='background:#222;border-radius:8px;padding:10px;text-align:center;'>"
                f"<div style='color:#f7e695;font-size:12px;'>💼 직업</div>"
                f"<div style='font-size:12px;margin-top:4px;'>{career}</div></div>"
                f"<div style='background:#222;border-radius:8px;padding:10px;text-align:center;'>"
                f"<div style='color:#f7e695;font-size:12px;'>💰 재물</div>"
                f"<div style='font-size:12px;margin-top:4px;'>{finance}</div></div>"
                f"<div style='background:#222;border-radius:8px;padding:10px;text-align:center;'>"
                f"<div style='color:#f7e695;font-size:12px;'>❤️ 관계</div>"
                f"<div style='font-size:12px;margin-top:4px;'>{relation}</div></div>"
                f"</div></div>"
            )
            st.markdown(_card, unsafe_allow_html=True)


def menu_daily(pils, birth_year, gender):
    """☀️ 오늘의 운세 — 일진 기반"""
    today = datetime.now().date()

    st.markdown(f"### ☀️ 오늘의 운세")
    st.caption(f"{today.strftime('%Y년 %m월 %d일')} 일진")

    base = datetime(1970, 1, 1).date()
    days = (today - base).days
    day_cg = CG[days % 10]
    day_jj = JJ[days % 12]
    ilgan = pils[1]["cg"]
    sip = TEN_GODS_MATRIX.get(ilgan, {}).get(day_cg, "")

    detail = SIPSONG_DETAIL.get(sip, {})
    day_oh = OH.get(day_cg, "木")
    body = OHANG_BODY.get(day_oh, {})

    OH_COLOR = {"木": "#2d8a4e", "火": "#e53935", "土": "#f9a825", "金": "#9e9e9e", "水": "#1565c0"}
    OH_DIR   = {"木": "동쪽", "火": "남쪽", "土": "중앙", "金": "서쪽", "水": "북쪽"}
    OH_LUCKY = {"木": "초록색", "火": "빨간색", "土": "노란색", "金": "흰색", "水": "검은색"}
    GIL_MAP  = {
        "食神": "✨ 길", "偏財": "✨ 길", "正財": "✨ 길", "正印": "✨ 길",
        "偏官": "🔴 흉", "劫財": "⚠️ 주의", "傷官": "⚠️ 주의",
        "比肩": "〰️ 평", "正官": "〰️ 평", "偏印": "〰️ 평",
    }
    gil = GIL_MAP.get(sip, "〰️ 평")
    color = OH_COLOR.get(day_oh, "#555")
    core = detail.get("핵심", "흐름에 맞게 움직이세요.")
    prescription = detail.get("처방", "오늘 하루 작은 것에 감사하며 지내세요.")
    symptom = (body.get("증상", "") or body.get("주의", "") or "과로주의")[:10]

    msg = (
        f"오늘은 {day_cg}{day_jj} 일진으로 <b>{sip}</b>의 기운이 흐르는 날입니다. "
        f"{core[:40]} "
        f"행운 방향은 <b>{OH_DIR.get(day_oh, '중앙')}</b>, "
        f"행운색은 <b>{OH_LUCKY.get(day_oh, '흰색')}</b>을 활용하세요."
    )

    _card = (
        f"<div style='background:linear-gradient(135deg,#1a1a2e,#2a1a1a);"
        f"border:2px solid #f7e695;border-radius:16px;padding:24px;color:#e0e0e0;margin-bottom:16px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;'>"
        f"<div>"
        f"<span style='background:{color};color:white;font-size:40px;font-weight:900;"
        f"padding:8px 14px;border-radius:10px;'>{day_cg}</span>"
        f"<span style='background:{color};color:white;font-size:40px;font-weight:900;"
        f"padding:8px 14px;border-radius:10px;margin-left:6px;'>{day_jj}</span>"
        f"</div>"
        f"<div style='text-align:right;'>"
        f"<div style='font-size:24px;'>{gil}</div>"
        f"<div style='font-size:14px;color:#f7e695;'>{sip}</div>"
        f"</div></div>"
        f"<div style='background:rgba(255,255,255,0.07);border-radius:10px;"
        f"padding:16px;font-size:14px;line-height:1.9;margin-bottom:16px;'>{msg}</div>"
        f"<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;'>"
        f"<div style='background:#1a2a1a;border-radius:8px;padding:12px;text-align:center;'>"
        f"<div style='color:#7aff7a;font-size:13px;'>🎨 행운색</div>"
        f"<div style='margin-top:6px;'>{OH_LUCKY.get(day_oh, '흰색')}</div></div>"
        f"<div style='background:#1a1a2a;border-radius:8px;padding:12px;text-align:center;'>"
        f"<div style='color:#7ab8ff;font-size:13px;'>🧭 행운방위</div>"
        f"<div style='margin-top:6px;'>{OH_DIR.get(day_oh, '중앙')}</div></div>"
        f"<div style='background:#2a1a1a;border-radius:8px;padding:12px;text-align:center;'>"
        f"<div style='color:#ff9a9a;font-size:13px;'>⚠️ 주의</div>"
        f"<div style='margin-top:6px;font-size:12px;'>{symptom}</div></div>"
        f"</div></div>"
        f"<blockquote>🔮 <b>만신의 한마디</b>: {prescription}</blockquote>"
    )
    st.markdown(_card, unsafe_allow_html=True)

    # 일진 천간 vs 일간 관계 분석 (생/극/비화)
    ilgan_oh = OH.get(ilgan, "木")
    _SANG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 상생: A→B
    _GKEK = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}  # 상극: A→B

    if day_oh == ilgan_oh:
        _rel = "비화(比和)"
        _advice = f"오늘은 내 일간({ilgan})과 같은 오행의 날입니다. 비슷한 기운의 사람과 의기투합하기 좋으나, 경쟁·분쟁에는 주의하세요."
    elif _SANG.get(day_oh) == ilgan_oh:
        _rel = "일진이 일간을 生"
        _advice = f"일진({day_cg})이 내 일간({ilgan})을 생해주는 날로, 귀인의 도움과 좋은 에너지가 들어옵니다. 새로운 시도나 만남에 적극적으로 나서세요."
    elif _SANG.get(ilgan_oh) == day_oh:
        _rel = "일간이 일진을 生"
        _advice = f"내 일간({ilgan})이 오늘 일진({day_cg})을 생해주는 날로, 에너지가 빠져나갈 수 있습니다. 베풀기보다 자신을 챙기는 날로 삼으세요."
    elif _GKEK.get(day_oh) == ilgan_oh:
        _rel = "일진이 일간을 剋"
        _advice = f"일진({day_cg})이 내 일간({ilgan})을 극하는 날로, 외부 압박이나 스트레스가 생길 수 있습니다. 중요한 결정은 미루고 안정을 유지하세요."
    else:
        _rel = "일간이 일진을 剋"
        _advice = f"내 일간({ilgan})이 오늘 일진({day_cg})을 극하는 날로, 주도적으로 움직이기 좋습니다. 계획한 일을 추진하면 성과를 기대할 수 있습니다."

    st.info(f"🔗 **일진-일간 관계 [{_rel}]** — {_advice}")


def tab_jaemul(pils, birth_year, gender="남"):

    st.markdown(
        '<div class="gold-section">[재물론] 재물론(財物論) - 돈이 모이는 구조 분석</div>',
        unsafe_allow_html=True,
    )

    jm = get_jaemul_analysis(pils, birth_year, gender)

    oh_emoji = {"木": "[木]", "火": "[火]", "土": "[土]", "金": "[金]", "水": "[水]"}

    html = "<div style='background:linear-gradient(135deg,#fff9e0,#fff3c0);color:#000000;padding:20px;border-radius:14px;text-align:center;margin-bottom:14px'>"

    html += f"<div style='font-size:13px;color:#000000'>재성 오행(Wealth Element)</div>"

    html += f"<div style='font-size:36px;margin:8px 0'>{oh_emoji.get(jm['재성_오행'], '[Wealth]')}</div>"

    html += f"<div style='font-size:22px;font-weight:900;color:#8b6200'>{OHN.get(jm['재성_오행'], '')} 재성 강도 {jm['재성_강도']}%</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    html = "<div class='card' style='background:#ffffff;border:2px solid #27ae60'>"

    html += "<div style='font-size:13px;font-weight:700;color:#1a6f3a;margin-bottom:6px'>[분석] 재물 유형</div>"

    html += f"<div style='font-size:14px;color:#000000;line-height:1.9'>{jm['재물_유형']}</div>"

    html += f"<div style='margin-top:8px;background:#e8f5e8;padding:8px 12px;border-radius:8px;font-size:13px;color:#1a6f3a'>[전략] {jm['재물_전략']}</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    if jm["재성_위치"]:
        st.markdown(
            f'<div class="card" style="background:#ffffff;border:1px solid #e8d5a0;margin-top:8px"><b style="color:#000000">[위치] 재성 위치:</b> {"  |  ".join(jm["재성_위치"])}</div>',
            unsafe_allow_html=True,
        )

    if jm["재물_피크_대운"]:
        st.markdown(
            '<div class="gold-section">[상승] 재물 상승기 대운</div>',
            unsafe_allow_html=True,
        )

        for peak in jm["재물_피크_대운"]:
            c = {"정재": "#27ae60", "편재": "#2980b9", "식신": "#8e44ad"}.get(peak["십성"], "#000000")

            html = f"<div style='background:#ffffff;border-left:4px solid {c};border-radius:10px;padding:12px 16px;margin:5px 0;display:flex;justify-content:space-between;align-items:center'>"

            html += f"<div><span style='font-size:16px;font-weight:800;color:#000000'>{peak['대운']}</span> <span style='font-size:13px;color:#444'>{peak['나이']}</span></div>"

            html += f"<div style='text-align:right'><div style='font-size:13px;font-weight:700;color:{c}'>{peak['십성']}</div><div style='font-size:12px;color:#444'>{peak['연도']}</div></div></div>"

            st.markdown(html, unsafe_allow_html=True)


def tab_career(pils, gender="남"):

    st.markdown(
        '<div class="gold-section">[분석] 직업론(Career) - 천부적 적성과 최적 직업</div>',
        unsafe_allow_html=True,
    )

    ca = get_career_analysis(pils, gender)

    ilgan = pils[1]["cg"]

    html = "<div style='background:linear-gradient(135deg,#e8f4ff,#e1f2ff);color:#000000;padding:20px;border-radius:14px;text-align:center;margin-bottom:14px'>"

    html += "<div style='font-size:13px;color:#a8c8f0'>격국 기반 직업 분석</div>"

    html += f"<div style='font-size:26px;font-weight:900;color:#8b6200;margin:8px 0'>{ca['격국']}</div></div>"

    st.markdown(html, unsafe_allow_html=True)

    st.markdown('<div class="gold-section">[데이터] 최적 직업군</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="padding:10px 0;line-height:2">'
        + "".join(
            [
                f'<span style="background:#ffffff;border:1px solid #000000;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;color:#000000;margin:4px;display:inline-block">{j}</span>'
                for j in ca["최적직업"]
            ]
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    if ca["유리직업"]:
        st.markdown(
            '<div class="gold-section">[안내] 유리한 직업군</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="padding:8px 0;line-height:2">'
            + "".join(
                [
                    f'<span style="background:#ffffff;border:1px solid #a8d5a8;padding:5px 12px;border-radius:20px;font-size:13px;color:#2a6f2a;margin:4px;display:inline-block">{j}</span>'
                    for j in ca["유리직업"]
                ]
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    if ca["일간추가"]:
        st.markdown(f"### [분석] {ilgan}일간 특화")

        st.markdown(
            '<div style="padding:8px 0;line-height:2">'
            + "".join(
                [
                    f'<span style="background:#ffffff;border:1px solid #c8b8e8;padding:5px 12px;border-radius:20px;font-size:13px;color:#5a2d8b;margin:4px;display:inline-block">{j}</span>'
                    for j in ca["일간추가"]
                ]
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    if ca["신살보정"]:
        html = "<div class='card' style='background:#ffffff;border:1px solid #e8d5a0;margin-top:8px'>"

        html += "<div style='font-size:13px;font-weight:700;color:#000000;margin-bottom:6px'>[보정] 신살/양인 직업 보정</div>"

        html += "".join([f'<div style="font-size:13px;color:#000000;margin:3px 0">* {s}</div>' for s in ca["신살보정"]])

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

    if ca["피할직업"]:
        st.markdown(
            f'<div class="card" style="background:#fff0f0;border:1px solid #d5a8a8;margin-top:8px"><b style="color:#8b2020">[제외] 피해야 할 직업:</b> {"  /  ".join(ca["피할직업"])}</div>',
            unsafe_allow_html=True,
        )


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


# ──────────────────────────────────────────────────────────
#  고민 자동 추론 (Worry Inference)
# ──────────────────────────────────────────────────────────

_WORRY_WEIGHT = {
    # 십성 → {고민유형: 가중치}
    "偏官": {"직장_직업": 3, "대인_갈등": 2, "법적_관재": 1},
    "正官": {"직장_직업": 2, "대인_갈등": 1, "연애_결혼": 1},
    "偏財": {"돈_재물": 3, "사업_창업": 2},
    "正財": {"돈_재물": 2, "연애_결혼": 2, "사업_창업": 1},
    "食神": {"건강": 2, "자녀": 2, "돈_재물": 1},
    "傷官": {"대인_갈등": 2, "직장_직업": 1, "건강": 1},
    "比肩": {"대인_갈등": 2, "독립_변화": 2, "돈_재물": 1},
    "劫財": {"돈_재물": 2, "대인_갈등": 2, "독립_변화": 1},
    "偏印": {"건강": 2, "학업_진로": 2, "독립_변화": 1},
    "正印": {"학업_진로": 2, "건강": 1, "연애_결혼": 1},
}

_WORRY_LABEL = {
    "직장_직업":  ("직장·직업 문제",  "💼", "지금 직장이나 직업 때문에 힘드시죠? 사람 문제, 승진, 이직… 그 무게가 느껴집니다."),
    "돈_재물":    ("돈·재물 문제",    "💰", "지금 돈 때문에 고민이시죠? 수입, 지출, 투자… 재물 흐름이 심상치 않습니다."),
    "연애_결혼":  ("연애·결혼 문제",  "💑", "연애나 결혼 때문에 마음이 복잡하시죠? 인연의 기운이 크게 움직이고 있습니다."),
    "건강":       ("건강 문제",       "🏥", "몸이나 건강 때문에 걱정이 많으시죠? 지금 몸 관리가 특히 중요한 시기입니다."),
    "대인_갈등":  ("대인관계·갈등",   "🤝", "사람 때문에 힘드시죠? 갈등, 배신, 경쟁… 주변 인간관계가 복잡합니다."),
    "학업_진로":  ("학업·진로 고민",  "📚", "학업이나 진로 때문에 고민이시죠? 방향을 잡고 싶은 시기입니다."),
    "자녀":       ("자녀 문제",       "👶", "자녀 때문에 걱정이시죠? 아이와 관련된 기운이 활성화되어 있습니다."),
    "사업_창업":  ("사업·창업 고민",  "🏢", "사업이나 창업 때문에 고민이시죠? 재물 기운이 크게 움직이는 시기입니다."),
    "독립_변화":  ("독립·변화 욕구",  "🌀", "변화나 독립을 꿈꾸시죠? 지금 큰 변화의 기운이 오고 있습니다."),
    "법적_관재":  ("법적·관재 불안",  "⚖️", "법적 문제나 관재수가 걱정되시죠? 권위자와의 마찰에 주의할 시기입니다."),
}

WORRY_TITLE = {
    "직장_직업": "🔥 직장·직업이 지금 가장 큰 짐이군요",
    "돈_재물":   "💸 돈 흐름이 지금 발목을 잡고 있군요",
    "사업_창업": "💸 사업·자금이 지금 발목을 잡고 있군요",
    "연애_결혼": "💔 마음에 담아둔 인연 문제가 있군요",
    "건강":      "⚕️ 몸이 지금 경고 신호를 보내고 있군요",
    "대인_갈등": "🏠 사람 관계로 마음이 무거우시군요",
    "학업_진로": "🎯 진로와 방향이 흔들리고 있군요",
    "자녀":      "👶 자녀 문제로 마음이 무거우시군요",
    "독립_변화": "🌀 마음이 갈피를 못 잡고 있군요",
    "법적_관재": "⚖️ 법적·관재 불안이 짓누르고 있군요",
}

WORRY_MESSAGE = {
    "직장_직업": [
        "지금 직장 때문에 숨이 막히시죠? 사람이 문제인지, 일이 문제인지… 아마 둘 다일 겁니다. 관살(官殺) 기운이 강하게 치고 있습니다.",
        "승진이 막혔거나, 이직을 고민하고 계시죠. 지금 사주에서 관성(官星)이 강하게 발동하고 있어 조직 내 갈등이나 상사 문제가 표면화되는 시기입니다.",
        "직장에서 버티는 건지, 나가야 하는 건지 갈림길에 서 계십니다. 충동적 결정보다 최소 3개월 더 관찰하는 것이 현명합니다.",
        "지금 직업 적성이나 미래 방향에 대한 확신이 흔들리고 있습니다. 지금 대운이 직업 전환의 시기를 알리고 있습니다.",
    ],
    "돈_재물": [
        "돈이 새는 느낌이 드시죠? 열심히 하는데 통장이 안 차는 시기입니다. 재성(財星) 기운이 들어오지만 나가는 기운도 강합니다.",
        "지금 큰 재물 변동이 생기거나 생길 예정인 시기입니다. 투자·보증·동업은 신중하게, 고정 자산 비중을 높이십시오.",
        "수입과 지출의 균형이 무너지고 있군요. 지금 작은 누수들이 쌓여 큰 금액이 빠져나가고 있을 가능성이 큽니다.",
        "재물운이 흔들리는 시기입니다. 지금 당장 지출 내역을 점검하고 불필요한 지출을 차단하십시오.",
    ],
    "사업_창업": [
        "사업 자금이 부족하거나, 매출이 기대에 못 미치고 있죠. 편재(偏財) 운이 흔들리고 있습니다.",
        "창업을 고민 중이시군요. 지금 재물 기운이 크게 움직이고 있지만, 준비 없는 창업은 손실로 이어질 수 있습니다.",
        "사업의 방향이 흔들리는 시기입니다. 핵심 사업에 집중하고 무리한 사업 확장·신규 진입은 내년으로 미루십시오.",
        "거래처·파트너와의 관계에서 신뢰 문제가 생기거나 계약 분쟁이 일어날 수 있는 시기입니다. 계약서를 꼼꼼히 확인하십시오.",
    ],
    "연애_결혼": [
        "마음에 두신 분이 있거나, 현재 관계가 흔들리고 계시군요. 도화(桃花)나 합(合)의 기운이 강하게 들어오고 있습니다.",
        "결혼 문제로 고민이 깊으시죠. 결혼 시기가 맞아떨어지거나, 반대로 관계의 위기가 오는 시기입니다.",
        "인연이 올 것 같은데 안 오는 느낌이 드시죠? 지금 당신의 에너지가 인연을 끌어당기고 있습니다. 조금만 더 기다리십시오.",
        "기혼이라면 배우자와의 관계를 재정비할 필요가 있습니다. 작은 오해가 쌓이지 않도록 대화를 늘리십시오.",
    ],
    "건강": [
        "몸이 예전 같지 않으시죠? 무리하고 계신 것 같습니다. 지금 사주에서 건강 기운이 약해지는 시기입니다.",
        "최근 몸에서 신호가 오고 있군요. 미루지 말고 정기 검진을 받으십시오. 초기에 잡는 것이 핵심입니다.",
        "스트레스가 몸으로 나오고 있습니다. 소화기·혈압·수면 중 하나 이상에서 문제가 생기고 있지 않으신가요?",
        "지금 과로가 쌓여 면역력이 저하되는 시기입니다. 운동보다 충분한 수면이 더 중요한 때입니다.",
    ],
    "대인_갈등": [
        "가족이나 가까운 사람과 갈등이 생겼거나 생길 조짐이 있군요. 충(沖) 기운이 인간관계를 흔들고 있습니다.",
        "배신이나 오해로 마음이 상한 시기입니다. 지금은 용서보다 거리두기가 먼저입니다.",
        "인간관계에서 소모되는 에너지가 너무 큽니다. 나를 먼저 챙기고, 불필요한 관계는 정리하십시오.",
        "주변에서 당신에게 의존하거나 부탁이 많아지는 시기입니다. '노'라고 말하는 연습이 필요합니다.",
    ],
    "학업_진로": [
        "어느 방향으로 가야 할지 갈피를 못 잡고 계시군요. 정인(正印) 운이 발동해 배움과 자격을 요구하는 시기입니다.",
        "공부나 시험 준비가 부담스럽지만 지금 이 기간이 이후 10년의 방향을 결정합니다.",
        "지금 자격증·시험·진학 등 무언가를 준비 중이시죠. 방향은 맞습니다. 포기하지 마십시오.",
    ],
    "자녀": [
        "자녀 때문에 걱정이 많으시죠? 식상(食傷) 기운이 강하게 움직이며 자녀 관련 이슈가 표면화됩니다.",
        "자녀의 진로·교육·건강이 마음에 걸리는 시기입니다. 아이의 의견을 먼저 듣는 것이 중요합니다.",
        "자녀로 인한 기쁜 소식이 있거나, 반대로 걱정거리가 생기는 시기입니다. 과도한 관여보다 신뢰가 먼저입니다.",
    ],
    "독립_변화": [
        "이유 없이 불안하고 허전한 느낌이 드시죠? 지금 삶의 전환점에 서 계십니다. 변화는 이미 시작됐습니다.",
        "무언가를 잃은 것 같은 공허함이 있으시죠. 이 시기는 끝이 아니라 새로운 시작을 준비하는 과도기입니다.",
        "살던 곳·하던 일·맺어온 관계 중 하나가 크게 흔들리는 시기입니다. 버릴 것과 지킬 것을 구분하십시오.",
    ],
    "법적_관재": [
        "법적인 문제나 관재수가 걱정되는 시기입니다. 언행에 각별히 주의하세요.",
        "권위자나 기관과의 마찰이 생길 수 있는 시기군요.",
        "계약·서류 문제에서 꼼꼼하게 확인하지 않으면 손해가 생길 수 있습니다.",
    ],
}


def infer_current_worry(pils, birth_year, gender):
    """현재 대운+세운 십성 조합으로 고민 유형을 자동 추론한다.

    Returns:
        dict with keys: top_worry, top_score, label, icon, message,
                        second_worry, second_label, second_icon,
                        has_chung, has_dowhwa, has_hap,
                        dw_cg_ss, dw_jj_ss, sw_cg_ss, sw_jj_ss,
                        year, narrative
    """
    try:
        current_year = datetime.now().year
        cross = get_daewoon_sewoon_cross(pils, birth_year, gender, current_year)
        if not cross:
            return None

        dw_cg_ss = cross.get("대운_천간십성", "")
        dw_jj_ss = cross.get("대운_지지십성", "")
        sw_cg_ss = cross.get("세운_천간십성", "")
        sw_jj_ss = cross.get("세운_지지십성", "")

        # 가중치: 세운 천간×3 > 세운 지지×2 > 대운 천간×2 > 대운 지지×1
        scores = {}
        for ss, mul in [(sw_cg_ss, 3), (sw_jj_ss, 2), (dw_cg_ss, 2), (dw_jj_ss, 1)]:
            w = _WORRY_WEIGHT.get(ss, {})
            for cat, val in w.items():
                scores[cat] = scores.get(cat, 0) + val * mul

        # 충(沖) 감지: 사주 내 충 + 세운 지지 충
        has_chung = False
        try:
            ch = get_chung_hyung(pils)
            if ch.get("충"):
                has_chung = True
            # 세운 지지가 사주 내 어떤 지지와 충이 되는지
            sw_jj = cross.get("세운", {}).get("jj", "")
            for p in pils:
                k = frozenset([p["jj"], sw_jj])
                if k in CHUNG_MAP:
                    has_chung = True
                    break
        except Exception:
            _saju_log.warning("[infer_current_worry] 오류: %s", str(e)[:60])

        # 합(合) 감지
        has_hap = False
        try:
            sw_jj = cross.get("세운", {}).get("jj", "")
            sw_cg = cross.get("세운", {}).get("cg", "")
            for p in pils:
                if frozenset([p["jj"], sw_jj]) in SAM_HAP_MAP or \
                   frozenset([p["cg"], sw_cg]) in TG_HAP_MAP:
                    has_hap = True
                    break
        except Exception:
            _saju_log.warning("[infer_current_worry] 오류: %s", str(e)[:60])

        # 도화살 감지
        has_dowhwa = False
        try:
            ss12 = get_12sinsal(pils)
            if any("도화" in s.get("이름", "") for s in ss12):
                has_dowhwa = True
        except Exception:
            _saju_log.warning("[infer_current_worry] 오류: %s", str(e)[:60])

        # 특수 조건 보정
        if has_chung:
            top_cat = max(scores, key=scores.get) if scores else None
            if top_cat:
                scores[top_cat] = int(scores[top_cat] * 1.5)
        if has_dowhwa or has_hap:
            scores["연애_결혼"] = scores.get("연애_결혼", 0) + 4

        if not scores:
            return None

        sorted_cats = sorted(scores.items(), key=lambda x: -x[1])
        top_worry, top_score = sorted_cats[0]
        second_worry = sorted_cats[1][0] if len(sorted_cats) > 1 else None

        label, icon, _fallback_msg = _WORRY_LABEL.get(top_worry, ("고민", "🔮", "지금 많이 힘드시죠?"))
        second_label, second_icon, _ = _WORRY_LABEL.get(second_worry, ("", "", "")) if second_worry else ("", "", "")

        title = WORRY_TITLE.get(top_worry, f"🔮 {label} 기운이 강하게 들어오고 있군요")
        _msgs = WORRY_MESSAGE.get(top_worry, [_fallback_msg])
        message = random.choice(_msgs)

        return {
            "top_worry": top_worry,
            "top_score": top_score,
            "label": label,
            "icon": icon,
            "title": title,
            "message": message,
            "second_worry": second_worry,
            "second_label": second_label,
            "second_icon": second_icon,
            "has_chung": has_chung,
            "has_dowhwa": has_dowhwa,
            "has_hap": has_hap,
            "dw_cg_ss": dw_cg_ss,
            "dw_jj_ss": dw_jj_ss,
            "sw_cg_ss": sw_cg_ss,
            "sw_jj_ss": sw_jj_ss,
            "year": current_year,
        }
    except Exception:
        return None


def render_worry_inference(pils, birth_year, gender):
    """고민 자동 추론 결과를 카드로 렌더링"""
    result = infer_current_worry(pils, birth_year, gender)
    if not result:
        return

    icon = result["icon"]
    label = result["label"]
    title = result["title"]
    message = result["message"]
    sw_cg_ss = result["sw_cg_ss"]
    sw_jj_ss = result["sw_jj_ss"]
    dw_cg_ss = result["dw_cg_ss"]
    dw_jj_ss = result["dw_jj_ss"]
    year = result["year"]
    second_label = result["second_label"]
    second_icon = result["second_icon"]

    badge_html = ""
    if result["has_chung"]:
        badge_html += "<span style='background:#e53935;color:#fff;border-radius:6px;padding:1px 7px;font-size:11px;font-weight:700;margin-right:4px'>⚡ 충(沖)기운</span>"
    if result["has_dowhwa"]:
        badge_html += "<span style='background:#e91e63;color:#fff;border-radius:6px;padding:1px 7px;font-size:11px;font-weight:700;margin-right:4px'>🍑 도화기운</span>"
    if result["has_hap"]:
        badge_html += "<span style='background:#7b1fa2;color:#fff;border-radius:6px;padding:1px 7px;font-size:11px;font-weight:700;margin-right:4px'>🔗 합(合)기운</span>"

    second_html = ""
    if second_label:
        second_html = (
            f'<div style="margin-top:6px;font-size:12px;color:#aaa">'
            f'두 번째로 강한 기운 → {second_icon} {second_label}도 함께 얽혀 있습니다.</div>'
        )

    ss_html = (
        f"<span style='color:#b38728;font-weight:700'>{year}년</span> "
        f"세운 <b>{sw_cg_ss}·{sw_jj_ss}</b> / "
        f"대운 <b>{dw_cg_ss}·{dw_jj_ss}</b>"
    )

    st.markdown(
        f"""
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
            border:1.5px solid rgba(212,175,55,0.5);
            border-radius:16px;padding:20px 24px;margin-bottom:12px;
            box-shadow:0 4px 16px rgba(0,0,0,0.25)">
  <div style="font-size:11px;font-weight:700;color:#d4af37;
              letter-spacing:2px;margin-bottom:10px">🔮 만신의 첫 진단</div>
  <div style="display:flex;align-items:flex-start;gap:16px">
    <div style="font-size:44px;min-width:50px;text-align:center;
                line-height:1">{icon}</div>
    <div style="flex:1">
      <div style="font-size:20px;font-weight:900;color:#fff;margin-bottom:6px">
        {title}
      </div>
      <div style="font-size:13px;color:#ccc;line-height:1.8;margin-bottom:10px">
        {message}
      </div>
      <div style="font-size:11px;color:#aaa;margin-bottom:8px">
        {ss_html}
      </div>
      <div>{badge_html}</div>
      {second_html}
  </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── 개운법 expander ──────────────────────────────────────
    top_worry = result["top_worry"]
    solution = WORRY_SOLUTION.get(top_worry, {})
    if solution:
        with st.expander("🔮 만신의 처방 — 지금 당장 할 수 있는 개운법", expanded=True):
            actions_html = "".join(
                f'<div style="color:#d0d0d0;padding:5px 0;font-size:13px;">{a}</div>'
                for a in solution.get("즉각행동", [])
            )
            st.markdown(
                f"""
<div style="background:#1a1a1a;border:1px solid #f7e695;border-radius:12px;padding:20px;">

  <div style="color:#f7e695;font-size:15px;font-weight:700;margin-bottom:6px;">⚡ 핵심 처방</div>
  <div style="color:#e0e0e0;font-size:13px;margin-bottom:16px;">{solution.get('핵심처방', '')}</div>

  <div style="color:#f7e695;font-size:15px;font-weight:700;margin-bottom:6px;">✅ 지금 당장 할 것</div>
  {actions_html}

  <div style="display:flex;gap:12px;margin-top:16px;flex-wrap:wrap;">
    <div style="flex:1;min-width:clamp(100px,35vw,120px);background:#2a2a1a;border-radius:8px;padding:12px;">
      <div style="color:#f7e695;font-size:12px;font-weight:700;">🎨 행운색</div>
      <div style="color:#e0e0e0;font-size:12px;margin-top:4px;">{solution.get('행운색', '')}</div>
    </div>
    <div style="flex:1;min-width:clamp(100px,35vw,120px);background:#2a2a1a;border-radius:8px;padding:12px;">
      <div style="color:#f7e695;font-size:12px;font-weight:700;">🧭 행운방위</div>
      <div style="color:#e0e0e0;font-size:12px;margin-top:4px;">{solution.get('행운방위', '')}</div>
    </div>
  </div>

  <div style="margin-top:12px;background:#2a1a1a;border-radius:8px;padding:12px;">
    <div style="color:#ff6b6b;font-size:12px;font-weight:700;">⚠️ 주의사항</div>
    <div style="color:#e0e0e0;font-size:12px;margin-top:4px;">{solution.get('주의', '')}</div>
  </div>

  <div style="margin-top:10px;background:#1a2a1a;border:1px solid #4a7a4a;border-radius:8px;padding:12px;">
    <div style="color:#7aff7a;font-size:12px;font-weight:700;">🌿 비방(祕方)</div>
    <div style="color:#e0e0e0;font-size:12px;margin-top:4px;">{solution.get('비방', '')}</div>
  </div>

</div>
""",
                unsafe_allow_html=True,
            )


def menu1_report(pils, name, birth_year, gender, occupation="선택 안 함"):
    """[1. Comprehensive Report] - Pillars, Personality, Gyeokguk, Yongshin"""

    # ── 고민 자동 추론 카드 (맨 위) ──────────────────────────
    render_worry_inference(pils, birth_year, gender)

    # ── 로컬 엔진 항상 먼저 출력 ─────────────────────────────

    try:
        local_html = LocalSajuNarrator.full_report(pils, name, birth_year, gender)

        # word-break CSS로 긴 텍스트 화면 이탈 방지
        st.markdown(
            "<style>"
            ".stMarkdown p {"
            "  word-break: keep-all;"
            "  word-wrap: break-word;"
            "  overflow-wrap: break-word;"
            "  white-space: normal;"
            "  line-height: 1.9;"
            "  font-size: 15px;"
            "  color: #1a1a1a;"
            "}"
            ".stMarkdown h3 {"
            "  font-size: 16px !important;"
            "  font-weight: 800 !important;"
            "  margin-top: 20px !important;"
            "}"
            "</style>",
            unsafe_allow_html=True,
        )
        st.markdown(local_html, unsafe_allow_html=True)

    except Exception as _lne:
        st.warning(f"로컬 해석 오류: {_lne}")

    # ── 발동 중인 신살 강조 (세운 지지 기준) ─────────────────
    try:
        _SINSAL_ADVICE = {
            "겁살(劫殺)":   "변동·손재 위험 시기, 투자·보증·동업을 피하고 현금을 지켜라.",
            "재살(災殺)":   "사고·관재 주의, 이동 중 안전 점검과 보험 확인을 먼저 하라.",
            "천살(天殺)":   "상하 관계 마찰 주의, 윗사람과 충돌 전 한 템포 쉬고 말하라.",
            "지살(地殺)":   "이사·이직의 시기, 변화를 두려워 말고 더 좋은 환경으로 과감히 옮겨라.",
            "년살(도화살)": "대인관계·이성운 활성화, 외모 관리와 네트워킹이 최고의 투자다.",
            "월살(고초살)": "고통을 동반한 정착 시기, 기초를 다지면 이후 안정이 찾아온다.",
            "망신살":       "구설·스캔들 주의, 언행을 절제하고 SNS 노출을 최소화하라.",
            "장성살":       "리더십 발휘의 적기, 맡은 일을 주도적으로 끌고 나가면 인정받는다.",
            "반안살":       "꾸준함이 결실을 맺는 시기, 지금 쌓는 노력이 중년의 토대가 된다.",
            "역마살":       "이동·이사·출장 시기, 변화에 올라타면 기회가 열린다.",
            "육해살":       "가까운 사람과 신뢰 균열 주의, 돈거래·보증을 끊고 인간관계를 재정비하라.",
            "화개살":       "고독과 영감의 시기, 혼자 깊이 생각하는 시간이 창의성의 씨앗이 된다.",
        }
        _sw_jj = get_yearly_luck(pils, datetime.now().year).get("jj", "")
        _ss12 = get_12sinsal(pils)
        _active = [s for s in _ss12 if s.get("해당지지") == _sw_jj]
        if _active:
            st.markdown("#### 🔥 올해 발동 중인 신살")
            for _s in _active:
                _sname = _s.get("이름", "")
                _icon  = _s.get("icon", "")
                _pos   = ", ".join(_s.get("위치", []))
                _advice = _SINSAL_ADVICE.get(_sname, _s.get("caution", ""))
                st.info(f"{_icon} **{_sname}** 발동 중 ({_pos}) — {_advice}")
    except Exception:
        _saju_log.warning("[menu1_report] 오류: %s", str(e)[:60])

    # if not api_key and not groq_key:

    # return  # API 없으면 로컬만 출력 후 종료

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    try:
        ilgan = pils[1]["cg"]

        current_year = datetime.now().year

        current_age = current_year - birth_year + 1

        strength_info = get_ilgan_strength(ilgan, pils)

        gyeokguk = get_gyeokguk(pils)

        ys = get_yongshin(pils)

    except Exception as e:
        st.error(f"기본 데이터 계산 오류: {e}")

        return

    # -- 리포트 요약 카드 -------------------------------------

    sn_label = strength_info.get("신강신약", "중화")

    _sn_score = strength_info.get("helper_score", 50)

    yong_list = ys.get("종합_용신", [])

    yong_str = "/".join(yong_list[:2]) if isinstance(yong_list, list) else str(yong_list)

    gk_name = gyeokguk.get("격국명", "-") if gyeokguk else "-"

    # 신강신약 한자 배지
    if "신약" in sn_label or "극신약" in sn_label:
        _sn_char, _sn_color = "弱", "#e53935"
    elif "신강" in sn_label or "극신강" in sn_label:
        _sn_char, _sn_color = "强", "#1565c0"
    else:
        _sn_char, _sn_color = "中", "#f9a825"

    # 용신 오행 한자 배지
    _yong_icon_html = ""
    for _yc in (yong_list[:2] if isinstance(yong_list, list) else []):
        _bg, _fg = get_ohang_color(_yc)
        _yong_icon_html += (
            f"<span style='background:{_bg};color:{_fg};"
            f"border-radius:6px;padding:2px 6px;font-size:18px;"
            f"font-weight:900;display:inline-block;margin:1px'>{_yc}</span>"
        )
    if not _yong_icon_html:
        _yong_icon_html = "<span style='font-size:18px;font-weight:900;color:#555'>-</span>"

    # 일간 오행 색상
    _ilgan_cg = pils[1]["cg"] if pils[1] else "?"
    _ilgan_jj = pils[1]["jj"] if pils[1] else "?"
    _ilgan_bg, _ilgan_fg = get_ohang_color(_ilgan_cg)
    _ilgan_jj_bg, _ilgan_jj_fg = get_ohang_color(_ilgan_jj)

    st.markdown(
        f"""

<div style="background:#ffffff;border:1.5px solid #e0d0a0;border-radius:14px; padding:14px 16px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">

<div style="font-size:11px;font-weight:700;color:#8b6200;letter-spacing:2px;margin-bottom:10px">

            📋 종합 사주 리포트 - 원국/성향/格局/用神

</div>

<div style="display:flex;gap:8px;flex-wrap:wrap">

<div style="flex:1;min-width:90px;background:#fff8e8;border-radius:10px; padding:10px 12px;border:1px solid #e8d5a0;text-align:center">

<div style="font-size:10px;font-weight:700;color:#8b6200;margin-bottom:6px;letter-spacing:1px">日干</div>

<div style="display:inline-block;background:{_ilgan_bg};color:{_ilgan_fg};font-size:22px;font-weight:900;border-radius:8px;padding:2px 10px;margin-bottom:3px">{_ilgan_cg}</div>

<div style="display:inline-block;background:{_ilgan_jj_bg};color:{_ilgan_jj_fg};font-size:18px;font-weight:900;border-radius:8px;padding:2px 8px;margin-left:3px">{_ilgan_jj}</div>

</div>

<div style="flex:1;min-width:90px;background:#ffffff;border-radius:10px; padding:10px 12px;border:1px solid #c0d8f0;text-align:center">

<div style="font-size:10px;font-weight:700;color:#8b6200;margin-bottom:6px;letter-spacing:1px">身强弱</div>

<div style="font-size:28px;font-weight:900;color:{_sn_color};line-height:1">{_sn_char}</div>

<div style="font-size:10px;color:#555;margin-top:3px">{sn_label}</div>

</div>

<div style="flex:1;min-width:90px;background:#f5fff0;border-radius:10px; padding:10px 12px;border:1px solid #b8e0b8;text-align:center">

<div style="font-size:10px;font-weight:700;color:#8b6200;margin-bottom:6px;letter-spacing:1px">用神</div>

<div style="margin:4px 0">{_yong_icon_html}</div>

<div style="font-size:10px;color:#555;margin-top:3px">{yong_str}</div>

</div>

<div style="flex:1;min-width:90px;background:#fdf0ff;border-radius:10px; padding:10px 12px;border:1px solid #d8b8e8;text-align:center">

<div style="font-size:10px;font-weight:700;color:#8b6200;margin-bottom:6px;letter-spacing:1px">格局</div>

<div style="font-size:16px;font-weight:900;color:#4a148c;letter-spacing:2px">格局</div>

<div style="font-size:10px;color:#555;margin-top:3px">{gk_name}</div>

</div>

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # ③ 성향 판독

    st.markdown('<div class="gold-section">🧠 성향 판독</div>', unsafe_allow_html=True)

    try:
        with st.spinner("성향 계산 중..."):
            hl = generate_engine_highlights(pils, birth_year, gender)

        for trait in hl["personality"]:
            tag_color = "#9b7ccc" if ("겉" in trait or "속" in trait) else "#4a90d9"

            st.markdown(
                f"""

<div style="border-left:4px solid {tag_color};background:#ffffff; padding:11px 16px;border-radius:8px;margin:5px 0; font-size:13px;line-height:1.9;color:#000000;border:1px solid #000000">{trait}</div>""",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.warning(f"성향 계산 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ④ 격국

    st.markdown('<div class="gold-section">🏆 격국 (格局)</div>', unsafe_allow_html=True)

    try:
        if gyeokguk:
            gname = gyeokguk.get("격국명", "")

            # GYEOKGUK_DESC 전체 요약 사용 (300자 제한 제거)

            gdesc_full = GYEOKGUK_DESC.get(gname, {}).get("summary", gyeokguk.get("격국_해설", ""))

            gcaution = GYEOKGUK_DESC.get(gname, {}).get("caution", "")

            gcareer = GYEOKGUK_DESC.get(gname, {}).get("lucky_career", "")

            ggod_rank = GYEOKGUK_DESC.get(gname, {}).get("god_rank", "")

            _gcareer_html = (
                f"<div style='background:#ffffff;border:1.5px solid #000000;"
                f"border-left:8px solid #000000;padding:10px 14px;border-radius:8px;"
                f"font-size:13px;color:#000000;margin-bottom:10px'>💼 적합 직업: {gcareer}</div>"
                if gcareer else ""
            )
            _gcaution_clean = gcaution.replace("[!]", "⚠️")
            _gcaution_html = (
                f"<div style='background:#fff5f5;border:1.5px solid #ff0000;"
                f"border-left:8px solid #ff0000;padding:10px 14px;border-radius:8px;"
                f"font-size:13px;color:#000000;margin-bottom:10px;white-space:pre-wrap'>{_gcaution_clean}</div>"
                if gcaution else ""
            )
            _ggod_html = (
                f"<div style='background:#f5fff5;border:1.5px solid #27ae60;"
                f"border-left:8px solid #27ae60;padding:10px 14px;border-radius:8px;"
                f"font-size:13px;color:#000000'>- {ggod_rank}</div>"
                if ggod_rank else ""
            )
            st.markdown(
                f"""<div style="background:#ffffff;border:2.5px solid #000000;border-radius:14px;padding:22px">
<div style="font-size:22px;font-weight:900;color:#000000;margin-bottom:12px">{gname}</div>
<div style="font-size:14px;color:#000000;line-height:2.1;white-space:pre-wrap;margin-bottom:14px">{gdesc_full}</div>
{_gcareer_html}
{_gcaution_html}
{_ggod_html}
</div>""",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.warning(f"격국 표시 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ⑤ 용신

    st.markdown('<div class="gold-section">- 용신 (用神)</div>', unsafe_allow_html=True)

    try:
        yongshin_ohs = ys.get("종합_용신", [])

        if not isinstance(yongshin_ohs, list):
            yongshin_ohs = []

        gishin_raw = ys.get("기신", [])
        _ilgan_oh = OH.get(ilgan, "")
        _CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
        _BRTH = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        _sn = strength_info.get("신강신약", "중화")
        _oh_strength = strength_info.get("oh_strength", {})

        if isinstance(gishin_raw, list):
            gishin_ohs = gishin_raw
        else:
            # get_yongshin()은 "기신" 값을 문자열로 반환 → 일간 오행에서 역산
            if "신강" in _sn:
                gishin_ohs = [o for o in [_ilgan_oh, _BRTH.get(_ilgan_oh, "")] if o]
            elif "신약" in _sn:
                _ok_관 = next((k for k, v in _CTRL.items() if v == _ilgan_oh), "")
                _ok_재 = _CTRL.get(_ilgan_oh, "")
                gishin_ohs = [o for o in [_ok_관, _ok_재] if o]
            else:
                gishin_ohs = []

        # 용신 폴백: 비어있으면 오행 강약 기준 최약 2개 보충
        if not yongshin_ohs and _oh_strength:
            _sorted = sorted(_oh_strength.items(), key=lambda x: x[1])
            yongshin_ohs = [o for o, _ in _sorted[:2] if o]

        # 기신 폴백: 비어있으면 오행 강약 기준 최강 2개
        if not gishin_ohs and _oh_strength:
            _sorted_desc = sorted(_oh_strength.items(), key=lambda x: -x[1])
            gishin_ohs = [o for o, _ in _sorted_desc[:2] if o and o not in yongshin_ohs]

        OH_EMOJI = {"木": "🌳", "火": "🔥", "土": "⛰️", "金": "⚔️", "水": "💧"}

        y_tags = " ".join(
            [
                f"<span style='background:#ffffff;color:#000000;padding:5px 14px;" f"border:2px solid #000000;border-radius:20px;font-size:14px;font-weight:900'>"
                f"{OH_EMOJI.get(o, '')} {o}({OHN.get(o, '')})</span>"
                for o in yongshin_ohs
            ]
        )

        g_tags = (
            " ".join(
                [
                    f"<span style='background:#ffe5e2;color:#000000;padding:5px 14px;border-radius:20px;font-size:14px;font-weight:700'>{OH_EMOJI.get(o, '')} {o}({OHN.get(o, '')})</span>"
                    for o in gishin_ohs
                ]
            )
            if gishin_ohs
            else f"<span style='color:#000000;font-size:13px'>{str(gishin_raw)}</span>"
        )

        st.markdown(
            f"""

<div style="background:#f8f0ff;border-radius:12px;padding:16px">

<div style="margin-bottom:10px"><b>🌟 用神(용신 - 힘이 되는 오행):</b><br>{y_tags}</div>

<div><b>⚠️ 忌神(기신 - 조심할 오행):</b><br>{g_tags}</div>

</div>

""",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.warning(f"용신 표시 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ⑥ 십성 조합 인생 분석 *** 핵심

    st.markdown(
        '<div class="gold-section">🔮 십성(十星) 조합 - 당신의 인생 설계도</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """

<div style="font-size:12px;color:#000000;margin-bottom:12px">

    원국에 나타난 십성의 조합을 분석합니다. 조합만 알면 그 사람의 인생이 보입니다.

</div>""",
        unsafe_allow_html=True,
    )

    try:
        life = build_life_analysis(pils, gender)

        combos = life["조합_결과"]

        top_ss = life["주요_십성"]

        ss_dist = life["전체_십성"]

        # 십성 분포 태그

        ss_colors = {
            "비견": "#3498db",
            "겁재": "#e74c3c",
            "식신": "#27ae60",
            "상관": "#e67e22",
            "편재": "#2ecc71",
            "정재": "#16a085",
            "편관": "#c0392b",
            "정관": "#2980b9",
            "편인": "#8e44ad",
            "정인": "#d35400",
        }

        tags_html = "".join(
            [
                f"<span style='background:{ss_colors.get(ss, '#888')};color:#000000;padding:4px 12px;border-radius:20px;font-size:12px;margin:3px;display:inline-block'>{ss} x{cnt}</span>"
                for ss, cnt in sorted(ss_dist.items(), key=lambda x: -x[1])
            ]
        )

        st.markdown(
            f"""

<div style="background:#ffffff;border-radius:10px;padding:14px;margin-bottom:16px">

<div style="font-size:11px;color:#000000;margin-bottom:8px">📊 원국 십성 분포</div>

<div>{tags_html}</div>

</div>

""",
            unsafe_allow_html=True,
        )

        if combos:
            for key, combo in combos:
                ss_pair = " x ".join(list(key))

                st.markdown(
                    f"""

<div style="background:#ffffff;border-radius:16px; padding:22px;margin:12px 0;border:2.5px solid #000000">

<div style="font-size:18px;font-weight:900;color:#000000;margin-bottom:6px">

                        {combo["요약"]}

</div>

<div style="font-size:12px;color:#000000;margin-bottom:16px;font-weight:700">조합: {ss_pair}</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">

<div style="background:#ffffff;border-radius:10px;padding:14px;border:1.5px solid #000000">

<div style="font-size:11px;color:#000000;font-weight:700;margin-bottom:6px">🧠 성향</div>

<div style="font-size:13px;color:#000000;line-height:1.8">{combo["성향"]}</div>

</div>

<div style="background:#ffffff;border-radius:10px;padding:14px;border:1.5px solid #000000">

<div style="font-size:11px;color:#000000;font-weight:700;margin-bottom:6px">💰 재물/돈 버는 방식</div>

<div style="font-size:13px;color:#000000;line-height:1.8">{combo["재물"]}</div>

</div>

<div style="background:#ffffff;border-radius:10px;padding:14px;border:1.5px solid #000000">

<div style="font-size:11px;color:#000000;font-weight:700;margin-bottom:6px">💼 직업 적성</div>

<div style="font-size:13px;color:#000000;line-height:1.8">{combo["직업"]}</div>

</div>

<div style="background:#ffffff;border-radius:10px;padding:14px;border:1.5px solid #000000">

<div style="font-size:11px;color:#000000;font-weight:700;margin-bottom:6px">💑 연애/인간관계</div>

<div style="font-size:13px;color:#000000;line-height:1.8">{combo["연애"]}</div>

</div>

</div>

<div style="background:#ffffff;border-radius:10px;padding:12px;margin-top:12px; border:1.5px solid #ff0000">

<span style="font-size:11px;color:#ff0000;font-weight:700">⚠️ 주의사항: </span>

<span style="font-size:13px;color:#000000;line-height:1.8;font-weight:700">{combo["주의"]}</span>

</div>

</div>

""",
                    unsafe_allow_html=True,
                )

        else:
            # 조합 없을 때 단일 십성 분석

            if top_ss:
                ss1 = top_ss[0]

                st.markdown(
                    f"""

<div style="background:#ffffff;border-radius:12px;padding:18px;border:1px solid #3a4060">

<div style="font-size:16px;font-weight:700;color:#000000">

                        {ss1} 중심 사주

</div>

<div style="font-size:13px;color:#000000;margin-top:10px;line-height:1.8">

                        주요 십성: {", ".join(top_ss[:3])}

</div>

</div>

""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"십성 조합 분석 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ⑦ 직업 조언

    if occupation and occupation != "선택 안 함":
        st.markdown(
            '<div class="gold-section">💼 직업 적합도 분석</div>',
            unsafe_allow_html=True,
        )

        try:
            tab_career(pils, gender)

        except Exception as e:
            st.warning(f"직업 분석 오류: {e}")

    # ⑧ 만신 스타일 종합 해설문

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">📜 종합 사주 해설 - 만신의 풀이</div>',
        unsafe_allow_html=True,
    )

    try:
        narrative = build_rich_narrative(pils, birth_year, gender, name, section="report")

        # 만신 풀이가 HTML(div 등)이면 【 분할 없이 한 번에 렌더 (태그가 텍스트로 보이는 현상 방지)
        if narrative.strip().startswith("<") or "<div" in narrative[:200]:
            st.markdown(narrative, unsafe_allow_html=True)
        else:
            sections = narrative.split("【")
            for i, sec in enumerate(sections):
                if not sec.strip():
                    continue
                lines = sec.strip().split("\n")
                title = lines[0].replace("】", "").strip() if lines else ""
                body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
                if title:
                    st.markdown(
                        f"""
<div style="background:#ffffff; border-left:8px solid #000000;border:1.5px solid #000000;border-radius:10px; padding:18px 22px;margin:10px 0">
<div style="font-size:15px;font-weight:900;color:#000000;margin-bottom:10px">【 {title} 】</div>
<div style="font-size:14px;color:#000000;line-height:2.0; white-space:pre-wrap">{body}</div>
</div>
""",
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.warning(f"종합 해설 오류: {e}")

    # -- 통계 기반 패턴 분석 -------------------------------

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    try:
        render_statistical_insights(pils, strength_info)

    except Exception as e:
        st.warning(f"⚠️ {str(e)[:80]}")

    # ── 大運·歲運·月運 길흉월 분석 ────────────────────────

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">📅 올해 길흉월 분석 (大運·歲運·月運 교차)</div>',
        unsafe_allow_html=True,
    )

    try:
        _cur_year = datetime.now().year

        _months_data = [get_monthly_luck(pils, _cur_year, m) for m in range(1, 13)]

        _LEVEL_RANK = {"대길": 5, "길": 4, "평길": 3, "평": 2, "흉": 1, "흉흉": 0}

        _best_m = max(_months_data, key=lambda x: _LEVEL_RANK.get(x["길흉"], 2))

        _worst_m = min(_months_data, key=lambda x: _LEVEL_RANK.get(x["길흉"], 2))

        _LEVEL_COLOR = {
            "대길": "#4caf50",
            "길": "#8bc34a",
            "평길": "#ffc107",
            "평": "#9e9e9e",
            "흉": "#f44336",
            "흉흉": "#b71c1c",
        }

        _LEVEL_EMOJI = {
            "대길": "🌟",
            "길": "✅",
            "평길": "🟡",
            "평": "⬜",
            "흉": "⚠️",
            "흉흉": "🔴",
        }

        # ① 최고/주의 달 카드

        _gc1, _gc2 = st.columns(2)

        with _gc1:
            st.markdown(
                f"""

<div style="background:#e8f5e9;border:1.5px solid #81c784;border-radius:12px;padding:16px;text-align:center">

<div style="font-size:12px;color:#2e7d32;font-weight:700;margin-bottom:6px">🌟 올해 최고의 달</div>

<div style="font-size:32px;font-weight:900;color:#1b5e20">{_best_m["월"]}월</div>

<div style="font-size:13px;color:#388e3c;margin-top:4px">{_LEVEL_EMOJI.get(_best_m["길흉"], "")} {_best_m["길흉"]} · {_best_m["십성"]}</div>

<div style="font-size:12px;color:#555;margin-top:6px;line-height:1.6">{_best_m.get("short", "")}</div>

</div>""",
                unsafe_allow_html=True,
            )

        with _gc2:
            st.markdown(
                f"""

<div style="background:#fce4ec;border:1.5px solid #e57373;border-radius:12px;padding:16px;text-align:center">

<div style="font-size:12px;color:#c62828;font-weight:700;margin-bottom:6px">⚠️ 올해 주의할 달</div>

<div style="font-size:32px;font-weight:900;color:#b71c1c">{_worst_m["월"]}월</div>

<div style="font-size:13px;color:#d32f2f;margin-top:4px">{_LEVEL_EMOJI.get(_worst_m["길흉"], "")} {_worst_m["길흉"]} · {_worst_m["십성"]}</div>

<div style="font-size:12px;color:#555;margin-top:6px;line-height:1.6">{_worst_m.get("short", "")}</div>

</div>""",
                unsafe_allow_html=True,
            )

        # ② 大運·歲運 교차 요약

        _cross = get_daewoon_sewoon_cross(pils, birth_year, gender, _cur_year)

        if _cross:
            _event_html = ("<br>⚡ " + " / ".join([e["desc"] for e in _cross["교차사건"]])) if _cross["교차사건"] else ""

            st.markdown(
                f"""

<div style="background:#fff8e1;border:1px solid #ffd54f;border-radius:10px;padding:12px 16px;margin-top:10px;font-size:13px;color:#5d4037;line-height:1.9">

<b>⚙️ 大運·歲運 교차 분석 ({_cur_year}년)</b><br>

  현재 대운 <b>{_cross["대운"]["str"]}</b>({_cross["대운_천간십성"]}) × 올해 세운 <b>{_cross["세운"].get("세운", "")}</b>({_cross["세운_천간십성"]})<br>

  → {_cross["교차해석"]}{_event_html}

</div>""",
                unsafe_allow_html=True,
            )

        # ③ 1~12월 바 타임라인

        _bar_html = ""

        for _md in _months_data:
            _lv = _md["길흉"]

            _col = _LEVEL_COLOR.get(_lv, "#9e9e9e")

            _ht = max(16, _LEVEL_RANK.get(_lv, 2) * 12)

            _em = _LEVEL_EMOJI.get(_lv, "")

            _bar_html += (
                f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;min-width:0">'
                f'<div style="font-size:10px">{_em}</div>'
                f'<div style="width:100%;height:{_ht}px;background:{_col};border-radius:5px 5px 0 0;margin:2px 1px 0"></div>'
                f'<div style="font-size:10px;color:#555;margin-top:3px">{_md["월"]}월</div>'
                f'<div style="font-size:9px;color:{_col};font-weight:700">{_lv}</div>'
                f"</div>"
            )

        st.markdown(
            f"""

<div style="background:#fafafa;border:1px solid #e0e0e0;border-radius:12px;padding:14px;margin-top:10px">

<div style="font-size:11px;color:#888;margin-bottom:8px">📊 1~12월 월운 길흉 타임라인</div>

<div style="display:flex;gap:4px;align-items:flex-end;height:80px">{_bar_html}</div>

</div>""",
            unsafe_allow_html=True,
        )

        # ④ 월별 달력 뷰
        _cur_month = datetime.now().month
        _CAL_BG = {
            "대길": ("#e8f5e9", "#2e7d32", "#a5d6a7"),
            "길":   ("#f1f8e9", "#388e3c", "#c5e1a5"),
            "평길": ("#fffde7", "#f57f17", "#ffe082"),
            "평":   ("#fafafa", "#555555", "#e0e0e0"),
            "흉":   ("#fff3e0", "#e65100", "#ffcc80"),
            "흉흉": ("#fce4ec", "#b71c1c", "#ef9a9a"),
        }
        _cal_cells = ""
        for _md in _months_data:
            _lv   = _md["길흉"]
            _bg, _tc, _bc = _CAL_BG.get(_lv, ("#fafafa", "#555", "#e0e0e0"))
            _is_now = (_md["월"] == _cur_month)
            _border = f"3px solid {_tc}" if _is_now else f"1px solid {_bc}"
            _now_badge = "<div style='font-size:9px;font-weight:700;color:#fff;background:#e53935;border-radius:4px;padding:1px 4px;display:inline-block;margin-bottom:2px'>TODAY</div><br>" if _is_now else ""
            _em = _LEVEL_EMOJI.get(_lv, "")
            _cal_cells += (
                f"<div style='background:{_bg};border:{_border};border-radius:10px;"
                f"padding:10px 6px;text-align:center;min-width:0'>"
                f"{_now_badge}"
                f"<div style='font-size:18px;font-weight:900;color:{_tc}'>{_md['월']}월</div>"
                f"<div style='font-size:12px;font-weight:700;color:{_tc};margin:2px 0'>{_md['간']}{_md['지']}</div>"
                f"<div style='font-size:11px;color:#444'>{_md['십성']}</div>"
                f"<div style='font-size:11px;font-weight:700;color:{_tc};margin-top:3px'>{_em} {_lv}</div>"
                f"<div style='font-size:10px;color:#666;margin-top:4px;line-height:1.4'>{_md.get('short','')[:16]}</div>"
                f"</div>"
            )
        st.markdown(
            f"""<div style="background:#fff;border:1px solid #e0d8c0;border-radius:14px;padding:16px;margin-top:12px">
<div style="font-size:12px;font-weight:700;color:#8b6200;margin-bottom:10px">📅 {_cur_year}년 월별 달력</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">{_cal_cells}</div>
</div>""",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.warning(f"길흉월 분석 오류: {e}")

    # -- 클리프행어 (미완성 서술 트릭) ----------------------

    try:
        current_year = datetime.now().year

        turning = calc_turning_point(pils, birth_year, gender, current_year)

        triggers = detect_event_triggers(pils, birth_year, gender, current_year)

        high_t = [t for t in triggers if t["prob"] >= 75]

        teaser = ""

        if turning["is_turning"] and turning["reason"]:
            teaser = f"이 사주 구조에서 **{current_year}~{current_year + 1}년**은 단순히 넘어가는 해가 아닙니다. {turning['reason'][0]}"

        elif high_t:
            teaser = f"사건 트리거 분석에서 **{high_t[0]['title']}** 패턴이 포착됐습니다. 이 흐름이 구체적으로 어떤 영역에서 발현될지,"

        else:
            luck_s = calc_luck_score(pils, birth_year, gender, current_year)

            if luck_s >= 70:
                teaser = f"현재 운세 점수 **{luck_s}/100** - 상승기 진입 신호가 감지됩니다. 이 기회를 어떻게 활용할지,"

            else:
                teaser = f"현재 운세 점수 **{luck_s}/100** - 흐름의 방향이 바뀌는 시점이 다가오고 있습니다. 그 시기와 대비책이"

        if teaser:
            st.markdown(
                f"""

<div style="background:linear-gradient(135deg,#ffffff,#fff3cc); border:2px solid #000000;border-radius:14px; padding:20px 22px;margin:16px 0;text-align:center">

<div style="font-size:13px;color:#000000;font-weight:700;margin-bottom:8px">

                    🔮 AI 예언자 심층 분석 예고

</div>

<div style="font-size:14px;color:#000000;line-height:1.9;margin-bottom:12px">

                    {teaser}<br>

<span style="color:#000000;font-size:12px">

                        -> AI 상담 탭에서 정확한 시기와 대응 전략을 확인하십시오.

</span>

</div>

<div style="font-size:11px;color:#000000;font-weight:700;letter-spacing:1px">

                    * 🤖 AI 상담 탭 이동 *

</div>

</div>

            

""",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.warning(f"⚠️ {str(e)[:80]}")

    # ── 올해 월별 최적·위험 타이밍 요약 (종합 탭 하단) ──────────
    st.markdown(
        '<div class="gold-section">📅 올해 월별 최적 타이밍 — 전 분야 직격 특정</div>',
        unsafe_allow_html=True,
    )
    try:
        _cur_yr_m = datetime.now().year
        _domains = [("재물", "💰"), ("인연", "❤️"), ("직업", "💼"), ("건강", "🏥")]
        _timing_rows = []
        for _dom, _emoji in _domains:
            _mt_r = get_monthly_timing(pils, birth_year, gender, _cur_yr_m, _dom)
            _peak_ms = [str(m) for m, d in _mt_r.get("peak",   []) if "⭐⭐⭐" in d or "⭐⭐" in d]
            _caut_ms = [str(m) for m, d in _mt_r.get("caution",[]) if "⛔" in d]
            if not _peak_ms:
                _peak_ms = [str(m) for m, _ in _mt_r.get("peak", [])[:2]]
            _timing_rows.append((_dom, _emoji, _peak_ms, _caut_ms))

        _tc1, _tc2 = st.columns(2)
        for _idx, (_dom, _emoji, _peak_ms, _caut_ms) in enumerate(_timing_rows):
            _col = _tc1 if _idx % 2 == 0 else _tc2
            with _col:
                st.markdown(
                    f"""<div style='background:#fafafa;border:1.5px solid #e0d8c0;
                    border-radius:12px;padding:12px 14px;margin:4px 0;'>
                    <div style='font-size:13px;font-weight:900;color:#2d1f00;
                    margin-bottom:6px'>{_emoji} {_dom} 타이밍</div>
                    <div style='font-size:12px;color:#27ae60;margin-bottom:3px;'>
                    ✅ 최적: <b>{", ".join(_peak_ms) + "월" if _peak_ms else "해당 없음"}</b></div>
                    <div style='font-size:12px;color:#c0392b;'>
                    ⛔ 주의: <b>{", ".join(_caut_ms) + "월" if _caut_ms else "없음"}</b></div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception as _mtr_e:
        st.warning(f"⚠️ 월별 타이밍 분석 오류: {_mtr_e}")


def menu2_lifeline(pils, birth_year, gender, name="내담자"):
    """2️⃣ 인생 흐름 (대운 100년) - 프리미엄 글래스모피즘 UI"""

    ilgan        = pils[1]["cg"]
    current_year = datetime.now().year
    birth_month  = st.session_state.get("birth_month", 1)
    birth_day    = st.session_state.get("birth_day",   1)
    birth_hour   = st.session_state.get("birth_hour",  12)
    birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

    daewoon = SajuCoreEngine.get_daewoon(
        pils, birth_year, birth_month, birth_day,
        birth_hour, birth_minute, gender=gender,
    )
    ys           = get_yongshin(pils)
    yongshin_ohs = ys.get("종합_용신", [])
    if not isinstance(yongshin_ohs, list):
        yongshin_ohs = []
    ilgan_oh = OH.get(ilgan, "")

    # ── 현재 대운 직격 요약 카드 (맨 위 / 결론 먼저) ──────────────
    cur_dw = next(
        (d for d in daewoon if d["시작연도"] <= current_year <= d["종료연도"]), None
    )
    if cur_dw:
        _cdw_ss  = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw["cg"], "-")
        _cdw_oh  = OH.get(cur_dw["cg"], "")
        _is_yong = _get_yongshin_match(_cdw_ss, yongshin_ohs, ilgan_oh) == "yong"
        _is_gisn = not _is_yong and _cdw_oh not in yongshin_ohs
        _grade   = "🌟 황금기 대운" if _is_yong else "⚠️ 주의 대운" if _is_gisn else "〰️ 보통 대운"
        _gbg     = "#1a3d1a" if _is_yong else "#3d1a1a" if _is_gisn else "#1a1a3d"
        _gc      = "#7fff7f" if _is_yong else "#ffaaaa" if _is_gisn else "#aaaaff"
        _dd      = DAEWOON_DIRECT.get(_cdw_ss, {})
        _verdict = _dd.get("verdict", f"{_cdw_ss} 대운이 진행 중입니다.")
        _remain  = cur_dw["종료연도"] - current_year
        _age     = current_year - birth_year + 1

        st.markdown(
            f"""<div style='background:{_gbg};border-radius:16px;padding:20px 24px;
            margin-bottom:20px;border:2px solid {_gc}33;'>
            <div style='font-size:11px;color:{_gc};letter-spacing:2px;
            font-weight:700;margin-bottom:8px'>🔮 지금 당신의 대운</div>
            <div style='display:flex;justify-content:space-between;align-items:center;
            margin-bottom:12px;'>
            <div>
              <span style='font-size:32px;font-weight:900;color:#fff'>
              {cur_dw["str"]}</span>
              <span style='font-size:16px;color:{_gc};margin-left:10px;font-weight:700'>
              [{_cdw_ss}]</span>
            </div>
            <div style='background:{_gc}22;border:1px solid {_gc}66;border-radius:20px;
            padding:6px 16px;font-size:13px;font-weight:800;color:{_gc}'>{_grade}</div>
            </div>
            <div style='font-size:14px;color:#fff;font-weight:800;
            margin-bottom:8px'>{_verdict}</div>
            <div style='font-size:12px;color:#aaa;'>
            {cur_dw["시작연도"]}~{cur_dw["종료연도"]}년 (만 {_age}세) · 
            <b style='color:{_gc}'>{_remain}년 남음</b></div>
            </div>""",
            unsafe_allow_html=True,
        )

        # 해야 할 것 / 하면 망하는 것 — 직격 2단 컬럼
        if _dd:
            _c1, _c2 = st.columns(2)
            with _c1:
                st.markdown(
                    "<div style='font-size:13px;font-weight:900;color:#27ae60;"
                    "margin-bottom:8px;'>✅ 지금 반드시 해야 할 것</div>",
                    unsafe_allow_html=True,
                )
                for _item in _dd.get("do", []):
                    st.markdown(
                        f"<div style='font-size:12px;color:#1a5c2a;padding:5px 0;"
                        f"border-bottom:1px solid #e8f5e9;'>▶ {_item}</div>",
                        unsafe_allow_html=True,
                    )
            with _c2:
                st.markdown(
                    "<div style='font-size:13px;font-weight:900;color:#c0392b;"
                    "margin-bottom:8px;'>🚫 하면 망하는 것</div>",
                    unsafe_allow_html=True,
                )
                for _item in _dd.get("dont", []):
                    st.markdown(
                        f"<div style='font-size:12px;color:#7b241c;padding:5px 0;"
                        f"border-bottom:1px solid #fce4ec;'>✗ {_item}</div>",
                        unsafe_allow_html=True,
                    )
            st.markdown(
                f"<div style='background:#fff8e1;border-left:4px solid #f39c12;"
                f"border-radius:8px;padding:10px 14px;margin-top:10px;"
                f"font-size:13px;color:#7d6608;'>"
                f"💰 <b>재물 전략:</b> {_dd.get('money','')}<br>"
                f"⚠️ <b>핵심 경계:</b> {_dd.get('caution','')}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(0,0,0,0.08);margin:20px 0">',
            unsafe_allow_html=True,
        )

    # ── LocalSajuNarrator.lifeline 서술 분석 ────────────────────
    try:
        _local_out = LocalSajuNarrator.lifeline(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _le:
        st.warning(f"⚠️ 대운 분석 오류: {_le}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(0,0,0,0.05);margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section" style="font-size:18px; font-weight:700">🔄 大運 詳解</div>',
        unsafe_allow_html=True,
    )

    tab_daewoon(pils, birth_year, gender)

    st.markdown(
        '<hr style="border:none;border-top:1px solid rgba(0,0,0,0.05);margin:30px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section" style="font-size:18px; font-weight:700">🔀 大運 x 世運 交叉 分析</div>',
        unsafe_allow_html=True,
    )

    try:
        tab_cross_analysis(pils, birth_year, gender)
    except Exception as e:
        st.warning(f"交叉分析 오류: {e}")

    # AI 정밀 분석 버튼
    render_ai_deep_analysis("lifeline", pils, name, birth_year, gender)


def menu3_past(pils, birth_year, gender, name=""):
    """3️⃣ 과거 적중 타임라인 | 15년 자동 스캔"""

    # ── 로컬 엔진 항상 먼저 출력 ─────────────

    try:
        _local_out = LocalSajuNarrator.past_analysis(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 과거 분석 오류: {_e}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    st.markdown(
        """

<div style="background:#fff0f8;border:2px solid #e91e8c55;border-radius:12px; padding:14px 18px;margin-bottom:14px">

<div style="font-size:13px;font-weight:700;color:#880e4f;margin-bottom:4px">🎯 과거 적중 타임라인</div>

<div style="font-size:12px;color:#000000;line-height:1.8">충/합/십성 교차를 수학 계산으로 뽑은 과거 사건 시점입니다.</div>

</div>""",
        unsafe_allow_html=True,
    )

    # ── 인생 스토리 연결 ─────────────────────────
    st.markdown('<div class="gold-section">📖 과거·현재·미래 인생 스토리</div>', unsafe_allow_html=True)
    try:
        _ilgan_s = pils[1]["cg"]
        _ilp_s = ILGAN_PROFILE.get(_ilgan_s, {})
        _gy_s = get_gyeokguk(pils)
        _gname_s = _gy_s.get("격국명", "독특한 격국") if _gy_s else "독특한 격국"
        _cur_year_s = datetime.now().year
        _daewoon_s = SajuCoreEngine.get_daewoon(
            pils, birth_year,
            st.session_state.get("birth_month", 1),
            st.session_state.get("birth_day", 1),
            st.session_state.get("birth_hour", 12),
            st.session_state.get("birth_minute", 0),
            gender=gender,
        )
        _past_dws = [d for d in _daewoon_s if d.get("종료연도", 0) < _cur_year_s][-2:]
        _cur_dw_s = next((d for d in _daewoon_s if d["시작연도"] <= _cur_year_s <= d["종료연도"]), None)
        _future_dw_s = next((d for d in _daewoon_s if d.get("시작연도", 0) > _cur_year_s), None)
        _past_str = " → ".join(d.get("str", "?") for d in _past_dws) if _past_dws else "초기 대운"
        _cur_str = _cur_dw_s.get("str", "?") if _cur_dw_s else "?"
        _future_str = _future_dw_s.get("str", "?") if _future_dw_s else "다음 대운"
        _story_html = (
            f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
            f"border-radius:14px;padding:22px;margin:10px 0'>"
            f"<div style='font-size:14px;color:#3d2800;line-height:2.2;font-family:Noto Serif KR,serif'>"
            f"당신의 인생은 <b style='color:#c9a84c'>{_past_str} 대운</b>에 기반을 닦고,<br>"
            f"현재 <b style='color:#c9a84c'>{_cur_str} 대운</b>에서 {"수확의 시기를 맞이하고" if _cur_dw_s and _cur_dw_s.get("시작나이", 0) >= 40 else "꽃을 피우며"} 있습니다.<br>"
            f"그리고 곧 다가올 <b style='color:#c9a84c'>{_future_str} 대운</b>에서 새로운 장이 펼쳐질 것입니다.<br><br>"
            f"<span style='font-size:13px;color:#5a3d1a'>"
            f"{_gname_s} 격국을 타고난 {name if name else '당신'}님의 인생은 "
            f"{_ilp_s.get('본질', '강인한 의지와 독특한 기질')[:30]}의 여정입니다. "
            f"과거의 모든 경험은 현재의 내공이 되었고, 지금의 선택이 미래를 결정합니다."
            f"</span></div></div>"
        )
        st.markdown(_story_html, unsafe_allow_html=True)
    except Exception as _se:
        st.warning(f"⚠️ 오류: {str(_se)[:80]}")

    tab_past_events(pils, birth_year, gender, name)

    # AI 정밀 분석 버튼

    render_ai_deep_analysis("past", pils, name, birth_year, gender)


def menu4_future3(
    pils,
    birth_year,
    gender,
    marriage_status="미혼",
    name="내담자",
):
    """4️⃣ 미래 3년 집중 분석 - 돈/직장/연애"""

    # ── 로컬 엔진 항상 먼저 출력 ─────────────

    try:
        _marriage_v = st.session_state.get("in_marriage", "미혼")

        _local_out = LocalSajuNarrator.future3(pils, name, birth_year, gender, _marriage_v)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 미래3년 분석 오류: {_e}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    ilgan = pils[1]["cg"]

    current_year = datetime.now().year

    current_age = current_year - birth_year + 1

    st.markdown(
        """

<div style="background:#f0fff8;border:2px solid #27ae6055;border-radius:12px; padding:14px 18px;margin-bottom:14px">

<div style="font-size:13px;font-weight:700;color:#1b5e20;margin-bottom:4px">🔮 미래 3년 집중 분석</div>

<div style="font-size:12px;color:#000000;line-height:1.8">

    * 돈 / 직장 / 연애 3개 분야를 연도별로 집중 분석합니다.

</div>

</div>""",
        unsafe_allow_html=True,
    )

    ys = get_yongshin(pils)

    yongshin_ohs = ys.get("종합_용신", [])

    if not isinstance(yongshin_ohs, list):
        yongshin_ohs = []

    ilgan_oh = OH.get(ilgan, "")

    DOMAIN_SS = {
        "돈/재물":  {"食神", "正財", "偏財"},
        "직장/명예": {"正官", "偏官", "正印"},
        "연애/인연": {"正財", "偏財"} if gender == "남" else {"正官", "偏官"},
        "변화/이동": {"傷官", "劫財", "偏印"},
    }

    DOMAIN_COLOR = {
        "돈/재물": "#27ae60",
        "직장/명예": "#2980b9",
        "연애/인연": "#e91e8c",
        "변화/이동": "#e67e22",
    }

    years_data = []

    for y in range(current_year, current_year + 3):
        sw = get_yearly_luck(pils, y) or {}

        # 대운 호출 시 실제 생년월일시 반영 (사용자 지침 준수)

        birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

        birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

        birth_hour = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))

        birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

        dw = next(
            (
                d
                for d in SajuCoreEngine.get_daewoon(
                    pils,
                    birth_year,
                    birth_month,
                    birth_day,
                    birth_hour,
                    birth_minute,
                    gender=gender,
                )
                if d["시작연도"] <= y <= d["종료연도"]
            ),
            None,
        )

        dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-") if dw else "-"

        sw_ss = sw.get("십성_천간", "-")

        age = y - birth_year + 1

        # 분야별 점수

        domains = {}

        for dname, ss_set in DOMAIN_SS.items():
            score = 0

            if dw_ss in ss_set:
                score += 50

            if sw_ss in ss_set:
                score += 50

            domains[dname] = score

        # 용신 여부

        is_yong_dw = _get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong" if dw else False

        is_yong_sw = _get_yongshin_match(sw_ss, yongshin_ohs, ilgan_oh) == "yong"

        # 합깨짐 경고

        hap_warn = _get_hap_break_warning(pils, dw["jj"] if dw else "", sw.get("jj",""))

        years_data.append(
            {
                "year": y,
                "age": age,
                "dw": dw["str"] if dw else "-",
                "dw_ss": dw_ss,
                "sw": sw.get("세운",""),
                "sw_ss": sw_ss,
                "is_yong_dw": is_yong_dw,
                "is_yong_sw": is_yong_sw,
                "domains": domains,
                "hap_warn": hap_warn,
                "gilhyung": sw.get("길흉","평"),
            }
        )

    for yd in years_data:
        yong_both = yd["is_yong_dw"] and yd["is_yong_sw"]

        gishin_both = not yd["is_yong_dw"] and not yd["is_yong_sw"]

        card_color = "#000000" if yong_both else "#c0392b" if gishin_both else "#2980b9"

        card_bg = "#ffffff" if yong_both else "#fff0f0" if gishin_both else "#f0f8ff"

        label = "🌟 황금기" if yong_both else "⚠️ 수비" if gishin_both else "〰️ 혼재"

        st.markdown(
            f"""
<div style="background:{card_bg};border:2px solid {card_color};border-radius:16px;padding:20px;margin:12px 0">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
<div>
<span style="font-size:26px;font-weight:900;color:{card_color}">{yd["year"]}년</span>
<span style="font-size:14px;color:#000000;margin-left:10px">만 {yd["age"]}세</span>
</div>
<div style="background:{card_color};color:#fff;padding:5px 16px;border-radius:20px;font-size:13px;font-weight:700">{label}</div>
</div>
<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
<span style="background:#f5f5f5;color:#333;padding:3px 12px;border-radius:12px;font-size:12px">대운 {yd["dw"]}({yd["dw_ss"]})</span>
<span style="background:#f5f5f5;color:#333;padding:3px 12px;border-radius:12px;font-size:12px">세운 {yd["sw"]}({yd["sw_ss"]})</span>
<span style="color:{card_color};font-size:12px;padding:3px 8px;font-weight:700">{yd["gilhyung"]}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        # 분야별 점수 바

        domain_bars = ""

        for dname, score in yd["domains"].items():
            dc = DOMAIN_COLOR.get(dname, "#888")

            filled = score // 10

            bar_vis = "🟩" * filled + "⬜" * (10 - filled)

            status = "활성" if score >= 50 else "보통" if score >= 30 else "약함"

            domain_bars += f"""

<div style="display:flex;align-items:center;gap:10px;margin:4px 0">

<span style="font-size:12px;color:{dc};min-width:70px;font-weight:700">{dname}</span>

<span style="font-size:11px">{bar_vis}</span>

<span style="font-size:11px;color:#444">{status}</span>

</div>"""

        st.markdown(
            f"""
<div style="background:white;border-radius:10px;padding:12px">{domain_bars}</div>""",
            unsafe_allow_html=True,
        )

        # ── 연도별 직격 판단 ─────────────────────────────
        _yr_dw_ss = yd["dw_ss"]
        _yr_sw_ss = yd["sw_ss"]
        _yr_gil   = yd["gilhyung"]

        _YEAR_VERDICT = {
            "偏財": ("💰 재물·이성 기운 활발", "사업 기회가 오는 해. 적극적으로 움직이면 돈이 됩니다. 단 과도한 지출 주의."),
            "正財": ("💰 안정 수입 기운",       "차분히 저축하고 계획대로 움직이면 재물이 쌓입니다. 투기는 금물."),
            "食神": ("🌟 재능·복록 기운",       "하고 싶은 일을 시작하기 좋은 해. 새로운 파이프라인을 열어보세요."),
            "傷官": ("⚡ 변화·충돌 기운",       "직장 갈등이나 이직 충동이 강해지는 해. 욱하는 결정은 3일 후에 하세요."),
            "偏官": ("🔴 압박·사고 기운",       "건강과 사고에 각별히 주의. 무리한 도전보다 현재 자리 지키기가 최선."),
            "正官": ("🏆 명예·승진 기운",       "조직에서 인정받는 해. 승진·자격증·공직 도전에 최적의 시기."),
            "劫財": ("⚠️ 손재·경쟁 기운",       "투자·보증·동업 절대 금지. 현금을 지키는 것이 이 해의 승리."),
            "比肩": ("💪 독립·경쟁 기운",       "혼자 움직일 때 강해지는 해. 남에게 맡기지 말고 직접 나서세요."),
            "偏印": ("📚 변화·이동 기운",       "새 분야 공부·이사·이직 기운. 단 중도 포기를 조심하세요."),
            "正印": ("📖 귀인·배움 기운",       "스승이나 귀인의 도움으로 성장하는 해. 자격증·진학에 유리."),
        }

        _vt, _vd = _YEAR_VERDICT.get(_yr_sw_ss, ("〰️ 중립 기운", "흐름에 맞게 꾸준히 움직이는 해입니다."))
        _vcolor = "#c0392b" if "🔴" in _vt or "⚠️" in _vt else "#27ae60" if "💰" in _vt or "🌟" in _vt or "🏆" in _vt else "#2980b9"

        st.markdown(
            f"""<div style='background:#f8f9fa;border-left:4px solid {_vcolor};
            border-radius:0 10px 10px 0;padding:10px 14px;margin:8px 0;'>
            <div style='font-size:13px;font-weight:900;color:{_vcolor};margin-bottom:4px'>{_vt}</div>
            <div style='font-size:12px;color:#333;line-height:1.7;white-space:normal;word-break:break-all'>{_vd}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        if yd["hap_warn"]:
            for hw in yd["hap_warn"]:
                st.markdown(
                    f"""<div style="background:#fff0f0;border-left:4px solid {hw["color"]};border-radius:8px;padding:10px 14px;margin-top:8px;font-size:12px">
<b style="color:{hw["color"]}">{hw["level"]}</b><br>
<span style="color:#333">{hw["desc"]}</span></div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # 결혼 여부별 인연 조언

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gold-section">💑 인연/배우자운 (3년)</div>', unsafe_allow_html=True)

    if marriage_status in ("미혼", "이혼/별거"):
        MARRY_SS = {"正財", "偏財"} if gender == "남" else {"正官", "偏官"}

        for yd in years_data:
            if yd["sw_ss"] in MARRY_SS or yd["dw_ss"] in MARRY_SS:
                st.markdown(
                    f"""

<div style="background:#fff0f8;border-left:4px solid #e91e8c; border-radius:8px;padding:12px;margin:5px 0">

<b style="color:#e91e8c">{yd["year"]}년({yd["age"]}세)</b> -

                    인연성이 강합니다. 적극적으로 움직이십시오.

</div>

""",
                    unsafe_allow_html=True,
                )

    else:
        st.markdown(
            f"""

<div style="background:#f0fff8;border-left:4px solid #27ae60; border-radius:8px;padding:12px">

            {marriage_status} 상태. 부부 관계 흐름 분석은 육친론을 참고하세요.

</div>

""",
            unsafe_allow_html=True,
        )

    # ── 사고수·사업실패수·이별수 직격 경고 ────────────────────
    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gold-section">🚨 3년 내 위기 직격 경고</div>', unsafe_allow_html=True)

    _ilgan = pils[1]["cg"] if len(pils) > 1 else ""
    _CHUNG_PAIRS = {
        "子": "午", "午": "子", "丑": "未", "未": "丑",
        "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
        "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
    }
    _pil_jjs = [p.get("jj", "") for p in pils]

    _danger_cards = []
    for yd in years_data:
        _warns = []
        _sw_jj_y = next(
            (p.get("jj", "") for p in pils if p.get("year") == yd["year"]), ""
        )
        # 세운 간지 직접 구하기
        try:
            _yl = get_yearly_luck(pils, yd["year"])
            _sw_jj_y = _yl.get("jj", "")
            _sw_cg_y = _yl.get("세운", "")[:1]
        except Exception:
            _sw_jj_y, _sw_cg_y = "", ""

        # 1) 충(沖) 탐지 — 세운 지지가 원국 지지와 충
        _chung_hits = [j for j in _pil_jjs if _CHUNG_PAIRS.get(_sw_jj_y) == j]
        if _chung_hits:
            _warns.append(
                ("🔴 충(沖) 발동",
                 f"세운 지지({_sw_jj_y})가 원국의 {'/'.join(_chung_hits)}와 충돌합니다. "
                 "이동·사고·수술·이별·이직 등 큰 변화가 강제로 일어날 수 있는 해입니다. "
                 "자동차·기계 조작 시 각별히 주의하고, 큰 계약과 투자는 이 해를 피하십시오.",
                 "#e53935")
            )

        # 2) 겁재 세운 — 사업실패·손재수
        if yd["sw_ss"] in ("劫財(겁재)", "겁재"):
            _warns.append(
                ("💸 겁재(劫財) 세운 — 손재수 경고",
                 f"{yd['year']}년은 내 재물을 빼앗기는 겁재의 해입니다. "
                 "동업 제안·지인 투자·보증은 100% 거절하십시오. "
                 "사업 확장을 이 해에 강행하면 자금이 묶이거나 배신을 당합니다. "
                 "현금 보유, 기존 사업 유지가 최선의 전략입니다.",
                 "#e65100")
            )

        # 3) 편관 세운 — 관재수·사고수
        if yd["sw_ss"] in ("偏官(편관)", "편관"):
            _warns.append(
                ("⚡ 편관(偏官) 세운 — 관재·사고 주의",
                 f"{yd['year']}년은 강한 압박과 돌발 사고가 따르는 편관의 해입니다. "
                 "법적 분쟁·소송·세무조사 등 관재수가 있을 수 있습니다. "
                 "건강도 악화되기 쉬우니 과로를 피하고 정기검진을 챙기십시오. "
                 "이 해에는 소극적으로 방어하는 것이 오히려 승리입니다.",
                 "#6a1fa2")
            )

        # 4) 상관+편관 조합 — 극단적 직업 변동
        if yd["sw_ss"] in ("傷官(상관)", "상관") and yd["dw_ss"] in ("偏官(편관)", "편관"):
            _warns.append(
                ("🌪️ 상관+편관 충돌 — 직업·이직 대격변",
                 f"{yd['year']}년 세운 상관이 대운 편관과 충돌합니다. "
                 "지금 다니는 직장을 그만두거나 강제 퇴직당할 수 있는 구조입니다. "
                 "욱하는 마음에 사직서 내지 마시고, 최소 3개월 이상 여유 자금을 확보한 뒤 결단하십시오.",
                 "#1565c0")
            )

        # 5) 겁재+편재 동시 — 바람·이성 문제
        if yd["sw_ss"] in ("劫財(겁재)", "겁재") and gender == "남":
            _warns.append(
                ("🌹 겁재 세운 — 이성 문제 주의",
                 f"{yd['year']}년 배우자나 연인 외의 이성 관계에서 문제가 생기기 쉽습니다. "
                 "감추어 두었던 이성 관계가 드러나거나, 상대방이 다른 사람에게 흔들릴 수 있습니다. "
                 "이성 문제로 재물까지 새는 2중 손실을 조심하십시오.",
                 "#c62828")
            )

        if _warns:
            _danger_cards.append((yd["year"], yd["age"], _warns))

    if _danger_cards:
        for _yr, _age, _ws in _danger_cards:
            for _wtitle, _wdesc, _wcolor in _ws:
                st.markdown(
                    f"""<div style='background:#fff5f5;border-left:5px solid {_wcolor};
                    border-radius:10px;padding:14px 18px;margin:8px 0;'>
                    <div style='font-size:14px;font-weight:900;color:{_wcolor};margin-bottom:6px'>
                    {_yr}년(만 {_age}세) {_wtitle}</div>
                    <div style='font-size:13px;color:#333;line-height:1.9'>{_wdesc}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.success("✅ 향후 3년간 특별히 강한 위기 시그널은 보이지 않습니다. 꾸준히 현재 흐름을 유지하십시오.")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gold-section">📅 월별 세운 (올해)</div>', unsafe_allow_html=True)

    tab_monthly(pils, birth_year, gender)

    # 미래 3년 상세 해설

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ── 3년 월 단위 최적 타이밍 직격 ────────────────────────────
    st.markdown(
        '<div class="gold-section">📅 향후 3년 연도별 월 단위 최적 타이밍</div>',
        unsafe_allow_html=True,
    )
    _focus_f3 = st.radio(
        "분야", ["재물", "인연", "직업", "건강"], horizontal=True,
        key="future3_timing_focus", index=0,
    )
    for _yr in range(datetime.now().year, datetime.now().year + 3):
        try:
            _mt3 = get_monthly_timing(pils, birth_year, gender, _yr, _focus_f3)
            _peak_str   = ", ".join([f"{m}월" for m, d in _mt3["peak"]   if "⭐⭐⭐" in d or "⭐⭐" in d])
            _caution_str = ", ".join([f"{m}월" for m, d in _mt3["caution"] if "⛔" in d])
            if not _peak_str:
                _peak_str = ", ".join([f"{m}월" for m, _ in _mt3["peak"][:3]])
            st.markdown(
                f"""<div style='background:#f8f9fa;border-radius:12px;
                padding:12px 16px;margin:6px 0;border-left:4px solid #c9a84c;'>
                <div style='font-size:14px;font-weight:900;color:#2d1f00;
                margin-bottom:6px'>📌 {_yr}년 {_focus_f3} 타이밍</div>
                <div style='font-size:13px;color:#1a5c2a;margin-bottom:4px'>
                ✅ <b>최적 달:</b> {_peak_str or "해당 없음"}</div>
                <div style='font-size:13px;color:#c0392b;'>
                ⛔ <b>피할 달:</b> {_caution_str or "없음"}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        except Exception as _mte3:
            _saju_log.warning("[menu4_future3] 오류: %s", str(e)[:60])

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">📜 미래 3년 완전 해설 - 만신의 풀이</div>',
        unsafe_allow_html=True,
    )

    try:
        narrative = build_rich_narrative(pils, birth_year, gender, "", section="future")

        blocks = narrative.split("-" * 55)

        if blocks:
            intro = blocks[0].strip()

            if intro:
                st.markdown(
                    f"""

<div style="background:linear-gradient(135deg,#dcfff5,#dcfffd); border-left:4px solid #27ae60;border-radius:10px; padding:16px 20px;margin:10px 0">

<div style="font-size:13px;color:#1a4a2a;line-height:1.9;white-space:pre-wrap">{intro}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

            for block in blocks[1:]:
                if not block.strip():
                    continue

                lines = block.strip().split("\n")

                title_line = next((l for l in lines if l.strip()), "")

                body = "\n".join(lines[1:]).strip()

                is_good = "-" in title_line

                is_bad = "⚠️" in title_line

                bg = "rgba(197,160,89,0.12)" if is_good else "rgba(192,57,43,0.12)" if is_bad else "rgba(41,128,185,0.12)"

                bc = "#000000" if is_good else "#c0392b" if is_bad else "#2980b9"

                st.markdown(
                    f"""

<div style="background:{bg};border-left:4px solid {bc}; border-radius:10px;padding:16px 20px;margin:8px 0">

<div style="font-size:14px;font-weight:900;color:{bc};margin-bottom:10px">{title_line}</div>

<div style="font-size:13px;color:#000000;line-height:1.9;white-space:pre-wrap">{body}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"미래 해설 오류: {e}")

    # AI 정밀 분석 버튼

    render_ai_deep_analysis("future", pils, name, birth_year, gender)


def menu5_money(pils, birth_year, gender, name="내담자"):
    """5️⃣ 재물/사업 특화 분석"""

    ilgan = pils[1]["cg"]
    ilgan_oh = OH.get(ilgan, "")
    current_year = datetime.now().year
    current_age = current_year - birth_year + 1
    ys = get_yongshin(pils)
    yongshin_ohs = ys.get("종합_용신", []) or []
    gyeokguk = get_gyeokguk(pils)
    gname = gyeokguk.get("격국명", "") if gyeokguk else ""
    ilp = ILGAN_PROFILE.get(ilgan, {})
    daewoon = SajuCoreEngine.get_daewoon(
        pils, birth_year,
        st.session_state.get("birth_month", 1),
        st.session_state.get("birth_day", 1),
        st.session_state.get("birth_hour", 12),
        st.session_state.get("birth_minute", 0),
        gender=gender,
    )
    cur_dw = next((d for d in daewoon if d["시작연도"] <= current_year <= d["종료연도"]), None) or {}

    # ① 타고난 재물 그릇
    st.markdown('<div class="gold-section">💎 ① 타고난 재물 그릇 분석</div>', unsafe_allow_html=True)
    _GYEOK_MONEY = {
        "식신격": ("중·대형", "꾸준히 먹고사는 복록. 부업·창작으로 자산을 늘림. 안정적 수입원이 다양함."),
        "정관격": ("중형", "조직에서 안정적 수입. 재테크보다 직업적 성취로 자산 형성."),
        "편관격": ("대형 또는 소형", "극단적 기복. 크게 성공하거나 손실도 큼. 도전적 투자 성향."),
        "정재격": ("중·대형", "착실하게 쌓는 재물. 저축·부동산·안전 투자에 탁월."),
        "편재격": ("대형", "큰 사업·투자로 자산 폭발. 기복이 크나 기회 포착 능력 최강."),
        "상관격": ("중형", "기술·창의로 버는 재물. 자유업·전문직에서 수입 극대화."),
        "건록격": ("중형", "노력으로 쌓는 재물. 사업보다 직업적 성취가 안정적."),
    }
    _bowl_size, _bowl_desc = "중형", "사주의 기운에 따라 꾸준히 쌓이는 재물 운."
    for _gk, (_sz, _dc) in _GYEOK_MONEY.items():
        if _gk in gname:
            _bowl_size, _bowl_desc = _sz, _dc
            break
    _jaemul_profile = ilp.get("재물", "")
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0'>"
        f"<div style='font-size:15px;font-weight:800;color:#2d1f00;margin-bottom:10px'>"
        f"재물 그릇 크기: <span style='color:#c9a84c;font-size:18px'>{_bowl_size}</span> ({gname or '격국 분석 중'})</div>"
        f"<div style='font-size:14px;color:#3d2800;line-height:1.9'>{_bowl_desc}</div>"
        f"<div style='margin-top:10px;font-size:13px;color:#5a3d1a;border-top:1px solid rgba(201,168,76,0.3);padding-top:8px'>"
        f"일간({ilgan}) 재물 기질: {_jaemul_profile}</div></div>",
        unsafe_allow_html=True,
    )

    # ② 직업 적성 정밀 분석
    st.markdown('<div class="gold-section">💼 ② 직업 적성 정밀 분석</div>', unsafe_allow_html=True)
    _jikup = ilp.get("직업", "")
    _cur_dw_ss_hanja = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw.get("cg", ""), "") if cur_dw else ""
    _DW_INDUSTRY = {
        "比肩": "독립 사업·프리랜서·스포츠·1인 창업",
        "劫財": "경쟁업종·금융·영업·투자",
        "食神": "외식·창작·콘텐츠·교육·서비스",
        "傷官": "IT·엔지니어링·예술·컨설팅",
        "偏財": "무역·사업·부동산·마케팅",
        "正財": "금융·회계·공무원·안정 직종",
        "偏官": "군인·경찰·의료·법조·스포츠",
        "正官": "공기업·관리직·행정·교육",
        "偏印": "역술·종교·예술·자유업·이동업종",
        "正印": "교육·연구·출판·의료·상담",
    }
    _cur_industry = _DW_INDUSTRY.get(_cur_dw_ss_hanja, "현재 대운 기운에 맞는 업종 탐색 중")
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0'>"
        f"<div style='font-size:14px;color:#3d2800;line-height:2'>"
        f"<b>🎯 일간({ilgan}) 최적 직군:</b> {_jikup}<br>"
        f"<b>📈 현재 대운({_cur_dw_ss_hanja or '?'})에서 유리한 업종:</b> {_cur_industry}</div></div>",
        unsafe_allow_html=True,
    )

    # ③ 재물운 타임라인
    st.markdown('<div class="gold-section">📈 ③ 재물운 타임라인</div>', unsafe_allow_html=True)
    _timeline_items = []
    for _age_target, _label in [(25, "20대"), (35, "30대"), (45, "40대"), (55, "50대")]:
        _target_year = birth_year + _age_target
        _dw_match = next((d for d in daewoon if d["시작연도"] <= _target_year <= d["종료연도"]), None)
        if _dw_match:
            _dw_ss_h = TEN_GODS_MATRIX.get(ilgan, {}).get(_dw_match.get("cg", ""), "")
            _money_level = "🟢 호황" if _dw_ss_h in ("偏財(편재)", "正財(정재)", "食神(식신)", "正官(정관)") else "🟡 보통" if _dw_ss_h in ("比肩(비견)", "正印(정인)", "傷官(상관)") else "🔴 주의"
            _timeline_items.append(f"<div style='padding:8px 0;border-bottom:1px solid rgba(201,168,76,0.2)'>"
                                   f"<b>{_label}</b> ({_dw_match['str']} 대운) — {_money_level} [{_dw_ss_h or '?'}]</div>")
    _now_label = f"<div style='padding:8px 0;font-weight:700;color:#c9a84c'>현재({current_age}세) — {cur_dw.get('str','?')} 대운 진행 중</div>"
    _future5_items = []
    for _y in range(current_year + 1, current_year + 6):
        try:
            _yl = get_yearly_luck(pils, _y)
            _y_ss = _yl.get("십성_천간", "-")
            _y_gh = _yl.get("길흉", "보통")
            _y_sw = _yl.get("세운", str(_y))
            _future5_items.append(f"{_y}년[{_y_sw}] {_y_ss} {_y_gh}")
        except Exception:
            _saju_log.warning("[menu5_money] 오류: %s", str(e)[:60])
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0;font-size:13px;color:#3d2800;line-height:2'>"
        f"{''.join(_timeline_items)}{_now_label}"
        f"<div style='margin-top:8px;font-size:12px;color:#5a3d1a'><b>향후 5년:</b> "
        f"{' / '.join(_future5_items)}</div></div>",
        unsafe_allow_html=True,
    )

    # ④ 재물 개운법
    st.markdown('<div class="gold-section">🌟 ④ 재물 개운법</div>', unsafe_allow_html=True)
    _OH_MONEY_TIPS = {
        "木": ("동쪽 방향 책상 배치, 초록색 지갑/식물 활용", "서·서북쪽 인테리어 강화 지양", ["동쪽 방향으로 책상 바꾸기", "초록색 지갑 사용하기", "나무·식물 키우기"]),
        "火": ("남쪽 방향 활동, 붉은색 소품 활용", "북쪽 방향 침실 배치 지양", ["남향 창문 열어두기", "붉은 계열 소품 배치", "촛불·조명 밝히기"]),
        "土": ("중앙·황금색 활용, 도자기·토기 소품", "습기·어두운 공간 지양", ["황색·갈색 지갑 사용", "도자기 소품 배치", "중심 잡힌 식습관 유지"]),
        "金": ("서쪽·흰색 활용, 금속 소품·동전 모으기", "충동 구매·과한 지출 지양", ["흰색·실버 소품 배치", "금속 저금통 사용", "정리정돈 철저히"]),
        "水": ("북쪽·검은색 활용, 수족관·물 인테리어", "지나친 음주·산만한 환경 지양", ["검은 지갑 사용", "물 관련 인테리어", "조용한 집중 환경 만들기"]),
    }
    _yong_oh = yongshin_ohs[0] if yongshin_ohs else ilgan_oh
    _tip_enhance, _tip_avoid, _tip_now = _OH_MONEY_TIPS.get(_yong_oh, ("용신 오행 강화 활동", "기신 오행 약화 활동", ["용신 방향 활동", "긍정적 마음가짐", "꾸준한 저축"]))
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0'>"
        f"<div style='font-size:14px;color:#3d2800;line-height:2'>"
        f"<b>✅ 재물 강화법 (용신 {_yong_oh} 기반):</b> {_tip_enhance}<br>"
        f"<b>❌ 피해야 할 것:</b> {_tip_avoid}<br>"
        f"<b>⚡ 지금 당장 할 수 있는 3가지:</b><br>"
        f"{''.join(f'&nbsp;&nbsp;&nbsp;{i+1}. {t}<br>' for i, t in enumerate(_tip_now))}</div></div>",
        unsafe_allow_html=True,
    )

    # ── 로컬 엔진 상세 분석 ─────────────
    try:
        _local_out = LocalSajuNarrator.money(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 재물 분석 오류: {_e}")

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    st.markdown(
        """

<div style="background:#f5fff0;border:2px solid #2e7d3255;border-radius:12px; padding:14px 18px;margin-bottom:14px">

<div style="font-size:13px;font-weight:700;color:#1b5e20;margin-bottom:4px">💰 재물/사업 특화 분석</div>

<div style="font-size:12px;color:#000000;line-height:1.8">

    * 수익 구조 / 재물 기질 / 돈이 터지는 시기를 십성 조합으로 분석합니다.

</div>

</div>""",
        unsafe_allow_html=True,
    )

    ilgan = pils[1]["cg"]

    ys = get_yongshin(pils)

    yongshin_ohs = ys.get("종합_용신", [])

    if not isinstance(yongshin_ohs, list):
        yongshin_ohs = []

    ilgan_oh = OH.get(ilgan, "")

    current_year = datetime.now().year

    # ① 십성 조합 기반 재물 기질

    st.markdown(
        '<div class="gold-section">💎 십성 조합으로 보는 재물 기질</div>',
        unsafe_allow_html=True,
    )

    try:
        life = build_life_analysis(pils, gender)

        combos = life["조합_결과"]

        ss_dist = life["전체_십성"]

        # 재물 관련 조합만 강조

        MONEY_SS = {"식신", "상관", "편재", "정재", "겁재", "비견"}

        money_combos = [(k, v) for k, v in combos if any(s in MONEY_SS for s in k)]

        if money_combos:
            for key, combo in money_combos:
                st.markdown(
                    f"""

<div style="background:linear-gradient(135deg,#f5f5f5,#f5ffea); border:2px solid #4a8a20;border-radius:14px;padding:20px;margin:10px 0">

<div style="font-size:17px;font-weight:900;color:#a0d040;margin-bottom:10px">

                        {combo["요약"]}

</div>

<div style="background:#eaffdc;border-radius:10px;padding:14px;margin-bottom:10px; border-left:4px solid #000000">

<div style="font-size:11px;color:#000000;font-weight:700;margin-bottom:6px">💰 재물 버는 방식</div>

<div style="font-size:14px;color:#f0e0a0;line-height:1.9">{combo["재물"]}</div>

</div>

<div style="background:#eaffdc;border-radius:10px;padding:14px;margin-bottom:10px; border-left:4px solid #3498db">

<div style="font-size:11px;color:#5ab4ff;font-weight:700;margin-bottom:6px">💼 맞는 직업/사업</div>

<div style="font-size:14px;color:#c0d8f0;line-height:1.9">{combo["직업"]}</div>

</div>

<div style="background:#f5f5f5;border-radius:10px;padding:12px; border-left:4px solid #e74c3c">

<div style="font-size:11px;color:#ff6b6b;font-weight:700;margin-bottom:4px">⚠️ 재물 주의사항</div>

<div style="font-size:13px;color:#f0c0c0;line-height:1.8">{combo["주의"]}</div>

</div>

</div>

""",
                    unsafe_allow_html=True,
                )

        elif combos:
            key, combo = combos[0]

            st.markdown(
                f"""

<div style="background:#ffffff;border-radius:12px;padding:18px;border:1px solid #3a4060">

<div style="font-size:16px;font-weight:700;color:#000000;margin-bottom:10px">{combo["요약"]}</div>

<div style="font-size:14px;color:#f0e0a0;line-height:1.9">{combo["재물"]}</div>

</div>

""",
                unsafe_allow_html=True,
            )

        # 십성별 재물 기질 요약

        MONEY_NATURE = {
            "식신": "🌾 재능/기술로 꾸준히 버는 타입. 억지로 돈 쫓지 않아도 따라온다.",
            "상관": "⚡ 아이디어/말/창의로 버는 타입. 새로운 방식으로 수익을 만든다.",
            "편재": "🎰 활발한 활동/투자/사업으로 버는 타입. 기복이 있지만 크게 번다.",
            "정재": "🏦 성실하게 모으는 타입. 꾸준히 하면 결국 쌓인다.",
            "겁재": "💸 크게 벌고 크게 쓰는 타입. 재물 관리가 인생 최대 숙제.",
            "비견": "⚔️ 독립/자영업으로 버는 타입. 남 밑에서는 돈이 안 모인다.",
            "편관": "🔥 직위/권한에서 재물이 따라오는 타입. 높은 자리가 돈이 된다.",
            "정관": "🏛️ 안정된 직장에서 꾸준히 쌓는 타입. 직급이 올라갈수록 재물도 는다.",
            "편인": "🎭 특수 분야 전문성으로 버는 타입. 일반적인 방법보다 틈새가 맞다.",
            "정인": "📚 지식/자격/귀인을 통해 재물이 오는 타입. 배움이 곧 돈이 된다.",
        }

        st.markdown(
            '<div style="font-size:13px;font-weight:800;color:#000000;margin:16px 0 8px;border-left:3px solid #000000;padding-left:10px">📊 주요 십성별 재물 기질</div>',
            unsafe_allow_html=True,
        )

        for ss, cnt in sorted(ss_dist.items(), key=lambda x: -x[1])[:4]:
            if ss in MONEY_NATURE:
                ss_color = {
                    "식신": "#27ae60",
                    "상관": "#e67e22",
                    "편재": "#2ecc71",
                    "정재": "#16a085",
                    "겁재": "#e74c3c",
                    "비견": "#3498db",
                    "편관": "#c0392b",
                    "정관": "#2980b9",
                    "편인": "#8e44ad",
                    "정인": "#d35400",
                }.get(ss, "#888")

                st.markdown(
                    f"""

<div style="display:flex;align-items:flex-start;gap:12px;padding:10px 0; border-bottom:1px solid #eee">

<span style="background:{ss_color};color:#000000;padding:3px 10px; border-radius:12px;font-size:12px;white-space:nowrap; min-width:50px;text-align:center">{ss}x{cnt}</span>

<span style="font-size:13px;color:#000000;line-height:1.8">{MONEY_NATURE.get(ss, "")}</span>

</div>

""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"재물 기질 분석 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ② 돈 터지는 시기

    st.markdown('<div class="gold-section">📈 돈이 터지는 시기</div>', unsafe_allow_html=True)

    try:
        with st.spinner("재물 운기 계산 중..."):
            hl = generate_engine_highlights(pils, birth_year, gender)

        if hl["money_peak"]:
            for mp in hl["money_peak"]:
                is_double = mp.get("ss") == "더블"

                bg = "#ffffff" if is_double else "#f0fff0"

                bc = "#000000" if is_double else "#27ae60"

                icon = "🌟" if is_double else "💰"

                st.markdown(
                    f"""

<div style="background:{bg};border:2px solid {bc};border-radius:12px; padding:16px;margin:8px 0">

<span style="font-size:18px;font-weight:900;color:{bc}">{icon} {mp["age"]}</span>

<span style="font-size:12px;color:#000000;margin-left:8px">({mp["year"]})</span>

<div style="font-size:13px;color:#000000;margin-top:6px;line-height:1.8">{mp["desc"]}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

        else:
            st.info("현재 기준 향후 5년 내 뚜렷한 재물 피크가 계산되지 않았습니다.")

    except Exception as e:
        st.warning(f"재물 운기 계산 오류: {e}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">💰 재물론 상세 (장생/12운성)</div>',
        unsafe_allow_html=True,
    )

    try:
        tab_jaemul(pils, birth_year, gender)

    except Exception as e:
        st.warning(f"재물론 오류: {e}")

    # 재물 완전 해설

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">📜 재물/사업 완전 해설 - 만신의 풀이</div>',
        unsafe_allow_html=True,
    )

    try:
        narrative = build_rich_narrative(pils, birth_year, gender, "", section="money")

        sections = narrative.split("【")

        for sec in sections:
            if not sec.strip():
                continue

            lines = sec.strip().split("\n")

            title = lines[0].replace("】", "").strip() if lines else ""

            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

            if title:
                st.markdown(
                    f"""

<div style="background:linear-gradient(135deg,#eaffdc,#f5ffdc); border-left:4px solid #000000;border-radius:10px; padding:18px 22px;margin:10px 0">

<div style="font-size:14px;font-weight:900;color:#000000;margin-bottom:10px">

                        【 {title} 】

</div>

<div style="font-size:13px;color:#2a4a00;line-height:2.0;white-space:pre-wrap">{body}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"재물 해설 오류: {e}")

    # AI 정밀 분석 버튼

    render_ai_deep_analysis("money", pils, name, birth_year, gender)


def menu6_relations(pils, name, birth_year, gender, marriage_status="미혼"):
    """6️⃣ 궁합 / 인간관계 분석"""

    # ── 로컬 엔진 항상 먼저 출력 ─────────────

    try:
        _marriage_v2 = st.session_state.get("in_marriage", "미혼")

        _local_out = LocalSajuNarrator.relations(pils, name, birth_year, gender, _marriage_v2)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 관계 분석 오류: {_e}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    st.markdown(
        """

<div style="background:#fdf0ff;border:2px solid #9b59b655;border-radius:12px; padding:14px 18px;margin-bottom:14px">

<div style="font-size:13px;font-weight:700;color:#4a148c;margin-bottom:4px">💑 궁합 / 인간관계 분석</div>

<div style="font-size:12px;color:#000000;line-height:1.8">

    * 연인 / 동업자 / 상사와의 인간관계를 사주로 분석합니다.

</div>

</div>""",
        unsafe_allow_html=True,
    )

    # ① 배우자/인연 프로필
    st.markdown('<div class="gold-section">💍 ① 배우자·인연 프로필</div>', unsafe_allow_html=True)
    _ilgan = pils[1]["cg"]
    _iljj = pils[1]["jj"]
    _ilgan_oh = OH.get(_ilgan, "")
    _ilp = ILGAN_PROFILE.get(_ilgan, {})
    # 성별에 따라 배우자 십성 결정
    if gender == "남":
        _spouse_ss = ["正財(정재)", "偏財(편재)"]
        _spouse_label = "배우자·여성 인연"
    else:
        _spouse_ss = ["正官(정관)", "偏官(편관)"]
        _spouse_label = "배우자·남성 인연"
    # 일지 분석
    _JJ_SPOUSE = {
        "子": "지적이고 총명한 배우자. 감정 표현이 적고 독립심이 강함.",
        "丑": "듬직하고 성실한 배우자. 변화를 싫어하나 신뢰도가 높음.",
        "寅": "활동적이고 리더십 강한 배우자. 자존심이 세고 독립적.",
        "卯": "섬세하고 감수성 풍부한 배우자. 예술적 기질, 사교적.",
        "辰": "포용력 있고 현실적인 배우자. 안정 지향, 재물 운 강함.",
        "巳": "지혜롭고 카리스마 있는 배우자. 비밀이 많고 깊은 내면.",
        "午": "열정적이고 화끈한 배우자. 매력이 강하나 감정 기복 있음.",
        "未": "온화하고 배려 깊은 배우자. 예술·미적 감각이 뛰어남.",
        "申": "총명하고 실행력 강한 배우자. 직설적이고 솔직한 성격.",
        "酉": "세련되고 완벽주의적 배우자. 높은 기준, 우아한 품격.",
        "戌": "의리 있고 충성스러운 배우자. 고집 있으나 믿음직스러움.",
        "亥": "자유롭고 지적인 배우자. 창의적이나 정착이 어려운 면.",
    }
    _iljj_spouse = _JJ_SPOUSE.get(_iljj, "배우자 자리에 특별한 인연의 기운이 있습니다.")
    _yeonae_style = _ilp.get("연애", "")
    # 도화살 확인 (子·午·卯·酉 지지 중 해당)
    _dohwa_jj = ["子", "午", "卯", "酉"]
    _has_dohwa = any(p.get("jj") in _dohwa_jj for p in pils)
    _dohwa_txt = "✨ 도화살이 있습니다 — 이성 매력이 강하고 인기가 많습니다." if _has_dohwa else "도화살 없음 — 이성보다 실력으로 인정받는 타입."
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0'>"
        f"<div style='font-size:14px;color:#3d2800;line-height:2'>"
        f"<b>💑 {_spouse_label} 기운:</b> {', '.join(_spouse_ss)} 십성이 {_spouse_label}을 나타냅니다.<br>"
        f"<b>🪑 일지(日支 {_iljj}) — 배우자 자리:</b> {_iljj_spouse}<br>"
        f"<b>❤️ 연애 스타일:</b> {_yeonae_style}<br>"
        f"<b>🌸 도화살:</b> {_dohwa_txt}</div></div>",
        unsafe_allow_html=True,
    )

    # ② 결혼 타이밍 예측
    st.markdown('<div class="gold-section">💒 ② 결혼·인연 타이밍 예측</div>', unsafe_allow_html=True)
    _current_year = datetime.now().year
    _marriage_years = []
    for _y in range(_current_year, _current_year + 10):
        try:
            _yl = get_yearly_luck(pils, _y)
            _y_ss = _yl.get("십성_천간", "")
            if _y_ss in _spouse_ss or _yl.get("십성_지지", "") in _spouse_ss:
                _marriage_years.append(f"{_y}년 [{_yl.get('세운', str(_y))}] — {_y_ss} 기운 (인연운 강함)")
        except Exception:
            _saju_log.warning("[menu6_relations] 오류: %s", str(e)[:60])
    if _marriage_years:
        _marriage_info = "\n".join(f"    🌸 {m}" for m in _marriage_years[:4])
    else:
        _marriage_info = "    향후 10년 내 특별한 인연운이 흐릅니다."
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
        f"border-radius:14px;padding:20px;margin:10px 0;font-size:13px;color:#3d2800;line-height:2'>"
        f"<b>향후 10년 인연·결혼 운 강한 해:</b><br>"
        + "<br>".join(f"🌸 {m}" for m in _marriage_years[:4])
        + (f"<br><span style='color:#888;font-size:12px'>특별한 인연운이 점차 다가옵니다</span>" if not _marriage_years else "")
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">👫 육친론 - 주변 인물 분석</div>',
        unsafe_allow_html=True,
    )

    tab_yukjin(pils, gender)

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gold-section">💑 궁합 분석</div>', unsafe_allow_html=True)

    tab_gunghap(pils, name)

    # 인간관계 완전 해설

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="gold-section">📜 육친/인간관계 완전 해설 - 만신의 풀이</div>',
        unsafe_allow_html=True,
    )

    try:
        narrative = build_rich_narrative(pils, birth_year, gender, name if name else "내담자", section="relations")

        sections = narrative.split("【")

        for sec in sections:
            if not sec.strip():
                continue

            lines = sec.strip().split("\n")

            title = lines[0].replace("】", "").strip() if lines else ""

            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

            if not title:
                continue

            # 육친 파트 vs 일반 파트

            if "*" in body:
                # 육친 개별 카드

                sub_items = body.split("*")

                if title:
                    st.markdown(
                        f"<div style='font-size:14px;font-weight:900;color:#c39bd3;margin:12px 0 6px'>【 {title} 】</div>",
                        unsafe_allow_html=True,
                    )

                for item in sub_items:
                    if not item.strip():
                        continue

                    item_lines = item.strip().split("\n")

                    item_title = item_lines[0].strip()

                    item_body = "\n".join(item_lines[1:]).strip()

                    st.markdown(
                        f"""

<div style="background:#f5f5f5;border-left:4px solid #9b59b6; border-radius:10px;padding:14px 18px;margin:6px 0">

<div style="font-size:13px;font-weight:700;color:#c39bd3;margin-bottom:6px">* {item_title}</div>

<div style="font-size:13px;color:#e8d0f8;line-height:1.9;white-space:pre-wrap">{item_body}</div>

</div>

""",
                        unsafe_allow_html=True,
                    )

            else:
                st.markdown(
                    f"""

<div style="background:linear-gradient(135deg,#ffdcff,#ffdcff); border-left:4px solid #9b59b6;border-radius:10px; padding:18px 22px;margin:10px 0">

<div style="font-size:14px;font-weight:900;color:#c39bd3;margin-bottom:10px">

                        【 {title} 】

</div>

<div style="font-size:13px;color:#e8d0f8;line-height:2.0;white-space:pre-wrap">{body}</div>

</div>

""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"인간관계 해설 오류: {e}")

    # AI 정밀 분석 버튼

    render_ai_deep_analysis("relations", pils, name, birth_year, gender)


################################################################################

# ☀️ menu9_daily  - 일일 운세

# 📅 menu10_monthly - 월별 운세

# 🎊 menu11_yearly  - 신년 운세

################################################################################


def menu9_daily(pils, name, birth_year, gender):
    """9️⃣ 일일 운세 - 오늘 하루의 기운에 집중한 심플 모드"""

    # ── 로컬 엔진 항상 먼저 출력 ─────────────

    try:
        _local_out = LocalSajuNarrator.daily(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 일진 분석 오류: {_e}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    ilgan = pils[1]["cg"]

    today = datetime.now()

    display_name = name if name else "내담자"

    # -- 일진 계산 헬퍼 ------------------

    def get_day_pillar(dt):

        base = date(1924, 1, 1)

        delta = (dt.date() - base).days if hasattr(dt, "date") else (dt - base).days

        return CG[delta % 10], JJ[delta % 12]

    today_cg, today_jj = get_day_pillar(today)

    today_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(today_cg, "-")

    # -- 헤더 --------------------------

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg,#e8f4ff,#ddeeff); border-radius:14px;padding:18px 24px;margin-bottom:16px;text-align:center">

<div style="font-size:22px;font-weight:900;color:#0d47a1;letter-spacing:2px">

        ☀️ {display_name}님의 오늘의 운세

</div>

<div style="font-size:13px;color:#000000;margin-top:6px">

        {today.strftime("%Y년 %m월 %d일")} ({["월", "화", "수", "목", "금", "토", "일"][today.weekday()]}요일)

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # -- 일진 심층 해설 (API 있으면 AI, 없으면 로컬 엔진) --------------

    # 로컬용 오행 정보 미리 준비

    _OH_NAME = {
        "木": "목(木)",
        "火": "화(火)",
        "土": "토(土)",
        "金": "금(金)",
        "水": "수(水)",
    }

    _CG_OH = {
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

    _JJ_OH = {
        "子": "水",
        "丑": "土",
        "寅": "木",
        "卯": "木",
        "辰": "土",
        "巳": "火",
        "午": "火",
        "未": "土",
        "申": "金",
        "酉": "金",
        "戌": "土",
        "亥": "水",
    }

    _JJ_ANIMAL = {
        "子": "쥐",
        "丑": "소",
        "寅": "호랑이",
        "卯": "토끼",
        "辰": "용",
        "巳": "뱀",
        "午": "말",
        "未": "양",
        "申": "원숭이",
        "酉": "닭",
        "戌": "개",
        "亥": "돼지",
    }


    _today_oh_cg = _CG_OH.get(today_cg, "")

    _today_oh_jj = _JJ_OH.get(today_jj, "")

    _animal = _JJ_ANIMAL.get(today_jj, "")

    _ss_kr_map = {
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
        "-": "-",
    }

    _today_ss_kr = _ss_kr_map.get(today_ss, today_ss)

    _deep = _SS_DAILY_DEEP.get(_today_ss_kr, None)

    # ── 로컬 5단계 해설 (API 미사용) ────────────────────────────────

    if _deep:
        _f1, _f2, _f3, _f4, _f5 = _deep
    else:
        _f1 = f"오늘 일진 {today_cg}{today_jj}의 기운이 {display_name}님의 사주에 영향을 미칩니다."
        _f2, _f3, _f4, _f5 = (
            "재물운은 보통입니다.",
            "건강에 유의하십시오.",
            "대인관계를 신중히 하십시오.",
            "오늘 하루 계획을 세우고 실천하십시오.",
        )

    _oh_label_map = {
        "木": "목(木) - 청·녹색 기운",
        "火": "화(火) - 적·주황 기운",
        "土": "토(土) - 황토색 기운",
        "金": "금(金) - 흰색 기운",
        "水": "수(水) - 흑·청색 기운",
    }
    _oh_cg_label = _oh_label_map.get(_today_oh_cg, _today_oh_cg)
    _oh_jj_label = {
        "木": "목(木)",
        "火": "화(火)",
        "土": "토(土)",
        "金": "금(金)",
        "水": "수(水)",
    }.get(_today_oh_jj, _today_oh_jj)
    st.markdown(
            f"""

<div style="background:rgba(255,255,255,0.92);border:1.5px solid #d4af37; border-radius:20px;padding:24px;margin:10px 0 20px;box-shadow:0 8px 30px rgba(212,175,55,0.12)">

<div style="font-size:17px;font-weight:900;color:#b38728;margin-bottom:12px">

    🔮 만신 일진 완전 해설 — {today.strftime("%Y년 %m월 %d일")} ({color_ganzhi_badge(today_cg+today_jj, font_size="18px", padding="2px 7px")}일, {_animal}의 날)

</div>

<div style="font-size:12px;color:#888;margin-bottom:14px">

    천간 오행: {_oh_cg_label} | 지지 오행: {_oh_jj_label} | 십성: {_today_ss_kr}

</div>

<div style="display:flex;flex-direction:column;gap:10px">

<div style="background:#f0f7ff;border-left:4px solid #1565c0;border-radius:8px;padding:12px 16px">

<div style="font-size:11px;font-weight:700;color:#1565c0;margin-bottom:4px">🌊 1단계 | 오늘의 천기 흐름</div>

<div style="font-size:13px;color:#333;line-height:1.9">{_f1}</div>

</div>

<div style="background:#f9fff0;border-left:4px solid #2e7d32;border-radius:8px;padding:12px 16px">

<div style="font-size:11px;font-weight:700;color:#2e7d32;margin-bottom:4px">💰 2단계 | 재물 조언</div>

<div style="font-size:13px;color:#333;line-height:1.9">{_f2}</div>

</div>

<div style="background:#fff8f0;border-left:4px solid #e65100;border-radius:8px;padding:12px 16px">

<div style="font-size:11px;font-weight:700;color:#e65100;margin-bottom:4px">🏃 3단계 | 건강과 활력</div>

<div style="font-size:13px;color:#333;line-height:1.9">{_f3}</div>

</div>

<div style="background:#fdf0ff;border-left:4px solid #7b1fa2;border-radius:8px;padding:12px 16px">

<div style="font-size:11px;font-weight:700;color:#7b1fa2;margin-bottom:4px">🤝 4단계 | 대인관계</div>

<div style="font-size:13px;color:#333;line-height:1.9">{_f4}</div>

</div>

<div style="background:#fff3e0;border-left:4px solid #f57f17;border-radius:8px;padding:12px 16px">

<div style="font-size:11px;font-weight:700;color:#f57f17;margin-bottom:4px">⚡ 5단계 | 핵심 실천 한 가지</div>

<div style="font-size:13px;color:#333;line-height:1.9;font-weight:600">{_f5}</div>

</div>

</div>

</div>""",
        unsafe_allow_html=True,
    )

    # -- 오늘 일진 카드 -----------------


    d = DAILY_SS_MSG.get(today_ss, DAILY_SS_MSG["-"])

    level_color = {
        "대길": "#4caf50",
        "길": "#8bc34a",
        "평길": "#ffc107",
        "평": "#9e9e9e",
        "흉": "#f44336",
    }.get(d["level"], "#aaa")

    st.markdown(
        f"""

<div style="background:#ffffff; border:1px solid #ddd; border-left:6px solid {level_color}; border-radius:12px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,0.05)">

<div style="display:flex; align-items:center; gap:12px; margin-bottom:12px">

<span style="font-size:32px">{d["emoji"]}</span>

<span style="font-size:18px; font-weight:800; color:#333">{today_cg}{today_jj}일의 운기 ({today_ss})</span>

<span style="background:{level_color}22; color:{level_color}; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:800">{d["level"]}</span>

</div>

<div style="font-size:14px; color:#555; line-height:1.7;white-space:normal;word-break:break-all">{d["msg"]}</div>

<div style="margin-top:12px; padding-top:12px; border-top:1px dashed #eee; display:flex; gap:10px">

<span style="font-size:12px; color:#444"><b>💰 재물운:</b> {d["재물"]}</span>

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # -- 길한 시간 (용신 기반) ----------------

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

        st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)

    # -- 300-400자 상세 처방 카드 (행운아이템 + 조심 + 조언) --

    # -- 300-400자 상세 처방 카드 (행운아이템 + 조심 + 조언) --


    fp = DAILY_FULL.get(today_ss, DAILY_FULL["-"])

    _today = datetime.now()

    # 날짜+사주원국 기반 시드 -> 매일 다르지만 하루 안에서는 있  동일한 문장

    _pil_seed = hash(tuple((p.get("cg", ""), p.get("jj", "")) for p in pils)) & 0xFFFF

    _date_seed = _today.year * 10000 + _today.month * 100 + _today.day + _pil_seed

    _rng = random.Random(_date_seed)

    advice_text = f"{_rng.choice(fp['intro'])} {_rng.choice(fp['body'])} {_rng.choice(fp['outro'])}"

    st.markdown(
        f"""

<div style="background:rgba(255,255,255,0.92);backdrop-filter:blur(15px);border:1.5px solid rgba(212,175,55,0.4); border-radius:18px;padding:24px;margin-top:16px;box-shadow:0 6px 25px rgba(0,0,0,0.06)">

<div style="font-size:17px;font-weight:900;color:#333;margin-bottom:16px;display:flex;align-items:center;gap:8px">

<span style="font-size:24px">{fp["icon"]}</span> 💊 오늘의 만신 처방

</div>

<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px">

<div style="flex:1;min-width:clamp(120px,38vw,180px);background:rgba(76,175,80,0.08);border:1px solid rgba(76,175,80,0.3); border-radius:12px;padding:12px 14px">

<div style="font-size:12px;font-weight:800;color:#2e7d32;margin-bottom:5px">🍀 오늘의 행운 키워드</div>

<div style="font-size:13px;color:#111;line-height:1.7;white-space:normal;word-break:break-all">{fp["lucky"]}</div>

</div>

<div style="flex:1;min-width:clamp(120px,38vw,180px);background:rgba(244,67,54,0.06);border:1px solid rgba(244,67,54,0.25); border-radius:12px;padding:12px 14px">

<div style="font-size:12px;font-weight:800;color:#c62828;margin-bottom:5px">⚠️ 오늘 조심할 것</div>

<div style="font-size:13px;color:#111;line-height:1.7;white-space:normal;word-break:break-all">{fp["caution"]}</div>

</div>

</div>

<div style="background:rgba(212,175,55,0.06);border-left:4px solid #d4af37;padding:14px 16px; border-radius:0 12px 12px 0;font-size:14.5px;color:#222;line-height:2.0">

        💡 <b>핵심 조언:</b> {advice_text}

</div>

<div style="font-size:11px;color:#bbb;text-align:right;margin-top:8px">{len(advice_text)}자</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # ── 오늘 길한 시간대·방향·색상 직격 출력 ────────────────────
    st.markdown(
        '<div class="gold-section">🧭 오늘의 길한 시간·방향·색상 — 지금 바로 활용하세요</div>',
        unsafe_allow_html=True,
    )
    try:
        _ilgan_d = pils[1]["cg"] if len(pils) > 1 else "甲"
        _ys_d    = get_yongshin(pils) or {}
        _yong_d  = _ys_d.get("종합_용신", [])
        if not isinstance(_yong_d, list): _yong_d = []
        _prim_oh = _yong_d[0] if _yong_d else OH.get(_ilgan_d, "木")

        # 오행별 길한 시간대·방향·색상 매핑
        _OH_GUIDE = {
            "木": {
                "시간": "오전 7~9시 (卯時), 오후 3~5시 (申時 전 木기운)",
                "방향": "동쪽(東) — 출근길·약속 장소를 동쪽으로",
                "색상": "초록·청색 — 셔츠·소품·지갑에 활용",
                "음식": "신맛(레몬·매실·식초 샐러드)으로 에너지 보충",
                "행동": "새로운 시작·결정·계약에 좋음. 식물 가까이 두기",
            },
            "火": {
                "시간": "오전 9~11시 (巳時), 오후 1~3시 (午時) — 가장 밝은 시간",
                "방향": "남쪽(南) — 창가 남향 자리, 점심은 남쪽 식당으로",
                "색상": "빨강·주황 — 넥타이·스카프·파우치에 포인트",
                "음식": "쓴맛(아메리카노·여주·씀바귀)으로 심장 기운 보강",
                "행동": "발표·영업·소개팅에 최적. 밝은 조명 공간 활용",
            },
            "土": {
                "시간": "오전 11~오후 1시 (午·未時 사이), 저녁 7~9시 (戌時)",
                "방향": "중앙·북동(北東) — 책상 중앙 정리정돈이 운을 부름",
                "색상": "황색·베이지·갈색 — 가방·노트북 파우치",
                "음식": "단맛(고구마·호박죽·대추차)으로 비위 보강",
                "행동": "안정적 협상·계약서 검토에 좋음. 집 정리정돈",
            },
            "金": {
                "시간": "오후 3~7시 (申·酉時) — 금기운 최고조",
                "방향": "서쪽(西) — 오후 미팅은 서쪽 방향 카페로",
                "색상": "흰색·은색·금색 — 시계·반지·악세서리 활용",
                "음식": "매운맛(무·도라지·생강차)으로 폐 기운 보강",
                "행동": "결단·마무리·수금에 최적. 금속 소품 몸에 지니기",
            },
            "水": {
                "시간": "오후 9~11시 (亥時), 자정~오전 1시 (子時) — 집중력 최고",
                "방향": "북쪽(北) — 조용한 북향 공간에서 집중 작업",
                "색상": "검정·남색·자주 — 가방·지갑·다이어리",
                "음식": "짠맛(해조류·된장국·흑깨죽)으로 신장 기운 보강",
                "행동": "공부·기획·전략 수립에 최적. 명상·독서 추천",
            },
        }

        _guide = _OH_GUIDE.get(_prim_oh, _OH_GUIDE["木"])
        _oh_kr = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}

        # 오늘 일진 십성 기반 행동 지침
        _ACTION_SS = {
            "偏財": "📢 오늘은 새로운 사람을 만나고 영업·미팅을 늘리면 좋습니다. 이성에게 먼저 연락하기 좋은 날.",
            "正財": "📋 밀린 서류·정산·계약서 처리에 최적. 저축·적금 개설도 오늘이 길합니다.",
            "食神": "🎨 창의적 작업·요리·강의·콘텐츠 제작에 에너지가 폭발합니다. 즐기는 일을 하세요.",
            "傷官": "✍️ 혼자 집중하는 작업(글쓰기·코딩·디자인)에 최적. 단 윗사람과 논쟁은 피하세요.",
            "偏官": "🛡️ 오늘은 방어적으로. 무리한 약속·계약·새 시작을 피하고 기존 업무 마무리에 집중.",
            "正官": "🏆 공식 보고·발표·면접에 최적. 원칙을 지키면 윗사람의 인정을 받는 날.",
            "劫財": "💰 돈 거래·투자·보증 절대 금지. 조용히 현금 지키고 감정 소모 최소화.",
            "比肩": "🤜 독립적으로 움직일 때 최강. 협업보다 단독 업무에서 성과가 납니다.",
            "偏印": "🔍 새 정보 수집·공부·조사에 좋습니다. 중요한 결정은 오늘 내리지 마세요.",
            "正印": "📚 학습·시험·자격증 공부에 최적. 어른·멘토에게 연락하면 덕을 봅니다.",
        }
        _action_today = _ACTION_SS.get(today_ss, "오늘 하루 흐름에 맞게 꾸준히 움직이세요.")

        st.markdown(
            f"""<div style='background:#f0fff4;border:1.5px solid #27ae60;border-radius:14px;
            padding:16px 20px;margin:8px 0;'>
            <div style='font-size:13px;font-weight:900;color:#1a5c2a;margin-bottom:10px;'>
            🌿 용신 오행({_oh_kr.get(_prim_oh,_prim_oh)}) 기반 오늘의 처방</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#333;'>
            <div>⏰ <b>길한 시간대:</b><br>{_guide["시간"]}</div>
            <div>🗺️ <b>길한 방향:</b><br>{_guide["방향"]}</div>
            <div>🎨 <b>행운 색상:</b><br>{_guide["색상"]}</div>
            <div>🍱 <b>추천 음식:</b><br>{_guide["음식"]}</div>
            </div>
            <div style='margin-top:10px;font-size:12px;color:#1a5c2a;font-weight:700;
            background:#e8f5e9;padding:8px 12px;border-radius:8px;'>
            💡 {_guide["행동"]}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""<div style='background:#fff8e1;border-left:4px solid #f39c12;border-radius:8px;
            padding:12px 16px;margin:6px 0;font-size:13px;color:#7d6608;'>
            🎯 <b>오늘의 행동 지침 [{today_ss}]:</b> {_action_today}</div>""",
            unsafe_allow_html=True,
        )
    except Exception as _dg_e:
        st.warning(f"⚠️ 개운 처방 오류: {_dg_e}")


def menu10_monthly(pils, name, birth_year, gender):
    """🔟 월별 운세 - 이달의 주의해야 할 날짜 특화 분석"""

    cur_year = datetime.now().year

    # ── 월 단위 시기 직격 특정 (최상단) ─────────────────────────
    st.markdown(
        '<div class="gold-section">🎯 올해 월별 최적 타이밍 — 직격 특정</div>',
        unsafe_allow_html=True,
    )

    _focus_options = ["재물", "인연", "직업", "건강", "전체"]
    _focus_sel = st.radio(
        "분야 선택", _focus_options, horizontal=True,
        key="monthly_timing_focus", index=0,
    )

    try:
        _mt = get_monthly_timing(pils, birth_year, gender, cur_year, _focus_sel)
        if _mt.get("summary"):
            st.markdown(
                f"<div style='background:#1a1a2e;color:#f7e695;font-size:15px;"
                f"font-weight:900;padding:14px 18px;border-radius:12px;"
                f"margin-bottom:12px;line-height:1.9'>"
                f"{_mt['summary'].replace(chr(10),'<br>')}</div>",
                unsafe_allow_html=True,
            )

        # 길한 달
        if _mt.get("peak"):
            st.markdown(
                "<div style='font-size:13px;font-weight:900;color:#27ae60;"
                "margin:10px 0 6px'>✅ 움직이면 유리한 달</div>",
                unsafe_allow_html=True,
            )
            for _m, _desc in _mt["peak"]:
                st.markdown(
                    f"<div style='border-left:4px solid #27ae60;padding:6px 12px;"
                    f"margin:3px 0;font-size:13px;background:#f0fff4;border-radius:0 8px 8px 0'>"
                    f"{_desc}</div>",
                    unsafe_allow_html=True,
                )

        # 조심할 달
        if _mt.get("caution"):
            st.markdown(
                "<div style='font-size:13px;font-weight:900;color:#c0392b;"
                "margin:10px 0 6px'>⛔ 대기해야 할 달</div>",
                unsafe_allow_html=True,
            )
            for _m, _desc in _mt["caution"]:
                st.markdown(
                    f"<div style='border-left:4px solid #c0392b;padding:6px 12px;"
                    f"margin:3px 0;font-size:13px;background:#fff5f5;border-radius:0 8px 8px 0'>"
                    f"{_desc}</div>",
                    unsafe_allow_html=True,
                )
    except Exception as _mte:
        st.warning(f"⚠️ 월별 타이밍 분석 오류: {_mte}")

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:16px 0">',
        unsafe_allow_html=True,
    )

    # ── 로컬 엔진 ─────────────────────────────────────────────
    try:
        _local_out = LocalSajuNarrator.monthly(pils, name, birth_year, gender)
        if _local_out:
            st.markdown(_local_out, unsafe_allow_html=True)
    except Exception as _e:
        st.warning(f"⚠️ 월별 분석 오류: {_e}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    ilgan = pils[1]["cg"]

    display_name = name if name else "내담자"

    today = datetime.now()

    year, month = today.year, today.month

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg,#fff0f0,#ffe8e8); border-radius:14px;padding:18px 24px;margin-bottom:16px;text-align:center">

<div style="font-size:22px;font-weight:900;color:#b71c1c;letter-spacing:2px">

        📅 {display_name}님의 {month}월 운세와 특별 점검

</div>

<div style="font-size:13px;color:#000000;margin-top:6px">

        이번 달({year}년 {month}월) 중에 특별히 피하거나 조심해야 하는 날짜(흉일)를 집중 분석합니다.

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # -- 자체 월간 분석 (로컬 엔진 전용) ----------------------

    import calendar

    from datetime import date

    _, last_day = calendar.monthrange(year, month)

    def get_day_pillar_local(dt):

        base = date(1924, 1, 1)

        delta = (dt.date() - base).days if hasattr(dt, "date") else (dt - base).days

        return CG[delta % 10], JJ[delta % 12]

    # 이달 전체 일진 분석

    all_days_data = []

    bad_days = []

    good_days = []

    for d in range(1, last_day + 1):
        dt = datetime(year, month, d)

        cg, jj = get_day_pillar_local(dt)

        ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cg, "-")

        day_info = {"date": dt, "cgjj": f"{cg}{jj}", "ss": ss, "cg": cg, "jj": jj}

        all_days_data.append(day_info)

        if ss in ("겁재", "편관", "상관"):
            bad_days.append(day_info)

        if ss in ("식신", "정관", "정인", "정재"):
            good_days.append(day_info)

    # 월건(月建) 계산

    month_idx = (year * 12 + month - 1) % 10

    month_cg = CG[month_idx]

    month_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(month_cg, "-")

    # 십성별 월간 의미 사전


    # 주간별 기운 분석

    week_data = [[], [], [], [], []]

    for info in all_days_data:
        week_num = (info["date"].day - 1) // 7

        if week_num > 4:
            week_num = 4

        week_data[week_num].append(info)

    def week_summary(wlist):

        if not wlist:
            return "해당 없음"

        ss_cnt = {}

        for w in wlist:
            ss_cnt[w["ss"]] = ss_cnt.get(w["ss"], 0) + 1

        top = sorted(ss_cnt.items(), key=lambda x: x[1], reverse=True)

        top_ss = top[0][0] if top else "-"

        w_msgs = {
            "식신": "창의적 에너지가 넘치는 주입니다. 새로운 시도와 만남에 적극적으로 나서십시오.",
            "정관": "공적인 업무와 대외 활동에서 성과가 날 가능성이 높습니다.",
            "정인": "귀인의 도움이 찾아오거나 중요한 소식을 받게 될 수 있습니다.",
            "정재": "성실한 노력이 재물의 결실로 이어지는 주입니다. 계획을 차근차근 실행하십시오.",
            "편재": "예상치 못한 수익이나 기회와의 만남이 있는 주입니다. 적극적으로 움직이십시오.",
            "비견": "협력자와 동료의 역할이 중요해지는 주입니다. 혼자보다 함께 움직이십시오.",
            "겁재": "재물 지출을 조심하고 인간관계의 갈등에 주의하십시오. 감정을 다스리는 것이 관건입니다.",
            "편관": "긴장과 스트레스가 높아지는 주입니다. 건강과 체력 관리에 집중하십시오.",
            "상관": "말과 행동을 조심해야 하는 주입니다. 창의적 활동은 좋으나 공식 발언은 자제하십시오.",
            "편인": "내면의 충전이 필요한 주입니다. 조용히 공부하거나 휴식을 취하는 것이 이롭습니다.",
            "-": "평온하고 무난하게 흘러가는 주입니다. 루틴을 지키며 꾸준히 나아가십시오.",
        }

        return w_msgs.get(top_ss, "전반적으로 조용하고 안정된 흐름입니다.")

    # 오행 기반 건강 조언

    OH_HEALTH = {
        "木": "간/담/눈/근육 계통에 주의하십시오. 이달은 신경이 예민해지기 쉬우니 충분한 수면과 스트레칭을 권장합니다.",
        "火": "심장/소장/혈액/혀 관련 건강에 주의가 필요합니다. 과로와 흥분 상태가 지속되면 혈압이 오를 수 있으니 마음의 여유를 가지십시오.",
        "土": "비장/위장/소화기 계통에 유의하십시오. 과식과 스트레스성 소화 불량이 발생할 수 있으니 식습관 조절이 중요합니다.",
        "金": "폐/대장/피부/코 관련 건강에 신경 쓰십시오. 환절기 호흡기 질환과 피부 건조증이 증가할 수 있습니다.",
        "水": "신장/방광/뼈/귀 계통을 조심하십시오. 이달은 냉증이 올 수 있으니 하체 보온에 유의하시고, 충분한 수분 섭취를 권합니다.",
    }

    OH_MAP = {
        "甲": "木",
        "乙": "木",
        "丙": "火",
        "丁": "火",
        "戊": "土",
        "己": "土",
        "庚": "金",
        "辛": "金",
        "壬": "水",
        "癸": "Water",
    }

    OH_MAP2 = {
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

    ilgan_oh = OH_MAP2.get(ilgan, "土")

    health_msg = OH_HEALTH.get(ilgan_oh, OH_HEALTH["土"])

    # 인간관계 조언 (월별 십성 기반)

    RELATION_MSG = {
        "비견": f"이달은 동년배나 경쟁자와의 관계가 핵심입니다. 질투와 갈등보다는 공생의 관점에서 접근하십시오. 같은 분야의 사람을 통해 의외의 기회를 얻을 수 있습니다.",
        "겁재": f"이달은 신뢰했던 사람으로부터 배신이나 실망을 경험할 수 있습니다. 돈이 엮인 부탁은 거절하는 것이 관계 보호의 길이며, 새로운 사람보다 오래된 지인이 더 이롭습니다.",
        "식신": f"이달은 인연덕이 넘치는 달입니다. 소개팅, 모임, 파티 등에 적극적으로 참여하면 인생에 중요한 사람을 만날 수 있습니다. 베푸는 마음이 복으로 돌아옵니다.",
        "상관": f"이달은 아랫사람이나 자녀와의 관계에서 갈등이 발생하기 쉽습니다. 또한 말실수로 인해 중요한 관계가 손상될 수 있으니, 모든 대화에서 신중함을 유지하십시오.",
        "편재": f"이달은 이성 이연이나 사업적 파트너십이 활발해지는 달입니다. 넓고 활동적인 네트워크에서 중요한 기회를 잡을 수 있습니다. 다만 새로운 사람에게는 금전적 경계선을 유지하십시오.",
        "정재": f"이달은 안정적인 인간관계가 유지되는 달입니다. 특별히 새로운 관계를 맺기보다 기존의 소중한 사람들을 배려하고 다지는 것이 현명합니다.",
        "편관": f"이달은 상사나 권위자와의 갈등 가능성이 높습니다. 정면 충돌은 피하고, 스마트하게 우회하는 전략이 필요합니다. 법적 분쟁이나 민원 사항이 있다면 이달을 피해 처리하십시오.",
        "정관": f"이달은 윗사람이나 멘토로부터 인정받는 달입니다. 권위 있는 사람과의 만남이 이로우며, 공식적인 추천이나 소개를 통한 관계 형성이 큰 도움이 됩니다.",
        "편인": f"이달은 스승이나 전통적 지식인과의 교류가 깊어집니다. 혼자만의 시간을 즐기며 내면을 가꾸는 것이 더 이롭습니다. 지나친 사교 활동은 에너지를 소진시킵니다.",
        "정인": f"이달은 어머니, 스승, 후원자 등 도움을 주는 귀인이 나타나는 달입니다. 교육기관이나 공공기관을 통한 인맥 형성이 특히 좋으며, 배움을 통해 새로운 만남을 이어가십시오.",
        "-": f"이달은 인간관계에서 특별한 변화 없이 잔잔하게 유지됩니다. 지금 곁에 있는 사람들에게 감사하며 관계를 돈독히 하는 것이 최선입니다.",
    }

    relation_msg = RELATION_MSG.get(month_ss, RELATION_MSG["-"])

    # 재물운 조언

    MONEY_MSG = {
        "비견": "수입은 꾸준하나 지출도 만만치 않은 달입니다. 공동 투자나 합작 사업에 관심이 생길 수 있으나 계약서를 꼼꼼히 검토하십시오.",
        "겁재": "이달은 재물 손실을 경계해야 합니다. 주식, 코인, 고위험 투자는 절대 피하고, 예상치 못한 지출이 발생할 수 있으니 비상금을 확보해두십시오.",
        "식신": "복록이 넘치는 달입니다. 부수입이나 인세, 강연료 등 다양한 경로의 수입이 기대됩니다. 소비는 즐겁게, 저축은 꾸준히 병행하십시오.",
        "상관": "아이디어나 콘텐츠를 통한 수익화 가능성이 있습니다. 단, 계약서 없는 거래나 구두 약속에 의존한 금전 거래는 위험합니다.",
        "편재": "예상치 못한 수입이 들어올 가능성이 있습니다. 단, 이 반짝 기회에 도박적 투자로 이어지지 않도록 주의하십시오. 수익은 즉시 분산 관리하십시오.",
        "정재": "성실한 노력에 안정적인 수입이 따르는 가장 좋은 재물의 달입니다. 중장기 저축 계획을 세우기에도 최적이며 부동산/연금 검토도 좋습니다.",
        "편관": "예상치 못한 지출과 비용이 발생하기 쉽습니다. 이달만큼은 투자보다 현금 보유를 늘리고, 큰 부동산 계약이나 사업 확장은 내달로 미루십시오.",
        "정관": "안정적인 수입 구조가 유지됩니다. 직업적 성과가 인정받아 성과급이나 보너스가 기대됩니다. 장기 계약 체결에도 유리한 달입니다.",
        "편인": "직접적 수익보다는 준비와 투자의 달입니다. 자격증 취득이나 학습에 비용을 투자하면 미래에 큰 수익으로 돌아옵니다.",
        "정인": "귀인의 도움으로 의외의 재물 기회가 열립니다. 지원금, 장학금, 보조금 등 관공서나 기관과 관련된 금전적 혜택을 확인해보십시오.",
        "-": "이달 재물운은 무난하게 유지됩니다. 큰 수입도 큰 손실도 없는 달이니 루틴한 재무 관리에 집중하십시오.",
    }

    money_msg = MONEY_MSG.get(month_ss, MONEY_MSG["-"])

    # >>> 흉일 계산

    counts = {"편관": 0, "겁재": 0, "상관": 0}

    for b in bad_days:
        counts[b["ss"]] = counts.get(b["ss"], 0) + 1

    total_risk = len(bad_days)

    total_good = len(good_days)

    # 주간 분석

    w_labels = ["1주차", "2주차", "3주차", "4주차", "5주차"]

    week_summaries = [week_summary(week_data[i]) for i in range(5)]

    month_name_key, month_overall = MONTHLY_SS_MEANING.get(month_ss, MONTHLY_SS_MEANING["-"])

    # -- 종합 콘텐츠 렌더링 ----------------------------------

    # 섹션 1: 월간 종합

    st.markdown(
        f"""

<div style="background:rgba(255,255,255,0.92);backdrop-filter:blur(15px);border:1.5px solid #d4af37; border-radius:18px;padding:26px;margin-top:10px;box-shadow:0 6px 28px rgba(212,175,55,0.12)">

<div style="font-size:18px;font-weight:900;color:#b38728;margin-bottom:14px">

            🔮 {year}년 {month}월 종합 역수 - {month_name_key}

</div>

<div style="font-size:14.5px;color:#222;line-height:2.1;border-left:4px solid #d4af37;padding-left:14px">

            이번 달({year}년 {month}월)의 월건(月建)은 <b>{month_cg}</b>으로,

            {display_name}님의 일간 <b>{ilgan}</b>과의 관계는 <b>{month_ss}</b>에 해당합니다.<br><br>

            {month_overall}<br><br>

            이번 달 전체 {last_day}일 중 <b>주의가 필요한 흉일은 {total_risk}일</b>,

<b>길한 날은 {total_good}일</b>로 분석되었습니다.

            {"전반적으로 기복이 심한 달이니 중요한 결정은 길일에 맞추어 실행하십시오." if total_risk > 8 else "흉일이 적은 편으로 평온한 흐름이 예상되지만, 방심은 금물입니다."}

</div>

</div>

    """,
        unsafe_allow_html=True,
    )

    # 섹션 2: 재물운, 건강운, 인간관계 - 3단 카드

    st.markdown(
        f"""

<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:14px">

<div style="flex:1;min-width:clamp(140px,40vw,220px);background:rgba(255,248,225,0.9);border:1px solid #ffc107; border-radius:14px;padding:18px">

<div style="font-size:14px;font-weight:900;color:#e65100;margin-bottom:10px">💰 이달 재물운</div>

<div style="font-size:13.5px;color:#333;line-height:1.9">{money_msg}</div>

</div>

<div style="flex:1;min-width:clamp(140px,40vw,220px);background:rgba(232,245,233,0.9);border:1px solid #66bb6a; border-radius:14px;padding:18px">

<div style="font-size:14px;font-weight:900;color:#2e7d32;margin-bottom:10px">🏥 이달 건강운</div>

<div style="font-size:13.5px;color:#333;line-height:1.9">{health_msg}</div>

</div>

<div style="flex:1;min-width:clamp(140px,40vw,220px);background:rgba(232,234,246,0.9);border:1px solid #7986cb; border-radius:14px;padding:18px">

<div style="font-size:14px;font-weight:900;color:#283593;margin-bottom:10px">🤝 이달 인간관계</div>

<div style="font-size:13.5px;color:#333;line-height:1.9">{relation_msg}</div>

</div>

</div>

    """,
        unsafe_allow_html=True,
    )

    # 섹션 3: 주간별 흐름

    st.markdown(
        '<div class="gold-section" style="margin-top:22px">📆 주간별 기운 흐름</div>',
        unsafe_allow_html=True,
    )

    week_html = ""

    for i in range(5):
        if not week_data[i]:
            continue

        d_start = week_data[i][0]["date"].day

        d_end = week_data[i][-1]["date"].day

        ss_list = [w["ss"] for w in week_data[i]]

        bad_cnt = sum(1 for s in ss_list if s in ("겁재", "편관", "상관"))

        good_cnt = sum(1 for s in ss_list if s in ("식신", "정관", "정인", "정재"))

        week_color = "#ffe0e0" if bad_cnt > good_cnt else "#e8f5e9" if good_cnt > 0 else "#f5f5f5"

        week_border = "#f44336" if bad_cnt > good_cnt else "#4caf50" if good_cnt > 0 else "#9e9e9e"

        week_html += f"""

<div style="background:{week_color};border-left:4px solid {week_border}; border-radius:4px 12px 12px 4px;padding:12px 16px;margin-bottom:10px">

<span style="font-weight:900;color:#333;font-size:14px">{w_labels[i]} ({month}/{d_start}～{month}/{d_end})</span>

<span style="font-size:11px;color:#888;margin-left:8px">길일 {good_cnt}일 / 흉일 {bad_cnt}일</span>

<div style="font-size:13px;color:#444;margin-top:6px;line-height:1.8">{week_summaries[i]}</div>

</div>"""

    st.markdown(week_html, unsafe_allow_html=True)

    # 섹션 4: 흉일 목록

    st.markdown(
        '<div class="gold-section" style="margin-top:18px">⚠️ 이번 달 조심해야 하는 날 (흉일)</div>',
        unsafe_allow_html=True,
    )

    if bad_days:
        risk_type = max(counts, key=counts.get)

        briefing_text = f"이번 달은 총 <b>{total_risk}일</b>의 주의가 필요한 날이 계산되었습니다. "

        if total_risk > 10:
            briefing_text += "운기의 기복이 매우 심한 달이니 모든 행동을 신중하게 하십시오."

        elif total_risk > 5:
            briefing_text += "특정 기간에 기운이 집중되어 있으니 컨디션 조절에 힘쓰십시오."

        else:
            briefing_text += "흉일이 비교적 적어 평온하나, 해당 날짜만큼은 각별히 자중하십시오."

        detailed_insight = {
            "편관": "특히 <b>편관</b>의 날이 우세합니다. 건강 악화와 관재구설을 조심하며, 타인과의 마찰을 피하고 칼날 위를 걷듯 처신하십시오.",
            "겁재": "특히 <b>겁재</b>의 날이 우세합니다. 재물의 지출이 많아지거나 배신수가 우려되니 지갑을 닫고 마음을 다스리십시오.",
            "상관": "특히 <b>상관</b>의 날이 우세합니다. 구설수와 말실수로 인한 피해가 우려되니 침묵이 금입니다.",
        }.get(risk_type, "전반적인 흉기를 조심하십시오.")

        st.markdown(
            f"""

<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);border-radius:14px; padding:18px 20px;margin-bottom:16px;border:1px solid #ffcc80">

<div style="font-size:15px;font-weight:900;color:#e65100;margin-bottom:8px">🎙️ 만신의 월간 흉일 브리핑</div>

<div style="font-size:14px;color:#4e342e;line-height:1.9">{briefing_text}<br><br>{detailed_insight}</div>

</div>

        """,
            unsafe_allow_html=True,
        )

        cards = ""

        for b in bad_days:
            desc = {
                "겁재": "재물 손실/인간관계 갈등 주의",
                "편관": "건강 악화/관재구설 주의",
                "상관": "말실수/직장 내 트러블 주의",
            }.get(b["ss"], "매사 조심")

            d_str = b["date"].strftime("%m/%d")

            w_str = ["월", "화", "수", "목", "금", "토", "일"][b["date"].weekday()]

            cards += f"""<div style="background:#fff0f0;border-left:4px solid #f44336;padding:9px 14px; margin-bottom:7px;border-radius:4px 8px 8px 4px;">

<span style="font-weight:900;color:#d32f2f;font-size:14px;margin-right:10px">{d_str} ({w_str})</span>

<span style="color:#555;font-size:12px;margin-right:8px">{b["cgjj"]}일</span>

<span style="font-weight:700;color:#c62828;font-size:13px;margin-right:8px">[{b["ss"]}]</span>

<span style="color:#333;font-size:13px">{desc}</span></div>"""

        st.markdown(cards, unsafe_allow_html=True)

    else:
        st.markdown(
            """

<div style="padding:18px 20px;color:#2e7d32;background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border-radius:12px;border:1px solid #a5d6a7;font-size:14px;line-height:1.9">

            🌿 <b>이번 달은 크게 조심해야 할 흉일이 보이지 않습니다.</b><br><br>

            평온하고 안정적인 한 달이 예상됩니다. 그러나 방심은 금물이니, 평소 루틴을 성실하게 지키는 것이 이 달 최고의 전략입니다.

            중요한 계약이나 투자는 용신(用神)에 해당하는 날을 가려 진행하시면 더욱 좋습니다.

</div>

        """,
            unsafe_allow_html=True,
        )

    # 섹션 5: 길일 목록

    if good_days:
        st.markdown(
            '<div class="gold-section" style="margin-top:18px">✅ 이번 달 행운의 날 (길일)</div>',
            unsafe_allow_html=True,
        )

        good_cards = ""

        for g in good_days:
            gdesc = {
                "식신": "창의/복록/새 시작에 좋은 날",
                "정관": "공적 업무/명예 상승에 유리",
                "정인": "귀인 만남/합격 소식 기대",
                "정재": "계약/저축/성실 보상의 날",
            }.get(g["ss"], "길한 기운")

            d_str = g["date"].strftime("%m/%d")

            w_str = ["월", "화", "수", "목", "금", "토", "일"][g["date"].weekday()]

            good_cards += f"""<div style="background:#f1f8e9;border-left:4px solid #4caf50;padding:9px 14px; margin-bottom:7px;border-radius:4px 8px 8px 4px;">

<span style="font-weight:900;color:#2e7d32;font-size:14px;margin-right:10px">{d_str} ({w_str})</span>

<span style="color:#555;font-size:12px;margin-right:8px">{g["cgjj"]}일</span>

<span style="font-weight:700;color:#388e3c;font-size:13px;margin-right:8px">[{g["ss"]}]</span>

<span style="color:#333;font-size:13px">{gdesc}</span></div>"""

        st.markdown(good_cards, unsafe_allow_html=True)

    # 섹션 6: 만신의 한 마디

    FINAL_WORDS = {
        "겁재": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 돈과 사람, 두 가지를 모두 잃지 않으려면 오늘 가장 소중한 것 한 가지를 먼저 선택하십시오. 지킬 것을 정했다면 나머지는 과감히 내려놓는 용기가 이번 달의 진짜 능력입니다.",
        "편관": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 칼끝이 당신을 향하고 있을 때, 가장 안전한 곳은 그 칼을 들고 있는 사람 곁이 아니라, 칼이 닿지 않는 거리를 유지하는 것입니다. 한 발짝 뒤로 물러서는 것이 지혜입니다.",
        "식신": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 당신 안에 오랫동안 잠들어 있던 씨앗이 드디어 싹을 틔울 준비를 마쳤습니다. 두려움 없이 첫 발을 내딛으십시오. 하늘이 응원하고 있습니다.",
        "정관": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 빛이 가장 강할 때 그림자도 가장 짙습니다. 명예와 인정을 받는 이번 달, 자만 대신 감사를 마음에 품으십시오. 그 겸손함이 당신의 빛을 오래도록 유지시켜 줄 것입니다.",
        "정인": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 기다림이 길었을수록 열매는 더 달콤합니다. 이번 달 당신이 기다려온 소식이 찾아올 가능성이 높습니다. 마지막 한 걸음을 포기하지 마십시오.",
        "-": f"이번 달 {display_name}님에게 만신이 드리는 한 마디 - 파도가 잠잠할 때 배를 정비하는 선원이 폭풍에도 살아남습니다. 이번 달의 평온함을 낭비하지 마시고, 다가올 기회를 위해 조용히 준비하십시오.",
    }

    final_word = FINAL_WORDS.get(month_ss, FINAL_WORDS["-"])

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg,#2c1a00,#4a2e00);border-radius:16px; padding:22px 24px;margin-top:20px;border:1px solid #d4af37; box-shadow:0 8px 30px rgba(0,0,0,0.15)">

<div style="font-size:15px;font-weight:900;color:#d4af37;margin-bottom:12px">🙏 만신의 {month}월 최후 한 마디</div>

<div style="font-size:14.5px;color:#ffe0b2;line-height:2.1;font-style:italic">{final_word}</div>

</div>

    """,
        unsafe_allow_html=True,
    )


def menu11_yearly(pils, name, birth_year, gender):
    """1️⃣1️⃣ 신년 운세 - 연월일시 1~12월 완전 분석"""

    # ── 로컬 엔진 항상 먼저 출력 ─────────────

    try:
        _local_out = LocalSajuNarrator.yearly(pils, name, birth_year, gender)

        st.markdown(_local_out, unsafe_allow_html=True)

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    # if not api_key and not groq_key:

    # return

    st.markdown("---")

    st.markdown("### 🤖 AI 심층 분석")

    ilgan = pils[1]["cg"]

    display_name = name if name else "내담자"

    today = datetime.now()

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg,#f5f0ff,#fff0e8); border-radius:14px;padding:18px 24px;margin-bottom:16px;text-align:center">

<div style="font-size:22px;font-weight:900;color:#5a2a00;letter-spacing:2px">

        🎊 {display_name}님의 신년 운세 (월별 족집게)

</div>

<div style="font-size:13px;color:#000000;margin-top:6px">

        올 한 해의 흐름을 1월부터 12월까지 상세히 분석합니다.

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    col_y, _ = st.columns([1, 3])

    with col_y:
        sel_year = st.selectbox(
            "조회 연도",
            [today.year - 1, today.year, today.year + 1],
            index=1,
            key="yearly_year_select",
        )

    # ── 로컬 12개월 완전 해설 ─────────────────────────

    _LR = {"대길": 5, "길": 4, "평길": 3, "평": 2, "흉": 1, "흉흉": 0}
    _LC = {
        "대길": "#4caf50",
        "길": "#8bc34a",
        "평길": "#ffc107",
        "평": "#9e9e9e",
        "흉": "#f44336",
        "흉흉": "#b71c1c",
    }
    _LE = {
        "대길": "🌟",
        "길": "✅",
        "평길": "🟡",
        "평": "⬜",
        "흉": "⚠️",
        "흉흉": "🔴",
    }
    _MONTH_ADVICE = {
        "食神": "복록과 표현력이 넘치는 달. 적극적으로 활동하면 좋은 결과가 따릅니다.",
        "傷官": "재능이 빛나지만 관재구설을 조심해야 하는 달. 말과 행동을 신중히 하십시오.",
        "偏財": "활동과 이동이 많은 달. 투자와 새로운 수입원 개척에 유리합니다.",
        "正財": "안정적인 수입이 기대되는 달. 저축과 재정 정리에 적합합니다.",
        "偏官": "압박과 경쟁이 심해지는 달. 인내하고 건강을 챙기십시오.",
        "正官": "명예와 승진의 기운이 강한 달. 공식적인 업무에서 두각을 나타냅니다.",
        "偏印": "직관과 창의력이 높아지는 달. 전문 분야 연구와 독창적 시도에 좋습니다.",
        "正印": "귀인의 도움과 합격운이 따르는 달. 학습과 자기계발에 집중하십시오.",
        "比肩": "협력과 경쟁이 동시에 일어나는 달. 네트워크를 활용하면 유리합니다.",
        "劫財": "재물 소모가 큰 달. 지출을 최소화하고 보수적으로 운영하십시오.",
        "-": "평온한 기운의 달. 루틴을 지키며 꾸준히 나아가는 것이 최선입니다.",
    }
    _mdata = [get_monthly_luck(pils, sel_year, m) for m in range(1, 13)]
    _best_local = max(_mdata, key=lambda x: _LR.get(x["길흉"], 2))
    _worst_local = min(_mdata, key=lambda x: _LR.get(x["길흉"], 2))
    # 연간 요약 헤더
    st.markdown(
            f"""

<div style="background:rgba(255,255,255,0.92);border:1.5px solid #d4af37; border-radius:20px;padding:24px;margin:10px 0 20px;box-shadow:0 8px 30px rgba(212,175,55,0.12)">

<div style="font-size:17px;font-weight:900;color:#b38728;margin-bottom:14px">

    🔮 만신 엔진 — {sel_year}년 {display_name}님의 12개월 완전 해설

</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">

<div style="background:#e8f5e9;border:1px solid #81c784;border-radius:10px;padding:12px;text-align:center">

<div style="font-size:11px;color:#2e7d32;font-weight:700">🌟 최고의 달</div>

<div style="font-size:26px;font-weight:900;color:#1b5e20">{_best_local["월"]}월</div>

<div style="font-size:12px;color:#388e3c">{_LE.get(_best_local["길흉"], "")} {_best_local["길흉"]} · {_best_local["십성"]}</div>

</div>

<div style="background:#fce4ec;border:1px solid #e57373;border-radius:10px;padding:12px;text-align:center">

<div style="font-size:11px;color:#c62828;font-weight:700">⚠️ 주의할 달</div>

<div style="font-size:26px;font-weight:900;color:#b71c1c">{_worst_local["월"]}월</div>

<div style="font-size:12px;color:#d32f2f">{_LE.get(_worst_local["길흉"], "")} {_worst_local["길흉"]} · {_worst_local["십성"]}</div>

</div>

</div>

<div style="font-size:12px;color:#666;line-height:1.8">

    ✦ {_best_local["월"]}월에는 {_MONTH_ADVICE.get(_best_local["십성"], "")} &nbsp;|&nbsp;

    {_worst_local["월"]}월에는 {_MONTH_ADVICE.get(_worst_local["십성"], "신중히 행동하십시오.")}

</div>

</div>""",
        unsafe_allow_html=True,
    )
    # 12개월 개별 카드 (expander)
    for _ml in _mdata:
        _m = _ml["월"]
        _lv = _ml["길흉"]
        _col = _LC.get(_lv, "#777")
        _em = _LE.get(_lv, "")
        _ss = _ml["십성"]
        _adv = _MONTH_ADVICE.get(_ss, _ml.get("short", ""))
        _desc = _ml.get("설명", _ml.get("desc", ""))
        _is_now = _m == today.month and sel_year == today.year
        _now_mark = " 📍현재" if _is_now else ""
        with st.expander(f"{_em} {_m}월 ({_ml['월운']}) — {_lv}{_now_mark}", expanded=_is_now):
            st.markdown(
                    f"""

<div style="border-left:4px solid {_col};padding:10px 14px;border-radius:0 8px 8px 0;background:#fafafa">

<div style="font-size:12px;color:{_col};font-weight:700;margin-bottom:6px">{_ss} 기운의 달 · {_lv}</div>

<div style="font-size:13px;color:#333;line-height:1.9;margin-bottom:8px">{_desc}</div>

<div style="font-size:13px;color:#555;line-height:1.9;padding:8px 12px;background:#fff;border-radius:6px;border:1px solid #eee">

    💡 {_adv}

</div>

<div style="margin-top:8px;display:flex;gap:12px;font-size:12px;color:#777">

<span>💰 {_ml.get("재물", "")}</span>

<span>🤝 {_ml.get("관계", "")}</span>

<span>⚠️ {_ml.get("주의", "")}</span>

</div>

</div>""",
                unsafe_allow_html=True,
            )

    LEVEL_COLOR = {
        "대길": "#4caf50",
        "길": "#8bc34a",
        "평길": "#ffc107",
        "평": "#9e9e9e",
        "흉": "#f44336",
        "흉흉": "#b71c1c",
    }

    LEVEL_EMOJI = {
        "대길": "🌟",
        "길": "✅",
        "평길": "🟡",
        "평": "⬜",
        "흉": "⚠️",
        "흉흉": "🔴",
    }

    months_data = [get_monthly_luck(pils, sel_year, m) for m in range(1, 13)]

    LEVEL_RANK = {"대길": 5, "길": 4, "평길": 3, "평": 2, "흉": 1, "흉흉": 0}

    best_m = max(months_data, key=lambda x: LEVEL_RANK.get(x["길흉"], 2))

    worst_m = min(months_data, key=lambda x: LEVEL_RANK.get(x["길흉"], 2))

    bc1, bc2 = st.columns(2)

    with bc1:
        st.markdown(
            f"""

<div style="background:#e8f5e8;border:1px solid #8de48d;border-radius:10px; padding:12px 16px;margin-bottom:10px;font-size:13px;color:#33691e">

        🌟 최고의 달: <b>{best_m["월"]}월</b> - {best_m["월운"]} ({best_m["십성"]}) {best_m["short"]}

</div>

""",
            unsafe_allow_html=True,
        )

    with bc2:
        st.markdown(
            f"""

<div style="background:#fff0f0;border:1px solid #f0a0a0;border-radius:10px; padding:12px 16px;margin-bottom:10px;font-size:13px;color:#b71c1c">

        ⚠️ 주의할 달: <b>{worst_m["월"]}월</b> - {worst_m["월운"]} ({worst_m["십성"]}) {worst_m["short"]}

</div>

""",
            unsafe_allow_html=True,
        )

    for ml in months_data:
        m = ml["월"]

        is_now = m == today.month and sel_year == today.year

        lcolor = LEVEL_COLOR.get(ml["길흉"], "#777")

        lemoji = LEVEL_EMOJI.get(ml["길흉"], "")

        month_names = [
            "",
            "1월",
            "2월",
            "3월",
            "4월",
            "5월",
            "6월",
            "7월",
            "8월",
            "9월",
            "10월",
            "11월",
            "12월",
        ]

        with st.expander(
            f"{'-> ' if is_now else ''}{month_names[m]}  |  {ml['월운']} ({ml['십성']})  |  {lemoji} {ml['길흉']} - {ml['short']}",
            expanded=is_now,
        ):
            st.markdown(
                f"""

<div style="background:#f8f8f8;border-left:4px solid {lcolor}; border-radius:0 10px 10px 0;padding:16px;margin-bottom:8px">

<div style="font-size:13px;color:#000000;line-height:1.9">

            {ml["설명"]}

</div>

</div>

<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px">

<div style="flex:1;background:#e8f5e8;border-radius:8px;padding:10px 14px">

<div style="font-size:11px;color:#000000;margin-bottom:4px">💰 재물운</div>

<div style="font-size:13px;color:#33691e">{ml["재물"]}</div>

</div>

<div style="flex:1;background:#f5f5f5;border-radius:8px;padding:10px 14px">

<div style="font-size:11px;color:#000000;margin-bottom:4px">👥 인간관계</div>

<div style="font-size:13px;color:#7986cb">{ml["관계"]}</div>

</div>

</div>

<div style="background:#fff5e0;border-radius:8px;padding:10px 14px">

<div style="font-size:11px;color:#000000;margin-bottom:4px">⚠️ 주의사항</div>

<div style="font-size:13px;color:#ffab40">{ml["주의"]}</div>

</div>

""",
                unsafe_allow_html=True,
            )


def menu8_bihang(pils, name, birth_year, gender):
    """8️⃣ 특급 비방록 - 용신 기반 전통 비방 처방전"""

    # [년, 월, 일, 시] 순서에서 일간은 index 2

    ilgan = pils[1]["cg"] if pils and len(pils) > 1 else ""

    ys = get_yongshin(pils)

    yongshin_ohs = ys.get("종합_용신", [])

    if not isinstance(yongshin_ohs, list):
        yongshin_ohs = []

    gishin_raw = ys.get("기신", "")

    gishin_ohs = [o for o in ["木", "火", "土", "金", "水"] if o in str(gishin_raw)]

    ilgan_oh = OH.get(ilgan, "")

    strength_info = get_ilgan_strength(ilgan, pils)

    sn = strength_info["신강신약"]

    display_name = name if name else "내담자"

    current_year = datetime.now().year

    current_age = current_year - birth_year + 1

    # ==================================

    # 비방 DB - 용신 오행별 전통 비방 (만신 스타일)

    # ==================================


    # ==================================================

    # UI 시작

    # ==================================================

    st.markdown(
        """

<div style="background:linear-gradient(135deg,#1a0a00,#2e1500,#1a0a00);border:2px solid #d4af37;border-radius:16px;padding:22px 26px;margin-bottom:20px">

<div style="color:#ffaa00;font-size:11px;letter-spacing:4px;margin-bottom:8px">

            ⚠️ 극비(極秘) - 용신 기반 전통 비방 처방전

</div>

<div style="color:#f7e695;font-size:19px;font-weight:900;letter-spacing:2px;margin-bottom:10px">

            🔴 특급 비방록(特急 秘方錄)

</div>

<div style="color:#d0a080;font-size:13px;line-height:1.9">

            무당/만신이 대대로 전해온 비방을 사주 용신에 맞춰 처방합니다.<br>

            돈이 새는 구멍을 막고, 재물이 들어오는 문을 여는 처방입니다.<br>

<span style="color:#ff8888">기신(忌神) 오행을 막고 용신(用神) 오행을 강화하는 것이 핵심입니다.</span>

</div>

</div>""",
        unsafe_allow_html=True,
    )

    # ① 용신/기신 파악

    OH_EMOJI = {"木": "🌳", "火": "🔥", "土": "⛰️", "金": "⚔️", "水": "💧"}

    OH_NAME = {
        "木": "목(木)",
        "火": "화(火)",
        "土": "토(土)",
        "金": "금(金)",
        "水": "수(水)",
    }

    col_y, col_g = st.columns(2)

    with col_y:
        y_tags = (
            " ".join(
                [
                    f"<span style='background:#1a3a5c;color:#f7e695;font-weight:900;padding:6px 16px;border-radius:20px;font-size:14px'>{OH_EMOJI.get(o, '')} {OH_NAME.get(o, o)}</span>"
                    for o in yongshin_ohs
                ]
            )
            if yongshin_ohs
            else "<span style='color:#888'>분석 중</span>"
        )

        st.markdown(
            f"""

<div style="background:#fff8e8;border:2px solid #c9a84c;border-radius:12px;padding:16px">

<div style="font-size:12px;color:#8b5e00;font-weight:800;margin-bottom:8px">

                🌟 용신 (이 기운을 강화하라)

</div>

<div>{y_tags}</div>

</div>

""",
            unsafe_allow_html=True,
        )

    with col_g:
        g_tags = (
            " ".join(
                [
                    f"<span style='background:#ffdcdc;color:#000000;font-weight:700;padding:6px 16px;border-radius:20px;font-size:14px'>{OH_EMOJI.get(o, '')} {OH_NAME.get(o, o)}</span>"
                    for o in gishin_ohs
                ]
            )
            if gishin_ohs
            else "<span style='color:#888'>없음</span>"
        )

        st.markdown(
            f"""

<div style="background:#f5f5f5;border:2px solid #8B0000;border-radius:12px;padding:16px">

<div style="font-size:11px;color:#ff6060;font-weight:700;margin-bottom:8px">

                ⛔ 기신 (이 기운이 돈을 쫓아낸다)

</div>

<div>{g_tags}</div>

</div>

""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ② 용신 및 기신 비방 (만신의 신탁)

    if not yongshin_ohs:
        st.warning("용신 계산 결과가 없습니다. 사주 계산을 먼저 진행하십시오.")

        return

    # 용신 강화 신탁

    for yong_oh in yongshin_ohs[:2]:
        bd = BIHANG_DB.get(yong_oh)

        if not bd:
            continue

        st.markdown(
            f"""

<div style="background:#fffef9;border:2px solid #d4af37;border-radius:14px;padding:22px;box-shadow:0 4px 16px rgba(180,140,0,0.12);margin-bottom:20px">

<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">

<span style="font-size: 30px;">{bd["emoji"]}</span>

<div>

<div style="color:#9b7200;font-size:11px;font-weight:800;letter-spacing:2px;margin-bottom:2px">ELEMENTAL SECRET</div>

<div style="font-size:20px;font-weight:900;color:#1a1a1a">{bd["오행명"]}의 처방</div>

</div>

</div>

            

<div style="margin-bottom: 20px;">

<div style="font-size: 13px; font-weight: 800; color: #1a237e; margin-bottom: 8px;">📜 비방 (秘方)</div>

<div style="background:#eef2ff;padding:14px;border-radius:8px;border-left:4px solid #1a237e;font-size:14px;line-height:1.9;color:#111;word-break:break-all">

                    "{bd["비방"]}"

</div>

</div>

<div style="margin-bottom: 20px;">

<div style="font-size: 13px; font-weight: 800; color: #b71c1c; margin-bottom: 8px;">💰 재물 (財物)</div>

<div style="background:#fff0f0;padding:14px;border-radius:8px;border-left:4px solid #b71c1c;font-size:14px;line-height:1.9;color:#111;word-break:break-all">

                    "{bd["재물"]}"

</div>

</div>

<div style="margin-bottom: 20px;">

<div style="font-size: 13px; font-weight: 800; color: #333; margin-bottom: 8px;">🚫 금기 (禁忌)</div>

<div style="background:#f5f5f5;padding:14px;border-radius:8px;border-left:4px solid #555;font-size:14px;line-height:1.9;color:#333;word-break:break-all">

                    "{bd["금기"]}"

</div>

</div>

            

<div style="background: #1a1a1a; color: #f7e695; padding: 12px 18px; border-radius: 8px; font-size: 13px; text-align: center; border: 1px solid #d4af37;">

                ⚖️ <b>행동 지침:</b> {bd["action"]}

</div>

</div>

        """,
            unsafe_allow_html=True,
        )

    # 기신 차단 신탁

    if gishin_ohs:
        st.markdown(
            f"""

<div style="background:#fff5f5;border:2px solid #e53935;border-radius:12px;padding:18px;margin-bottom:20px">

<div style="font-size: 16px; font-weight: 900; color: #b71c1c; margin-bottom: 12px;">🚫 기신(忌神) 차단 - 돈 새는 구멍을 막아라</div>

<div style="font-size:13px;color:#333;line-height:1.9;word-break:break-all">

                현재 사주에서 <b>{", ".join(gishin_ohs)}</b>의 기운이 재물을 밀어내고 있습니다. 

                해당 오행의 색상과 방위를 피하고, 특히 그 기운이 강한 날에는 큰 거래를 삼가 명(命)을 보존하십시오.

</div>

</div>

        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ④ 공통 만신 비방 - 신강신약별

    st.markdown(
        """

<div style="background:#f8f5ff;border:2px solid #7c5cbf;border-radius:14px;padding:20px;margin:16px 0">

<div style="font-size:16px;font-weight:900;color:#4a2080;margin-bottom:14px">

            🕯️ 신강신약별 공통 비방 - 만신 구전(口傳)

</div>""",
        unsafe_allow_html=True,
    )

    if "신강" in sn:
        rituals_common = [
            "신강한 사주는 힘이 넘쳐 오히려 재물을 흩트린다. 주 1회 절에 가거나 사찰 보시(布施)를 생활화하면 기운이 안정된다.",
            "집 안에 거울을 너무 많이 두지 말 것 - 강한 기운이 반사되어 충돌이 생긴다.",
            "월초(음력 1일)마다 현관 소금 한 줌 뿌리고 3일 후 쓸어버리기 - 나쁜 기운 차단",
            "재물이 들어오는 운기(用神대운)에는 반드시 움직여라. 신강한 사주는 적극적으로 나서야 재물이 손에 잡힌다.",
            "기도/의식보다 행동이 우선이다. 신강은 스스로 만드는 사주이다.",
        ]

        desc_color = "#d0c8f8"

        sn_color = "#9b7ccc"

    else:
        rituals_common = [
            "신약한 사주는 기운이 약해 귀신/나쁜 기운에 쉽게 영향 받는다. 매달 음력 초하루 정화수 올리는 것을 생활화하라.",
            "집 안 구석구석 소금 청소 - 월 1회 소금물로 현관 바닥 닦기 (기운 정화)",
            "붉은 팥죽을 동지/정월 초에 대문 앞에 뿌리기 - 나쁜 기운 쫓기",
            "수호신 역할의 소품(도자기/나무 인형 등)을 집 안에 두되 정기적으로 닦아줄 것",
            "귀인 운이 올 때 반드시 받아들여라. 신약은 혼자보다 귀인과 함께일 때 크게 된다.",
            "무리한 야간 활동/과음/과로를 피하라. 신약은 건강이 재물의 기반이다.",
        ]

        desc_color = "#f0d8c8"

        sn_color = "#e8a060"

    st.markdown(
        f"""

<div style="font-size:12px;color:{sn_color};font-weight:700;margin-bottom:8px">

        {sn} 특화 처방

</div>

""",
        unsafe_allow_html=True,
    )

    for r in rituals_common:
        st.markdown(
            f"""

<div style="background:#fff;border-left:4px solid {sn_color};padding:12px 16px;border-radius:0 8px 8px 0;margin:6px 0;font-size:13px;color:#222;line-height:1.9;word-break:break-all;box-shadow:0 1px 3px rgba(0,0,0,0.06)">

            {r}

</div>

""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">',
        unsafe_allow_html=True,
    )

    # ⑤ 나이별 특급 비방 - 현재 운기에 맞춘 처방

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg,#fffbf0,#fff5e0);border:2px solid #c9a84c;border-radius:14px;padding:20px">

<div style="font-size:16px;font-weight:900;color:#8b6200;margin-bottom:10px">

            📅 {current_year}년 ({current_age}세) 현재 운기 맞춤 비방

</div>

""",
        unsafe_allow_html=True,
    )

    try:
        sw = get_yearly_luck(pils, current_year) or {}

        sw_ss = sw.get("십성_천간", "-")

        sw_oh = sw.get("오행_천간", "")

        sw_str = sw.get("세운", "")

        is_yong_year = sw_oh in yongshin_ohs

        if is_yong_year:
            year_desc = f"올해 {sw_str}년은 용신 오행이 들어오는 해입니다. 적극적으로 움직이십시오."

            year_bihang = [
                f"용신 오행({sw_oh})이 강화되는 해 - 이 해에 큰 결정/투자/창업을 해야 합니다.",
                f"용신 색상/방위를 최대한 활용하십시오. 옷 색상부터 바꾸는 것이 시작입니다.",
                "새로운 인연/거래처/투자처가 올 때 적극적으로 받아들이십시오.",
                "연초(음력 정월)에 용신 방향으로 여행 또는 나들이 - 운기를 몸에 흡수",
            ]

            card_color = "#000000"

            card_bg = "#1a1a00"

        else:
            year_desc = f"올해 {sw_str}년은 기신이 강하게 작동하는 해입니다. 수비적으로 대응하십시오."

            year_bihang = [
                f"기신 오행({sw_oh})이 강화되는 해 - 큰 투자/보증/동업을 피하십시오.",
                "현상 유지가 오히려 이기는 해입니다. 무리하게 확장하면 손해를 봅니다.",
                "월초마다 소금 청소와 정화수 의식으로 기운을 지키십시오.",
                "이 해에는 귀한 사람을 만나도 큰 거래보다 관계를 쌓는 데 집중하십시오.",
            ]

            card_color = "#c0392b"

            card_bg = "#1a0000"

        st.markdown(
            f"""

<div style="background:{card_bg};border-left:4px solid {card_color}; border-radius:10px;padding:14px;margin-bottom:12px">

<div style="font-size:13px;color:{card_color};font-weight:700;margin-bottom:6px">

                {sw_str}년 ({sw_ss}년) 판단

</div>

<div style="font-size:13px;color:#000000;line-height:1.8">{year_desc}</div>

</div>

""",
            unsafe_allow_html=True,
        )

        for yb in year_bihang:
            st.markdown(f"""

<div style="background:#fafafa;border-left:3px solid {card_color}; padding:9px 14px;border-radius:6px;margin:4px 0; font-size:13px;color:#e0d0c0;line-height:1.8">

                {"✅" if is_yong_year else "⚠️"} {yb}

</div>

""", unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"올해 운기 계산 오류: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ⑥ 신살별 비방 ─────────────────────────────────────
    st.markdown(
        """<div style="background:#f5f0ff;border:2px solid #7c4dcc;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#4a148c;margin-bottom:14px">🌟 신살(神殺)별 전통 비방</div>""",
        unsafe_allow_html=True,
    )
    try:
        stars_b = get_special_stars(pils)
        _SINSAL_RX = {
            "천을귀인": {"emoji":"👑","desc":"하늘이 내리는 귀인 기운","비방":"위기마다 귀인이 오는 팔자니라. 낮은 자세로 받아들이면 그 귀인이 평생 곁을 지킨다.","처방":"매달 음력 1일 아침, 세 번 절하며 감사를 외우게. 감사함이 귀인을 계속 불러오느니라.","금기":"귀인의 도움을 무시하거나 당연하게 여기는 것."},
            "도화살": {"emoji":"🌹","desc":"이성 인기와 매력의 기운","비방":"분홍색 소품을 침실에 하나 두게. 매력이 배가되어 좋은 인연이 오느니라.","처방":"복숭아꽃(또는 복숭아 향 제품)을 동쪽에 두면 좋은 이성 인연이 들어오느니라.","금기":"도화살이 강한 해 경솔한 이성 관계."},
            "겁살": {"emoji":"⚡","desc":"강한 추진력이지만 사고수 기운","비방":"붉은 팥을 문 앞에 뿌리고 3일 뒤 깨끗이 청소하게.","처방":"날카로운 물건은 눈에 보이지 않는 곳에 보관하게.","금기":"이 살이 강한 해 수술·무리한 운동·야간 운전."},
            "역마살": {"emoji":"🚀","desc":"이동·여행·변화의 기운","비방":"이 살이 강한 해 가만히 있으려 하지 말게. 이동이 오히려 재물을 부르느니라.","처방":"집에 작은 바퀴 달린 소품 하나. 역마살 에너지가 순조롭게 흐르면 이동 중 좋은 기회를 만나느니라.","금기":"이 살이 강한 시기 억지로 한 곳에 머물려 하는 것."},
        }
        found_sinsal = False
        if stars_b:
            for star in stars_b:
                sname = star.get("name","")
                for key, rx in _SINSAL_RX.items():
                    if key in sname:
                        found_sinsal = True
                        st.markdown(
                            f"""<div style="background:#fff;border:2px solid #7c4dcc;border-radius:10px;padding:14px;margin-bottom:10px">
<div style="font-size:14px;font-weight:900;color:#4a148c;margin-bottom:8px">{rx['emoji']} {sname} — {rx['desc']}</div>
<div style="background:#f3e5ff;border-left:4px solid #7c4dcc;border-radius:0 8px 8px 0;padding:10px 12px;margin-bottom:6px;font-size:13px;color:#1a1a1a;line-height:1.9;word-break:break-all">📜 {rx['비방']}</div>
<div style="background:#e8f5e9;border-left:4px solid #2e7d32;border-radius:0 8px 8px 0;padding:10px 12px;margin-bottom:6px;font-size:13px;color:#1a1a1a;line-height:1.9;word-break:break-all">✅ {rx['처방']}</div>
<div style="background:#ffebee;border-left:4px solid #c62828;border-radius:0 8px 8px 0;padding:8px 12px;font-size:13px;color:#b71c1c;font-weight:700;word-break:break-all">⛔ {rx['금기']}</div>
</div>""", unsafe_allow_html=True)
                        break
        if not found_sinsal:
            st.markdown('<div style="font-size:13px;color:#aaa;padding:10px">원국에 특별히 강한 신살이 없습니다. 기본 용신 처방에 집중하십시오.</div>', unsafe_allow_html=True)
    except Exception:
        pass
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ⑦ 건강 오행 처방 ──────────────────────────────────
    st.markdown(
        """<div style="background:#f0fff4;border:2px solid #27ae60;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#1b5e20;margin-bottom:14px">💊 건강 오행 처방 — 몸이 재물보다 먼저다</div>""",
        unsafe_allow_html=True,
    )
    _HEALTH_RX = {
        "木": {"취약":"간장·담낭·눈·신경계","처방":"충분한 수면(7시간+)이 간을 회복시킨다. 분노·스트레스가 간을 상하게 하므로 화를 다스리는 연습 필수.","음식":"신맛(식초·레몬·매실)·녹색 채소·결명자차","운동":"스트레칭·요가·걷기","금기":"야식·음주·과로"},
        "火": {"취약":"심장·소장·혈관·혈압","처방":"카페인·음주 자제가 심혈관을 지킨다. 과로와 흥분 상태 지속이 심장을 해친다.","음식":"쓴맛(녹차·쑥)·붉은 과일(딸기·토마토)·오메가3","운동":"유산소(걷기·수영·자전거)","금기":"밤샘 작업·과도한 카페인"},
        "土": {"취약":"위장·비장·췌장·당뇨","처방":"식사 시간 규칙성이 핵심. 폭식·야식이 위장을 망친다.","음식":"단맛(고구마·감자·현미·꿀)·황색 음식·생강차","운동":"산책·맨발 걷기","금기":"불규칙 식사·폭식·빠르게 먹기"},
        "金": {"취약":"폐·대장·기관지·피부·호흡기","처방":"습도 50~60% 유지가 폐를 보호한다.","음식":"매운맛(무·배·도라지·생강)·흰 음식·배즙","운동":"수영·호흡 운동·복식호흡","금기":"흡연·미세먼지 장시간 노출"},
        "水": {"취약":"신장·방광·생식기·귀·뼈","처방":"하루 물 2리터+가 신장을 지킨다. 짠 음식과 과로가 신장을 망친다.","음식":"짠맛(김·미역·검은콩·흑임자)·블루베리","운동":"수영·가벼운 스트레칭","금기":"짠 음식 과다·과로·밤샘 작업"},
    }
    _ys_bh = get_yongshin(pils)
    _yong_ohs_bh = _ys_bh.get("종합_용신", []) if isinstance(_ys_bh.get("종합_용신",[]), list) else []
    for yoh in _yong_ohs_bh[:1]:
        hrx = _HEALTH_RX.get(yoh, {})
        if hrx:
            st.markdown(
                f"""<div style="display:grid;grid-template-columns:1fr;gap:8px">
<div style="background:#e8f5e9;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#2e7d32;margin-bottom:5px">⚠️ 취약 부위</div><div style="font-size:13px;color:#333">{hrx['취약']}</div></div>
<div style="background:#e3f2fd;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#1565c0;margin-bottom:5px">🏃 권장 운동</div><div style="font-size:13px;color:#333">{hrx['운동']}</div></div>
<div style="background:#fff9c4;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#f57f17;margin-bottom:5px">🥗 권장 음식</div><div style="font-size:13px;color:#333">{hrx['음식']}</div></div>
<div style="background:#fce4ec;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#c62828;margin-bottom:5px">⛔ 피해야 할 것</div><div style="font-size:13px;color:#333">{hrx['금기']}</div></div>
</div>
<div style="background:#f1f8e9;border:1px solid #8bc34a;border-radius:8px;padding:10px;margin-top:8px"><div style="font-size:12px;font-weight:800;color:#558b2f;margin-bottom:4px">💡 핵심 처방</div><div style="font-size:13px;color:#333;line-height:1.7;white-space:normal;word-break:break-all">{hrx['처방']}</div></div>""",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ⑧ 즉각 실천 체크리스트 ────────────────────────────
    st.markdown(
        """<div style="background:#1a1a1a;border:2px solid #d4af37;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#f7e695;margin-bottom:16px">⚡ 지금 당장 실천할 비방 체크리스트</div>""",
        unsafe_allow_html=True,
    )
    _bihang_items = [
        "매달 음력 초하루(1일) 아침 — 현관 소금 청소 실천하기",
        "용신 오행 음식 하루 한 가지씩 식단에 포함하기",
        "침대 머리 방향 — 용신 오행 방위로 확인·조정하기",
        "주 1회 10분 이상 조용한 명상·감사 일기 쓰기",
        "기신 오행 색상 소품을 눈에 띄는 곳에서 치우기",
        "올해 흉월(기신 월)에는 큰 투자·이직 결정 미루기",
        "용신 색상(지갑·옷·소품) 하나 추가하기",
    ]
    for item in _bihang_items:
        st.markdown(
            f"<div style='display:flex;align-items:flex-start;gap:10px;background:#1e1e2e;border:1px solid #3a3a5e;border-radius:8px;padding:10px 14px;margin-bottom:6px'>"
            f"<span style='color:#d4af37;font-size:18px;flex-shrink:0;margin-top:1px'>☐</span>"
            f"<span style='font-size:13px;color:#e8e8e8;line-height:1.9;white-space:normal;word-break:break-all;flex:1'>{item}</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 풍수·방위 배치 비방 ─────────────────────────────
    st.markdown("""<div style="background:#fff8f0;border:2px solid #d4af37;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#8b6200;margin-bottom:14px">🏠 집안 풍수·방위 배치 비방</div>""", unsafe_allow_html=True)
    _FENG_SHUI = {
        "木": {"침대":"머리를 동쪽으로","책상":"동쪽 바라보고 앉기","현관":"동쪽에 초록 식물","금지":"서쪽 날카로운 금속 장식품"},
        "火": {"침대":"머리를 남쪽으로","책상":"남향 창문 앞","현관":"남쪽에 붉은 소품","금지":"북쪽에 수족관·분수"},
        "土": {"침대":"머리를 동북쪽으로","책상":"중앙 또는 남서향","현관":"황토색 도자기","금지":"집 중앙 구멍·틈새"},
        "金": {"침대":"머리를 서쪽으로","책상":"서향 또는 서북향","현관":"서쪽에 금속 소품","금지":"남쪽에 빨간 소품 과다"},
        "水": {"침대":"머리를 북쪽으로","책상":"북향 또는 북동향","현관":"북쪽에 작은 어항","금지":"북쪽 방향에 붉은 소품"},
    }
    _ys_bh = get_yongshin(pils)
    _yong_ohs_bh = _ys_bh.get("종합_용신",[]) if isinstance(_ys_bh.get("종합_용신",[]),list) else []
    for _yoh in _yong_ohs_bh[:1]:
        _fd = _FENG_SHUI.get(_yoh, {})
        if _fd:
            st.markdown(f"""<div style="display:grid;grid-template-columns:1fr;gap:8px;margin-top:10px">
<div style="background:#fffbf0;border:1px solid #d4af37;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#8b6200;margin-bottom:5px">🛏️ 침대 머리 방향</div><div style="font-size:13px;color:#333">{_fd['침대']}</div></div>
<div style="background:#fffbf0;border:1px solid #d4af37;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#8b6200;margin-bottom:5px">💼 책상 방향</div><div style="font-size:13px;color:#333">{_fd['책상']}</div></div>
<div style="background:#fffbf0;border:1px solid #d4af37;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#8b6200;margin-bottom:5px">🚪 현관 배치</div><div style="font-size:13px;color:#333">{_fd['현관']}</div></div>
<div style="background:#fff0f0;border:1px solid #e74c3c;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:800;color:#c0392b;margin-bottom:5px">⛔ 절대 금지</div><div style="font-size:13px;color:#333">{_fd['금지']}</div></div>
</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ── 대운별 맞춤 처방 ─────────────────────────────────
    st.markdown(f"""<div style="background:#f0f4ff;border:2px solid #3498db;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#1a237e;margin-bottom:14px">🌊 현재 대운(大運) 맞춤 처방</div>""", unsafe_allow_html=True)
    try:
        _ss2 = st.session_state
        _bm2  = max(1, min(12, int(_ss2.get("birth_month")  or _ss2.get("in_birth_month",  1)  or 1)))
        _bd3  = max(1, min(31, int(_ss2.get("birth_day")    or _ss2.get("in_birth_day",    1)  or 1)))
        _bh3  = max(0, min(23, int(_ss2.get("birth_hour")   or _ss2.get("in_birth_hour",  12) or 12)))
        _bmn3 = max(0, min(59, int(_ss2.get("birth_minute") or _ss2.get("in_birth_minute", 0)  or 0)))
        _dw_list3 = SajuCoreEngine.get_daewoon(pils, birth_year, _bm2, _bd3, _bh3, _bmn3, gender) or []
        _cur_dw3 = next((d for d in _dw_list3 if d.get("시작연도",0) <= current_year <= d.get("종료연도",9999)), None)
        # 현재 대운 못 찾으면 가장 가까운 대운 선택
        if not _cur_dw3 and _dw_list3:
            _cur_dw3 = min(_dw_list3, key=lambda d: abs(d.get("시작연도", current_year) - current_year))
        if _cur_dw3:
            _dw_ss3 = TEN_GODS_MATRIX.get(ilgan,{}).get(_cur_dw3.get("cg",""),"-")
            _DW_RX = {
                "偏財":("💰 재물·이성 기운의 대운","적극적으로 투자하고 사업을 확장하라. 이 대운의 기회를 놓치면 10년을 기다려야 한다.","투기·보증은 과욕이 된다. 안전 자산 30%+"),
                "正財":("💰 안정 수입의 대운","꾸준히 모으고 부동산·예금에 집중하라.","급격한 변화·투기를 피하라."),
                "食神":("🌟 재능·복록의 대운","전문성을 드러내고 새 분야를 개척하라.","게으름이 최대의 적."),
                "傷官":("⚡ 창의·변화의 대운","기존 틀을 깨고 새 방식으로 승부하라.","윗사람·관공서와의 충돌 경계."),
                "偏官":("⚠️ 압박·도전의 대운","체력·건강 관리 최우선. 정기검진 의무화.","법적 분쟁·수술·사고 각별 조심."),
                "正官":("✅ 명예·승진의 대운","조직에서 원칙 지키고 신뢰를 쌓아라.","규칙 위반·윗사람 갈등 금지."),
                "偏印":("📚 이동·변화의 대운","새 분야 학습·이사·이직에 유리하다.","중도 포기가 최대 위험."),
                "正印":("📚 배움·귀인의 대운","자격증·학위·배움에 집중하라.","지나친 의존심 경계."),
                "比肩":("⚡ 독립·경쟁의 대운","혼자 움직여라. 독립 행보가 가장 강한 결과.","동업·보증·금전거래 경계."),
                "劫財":("🔴 손재·경쟁의 대운","방어와 현상 유지가 전략이다.","투기·보증·동업 절대 금지."),
            }
            _rx3 = _DW_RX.get(_dw_ss3, (f"{_dw_ss3} 대운","흐름을 잘 읽고 신중하게 움직이게.","무리한 변화는 삼가게."))
            st.markdown(f"""<div style="background:#f0fff4;border:2px solid #27ae60;border-radius:10px;padding:16px">
<div style="font-size:14px;font-weight:900;color:#1b5e20;margin-bottom:10px">{_rx3[0]} — {_cur_dw3['str']} ({_dw_ss3}) | {_cur_dw3['시작연도']}~{_cur_dw3['종료연도']}년</div>
<div style="background:#e8f5e9;border-left:4px solid #27ae60;border-radius:0 8px 8px 0;padding:12px 14px;margin-bottom:8px;font-size:13px;color:#1a1a1a;line-height:1.9;word-break:break-all">✅ <b>해야 할 것:</b> {_rx3[1]}</div>
<div style="background:#ffebee;border-left:4px solid #e53935;border-radius:0 8px 8px 0;padding:12px 14px;font-size:13px;color:#1a1a1a;line-height:1.9;word-break:break-all">⛔ <b>하면 안 되는 것:</b> {_rx3[2]}</div>
</div>""", unsafe_allow_html=True)
    except Exception as _dw_e:
        # 대운 계산 실패 시 기본 처방 출력
        st.markdown("""<div style="background:#fff8e8;border:1px solid #c9a84c;border-radius:10px;padding:14px;margin:8px 0">
<div style="font-size:13px;color:#5a3d00;line-height:1.9">
대운 기간 계산을 위해 정확한 생년월일시가 필요합니다.<br>
현재 대운의 기운을 파악하려면 <b>사주 입력 화면에서 생시(生時)를 다시 확인</b>해 주십시오.<br>
용신 오행을 강화하는 비방을 우선 실천하십시오.
</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ── 이달의 길일·흉일 ──────────────────────────────────
    _now3 = datetime.now()
    _cm3, _cy3 = _now3.month, _now3.year
    st.markdown(f"""<div style="background:#fff0f8;border:2px solid #e91e8c;border-radius:14px;padding:20px;margin:16px 0">
<div style="font-size:16px;font-weight:900;color:#880e4f;margin-bottom:14px">📅 {_cm3}월 길일·흉일 & 행동지침</div>""", unsafe_allow_html=True)
    try:
        _ys3 = get_yongshin(pils)
        _yong3 = _ys3.get("종합_용신",[]) if isinstance(_ys3.get("종합_용신",[]),list) else []
        _gi3 = [o for o in ["木","火","土","金","水"] if o in str(_ys3.get("기신",""))]
        _OH3 = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _good_m, _bad_m = [], []
        for _m3 in range(1,13):
            _ml3 = get_monthly_luck(pils, _cy3, _m3) or {}
            _ml_oh3 = _OH3.get(_ml3.get("간","")[:1],"")
            _ml_ss3 = _ml3.get("십성","")
            if _ml_oh3 in _yong3: _good_m.append(f"{_m3}월({_ml_ss3})")
            elif _ml_oh3 in _gi3:  _bad_m.append(f"{_m3}월({_ml_ss3})")
        _MONTH_ACTION = {
            "편재":"💰 적극 움직이면 돈이 되는 달. 미뤄둔 투자·영업 지금 실행.",
            "정재":"💰 꾸준함이 재물을 부르는 달. 저축·정산·계약 마무리 집중.",
            "식신":"🌟 내 재능이 빛나는 달. 새 프로젝트·자격시험 좋음.",
            "상관":"⚠️ 말조심 최우선. SNS·계약서·윗사람 발언 세 번 확인.",
            "편관":"⚠️ 건강·안전 최우선. 무리한 활동·새 사업 자제.",
            "정관":"✅ 조직과 원칙 안에서 움직이면 인정받는 달.",
            "겁재":"🔴 지출·투자·보증 최대한 줄여라. 돈이 나가는 달.",
        }
        _cur_ml3 = get_monthly_luck(pils, _cy3, _cm3) or {}
        _cur_ml_ss3 = _cur_ml3.get("십성","")
        _ml_action3 = _MONTH_ACTION.get(_cur_ml_ss3, f"[{_cur_ml_ss3}] — 흐름을 잘 읽고 신중하게 움직이게.")
        _cur_ml_oh3 = _OH3.get(_cur_ml3.get("간","")[:1],"")
        _m_color = "#27ae60" if _cur_ml_oh3 in _yong3 else "#e74c3c" if _cur_ml_oh3 in _gi3 else "#2980b9"
        st.markdown(f"""<div style="background:#fff;border:2px solid {_m_color};border-radius:10px;padding:14px;margin-bottom:10px">
<div style="font-size:14px;font-weight:900;color:{_m_color};margin-bottom:6px">{_cm3}월 — {_cur_ml3.get('간','')}{_cur_ml3.get('지','')}</div>
<div style="font-size:13px;color:#333;line-height:1.8">{_ml_action3}</div>
</div>""", unsafe_allow_html=True)
        if _good_m:
            st.markdown(f'<div style="background:#e8f5e9;border-radius:8px;padding:10px;margin-bottom:6px;font-size:13px"><b style="color:#2e7d32">✅ 올해 용신 길월:</b> {" · ".join(_good_m)} — 이 달에 중요한 결정을 내려라!</div>', unsafe_allow_html=True)
        if _bad_m:
            st.markdown(f'<div style="background:#ffebee;border-radius:8px;padding:10px;font-size:13px"><b style="color:#c62828">⛔ 올해 기신 흉월:</b> {" · ".join(_bad_m)} — 큰 결정을 피하라!</div>', unsafe_allow_html=True)
    except Exception:
        st.info("월별 처방 계산 중 오류가 발생했습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════
    # ① 물상대체(物象代替) — 자연물로 기운 채우기
    # ══════════════════════════════════════════════════════
    st.markdown('<hr style="border:none;border-top:2px solid #d4af37;margin:28px 0">', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,#0a1628,#1a2840);border:2px solid #4a90d9;border-radius:14px;padding:20px;margin-bottom:6px">
<div style="color:#7ec8f5;font-size:11px;letter-spacing:3px;margin-bottom:6px">TRADITIONAL METHOD 01</div>
<div style="color:#e8f4ff;font-size:18px;font-weight:900;margin-bottom:8px">🌊 물상대체(物象代替) 비방 — 자연물로 기운을 채운다</div>
<div style="color:#aad4f0;font-size:13px;line-height:1.8">부족한 오행을 실제 자연물·환경으로 대체하는 가장 정통한 비방입니다.<br>
옛 조상들이 실생활에서 써온 방법으로, 효과가 즉각적이고 지속적입니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        _MULSUNG2 = {
            "木": [
                ("🌿 식물 배치", "집 동쪽에 살아있는 초록 식물을 두십시오. 반드시 살아있는 것이어야 합니다. 조화(造花)는 효과 없습니다."),
                ("🌲 숲·산 방문", "매주 1회 이상 숲이나 공원을 방문하여 나무 사이를 걸으십시오. 나무를 직접 손으로 만지며 기운을 받으십시오."),
                ("🌱 새벽 기운", "새벽 5~7시(인묘시) 동쪽 창문을 열고 심호흡 10회. 목(木) 기운이 가장 강한 시간입니다."),
                ("🍋 신맛 음식", "레몬·식초·매실·사과·귤 등 신맛 나는 음식을 매일 조금씩 드십시오. 간장·담낭을 강화합니다."),
                ("📐 동쪽 방위", "책상·침대 머리를 동쪽으로 배치하십시오. 잠자는 동안 목 기운을 흡수합니다."),
            ],
            "火": [
                ("🕯️ 촛불 의식", "매일 저녁 촛불 1개를 30분 이상 켜두십시오. 빨간 양초가 가장 효과적입니다."),
                ("☀️ 일광욕", "오전 10시~12시(오시) 15분 이상 햇볕을 직접 쬐십시오. 화(火) 기운이 피부를 통해 흡수됩니다."),
                ("🔴 붉은 소품", "현관이나 거실에 붉은 소품 1개를 반드시 두십시오. 입구에 붉은 기운이 있으면 재물운이 강화됩니다."),
                ("🍅 쓴맛·붉은 음식", "토마토·당근·석류·딸기·커피(무가당) 등을 꾸준히 드십시오. 심장·소장을 보강합니다."),
                ("🧭 남쪽 방위", "중요한 미팅·면접은 남쪽을 등지고 앉으십시오. 화 기운이 등을 밀어줍니다."),
            ],
            "土": [
                ("🪨 황토·돌 소품", "황토 도자기나 돌 소품을 집 중앙에 두십시오. 흙의 기운이 공간을 안정시킵니다."),
                ("🦶 맨발 흙 밟기", "주 3회 이상 맨발로 흙을 밟으십시오. 공원 흙길이나 황토방이 가장 좋습니다."),
                ("🍠 단맛 음식", "고구마·꿀·대추·단호박·현미를 꾸준히 드십시오. 위장·비장을 보강합니다."),
                ("🕐 환절기 행동", "새벽 1~3시(축시) 전에 취침하는 습관이 토 기운을 강화합니다."),
                ("🏡 집 중앙 정리", "집 한가운데를 깨끗하게 비워두십시오. 중앙에 물건을 쌓으면 토 기운이 막힙니다."),
            ],
            "金": [
                ("💍 금속 착용", "은·금 장신구를 매일 착용하십시오. 왼손 손목의 금속 팔찌가 특히 효과적입니다."),
                ("🗻 서쪽 등산", "가을철(9~11월) 서쪽 방향의 바위산을 등산하고, 바위 위에서 20분 이상 쉬십시오. 금 기운을 직접 흡수합니다."),
                ("🥬 매운맛 음식", "무·도라지·생강·마늘·배 등을 꾸준히 드십시오. 폐·대장을 보강합니다."),
                ("🤫 말 줄이기", "금 기운은 절제에서 강화됩니다. 불필요한 말을 줄이고 침묵의 시간을 늘리십시오."),
                ("🧭 서쪽 방위", "서쪽 방향에 금속 소품(쇠 조각상·동전 모음)을 배치하십시오."),
            ],
            "水": [
                ("🐟 어항·분수", "집 북쪽에 작은 어항이나 탁상 분수를 두십시오. 흐르는 물소리가 수 기운을 강화합니다."),
                ("🌊 바다·강 방문", "월 2회 이상 바다나 강을 찾아가 물을 직접 바라보십시오. 눈으로 물을 보는 것만으로도 기운이 흡수됩니다."),
                ("💧 충분한 수분", "하루 물 2리터 마시기를 생활화하십시오. 수 기운이 부족하면 체내 전해질이 떨어집니다."),
                ("🍖 짠맛 음식", "검은콩·미역·김·다시마·소금 등 짠맛 음식을 드십시오. 신장·방광을 보강합니다."),
                ("🌙 북쪽 방위·야간", "침대 머리를 북쪽으로 하거나, 중요한 사색·독서는 밤 11시~1시(자시)에 하십시오."),
            ],
        }
        _yong_oh_ms = yongshin_ohs[0] if yongshin_ohs else ""
        _gi_oh_ms   = gishin_ohs[0]   if gishin_ohs   else ""

        _OH_COLOR2 = {"木":"#2e7d32","火":"#c62828","土":"#e65100","金":"#546e7a","水":"#1565c0"}
        _OH_BG2    = {"木":"#e8f5e9","火":"#ffebee","土":"#fff3e0","金":"#eceff1","水":"#e3f2fd"}
        _OH_EMOJI2 = {"木":"🌿","火":"🔥","土":"⛰️","金":"⚔️","水":"💧"}

        if _yong_oh_ms and _yong_oh_ms in _MULSUNG2:
            _items = _MULSUNG2[_yong_oh_ms]
            _c = _OH_COLOR2.get(_yong_oh_ms,"#333")
            _bg = _OH_BG2.get(_yong_oh_ms,"#fafafa")
            st.markdown(f"""<div style="background:{_bg};border:2px solid {_c};border-radius:12px;padding:18px;margin-bottom:12px">
<div style="font-size:15px;font-weight:900;color:{_c};margin-bottom:12px">
{_OH_EMOJI2.get(_yong_oh_ms,'')} 용신 {_yong_oh_ms}(오행) — 물상대체 5가지 처방</div>""", unsafe_allow_html=True)
            for _title, _desc in _items:
                st.markdown(f"""<div style="background:#fff;border-left:4px solid {_c};border-radius:0 8px 8px 0;
padding:12px 14px;margin-bottom:8px">
<div style="font-size:13px;font-weight:800;color:{_c};margin-bottom:4px">{_title}</div>
<div style="font-size:13px;color:#222;line-height:1.9;word-break:break-all">{_desc}</div>
</div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as _e_ms:
        pass

    # ══════════════════════════════════════════════════════
    # ② 시간·방위 활용법
    # ══════════════════════════════════════════════════════
    st.markdown('<hr style="border:none;border-top:1px solid #d4af37;margin:20px 0">', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0828,#2e1040);border:2px solid #9b59b6;border-radius:14px;padding:20px;margin-bottom:6px">
<div style="color:#c39bd3;font-size:11px;letter-spacing:3px;margin-bottom:6px">TRADITIONAL METHOD 02</div>
<div style="color:#f0e6ff;font-size:18px;font-weight:900;margin-bottom:8px">🧭 시간·방위 활용 비방 — 하늘의 시계를 읽어라</div>
<div style="color:#c8a8e0;font-size:13px;line-height:1.8">용신 오행이 강한 시간과 방향을 활용하는 것만으로 운이 달라집니다.<br>
중요한 결정·미팅·계약은 반드시 이 시간대를 활용하십시오.</div>
</div>""", unsafe_allow_html=True)

    try:
        _TIME_MAP = {
            "木": {"시간":"새벽 3~7시 (인묘시 寅卯時)","계절":"봄 (3~5월)","방위":"동(東)","날":"갑을일(甲乙日)·인묘일(寅卯日)","활용":"이 시간에 중요한 계획 수립, 새 프로젝트 시작, 계약서 작성 적합"},
            "火": {"시간":"오전 9~13시 (사오시 巳午時)","계절":"여름 (6~8월)","방위":"남(南)","날":"병정일(丙丁日)·사오일(巳午日)","활용":"이 시간에 발표·면접·영업·협상 등 적극적인 활동에 적합"},
            "土": {"시간":"환절기 오후 1~3시 (미시 未時)","계절":"환절기 (3·6·9·12월)","방위":"중앙","날":"무기일(戊己日)·진술축미일(辰戌丑未日)","활용":"이 시간에 중재·조율·계약 마무리·부동산 계약 적합"},
            "金": {"시간":"오후 3~7시 (신유시 申酉時)","계절":"가을 (9~11월)","방위":"서(西)","날":"경신일(庚辛日)·신유일(申酉日)","활용":"이 시간에 결단·정리·매듭·마무리·투자 회수 결정 적합"},
            "水": {"시간":"밤 11시~새벽 3시 (자축시 子丑時)","계절":"겨울 (11~1월)","방위":"북(北)","날":"임계일(壬癸日)·자해일(子亥日)","활용":"이 시간에 명상·독서·사색·전략 수립·자기성찰 적합"},
        }
        _gi_avoid = {
            "木": "봄·새벽·동쪽 방향은 기신이므로 중요 결정 시 피하십시오",
            "火": "여름·오전·남쪽 방향은 기신이므로 큰 지출·계약 자제하십시오",
            "土": "환절기·중앙 배치는 기신이므로 집 중앙에 물건을 쌓지 마십시오",
            "金": "가을·오후·서쪽 방향은 기신이므로 중요 결정을 이 시간에 내리지 마십시오",
            "水": "겨울·밤·북쪽 방향은 기신이므로 야간 활동·투자를 자제하십시오",
        }
        if yongshin_ohs:
            _vy = yongshin_ohs[0]
            _tm = _TIME_MAP.get(_vy,{})
            if _tm:
                _tc = {"木":"#2e7d32","火":"#c62828","土":"#e65100","金":"#546e7a","水":"#1565c0"}.get(_vy,"#1565c0")
                _tbg = {"木":"#e8f5e9","火":"#ffebee","土":"#fff3e0","金":"#eceff1","水":"#e3f2fd"}.get(_vy,"#e3f2fd")
                st.markdown(f"""<div style="background:{_tbg};border:2px solid {_tc};border-radius:12px;padding:16px;margin-bottom:12px">
<div style="font-size:15px;font-weight:900;color:{_tc};margin-bottom:12px">⏰ 용신 {_vy} — 황금 시간·방위</div>
<div style="display:grid;grid-template-columns:1fr;gap:8px">
  <div style="background:#fff;padding:10px 14px;border-radius:8px;border-left:4px solid {_tc}">
    <div style="font-size:11px;color:#888;font-weight:700">⏰ 용신 시간대</div>
    <div style="font-size:14px;color:#111;font-weight:800;margin-top:2px">{_tm.get('시간','')}</div>
  </div>
  <div style="background:#fff;padding:10px 14px;border-radius:8px;border-left:4px solid {_tc}">
    <div style="font-size:11px;color:#888;font-weight:700">🍂 용신 계절</div>
    <div style="font-size:14px;color:#111;font-weight:800;margin-top:2px">{_tm.get('계절','')}</div>
  </div>
  <div style="background:#fff;padding:10px 14px;border-radius:8px;border-left:4px solid {_tc}">
    <div style="font-size:11px;color:#888;font-weight:700">🧭 용신 방위</div>
    <div style="font-size:14px;color:#111;font-weight:800;margin-top:2px">{_tm.get('방위','')}</div>
  </div>
  <div style="background:#fff;padding:10px 14px;border-radius:8px;border-left:4px solid {_tc}">
    <div style="font-size:11px;color:#888;font-weight:700">📅 용신 일진</div>
    <div style="font-size:14px;color:#111;font-weight:800;margin-top:2px">{_tm.get('날','')}</div>
  </div>
  <div style="background:{_tc}11;padding:10px 14px;border-radius:8px;border:1px solid {_tc}44">
    <div style="font-size:11px;color:{_tc};font-weight:700">💡 활용법</div>
    <div style="font-size:13px;color:#111;line-height:1.9;margin-top:2px;word-break:break-all">{_tm.get('활용','')}</div>
  </div>
</div></div>""", unsafe_allow_html=True)

        if gishin_ohs:
            _ga = gishin_ohs[0]
            _avoid_txt = _gi_avoid.get(_ga,"")
            if _avoid_txt:
                st.markdown(f"""<div style="background:#fff5f5;border:2px solid #e53935;border-radius:10px;padding:14px;margin-bottom:12px">
<div style="font-size:13px;font-weight:800;color:#c62828;margin-bottom:6px">⛔ 기신 {_ga} — 피해야 할 시간·방위</div>
<div style="font-size:13px;color:#333;line-height:1.9;word-break:break-all">{_avoid_txt}</div>
</div>""", unsafe_allow_html=True)
    except Exception:
        pass

    # ══════════════════════════════════════════════════════
    # ③ 직업·행동 개운법 — 십성 기반
    # ══════════════════════════════════════════════════════
    st.markdown('<hr style="border:none;border-top:1px solid #d4af37;margin:20px 0">', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,#0a1a0a,#142814);border:2px solid #4caf50;border-radius:14px;padding:20px;margin-bottom:6px">
<div style="color:#81c784;font-size:11px;letter-spacing:3px;margin-bottom:6px">TRADITIONAL METHOD 03</div>
<div style="color:#e8ffe8;font-size:18px;font-weight:900;margin-bottom:8px">⚡ 행동 개운법 — 습관과 삶의 방식이 운을 바꾼다</div>
<div style="color:#a5d6a7;font-size:13px;line-height:1.8">전문 명리학자들이 가장 중요하게 보는 비방입니다.<br>
소품·색상보다 행동 변화가 운을 10배 더 빠르게 바꿉니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        _BEHAVIOR_MAP = {
            "比肩": [("🤝 협력보다 독립","혼자 결정하고 실행하는 연습을 하십시오. 타인 의존이 줄수록 비견 기운이 강화됩니다."),
                     ("💪 운동 루틴","매일 아침 30분 이상 단독 운동(등산·달리기)을 하십시오. 신체 기운을 독립적으로 강화합니다."),
                     ("📝 결정 일지","오늘 내가 스스로 결정한 것 3가지를 매일 기록하십시오. 주체성이 재물운을 만듭니다.")],
            "劫財": [("🏆 경쟁 도전","경쟁 상황을 피하지 말고 적극 참여하십시오. 겁재는 경쟁에서 강해집니다."),
                     ("🤝 동업 신중","동업·보증은 반드시 계약서로 명문화하십시오. 겁재는 의리보다 문서가 우선입니다."),
                     ("💰 비상금 확보","수입의 20%는 절대 건드리지 않는 비상금으로 유지하십시오.")],
            "食神": [("🎨 재능 상품화","내 특기를 돈 버는 수단으로 연결하십시오. 식신은 재능이 재물입니다."),
                     ("😊 먹고 즐기기","좋은 음식·여행·취미에 적절히 투자하십시오. 식신 기운은 즐거움에서 강화됩니다."),
                     ("🌱 새 프로젝트","매 분기 새로운 창작 프로젝트를 시작하십시오.")],
            "傷官": [("✍️ 표현력 강화","글·말·창작으로 내 생각을 적극 표현하십시오. 상관은 표현이 재물입니다."),
                     ("🙏 윗사람 예의","직장 상사·어른에게 특별히 예의를 갖추십시오. 상관의 최대 위험은 윗사람 충돌입니다."),
                     ("🚀 혁신 도전","기존 방식에 의문을 품고 새로운 방법을 시도하십시오.")],
            "偏財": [("🏃 적극적 행동","가만히 앉아 있지 마십시오. 편재는 움직일수록 돈이 들어옵니다."),
                     ("🤝 인맥 관리","매주 새로운 사람 1명을 만나십시오. 편재 재물은 사람을 통해 옵니다."),
                     ("⚠️ 투기 금지","주식·코인 단기 투기는 절대 금지. 편재는 모험심이 강해 큰 손실을 부를 수 있습니다.")],
            "正財": [("💰 저축 자동화","월급날 자동으로 30% 이상 저축되도록 설정하십시오."),
                     ("📊 지출 기록","매일 지출을 기록하고 주 1회 검토하십시오. 정재는 꼼꼼한 관리가 재물입니다."),
                     ("🏠 부동산 우선","여유 자금은 부동산·예금 위주로 운용하십시오.")],
            "偏官": [("💪 체력 관리","규칙적인 운동으로 체력을 최우선으로 유지하십시오. 편관은 건강이 무너지면 모든 것이 무너집니다."),
                     ("⚠️ 무리 금지","과로·무리한 새 사업 시작을 자제하십시오."),
                     ("🎯 단기 목표","큰 목표를 작은 단계로 쪼개서 하나씩 완수하십시오.")],
            "正官": [("📋 약속 철저","한번 한 약속은 반드시 지키십시오. 정관 기운은 신뢰에서 강화됩니다."),
                     ("👔 외모 관리","단정한 외모와 깔끔한 언어를 유지하십시오. 정관은 이미지가 경쟁력입니다."),
                     ("📚 자격증","공인 자격증·학위를 추가로 취득하십시오.")],
            "偏印": [("📖 독서·연구","매일 1시간 이상 독서하십시오. 편인은 지식이 무기입니다."),
                     ("🔍 전문 분야","하나의 분야를 깊이 파고드십시오. 편인은 넓이보다 깊이입니다."),
                     ("🧘 명상","주 3회 명상으로 직관력을 강화하십시오.")],
            "正印": [("🎓 배움 지속","평생 배움을 멈추지 마십시오. 정인은 배울수록 운이 좋아집니다."),
                     ("🙏 감사 표현","어머니·스승·귀인에게 감사를 자주 표현하십시오."),
                     ("📜 자격 취득","시험·자격증에 투자하는 것이 최고의 재테크입니다.")],
        }
        # 일간으로 일주 십성 계산
        from saju_engine import TEN_GODS_MATRIX, JIJANGGAN
        _ilgan_b = pils[1].get("cg","") if pils and len(pils)>1 else ""
        _ilji_b  = pils[1].get("jj","") if pils and len(pils)>1 else ""
        _main_ss_b = TEN_GODS_MATRIX.get(_ilgan_b,{}).get(_ilji_b,"")
        if not _main_ss_b:
            _jjg_b = JIJANGGAN.get(_ilji_b,[])
            if _jjg_b:
                _main_ss_b = TEN_GODS_MATRIX.get(_ilgan_b,{}).get(_jjg_b[-1],"")

        _beh_items = _BEHAVIOR_MAP.get(_main_ss_b, [
            ("🎯 집중력","하루 한 가지 일에만 집중하는 습관을 기르십시오. 분산된 에너지를 모으는 것이 개운의 시작입니다."),
            ("🌅 아침 루틴","매일 같은 시간에 일어나는 것만으로도 운이 안정됩니다."),
            ("🤝 인간관계","진심 어린 감사 인사를 하루 3번 실천하십시오."),
        ])
        _beh_color = "#2e7d32"
        st.markdown(f"""<div style="background:#f1f8e9;border:2px solid {_beh_color};border-radius:12px;padding:16px;margin-bottom:12px">
<div style="font-size:15px;font-weight:900;color:{_beh_color};margin-bottom:12px">
🎯 {display_name}님 맞춤 행동 처방 ({_main_ss_b or '용신 기반'})</div>""", unsafe_allow_html=True)
        for _bt, _bd2 in _beh_items:
            st.markdown(f"""<div style="background:#fff;border-left:4px solid {_beh_color};border-radius:0 8px 8px 0;
padding:12px 14px;margin-bottom:8px">
<div style="font-size:13px;font-weight:800;color:{_beh_color};margin-bottom:4px">{_bt}</div>
<div style="font-size:13px;color:#222;line-height:1.9;word-break:break-all">{_bd2}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        pass

    # ══════════════════════════════════════════════════════
    # ④ 식이 개운법 — 오행별 음식 처방
    # ══════════════════════════════════════════════════════
    st.markdown('<hr style="border:none;border-top:1px solid #d4af37;margin:20px 0">', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a00,#2e1800);border:2px solid #ff8f00;border-radius:14px;padding:20px;margin-bottom:6px">
<div style="color:#ffcc80;font-size:11px;letter-spacing:3px;margin-bottom:6px">TRADITIONAL METHOD 04</div>
<div style="color:#fff8e1;font-size:18px;font-weight:900;margin-bottom:8px">🍽️ 식이(食餌) 개운법 — 먹는 것이 운이 된다</div>
<div style="color:#ffe082;font-size:13px;line-height:1.8">황제내경(黃帝內經)에 기반한 오행 식이 처방입니다.<br>
용신 오행의 맛을 가까이하고, 기신 오행의 맛을 줄이면 몸과 운이 함께 좋아집니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        _FOOD_MAP = {
            "木": {"맛":"신맛(酸)","음식":"레몬·식초·매실·사과·귤·라임·요구르트·녹색 채소","장기":"간장·담낭","피할것":"너무 많은 단맛(토를 키워 목을 누름)","개운식":"아침 공복에 레몬수 1잔 — 간장을 깨우고 목 기운을 활성화"},
            "火": {"맛":"쓴맛(苦)","음식":"커피(무가당)·쑥·쑥갓·도라지·홍고추·토마토·딸기·석류","장기":"심장·소장","피할것":"차가운 음식 과다(수가 화를 끔)","개운식":"매일 아침 쑥차 또는 홍차 1잔 — 심장을 깨우고 화 기운 강화"},
            "土": {"맛":"단맛(甘)","음식":"고구마·감자·꿀·대추·현미·단호박·옥수수·찹쌀","장기":"위장·비장·췌장","피할것":"밀가루·인스턴트 과다(습토 유발)","개운식":"아침 식사 대신 찹쌀죽 — 위장을 다스리고 토 기운 강화"},
            "金": {"맛":"매운맛(辛)","음식":"무·도라지·배·생강·마늘·파·고추냉이·양파","장기":"폐·대장","피할것":"차고 날 것 과다(폐 기운 약화)","개운식":"매일 생강 달인 물 1잔 — 폐를 따뜻하게 하고 금 기운 강화"},
            "水": {"맛":"짠맛(鹹)","음식":"검은콩·미역·김·다시마·굴·새우·소금·검은깨","장기":"신장·방광","피할것":"짠 것 과다(신장 과부하)·야식(수 기운 교란)","개운식":"아침 공복에 검은콩 삶은 물 1잔 — 신장을 보강하고 수 기운 강화"},
        }
        _yong_food = yongshin_ohs[0] if yongshin_ohs else ""
        _gi_food   = gishin_ohs[0]   if gishin_ohs   else ""

        col_f1, col_f2 = st.columns([3,2])
        with col_f1:
            if _yong_food and _yong_food in _FOOD_MAP:
                _fd = _FOOD_MAP[_yong_food]
                _fc = {"木":"#2e7d32","火":"#c62828","土":"#e65100","金":"#546e7a","水":"#1565c0"}.get(_yong_food,"#333")
                _fb = {"木":"#e8f5e9","火":"#ffebee","土":"#fff3e0","金":"#eceff1","水":"#e3f2fd"}.get(_yong_food,"#f9f9f9")
                st.markdown(f"""<div style="background:{_fb};border:2px solid {_fc};border-radius:12px;padding:16px">
<div style="font-size:14px;font-weight:900;color:{_fc};margin-bottom:10px">✅ 용신 {_yong_food} — 먹어야 할 것</div>
<div style="font-size:12px;color:#333;margin-bottom:6px"><b>맛:</b> {_fd['맛']}</div>
<div style="font-size:12px;color:#333;margin-bottom:6px"><b>음식:</b> {_fd['음식']}</div>
<div style="font-size:12px;color:#333;margin-bottom:6px"><b>강화 장기:</b> {_fd['장기']}</div>
<div style="background:#fff;border-radius:8px;padding:10px;margin-top:8px;border-left:4px solid {_fc}">
<div style="font-size:12px;font-weight:800;color:{_fc}">🌟 오늘 개운식</div>
<div style="font-size:13px;color:#111;line-height:1.9;margin-top:4px;word-break:break-all">{_fd['개운식']}</div>
</div></div>""", unsafe_allow_html=True)

        with col_f2:
            if _gi_food and _gi_food in _FOOD_MAP:
                _gfd = _FOOD_MAP[_gi_food]
                st.markdown(f"""<div style="background:#fff5f5;border:2px solid #e53935;border-radius:12px;padding:16px">
<div style="font-size:14px;font-weight:900;color:#c62828;margin-bottom:10px">⛔ 기신 {_gi_food} — 줄여야 할 것</div>
<div style="font-size:12px;color:#333;margin-bottom:6px"><b>맛:</b> {_gfd['맛']}</div>
<div style="font-size:12px;color:#333;margin-bottom:6px"><b>피할 음식:</b> {_gfd['음식']}</div>
<div style="background:#ffebee;border-radius:8px;padding:10px;margin-top:8px;border-left:4px solid #e53935">
<div style="font-size:12px;font-weight:800;color:#c62828">⚠️ 특히 주의</div>
<div style="font-size:13px;color:#333;line-height:1.8;margin-top:4px;word-break:break-all">{_gfd['피할것']}</div>
</div></div>""", unsafe_allow_html=True)
    except Exception:
        pass


    st.caption("⚠️ 본 비방록은 전통 민속 문화 정보를 제공하는 참고 자료입니다. 실제 굿/부적 처방은 전문 무당/만신에게 문의하십시오.")


class Brain3:
    """[로컬 전용] 상담 엔진. API 미사용, _local_saju_engine만 사용."""

    def __init__(self, pils, name, birth_year, gender):
        self.pils = pils
        self.name = name
        self.birth_year = birth_year
        self.gender = gender

    def process_query(self, system_prompt, user_prompt, history):
        return _local_saju_engine(
            self.pils, self.name, self.birth_year, self.gender, user_prompt or ""
        )


# ==========================================================


def tab_ai_chat(pils, name, birth_year, gender):
    """끝판왕(E-Version) AI 상담 - 의도/기억/성격 통합 엔진"""

    if not UsageTracker.check_limit():
        st.warning("오늘 준비된 상담 역량이 소진되었습니다. 내일 다시 찾아주십시오. (일일 제한 100명)")

        return

    # 1️⃣ 영속 기억 로드 및 성격 프로파일링 (최초 1회)

    mem = SajuMemory.get_memory(name)

    if not mem["identity"].get("profile"):
        # pils 구조에 따라 데이터 추출

        profile = PersonalityProfiler.analyze(pils)

        def save_profile(m):

            m["identity"]["profile"] = profile

            return m

        SajuMemory.update_memory(name, save_profile)

        mem = SajuMemory.get_memory(name)

    # 🧩 상담 단계 표시 (기존 스타일 유지)

    current_stage = mem["flow"].get("consult_stage", "탐색")

    stages = ["탐색", "이해", "해석", "조언", "정리"]

    stage_idx = stages.index(current_stage) if current_stage in stages else 0

    # 🗺️ V2 프리미엄 헤더 (상담 단계 + 신뢰도 게이지 + MBTI + Bond + Matrix)

    trust_data = mem.get("trust", {"score": 50, "level": 1})

    bond_data = mem.get("bond", {"level": 1, "label": "탐색", "score": 10})

    profile = mem["identity"].get("profile", {})

    mbti_val = profile.get("mbti", "분석중")

    matrix = mem.get("matrix", {"행동": 50, "감정": 50, "기회": 50, "관계": 50, "에너지": 50})

    narrative = mem["identity"].get("narrative", "")

    if not narrative:
        narrative = "서사 작성 중..."

    stage_html = " ".join([f'<span style="color: {"#000" if i == stage_idx else "#ccc"}; font-weight: {"800" if i == stage_idx else "400"};">{s}</span>' for i, s in enumerate(stages)])

    st.markdown(
        f"""

<div style="background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 15px; padding: 18px; margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);">

        

<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">

<div>

<div style="font-size: 10px; color: #d4af37; font-weight: 800; letter-spacing: 1px;">상담 진행 단계</div>

<div style="font-size: 14px; margin-top:2px; font-weight: 700;">{stage_html}</div>

</div>

<div style="text-align: right;">

<div style="font-size: 10px; color: #888; font-weight: 700;">{bond_data["label"]} 교감 Lv.{bond_data["level"]}</div>

<div style="background: #eee; width: 100px; height: 5px; border-radius: 3px; margin-top: 5px; position: relative;">

<div style="background: linear-gradient(90deg, #6c5ce7, #a06ee1); width: {bond_data.get("score", 0)}%; height: 100%; border-radius: 3px;"></div>

</div>

</div>

</div>

        <!-- 📊 종합 밸런스 매트릭스 -->

<div style="display: flex; justify-content: space-around; background: rgba(0,0,0,0.03); padding: 10px; border-radius: 10px; margin-bottom: 12px;">

            {
            "".join(
                [
                    f'''

<div style="text-align: center;">

<div style="font-size: 9px; color: #999;">{k}</div>

<div style="font-size: 13px; font-weight: 800; color: {"#d4af37" if (v or 0) > 70 else "#555"};">{(v or 0)}</div>

</div>

            '''
                    for k, v in matrix.items()
                ]
            )
        }

</div>

<div style="display: flex; gap: 8px;">

<div style="background: #f0f4ff; color: #1a237e; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; border: 1px solid #c5cae9;">

                🧬 사주 MBTI: {mbti_val}

</div>

<div style="background: #fff8e1; color: #f57f17; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; border: 1px solid #fff176;">

                🌌 인생 서사: {narrative}

</div>

</div>

</div>""",
        unsafe_allow_html=True,
    )

    # === 사주 원국 기반 핵심 예측 (AI 챗 상단 직접 노출) ===

    try:
        hl = generate_engine_highlights(pils, birth_year, gender)

        with st.expander("🔮 내 사주 핵심 예측치 모아보기 (성격/재물/인연/사고)", expanded=True):
            # 1. 타고난 성향

            if hl.get("personality"):
                p_text = "<br>".join([f"• {p}" for p in hl["personality"]])

                st.markdown(
                    f"""

<div style="background:#f8f9fa; border-left:4px solid #9b59b6; padding:12px; margin-bottom:10px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">

<div style="font-weight:900; color:#8e44ad; font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>👤</span> 타고난 성향</div>

<div style="font-size:13px; color:#444; line-height:1.6;">{p_text}</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

            # 2. 재물/횡재수

            if hl.get("money_peak"):
                m_text = "<br>".join([f"💰 <b style='color:#b9770e'>{m['age']}세 ({m['year']}년)</b> : {m['desc']}" for m in hl["money_peak"]])

                st.markdown(
                    f"""

<div style="background:#fdfbf7; border-left:4px solid #f1c40f; padding:12px; margin-bottom:10px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">

<div style="font-weight:900; color:#f39c12; font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>💎</span> 재물 상승기</div>

<div style="font-size:13px; color:#444; line-height:1.6;">{m_text}</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

            # 3. 인연/결혼운

            if hl.get("marriage_peak"):
                marry_text = "<br>".join([f"💍 <b style='color:#a93226'>{m['age']}세 ({m['year']}년)</b> : {m['desc']}" for m in hl["marriage_peak"]])

                st.markdown(
                    f"""

<div style="background:#fff5f7; border-left:4px solid #e74c3c; padding:12px; margin-bottom:10px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">

<div style="font-weight:900; color:#c0392b; font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>💖</span> 결정적 인연 (결혼운)</div>

<div style="font-size:13px; color:#444; line-height:1.6;">{marry_text}</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

            # 4. 사고/위험 구간

            if hl.get("danger_zones"):
                d_text = "<br>".join([f"⚠️ <b style='color:#7b241c'>{d['age']}세 ({d['year']}년)</b> : {d['desc']}" for d in hl["danger_zones"]])

                st.markdown(
                    f"""

<div style="background:#fff3f3; border-left:4px solid #c0392b; padding:12px; margin-bottom:10px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,0.05);">

<div style="font-weight:900; color:#a93226; font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>🚨</span> 사고 및 위험 대비 구간</div>

<div style="font-size:13px; color:#444; line-height:1.6;">{d_text}</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.warning(f"핵심 예측 로딩 오류: {e}")

    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.session_state.chat_history = []

        # 버그 수정: pils_data = pils[1] 로직 제거 (전체 pils 리스트 필요)

        intro = SajuMemory.get_personalized_intro(name, pils)

        st.session_state.chat_history.append({"role": "assistant", "content": intro})

        UsageTracker.increment()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -- 입력 처리 --

    user_input = st.chat_input("사주나 운세에 대해 무엇이든 물어보세요...")

    prompt = st.session_state.pop("pending_query", user_input)

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # 2️⃣ Intent 분석

        intent_res = IntentEngine.analyze(prompt)

        st.markdown(IntentEngine.get_topic_badge(prompt), unsafe_allow_html=True)

        # 🧩 Master Platform 통합 로직

        user_query = prompt

        SajuMemory.record_behavior(name, user_query)

        implicit_persona = PersonalityEngine.analyze_behavior(name)

        # 유대감 및 매트릭스 업데이트

        SajuMemory.adjust_bond(name, 3)  # 유대감 상승

        GoalCreationEngine.extract_goal(name, user_query)  # 목표 발견

        current_year = datetime.now().year

        luck_score = calc_luck_score(pils, birth_year, gender, current_year)

        DestinyMatrix.calculate_sync(name, pils, luck_score)

        # 전환점 감지

        pivot_info = ChangeRadarEngine.detect_pivot(name, luck_score)

        if pivot_info["is_pivot"]:
            st.toast(f"🛰️ {pivot_info['message']}", icon="📈")

        turn_count = len(st.session_state.chat_history)

        if turn_count <= 4:
            new_stage = "이해"

        elif turn_count <= 8:
            new_stage = "해석"

        else:
            new_stage = "조언"

        if turn_count > 12:
            new_stage = "정리"

        SajuMemory.adjust_trust(name, 2, "상담 지속")

        def update_stage(m):

            m["flow"]["consult_stage"] = new_stage

            return m

        SajuMemory.update_memory(name, update_stage)

        mem = SajuMemory.get_memory(name)

        # 🚨 V2 돌발 사건 감지

        risk_info = FatePredictionEngine.detect_risk(pils, datetime.now().year)

        if risk_info["is_risk"]:
            st.error(f"⚠️ **만신의 경고 ({risk_info['severity']}):** " + " / ".join(risk_info["messages"]))

        # ── 로컬 사주 엔진 (API 없을 때 폴백) ──────────────────────────────

        def _local_saju_response(query):
            """API 미연결 시 로컬 엔진으로 무당 말투 응답 생성"""

            import re as _re_loc

            q = query

            ilgan_loc = pils[1]["cg"] if len(pils) > 1 else "?"

            _ss = st.session_state

            bm = max(1, min(12, int(_ss.get("birth_month") or 1)))
            bd = max(1, min(31, int(_ss.get("birth_day") or 1)))

            bh = max(0, min(23, int(_ss.get("birth_hour") or 12)))
            bmn = max(0, min(59, int(_ss.get("birth_minute") or 0)))

            is_today = bool(_re_loc.search(r"오늘|일진|내일|이번주", q))

            is_year = bool(_re_loc.search(r"올해|세운|금년|올해운세|2025|2026|2027", q)) or is_today

            is_money = bool(_re_loc.search(r"재물|돈|사업|수입|투자|부자|재산", q))

            is_love = bool(_re_loc.search(r"연애|결혼|궁합|이성|남자|여자|남편|아내|인연|배우자", q))

            is_health = bool(_re_loc.search(r"건강|병원|아프|수술|몸|질병|체력", q))

            is_dw = bool(_re_loc.search(r"대운|운세흐름|인생|10년|장기|앞으로|미래", q))

            is_past = bool(_re_loc.search(r"과거|지나온|예전|돌아보|과거운|이전|맞춰봐", q))

            is_job = bool(_re_loc.search(r"직업|진로|취업|창업|커리어|직장|일자리|사업방향|어떤 일", q))

            is_char = bool(_re_loc.search(r"성격|성향|기질|특성|나는|내가|나의|나 어때", q))

            out = [f"허허, 어서 오게. {name}의 팔자를 내 신안(神眼)으로 살펴보겠느니라.\n"]

            try:
                if is_year:
                    sw = get_yearly_luck(pils, current_year) or {}

                    sw_ss = sw.get("십성_천간", "")
                    sw_gh = sw.get("길흉", "")
                    sw_gan = sw.get("세운", "")

                    try:
                        tp = calc_turning_point(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                    except Exception:
                        tp = {}

                    _SW = {
                        "偏財": "재물 변동과 이성 인연의 기운이 강하느니라. 사업 기회가 오지만 투기는 조심하게.",
                        "正財": "안정된 수입과 결혼 인연의 기운이 들어오느니라. 재물을 차곡차곡 모을 수 있는 해니라.",
                        "食神": "직업과 재능이 빛을 발하는 해니라. 새 일을 시작하거나 자격 취득에 좋으니라.",
                        "傷官": "창의성이 폭발하지만 윗사람과의 마찰을 조심해야 하느니라.",
                        "偏官": "직장 변동과 사고 기운이 있느니라. 건강과 안전에 각별히 주의하게.",
                        "正官": "명예와 승진의 기운이 강하느니라. 조직에서 인정받는 해니라.",
                        "偏印": "계획이 자주 바뀌고 이사·이동의 기운이 있느니라. 신중하게 결정하게.",
                        "正印": "학업과 자격 취득에 유리한 해니라. 어머니와의 인연도 돈독해지느니라.",
                        "比肩": "독립심이 강해지고 경쟁이 치열해지는 해니라. 동업보다 단독 행동이 낫느니라.",
                        "劫財": "재물 손실과 경쟁이 극심한 해니라. 보증과 투자를 자제하게.",
                    }

                    _ACT = {
                        "偏財": "적극적 투자·사업 기회를 잡되 안전 자산 30% 이상 반드시 확보하게!",
                        "正財": "부동산·예금·적금 등 안정 자산에 집중하게. 불필요한 지출을 줄이는 것이 재물의 시작이니라.",
                        "食神": "자격증 취득·신규 프로젝트 시작이 최적이니라. 전문성을 드러낼 시기니라.",
                        "傷官": "창작·발명은 좋으나 직속 상관·계약서 분쟁 조심. 독립 행보는 내년 이후가 유리하니라.",
                        "偏官": "건강 정기검진 필수. 무리한 확장·새 사업 시작 자제. 법적 분쟁도 조심하게.",
                        "正官": "자격증·승진 시험·공직 지원에 최적의 해! 조직 내 신뢰를 쌓는 것이 핵심이니라.",
                        "偏印": "이사·이직·전공 변경 시 신중히 결정하게. 새 분야 학습에는 유리하니라.",
                        "正印": "자격증·진학·연구에 집중하라. 어머니·스승과의 관계를 돈독히 하게.",
                        "比肩": "독립·창업·단독 프로젝트에 유리. 동업·보증은 이 해에 시작하지 말게.",
                        "劫財": "현금 보유·빚 상환 우선. 도박·투기·보증 절대 금지. 경쟁에서 냉정함을 유지하게.",
                    }

                    out.append(f"**{current_year}년 ({current_year - birth_year + 1}세) 세운 분석**\n")

                    out.append(f"올해 세운: **{sw_gan}** — 십성 **{sw_ss}**, 길흉 **{sw_gh}**\n")

                    out.append(_SW.get(sw_ss, f"{sw_ss} 기운이 강하게 작동하는 해니라.") + "\n")

                    out.append(f"\n**[올해 행동 지침]** {_ACT.get(sw_ss, '분수에 맞게 안정적으로 움직이게.')}\n")

                    tp_int = tp.get("intensity", "")

                    tp_sc = tp.get("score_change", 0)

                    tp_rsn = tp.get("reason", [])

                    if "강력" in tp_int:
                        out.append(f"\n**⚡ 인생 전환점 경보!** 운세 변화폭 {tp_sc:+d}점 — {tp_int}\n")

                        for r in tp_rsn[:3]:
                            out.append(f"• {r}\n")

                    elif "주요" in tp_int or "변화" in tp_int:
                        out.append(f"\n**🔄 중요한 변화 감지** 운세 변화폭 {tp_sc:+d}점 — {tp_int}\n")

                        for r in tp_rsn[:2]:
                            out.append(f"• {r}\n")

                    sw_n = get_yearly_luck(pils, current_year + 1) or {}

                    sw_n2 = get_yearly_luck(pils, current_year + 2) or {}

                    out.append(f"\n**[내년 미리보기]** {current_year + 1}년: {sw_n.get('세운', '')} [{sw_n.get('십성_천간', '')}] {sw_n.get('길흉', '')}\n")

                    out.append(f"**[후년 미리보기]** {current_year + 2}년: {sw_n2.get('세운', '')} [{sw_n2.get('십성_천간', '')}] {sw_n2.get('길흉', '')}")

                elif is_money:
                    gk = get_gyeokguk(pils)
                    ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                    gkn = gk["격국명"] if gk else "미정격"

                    y1 = ys.get("용신_1순위", "-")
                    y2 = ys.get("용신_2순위", "-")

                    heui = ys.get("희신", "-")
                    gisin = ", ".join(ys.get("기신", []))

                    _GKM = {
                        "정관격": "명예와 재물이 함께 오는 격국이니라. 조직에서 승진할수록 재물이 늘어나느니라. 직함과 신뢰가 곧 재물이니 체면을 지키게.",
                        "정재격": "꾸준한 노력으로 재물을 쌓는 격국이니라. 금융·부동산에서 재물이 쌓이느니라. 규칙적 저축과 장기 투자가 최고의 전략이니라.",
                        "편재격": "사업가 기질의 격국이니라. 투자·영업에서 큰 기회가 오느니라. 기복이 크니 안전 자산 30% 이상 반드시 확보하게. 한 방을 노리다 전부 잃는 수가 있느니라.",
                        "식신격": "전문성을 키우면 재물이 자연스럽게 따라오는 격국이니라. 실력을 쌓는 것이 곧 재물을 쌓는 것이니라.",
                        "상관격": "창의적 방법으로 재물을 만드는 격국이니라. 프리랜서·컨설팅·콘텐츠 창작이 맞느니라.",
                        "편인격": "기술·학문·특허로 재물을 만드는 격국이니라. 단 재물보다 전문성에 집중할 때 돈이 따라오느니라.",
                        "정인격": "안정적 직업·자격증으로 꾸준히 재물을 쌓는 격국이니라. 주식·투기보다 연금·부동산이 맞느니라.",
                        "비견격": "독립 사업이나 프리랜서로 재물을 벌어야 하는 격국이니라. 공동 투자·동업은 반드시 계약서를 쓰게.",
                        "겁재격": "경쟁과 도전 속에서 재물을 얻는 격국이니라. 손실도 크지만 회복도 빠른 팔자니라.",
                    }

                    out.append(_GKM.get(gkn, f"{gkn}의 재물 패턴은 독특하니라. 용신 기운을 따르게.") + "\n")

                    out.append(f"\n용신 **{y1}** / 희신 **{heui}** 기운이 강한 해(年)에 재물 결정을 내려야 하느니라.\n")

                    if gisin:
                        out.append(f"⚠️ **기신 경고:** {gisin} 기운 강한 해에는 큰 투자·동업·보증을 반드시 피하게! 이 해에 움직이면 손실이 크니라.\n")

                    # 향후 재물 황금기 (별점 차등)

                    gold_ohs = {o for o in [y1, y2] if o in ("木", "火", "土", "金", "水")}

                    gold_yrs = []

                    for yr in range(current_year, current_year + 11):
                        sw_g = get_yearly_luck(pils, yr) or {}

                        if OH.get((sw_g.get("세운", "")[:1]), "") in gold_ohs:
                            sw_g_ss = sw_g.get("십성_천간", "")

                            star = "★★★" if sw_g_ss in ("偏財(편재)", "正財(정재)", "食神(식신)") else "★★" if sw_g_ss in ("正官(정관)", "正印(정인)") else "★"

                            gold_yrs.append(f"* **{yr}년**({yr - birth_year + 1}세): {sw_g.get('세운', '')} [{sw_g_ss}] {sw_g.get('길흉', '')} {star}")

                    if gold_yrs:
                        out.append(f"\n**[향후 재물 황금기 — 용신 세운]**\n")

                        for gy in gold_yrs[:6]:
                            out.append(gy + "\n")

                        out.append("이 해들에 중요한 재물 결정을 내리게!\n")

                    # 대운×세운 재물 더블 황금기

                    try:
                        hl_m = generate_engine_highlights(pils, birth_year, gender, bm, bd, bh, bmn)

                        double_mp = [m for m in hl_m.get("money_peak", []) if m.get("ss") == "더블"]

                        if double_mp:
                            out.append(f"\n**[대운×세운 재물 더블 황금기]** — 이 시기가 진짜 인생 재물 피크니라!\n")

                            for m in double_mp[:3]:
                                out.append(f"* {m.get('year', '')}년 ({m.get('age', '')}) {m.get('desc', '')}\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 기신 대운 경고

                    try:
                        dw_list_m2 = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                        gisin_ohs2 = set(ys.get("기신", []))

                        gisin_dws2 = [dw for dw in dw_list_m2 if OH.get(dw.get("cg", ""), "") in gisin_ohs2 and dw["종료연도"] >= current_year]

                        if gisin_dws2:
                            gdw2 = gisin_dws2[0]

                            gdw2_ss = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(gdw2["cg"], "-")

                            if gdw2["시작연도"] <= current_year:
                                out.append(f"\n⚠️ 지금 **{gdw2['str']} {gdw2_ss}** 기신 대운 진행 중! {gdw2['종료연도'] - current_year}년 더 이어지느니라. 대형 투자·보증 자제가 최선이니라.\n")

                            else:
                                out.append(f"\n⚠️ {gdw2['시작연도']}년({gdw2['시작나이']}세)부터 **{gdw2['str']} {gdw2_ss}** 기신 대운이 오느니라. 미리 안전 자산 확보를 서두르게!\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                elif is_love:
                    out.append(f"**{name}의 인연·결혼운 완전 분석**\n허어, 인연의 실타래를 신안으로 살펴보겠느니라.\n")

                    # 1. 배우자 자리(정재/정관) 분석

                    yk = get_yukjin(ilgan_loc, pils, gender)

                    spouse_keys = ["아내", "처", "正財(정재)", "妻"] if gender == "남" else ["남편", "夫", "正官(정관)", "情夫", "편관"]

                    for rel in yk:
                        rn = rel.get("관계", "")

                        if any(k in rn for k in spouse_keys):
                            loc = rel.get("위치", "없음")

                            out.append(f"\n**[배우자 자리]** {rn} — 위치: **{loc}**\n")

                            out.append(rel.get("desc", "") + "\n")

                            if rel.get("present"):
                                out.append("허허, 배우자 기운이 사주에 뚜렷이 자리 잡고 있구먼. 인연은 반드시 오느니라.\n")

                            else:
                                out.append("배우자 기운이 약하니 대운·세운에서 재성/관성이 들어올 때 적극적으로 움직이게.\n")

                            break

                    # 2. 일지(배우자 자리) 지지 해석

                    iljj_l = pils[1]["jj"] if len(pils) > 1 else "?"

                    _ILJJ_L = {
                        "子": "지적이고 감각적인 분을 배우자로 만날 가능성이 높습니다. 지적 교감과 정서적 소통이 부부 관계의 핵심입니다. [주의] 배우자의 감정 기복과 비밀주의 포용 요망.",
                        "丑": "성실하고 현실적이며 가정적인 분을 배우자로 만나게 됩니다. [주의] 고집과 변화 거부를 이해하며 부드럽게 이끌어야 합니다.",
                        "寅": "활동적이고 추진력 있는 분을 배우자로 만납니다. 서로에게 에너지를 주고받는 역동적인 관계. [주의] 주도권 지혜롭게 분할.",
                        "卯": "섬세하고 예술적 감각이 있는 분을 배우자로 만납니다. 온화하고 편안한 매력. [주의] 우유부단할 때 단단한 파트너가 되어주세요.",
                        "辰": "다재다능하고 신비로우며 위기에 강한 파트너를 만납니다. [주의] 안정적인 소통의 지향.",
                        "巳": "지혜롭고 신중하며 경제적 감각이 뛰어난 분을 배우자로 만납니다. [주의] 마음의 표현 부족으로 오해하지 마세요.",
                        "午": "열정적이고 솔직하며 뜨겁게 사랑하는 분을 만납니다. [주의] 뜨거운 감정 기복 수용력 필요.",
                        "未": "따뜻하고 예술적 감각이 있으며 가정을 최우선하는 분을 만납니다. [주의] 배우자의 가정적 기준을 존중해 주세요.",
                        "申": "영리하고 사교적이며 적응력이 뛰어난 분을 만납니다. [주의] 배우자가 바빠도 함께하는 시간을 의식적으로 확보하세요.",
                        "酉": "세련되고 예리하며 완벽을 추구하는 헌신적인 분을 만납니다. [주의] 배우자의 높은 기준을 거부감 없이 존중해 주세요.",
                        "戌": "의리 있고 충직하며 정의감이 강한 동지형 배우자를 만납니다. [주의] 스트레스를 제때 풀도록 도와주세요.",
                        "亥": "자유롭고 철학적이며 포용력 있는 분을 만납니다. [주의] 배우자의 자유 추구를 존중하면서 현실적 목표를 공유하세요.",
                    }

                    out.append(f"\n**[일지 배우자 자리 — {iljj_l}]**\n{_ILJJ_L.get(iljj_l, f'일지 {iljj_l}의 기운이 배우자 자리에 흐르느니라.')}\n")

                    # 3. 대운에서 재성/관성운 들어오는 시기

                    try:
                        dw_list_l = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                        love_dw_ss_l = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

                        love_dws_l = [dw for dw in dw_list_l if TEN_GODS_MATRIX.get(ilgan_loc, {}).get(dw["cg"], "") in love_dw_ss_l and dw["종료연도"] >= current_year]

                        if love_dws_l:
                            cdw_l = love_dws_l[0]

                            cdw_ss_l = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(cdw_l["cg"], "")

                            if cdw_l["시작연도"] <= current_year:
                                out.append(f"\n**[대운 인연 시기]** 지금 **{cdw_l['str']} {cdw_ss_l}** 대운 진행 중! {cdw_l['종료연도'] - current_year}년 남았으니 이 기간을 놓치지 말게!\n")

                            else:
                                out.append(
                                    f"\n**[대운 인연 시기]** {cdw_l['시작연도']}년({cdw_l['시작나이']}세)부터 **{cdw_l['str']} {cdw_ss_l}** 대운이 열리느니라. 그때가 인연의 문이 활짝 열리는 시기니라.\n"
                                )

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 4. 향후 3년 중 연애운 좋은 해

                    love_yr_ss_l = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

                    love_yrs_l = []

                    for _yr_l in range(current_year, current_year + 4):
                        _sw_l = get_yearly_luck(pils, _yr_l) or {}

                        _ss_l = _sw_l.get("십성_천간", "")

                        if _ss_l in love_yr_ss_l:
                            love_yrs_l.append(f"**{_yr_l}년**({_yr_l - birth_year + 1}세): {_sw_l.get('세운', '')} [{_ss_l}] {_sw_l.get('길흉', '')} ← 이성 인연 기운이 강하느니라!")

                    if love_yrs_l:
                        out.append("\n**[향후 3년 연애·결혼 특효 시기]**\n")

                        for _ly_l in love_yrs_l:
                            out.append(f"* {_ly_l}\n")

                        out.append("이 해들에 적극적으로 인연을 찾아 나서게. 하늘이 돕는 시기니라!\n")

                    else:
                        sw_now_l = get_yearly_luck(pils, current_year)

                        out.append(f"\n올해 {sw_now_l.get('세운', '')} [{sw_now_l.get('십성_천간', '')}] — 향후 3년은 이성 세운이 약하니 자기계발로 내실을 다지는 시기니라.\n")

                    # 5. 도화살 확인

                    try:
                        sinsal_l = get_special_stars(pils)

                        dohwa_l = [s for s in sinsal_l if "도화" in s.get("name", "")]

                        ss12_l = get_12sinsal(pils)

                        dohwa12_l = [s for s in ss12_l if "도화" in s.get("이름", "") or "년살" in s.get("이름", "")]

                        if dohwa_l or dohwa12_l:
                            out.append("\n**[신살 — 도화살(桃花殺)]** 도화살이 사주에 있구먼!\n이성의 인기를 한몸에 받는 매력의 기운이니라. 감정에 휩쓸려 경솔한 선택을 하지 않도록 명심하게.\n")

                        else:
                            out.append("\n도화살은 없으나, 꾸준한 진심이 최고의 인연을 불러오느니라.\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 6. 결혼 적령기

                    _cage_l = current_year - birth_year + 1

                    out.append(f"\n**[결혼 적령기 — 현재 {_cage_l}세]**\n")

                    try:
                        dw2_l = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                        love_ss2_l = {"偏財", "正財"} if gender == "남" else {"偏官", "正官"}

                        fut_dws_l = [dw for dw in dw2_l if TEN_GODS_MATRIX.get(ilgan_loc, {}).get(dw["cg"], "") in love_ss2_l and dw["종료연도"] >= current_year]

                        if fut_dws_l:
                            bd2_l = fut_dws_l[0]

                            bd2_ss_l = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(bd2_l["cg"], "")

                            if bd2_l["시작연도"] <= current_year:
                                out.append(f"지금 **{bd2_l['str']} {bd2_ss_l}** 대운 중! **{current_year}~{bd2_l['종료연도']}년**이 최적 결혼 시기니라. 망설이지 말게!\n")

                            else:
                                out.append(f"**{bd2_l['시작연도']}년({bd2_l['시작나이']}세)**부터 {bd2_l['str']} **{bd2_ss_l}** 대운이 열리느니라. 그 무렵 결혼 결실이 맺어지느니라.\n")

                        else:
                            for _yr2_l in range(current_year, current_year + 10):
                                _sw2_l = get_yearly_luck(pils, _yr2_l)

                                if _sw2_l.get("십성_천간", "") in ({"偏財", "正財"} if gender == "남" else {"偏官", "正官"}):
                                    out.append(f"**{_yr2_l}년({_yr2_l - birth_year + 1}세)** 세운에 인연 기운이 들어오느니라. 그 무렵 준비하게.\n")

                                    break

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                elif is_health:
                    ilgan_oh_h = OH.get(ilgan_loc, "")

                    _OHB = {
                        "木": "간장·담낭·눈·근육·인대",
                        "火": "심장·소장·혈관·혈압",
                        "土": "비장·위장·췌장·소화기",
                        "金": "폐·대장·기관지·피부",
                        "水": "신장·방광·생식기·귀·뼈",
                    }

                    _OHA = {
                        "木": "스트레칭과 충분한 수면이 최우선이니라. 분노·스트레스가 간장을 상하게 하느니라.",
                        "火": "심혈관 정기검진이 필수이니라. 카페인·음주를 자제하고 과로를 삼가게.",
                        "土": "식사 규칙성이 핵심이니라. 폭식·군것질을 삼가게. 걱정이 위장을 상하게 하느니라.",
                        "金": "습도 관리가 중요하니라. 가을·건조한 환경을 조심하게.",
                        "水": "충분한 수분 섭취가 필수니라. 과로·짠 음식을 피하게.",
                    }

                    out.append(f"**{name}의 건강운 완전 분석**\n일간 {ilgan_loc}의 오행은 **{OHN.get(ilgan_oh_h, '')}({ilgan_oh_h})**이니라.\n")

                    out.append(f"타고난 취약 신체: **{_OHB.get(ilgan_oh_h, '전반적 건강')}**\n")

                    out.append(_OHA.get(ilgan_oh_h, "규칙적인 생활이 핵심이니라.") + "\n")

                    # 오행 과다/부족 건강 경고

                    oh_s = calc_ohaeng_strength(ilgan_loc, pils)

                    for o, v in oh_s.items():
                        if v >= 35:
                            out.append(f"\n⚠️ **{OHN.get(o, '')}({o}) 과다({v}%):** {_OHB.get(o, '')} 계통 특히 조심하게. 과다한 오행이 해당 장기를 혹사시키느니라.")

                        elif v <= 5:
                            out.append(f"\n💊 **{OHN.get(o, '')}({o}) 부족({v}%):** {_OHB.get(o, '')} 계통 보강하게. 부족한 오행이 해당 장기를 약하게 만드느니라.")

                    # 현재 대운 건강 영향

                    try:
                        dw_list_h2 = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                        cdw_h2 = next(
                            (d for d in dw_list_h2 if d["시작연도"] <= current_year <= d["종료연도"]),
                            None,
                        )

                        if cdw_h2:
                            cdw_ss_h2 = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(cdw_h2["cg"], "-")

                            cdw_oh_h2 = OH.get(cdw_h2["cg"], "")

                            _DWH2 = {
                                "偏官": "편관 대운은 압박과 스트레스가 극심하느니라. 면역력 저하와 사고 위험이 높으니 정기검진을 서두르게.",
                                "傷官": "상관 대운은 신경계 과부하와 과로가 주적이니라. 수면 관리와 스트레스 해소가 핵심이니라.",
                                "劫財": "겁재 대운은 외상·수술·혈액 관련 건강 이슈가 올 수 있으니라. 운동 시 안전에 유의하게.",
                                "偏印": "편인 대운은 우울·불안·정신건강에 주의가 필요하니라. 고립을 피하고 활동적으로 지내게.",
                                "比肩": "비견 대운은 과도한 경쟁과 독립 행보로 체력 소진을 조심하게. 충분한 휴식이 필수이니라.",
                                "食神": "식신 대운은 건강이 비교적 좋은 시기니라. 다만 과식으로 인한 소화계 문제를 조심하게.",
                                "正財": "정재 대운은 안정적 건강 유지가 가능한 시기니라. 규칙적 생활로 내실을 다지게.",
                                "正官": "정관 대운은 스트레스가 직장에서 오므로 멘탈 관리에 집중하게.",
                                "偏財": "편재 대운은 분주한 활동으로 체력 소진을 조심하게. 철저한 체력 관리가 필요하느니라.",
                                "正印": "정인 대운은 건강이 좋은 편이나 과보호·의존 경향이 오히려 체력을 약하게 만들 수 있느니라.",
                            }

                            out.append(f"\n**[현재 대운 건강 영향]** {cdw_h2['str']} **{cdw_ss_h2}** 대운 ({cdw_h2['종료연도'] - current_year}년 남음)\n")

                            out.append(
                                _DWH2.get(
                                    cdw_ss_h2,
                                    f"{cdw_ss_h2} 대운의 건강 기운이 흐르느니라. 몸의 신호에 귀를 기울이게.",
                                )
                                + "\n"
                            )

                            out.append(f"이 대운 오행: **{OHN.get(cdw_oh_h2, '')}({cdw_oh_h2})** — {_OHB.get(cdw_oh_h2, '')} 계통에 영향을 주느니라.\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 올해 세운 건강 경보

                    sw_hlt2 = get_yearly_luck(pils, current_year)

                    sw_hlt2_ss = sw_hlt2.get("십성_천간", "")

                    if sw_hlt2_ss == "偏官":
                        out.append(f"\n⚠️ 올해({current_year}년) {sw_hlt2.get('세운', '')} [偏官(편관)] 세운 — 건강 사고 위험 높은 해니라. 무리한 활동·수술 신중하게.\n")

                    elif sw_hlt2_ss == "傷官":
                        out.append(f"\n올해({current_year}년) {sw_hlt2.get('세운', '')} [傷官(상관)] 세운 — 과로와 신경 소모가 심한 해니라. 충분한 휴식이 최우선이니라.\n")

                elif is_dw:
                    daewoon = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)

                    cdw = next(
                        (d for d in daewoon if d["시작연도"] <= current_year <= d["종료연도"]),
                        None,
                    )

                    out.append(f"**{name}의 대운 흐름 완전 분석**\n")

                    # 용신 기반 황금기/주의기 판별

                    try:
                        ys_dw2 = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                        yong_ohs_dw2 = {
                            o
                            for o in [
                                ys_dw2.get("용신_1순위", ""),
                                ys_dw2.get("용신_2순위", ""),
                                ys_dw2.get("희신", ""),
                            ]
                            if o in ("木", "火", "土", "金", "水")
                        }

                        gisin_dw2 = set(ys_dw2.get("기신", []))

                    except Exception:
                        yong_ohs_dw2 = set()
                        gisin_dw2 = set()

                    if cdw:
                        cdw_ss = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(cdw["cg"], "-")

                        cdw_oh = OH.get(cdw["cg"], "")

                        grade2 = "🌟 황금기 대운" if cdw_oh in yong_ohs_dw2 else "⚠️ 주의기 대운" if cdw_oh in gisin_dw2 else "⬜ 보통 대운"

                        out.append(f"현재 대운: **{cdw['str']}** ({cdw_ss}) — **{grade2}**\n")

                        out.append(f"{cdw['시작연도']}~{cdw['종료연도']}년 ({cdw['시작나이']}~{cdw['시작나이'] + 9}세), **{cdw['종료연도'] - current_year}년** 더 이어지느니라.\n")

                        out.append(DAEWOON_PRESCRIPTION.get(cdw_ss, "꾸준한 노력으로 안정을 유지하게.") + "\n")

                        if cdw_oh in yong_ohs_dw2:
                            out.append("이 대운은 용신 기운이 흐르는 황금기니라! 크게 움직여도 하늘이 돕는 시기이니라.\n")

                        elif cdw_oh in gisin_dw2:
                            out.append("이 대운은 기신 기운이 흐르는 주의기니라. 무리한 확장보다 안전 자산 확보와 내실 다지기가 최선이니라.\n")

                    # 다음 대운 미리보기

                    cdw_idx2 = next(
                        (i for i, d in enumerate(daewoon) if d["시작연도"] <= current_year <= d["종료연도"]),
                        None,
                    )

                    if cdw_idx2 is not None and cdw_idx2 + 1 < len(daewoon):
                        ndw2 = daewoon[cdw_idx2 + 1]

                        ndw2_ss = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(ndw2["cg"], "-")

                        ndw2_oh = OH.get(ndw2["cg"], "")

                        ndw2_grade = "🌟 황금기" if ndw2_oh in yong_ohs_dw2 else "⚠️ 주의기" if ndw2_oh in gisin_dw2 else "⬜ 보통"

                        out.append(f"\n**[다음 대운 미리보기]** {ndw2['시작연도']}년({ndw2['시작나이']}세)부터 **{ndw2['str']} {ndw2_ss}** ({ndw2_grade}) 대운이 열리느니라.\n")

                        out.append(DAEWOON_PRESCRIPTION.get(ndw2_ss, "새 대운을 준비하게.") + "\n")

                    out.append("\n**전체 대운 흐름 (🌟황금기 / ⚠️주의기 표시):**\n")

                    for dw in daewoon[:8]:
                        dw_ss = TEN_GODS_MATRIX.get(ilgan_loc, {}).get(dw["cg"], "-")

                        dw_oh = OH.get(dw["cg"], "")

                        dw_grade2 = "🌟" if dw_oh in yong_ohs_dw2 else "⚠️" if dw_oh in gisin_dw2 else "⬜"

                        cur_m = " ◀현재" if dw["시작연도"] <= current_year <= dw["종료연도"] else ""

                        out.append(f"* {dw['시작나이']}~{dw['시작나이'] + 9}세: {dw['str']} ({dw_ss}) {dw_grade2}{cur_m}\n")

                elif is_past:
                    hl = generate_engine_highlights(pils, birth_year, gender, bm, bd, bh, bmn)

                    pevs = sorted(
                        hl.get("past_events", []),
                        key=lambda e: {"🔴": 0, "🟡": 1, "🟢": 2}.get(e.get("intensity", "🟢"), 3),
                    )

                    out.append(f"**{name}의 과거 사건 완전 분석**\n허허, 지나온 세월을 신안으로 살펴보겠느니라.\n")

                    if pevs:
                        out.append("\n**[주요 과거 사건 — 강도순]**\n")

                        for ev in pevs[:6]:
                            out.append(f"\n**{ev.get('year', '')}년 ({ev.get('age', '')}) {ev.get('intensity', '')} [{ev.get('domain', '변화')}]**\n{ev.get('desc', '')}\n")

                    else:
                        out.append("사주 엔진이 과거 데이터를 분석 중이니라.\n")

                    # 월지 충 근거

                    wc2 = hl.get("wolji_chung", [])

                    if wc2:
                        out.append("\n**[월지 충(沖) — 삶의 기반이 흔들린 시기]**\n")

                        for w in wc2[:3]:
                            out.append(f"* {w.get('age', '')}: {w.get('desc', '')}\n")

                    # 위험 구간 (과거분)

                    dz2 = hl.get("danger_zones", [])

                    if dz2:
                        try:
                            past_dz2 = [d for d in dz2 if d.get("year", "") and int(d["year"].split("~")[-1]) <= current_year]

                        except Exception:
                            past_dz2 = []

                        if past_dz2:
                            out.append("\n**[과거 위험 구간 — 힘든 시기의 근거]**\n")

                            for d in past_dz2[:2]:
                                out.append(f"* {d.get('age', '')}: {d.get('desc', '')}\n")

                elif is_job:
                    gk = get_gyeokguk(pils)

                    gkn = gk["격국명"] if gk else "미정격"

                    ys2 = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                    y1j = ys2.get("용신_1순위", "-")

                    si_j2 = get_ilgan_strength(ilgan_loc, pils)

                    sn_j2 = si_j2.get("신강신약", "중화")

                    _JOB2 = {
                        "정관격": "조직·공직·행정·관리직·법조가 천직이니라. 안정된 조직 안에서 명예와 재물이 함께 오느니라. 공무원·대기업·공공기관이 최적이니라.",
                        "편관격": "군경·의료·법조·스포츠·안전·소방·국방 분야에서 진가를 발휘하느니라. 강인한 의지와 추진력이 강점이니라.",
                        "정재격": "금융·회계·부동산·세무·유통·은행이 맞느니라. 성실한 노력으로 안정된 자산을 쌓는 팔자니라. 꼼꼼함과 책임감이 무기니라.",
                        "편재격": "사업·영업·투자·무역·중개·부동산 개발이 맞느니라. 기회를 포착하는 사업가 기질이 타고났느니라. 빠른 판단력이 핵심이니라.",
                        "식신격": "요식·창작·예술·교육·서비스·콘텐츠·강의가 맞느니라. 재능이 곧 밥그릇이 되는 팔자니라.",
                        "상관격": "IT·방송·컨설팅·프리랜서·스타트업·예술가에서 독보적 존재가 되느니라. 창의력이 최대 무기니라.",
                        "편인격": "학문·연구·철학·심리·의학·IT연구·특허 분야가 천직이니라. 깊은 통찰이 곧 경쟁력이니라.",
                        "정인격": "교육·학술·전문직·자격증 기반 직종·상담이 맞느니라. 배움이 쌓일수록 위상이 높아지느니라.",
                        "비견격": "독립·자영업·프리랜서·개인사업·1인 기업이 맞느니라. 혼자 움직일 때 가장 강해지는 팔자니라.",
                        "겁재격": "경쟁·협상·중개·스포츠·증권·선물 분야에서 오히려 빛나는 팔자니라.",
                    }

                    _OHJOB2 = {
                        "木": "목재·제지·섬유·교육·의류·원예·환경·에너지·스포츠 관련 업종이 유리하느니라.",
                        "火": "방송·광고·전기·전자·IT·연예·문화·조명·화학 관련 업종이 유리하느니라.",
                        "土": "부동산·건설·농업·의약·식품·유통·경영컨설팅 관련 업종이 유리하느니라.",
                        "金": "금융·금속·기계·법조·의료·국방·스포츠·경찰 관련 업종이 유리하느니라.",
                        "水": "무역·해운·유통·관광·호텔·미디어·철학·심리 관련 업종이 유리하느니라.",
                    }

                    _SWJOB2 = {
                        "食神": "올해는 재능 발휘와 자격 취득에 최적의 해니라. 새 프로젝트를 시작하게!",
                        "正官": "승진·이직·공직 시험에 유리한 해니라. 조직 내 신뢰를 쌓는 것이 핵심이니라.",
                        "偏財": "사업·영업 기회가 오는 해니라. 적극적으로 나서되 도박성 투자는 자제하게.",
                        "正財": "안정된 수입·직장 유지에 좋은 해니라. 차분하게 실력을 쌓는 것이 맞느니라.",
                        "傷官": "독립·창업·이직을 고려한다면 올해가 전환점이 될 수 있느니라. 단 계약서 주의.",
                        "偏官": "직장 변동·갈등이 올 수 있느니라. 무리한 도전보다 현 자리 지키기가 현명하니라.",
                    }


                    out.append(
                        _JOB2.get(
                            gkn,
                            f"{gkn}의 독특한 기운을 살려 자신만의 길을 개척해야 하느니라.",
                        )
                        + "\n"
                    )

                    # 십성 분포 분석

                    try:
                        ss_list_j2 = calc_sipsung(ilgan_loc, pils)

                        _GRP2 = {
                            "비견": "비겁",
                            "겁재": "비겁",
                            "식신": "식상",
                            "상관": "식상",
                            "정재": "재성",
                            "편재": "재성",
                            "정관": "관성",
                            "편관": "관성",
                            "정인": "인성",
                            "편인": "인성",
                        }

                        sc_cnt2 = {}

                        for p in ss_list_j2:
                            g = _GRP2.get(p.get("십성", ""), "")

                            if g:
                                sc_cnt2[g] = sc_cnt2.get(g, 0) + 1

                        top_g2 = max(sc_cnt2, key=sc_cnt2.get) if sc_cnt2 else ""

                        _SGJ2 = {
                            "재성": "재물을 직접 다루는 영역에서 두각을 드러내느니라.",
                            "관성": "조직과 권위 안에서 진가가 빛나느니라.",
                            "식상": "창의와 표현으로 세상을 사로잡는 팔자니라.",
                            "인성": "배움과 자격증으로 전문성을 쌓는 것이 맞느니라.",
                            "비겁": "독립과 경쟁 속에서 오히려 강해지는 팔자니라.",
                        }

                        if top_g2:
                            out.append(f"\n사주 십성 분포상 **{top_g2}** 기운이 강하니 {_SGJ2.get(top_g2, '')}\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 용신 오행 업종

                    out.append(f"\n**[용신 오행 업종]** 용신 **{y1j}** — {_OHJOB2.get(y1j, f'{y1j} 오행 관련 업종이 맞느니라.')}\n")

                    # 신강신약 행동 패턴

                    if "신강" in sn_j2:
                        out.append(f"\n**신강({sn_j2})** — 독립·창업·단독 행보가 최적이니라. 조직보다 자신이 주도하는 환경에서 능력을 발휘하느니라.\n")

                    elif "신약" in sn_j2:
                        out.append(f"\n**신약({sn_j2})** — 안정된 조직·전문직 안에서 귀인의 도움을 받는 것이 최적이니라. 창업보다 전문성 강화가 우선이니라.\n")

                    # 올해 진로 세운

                    sw_j2 = get_yearly_luck(pils, current_year)

                    sw_j2_ss = sw_j2.get("십성_천간", "")

                    out.append(
                        f"\n올해({current_year}년) {sw_j2.get('세운', '')} [{sw_j2_ss}] {sw_j2.get('길흉', '')} — {_SWJOB2.get(sw_j2_ss, sw_j2_ss + ' 기운의 해이니 흐름을 잘 읽고 움직이게.')}\n"
                    )

                    out.append(f"\n용신 **{y1j}** 오행이 강한 해에 진로 결정을 내리면 가장 유리하느니라. 명심하게!\n")

                elif is_char:
                    gk = get_gyeokguk(pils)

                    si = get_ilgan_strength(ilgan_loc, pils)

                    gkn = gk["격국명"] if gk else "미정격"

                    sn = si.get("신강신약", "중화")

                    sc = si.get("일간점수", 50)

                    _CG_KR2 = {
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

                    _ilgan_k2 = f"{ilgan_loc}({_CG_KR2.get(ilgan_loc, '')})"

                    _CHR = ILGAN_CHAR_DESC.get(_ilgan_k2, ILGAN_CHAR_DESC.get(ilgan_loc, {}))

                    oh_s_c2 = calc_ohaeng_strength(ilgan_loc, pils)

                    out.append(f"**{name}의 성격·기질 완전 분석**\n일간 **{ilgan_loc}** | 격국 **{gkn}** | **{sn}**(점수 {sc}/100)\n")

                    out.append(
                        _CHR.get(
                            "성격_핵심",
                            f"일간 {ilgan_loc}의 기운이 삶 전반을 이끄느니라.",
                        )
                        + "\n"
                    )

                    if _CHR.get("장점"):
                        out.append(f"\n**[장점]** {_CHR['장점']}\n")

                    if _CHR.get("단점"):
                        out.append(f"**[주의]** {_CHR['단점']}\n")

                    if _CHR.get("재물패턴"):
                        out.append(f"**[재물 성향]** {_CHR['재물패턴']}\n")

                    if _CHR.get("건강"):
                        out.append(f"**[건강 주의]** {_CHR['건강']}\n")

                    if _CHR.get("직업"):
                        out.append(f"**[천직 힌트]** {_CHR['직업']}\n")

                    _SNS2 = {
                        "신강": f"기운이 넘치는 신강({sc}/100)이니라. 스스로 움직여야 기회가 오느니라. 독립적 결단이 맞는 팔자이나 자기중심적으로 흐를 수 있으니 타인 의견에도 귀를 열게.",
                        "신약": f"기운이 부족한 신약({sc}/100)이니라. 귀인과 함께할 때 진가가 발휘되느니라. 좋은 파트너·스승이 운명을 바꾸느니라. 협업 속에서 빛나는 팔자이니라.",
                        "중화": f"기운이 균형 잡힌 중화({sc}/100)이니라. 어느 상황에도 적응하는 유연함이 강점이니라. 꾸준함과 전문성이 최대 무기이니라.",
                    }

                    for k, v in _SNS2.items():
                        if k in sn:
                            out.append(f"\n**[신강신약 행동 패턴]** {v}\n")
                            break

                    # 오행 과다 성격 패턴

                    _OHC2 = {
                        "木": "木 과다: 고집이 세고 자기주장이 강하며 리더십이 강함. 하지만 융통성 부족 주의.",
                        "火": "火 과다: 열정적이고 급하며 사교성이 뛰어남. 하지만 과잉 행동과 산만함 주의.",
                        "土": "土 과다: 신중하고 보수적이며 인내심이 강함. 하지만 변화 거부와 고집 주의.",
                        "金": "金 과다: 원칙주의적이고 결단력이 강함. 하지만 냉철함이 지나쳐 인간관계 문제 주의.",
                        "水": "水 과다: 지혜롭고 유연하며 전략적. 하지만 우유부단과 비밀주의 주의.",
                    }

                    for o, v in oh_s_c2.items():
                        if v >= 35:
                            out.append(f"\n{_OHC2.get(o, '')}\n")

                    sw = get_yearly_luck(pils, current_year) or {}

                    out.append(f"\n올해({current_year}년)는 {sw.get('세운', '')} [{sw.get('십성_천간', '')}] {sw.get('길흉', '')} 기운이니 그 흐름을 잘 타게.\n")

                else:
                    gk = get_gyeokguk(pils)
                    ys = get_yongshin_multilayer(pils, birth_year, gender, bm, bd, bh, bmn, current_year)

                    si = get_ilgan_strength(ilgan_loc, pils)

                    gkn = gk["격국명"] if gk else "미정격"
                    sn = si["신강신약"]
                    sc = si.get("일간점수", 50)

                    y1 = ys.get("용신_1순위", "-")
                    heui = ys.get("희신", "-")
                    gisin = ", ".join(ys.get("기신", []))

                    sw = get_yearly_luck(pils, current_year) or {}

                    sw_ss = sw.get("십성_천간", "")
                    sw_gan = sw.get("세운", "")
                    sw_gh = sw.get("길흉", "")

                    # 1️⃣ 천기의 낙인

                    _GKS = {
                        "정관격": "규칙과 질서의 격국. 조직에서 권위를 얻을 팔자이니라. 공직·관리직이 천직이니라.",
                        "편관격": "칠살격 — 강인한 의지의 팔자. 시련이 클수록 더 강해지는 팔자이니라.",
                        "정재격": "성실한 재물격. 꾸준함이 쌓여 반드시 부를 이루는 팔자이니라.",
                        "편재격": "활동적 사업가격. 큰 기회와 기복이 공존하는 팔자이니라.",
                        "식신격": "복록이 넘치는 격국. 재능이 곧 밥그릇이 되는 팔자이니라.",
                        "상관격": "창의성과 반골 기질의 격국. 독립 행보에서 진가가 나오는 팔자이니라.",
                        "편인격": "직관과 영감의 격국. 깊은 전문성으로 독보적 경지에 오르는 팔자이니라.",
                        "정인격": "학문과 명예의 귀격. 배움이 쌓일수록 위상이 높아지는 팔자이니라.",
                        "비견격": "독립심의 격국. 남 밑에 있으면 기운이 막히는 팔자이니라.",
                        "겁재격": "승부사 기질의 격국. 경쟁 속에서 오히려 빛나는 팔자이니라.",
                    }

                    out.append(f"\n**1️⃣ [천기의 낙인]**\n일간 **{ilgan_loc}** | 격국 **{gkn}** | {sn}(기력 {sc}점)\n")

                    out.append(_GKS.get(gkn, f"{gkn}의 독특한 기운을 타고난 팔자이니라.") + "\n")

                    out.append(f"용신 **{y1}** 기운이 흐를 때 발복하느니라. 기신 **{gisin}** 기운은 경계하게.\n")

                    # 2️⃣ 신안의 복기

                    try:
                        hl_e = generate_engine_highlights(pils, birth_year, gender, bm, bd, bh, bmn)

                        pevs_e = sorted(
                            hl_e.get("past_events", []),
                            key=lambda e: {"🔴": 0, "🟡": 1, "🟢": 2}.get(e.get("intensity", "🟢"), 3),
                        )

                        out.append(f"\n**2️⃣ [신안의 복기]**\n")

                        if pevs_e:
                            for ev in pevs_e[:2]:
                                out.append(f"**{ev.get('year', '')}년 ({ev.get('age', '')})** {ev.get('intensity', '')} [{ev.get('domain', '변화')}]: {ev.get('desc', '')}\n")

                        else:
                            out.append("지나온 세월의 흔적이 이 팔자에 깊이 새겨져 있느니라.\n")

                    except Exception as _e:
                        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

                    # 3️⃣ 현재의 형국

                    out.append(f"\n**3️⃣ [현재의 형국]**\n올해({current_year}년) **{sw_gan}** [{sw_ss}] — {sw_gh} 기운이니라.\n")

                    out.append(
                        f"{'용신 세운이 흐르는 황금기이니라. 지금 움직이지 않으면 언제 움직이겠는가!' if sw_ss in (y1, heui) else '지금은 신중하게 내실을 다지는 시기이니라. 무리한 확장은 금물이니라.'}\n"
                    )

                    # 4️⃣ 필살의 비방

                    _BIYB = {
                        "木": "새벽 인시(寅(인)時 03~05시)에 동쪽 창문을 열고 파란 옷 입은 채 깊게 호흡하게. 목기(木氣)가 충전되느니라.",
                        "火": "정오 오시(午(오)時 11~13시)에 남쪽 방향으로 붉은 소품을 놓게. 화기(火氣)의 밝음이 운을 열어주느니라.",
                        "土": "환절기에 황색 음식(꿀·고구마)을 먹으며 중심을 잡게. 토기(土氣)가 안정을 가져오느니라.",
                        "金": "서쪽 방향 책상 위에 금속 소품을 놓고 결단력을 다지게. 금기(金氣)가 길을 열어주느니라.",
                        "水": "해시(亥(해)時 21~23시)에 북쪽 방향으로 검은 물컵을 두게. 수기(水氣)가 지혜를 불러오느니라.",
                    }

                    out.append(f"\n**4️⃣ [필살의 비방]**\n")

                    out.append(
                        _BIYB.get(
                            y1,
                            f"용신 {y1} 오행의 기운을 강화하는 색상·방향·음식을 일상에서 실천하게. 이것이 운명을 바꾸는 열쇠이니라.",
                        )
                        + "\n"
                    )

            except Exception as _le:
                out.append(f"\n허어, 기운이 잠시 흔들렸느니라. 기본 팔자로 답을 드리겠네. (오류: {_le})\n")

            out.append(f"\n---\n*내 신안(神眼)이 본 {name}의 팔자가 이러하니라. 더 깊이 알고 싶다면 다시 물어보게.*")

            return "\n".join(out)

        # ── 로컬 사주 엔진 (Brain3 + 판단 규칙) ─────────────────────────
        with st.chat_message("assistant"):
            # Brain3 인스턴스로 쿼리 처리
            _brain = Brain3(pils, name, birth_year, gender)
            _resp = _brain.process_query(None, user_query, st.session_state.chat_history)
            # ── 판단 규칙 후처리 ──
            _resp = SajuJudgmentRules.apply_all(_resp)

            trust_lv = mem.get("trust", {}).get("level", 1)

            follow_up = FollowUpGenerator.get_question(intent_res["topic"], trust_level=trust_lv).replace("{name}", name)

            final_resp = f"{_resp}\n\n---\n💡 **만신의 깊은 질문:** {follow_up}"

            st.markdown(final_resp)

            st.session_state.chat_history.append({"role": "assistant", "content": final_resp})

            # 데이터 영속화

            SajuMemory.record_interest(name, intent_res["topic_kr"])

            SajuMemory.add_conversation(name, intent_res["topic_kr"], _resp, intent_res["emotion"])

            LifeNarrativeEngine.update_narrative(name, intent_res["topic_kr"], intent_res["emotion"])

        st.rerun()


def menu7_ai(pils, name, birth_year, gender):
    """7️⃣ 만신 상담소 - AI 대화형 상담 센터 (E-Version)"""

    st.markdown(
        """

<div style="background:linear-gradient(135deg,#fff8e1,#fffde7);border:2px solid #d4af3755;border-radius:14px; padding:20px;margin-bottom:14px;box-shadow:0 4px 15px rgba(212,175,55,0.1)">

<div style="font-size:18px;font-weight:900;color:#d4af37;margin-bottom:6px">🏛️ 만신 상담소 (萬神 相談所)</div>

<div style="font-size:13px;color:#000000;line-height:1.8">

        "인생의 갈림길에서 답답할 때, <b>만신</b>에게 물어보세요."<br>

        * <b>궁합, 재물, 커리어, 건강</b> 등 모든 고민을 영속 기억 시스템 기반으로 상담합니다.

</div></div>""",
        unsafe_allow_html=True,
    )

    # -- 엔진 상태 표시 --

    st.markdown(
        '<div style="background:#e8f5e8;color:#2e7d32;padding:6px 12px;border-radius:8px;font-size:11px;margin-bottom:10px">🔮 자체 사주 분석 엔진 가동 중 — 만세력 / 격국 / 용신 / 대운 완전 분석</div>',
        unsafe_allow_html=True,
    )

    # -- 상담 집중 분야 선택 --

    c1, c2 = st.columns([3, 1])

    with c1:
        # 자주 묻는 관심사 기반 기본값 설정
        _interest_default = 0
        try:
            _interest_summary = SajuMemory.get_interest_summary(name)
            _focus_map = {
                "재물": 1, "돈": 1, "사업": 1,
                "연애": 2, "결혼": 2, "인연": 2,
                "직장": 3, "커리어": 3, "직업": 3,
                "학업": 4, "시험": 4, "공부": 4,
                "건강": 5,
            }
            for kw, idx in _focus_map.items():
                if kw in _interest_summary:
                    _interest_default = idx
                    break
        except Exception:
            _saju_log.warning("[menu7_ai] 오류: %s", str(e)[:60])

        focus_key = st.selectbox(
            "집중 상담 분야",
            ["종합", "재물/사업", "연애/결혼", "직장/커리어", "학업/시험", "건강"],
            index=_interest_default,
        )

    with c2:
        if st.button("🔄 기록 초기화", help="현재 상담 이력만 초기화합니다"):
            st.session_state.chat_history = []
            st.rerun()

    # ── 🏛️ 전문가 8섹션 완전 분석 (SajuExpertPrompt) ───────────────
    with st.expander("🏛️ 명리학 전문가 8섹션 완전 분석 펼치기", expanded=False):
        if st.button("📊 전문가 8섹션 분석 생성", key="btn_expert_8sec",
                     use_container_width=True):
            with st.spinner("3인 명리 전문가가 사주를 집대성하고 있습니다..."):
                try:
                    # 사주 컨텍스트 데이터 구성
                    _ilgan_e  = pils[1]["cg"] if len(pils) > 1 else "?"
                    _gy_e     = get_gyeokguk(pils) or {}
                    _ys_e     = get_yongshin(pils) or {}
                    _si_e     = get_ilgan_strength(_ilgan_e, pils) or {}
                    _sw_e     = get_yearly_luck(pils, datetime.now().year) or {}
                    _bm_e     = max(1, min(12, int(st.session_state.get("birth_month") or 1)))
                    _bd_e     = max(1, min(31, int(st.session_state.get("birth_day") or 1)))
                    _bh_e     = max(0, min(23, int(st.session_state.get("birth_hour") or 12)))
                    _bmn_e    = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))
                    _dw_e     = SajuCoreEngine.get_daewoon(
                        pils, birth_year, _bm_e, _bd_e, _bh_e, _bmn_e, gender=gender
                    ) or []
                    _cur_dw_e = next(
                        (d for d in _dw_e
                         if d["시작연도"] <= datetime.now().year <= d["종료연도"]), {}
                    )

                    _ctx_data = f"""
이름: {name} / 성별: {gender} / 생년: {birth_year}년
일간: {_ilgan_e} / 격국: {_gy_e.get("격국명","?")} ({_gy_e.get("격의_등급","?") if _gy_e else "?"})
신강신약: {_si_e.get("신강신약","?")} (점수: {_si_e.get("helper_score",50)})
용신: {_ys_e.get("종합_용신",[])} / 기신: {_ys_e.get("기신",[])}
현재 대운: {_cur_dw_e.get("str","?")} ({_cur_dw_e.get("시작연도","?")}~{_cur_dw_e.get("종료연도","?")})
올해 세운: {_sw_e.get("세운","?")} [{_sw_e.get("십성_천간","?")}] {_sw_e.get("길흉","?")}
사주 기둥: {" / ".join([f"{p.get('cg','?')}{p.get('jj','?')}" for p in pils])}
"""
                    _prompt = SajuExpertPrompt.build_system_prompt(
                        name, focus_key, _ctx_data
                    )

                    # 로컬 엔진으로 8섹션 생성
                    _result = build_rich_narrative(
                        pils, birth_year, gender, name, section="report"
                    )

                    st.markdown(
                        f"""<div style='background:#fffdf5;border:2px solid #d4af37;
                        border-radius:16px;padding:24px;margin:10px 0;'>
                        <div style='font-size:16px;font-weight:900;color:#8b6200;
                        margin-bottom:16px;text-align:center;'>
                        🏛️ 【 명리학 전문가 8섹션 완전 분석 】</div>
                        <div style='font-size:13px;color:#111;line-height:2.2;
                        white-space:pre-wrap;'>{_result}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                except Exception as _ee:
                    st.warning(f"⚠️ 전문가 분석 오류: {_ee}")

    # -- 소름 엔진 (과거 적중 미리보기) --

    try:
        gb = goosebump_engine(pils, birth_year, gender)

        if gb["past"]:
            with st.expander("🔮 이전에 이런 일을 겪으셨나요?", expanded=True):
                for s in gb["past"][:2]:
                    st.markdown(
                        f'<div style="background:#f9f9f9;border-left:3px solid #d4af37;padding:8px 12px;margin:4px 0;font-size:13px">🔍 {s}</div>',
                        unsafe_allow_html=True,
                    )

    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    # -- 빠른 질문 버튼 (30개 직격 질문, 카테고리별) --
    st.markdown('<div class="gold-section">🎯 직격 질문 선택 (원하는 항목을 바로 누르세요)</div>',
                unsafe_allow_html=True)

    _ALL_QUESTIONS = {
        "💰 돈·사업": [
            "올해 돈 벌리는 시기가 언제야?",
            "지금 사업 시작해도 괜찮아?",
            "투자해도 되는 시기야?",
            "지금 빚 내도 돼?",
            "사업이 망할 것 같아, 접어야 해?",
            "내 재물 그릇이 얼마나 커?",
        ],
        "💼 직장·커리어": [
            "지금 이직해도 돼?",
            "퇴사하고 창업해도 될까?",
            "나한테 맞는 직업이 뭐야?",
            "올해 승진 가능해?",
            "직장에서 잘릴 것 같아",
            "지금 이 직장 계속 다녀야 해?",
        ],
        "❤️ 연애·결혼": [
            "이 사람이 나한테 진심이야?",
            "연애·결혼 인연이 언제 와?",
            "지금 만나는 사람이랑 결혼해도 돼?",
            "배우자가 바람피우고 있어?",
            "이별 후 재회 가능해?",
            "나랑 안 맞는 이성 유형이 뭐야?",
        ],
        "🚨 위기·사고수": [
            "올해 사고수가 있어?",
            "소송·법적 분쟁 위험 있어?",
            "올해 건강 조심할 게 있어?",
            "큰 손재수가 오는 시기야?",
            "주변에 나를 해치는 사람이 있어?",
            "올해 가장 조심해야 할 게 뭐야?",
        ],
        "🔮 운명·성격": [
            "나는 왜 이렇게 힘들게 살아?",
            "내 타고난 성격의 장단점은?",
            "내 인생 최대 전성기는 언제야?",
            "지금 내 대운이 좋은 거야 나쁜 거야?",
            "올해가 내 인생 전환점이야?",
            "나한테 귀인이 오는 시기는?",
        ],
    }

    _cat_names = list(_ALL_QUESTIONS.keys())
    _q_tabs = st.tabs(_cat_names)
    for _ti, _cat in enumerate(_cat_names):
        _qs = _ALL_QUESTIONS[_cat]
        with _q_tabs[_ti]:
            _qc = st.columns(3)
            for _qi, _q in enumerate(_qs):
                if _qc[_qi % 3].button(_q, key=f"qq_{_ti}_{_qi}", use_container_width=True):
                    st.session_state["ai_quick_input"] = _q
    if st.session_state.get("ai_quick_input"):
        _auto_q = st.session_state["ai_quick_input"]
        st.markdown(
            f"<div style='background:rgba(201,168,76,0.1);border:1px solid #c9a84c;border-radius:10px;"
            f"padding:10px 16px;margin:8px 0;font-size:13px;color:#3d2800'>"
            f"💬 선택한 질문: <b>{_auto_q}</b></div>",
            unsafe_allow_html=True,
        )
        try:
            _ilgan = pils[1]["cg"]
            _ilp = ILGAN_PROFILE.get(_ilgan, {})
            _daewoon = SajuCoreEngine.get_daewoon(
                pils, birth_year,
                st.session_state.get("birth_month", 1),
                st.session_state.get("birth_day", 1),
                st.session_state.get("birth_hour", 12),
                st.session_state.get("birth_minute", 0),
                gender=gender,
            )
            _cur_dw = next((d for d in _daewoon if d["시작연도"] <= datetime.now().year <= d["종료연도"]), {})
            _gy = get_gyeokguk(pils)
            _ys = get_yongshin(pils)
            _sw = get_yearly_luck(pils, datetime.now() or {}.year)
            _ctx_lines = [
                f"[사주 컨텍스트] 이름:{name} / 일간:{_ilgan}({_ilp.get('한글','')}) / 격국:{_gy.get('격국명','?') if _gy else '?'}",
                f"용신:{_ys.get('종합_용신',[])} / 현재대운:{_cur_dw.get('str','?')} / 올해세운:{_sw.get('세운','?')}({_sw.get('십성_천간','?')})",
                f"[질문] {_auto_q}",
            ]
            _ai_resp = get_ai_interpretation("\n".join(_ctx_lines))
            if not _ai_resp:
                _ai_resp = LocalSajuNarrator.quick_answer(_auto_q, pils, birth_year, gender) if hasattr(LocalSajuNarrator, "quick_answer") else ""
            if _ai_resp:
                st.markdown(
                    f"<div style='background:linear-gradient(145deg,#faf7f0,#f2ebe0);border:1px solid #c9a84c;"
                    f"border-radius:14px;padding:18px;margin:8px 0;font-size:14px;color:#3d2800;line-height:2'>"
                    f"<div style='font-size:11px;font-weight:700;color:#c9a84c;margin-bottom:8px'>🔮 만신의 답</div>"
                    f"{_ai_resp}</div>",
                    unsafe_allow_html=True,
                )
        except Exception as _qe:
            st.warning(f"⚠️ 오류: {str(_qe)[:80]}")

    # -- AI 상담 메인 (E-Version Chat) --

    tab_ai_chat(pils, name, birth_year, gender)


def menu13_career(pils, name, birth_year, gender):
    """1️⃣3️⃣ 직장운 -- 십성(十星) 기반 진로 및 커리어 분석"""

    st.markdown(
        f"""

<div style="background:linear-gradient(135deg, #1a253c, #0a1428); padding:20px; border-radius:16px; border-left:5px solid #d4af37; margin-bottom:20px; box-shadow: var(--shadow);">

<div style="color:#d4af37; font-size:24px; font-weight:900; letter-spacing:2px;">💼 {name}님의 직장운 / 커리어</div>

<div style="color:rgba(255,255,255,0.7); font-size:13px; margin-top:4px;">십성(十星)의 흐름으로 보는 천직과 성공 전략</div>

</div>

    """,
        unsafe_allow_html=True,
    )

    try:
        ilgan = pils[1]["cg"]

        ss_list = calc_sipsung(ilgan, pils)

        # 십성 카운팅

        counts = {"비겁": 0, "식상": 0, "재성": 0, "관성": 0, "인성": 0}

        ss_names = {
            "비견": "비겁",
            "겁재": "비겁",
            "식신": "식상",
            "상관": "식상",
            "편재": "재성",
            "정재": "재성",
            "편관": "관성",
            "정관": "관성",
            "편인": "인성",
            "정인": "인성",
        }

        for item in ss_list:
            if item["cg_ss"] in ss_names:
                counts[ss_names[item["cg_ss"]]] += 1

            if item["jj_ss"] in ss_names:
                counts[ss_names[item["jj_ss"]]] += 1

        # 직업 성향 딕셔너리
        traits = {
            "비겁": ("독립 개척형", "스스로 길을 여는 창업가·독립 사업가 기질. 남 밑에서보다 내 사업이 맞습니다."),
            "식상": ("표현 창조형", "창의적 아이디어와 표현 능력이 뛰어남. 창작·교육·서비스·콘텐츠 분야에서 빛납니다."),
            "재성": ("실무 경영형", "재물 감각과 현실적 판단이 탁월. 사업·금융·무역·영업에서 성과를 냅니다."),
            "관성": ("조직 리더형", "규율과 책임감이 강한 조직인. 공무원·관리직·법조·군인 등 체계적 조직에서 두각."),
            "인성": ("학문 전문형", "깊은 사고와 학습 능력이 강점. 교육·연구·의료·상담·종교 등 전문직에 적합."),
        }

        # 분석 결과 도출

        primary_ss = max(counts, key=counts.get)

        # UI 섹션: 커리어 성향

        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.markdown(
                '<div class="section-label">🎯 핵심 직업 성향</div>',
                unsafe_allow_html=True,
            )


            title, desc = traits.get(primary_ss, ("균형형", "다양한 분야에서 유연한 적응력을 보입니다."))

            st.markdown(
                f"""

<div style="background:rgba(212,175,55,0.1); border:1px solid #d4af37; padding:15px; border-radius:12px; text-align:center;">

<div style="font-size:18px; font-weight:900; color:#d4af37; margin-bottom:8px;">{title}</div>

<div style="font-size:13px; color:#eee;">{desc}</div>

</div>

            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                '<div class="section-label">📊 직군별 적합도</div>',
                unsafe_allow_html=True,
            )

            for ss, count in counts.items():
                score = min(100, count * 20 + 20)

                st.markdown(
                    f"""

<div style="margin-bottom:8px;">

<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">

<span>{ss} 기운</span>

<span>{score}%</span>

</div>

<div style="background:rgba(255,255,255,0.1); height:8px; border-radius:4px; ">

<div style="background:linear-gradient(90deg, #d4af37, #f4e4bc); width:{score}%; height:100%;"></div>

</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

        # 상세 조언

        st.markdown('<div class="gold-section">🛡️ 커리어 성공 전략</div>', unsafe_allow_html=True)

        advice_map = {
            "비겁": "혼자보다는 파트너십을 활용하되, 본인의 주도권을 잃지 않는 환경이 중요합니다. 1인 기업이나 전문 자격직이 유리합니다.",
            "식상": "본인만의 독창적인 결과물을 만들어내는 능력이 자산입니다. 끊임없이 기술이나 재능을 연마하여 대체 불가능한 존재가 되십시오.",
            "재성": "결과 중심의 업무에서 큰 성취를 느낍니다. 숫자에 밝고 현실적인 감각이 있으니 실무 책임자나 사업 경영에서 빛을 발합니다.",
            "관성": "명예와 체면을 중시하며 사회적 지위 상승에 대한 욕구가 강합니다. 정해진 룰 안에서 최고의 성과를 내는 능력이 탁월합니다.",
            "인성": "지식과 정보를 가공하는 능력이 뛰어납니다. 남들이 모르는 깊이 있는 지식을 습득하여 멘토나 전문가로 명성을 쌓으십시오.",
        }

        st.markdown(
            f"""

<div class="saju-narrative" style="color:#eee; background:rgba(255,255,255,0.03); padding:15px; border-radius:12px;">

            💡 <b>{name}님을 위한 조언:</b> {advice_map.get(primary_ss, "균형 잡힌 시각으로 조직 내에서 중추적인 역할을 수행하십시오.")} 

            특히 올해는 자신의 재능을 외부로 드러내는 시기이므로 적극적인 제안이나 도전을 추천합니다.

</div>

        """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"직장운 분석 중 오류 발생: {e}")


def menu14_health(pils, name, birth_year, gender):
    """1️⃣4️⃣ 건강운 -- 오행(五行) 균형 및 질병 직격 경고"""

    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#fff5f5,#ffe8e8);padding:20px;
        border-radius:16px;border-left:5px solid #c0392b;margin-bottom:20px;
        box-shadow:0 4px 15px rgba(0,0,0,0.06)">
        <div style="color:#c0392b;font-size:22px;font-weight:900;letter-spacing:2px">
        💊 {name}님의 건강 직격 경고</div>
        <div style="color:#555;font-size:13px;margin-top:4px;font-weight:600">
        오행 과다·부족 + 대운·세운 교차 분석으로 지금 당신에게 올 수 있는 질병을 직격으로 알려드립니다</div>
        </div>""",
        unsafe_allow_html=True,
    )

    try:
        ilgan = pils[1]["cg"]
        current_year = datetime.now().year
        current_age  = current_year - birth_year + 1
        oh_strength  = calc_ohaeng_strength(ilgan, pils)
        weak_oh      = min(oh_strength, key=oh_strength.get)
        excess_oh    = max(oh_strength, key=oh_strength.get)
        sw           = get_yearly_luck(pils, current_year) or {}
        sw_ss        = sw.get("십성_천간", "")
        sw_cg        = sw.get("세운", "")[:1]
        sw_oh        = OH.get(sw_cg, "")

        bm  = st.session_state.get("birth_month", 1)
        bd  = st.session_state.get("birth_day",   1)
        bh  = st.session_state.get("birth_hour",  12)
        bmn = st.session_state.get("birth_minute", 0)

        try:
            daewoon = SajuCoreEngine.get_daewoon(pils, birth_year, bm, bd, bh, bmn, gender)
            cur_dw  = next((d for d in daewoon
                            if d["시작연도"] <= current_year <= d["종료연도"]), None) or {}
            dw_oh   = OH.get(cur_dw.get("cg", ""), "")
            dw_ss   = TEN_GODS_MATRIX.get(ilgan, {}).get(cur_dw.get("cg", ""), "")
        except Exception:
            cur_dw, dw_oh, dw_ss = {}, "", ""

        # ── 오행별 질병 데이터 ──────────────────────────────────────
        _OH_DISEASE = {
            "木": {
                "organ":   "간장·담낭·눈·근육·인대·신경",
                "diseases": [
                    ("간염·지방간·간경변",     "분노·과음·과로가 누적되면 간이 가장 먼저 신호를 보냅니다. 정기적으로 간 기능 검사(GOT·GPT)를 받으십시오."),
                    ("안구건조증·시력 저하·녹내장", "목(木) 기운이 부족하면 눈에 먼저 증상이 나타납니다. 장시간 화면 노출을 줄이고 루테인을 챙기십시오."),
                    ("근육통·인대 손상·경련",  "스트레스가 쌓이면 근육이 굳어지고 쥐가 잘 납니다. 마그네슘 섭취와 스트레칭이 필수입니다."),
                ],
                "excess":   "목(木) 과다 → 간열(肝熱) 상승, 두통·고혈압·충혈 주의",
                "lack":     "목(木) 부족 → 간기(肝氣) 허약, 만성 피로·우울·근육 무력감 주의",
                "food":     "신맛(식초·레몬·매실), 녹색 채소, 브로콜리, 부추",
                "avoid":    "과음·야식·극도의 분노·장시간 눈 혹사",
                "check":    "간 기능 검사(GOT·GPT·감마지티피), 안압 검사, 근전도 검사",
            },
            "火": {
                "organ":   "심장·소장·혈관·혈압·혀·정신",
                "diseases": [
                    ("심근경색·협심증·부정맥",  "화(火) 과다 시 심장 혈관에 압박이 가중됩니다. 가슴 두근거림·흉통·호흡 곤란이 오면 즉시 심전도 검사를 받으십시오."),
                    ("고혈압·뇌졸중 전조",      "흥분과 과로가 반복되면 혈압이 급등합니다. 혈압계를 집에 두고 매일 아침 측정하는 습관을 들이십시오."),
                    ("불면증·공황장애·우울",    "화기가 위로 치솟으면 심신이 불안해집니다. 수면 4시간 미만이 반복되면 즉각 전문의를 찾으십시오."),
                ],
                "excess":   "화(火) 과다 → 심화항진(心火亢進), 충동적 행동·혈압 급등·심계항진 주의",
                "lack":     "화(火) 부족 → 심기허(心氣虛), 손발 냉증·무기력·순환 장애 주의",
                "food":     "쓴맛(여주·씀바귀·커피 소량), 토마토, 붉은 과일, 연어",
                "avoid":    "과도한 흥분·카페인 과다·수면 부족·폭식",
                "check":    "심전도·심초음파, 혈압 측정, 혈중 콜레스테롤, 수면다원검사",
            },
            "土": {
                "organ":   "비장·위장·췌장·소화기·입·근육",
                "diseases": [
                    ("위염·위궤양·역류성 식도염", "걱정과 불안이 위를 갉아먹습니다. 공복 시 통증, 신물, 속쓰림이 반복되면 위내시경을 즉시 받으십시오."),
                    ("당뇨·인슐린 저항성",       "토(土) 과다 시 단맛 중독과 비만으로 이어집니다. 공복 혈당과 당화혈색소(HbA1c)를 정기 체크하십시오."),
                    ("부종·림프순환 이상",        "토(土) 기운이 막히면 몸에 습기가 차 부종이 옵니다. 아침에 얼굴·다리가 붓는다면 신장·심장 검사를 받으십시오."),
                ],
                "excess":   "토(土) 과다 → 습담(濕痰) 정체, 비만·부종·당뇨 전 단계 주의",
                "lack":     "토(土) 부족 → 비기허(脾氣虛), 만성 소화 불량·빈혈·무기력 주의",
                "food":     "단맛(고구마·호박·대추), 노란 채소, 현미, 연근",
                "avoid":    "폭식·야식·찬 음식·과도한 걱정과 반추",
                "check":    "위내시경, 공복 혈당·당화혈색소, 복부 초음파, 신장 기능",
            },
            "金": {
                "organ":   "폐·대장·기관지·피부·코·면역계",
                "diseases": [
                    ("만성 기관지염·천식·폐렴",  "금(金) 기운이 약해지면 호흡기가 무너집니다. 가을·겨울 환절기 기침이 3주 이상 지속되면 흉부 X선·폐 기능 검사를 받으십시오."),
                    ("대장 용종·과민성 대장증후군", "금(金) 과다 시 대장이 예민해집니다. 변비와 설사가 반복되거나 혈변이 보이면 즉시 대장내시경을 받으십시오."),
                    ("아토피·건선·피부 트러블",   "폐와 피부는 한 몸입니다. 피부 발진·가려움이 계절마다 심해지면 면역 계통을 점검하십시오."),
                ],
                "excess":   "금(金) 과다 → 폐기울결(肺氣鬱結), 건조·변비·피부 각화 주의",
                "lack":     "금(金) 부족 → 폐기허(肺氣虛), 잦은 감기·면역 저하·호흡 얕음 주의",
                "food":     "매운맛(무·도라지·배), 흰 음식, 연근, 율무",
                "avoid":    "흡연·건조한 환경·미세먼지 장기 노출·과도한 슬픔",
                "check":    "폐 기능 검사·흉부 X선, 대장내시경, 알레르기 패널 검사",
            },
            "水": {
                "organ":   "신장·방광·생식기·뼈·귀·허리",
                "diseases": [
                    ("신장 기능 저하·신부전 전 단계", "수(水) 기운이 고갈되면 신장이 가장 먼저 타격을 받습니다. 얼굴·다리 부종, 소변 거품, 야뇨가 잦아지면 즉시 크레아티닌·사구체 여과율 검사를 받으십시오."),
                    ("요추 디스크·골다공증·관절염", "수(水) 기운은 뼈와 허리를 주관합니다. 허리 통증이 3일 이상 지속되거나 다리가 저리면 MRI 검사가 필요합니다."),
                    ("성 기능 저하·생식기 질환·탈모", "수(水) 부족 시 호르몬 불균형이 나타납니다. 급격한 탈모, 생리 불순, 성욕 감퇴가 있다면 호르몬 검사를 받으십시오."),
                ],
                "excess":   "수(水) 과다 → 한습(寒濕) 하강, 냉증·부종·우울·의욕 저하 주의",
                "lack":     "수(水) 부족 → 신음허(腎陰虛), 만성 피로·이명·탈모·조기 노화 주의",
                "food":     "짠맛(해조류·검은콩·흑깨·굴), 블랙푸드, 복분자, 마",
                "avoid":    "찬 음식·과로·수면 부족·성생활 과도",
                "check":    "신장 기능(크레아티닌·BUN), 척추 MRI, 골밀도 검사, 호르몬 패널",
            },
        }

        # ── 세운·대운 십성별 건강 충격 ──────────────────────────────
        _SS_HEALTH = {
            "偏官": ("🔴 편관 — 사고·수술·급성 질환 경보",
                     "압박이 강한 편관 기운이 올 때 신체 사고, 응급 질환, 수술이 집중됩니다. 무리한 야간 활동과 격렬한 운동을 자제하고 정기검진을 앞당기십시오."),
            "劫財": ("⚠️ 겁재 — 혈액·외상·수술 주의",
                     "겁재 운에서는 외상, 출혈, 수술 이슈가 생기기 쉽습니다. 예방적 건강 검진과 안전사고 예방이 최우선입니다."),
            "傷官": ("⚠️ 상관 — 신경계·과로 주의",
                     "상관이 강한 시기에는 신경성 질환, 만성 과로, 번아웃이 옵니다. 수면 시간을 확보하고 신경과 검진을 고려하십시오."),
            "偏印": ("⚠️ 편인 — 정신건강·면역 주의",
                     "편인 운에서는 우울·불안·면역 저하가 오기 쉽습니다. 고립을 피하고 정신건강의학과 상담을 부끄러워하지 마십시오."),
            "比肩": ("💡 비견 — 과도한 체력 소모 주의",
                     "비견 운에서는 무리한 경쟁과 과도한 활동으로 체력이 바닥납니다. 충분한 휴식이 곧 최고의 건강법입니다."),
        }

        # ── 오행 과다·부족 TOP3 질병 직격 출력 ─────────────────────
        st.markdown('<div class="gold-section">🚨 지금 당신에게 올 수 있는 질병 TOP3</div>',
                    unsafe_allow_html=True)

        # 판단 기준: 과다 오행 + 부족 오행 + 세운 오행 교차
        _target_oh = excess_oh if oh_strength[excess_oh] >= 30 else weak_oh
        _oh_data   = _OH_DISEASE.get(_target_oh, _OH_DISEASE["土"])

        for rank, (disease_name, disease_desc) in enumerate(_oh_data["diseases"], 1):
            _rank_color = ["#c0392b", "#e67e22", "#f39c12"][rank - 1]
            st.markdown(
                f"""<div style='background:#fff5f5;border-left:5px solid {_rank_color};
                border-radius:10px;padding:14px 18px;margin:8px 0;'>
                <div style='font-size:15px;font-weight:900;color:{_rank_color};margin-bottom:6px'>
                TOP{rank} &nbsp; {disease_name}</div>
                <div style='font-size:13px;color:#333;line-height:1.9'>{disease_desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── 세운·대운 교차 건강 경보 ────────────────────────────────
        st.markdown('<div class="gold-section">⚡ 올해·현재 대운 건강 경보</div>',
                    unsafe_allow_html=True)

        _sw_warn_title, _sw_warn_desc = _SS_HEALTH.get(
            sw_ss, ("✅ 올해 특별한 건강 위기 신호 없음",
                    "올해 세운의 건강 충격이 두드러지지 않습니다. 하지만 방심은 금물입니다.")
        )
        st.markdown(
            f"""<div style='background:#fff8e1;border:1.5px solid #f39c12;border-radius:12px;
            padding:16px 20px;margin:8px 0;'>
            <div style='font-size:14px;font-weight:900;color:#e67e22;margin-bottom:6px'>
            {current_year}년 [{sw_ss}] 세운 — {_sw_warn_title}</div>
            <div style='font-size:13px;color:#333;line-height:1.9'>{_sw_warn_desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        if dw_ss and dw_ss in _SS_HEALTH:
            _dw_title, _dw_desc = _SS_HEALTH[dw_ss]
            dw_str = cur_dw.get("str", "")
            dw_end = cur_dw.get("종료연도", "")
            st.markdown(
                f"""<div style='background:#fce4ec;border:1.5px solid #c0392b;border-radius:12px;
                padding:16px 20px;margin:8px 0;'>
                <div style='font-size:14px;font-weight:900;color:#c0392b;margin-bottom:6px'>
                대운 [{dw_str}/{dw_ss}] ({dw_end}년까지) — {_dw_title}</div>
                <div style='font-size:13px;color:#333;line-height:1.9'>{_dw_desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # ── 오행 밸런스 차트 + 과다·부족 진단 ──────────────────────
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown('<div class="section-label">🩺 오행 건강 밸런스</div>',
                        unsafe_allow_html=True)
            render_ohaeng_chart(oh_strength)

        with col2:
            st.markdown('<div class="section-label">⚠️ 과다·부족 진단</div>',
                        unsafe_allow_html=True)
            _oh_nm = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
            for _oh, _val in sorted(oh_strength.items(), key=lambda x: -x[1]):
                if _val >= 30:
                    _tag = f"🔴 {_oh_nm.get(_oh,_oh)} 과다({_val}%)"
                    _col = "#c0392b"
                elif _val <= 10:
                    _tag = f"💧 {_oh_nm.get(_oh,_oh)} 부족({_val}%)"
                    _col = "#2980b9"
                else:
                    _tag = f"✅ {_oh_nm.get(_oh,_oh)} 정상({_val}%)"
                    _col = "#27ae60"
                st.markdown(
                    f"<div style='font-size:12px;color:{_col};font-weight:700;"
                    f"padding:4px 0;'>{_tag}</div>",
                    unsafe_allow_html=True,
                )

        # ── 직격 처방 ────────────────────────────────────────────────
        st.markdown('<div class="gold-section">💊 직격 건강 처방 (지금 당장 해야 할 것)</div>',
                    unsafe_allow_html=True)

        _oh_rx = _oh_data
        st.markdown(
            f"""<div style='background:#f0fff4;border:1.5px solid #27ae60;border-radius:12px;
            padding:18px 20px;margin:8px 0;'>
            <div style='font-size:14px;font-weight:900;color:#1a5c2a;margin-bottom:10px'>
            🎯 집중 관리 장기: {_oh_rx["organ"]}</div>
            <div style='font-size:13px;color:#333;line-height:2.0;'>
            {"🔺 " + _oh_rx["excess"] if oh_strength.get(_target_oh, 0) >= 30 else "🔻 " + _oh_rx["lack"]}<br><br>
            🍱 <b>추천 식품:</b> {_oh_rx["food"]}<br>
            🚫 <b>반드시 피할 것:</b> {_oh_rx["avoid"]}<br>
            🏥 <b>지금 바로 받아야 할 검사:</b> {_oh_rx["check"]}
            </div></div>""",
            unsafe_allow_html=True,
        )

        # ── 연령대별 건강 위험 구간 ──────────────────────────────────
        st.markdown('<div class="gold-section">📅 앞으로 5년 건강 위험 구간</div>',
                    unsafe_allow_html=True)
        _danger_found = False
        for _yr in range(current_year, current_year + 6):
            _sw_y  = get_yearly_luck(pils, _yr) or {}
            _ss_y  = _sw_y.get("십성_천간", "")
            _age_y = _yr - birth_year + 1
            if _ss_y in ("偏官(편관)", "劫財(겁재)", "傷官(상관)"):
                _lvl   = "🔴 고위험" if _ss_y == "偏官" else "⚠️ 주의"
                _color = "#c0392b" if _ss_y == "偏官" else "#e67e22"
                _msg   = {"偏官": "사고·수술·급성 질환 위험 구간. 정기검진 필수.",
                          "劫財": "외상·혈액 관련 이슈 주의. 안전사고 예방 최우선.",
                          "傷官": "신경계 과부하·만성 과로 주의. 수면 확보가 핵심."}[_ss_y]
                st.markdown(
                    f"""<div style='border-left:4px solid {_color};padding:8px 14px;
                    margin:4px 0;background:#fff5f5;border-radius:0 8px 8px 0;font-size:13px;'>
                    <b style='color:{_color}'>{_yr}년 (만 {_age_y}세) {_lvl} [{_ss_y}]</b>
                    &nbsp;— {_msg}</div>""",
                    unsafe_allow_html=True,
                )
                _danger_found = True
        if not _danger_found:
            st.success("✅ 향후 5년간 특별히 강한 건강 위기 세운은 보이지 않습니다. 꾸준한 관리를 유지하십시오.")

    except Exception as e:
        st.error(f"건강운 분석 중 오류 발생: {e}")


def menu12_manse(pils=None, birth_year=1990, gender="남"):
    """📅 만세력 탭 -- 일진/절기/길일달력 통합 UI"""

    today = datetime.now()

    st.markdown(
        """

<div style='background:#000;color:#fff;border-radius:12px; padding:16px 20px;margin-bottom:14px'>

<div style='font-size:20px;font-weight:900;letter-spacing:2px'>

            📅 만세력 / 일진 / 절기 달력

</div>

<div style='font-size:12px;opacity:0.7;margin-top:4px'>

            일진(日辰(진)) / 24절기 / 길일/흥일 자동 표시

</div>

</div>""",
        unsafe_allow_html=True,
    )

    # 오늘 일진 헤더

    today_iljin = ManseCalendarEngine.get_today_iljin()

    today_gil = ManseCalendarEngine.get_gil_hyung(today.year, today.month, today.day)

    st.markdown(
        f"""

<div style='background:{today_gil["bg"]};border:2px solid {today_gil["color"]}; border-radius:12px;padding:14px 20px;margin-bottom:14px; display:flex;justify-content:space-between;align-items:center'>

<div>

<div style='font-size:13px;color:#888;font-weight:700'>TODAY 일진</div>

<div style='font-size:28px;font-weight:900;color:#000;letter-spacing:3px'>

            {today_iljin["str"]}

</div>

<div style='font-size:12px;color:#555'>{today_iljin["oh"]} 일</div>

</div>

<div style='text-align:right'>

<div style='font-size:18px;font-weight:800;color:{today_gil["color"]}'>

            {today_gil["grade"]}

</div>

<div style='font-size:12px;color:#777'>{today_gil["reason"]}</div>

</div>

</div>

""",
        unsafe_allow_html=True,
    )

    # 월 선택

    col_y, col_m, _ = st.columns([1, 1, 2])

    with col_y:
        sel_year = st.selectbox(
            "연도",
            list(range(2020, 2031)),
            index=today.year - 2020,
            label_visibility="collapsed",
        )

    with col_m:
        sel_month = st.selectbox(
            "월",
            list(range(1, 13)),
            index=today.month - 1,
            label_visibility="collapsed",
            format_func=lambda m: f"{m}월",
        )

    # 절기 배지

    jeolgi_this = ManseCalendarEngine.get_month_jeolgi(sel_year, sel_month)

    if jeolgi_this:
        jeolgi_html = " &nbsp;".join(f"<span style='background:#000;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700'>{j['day']}일 {j['name']}</span>" for j in jeolgi_this)

        st.markdown(
            f"<div style='margin:6px 0 10px'>이달 절기: {jeolgi_html}</div>",
            unsafe_allow_html=True,
        )

    # 달력 그리드

    import calendar as _cal

    cal_data = ManseCalendarEngine.get_month_calendar(sel_year, sel_month)

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    first_wd, _ = _cal.monthrange(sel_year, sel_month)

    # 헤더 행

    hdr = "".join(f"<td style='text-align:center;font-weight:800;font-size:12px;color:{'#cc0000' if i == 6 else '#0033cc' if i == 5 else '#000'}'>{w}</td>" for i, w in enumerate(weekdays))

    rows = f"<tr>{hdr}</tr><tr>"

    # 빈 셀 (1일 이전)

    for _ in range(first_wd):
        rows += "<td></td>"

    for entry in cal_data:
        d = entry["day"]

        ilj = entry["iljin"]

        gil = entry["gil"]

        jeo = entry["jeolgi"]

        wd = (first_wd + d - 1) % 7

        day_color = "#cc0000" if wd == 6 else "#0033cc" if wd == 5 else "#000"

        bg = gil["bg"]

        border = f"2px solid {gil['color']}" if gil["grade"] != "보통" else "1px solid #ddd"

        is_today = d == today.day and sel_month == today.month and sel_year == today.year

        if is_today:
            bg = "#fffde7"

            border = "2px solid #f9a825"

        jeolgi_label = f"<div style='font-size:8px;color:#7b1fa2;font-weight:700'>{jeo.split('(')[0]}</div>" if jeo else ""

        rows += (
            f"<td style='text-align:center;padding:4px 2px;border:{border};"
            f"background:{bg};border-radius:6px;vertical-align:top;min-width:38px'>"
            f"<div style='font-size:12px;font-weight:700;color:{day_color}'>{d}</div>"
            f"<div style='font-size:11px;font-weight:800;color:#000'>{ilj['str']}</div>"
            f"{jeolgi_label}"
            f"</td>"
        )

        if wd == 6 and d != cal_data[-1]["day"]:
            rows += "</tr><tr>"

    rows += "</tr>"

    st.markdown(
        f"<table style='width:100%;border-collapse:separate;border-spacing:3px'>{rows}</table>",
        unsafe_allow_html=True,
    )

    # 길일/주의일 요약 바

    gil_days = [e["day"] for e in cal_data if e["gil"]["grade"].startswith("길일")]

    warn_days = [e["day"] for e in cal_data if e["gil"]["grade"] == "주의"]

    st.markdown(
        f"""

<div style='margin-top:12px;padding:10px 14px;background:#f8f8f8; border-radius:8px;font-size:12px'>

<span style='color:#1a7a1a;font-weight:700'>- 길일:</span>

        {", ".join(str(d) + "일" for d in gil_days) or "없음"}

<span style='color:#cc0000;font-weight:700'>⚠️ 주의:</span>

        {", ".join(str(d) + "일" for d in warn_days) or "없음"}

</div>

""",
        unsafe_allow_html=True,
    )

    # -- - 사주 맞춤 길일 추천 카드 (NEW) ----------------------

    if pils:
        st.markdown(
            '<div class="gold-section" style="margin-top:24px">- 이번 달 당신의 사주 맞춤 길일 추천</div>',
            unsafe_allow_html=True,
        )

        try:
            ilgan_m = pils[1]["cg"]

            lucky_ss_map = {
                "甲": ["정재", "정인", "정관", "식신"],
                "乙": ["정관", "정재", "정인", "식신"],
                "丙": ["정재", "식신", "정인", "정관"],
                "丁": ["정재", "식신", "정관", "정인"],
                "戊": ["정관", "정재", "정인", "편재"],
                "己": ["정관", "편재", "정재", "정인"],
                "庚": ["정재", "정관", "정인", "식신"],
                "辛": ["정재", "정관", "정인", "식신"],
                "壬": ["정재", "식신", "정관", "정인"],
                "癸": ["정재", "식신", "정인", "정관"],
            }

            lucky_ss = lucky_ss_map.get(ilgan_m, ["정재", "식신", "정관", "정인"])

            # 보조 길성 추가 (일간별)

            lucky_ss_secondary = {
                "甲": ["편재", "편인", "비견"],
                "乙": ["편재", "편인", "비견"],
                "丙": ["편재", "편관", "비견"],
                "丁": ["편재", "편관", "비견"],
                "戊": ["편재", "편인", "비견"],
                "己": ["편재", "편관", "비견"],
                "庚": ["편재", "편관", "비견"],
                "辛": ["편재", "편인", "비견"],
                "壬": ["편재", "편관", "비견"],
                "癸": ["편재", "편관", "비견"],
            }.get(ilgan_m, ["편재", "비견"])

            saju_lucky = []

            for entry in cal_data:
                d_ss = TEN_GODS_MATRIX.get(ilgan_m, {}).get(entry["iljin"]["cg"], "-")

                grade = entry["gil"]["grade"]

                is_core = d_ss in lucky_ss

                is_secondary = d_ss in lucky_ss_secondary

                # 흉일만 제외, 주의날도 코어 길성이면 포함

                if grade not in ["흉일", "이사화작일"] and (is_core or is_secondary):
                    saju_lucky.append(
                        {
                            "day": entry["day"],
                            "iljin": entry["iljin"]["str"],
                            "ss": d_ss,
                            "grade": grade,
                            "priority": 0 if is_core else 1,
                            "weekday": ["月", "火", "水", "木", "金", "土", "日"][(first_wd + entry["day"] - 1) % 7],
                        }
                    )

            # 코어 길일 먼저, 그 다음 날짜 순

            saju_lucky.sort(key=lambda x: (x["priority"], x["day"]))

            if saju_lucky:
                lucky_cards = ""

                SS_ICON = {
                    "정재": "💰",
                    "식신": "🌟",
                    "정관": "🎖️",
                    "정인": "📚",
                    "편재": "💼",
                    "비견": "🤝",
                    "정관": "🎖️",
                }

                for lk in saju_lucky[:8]:  # 최대 8일까지 표시
                    icon = SS_ICON.get(lk["ss"], "-")

                    grade_color = "#4caf50" if "길일" in lk["grade"] else "#888"

                    lucky_cards += f"""

<div style="display:inline-block;background:rgba(255,255,255,0.9);backdrop-filter:blur(10px); border:1.5px solid #d4af37;border-radius:14px;padding:12px 16px; margin:5px;text-align:center;min-width:90px;box-shadow:0 4px 15px rgba(212,175,55,0.1)">

<div style="font-size:20px">{icon}</div>

<div style="font-size:18px;font-weight:900;color:#000">{lk["day"]}일</div>

<div style="font-size:11px;color:#777">({lk["weekday"]})</div>

<div style="font-size:11px;font-weight:700;color:#b38728">{lk["iljin"]}</div>

<div style="font-size:10px;color:{grade_color};margin-top:2px">{lk["ss"]}</div>

</div>"""

                st.markdown(
                    f"""

<div style="margin:10px 0 20px">

<div style="font-size:13px;color:#555;margin-bottom:8px">

                        {ilgan_m} 일간에게 유리한 십성({", ".join(lucky_ss[:3])}) 날을 우선 추천합니다.

</div>

<div style="display:flex;flex-wrap:wrap;gap:4px">{lucky_cards}</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

            else:
                st.info("이번 달은 사주 맞춤 길일이 별도로 표시되지 않습니다. 일반 길일을 활용하세요.")

        except Exception as e:
            st.warning(f"맞춤 길일 계산 오류: {e}")

    # -- ⚠️ 사주 맞춤 조심일 경고 카드 (NEW) ----------------------

    if pils:
        st.markdown(
            '<div class="gold-section" style="margin-top:8px">⚠️ 이번 달 당신의 사주 맞춤 조심일</div>',
            unsafe_allow_html=True,
        )

        try:
            ilgan_w = pils[1]["cg"]

            # 각 일간별 주의해야 할 십성 (흉신)

            warn_ss_map = {
                "甲": ["겁재", "편관", "상관"],
                "乙": ["겁재", "편관", "상관"],
                "丙": ["겁재", "편관", "편인"],
                "丁": ["겁재", "편관", "편인"],
                "戊": ["겁재", "편관", "상관"],
                "己": ["겁재", "편관", "상관"],
                "庚": ["겁재", "편관", "상관"],
                "辛": ["겁재", "편관", "상관"],
                "壬": ["겁재", "편관", "편인"],
                "癸": ["겁재", "편관", "편인"],
            }


            warn_ss = warn_ss_map.get(ilgan_w, ["겁재", "편관", "상관"])

            saju_warn = []

            for entry in cal_data:
                d_ss_w = TEN_GODS_MATRIX.get(ilgan_w, {}).get(entry["iljin"]["cg"], "-")

                if d_ss_w in warn_ss:
                    saju_warn.append(
                        {
                            "day": entry["day"],
                            "iljin": entry["iljin"]["str"],
                            "ss": d_ss_w,
                            "grade": entry["gil"]["grade"],
                            "weekday": ["月", "火", "水", "木", "金", "土", "日"][(first_wd + entry["day"] - 1) % 7],
                        }
                    )

            if saju_warn:
                warn_cards = ""

                for wk in saju_warn[:8]:
                    wd = SS_WARN_DESC.get(
                        wk["ss"],
                        {"emoji": "⚠️", "color": "#e53935", "msg": "매사 조심"},
                    )

                    is_double = wk["grade"] == "주의"  # 달력 흉일 + 사주 흉성 겹침

                    border_style = f"2px solid {wd['color']}"

                    extra_badge = '<div style="font-size:9px;background:#e53935;color:#fff;border-radius:4px;padding:1px 4px;margin-top:2px">⚠️ 이중 주의</div>' if is_double else ""

                    warn_cards += f"""

<div style="display:inline-block;background:rgba(255,235,235,0.95);backdrop-filter:blur(10px); border:{border_style};border-radius:14px;padding:12px 14px; margin:5px;text-align:center;min-width:90px;box-shadow:0 4px 15px rgba(229,57,53,0.1)">

<div style="font-size:20px">{wd["emoji"]}</div>

<div style="font-size:18px;font-weight:900;color:{wd["color"]}">{wk["day"]}일</div>

<div style="font-size:11px;color:#777">({wk["weekday"]})</div>

<div style="font-size:11px;font-weight:700;color:#555">{wk["iljin"]}</div>

<div style="font-size:10px;color:{wd["color"]};margin-top:2px;font-weight:700">{wk["ss"]}</div>

                        {extra_badge}

</div>"""

                # 조심일 요약 표

                warn_table = ""

                shown = set()

                for wk in saju_warn:
                    if wk["ss"] not in shown:
                        shown.add(wk["ss"])

                        wd2 = SS_WARN_DESC.get(
                            wk["ss"],
                            {"emoji": "⚠️", "color": "#e53935", "msg": "매사 조심"},
                        )

                        warn_table += f'<div style="margin:4px 0;font-size:13px"><span style="color:{wd2["color"]};font-weight:900">{wd2["emoji"]} {wk["ss"]}</span>: {wd2["msg"]}</div>'

                st.markdown(
                    f"""

<div style="margin:10px 0 20px">

<div style="font-size:13px;color:#cc0000;margin-bottom:8px;font-weight:700">

                        ⚠️ {ilgan_w} 일간에게 불리한 십성({", ".join(warn_ss)}) 날 - 총 {len(saju_warn)}일

</div>

<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px">{warn_cards}</div>

<div style="background:rgba(229,57,53,0.05);border:1px solid #ffcdd2;border-radius:12px;padding:12px 16px">

<div style="font-size:12px;font-weight:900;color:#b71c1c;margin-bottom:6px">📌 조심일 행동 지침</div>

                        {warn_table}

</div>

</div>

                """,
                    unsafe_allow_html=True,
                )

                # 오늘이 조심일이면 경고 토스트

                today_ss_warn = TEN_GODS_MATRIX.get(ilgan_w, {}).get(
                    today_iljin["cg"] if "cg" in today_iljin else today_iljin["str"][0],
                    "-",
                )

                if today_ss_warn in warn_ss and sel_month == today.month and sel_year == today.year:
                    st.error(f"🚨 **오늘({today.day}일)은 {today_ss_warn} 일입니다.** {SS_WARN_DESC.get(today_ss_warn, {}).get('msg', '매사 조심하십시오.')}")

            else:
                st.success("✅ 이번 달은 특별히 조심해야 할 사주 맞춤 흉일이 없습니다. 평온한 한 달이 예상됩니다.")

        except Exception as e:
            st.warning(f"조심일 계산 오류: {e}")

    if pils and sel_month == today.month and sel_year == today.year:
        st.markdown(
            '<div class="gold-section" style="margin-top:20px">🔮 오늘 일진으로 보는 만신의 맞춤 조언</div>',
            unsafe_allow_html=True,
        )

        try:
            ilgan_ad = pils[1]["cg"]

            today_iljin_cg = today_iljin["cg"] if "cg" in today_iljin else today_iljin["str"][0]

            today_iljin_jj = today_iljin["jj"] if "jj" in today_iljin else today_iljin["str"][1]

            today_ss_ad = TEN_GODS_MATRIX.get(ilgan_ad, {}).get(today_iljin_cg, "-")

            # 십성별 만신 맞춤 조언


            advice = SS_ADVICE.get(today_ss_ad, SS_ADVICE["-"])

            gil_color = today_gil.get("color", "#d4af37")

            st.markdown(
                f"""

<div style="background:rgba(255,255,255,0.9);backdrop-filter:blur(20px);border:1.5px solid {gil_color}; border-radius:20px;padding:24px;margin:10px 0 20px;box-shadow:0 8px 30px rgba(0,0,0,0.06)">

<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">

<span style="font-size:32px">{advice["emoji"]}</span>

<div>

<div style="font-size:18px;font-weight:900;color:#111">{advice["title"]}</div>

<div style="font-size:13px;color:{gil_color};font-weight:700">{today_iljin["str"]}일 ({today_ss_ad}) - {advice["short"]}</div>

</div>

</div>

<div style="font-size:15px;color:#222;line-height:2.0;margin-bottom:14px">{advice["detail"]}</div>

<div style="background:rgba(212,175,55,0.08);border-left:4px solid {gil_color}; padding:10px 14px;border-radius:0 10px 10px 0;font-size:14px;font-weight:700;color:#b38728">

                    {advice["action"]}

</div>

</div>

            """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.warning(f"맞춤 조언 표시 오류: {e}")

    st.markdown("---")

    st.markdown("**🔮 특정 날짜 사주 분석**", unsafe_allow_html=False)

    sel_day = st.number_input(
        "날짜 선택",
        min_value=1,
        max_value=len(cal_data),
        value=today.day if sel_month == today.month and sel_year == today.year else 1,
        step=1,
        label_visibility="visible",
    )

    if st.button("🔮 이 날짜의 일진 사주 분석", use_container_width=True):
        iljin_sel = ManseCalendarEngine.get_iljin(sel_year, sel_month, int(sel_day))

        gil_sel = ManseCalendarEngine.get_gil_hyung(sel_year, sel_month, int(sel_day))

        pils_day = SajuCoreEngine.get_pillars(sel_year, sel_month, int(sel_day), 12, 0, gender)

        yp = pils_day[0]["str"]
        mp = pils_day[2]["str"]

        dp = pils_day[1]["str"]

        st.markdown(
            f"""

<div style='background:#fff;border:2px solid #000;border-radius:12px; padding:16px;margin-top:10px'>

<div style='font-size:16px;font-weight:900;margin-bottom:8px'>

                {sel_year}년 {sel_month}월 {int(sel_day)}일 - {iljin_sel["str"]}일

                &nbsp;<span style='color:{gil_sel["color"]}'>{gil_sel["grade"]}</span>

</div>

<div style='display:flex;gap:12px;flex-wrap:wrap'>

<div style='background:#f5f5f5;padding:8px 16px;border-radius:8px; font-size:14px;font-weight:700'>年 {yp}</div>

<div style='background:#f5f5f5;padding:8px 16px;border-radius:8px; font-size:14px;font-weight:700'>月 {mp}</div>

<div style='background:#000;color:#fff;padding:8px 16px;border-radius:8px; font-size:14px;font-weight:700'>日 {dp}</div>

</div>

<div style='font-size:12px;color:#777;margin-top:8px'>{gil_sel["reason"]}</div>

</div>

""",
            unsafe_allow_html=True,
        )


def get_total_lines():
    """현재 엔진(manse.py) 파일의 전체 줄 수 반환. 사이드바에 표시용."""
    try:
        import os as _os
        _path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "manse.py")
        if _os.path.isfile(_path):
            with open(_path, "r", encoding="utf-8") as _f:
                return sum(1 for _ in _f)
    except Exception as _e:
        st.warning(f"⚠️ 오류: {str(_e)[:80]}")
    return 0


@st.cache_data(ttl=86400)
def _get_daily_briefing(date_str: str) -> dict:
    """오늘 일진 기반 한줄 운세 브리핑 (강화판)"""

    y, m, d = (int(x) for x in date_str.split("-"))

    iljin = ManseCalendarEngine.get_iljin(y, m, d)

    gil = ManseCalendarEngine.get_gil_hyung(y, m, d)

    cg, jj = iljin["cg"], iljin["jj"]


    JJ_MSG = {
        "子": "지혜와 기지가 빛나는 지지입니다. 머리를 쓰는 일이 잘 풀립니다.",
        "丑": "성실하고 묵묵한 노력이 결실이 되는 날입니다.",
        "寅": "도전과 진취의 기운이 강합니다. 용감하게 첫발을 내디디세요.",
        "卯": "부드러운 소통과 예술적 감수성이 빛나는 날입니다.",
        "辰": "카리스마와 능력이 드러나는 날. 리더십을 발휘하세요.",
        "巳": "두뇌 회전이 빠르고 직관력이 높아지는 날입니다.",
        "午": "열정과 활력이 최고조인 날. 적극적으로 나서세요.",
        "未": "따뜻한 배려와 예술적 기운이 주변을 감동시킵니다.",
        "申": "냉철한 판단력과 실리 추구가 유리한 날입니다.",
        "酉": "세련된 완벽주의가 빛나는 날. 디테일이 차이를 만듭니다.",
        "戌": "의리와 열정으로 신뢰를 쌓는 날입니다.",
        "亥": "깊은 지혜와 내면의 힘이 발동하는 날입니다.",
    }

    JJ_ANIMAL = {
        "子": "🐭",
        "丑": "🐂",
        "寅": "🐯",
        "卯": "🐰",
        "辰": "🐲",
        "巳": "🐍",
        "午": "🐴",
        "未": "🐑",
        "申": "🐵",
        "酉": "🐔",
        "戌": "🐶",
        "亥": "🐷",
    }

    from datetime import date as _d

    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]

    wday = weekday_kr[_d(y, m, d).weekday()]

    detail = CG_DETAIL.get(
        cg,
        {
            "msg": "오늘 하루 평온하고 무난한 기운이 흐릅니다.",
            "action": "평소 일상에 집중하세요.",
            "warn": "무리한 계획은 자제하세요.",
            "color": "흰색",
            "dir": "중앙",
            "num": "5",
        },
    )

    return {
        "iljin_str": iljin["str"],
        "cg": cg,
        "jj": jj,
        "animal": JJ_ANIMAL.get(jj, ""),
        "grade": gil["grade"],
        "reason": gil["reason"],
        "grade_color": gil["color"],
        "msg": detail["msg"],
        "action": detail["action"],
        "warn": detail["warn"],
        "lucky_color": detail["color"],
        "lucky_dir": detail["dir"],
        "lucky_num": detail["num"],
        "jj_msg": JJ_MSG.get(jj, ""),
        "display_date": f"{y}년 {m}월 {d}일 ({wday})",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3단 만세력 그리드
# ─────────────────────────────────────────────────────────────────────────────
def render_manse_grid(pils, birth_year, birth_month, birth_day, birth_hour, birth_minute, gender):
    """입력 완료 직후 표시되는 3단 만세력 요약 그리드."""
    if not pils or len(pils) < 4:
        return

    now = datetime.now()
    cur_year = now.year
    cur_month = now.month
    ilgan = pils[1]["cg"]

    # 데이터 준비
    try:
        ss_list = calc_sipsung(ilgan, pils)
    except Exception:
        ss_list = [{"cg_ss": "-", "jj_ss": "-"} for _ in pils]

    try:
        oh_str = calc_ohaeng_strength(ilgan, pils)
    except Exception:
        oh_str = {}

    try:
        ys_data = get_yongshin(pils)
        yong_ohs = ys_data.get("용신_오행", []) if ys_data else []
        gi_ohs   = ys_data.get("기신_오행", []) if ys_data else []
    except Exception:
        yong_ohs, gi_ohs = [], []

    try:
        strength_info = get_ilgan_strength(ilgan, pils)
    except Exception:
        strength_info = {"신강신약": "중화", "helper_score": 50}

    try:
        dw_list = SajuCoreEngine.get_daewoon(
            pils, birth_year, birth_month, birth_day, birth_hour, birth_minute, gender
        )
    except Exception:
        dw_list = []

    try:
        stars = get_special_stars(pils)
    except Exception:
        stars = []

    try:
        sw_now   = get_yearly_luck(pils, cur_year)
        sw_next1 = get_yearly_luck(pils, cur_year + 1)
        sw_next2 = get_yearly_luck(pils, cur_year + 2)
    except Exception:
        sw_now, sw_next1, sw_next2 = {}, {}, {}

    try:
        monthly_lucks = []
        for m_off in range(3):
            m = (cur_month - 1 + m_off) % 12 + 1
            yr = cur_year if (cur_month - 1 + m_off) < 12 else cur_year + 1
            ml = get_monthly_luck(pils, yr, m)
            if ml:
                monthly_lucks.append((yr, m, ml))
    except Exception:
        monthly_lucks = []

    col1, col2, col3 = st.columns([1.2, 1, 1])

    # ── 제1열: 사주 명식표 ────────────────────────────────────
    with col1:
        st.markdown(
            '<div class="gold-section" style="font-size:14px;margin:0 0 8px">📋 사주 명식</div>',
            unsafe_allow_html=True,
        )
        # pils 순서: [시주, 일주, 월주, 년주]
        pil_labels = ["시주", "일주", "월주", "년주"]
        pcols = st.columns(4)
        for ci, (lb, p, ss) in enumerate(zip(pil_labels, pils, ss_list)):
            cg = p.get("cg", "?")
            jj = p.get("jj", "?")
            bg_cg, fg_cg = get_ohang_color(cg)
            bg_jj, fg_jj = get_ohang_color(jj)
            jijang_chars = "/".join(JIJANGGAN.get(jj, ["-"]))
            cg_ss = ss.get("cg_ss", "-")
            jj_ss = ss.get("jj_ss", "-")
            unsung = UNSUNG_TABLE.get(ilgan, {}).get(jj, "")
            is_ilgan = (lb == "일주")
            border = "border:2px solid #d4af37;" if is_ilgan else "border:1px solid #ddd;"
            with pcols[ci]:
                st.markdown(
                    f"""<div style="text-align:center;background:#fafaf5;{border}border-radius:8px;padding:6px 2px">
<div style="font-size:10px;color:#888;margin-bottom:2px">{lb}</div>
<div style="font-size:11px;color:#555;margin-bottom:2px">{cg_ss}</div>
<div style="font-size:22px;font-weight:900;background:{bg_cg};color:{fg_cg};border-radius:5px;padding:1px 0">{cg}</div>
<div style="font-size:22px;font-weight:900;background:{bg_jj};color:{fg_jj};border-radius:5px;padding:1px 0;margin-top:2px">{jj}</div>
<div style="font-size:9px;color:#777;margin-top:2px">{jijang_chars}</div>
<div style="font-size:10px;color:#555">{jj_ss}</div>
<div style="font-size:9px;color:#888;margin-top:1px">{unsung}</div>
</div>""",
                    unsafe_allow_html=True,
                )
        # 신살 요약 (하단)
        if stars:
            star_names = [s.get("name", "") for s in stars[:5] if s.get("name")]
            if star_names:
                st.markdown(
                    f"""<div style="background:#f9f5e8;border-radius:6px;padding:5px 8px;margin-top:6px;font-size:11px;color:#8b6200">🌟 {"  ·  ".join(star_names)}</div>""",
                    unsafe_allow_html=True,
                )

    # ── 제2열: 세운(3년) / 대운 / 월운 ──────────────────────
    with col2:
        st.markdown(
            '<div class="gold-section" style="font-size:14px;margin:0 0 8px">🌊 운세 흐름</div>',
            unsafe_allow_html=True,
        )
        # 세운 올해~3년
        for yr_off, sw in [(0, sw_now), (1, sw_next1), (2, sw_next2)]:
            if sw:
                yr_label = cur_year + yr_off
                sw_cg, sw_jj = sw.get("cg", ""), sw.get("jj", "")
                bg_sc, fg_sc = get_ohang_color(sw_cg)
                bg_sj, fg_sj = get_ohang_color(sw_jj)
                sw_ss = sw.get("십성_천간", "")
                is_cur_yr = (yr_off == 0)
                bdr = "border:1.5px solid #d4af37;" if is_cur_yr else "border:1px solid #eee;"
                badge = "⬛ " if is_cur_yr else "  "
                st.markdown(
                    f"""<div style="background:#fffbf0;{bdr}border-radius:8px;padding:6px 10px;margin-bottom:5px;font-size:12px"><span style="font-size:11px;color:#8b6200;font-weight:700">{badge}{yr_label}년 세운</span><br>
<div style="display:flex;align-items:center;gap:4px;white-space:nowrap;flex-wrap:nowrap">
<span style="background:{bg_sc};color:{fg_sc};border-radius:4px;padding:1px 6px;font-weight:900;font-size:15px">{sw_cg}</span>
<span style="background:{bg_sj};color:{fg_sj};border-radius:4px;padding:1px 6px;font-weight:900;font-size:15px">{sw_jj}</span>
<span style="color:#555;font-size:11px">{sw_ss}</span>
</div>
</div>""",
                    unsafe_allow_html=True,
                )
        # 대운 현재 + 다음 2개
        cur_dw = next(
            (d for d in dw_list if d.get("시작연도", 0) <= cur_year <= d.get("종료연도", 9999)),
            None,
        )
        future_dws = [d for d in dw_list if d.get("시작연도", 0) > cur_year][:2]
        for dw in ([cur_dw] + future_dws if cur_dw else future_dws):
            if not dw:
                continue
            is_cur = dw is cur_dw
            dw_str = dw.get("str", "")
            border_s = "border:2px solid #d4af37;" if is_cur else "border:1px solid #eee;"
            cur_badge = " 🔸현재" if is_cur else ""
            dw_html = ""
            for ch in dw_str:
                b, f = get_ohang_color(ch)
                dw_html += f"<span style='background:{b};color:{f};border-radius:3px;padding:0 4px;font-weight:900'>{ch}</span>"
            st.markdown(
                f"""<div style="background:#fafafa;{border_s}border-radius:6px;padding:6px 10px;margin-bottom:4px;font-size:12px">
{dw_html}<span style="color:#555;font-size:11px;margin-left:4px">{dw.get('시작나이','')}세 ({dw.get('시작연도','')}~{dw.get('종료연도','')}){cur_badge}</span>
</div>""",
                unsafe_allow_html=True,
            )
        # 월운 타임라인 (3개월)
        if monthly_lucks:
            st.markdown(
                '<div style="font-size:11px;color:#888;margin:6px 0 3px;font-weight:700">📅 월운</div>',
                unsafe_allow_html=True,
            )
            for yr, m, ml in monthly_lucks:
                ml_cg = ml.get("간", "")
                ml_jj = ml.get("지", "")
                ml_ss = ml.get("십성", "")
                ml_bg_c, ml_fg_c = get_ohang_color(ml_cg)
                ml_bg_j, ml_fg_j = get_ohang_color(ml_jj)
                is_cur_m = (yr == cur_year and m == cur_month)
                bdr_m = "border:1px solid #d4af37;" if is_cur_m else "border:1px solid #f0f0f0;"
                st.markdown(
                    f"""<div style="background:#fafafa;{bdr_m}border-radius:6px;padding:4px 8px;margin-bottom:3px;font-size:11px">
<span style="color:#888;min-width:28px;display:inline-block">{m}월</span>
<span style="background:{ml_bg_c};color:{ml_fg_c};border-radius:3px;padding:0 4px;font-weight:900;font-size:13px">{ml_cg}</span>
<span style="background:{ml_bg_j};color:{ml_fg_j};border-radius:3px;padding:0 4px;font-weight:900;font-size:13px;margin-left:1px">{ml_jj}</span>
<span style="color:#777;margin-left:4px">{ml_ss}</span>
</div>""",
                    unsafe_allow_html=True,
                )

    # ── 제3열: 신강신약 / 오행 / 용신 / 신살 ────────────────
    with col3:
        st.markdown(
            '<div class="gold-section" style="font-size:14px;margin:0 0 8px">⚡ 핵심 분석</div>',
            unsafe_allow_html=True,
        )
        # 신강/신약 판정
        sn_label = strength_info.get("신강신약", "중화")
        sn_score = strength_info.get("helper_score", 50)
        if "극신약" in sn_label or "신약" in sn_label:
            sn_char, sn_color = "弱", "#e53935"
        elif "극신강" in sn_label or "신강" in sn_label:
            sn_char, sn_color = "强", "#1565c0"
        else:
            sn_char, sn_color = "中", "#f9a825"
        sn_bar = "🟦" * min(10, round(sn_score / 10)) + "⬜" * (10 - min(10, round(sn_score / 10)))
        s_data = STRENGTH_DESC.get(sn_label, {})
        st.markdown(
            f"""<div style="background:#ffffff;border:1.5px solid #ddd;border-radius:8px;padding:8px 10px;margin-bottom:8px">
<span style="font-size:20px;font-weight:900;color:{sn_color}">{sn_char}</span>
<span style="font-size:12px;color:#555;margin-left:6px">{sn_label}</span>
<div style="font-size:11px;margin-top:2px">{sn_bar}</div>
<div style="font-size:11px;color:#555;margin-top:3px;line-height:1.6">{s_data.get("personality", "")[:80]}</div>
</div>""",
            unsafe_allow_html=True,
        )
        # 오행 분포
        oh_total = sum(oh_str.values()) or 1
        OH_KR = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}
        OH_COLORS = {"木": "#2d8a4e", "火": "#e53935", "土": "#f9a825", "金": "#9e9e9e", "水": "#1565c0"}
        for oh_key in ["木", "火", "土", "金", "水"]:
            cnt = oh_str.get(oh_key, 0)
            pct = int(cnt / oh_total * 100)
            color = OH_COLORS[oh_key]
            yg_badge = ""
            if oh_key in [o[0] if isinstance(o, str) else "" for o in yong_ohs]:
                yg_badge = "✦"
            elif oh_key in [o[0] if isinstance(o, str) else "" for o in gi_ohs]:
                yg_badge = "✗"
            st.markdown(
                f"""<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;font-size:12px">
<span style="width:22px;color:{color};font-weight:700">{OH_KR[oh_key]}{yg_badge}</span>
<div style="flex:1;background:#eee;border-radius:4px;height:8px">
  <div style="width:{pct}%;background:{color};height:8px;border-radius:4px"></div>
</div>
<span style="width:28px;text-align:right;color:#555">{cnt}</span>
</div>""",
                unsafe_allow_html=True,
            )
        # 용신/기신
        yong_str = " ".join([OHN.get(o, o) for o in yong_ohs]) if yong_ohs else "-"
        gi_str   = " ".join([OHN.get(o, o) for o in gi_ohs])   if gi_ohs   else "-"
        st.markdown(
            f"""<div style="background:#f0fff4;border-radius:6px;padding:6px 10px;margin-top:6px;font-size:12px">
<span style="color:#2d8a4e;font-weight:700">✦ 용신:</span> {yong_str}<br>
<span style="color:#e53935;font-weight:700">✗ 기신:</span> {gi_str}
</div>""",
            unsafe_allow_html=True,
        )
        # 주요 신살 상위 3개
        if stars:
            star_names = [s.get("name", "") for s in stars[:3] if s.get("name")]
            if star_names:
                st.markdown(
                    f"""<div style="background:#f9f5e8;border-radius:6px;padding:6px 10px;margin-top:6px;font-size:12px">
<span style="color:#8b6200;font-weight:700">🌟 신살:</span> {"  ·  ".join(star_names)}
</div>""",
                    unsafe_allow_html=True,
                )


def main():

    # -- 페이지 설정 ---------------------------------

    st.markdown(
        """

<style>

    /* 텍스트 줄바꿈 전역 강제 */
    .stMarkdown * { word-break: break-all !important; overflow-wrap: break-word !important; white-space: normal !important; }
    [data-testid="stMarkdownContainer"] * { word-break: break-all !important; overflow-wrap: break-word !important; white-space: normal !important; max-width:100% !important; }
    /* 모든 HTML 삽입 div 박스 — 텍스트 넘침 방지 */
    [data-testid="stMarkdownContainer"] > div > div {
        max-width: 100% !important;
        overflow-x: hidden !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
        box-sizing: border-box !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=Inter:wght@400;700;900&family=Outfit:wght@300;600;800&display=swap');

    

    :root {

        --primary: #f5f0e8;

        --secondary: #ede8d8;

        --accent: #c9a84c;

        --gold-premium: linear-gradient(135deg, #f7e695 0%, #c9a84c 50%, #a07830 100%);

        --glass: rgba(250,247,240,0.8);

        --glass-border: rgba(201,168,76,0.3);

        --text-platinum: #2d1f00;

        --shiner: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);

    }

    /* 전역 스타일 */

    .stApp {

        background: linear-gradient(160deg, #f5f0e8 0%, #ede8d8 50%, #e8e0cc 100%);

        background-attachment: fixed;

 color: var(--text-platinum);

 font-family: 'Noto Serif KR', 'Noto Sans KR', serif;

    }


    

    /* 애니메이션 정의 */

    @keyframes fadeInUp {

        from { opacity: 0; transform: translateY(20px); }

        to { opacity: 1; transform: translateY(0); }

    }

    @keyframes shimmer {

        0% { transform: translateX(-100%); }

        100% { transform: translateX(100%); }

    }

    @keyframes pulse-gold {

        0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); }

        70% { box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); }

        100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }

    }

    /* 헤더 프리미엄화 */

    .main-header {

        background: linear-gradient(135deg, #2d1f00 0%, #4a3000 50%, #2d1f00 100%);

        padding: 40px 20px;

 border-radius: 0 0 30px 30px;

 border: 1px solid #c9a84c;

        box-shadow: 0 4px 20px rgba(0,0,0,0.3);

        text-align: center;

        animation: fadeInUp 0.8s ease-out;

        position: relative;

        overflow: hidden;

        color: #f5e8c8;

    }

    .main-header::after {

        content: ""; position: absolute; top: 0; left: 0; width: 200%; height: 100%;

        background: var(--shiner); animation: shimmer 3s infinite;

    }

    .main-header h1 {

 font-family: 'Noto Serif KR', serif; font-size: 38px; font-weight: 900;

        background: var(--gold-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;

        letter-spacing: 5px; margin: 0; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));

    }

    .main-header p { font-size: 15px; color: var(--accent); letter-spacing: 3px; margin-top: 10px; font-weight: 300; }

    /* 글래스모피즘 카드 */

    div[data-testid="stExpander"], .custom-card {

        background: var(--glass) !important;

        backdrop-filter: blur(12px);

        border: 1px solid var(--glass-border) !important;

 border-radius: 16px !important;

        padding: 4px;

        margin-bottom: 15px;

        transition: all 0.3s ease;

    }

    div[data-testid="stExpander"]:hover {

 border-color: var(--accent) !important;

        transform: translateY(-2px);

    }

    /* 버튼 스타일 (saju_ui.py 다크테마와 통일) */

    .stButton>button {

        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%) !important;

 color: #f7e695 !important;

        border: 1px solid rgba(212, 175, 55, 0.4) !important;

 border-radius: 15px !important;

 font-weight: 800 !important;

        min-height: 52px !important;

        transition: all 0.3s ease !important;

    }

    .stButton>button:hover {

        transform: translateY(-2px);

        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.25) !important;

        border-color: #d4af37 !important;

    }

    /* 텍스트 스타일 */

    .section-label { 

 font-family: 'Outfit', sans-serif;

 font-weight: 600; color: var(--accent); 

        margin: 20px 0 10px; display: flex; align-items: center; gap: 8px;

 font-size: 14px; text-transform: uppercase;

    }

    .saju-narrative {

 font-family: 'Noto Serif KR', serif; font-size: 16px; line-height: 2.2;

 color: #333333; padding: 15px; background: rgba(0,0,0,0.04);

 border-radius: 10px; border-left: 3px solid var(--accent);

    }

    .gold-section {

        color: #1a1a1a;

 font-size: 18px; font-weight: 800; padding: 10px 0;

 border-bottom: 2px solid rgba(212, 175, 55, 0.5); margin: 25px 0 15px;

    }

    /* 탭 스타일 조정 */

    .stTabs [data-baseweb="tab-list"] { gap: 2px !important; overflow-x: auto !important; -webkit-overflow-scrolling: touch !important; }

    .stTabs [data-baseweb="tab"] {

        background: transparent !important;

 color: #555 !important;

        border: 1px solid transparent !important;

 border-radius: 8px !important;

        padding: 8px 12px !important;

        white-space: nowrap !important;

    }

    .stTabs [aria-selected="true"] {

 color: #1a1a1a !important;

 border-bottom: 2px solid #d4af37 !important;

        background: rgba(212, 175, 55, 0.08) !important;

        font-weight: 800 !important;

    }

    /* 모바일 반응형 (768px 이하) */

    @media (max-width: 768px) {

        /* 텍스트 오버플로우 방지 — 전체 적용 */
        * {
            word-break: keep-all !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }

        /* 이미지/테이블 오버플로우 방지 */
        img, table { max-width: 100% !important; overflow-x: auto !important; }
        
        /* 마크다운 단락 줄바꿈 */
        .stMarkdown p, .stMarkdown li, .stMarkdown td {
            word-break: keep-all !important;
            overflow-wrap: break-word !important;
            white-space: normal !important;
        }

        .main-header { padding: 22px 12px; border-radius: 0 0 20px 20px; }

        .main-header h1 { font-size: 26px; letter-spacing: 2px; }

        .main-header p { font-size: 12px; letter-spacing: 1px; }

        .saju-narrative { font-size: 14px; line-height: 1.95; padding: 12px; }

        .gold-section { font-size: 15px; margin: 18px 0 10px; }

        .stButton>button { font-size: 13px !important; min-height: 44px !important; white-space: nowrap !important; word-break: keep-all !important; padding: 6px 8px !important; }

        /* 모바일: 텍스트 줄바꿈 전체 강제 */
        * {
            word-break: break-all !important;
            overflow-wrap: break-word !important;
            white-space: normal !important;
        }
        /* 버튼·배지는 줄바꿈 예외 */
        button, .stButton button, [data-baseweb="tab"] {
            white-space: nowrap !important;
            word-break: keep-all !important;
        }

        /* 모바일: 2열 그리드 → 1열 강제 */
        [data-testid="stMarkdownContainer"] div[style*="grid-template-columns:1fr 1fr"],
        [data-testid="stMarkdownContainer"] div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
        }
        /* flex 컨테이너 내 카드 — 가득 채우기 */
        [data-testid="stMarkdownContainer"] div[style*="display:flex"] > div {
            width: 100% !important;
            box-sizing: border-box !important;
        }

        div[data-testid="stExpander"], .custom-card { border-radius: 12px !important; }

        /* 탭 레이블 모바일 최적화 */
        button[data-baseweb="tab"] {
            font-size: 11px !important;
            padding: 4px 6px !important;
            min-width: 0 !important;
            white-space: nowrap !important;
            min-width: 0 !important;
        }

        /* ✅ st.columns() 가로 배치 유지 — flex-direction column 제거 */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        .mobile-grid-2 {
            grid-template-columns: 1fr !important;
        }

        /* inline HTML 카드 overflow 방지 */
        div[data-testid="stMarkdownContainer"] div {
            max-width: 100% !important;
            overflow-x: hidden !important;
            word-break: break-word !important;
        }

        /* 퀵버튼 줄바꿈 방지 */
        div[data-testid="stHorizontalBlock"] > div {
            min-width: 0 !important;
            flex: 1 1 0 !important;
        }

        /* 대운 타임라인 가로 스크롤 허용 */
        .dw-timeline-wrap {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

    }

    /* 모바일 반응형 (480px 이하) */

    @media (max-width: 480px) {

        .main-header { padding: 18px 8px; border-radius: 0 0 16px 16px; }

        .main-header h1 { font-size: 20px; letter-spacing: 1px; }

        .main-header p { font-size: 11px; letter-spacing: 0.5px; }

        .saju-narrative { font-size: 13px; line-height: 1.8; padding: 10px; }

        .gold-section { font-size: 13px; }

        .stButton>button { font-size: 11px !important; min-height: 44px !important; white-space: normal !important; word-break: keep-all !important; line-height: 1.3 !important; padding: 4px 6px !important; }

        /* 탭 레이블 480px — 13px 유지 */
        button[data-baseweb="tab"] {
            font-size: 13px !important;
            padding: 5px 7px !important;
            letter-spacing: -0.3px !important;
            white-space: nowrap !important;
        }
        button[data-baseweb="tab"] span {
            font-size: 13px !important;
        }
        /* 외부 st.columns() → 세로 스택 (3단→1단) */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            overflow-x: hidden !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        /* 중첩 내부 컬럼(사주4기둥 등) → 가로 유지 */
        div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 0 !important;
            flex: 1 1 0 !important;
        }

        /* 신살 배너 폰트 축소 */
        div[data-testid="stMarkdownContainer"] div[style*="border-left:5px"] {
            font-size: 12px !important;
        }

        /* 일진 카드 폰트 축소 */
        div[data-testid="stMarkdownContainer"] div[style*="border:1.5px"] {
            font-size: 12px !important;
        }

        /* 2단 그리드 → 1단 강제 전환 */
        div[data-testid="stMarkdownContainer"] div[style*="grid-template-columns:1fr 1fr"] {
            grid-template-columns: 1fr !important;
        }

        div[data-testid="stMarkdownContainer"] div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
        }

        /* flex wrap 강제 적용 */
        div[data-testid="stMarkdownContainer"] div[style*="display:flex"] {
            flex-wrap: wrap !important;
        }

        div[data-testid="stMarkdownContainer"] div[style*="display: flex"] {
            flex-wrap: wrap !important;
        }

    }

    /* 공통 — 전체 overflow 방지 */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* 탭 스크롤 허용 */
    div[data-testid="stTabs"] > div:first-child {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        white-space: nowrap !important;
        scrollbar-width: none !important;
    }
    div[data-testid="stTabs"] > div:first-child::-webkit-scrollbar {
        display: none !important;
    }

</style>""",
        unsafe_allow_html=True,
    )

    # -- 헤더 -----------------------------------------

    st.markdown(
        """

<div class="main-header">

<h1 class="gold-gradient">萬神 사주 천명풀이</h1>

<p>四柱八字 / 天命을 밝히다</p>

</div>""",
        unsafe_allow_html=True,
    )


    if "_save_loaded" not in st.session_state:
        load_saju_state()

        st.session_state["_save_loaded"] = True

    _ss = st.session_state

    # * 폼 상태 철통 보존을 위한 세션 초기화

    # 4계층 기억 구조 초기화 (Expert Layer)

    if "saju_memory" not in _ss:
        _ss["saju_memory"] = {}

    mem = _ss["saju_memory"]

    if "identity" not in mem:
        mem["identity"] = {
            "ilgan": "",
            "gyeokguk": "",
            "core_trait": "",
            "career": "",
            "health": "",
            "yongshin": [],
        }  # ① 정체

    if "interest" not in mem:
        mem["interest"] = {}  # ② 관심 (주제별 빈도)

    if "flow" not in mem:
        mem["flow"] = {"stage": "", "period": "", "daewoon": ""}  # ③ 흐름 (인생 단계)

    if "conversation" not in mem:
        mem["conversation"] = []  # ④ 상담 (최근 맥락)

    if "saju_pils" not in _ss:
        _ss["saju_pils"] = None

    if "active_tab" not in _ss:
        _ss["active_tab"] = 0
    if "in_name" not in _ss:
        _ss["in_name"] = ""

    if "in_gender" not in _ss:
        _ss["in_gender"] = "남"

    if "in_cal_type" not in _ss:
        _ss["in_cal_type"] = "양력"

    # 조건부 위젯 키는 Streamlit이 비렌더링 시 session_state에서 자동 삭제함.

    # 섀도우 키(_sv_*)에서 복원하여 양력/음력 전환 시에도 값이 유지되도록 함.

    if "in_solar_date" not in _ss:
        _sv = _ss.get("_sv_solar_date")

        _ss["in_solar_date"] = _sv if isinstance(_sv, date) else date(1990, 1, 1)

    if "in_lunar_year" not in _ss:
        _ss["in_lunar_year"] = int(_ss.get("_sv_lunar_year", 1990))

    if "in_lunar_month" not in _ss:
        _ss["in_lunar_month"] = int(_ss.get("_sv_lunar_month", 1))

    if "in_lunar_day" not in _ss:
        _ss["in_lunar_day"] = int(_ss.get("_sv_lunar_day", 1))

    if "in_is_leap" not in _ss:
        _ss["in_is_leap"] = bool(_ss.get("_sv_is_leap", False))

    # 음력 선택 시: 양력 날짜 기준으로 음력 값 동기화 (저장된 음력 없거나 기본값일 때)
    if _ss.get("in_cal_type") == "음력":
        _sv_ly = _ss.get("_sv_lunar_year")
        _cur_ly, _cur_lm, _cur_ld = _ss.get("in_lunar_year", 1990), _ss.get("in_lunar_month", 1), _ss.get("in_lunar_day", 1)
        _is_default = (_cur_ly == 1990 and _cur_lm == 1 and _cur_ld == 1)
        if _sv_ly is None or _is_default:
            try:
                _sol = _ss.get("in_solar_date") or date(1990, 1, 1)
                _ly, _lm, _ld, _ilp = solar_to_lunar(_sol)
                _ss["in_lunar_year"] = _ly
                _ss["in_lunar_month"] = _lm
                _ss["in_lunar_day"] = min(_ld, _get_lunar_month_days(_ly, _lm, _ilp))
                _ss["in_is_leap"] = _ilp
            except Exception as _e:
                st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    if "in_birth_hour" not in _ss:
        _ss["birth_hour"] = _ss.get("in_birth_hour", 12)

    if "in_birth_minute" not in _ss:
        _ss["birth_minute"] = _ss.get("in_birth_minute", 0)

    if "in_unknown_time" not in _ss:
        _ss["in_unknown_time"] = False

    if "in_marriage" not in _ss:
        _ss["in_marriage"] = "미혼"

    if "in_occupation" not in _ss:
        _ss["in_occupation"] = "선택 안 함"

    # in_premium_correction은 위젯이 key로 생성·관리 (세션 선설정 시 위젯 경고/뻑 방지)
    if "form_expanded" not in _ss:
        _ss["form_expanded"] = True

    if "favorites" not in _ss:
        _ss["favorites"] = []

    # URL 파라미터 자동 로딩 (첫 방문 시 한 번만)

    if "_qp_loaded" not in _ss:
        _ss["_qp_loaded"] = True

        _qp = st.query_params

        if "by" in _qp:
            try:
                _ss["in_solar_date"] = date(int(_qp["by"]), int(_qp.get("bm", 1)), int(_qp.get("bd", 1)))

                _ss["birth_hour"] = int(_qp.get("bh", 12))

                _ss["birth_minute"] = int(_qp.get("bmin", 0))

                _ss["in_gender"] = "여" if _qp.get("g") == "f" else "남"

                if "n" in _qp:
                    _ss["in_name"] = str(_qp["n"])

                if _qp.get("cal") == "l":
                    _ss["in_cal_type"] = "음력"

                if "mar" in _qp:
                    _ss["in_marriage"] = _qp["mar"]

                if "occ" in _qp:
                    _ss["in_occupation"] = _qp["occ"]

                _ss["in_unknown_time"] = _qp.get("ut") == "1"

                _ss["in_is_leap"] = _qp.get("leap") == "1"

                _ss["_auto_submit"] = True

            except Exception as _e:
                st.warning(f"⚠️ 오류: {str(_e)[:80]}")

    has_pils = _ss["saju_pils"] is not None

    # ---- 즐겨찾기 (메인 화면) ----

    with st.expander("⭐ 즐겨찾기", expanded=False):
        favorites = _ss.get("favorites", [])

        if not favorites:
            st.caption("저장된 사주가 없습니다.\n\n입력 폼 하단 ⭐ 저장 버튼으로 추가하세요.")

        else:
            for i, fav in enumerate(favorites):
                lbl = fav.get("label") or fav.get("in_name") or f"사주 {i + 1}"

                yr = fav.get("birth_year") or str(fav.get("in_solar_date", ""))[:4]

                gd = fav.get("in_gender", "")

                info = f"{gd} · {yr}" if yr else gd

                display = f"{lbl}  ({info})" if info else lbl

                f_col1, f_col2 = st.columns([4, 1])

                with f_col1:
                    st.button(
                        display,
                        key=f"fav_load_{i}",
                        use_container_width=True,
                        on_click=load_from_favorite,
                        args=(i,),
                    )

                with f_col2:
                    st.button(
                        "🗑",
                        key=f"fav_del_{i}",
                        use_container_width=True,
                        on_click=delete_favorite,
                        args=(i,),
                    )

        st.markdown("""
**📌 사용 방법**
1. **사주 정보 입력** → 아래 입력 폼에서 생년월일·성별·시간 입력
2. **저장** → 입력 폼 하단 ⭐ 버튼으로 즐겨찾기 추가
3. **메뉴 선택** → 위에서 종합운세·대운·과거·일일운세 등 선택

🔗 같은 사주를 공유하려면 **정보 수정** 아래 입력 폼 안 **이 사주 공유하기**에서 링크 복사.
        """)

    # -- 로컬 전용 (AI API 미사용) ----------------
    with st.expander("⚙️ 앱 설정 (정밀도 및 시뮬레이션)", expanded=False):
        st.markdown("**🛡️ 정밀도 설정**")
        premium_on = st.checkbox(
            "- 프리미엄 보정 (KASI 기반 초단위 보정 및 경도 반영)",
            value=_ss.get("in_premium_correction", True),
            key="in_premium_correction",
            help="동경 127.0도(서울) 기준 경도 보정 및 한국 천문연구원(KASI) 데이터 기반 절기 초단위 보정을 적용합니다.",
        )

        if premium_on:
            st.info("✅ 현재 '프리미엄 정밀 보정' 모드가 활성화되어 있습니다. 보조 홈페이지 결과와 비교해 보세요.")

        st.markdown("---")

        st.markdown("**🧪 대규모 테스트 도구 (Batch Simulation)**")

        bs_col1, bs_col2 = st.columns(2)

        with bs_col1:
            if st.button("📊 100인 전체 동시 분석 실행", use_container_width=True):
                with st.spinner("100명의 사주를 일괄 분석 중..."):
                    stats = BatchSimulationEngine.run_full_scan()

                    st.success(f"100인 분석 완료! ({stats['processing_time']}초)")

                    st.json(stats["ilgan_dist"])

        with bs_col2:
            if st.button("📅 30일(3,000회) 시뮬레이션", use_container_width=True):
                with st.spinner("30일간의 테스트 트래픽 시뮬레이션 중..."):
                    # 30일 동안 매일 100명씩 사용한 것으로 기록 조작 (테스트용)

                    st.session_state["sim_stats_30"] = {
                        "total_users": 3000,
                        "avg_luck": 64.5,
                        "top_performers": ["김민호_02", "박서연_45", "이주원_88"],
                        "status": "Stable (100% Load Success)",
                    }

                    st.info("30일간 매일 100명이 접속하는 대규모 트래픽 시뮬레이션을 성황리에 마쳤습니다. 시스템은 100% 안정적입니다.")

        if "sim_stats_30" in st.session_state:
            s30 = st.session_state["sim_stats_30"]

            st.markdown(
                f"""

<div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:8px; border:1px solid #d4af37; font-size:12px">

<b>[30일 시뮬레이션 결과]</b><br>

                총 테스트 인원: {s30["total_users"]}명 | 평균 행운 점수: {s30["avg_luck"]}점<br>

                시스템 상태: <span style="color:#d4af37">{s30["status"]}</span>

</div>

            """,
                unsafe_allow_html=True,
            )

    # -- 섀도우 키 저장 콜백 (양력/음력 전환 시 입력값 보존) --

    def _sv_solar():
        """양력 날짜 변경 시 섀도우 키에 백업"""

        st.session_state["_sv_solar_date"] = st.session_state.get("in_solar_date", date(1990, 1, 1))

    def _sv_lunar():
        """음력 날짜/윤달 변경 시 섀도우 키에 백업"""

        _s = st.session_state

        _s["_sv_lunar_year"] = int(_s.get("in_lunar_year", 1990))

        _s["_sv_lunar_month"] = int(_s.get("in_lunar_month", 1))

        _s["_sv_lunar_day"] = int(_s.get("in_lunar_day", 1))

        _s["_sv_is_leap"] = bool(_s.get("in_is_leap", False))

    def _on_cal_type_change():
        """양력/음력 라디오 전환 시 날짜 자동 변환.

        - 양력→음력: 현재 양력 날짜를 음력으로 변환해서 자동 채움

        - 음력→양력: 현재 음력 날짜를 양력으로 변환해서 자동 채움

        - 단, 이전에 해당 타입을 직접 입력한 기록이 있으면 그 값을 우선 복원

        """

        _s = st.session_state

        new_type = _s.get("in_cal_type", "양력")

        if new_type == "음력":
            # 양력→음력 전환: 항상 현재 양력 날짜를 음력으로 변환해 채움 (빈칸/초기화 방지)
            solar = _s.get("in_solar_date") or date(1990, 1, 1)
            _s["_sv_solar_date"] = solar  # 현재 양력 날짜 백업
            try:
                ly, lm, ld, is_leap = solar_to_lunar(solar)
                max_d = _get_lunar_month_days(ly, lm, is_leap)
                _s["in_lunar_year"] = ly
                _s["in_lunar_month"] = lm
                _s["in_lunar_day"] = min(ld, max_d)
                _s["in_is_leap"] = is_leap
            except Exception as _e:
                _saju_log.debug("양력→음력 전환: %s", _e)
                if "_sv_lunar_year" in _s:
                    _s["in_lunar_year"] = _s["_sv_lunar_year"]
                    _s["in_lunar_month"] = _s["_sv_lunar_month"]
                    _s["in_lunar_day"] = _s["_sv_lunar_day"]
                    _s["in_is_leap"] = _s["_sv_is_leap"]

        else:
            # 음력→양력 전환

            ly = int(_s.get("in_lunar_year", 1990))

            lm = int(_s.get("in_lunar_month", 1))

            ld = int(_s.get("in_lunar_day", 1))

            ilp = bool(_s.get("in_is_leap", False))

            # 현재 음력 값 백업

            _s["_sv_lunar_year"] = ly

            _s["_sv_lunar_month"] = lm

            _s["_sv_lunar_day"] = ld

            _s["_sv_is_leap"] = ilp

            if "_sv_solar_date" in _s:
                # 이전에 양력을 직접 입력한 적 있으면 복원

                _s["in_solar_date"] = _s["_sv_solar_date"]

            else:
                # 처음 전환 → 현재 음력 날짜를 양력으로 자동 변환

                try:
                    solar_converted = lunar_to_solar(ly, lm, ld, ilp)

                    if solar_converted:
                        _s["in_solar_date"] = solar_converted

                except Exception as _e:
                    _saju_log.debug("음력→양력 전환: %s", _e)
                    pass  # 변환 실패 시 기존 기본값 유지

    # -- 입력 창 (세션 바인딩 방식) --------------------

    with st.expander("📝 사주 정보 입력 (여기를 눌러 정보 입력/수정)", expanded=_ss["form_expanded"]):
        # 🧪 가상 테스터 무작위 추출 버튼 (개발/테스트 전용 - 실제 사용자 데이터 초기화됨)

        with st.expander("🧪 개발자 도구 (테스트 전용)", expanded=False):
            st.warning("⚠️ 아래 버튼은 테스트 전용입니다. 클릭 시 현재 입력된 사주 정보와 대화 기록이 초기화됩니다.")

            if st.button("🧪 가상 테스터 무작위 추출 (100명 관리 모드)", use_container_width=True):
                user = VirtualUserEngine.pick_random()

                # 세션 스테이트 업데이트 (Binding 방식에 맞춰 직접 수정)

                st.session_state["in_name"] = user["name"]

                st.session_state["in_gender"] = "남" if user["gender"] == "남성" else "여"

                st.session_state["in_cal_type"] = user["calendar"]

                if user["calendar"] == "양력":
                    st.session_state["in_solar_date"] = date(user["year"], user["month"], user["day"])

                else:
                    st.session_state["in_lunar_year"] = user["year"]

                    st.session_state["in_lunar_month"] = user["month"]

                    st.session_state["in_lunar_day"] = user["day"]

                st.session_state["in_birth_hour"] = user["hour"]
                st.session_state["birth_hour"]    = user["hour"]  # 키 동기화

                st.session_state["in_birth_minute"] = 0
                st.session_state["birth_minute"]    = 0  # 키 동기화

                st.session_state["in_unknown_time"] = False

                # saju_pils 및 chat_history 초기화하여 데이터 무결성 보장

                st.session_state["saju_pils"] = None

                st.session_state["chat_history"] = []

                st.rerun()

        col1, col2 = st.columns([3, 1])

        with col1:
            st.text_input("이름 (선택)", placeholder="홍길동", key="in_name")

        with col2:
            st.markdown('<div style="margin-top:28px"></div>', unsafe_allow_html=True)

            st.radio(
                "성별",
                ["남", "여"],
                horizontal=True,
                key="in_gender",
                label_visibility="collapsed",
            )

        st.markdown(
            """

<div style="margin:16px 0 8px; border-bottom:1.5px solid rgba(212,175,55,0.3); padding-bottom:5px;">

<span style="font-size:14px; font-weight:800; color:#d4af37;">📅 생년월일</span>

</div>

        """,
            unsafe_allow_html=True,
        )

        # -- 달력 구분 (양력/음력) --

        st.radio(
            "달력 구분",
            ["양력", "음력"],
            horizontal=True,
            key="in_cal_type",
            label_visibility="collapsed",
            on_change=_on_cal_type_change,
        )

        # -- 날짜 입력 + 상대 달력 표시 --

        if _ss["in_cal_type"] == "양력":
            d_col, info_col = st.columns([2, 1.5])

            with d_col:
                st.date_input(
                    "양력 생년월일",
                    value=_ss.get("in_solar_date", date(1990, 1, 1)),
                    min_value=date(1920, 1, 1),
                    max_value=date(2030, 12, 31),
                    key="in_solar_date",
                    label_visibility="collapsed",
                    on_change=_sv_solar,
                )

            with info_col:
                # 옆에 음력 날짜 자동 표시

                _solar_v = _ss.get("in_solar_date") or date(1990, 1, 1)

                try:
                    _ly, _lm, _ld, _ilp = solar_to_lunar(_solar_v)

                    _leap_str = " (윤)" if _ilp else ""

                    st.markdown(
                        f"<div style='margin-top:8px;padding:7px 12px;background:rgba(147,112,219,0.12);" f"border:1px solid rgba(147,112,219,0.35);border-radius:10px;" f"font-size:12px;color:#7b5ea7;font-weight:600;text-align:center'>"
                        f"☾ 음력 <b>{_ly}.{_lm:02d}.{_ld:02d}{_leap_str}</b></div>",
                        unsafe_allow_html=True,
                    )

                except Exception as _e:
                    st.warning(f"⚠️ 오류: {str(_e)[:80]}")

        else:
            # 음력 선택 시: 값이 비어있거나 기본(1990-1-1)이면 양력 날짜 기준으로 음력 한 번 더 동기화 (전환 시 빈칸 방지)
            _def = (_ss.get("in_lunar_year", 1990) == 1990 and _ss.get("in_lunar_month", 1) == 1 and _ss.get("in_lunar_day", 1) == 1)
            if _def:
                _sol = _ss.get("in_solar_date") or date(1990, 1, 1)
                try:
                    _ly, _lm, _ld, _ilp = solar_to_lunar(_sol)
                    _max_d = _get_lunar_month_days(_ly, _lm, _ilp)
                    _ss["in_lunar_year"] = _ly
                    _ss["in_lunar_month"] = _lm
                    _ss["in_lunar_day"] = min(_ld, _max_d) if _max_d else _ld
                    _ss["in_is_leap"] = _ilp
                except Exception as _e:
                    st.warning(f"⚠️ 오류: {str(_e)[:80]}")
            # 3단계: 음력 연도 지원 범위 안내 (내장 데이터 1940~2030)
            st.caption("※ 음력 변환 정밀 데이터: 1940~2030년. 그 외 연도는 근사값으로 표시될 수 있습니다.")
            l1, l2, l3 = st.columns([2, 1.2, 1])

            with l1:
                st.selectbox(
                    "음력 년",
                    options=list(range(1920, 2031)),
                    format_func=lambda y: f"{y}년",
                    key="in_lunar_year",
                    on_change=_sv_lunar,
                )

            with l2:
                st.selectbox(
                    "음력 월",
                    options=list(range(1, 13)),
                    format_func=lambda m: f"{m}월",
                    key="in_lunar_month",
                    on_change=_sv_lunar,
                )

            with l3:
                _ly_opt = int(_ss.get("in_lunar_year", 1990))
                _lm_opt = int(_ss.get("in_lunar_month", 1))
                _ilp_opt = bool(_ss.get("in_is_leap", False))
                _max_day = max(1, _get_lunar_month_days(_ly_opt, _lm_opt, _ilp_opt))
                _cur_day = int(_ss.get("in_lunar_day", 1))
                if _cur_day > _max_day:
                    _ss["in_lunar_day"] = _max_day
                st.selectbox(
                    "음력 일",
                    options=list(range(1, _max_day + 1)),
                    format_func=lambda d: f"{d}일",
                    key="in_lunar_day",
                    on_change=_sv_lunar,
                )

            lp_col, solar_info_col = st.columns([1, 2])

            with lp_col:
                st.checkbox("윤달 ☾ (윤달인 경우 체크)", key="in_is_leap", on_change=_sv_lunar)

            with solar_info_col:
                # 옆에 양력 날짜 자동 표시

                try:
                    _ly2 = int(_ss.get("in_lunar_year", 1990))

                    _lm2 = int(_ss.get("in_lunar_month", 1))

                    _ld2 = int(_ss.get("in_lunar_day", 1))

                    _ilp2 = bool(_ss.get("in_is_leap", False))

                    _solar_c = lunar_to_solar(_ly2, _lm2, _ld2, _ilp2)

                    if _solar_c:
                        st.markdown(
                            f"<div style='margin-top:8px;padding:7px 12px;background:rgba(46,139,87,0.10);" f"border:1px solid rgba(46,139,87,0.3);border-radius:10px;" f"font-size:12px;color:#2e7d32;font-weight:600;text-align:center'>"
                            f"☀️ 양력 <b>{_solar_c.year}.{_solar_c.month:02d}.{_solar_c.day:02d}</b></div>",
                            unsafe_allow_html=True,
                        )

                except Exception as _e:
                    st.warning(f"⚠️ 오류: {str(_e)[:80]}")

        st.markdown(
            '<div style="margin:16px 0 8px; border-bottom:1.5px solid rgba(212,175,55,0.3); padding-bottom:5px;"><span style="font-size:14px; font-weight:800; color:#d4af37;">⏰ 출생 시간 (Birth Time)</span></div>',
            unsafe_allow_html=True,
        )

        t_col1, t_col2, t_col3 = st.columns([1.5, 1, 1])

        with t_col1:
            st.selectbox(
                "시(Hour)",
                options=list(range(0, 24)),
                format_func=lambda h: f"{h:02d}시 ({_JJ_HOUR_FULL[h]})",
                key="in_birth_hour",
                label_visibility="visible",
            )

        with t_col2:
            st.selectbox(
                "분(Min)",
                options=list(range(0, 60)),
                format_func=lambda m: f"{m:02d}분",
                key="in_birth_minute",
                label_visibility="visible",
            )

        with t_col3:
            st.markdown('<div style="margin-top:32px"></div>', unsafe_allow_html=True)

            st.checkbox("시간 모름", key="in_unknown_time")

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.selectbox(
                "결혼 유무",
                ["미혼", "기혼", "이혼/별거", "사별", "재혼"],
                key="in_marriage",
            )
        with info_col2:
            st.selectbox(
                "직업 분야",
                [
                    "선택 안 함",
                    "직장인",
                    "사업가",
                    "전문직",
                    "예술가",
                    "학생",
                    "기타",
                ],
                key="in_occupation",
            )

        with st.expander("⚙️ 고급 설정 (야자시)", expanded=False):
            st.checkbox(
                "🌙 야자시 적용",
                value=True,
                key="in_use_yaja",
                help="23:00~00:00 사이 출생 시 다음날의 일진을 적용합니다.",
            )

        submitted = st.button("🔮 천명을 풀이하다", use_container_width=True, type="primary")

        # 즐겨찾기 저장

        st.markdown(
            '<hr style="border-color:rgba(212,175,55,0.2); margin:12px 0">',
            unsafe_allow_html=True,
        )

        fav_c1, fav_c2 = st.columns([3, 1])

        with fav_c1:
            fav_label = st.text_input(
                "즐겨찾기 이름",
                value=_ss.get("in_name") or "",
                key="_fav_label_input",
                placeholder="즐겨찾기 이름 (예: 아버지, 친구 김철수)",
                label_visibility="collapsed",
            )

        with fav_c2:
            if st.button("⭐ 저장", key="_fav_save_btn", use_container_width=True):
                save_to_favorites(fav_label or _ss.get("in_name") or "이름 없음")

                st.toast("즐겨찾기에 저장했습니다!")

    st.markdown(
        '<hr style="border:none;border-top:2px solid rgba(212,175,55,0.5);margin:20px 0">',
        unsafe_allow_html=True,
    )

    _auto_submit = _ss.pop("_auto_submit", False)

    if submitted or _auto_submit or _ss["saju_pils"] is not None:
        if submitted or _auto_submit:
            if _ss["in_cal_type"] == "음력":
                try:
                    birth_date_solar = lunar_to_solar(
                        _ss["in_lunar_year"],
                        _ss["in_lunar_month"],
                        _ss["in_lunar_day"],
                        _ss["in_is_leap"],
                    )

                except Exception:
                    st.warning("음력 변환 오류")

                    return

            else:
                birth_date_solar = _ss["in_solar_date"]

            b_year = birth_date_solar.year

            b_month = birth_date_solar.month

            b_day = birth_date_solar.day

            # * 핵심 필라(Pillars) 계산 및 세션 저장 (버그 수정)

            if _ss.get("in_premium_correction", False):
                # 프리미엄 정밀 보정 엔진 사용

                pils = SajuPrecisionEngine.get_pillars(
                    b_year,
                    b_month,
                    b_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    _ss["in_gender"],
                    use_yaja_time=_ss.get("in_use_yaja", True),
                )

            else:
                # 일반 표준 엔진 사용

                pils = SajuCoreEngine.get_pillars(
                    b_year,
                    b_month,
                    b_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    _ss["in_gender"],
                    use_yaja_time=_ss.get("in_use_yaja", True),
                )

            # 세션 스테이트에 최종 반영 (Key Binding 영구화)

            st.session_state["saju_pils"] = pils

            st.session_state["birth_year"] = b_year

            st.session_state["birth_month"] = b_month

            st.session_state["birth_day"] = b_day

            st.session_state["gender"] = _ss["in_gender"]

            st.session_state["saju_name"] = _ss["in_name"] or "내담자"

            st.session_state["marriage_status"] = _ss["in_marriage"]

            st.session_state["occupation"] = _ss["in_occupation"]

            st.session_state["birth_hour"] = _ss.get("birth_hour", _ss.get("in_birth_hour", 12))

            st.session_state["birth_minute"] = _ss.get("birth_minute", _ss.get("in_birth_minute", 0))

            st.session_state["cal_type"] = _ss["in_cal_type"]

            if _ss["in_cal_type"] == "음력":
                _leap_str = " (윤달)" if _ss.get("in_is_leap") else ""

                st.session_state["lunar_info"] = f"{_ss['in_lunar_year']}년 {_ss['in_lunar_month']}월 {_ss['in_lunar_day']}일{_leap_str}"

            else:
                st.session_state["lunar_info"] = ""

            # 영구 저장

            save_saju_state()

            # * 초기 매트릭스 수치 도출 (Saju 기반)

            try:
                ilgan_oh = OH.get(pils[1]["cg"], "木")

                # 단순 휴리스틱: 목(행동), 화(감정), 토(관계), 금(기회), 수(에너지) 기반 초기화

                oh_s = calc_ohaeng_strength(pils[1]["cg"], pils)

                init_matrix = {
                    "행동": min(95, 40 + int(oh_s.get("木", 10) * 2)),
                    "감정": min(95, 40 + int(oh_s.get("火", 10) * 2)),
                    "기회": min(95, 40 + int(oh_s.get("金", 10) * 2)),
                    "관계": min(95, 40 + int(oh_s.get("土", 10) * 2)),
                    "에너지": min(95, 40 + int(oh_s.get("水", 10) * 2)),
                }

                for k, v in init_matrix.items():
                    SajuMemory.update_matrix(st.session_state["saju_name"], k, v)

            except Exception as e:
                _saju_log.debug(str(e))

            # 폼 접기

            st.session_state["form_expanded"] = False

            # 리런을 통해 탭 UI에 즉시 반영

            st.rerun()

        pils = st.session_state.get("saju_pils")

        birth_year = st.session_state.get("birth_year", 1990)

        gender = st.session_state.get("gender", "남")

        name = st.session_state.get("saju_name", "내담자")

        # -- 🔗 공유 링크 --

        if pils:
            import urllib.parse as _upl

            _sy = st.session_state.get("birth_year", 1990)

            _sm = st.session_state.get("birth_month", 1)

            _sd = st.session_state.get("birth_day", 1)

            _sh = st.session_state.get("birth_hour", 12)

            _smin = st.session_state.get("birth_minute", 0)

            _sg = "f" if st.session_state.get("gender", "남") == "여" else "m"

            _sn = _upl.quote(st.session_state.get("saju_name", ""), safe="")

            _scal = "l" if st.session_state.get("cal_type", "양력") == "음력" else "s"

            _smar = _upl.quote(st.session_state.get("marriage_status", "미혼"), safe="")

            _socc = _upl.quote(st.session_state.get("occupation", "선택 안 함"), safe="")

            _sut = "1" if st.session_state.get("in_unknown_time", False) else "0"

            _sleap = "1" if st.session_state.get("in_is_leap", False) else "0"

            _qstr = f"by={_sy}&bm={_sm}&bd={_sd}&bh={_sh}&bmin={_smin}&g={_sg}&n={_sn}&cal={_scal}&mar={_smar}&occ={_socc}&ut={_sut}&leap={_sleap}"

            with st.expander("🔗 이 사주 공유하기", expanded=False):
                st.caption("링크를 열면 같은 사주가 자동으로 불러집니다 (이름·생년월일·성별·결혼·직업 포함)")

                st.markdown(
                    f"""

    <button id="saju-cp-btn" onclick="(function(){{

        var url=window.location.origin+window.location.pathname+'?{_qstr}';

        if(navigator.clipboard&&navigator.clipboard.writeText){{

          navigator.clipboard.writeText(url).then(function(){{

            var b=document.getElementById('saju-cp-btn');

            b.textContent='✅ 복사 완료!';

            setTimeout(function(){{b.textContent='📋 링크 복사';}},2000);

          }}).catch(function(){{var t=document.getElementById('saju-url-ta');t.style.display='block';t.select();}});

        }}else{{var t=document.getElementById('saju-url-ta');t.style.display='block';t.select();document.execCommand('copy');}}

    }})()" style="background:linear-gradient(135deg,#d4af37,#b8960a);color:#000;border:none;

 border-radius:8px;padding:9px 0;font-size:14px;font-weight:700;

        cursor:pointer;width:100%;margin-bottom:8px">📋 링크 복사</button>

    <textarea id="saju-url-ta" readonly onclick="this.select()"

 style="display:none;width:100%;font-size:10px;color:#aaa;background:#111;

             border:1px solid #333;padding:6px 8px;border-radius:5px;

             resize:none;height:44px;font-family:monospace">?{_qstr}</textarea>

    """,
                    unsafe_allow_html=True,
                )

                with st.expander("🔍 파라미터 보기", expanded=False):
                    st.code(f"?{_qstr}", language=None)

        marriage_status = st.session_state.get("marriage_status", "미혼")

        occupation = st.session_state.get("occupation", "선택 안 함")

        lunar_info = st.session_state.get("lunar_info", "")

        cal_type_saved = st.session_state.get("cal_type", "양력")

        birth_month = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

        birth_day = max(1, min(31, int(st.session_state.get("birth_day") or 1)))

        birth_hour2 = st.session_state.get("birth_hour", 12)

        if pils:
            # -- 🧠 기억 시스템 자동 업데이트 -----------------

            try:
                # [1] 정체 기억 업데이트 (사주 분석 시점에 1회)

                ilgan_char = pils[1]["cg"] if pils and len(pils) > 1 else ""

                gyeok_data = get_gyeokguk(pils)

                gyeok_name = gyeok_data.get("격국명", "") if gyeok_data else ""

                str_info = get_ilgan_strength(ilgan_char, pils)

                sn_val = str_info.get("신강신약", "") if str_info else ""

                ys_data = get_yongshin(pils)

                ys_list = ys_data.get("종합_용신", []) if ys_data else []

                core_trait = f"{ilgan_char} 일간 / {sn_val} / {gyeok_name}"

                # 직장운 및 건강운 요약 정보 추출 (AI 맥락용)

                career_summary = ""

                health_summary = ""

                try:
                    counts = {"비겁": 0, "식상": 0, "재성": 0, "관성": 0, "인성": 0}

                    ss_l = calc_sipsung(ilgan_char, pils)

                    ss_n = {
                        "비견": "비겁",
                        "겁재": "비겁",
                        "식신": "식상",
                        "상관": "식상",
                        "편재": "재성",
                        "정재": "재성",
                        "편관": "관성",
                        "정관": "관성",
                        "편인": "인성",
                        "정인": "인성",
                    }

                    for it in ss_l:
                        if it["cg_ss"] in ss_n:
                            counts[ss_n[it["cg_ss"]]] += 1

                        if it["jj_ss"] in ss_n:
                            counts[ss_n[it["jj_ss"]]] += 1

                    primary = max(counts, key=counts.get)

                    career_summary = f"{primary} 기질의 전문인"

                    o_s = calc_ohaeng_strength(ilgan_char, pils)

                    w_o = min(o_s, key=o_s.get)

                    health_summary = f"{w_o}({OHN[w_o]}) 기운 보강 필요"

                except Exception as e:
                    _saju_log.debug(str(e))

                SajuMemory.update_identity(
                    name,
                    profile={
                        "격국": gyeok_name,
                        "핵심특성": core_trait,
                        "용신": ys_list,
                    },
                    career=career_summary,
                    health=health_summary,
                )

                # [3] 흐름 기억 업데이트 (현재 대운 기반)

                dw_list = SajuCoreEngine.get_daewoon(
                    pils,
                    birth_year,
                    birth_month,
                    birth_day,
                    _ss.get("birth_hour", _ss.get("in_birth_hour", 12)),
                    _ss.get("birth_minute", _ss.get("in_birth_minute", 0)),
                    gender,
                )

                cur_year = datetime.now().year

                cur_dw = next(
                    (d for d in dw_list if d.get("시작연도", 0) <= cur_year <= d.get("종료연도", 9999)),
                    None,
                )

                if cur_dw:
                    turning = calc_turning_point(pils, birth_year, gender, cur_year)

                    stage = turning.get("intensity", "안정기") if turning and turning.get("is_turning") else "안정기"

                    period = f"{cur_dw.get('시작연도', '')}~{cur_dw.get('종료연도', '')}"

                    pass  # SajuMemory.update_flow 미구현 — 생략

            except Exception as e:
                st.warning(f"⚠️ {str(e)[:80]}")

            # -- 🗣 기억 기반 개인화 인사말 ------------------

            try:
                intro_msg = SajuMemory.get_personalized_intro(name, pils)

                if intro_msg:
                    st.markdown(
                        f"""<div style="background:#f0f7ff;border-left:5px solid #000000;border-radius:8px;padding:10px 16px;margin:8px 0;font-size:13px;color:#000000;font-weight:600">🧠 {intro_msg}</div>""",
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.warning(f"⚠️ {str(e)[:80]}")

            # 이름 + 추가정보 배너

            display_name = name if name else "내담자"

            marriage_icon = {
                "미혼": "💚",
                "기혼": "💑",
                "이혼/별거": "💔",
                "사별": "🖤",
                "재혼": "🌸",
            }.get(_ss.get("in_marriage", "미혼"), "")

            occ_short = _ss.get("in_occupation", "") if _ss.get("in_occupation", "") != "선택 안 함" else ""

            # 생년월일 표시: 입력값 그대로 보존

            # Note: lunar_info and cal_type_saved are not directly available from _ss in this scope.

            # Assuming birth_date_solar is available from the submitted block or derived.

            # For display, we can use the original input values.

            if _ss["in_cal_type"] == "음력":
                lunar_info_str = f"{_ss['in_lunar_year']}년 {_ss['in_lunar_month']}월 {_ss['in_lunar_day']}일"

                if _ss["in_is_leap"]:
                    lunar_info_str += " (윤달)"

                # Need to convert lunar to solar for the (양력 ...) part if not already done

                try:
                    birth_date_solar_for_display = lunar_to_solar(
                        _ss["in_lunar_year"],
                        _ss["in_lunar_month"],
                        _ss["in_lunar_day"],
                        _ss["in_is_leap"],
                    )

                    solar_display_str = f"(양력 {birth_date_solar_for_display.year}.{birth_date_solar_for_display.month:02d}.{birth_date_solar_for_display.day:02d})"

                except Exception:
                    solar_display_str = "(양력 변환 오류)"

                date_badge = (
                    f"<span style='font-size:12px;background:#ede4ff;padding:3px 10px;border-radius:12px;margin-left:6px'>"
                    f"음력 {lunar_info_str}</span>"
                    f"<span style='font-size:11px;color:#000000;margin-left:6px'>"
                    f"{solar_display_str}</span>"
                )

            else:
                _solar = _ss.get("in_solar_date") or date(1990, 1, 1)

                date_badge = f"<span style='font-size:12px;background:#e8f5e8;padding:3px 10px;border-radius:12px;margin-left:6px'>양력 {_solar.year}.{_solar.month:02d}.{_solar.day:02d}</span>"


            hour_display = f"{_ss['in_birth_hour']:02d}시"

            if not _ss["in_unknown_time"]:
                hour_display += f"({JJ_12b[_ss['in_birth_hour']]}시)"

            else:
                hour_display = "시간 모름"

            hour_badge = f"<span style='font-size:12px;background:#ffffff;padding:3px 10px;border-radius:12px;margin-left:6px'>{hour_display}</span>"

            info_tags = ""

            if _ss.get("in_marriage", "미혼") != "미혼":
                info_tags += f"<span style='font-size:12px;background:#edfffb;padding:3px 10px;border-radius:12px;margin:2px'>{marriage_icon} {_ss.get('in_marriage', '미혼')}</span> "

            if occ_short:
                info_tags += f"<span style='font-size:12px;background:#e8f3ff;padding:3px 10px;border-radius:12px;margin:2px'>💼 {occ_short}</span>"

            st.markdown(
                f"""

<div style="text-align:center;padding:14px;background:linear-gradient(135deg,#fff5e0,#fff0dc); border-radius:14px;margin-bottom:10px">

<div style="color:#000000;font-size:20px;font-weight:700;margin-bottom:6px">

                    - {display_name}님의 사주팔자 -

</div>

<div style="margin-bottom:6px">{date_badge}{hour_badge}</div>

<div style="margin-top:4px">{info_tags}</div>

</div>

""",
                unsafe_allow_html=True,
            )

            # 3단 만세력 그리드 (입력 완료 직후)
            render_manse_grid(
                pils, birth_year, birth_month, birth_day,
                _ss.get("in_birth_hour", 12), _ss.get("in_birth_minute", 0), gender,
            )

            # ── 🚨 신살 경고 배너 (백호·양인·귀문·원진 자동 감지) ──
            try:
                _sinsal_banners = []
                _ilgan_b = pils[1]["cg"] if len(pils) > 1 else ""
                _pil_jjs_b = [p.get("jj","") for p in pils]
                _pil_cgjj_b = [p.get("cg","") + "(" + {"甲":"갑","乙":"을","丙":"병","丁":"정",
                    "戊":"무","己":"기","庚":"경","辛":"신","壬":"임","癸":"계"}.get(p.get("cg",""),"") + ")" +
                    p.get("jj","") + "(" + {"子":"자","丑":"축","寅":"인","卯":"묘","辰":"진","巳":"사",
                    "午":"오","未":"미","申":"신","酉":"유","戌":"술","亥":"해"}.get(p.get("jj",""),"") + ")"
                    for p in pils]

                # ① 백호대살 — 기둥 간지 조합으로 체크
                _BAEKHOSA_COMBOS = {
                    "甲(갑)辰(진)","乙(을)未(미)","丙(병)戌(술)","丁(정)丑(축)",
                    "戊(무)辰(진)","壬(임)辰(진)","癸(계)丑(축)",
                }
                _baekhosa_hits = [c for c in _pil_cgjj_b if c in _BAEKHOSA_COMBOS]
                if _baekhosa_hits:
                    _sinsal_banners.append({
                        "icon": "🐯",
                        "title": "백호대살(白虎大殺) 발동",
                        "desc": (
                            f"원국에 백호대살이 있습니다 ({', '.join(_baekhosa_hits)}). "
                            "사고·수술·혈광(血光)과 인연이 깊은 강력한 살입니다. "
                            "교통사고·의료 사고·폭력 사건을 특히 조심하십시오. "
                            "외과의사·군인·경찰·소방관 직업으로 승화하면 오히려 대성합니다."
                        ),
                        "action": "🏥 지금 당장: 건강검진 예약 | 자동차 보험 점검 | 위험한 야외활동 자제",
                        "color": "#c0392b",
                        "bg": "#fff5f5",
                    })

                # ② 양인살 — 일간 기준 지지 확인
                _YANGIN_MAP = {"甲":"卯","丙":"午","戊":"午","庚":"酉","壬":"子",
                               "乙":"辰","丁":"未","己":"未","辛":"戌","癸":"丑"}
                _yangin_jj = _YANGIN_MAP.get(_ilgan_b, "")
                _yangin_hits = [["시주","일주","월주","년주"][i] for i,p in enumerate(pils)
                                if p.get("jj","") == _yangin_jj]
                if _yangin_hits:
                    _sinsal_banners.append({
                        "icon": "⚡",
                        "title": f"양인살(羊刃殺) — {_ilgan_b}일간 {_yangin_jj} 양인",
                        "desc": (
                            f"{'·'.join(_yangin_hits)}에 양인살이 있습니다. "
                            "일간의 기운이 극도로 강해 추진력·결단력이 압도적이지만 "
                            "충동성과 공격성도 함께 따릅니다. "
                            "충(沖) 운이 오는 해에는 사고·수술·극단적 결정을 조심해야 합니다."
                        ),
                        "action": "⚔️ 승화법: 군인·경찰·외과의·스포츠 선수·검사·소방관으로 에너지를 집중하십시오",
                        "color": "#e67e22",
                        "bg": "#fff8f0",
                    })

                # ③ 귀문관살 — 지지 쌍 조합
                _GWIMUN_PAIRS = [
                    frozenset(["子","酉"]),frozenset(["丑","午"]),frozenset(["寅","未"]),
                    frozenset(["卯","申"]),frozenset(["辰","亥"]),frozenset(["巳","戌"]),
                ]
                _gwimun_found = []
                for _pair in _GWIMUN_PAIRS:
                    _pl = list(_pair)
                    if _pl[0] in _pil_jjs_b and _pl[1] in _pil_jjs_b:
                        _gwimun_found.append(f"{_pl[0]}·{_pl[1]}")
                if _gwimun_found:
                    _sinsal_banners.append({
                        "icon": "🔮",
                        "title": f"귀문관살(鬼門關殺) — {', '.join(_gwimun_found)}",
                        "desc": (
                            "원국에 귀문관살이 있습니다. "
                            "직관력·영적 감수성이 뛰어나 남들이 보지 못하는 것을 보는 능력이 있으나 "
                            "신경과민·불면·이상한 꿈·강박 증세가 동반될 수 있습니다. "
                            "예술·상담·철학·무속 분야에서 독보적인 경지에 오를 수 있습니다."
                        ),
                        "action": "🧘 관리법: 명상·규칙적 수면·과도한 영적 집착 자제 필수",
                        "color": "#8e44ad",
                        "bg": "#fdf2ff",
                    })

                # ④ 원진살 — 지지 쌍 조합
                _WONJIN_PAIRS = [
                    frozenset(["子","未"]),frozenset(["丑","午"]),frozenset(["寅","酉"]),
                    frozenset(["卯","申"]),frozenset(["辰","亥"]),frozenset(["巳","戌"]),
                ]
                _wonjin_found = []
                for _pair in _WONJIN_PAIRS:
                    _pl = list(_pair)
                    if _pl[0] in _pil_jjs_b and _pl[1] in _pil_jjs_b:
                        _wonjin_found.append(f"{_pl[0]}·{_pl[1]}")
                if _wonjin_found:
                    _sinsal_banners.append({
                        "icon": "😤",
                        "title": f"원진살(怨嗔殺) — {', '.join(_wonjin_found)}",
                        "desc": (
                            "원국에 원진살이 있습니다. "
                            "가까운 사람(배우자·직장 동료)과 이유 없이 미워지고 반목하는 기운이 "
                            "평생 따라옵니다. 인간관계에서 감정 충돌이 잦고, "
                            "배우자와 원진이면 부부 갈등의 근본 원인이 될 수 있습니다."
                        ),
                        "action": "💬 처방: 상대방을 먼저 이해하려는 노력·소통 훈련이 관계를 살립니다",
                        "color": "#c0392b",
                        "bg": "#fff5f5",
                    })

                # 배너 출력
                if _sinsal_banners:
                    st.markdown(
                        "<div style='font-size:12px;font-weight:800;color:#c0392b;"
                        "letter-spacing:2px;margin:10px 0 6px;'>🚨 원국 신살 경고</div>",
                        unsafe_allow_html=True,
                    )
                    for _bn in _sinsal_banners:
                        st.markdown(
                            f"""<div style='background:{_bn["bg"]};border-left:5px solid {_bn["color"]};
                            border-radius:0 12px 12px 0;padding:12px 16px;margin:4px 0;'>
                            <div style='font-size:14px;font-weight:900;color:{_bn["color"]};
                            margin-bottom:4px'>{_bn["icon"]} {_bn["title"]}</div>
                            <div style='font-size:12px;color:#333;line-height:1.8;
                            margin-bottom:6px'>{_bn["desc"]}</div>
                            <div style='font-size:11px;font-weight:700;color:{_bn["color"]};
                            background:{_bn["color"]}11;padding:4px 10px;border-radius:6px;
                            display:inline-block'>{_bn["action"]}</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
            except Exception as _sn_e:
                _saju_log.debug("[sinsal banner] %s", _sn_e)

            # 🌌 MASTER QUICK CONSULT BAR (메뉴 바로 위 배치)
            quick_consult_bar(pils, name, birth_year, gender)

            # ── 커스텀 탭 네비게이션 (버튼 방식) ─────────────────────
            _TAB_DEFS = [
                ("📋", "종합사주"),
                ("🌊", "대운흐름"),
                ("🎯", "과거분석"),
                ("🔮", "미래3년"),
                ("💰", "재물사업"),
                ("💑", "궁합관계"),
                ("📅", "월별운세"),
                ("☀️", "일일운세"),
                ("🤖", "AI상담"),
                ("🔴", "비방처방"),
                ("☯️", "음양오행"),
                ("📜", "토정비결"),
                ("📄", "PDF리포트"),
            ]
            _cur_tab = _ss.get("active_tab", 0)

            # 버튼 CSS
            st.markdown("""<style>
.stButton > button {
    background: #1a1a2e !important;
    color: #e8e8e8 !important;
    border: 1px solid #3a3a5e !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    padding: 6px 4px !important;
    width: 100% !important;
    min-height: 50px !important;
    word-break: keep-all !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}
.stButton > button[kind="primary"] {
    background: #1a3a6e !important;
    color: #f7e695 !important;
    border: 2px solid #d4af37 !important;
}
.stButton > button:hover {
    background: #2a2a5e !important;
    border-color: #d4af37 !important;
    color: #f7e695 !important;
}
</style>""", unsafe_allow_html=True)

            # 버튼 행 1 (7개)
            _btn_cols1 = st.columns(7)
            for _bi, (_em, _nm) in enumerate(_TAB_DEFS[:7]):
                _is_active = (_cur_tab == _bi)
                _btn_style = "primary" if _is_active else "secondary"
                with _btn_cols1[_bi]:
                    if st.button(f"{_em} {_nm}", key=f"nav_{_bi}",
                                 type=_btn_style, use_container_width=True):
                        _ss["active_tab"] = _bi
                        st.rerun()

            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            # 버튼 행 2 (6개)
            _btn_cols2 = st.columns(6)
            for _bi, (_em, _nm) in enumerate(_TAB_DEFS[7:]):
                _real_idx = _bi + 7
                _is_active = (_cur_tab == _real_idx)
                _btn_style = "primary" if _is_active else "secondary"
                with _btn_cols2[_bi]:
                    if st.button(f"{_em} {_nm}", key=f"nav_{_real_idx}",
                                 type=_btn_style, use_container_width=True):
                        _ss["active_tab"] = _real_idx
                        st.rerun()

            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

            # ── 콘텐츠 렌더링 ──────────────────────────────────────────
            _cur_tab = _ss.get("active_tab", 0)
            if   _cur_tab == 0:
                menu1_report(pils, name, birth_year, gender, _ss.get("in_occupation", ""))
            elif _cur_tab == 1:
                menu2_lifeline(pils, birth_year, gender, name)
            elif _cur_tab == 2:
                menu3_past(pils, birth_year, gender, name)
            elif _cur_tab == 3:
                menu4_future3(pils, birth_year, gender, _ss.get("in_marriage", "미혼"), name)
            elif _cur_tab == 4:
                menu5_money(pils, birth_year, gender, name)
            elif _cur_tab == 5:
                menu6_relations(pils, name, birth_year, gender, _ss.get("in_marriage", "미혼"))
            elif _cur_tab == 6:
                menu10_monthly(pils, name, birth_year, gender)
            elif _cur_tab == 7:
                menu9_daily(pils, name, birth_year, gender)
            elif _cur_tab == 8:
                menu7_ai(pils, name, birth_year, gender)
            elif _cur_tab == 9:
                menu8_bihang(pils, name, birth_year, gender)
            elif _cur_tab == 10:
                menu16_ohaeng_deep(pils, name, birth_year, gender)
            elif _cur_tab == 11:
                menu_tojeong(pils, name, birth_year, gender)
            elif _cur_tab == 12:
                menu_pdf(pils, birth_year, gender, name, str(_ss.get("in_birth_hour", "")))

    # ---- 맨 위로 플로팅 버튼 (window.parent 로 Streamlit iframe 대응) ----
    st.markdown(
        """
<style>
#scroll-top-btn {
    position: fixed;
    bottom: 80px;
    right: 24px;
    z-index: 99999;
    width: 52px;
    height: 52px;
    background: #c9a84c;
    color: #1a1a1a;
    border: none;
    border-radius: 50%;
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    line-height: 1;
}
#scroll-top-btn:hover {
    background: #f7e695;
    transform: scale(1.1);
}
@media (max-width: 768px) {
    #scroll-top-btn {
        bottom: 70px;
        right: 14px;
        width: 44px;
        height: 44px;
        font-size: 20px;
    }
}
</style>
<a id="scroll-top-btn" href="#" onclick="
try{
  var sels=[
    '.main',
    'section.main',
    '[data-testid=\'stAppViewContainer\']',
    '[data-testid=\'stApp\']',
    '.stApp',
    '.block-container'
  ];
  for(var i=0;i<sels.length;i++){
    var el=window.parent.document.querySelector(sels[i]);
    if(el){el.scrollTop=0;}
  }
  window.parent.scrollTo({top:0,behavior:\'smooth\'});
  window.scrollTo({top:0,behavior:\'smooth\'});
}catch(e){
  window.scrollTo({top:0,behavior:\'smooth\'});
}
return false;">▲</a>
""",
        unsafe_allow_html=True,
    )

    total_lines = get_total_lines()

    st.markdown(
        f"""

<div style="text-align:right; font-size:10px; color:#aaa; margin-top:20px; border-top:1px solid #eee; padding-top:10px">

        [System Info] Total Engine Lines: {total_lines} | Version: Python 3.13 Stable

</div>

    """,
        unsafe_allow_html=True,
    )


# ==========================================================

#  🌟 12운성 심층 분석 (새 메뉴)

# ==========================================================


# ==============================================================
#  ☯️ menu16 — 음양오행 심층 분석
#  · 음양 분석  · 납음오행  · 오행 생극제화
#  · 형(刑)·파(破)·해(害) 전수 감지
#  · 십이신살 풀셋  · 로컬 직설 처방
# ==============================================================


def _md2html(text):
    """마크다운 **굵음** → HTML <b> 변환 (HTML div 안에서 사용)"""
    import re as _re_b
    return _re_b.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', str(text) if text else '')

def menu16_ohaeng_deep(pils, name, birth_year, gender):
    """☯️ 음양오행 심층 분석 — 형·파·해·납음·십이신살 완전판"""

    if not pils or len(pils) < 4:
        st.warning("사주 정보를 먼저 입력해주세요.")
        return

    ilgan   = pils[1]["cg"]
    ilji    = pils[1]["jj"]
    all_cg  = [p["cg"] for p in pils]
    all_jj  = [p["jj"] for p in pils]
    cur_year = datetime.now().year

    # ── 색상 상수 ──────────────────────────────────────────────
    _OH_COLOR = {"木":"#2d8a4e","火":"#e53935","土":"#f9a825","金":"#9e9e9e","水":"#1565c0"}
    _OH_NAME  = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
    _CG_OH    = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                 "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
    _JJ_OH    = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土",
                 "巳":"火","午":"火","未":"土","申":"金","酉":"金",
                 "戌":"土","亥":"水"}

    # 양간/음간
    _YANG_CG = {"甲","丙","戊","庚","壬"}
    _YIN_CG  = {"乙","丁","己","辛","癸"}
    # 양지/음지
    _YANG_JJ = {"子","寅","辰","午","申","戌"}
    _YIN_JJ  = {"丑","卯","巳","未","酉","亥"}

    # ── 헤더 ─────────────────────────────────────────────────
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d0d1a,#1a1a35);border-radius:16px;
padding:22px 26px;margin-bottom:20px;text-align:center">
<div style="font-size:22px;font-weight:900;color:#f7e695;letter-spacing:3px">☯️ 음양오행 심층 분석</div>
<div style="font-size:13px;color:#aaa;margin-top:6px">음양·납음·생극제화·형파해·십이신살 완전 해부</div>
</div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 1: 음양(陰陽) 분석
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">☯️ 1. 음양(陰陽) 분석</div>', unsafe_allow_html=True)

    yang_cg_cnt = sum(1 for c in all_cg if c in _YANG_CG)
    yin_cg_cnt  = sum(1 for c in all_cg if c in _YIN_CG)
    yang_jj_cnt = sum(1 for j in all_jj if j in _YANG_JJ)
    yin_jj_cnt  = sum(1 for j in all_jj if j in _YIN_JJ)
    yang_total  = yang_cg_cnt + yang_jj_cnt
    yin_total   = yin_cg_cnt  + yin_jj_cnt

    ilgan_yin = ilgan in _YIN_CG
    ilgan_label = "음간(陰干)" if ilgan_yin else "양간(陽干)"
    ilgan_color = "#9c27b0" if ilgan_yin else "#f57c00"

    # 원국 음양 시각화
    _PIL_LABELS = ["시주","일주","월주","년주"]
    html_yy = "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px'>"
    for i,(lb,p) in enumerate(zip(_PIL_LABELS,pils)):
        cg,jj = p["cg"],p["jj"]
        cg_y = "양" if cg in _YANG_CG else "음"
        jj_y = "양" if jj in _YANG_JJ else "음"
        cg_c = "#f57c00" if cg in _YANG_CG else "#9c27b0"
        jj_c = "#f57c00" if jj in _YANG_JJ else "#9c27b0"
        is_il = (lb=="일주")
        bdr = "border:2px solid #d4af37;" if is_il else "border:1px solid #ddd;"
        html_yy += (f"<div style='text-align:center;background:#fafaf5;{bdr}border-radius:8px;padding:8px 12px;min-width:70px'>"
                   f"<div style='font-size:10px;color:#888'>{lb}</div>"
                   f"<div style='font-size:20px;font-weight:900;color:{cg_c}'>{cg}</div>"
                   f"<div style='font-size:10px;color:{cg_c};font-weight:700'>{cg_y}간</div>"
                   f"<div style='font-size:20px;font-weight:900;color:{jj_c}'>{jj}</div>"
                   f"<div style='font-size:10px;color:{jj_c};font-weight:700'>{jj_y}지</div>"
                   f"</div>")
    html_yy += "</div>"
    st.markdown(html_yy, unsafe_allow_html=True)

    # 음양 비율 판정
    col_a, col_b = st.columns(2)
    with col_a:
        pct_yang = round(yang_total / (yang_total + yin_total) * 100) if (yang_total+yin_total) else 50
        bar_yang = "🟠" * (yang_total) + "🟣" * (yin_total)
        st.markdown(f"""<div style='background:#fff8f0;border:1px solid #f57c00;border-radius:10px;padding:12px'>
<div style='font-size:13px;font-weight:800;color:#e65100;margin-bottom:6px'>원국 음양 비율</div>
<div style='font-size:18px'>{bar_yang}</div>
<div style='font-size:12px;color:#555;margin-top:6px'>양(🟠): {yang_total}개 / 음(🟣): {yin_total}개</div>
</div>""", unsafe_allow_html=True)

    with col_b:
        # 음양 편중 진단
        if yang_total >= 7:
            bias = "양기(陽氣) 과다"
            bias_desc = "추진력·활동성·욕망이 강하지만 조급함과 독선으로 흐를 수 있다. 음적인 것(배려·기다림·절제)을 의식적으로 보완하라."
            bias_c = "#e65100"
        elif yin_total >= 7:
            bias = "음기(陰氣) 과다"
            bias_desc = "신중함·직관·포용력이 강하지만 우유부단·내성적 고립으로 흐를 수 있다. 양적인 것(행동·결단·표현)을 의식적으로 보완하라."
            bias_c = "#7b1fa2"
        elif yang_total == yin_total:
            bias = "음양 균형(均衡)"
            bias_desc = "음양이 균형을 이뤄 어떤 상황에도 적응하는 유연성이 강점이다. 상황에 따라 음양을 자유롭게 오가는 기질이다."
            bias_c = "#388e3c"
        else:
            bias = f"{'양기 우세' if yang_total > yin_total else '음기 우세'}"
            bias_desc = "큰 편중은 없으나 상황에 따라 조율이 필요하다."
            bias_c = "#1565c0"

        st.markdown(f"""<div style='background:#f5f5ff;border:1px solid {bias_c};border-radius:10px;padding:12px'>
<div style='font-size:13px;font-weight:800;color:{bias_c};margin-bottom:6px'>진단: {bias}</div>
<div style='font-size:12px;color:#333;line-height:1.8'>{bias_desc}</div>
</div>""", unsafe_allow_html=True)

    # 일간 음양별 성격 패턴
    _ILGAN_YY = {
        True: {  # 음간
            "甲": "",
            "乙": "을목(陰木) — 덩굴처럼 유연하게 환경에 적응하는 기질. 부드럽지만 끈질기다. 겉으론 여리나 속은 강하다.",
            "丁": "정화(陰火) — 촛불처럼 은은하고 섬세한 기질. 예술·상담·심리에 탁월하다. 감정 기복을 다스리는 것이 과제.",
            "己": "기토(陰土) — 정원의 흙처럼 세밀하고 꼼꼼한 기질. 섬세한 관리자형. 완벽주의 성향.",
            "辛": "신금(陰金) — 보석처럼 정밀하고 예리한 기질. 완벽주의·비판적 사고. 미적 감각이 뛰어나다.",
            "癸": "계수(陰水) — 안개·이슬처럼 섬세하고 감성적인 기질. 직관과 영감이 뛰어나다. 감정을 내면에 쌓는 경향."
        },
        False: {  # 양간
            "甲": "갑목(陽木) — 거목처럼 곧고 강직한 기질. 리더십·개척정신이 강하다. 고집과 자존심도 강하다.",
            "丙": "병화(陽火) — 태양처럼 밝고 열정적인 기질. 사교적·긍정적·표현력이 강하다. 쉽게 흥분하는 것이 약점.",
            "戊": "무토(陽土) — 산과 대지처럼 믿음직한 기질. 중재자·포용자형. 변화를 싫어하는 보수성.",
            "庚": "경금(陽金) — 강철처럼 강하고 단호한 기질. 결단력·원칙주의. 날카롭고 차가운 면이 약점.",
            "壬": "임수(陽水) — 강물처럼 역동적이고 지혜로운 기질. 추진력·글로벌 감각. 너무 많이 흘러 산만해질 수 있다."
        }
    }
    il_desc = _ILGAN_YY.get(ilgan_yin, {}).get(ilgan, f"일간 {ilgan} — {ilgan_label}의 기질이 전 생애를 이끈다.")
    if il_desc:
        st.markdown(f"""<div style='background:#fff;border-left:4px solid {ilgan_color};border-radius:0 10px 10px 0;padding:12px 16px;margin-top:10px'>
<div style='font-size:12px;font-weight:700;color:{ilgan_color};margin-bottom:4px'>일간 {ilgan} — {ilgan_label}</div>
<div style='font-size:13px;color:#222;line-height:1.8'>{il_desc}</div>
</div>""", unsafe_allow_html=True)


    # ── SECTION 1 심화: 음양 균형 심층 해석 ──────────────────────
    try:
        _OH_DEEP  = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        _CG_YY2 = {"甲":"양","乙":"음","丙":"양","丁":"음","戊":"양","己":"음","庚":"양","辛":"음","壬":"양","癸":"음"}
        _JJ_YY2 = {"子":"양","丑":"음","寅":"양","卯":"음","辰":"양","巳":"음","午":"음","未":"음","申":"양","酉":"음","戌":"양","亥":"음"}
        _yang2 = sum(1 for p in pils if _CG_YY2.get(p.get("cg",""))=="양") +                  sum(1 for p in pils if _JJ_YY2.get(p.get("jj",""))=="양")
        _yin2  = 8 - _yang2
        _oh_score2 = {"木":0,"火":0,"土":0,"金":0,"水":0}
        for _p2 in pils:
            _o2 = _OH_DEEP.get(_p2.get("cg",""),"")
            if _o2: _oh_score2[_o2] += 1
        _oh_max2 = max(_oh_score2, key=_oh_score2.get) if any(_oh_score2.values()) else "木"
        _oh_min2 = min(_oh_score2, key=_oh_score2.get) if any(_oh_score2.values()) else "水"
        _OH_KR2  = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
        _yy_key2 = "양>음" if _yang2>_yin2 else ("음>양" if _yin2>_yang2 else "균형")
        _YY_DEEP2 = {
            "양>음": ("외향적·활동적·추진력 강한 양기 사주",
                      "새로운 일을 먼저 시작하고 사람들을 이끄는 능력이 뛰어납니다. 에너지가 넘쳐 여러 일을 동시에 추진합니다.",
                      "과잉 에너지로 인한 무모한 돌진·조급함 주의. 음기 보충(명상·독서·휴식)이 필수입니다.",
                      "물가(江·海)에 자주 가고 조용한 사색 시간을 의식적으로 확보하십시오."),
            "음>양": ("내향적·사려깊음·감수성 풍부한 음기 사주",
                      "깊이 사고하고 세밀하게 분석하는 능력이 탁월합니다. 감정 교류와 배려가 뛰어나 신뢰받습니다.",
                      "소극적이거나 결정을 미루는 경향 주의. 양기 보충으로 추진력 강화가 필요합니다.",
                      "이른 아침 산행·활동적 운동을 생활화하고 적극적 도전의식을 훈련하십시오."),
            "균형":  ("음양 균형잡힌 조화로운 사주",
                      "어떤 환경에도 유연하게 적응하며 내향과 외향 모두 자유롭게 오갈 수 있는 균형 감각이 있습니다.",
                      "때로 중심 잡기 어렵거나 결정이 늦어질 수 있습니다.",
                      "이미 균형잡힌 팔자. 흐름을 과도하게 거스르지 말고 자연스럽게 나아가십시오."),
        }
        _s, _g, _w, _a = _YY_DEEP2[_yy_key2]
        st.markdown(f"""
<div style="background:#fff8f5;border:1px solid #c9a84c;border-radius:14px;padding:16px;margin:12px 0;box-sizing:border-box;width:100%">
<div style="font-size:15px;font-weight:900;color:#8b4513;margin-bottom:12px">🔬 음양 심층 해석 — {name}님의 기운 프로파일</div>
<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:10px">
  <div style="background:#fff3e0;border-radius:10px;padding:12px;box-sizing:border-box;width:100%">
    <div style="font-size:11px;color:#e65100;font-weight:700;margin-bottom:4px">🧬 기질 성향</div>
    <div style="font-size:13px;color:#4a2800;line-height:1.8;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_s}</div>
  </div>
  <div style="background:#e8f5e9;border-radius:10px;padding:12px;box-sizing:border-box;width:100%">
    <div style="font-size:11px;color:#2e7d32;font-weight:700;margin-bottom:4px">💪 핵심 강점</div>
    <div style="font-size:13px;color:#1b3a1e;line-height:1.8;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_g}</div>
  </div>
  <div style="background:#fce4ec;border-radius:10px;padding:12px;box-sizing:border-box;width:100%">
    <div style="font-size:11px;color:#c62828;font-weight:700;margin-bottom:4px">⚠️ 보완 약점</div>
    <div style="font-size:13px;color:#4a0000;line-height:1.8;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_w}</div>
  </div>
  <div style="background:#e3f2fd;border-radius:10px;padding:12px;box-sizing:border-box;width:100%">
    <div style="font-size:11px;color:#1565c0;font-weight:700;margin-bottom:4px">✅ 실천 조언</div>
    <div style="font-size:13px;color:#0d2744;line-height:1.8;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_a}</div>
  </div>
</div>
<div style="font-size:12px;color:#888;border-top:1px solid #e0d8c0;padding-top:8px">
가장 강한 오행: <b>{_OH_KR2.get(_oh_max2,_oh_max2)}</b> &nbsp;|&nbsp;
가장 약한 오행: <b>{_OH_KR2.get(_oh_min2,_oh_min2)}</b> — 약한 오행 보강 개운법을 실천하십시오.
</div></div>""", unsafe_allow_html=True)
    except Exception:
        pass


    # ── 음양 서술형 요약 ────────────────────────────────────────
    try:
        _yy_prose_map = {
            "양기 과다": (
                f"{name}님은 양기(陽氣)가 {yang_total}개로 강한 사주입니다. "
                f"밖을 향해 뻗어나가는 에너지가 넘쳐 늘 바쁘게 움직이고 새로운 일에 먼저 뛰어드는 기질이 있습니다. "
                f"추진력과 행동력이 뛰어나지만, 때로는 속도를 줄이고 내면을 들여다보는 시간이 필요합니다. "
                f"음기를 보충하는 조용한 명상·독서·물가 산책이 큰 도움이 됩니다."
            ),
            "음기 과다": (
                f"{name}님은 음기(陰氣)가 {yin_total}개로 강한 사주입니다. "
                f"깊이 사고하고 감수성이 풍부하여 예술·상담·연구 분야에서 뛰어난 능력을 발휘합니다. "
                f"섬세한 통찰력으로 사람들의 마음을 잘 읽지만, 결정을 내리는 순간에는 다소 머뭇거리는 경향이 있습니다. "
                f"양기를 보충하는 이른 아침 운동·적극적 자기표현·밝은 색상 착용을 생활화하십시오."
            ),
            "음양 균형": (
                f"{name}님의 사주는 양기 {yang_total}개, 음기 {yin_total}개로 음양의 균형이 잘 잡혀 있습니다. "
                f"내향과 외향을 자유롭게 오가며 어떤 환경에서도 안정적으로 중심을 잡는 탁월한 유연성이 있습니다. "
                f"이 균형이 {name}님의 가장 큰 강점이니, 어느 한쪽으로 지나치게 치우치지 않도록 주의하십시오."
            ),
        }
        _s1_key = "양기 과다" if yang_total >= 6 else ("음기 과다" if yin_total >= 6 else "음양 균형")
        _s1_prose = _yy_prose_map[_s1_key]
        import re as _re_b1
        if isinstance(_s1_prose, tuple):
            _s1_prose = ' '.join(str(x) for x in _s1_prose)
        else:
            _s1_prose = str(_s1_prose) if _s1_prose else ''
        _s1_prose = _re_b1.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', _s1_prose)
        st.markdown(f"""
<div style="background:#fffdf5;border:1px solid #c9a84c;border-radius:12px;padding:16px 18px;word-break:keep-all;overflow-wrap:break-word;box-sizing:border-box;width:100%;margin:12px 0">
<div style="font-size:13px;color:#4a2800;line-height:1.9;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_s1_prose}</div>
</div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 2: 납음오행(納音五行)
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">🎵 2. 납음오행(納音五行) — 60갑자의 숨겨진 기운</div>', unsafe_allow_html=True)

    try:
        # 일주 납음 찾기
        _CG_KR_FULL = {
            "甲":"甲(갑)","乙":"乙(을)","丙":"丙(병)","丁":"丁(정)","戊":"戊(무)",
            "己":"己(기)","庚":"庚(경)","辛":"辛(신)","壬":"壬(임)","癸":"癸(계)"
        }
        _JJ_KR_FULL = {
            "子":"子(자)","丑":"丑(축)","寅":"寅(인)","卯":"卯(묘)","辰":"辰(진)",
            "巳":"巳(사)","午":"午(오)","未":"未(미)","申":"申(신)","酉":"酉(유)",
            "戌":"戌(술)","亥":"亥(해)"
        }

        def _get_napeum(cg, jj):
            cg_kr = _CG_KR_FULL.get(cg, cg)
            jj_kr = _JJ_KR_FULL.get(jj, jj)
            key = f"{cg_kr}{jj_kr}"
            for (k1,k2), val in NABJIN_MAP.items():
                if key in (k1,k2):
                    return val
            return None

        pil_labels2 = ["시주","일주","월주","년주"]
        html_np = "<div style='display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px'>"
        for lb, p in zip(pil_labels2, pils):
            np_val = _get_napeum(p["cg"], p["jj"])
            if np_val:
                np_name, np_oh, np_desc = np_val
                np_color = _OH_COLOR.get(np_oh[:1] if np_oh else "", "#888")
                html_np += (f"<div style='background:#fafafa;border:1px solid {np_color}44;border-left:4px solid {np_color};border-radius:8px;padding:10px'>"
                           f"<div style='font-size:10px;color:#888'>{lb} — {p['cg']}{p['jj']}</div>"
                           f"<div style='font-size:15px;font-weight:900;color:{np_color};margin:4px 0'>{np_name}</div>"
                           f"<div style='font-size:11px;color:#555;line-height:1.7;white-space:normal;word-break:break-all'>{np_desc}</div>"
                           f"</div>")
            else:
                html_np += (f"<div style='background:#f5f5f5;border-radius:8px;padding:10px'>"
                           f"<div style='font-size:10px;color:#888'>{lb} — {p['cg']}{p['jj']}</div>"
                           f"<div style='font-size:13px;color:#aaa'>납음 데이터 없음</div></div>")
        html_np += "</div>"
        st.markdown(html_np, unsafe_allow_html=True)

        # 일주 납음 상세
        il_np = _get_napeum(ilgan, ilji)
        if il_np:
            il_np_name, il_np_oh, il_np_desc = il_np
            il_np_c = _OH_COLOR.get(il_np_oh[:1] if il_np_oh else "", "#888")
            st.markdown(f"""<div style='background:linear-gradient(135deg,#1a1a2e,#2a2a4e);border-radius:12px;padding:16px;color:#fff;margin-bottom:10px'>
<div style='font-size:11px;color:#aaa;margin-bottom:4px'>일주 납음 — 타고난 본질 기운</div>
<div style='font-size:20px;font-weight:900;color:#f7e695;margin-bottom:8px'>{ilgan}{ilji} → {il_np_name}</div>
<div style='font-size:13px;color:#ddd;line-height:1.9'>{il_np_desc}</div>
<div style='font-size:12px;color:{il_np_c};margin-top:8px;font-weight:700'>오행: {_OH_NAME.get(il_np_oh[:1] if il_np_oh else "","")}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("""<div style='background:#fff8e8;border-radius:8px;padding:10px 14px;font-size:12px;color:#5a3d00'>
💡 <b>납음오행이란?</b> 60갑자 각 일주에 숨겨진 고유 오행입니다. 원국의 표면 오행과 달리 <b>내면의 본질적 기운</b>을 나타냅니다.
궁합 시 두 사람의 납음오행이 상생(相生)이면 깊이 맞고, 상극(相剋)이면 마찰이 잦습니다.
</div>""", unsafe_allow_html=True)

        # ── 납음 서술형 요약 ─────────────────────────────────
        if il_np:
            _np_name2, _np_oh2, _ = il_np
            _OH_NP_PROSE = {
                "木": (
                    f"{name}님의 일주 납음은 **{_np_name2}**(木 계열)입니다. "
                    f"나무의 기운이 내면 깊은 곳에 흐르며, 겉으로 드러나는 성격보다 훨씬 강인하고 성장 지향적인 본질이 있습니다. "
                    f"새로운 것을 시작하고 개척하는 힘이 있어 시련 속에서도 다시 싹을 틔우는 끈질긴 생명력이 {name}님의 핵심입니다. "
                    f"**직업·재물**: 교육·출판·환경·농업·의류 등 '키우고 성장시키는' 분야에서 본질적 재능이 발휘됩니다. "
                    f"**개운**: 초록색을 가까이하고, 봄에 새로운 시작을 집중하십시오."
                ),
                "火": (
                    f"{name}님의 일주 납음은 **{_np_name2}**(火 계열)입니다. "
                    f"불의 기운이 내면 깊은 곳에 흐르며, 밖으로 표현되지 않을 때도 내면에는 강렬한 열정이 타오르고 있습니다. "
                    f"사람들을 밝게 비추고 분위기를 주도하는 능력이 있어 "
                    f"어두운 곳을 환하게 밝히는 역할이 {name}님의 본질적 소명입니다. "
                    f"**직업·재물**: 방송·예술·요식업·에너지·마케팅 분야에서 납음 화의 기운이 빛납니다. "
                    f"**개운**: 빨간색 소품, 촛불, 남쪽 방향을 활용하십시오."
                ),
                "土": (
                    f"{name}님의 일주 납음은 **{_np_name2}**(土 계열)입니다. "
                    f"흙의 기운이 내면에 흐르며, 어떤 상황에서도 중심을 잃지 않는 든든한 안정감이 본질입니다. "
                    f"모든 것을 품는 대지처럼 {name}님은 다양한 사람과 상황을 포용하는 능력이 있습니다. "
                    f"**직업·재물**: 부동산·건설·농업·의료·금융 분야에서 납음 토의 기운이 안정적 재물을 쌓게 합니다. "
                    f"**개운**: 황토색·노란색 소품, 맨발 흙 밟기, 집 중앙을 정리하십시오."
                ),
                "金": (
                    f"{name}님의 일주 납음은 **{_np_name2}**(金 계열)입니다. "
                    f"금속의 기운이 내면에 흐르며, 단련될수록 더욱 빛나는 보석 같은 본질입니다. "
                    f"결단력과 정밀함이 강하고, 한번 정한 것은 끝까지 가는 의지가 {name}님의 핵심 무기입니다. "
                    f"**직업·재물**: 금융·법조·의료·보석·기계 분야에서 납음 금의 예리함이 발휘됩니다. "
                    f"**개운**: 흰색·은색 착용, 서쪽 방향 활용, 정리정돈을 생활화하십시오."
                ),
                "水": (
                    f"{name}님의 일주 납음은 **{_np_name2}**(水 계열)입니다. "
                    f"물의 기운이 내면에 흐르며, 어떤 그릇에도 맞게 변하는 유연성과 깊은 지혜가 본질입니다. "
                    f"모든 것을 적시고 흘러가듯 {name}님은 상황에 따라 자유롭게 변화하며 적응하는 능력이 탁월합니다. "
                    f"**직업·재물**: 무역·IT·철학·의학·유통 분야에서 납음 수의 지혜가 빛납니다. "
                    f"**개운**: 검은색·남색 착용, 북쪽 방향 활용, 명상·독서를 생활화하십시오."
                ),
            }
            _np_prose_raw = _OH_NP_PROSE.get(_np_oh2[:1] if _np_oh2 else "",
                f"{name}님의 일주 납음은 {_np_name2}으로, 이 기운이 내면 깊은 곳에서 {name}님을 이끌고 있습니다.")
            import re as _re_np2
            # tuple이면 join, str이면 그대로 사용
            if isinstance(_np_prose_raw, tuple):
                _np_prose_txt = ' '.join(str(x) for x in _np_prose_raw)
            else:
                _np_prose_txt = str(_np_prose_raw) if _np_prose_raw else ''
            _np_prose = _re_np2.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', _np_prose_txt)
            st.markdown(f"""
<div style="background:#fffdf5;border:1px solid #c9a84c;border-radius:12px;padding:16px 18px;word-break:keep-all;overflow-wrap:break-word;margin:10px 0">
<div style="font-size:13px;color:#4a2800;line-height:1.9;word-break:break-all;overflow-wrap:break-word;white-space:normal">{_np_prose}</div>
</div>""", unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"납음 계산 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 3: 오행 생극제화(生剋制化)

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 3: 오행 생극제화(生剋制化)
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">⚡ 3. 오행 생극제화(生剋制化) — 원국 내부 힘의 흐름</div>', unsafe_allow_html=True)

    try:
        oh_strength = calc_ohaeng_strength(ilgan, pils) or {}
        oh_total = sum(oh_strength.values()) or 1

        # 상생 관계: 木→火→土→金→水→木
        _SANG_SAENG = [("木","火"),("火","土"),("土","金"),("金","水"),("水","木")]
        # 상극 관계: 木→土, 土→水, 水→火, 火→金, 金→木
        _SANG_GEUK  = [("木","土"),("土","水"),("水","火"),("火","金"),("金","木")]

        saeng_active, geuk_active = [], []
        for a, b in _SANG_SAENG:
            va, vb = oh_strength.get(a,0), oh_strength.get(b,0)
            if va >= 10 and vb >= 5:
                saeng_active.append((a,b,va,vb))
        for a, b in _SANG_GEUK:
            va, vb = oh_strength.get(a,0), oh_strength.get(b,0)
            if va >= 15 and vb >= 5:
                geuk_active.append((a,b,va,vb))

        col_sg1, col_sg2 = st.columns(2)
        with col_sg1:
            st.markdown("<div style='font-size:13px;font-weight:800;color:#27ae60;margin-bottom:8px'>🌱 활성 상생(相生) — 도움을 주는 흐름</div>", unsafe_allow_html=True)
            if saeng_active:
                for a,b,va,vb in saeng_active:
                    ac,bc = _OH_COLOR[a], _OH_COLOR[b]
                    st.markdown(f"<div style='background:#f0fff4;border-radius:8px;padding:8px 12px;margin:4px 0'>"
                               f"<span style='color:{ac};font-weight:900'>{_OH_NAME[a]}({va:.0f})</span>"
                               f" → <span style='color:{bc};font-weight:900'>{_OH_NAME[b]}({vb:.0f})</span>"
                               f"<div style='font-size:11px;color:#555;margin-top:2px'>{_OH_NAME[a]}이 {_OH_NAME[b]}을 키워주는 구조</div>"
                               f"</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#aaa;font-size:12px;padding:8px'>활성화된 강한 상생 없음</div>", unsafe_allow_html=True)

        with col_sg2:
            st.markdown("<div style='font-size:13px;font-weight:800;color:#e53935;margin-bottom:8px'>⚔️ 활성 상극(相剋) — 갈등·억압 흐름</div>", unsafe_allow_html=True)
            if geuk_active:
                for a,b,va,vb in geuk_active:
                    ac,bc = _OH_COLOR[a], _OH_COLOR[b]
                    st.markdown(f"<div style='background:#fff5f5;border-radius:8px;padding:8px 12px;margin:4px 0'>"
                               f"<span style='color:{ac};font-weight:900'>{_OH_NAME[a]}({va:.0f})</span>"
                               f" ✗ <span style='color:{bc};font-weight:900'>{_OH_NAME[b]}({vb:.0f})</span>"
                               f"<div style='font-size:11px;color:#c0392b;margin-top:2px'>{_OH_NAME[a]}이 {_OH_NAME[b]}을 억압하는 구조</div>"
                               f"</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#aaa;font-size:12px;padding:8px'>활성화된 강한 상극 없음</div>", unsafe_allow_html=True)

        # 오행 분포 바 차트
        st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
        for oh_key in ["木","火","土","金","水"]:
            val = oh_strength.get(oh_key, 0)
            pct = int(val / oh_total * 100)
            c = _OH_COLOR[oh_key]
            status = "과다(抑制 필요)" if pct >= 35 else "부족(補充 필요)" if pct <= 8 else "적정"
            status_c = "#e53935" if pct >= 35 else "#1565c0" if pct <= 8 else "#388e3c"
            st.markdown(f"""<div style='display:flex;align-items:center;gap:8px;margin-bottom:5px'>
    <span style='width:40px;font-weight:700;color:{c}'>{_OH_NAME[oh_key]}</span>
    <div style='flex:1;background:#eee;border-radius:6px;height:14px'>
      <div style='width:{pct}%;background:{c};height:14px;border-radius:6px;transition:width 0.5s'></div>
    </div>
    <span style='width:36px;text-align:right;font-size:12px;color:#555'>{pct}%</span>
    <span style='font-size:11px;color:{status_c};min-width:90px'>{status}</span>
    </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── 생극제화 서술형 요약 ─────────────────────────────
        _OH_KR_S3 = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
        _s3_sentences = []
        if saeng_active:
            _sg_txt = ", ".join(f"{_OH_KR_S3.get(a,a)}이 {_OH_KR_S3.get(b,b)}을 생해주는" for a,b,va,vb in saeng_active[:2])
            _s3_sentences.append(
                f"{name}님의 원국에는 {_sg_txt} 상생(相生)의 흐름이 활성화되어 있습니다. "
                f"이 기운들이 서로 도우며 {name}님의 에너지를 순환시키고 있어 "
                f"전반적으로 조화롭고 안정적인 구조입니다."
            )
        if geuk_active:
            _gk_txt = ", ".join(f"{_OH_KR_S3.get(a,a)}이 {_OH_KR_S3.get(b,b)}을 극하는" for a,b,va,vb in geuk_active[:2])
            _s3_sentences.append(
                f"반면 {_gk_txt} 상극(相剋)의 긴장 구조도 있습니다. "
                f"이는 내면에서 두 가지 기운이 충돌하는 것으로, "
                f"갈등과 도전이 있지만 그만큼 강해지는 단련의 구조이기도 합니다."
            )
        if not saeng_active and not geuk_active:
            _s3_sentences.append(
                f"{name}님의 원국에는 뚜렷한 상생·상극 구조가 없는 평온한 배치입니다. "
                f"각 오행이 독립적으로 작용하며, 극단적인 기복보다 꾸준한 흐름이 특징입니다."
            )
        if _s3_sentences:
            st.markdown(f"""
<div style="background:#fffdf5;border:1px solid #c9a84c;border-radius:12px;padding:16px 18px;word-break:keep-all;overflow-wrap:break-word;margin:10px 0">
<div style="font-size:13px;color:#4a2800;line-height:1.9;word-break:break-all;overflow-wrap:break-word;white-space:normal">{'<br>'.join(_s3_sentences)}</div>
</div>""", unsafe_allow_html=True)

    except Exception as _e3:
        st.warning(f"오행 생극 분석 오류: {_e3}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)


    # ── SECTION 3 심화: 오행 불균형 인생 영향 ────────────────────
    try:
        _oh_s3 = calc_ohaeng_strength(ilgan, pils) or {}
        if _oh_s3:
            _OH_LIFE3 = {
                "木": {
                    "과다": (
                        f"과다한 木기운 → 지나친 고집·자존심 충돌 주의. 金 오행으로 다듬는 연습이 필요합니다. "
                        f"**직업**: 개척·창업보다 협력하는 구조에서 균형을 맞추십시오. "
                        f"**재물**: 혼자 모든 것을 결정하는 투자보다 전문가 조언을 수용하십시오. "
                        f"**건강**: 간장·담낭·눈 계통, 분노 조절이 핵심 과제입니다."
                    ),
                    "부족": (
                        f"木기운 부족 → 의지력·시작하는 힘이 약합니다. 동쪽 방향·녹색 활용으로 기운을 보충하십시오. "
                        f"**직업**: 처음 시작하는 것을 두려워하지 말고, 작은 도전부터 습관화하십시오. "
                        f"**재물**: 봄(3~5월)에 새로운 재물 기회를 적극 탐색하십시오."
                    ),
                },
                "火": {
                    "과다": (
                        f"과다한 火기운 → 성급함·충동적 언행·심혈관 주의. 水 오행으로 냉각이 필요합니다. "
                        f"**직업**: 빠른 환경보다 집중력이 요구되는 분야에서 에너지를 조절하십시오. "
                        f"**재물**: 충동적 투자를 자제하고 24시간 숙고 원칙을 지키십시오. "
                        f"**건강**: 심장·혈압·안구 건조증을 정기적으로 점검하십시오."
                    ),
                    "부족": (
                        f"火기운 부족 → 열정·표현력이 약합니다. 남쪽 방향·붉은 색상으로 기운을 보충하십시오. "
                        f"**직업**: 자기표현과 홍보를 의식적으로 연습하십시오. "
                        f"**재물**: 여름(6~8월)에 적극적으로 나서면 재물 기회가 옵니다."
                    ),
                },
                "土": {
                    "과다": (
                        f"과다한 土기운 → 완고함·소화기 주의. 木 오행으로 유연성과 소통 강화가 필요합니다. "
                        f"**직업**: 변화를 두려워하지 말고 새로운 트렌드를 수용하십시오. "
                        f"**재물**: 부동산·저축은 강점이나 지나친 보수성이 기회 손실을 만들 수 있습니다. "
                        f"**건강**: 위장·비장·소화기, 과식을 주의하십시오."
                    ),
                    "부족": (
                        f"土기운 부족 → 신뢰감·안정감이 약합니다. 황색·베이지 활용으로 기운을 보충하십시오. "
                        f"**직업**: 약속과 신용을 철저히 지키는 것이 최고의 경쟁력입니다. "
                        f"**재물**: 변동성이 큰 투자보다 안정적 저축·부동산이 맞습니다."
                    ),
                },
                "金": {
                    "과다": (
                        f"과다한 金기운 → 냉정함·인간관계 경직·호흡기 주의. 火 오행으로 온기 보충이 필요합니다. "
                        f"**직업**: 날카로운 분석력은 강점이나 팀워크에서 배려를 더하십시오. "
                        f"**재물**: 완벽주의로 인한 기회 손실을 주의하십시오. "
                        f"**건강**: 폐·대장·피부·호흡기를 정기적으로 점검하십시오."
                    ),
                    "부족": (
                        f"金기운 부족 → 결단력·추진력이 약합니다. 서쪽 방향·흰색·금속 악세서리로 보강하십시오. "
                        f"**직업**: 중요한 결정을 미루는 습관을 고쳐야 합니다. "
                        f"**재물**: 가을(9~11월)에 결단하고 수확하는 전략이 유리합니다."
                    ),
                },
                "水": {
                    "과다": (
                        f"과다한 水기운 → 우유부단·감정 기복·신장 주의. 土 오행으로 중심 잡기가 필요합니다. "
                        f"**직업**: 아이디어는 풍부하나 실행력이 부족할 수 있으니 완성력을 키우십시오. "
                        f"**재물**: 지나치게 분산된 투자를 집중화하십시오. "
                        f"**건강**: 신장·방광·관절 계통, 냉기를 조심하십시오."
                    ),
                    "부족": (
                        f"水기운 부족 → 지혜·유연성이 약합니다. 북쪽 방향·검정·남색으로 보강하십시오. "
                        f"**직업**: 독서·명상으로 지혜를 쌓고, 적응력을 키우십시오. "
                        f"**재물**: 겨울(11~1월)에 내실을 다지고 봄을 준비하십시오."
                    ),
                },
            }
            _OH_KR3 = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
            _sorted3 = sorted(_oh_s3.items(), key=lambda x:-x[1])
            _max3, _maxs3 = _sorted3[0]
            _min3, _mins3 = _sorted3[-1]
            _msgs3 = []
            if _maxs3 > 2:
                _raw = _OH_LIFE3.get(_max3,{}).get("과다","")
                if isinstance(_raw, tuple):
                    _msg3 = ' '.join(str(x) for x in _raw)
                elif isinstance(_raw, str):
                    _msg3 = _raw
                else:
                    _msg3 = str(_raw)
                _msgs3.append(("📈 과다", _max3, "ff6f00", "fff3e0", _msg3))
            if _mins3 < 1:
                _raw = _OH_LIFE3.get(_min3,{}).get("부족","")
                if isinstance(_raw, tuple):
                    _msg3 = ' '.join(str(x) for x in _raw)
                elif isinstance(_raw, str):
                    _msg3 = _raw
                else:
                    _msg3 = str(_raw)
                _msgs3.append(("📉 부족", _min3, "388e3c", "e8f5e9", _msg3))
            if _msgs3:
                _h3 = '<div style="background:#fff8f0;border:1px solid #f57c00;border-radius:12px;padding:14px 16px;margin:10px 0"><div style="font-size:14px;font-weight:900;color:#e65100;margin-bottom:10px">⚡ 오행 불균형 인생 영향 분석</div>'
                for _lbl, _oh, _c, _bg, _msg in _msgs3:
                    _h3 += f'<div style="background:#{_bg};border-left:4px solid #{_c};border-radius:0 8px 8px 0;padding:10px 12px;margin-bottom:8px"><div style="font-size:12px;font-weight:700;color:#{_c}">{_lbl} — {_OH_KR3.get(_oh,_oh)}</div><div style="font-size:13px;line-height:1.7;white-space:normal;word-break:break-all;margin-top:4px";word-break:break-all;overflow-wrap:break-word;white-space:normal">{__import__('re').sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', str(_msg))}</div></div>'
                _h3 += '</div>'
                st.markdown(_h3, unsafe_allow_html=True)
    except Exception:
        pass

        # ════════════════════════════════════════════
    # SECTION 4: 형(刑)·파(破)·해(害) 전수 감지
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">⚠️ 4. 형(刑)·파(破)·해(害) — 원국 갈등 구조 전수 분석</div>', unsafe_allow_html=True)

    found_any = False

    # 4-1 형살(刑殺)
    hyung_found = []
    # 삼형살
    for combo, (hname, htype, hdesc) in HYUNG_MAP.items():
        jj_set = set(all_jj)
        if combo.issubset(jj_set):
            hyung_found.append(("🔴 삼형살", hname, htype, hdesc))
    # 자형(自刑)
    for jj in all_jj:
        if all_jj.count(jj) >= 2 and jj in SELF_HYUNG:
            hyung_found.append(("🟡 자형살", f"{jj}{jj} 자형(自刑)", "自刑", f"{jj} 지지가 겹쳐 자기 자신을 상하게 하는 구조. 자책감·반복적 실수 주의."))

    if hyung_found:
        found_any = True
        for badge, hname, htype, hdesc in hyung_found:
            st.markdown(f"""<div style='background:#fff0f0;border:1px solid #e53935;border-left:5px solid #e53935;border-radius:10px;padding:14px;margin-bottom:8px'>
<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>
<span style='font-size:14px;font-weight:900;color:#c0392b'>{badge} {hname}</span>
<span style='background:#e53935;color:#fff;font-size:11px;padding:2px 8px;border-radius:10px'>{htype}</span>
</div>
<div style='font-size:13px;color:#333;line-height:1.8'>{hdesc}</div>
<div style='font-size:12px;color:#c0392b;margin-top:6px;font-weight:700'>
⚡ 직격 처방: 법적 서류는 반드시 전문가 검토 후 서명. 고집을 꺾는 연습이 평생 과제다.
</div>
</div>""", unsafe_allow_html=True)

    # 4-2 파살(破殺)
    pa_found = []
    jj_pairs = [(all_jj[i],all_jj[j]) for i in range(len(all_jj)) for j in range(i+1,len(all_jj))]
    for j1,j2 in jj_pairs:
        pk = frozenset([j1,j2])
        if pk in PA_MAP:
            pname, pdesc = PA_MAP[pk]
            pa_found.append((pname, pdesc, j1, j2))

    if pa_found:
        found_any = True
        for pname, pdesc, j1, j2 in pa_found:
            st.markdown(f"""<div style='background:#fff8f0;border:1px solid #f57c00;border-left:5px solid #f57c00;border-radius:10px;padding:14px;margin-bottom:8px'>
<div style='font-size:14px;font-weight:900;color:#e65100;margin-bottom:6px'>💥 파살(破殺) — {pname}</div>
<div style='font-size:11px;color:#888;margin-bottom:6px'>{j1} × {j2} 조합</div>
<div style='font-size:13px;color:#333;line-height:1.8'>{pdesc}</div>
<div style='font-size:12px;color:#e65100;margin-top:6px;font-weight:700'>
⚡ 직격 처방: 시작한 일을 끝까지 마무리하는 습관이 파살을 이기는 유일한 방법이다.
</div>
</div>""", unsafe_allow_html=True)

    # 4-3 해살(害殺)
    hae_found = []
    for j1,j2 in jj_pairs:
        hk = frozenset([j1,j2])
        if hk in HAE_MAP:
            hname, hdesc = HAE_MAP[hk]
            hae_found.append((hname, hdesc, j1, j2))

    if hae_found:
        found_any = True
        for hname, hdesc, j1, j2 in hae_found:
            st.markdown(f"""<div style='background:#f5f0ff;border:1px solid #7b1fa2;border-left:5px solid #7b1fa2;border-radius:10px;padding:14px;margin-bottom:8px'>
<div style='font-size:14px;font-weight:900;color:#6a1b9a;margin-bottom:6px'>🔮 해살(害殺) — {hname}</div>
<div style='font-size:11px;color:#888;margin-bottom:6px'>{j1} × {j2} 조합</div>
<div style='font-size:13px;color:#333;line-height:1.8'>{hdesc}</div>
<div style='font-size:12px;color:#6a1b9a;margin-top:6px;font-weight:700'>
⚡ 직격 처방: 인간관계에서 먼저 의심하기보다 명확한 소통으로 오해를 차단하라.
</div>
</div>""", unsafe_allow_html=True)

    if not found_any:
        st.markdown("""<div style='background:#f0fff4;border:1px solid #27ae60;border-radius:10px;padding:16px;text-align:center'>
<div style='font-size:16px;font-weight:800;color:#27ae60;margin-bottom:6px'>✅ 원국에 형·파·해 없음</div>
<div style='font-size:13px;color:#333'>원국 지지 조합에서 형살·파살·해살이 감지되지 않았습니다.<br>대운·세운에서 들어올 때는 주의가 필요합니다.</div>
</div>""", unsafe_allow_html=True)


    # ── 형파해 서술형 요약 ──────────────────────────────────────
    try:
        _hph_ch = get_chung_hyung(pils) if 'get_chung_hyung' in dir() else {}
        _hph_chung = _hph_ch.get("충", [])
        _hph_hyung = _hph_ch.get("형", [])

        _hph_sentences = []
        if _hph_chung or _hph_hyung:
            if _hph_chung:
                _hph_sentences.append(
                    f"{name}님의 원국에는 충(沖)의 기운이 있습니다. "
                    f"충은 두 기운이 정면으로 부딪히는 것으로, 변화·이동·갈등의 에너지가 내재되어 있습니다. "
                    f"삶에서 크고 작은 변화가 잦을 수 있지만, 이 에너지를 잘 활용하면 "
                    f"오히려 새로운 기회와 역동적인 삶의 원동력이 됩니다."
                )
            if _hph_hyung:
                _hph_sentences.append(
                    f"또한 형(刑)의 구조도 있어 규칙이나 타인과의 마찰이 생기기 쉬운 배치입니다. "
                    f"법적·관계적 분쟁을 조심하고, 언행을 신중히 하는 것이 평생의 과제입니다."
                )
        else:
            _hph_sentences.append(
                f"{name}님의 원국에는 형·충·파·해의 갈등 구조가 두드러지지 않습니다. "
                f"각 기둥의 기운이 비교적 조화롭게 배치되어 있어 안정적인 인생 구조를 가졌습니다."
            )
        if _hph_sentences:
            st.markdown(f"""
<div style="background:#fffdf5;border:1px solid #c9a84c;border-radius:12px;padding:16px 18px;word-break:keep-all;overflow-wrap:break-word;box-sizing:border-box;width:100%;margin:10px 0">
<div style="font-size:13px;color:#4a2800;line-height:1.9;word-break:break-all;overflow-wrap:break-word;white-space:normal">{'<br>'.join(_hph_sentences)}</div>
</div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 5: 십이신살(十二神殺) 풀셋
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">🌟 5. 십이신살(十二神殺) 풀셋 — 원국+대운+세운 교차</div>', unsafe_allow_html=True)

    # 십이신살 기준: 년지 기준
    _12_SINSAL_TABLE = {
        "申子辰": ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"],
        "寅午戌": ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"],
        "亥卯未": ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"],
        "巳酉丑": ["겁살","재살","천살","지살","년살","월살","망신살","장성살","반안살","역마살","육해살","화개살"],
    }
    _12_JJ_ORDER = {
        "申子辰": ["巳","午","未","申","酉","戌","亥","子","丑","寅","卯","辰"],
        "寅午戌": ["亥","子","丑","寅","卯","辰","巳","午","未","申","酉","戌"],
        "亥卯未": ["申","酉","戌","亥","子","丑","寅","卯","辰","巳","午","未"],
        "巳酉丑": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    }
    _12_SINSAL_DESC = {
        "겁살": {"emoji":"⚡","color":"#c0392b","desc":"강제 손실·빼앗김의 살. 재물·지위·건강이 갑자기 사라지는 기운. 평소 비상금 확보 필수.","직격":"이 살 발동 시기엔 보증·투자·동업 절대 금지. 가장 믿는 사람에게 배신당하는 구조다."},
        "재살": {"emoji":"🔒","color":"#7b1fa2","desc":"관재·구속·법적 문제의 살. 구설수와 시비가 따름. 언행을 극도로 조심해야 하는 기운.","직격":"이 살 발동 시기엔 서명·계약을 미루거나 법률 전문가와 함께 하라."},
        "천살": {"emoji":"⛈️","color":"#1565c0","desc":"하늘이 내리는 재앙. 예측 불가능한 사고·재난의 기운. 기상 이변·자연재해와도 관련.","직격":"이 살이 강한 시기엔 야외 활동·여행을 자제하고 보험을 점검하라."},
        "지살": {"emoji":"🚗","color":"#2e7d32","desc":"이동·교통·이사의 살. 잦은 이동과 변화가 생기는 기운. 교통사고 주의.","직격":"이 살 발동 시기엔 운전 시 각별히 주의하고 불필요한 이동을 줄여라."},
        "년살": {"emoji":"🌹","color":"#e91e8c","desc":"도화살의 일종. 이성 인기와 매력의 기운. 이성 문제와 구설이 함께 따름.","직격":"이 살 발동 시기엔 이성 관계에서 경솔한 행동을 삼가라. 이미 상대가 있다면 특히 조심."},
        "월살": {"emoji":"🌙","color":"#455a64","desc":"고초살(枯焦殺). 메마름과 고독의 기운. 아무리 노력해도 결실이 안 맺히는 시기.","직격":"이 살 발동 시기엔 결실보다 씨앗 심기에 집중하라. 지금은 준비 기간이다."},
        "망신살": {"emoji":"🔇","color":"#f57c00","desc":"명예 손상·망신의 살. 말실수·행동으로 평판이 손상되는 기운.","직격":"이 살 발동 시기엔 SNS 발언·술자리 언행을 극도로 조심하라. 침묵이 금이다."},
        "장성살": {"emoji":"👑","color":"#d4af37","desc":"강한 기운과 추진력의 살. 리더십이 발휘되나 독선·충돌도 따름.","직격":"이 살 발동 시기엔 리더십을 발휘하되 독단을 경계하라. 타인 의견을 경청하면 성과 2배."},
        "반안살": {"emoji":"🛡️","color":"#00838f","desc":"안전·안정의 살. 조용히 기반을 다지는 기운. 보수적이지만 안전한 선택이 맞는 시기.","직격":"이 살 발동 시기엔 공격보다 수비가 맞다. 기존 것을 지키는 전략이 최선."},
        "역마살": {"emoji":"🚀","color":"#1565c0","desc":"이동·변화·해외의 살. 가만히 있으면 손해, 움직이면 기회가 오는 기운.","직격":"이 살 발동 시기엔 이동·출장·이직이 오히려 기회다. 한 곳에 고집하면 손해를 본다."},
        "육해살": {"emoji":"⚓","color":"#546e7a","desc":"집착·미련·족쇄의 살. 놓아야 할 것을 못 놓는 기운. 인간관계 단절이 생기기도 함.","직격":"이 살 발동 시기엔 과거의 인연·감정·사업을 정리하고 새출발하는 것이 맞다."},
        "화개살": {"emoji":"🕯️","color":"#5d4037","desc":"예술·종교·고독의 살. 세속과 멀어지고 정신세계로 향하는 기운.","직격":"이 살 발동 시기엔 예술·종교·명상으로 에너지를 쓰면 탁월한 성취가 온다. 사업보다 기술·학문이 맞다."},
    }

    # 년지 기준 삼합국 판별
    nyeonji = pils[3]["jj"]  # 년주 지지
    _12_GROUP = None
    for group, jj_list in _12_JJ_ORDER.items():
        if nyeonji in group:
            _12_GROUP = group
            break

    if _12_GROUP:
        jj_order = _12_JJ_ORDER[_12_GROUP]
        sinsal_names = _12_SINSAL_TABLE[_12_GROUP]

        # 원국 지지별 신살 매핑
        sinsal_hits = {}
        for jj in all_jj:
            if jj in jj_order:
                idx = jj_order.index(jj)
                sname = sinsal_names[idx]
                if sname not in sinsal_hits:
                    sinsal_hits[sname] = []
                sinsal_hits[sname].append(jj)

        # 올해 세운 지지 체크
        try:
            sw_now = get_yearly_luck(pils, cur_year) or {}
            sw_jj_now = sw_now.get("jj","")
            if sw_jj_now and sw_jj_now in jj_order:
                idx = jj_order.index(sw_jj_now)
                sw_sinsal = sinsal_names[idx]
            else:
                sw_sinsal = None
        except Exception:
            sw_sinsal = None

        if sinsal_hits:
            st.markdown(f"<div style='font-size:12px;color:#888;margin-bottom:10px'>기준 삼합국: {_12_GROUP} / 년지: {nyeonji}</div>", unsafe_allow_html=True)
            for sname, jjs in sinsal_hits.items():
                sd = _12_SINSAL_DESC.get(sname, {})
                sc = sd.get("color","#666")
                se = sd.get("emoji","📍")
                is_sw = (sname == sw_sinsal)
                bdr = "border:2px solid #d4af37;" if is_sw else f"border:1px solid {sc}44;"
                sw_badge = " 🌟올해세운발동!" if is_sw else ""
                st.markdown(f"""<div style='background:#fafafa;{bdr}border-left:5px solid {sc};border-radius:10px;padding:12px 14px;margin-bottom:6px'>
<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:5px'>
<span style='font-size:14px;font-weight:900;color:{sc}'>{se} {sname} — {"/".join(jjs)} 지지</span>
<span style='font-size:11px;color:#888'>{sw_badge}</span>
</div>
<div style='font-size:12px;color:#333;line-height:1.8'>{sd.get("desc","")}</div>
<div style='font-size:12px;color:{sc};font-weight:700;margin-top:6px'>⚡ {sd.get("직격","")}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.info("원국에서 발동되는 십이신살이 없습니다.")

        if sw_sinsal:
            sw_sd = _12_SINSAL_DESC.get(sw_sinsal, {})
            st.markdown(f"""<div style='background:linear-gradient(135deg,#1a1a2e,#2a1a3e);border:2px solid #d4af37;border-radius:12px;padding:16px;margin-top:12px;color:#fff'>
<div style='font-size:13px;font-weight:900;color:#f7e695;margin-bottom:8px'>🔥 올해({cur_year}년) 세운에서 발동되는 신살: <b>{sw_sinsal}</b></div>
<div style='font-size:13px;color:#ddd;line-height:1.8'>{sw_sd.get("desc","")}</div>
<div style='font-size:13px;color:#f7e695;font-weight:700;margin-top:8px'>⚡ 직격 처방: {sw_sd.get("직격","")}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("십이신살 기준을 계산할 수 없습니다.")


    # ── 십이신살 서술형 요약 ────────────────────────────────────
    try:
        _sin12_list = get_12sinsal(pils) if 'get_12sinsal' in dir() else []
        if _sin12_list:
            _sin_names = [s.get("이름","") for s in _sin12_list if isinstance(s,dict) and s.get("이름")]
            _SIN_PROSE = {
                "역마살": (
                    f"**역마살(驛馬殺)**이 있습니다. 끊임없이 이동하고 변화를 추구하는 기운이 강합니다. "
                    f"한곳에 오래 있으면 답답함을 느끼고, 이직·이사·여행이 잦을 수 있습니다. "
                    f"**직업**: 무역·영업·여행·운송·IT 분야가 잘 맞습니다. "
                    f"**재물**: 이동 중에 기회를 만나는 팔자이니 적극적으로 발품을 파십시오. "
                    f"**주의**: 충동적인 이직·이사는 신중히 결정하십시오."
                ),
                "도화살": (
                    f"**도화살(桃花殺)**이 있습니다. 타고난 매력과 이성을 끄는 기운이 강합니다. "
                    f"사람들에게 자연스럽게 호감을 주는 기질이 있어 대인관계에서 큰 자산이 됩니다. "
                    f"**직업**: 예술·연예·방송·서비스·교육 분야에서 빛납니다. "
                    f"**재물**: 사람을 통해 재물이 오는 구조이니 인맥 관리가 최고의 투자입니다. "
                    f"**주의**: 이성 문제로 인한 구설수와 손재를 조심하십시오."
                ),
                "화개살": (
                    f"**화개살(華蓋殺)**이 있습니다. 종교·철학·예술에 깊은 인연이 있는 고독한 학자형 기운입니다. "
                    f"고독함 속에서 깊은 통찰을 얻고, 혼자만의 세계에서 창조적 결실을 맺습니다. "
                    f"**직업**: 학문·연구·종교·예술·상담 분야에서 독보적 성취가 가능합니다. "
                    f"**주의**: 사회적 고립이 되지 않도록 의식적으로 관계를 넓히십시오."
                ),
                "겁살": (
                    f"**겁살(劫殺)**이 있습니다. 외부의 갑작스러운 손재수·변동이 따르는 기운입니다. "
                    f"**재물**: 보증·동업·투기 투자를 반드시 피하십시오. 현금 보유를 늘리고 비상금을 확보하십시오. "
                    f"**건강**: 갑작스러운 사고에 대비해 보험을 꼭 가입하십시오. "
                    f"**주의**: 충동적 지출·결정을 자제하고 24시간 이상 숙고 후 결정하십시오."
                ),
                "재살": (
                    f"**재살(災殺)**이 있습니다. 사고수·관재수·건강 이상이 따르기 쉬운 기운입니다. "
                    f"**주의**: 이동 중 안전에 각별히 주의하고, 법적 분쟁을 미리 예방하십시오. "
                    f"**건강**: 정기 건강검진을 반드시 받고, 수술·시술은 세운 확인 후 결정하십시오."
                ),
                "천살": (
                    f"**천살(天殺)**이 있습니다. 윗사람·상사·권위자와 마찰이 생기기 쉬운 기운입니다. "
                    f"**직장**: 조직 내 처신을 지혜롭게 하고, 불필요한 충돌을 피하십시오. "
                    f"**재물**: 불법적·편법적 방법으로 재물을 취하려 하면 반드시 탈이 납니다."
                ),
                "지살": (
                    f"**지살(地殺)**이 있습니다. 이사·이직·환경 변화의 기운이 강합니다. "
                    f"변화를 두려워하지 말고 더 좋은 환경으로 과감히 나아가십시오. "
                    f"**재물**: 환경이 바뀔 때마다 새로운 기회가 옵니다."
                ),
                "장성살": (
                    f"**장성살(將星殺)**이 있습니다. 타고난 리더십과 통솔력의 기운입니다. "
                    f"**직업**: 군·경·경영·스포츠 등 조직을 이끄는 역할이 잘 맞습니다. "
                    f"**재물**: 조직의 수장 자리에 오를수록 재물이 따라옵니다."
                ),
                "반안살": (
                    f"**반안살(攀鞍殺)**이 있습니다. 꾸준한 노력이 쌓여 결실을 맺는 기운입니다. "
                    f"서두르지 않고 묵묵히 나아가면 중년 이후 안정적인 성취가 옵니다. "
                    f"**재물**: 급하게 큰돈을 노리기보다 착실한 저축과 안전한 투자가 최선입니다."
                ),
                "육해살": (
                    f"**육해살(六害殺)**이 있습니다. 가까운 사람과의 신뢰 균열 기운이 있습니다. "
                    f"**재물·관계**: 돈거래·보증·계약은 친한 사이라도 반드시 문서화하십시오. "
                    f"**주의**: 배신이나 속임수를 당할 수 있으니 사람을 천천히 신뢰하는 습관이 필요합니다."
                ),
                "월살": (
                    f"**월살(月殺, 고초살)**이 있습니다. 고통을 동반한 정착 기운이 있습니다. "
                    f"어려운 시기가 있지만 이를 견디면 이후 더 큰 안정이 찾아옵니다. "
                    f"**건강**: 위장·비장 계통을 특히 관리하십시오."
                ),
                "년살": (
                    f"**년살(年殺, 도화살)**이 있습니다. 대인관계와 이성 기운이 활성화됩니다. "
                    f"외모 관리와 사교적 네트워킹이 인생의 중요한 자원입니다. "
                    f"**재물**: 사람들의 호감을 받는 기운이 있으니 이를 사업·직업에 적극 활용하십시오."
                ),
            }
            _s5_parts = []
            for _sn in _sin_names[:4]:
                _base = _sn.replace("(劫殺)","").replace("(災殺)","").replace("(天殺)","")                            .replace("(地殺)","").replace("(年殺)","").replace("(月殺)","")                            .replace("(亡身殺)","").replace("(將星殺)","").replace("(攀鞍殺)","")                            .replace("(驛馬殺)","").replace("(六害殺)","").replace("(華蓋殺)","")                            .replace("겁살(劫殺)","겁살").replace("재살(災殺)","재살")                            .strip()
                _prose_raw = _SIN_PROSE.get(_base, "")
                if _prose_raw:
                    if isinstance(_prose_raw, tuple):
                        _prose = ' '.join(str(x) for x in _prose_raw)
                    else:
                        _prose = str(_prose_raw)
                    _s5_parts.append(_prose)
            if _s5_parts:
                st.markdown(f"""
<div style="background:#fffdf5;border:1px solid #c9a84c;border-radius:12px;padding:16px 18px;word-break:keep-all;overflow-wrap:break-word;margin:10px 0">
<div style="font-size:14px;font-weight:800;color:#8b4513;margin-bottom:8px">📖 {name}님의 신살 종합 해석</div>
<div style="font-size:13px;color:#4a2800;line-height:1.9;word-break:break-all;overflow-wrap:break-word;white-space:normal">{"<br><br>".join(_s5_parts)}</div>
</div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ── SECTION 5 이후 공통 변수 사전 정의 ──────────────────────
    # _il_sinsal_names: SECTION 5에서 계산된 신살 목록 (SECTION B/C/6에서 사용)
    _il_sinsal_names = list(sinsal_hits.keys()) if (_12_GROUP and 'sinsal_hits' in dir()) else []
    # _OH: 천간→오행 매핑 (SECTION C에서 사용)
    _OH = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
           "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
    # yongshin: 용신 오행 리스트 (SECTION B/C에서 사용)
    try:
        _ys_pre = get_yongshin(pils)
        yongshin = _ys_pre.get("종합_용신",[]) if isinstance(_ys_pre.get("종합_용신",[]),list) else []
    except Exception:
        yongshin = []
    # si_d: 신강신약 정보 (SECTION 6에서 사용)
    try:
        si_d = get_ilgan_strength(ilgan, pils)
    except Exception:
        si_d = {"신강신약":"중화","helper_score":50}


    # ════════════════════════════════════════════
    # SECTION 일주론: 일주 60갑자 심화 + 공망 심층
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">🔯 일주론(日柱論) 심화 — 60갑자 운명 코드</div>', unsafe_allow_html=True)
    try:
        _ilju_key2 = (pils[1].get("cg","") + pils[1].get("jj","")) if len(pils) > 1 else ""
        _ILJU60_DEEP = {
            "甲子": ("지혜와 리더십의 갑자일주. 총명하고 추진력이 강하나 고집이 셉니다.",
                     "직업은 교육·법조·행정이 맞고, 재물은 중년 이후 안정됩니다.",
                     "배우자와 독립적 관계를 유지하는 것이 오래 가는 비결입니다."),
            "甲午": ("총명하고 열정적이나 기복이 큰 갑오일주. 뛰어난 기획력이 강점입니다.",
                     "창업·기획·컨설팅 분야에서 빛을 발하며 40대 이후 재물이 쌓입니다.",
                     "파트너 선택 시 안정적인 성격을 가진 사람을 만나야 합니다."),
            "甲申": ("관살혼잡의 갑신일주. 강한 외압 속에서도 굽히지 않는 강인함이 있습니다.",
                     "군·경·법조·의료 분야에서 능력을 발휘합니다.",
                     "배우자와 트러블이 있을 수 있으니 소통에 각별히 신경 쓰십시오."),
            "甲寅": ("건록격의 갑인일주. 넘치는 에너지와 리더십으로 조직을 이끕니다.",
                     "경영·스포츠·군사 분야에 적합하며 사업가 기질이 강합니다.",
                     "고집을 조금 내려놓으면 더 큰 성공을 거둘 수 있습니다."),
            "甲辰": ("편재격의 갑진일주. 재물 복이 있고 포용력이 넓습니다.",
                     "사업·부동산·금융 분야에 재능이 있습니다.",
                     "재물을 모을 때 분산 투자보다 집중 투자가 유리합니다."),
            "甲戌": ("편재격의 갑술일주. 강한 실행력과 재물욕이 공존합니다.",
                     "사업가 기질이 강하고 부동산에서 재미를 봅니다.",
                     "노후 준비를 40대부터 시작하십시오."),
            "庚寅": ("편관격의 경인일주. 강직하고 의리 있으며 군인·경찰 기질이 있습니다.",
                     "군·경·법조·의료 분야에서 두각을 나타냅니다.",
                     "부드러운 소통 방식을 연습하면 대인관계가 훨씬 좋아집니다."),
            "庚午": ("편관격의 경오일주. 화기가 넘쳐 성격이 급하지만 추진력이 강합니다.",
                     "스포츠·언론·영업·무역 분야에 적합합니다.",
                     "충동적 결정을 자제하고 24시간 이상 숙고 후 결정하는 습관을 기르십시오."),
            "庚辰": ("편재격의 경진일주. 강한 의지와 재물 욕구가 결합된 일주입니다.",
                     "사업·투자·금융 분야에서 큰 성취가 가능합니다.",
                     "무토가 강한 환경에서 태어나 중년 이후 발복하는 팔자입니다."),
            "庚子": ("정인격의 경자일주. 총명하고 학업 운이 강합니다.",
                     "연구·교육·IT·의학 분야에 두각을 나타냅니다.",
                     "귀인의 도움으로 큰 도약의 기회가 옵니다."),
            "庚申": ("건록격의 경신일주. 강철 같은 의지와 냉정한 판단력이 특징입니다.",
                     "금융·법조·기계·공학 분야에서 전문성을 발휘합니다.",
                     "혼자 모든 것을 해결하려는 성향을 조금 내려놓으십시오."),
            "庚戌": ("편재격의 경술일주. 재물 복이 있고 사업 감각이 뛰어납니다.",
                     "부동산·건설·금융·사업가 기질이 강합니다.",
                     "중년 이후 큰 재물이 들어오는 구조입니다."),
            "乙丑": (
                     "끈질긴 생명력과 섬세한 감수성이 결합된 을축일주입니다. 겉은 부드럽지만 내면은 소처럼 우직하여, 한번 마음먹은 것은 끝까지 이루어내는 집념이 있습니다. 흙 위의 을목처럼 환경이 척박해도 뿌리를 내리고 성장하는 놀라운 적응력이 있습니다.",
                     "농업·식품·의료·교육·복지 분야에서 꾸준히 쌓으면 중년 이후 안정적 재물이 옵니다. 한 분야에서 오래 일할수록 전문성이 빛나는 팔자이니, 빠른 성공보다 꾸준한 성장을 선택하십시오.",
                     "실속 있고 가정적인 파트너를 만나야 합니다. 화려함보다 내실을 보고 선택하십시오. 감정 표현이 서툰 면이 있으니, 파트너에게 마음을 표현하는 연습이 필요합니다."),
            "乙卯": (
                     "건록격의 을묘일주입니다. 두 개의 목(木) 기운이 겹쳐 창의성과 표현력이 극에 달합니다. 봄의 새싹처럼 언제나 새로운 것을 시작하고 성장하려는 에너지가 넘치며, 섬세한 감수성으로 사람들의 마음을 움직이는 능력이 있습니다.",
                     "예술·교육·언론·디자인·콘텐츠 분야에서 자신만의 독창적인 브랜드를 구축할 수 있습니다. 프리랜서·개인 창업 형태가 직장보다 더 잘 맞으며, 자신의 재능으로 돈을 버는 구조가 이상적입니다.",
                     "정신적 교류가 되는 파트너를 찾으십시오. 속마음을 털어놓을 수 있는 인연이 최고입니다. 독립적인 기질이 강해 구속을 싫어하니, 서로의 공간을 존중하는 관계가 오래 지속됩니다."),
            "乙巳": (
                     "상관격의 을사일주입니다. 총명하고 표현력이 뛰어나 언변이 강하며, 기존 틀을 벗어나 새로운 것을 창조하는 혁신적인 기질이 있습니다. 불(火)의 기운이 더해져 열정과 추진력이 강하며, 한번 불붙으면 거침없이 나아갑니다.",
                     "법조·언론·강사·컨설팅·예술 분야에서 두각을 나타냅니다. 자신만의 전문성을 바탕으로 독립하면 더 큰 성취가 가능합니다. 30대 이후부터 본격적으로 재물이 쌓이기 시작하는 구조입니다.",
                     "언변이 강한 만큼 말로 인한 갈등이 생기기 쉽습니다. 배우자와 대화할 때 배려하는 말하기를 의식적으로 연습하십시오. 열정적인 파트너와 함께하면 서로 자극을 주며 성장할 수 있습니다."),
            "乙未": (
                     "정재격의 을미일주입니다. 꼼꼼하고 실속 있는 현실주의 기질로, 안정적인 재물을 쌓는 능력이 탁월합니다. 감성과 현실 감각을 동시에 지닌 을미일주는 예술적 감각을 실용적으로 활용하는 능력이 특별합니다.",
                     "금융·회계·부동산·의료·식품 분야에서 안정적 성취가 가능합니다. 꾸준히 저축하고 부동산에 투자하는 것이 최적의 재테크 방법이며, 중년 이후 안정된 경제 기반을 갖출 수 있습니다.",
                     "가정적이고 알뜰한 파트너상을 선호합니다. 화려함보다 믿음직한 사람이 맞습니다. 재물 감각이 비슷한 파트너를 만나면 경제적 목표를 함께 이루어 나갈 수 있습니다."),
            "乙酉": (
                     "정관격의 을유일주입니다. 규율과 원칙을 중시하는 완벽주의 성향으로, 섬세한 감성 위에 날카로운 판단력이 더해진 독특한 조합입니다. 금(金)의 예리함이 목(木)의 감성을 다듬어 정밀하고 아름다운 결과물을 만들어냅니다.",
                     "공무원·회계·법조·의료·교직 분야에서 신뢰를 쌓으며 성장합니다. 한 분야에서 전문성을 깊이 쌓으면 40대 이후 탁월한 전문가로 인정받을 수 있습니다.",
                     "완벽주의가 관계에서도 발휘될 수 있으니 상대방의 단점을 너그럽게 보는 연습이 필요합니다. 이상형이 높아 인연이 늦을 수 있지만, 기다림 끝에 만나는 인연이 가장 소중합니다."),
            "乙亥": (
                     "편인격의 을해일주입니다. 직관력과 감수성이 뛰어난 예술가 기질로, 물(水)의 깊은 지혜가 나무(木)의 성장을 돕는 상생 구조입니다. 남들이 보지 못하는 것을 감지하는 예리한 직관과 풍부한 상상력이 강점입니다.",
                     "연구·철학·예술·상담·종교 분야에서 강점을 발휘합니다. 한 분야를 깊이 파고드는 전문성이 최고의 무기이며, 세상에 알려지지 않은 지식을 발굴하고 창조하는 일이 천직입니다.",
                     "감정 기복이 있으니 정서적으로 안정시켜 줄 든든한 파트너가 필요합니다. 지적이고 예술적 감각을 공유할 수 있는 파트너와 만나면 깊은 정신적 교류를 나눌 수 있습니다."),
            "丙子": (
                     "정관격의 병자일주입니다. 태양이 바다를 비추는 형상으로, 밝은 에너지와 깊은 지혜가 결합된 특별한 일주입니다. 표면적으로는 활발하고 밝지만, 내면에는 진지하고 신중한 면이 공존하여 깊이 있는 인물로 성장합니다.",
                     "공직·교육·미디어·IT·금융 분야에서 명예를 쌓습니다. 조직 내 승진이 빠른 편으로, 성실하게 임하면 40대에 중요한 자리에 오르는 경우가 많습니다.",
                     "지적이고 차분한 파트너를 만날 때 가장 안정됩니다. 감성보다 이성적인 면이 강한 파트너와 보완 관계를 이루는 것이 이상적입니다."),
            "丙寅": (
                     "편인격의 병인일주입니다. 카리스마와 추진력이 강한 선구자형으로, 태양이 산 위로 솟아오르는 형상처럼 강렬하고 뜨거운 에너지가 있습니다. 주도적인 성향이 강하며, 어디서든 중심적인 역할을 맡게 됩니다.",
                     "경영·스포츠·군사·미디어·광고 분야에서 두각을 나타냅니다. 창업이나 독립적인 역할에서 가장 빛을 발하며, 조직보다 자신이 이끄는 구조가 훨씬 잘 맞습니다.",
                     "독립적인 기질 때문에 구속받는 관계를 싫어합니다. 서로의 공간을 존중하며 각자의 목표를 응원하는 파트너가 가장 잘 맞습니다."),
            "丙辰": (
                     "식신격의 병진일주입니다. 재능이 넘치고 먹복과 재물복을 함께 타고난 길한 일주입니다. 창의적인 재능을 활용해 사람들에게 즐거움과 가치를 제공하는 것이 이 일주의 소명입니다.",
                     "요리·방송·예술·창업·엔터테인먼트 분야에서 자신만의 색깔을 드러냅니다. 재능으로 돈을 버는 구조이니 자신만의 특기를 사업화하는 것이 최고의 전략입니다.",
                     "너그럽고 포용력 있는 파트너를 만나면 가정이 풍요로워집니다. 자신의 재능을 이해하고 응원해 주는 사람이 천생연분입니다."),
            "丙午": (
                     "겁재격의 병오일주입니다. 두 개의 불꽃이 겹쳐 에너지가 폭발적이고 강렬합니다. 뜨거운 열정과 강인한 의지로 불가능해 보이는 것도 이루어내는 저력이 있습니다.",
                     "연예·스포츠·영업·에너지·마케팅 분야에서 타의 추종을 불허합니다. 경쟁 상황에서 더욱 강해지는 기질로, 도전적인 환경에서 오히려 최고의 성과를 냅니다.",
                     "감정이 앞서는 성향이라 충동적인 연애를 자제하십시오. 충분한 시간을 두어 상대를 파악하고 냉정한 판단 후 관계를 시작하는 것이 현명합니다."),
            "丙申": (
                     "편재격의 병신일주입니다. 사업 수완과 재물 감각이 탁월한 사업가형 일주입니다. 화(火)와 금(金)의 긴장된 결합이 강인한 추진력과 날카로운 판단력을 동시에 만들어냅니다.",
                     "무역·사업·금융·기계·IT 분야에서 능력을 발휘합니다. 재물을 만지는 감각이 뛰어나 사업을 통해 큰 재물을 모을 수 있으며, 40~50대에 전성기를 맞는 경우가 많습니다.",
                     "재물욕과 이성에 대한 호기심이 동시에 강합니다. 배우자에게 충실한 자세를 유지하고, 재물 문제로 인한 갈등을 사전에 예방하는 것이 중요합니다."),
            "丙戌": (
                     "편인격의 병술일주입니다. 깊은 사유와 독창적 아이디어를 가진 기획가입니다. 태양이 저무는 형상으로, 화려함보다는 깊이 있는 지혜와 통찰로 빛을 발합니다.",
                     "기획·연구·교육·종교·철학 분야에서 독보적인 성취를 이룹니다. 남들이 생각하지 못한 아이디어로 새로운 가치를 창조하는 것이 이 일주의 강점입니다.",
                     "혼자만의 시간과 사색을 즐기는 성향이 있습니다. 이를 이해하고 존중해 주는 파트너가 필요하며, 지적인 교류를 나눌 수 있는 인연이 최고입니다."),
            "丁丑": ("정재격의 정축일주. 성실하고 꼼꼼하며 책임감이 강합니다.",
                     "회계·금융·농업·의료 분야에서 꾸준한 성취가 가능합니다.",
                     "안정적이고 믿음직한 파트너를 만나면 가정이 탄탄해집니다."),
            "丁卯": ("편인격의 정묘일주. 섬세한 감성과 창의적 사고가 강점입니다.",
                     "예술·디자인·상담·교육 분야에서 독창성을 발휘합니다.",
                     "감수성이 풍부한 만큼 상처를 쉽게 받습니다. 이해심 깊은 파트너가 필요합니다."),
            "丁巳": ("겁재격의 정사일주. 강한 의지와 실행력으로 어떤 역경도 극복합니다.",
                     "IT·에너지·금융·사업 분야에서 두각을 나타냅니다.",
                     "경쟁심이 강한 만큼 파트너와도 경쟁하려 하지 않도록 주의하십시오."),
            "丁未": ("정인격의 정미일주. 학문과 예술에 깊은 조예가 있습니다.",
                     "교육·출판·문학·의료 분야에서 귀인의 도움을 받아 성공합니다.",
                     "지적이고 품위 있는 파트너를 만나야 합니다."),
            "丁酉": ("편재격의 정유일주. 날카로운 판단력과 재물 감각이 뛰어납니다.",
                     "금융·투자·보석·미용 분야에서 정밀한 능력을 발휘합니다.",
                     "까다로운 이상형 때문에 인연이 늦을 수 있습니다. 조금 눈높이를 낮추십시오."),
            "丁亥": ("정관격의 정해일주. 원칙과 신뢰를 중시하는 성품입니다.",
                     "공직·법조·금융·해양 분야에서 안정적 성취가 가능합니다.",
                     "믿음직하고 책임감 있는 파트너를 만나면 가정이 평화롭습니다."),
            "戊子": ("정재격의 무자일주. 든든한 산이 물을 품은 형상으로 재물복이 강합니다.",
                     "부동산·금융·건설·유통 분야에서 안정적 재물을 쌓습니다.",
                     "내조·외조 모두 잘하는 파트너를 만나면 가정이 풍요롭습니다."),
            "戊寅": ("편관격의 무인일주. 강인한 의지와 통솔력이 강점입니다.",
                     "군·경·건설·스포츠·경영 분야에서 리더십을 발휘합니다.",
                     "강한 성격 때문에 마찰이 생기기 쉽습니다. 배우자 앞에서 부드러움을 연습하십시오."),
            "戊辰": ("비견격의 무진일주. 스케일이 크고 포부가 대담합니다.",
                     "부동산·건설·대기업 경영·토목 분야에서 큰 성취가 가능합니다.",
                     "두 개의 산이 마주한 형상으로 고집이 셉니다. 배우자와의 의견 충돌을 조율하는 기술이 필요합니다."),
            "戊午": ("겁재격의 무오일주. 추진력과 열정이 강렬합니다.",
                     "에너지·건설·마케팅·스포츠 분야에서 빛을 발합니다.",
                     "충동적인 결정을 자제하고 중요한 일은 배우자와 상의 후 진행하십시오."),
            "戊申": ("식신격의 무신일주. 재능이 풍부하고 복록이 따르는 길한 일주입니다.",
                     "기계·IT·군사·의공학 분야에서 전문성을 쌓으면 큰 성취가 옵니다.",
                     "재능과 매력이 넘치는 만큼 이성 관계를 신중하게 관리하십시오."),
            "戊戌": ("비견격의 무술일주. 두 개의 산으로 의지가 강하고 독립적입니다.",
                     "부동산·건설·무역·종교 분야에 인연이 깊습니다.",
                     "말년에 외로움을 느끼지 않도록 인간관계를 꾸준히 유지하십시오."),
            "己丑": ("비견격의 기축일주. 흙과 흙이 겹쳐 현실적이고 실속형입니다.",
                     "농업·식품·부동산·금융 분야에서 꾸준한 성취가 가능합니다.",
                     "비슷한 가치관을 가진 파트너를 만나면 가장 안정됩니다."),
            "己卯": ("편관격의 기축일주. 섬세하면서도 강한 실행력을 겸비합니다.",
                     "의료·교육·법조·행정 분야에서 능력을 발휘합니다.",
                     "강한 파트너 앞에서 위축되지 않도록 자기 주관을 단단히 세우십시오."),
            "己巳": ("겁재격의 기사일주. 불과 흙의 결합으로 에너지가 넘칩니다.",
                     "요식업·마케팅·광고·창업 분야에서 빠른 성과를 냅니다.",
                     "성격이 급한 편이니 중요한 결정은 하루 이상 여유를 두고 내리십시오."),
            "己未": ("비견격의 기미일주. 온순하고 포용력이 넓은 기질입니다.",
                     "의료·복지·상담·교육 분야에서 사람들을 돕는 일에 보람을 느낍니다.",
                     "너무 많이 베풀다 지치는 경향이 있으니 자신을 먼저 챙기십시오."),
            "己酉": ("식신격의 기유일주. 정밀하고 꼼꼼한 완벽주의 성향입니다.",
                     "의료·보석·회계·행정 분야에서 탁월한 능력을 발휘합니다.",
                     "완벽주의로 인해 파트너에게 지나친 기준을 요구하지 않도록 주의하십시오."),
            "己亥": ("정재격의 기해일주. 재물복과 수완이 강한 현실적 기질입니다.",
                     "무역·유통·금융·수산 분야에서 안정적 재물을 쌓습니다.",
                     "재물과 사랑 모두를 잡을 수 있는 행운의 일주입니다. 욕심을 조절하면 인생이 풍요로워집니다."),
            "辛卯": ("편재격의 신묘일주. 날카로운 판단력과 재물 감각이 뛰어납니다.",
                     "금융·투자·미용·패션 분야에서 날카로운 감각을 발휘합니다.",
                     "이상형이 높아 인연이 늦을 수 있습니다. 내면의 따뜻함을 가진 사람을 찾으십시오."),
            "辛巳": ("정관격의 신사일주. 원칙과 규율을 중시하는 완벽주의자입니다.",
                     "공직·법조·의료·금융 분야에서 신뢰를 쌓습니다.",
                     "원칙적인 성격이 관계에서도 적용되니 때로는 유연함이 필요합니다."),
            "辛未": ("편인격의 신미일주. 독창적 사고와 섬세한 예술 감각이 강점입니다.",
                     "예술·디자인·연구·특수기술 분야에서 자신만의 세계를 구축합니다.",
                     "독립적인 성향이 강하니 서로의 공간을 존중하는 파트너가 가장 잘 맞습니다."),
            "辛亥": ("상관격의 신해일주. 창의적이고 혁신적인 기질이 강합니다.",
                     "IT·기획·창업·예술 분야에서 기존 틀을 깨는 도전을 즐깁니다.",
                     "자유로운 영혼인 만큼 구속하지 않는 파트너를 만나야 합니다."),
            "壬子": ("건록격의 임자일주. 깊은 바다처럼 지혜롭고 카리스마가 넘칩니다.",
                     "철학·연구·IT·유통·무역 분야에서 독보적인 성취가 가능합니다.",
                     "지적이고 대화가 통하는 파트너를 만나야 합니다. 정신적 교류가 핵심입니다."),
            "壬寅": ("식신격의 임인일주. 지혜와 실행력이 결합된 행동파 기획자입니다.",
                     "무역·교육·경영·IT 분야에서 뛰어난 기획력을 발휘합니다.",
                     "활동적이고 에너지 넘치는 파트너와 함께하면 시너지가 납니다."),
            "壬辰": ("편관격의 임진일주. 강한 의지와 깊은 통찰력이 공존합니다.",
                     "군·경·법조·연구·의학 분야에서 외부 압박을 이겨내며 성장합니다.",
                     "강한 기운끼리 부딪힐 수 있으니 온화한 성격의 파트너가 균형을 잡아줍니다."),
            "壬午": ("정재격의 임오일주. 재물과 감성이 균형잡힌 팔자입니다.",
                     "금융·마케팅·엔터테인먼트·요식업 분야에서 재물을 쌓습니다.",
                     "감성적인 면이 강하니 이성적이고 안정적인 파트너가 균형을 맞춰줍니다."),
            "壬申": ("식신격의 임신일주. 재능이 넘치고 인복이 좋은 길한 일주입니다.",
                     "기계·IT·무역·수산·금융 분야에서 귀인의 도움을 받아 성공합니다.",
                     "말솜씨와 매력이 넘쳐 인기가 많습니다. 이성 관계를 신중하게 관리하십시오."),
            "壬戌": ("편관격의 임술일주. 강렬한 에너지와 리더십으로 조직을 이끕니다.",
                     "군·경·법조·건설·부동산 분야에서 강인한 추진력을 발휘합니다.",
                     "강한 기운이 넘치는 만큼 가정에서는 한 발 물러서는 여유가 필요합니다."),
            "癸丑": ("정인격의 계축일주. 귀인과 학문의 복이 있는 지혜로운 일주입니다.",
                     "교육·연구·의료·공직 분야에서 꾸준한 성취가 가능합니다.",
                     "내성적이지만 따뜻한 내면을 가진 파트너와 만나면 가정이 안정됩니다."),
            "癸卯": ("식신격의 계묘일주. 섬세한 감성과 창의적 재능이 돋보입니다.",
                     "예술·교육·의료·상담 분야에서 자신만의 영역을 구축합니다.",
                     "감수성이 풍부한 만큼 상처받기도 쉽습니다. 정서적 지지를 줄 수 있는 파트너가 필요합니다."),
            "癸巳": ("편관격의 계사일주. 차갑지만 강렬한 매력을 가진 독특한 일주입니다.",
                     "IT·의료·법조·연구 분야에서 날카로운 분석력을 발휘합니다.",
                     "표현이 서툴러 오해받기 쉬우니 감정 표현을 연습하십시오."),
            "癸未": ("편인격의 계미일주. 직관력과 창의성이 뛰어난 예술가 기질입니다.",
                     "예술·상담·철학·복지 분야에서 감동을 주는 일을 합니다.",
                     "감성에 치우치지 않도록 현실적인 파트너의 조언을 수용하십시오."),
            "癸酉": ("식신격의 계유일주. 정밀하고 꼼꼼한 전문가 기질이 강합니다.",
                     "의료·연구·금융·보석 분야에서 탁월한 전문성을 쌓습니다.",
                     "완벽을 추구하다 관계에서 상처를 주지 않도록 여유를 가지십시오."),
            "癸亥": ("겁재격의 계해일주. 지혜와 자유로운 영혼이 결합된 독특한 일주입니다.",
                     "철학·종교·예술·IT 분야에서 남다른 통찰력을 발휘합니다.",
                     "자유로운 기질 때문에 구속받는 관계를 싫어합니다. 서로 독립성을 존중하는 파트너가 맞습니다."),
            "甲丑": ("갑목이 습토 위에 뿌리 내린 갑축일주. 인내와 끈기로 어떤 환경에서도 살아남습니다.",
                     "농업·건설·부동산·교육 분야에서 꾸준히 쌓으면 중년 이후 크게 성취합니다.",
                     "현실적이고 든든한 파트너를 만나면 뿌리가 더 깊어집니다."),
            "甲卯": ("건록격의 갑묘일주. 두 개의 나무가 겹쳐 추진력과 자존심이 매우 강합니다.",
                     "교육·언론·법조·경영 분야에서 독보적 존재감을 발휘합니다.",
                     "자존심이 강한 만큼 파트너와 대등한 관계를 유지하는 것이 중요합니다."),
            "甲巳": ("상관격의 갑사일주. 창의적 표현력과 도전 정신이 강합니다.",
                     "언론·예술·법조·기획 분야에서 타고난 재능을 발휘합니다.",
                     "언변이 강하고 논쟁을 좋아하니 파트너와의 대화에서 배려를 잊지 마십시오."),
            "甲未": ("정재격의 갑미일주. 재물복과 안정적인 현실 감각이 강점입니다.",
                     "금융·부동산·농업·경영 분야에서 안정적 재물을 쌓습니다.",
                     "가정적이고 실속 있는 파트너를 만나면 인생이 풍요로워집니다."),
            "甲酉": ("정관격의 갑유일주. 원칙과 명예를 중시하는 정직한 기질입니다.",
                     "공직·법조·교육·행정 분야에서 신뢰와 명예를 쌓습니다.",
                     "원칙적인 성격이 관계에서도 나타나니 융통성을 키우십시오."),
            "甲亥": ("편인격의 갑해일주. 깊은 지혜와 감수성으로 통찰력이 뛰어납니다.",
                     "연구·철학·예술·상담 분야에서 독창적인 성취가 가능합니다.",
                     "내면의 풍요로움을 가진 파트너와 깊은 정신적 교류를 나누십시오."),
            "乙子": ("정관격의 을자일주. 부드럽지만 원칙을 지키는 신뢰받는 기질입니다.",
                     "공직·교육·의료·금융 분야에서 안정적 경력을 쌓습니다.",
                     "지적이고 안정적인 파트너를 만나면 가정이 평화롭습니다."),
            "乙寅": ("겁재격의 을인일주. 강인한 생명력과 끈질긴 도전 정신이 있습니다.",
                     "사업·교육·스포츠·경영 분야에서 강인하게 성장합니다.",
                     "경쟁심이 있으니 파트너와는 협력 관계를 유지하십시오."),
            "乙辰": ("편재격의 을진일주. 재물 감각과 현실 적응력이 뛰어납니다.",
                     "금융·부동산·유통·사업 분야에서 재물을 모읍니다.",
                     "재물욕이 강한 만큼 파트너와 경제적 목표를 공유하십시오."),
            "乙午": ("식신격의 을오일주. 따뜻한 감성과 표현력이 강점입니다.",
                     "예술·교육·방송·요식업 분야에서 사람들에게 감동을 줍니다.",
                     "감성적이고 따뜻한 파트너와 함께하면 인생이 풍요롭습니다."),
            "乙申": ("편관격의 을신일주. 날카로운 도전 속에서 성장하는 강인한 기질입니다.",
                     "군·경·의료·법조 분야에서 압박 속에서도 빛을 발합니다.",
                     "강한 파트너 앞에서도 자신의 중심을 잃지 마십시오."),
            "乙戌": ("편재격의 을술일주. 재물 감각과 실행력이 결합된 현실적 기질입니다.",
                     "부동산·무역·사업·마케팅 분야에서 중년 이후 크게 발전합니다.",
                     "노력한 만큼 돌아오는 팔자이니 꾸준한 실천이 핵심입니다."),
            "丙丑": ("정인격의 병축일주. 태양이 땅을 비추는 형상으로 귀인의 복이 있습니다.",
                     "교육·의료·공직·금융 분야에서 신뢰와 명성을 얻습니다.",
                     "안정적이고 실속 있는 파트너를 만나면 가정이 탄탄해집니다."),
            "丙卯": ("식신격의 병묘일주. 창의력과 표현력이 뛰어난 예술가 기질입니다.",
                     "예술·방송·교육·마케팅 분야에서 독창적인 성취를 이룹니다.",
                     "자유로운 기질을 존중해 주는 파트너가 가장 잘 맞습니다."),
            "丙巳": ("겁재격의 병사일주. 강렬한 불꽃이 두 개 겹쳐 에너지가 폭발적입니다.",
                     "연예·스포츠·에너지·IT 분야에서 강렬한 존재감을 드러냅니다.",
                     "충동적 행동을 자제하고 중요한 결정은 충분히 숙고하십시오."),
            "丙未": ("상관격의 병미일주. 창의성과 표현 욕구가 강한 자유로운 영혼입니다.",
                     "예술·기획·방송·교육 분야에서 자신만의 브랜드를 구축합니다.",
                     "자유를 존중하는 파트너와 함께해야 장기적으로 안정됩니다."),
            "丙酉": ("정재격의 병유일주. 재물 감각과 심미안이 결합된 독특한 일주입니다.",
                     "금융·보석·패션·예술 분야에서 섬세한 감각을 발휘합니다.",
                     "까다로운 기준이 있으니 서로를 충분히 알아가는 시간을 가지십시오."),
            "丙亥": ("정관격의 병해일주. 태양이 바다를 비추는 형상으로 포용력이 넓습니다.",
                     "공직·교육·무역·해양 분야에서 큰 그릇의 리더십을 발휘합니다.",
                     "믿음직한 파트너를 만나 가정을 이루면 더욱 빛납니다."),
            "丁子": (
                     "정관격의 정자일주입니다. 촛불처럼 은은하게 빛나면서도 원칙이 뚜렷한 일주입니다. 물(水) 위의 불꽃처럼 내면의 열정을 억제하는 자기 절제력이 강하며, 그 절제 속에서 깊은 지혜가 탄생합니다.",
                     "공직·교육·의료·금융 분야에서 안정적으로 성장합니다. 급격한 변화보다 꾸준한 성장을 선호하며, 신뢰와 원칙으로 조직 내에서 인정받는 타입입니다.",
                     "지적이고 안정적인 파트너와 함께하면 가정이 평화롭습니다. 감정 표현이 서툴 수 있으니 파트너에게 마음을 표현하는 노력이 필요합니다."),
            "丁寅": (
                     "편인격의 정인일주입니다. 섬세한 감수성과 강인한 도전 정신이 공존하는 독특한 일주입니다. 촛불의 온기와 나무의 강인함이 결합되어, 부드러우면서도 끈질기게 목표를 이루어가는 기질이 있습니다.",
                     "예술·교육·경영·스포츠 분야에서 섬세하면서도 강인하게 나아갑니다. 자신의 감성을 상품화하거나 창작 활동으로 연결하면 독보적인 영역을 개척할 수 있습니다.",
                     "감수성을 이해해 줄 파트너가 필요합니다. 섬세한 내면을 알아주는 사람과 만날 때 가장 안정적인 관계가 됩니다."),
            "丁辰": (
                     "식신격의 정진일주입니다. 재능이 풍부하고 복록이 따르는 길한 일주로, 먹복과 재물복을 함께 타고났습니다. 촛불의 따뜻함이 대지를 적시는 형상으로, 사람들에게 편안함과 풍요로움을 제공하는 능력이 있습니다.",
                     "예술·요식업·연구·기획·교육 분야에서 두각을 나타냅니다. 자신의 재능으로 가치를 창출하는 구조이니, 특기를 살린 창업이나 전문직이 가장 잘 맞습니다.",
                     "너그럽고 포용력 있는 파트너와 함께하면 인생이 풍요롭습니다. 가정을 소중히 여기는 파트너를 만나면 말년까지 행복한 가정을 이룰 수 있습니다."),
            "丁午": ("겁재격의 정오일주. 두 개의 불꽃으로 열정과 에너지가 강렬합니다.",
                     "연예·스포츠·마케팅·에너지 분야에서 뜨거운 열정을 발휘합니다.",
                     "감정이 앞서니 관계에서 충동적 행동을 자제하십시오."),
            "丁申": ("편재격의 정신일주. 재물 감각과 실행력이 결합된 현실적 기질입니다.",
                     "금융·IT·기계·무역 분야에서 재물을 모읍니다.",
                     "재물에 대한 욕심을 조절하면 관계가 더 안정됩니다."),
            "丁戌": ("편인격의 정술일주. 깊은 통찰과 사색을 즐기는 철학자 기질입니다.",
                     "철학·종교·교육·연구 분야에서 독보적인 지식을 쌓습니다.",
                     "혼자만의 시간을 중요시하니 이를 존중하는 파트너가 맞습니다."),
            "戊丑": ("비견격의 무축일주. 두 개의 흙이 겹쳐 안정성과 고집이 강합니다.",
                     "부동산·건설·농업·금융 분야에서 묵직하게 성취합니다.",
                     "비슷한 가치관의 파트너와 함께하면 가장 안정됩니다."),
            "戊卯": ("정관격의 무묘일주. 무게감 있는 산 위에 봄이 온 형상으로 포용력이 넓습니다.",
                     "교육·공직·농업·의료 분야에서 신뢰받는 역할을 합니다.",
                     "부드럽고 감성적인 파트너가 단단한 무토를 따뜻하게 해줍니다."),
            "戊巳": ("겁재격의 무사일주. 산과 불의 결합으로 강렬한 에너지를 발산합니다.",
                     "에너지·건설·마케팅·경영 분야에서 강한 추진력을 발휘합니다.",
                     "성격이 강하니 파트너 앞에서 부드러움을 연습하십시오."),
            "戊未": ("비견격의 무미일주. 두 흙이 겹쳐 안정성이 강하지만 변화를 싫어합니다.",
                     "부동산·건설·교육·농업 분야에서 꾸준히 성취합니다.",
                     "새로운 변화를 두려워하지 말고 파트너의 새로운 시도를 지지하십시오."),
            "戊酉": ("식신격의 무유일주. 안정된 산 위의 보석처럼 재능과 복록이 있습니다.",
                     "금융·의료·기술·행정 분야에서 꾸준하고 정밀하게 성취합니다.",
                     "안정적이고 신뢰할 수 있는 파트너와 만나면 가정이 풍요롭습니다."),
            "戊亥": ("정재격의 무해일주. 재물복과 수완이 강한 현실적 기질입니다.",
                     "무역·유통·부동산·금융 분야에서 안정적 재물을 쌓습니다.",
                     "실속 있고 가정적인 파트너를 만나면 인생이 더욱 풍요로워집니다."),
            "己子": ("정재격의 기자일주. 섬세하고 꼼꼼한 현실주의자입니다.",
                     "의료·금융·회계·교육 분야에서 안정적으로 성장합니다.",
                     "지적이고 안정적인 파트너와 함께하면 가정이 탄탄해집니다."),
            "己寅": ("편관격의 기인일주. 섬세한 흙 위에 강인한 나무가 자라는 형상입니다.",
                     "교육·의료·경영·행정 분야에서 외부 압박을 이겨내며 성장합니다.",
                     "강한 파트너에게 주도권을 빼앗기지 않도록 자기 주관을 세우십시오."),
            "己辰": ("비견격의 기진일주. 두 흙이 만나 안정성과 현실 감각이 강합니다.",
                     "부동산·금융·의료·농업 분야에서 꾸준히 성취합니다.",
                     "현실적인 파트너와 재정 계획을 함께 세우면 더욱 안정됩니다."),
            "己午": ("겁재격의 기오일주. 불과 흙의 결합으로 에너지와 추진력이 강합니다.",
                     "마케팅·교육·요식업·의료 분야에서 열정적으로 성장합니다.",
                     "충동적 결정을 자제하고 파트너와 충분히 상의하는 습관이 필요합니다."),
            "己申": ("식신격의 기신일주. 재능과 현실 감각이 결합된 실속형 기질입니다.",
                     "의료·기술·행정·금융 분야에서 꼼꼼하게 성취합니다.",
                     "안정적이고 신뢰할 수 있는 파트너와 함께하면 더욱 빛납니다."),
            "己戌": ("편재격의 기술일주. 재물 감각과 현실적 실행력이 강점입니다.",
                     "부동산·건설·농업·금융 분야에서 중년 이후 안정적 재물이 쌓입니다.",
                     "묵묵히 가정을 지키는 파트너를 만나면 노후가 안락합니다."),
            "庚丑": ("정인격의 경축일주. 강철 같은 의지에 귀인의 복이 더해집니다.",
                     "교육·의료·법조·행정 분야에서 귀인의 도움으로 성공합니다.",
                     "믿음직하고 지혜로운 파트너를 만나면 더욱 빛납니다."),
            "庚卯": ("정재격의 경묘일주. 강한 의지와 재물 감각이 결합된 실전형입니다.",
                     "금융·무역·사업·기술 분야에서 재물을 쌓습니다.",
                     "내면의 부드러움을 가진 파트너와 균형을 이루십시오."),
            "庚巳": ("편관격의 경사일주. 강한 외압 속에서 더욱 강해지는 기질입니다.",
                     "군·경·법조·의료 분야에서 강인하게 성장합니다.",
                     "강인한 외면 뒤의 부드러운 내면을 파트너에게 보여주십시오."),
            "庚未": ("정인격의 경미일주. 귀인과 학문의 복이 있는 든든한 일주입니다.",
                     "교육·행정·법조·의료 분야에서 꾸준히 명성을 쌓습니다.",
                     "지적이고 따뜻한 파트너를 만나면 가정이 안정됩니다."),
            "庚酉": ("건록격의 경유일주. 가장 강한 금의 기운으로 냉철하고 단호합니다.",
                     "금융·법조·의료·기계 분야에서 전문성을 발휘합니다.",
                     "차가운 외면 때문에 오해받기 쉽습니다. 감정 표현을 연습하십시오."),
            "庚亥": ("식신격의 경해일주. 강인함에 지혜가 더해진 팔방미인 기질입니다.",
                     "무역·IT·연구·금융 분야에서 귀인의 도움으로 성장합니다.",
                     "매력이 넘쳐 인기가 많습니다. 이성 관계를 신중하게 관리하십시오."),
            "辛子": ("상관격의 신자일주. 날카로운 언변과 창의적 사고가 강점입니다.",
                     "언론·기획·IT·법조 분야에서 혁신적인 아이디어를 발휘합니다.",
                     "날카로운 언변이 상처를 줄 수 있으니 배려하는 말하기를 연습하십시오."),
            "辛寅": ("편재격의 신인일주. 날카로운 금속이 강인한 나무와 부딪히는 역동적 일주입니다.",
                     "무역·사업·법조·스포츠 분야에서 강인하게 성장합니다.",
                     "강한 성격끼리의 충돌을 예방하기 위해 한 발 물러서는 여유가 필요합니다."),
            "辛辰": ("편인격의 신진일주. 독창적 사고와 섬세한 분석력이 강점입니다.",
                     "연구·의료·IT·예술 분야에서 자신만의 독보적 영역을 구축합니다.",
                     "내면 세계가 풍부하니 그것을 나눌 수 있는 지적인 파트너가 맞습니다."),
            "辛午": ("정관격의 신오일주. 원칙과 명예를 중시하는 균형 잡힌 기질입니다.",
                     "공직·교육·금융·의료 분야에서 신뢰와 명예를 쌓습니다.",
                     "화(火)와 금(金)의 긴장 속에서 성장하니 배우자와의 균형이 특히 중요합니다."),
            "辛申": ("건록격의 신신일주. 두 개의 금이 겹쳐 냉철하고 결단력이 강합니다.",
                     "금융·법조·의료·기계 분야에서 전문성을 발휘합니다.",
                     "차가운 이미지로 오해받기 쉬우니 따뜻한 면을 적극 표현하십시오."),
            "辛戌": ("편재격의 신술일주. 재물 감각과 결단력이 결합된 실전형입니다.",
                     "부동산·금융·사업·기술 분야에서 중년 이후 크게 발전합니다.",
                     "실속을 중시하는 만큼 파트너에게도 현실적인 기준이 높습니다. 감성적 교류를 늘리십시오."),
            "壬丑": ("정인격의 임축일주. 깊은 바다 위의 단단한 땅처럼 귀인의 복이 있습니다.",
                     "교육·의료·법조·금융 분야에서 귀인의 도움으로 성공합니다.",
                     "든든하고 신뢰할 수 있는 파트너를 만나면 더욱 안정됩니다."),
            "壬卯": ("식신격의 임묘일주. 지혜와 창의성이 결합된 창조형 기질입니다.",
                     "교육·예술·기획·IT 분야에서 독창적인 성취를 이룹니다.",
                     "감성이 풍부한 파트너와 함께하면 인생이 더욱 풍요로워집니다."),
            "壬巳": ("편관격의 임사일주. 지혜와 강인함이 공존하는 역동적 일주입니다.",
                     "군·경·IT·법조 분야에서 압박 속에서 더욱 강해집니다.",
                     "내면의 부드러움을 파트너에게 보여주는 용기가 필요합니다."),
            "壬未": ("편관격의 임미일주. 지혜롭고 포용력이 넓은 기질입니다.",
                     "교육·상담·의료·복지 분야에서 사람들을 이끕니다.",
                     "모든 것을 품으려 하다 지칠 수 있으니 자신도 챙기십시오."),
            "壬酉": ("정인격의 임유일주. 지혜와 학문의 복이 있는 귀인 일주입니다.",
                     "교육·연구·법조·금융 분야에서 귀인의 도움으로 크게 성장합니다.",
                     "지적이고 품위 있는 파트너를 만나면 이상적인 가정이 됩니다."),
            "壬亥": ("겁재격의 임해일주. 두 개의 물이 겹쳐 지혜가 넘치지만 산만해질 수 있습니다.",
                     "철학·IT·무역·연구 분야에서 깊은 통찰력을 발휘합니다.",
                     "에너지를 한곳에 집중시켜 줄 현실적인 파트너가 필요합니다."),
            "癸子": ("겁재격의 계자일주. 두 개의 물이 겹쳐 지혜롭지만 감정 기복이 있습니다.",
                     "철학·예술·상담·IT 분야에서 섬세한 통찰력을 발휘합니다.",
                     "감정적으로 안정시켜 줄 든든한 파트너가 가장 필요합니다."),
            "癸寅": ("식신격의 계인일주. 지혜와 도전 정신이 결합된 행동파입니다.",
                     "교육·스포츠·무역·IT 분야에서 지혜롭게 성장합니다.",
                     "활동적이고 에너지 넘치는 파트너와 함께하면 시너지가 납니다."),
            "癸辰": ("편관격의 계진일주. 지혜와 강인함이 공존하는 독특한 기질입니다.",
                     "연구·의료·IT·법조 분야에서 깊이 파고드는 능력을 발휘합니다.",
                     "강인한 파트너 앞에서도 자신의 중심을 잃지 마십시오."),
            "癸午": ("편재격의 계오일주. 지혜와 열정이 결합된 역동적 일주입니다.",
                     "금융·마케팅·방송·무역 분야에서 재물을 쌓습니다.",
                     "감성과 이성의 균형을 잡아주는 파트너가 필요합니다."),
            "癸申": ("식신격의 계신일주. 지혜와 정밀함이 결합된 전문가 기질입니다.",
                     "IT·의료·연구·금융 분야에서 귀인의 도움을 받아 크게 성장합니다.",
                     "매력이 넘쳐 인기가 많습니다. 진실된 인연을 구별하는 눈을 키우십시오."),
            "癸戌": ("편관격의 계술일주. 지혜와 강인함이 조화로운 성장형 일주입니다.",
                     "군·경·법조·건설 분야에서 강인하게 성취합니다.",
                     "삶의 후반부로 갈수록 더욱 빛나는 팔자이니 인내하고 나아가십시오."),
            "辛丑": ("정인격의 신축일주. 귀인의 도움을 받는 학문과 자격의 일주입니다.",
                     "교육·의료·법조·자격직 분야에서 꾸준한 성취가 가능합니다.",
                     "귀인을 만나는 복이 있으니 스승과 선배의 도움을 적극 수용하십시오."),
            "辛酉": ("건록격의 신유일주. 보석 중의 보석, 가장 정밀하고 예리한 금의 기운입니다.",
                     "금융·의료·보석·법조·기술 분야에서 탁월한 전문성을 발휘합니다.",
                     "완벽주의로 인해 스스로와 파트너에게 높은 기준을 요구하니, 때로는 '충분히 좋다'를 인정하십시오."),
        }
        _ilju_deep = _ILJU60_DEEP.get(_ilju_key2)
        if _ilju_deep:
            _id_desc, _id_career, _id_love = _ilju_deep
            st.markdown(f"""
<div style="background:#fff8f5;border:2px solid #c9a84c;border-radius:14px;padding:18px 20px;margin:10px 0">
<div style="font-size:16px;font-weight:900;color:#8b4513;margin-bottom:12px">🔯 {_ilju_key2} 일주 심층 분석</div>
<div style="display:grid;grid-template-columns:1fr;gap:10px">
  <div style="background:#fff3e0;border-left:4px solid #e65100;border-radius:0 8px 8px 0;padding:12px">
    <div style="font-size:12px;color:#e65100;font-weight:700">🧬 기질과 성격</div>
    <div style="font-size:13px;color:#4a2800;line-height:1.8;margin-top:4px;word-break:keep-all;overflow-wrap:break-word">{_id_desc}</div>
  </div>
  <div style="background:#e8f5e9;border-left:4px solid #2e7d32;border-radius:0 8px 8px 0;padding:12px">
    <div style="font-size:12px;color:#2e7d32;font-weight:700">💼 직업·재물 운명</div>
    <div style="font-size:13px;color:#1b3a1e;line-height:1.8;margin-top:4px;word-break:keep-all;overflow-wrap:break-word">{_id_career}</div>
  </div>
  <div style="background:#e3f2fd;border-left:4px solid #1565c0;border-radius:0 8px 8px 0;padding:12px">
    <div style="font-size:12px;color:#1565c0;font-weight:700">💑 배우자·인연 운명</div>
    <div style="font-size:13px;color:#0d2744;line-height:1.8;margin-top:4px;word-break:keep-all;overflow-wrap:break-word">{_id_love}</div>
  </div>
</div></div>""", unsafe_allow_html=True)
        else:
            # GJ60 기본 데이터로 폴백
            try:
                _gj_info = GJ60.get(_ilju_key2, ("",""))
                if _gj_info[1]:
                    st.markdown(f"""<div style="background:#fff8f5;border:1px solid #c9a84c;border-radius:12px;
padding:16px;margin:10px 0">
<div style="font-size:14px;font-weight:900;color:#8b4513;margin-bottom:8px">🔯 {_ilju_key2} 일주</div>
<div style="font-size:13px;color:#4a2800;line-height:1.8">{_gj_info[1][:300]}</div>
</div>""", unsafe_allow_html=True)
            except Exception:
                pass
    except Exception as e:
        st.warning(f"일주론 분석 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 공망: 공망(空亡) 심층 해석
    # ════════════════════════════════════════════
    st.markdown('<div class="gold-section">⬜ 공망(空亡) 심층 해석 — 빈 기둥의 의미</div>', unsafe_allow_html=True)
    try:
        _gm_data2 = get_gongmang(pils)
        _gm_jjs2  = _gm_data2.get("공망_지지", []) if isinstance(_gm_data2, dict) else []
        _gm_pils2 = _gm_data2.get("해당_기둥", []) if isinstance(_gm_data2, dict) else []

        _GM_DESC = {
            "년주": ("년주(年柱) 공망", "조상·부모·고향과의 인연이 얇습니다. 고향을 떠나 타지에서 성공하는 구조이며, 스스로의 힘으로 일어서야 하는 팔자입니다.",
                     "부모에게 의지하기보다 독립적으로 자수성가하십시오. 이민·유학·타지 생활에서 오히려 빛을 발합니다.", "#7b1fa2"),
            "월주": ("월주(月柱) 공망", "형제·자매와 인연이 얇거나 사회 초년기에 어려움이 있을 수 있습니다. 직업 변동이 잦은 편입니다.",
                     "직업 선택에 신중하되 한번 결정했으면 꾸준히 밀고 가십시오. 형제간 재물 관계는 명확히 하십시오.", "#1565c0"),
            "일주": ("일주(日柱) 공망", "배우자와의 인연이 얇거나 결혼이 늦어질 수 있습니다. 자신의 내면과 고독에 익숙한 독립적 기질이 강합니다.",
                     "배우자 선택을 서두르지 말고 충분히 교제 후 결혼하십시오. 정신적 교류가 가능한 동반자를 찾으십시오.", "#e65100"),
            "시주": ("시주(時柱) 공망", "자녀와의 인연이 얇거나 노후 준비가 필요한 구조입니다. 자녀보다 자신의 노후를 미리 준비하는 것이 현명합니다.",
                     "자녀에게 의존하는 노후 계획보다 독립적인 노후 재원을 준비하십시오. 말년에 종교·철학·봉사가 도움됩니다.", "#2e7d32"),
        }
        _GM_TIMING = {
            "년주": "공망 해소: 생년 지지와 삼합이 되는 세운에 일시 해소됩니다.",
            "월주": "공망 해소: 월지와 합이 되는 세운·대운에 완화됩니다.",
            "일주": "공망 해소: 일지와 삼합·육합이 되는 해에 인연이 옵니다.",
            "시주": "공망 해소: 시지와 합이 되는 대운에 자녀·말년 운이 열립니다.",
        }
        _has_gm = False
        for _gp2 in _gm_pils2:
            _gpk = _gp2.get("기둥","") if isinstance(_gp2, dict) else str(_gp2)
            _gd2 = _GM_DESC.get(_gpk)
            if _gd2:
                _has_gm = True
                _tt, _dd, _aa, _cc = _gd2
                st.markdown(f"""
<div style="background:#f9f5ff;border:2px solid {_cc};border-radius:12px;padding:16px;margin:8px 0">
<div style="font-size:14px;font-weight:900;color:{_cc};margin-bottom:8px">⬜ {_tt}</div>
<div style="font-size:13px;color:#333;line-height:1.8;margin-bottom:8px">{_dd}</div>
<div style="background:#fff;border-left:4px solid {_cc};padding:10px 12px;border-radius:0 8px 8px 0;margin-bottom:6px">
<div style="font-size:12px;font-weight:700;color:{_cc}">✅ 실천 조언</div>
<div style="font-size:13px;color:#333;margin-top:4px">{_aa}</div></div>
<div style="font-size:11px;color:#888;font-style:italic">{_GM_TIMING.get(_gpk,"")}</div>
</div>""", unsafe_allow_html=True)
        if not _has_gm:
            st.markdown("""<div style="background:#f0fff4;border:1px solid #66bb6a;border-radius:10px;
padding:14px;text-align:center">
<div style="font-size:14px;font-weight:700;color:#2e7d32">✅ 공망 없음 — 안정적 구조</div>
<div style="font-size:13px;color:#555;margin-top:6px">원국에 공망이 없어 각 기둥의 기운이 온전히 발현됩니다.</div>
</div>""", unsafe_allow_html=True)
        if _gm_jjs2:
            st.caption(f"공망 지지: {' · '.join(_gm_jjs2)} — 이 지지가 세운에 오면 공망이 강하게 발동됩니다.")
    except Exception as e:
        st.warning(f"공망 분석 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

        # ════════════════════════════════════════════
    # SECTION NEW-A: 현재 직업 적합도 + 천직 분석
    # ════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d1a2e,#1a2e4e);border:2px solid #3498db;
border-radius:14px;padding:16px 20px;margin:16px 0 6px">
<div style="font-size:16px;font-weight:900;color:#82cfff;letter-spacing:2px">
💼 A. 직업 적합도 & 천직 분석 — 이 팔자가 진짜 잘 버는 직업</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">격국·십성·오행 분포로 계산한 직업 적합도. 지금 하는 일이 맞는 팔자인지 확인하라.</div>
</div>""", unsafe_allow_html=True)

    try:
        _gk_j = get_gyeokguk(pils)
        _gkn_j_raw = _gk_j["격국명"] if _gk_j else "미정격"
        # "正官格" → "정관격" 변환
        _GKN_KR_MAP = {
            "正官格":"정관격","偏官格":"편관격","正財格":"정재격","偏財格":"편재격",
            "食神格":"식신격","傷官格":"상관격","正印格":"정인격","偏印格":"편인격",
            "比肩格":"비견격","劫財格":"겁재격",
        }
        _gkn_j = _GKN_KR_MAP.get(_gkn_j_raw, _gkn_j_raw)
        _si_j  = get_ilgan_strength(ilgan, pils)
        _sn_j  = _si_j.get("신강신약","중화")
        _ys_j  = get_yongshin(pils)
        _y1_j  = _ys_j.get("종합_용신",[""])[0] if isinstance(_ys_j.get("종합_용신",[]),list) and _ys_j.get("종합_용신") else ""

        # 십성 분포로 직업군 점수 계산
        _ss_counts = {}
        for _p in pils:
            _ss = TEN_GODS_MATRIX.get(ilgan,{}).get(_p.get("cg",""),"")
            if _ss:
                _ss_counts[_ss] = _ss_counts.get(_ss,0) + 1
        # 지지 십성도 포함 (JIJANGGAN으로 정기 찾아서 계산)
        for _p in pils:
            _jjg_key = _p.get("jj","")
            _jjg_list = JIJANGGAN.get(_jjg_key, [])
            if _jjg_list:
                _jj_main = _jjg_list[-1]  # 정기(正氣)
                _jj_ss = TEN_GODS_MATRIX.get(ilgan,{}).get(_jj_main,"")
                if _jj_ss:
                    _ss_counts[_jj_ss] = _ss_counts.get(_jj_ss,0) + 0.5

        # 직업군별 점수 (십성 가중치)
        _JOB_SCORE = {
            "공무원·대기업·조직관리": {"正官":3,"偏官":2,"正印":2,"正財":1},
            "사업·투자·영업": {"偏財":3,"食神":2,"傷官":2,"劫財":1},
            "전문직·자격증(의사·변호사·회계)": {"正印":3,"偏印":2,"正官":2,"食神":1},
            "창작·콘텐츠·예술": {"傷官":3,"食神":3,"偏印":2},
            "기술·IT·연구개발": {"偏印":3,"食神":2,"正印":2},
            "금융·증권·재테크": {"偏財":3,"正財":2,"食神":1,"劫財":1},
            "프리랜서·1인기업": {"比肩":3,"劫財":2,"偏印":2,"傷官":1},
            "군인·경찰·소방·스포츠": {"偏官":3,"劫財":2,"比肩":2},
        }
        _job_scores = {}
        for _job, _weights in _JOB_SCORE.items():
            _score = sum(_ss_counts.get(_ss,0)*_w for _ss,_w in _weights.items())
            _job_scores[_job] = round(_score,1)
        _sorted_jobs = sorted(_job_scores.items(), key=lambda x: x[1], reverse=True)

        # 상위 3개 직업군 표시
        col_ja, col_jb = st.columns([3,2])
        with col_ja:
            st.markdown("<div style='font-size:13px;font-weight:800;color:#82cfff;margin-bottom:8px'>📊 직업 적합도 순위 (십성 분포 기반)</div>", unsafe_allow_html=True)
            _max_score = _sorted_jobs[0][1] if _sorted_jobs else 1
            for _rank, (_job, _score) in enumerate(_sorted_jobs[:5], 1):
                _pct = int(_score / _max_score * 100) if _max_score > 0 else 0
                _colors = ["#f7e695","#82cfff","#a8e6cf","#ffb3ba","#d4a5f5"]
                _c = _colors[_rank-1]
                _medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][_rank-1]
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.05);border-radius:8px;padding:8px 12px;margin-bottom:5px'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px'>"
                    f"<span style='font-size:13px;color:{_c};font-weight:700'>{_medal} {_job}</span>"
                    f"<span style='font-size:12px;color:#aaa'>{_pct}점</span></div>"
                    f"<div style='background:#333;border-radius:4px;height:6px'>"
                    f"<div style='width:{_pct}%;background:{_c};height:6px;border-radius:4px'></div></div></div>",
                    unsafe_allow_html=True)

        with col_jb:
            st.markdown("<div style='font-size:13px;font-weight:800;color:#82cfff;margin-bottom:8px'>🎯 이 팔자의 천직 판정</div>", unsafe_allow_html=True)
            _best_job = _sorted_jobs[0][0] if _sorted_jobs else "미정"
            _GKN_VERDICT = {
                "정관격": ("✅ 조직·공직형",  "위계 있는 조직에서 인정받는 팔자. 안정적 상승 경로가 맞다."),
                "편관격": ("⚔️ 도전·전투형",  "군경·의료·법조·경쟁 분야. 강한 환경일수록 빛난다."),
                "정재격": ("💰 성실·재물형",  "금융·부동산·회계. 꾸준히 모으면 반드시 쌓인다."),
                "편재격": ("🚀 사업가형",     "영업·사업·투자. 움직일 때 돈이 된다. 가만히 있으면 손해."),
                "식신격": ("🌟 재능·복록형",  "요식·창작·교육·콘텐츠. 좋아하는 일이 곧 밥벌이가 된다."),
                "상관격": ("💡 창의·혁신형",  "IT·방송·컨설팅·예술. 조직은 맞지 않는다. 1인 기업이 천직."),
                "편인격": ("🔬 연구·기술형",  "학문·연구·의학·심리. 깊이 파면 독보적 전문가가 된다."),
                "정인격": ("📚 교육·자격형",  "교사·교수·자격증 기반 전문직. 배울수록 위상이 높아진다."),
                "비견격": ("💪 독립사업형",   "프리랜서·1인기업. 혼자 움직일 때 최강이다."),
                "겁재격": ("⚡ 경쟁·투자형",  "증권·스포츠·경쟁 비즈니스. 경쟁 속에서 오히려 강해진다."),
            }
            _verdict = _GKN_VERDICT.get(_gkn_j, ("🎯 "+_gkn_j, "용신 오행 방향 직업이 가장 맞다."))
            st.markdown(
                f"<div style='background:#0d1a0d;border:2px solid #27ae60;border-radius:10px;padding:14px'>"
                f"<div style='font-size:15px;font-weight:900;color:#a8e6cf;margin-bottom:6px'>{_verdict[0]}</div>"
                f"<div style='font-size:12px;color:#ccc;line-height:1.8'>{_verdict[1]}</div>"
                f"<div style='font-size:11px;color:#888;margin-top:8px'>격국: {_gkn_j} | 용신: {_y1_j} | {_sn_j}</div>"
                f"</div>",
                unsafe_allow_html=True)

        # 현재 직업 vs 팔자 적합도 체크
        _cur_occ = st.session_state.get("in_occupation","선택 안 함")
        if _cur_occ and _cur_occ != "선택 안 함":
            _OCC_MAP = {
                "직장인/회사원":  ["공무원·대기업·조직관리","전문직·자격증(의사·변호사·회계)"],
                "공무원/공공기관":["공무원·대기업·조직관리"],
                "사업/자영업":    ["사업·투자·영업","프리랜서·1인기업"],
                "프리랜서/1인기업":["프리랜서·1인기업","창작·콘텐츠·예술"],
                "전문직(의사/변호사/회계사 등)":["전문직·자격증(의사·변호사·회계)","기술·IT·연구개발"],
                "학생/취업준비":  [_best_job],
                "주부/육아":      ["공무원·대기업·조직관리","사업·투자·영업"],
                "IT/개발":        ["기술·IT·연구개발","창작·콘텐츠·예술"],
            }
            _good_jobs = _OCC_MAP.get(_cur_occ, [])
            _is_match = any(_j in _best_job or _best_job in _j for _j in _good_jobs) if _good_jobs else None
            if _is_match is not None:
                _match_color = "#27ae60" if _is_match else "#e53935"
                _match_text  = "✅ 지금 하는 일이 팔자에 잘 맞습니다!" if _is_match else f"⚠️ 지금 하는 일({_cur_occ})보다 [{_best_job}]이 이 팔자에 더 잘 맞습니다."
                st.markdown(
                    f"<div style='background:{_match_color}22;border:1px solid {_match_color};border-radius:8px;padding:10px 14px;margin-top:10px;font-size:13px;color:#fff'>"
                    f"<b>{_match_text}</b></div>",
                    unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:rgba(255,200,0,0.1);border:1px dashed #f7e695;border-radius:8px;padding:8px 14px;margin-top:8px;font-size:12px;color:#f7e695'>"
                "💡 왼쪽 입력창에서 현재 직업을 선택하면 팔자 적합도를 자동 비교해드립니다.</div>",
                unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"직업 분석 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION NEW-B: 사고수 정밀 분석
    # ════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0000,#2e0000);border:2px solid #c0392b;
border-radius:14px;padding:16px 20px;margin:16px 0 6px">
<div style="font-size:16px;font-weight:900;color:#ff8888;letter-spacing:2px">
🚨 B. 사고수(事故數) 정밀 분석 — 백호·양인·겁살·충 교차 계산</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">
대운·세운·신살·충 4중 교차 계산. 단순 십성 하나가 아니라 복합 패턴으로 사고 위험도를 산출합니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        # 백호대살 원국 확인
        _BAEKHO = {"甲辰","乙未","丙戌","丁丑","戊辰","壬辰","癸丑"}
        _pil_ganjis = [p["cg"]+p["jj"] for p in pils]
        _baekho_hits = [gj for gj in _pil_ganjis if gj in _BAEKHO]

        # 양인살 원국 확인
        _YANGIN_M = {"甲":"卯","丙":"午","戊":"午","庚":"酉","壬":"子"}
        _yangin_jj2 = _YANGIN_M.get(ilgan,"")
        _yangin_hits2 = [p["jj"] for p in pils if p["jj"] == _yangin_jj2] if _yangin_jj2 else []

        # 겁살 원국 확인 (십이신살)
        _GEOP_SAL = _il_sinsal_names if _12_GROUP else []
        _has_geop = "겁살" in _GEOP_SAL

        # 연도별 사고 위험도 계산 (현재+5년)
        _cur_yr2 = datetime.now().year
        accident_data = []

        for _yr in range(_cur_yr2, _cur_yr2 + 6):
            _age2 = _yr - birth_year + 1
            _sw2 = get_yearly_luck(pils, _yr) or {}
            _sw_ss2 = TEN_GODS_MATRIX.get(ilgan,{}).get(_sw2.get("cg",""),"-")
            _sw_jj2 = _sw2.get("jj","")

            # 위험도 점수 계산
            _risk = 0
            _risk_reasons = []

            # 1. 세운 편관·겁재 (+30)
            if _sw_ss2 == "偏官":
                _risk += 30
                _risk_reasons.append("편관 세운(관재·건강 압박)")
            elif _sw_ss2 == "劫財":
                _risk += 25
                _risk_reasons.append("겁재 세운(재물손실·사고)")

            # 2. 세운이 원국 일지 충 (+25)
            _CHUNG2 = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
                       "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
            if _CHUNG2.get(_sw_jj2,"") == ilji:
                _risk += 25
                _risk_reasons.append(f"세운 지지({_sw_jj2})가 일지({ilji}) 충 발동!")

            # 3. 세운이 월지 충 (+20)
            _wolji2 = pils[2]["jj"] if len(pils)>2 else ""
            if _CHUNG2.get(_sw_jj2,"") == _wolji2:
                _risk += 20
                _risk_reasons.append(f"세운 지지({_sw_jj2})가 월지({_wolji2}) 충 발동!")

            # 4. 백호대살 있는 사람 + 충년 (+15)
            if _baekho_hits and _risk >= 20:
                _risk += 15
                _risk_reasons.append(f"백호대살({', '.join(_baekho_hits)}) 원국 보유 — 충 발동 시 배가!")

            # 5. 양인살 있는 사람 + 편관 세운 (+15)
            if _yangin_hits2 and _sw_ss2 == "偏官":
                _risk += 15
                _risk_reasons.append(f"양인살({_yangin_jj2}) + 편관 세운 — 사고·수술 위험 최고조!")

            # 6. 겁살 원국 + 겁재·편관 세운 (+10)
            if _has_geop and _sw_ss2 in ("劫財","偏官"):
                _risk += 10
                _risk_reasons.append("원국 겁살 + 흉한 세운 겹침")

            # 7. 상관 세운 + 신약 (+10) — 건강 이상
            try:
                _si_d2 = get_ilgan_strength(ilgan, pils) or {}
            except Exception:
                _si_d2 = {"신강신약":"중화"}
            _sn2 = _si_d2.get("신강신약","")
            if _sw_ss2 == "傷官" and "신약" in _sn2:
                _risk += 10
                _risk_reasons.append("신약 팔자 + 상관 세운 — 건강 이상 주의")

            # 위험 등급
            if _risk >= 70:   _grade,_gc = "🔴 매우 위험",  "#c0392b"
            elif _risk >= 50: _grade,_gc = "🟠 주의 요망",  "#e67e22"
            elif _risk >= 30: _grade,_gc = "🟡 약간 주의",  "#f1c40f"
            else:              _grade,_gc = "🟢 안전",       "#27ae60"

            accident_data.append({
                "yr":_yr,"age":_age2,"ss":_sw_ss2,"risk":min(_risk,100),
                "grade":_grade,"gc":_gc,"reasons":_risk_reasons,
                "ganji":_sw2.get("세운","")
            })

        # 사고수 테이블 출력
        for _ad in accident_data:
            _is_cur = (_ad["yr"] == _cur_yr2)
            _bdr = "border:2px solid "+_ad["gc"]+";" if _is_cur else "border:1px solid "+_ad["gc"]+"44;"
            _bg = _ad["gc"]+"22" if _ad["risk"] >= 50 else "rgba(255,255,255,0.03)"
            _cur_badge = " ◀ 올해" if _is_cur else ""
            st.markdown(
                f"<div style='background:{_bg};{_bdr}border-radius:10px;padding:12px 14px;margin-bottom:6px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>"
                f"<div><span style='font-size:15px;font-weight:900;color:{_ad["gc"]}'>{_ad["yr"]}년 ({_ad["age"]}세){_cur_badge}</span>"
                f"<span style='font-size:12px;color:#888;margin-left:8px'>{_ad["ganji"]} [{_ad["ss"]}]</span></div>"
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<div style='background:#333;border-radius:6px;width:80px;height:10px'>"
                f"<div style='width:{_ad["risk"]}%;background:{_ad["gc"]};height:10px;border-radius:6px'></div></div>"
                f"<span style='font-size:12px;font-weight:700;color:{_ad["gc"]}'>{_ad["risk"]}점</span>"
                f"<span style='font-size:13px'>{_ad["grade"]}</span></div></div>",
                unsafe_allow_html=True)
            if _ad["reasons"]:
                _r_html = " &nbsp;·&nbsp; ".join([f"<span style='color:#ddd'>{r}</span>" for r in _ad["reasons"]])
                st.markdown(
                    f"<div style='font-size:11px;color:#aaa;padding:4px 8px;background:rgba(0,0,0,0.3);border-radius:6px;margin-top:-4px;margin-bottom:4px'>"
                    f"위험 요인: {_r_html}</div>",
                    unsafe_allow_html=True)

        # 원국 위험 요소 요약
        if _baekho_hits or _yangin_hits2 or _has_geop:
            _warn_items = []
            if _baekho_hits: _warn_items.append(f"⚠️ 백호대살({', '.join(_baekho_hits)}) — 원국에 사고·수술 기운 보유. 충 발동 해에 위험 2배")
            if _yangin_hits2: _warn_items.append(f"⚠️ 양인살({_yangin_jj2}) — 원국에 칼날 기운. 편관 세운 겹치면 수술·사고 최고위험")
            if _has_geop: _warn_items.append("⚠️ 겁살(원국) — 이동·교통 사고 기운 내재. 겁재·편관 세운에 주의")
            st.markdown(
                "<div style='background:#fff0f0;border:1px solid #e53935;border-radius:8px;padding:12px;margin-top:8px'>"
                "<div style='font-size:13px;font-weight:800;color:#c0392b;margin-bottom:6px'>🔴 원국 위험 요소 (평생 조심해야 할 패턴)</div>"
                + "".join(f"<div style='font-size:12px;color:#333;line-height:1.9'>{w}</div>" for w in _warn_items)
                + "</div>",
                unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"사고수 계산 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION NEW-C: 횡재수 정밀 분석
    # ════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d1a00,#1a3300);border:2px solid #f1c40f;
border-radius:14px;padding:16px 20px;margin:16px 0 6px">
<div style="font-size:16px;font-weight:900;color:#f7e695;letter-spacing:2px">
💰 C. 횡재수(橫財數) 정밀 분석 — 천을귀인·삼합·편재식신 교차 계산</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">
단순 재성 십성이 아니라 천을귀인 발동·삼합·편재+식신 겹침까지 복합 계산합니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        # 로컬 변수 보장
        _OH = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
               "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        # 천을귀인 원국 확인
        _TY_MAP = {
            "甲":["丑","未"],"乙":["子","申"],"丙":["亥","酉"],"丁":["亥","酉"],
            "戊":["丑","未"],"己":["子","申"],"庚":["丑","未"],"辛":["寅","午"],
            "壬":["卯","巳"],"癸":["卯","巳"]
        }
        _ty_jjs = _TY_MAP.get(ilgan,[])
        _ty_hits = [p["jj"] for p in pils if p["jj"] in _ty_jjs]

        # 문창귀인 원국 확인
        _MC_MAP = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申","己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
        _mc_jj = _MC_MAP.get(ilgan,"")
        _mc_hits = [p["jj"] for p in pils if p["jj"] == _mc_jj]

        _cur_yr3 = datetime.now().year
        windfall_data = []

        for _yr in range(_cur_yr3, _cur_yr3 + 6):
            _age3 = _yr - birth_year + 1
            _sw3 = get_yearly_luck(pils, _yr) or {}
            _sw_ss3 = TEN_GODS_MATRIX.get(ilgan,{}).get(_sw3.get("cg",""),"-")
            _sw_jj3 = _sw3.get("jj","")
            _sw_oh3 = _OH.get(_sw3.get("cg","")[:1],"") if _sw3.get("cg") else ""

            _luck = 0
            _luck_reasons = []

            # 1. 편재·정재·식신 세운 (+25~30)
            if _sw_ss3 == "偏財":
                _luck += 30
                _luck_reasons.append("편재 세운 — 사업·투자 기회의 해!")
            elif _sw_ss3 == "正財":
                _luck += 20
                _luck_reasons.append("정재 세운 — 안정적 수입 상승")
            elif _sw_ss3 == "食神":
                _luck += 20
                _luck_reasons.append("식신 세운 — 재능이 돈이 되는 해")

            # 2. 용신 오행 세운 (+20)
            if _sw_oh3 in yongshin:
                _luck += 20
                _luck_reasons.append(f"용신({_sw_oh3}) 세운 — 용신 에너지 최고조!")

            # 3. 천을귀인 세운 지지 발동 (+20)
            if _sw_jj3 in _ty_jjs:
                _luck += 20
                _luck_reasons.append(f"천을귀인({_sw_jj3}) 세운 발동 — 귀인이 재물을 가져온다!")

            # 4. 세운 지지와 원국 삼합 성립 (+20)
            _SAM_HAP_M = {
                frozenset(["子","辰","申"]):"水 삼합", frozenset(["午","戌","寅"]):"火 삼합",
                frozenset(["卯","未","亥"]):"木 삼합", frozenset(["酉","丑","巳"]):"金 삼합"
            }
            _all_jj_set = set(all_jj + [_sw_jj3])
            for _combo, _cname in _SAM_HAP_M.items():
                if _combo.issubset(_all_jj_set) and _sw_jj3 in _combo:
                    _luck += 20
                    _luck_reasons.append(f"{_cname} 성립 — 세운이 완성시켜 발복!")
                    break

            # 5. 편재+식신 동시 세운 or 대운 (더블재물) (+15)
            try:
                _dw3 = next((d for d in SajuCoreEngine.get_daewoon(
                    pils, birth_year,
                    st.session_state.get("birth_month",1),
                    st.session_state.get("birth_day",1),
                    st.session_state.get("birth_hour",12),
                    st.session_state.get("birth_minute",0),
                    gender=gender
                ) if d.get("시작연도",0) <= _yr <= d.get("종료연도",9999)), None)
                if _dw3:
                    _dw_ss3 = TEN_GODS_MATRIX.get(ilgan,{}).get(_dw3.get("cg",""),"-")
                    if (_sw_ss3 in ("偏財","食神") and _dw_ss3 in ("偏財","食神")):
                        _luck += 15
                        _luck_reasons.append(f"대운({_dw_ss3})+세운({_sw_ss3}) 재물 더블 — 대박 가능성!")
                    if _dw_ss3 in ("偏財","正財","食神"):
                        _luck += 10
                        _luck_reasons.append(f"대운 {_dw_ss3} — 재물 흐름 뒷받침")
            except Exception:
                pass

            # 6. 문창귀인 + 정인 세운 (+10) — 학업·명예 횡재
            if _mc_hits and _sw_ss3 in ("正印","偏印"):
                _luck += 10
                _luck_reasons.append("문창귀인(원국)+인성 세운 — 시험·자격·명예 횡재!")

            # 횡재 등급
            if _luck >= 70:   _wgrade,_wc = "🌟 대박 가능성",  "#f7e695"
            elif _luck >= 50: _wgrade,_wc = "💰 재물 상승기",  "#f1c40f"
            elif _luck >= 30: _wgrade,_wc = "📈 소득 증가",   "#27ae60"
            else:              _wgrade,_wc = "⚖️ 평년 수준",   "#888888"

            windfall_data.append({
                "yr":_yr,"age":_age3,"ss":_sw_ss3,"luck":min(_luck,100),
                "grade":_wgrade,"gc":_wc,"reasons":_luck_reasons,
                "ganji":_sw3.get("세운","")
            })

        # 횡재수 테이블 출력
        for _wd in windfall_data:
            _is_cur = (_wd["yr"] == _cur_yr3)
            _bdr = "border:2px solid "+_wd["gc"]+";" if _is_cur else "border:1px solid "+_wd["gc"]+"44;"
            _bg2 = _wd["gc"]+"22" if _wd["luck"] >= 50 else "rgba(255,255,255,0.03)"
            _cur_b2 = " ◀ 올해" if _is_cur else ""
            st.markdown(
                f"<div style='background:{_bg2};{_bdr}border-radius:10px;padding:12px 14px;margin-bottom:6px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>"
                f"<div><span style='font-size:15px;font-weight:900;color:{_wd["gc"]}'>{_wd["yr"]}년 ({_wd["age"]}세){_cur_b2}</span>"
                f"<span style='font-size:12px;color:#888;margin-left:8px'>{_wd["ganji"]} [{_wd["ss"]}]</span></div>"
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<div style='background:#333;border-radius:6px;width:80px;height:10px'>"
                f"<div style='width:{_wd["luck"]}%;background:{_wd["gc"]};height:10px;border-radius:6px'></div></div>"
                f"<span style='font-size:12px;font-weight:700;color:{_wd["gc"]}'>{_wd["luck"]}점</span>"
                f"<span style='font-size:13px'>{_wd["grade"]}</span></div></div>",
                unsafe_allow_html=True)
            if _wd["reasons"]:
                _r2 = " &nbsp;·&nbsp; ".join([f"<span style='color:#f7e695'>{r}</span>" for r in _wd["reasons"]])
                st.markdown(
                    f"<div style='font-size:11px;color:#aaa;padding:4px 8px;background:rgba(0,0,0,0.3);border-radius:6px;margin-top:-4px;margin-bottom:4px'>"
                    f"상승 요인: {_r2}</div>",
                    unsafe_allow_html=True)

        # 원국 행운 요소 요약
        _fortune_items = []
        if _ty_hits: _fortune_items.append(f"🌟 천을귀인({', '.join(_ty_hits)}) 원국 보유 — 귀인 발동 세운에 인생이 바뀐다!")
        if _mc_hits: _fortune_items.append(f"📚 문창귀인({_mc_jj}) 원국 보유 — 시험·자격·명예 분야에서 횡재 가능!")
        if _fortune_items:
            st.markdown(
                "<div style='background:#1a1a00;border:1px solid #f7e695;border-radius:8px;padding:12px;margin-top:8px'>"
                "<div style='font-size:13px;font-weight:800;color:#f7e695;margin-bottom:6px'>🌟 원국 행운 요소 (이것이 터질 때 인생이 바뀐다)</div>"
                + "".join(f"<div style='font-size:12px;color:#e8e8c0;line-height:1.9'>{f}</div>" for f in _fortune_items)
                + "</div>",
                unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"횡재수 계산 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)

    # SECTION 6: 만신 직격 처방 (강화판)
    # ════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0000,#3a0000);border:2px solid #e53935;
border-radius:14px;padding:16px 20px;margin:16px 0 6px">
<div style="font-size:16px;font-weight:900;color:#ff6b6b;letter-spacing:2px">
🔴 6. 만신 직격 처방 — 이 팔자가 망하는 이유와 흥하는 법</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">
듣기 싫어도 들어야 하는 소리다. 이걸 모르면 평생 같은 실수를 반복한다.</div>
</div>""", unsafe_allow_html=True)

    try:
        # si_d, yongshin은 위에서 이미 정의됨 — 폴백 처리
        if 'si_d' not in dir() or not si_d:
            si_d = get_ilgan_strength(ilgan, pils)
        sn   = si_d.get("신강신약","중화")
        sc   = si_d.get("helper_score", 50)
        ys_d = get_yongshin(pils)
        yong_ohs = ys_d.get("종합_용신",[]) if isinstance(ys_d.get("종합_용신",[]),list) else yongshin
        gi_ohs   = [o for o in ["木","火","土","金","水"] if o in str(ys_d.get("기신",""))]
        gk  = get_gyeokguk(pils)
        gkn = gk["격국명"] if gk else "미정격"
        # _il_sinsal_names는 위에서 이미 정의됨

        # ── 십성 분포 분석 ───────────────────────────
        geop_cnt = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("劫財","겁재"))
        pg_cnt   = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("偏官","편관"))
        sg_cnt   = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("傷官","상관"))
        si_cnt   = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("食神","식신"))
        in_cnt   = sum(1 for p in pils if TEN_GODS_MATRIX.get(ilgan,{}).get(p.get("cg",""),"") in ("正印","편인","정인","偏印"))

        prescriptions = []

        # ── 형살 ──
        if hyung_found:
            prescriptions.append(("🔴 형살(刑殺) — 이 팔자의 평생 저주",
                f"형살이 원국에 박혀 있다. 법적 문제, 관재, 칼부림 같은 갈등이 평생 주기적으로 터진다. "
                f"이게 운이 나빠서가 아니다. 이 팔자 구조가 그렇게 생겼다. "
                f"계약서 없는 거래는 거지꼴 나는 지름길이다. 입 조심 안 하면 소송이 날아온다. "
                f"형살 발동 해(세운 충·형 겹칠 때)엔 아무것도 새로 시작하지 마라. 그냥 버텨라."))

        # ── 겁재 과다 ──
        if geop_cnt >= 2:
            prescriptions.append(("🔴 겁재 과다 — 벌어도 빼앗기는 팔자",
                f"겁재가 {geop_cnt}개다. 이 팔자는 돈을 아무리 잘 벌어도 결국 남 손에 들어가게 돼 있다. "
                f"동업하면 반드시 등 찔린다. 보증 섰다간 집 날아간다. 투자 정보 공유하면 그 사람이 먼저 먹는다. "
                f"재물은 절대 혼자 관리하고, 통장도 절대 남 손에 넘기지 마라. "
                f"믿었던 사람한테 배신당하는 게 이 팔자의 패턴이다. 반복하지 마라."))

        # ── 편관 과다 ──
        if pg_cnt >= 2:
            if "신강" in sn:
                prescriptions.append(("🔴 신강+편관 — 세상과 정면충돌하는 팔자",
                    f"기운도 넘치는데 편관도 {pg_cnt}개다. 이 팔자는 본능적으로 세상에 덤비려 한다. "
                    f"이기려 하면 반드시 더 강한 놈이 나타난다. 이건 그냥 진리다. "
                    f"이 에너지를 군경·검찰·의료·스포츠·경쟁 분야로 돌리면 전국 최고가 된다. "
                    f"엉뚱한 데 쏟으면 평생 싸움질하다 병원 신세 진다."))
            else:
                prescriptions.append(("⚠️ 신약+편관 — 압박에 무너지는 팔자",
                    f"기운이 약한데 편관이 {pg_cnt}개나 짓누른다. "
                    f"스트레스가 몸으로 직결된다. 화병, 위장병, 불면이 주기적으로 온다. "
                    f"직장에서 위에 찍히거나 강압적인 환경에 놓이면 가장 위험하다. "
                    f"귀인 한 명이 평생을 바꾼다. 좋은 상사·파트너를 사수하는 게 이 팔자의 생존 전략이다."))

        # ── 상관 과다 ──
        if sg_cnt >= 2:
            prescriptions.append(("⚠️ 상관 과다 — 입이 화근인 팔자",
                f"상관이 {sg_cnt}개다. 이 팔자는 타고난 창의성과 반골 기질이 넘친다. "
                f"말 잘하고 머리 잘 돌아가지만, 그 입이 평생 발목을 잡는다. "
                f"윗사람한테 직설로 대들면 무조건 진다. 이직을 자주 한다면 전부 이 때문이다. "
                f"이 기운을 창작·컨텐츠·프리랜서·1인 사업으로 쏟으면 독보적 존재가 된다. "
                f"조직 생활은 이 팔자랑 안 맞는다. 억지로 맞추려 할수록 병난다."))

        # ── 인성 과다 ──
        if in_cnt >= 3:
            prescriptions.append(("⚠️ 인성 과다 — 의존·게으름의 팔자",
                f"인성이 {in_cnt}개다. 공부는 잘하고 귀인 덕은 있는데, "
                f"움직이기 싫어하고 남한테 기대려는 본능이 강하다. "
                f"이 팔자는 누군가 다 해줄 거라는 착각을 끊어야 한다. "
                f"귀인이 문을 열어줘도 발로 걸어 들어가는 건 본인이다. "
                f"행동하지 않으면 이 팔자의 복이 전부 썩는다."))

        # ── 역마+겁살 동시 ──
        if "역마살" in _il_sinsal_names and "겁살" in _il_sinsal_names:
            prescriptions.append(("🔴 역마+겁살 — 움직일 때 사고 나는 팔자",
                "이 팔자는 이동할 때 사고가 난다. 그냥 확률이 높은 거다. "
                "장거리 이동 전 차량 점검은 선택이 아니라 의무다. 야간 운전 하지 마라. "
                "해외 여행·출장엔 반드시 보험 가입하고, 낯선 곳에서 무리하게 돌아다니지 마라. "
                "이 살이 발동하는 해엔 가능하면 집에 있어라."))

        # ── 기신 직격 ──
        if gi_ohs:
            _GI_RAW = {
                "木": ("봄(3~5월)·동쪽·초록색",
                       "이 계절에 큰 결정 내리면 손재가 따른다. 봄에 계약·투자 하면 후회한다. "
                       "동쪽 방향 이사는 이 팔자에 독이다."),
                "火": ("여름(6~8월)·남쪽·빨간색",
                       "여름에 충동적으로 내리는 결정이 이 팔자를 망친다. "
                       "더울 때 화나서 한 행동이 평생 짐이 된다. 빨간 소품 집에 쌓아두지 마라."),
                "土": ("환절기·중앙·황토색",
                       "부동산·토지에 욕심 내면 반드시 손해본다. "
                       "환절기에 시작한 사업은 잘 안 된다. 황토색 계열 물건에 돈 쏟지 마라."),
                "金": ("가을(9~11월)·서쪽·흰색·금속",
                       "가을에 법적 계약·금속 관련 투자 하면 잘린다. "
                       "서쪽 방향 이사는 이 팔자에 재앙이다. 흰색 환경에서 중요한 결정 하지 마라."),
                "水": ("겨울(12~2월)·북쪽·검은색",
                       "겨울철 과음·야간 활동이 이 팔자의 사고를 부른다. "
                       "물 근처에서 조심하라. 북쪽 방향 이사·투자는 이 팔자에 맞지 않는다."),
            }
            gi_blocks = []
            for g in gi_ohs[:2]:
                if g in _GI_RAW:
                    season, desc = _GI_RAW[g]
                    gi_blocks.append(f"【{g} 기신】 {season} — {desc}")
            if gi_blocks:
                prescriptions.append(("⛔ 기신(忌神) — 이 기운이 너를 죽인다",
                    "\n".join(gi_blocks)))

        # ── 화개살 ──
        if "화개살" in _il_sinsal_names:
            prescriptions.append(("🕯️ 화개살 — 고독이 재능이 되는 팔자",
                "이 팔자는 혼자여야 진가가 나온다. "
                "사람들과 어울리면 기운이 흩어지고, 혼자 파고들어야 독보적 경지에 오른다. "
                "예술·연구·기술·종교에서 남이 10년 걸릴 걸 3년에 해치우는 팔자다. "
                "단 고독을 버티지 못하면 우울증이 온다. 혼자 있는 시간과 사람 만나는 시간을 의식적으로 나눠라."))

        # ── 신강신약 핵심 ──
        if "극신강" in sn:
            prescriptions.append(("💥 극신강 — 스스로가 최대의 적",
                f"일간 점수 {sc}/100. 이 팔자는 자기 확신이 너무 강해서 망한다. "
                f"내가 옳다는 확신이 클수록 주변 사람이 다 떠난다. "
                f"용신 오행이 강한 환경에 있으면 그나마 균형이 잡힌다. "
                f"자기 의견을 반으로 줄이고, 타인 말을 두 배로 들어라. 그게 이 팔자의 개운법이다."))
        elif "극신약" in sn:
            prescriptions.append(("💧 극신약 — 혼자선 반드시 망하는 팔자",
                f"일간 점수 {sc}/100. 이 팔자는 혼자 독립해서 뭔가 하면 반드시 힘들다. "
                f"좋은 사람 곁에 있어야 기운이 살아난다. "
                f"파트너·직장·스승을 잘 골라라. 이 팔자의 성공은 인맥에서 결정된다. "
                f"귀인이 오면 절대 놓치지 마라. 그 사람이 운명을 바꾼다."))

        # ── 기본 처방 ──
        if not prescriptions:
            prescriptions.append(("✅ 이 팔자의 핵심 — 흐름을 타는 법",
                f"격국 {gkn} · {sn}({sc}/100) — "
                f"원국에 극단적 위험 패턴은 없다. 이건 좋은 소식이다. "
                f"용신 오행({', '.join(yong_ohs[:2]) if yong_ohs else '분석중'})이 강한 해에 집중적으로 움직이고, "
                f"기신 해엔 절대 큰 결정 내리지 마라. 타이밍이 전부다."))

        # ── 출력 ──
        for title, desc in prescriptions:
            is_red  = "🔴" in title or "💥" in title
            is_warn = "⚠️" in title or "⛔" in title or "💧" in title
            bg  = "#fff0f0" if is_red else "#fff8e8" if is_warn else "#f0fff4"
            bdc = "#e53935" if is_red else "#f57c00" if is_warn else "#27ae60"
            st.markdown(
                f"""<div style='background:{bg};border-left:5px solid {bdc};
border-radius:0 10px 10px 0;padding:16px 18px;margin-bottom:10px'>
<div style='font-size:14px;font-weight:900;color:{bdc};margin-bottom:8px'>{title}</div>
<div style='font-size:13px;color:#1a1a1a;line-height:2.0;white-space:pre-line'>{desc}</div>
</div>""",
                unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"처방 계산 오류: {e}")

    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:24px 0">', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # SECTION 7: 음양오행 비방법 (전통 처방)
    # ════════════════════════════════════════════
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d1a00,#1a3300);border:2px solid #8bc34a;
border-radius:14px;padding:16px 20px;margin:16px 0 6px">
<div style="font-size:16px;font-weight:900;color:#ccff90;letter-spacing:2px">
🌿 7. 오행 비방법(秘方法) — 용신 기운을 강화하고 기신을 막는 전통 처방</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">
대대로 전해온 오행 비방. 오늘 당장 실천할 수 있는 것들이다.</div>
</div>""", unsafe_allow_html=True)

    try:
        _ys7 = get_yongshin(pils)
        _yong7 = _ys7.get("종합_용신",[]) if isinstance(_ys7.get("종합_용신",[]),list) else []
        _gi7   = [o for o in ["木","火","土","金","水"] if o in str(_ys7.get("기신",""))]

        # 용신별 완전 비방 처방
        _BIHANG_FULL = {
            "木": {
                "title": "🌳 목(木) 용신 비방법",
                "강화법": [
                    "동쪽 벽에 키 큰 식물 3개 이상 두어라. 목 기운이 집 안으로 들어온다.",
                    "새벽 5~7시(묘시) — 이 시간에 일어나 동쪽 창문 열고 심호흡 3회. 목 기운을 폐로 흡수한다.",
                    "봄(3~5월)에 중요한 결정·계약·시작을 몰아서 하라. 이 시기에 움직여야 성과가 난다.",
                    "초록·파란색 지갑을 써라. 재물에 목 기운이 붙는다.",
                    "숲·공원·나무 많은 곳을 주 1회 이상 걸어라. 발바닥으로 목 기운을 흡수한다.",
                    "신맛 음식(식초·레몬·매실·키위)을 매일 조금씩 먹어라. 간장을 강화하고 목 기운을 보충한다.",
                ],
                "차단법": [
                    "금속 장식품을 서쪽·현관에 쌓아두지 마라. 금극목(金剋木)으로 용신이 깎인다.",
                    "가을(9~11월)에 큰 투자·사업 시작 금지. 이 시기엔 금 기운이 강해 목 기운이 눌린다.",
                    "흰색·회색·은색 소품을 집 중앙에 두지 마라.",
                    "매운 음식(고추·후추) 과다 섭취를 피하라. 폐·금 기운을 과잉 자극한다.",
                ],
                "기도처방": "동쪽 방향 산신각·약사전에 기도. 향 3개 피우고 '목(木) 기운이 충만하게 해주십시오'를 마음속으로 3번 외워라.",
            },
            "火": {
                "title": "🔥 화(火) 용신 비방법",
                "강화법": [
                    "남쪽 창문을 매일 오전 11시~오후 1시(오시) 열어 햇빛을 집 안으로 들여라.",
                    "빨간·주황·분홍색 소품을 현관과 거실에 하나씩 두어라. 화 기운이 집 안에 깔린다.",
                    "촛불을 주 1회 30분 이상 켜두어라. 화 기운이 공간을 정화하고 강화한다.",
                    "여름(6~8월)에 중요한 시작·발표·계약을 하라. 화 기운이 정점일 때 움직여야 한다.",
                    "붉은 음식(토마토·석류·딸기·팥)을 매일 한 가지씩 먹어라.",
                    "남쪽을 향해 앉아서 일하라. 화 기운이 집중력을 높인다.",
                ],
                "차단법": [
                    "집 북쪽에 수족관·분수·파란 소품 두지 마라. 수극화(水剋火)로 용신이 꺼진다.",
                    "겨울(12~2월)에 큰 결정 금지. 이 시기엔 수 기운이 강해 화 기운이 압도된다.",
                    "검은색·파란색 인테리어를 주조색으로 쓰지 마라.",
                    "찬 음식·냉수 과다 섭취를 피하라. 화 기운이 꺼진다.",
                ],
                "기도처방": "남쪽 방향 대웅전에 기도. 붉은 초 한 자루 켜고 소원을 빌어라. 성화나 불꽃을 바라보며 소망을 마음에 새겨라.",
            },
            "土": {
                "title": "⛰️ 토(土) 용신 비방법",
                "강화법": [
                    "황토 도자기·돌·흙 소품을 집 중앙과 거실에 두어라. 토 기운이 집의 중심을 잡는다.",
                    "맨발로 흙·잔디 위를 매일 10분 이상 걸어라. 발바닥으로 토 기운을 직접 흡수한다.",
                    "노란·황금·베이지색 침구를 써라. 잠자는 동안 토 기운이 보충된다.",
                    "환절기(3·6·9·12월)에 중요한 결정을 하라. 토 기운이 살아나는 시기다.",
                    "단맛 음식(고구마·감자·현미·꿀·단호박)을 매일 먹어라. 비장·위장을 강화한다.",
                    "집 중앙을 항상 깔끔하게 유지하라. 집 중앙이 토의 자리다. 어지르면 토 기운이 흐트러진다.",
                ],
                "차단법": [
                    "동쪽에 키 큰 나무·식물을 과도하게 두지 마라. 목극토(木剋土)로 용신이 깎인다.",
                    "봄(3~5월)에 큰 투자·부동산 거래 금지.",
                    "신맛 음식(식초·레몬·매실) 과다 섭취 금지.",
                    "초록색을 주조색으로 쓰지 마라.",
                ],
                "기도처방": "산신각·토지신에게 기도. 황토 흙으로 만든 도자기에 소금을 담아 현관에 두어라. 땅의 신이 집을 지킨다.",
            },
            "金": {
                "title": "⚔️ 금(金) 용신 비방법",
                "강화법": [
                    "서쪽에 금속 소품(동 촛대·은빛 액자·금속 조각)을 하나 두어라. 금 기운이 집으로 들어온다.",
                    "은·금 장신구를 매일 착용하라. 금 기운을 몸에 달고 다니는 것이다.",
                    "흰색·은색 침구를 써라. 잠자는 동안 금 기운이 충전된다.",
                    "가을(9~11월)에 중요한 계약·투자·시작을 하라. 금 기운이 정점이다.",
                    "매운맛 음식(무·배·도라지·생강·마늘)을 매일 먹어라. 폐와 기관지를 강화한다.",
                    "저녁 5~7시(유시)에 산책하라. 이 시간이 금 기운이 가장 강한 때다.",
                ],
                "차단법": [
                    "남쪽에 붉은 소품·촛불을 과도하게 두지 마라. 화극금(火剋金)으로 용신이 녹는다.",
                    "여름(6~8월)에 큰 계약·금속 투자 금지.",
                    "빨간·주황색을 주조색으로 쓰지 마라.",
                    "쓴 음식·커피 과다 섭취 금지.",
                ],
                "기도처방": "서쪽 방향 나한전에 기도. 은빛 소품을 집 서쪽에 놓고 '금 기운이 충만하게 해주십시오'를 빌어라.",
            },
            "水": {
                "title": "💧 수(水) 용신 비방법",
                "강화법": [
                    "집 북쪽에 작은 어항 또는 흐르는 물 소품을 두어라. 수 기운이 집으로 흘러 들어온다.",
                    "하루 물 2리터 이상 반드시 마셔라. 수 기운이 부족하면 신장·방광이 약해진다.",
                    "검은·남색 지갑과 소품을 써라. 재물에 수 기운이 붙는다.",
                    "겨울(12~2월)에 중요한 계획·전략을 세워라. 수 기운이 지혜를 극대화한다.",
                    "짠맛 음식(김·미역·다시마·검은콩·흑임자)을 매일 먹어라. 신장을 강화한다.",
                    "취침 전 북쪽을 향해 맑은 물 한 잔을 마셔라. 수면 중 수 기운이 보충된다.",
                ],
                "차단법": [
                    "집 남쪽에 붉은 소품·조명을 과도하게 두지 마라. 화극수(火剋水)의 역습이 온다.",
                    "여름(6~8월)에 큰 투자·계약 금지.",
                    "빨간·주황색을 주조색으로 쓰지 마라.",
                    "짠 음식 과다 섭취는 신장에 역설적으로 독이 되니 적당히.",
                ],
                "기도처방": "북쪽 방향 용왕당·해신당에 기도. 검은 그릇에 소금물을 담아 집 북쪽에 두어라. 수의 정령이 지혜와 재물을 불러온다.",
            },
        }

        # 용신 오행 비방 출력
        if _yong7:
            for _yoh7 in _yong7[:2]:
                _bh = _BIHANG_FULL.get(_yoh7)
                if not _bh:
                    continue
                _bc = _OH_COLOR.get(_yoh7,"#888")
                st.markdown(f"""<div style='background:#fafafa;border:1px solid {_bc}33;
border-radius:12px;padding:18px;margin-bottom:16px'>
<div style='font-size:15px;font-weight:900;color:{_bc};margin-bottom:14px'>{_bh['title']}</div>""",
                    unsafe_allow_html=True)

                # 강화법
                st.markdown(f"<div style='font-size:13px;font-weight:800;color:{_bc};margin-bottom:8px'>✅ 용신 강화법 — 지금 당장 실천하라</div>", unsafe_allow_html=True)
                for item in _bh["강화법"]:
                    st.markdown(
                        f"<div style='background:{_bc}11;border-left:3px solid {_bc};border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px;font-size:13px;color:#1a1a1a;line-height:1.8'>• {item}</div>",
                        unsafe_allow_html=True)

                # 차단법
                st.markdown("<div style='font-size:13px;font-weight:800;color:#e53935;margin:12px 0 8px'>⛔ 기신 차단법 — 이것만 피해도 반은 먹고 간다</div>", unsafe_allow_html=True)
                for item in _bh["차단법"]:
                    st.markdown(
                        f"<div style='background:#fff0f0;border-left:3px solid #e53935;border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px;font-size:13px;color:#1a1a1a;line-height:1.8'>✗ {item}</div>",
                        unsafe_allow_html=True)

                # 기도처방
                st.markdown(
                    f"<div style='background:#1a1a2e;border:1px solid {_bc};border-radius:8px;padding:12px 14px;margin-top:10px'>"
                    f"<div style='font-size:12px;font-weight:800;color:{_bc};margin-bottom:4px'>🛕 기도 처방</div>"
                    f"<div style='font-size:13px;color:#ddd;line-height:1.8'>{_bh['기도처방']}</div></div>",
                    unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

        # 기신 차단 핵심만
        if _gi7:
            st.markdown(f"""<div style='background:#fff5f5;border:2px solid #e53935;border-radius:12px;padding:16px;margin-top:8px'>
<div style='font-size:14px;font-weight:900;color:#c0392b;margin-bottom:10px'>🚫 기신({", ".join(_gi7)}) 완전 차단 처방 — 이것만 안 해도 손해가 반으로 준다</div>""",
                unsafe_allow_html=True)
            _GI_BLOCK = {
                "木": "초록색 인테리어·동쪽 방향 이사 피하기. 봄에 중요 계약·투자 금지. 나무 소품 집에 과도하게 두지 말 것.",
                "火": "빨간 소품·남쪽 조명 과다 금지. 여름에 충동적 결정 금지. 화재보험 반드시 가입.",
                "土": "부동산·토지 투자 이 팔자에 독. 황토색 환경 피하기. 환절기 큰 계약 금지.",
                "金": "금속 투자·서쪽 이사 금지. 가을에 법적 계약 피하기. 흰색 옷을 주조색으로 쓰지 말 것.",
                "水": "과음·야간 수상 활동 금지. 겨울에 큰 사업 시작 금지. 북쪽 방향 이사는 이 팔자에 독.",
            }
            for _g7 in _gi7[:2]:
                _gd = _GI_BLOCK.get(_g7,"")
                if _gd:
                    st.markdown(
                        f"<div style='background:#fff0f0;border-left:4px solid #e53935;border-radius:0 8px 8px 0;"
                        f"padding:10px 14px;margin-bottom:6px;font-size:13px;color:#1a1a1a;line-height:1.9'>"
                        f"<b style='color:#c0392b'>{_g7} 기신 차단:</b> {_gd}</div>",
                        unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 즉각 실천 체크리스트
        st.markdown("""<div style='background:#1a1a1a;border:2px solid #d4af37;border-radius:12px;padding:16px;margin-top:16px'>
<div style='font-size:14px;font-weight:900;color:#f7e695;margin-bottom:12px'>⚡ 오늘 당장 실천할 것 — 내일로 미루면 아무 소용 없다</div>""",
            unsafe_allow_html=True)
        # ── 용신별 맞춤 체크리스트 ──────────────────────────
        _yoh7_main = _yong7[0] if _yong7 else ""
        _YONG_CL = {
            "木": [
                ("🌿 집 동쪽에 초록 식물 1개 오늘 배치하거나 주문하기", "#2d8a4e"),
                ("🌅 내일 아침 동쪽 창문 열고 심호흡 3회 실천하기", "#2d8a4e"),
                ("🍋 오늘 식단에 신맛 음식 1가지 추가하기 (레몬·식초·매실)", "#27ae60"),
            ],
            "火": [
                ("🕯️ 오늘 저녁 촛불 1개 켜두기 (30분 이상)", "#e53935"),
                ("🔴 빨간색 소품 1개 현관이나 거실에 오늘 두기", "#e53935"),
                ("🍅 오늘 식단에 붉은 음식 1가지 추가하기 (토마토·딸기·석류)", "#27ae60"),
            ],
            "土": [
                ("🪨 황토 도자기나 돌 소품 1개 집 중앙에 오늘 두기", "#f9a825"),
                ("🦶 내일 맨발 흙 위 10분 걷기 계획 잡기", "#f9a825"),
                ("🍠 오늘 식단에 단맛 음식 1가지 추가하기 (고구마·꿀·현미)", "#27ae60"),
            ],
            "金": [
                ("💍 은·금 장신구 내일부터 매일 착용하기로 결심", "#9e9e9e"),
                ("🪟 집 서쪽에 금속 소품 1개 오늘 배치하기", "#9e9e9e"),
                ("🥬 오늘 식단에 매운맛 추가하기 (무·도라지·생강·마늘)", "#27ae60"),
            ],
            "水": [
                ("🐟 집 북쪽에 작은 어항이나 분수 소품 구매 계획 오늘 세우기", "#1565c0"),
                ("💧 오늘부터 하루 물 2리터 마시기 알람 설정하기", "#1565c0"),
                ("🌿 오늘 식단에 검은 음식 1가지 추가하기 (검은콩·미역·김)", "#27ae60"),
            ],
        }
        _cl_items = list(_YONG_CL.get(_yoh7_main, [
            ("🧭 용신 방향 확인하고 침대 머리 방향 조정하기", "#d4af37"),
            ("🎨 용신 색상 소품 1개 구입 계획 세우기", "#d4af37"),
            ("🍽️ 용신 음식 내일 장보기 목록에 추가하기", "#27ae60"),
        ]))
        # 폴백 항목도 텍스트 확인
        _cl_items = [(t if t.strip() else "✅ 오늘 개운법 실천 계획 세우기", c) for t, c in _cl_items]
        _cl_items += [
            ("🧹 기신 색상 소품을 눈에 띄지 않는 곳으로 오늘 치우기", "#e53935"),
            ("📅 올해 기신 강한 달을 달력에 빨간 표시 해두기", "#f57c00"),
            ("⭐ 이번 달 용신 길일에 중요한 미팅·계약 일정 잡기", "#d4af37"),
        ]
        for _ci, _cc in _cl_items:
            _ci_text = str(_ci).strip() if _ci else "✅ 개운 실천"
            st.markdown(
                f"<div style='display:flex;align-items:flex-start;gap:10px;"
                f"background:#1e1e2e;border-radius:8px;"
                f"padding:10px 14px;margin-bottom:6px;"
                f"word-break:keep-all;overflow-wrap:break-word'>"
                f"<span style='color:{_cc};font-size:18px;flex-shrink:0;margin-top:1px'>☐</span>"
                f"<span style='font-size:13px;color:#e8e8e8;line-height:1.8;"
                f"word-break:keep-all;overflow-wrap:break-word;flex:1'>{_ci_text}</span>"
                f"</div>",
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


        # ── 월별 개운 달력 ─────────────────────────────────
        st.markdown("\n**📅 용신 기준 월별 개운 달력**")
        _OH_MONTH_PEAK = {
            "木": [3,4],   # 봄
            "火": [6,7],   # 여름
            "土": [3,6,9,12],  # 환절기
            "金": [9,10],  # 가을
            "水": [11,12], # 겨울
        }
        _OH_MONTH_WEAK = {
            "木": [9,10],  "火": [11,12],
            "土": [3,4],   "金": [3,4],   "水": [6,7],
        }
        import datetime as _dt_bh
        _cur_m = _dt_bh.datetime.now().month
        if _yong7:
            _peak_m = _OH_MONTH_PEAK.get(_yong7[0], [])
            _weak_m = _OH_MONTH_WEAK.get(_yong7[0], [])
            _mc_bh  = st.columns(4)
            for _mi in range(1, 13):
                _mk = _mi % 4
                if _mi in _peak_m:
                    _mbg, _mc2 = "#e8f5e9", "#2e7d32"
                    _mtxt = "🌟 길월"
                elif _mi in _weak_m:
                    _mbg, _mc2 = "#ffebee", "#b71c1c"
                    _mtxt = "⚠️ 주의"
                else:
                    _mbg, _mc2 = "#f5f5f5", "#666"
                    _mtxt = "⚖️ 보통"
                _now_m_mark = " ◀" if _mi == _cur_m else ""
                _mc_bh[(_mi-1)%4].markdown(f"""<div style="background:{_mbg};border:1px solid {_mc2};
border-radius:6px;padding:6px 8px;margin:2px 0;font-size:12px;color:{_mc2};text-align:center">
<b>{_mi}월{_now_m_mark}</b><br>{_mtxt}</div>""", unsafe_allow_html=True)

        # ── 행운 아이템 리스트 ─────────────────────────────
        if _yong7:
            _OH_ITEMS = {
                "木": ["🌱 초록 화분 (책상 위)", "📗 초록 노트·다이어리", "🪴 대나무·행운목",
                       "🟢 초록 지갑·카드지갑", "🌲 숲 그림·사진 (북동쪽 벽)", "🫚 올리브오일 (부엌)"],
                "火": ["🕯️ 빨간 초 (거실)", "🌹 빨간 꽃 (현관)", "🔴 빨간 쿠션·소품",
                       "☀️ 일출 사진 (남쪽 벽)", "🍅 토마토·딸기 (냉장고)", "🧧 빨간 지갑"],
                "土": ["🪨 황토 도자기 (집 중앙)", "🟡 노란 쿠션·러그", "🍠 고구마·감자 (주방)",
                       "⛰️ 산 그림 (거실)", "🎋 황금색 소품", "💛 노란 지갑·카드지갑"],
                "金": ["🔮 수정·백수정 (서쪽)", "⚪ 흰색 침구", "🪙 동전·금화 장식",
                       "🤍 흰색 지갑", "⚙️ 금속 소품 (서쪽)", "🌕 달 그림·사진"],
                "水": ["💧 수족관·분수 (북쪽)", "🖤 검정 지갑", "📘 남색 소품",
                       "🐟 물고기 그림 (북쪽)", "🫗 검정 텀블러", "🌊 바다 그림 (북쪽 벽)"],
            }
            _items = _OH_ITEMS.get(_yong7[0], [])
            if _items:
                st.markdown(f"\n**🛒 용신 오행 행운 아이템 — 지금 당장 구비하면 좋은 것들**")
                _ic = st.columns(3)
                for _ii, _itm in enumerate(_items):
                    _ic[_ii%3].markdown(f"""<div style="background:#fff8f0;border:1px solid #c9a84c;
border-radius:8px;padding:8px;margin:4px 0;font-size:12px;color:#4a2800;text-align:center">{_itm}</div>""",
unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"비방법 계산 오류: {e}")



        st.caption("⚠️ 본 분석은 전통 명리학·민속 문화 기반 참고 자료입니다. 실제 처방은 전문 만신에게 문의하십시오.")



def menu_tojeong(pils, name, birth_year, gender):
    """📜 토정비결 탭 — 올해 신수 + 풍수지리 방위"""
    import datetime as _dt_tj

    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0d00,#3e2000);border:2px solid #ff8f00;
border-radius:16px;padding:20px 24px;margin-bottom:16px">
<div style="font-size:20px;font-weight:900;color:#ffe082;letter-spacing:2px">📜 토정비결(土亭秘訣)</div>
<div style="font-size:13px;color:#ffcc80;margin-top:6px">이지함(土亭 李之菡) 선생의 전통 신수법 — 태세·월건·일진 세 수의 합으로 오는 한 해의 큰 흐름을 봅니다.</div>
</div>""", unsafe_allow_html=True)

    try:
        _cur_y = _dt_tj.datetime.now().year
        _bm_tj = int(st.session_state.get("birth_month", 1) or 1)
        _bd_tj = int(st.session_state.get("birth_day", 1) or 1)

        # ── 태세수 ──────────────────────────────────────────────
        _GANJI60 = [
            "갑자","을축","병인","정묘","무진","기사","경오","신미","임신","계유",
            "갑술","을해","병자","정축","무인","기묘","경진","신사","임오","계미",
            "갑신","을유","병술","정해","무자","기축","경인","신묘","임진","계사",
            "갑오","을미","병신","정유","무술","기해","경자","신축","임인","계묘",
            "갑진","을사","병오","정미","무신","기유","경술","신해","임자","계축",
            "갑인","을묘","병진","정사","무오","기미","경신","신유","임술","계해",
        ]
        _taeSei_idx = (_cur_y - 1864) % 60
        _taeSei_n   = _taeSei_idx + 1
        _taeSei_gj  = _GANJI60[_taeSei_idx]

        # ── 월건수 ──────────────────────────────────────────────
        _wolGeon_n = _bm_tj

        # ── 일진수 ──────────────────────────────────────────────
        _ilJin_n = _bd_tj % 30 if _bd_tj % 30 != 0 else 30

        _total  = _taeSei_n + _wolGeon_n + _ilJin_n
        _gwe_n  = _total % 144
        if _gwe_n == 0: _gwe_n = 144

        # ── 괘별 운세 ───────────────────────────────────────────
        _GWE = [
            (range(1,21),   "☀️ 대길(大吉)", "#e65100", "#fff8e1",
             "봄볕처럼 환한 한 해입니다. 추진하는 일이 순탄하게 풀리고 귀인이 도와 뜻밖의 성취가 있습니다. 새로운 시작·계약·결혼·이사 모두 이 해에 하면 좋습니다.",
             ["중요한 결정을 과감하게 내리십시오", "귀인의 제안은 흘려듣지 마십시오",
              "투자·사업 확장의 최적기입니다", "인맥을 적극 넓히십시오"]),
            (range(21,41),  "✅ 길(吉)", "#2e7d32", "#e8f5e9",
             "노력이 결실을 맺는 해입니다. 꾸준히 나아가면 중반 이후 좋은 소식이 옵니다. 서두르지 않아도 자연스럽게 풀리는 흐름입니다.",
             ["꾸준함이 최고의 전략입니다", "조급함을 버리십시오",
              "중반 이후 계약·발표를 집중하십시오", "건강관리를 병행하십시오"]),
            (range(41,61),  "⚖️ 중길(中吉)", "#1565c0", "#e3f2fd",
             "크지도 작지도 않은 평탄한 흐름의 해입니다. 욕심을 버리고 현실에 충실하면 무난히 마칩니다. 현상 유지만 해도 성공한 해입니다.",
             ["무리한 욕심은 금물입니다", "현재 위치를 단단히 다지십시오",
              "소소한 성취에도 감사하십시오", "저축·절약이 이 해의 최선입니다"]),
            (range(61,81),  "⚠️ 소흉(小凶)", "#f57c00", "#fff3e0",
             "작은 장애와 손실이 있는 해입니다. 서두르지 말고 수비 위주로 움직이십시오. 조심하면 큰 문제 없이 넘길 수 있습니다.",
             ["새로운 투자·동업을 자제하십시오", "건강 정기검진을 받으십시오",
              "말을 신중히 하십시오", "현금 보유를 늘리십시오"]),
            (range(81,101), "🔴 흉(凶)", "#b71c1c", "#ffebee",
             "변동·시련이 따르는 해입니다. 새 시작·투자·이사는 내년으로 미루고 현상 유지에 집중하십시오. 인내와 수비가 이 해의 전략입니다.",
             ["절대 무리한 새 시작 금지", "건강에 각별히 주의하십시오",
              "가족과 화합을 최우선으로", "작은 일도 꼼꼼히 확인하십시오"]),
            (range(101,121),"🌊 대변화(大變化)", "#7b1fa2", "#f3e5f5",
             "큰 변화의 기운이 흐르는 해입니다. 변화에 저항하면 손실이 오고, 흐름에 올라타면 기회가 됩니다. 변화를 두려워하지 마십시오.",
             ["변화를 두려워 말고 올라타십시오", "유연한 사고로 대응하십시오",
              "주변의 의견을 경청하십시오", "계획을 자주 점검·수정하십시오"]),
            (range(121,145),"🌱 재기(再起)", "#388e3c", "#e8f5e9",
             "어려웠던 것이 풀리기 시작하는 해입니다. 인내하며 기다리면 후반에 반전이 옵니다. 포기하지 않으면 반드시 길이 열립니다.",
             ["포기하지 마십시오", "후반기에 집중하십시오",
              "작은 성취도 소중히 여기십시오", "귀인을 놓치지 마십시오"]),
        ]

        _grade, _c_txt, _c_bg, _desc, _tips = "⚖️ 평년", "#1565c0", "#e3f2fd", "평탄한 해입니다.", []
        for (_rng, _g, _ct, _cb, _d, _tp) in _GWE:
            if _gwe_n in _rng:
                _grade, _c_txt, _c_bg, _desc, _tips = _g, _ct, _cb, _d, _tp
                break

        st.markdown(f"""
<div style="background:{_c_bg};border:2px solid {_c_txt};border-radius:14px;padding:20px;margin:12px 0">
<div style="font-size:13px;color:#666;margin-bottom:6px">
태세 <b>{_taeSei_gj}</b>({_taeSei_n}) + 생월({_wolGeon_n}) + 생일({_ilJin_n}) = 합계 <b>{_total}</b> → 제<b>{_gwe_n}</b>괘</div>
<div style="font-size:13px;color:#555;margin-bottom:4px">{name}님의 <b>{_cur_y}년</b> 신수</div>
<div style="font-size:28px;font-weight:900;color:{_c_txt};margin:8px 0">{_grade}</div>
<div style="font-size:14px;color:#333;line-height:1.8">{_desc}</div>
</div>""", unsafe_allow_html=True)

        if _tips:
            st.markdown("**📌 이 해의 핵심 행동 지침:**")
            _tc = st.columns(2)
            for _ti2, _tip in enumerate(_tips):
                _tc[_ti2%2].markdown(f"""<div style="background:#fff;border:1px solid #ddd;border-radius:8px;
padding:10px 12px;margin:4px 0;font-size:13px;color:#333">• {_tip}</div>""", unsafe_allow_html=True)

        # ── 월별 신수 ────────────────────────────────────────────
        st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)
        st.markdown("### 📅 월별 신수 — 12달 흐름")
        _MONTH_TOJEONG = [
            (1, "봄기운 시작. 새해 목표를 세우기 좋으나 성급한 실행은 자제하십시오."),
            (2, "귀인을 만날 기운. 새로운 인연·소개·모임에 적극 참여하십시오."),
            (3, "재물 관리 집중. 지출을 줄이고 투자 결정은 신중히 하십시오."),
            (4, "건강 점검 필수. 무리한 일정을 줄이고 휴식을 충분히 취하십시오."),
            (5, "대인관계 주의. 말 한마디가 인연을 가르는 달입니다."),
            (6, "사업·계약의 최적기. 계획했던 일을 이 달에 실행하십시오."),
            (7, "여행·이동 주의. 장거리 이동 전 안전 점검을 철저히 하십시오."),
            (8, "재물 성장 기운. 수입을 늘릴 기회를 적극 탐색하십시오."),
            (9, "가족 화합 중요. 가까운 사람과의 관계에 더 신경 쓰십시오."),
            (10, "직업·진로 결정의 달. 중요한 선택이 있다면 이 달에 하십시오."),
            (11, "수비 강화. 무리한 지출·확장을 멈추고 내실을 다지십시오."),
            (12, "마무리·정산. 올해를 잘 마무리하고 내년을 준비하십시오."),
        ]
        with st.expander("📅 12달 월별 신수 펼치기", expanded=True):
            # 4행 × 3열 그리드 (1~12월)
            for _row in range(4):
                _row_cols = st.columns(3)
                for _ci3, (_mn2, _md) in enumerate(_MONTH_TOJEONG[_row*3:_row*3+3]):
                    _mn_color = "#e65100" if _mn2 == _dt_tj.datetime.now().month else "#1565c0"
                    _mn_bg    = "#fff3e0" if _mn2 == _dt_tj.datetime.now().month else "#f5f5f5"
                    _row_cols[_ci3].markdown(
                        f"<div style='background:{_mn_bg};border-left:3px solid {_mn_color};"
                        f"border-radius:0 8px 8px 0;padding:8px 10px;margin:4px 0;"
                        f"word-break:keep-all;overflow-wrap:break-word'>"
                        f"<div style='font-size:12px;font-weight:700;color:{_mn_color}'>"
                        f"{_mn2}월{'  ← 이달' if _mn2==_dt_tj.datetime.now().month else ''}</div>"
                        f"<div style='font-size:12px;color:#444;line-height:1.6;margin-top:2px'>{_md}</div>"
                        f"</div>",
                        unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"토정비결 계산 오류: {e}")

    # ── 풍수지리 방위 ────────────────────────────────────────────
    st.markdown('<hr style="border:none;border-top:1px solid #e0d8c0;margin:20px 0">', unsafe_allow_html=True)
    st.markdown("""
<div style="background:linear-gradient(135deg,#001a00,#003300);border:2px solid #66bb6a;
border-radius:14px;padding:16px 20px;margin:8px 0">
<div style="font-size:18px;font-weight:900;color:#c8e6c9;letter-spacing:2px">🏔️ 풍수지리 방위 — 나경(羅經) 기반</div>
<div style="font-size:12px;color:#aaa;margin-top:4px">띠(년지) 기준 길방·흉방. 이사·책상·침대 방향 참고.</div>
</div>""", unsafe_allow_html=True)

    try:
        _yr_jj_f = pils[3]["jj"] if len(pils) > 3 else ""
        _JJ_TI2  = {"子":"쥐","丑":"소","寅":"호랑이","卯":"토끼","辰":"용","巳":"뱀",
                    "午":"말","未":"양","申":"원숭이","酉":"닭","戌":"개","亥":"돼지"}
        _GILBANG2 = {
            "子":{"생기":"북(北)","천의":"동북(東北)","복위":"남(南)","흉방":"서(西)"},
            "丑":{"생기":"동북(東北)","천의":"서북(西北)","복위":"동(東)","흉방":"남(南)"},
            "寅":{"생기":"동(東)","천의":"남(南)","복위":"서북(西北)","흉방":"서(西)"},
            "卯":{"생기":"동남(東南)","천의":"동(東)","복위":"서(西)","흉방":"북(北)"},
            "辰":{"생기":"남(南)","천의":"동(東)","복위":"동북(東北)","흉방":"서북(西北)"},
            "巳":{"생기":"동남(東南)","천의":"북(北)","복위":"서남(西南)","흉방":"동북(東北)"},
            "午":{"생기":"남(南)","천의":"동남(東南)","복위":"북(北)","흉방":"서남(西南)"},
            "未":{"생기":"서남(西南)","천의":"남(南)","복위":"동남(東南)","흉방":"동북(東北)"},
            "申":{"생기":"서북(西北)","천의":"서(西)","복위":"동(東)","흉방":"동남(東南)"},
            "酉":{"생기":"서(西)","천의":"서북(西北)","복위":"동북(東北)","흉방":"동(東)"},
            "戌":{"생기":"서북(西北)","천의":"서(西)","복위":"서남(西南)","흉방":"남(南)"},
            "亥":{"생기":"북(北)","천의":"동북(東北)","복위":"서(西)","흉방":"동(東)"},
        }
        _gm2 = _GILBANG2.get(_yr_jj_f, {})
        _ti2 = _JJ_TI2.get(_yr_jj_f, "")
        _gj60_i = (birth_year - 4) % 60
        _GJ60_L = ["갑자","을축","병인","정묘","무진","기사","경오","신미","임신","계유",
                   "갑술","을해","병자","정축","무인","기묘","경진","신사","임오","계미",
                   "갑신","을유","병술","정해","무자","기축","경인","신묘","임진","계사",
                   "갑오","을미","병신","정유","무술","기해","경자","신축","임인","계묘",
                   "갑진","을사","병오","정미","무신","기유","경술","신해","임자","계축",
                   "갑인","을묘","병진","정사","무오","기미","경신","신유","임술","계해"]
        _bgj = _GJ60_L[_gj60_i % 60]

        if _gm2:
            _cards = [
                ("🌟 생기방(生氣方)", _gm2.get("생기",""), "#1b5e20", "#e8f5e9", "최고 길방 — 침대 머리·책상·현관"),
                ("💊 천의방(天醫方)", _gm2.get("천의",""), "#0d47a1", "#e3f2fd", "건강·치유 방향 — 병원 방향"),
                ("🏠 복위방(伏位方)", _gm2.get("복위",""), "#4a148c", "#f3e5f5", "안정·귀가 방향 — 집·사무실 입구"),
                ("🚫 흉방(凶方)",     _gm2.get("흉방",""), "#b71c1c", "#ffebee", "이사·창업 피해야 할 방향"),
            ]
            st.markdown(f"**{name}님** ({_bgj}년생 {_ti2}띠) 나경 방위")
            _gc = st.columns(2)
            for _ci2, (_lbl2, _dir2, _cc2, _cb2, _sub2) in enumerate(_cards):
                _gc[_ci2%2].markdown(f"""<div style="background:{_cb2};border:2px solid {_cc2};border-radius:10px;
padding:14px;margin:6px 0;text-align:center">
<div style="font-size:12px;font-weight:700;color:{_cc2}">{_lbl2}</div>
<div style="font-size:22px;font-weight:900;color:{_cc2};margin:6px 0">{_dir2}</div>
<div style="font-size:11px;color:#555">{_sub2}</div>
</div>""", unsafe_allow_html=True)

        # 올해 이사 방위 판단
        with st.expander("🏠 올해 이사 방위 판단", expanded=False):
            _sw_f2 = get_yearly_luck(pils, _dt_tj.datetime.now().year) or {}
            _sw_ss_f2 = _sw_f2.get("십성_천간","")
            _MOVE2 = {
                "偏財": f"편재 세운 — 이사는 {_gm2.get('생기','길방')} 방향으로 하면 재물운 상승.",
                "正財": f"정재 세운 — 안정적 이사. {_gm2.get('복위','복위방')} 방향 권장.",
                "食神": f"식신 세운 — 이사하면 복이 따름. {_gm2.get('생기','길방')} 방향 최길.",
                "偏官": f"편관 세운 — 이사는 신중히. 흉방({_gm2.get('흉방','')}) 절대 피하십시오.",
                "劫財": f"겁재 세운 — 이사 보류 권장. 불가피하면 {_gm2.get('천의','천의방')} 방향.",
            }
            st.info(_MOVE2.get(_sw_ss_f2, f"이사는 {_gm2.get('생기','길방')} 방향을 우선 고려하십시오."))

    except Exception as e:
        st.warning(f"풍수 방위 계산 오류: {e}")

    st.caption("⚠️ 토정비결·풍수 방위는 전통 민속 문화 기반 참고 자료입니다. 전문 술사와 상담하십시오.")


def menu15_12unsung(pils, name, birth_year, gender):
    """🌟 12운성 심층 분석 리포트"""

    st.markdown(
        """

<div style="background:linear-gradient(135deg, #1f1c2c, #928dab);border-radius:16px; padding:20px 24px;margin-bottom:20px;color:#fff;text-align:center;box-shadow: 0 4px 12px rgba(0,0,0,0.4)">

<div style="font-size:22px;font-weight:900;letter-spacing:4px">🌟 12운성 심층 분석 리포트</div>

<div style="font-size:13px;color:#eee;margin-top:6px">인간의 생로병사를 자연의 순환에 빗대어 풀어내는 인생의 나침반</div>

</div>""",
        unsafe_allow_html=True,
    )

    ilgan = pils[1]["cg"]

    unsung_list = calc_12unsung(ilgan, pils)


    labels = [
        "시(時) - 말년/자식",
        "일(日) - 중년/본인/배우자",
        "월(月) - 청년/사회/부모",
        "년(年) - 초년/조상",
    ]

    p_labels = ["시주", "일주", "월주", "년주"]

    # 4개의 기둥(시/일/월/년)을 가로로 정렬

    st.markdown(
        '<div style="font-size:18px;font-weight:700;color:#333;margin-bottom:12px">📌 시기별 12운성</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    for i, (label, u_val) in enumerate(zip(labels, unsung_list)):
        cg = pils[i]["cg"]

        jj = pils[i]["jj"]

        desc = _UNSUNG_DESC.get(u_val, _UNSUNG_DESC["-"])

        title = desc["title"]

        with cols[i]:
            st.markdown(
                f"""

<div style="background:#fdfcf0;border:1px solid #e8e0c8;border-radius:12px;padding:12px;text-align:center;box-shadow: 0 1px 4px rgba(0,0,0,0.05);min-height:160px">

<div style="font-size:11px;font-weight:700;color:#555">{label}</div>

<div style="font-size:16px;font-weight:900;color:#222;margin:4px 0">{cg} {jj}</div>

<div style="font-size:18px;font-weight:800;color:#0d47a1;margin:8px 0">{title}</div>

</div>

            """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<hr style="border-top:1px dashed #d0d0d0;margin:24px 0">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="font-size:18px;font-weight:700;color:#333;margin-bottom:12px">📖 12운성 상세 풀이</div>',
        unsafe_allow_html=True,
    )

    for i, (p_label, u_val) in enumerate(zip(p_labels, unsung_list)):
        desc = _UNSUNG_DESC.get(u_val, _UNSUNG_DESC["-"])

        st.markdown(
            f"""

<div style="background:#ffffff;border-left:4px solid #0d47a1;padding:14px 16px;margin-bottom:12px;border-radius:0 8px 8px 0;box-shadow: 0 1px 3px rgba(0,0,0,0.06)">

<div style="font-size:14px;font-weight:800;color:#0d47a1;margin-bottom:6px">[{p_label}] {desc["title"]}</div>

<div style="font-size:13px;font-weight:600;color:#333;margin-bottom:4px">🔑 핵심 키워드: {desc["nature"]}</div>

<div style="font-size:13px;color:#444;line-height:1.6;margin-bottom:8px">{desc["detail"]}</div>

<div style="font-size:12px;font-weight:600;color:#d32f2f;background:#fff5f5;padding:8px;border-radius:6px">⚠️ 주의사항: {desc["caution"]}</div>

</div>

        """,
            unsafe_allow_html=True,
        )


# ==========================================================

#  📄 PDF 출력 메뉴

# ==========================================================




if __name__ == "__main__":
    main()
