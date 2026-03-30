"""
fix_tab_pdf.py
==============
manse.py 의 render_pdf_download_btn 함수를
탭별 즉시 PDF 생성 방식으로 교체합니다.
이미 적용된 경우 문법 검사만 수행합니다.
"""

import py_compile, sys

TARGET = "manse.py"

with open(TARGET, encoding="utf-8") as f:
    src = f.read()

# ── 교체 대상 (기존 단순 탭 이동 버전) ──────────────────────────────────────
OLD = '''def render_pdf_download_btn(tab_name, pils, name, birth_year, gender):
    """각 탭 하단 PDF 빠른 출력 버튼"""
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(212,175,55,0.2);margin:24px 0 12px'>",
        unsafe_allow_html=True,
    )
    _col_pdf1, _col_pdf2, _col_pdf3 = st.columns([1,2,1])
    with _col_pdf2:
        if st.button(
            f"📄 이 내용 PDF로 출력",
            key=f"pdf_quick_{tab_name}",
            use_container_width=True,
        ):
            st.session_state["active_tab"] = 14  # PDF 탭으로 이동
            st.rerun()'''

# ── 교체 내용 (탭별 즉시 PDF 생성 버전) ─────────────────────────────────────
NEW = r'''def render_pdf_download_btn(tab_name, pils, name, birth_year, gender):
    """각 탭 전용 PDF 즉시 생성 버튼"""
    import io, os, re as _re
    from datetime import datetime as _dt2

    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(212,175,55,0.2);margin:24px 0 12px'>",
        unsafe_allow_html=True,
    )

    _TAB_LABEL = {
        "lifeline":          "대운흐름",
        "past":              "과거분석",
        "future3":           "미래3년",
        "money":             "재물사업",
        "relations":         "궁합관계",
        "health":            "건강분석",
        "daily":             "일일운세",
        "monthly":           "월별운세",
        "gaewoon":           "개운처방",
        "ohaeng":            "음양오행",
        "tojeong":           "토정비결",
        "current_situation": "현재상황",
    }
    _label = _TAB_LABEL.get(tab_name, tab_name)

    _col1, _col2, _col3 = st.columns([1, 2, 1])
    with _col2:
        if st.button(
            f"📄 {_label} PDF 출력",
            key=f"pdf_quick_{tab_name}",
            use_container_width=True,
            type="secondary",
        ):
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.units import mm
                from reportlab.pdfgen import canvas
                from reportlab.pdfbase.ttfonts import TTFont
                from reportlab.pdfbase import pdfmetrics

                _buf = io.BytesIO()
                W, H = A4
                MARGIN = 18 * mm
                BOT    = 20 * mm

                # ── 한글 폰트 등록 ────────────────────────────────────────
                _FONTS = [
                    ("Malgun",      "C:/Windows/Fonts/malgun.ttf"),
                    ("NanumGothic", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
                    ("UnDotum",     "/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf"),
                ]
                _BF = "Helvetica"
                for _fn, _fp in _FONTS:
                    if os.path.exists(_fp):
                        try:
                            pdfmetrics.registerFont(TTFont(_fn, _fp))
                            _BF = _fn
                            break
                        except Exception:
                            pass

                c = canvas.Canvas(_buf, pagesize=A4)
                y = H - MARGIN

                # ── 헬퍼 함수 ────────────────────────────────────────────
                def _new_page():
                    c.showPage()
                    return H - MARGIN

                def _write(text, y, size=10, color=(0.1, 0.1, 0.1)):
                    if y < BOT + 10 * mm:
                        y = _new_page()
                    c.setFont(_BF, size)
                    c.setFillColorRGB(*color)
                    max_w = W - 2 * MARGIN
                    text = _re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', str(text or ""))
                    text = _re.sub(r'#{1,6}\s*', '', text)
                    text = _re.sub(r'<[^>]+>', '', text)
                    for raw in text.split("\n"):
                        raw = raw.strip()
                        if not raw:
                            y -= 3 * mm
                            continue
                        while raw:
                            if c.stringWidth(raw, _BF, size) <= max_w:
                                if y < BOT + 8 * mm:
                                    y = _new_page()
                                c.drawString(MARGIN, y, raw)
                                y -= (size * 0.45) * mm
                                break
                            lo, hi = 1, len(raw)
                            while lo < hi - 1:
                                mid = (lo + hi) // 2
                                if c.stringWidth(raw[:mid], _BF, size) <= max_w:
                                    lo = mid
                                else:
                                    hi = mid
                            if y < BOT + 8 * mm:
                                y = _new_page()
                            c.drawString(MARGIN, y, raw[:lo])
                            y -= (size * 0.45) * mm
                            raw = raw[lo:].lstrip()
                    return y

                def _sec(title, y):
                    if y < 45 * mm:
                        y = _new_page()
                    c.setFillColorRGB(0.15, 0.12, 0.05)
                    c.rect(MARGIN - 3*mm, y - 2*mm,
                           W - 2*MARGIN + 6*mm, 9*mm, fill=1, stroke=0)
                    c.setFillColorRGB(0.97, 0.88, 0.38)
                    c.setFont(_BF, 13)
                    c.drawString(MARGIN + 1*mm, y + 1.5*mm, title)
                    return y - 12 * mm

                # ── 표지 ─────────────────────────────────────────────────
                c.setFillColorRGB(0.08, 0.06, 0.02)
                c.rect(0, H - 55*mm, W, 55*mm, fill=1, stroke=0)
                c.setFillColorRGB(0.97, 0.90, 0.42)
                c.setFont(_BF, 22)
                c.drawCentredString(W / 2, H - 25*mm,
                                    f"만신 사주 \u2014 {_label} 리포트")
                c.setFillColorRGB(0.85, 0.82, 0.70)
                c.setFont(_BF, 11)
                c.drawCentredString(W / 2, H - 35*mm,
                                    f"{name} \ub2d8  |  {birth_year}\ub144\uc0dd  |  {gender}\uc131")
                c.setFillColorRGB(0.65, 0.62, 0.55)
                c.setFont(_BF, 9)
                c.drawCentredString(W / 2, H - 43*mm,
                                    f"\ucd9c\ub825\uc77c: {_dt2.now().strftime('%Y\ub144 %m\uc6d4 %d\uc77c')}")
                y = H - 65 * mm

                # ── 탭별 전용 콘텐츠 ─────────────────────────────────────
                from saju_interpreter import LocalSajuNarrator, get_yongshin
                from saju_engine import get_yearly_luck

                _cur_yr = _dt2.now().year

                if tab_name == "lifeline":
                    y = _sec("\U0001f30a \ub300\uc6b4\ud750\ub984 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.lifeline(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "past":
                    y = _sec("\U0001f570\ufe0f \uacfc\uac70 \ud0c0\uc784\ub77c\uc778 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.past_analysis(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "future3":
                    y = _sec("\U0001f52e \ubbf8\ub798 3\ub144 \uc9d1\uc911 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.future3(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "money":
                    y = _sec("\U0001f4b0 \uc7ac\ubb3c/\uc9c1\uc5c5 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.money(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "relations":
                    y = _sec("\U0001f491 \uad81\ud569/\uad00\uacc4 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.relations(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "health":
                    y = _sec("\U0001f3e5 \uac74\uac15 \ubd84\uc11d", y)
                    _OH_HEALTH = {
                        "\u6728": "\uac04\u00b7\ub2f4\u00b7\ub208\u00b7\uadfc\uc721 \u2014 \uc2a4\ud2b8\ub808\uc2a4\uc131 \uc9c8\ud658, \uacfc\ub85c \uc8fc\uc758",
                        "\u706b": "\uc2ec\uc7a5\u00b7\uc18c\uc7a5\u00b7\ud601\uad00 \u2014 \ud601\uc555\u00b7\uc2ec\uc7a5\u00b7\uc815\uc2e0\uac74\uac15 \uc8fc\uc758",
                        "\u571f": "\ube44\uc7a5\u00b7\uc704\u00b7\ucdb5\uc7a5 \u2014 \uc18c\ud654\uae30\u00b7\ub2f9\ub1e8\u00b7\uacfc\uc2dd \uc8fc\uc758",
                        "\u91d1": "\ud3d0\u00b7\ub300\uc7a5\u00b7\ud53c\ubd80\u00b7\ucf54 \u2014 \ud638\ud761\uae30\u00b7\ud53c\ubd80\u00b7\uc54c\ub808\ub974\uae30 \uc8fc\uc758",
                        "\u6c34": "\uc2e0\uc7a5\u00b7\ubc29\uad11\u00b7\uc0dd\uc2dd\uae30 \u2014 \uc2e0\uc7a5\u00b7\ubd80\uc885\u00b7\uc0dd\uc2dd\uae30 \uc8fc\uc758",
                    }
                    try:
                        from saju_engine import calc_ohaeng_strength
                        _oh_s = calc_ohaeng_strength(pils[1]["cg"], pils)
                        _oh_sorted = sorted(_oh_s.items(), key=lambda x: -x[1])
                        _oh_max = _oh_sorted[0][0] if _oh_sorted else ""
                        _oh_min = _oh_sorted[-1][0] if _oh_sorted else ""
                        y = _write(
                            f"\uac00\uc7a5 \uac15\ud55c \uc624\ud589({_oh_max}) \u2192 "
                            f"\ucde8\uc57d \uc7a5\uae30: {_OH_HEALTH.get(_oh_max, '')}",
                            y, size=9)
                        y = _write(
                            f"\uac00\uc7a5 \uc57d\ud55c \uc624\ud589({_oh_min}) \u2192 "
                            f"\ubcf4\uac15 \ud544\uc694: {_OH_HEALTH.get(_oh_min, '')}",
                            y, size=9)
                    except Exception:
                        pass
                    y = _write(LocalSajuNarrator.full_report(
                        pils, name, birth_year, gender)[:3000], y, size=9)

                elif tab_name == "daily":
                    y = _sec(
                        f"\u2600\ufe0f \uc624\ub298\uc758 \uc6b4\uc138 "
                        f"({_dt2.now().strftime('%Y.%m.%d')})", y)
                    y = _write(LocalSajuNarrator.daily(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "monthly":
                    y = _sec(
                        f"\U0001f4c5 \uc774\ub2ec\uc758 \uc6b4\uc138 "
                        f"({_dt2.now().month}\uc6d4)", y)
                    y = _write(LocalSajuNarrator.monthly(
                        pils, name, birth_year, gender), y, size=9)

                elif tab_name == "gaewoon":
                    y = _sec("\U0001f31f \uac1c\uc6b4 \ucc98\ubc29", y)
                    _ys   = get_yongshin(pils)
                    _yong = _ys.get("\uc885\ud569_\uc6a9\uc2e0", []) if _ys else []
                    _OHN  = {"\u6728": "\ubaa9(\u6728)", "\u706b": "\ud654(\u706b)",
                             "\u571f": "\ud1a0(\u571f)", "\u91d1": "\uae08(\u91d1)",
                             "\u6c34": "\uc218(\u6c34)"}
                    _RX   = {
                        "\u6728": "\ub3d9\ucabd \ubc29\ud5a5, \ucd08\ub85d\uc0c9 \ud65c\uc6a9, \uc0c8\ubcbd \uc0b0\ucc45, \ub098\ubb34\u00b7\uc2dd\ubb3c \uac00\uae4c\uc774",
                        "\u706b": "\ub0a8\ucabd \ubc29\ud5a5, \ubd89\uc740\uc0c9 \ud65c\uc6a9, \ubc1d\uc740 \uc0ac\uad50\ud65c\ub3d9, \ud587\ube5b \ucce8\uae30",
                        "\u571f": "\uc911\uc559\u00b7\ud669\ud1a0\uc0c9 \ud65c\uc6a9, \uaddc\uce59\uc801 \uc0dd\ud65c, \ud669\uc0c9 \uacc4\uc5f4 \uc74c\uc2dd",
                        "\u91d1": "\uc11c\ucabd \ubc29\ud5a5, \ud770\uc0c9\u00b7\uc740\uc0c9 \ud65c\uc6a9, \uc6d0\uce59 \uc138\uc6b0\uae30, \uae08\uc18d \uc18c\ud488",
                        "\u6c34": "\ubd81\ucabd \ubc29\ud5a5, \uac80\uc740\uc0c9 \ud65c\uc6a9, \ub3c5\uc11c\u00b7\uba85\uc0c1, \ubb3c\uac00 \uc0b0\ucc45",
                    }
                    if not _yong:
                        y = _write("\uc6a9\uc2e0 \uc815\ubcf4\ub97c \ubd88\ub7ec\uc624\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.", y, size=9)
                    for _yo in _yong[:3]:
                        y = _write(
                            f"\uc6a9\uc2e0({_OHN.get(_yo, _yo)}) \uac1c\uc6b4\ubc95: "
                            f"{_RX.get(_yo, '')}", y, size=9)

                elif tab_name == "ohaeng":
                    y = _sec("\u262f\ufe0f \uc74c\uc591\uc624\ud589 \uc2ec\uce35 \ubd84\uc11d", y)
                    y = _write(LocalSajuNarrator.full_report(
                        pils, name, birth_year, gender)[:4000], y, size=9)

                elif tab_name == "tojeong":
                    y = _sec("\U0001f4dc \ud1a0\uc815\ube44\uacb0", y)
                    _sw   = get_yearly_luck(pils, _cur_yr) or {}
                    _ss_t = _sw.get("\uc2ed\uc131_\ucc9c\uac04", "")
                    _gh_t = _sw.get("\uae38\ud751", "\ud3c9")
                    _age_t = _cur_yr - birth_year + 1
                    y = _write(
                        f"{_cur_yr}\ub144 {_age_t}\uc138 \u2014 {_ss_t} [{_gh_t}]",
                        y, size=11)
                    _TJ = {
                        "\u98df\u795e": f"{_cur_yr}\ub144\uc740 \uc7ac\ub2a5\uc774 \uaf43\ud53c\ub294 \ubcf5\ub85d\uc758 \ud574\uc785\ub2c8\ub2e4.",
                        "\u6b63\u8ca1": f"{_cur_yr}\ub144\uc740 \ucc29\uc2e4\ud788 \uc313\uc774\ub294 \uc7ac\ubb3c\uc758 \ud574\uc785\ub2c8\ub2e4.",
                        "\u504f\u8ca1": f"{_cur_yr}\ub144\uc740 \uc7ac\ubb3c\uacfc \ubcc0\ud654\uc758 \ud574\uc785\ub2c8\ub2e4.",
                        "\u6b63\u5b98": f"{_cur_yr}\ub144\uc740 \uba85\uc608\uc640 \uc2b9\uc9c4\uc758 \ud574\uc785\ub2c8\ub2e4.",
                        "\u504f\u5b98": f"{_cur_yr}\ub144\uc740 \uae34\uc7a5\uacfc \ubcc0\ub3d9\uc758 \ud574. \uac74\uac15 \uc8fc\uc758\ud558\uc2ed\uc2dc\uc624.",
                        "\u52ab\u8ca1": f"{_cur_yr}\ub144\uc740 \uc7ac\ubb3c \uc190\uc2e4 \uc8fc\uc758. \ud22c\uc790\u00b7\ubcf4\uc99d \uc0bc\uac00\ud558\uc2ed\uc2dc\uc624.",
                        "\u5461\u5b98": f"{_cur_yr}\ub144\uc740 \ucc3d\uc758\uc131\uc758 \ud574. \uc717\uc0ac\ub78c \ub9c8\ucc30 \uc870\uc2ec\ud558\uc2ed\uc2dc\uc624.",
                        "\u504f\u5370": f"{_cur_yr}\ub144\uc740 \ubcc0\ud654\u00b7\uc774\ub3d9\uc758 \ud574. \ud070 \uacb0\uc815\uc740 \uc2e0\uc911\ud788.",
                        "\u6b63\u5370": f"{_cur_yr}\ub144\uc740 \ud559\uc5c5\u00b7\uc790\uaca9\uc758 \ud574. \ubc30\uc6c0\uc5d0 \uc9d1\uc911\ud558\uc2ed\uc2dc\uc624.",
                        "\u6bd4\u80a9": f"{_cur_yr}\ub144\uc740 \ub3c5\ub9bd\uc2ec \uac15\ud574\uc9c0\ub294 \ud574. \ub2e8\ub3c5 \ud589\ub3d9 \uc720\ub9ac.",
                    }
                    y = _write(
                        _TJ.get(_ss_t, f"{_cur_yr}\ub144 {_ss_t} \uae30\uc6b4\uc758 \ud574\uc785\ub2c8\ub2e4."),
                        y, size=9)

                elif tab_name == "current_situation":
                    y = _sec("\U0001f3af \ud604\uc7ac \uc0c1\ud669 \uc9c4\ub2e8", y)
                    y = _write(LocalSajuNarrator.full_report(
                        pils, name, birth_year, gender)[:3000], y, size=9)

                # ── 푸터 ─────────────────────────────────────────────────
                c.setFont(_BF, 8)
                c.setFillColorRGB(0.5, 0.45, 0.35)
                c.drawString(MARGIN, 12*mm, "\ub9cc\uc138\ub825 \uc0ac\uc8fc \ucc9c\uba85\ud480\uc774")
                c.drawRightString(W - MARGIN, 12*mm,
                                  f"{_dt2.now().strftime('%Y.%m.%d')} \ucd9c\ub825")
                c.save()
                _buf.seek(0)

                st.download_button(
                    label=f"📥 {_label} PDF \ub2e4\uc6b4\ub85c\ub4dc",
                    data=_buf.read(),
                    file_name=(
                        f"\uc0ac\uc8fc_{name}_{_label}"
                        f"_{_dt2.now().strftime('%Y%m%d')}.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"pdf_dl_{tab_name}",
                )
                st.success(f"✅ {_label} PDF \uc0dd\uc131 \uc644\ub8cc!")

            except ImportError:
                st.error("❌ reportlab \ubbf8\uc124\uce58. pip install reportlab \uc2e4\ud589 \ud544\uc694")
            except Exception as _pe:
                st.error(f"❌ PDF \uc624\ub958: {str(_pe)[:80]}")'''

# ── 교체 실행 ────────────────────────────────────────────────────────────────
if OLD in src:
    src = src.replace(OLD, NEW)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)
    print("render_pdf_download_btn 교체 완료")
elif '"""각 탭 전용 PDF 즉시 생성 버튼"""' in src:
    print("이미 적용됨 -- 교체 생략")
else:
    print("WARNING: 교체 대상 함수를 찾지 못했습니다. manse.py를 확인하세요.")
    sys.exit(1)

# ── 문법 검사 ────────────────────────────────────────────────────────────────
try:
    py_compile.compile(TARGET, doraise=True)
    print("문법 OK")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
    sys.exit(1)
