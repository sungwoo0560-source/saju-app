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

@st.cache_data
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



@st.cache_data
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

    for jj in jjs:
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

GONGMANG_TABLE = {
    "甲": ("戌", "亥"),
    "乙": ("戌", "亥"),
    "丙": ("申", "酉"),
    "丁": ("申", "酉"),
    "戊": ("午", "未"),
    "己": ("午", "未"),
    "庚": ("辰", "巳"),
    "辛": ("辰", "巳"),
    "壬": ("寅", "卯"),
    "癸": ("寅", "卯"),
}

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


@st.cache_data
def get_gongmang(pils):
    """공망(空亡) 계산"""

    nyon_cg = pils[3]["cg"] if len(pils) > 3 else ""

    gong_pair = GONGMANG_TABLE.get(nyon_cg, ("", ""))

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



@st.cache_data
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


@st.cache_data
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

_HYUNG_JJ = {"丑", "刑", "巳", "申", "寅"}  # 삼형살 지지

_GIL_JJ = {"子", "卯", "午", "酉", "亥", "寅"}  # 귀인 지지 포함


@st.cache_data
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
    "乙": "辰",
    "丁": "未",
    "己": "未",
    "辛": "戌",
    "癸": "丑",
}



@st.cache_data
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


@st.cache_data
def get_oigyeok(pils):

    ilgan = pils[1]["cg"]

    ilgan_oh = OH.get(ilgan, "")

    # ✅ BUG FIX: 외부 함수(calc_ohaeng_strength/get_ilgan_strength) 호출 예외처리
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





@st.cache_data
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

    return result


@st.cache_data
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

    baekho = [
        "甲(갑)辰(진)",
        "乙(을)未(미)",
        "丙(병)戌(술)",
        "丁(정)丑(축)",
        "戊(무)辰(진)",
        "壬(임)戌(술)",
        "癸(계)丑(축)",
    ]

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
                "name": "천을귀인(天乙(을))",
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
    ilju_str = (pils[1]["cg"] + pils[1]["jj"]) if pils[1] else ""
    if ilju_str in GOEGANG_ILJU:
        stars.append({
            "name": f"괴강살(魁罡殺) [{ilju_str}]",
            "desc": GOEGANG_DESC,
        })

    return stars


@st.cache_data
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

    return result


@st.cache_data
def get_geunmyo_hwasil(pils):
    """근묘화실(根苗花實) – 4기둥 각각의 궁 의미와 십성 분석.
    반환: list of {궁, pillar, 간지, 십성, desc}
    """
    ilgan = pils[1]["cg"] if pils[1] else ""
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