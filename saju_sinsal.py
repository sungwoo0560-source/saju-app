# -*- coding: utf-8 -*-
"""
saju_sinsal.py - 신살(神殺) 계산 모듈
get_sam_hap, get_chung_hyung, get_gongmang, get_nabjin,
_get_extra_sinsal_v1, get_waryeong, get_yangin, get_oigyeok,
get_12sinsal, get_extra_sinsal, get_pahae, get_geunmyo_hwasil 포함
"""
import streamlit as st
from datetime import date, datetime, timedelta
import re
from saju_data import *

def _hash_pils(pils):
    return hash(tuple((p.get("cg", ""), p.get("jj", "")) for p in pils))
_PILS_HF = {list: _hash_pils}
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

@st.cache_data(hash_funcs=_PILS_HF)
def get_sam_hap(pils):

    jjs = set(p["jj"] for p in pils)

    results = []

    for combo, (name, oh, desc) in SAM_HAP_MAP.items():
        if combo.issubset(jjs):
            results.append(
                {
                    "type": "三合",
                    "name": name,
                    "oh": oh,
                    "desc": desc,
                    "narrative": f"🌟 [三合] {desc}으로 {name}이 形成! {oh} 기운이 命盤 전체를 강화하니라.",
                }
            )

    if not results:
        for combo, (name, oh, hap_type) in BAN_HAP_MAP.items():
            if combo.issubset(jjs):
                results.append(
                    {
                        "type": "半合",
                        "name": name,
                        "oh": oh,
                        "desc": hap_type,
                        "narrative": f"- [半合] {name}이 맺어져 {oh} 오행의 결속력이 생기리라.",
                    }
                )

    for combo, (name, oh, hap_type) in BANG_HAP_MAP.items():
        if combo.issubset(jjs):
            results.append(
                {
                    "type": "方合",
                    "name": name,
                    "oh": oh,
                    "desc": hap_type,
                    "narrative": f"🧭 [方合] {name}의 세력이 形成되어 {oh} 오행이 강성해지리라.",
                }
            )

    return results


# ==================================================

#  용신(用神) - 억부/조후/통관

# ==================================================



@st.cache_data(hash_funcs=_PILS_HF)
def get_chung_hyung(pils):
    """충/형/파/해/천간합 분석"""

    jjs = [p["jj"] for p in pils]

    cgs = [p["cg"] for p in pils]

    result = {"충": [], "형": [], "파": [], "해": [], "천간합": [], "자형": []}

    pairs_jj = [(jjs[i], jjs[j]) for i in range(len(jjs)) for j in range(i + 1, len(jjs))]

    pairs_cg = [(cgs[i], cgs[j]) for i in range(len(cgs)) for j in range(i + 1, len(cgs))]

    jj_set = set(jjs)

    for a, b in pairs_jj:
        k = frozenset([a, b])

        if k in CHUNG_MAP:
            n, rel, desc = CHUNG_MAP[k]

            result["충"].append({"name": n, "rel": rel, "desc": desc})

        if k in PA_MAP:
            n, desc = PA_MAP[k]
            result["파"].append({"name": n, "desc": desc})

        if k in HAE_MAP:
            n, desc = HAE_MAP[k]
            result["해"].append({"name": n, "desc": desc})

    for combo, (n, htype, desc) in HYUNG_MAP.items():
        if combo.issubset(jj_set):
            result["형"].append({"name": n, "type": htype, "desc": desc})

    for jj in set(jjs):
        if jjs.count(jj) >= 2 and jj in SELF_HYUNG:
            result["자형"].append({"name": f"{jj} 자형", "desc": "자책/자학 경향 주의"})

    for a, b in pairs_cg:
        k = frozenset([a, b])

        if k in TG_HAP_MAP:
            n, oh, htype = TG_HAP_MAP[k]

            result["천간합"].append(
                {
                    "name": n,
                    "oh": oh,
                    "type": htype,
                    "desc": f"{oh}({OHN.get(oh, '')})으로 화(化) - {htype}",
                }
            )

    return result


# ==================================================

#  공망(空亡)

# ==================================================

# 순중공망(旬中空亡) — 60갑자는 甲으로 시작하는 10개씩 6순(旬)으로 나뉘며,
# 각 순에서 쓰이지 않는 지지 2개가 그 순의 공망이다. 甲子旬=戌亥·甲戌旬=
# 申酉·甲申旬=午未·甲午旬=辰巳·甲辰旬=寅卯·甲寅旬=子丑. 키는 각 순의 시작
# 순번(60갑자 순번 0·10·20·30·40·50, 甲子=0). ★천간 1글자만으로는 순을
# 특정할 수 없다 — 甲子일과 甲戌일은 천간이 같아도 순이 다르고 공망도
# 다르므로, 반드시 일주(day pillar)의 천간+지지 조합 전체로 순을 판정
# 해야 한다(get_sunjung_gongmang 참고).
SUN_GONGMANG = {
    0: ("戌", "亥"),   # 甲子순(甲子~癸酉)
    10: ("申", "酉"),  # 甲戌순(甲戌~癸未)
    20: ("午", "未"),  # 甲申순(甲申~癸巳)
    30: ("辰", "巳"),  # 甲午순(甲午~癸卯)
    40: ("寅", "卯"),  # 甲辰순(甲辰~癸丑)
    50: ("子", "丑"),  # 甲寅순(甲寅~癸亥)
}


