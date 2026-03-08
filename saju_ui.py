# -*- coding: utf-8 -*-
"""
saju_ui.py - 사주 UI 컴포넌트 모듈
manse.py에서 from saju_ui import * 로 사용
"""

import streamlit as st


def _get_ohang_color(char):
    """오행별 (배경색, 글자색) 반환 — saju_ui 내부용"""
    wood  = (["甲","乙","寅","卯"], "#2d8a4e", "#ffffff")
    fire  = (["丙","丁","巳","午"], "#e53935", "#ffffff")
    earth = (["戊","己","辰","戌","丑","未"], "#f9a825", "#1a1a1a")
    metal = (["庚","辛","申","酉"], "#9e9e9e", "#ffffff")
    water = (["壬","癸","亥","子"], "#1565c0", "#ffffff")
    for chars, bg, fg in [wood, fire, earth, metal, water]:
        if char in chars:
            return bg, fg
    return "#555555", "#ffffff"


def inject_global_css():
    """전역 CSS — 전통 한지 크림 톤 + 프리미엄 앱 스타일 (st.set_page_config 직후 호출)"""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

/* ═══════════════════════════════════
   전체 배경 — 한지 크림 톤
═══════════════════════════════════ */
.stApp {
    background: linear-gradient(160deg, #f5f0e8 0%, #ede8d8 50%, #e8e0cc 100%);
    background-attachment: fixed;
    font-family: 'Noto Serif KR', 'Noto Sans KR', serif;
}

/* 한지 질감 패턴 오버레이 */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        url("data:image/svg+xml,%3Csvg width='200' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ═══════════════════════════════════
   메인 컨테이너
═══════════════════════════════════ */
.main .block-container {
    max-width: 960px !important;
    padding: 2rem 1.5rem !important;
    background: transparent;
}

/* ═══════════════════════════════════
   타이틀 헤더
═══════════════════════════════════ */
h1 {
    font-family: 'Noto Serif KR', serif !important;
    color: #2d1f00 !important;
    font-weight: 900 !important;
    letter-spacing: 0.15em !important;
    text-shadow: 1px 1px 0px rgba(139,93,0,0.15) !important;
}

h2, h3 {
    font-family: 'Noto Serif KR', serif !important;
    color: #3d2800 !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
}

/* ═══════════════════════════════════
   탭 스타일
═══════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(245,240,232,0.8) !important;
    border-bottom: 2px solid #c9a84c !important;
    gap: 2px;
    padding: 4px 4px 0;
    border-radius: 12px 12px 0 0;
    overflow-x: auto;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5a3d1a !important;
    font-family: 'Noto Serif KR', serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, #c9a84c, #a07830) !important;
    color: #fff8e8 !important;
    box-shadow: 0 -2px 8px rgba(201,168,76,0.3) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(201,168,76,0.2) !important;
    color: #2d1f00 !important;
}

/* ═══════════════════════════════════
   카드/박스 스타일 — 한지 카드
═══════════════════════════════════ */
.saju-card, .card {
    background: linear-gradient(145deg, #faf7f0, #f2ebe0);
    border: 1px solid rgba(201,168,76,0.4);
    border-radius: 16px;
    padding: 24px;
    box-shadow:
        0 2px 12px rgba(139,93,0,0.08),
        inset 0 1px 0 rgba(255,255,255,0.8);
    margin-bottom: 16px;
}

/* 다크 카드 (결과/해석 영역) */
.saju-card-dark {
    background: linear-gradient(145deg, #2d1f00, #1a1200);
    border: 1px solid #c9a84c;
    border-radius: 16px;
    padding: 24px;
    color: #f5e8c8;
    box-shadow:
        0 4px 20px rgba(0,0,0,0.3),
        inset 0 1px 0 rgba(201,168,76,0.2);
    margin-bottom: 16px;
}

/* ═══════════════════════════════════
   버튼 스타일
═══════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #a07830) !important;
    color: #fff8e8 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 32px !important;
    font-family: 'Noto Serif KR', serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    box-shadow: 0 4px 15px rgba(201,168,76,0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #d4b55a, #b08840) !important;
    box-shadow: 0 6px 20px rgba(201,168,76,0.5) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ═══════════════════════════════════
   기존 유틸리티 클래스 (호환성 유지)
═══════════════════════════════════ */
/* 사주 내러티브 블록 */
.saju-narrative {
    font-family: 'Noto Serif KR', serif;
    font-size: 15px;
    line-height: 2.1;
    color: #3d2800;
    padding: 14px;
    background: rgba(201,168,76,0.06);
    border-radius: 10px;
    border-left: 3px solid #c9a84c;
}
/* 골드 섹션 헤더 */
.gold-section {
    color: #2d1f00;
    font-size: 17px;
    font-weight: 800;
    padding: 8px 0;
    border-bottom: 2px solid rgba(201,168,76,0.5);
    margin: 22px 0 14px;
}
/* 기둥 박스 */
.pillar-box {
    background: linear-gradient(145deg, #faf7f0, #f2ebe0);
    border: 1px solid #c9a84c;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}
/* 툴팁 */
.saju-tooltip {
    position: relative;
    cursor: help;
    border-bottom: 1px dashed #8b6200;
}
.saju-tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background: #2d1f00;
    color: #f5e8c8;
    font-size: 12px;
    border-radius: 6px;
    padding: 6px 10px;
    position: absolute;
    z-index: 999;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    white-space: normal;
}
.saju-tooltip:hover .tooltiptext { visibility: visible; }
/* 섹션 라벨 */
.section-label {
    font-weight: 700;
    color: #8b6200;
    margin: 16px 0 8px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ═══════════════════════════════════
   모바일 반응형
═══════════════════════════════════ */
@media (max-width: 768px) {
    .pillar-box {
        font-size: 28px !important;
        width: 60px !important;
        height: 60px !important;
        padding: 6px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 11px !important;
        padding: 6px 8px !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
    }
    .saju-narrative {
        padding: 12px !important;
        font-size: 14px !important;
    }
    .stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 15px !important;
    }
    #scroll-top-btn {
        bottom: 70px !important;
        right: 12px !important;
        width: 44px !important;
        height: 44px !important;
        font-size: 18px !important;
    }
}
@media (max-width: 480px) {
    .pillar-box {
        font-size: 22px !important;
        width: 48px !important;
        height: 48px !important;
    }
    .gold-section {
        font-size: 15px !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_quick_consult_header():
    """퀵 상담창 헤더 렌더링"""
    st.markdown(
        """
<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
            border:1px solid rgba(212,175,55,0.4);
            border-radius:14px;padding:12px 18px;margin-bottom:10px;
            display:flex;align-items:center;gap:10px">
  <span style="font-size:22px">🔮</span>
  <div>
    <div style="font-size:14px;font-weight:900;color:#d4af37;letter-spacing:1px">
      즉각 천기(天機) 전수
    </div>
    <div style="font-size:11px;color:#aaa;margin-top:2px">
      어떤 탭에서든 바로 질문하세요 — 만신이 즉시 답합니다
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_quick_consult_response(response: str):
    """퀵 상담 응답 렌더링"""
    if not response:
        return
    st.markdown(
        f"""
<div style="background:linear-gradient(135deg,#fffbf0,#fff8e0);
            border:1.5px solid #d4af37;border-radius:12px;
            padding:18px 20px;margin-top:10px;
            font-size:14px;color:#333;line-height:2;
            box-shadow:0 4px 12px rgba(212,175,55,0.15)">
  <div style="font-size:11px;font-weight:700;color:#b38728;
              letter-spacing:2px;margin-bottom:10px">📜 만신의 답</div>
  {response}
</div>
""",
        unsafe_allow_html=True,
    )


def render_info_card(title: str, description: str):
    """정보 안내 카드 렌더링"""
    desc_html = description.replace("\n", "<br>")
    st.markdown(
        f"""
<div style="background:#f9f5e8;border:1px solid #e0d0a0;
            border-radius:10px;padding:12px 16px;margin-bottom:14px;
            font-size:13px;color:#555;line-height:1.9">
  <div style="font-size:13px;font-weight:800;color:#8b6200;margin-bottom:6px">
    ℹ️ {title}
  </div>
  {desc_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_daewoon_card(
    dw: dict,
    oh_cg: str,
    d_ss_cg: str,
    oh_jj: str,
    d_ss_jj: str,
    title: str,
    icon: str,
    narrative: str,
    prescription: str,
    alert_html: str,
    bdr: str,
    bg2: str,
    badge: str,
    OHE: dict,
):
    """대운 상세 카드 렌더링"""
    emoji_cg = OHE.get(oh_cg, "")
    emoji_jj = OHE.get(oh_jj, "")

    start_year = dw.get("시작연도", "")
    end_year = dw.get("종료연도", "")
    start_age = dw.get("시작나이", "")
    dw_str = dw.get("str", "")

    # 오행 색상 배지 생성
    _badge_style = (
        "display:inline-block;border-radius:8px;padding:2px 9px;"
        "font-size:22px;font-weight:900;margin-right:2px;"
    )
    _GZ_KR = {
        '甲':'갑','乙':'을','丙':'병','丁':'정','戊':'무',
        '己':'기','庚':'경','辛':'신','壬':'임','癸':'계',
        '子':'자','丑':'축','寅':'인','卯':'묘','辰':'진',
        '巳':'사','午':'오','未':'미','申':'신','酉':'유',
        '戌':'술','亥':'해',
    }
    _dw_html = ""
    for _ch in dw_str:
        _bg, _fg = _get_ohang_color(_ch)
        _dw_html += f"<span style='{_badge_style}background:{_bg};color:{_fg}'>{_ch}</span>"
    _dw_kr = "".join(_GZ_KR.get(c, c) for c in dw_str)

    st.markdown(
        f"""
<div style="{bg2}{bdr}border-radius:14px;padding:18px 20px;
            margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
  {badge}
  <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:12px">
    <div style="font-size:32px;min-width:40px;text-align:center">{icon}</div>
    <div style="flex:1">
      <div style="font-size:16px;font-weight:900;color:#333;margin-bottom:4px">
        {_dw_html}
        <span style="font-size:13px;color:#888;font-weight:400">({_dw_kr})</span>
        <span style="font-size:14px;font-weight:700;color:#555;margin-left:4px">대운</span>
        <span style="font-size:12px;color:#888;font-weight:400;margin-left:8px">
          {start_age}세 ({start_year}~{end_year}년)
        </span>
      </div>
      <div style="font-size:12px;color:#666;margin-top:2px">
        천간 {emoji_cg} {oh_cg} / {d_ss_cg} &nbsp;|&nbsp;
        지지 {emoji_jj} {oh_jj} / {d_ss_jj}
      </div>
      <div style="font-size:13px;font-weight:700;color:#8b6200;margin-top:4px">
        {title}
      </div>
    </div>
  </div>
  <div style="font-size:13px;color:#333;line-height:1.9;margin-bottom:10px">
    {narrative}
  </div>
  <div style="background:rgba(212,175,55,0.08);border-left:3px solid #d4af37;
              padding:8px 12px;border-radius:6px;font-size:12px;
              color:#7a5c00;margin-bottom:8px">
    💊 <b>처방:</b> {prescription}
  </div>
  {alert_html if alert_html else ""}
</div>
""",
        unsafe_allow_html=True,
    )
