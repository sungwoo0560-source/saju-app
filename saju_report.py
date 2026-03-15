# -*- coding: utf-8 -*-
"""
saju_report.py - PDF 리포트 생성 모듈
menu_pdf 포함
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
import io
import re
import base64
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
from saju_engine import *
from saju_sinsal import *
from saju_interpreter import *
from saju_ui import *

try:
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

_saju_log = _logging.getLogger("saju")

def menu_pdf(pils, birth_year, gender, name="내담자", birth_hour_str=""):
    """📄 PDF 출력 - 사주 천명 리포트 다운로드"""

    from datetime import datetime as _dt

    st.markdown(
        """

<div style="background:linear-gradient(135deg,#1a1a1a,#333);border-radius:16px; padding:20px 24px;margin-bottom:20px;color:#f7e695;text-align:center">

<div style="font-size:22px;font-weight:900;letter-spacing:4px">📄 사주 천명 리포트 PDF 출력</div>

<div style="font-size:13px;color:#ccc;margin-top:6px">아래 설정 후 생성 버튼을 누르면 PDF를 다운로드합니다</div>

</div>""",
        unsafe_allow_html=True,
    )

    # -- 출력 섹션 선택 --

    col1, col2 = st.columns(2)

    with col1:
        include_basic = st.checkbox("사주 기본 정보 (팔자/오행)", value=True, key="pdf_basic")

        include_yongshin = st.checkbox("용신/격국 상세 분석", value=True, key="pdf_yong")

        include_past = st.checkbox("과거 적중 (상세 서술)", value=True, key="pdf_past")

        include_dw = st.checkbox("대운 흐름 (10년 단위)", value=True, key="pdf_dw")

        include_current = st.checkbox("현재 운세 분석 (올해/내년)", value=True, key="pdf_current")

        include_future = st.checkbox("미래 5년 운세 흐름", value=True, key="pdf_future")

    with col2:
        include_ss = st.checkbox("십성 분포 분석", value=True, key="pdf_ss")

        include_sinsal = st.checkbox("신살 분석", value=True, key="pdf_sinsal")

        include_yukjin = st.checkbox("육친 분석", value=True, key="pdf_yukjin")

        include_fortune = st.checkbox("AI 종합운세 (전문 분석)", value=True, key="pdf_fortune")

        include_advice = st.checkbox("처방/조언", value=True, key="pdf_advice")

    if st.button("📥 PDF 생성 및 다운로드", use_container_width=True, key="pdf_gen_btn"):
        try:
            from reportlab.lib.pagesizes import A4

            from reportlab.lib.units import mm

            from reportlab.pdfgen import canvas

            from reportlab.pdfbase.ttfonts import TTFont

            from reportlab.pdfbase import pdfmetrics

            from reportlab.lib import colors

            # -- 폰트 등록: 한글/한자 지원 우선순위 --

            _FONT_CANDIDATES = [
                # Windows
                ("Malgun",      "C:/Windows/Fonts/malgun.ttf",    None),
                ("Batang",      "C:/Windows/Fonts/batang.ttc",     0),
                ("Gulim",       "C:/Windows/Fonts/gulim.ttc",      0),
                ("Dotum",       "C:/Windows/Fonts/dotum.ttc",      0),
                ("Malgun2",     "C:/Windows/Fonts/malgunbd.ttf",   None),
                ("NanumGothicW", os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/NanumGothic.ttf"), None),
                ("NanumGothic2", "C:/Windows/Fonts/NanumGothic.ttf", None),
                # Linux (Streamlit Cloud / Ubuntu)
                ("NanumGothic",  "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",      None),
                ("NanumGothicB", "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",  None),
                ("UnDotum",      "/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf",   None),
                ("BaekmukGulim", "/usr/share/fonts/truetype/baekmuk/gulim.ttf",          None),
                # 프로젝트 내 폰트 (repo에 추가 시)
                ("LocalFont",    os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf"), None),
            ]

            BASE_FONT = "Helvetica"

            for _fn, _fp, _fi in _FONT_CANDIDATES:
                if os.path.exists(_fp):
                    try:
                        if _fi is not None:
                            pdfmetrics.registerFont(TTFont(_fn, _fp, subfontIndex=_fi))

                        else:
                            pdfmetrics.registerFont(TTFont(_fn, _fp))

                        BASE_FONT = _fn

                        break

                    except Exception as e:
                        pass  # 다음 폰트 시도

            if BASE_FONT == "Helvetica":
                st.warning("⚠️ 한글 폰트를 찾지 못했습니다. PDF에 한글이 정상 출력되지 않을 수 있습니다. malgun.ttf 또는 Batang 폰트를 설치해주세요.")

            buf = io.BytesIO()

            c = canvas.Canvas(buf, pagesize=A4)

            W, H = A4

            MARGIN = 22 * mm

            BOT = 22 * mm  # 하단 여백

            y = H - 24 * mm  # 시작 y 위치

            def draw_line(c, y, color=(0.8, 0.7, 0.2), width=0.5):

                c.setStrokeColorRGB(*color)

                c.setLineWidth(width)

                c.line(MARGIN, y, W - MARGIN, y)

                return y - 3 * mm

            def new_page(c):

                c.showPage()

                return H - 24 * mm

            # 비BMP 이모지 + 특수기호 → PDF 안전 텍스트 변환


            # BMP 범위 특수기호 변환 (PDF 폰트 미지원 문자 대비)

            # ★ FIX: 한글 폰트(Malgun 등)도 ■/◆/▶ 등 특수기호를 지원하지 않으므로

            #        BASE_FONT 종류에 관계없이 항상 치환 적용


            def _safe_text(text):
                """비BMP 이모지 + 특수기호를 PDF 안전 텍스트로 변환

                ★ FIX: 한글 폰트도 ■/◆ 미지원이므로 항상 치환

                """

                result = []

                for ch in text or "":
                    o = ord(ch)

                    if o > 0xFFFF:
                        # 4바이트 이모지 → 맵에서 찾거나 빈 문자열

                        result.append(_EMOJI_MAP.get(ch, ""))

                    elif ch in _EMOJI_MAP:
                        result.append(_EMOJI_MAP[ch])

                    elif ch in _SYMBOL_MAP:
                        # ★ 항상 치환 (폰트 종류 무관) - Malgun도 ■/◆ 미지원

                        result.append(_SYMBOL_MAP[ch])

                    else:
                        result.append(ch)

                return "".join(result)

            def write(
                c,
                text,
                y,
                font=BASE_FONT,
                size=12,
                color=(0.1, 0.1, 0.1),
                indent=0,
                line_h=7.2,
            ):

                if y < BOT:
                    y = new_page(c)

                c.setFont(font, size)

                c.setFillColorRGB(*color)

                max_w = W - 2 * MARGIN - indent

                lines = []

                for raw in _safe_text(text or "").split("\n"):
                    if not raw.strip():
                        lines.append("")
                        continue

                    while raw:
                        if c.stringWidth(raw, font, size) <= max_w:
                            lines.append(raw)
                            break

                        lo, hi = 1, len(raw)

                        while lo < hi - 1:
                            mid = (lo + hi) // 2

                            if c.stringWidth(raw[:mid], font, size) <= max_w:
                                lo = mid

                            else:
                                hi = mid

                        bp = lo

                        sp = raw.rfind(" ", 0, bp + 1)

                        if sp > 0:
                            bp = sp

                        lines.append(raw[:bp])

                        raw = raw[bp:].lstrip()

                for ln in lines:
                    if y < BOT:
                        y = new_page(c)

                    c.drawString(MARGIN + indent, y, ln)

                    y -= line_h * mm

                return y

            def section_title(c, text, y):

                if y < 42 * mm:
                    y = new_page(c)

                # 골드 배경 바

                c.setFillColorRGB(0.15, 0.12, 0.05)

                c.rect(
                    MARGIN - 3 * mm,
                    y - 2 * mm,
                    W - 2 * MARGIN + 6 * mm,
                    9 * mm,
                    fill=1,
                    stroke=0,
                )

                c.setFillColorRGB(0.97, 0.88, 0.38)

                c.setFont(BASE_FONT, 14)

                c.drawString(MARGIN + 1 * mm, y + 1.5 * mm, text)

                y -= 11 * mm

                return y

            def subsection(c, text, y):
                """소제목 (이탤릭 느낌의 구분선)"""

                if y < BOT:
                    y = new_page(c)

                c.setFillColorRGB(0.25, 0.18, 0.05)

                c.setFont(BASE_FONT, 12)

                c.drawString(MARGIN, y, f"◆ {text}")

                y -= 6.5 * mm

                c.setStrokeColorRGB(0.75, 0.65, 0.25)

                c.setLineWidth(0.3)

                c.line(MARGIN, y + 1 * mm, W - MARGIN, y + 1 * mm)

                y -= 2 * mm

                return y

            import re as _re_pdf

            def _clean_narrative_for_pdf(cv, raw_text, y_start):
                """HTML/마크다운 정제 후 챕터·카테고리별로 subsection/write 처리"""

                # 1. HTML 태그 제거

                txt = _re_pdf.sub(r"<[^>]+>", "", raw_text or "")

                # 2. 마크다운 강조 기호 제거

                txt = _re_pdf.sub(r"\*{2,3}([^*\n]+)\*{2,3}", r"\1", txt)

                txt = _re_pdf.sub(r"\*([^*\n]+)\*", r"\1", txt)

                txt = _re_pdf.sub(r"_{2}([^_\n]+)_{2}", r"\1", txt)

                txt = _re_pdf.sub(r"_([^_\n]+)_", r"\1", txt)

                txt = _re_pdf.sub(r"^#{1,6}\s+", "", txt, flags=_re_pdf.MULTILINE)

                txt = _re_pdf.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", txt)  # [text](url)

                # 3. 구분선(---/===) 제거

                txt = _re_pdf.sub(r"^[-=─]{3,}\s*$", "", txt, flags=_re_pdf.MULTILINE)

                # 4. 연속 공백/빈줄 정리

                txt = _re_pdf.sub(r"[ \t]+", " ", txt)

                txt = _re_pdf.sub(r"\n{3,}", "\n\n", txt).strip()

                # 챕터 제목 패턴: [ 제N장 ... ] 또는 [ 제N장 | 부제 ]

                _chap_pat = _re_pdf.compile(r"^\s*\[\s*(제\s*\d+\s*[장절][^\]]{0,60})\s*\]\s*$")

                # 카테고리 레이블 패턴: [직업]: 내용

                _cat_pat = _re_pdf.compile(r"^\s*\[([가-힣\w]{1,12})\]\s*[:：]\s*(.*)$")

                # 불릿 패턴: * 내용 또는 - 내용

                _bullet_pat = _re_pdf.compile(r"^\s*[*\-•]\s+(.+)$")

                y = y_start

                _buf = []

                def _flush():

                    nonlocal y, _buf

                    if _buf:
                        combined = "\n".join(_buf).strip()

                        if combined:
                            y = write(cv, combined, y, size=12, line_h=7.5)

                        _buf = []

                for line in txt.split("\n"):
                    line = line.rstrip()

                    # 챕터 제목

                    m = _chap_pat.match(line)

                    if m:
                        _flush()

                        y = subsection(cv, m.group(1).strip(), y)

                        continue

                    # 카테고리 레이블 [직업]: ...

                    m = _cat_pat.match(line)

                    if m:
                        _flush()

                        label_text = f"[{m.group(1)}]  {m.group(2).strip()}"

                        y = write(
                            cv,
                            label_text,
                            y,
                            size=11,
                            color=(0.12, 0.22, 0.48),
                            line_h=7,
                        )

                        continue

                    # 불릿 포인트

                    m = _bullet_pat.match(line)

                    if m:
                        _flush()

                        y = write(
                            cv,
                            f"  • {m.group(1).strip()}",
                            y,
                            size=11,
                            color=(0.2, 0.2, 0.2),
                            line_h=7,
                        )

                        continue

                    # 빈 줄

                    if line.strip() == "":
                        _flush()

                        y -= 1.5 * mm

                        continue

                    _buf.append(line)

                _flush()

                return y

            # == 표지 ==

            c.setFillColorRGB(0.05, 0.05, 0.05)

            c.rect(0, H - 55 * mm, W, 55 * mm, fill=1, stroke=0)

            c.setFillColorRGB(0.97, 0.90, 0.42)

            c.setFont(BASE_FONT, 24)

            c.drawCentredString(W / 2, H - 28 * mm, "만신 사주 천명풀이")

            c.setFillColorRGB(0.85, 0.85, 0.85)

            c.setFont(BASE_FONT, 11)

            c.drawCentredString(W / 2, H - 36 * mm, "사주팔자 / 천명을 밝히다")

            c.setFillColorRGB(0.7, 0.7, 0.7)

            c.setFont(BASE_FONT, 9)

            c.drawCentredString(
                W / 2,
                H - 44 * mm,
                f"출력일: {_dt.now().strftime('%Y년 %m월 %d일 %H:%M')}",
            )

            y = H - 62 * mm

            # -- 이름/생년월일 --

            y = write(
                c,
                f"대상: {name}  |  성별: {gender}  |  출생연도: {birth_year}년",
                y,
                size=11,
                color=(0.2, 0.2, 0.2),
            )

            y -= 3 * mm

            ilgan = pils[1]["cg"]

            birth_month  = max(1, min(12, int(st.session_state.get("birth_month") or 1)))

            birth_day    = max(1, min(31, int(st.session_state.get("birth_day")   or 1)))

            birth_hour   = max(0, min(23, int(st.session_state.get("birth_hour")  or 12)))

            birth_minute = max(0, min(59, int(st.session_state.get("birth_minute") or 0)))

            # == 1. 사주 기본 정보 ==

            if include_basic:
                y = section_title(c, "사주 팔자", y)

                pil_names = ["연주(年柱)", "월주(月柱)", "일주(日柱)", "시주(時柱)"]

                # get_pillars returns [시, 일, 월, 연] -> Reverse for [연, 월, 일, 시] labeling

                for i, (pn, p) in enumerate(zip(pil_names, pils[::-1])):
                    cg_oh = OHN.get(OH.get(p["cg"], ""), "")

                    jj_oh = OHN.get(OH.get(p["jj"], ""), "")

                    y = write(
                        c,
                        f"  {pn}: {p['cg']} ({cg_oh})  {p['jj']} ({jj_oh})",
                        y,
                        size=10,
                    )

                y -= 3 * mm

                # 오행 분포

                oh_count = {}

                for p in pils:
                    for ch in [p["cg"], p["jj"]]:
                        o = OH.get(ch, "")

                        if o:
                            oh_count[o] = oh_count.get(o, 0) + 1

                oh_str = "  ".join([f"{OHN.get(o, o)} {v}개" for o, v in oh_count.items()])

                y = write(c, f"오행 분포: {oh_str}", y, size=10)

                # ── 오행 분포 바 차트 ──

                _oh_s = calc_ohaeng_strength(pils[1]["cg"], pils)

                _oh_ord = ["木", "火", "土", "金", "水"]

                _oh_rgb = {
                    "木": (0.18, 0.65, 0.18),
                    "火": (0.90, 0.22, 0.22),
                    "土": (0.85, 0.55, 0.10),
                    "金": (0.55, 0.55, 0.55),
                    "水": (0.13, 0.53, 0.87),
                }

                _oh_lbl = {
                    "木": "목(木)",
                    "火": "화(火)",
                    "土": "토(土)",
                    "金": "금(金)",
                    "水": "수(水)",
                }

                _cw = W - 2 * MARGIN

                _bw = _cw / 5 - 3 * mm

                _bmax_h = 32 * mm

                if y < _bmax_h + 18 * mm:
                    c.showPage()
                    y = H - 20 * mm

                _base_y = y - _bmax_h - 5 * mm

                for _i, _oh in enumerate(_oh_ord):
                    _val = _oh_s.get(_oh, 0)

                    _bh = _bmax_h * _val / 100

                    _bx = MARGIN + _i * (_cw / 5)

                    c.setFillColorRGB(*_oh_rgb[_oh])

                    c.rect(_bx + 1 * mm, _base_y, _bw, _bh, fill=1, stroke=0)

                    c.setFillColorRGB(0.15, 0.15, 0.15)

                    c.setFont(BASE_FONT, 8)

                    c.drawCentredString(_bx + 1 * mm + _bw / 2, _base_y + _bh + 1.5 * mm, f"{_val}%")

                    c.setFont(BASE_FONT, 7)

                    c.drawCentredString(_bx + 1 * mm + _bw / 2, _base_y - 4 * mm, _oh_lbl[_oh])

                c.setStrokeColorRGB(0.75, 0.75, 0.75)

                c.setLineWidth(0.5)

                c.line(MARGIN, _base_y, W - MARGIN, _base_y)

                y = _base_y - 8 * mm

            # == 2. 용신/격국 상세 분석 ==

            if include_yongshin:
                y = section_title(c, "용신 / 격국 / 신강신약 — 천명의 설계도", y)

                _gk = get_gyeokguk(pils)

                _ys_ml = get_yongshin_multilayer(pils, birth_year, gender, _dt.now().year)

                _si = get_ilgan_strength(ilgan, pils)

                _gkname = _gk["격국명"] if _gk else "미정격"

                _gkgrade = _gk.get("격의_등급", "") if _gk else ""

                _sn = _si["신강신약"]

                _score = _si.get("일간점수", 50)

                _yong1 = _ys_ml.get("용신_1순위", "-")

                _yong2 = _ys_ml.get("용신_2순위", "-")

                _heui = _ys_ml.get("희신", "-")

                _gisin = ", ".join(_ys_ml.get("기신", []))

                _dw_interp = _ys_ml.get("대운_해석", "")

                # 격국 서술

                _GK_NARR = {
                    "정관격": "정관격(正官格)은 규칙과 질서를 중시하며 조직에서 빛을 발하는 격국이니라. 명예와 체면을 소중히 여기고 공직·관리직·교육직에서 크게 성취하는 팔자니라. 이 격은 법도를 지키는 것이 곧 발복(發福)의 열쇠이니, 편법과 요행은 이 팔자에 어울리지 않느니라.",
                    "편관격": "편관격(偏官格)은 강인한 의지와 도전 정신이 핵심이니라. 칠살격(七殺格)이라고도 하며, 제화(制化)가 되면 영웅의 팔자요, 안 되면 파란만장한 고난의 팔자니라. 군경·의료·법조·스포츠처럼 강인함이 요구되는 분야에서 진가를 발휘하느니라.",
                    "정재격": "정재격(正財格)은 성실함과 꾸준함으로 재물을 쌓는 격국이니라. 한 푼 두 푼 모아 큰 부를 이루는 타입으로, 금융·회계·유통·부동산에서 두각을 나타내느니라. 갑작스러운 횡재보다는 땀의 대가가 인생을 풍요롭게 하느니라.",
                    "편재격": "편재격(偏財格)은 사업가 기질이 넘치는 격국이니라. 아버지 인연과 이성 인연이 굵직하며, 투자·무역·영업·자영업에서 두각을 나타내느니라. 편재는 움직이는 돈이라, 항상 유동적이고 과감한 결정이 필요하느니라.",
                    "식신격": "식신격(食神格)은 복록(福祿)이 넘치는 격국이니라. 먹을 복, 직업 복, 자식 복이 함께하며 창작·예술·요리·교육·서비스 분야에서 자연스럽게 빛을 발하느니라. 이 격은 억지로 밀어붙이기보다 흐름에 맡겨야 복이 흘러들어오느니라.",
                    "상관격": "상관격(傷官格)은 재기(才氣)와 창의성이 폭발하는 격국이니라. 규칙에 얽매이지 않는 자유로운 영혼으로 IT·예술·방송·컨설팅에서 독보적 존재가 되느니라. 다만 윗사람과의 마찰을 조심하고 언어를 조심해야 하느니라.",
                    "편인격": "편인격(偏印格)은 학문과 연구에 뛰어난 격국이니라. 철학·역술·의학·IT·연구직에서 독보적인 전문성을 쌓아가느니라. 계획이 자주 바뀌고 이사나 직업 변동이 잦을 수 있으나, 그 모든 경험이 결국 깊은 내공으로 쌓이느니라.",
                    "정인격": "정인격(正印格)은 학문과 자격의 격국이니라. 어머니의 음덕이 크고 교육·학술·자격 기반의 전문직에서 평생 성장하느니라. 성실히 배우고 익히는 것이 이 팔자의 발복 비결이니라.",
                    "비견격": "비견격(比肩格)은 독립심과 자존심이 강한 격국이니라. 자수성가형으로 독립사업·프리랜서·스포츠에서 진가를 발휘하느니라. 다만 재물이 손에 잡혀도 경쟁과 지출로 빠져나가기 쉬우니 저축 습관을 들이게.",
                    "겁재격": "겁재격(劫財格)은 강렬한 승부욕과 에너지를 가진 격국이니라. 영업·스포츠·투자·경쟁 분야에서 두각을 나타내지만, 재물이 들어오는 만큼 나가는 기운도 있으니 동업과 보증은 반드시 조심하게.",
                }

                _gk_desc = _GK_NARR.get(
                    _gkname,
                    f"{_gkname}은(는) 독특한 개성과 능력을 갖춘 격국이니라. 자신만의 방식으로 세상에 가치를 만들어내는 팔자니라.",
                )

                # 신강신약 서술

                _SN_NARR = {
                    "신강(身强)": "일간(日干)의 힘이 강하니라. 자기 주도적이고 추진력이 강하며, 스스로 움직여야 기회가 찾아오는 팔자니라. 다만 지나치게 강하면 독선이 되니, 용신으로 기운을 조율하는 것이 중요하느니라.",
                    "극신강(極身强)": "일간(日干)의 힘이 극도로 강하니라. 넘치는 에너지가 때로 독이 될 수 있느니라. 관살(官殺)로 제어하거나 재성(財星)으로 흘려보내야 이 강한 기운이 빛을 발하느니라.",
                    "신약(身弱)": "일간(日干)의 힘이 약하니라. 귀인과 함께할 때 가장 강해지는 팔자니라. 좋은 파트너, 훌륭한 스승과의 인연이 운명을 바꾸는 열쇠이며, 인성(印星) 대운에 크게 발복하느니라.",
                    "극신약(極身弱)": "일간(日干)의 힘이 극도로 약하니라. 오행의 도움이 절실히 필요한 팔자니라. 용신 오행을 철저히 활용하고, 무리한 독립 창업보다는 안정적인 조직 생활이 이 팔자에 맞느니라.",
                    "중화(中和)": "일간(日干)의 기운이 균형을 이루고 있느니라. 꾸준함과 성실함이 가장 큰 무기인 팔자니라. 한 분야를 깊이 파고드는 전략이 가장 효과적이며, 급격한 변화보다 점진적인 성장이 이 팔자의 발복 패턴이니라.",
                }

                _sn_desc = _SN_NARR.get(
                    _sn,
                    f"{_sn}의 기운을 가진 팔자니라. 용신 오행을 활용하여 균형을 잡는 것이 핵심이느니라.",
                )

                # 용신 활용 서술

                _OH_KR = {
                    "木": "목(木)",
                    "火": "화(火)",
                    "土": "토(土)",
                    "金": "금(金)",
                    "水": "수(水)",
                }

                _YONG_ADVICE = {
                    "木": "목(木) 용신이니라. 동쪽이 길방이요, 초록·파랑 계열의 색이 기운을 북돋아 주느니라. 식물을 가까이하고 봄에 중요한 결정을 내리는 것이 좋으니라.",
                    "火": "화(火) 용신이니라. 남쪽이 길방이요, 빨강·주황 계열의 색이 기운을 높여주느니라. 밝고 활기찬 환경에서 일하고 여름에 큰 결단을 내리게.",
                    "土": "토(土) 용신이니라. 중앙 또는 북동·남서 방향이 길방이요, 황토색·노랑 계열이 안정을 주느니라. 부동산·토지와 인연이 있으니 이쪽에 관심을 두어도 좋으니라.",
                    "金": "금(金) 용신이니라. 서쪽이 길방이요, 흰색·금색·은색 계열이 기운을 강화하느니라. 가을에 중요한 결정을 내리고 금속·철강 관련 분야와 인연이 있느니라.",
                    "水": "수(水) 용신이니라. 북쪽이 길방이요, 검정·남색·짙은 파랑 계열이 기운을 도와주느니라. 물 가까이 사는 것도 좋고 겨울에 지혜가 더욱 빛을 발하느니라.",
                }

                _yong_advice = _YONG_ADVICE.get(
                    _yong1,
                    f"{_yong1} 오행이 용신이니라. 이 오행을 일상에서 적극 활용하게.",
                )

                # 기신 경고

                _GISIN_WARN = {
                    "木": "기신(忌神)이 목(木) 기운이니 목 관련 해(寅(인)·卯(묘)년)에는 무리한 확장을 삼가게.",
                    "火": "기신이 화(火) 기운이니 화 관련 해(巳(사)·午(오)년)에는 심장·혈압 건강을 챙기고 충동적 결정을 자제하게.",
                    "土": "기신이 토(土) 기운이니 토 관련 해(辰(진)·戌(술)·丑(축)·未(미)년)에는 부동산 거래와 이사를 신중히 하게.",
                    "金": "기신이 금(金) 기운이니 금 관련 해(申(신)·酉(유)년)에는 수술·부상을 조심하고 투자를 자제하게.",
                    "水": "기신이 수(水) 기운이니 수 관련 해(亥(해)·子(자)년)에는 신장·방광 건강을 챙기고 유동성 투자를 줄이게.",
                }

                _gisin_warns = [_GISIN_WARN.get(g, f"{g} 기운이 흉하니 관련 해에 주의하게.") for g in _ys_ml.get("기신", [])]

                y = subsection(c, f"격국: {_gkname}  [{_gkgrade}]", y)

                y = write(c, _gk_desc, y, size=12, line_h=7.5)

                y -= 3 * mm

                y = subsection(c, f"신강신약: {_sn}  (일간 힘 점수 {_score}/100)", y)

                y = write(c, _sn_desc, y, size=12, line_h=7.5)

                y -= 3 * mm

                y = subsection(c, f"용신 · 희신 · 기신", y)

                y = write(
                    c,
                    f"용신 1순위: {_yong1}  |  2순위: {_yong2}  |  희신: {_heui}  |  기신: {_gisin}",
                    y,
                    size=12,
                )

                y = write(c, _yong_advice, y, size=12, line_h=7.5)

                if _gisin_warns:
                    for _gw in _gisin_warns:
                        y = write(
                            c,
                            f"  ⚠ {_gw}",
                            y,
                            size=11,
                            color=(0.6, 0.15, 0.1),
                            line_h=7,
                        )

                y -= 3 * mm

                if _dw_interp:
                    y = subsection(c, "현재 대운 해석", y)

                    y = write(c, f"  {_dw_interp}", y, size=12, line_h=7.5)

                y -= 3 * mm

                # -- 재물 황금기: 용신 오행이 세운 천간에 들어오는 해 (향후 20년) --

                _gold_yong_ohs = set()

                for _goh in [_yong1, _yong2]:
                    if _goh and _goh in ("木", "火", "土", "金", "水"):
                        _gold_yong_ohs.add(_goh)

                if _gold_yong_ohs:
                    _cy_gold = _dt.now().year

                    _gold_years = []

                    for _gy in range(_cy_gold, _cy_gold + 21):
                        _gsw = get_yearly_luck(pils, _gy)

                        _gsw_cg = (_gsw.get("세운") or "")[:1]

                        _gsw_oh = OH.get(_gsw_cg, "")

                        if _gsw_oh in _gold_yong_ohs:
                            _gage = _gy - birth_year + 1

                            _gss = _gsw.get("십성_천간", "")

                            _ggh = _gsw.get("길흉", "")

                            _is_jae = _gss in ("偏財", "正財")

                            _star = "★★" if _is_jae else "★"

                            _gold_years.append(f"{_gy}년 ({_gage}세): {_gsw.get('세운', '')} [{_gss}] {_ggh}  {_star}")

                    if _gold_years:
                        y = subsection(
                            c,
                            f"향후 20년 재물 황금기 — 용신({_yong1}) 세운 진입 연도",
                            y,
                        )

                        y = write(
                            c,
                            "  용신 오행이 세운 천간에 들어오는 해는 재물·성취 에너지가 극대화되는 시기니라.",
                            y,
                            size=11,
                            color=(0.35, 0.22, 0.0),
                            line_h=7,
                        )

                        y = write(
                            c,
                            "  (★★ = 재성 세운으로 재물 직접 활성화)",
                            y,
                            size=10,
                            color=(0.45, 0.28, 0.0),
                            line_h=6.5,
                        )

                        for _gy_str in _gold_years:
                            y = write(
                                c,
                                f"  {_gy_str}",
                                y,
                                size=11,
                                color=(0.48, 0.28, 0.02),
                                line_h=7,
                            )

                        y -= 3 * mm

                y -= 2 * mm

            # == 3. 십성 분포 분석 ==

            if include_ss:
                y = section_title(c, "십성 분포 분석", y)

                _pil_names = ["시주", "일주", "월주", "년주"]

                _ss_count = {}

                for _i, p in enumerate(pils):
                    ss_cg = TEN_GODS_MATRIX.get(ilgan, {}).get(p["cg"], "-")

                    ss_jj_list = JIJANGGAN.get(p["jj"], [])

                    ss_jj = TEN_GODS_MATRIX.get(ilgan, {}).get(ss_jj_list[-1] if ss_jj_list else "", "-")

                    y = write(
                        c,
                        f"  {_pil_names[_i]} {p['str']}: 천간 {ss_cg}  지지 {ss_jj}",
                        y,
                        size=10,
                    )

                    for _s in [ss_cg, ss_jj]:
                        if _s and _s != "-":
                            _ss_count[_s] = _ss_count.get(_s, 0) + 1

                _ss_summary = "  ".join([f"{k}×{v}" for k, v in sorted(_ss_count.items(), key=lambda x: -x[1])])

                y = write(
                    c,
                    f"  [십성 집계] {_ss_summary}",
                    y,
                    size=9,
                    color=(0.35, 0.35, 0.35),
                )

                y -= 4 * mm

            # == 3-B. 과거 적중 상세 서술 ==

            if include_past:
                y = section_title(c, "과거 사건 적중 — 신안으로 본 지나온 인생", y)

                import re as _re2

                try:
                    # 1순위: AI 캐시에서 과거 분석 텍스트 가져오기

                    _sk = pils_to_cache_key(pils)

                    _past_ai = get_ai_cache(_sk, "past") or ""

                    if _past_ai:
                        _past_clean = _re2.sub(r"<[^>]+>", "", _past_ai)

                        _past_clean = _re2.sub(r"\n{3,}", "\n\n", _past_clean).strip()

                        y = write(c, _past_clean, y, size=12, line_h=7.5)

                    else:
                        # 2순위: engine highlights + 대운×세운 교차로 상세 서술 생성

                        _hl = generate_engine_highlights(pils, birth_year, gender)

                        _pevs = sorted(
                            _hl.get("past_events", []),
                            key=lambda e: {"🔴": 0, "🟡": 1, "🟢": 2}.get(e.get("intensity", "🟢"), 3),
                        )

                        _current_y = _dt.now().year

                        _DOM_DETAIL = {
                            "직업변화": "직업 또는 직장에 큰 변동이 찾아왔느니라. 이직·부서 이동·창업 중 하나가 일어났을 것이니라.",
                            "결혼·교제": "인연의 기운이 강하게 들어왔느니라. 새로운 이성과의 만남이나 결혼·이별 중 하나가 있었느니라.",
                            "이사·이동": "삶의 터전이 흔들리는 시기니라. 이사·이민·장거리 이동의 기운이 강하게 들어왔느니라.",
                            "재물획득": "재물이 크게 들어오는 시기니라. 수입 증가·투자 성공·뜻밖의 횡재 중 하나가 있었느니라.",
                            "재물손실": "재물이 빠져나가는 시기니라. 지출 증가·투자 손실·보증·사기 중 하나가 있었느니라. 돌아보면 그때 조심해야 했느니라.",
                            "사고·관재": "위험한 기운이 들어온 시기니라. 사고·부상·법적 문제 중 하나가 발생했을 가능성이 높느니라.",
                            "질병·건강": "몸의 기운이 약해지는 시기니라. 건강 이상 신호나 수술·입원 중 하나가 있었느니라.",
                            "변화": "전반적으로 변화의 기운이 강했던 시기니라. 삶의 여러 방면에서 크고 작은 변화가 있었느니라.",
                        }

                        _SS_EVENT = {
                            "偏財": "편재(偏財) 기운이 활성화되어 재물 변동과 아버지 이슈, 이성 인연이 두드러졌느니라.",
                            "正財": "정재(正財) 기운이 들어와 안정적 수입 변화와 결혼·재산 형성의 기운이 작동했느니라.",
                            "食神": "식신(食神)이 빛을 발하여 직업 변화와 건강 이슈가 두드러졌느니라.",
                            "傷官": "상관(傷官)이 활성화되어 직장 마찰·이직·구설수의 기운이 강했느니라.",
                            "偏官": "편관(偏官)이 들어와 직장 변동과 사고·관재 기운이 강하게 작동했느니라.",
                            "正官": "정관(正官)의 기운으로 승진·결혼·명예와 관련된 변화가 있었느니라.",
                            "偏印": "편인(偏印)이 활성화되어 학업 중단·이사·계획 변경의 기운이 들어왔느니라.",
                            "正印": "정인(正印)의 기운으로 학업 성취·자격 취득·어머니 관련 사건이 있었느니라.",
                            "比肩": "비견(比肩)이 강해져 독립심과 경쟁이 극대화된 시기니라.",
                            "劫財": "겁재(劫財)가 들어와 재물 손실·형제 갈등·독립·창업의 기운이 강했느니라.",
                        }

                        if not _pevs:
                            y = write(
                                c,
                                "  허허, 이 시기에는 특별한 강한 사건의 기운이 감지되지 않는구먼. 비교적 평온한 흐름이었느니라.",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                        else:
                            for _ev in _pevs:
                                _itn = _ev.get("intensity", "🟢")

                                _yr = _ev.get("year", "")

                                _age = _ev.get("age", "")

                                _dom = _ev.get("domain", "변화")

                                _desc = _ev.get("desc", "")

                                _yr_int = int(_yr) if str(_yr).isdigit() else 0

                                # 제목 줄

                                _itn_label = {
                                    "🔴": "[강도: 최고]",
                                    "🟡": "[강도: 중]",
                                    "🟢": "[강도: 보통]",
                                }.get(_itn, "")

                                y = write(
                                    c,
                                    f"{_yr}년 ({_age})  {_itn_label}  [{_dom}]",
                                    y,
                                    size=13,
                                    color=(0.1, 0.1, 0.4),
                                )

                                y -= 1 * mm

                                # 기본 설명

                                _dom_detail = _DOM_DETAIL.get(_dom, _DOM_DETAIL["변화"])

                                y = write(c, f"  {_desc}", y, size=12, line_h=7.5)

                                y = write(
                                    c,
                                    f"  {_dom_detail}",
                                    y,
                                    size=11,
                                    color=(0.3, 0.3, 0.3),
                                    line_h=7,
                                )

                                # 대운×세운 교차 분석 추가

                                if _yr_int > 0:
                                    try:
                                        _cross = get_daewoon_sewoon_cross(pils, birth_year, gender, _yr_int)

                                        if _cross:
                                            _dw_s = _cross["대운"].get("str", "")

                                            _sw_s = _cross["세운"].get("세운", "")

                                            _dw_ss_c = _cross.get("대운_천간십성", "-")

                                            _sw_ss_c = _cross.get("세운_천간십성", "-")

                                            _interp = _cross.get("교차해석", "")

                                            _ss_ev = _SS_EVENT.get(_dw_ss_c, "") or _SS_EVENT.get(_sw_ss_c, "")

                                            y = write(
                                                c,
                                                f"  [명리 근거] {_dw_s} 대운({_dw_ss_c}) × {_sw_s} 세운({_sw_ss_c})",
                                                y,
                                                size=11,
                                                color=(0.2, 0.3, 0.5),
                                                line_h=7,
                                            )

                                            if _ss_ev:
                                                y = write(
                                                    c,
                                                    f"  {_ss_ev}",
                                                    y,
                                                    size=11,
                                                    color=(0.2, 0.3, 0.5),
                                                    line_h=7,
                                                )

                                            if _interp:
                                                y = write(
                                                    c,
                                                    f"  {_interp}",
                                                    y,
                                                    size=11,
                                                    color=(0.2, 0.3, 0.5),
                                                    line_h=7,
                                                )

                                            for _ce in _cross.get("교차사건", []):
                                                y = write(
                                                    c,
                                                    f"  ◦ {_ce['desc']}",
                                                    y,
                                                    size=11,
                                                    color=(0.5, 0.15, 0.1),
                                                    line_h=7,
                                                )

                                    except Exception as e:
                                        import logging as _rlog
                                        _rlog.getLogger("saju").warning("[PDF 오류] %s", e)

                                y -= 4 * mm

                except Exception as _pe:
                    y = write(c, f"  (과거 사건 계산 불가: {_pe})", y, size=11)

                y -= 4 * mm

            # == 4. 대운 흐름 ==

            if include_dw:
                y = section_title(c, "대운 흐름 (10년 단위)", y)

                current_year = _dt.now().year

                daewoon = SajuCoreEngine.get_daewoon(
                    pils,
                    birth_year,
                    birth_month,
                    birth_day,
                    birth_hour,
                    birth_minute,
                    gender,
                )

                ys2 = get_yongshin(pils)

                yongshin_ohs = ys2.get("종합_용신", [])

                ilgan_oh = OH.get(ilgan, "")

                for dw in daewoon[:10]:
                    dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(dw["cg"], "-")

                    is_cur = dw["시작연도"] <= current_year <= dw["종료연도"]

                    is_yong = get_yongshin_match(dw_ss, yongshin_ohs, ilgan_oh) == "yong"

                    cur_mark = " ◀현재" if is_cur else ""

                    yong_mark = " *용신" if is_yong else ""

                    presc = DAEWOON_PRESCRIPTION.get(dw_ss, "")

                    y = write(
                        c,
                        f"  {dw['시작나이']}~{dw['시작나이'] + 9}세  {dw['str']} ({dw_ss}){cur_mark}{yong_mark}",
                        y,
                        size=10,
                    )

                    if presc:
                        y = write(c, f"    -> {presc}", y, size=9, color=(0.4, 0.4, 0.4))

                # ── 대운 흐름 가로 막대 그래프 ──

                _DW_SC = {
                    "正財": 80,
                    "食神": 85,
                    "正官": 75,
                    "正印": 70,
                    "偏財": 65,
                    "偏官": 40,
                    "劫財": 35,
                    "傷官": 55,
                    "比肩": 60,
                    "偏印": 50,
                }

                _lbl_w = 30 * mm

                _gw = W - 2 * MARGIN - _lbl_w - 4 * mm

                _bh1 = 6.5 * mm

                _gap = 1.8 * mm

                _dw10 = daewoon[:10]

                _need = len(_dw10) * (_bh1 + _gap) + 14 * mm

                if y < _need:
                    c.showPage()
                    y = H - 20 * mm

                _top = y - 2 * mm

                for _j, _dw in enumerate(_dw10):
                    _dss = TEN_GODS_MATRIX.get(ilgan, {}).get(_dw["cg"], "-")

                    _ic = _dw["시작연도"] <= current_year <= _dw["종료연도"]

                    _iy = get_yongshin_match(_dss, yongshin_ohs, ilgan_oh) == "yong"

                    _sc = min(100, _DW_SC.get(_dss, 60) + (20 if _iy else 0))

                    _by = _top - _j * (_bh1 + _gap)

                    if _ic:
                        _rgb = (1.0, 0.55, 0.0)

                    elif _iy:
                        _rgb = (0.83, 0.68, 0.21)

                    elif _sc < 50:
                        _rgb = (0.96, 0.60, 0.60)

                    else:
                        _rgb = (0.63, 0.77, 0.97)

                    c.setFillColorRGB(0.15, 0.15, 0.15)

                    c.setFont(BASE_FONT, 7)

                    c.drawString(
                        MARGIN,
                        _by - _bh1 + 1.5 * mm,
                        f"{_dw['시작나이']}세 {_dw['str']} {_dss}",
                    )

                    _bl = _gw * _sc / 100

                    c.setFillColorRGB(*_rgb)

                    c.rect(
                        MARGIN + _lbl_w,
                        _by - _bh1 + 0.5 * mm,
                        _bl,
                        _bh1 - 1 * mm,
                        fill=1,
                        stroke=0,
                    )

                    c.setFillColorRGB(0.2, 0.2, 0.2)

                    c.setFont(BASE_FONT, 6)

                    c.drawString(MARGIN + _lbl_w + _bl + 1.5 * mm, _by - _bh1 + 2 * mm, str(_sc))

                    if _ic:
                        c.setFillColorRGB(0.8, 0.2, 0.0)

                        c.drawString(MARGIN + _lbl_w + _bl + 8 * mm, _by - _bh1 + 2 * mm, "◀현재")

                # 범례

                _ly = _top - len(_dw10) * (_bh1 + _gap) - 2 * mm

                _lx = MARGIN

                for _lc, _lt in [
                    ((0.83, 0.68, 0.21), "용신"),
                    ((1.0, 0.55, 0.0), "현재"),
                    ((0.63, 0.77, 0.97), "일반"),
                    ((0.96, 0.60, 0.60), "기신"),
                ]:
                    c.setFillColorRGB(*_lc)

                    c.rect(_lx, _ly, 4 * mm, 2.5 * mm, fill=1, stroke=0)

                    c.setFillColorRGB(0.2, 0.2, 0.2)

                    c.setFont(BASE_FONT, 7)

                    c.drawString(_lx + 5 * mm, _ly + 0.3 * mm, _lt)

                    _lx += 22 * mm

                y = _ly - 6 * mm

            # == 4-B. 현재 운세 분석 ==

            if include_current:
                _cy = _dt.now().year

                _cage = _cy - birth_year + 1

                y = section_title(c, f"현재 운세 — {_cy}년 ({_cage}세) 지금 이 순간", y)

                try:
                    _daewoon2 = SajuCoreEngine.get_daewoon(
                        pils,
                        birth_year,
                        birth_month,
                        birth_day,
                        birth_hour,
                        birth_minute,
                        gender,
                    )

                    _cdw = next(
                        (d for d in _daewoon2 if d["시작연도"] <= _cy <= d["종료연도"]),
                        None,
                    )

                    _sw_c = get_yearly_luck(pils, _cy)

                    _sw_n = get_yearly_luck(pils, _cy + 1)

                    _sw_n2 = get_yearly_luck(pils, _cy + 2)

                    _tp = calc_turning_point(pils, birth_year, gender, _cy)

                    _ys_c = get_yongshin(pils)

                    _yohs = _ys_c.get("종합_용신", [])

                    _ioh = OH.get(ilgan, "")

                    _cdw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(_cdw["cg"], "-") if _cdw else "-"

                    _is_yong_dw = _cdw and get_yongshin_match(_cdw_ss, _yohs, _ioh) == "yong"

                    _sw_c_ss = _sw_c.get("십성_천간", "-")

                    _sw_n_ss = _sw_n.get("십성_천간", "-")

                    # 현재 대운 상황

                    y = subsection(
                        c,
                        f"현재 대운: {_cdw['str'] if _cdw else '미상'} ({_cdw_ss})",
                        y,
                    )

                    if _cdw:
                        _dw_years_left = _cdw["종료연도"] - _cy

                        if _is_yong_dw:
                            y = write(
                                c,
                                f"허허, 이 대운은 용신(用神) 대운이로구먼! 지금이 바로 황금기니라.",
                                y,
                                size=12,
                                color=(0.1, 0.3, 0.1),
                                line_h=7.5,
                            )

                            y = write(
                                c,
                                f"이 대운은 앞으로 {_dw_years_left}년 더 이어지느니라. 이 시기를 놓치면 아니 되느니라.",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                            y = write(
                                c,
                                "적극적으로 움직이고 투자하고 새로운 도전을 두려워하지 말게. 하늘이 자네 편이로구먼.",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                        else:
                            _presc_c = DAEWOON_PRESCRIPTION.get(_cdw_ss, "내실을 다지고 준비하는 시기니라.")

                            y = write(
                                c,
                                f"허어, 이 대운은 기신(忌神)의 기운이 있는 시기니라. {_dw_years_left}년 후에 대운이 바뀌느니라.",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                            y = write(c, f"이 시기의 처방: {_presc_c}", y, size=12, line_h=7.5)

                            y = write(
                                c,
                                "무리한 확장과 급격한 변화는 삼가게. 내실을 다지는 것이 최선이니라.",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                    y -= 3 * mm

                    # 올해 세운 상세

                    y = subsection(
                        c,
                        f"올해 세운: {_sw_c.get('세운', '')} ({_sw_c_ss} / {_sw_c.get('길흉', '')})",
                        y,
                    )

                    _SW_DETAIL = {
                        "偏財": "올해는 재물 변동과 이성 인연의 기운이 강하느니라. 사업 기회가 오지만 투기는 조심하게.",
                        "正財": "올해는 안정된 수입과 결혼 인연의 기운이 들어오느니라. 재물을 차곡차곡 모을 수 있는 해니라.",
                        "食神": "올해는 직업과 재능이 빛을 발하는 해니라. 새로운 일을 시작하거나 자격 취득에 좋으니라.",
                        "傷官": "올해는 재기와 창의성이 폭발하지만 윗사람과의 마찰을 조심해야 하느니라.",
                        "偏官": "올해는 직장 변동과 사고 기운이 있느니라. 건강과 안전에 각별히 주의하게.",
                        "正官": "올해는 명예와 승진의 기운이 강하느니라. 조직에서 인정받는 해니라.",
                        "偏印": "올해는 계획이 자주 바뀌고 이사·이동의 기운이 있느니라. 신중하게 결정하게.",
                        "正印": "올해는 학업과 자격 취득에 유리한 해니라. 어머니와의 인연도 돈독해지느니라.",
                        "比肩": "올해는 독립심이 강해지고 경쟁이 치열해지는 해니라. 동업보다는 단독 행동이 낫느니라.",
                        "劫財": "올해는 재물 손실과 경쟁이 극심한 해니라. 보증과 투자를 최대한 자제하게.",
                    }

                    _sw_detail = _SW_DETAIL.get(_sw_c_ss, f"올해는 {_sw_c_ss} 기운이 강하게 작동하는 해니라.")

                    y = write(c, _sw_detail, y, size=12, line_h=7.5)

                    # 올해 길흉 판단

                    if "길" in _sw_c.get("길흉", ""):
                        y = write(
                            c,
                            "허허, 올해는 전반적으로 길한 기운이 흐르는구먼. 이 기운을 최대한 활용하게!",
                            y,
                            size=12,
                            color=(0.1, 0.3, 0.1),
                            line_h=7.5,
                        )

                    elif "흉" in _sw_c.get("길흉", ""):
                        y = write(
                            c,
                            "허어, 올해는 흉한 기운이 있으니 조심해야 하느니라. 무리한 결정은 삼가게.",
                            y,
                            size=12,
                            color=(0.5, 0.1, 0.1),
                            line_h=7.5,
                        )

                    y -= 3 * mm

                    # 전환점 강도

                    _tp_intensity = _tp.get("intensity", "보통")

                    _tp_reasons = _tp.get("reason", [])

                    y = subsection(c, f"올해 인생 전환점 강도: {_tp_intensity}", y)

                    if _tp_reasons:
                        for _r in _tp_reasons[:4]:
                            y = write(c, f"  ◦ {_r}", y, size=12, line_h=7.5)

                    y -= 3 * mm

                    # 내년 전망

                    y = subsection(
                        c,
                        f"내년 세운: {_sw_n.get('세운', '')} ({_sw_n_ss} / {_sw_n.get('길흉', '')})",
                        y,
                    )

                    _sw_n_detail = _SW_DETAIL.get(_sw_n_ss, f"내년은 {_sw_n_ss} 기운이 작동하는 해니라.")

                    y = write(c, _sw_n_detail, y, size=12, line_h=7.5)

                    y = write(
                        c,
                        f"내후년({_cy + 2}년): {_sw_n2.get('세운', '')} [{_sw_n2.get('십성_천간', '')}] — {_sw_n2.get('길흉', '')}",
                        y,
                        size=11,
                        color=(0.35, 0.35, 0.35),
                        line_h=7,
                    )

                    y -= 3 * mm

                    # 지금 해야 할 것 / 하지 말아야 할 것

                    y = subsection(c, "명심하게 — 지금 당장 해야 할 것 vs 하지 말아야 할 것", y)


                    _do, _dont = _DO_LIST.get(
                        _sw_c_ss,
                        ("현재 흐름에 맞는 결정을 내리게", "무리한 확장을 삼가게"),
                    )

                    y = write(
                        c,
                        f"  해야 할 것: {_do}",
                        y,
                        size=12,
                        color=(0.1, 0.3, 0.1),
                        line_h=7.5,
                    )

                    y = write(
                        c,
                        f"  하지 말 것: {_dont}",
                        y,
                        size=12,
                        color=(0.5, 0.1, 0.1),
                        line_h=7.5,
                    )

                except Exception as _ce:
                    y = write(c, f"  (현재 운세 계산 오류: {_ce})", y, size=11)

                y -= 5 * mm

            # == 4-C. 미래 5년 운세 흐름 ==

            if include_future:
                _cy2 = _dt.now().year

                y = section_title(c, f"미래 5년 운세 — {_cy2 + 1}년~{_cy2 + 5}년 흐름", y)

                try:
                    _daewoon3 = SajuCoreEngine.get_daewoon(
                        pils,
                        birth_year,
                        birth_month,
                        birth_day,
                        birth_hour,
                        birth_minute,
                        gender,
                    )

                    _ys3 = get_yongshin(pils)

                    _yohs3 = _ys3.get("종합_용신", [])

                    _ioh3 = OH.get(ilgan, "")

                    _GOOD_SS = {"正財", "食神", "正官", "正印", "偏財"}

                    _BAD_SS = {"偏官", "劫財", "傷官"}

                    _MID_SS = {"比肩", "偏印", "偏財"}

                    _FUTURE_DETAIL = {
                        "偏財": "재물 변동과 이성 인연이 두드러지는 해니라. 사업·투자에 기회가 오나 과욕은 금물이니라.",
                        "正財": "안정된 재물이 쌓이는 해니라. 결혼·자산 형성에 최적의 시기이니라.",
                        "食神": "직업과 재능이 빛을 발하는 해니라. 새로운 일을 시작하거나 자격을 취득하기 좋으니라.",
                        "傷官": "창의성이 폭발하나 인간관계 마찰을 조심해야 하는 해니라. 독립·창업 에너지가 강하느니라.",
                        "偏官": "변동과 도전의 기운이 강한 해니라. 건강과 안전에 주의하고 무리한 확장은 삼가게.",
                        "正官": "명예와 승진의 기운이 오는 해니라. 조직에서 인정받고 책임 있는 자리에 오를 기운이니라.",
                        "偏印": "계획 변경과 이사·이동의 기운이 있는 해니라. 새로운 학문이나 기술을 배우기 좋으니라.",
                        "正印": "학업과 자격 취득에 유리한 해니라. 귀인과의 인연이 강해지는 시기이니라.",
                        "比肩": "독립심과 경쟁이 극대화되는 해니라. 단독 행동이 유리하고 새로운 시작에 좋은 시기니라.",
                        "劫財": "재물 손실과 경쟁이 심한 해니라. 보증·투자를 자제하고 내실을 다지는 것이 최선이니라.",
                    }

                    for _fy in range(_cy2 + 1, _cy2 + 6):
                        _fage = _fy - birth_year + 1

                        _fsw = get_yearly_luck(pils, _fy)

                        _fsw_ss = _fsw.get("십성_천간", "-")

                        _fsw_gilhung = _fsw.get("길흉", "")

                        _fdw = next(
                            (d for d in _daewoon3 if d["시작연도"] <= _fy <= d["종료연도"]),
                            None,
                        )

                        _fdw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(_fdw["cg"], "-") if _fdw else "-"

                        _is_yong_y = get_yongshin_match(_fsw_ss, _yohs3, _ioh3) == "yong"

                        _is_gi_y = get_yongshin_match(_fsw_ss, _yohs3, _ioh3) == "gi"

                        if _is_yong_y or _fsw_ss in _GOOD_SS:
                            _fcol = (0.05, 0.28, 0.05)

                            _flabel = "◎ 길운"

                        elif _is_gi_y or _fsw_ss in _BAD_SS:
                            _fcol = (0.45, 0.08, 0.08)

                            _flabel = "▲ 주의"

                        else:
                            _fcol = (0.15, 0.15, 0.35)

                            _flabel = "○ 보통"

                        y = write(
                            c,
                            f"{_fy}년 ({_fage}세)  {_fsw.get('세운', '')}  [{_fsw_ss}]  {_flabel}  {_fsw_gilhung}",
                            y,
                            size=13,
                            color=_fcol,
                        )

                        _fd = _FUTURE_DETAIL.get(_fsw_ss, f"{_fsw_ss} 기운이 작동하는 해니라.")

                        y = write(
                            c,
                            f"  {_fd}",
                            y,
                            size=11,
                            color=(0.25, 0.25, 0.25),
                            line_h=7,
                        )

                        if _fdw:
                            y = write(
                                c,
                                f"  [대운: {_fdw['str']} {_fdw_ss}]",
                                y,
                                size=10,
                                color=(0.4, 0.4, 0.4),
                                line_h=6.5,
                            )

                        y -= 3 * mm

                except Exception as _fe:
                    y = write(c, f"  (미래 운세 계산 오류: {_fe})", y, size=11)

                y -= 4 * mm

            # == 4-E. 신살 분석 ==

            if include_sinsal:
                y = section_title(c, "신살 분석", y)

                try:
                    _sin12 = get_12sinsal(pils)

                    _extra = get_extra_sinsal(pils)

                    _all_sins = _sin12 + _extra

                    if _all_sins:
                        for _s in _all_sins:
                            _sname = _s.get("이름") or _s.get("name", "")

                            _sicon = _s.get("icon", "")

                            _sdesc = _s.get("desc", "")

                            _scaution = _s.get("caution", "")

                            _spos = ", ".join(_s.get("위치", [])) if _s.get("위치") else ""

                            _header = f"  {_sicon} {_sname}" + (f"  ({_spos})" if _spos else "")

                            y = write(c, _header, y, size=10, color=(0.1, 0.2, 0.5))

                            if _sdesc:
                                y = write(
                                    c,
                                    f"    {_sdesc}",
                                    y,
                                    size=9,
                                    color=(0.2, 0.2, 0.2),
                                    line_h=6,
                                )

                            if _scaution:
                                y = write(
                                    c,
                                    f"    주의: {_scaution}",
                                    y,
                                    size=8,
                                    color=(0.55, 0.15, 0.15),
                                    line_h=5.5,
                                )

                    else:
                        y = write(c, "  (감지된 신살 없음)", y, size=9)

                except Exception:
                    y = write(c, "  (신살 계산 불가)", y, size=9)

                y -= 4 * mm

            # == 4-F. 육친 분석 ==

            if include_yukjin:
                y = section_title(c, "육친 분석", y)

                try:
                    _yk = get_yukjin(ilgan, pils, gender)

                    for _rel in _yk:
                        _rname = _rel.get("관계", "")

                        _rwhere = _rel.get("위치", "없음")

                        _rdesc = _rel.get("desc", "")

                        _present = _rel.get("present", False)

                        _color = (0.1, 0.35, 0.1) if _present else (0.4, 0.4, 0.4)

                        y = write(c, f"  {_rname}  [{_rwhere}]", y, size=10, color=_color)

                        if _rdesc:
                            y = write(
                                c,
                                f"    {_rdesc}",
                                y,
                                size=9,
                                color=(0.25, 0.25, 0.25),
                                line_h=6,
                            )

                except Exception:
                    y = write(c, "  (육친 계산 불가)", y, size=9)

                y -= 4 * mm

            # == 5. AI 종합운세 / 전문 분석 ==

            if include_fortune:
                y = section_title(c, "만신 종합 천명풀이 — 전문 사주 분석", y)

                try:
                    _saju_key = pils_to_cache_key(pils)

                    # 캐시 우선 (prophet > general > lifeline)

                    _ai_raw = get_ai_cache(_saju_key, "prophet") or get_ai_cache(_saju_key, "general") or get_ai_cache(_saju_key, "lifeline") or ""

                    if _ai_raw:
                        y = _clean_narrative_for_pdf(c, _ai_raw, y)

                    else:
                        # 캐시 없음 → build_rich_narrative()로 직접 생성 (무당 말투 포함)

                        _narr = build_rich_narrative(pils, birth_year, gender, name, section="report")

                        if _narr:
                            y = _clean_narrative_for_pdf(c, _narr, y)

                        else:
                            # 최후 폴백: engine highlights

                            _hl3 = generate_engine_highlights(pils, birth_year, gender)

                            y = write(
                                c,
                                "허허, 내 신안(神眼)으로 이 사주를 풀어보겠느니라.\n",
                                y,
                                size=12,
                                line_h=7.5,
                            )

                            for _ln in _hl3.get("personality", []):
                                y = write(c, f"  {_ln}", y, size=12, line_h=7.5)

                            y -= 3 * mm

                            y = write(
                                c,
                                "앱에서 AI 분석을 먼저 실행하면 더 상세한 해석이 PDF에 포함됩니다.",
                                y,
                                size=11,
                                color=(0.45, 0.45, 0.45),
                                line_h=7,
                            )

                except Exception as _ae:
                    y = write(c, f"  (종합 분석 생성 오류: {_ae})", y, size=11)

                y -= 4 * mm

            # == 6. 처방/조언 ==

            if include_advice:
                y = section_title(c, "처방 — 만신이 내리는 핵심 조언", y)

                try:
                    _adv_dw_list = SajuCoreEngine.get_daewoon(
                        pils,
                        birth_year,
                        birth_month,
                        birth_day,
                        birth_hour,
                        birth_minute,
                        gender,
                    )

                    _adv_dw = next(
                        (dw for dw in _adv_dw_list if dw["시작연도"] <= _dt.now().year <= dw["종료연도"]),
                        None,
                    )

                    _adv_ys = get_yongshin(pils)

                    _adv_yohs = _adv_ys.get("종합_용신", [])

                    _adv_ioh = OH.get(ilgan, "")

                    _adv_sw = get_yearly_luck(pils, _dt.now().year)

                    _adv_sw_ss = _adv_sw.get("십성_천간", "-")

                    _adv_ys_ml = get_yongshin_multilayer(pils, birth_year, gender, _dt.now().year)

                    y = write(
                        c,
                        "허허, 내 신안(神眼)이 본 이 사주의 핵심 처방을 명심하게.",
                        y,
                        size=12,
                        color=(0.2, 0.1, 0.0),
                        line_h=7.5,
                    )

                    y -= 3 * mm

                    if _adv_dw:
                        _adv_dw_ss = TEN_GODS_MATRIX.get(ilgan, {}).get(_adv_dw["cg"], "-")

                        _presc_main = DAEWOON_PRESCRIPTION.get(_adv_dw_ss, "꾸준한 노력으로 안정을 유지하게.")

                        y = subsection(c, f"대운 처방 — {_adv_dw['str']} {_adv_dw_ss}대운", y)

                        y = write(
                            c,
                            f"  {_presc_main}",
                            y,
                            size=12,
                            color=(0.1, 0.35, 0.1),
                            line_h=7.5,
                        )

                        y -= 2 * mm

                    y = subsection(c, f"올해 세운 처방 — {_adv_sw.get('세운', '')} {_adv_sw_ss}", y)

                    _SW_PRESC = {
                        "偏財": "재물 기회에 적극 대응하게. 단, 검증되지 않은 투자는 반드시 피하게.",
                        "正財": "재산을 차곡차곡 모으는 해니라. 저축과 자산 형성에 집중하게.",
                        "食神": "재능을 꽃피우는 해니라. 새로운 일을 시작하고 자격증을 취득하게.",
                        "傷官": "창의적 도전은 좋으나 말과 행동을 조심하게. 분쟁을 피하게.",
                        "偏官": "건강 검진을 먼저 받게. 안전 수칙을 철저히 지키게. 법적 서류를 정리하게.",
                        "正官": "조직에서 성실히 하면 인정받는 해니라. 명예를 지키는 것이 최우선이니라.",
                        "偏印": "무모한 이사·변경을 자제하게. 새로운 학문을 배우는 것은 길하느니라.",
                        "正印": "배움에 투자하게. 어머니·어른과의 관계를 돈독히 하게.",
                        "比肩": "혼자서 결정하고 혼자서 실행하는 것이 이 해의 길이니라. 동업은 자제하게.",
                        "劫財": "지출을 최소화하게. 보증·투자는 절대 삼가게. 내실을 다지는 것이 최선이니라.",
                    }

                    _sw_presc = _SW_PRESC.get(_adv_sw_ss, "현재 흐름에 맞는 신중한 결정을 내리게.")

                    y = write(
                        c,
                        f"  {_sw_presc}",
                        y,
                        size=12,
                        color=(0.1, 0.3, 0.1),
                        line_h=7.5,
                    )

                    y -= 2 * mm

                    # 용신 활용 처방

                    _adv_yong1 = _adv_ys_ml.get("용신_1순위", "")

                    _YONG_PRESC = {
                        "木": "동쪽 방향에 중요한 공간을 배치하게. 초록 계열 소품을 활용하고 봄에 큰 결정을 내리게.",
                        "火": "남쪽이 길방이니라. 밝고 활기찬 환경에서 일하게. 붉은색 소품이 기운을 높여주니라.",
                        "土": "황토색·노랑 계열이 안정을 주느니라. 부동산 관련 분야에 관심을 두어도 좋으니라.",
                        "金": "서쪽이 길방이니라. 흰색·금색 소품을 활용하고 가을에 중요한 결정을 내리게.",
                        "水": "북쪽이 길방이니라. 물 가까이 사는 것도 좋고 검정·남색 계열이 기운을 도와주느니라.",
                    }

                    if _adv_yong1:
                        y = subsection(c, f"용신 {_adv_yong1} 활용 처방", y)

                        _yp = _YONG_PRESC.get(_adv_yong1, f"{_adv_yong1} 오행을 일상에서 적극 활용하게.")

                        y = write(c, f"  {_yp}", y, size=12, color=(0.0, 0.2, 0.4), line_h=7.5)

                        y -= 2 * mm

                except Exception as _adv_e:
                    y = write(c, f"  (처방 계산 오류: {_adv_e})", y, size=11)

                y -= 3 * mm

                y = write(
                    c,
                    "※ 이 리포트는 전통 사주명리학 분석 자료이며 참고용입니다.",
                    y,
                    size=10,
                    color=(0.45, 0.45, 0.45),
                )

            # -- 하단 푸터 --

            c.setFillColorRGB(0.6, 0.6, 0.6)

            c.setFont(BASE_FONT, 8)

            c.drawCentredString(
                W / 2,
                12 * mm,
                f"만신 사주 천명풀이  |  {_dt.now().strftime('%Y.%m.%d')} 출력",
            )

            c.save()

            buf.seek(0)

            fname = f"사주_{name}_{_dt.now().strftime('%Y%m%d_%H%M')}.pdf"

            _pdf_bytes = buf.read()
            _b64 = base64.b64encode(_pdf_bytes).decode()
            st.markdown(
                f'<div style="text-align:center;margin:20px 0;">'
                f'<a href="data:application/pdf;base64,{_b64}"'
                f' download="사주풀이_{name}.pdf"'
                f' style="display:inline-block;'
                f'background:linear-gradient(135deg,#c9a84c,#a07830);'
                f'color:#fff8e8;padding:14px 32px;border-radius:50px;'
                f'font-size:16px;font-weight:700;text-decoration:none;'
                f'box-shadow:0 4px 15px rgba(201,168,76,0.4);">'
                f'📄 PDF 다운로드</a></div>',
                unsafe_allow_html=True,
            )

            st.success(f"✅ PDF 생성 완료! 위 링크로 다운로드하세요.")

        except ImportError:
            st.error("❌ reportlab 미설치. `pip install reportlab` 을 실행해주세요.")

        except Exception as e:
            st.error(f"❌ PDF 생성 오류: {e}")


if __name__ == "__main__":
    main()