def get_sunjung_gongmang(cg, jj):
    """간지(주로 일주) 60갑자로 순중공망(旬中空亡) 지지 2개를 구한다.
    천간+지지 조합의 60갑자 순번을 직접 역산해 그 순의 시작점을 찾고,
    SUN_GONGMANG에서 해당 순의 공망을 반환한다."""
    try:
        cg_idx = CG.index(cg)
        jj_idx = JJ.index(jj)
    except ValueError:
        return ("", "")
    for idx in range(60):
        if idx % 10 == cg_idx and idx % 12 == jj_idx:
            return SUN_GONGMANG[idx - (idx % 10)]
    return ("", "")

GONGMANG_JJ_DESC = {
    "子": "자(子(자)) 공망 - 지혜/재물 기운이 허공에 뜹니다. 재물과 학업에 공허함이 따릅니다.",
    "丑": "축(丑(축)) 공망 - 인내/축적의 기운이 약해집니다. 노력이 물거품이 되는 경험을 합니다.",
    "寅": "인(寅(인)) 공망 - 성장/시작의 기운이 막힙니다. 새 출발이 쉽지 않습니다.",
    "卯": "묘(卯(묘)) 공망 - 창의/예술 기운이 허공에 뜹니다. 재능이 있어도 인정받기 어렵습니다.",
    "辰": "진(辰(진)) 공망 - 관직/조직 기운이 약해집니다. 직장/관직과의 인연이 불안정합니다.",
    "巳": "사(巳(사)) 공망 - 지혜/재능의 기운이 허공에 뜹니다. 화려함이 있어도 결실이 약합니다.",
    "午": "오(午(오)) 공망 - 명예/인정의 기운이 약해집니다. 노력 대비 인정받기 어렵습니다.",
    "未": "미(未(미)) 공망 - 재물/안정 기운이 허공에 뜹니다. 모아도 새는 재물 기운입니다.",
    "申": "신(申(신)) 공망 - 변화/이동 기운이 막힙니다. 새 환경으로의 변화가 어렵습니다.",
    "酉": "유(酉(유)) 공망 - 완성/결실의 기운이 약해집니다. 마무리가 항상 아쉽게 끝납니다.",
    "戌": "술(戌(술)) 공망 - 저장/축적의 기운이 허공에 뜹니다. 창고가 있어도 채우기 어렵습니다.",
    "亥": "해(亥(해)) 공망 - 지혜/영성의 기운이 약해집니다. 깊은 학문과 영적 기운이 허공에 뜹니다.",
}


@st.cache_data(hash_funcs=_PILS_HF)
def get_gongmang(pils):
    """공망(空亡) 계산 — 정통 순중공망(旬中空亡), 일주(day pillar) 60갑자
    기준. 일주의 천간+지지 조합 전체로 어느 순(旬)에 속하는지 판정한다."""

    il_cg = pils[1]["cg"] if len(pils) > 1 else ""
    il_jj = pils[1]["jj"] if len(pils) > 1 else ""

    gong_pair = get_sunjung_gongmang(il_cg, il_jj)

    result = {"공망_지지": gong_pair, "해당_기둥": []}

    for i, p in enumerate(pils):
        label = ["시주", "일주", "월주", "년주"][i]

        if p["jj"] in gong_pair:
            result["해당_기둥"].append(
                {
                    "기둥": label,
                    "지지": p["jj"],
                    "desc": GONGMANG_JJ_DESC.get(p["jj"], ""),
                }
            )

    return result


# ==================================================

#  일주론(日柱論) | 60갑자

# ==================================================


# ==================================================

#  납음오행(納音五行)

# ==================================================



@st.cache_data(hash_funcs=_PILS_HF)
def get_nabjin(cg, jj):

    pillar = cg + jj

    for k, v in NABJIN_MAP.items():
        if pillar in k:
            name, oh, desc = v

            return {"name": name, "oh": oh, "desc": desc}

    return {"name": "미상", "oh": "", "desc": ""}


# ==================================================

#  육친론(六親論)

# ==================================================


@st.cache_data(hash_funcs=_PILS_HF)
def _get_extra_sinsal_v1(pils):
    """기본 신살 감지 (원진/귀문/백호/양인/화개) - 내부용. 전체버전은 get_extra_sinsal() 사용"""

    ilgan = pils[1]["cg"]

    jjs = [p["jj"] for p in pils]

    jj_set = set(jjs)

    result = []

    pairs_jj = [(jjs[i], jjs[j]) for i in range(len(jjs)) for j in range(i + 1, len(jjs))]

    for a, b in pairs_jj:
        if (a, b) in EXTRA_SINSAL_DATA["원진"]["pairs"] or (b, a) in EXTRA_SINSAL_DATA["원진"]["pairs"]:
            d = EXTRA_SINSAL_DATA["원진"]

            result.append(
                {
                    "name": d["name"],
                    "icon": d["icon"],
                    "desc": d["desc"],
                    "remedy": d["remedy"],
                    "found": f"{a}/{b}",
                }
            )

            break

    for a, b in pairs_jj:
        if (a, b) in EXTRA_SINSAL_DATA["귀문"]["pairs"] or (b, a) in EXTRA_SINSAL_DATA["귀문"]["pairs"]:
            d = EXTRA_SINSAL_DATA["귀문"]

            result.append(
                {
                    "name": d["name"],
                    "icon": d["icon"],
                    "desc": d["desc"],
                    "remedy": d["remedy"],
                    "found": f"{a}/{b}",
                }
            )

            break

    for i, p in enumerate(pils):
        if p["cg"] + p["jj"] in EXTRA_SINSAL_DATA["백호"]["combos"]:
            d = EXTRA_SINSAL_DATA["백호"]

            label = ["시주", "일주", "월주", "년주"][i]

            result.append(
                {
                    "name": f"{d['name']} [{label}]",
                    "icon": d["icon"],
                    "desc": d["desc"],
                    "remedy": d["remedy"],
                    "found": p["str"],
                }
            )

    yang_jj = EXTRA_SINSAL_DATA["양인"]["jjs"].get(ilgan, "")

    if yang_jj and yang_jj in jj_set:
        d = EXTRA_SINSAL_DATA["양인"]

        result.append(
            {
                "name": f"{d['name']} [{yang_jj}]",
                "icon": d["icon"],
                "desc": d["desc"],
                "remedy": d["remedy"],
                "found": yang_jj,
            }
        )

    for combo, hg_jj in EXTRA_SINSAL_DATA["화개"]["map"].items():
        if hg_jj in jj_set and any(jj in combo for jj in jj_set):
            d = EXTRA_SINSAL_DATA["화개"]

            result.append(
                {
                    "name": f"{d['name']} [{hg_jj}]",
                    "icon": d["icon"],
                    "desc": d["desc"],
                    "remedy": d["remedy"],
                    "found": hg_jj,
                }
            )

            break

    return result


