# -*- coding: utf-8 -*-
"""육효 골든 생성기 공용 모듈 — judge_yukhyo_advanced의 실제 입력 전부를
menu_yukhyo(manse.py)와 동일한 규칙으로 재구성한다.

★배경(F-골든 편입 라운드): 기존 두 골든 생성기(yukhyo_judge_golden.py·
yukhyo_judge_golden_ext.py)는 judge_yukhyo_advanced를 실제 함수 그대로
호출하지만(재구현 아님), 넘기는 파라미터가 복신·공망·삼합·화효(+확장 쪽은
복음괘·반음괘)뿐이었다 — 일파·월파·동효충·원신·기신은 아예 계산하지
않은 채 기본값(전부 "영향 없음")으로 방치돼 있었다. 그래서 원신 관련
판정(F라운드1·2)이 골든으로 전혀 회귀보호되지 않는 공백이 있었다(매번
별도 진단 스크립트로 확인해야 했음). 이 모듈은 menu_yukhyo가 실제로
계산하는 입력 전부(일파·월파·동효충·원신 동정/충/화효·기신 동정/충/왕쇠·
복음괘·반음괘)를 재구성해, 두 생성기가 판정의 "완전한" 스냅샷이 되게 한다.

★근본 해결책 검토 결과(이 라운드 진단): menu_yukhyo는 이 계산들을 별도
함수로 분리해두지 않고 거대한 Streamlit 함수 안에 인라인으로 박아뒀다 —
"골든 생성기가 menu_yukhyo의 계산 코드를 직접 재사용"하려면 manse.py를
리팩터링해 이 계산을 함수로 뽑아내야 한다(그러면 골든이 앞으로 어떤
판정요소가 추가되든 자동 반영되는 진짜 근본 해결이 된다). 그런데 그건
manse.py 변경 = 배포 앱 변경 = Reboot 필요라 이번 라운드 범위(tests/만
건드려 Reboot 불필요하게 유지) 밖이다 — 다음 판정요소 추가 때 이 모듈을
다시 손으로 확장해야 하는 건 여전하지만, 최소한 지금 시점 기준으로는
완전판이다. manse.py 리팩터링은 별도 과제로 추천만 해둔다(보고 참고).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yukhyo_data as yd  # noqa: E402


def gua_of_hexa(hexa6):
    _ha = tuple(hexa6[0:3])
    _sa = tuple(hexa6[3:6])
    _ha_name = next((k for k, v in yd.BAGUA.items() if v["효"] == _ha), None)
    _sa_name = next((k for k, v in yd.BAGUA.items() if v["효"] == _sa), None)
    return _ha_name, _sa_name


def gua_parts(gua_name):
    for (sa, ha), name in yd.GUA_64.items():
        if name == gua_name:
            return sa, ha
    raise ValueError(f"GUA_64에 없는 괘명: {gua_name}")


def compute_judge_inputs(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji):
    """menu_yukhyo와 동일한 규칙으로 judge_yukhyo_advanced의 입력 전부와
    부가 메타(가·위치 등)를 계산해 dict로 반환한다. 이론상 있어야 할
    복신 대상이 본궁 순괘에도 없는(방어적 예외) 경우만 None."""
    sa_name, ha_name = gua_parts(gua_name)
    nap_ha = yd.NAPGAP[ha_name]
    nap_sa = yd.NAPGAP[sa_name]
    jiji6 = list(nap_ha["내괘_지지"]) + list(nap_sa["외괘_지지"])
    hexa6 = tuple(yd.BAGUA[ha_name]["효"]) + tuple(yd.BAGUA[sa_name]["효"])
    dong6 = [i in dong_idx_set for i in range(6)]

    gung_oh = yd.get_gung_ohang(gua_name)
    yukchin6 = [yd.get_yukchin(gung_oh, yd.JIJI_OHANG[j]) for j in jiji6]
    se_pos, eung_pos = yd.SEEUNG[gua_name]
    se_ohang = yd.JIJI_OHANG[jiji6[se_pos - 1]]

    # 응효(F라운드5) — 괘 하나로 완전히 고정되는 값(월건·일진·동효·질문
    # 유형 무관, F5 진단 실증). eung_rel은 질문유형이 '경쟁/동업'일 때만
    # judge에 적용되는 게 실제 판정이라(호출부 조건), 여기서는 값만
    # 계산해 두고 관계형 여부 필터링은 judge_from_inputs 호출부에서 한다.
    eung_jiji = jiji6[eung_pos - 1]
    eung_ohang = yd.JIJI_OHANG[eung_jiji]
    is_eung_dong = dong6[eung_pos - 1]
    is_eung_gongmang = yd.is_yukhyo_gongmang(eung_jiji, iljin_ganji)
    eung_rel = yd.get_yukhyo_eung_rel(eung_ohang, se_ohang)

    # 변괘(화지지) — 화효(화공화묘·회두생극)뿐 아니라 원신 화효·복음괘·
    # 반음괘 전부 이 한 번의 계산을 공유한다(menu_yukhyo의 _byeon_jiji6와 동일 역할).
    byeon_hexa = tuple((1 - hexa6[i]) if dong6[i] else hexa6[i] for i in range(6))
    byeon_ha_name, byeon_sa_name = gua_of_hexa(byeon_hexa)
    byeon_jiji6 = None
    if byeon_ha_name and byeon_sa_name:
        byeon_jiji6 = list(yd.NAPGAP[byeon_ha_name]["내괘_지지"]) + list(yd.NAPGAP[byeon_sa_name]["외괘_지지"])

    # 動한 모든 효의 화효 라벨 — menu_yukhyo의 _hwahyo_by_idx와 동일(용신·원신
    # 어느 위치든 이 dict 하나에서 조회, judge_hwahyo 중복 호출 없음).
    hwahyo_by_idx = {}
    if byeon_jiji6:
        for _i in range(6):
            if dong6[_i]:
                _bon_oh = yd.JIJI_OHANG[jiji6[_i]]
                _hwa_oh = yd.JIJI_OHANG[byeon_jiji6[_i]]
                _label, _ = yd.judge_hwahyo(_bon_oh, _hwa_oh, byeon_jiji6[_i], iljin_ganji)
                hwahyo_by_idx[_i] = _label

    target_yukchin = yd.QUESTION_YONGSHIN[qtype]
    if target_yukchin is None:
        yongshin_idx = se_pos - 1
    else:
        yongshin_idx = yd.pick_yongshin_idx(yukchin6, target_yukchin, dong6, se_pos)

    is_bokshin = yongshin_idx is None
    if is_bokshin:
        bokshin_info = yd.get_bokshin(gua_name, target_yukchin, se_pos)
        if bokshin_info is None:
            return None
        yongshin_ohang = bokshin_info["복신_오행"]
        yongshin_jiji = bokshin_info["복신_지지"]
        is_dong_y = False
        hwahyo_label = None
        yongshin_jinshen_label = None
    else:
        yongshin_ohang = yd.JIJI_OHANG[jiji6[yongshin_idx]]
        yongshin_jiji = jiji6[yongshin_idx]
        is_dong_y = dong6[yongshin_idx]
        hwahyo_label = hwahyo_by_idx.get(yongshin_idx) if is_dong_y else None
        # 진신·퇴신(F라운드7) — hwahyo_label과 같은 화지지 소스(byeon_jiji6).
        yongshin_jinshen_label = (
            yd.get_yukhyo_jinshen_label(yongshin_jiji, byeon_jiji6[yongshin_idx])
            if is_dong_y and byeon_jiji6 else None
        )

    is_gongmang_flag = yd.is_yukhyo_gongmang(yongshin_jiji, iljin_ganji)
    samhap_ohangs = yd.check_samhap_guk(jiji6)
    samhap_match = yongshin_ohang in samhap_ohangs

    # 육충 3종 — manse.py L28943-28951과 동일
    is_ilpa_flag = yd.is_yukhyo_chung(yongshin_jiji, iljin_ganji[1])
    is_wolpa_flag = yd.is_yukhyo_chung(yongshin_jiji, wolgeon_jj)
    if is_bokshin:
        is_donghyo_chung_flag = False
    else:
        is_donghyo_chung_flag = any(
            dong6[i] and i != yongshin_idx and yd.is_yukhyo_chung(jiji6[i], yongshin_jiji)
            for i in range(6)
        )

    # 원신·기신 — manse.py L28962-28992와 동일(동일 함수·동일 우선순위 재사용)
    yongshin_yukchin_label = target_yukchin if target_yukchin is not None else yukchin6[se_pos - 1]
    wongisin = yd.get_yukhyo_wongisin(yongshin_yukchin_label)

    wonsin_idx = yd.pick_yongshin_idx(yukchin6, wongisin["원신"], dong6, se_pos)
    if wonsin_idx is None:
        is_wonsin_dong = False
        is_wonsin_broken = False
        wonsin_hwahyo_label = None
        wonsin_jinshen_label = None
    else:
        wonsin_jiji = jiji6[wonsin_idx]
        is_wonsin_dong = dong6[wonsin_idx]
        # F라운드2: 動不爲空 — 공망은 안 보고 충(일파·월파)만 broken 조건.
        is_wonsin_broken = (
            yd.is_yukhyo_chung(wonsin_jiji, iljin_ganji[1])
            or yd.is_yukhyo_chung(wonsin_jiji, wolgeon_jj)
        )
        wonsin_hwahyo_label = hwahyo_by_idx.get(wonsin_idx) if is_wonsin_dong else None
        wonsin_jinshen_label = (
            yd.get_yukhyo_jinshen_label(wonsin_jiji, byeon_jiji6[wonsin_idx])
            if is_wonsin_dong and byeon_jiji6 else None
        )

    gisin_idx = yd.pick_yongshin_idx(yukchin6, wongisin["기신"], dong6, se_pos)
    if gisin_idx is None:
        is_gisin_dong = False
        is_gisin_broken = False
        is_gisin_wang = False
        gisin_hwahyo_label = None
        gisin_jinshen_label = None
    else:
        gisin_jiji = jiji6[gisin_idx]
        gisin_ohang = yd.JIJI_OHANG[gisin_jiji]
        is_gisin_dong = dong6[gisin_idx]
        # F라운드3: 動不爲空 — 원신(F2)과 동일 수정, 공망 항목 제거, 충만.
        is_gisin_broken = (
            yd.is_yukhyo_chung(gisin_jiji, iljin_ganji[1])
            or yd.is_yukhyo_chung(gisin_jiji, wolgeon_jj)
        )
        is_gisin_wang = yd.get_wangsae_label(yd.get_wangsae_score(gisin_ohang, wolgeon_jj, iljin_ganji[1])) == "왕(旺)"
        gisin_hwahyo_label = hwahyo_by_idx.get(gisin_idx) if is_gisin_dong else None
        gisin_jinshen_label = (
            yd.get_yukhyo_jinshen_label(gisin_jiji, byeon_jiji6[gisin_idx])
            if is_gisin_dong and byeon_jiji6 else None
        )

    gushin_idx = yd.pick_yongshin_idx(yukchin6, wongisin["구신"], dong6, se_pos)
    if gushin_idx is None:
        is_gushin_dong = False
    else:
        gushin_jiji = jiji6[gushin_idx]
        gushin_dong_raw = dong6[gushin_idx]
        # F라운드4: 動不爲空을 처음부터 반영(원신·기신처럼 뒤늦게 고치지
        # 않음) — 공망 없이 충(일파·월파)만.
        gushin_broken = (
            yd.is_yukhyo_chung(gushin_jiji, iljin_ganji[1])
            or yd.is_yukhyo_chung(gushin_jiji, wolgeon_jj)
        )
        is_gushin_dong = gushin_dong_raw and not gushin_broken

    is_bokum_gua = yd.is_bokum_gua(jiji6, byeon_jiji6, dong6) if byeon_jiji6 else False
    is_banum_gua = yd.is_banum_gua(jiji6, byeon_jiji6, dong6) if byeon_jiji6 else False

    # 육충괘·육합괘(F라운드6) — 본괘(jiji6) 그대로의 대응쌍 3쌍, 動 여부
    # 무관. 질문유형 게이팅 없이 전 유형 균일 적용이라 eung_rel과 달리
    # _JUDGE_KEYS에 바로 넣는다.
    is_yukchunggwe = yd.is_yukchunggwe(jiji6)
    is_yukhapgwe = yd.is_yukhapgwe(jiji6)

    base_score = yd._yukhyo_base_score(yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y)

    return {
        "gua": gua_name, "qtype": qtype, "target_yukchin": target_yukchin,
        "yongshin_idx": yongshin_idx, "is_bokshin": is_bokshin,
        "yongshin_jiji": yongshin_jiji, "yongshin_ohang": yongshin_ohang,
        "se_pos": se_pos, "se_ohang": se_ohang, "eung_pos": eung_pos,
        "wolgeon_jj": wolgeon_jj, "iljin_ganji": iljin_ganji,
        "is_dong_y": is_dong_y, "hwahyo_label": hwahyo_label,
        "yongshin_jinshen_label": yongshin_jinshen_label,
        "is_gongmang_flag": is_gongmang_flag, "samhap_match": samhap_match,
        "is_ilpa_flag": is_ilpa_flag, "is_wolpa_flag": is_wolpa_flag,
        "is_donghyo_chung_flag": is_donghyo_chung_flag,
        "wonsin_yukchin": wongisin["원신"], "is_wonsin_dong": is_wonsin_dong,
        "is_wonsin_broken": is_wonsin_broken, "wonsin_hwahyo_label": wonsin_hwahyo_label,
        "wonsin_jinshen_label": wonsin_jinshen_label,
        "gisin_yukchin": wongisin["기신"], "is_gisin_dong": is_gisin_dong,
        "is_gisin_broken": is_gisin_broken, "is_gisin_wang": is_gisin_wang,
        "gisin_hwahyo_label": gisin_hwahyo_label,
        "gisin_jinshen_label": gisin_jinshen_label,
        "gushin_yukchin": wongisin["구신"], "is_gushin_dong": is_gushin_dong,
        "eung_ohang": eung_ohang, "is_eung_dong": is_eung_dong,
        "is_eung_gongmang": is_eung_gongmang, "eung_rel": eung_rel,
        "is_bokum_gua": is_bokum_gua, "is_banum_gua": is_banum_gua,
        "is_yukchunggwe": is_yukchunggwe, "is_yukhapgwe": is_yukhapgwe,
        "base_score": base_score,
    }


# ★eung_rel(응효 생극)은 여기 안 넣는다 — 실제 앱(manse.py)은 질문유형이
# '경쟁/동업'일 때만 judge에 이 값을 넘기므로(F5 확정), judge_from_inputs가
# inputs["qtype"]을 보고 그 자리에서 게이팅한다(아래 참고). is_yukchunggwe·
# is_yukhapgwe(F6)는 질문유형 게이팅이 없어(전 유형 균일) 그냥 넣는다.
_JUDGE_KEYS = (
    "is_bokshin", "is_gongmang_flag", "samhap_match", "hwahyo_label",
    "is_ilpa_flag", "is_wolpa_flag", "is_donghyo_chung_flag",
    "is_wonsin_dong", "is_wonsin_broken", "wonsin_hwahyo_label",
    "is_gisin_dong", "is_gisin_broken", "is_gisin_wang", "gisin_hwahyo_label",
    "is_gushin_dong",
    "is_bokum_gua", "is_banum_gua",
    "is_yukchunggwe", "is_yukhapgwe",
    "yongshin_jinshen_label", "wonsin_jinshen_label", "gisin_jinshen_label",
)

RELATIONAL_QTYPES = ("경쟁/동업",)


def judge_from_inputs(inputs, **overrides):
    """compute_judge_inputs()가 반환한 dict를 judge_yukhyo_advanced 실제
    호출로 그대로 넘긴다 — 키 이름이 파라미터 이름과 1:1 대응이라 매핑
    실수가 날 자리가 없다. overrides로 특정 항목만 바꿔치기해 before/after
    비교(예: 확장 골든의 is_bokum_gua/is_banum_gua on/off)를 만들 수 있다.
    eung_rel은 manse.py와 동일하게 질문유형이 관계형(RELATIONAL_QTYPES)
    일 때만 실제로 넘기고, 그 외엔 None(미적용) — inputs["eung_rel"]은
    항상 원값(분류자)을 담고 있고 여기서 게이팅한다."""
    _kwargs = {k: inputs[k] for k in _JUDGE_KEYS}
    _kwargs["eung_rel"] = inputs["eung_rel"] if inputs["qtype"] in RELATIONAL_QTYPES else None
    _kwargs.update(overrides)
    return yd.judge_yukhyo_advanced(
        inputs["yongshin_ohang"], inputs["se_ohang"], inputs["wolgeon_jj"], inputs["iljin_ganji"][1],
        is_dong=inputs["is_dong_y"],
        **_kwargs,
    )
