# fix_current_status.py
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()

# ── 수정 1: 현재 상태 진단 텍스트 확장 ──
_OLD_DIAG = '''\
        _DIAG_HOT = {
            "火": f"{name}님의 사주는 태어난 계절에 불(火)기운이 집중되어, 전체적으로 에너지가 넘치고 뜨거운 사주입니다. 열정이 넘치고 추진력이 강하지만, 때로는 쉽게 지치거나 감정의 기복이 올 수 있습니다.",
            "木": f"{name}님의 사주는 木기운이 강하여 성장과 도전의 기운이 넘칩니다. 창의적이고 진취적이나 때로는 주변과 마찰이 생기기도 합니다.",
            "土": f"{name}님의 사주는 土기운이 강하여 안정과 신뢰의 기운이 중심입니다. 묵직하고 포용력이 크나 변화에 적응하는 데 시간이 걸릴 수 있습니다.",
            "金": f"{name}님의 사주는 金기운이 강하여 냉철하고 결단력 있는 기운이 중심입니다. 원칙과 의리가 강하나 때로는 고집스럽게 보일 수 있습니다.",
            "水": f"{name}님의 사주는 水기운이 강하여 지혜롭고 유연한 기운이 중심입니다. 통찰력이 뛰어나나 때로는 우유부단하거나 감정이 깊어질 수 있습니다.",
        }
        _DIAG_COLD = f"{name}님의 사주는 태어난 계절이 겨울로 차갑고 얼어붙은 기운이 강합니다. 인내심과 깊이가 있으나, 만물을 녹여줄 따뜻한 기운이 절실히 필요한 구조입니다."
        _DIAG_WEAK = f"반면 {_OHN2.get(_oh_min2,\'\')} 기운이 매우 부족하여, 이 오행과 관련된 영역(직업·건강·관계)에서 불균형이 나타나기 쉽습니다."'''

_NEW_DIAG = '''\
        _DIAG_HOT = {
            "火": (
                f"{name}님의 사주는 태어난 계절에 불(火)기운이 집중되어 있어, 전체적으로 에너지가 넘치고 뜨거운 사주입니다. "
                f"열정이 넘치고 추진력이 강하여 한번 목표를 정하면 강하게 밀어붙이는 기질이 있습니다. "
                f"사람들에게 활력을 불어넣는 능력이 있어 자연스럽게 주목받는 자리에 서게 됩니다. "
                f"다만 뜨거운 기운이 과하면 쉽게 지치거나 감정 기복이 생길 수 있으며, "
                f"충동적인 결정이나 과열된 경쟁으로 스스로를 소진시키는 경우도 있습니다. "
                f"지금 이 순간 {name}님의 가장 큰 숙제는 열정의 방향을 잘 조율하는 것입니다."
            ),
            "木": (
                f"{name}님의 사주는 木기운이 강하여 성장과 도전, 개척의 기운이 넘칩니다. "
                f"새로운 것을 시작하고 앞으로 나아가는 추진력이 탁월하며, 창의적인 아이디어가 끊임없이 샘솟습니다. "
                f"리더십과 독립심이 강해 스스로 길을 개척하는 타입이지만, "
                f"지나치게 앞서나가거나 고집스럽게 자신의 방향만 고집할 때 주변과 마찰이 생기기도 합니다. "
                f"균형 잡힌 성장을 위해 때로는 뒤를 돌아보고 주변의 의견에 귀 기울이는 여유가 필요합니다."
            ),
            "土": (
                f"{name}님의 사주는 土기운이 강하여 안정, 신뢰, 포용의 기운이 중심을 잡고 있습니다. "
                f"어떤 상황에서도 흔들리지 않는 묵직한 안정감이 있어 주변 사람들이 자연스럽게 의지합니다. "
                f"실속을 중시하고 현실적인 판단력이 뛰어나며 한번 맺은 인연을 소중히 여깁니다. "
                f"다만 변화를 싫어하고 새로운 환경에 적응하는 데 시간이 걸리며, "
                f"지나친 고집과 완고함이 발전의 걸림돌이 될 수 있습니다. "
                f"유연한 사고를 의식적으로 기르는 것이 지금 {name}님에게 가장 필요한 과제입니다."
            ),
            "金": (
                f"{name}님의 사주는 金기운이 강하여 냉철함, 결단력, 원칙의 기운이 중심입니다. "
                f"한번 결정하면 끝까지 밀고 나가는 강인한 의지와 날카로운 판단력이 돋보입니다. "
                f"의리와 원칙을 지키는 성품으로 신뢰를 얻으며 어떤 난관도 돌파해내는 저력이 있습니다. "
                f"하지만 지나치게 냉정하거나 융통성이 없어 보일 때 인간관계에 마찰이 생기기도 합니다. "
                f"강직함을 유지하되 상대방의 감정을 헤아리는 따뜻함을 더한다면 {name}님의 영향력은 더욱 커질 것입니다."
            ),
            "水": (
                f"{name}님의 사주는 水기운이 강하여 지혜, 유연함, 깊은 사색의 기운이 중심입니다. "
                f"복잡한 상황을 꿰뚫어 보는 통찰력과 다양한 상황에 적응하는 유연성이 탁월합니다. "
                f"내면이 풍요롭고 감수성이 뛰어나 예술·연구·철학 분야에서 남다른 능력을 발휘합니다. "
                f"다만 물처럼 너무 넓게 퍼지면 깊이가 없어지듯, 에너지가 분산되거나 "
                f"지나친 사색으로 결정을 미루는 우유부단함이 약점이 될 수 있습니다. "
                f"지금 {name}님에게는 생각을 행동으로 옮기는 결단력이 무엇보다 중요합니다."
            ),
        }
        _DIAG_COLD = (
            f"{name}님의 사주는 태어난 계절이 겨울로, 차갑고 얼어붙은 기운이 강한 구조입니다. "
            f"깊은 인내심과 통찰력, 묵묵히 견뎌내는 강인함이 내면에 자리 잡고 있습니다. "
            f"혼자서도 오랜 시간 버텨내는 저력이 있지만, 때로는 그 냉기가 감정의 벽이 되어 "
            f"가까운 사람들과의 소통을 어렵게 만들기도 합니다. "
            f"만물을 녹여줄 따뜻한 불(火)의 기운이 절실히 필요한 구조로, "
            f"따뜻한 인간관계와 정서적 교류가 {name}님의 운을 여는 핵심 열쇠입니다."
        )
        _DIAG_WEAK = (
            f"특히 {_OHN2.get(_oh_min2,\'\')} 기운이 사주 내에서 매우 부족합니다. "
            f"이 오행이 담당하는 영역 — 직업·건강·인간관계 중 한 곳에서 반복적인 어려움이 생기기 쉽습니다. "
            f"이 부족한 기운을 의식적으로 보완하는 것이 {name}님 인생의 균형을 잡는 핵심입니다."
        )'''