# ==================================================

#  🗓️ 만세력 엔진 (ManseCalendarEngine)

#  일진 / 절기 / 길일흉일 계산

# ==================================================

# 24절기 기본 날짜 (연도별 미세 차이는 A단계 라이브러리로 정밀화)


# 길일/흉일 기준 - 일진의 천간 기준 간단 판별

_GIL_CG = {"甲", "丙", "戊", "庚", "壬"}  # 양간 = 기본 길일

_HYUNG_JJ = {"丑", "戌", "巳", "申", "寅"}  # 삼형살 지지

_GIL_JJ = {"子", "卯", "午", "酉", "亥", "寅"}  # 귀인 지지 포함


@st.cache_data(hash_funcs=_PILS_HF)
def get_waryeong(pils):

    wol_jj = pils[2]["jj"] if len(pils) > 2 else ""

    result = {}

    grades = [
        (
            85,
            "왕(旺)",
            "#c0392b",
            "月令에서 가장 강한 기운. 이 오행이 사주를 주도합니다.",
        ),
        (60, "상(相)", "#e67e22", "月令의 지원을 받아 활발한 기운입니다."),
        (35, "휴(休)", "#f39c12", "月令에서 힘을 얻지 못하고 쉬는 기운입니다."),
        (15, "수(囚)", "#7f8c8d", "月令에서 억눌림을 받는 기운입니다."),
        (0, "사(死)", "#2c3e50", "月令에서 가장 힘을 잃은 기운입니다."),
    ]

    for oh in ["木", "火", "土", "金", "水"]:
        score = WARYEONG_TABLE[oh].get(wol_jj, 20)

        label, color, desc = "평", "#888", ""

        for threshold, lbl, col, dsc in grades:
            if score >= threshold:
                label, color, desc = lbl, col, dsc

                break

        result[oh] = {"score": score, "grade": label, "color": color, "desc": desc}

    return {"월지": wol_jj, "계절": JJ_MONTH_SEASON.get(wol_jj, ""), "오행별": result}


# ==================================================

#  외격(外格) + 양인(羊刃)

# ==================================================

YANGIN_MAP = {
    "甲": "卯",
    "丙": "午",
    "戊": "午",
    "庚": "酉",
    "壬": "子",
}

# 陰刃 유파 확장분 — 정통 양인(羊刃) 판정에서 제외(H1, 출처 미상).
# 양인은 양간의 제왕(帝旺)이 겁재와 겹칠 때 성립하는 개념이며, 음간은
# 12운성 역행으로 제왕과 겁재가 불일치해 정의상 성립하지 않는다.
# 참고용으로만 보존, get_yangin()은 이 상수를 참조하지 않는다.
_EUMIN_MAP_UNUSED = {
    "乙": "辰",
    "丁": "未",
    "己": "未",
    "辛": "戌",
    "癸": "丑",
}



@st.cache_data(hash_funcs=_PILS_HF)
def get_yangin(pils):

    ilgan = pils[1]["cg"]

    yangin_jj = YANGIN_MAP.get(ilgan, "")

    found = [["시주", "일주", "월주", "년주"][i] for i, p in enumerate(pils) if p["jj"] == yangin_jj]

    return {
        "일간": ilgan,
        "양인_지지": yangin_jj,
        "존재": bool(found),
        "위치": found,
        "설명": YANGIN_DESC.get(ilgan, {}),
    }


@st.cache_data(hash_funcs=_PILS_HF)
def get_oigyeok(pils):

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    # ✅ 외부함수 호출 예외처리
    try:
        oh_strength = calc_ohaeng_strength(ilgan, pils)
    except Exception:
        oh_strength = {"木": 20, "火": 20, "土": 20, "金": 20, "水": 20}

    try:
        strength_info = get_ilgan_strength(ilgan, pils)
        sn = strength_info.get("신강신약", "신약(身弱)") if strength_info else "신약(身弱)"
    except Exception:
        sn = "신약(身弱)"

    CTRL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

    BIRTH_R = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

    GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

    results = []

    # 종왕격

    if oh_strength.get(ilgan_oh, 0) >= 70 and sn == "신강(身强)":
        results.append(
            {
                "격": "종왕격(從旺格)",
                "icon": "👑",
                "color": "#000000",
                "desc": f"일간 오행({OHN.get(ilgan_oh, '')})이 사주를 지배. 같은 오행을 돕는 것이 용신.",
                "용신": f"{ilgan_oh}/{BIRTH_R.get(ilgan_oh, '')}",
                "기신": f"{CTRL.get(ilgan_oh, '')}",
                "caution": "종왕격을 내격으로 착각하면 완전히 반대 풀이가 됩니다.",
            }
        )

    # 종재격

    jae_oh = CTRL.get(ilgan_oh, "")

    if oh_strength.get(jae_oh, 0) >= 55 and sn == "신약(身弱)":
        results.append(
            {
                "격": "종재격(從財格)",
                "icon": "💰",
                "color": "#2980b9",
                "desc": f"재성({OHN.get(jae_oh, '')})이 사주를 압도. 재성을 따르는 것이 순리.",
                "용신": f"{jae_oh}/{GEN.get(jae_oh, '')}",
                "기신": f"{ilgan_oh} 비겁/{BIRTH_R.get(ilgan_oh, '')} 인성",
                "caution": "비겁/인성 운이 오면 오히려 크게 파란이 생깁니다.",
            }
        )

    # 종관격

    gwan_oh = next((k for k, v in CTRL.items() if v == ilgan_oh), "")

    if oh_strength.get(gwan_oh, 0) >= 55 and sn == "신약(身弱)":
        results.append(
            {
                "격": "종관격(從官格)",
                "icon": "🎖️",
                "color": "#27ae60",
                "desc": f"관성({OHN.get(gwan_oh, '')})이 사주를 지배. 공직/관직에서 크게 발복.",
                "용신": f"{gwan_oh}/{jae_oh}",
                "기신": f"{ilgan_oh} 비겁",
                "caution": "비겁이 오면 구설/관재가 생기기 쉽습니다.",
            }
        )

    # 종아격

    sik_oh = GEN.get(ilgan_oh, "")

    if oh_strength.get(sik_oh, 0) >= 55 and sn == "신약(身弱)":
        results.append(
            {
                "격": "종아격(從兒格)",
                "icon": "🎨",
                "color": "#8e44ad",
                "desc": f"식상({OHN.get(sik_oh, '')})이 사주를 지배. 창의/예술/기술의 기운 압도적.",
                "용신": f"{sik_oh}/{CTRL.get(ilgan_oh, '')}",
                "기신": "관성/인성",
                "caution": "관성/인성 운에서 건강/사고/좌절이 오기 쉽습니다.",
            }
        )

    return results


# ==================================================

#  12신살(十二神殺) 완전판

# ==================================================