if _OLD_DIAG in src:
    src = src.replace(_OLD_DIAG, _NEW_DIAG)
    print("수정 1 적용됨")
else:
    print("수정 1 불일치 — 스킵 (이미 적용됐거나 텍스트 다름)")

with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 저장 완료")

# ── 수정 2: PDF에 현재 상태 섹션 추가 ──
with open("saju_report.py", encoding="utf-8") as f:
    rep = f.read()

_PDF_INJECT = '''
def _pdf_current_status(pils, name, birth_year, gender, story, styles):
    """PDF용 현재 상태 진단 섹션"""
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.units import mm
    elements = []
    try:
        from saju_interpreter import get_yongshin, get_ilgan_strength
        from saju_engine import calc_ohaeng_strength, OH
        ilgan = pils[1]["cg"]
        oh_s = calc_ohaeng_strength(ilgan, pils)
        oh_max = max(oh_s, key=oh_s.get) if oh_s else ""
        oh_min = min(oh_s, key=oh_s.get) if oh_s else ""
        wol_jj = pils[2]["jj"] if len(pils) > 2 else ""
        OHN = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","水":"수(水)"}
        cold = ["亥","子","丑"]

        _DIAG = {
            "火": f"{name}님의 사주는 불(火)기운이 집중된 뜨거운 사주입니다. 열정과 추진력이 강하지만 감정 기복과 소진을 주의해야 합니다.",
            "木": f"{name}님의 사주는 木기운이 강한 성장·도전의 사주입니다. 창의성과 리더십이 뛰어나나 주변과의 마찰을 조심하십시오.",
            "土": f"{name}님의 사주는 土기운이 강한 안정·신뢰의 사주입니다. 포용력이 크나 변화 적응에 시간이 필요합니다.",
            "金": f"{name}님의 사주는 金기운이 강한 냉철·결단의 사주입니다. 의리와 원칙이 강하나 유연함을 기르는 것이 과제입니다.",
            "水": f"{name}님의 사주는 水기운이 강한 지혜·통찰의 사주입니다. 뛰어난 통찰력이 있으나 결단력을 키우는 것이 중요합니다.",
        }
        cold_txt = f"{name}님의 사주는 겨울 태생으로 차가운 기운이 강합니다. 따뜻한 인간관계와 정서적 교류가 운을 여는 열쇠입니다."

        diag_txt = cold_txt if wol_jj in cold else _DIAG.get(oh_max, "")
        weak_txt = f"※ {OHN.get(oh_min,'')} 기운이 부족하여 관련 영역에서 불균형이 나타나기 쉽습니다. 의식적인 보완이 필요합니다." if oh_min else ""

        elements.append(Paragraph("▣ 현재 상태 진단", styles["Heading2"]))
        elements.append(Spacer(1, 3*mm))
        if diag_txt:
            elements.append(Paragraph(diag_txt, styles["BodyText"]))
            elements.append(Spacer(1, 2*mm))
        if weak_txt:
            elements.append(Paragraph(weak_txt, styles["BodyText"]))
            elements.append(Spacer(1, 4*mm))
    except Exception as _e:
        pass
    return elements

'''

if '_pdf_current_status' not in rep:
    # def menu_pdf 앞에 삽입
    if 'def menu_pdf' in rep:
        rep = rep.replace('def menu_pdf', _PDF_INJECT + 'def menu_pdf', 1)
        with open("saju_report.py", "w", encoding="utf-8") as f:
            f.write(rep)
        print("saju_report.py 수정 완료")
    else:
        print("saju_report.py: menu_pdf 함수를 찾을 수 없음")
else:
    print("saju_report.py 이미 적용됨")

import py_compile
for fname in ["saju_interpreter.py", "saju_report.py"]:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"문법 OK: {fname}")
    except py_compile.PyCompileError as e:
        print(f"문법 오류 {fname}: {e}")