@st.cache_data(hash_funcs=_PILS_HF)
def get_12sinsal(pils):

    nyon_jj = pils[3]["jj"] if len(pils) > 3 else ""

    pil_jjs = [p["jj"] for p in pils]

    labels = ["시주", "일주", "월주", "년주"]

    san_groups = [
        "寅(인)午(오)戌(술)",
        "申(신)子(자)辰(진)",
        "巳(사)酉(유)丑(축)",
        "亥(해)卯(묘)未(미)",
    ]

    my_group = next((g for g in san_groups if nyon_jj in g), "寅(인)午(오)戌(술)")

    result = []

    for sname, jj_map in SINSAL_12_TABLE.items():
        sinsal_jj = jj_map.get(my_group, "")

        found = [labels[i] for i, jj in enumerate(pil_jjs) if jj == sinsal_jj]

        if found:
            d = SINSAL_12_DESC.get(sname, {})

            result.append(
                {
                    "이름": d.get("name", sname),
                    "icon": d.get("icon", "-"),
                    "type": d.get("type", "중"),
                    "위치": found,
                    "해당지지": sinsal_jj,
                    "desc": d.get("desc", ""),
                    "good": d.get("good", ""),
                    "caution": d.get("caution", ""),
                }
            )

    # 추가 신살

    jj_pairs = [frozenset([pil_jjs[i], pil_jjs[j]]) for i in range(4) for j in range(i + 1, 4)]

    for skey, sd in EXTRA_SINSAL.items():
        if skey in ("귀문관살", "원진살"):
            if any(p in sd["pairs"] for p in jj_pairs):
                result.append(
                    {
                        "이름": sd["name"],
                        "icon": sd["icon"],
                        "type": sd["type"],
                        "위치": ["사주내"],
                        "해당지지": "-",
                        "desc": sd["desc"],
                        "good": sd["good"],
                        "caution": sd["caution"],
                    }
                )

        elif skey == "백호대살":
            bh = [f"{p['cg']}{p['jj']}" for p in pils if f"{p['cg']}{p['jj']}" in sd["targets"]]

            if bh:
                result.append(
                    {
                        "이름": sd["name"],
                        "icon": sd["icon"],
                        "type": sd["type"],
                        "위치": bh,
                        "해당지지": "-",
                        "desc": sd["desc"],
                        "good": sd["good"],
                        "caution": sd["caution"],
                    }
                )

    # ── 상문살(喪門殺) / 조객살(弔客殺) ─────────────────────────
    _SANGMUN_MAP = {
        "子": "寅", "丑": "卯", "寅": "辰", "卯": "巳",
        "辰": "午", "巳": "未", "午": "申", "未": "酉",
        "申": "戌", "酉": "亥", "戌": "子", "亥": "丑",
    }
    _JOKAEK_MAP = {
        "子": "戌", "丑": "亥", "寅": "子", "卯": "丑",
        "辰": "寅", "巳": "卯", "午": "辰", "未": "巳",
        "申": "午", "酉": "未", "戌": "申", "亥": "酉",
    }
    _nyon_jj = pils[3]["jj"] if len(pils) > 3 else ""
    _pil_jjs = [p["jj"] for p in pils]
    _labels  = ["시주", "일주", "월주", "년주"]

    # 상문살
    _sangmun_jj = _SANGMUN_MAP.get(_nyon_jj, "")
    for _i, (_jj, _lbl) in enumerate(zip(_pil_jjs, _labels)):
        if _sangmun_jj and _jj == _sangmun_jj:
            result.append({
                "이름": "상문살(喪門殺)",
                "name": "상문살",
                "icon": "⚰️",
                "위치": _lbl,
                "pos": _lbl,
                "desc": (
                    "상문살(喪門殺)이 있습니다. "
                    "초상·죽음·이별의 기운이 드나드는 문이 열려 있는 신살입니다. "
                    "주변 가까운 사람의 부고 소식을 접하거나, "
                    "본인의 건강이 급격히 악화되는 시기가 옵니다. "
                    "대운·세운에서 상문살이 겹칠 때는 특히 주의가 필요합니다."
                ),
                "remedy": (
                    "처방: 병원 정기 검진을 미루지 마십시오. "
                    "조상 제사와 기제사를 정성껏 지내면 흉기가 완화됩니다. "
                    "장례식장·납골당 방문을 최소화하고, 문상 후 반드시 소금으로 정화하십시오."
                ),
            })
            break  # 중복 방지

    # 조객살
    _jokaek_jj = _JOKAEK_MAP.get(_nyon_jj, "")
    for _i, (_jj, _lbl) in enumerate(zip(_pil_jjs, _labels)):
        if _jokaek_jj and _jj == _jokaek_jj:
            result.append({
                "이름": "조객살(弔客殺)",
                "name": "조객살",
                "icon": "🪦",
                "위치": _lbl,
                "pos": _lbl,
                "desc": (
                    "조객살(弔客殺)이 있습니다. "
                    "상문살과 짝을 이루는 신살로, 문상을 자주 가거나 "
                    "죽음·이별과 관련된 일이 주변에 많이 생기는 기운입니다. "
                    "감정적으로 우울하고 무기력해지는 시기가 반복됩니다."
                ),
                "remedy": (
                    "처방: 주변 사람들의 건강에 관심을 기울이십시오. "
                    "본인도 정기 검진을 철저히 받으십시오. "
                    "밝은 색상의 옷을 착용하고 긍정적인 기운의 환경을 만드십시오."
                ),
            })
            break  # 중복 방지

    # ── 관재수(官災數) ────────────────────────────────────────────
    # 년지 기준 형살 지지 매핑 (삼형·상형 포함)
    _GWANJAE_MAP = {
        "子": ["卯"],
        "丑": ["戌", "未"],
        "寅": ["巳", "申"],
        "卯": ["子"],
        "辰": ["辰"],  # 자형
        "巳": ["寅", "申"],
        "午": ["午"],  # 자형
        "未": ["丑", "戌"],
        "申": ["寅", "巳"],
        "酉": ["酉"],  # 자형
        "戌": ["丑", "未"],
        "亥": ["亥"],  # 자형
    }
    _gwanjae_targets = set(_GWANJAE_MAP.get(_nyon_jj, []))
    for _i, (_jj, _lbl) in enumerate(zip(_pil_jjs, _labels)):
        if _gwanjae_targets and _jj in _gwanjae_targets:
            result.append({
                "이름": "관재수(官災數)",
                "name": "관재수",
                "icon": "⚖️",
                "위치": _lbl,
                "pos": _lbl,
                "desc": (
                    "관재수(官災數)가 있습니다. "
                    "법적 분쟁·소송·관청 문제가 생기기 쉬운 기운입니다. "
                    "편관(칠살)의 기운이 형살과 맞물려 관재·구설·처벌의 흉기가 발동합니다. "
                    "계약·보증·서류 관련 일에서 예상치 못한 분쟁이 발생하거나, "
                    "직장·관청과의 마찰로 억울한 상황이 생길 수 있습니다."
                ),
                "remedy": (
                    "처방: 계약서와 서류를 반드시 꼼꼼히 확인하십시오. "
                    "보증·연대보증은 절대 서지 마십시오. "
                    "분쟁 소지가 있는 거래는 피하고, 금전 대여도 자제하십시오. "
                    "법적 문제가 생기면 즉시 전문가 조언을 구하십시오."
                ),
            })
            break  # 중복 방지

    # ── 삼재수(三災數) ─────────────────────────────────────────────
    # 세운 년지(올해 지지) 계산: (year - 4) % 12 → 子=0 기준
    _JJ_CYCLE = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    _sewoon_jj = _JJ_CYCLE[(datetime.now().year - 4) % 12]

    # (세운 년지 3년 순서, 삼재에 걸리는 띠 set)
    _SAMJAE_GROUPS = [
        (["寅","卯","辰"], {"申","子","辰"}),
        (["巳","午","未"], {"亥","卯","未"}),
        (["申","酉","戌"], {"寅","午","戌"}),
        (["亥","子","丑"], {"巳","酉","丑"}),
    ]
    _SAMJAE_TYPE = ["들삼재(入三災)", "눌삼재(伏三災)", "날삼재(出三災)"]
    _SAMJAE_TYPE_DESC = [
        "삼재의 첫해로 재난이 들어오는 시기입니다. 이사·창업·큰 계약 등 새 출발을 삼가십시오.",
        "삼재의 한가운데로 재난이 가장 강하게 짓누르는 시기입니다. 건강·재물에 가장 주의가 필요합니다.",
        "삼재의 마지막 해로 재난이 빠져나가는 시기입니다. 끝까지 방심하지 말고 마무리를 신중히 하십시오.",
    ]

    for _sewoon_yrs, _affected_set in _SAMJAE_GROUPS:
        if _sewoon_jj in _sewoon_yrs and _nyon_jj in _affected_set:
            _sj_idx = _sewoon_yrs.index(_sewoon_jj)
            _sj_type = _SAMJAE_TYPE[_sj_idx]
            result.append({
                "이름": f"삼재수(三災數) — {_sj_type}",
                "name": "삼재수",
                "icon": "🔥",
                "위치": "년주",
                "pos": "년주",
                "desc": (
                    f"삼재수(三災數) — {_sj_type}에 해당합니다. "
                    f"{_SAMJAE_TYPE_DESC[_sj_idx]} "
                    "삼재는 화재·수재·풍재(질병·사고)의 세 가지 재난이 몰려오는 3년 기간으로, "
                    "이 기간에는 관재·건강·재물·이별 등 모든 분야에서 흉한 기운이 강해집니다."
                ),
                "remedy": (
                    "처방: 삼재부적을 몸에 지니거나 가정에 봉안하십시오. "
                    "동쪽 방향의 먼 여행과 이사를 삼가십시오. "
                    "새 사업 시작·투자·보증은 삼재 기간이 끝난 후로 미루십시오. "
                    "절(사찰)에서 삼재소멸 기도를 올리면 흉기가 완화됩니다."
                ),
            })
            break  # 삼재는 한 그룹에만 해당

    return result


@st.cache_data(hash_funcs=_PILS_HF)
def get_extra_sinsal(pils):
    """

    고급 신살 감지 로직 (Brain 1 정밀 분석)

    문창귀인, 천을귀인, 귀문관살, 백호대살 등

    """

    ilgan = pils[1]["cg"]

    all_jjs = [p["jj"] for p in pils]

    stars = []

    munchang_map = {
        "甲": "巳",
        "乙": "午",
        "丙": "申",
        "丁": "酉",
        "戊": "申",
        "己": "酉",
        "庚": "亥",
        "辛": "子",
        "壬": "寅",
        "癸": "卯",
    }

    if munchang_map.get(ilgan) in all_jjs:
        stars.append(
            {
                "name": "문창귀인(文昌)",
                "desc": "지혜가 총명하고 학문과 예술에 뛰어난 재능",
            }
        )

    gwimun_pairs = [
        {"子", "酉"},
        {"丑", "午"},
        {"寅", "未"},
        {"卯", "申"},
        {"辰", "亥"},
        {"巳", "戌"},
    ]

    for pair in gwimun_pairs:
        if pair.issubset(set(all_jjs)):
            stars.append(
                {
                    "name": "귀문관살(鬼門)",
                    "desc": "직관력이 뛰어나고 예민한 천재성, 영적 감각",
                }
            )

            break

    baekho = ["甲辰","乙未","丙戌","丁丑","戊辰","壬戌","癸丑"]

    for p in pils:
        if (p["cg"] + p["jj"]) in baekho:
            stars.append(
                {
                    "name": "백호대살(白虎)",
                    "desc": "강한 추진력과 전문성, 압도적인 에너지",
                }
            )

            break

    cheon_eul = {
        "甲": "未",
        "乙": "申",
        "丙": "酉",
        "丁": "亥",
        "戊": "未",
        "己": "申",
        "庚": "丑",
        "辛": "寅",
        "壬": "卯",
        "癸": "巳",
    }

    if cheon_eul.get(ilgan) in all_jjs:
        stars.append(
            {
                "name": "천을귀인(天乙貴人)",
                "desc": "인생의 위기에서 돕는 귀인이 상주하는 최고의 길성",
            }
        )

    # 학당귀인(學堂貴人) – 일간의 장생지가 사주 지지에 있는지
    hakdang_jj = HAKDANG_GWIIN.get(ilgan)
    if hakdang_jj and hakdang_jj in all_jjs:
        stars.append({
            "name": "학당귀인(學堂貴人)",
            "desc": HAKDANG_DESC,
        })

    # 암록(暗祿) – 일간의 암록 지지가 사주에 있는지
    amrok_jj_val = AMROK_JJ.get(ilgan)
    if amrok_jj_val and amrok_jj_val in all_jjs:
        stars.append({
            "name": "암록(暗祿)",
            "desc": AMROK_DESC,
        })

    # 괴강살(魁罡殺) – 일주(일간+일지) 기준
    ilju_str = (pils[1]["cg"] + pils[1]["jj"]) if len(pils) > 1 and pils[1] else ""
    if ilju_str in GOEGANG_ILJU:
        stars.append({
            "name": f"괴강살(魁罡殺) [{ilju_str}]",
            "desc": GOEGANG_DESC,
        })

    # ── 추가 신살 (Y-21) ────────────────────────────────────────
    ilji = pils[1]["jj"] if len(pils) > 1 else ""
    weol_jj = pils[2]["jj"] if len(pils) > 2 else ""
    nyeon_jj = pils[3]["jj"] if len(pils) > 3 else ""
    all_cgs = [p.get("cg", "") for p in pils]

    # 홍염살(紅艶煞) — 일간 기준 지지가 원국에 있을 때 (매력·연애운)
    _HONGYUM = {"甲":"午","乙":"申","丙":"寅","丁":"未","戊":"辰","己":"辰",
                "庚":"戌","辛":"酉","壬":"子","癸":"申"}
    if _HONGYUM.get(ilgan) in all_jjs:
        stars.append({"name":"홍염살(紅艶煞)",
                      "desc":"타고난 이성 흡인력 — 매력·인기·연예·예술 운 강함. 이성 관계 구설 주의"})

    # 도화살(桃花煞) — 년지 기준 (매력·인기)
    _DOWHWA = {"子":"酉","丑":"午","寅":"卯","卯":"子","辰":"酉","巳":"午",
               "午":"卯","未":"子","申":"酉","酉":"午","戌":"卯","亥":"子"}
    if nyeon_jj and _DOWHWA.get(nyeon_jj) in all_jjs:
        stars.append({"name":"도화살(桃花煞)",
                      "desc":"매력·인기 기운 강함 — 예능·서비스·이성 운에서 빛남. 합 운에 이성 구설 주의"})

    # 양인살(羊刃煞) — 일간 기준 양인 지지 (추진력)
    _YANGIN = {"甲":"卯","乙":"辰","丙":"午","丁":"未","戊":"午","己":"未",
               "庚":"酉","辛":"戌","壬":"子","癸":"丑"}
    if _YANGIN.get(ilgan) in all_jjs:
        stars.append({"name":"양인살(羊刃煞)",
                      "desc":"강렬한 추진력·결단력 — 군·경·외과·스포츠에서 능력 발휘. 충 운에 사고수 주의"})

    # 곡각살(曲脚煞) — 특정 일주 (골절·관절 주의)
    _GOKGAK = {"辛丑","辛未","癸丑","癸未","己丑","己未"}
    if ilju_str in _GOKGAK:
        stars.append({"name":"곡각살(曲脚煞)",
                      "desc":"골절·관절 부상 주의 — 이동·등산·스포츠 시 안전 최우선. 보험 필수"})

    # 음양차착살(陰陽差錯煞) — 특정 일주 (결혼 지연)
    _CHACHAEK = {"丙子","丁丑","戊寅","辛卯","壬辰","癸巳",
                 "丙午","丁未","戊申","辛酉","壬戌","癸亥"}
    if ilju_str in _CHACHAEK:
        stars.append({"name":"음양차착살(陰陽差錯)",
                      "desc":"결혼·인연 시기가 늦어지는 구조 — 서두르면 실패, 충분히 알아가고 결정"})

    # 효신살(梟神煞) — 일간의 편인 오행 지지가 일지에 있을 때
    _HYOSHIN = {"甲":["子","亥"],"乙":["子","亥"],"丙":["寅","卯"],"丁":["寅","卯"],
                "戊":["巳","午"],"己":["巳","午"],"庚":["辰","戌","丑","未"],
                "辛":["辰","戌","丑","未"],"壬":["申","酉"],"癸":["申","酉"]}
    if ilji and ilji in _HYOSHIN.get(ilgan, []):
        stars.append({"name":"효신살(梟神煞)",
                      "desc":"어머니·인성(印星)과 갈등 구조 — 독립심 강하고 자수성가형. 의존 관계 복잡"})

    # 복성귀인(福星貴人) — 일간 기준 지지가 원국에 있을 때
    _BOKSUNG = {"甲":"寅","乙":"丑","丙":"子","丁":"亥","戊":"戌","己":"酉",
                "庚":"申","辛":"未","壬":"午","癸":"巳"}
    if _BOKSUNG.get(ilgan) in all_jjs:
        stars.append({"name":"복성귀인(福星貴人)",
                      "desc":"복덕이 두텁고 어려움 속에서도 끝내 복이 따름 — 말년 운이 좋은 구조"})

    # 천덕귀인(天德貴人) — 월지 기준 특정 천간·지지가 원국에 있을 때
    _CHEON_DEOK = {"寅":"丁","卯":"申","辰":"壬","巳":"辛","午":"亥","未":"甲",
                   "申":"癸","酉":"寅","戌":"丙","亥":"乙","子":"巳","丑":"庚"}
    _cd_target = _CHEON_DEOK.get(weol_jj, "")
    if _cd_target and (_cd_target in all_cgs or _cd_target in all_jjs):
        stars.append({"name":"천덕귀인(天德貴人)",
                      "desc":"하늘의 덕이 함께하는 기운 — 위기 때 보이지 않는 도움, 귀인이 반드시 나타남"})

    # 금여성(金輿星) — 일간 기준 지지가 원국에 있을 때 (결혼 인연)
    _GEUMYEO = {"甲":"辰","乙":"巳","丙":"未","丁":"申","戊":"未","己":"申",
                "庚":"戌","辛":"亥","壬":"丑","癸":"寅"}
    if _GEUMYEO.get(ilgan) in all_jjs:
        stars.append({"name":"금여성(金輿星)",
                      "desc":"귀한 결혼 인연 구조 — 배우자가 인생을 바꿔주는 귀인형 인연"})

    # 위치 정보 없는 신살에 기본값 추가 (Y-32)
    _plbl = ["시주", "일주", "월주", "년주"]
    _jj_pos_map = {}
    for _pi, _pp in enumerate(pils[:4]):
        _jpv = _pp.get("jj", "")
        if _jpv:
            _jj_pos_map.setdefault(_jpv, []).append(_plbl[_pi])
    for _star in stars:
        if "위치" not in _star:
            _star["위치"] = "원국"

    return stars


@st.cache_data(hash_funcs=_PILS_HF)
def get_pahae(pils):
    """파살(破殺)·해살(害殺) 감지.
    반환: {"파살": [...pairs...], "해살": [...pairs...], "items": [...{name, pair, desc}...]}
    """
    all_jjs = [p["jj"] for p in pils if p]
    jj_set = set(all_jjs)
    result = {"파살": [], "해살": [], "items": []}

    for pair in PA_SAL_PAIRS:
        if pair.issubset(jj_set):
            desc = PA_SAL_DESC.get(pair, "")
            result["파살"].append(pair)
            result["items"].append({"type": "파살", "pair": sorted(pair), "desc": desc})

    for pair in HAE_SAL_PAIRS:
        if pair.issubset(jj_set):
            desc = HAE_SAL_DESC.get(pair, "")
            result["해살"].append(pair)
            result["items"].append({"type": "해살", "pair": sorted(pair), "desc": desc})

    # ── 상문살(喪門殺) / 조객살(弔客殺) ─────────────────────────
    _SANGMUN_MAP = {
        "子": "寅", "丑": "卯", "寅": "辰", "卯": "巳",
        "辰": "午", "巳": "未", "午": "申", "未": "酉",
        "申": "戌", "酉": "亥", "戌": "子", "亥": "丑",
    }
    _JOKAEK_MAP = {
        "子": "戌", "丑": "亥", "寅": "子", "卯": "丑",
        "辰": "寅", "巳": "卯", "午": "辰", "未": "巳",
        "申": "午", "酉": "未", "戌": "申", "亥": "酉",
    }
    _nyon_jj = pils[3]["jj"] if len(pils) > 3 else ""
    _pil_jjs = [p["jj"] for p in pils]
    _labels  = ["시주", "일주", "월주", "년주"]

    # 상문살
    _sangmun_jj = _SANGMUN_MAP.get(_nyon_jj, "")
    for _i, (_jj, _lbl) in enumerate(zip(_pil_jjs, _labels)):
        if _sangmun_jj and _jj == _sangmun_jj:
            result["items"].append({
                "이름": "상문살(喪門殺)",
                "name": "상문살",
                "icon": "⚰️",
                "위치": _lbl,
                "pos": _lbl,
                "desc": (
                    "상문살(喪門殺)이 있습니다. "
                    "초상·죽음·이별의 기운이 드나드는 문이 열려 있는 신살입니다. "
                    "주변 가까운 사람의 부고 소식을 접하거나, "
                    "본인의 건강이 급격히 악화되는 시기가 옵니다. "
                    "대운·세운에서 상문살이 겹칠 때는 특히 주의가 필요합니다."
                ),
                "remedy": (
                    "처방: 병원 정기 검진을 미루지 마십시오. "
                    "조상 제사와 기제사를 정성껏 지내면 흉기가 완화됩니다. "
                    "장례식장·납골당 방문을 최소화하고, 문상 후 반드시 소금으로 정화하십시오."
                ),
            })
            break  # 중복 방지

    # 조객살
    _jokaek_jj = _JOKAEK_MAP.get(_nyon_jj, "")
    for _i, (_jj, _lbl) in enumerate(zip(_pil_jjs, _labels)):
        if _jokaek_jj and _jj == _jokaek_jj:
            result["items"].append({
                "이름": "조객살(弔客殺)",
                "name": "조객살",
                "icon": "🪦",
                "위치": _lbl,
                "pos": _lbl,
                "desc": (
                    "조객살(弔客殺)이 있습니다. "
                    "상문살과 짝을 이루는 신살로, 문상을 자주 가거나 "
                    "죽음·이별과 관련된 일이 주변에 많이 생기는 기운입니다. "
                    "감정적으로 우울하고 무기력해지는 시기가 반복됩니다."
                ),
                "remedy": (
                    "처방: 주변 사람들의 건강에 관심을 기울이십시오. "
                    "본인도 정기 검진을 철저히 받으십시오. "
                    "밝은 색상의 옷을 착용하고 긍정적인 기운의 환경을 만드십시오."
                ),
            })
            break  # 중복 방지

    return result


@st.cache_data(hash_funcs=_PILS_HF)
def get_geunmyo_hwasil(pils):
    """근묘화실(根苗花實) – 4기둥 각각의 궁 의미와 십성 분석.
    반환: list of {궁, pillar, 간지, 십성, desc}
    """
    ilgan = pils[1].get("cg", "") if len(pils) > 1 and pils[1] else ""
    pillar_order = [
        ("근(根)", 0), ("묘(苗)", 2), ("화(花)", 1), ("실(實)", 3)
    ]
    result = []
    for gung, idx in pillar_order:
        p = pils[idx] if idx < len(pils) and pils[idx] else {}
        cg = p.get("cg", "-")
        jj = p.get("jj", "-")
        ss = TEN_GODS_MATRIX.get(ilgan, {}).get(cg, "-") if ilgan else "-"
        meta = GEUNMYO_HWASIL.get(gung, {})
        result.append({
            "궁": gung,
            "pillar": meta.get("pillar", ""),
            "간지": f"{cg}{jj}",
            "천간십성": ss,
            "desc": meta.get("desc", ""),
        })
    return result