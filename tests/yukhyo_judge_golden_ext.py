# -*- coding: utf-8 -*-
"""육효 판정(judge_yukhyo_advanced) 골든 확장 — 복음괘(伏吟卦)·반음괘(反吟卦) 전용.

★목적: 기존 tests/yukhyo_judge_golden.py의 442,368행(정지괘·단일효동6·
전효개동)은 복음괘·반음괘가 절대 발생하지 않는 동효패턴만 스윕한다(D라운드2·
A라운드1 진단으로 확인). 그래서 그 골든은 그대로 두고(회귀 안전선), 복음괘·
반음괘가 실제로 발생하는 동효조합만 골라 별도 파일로 얹는다.

★발생조합 15가지(A라운드1 진단): 63개 동효조합(1~6효동 전수) 중 "한
트라이그램의 초효(내괘) 또는 4효(외괘)는 靜하고 나머지 2효만 짝으로 함께
動"하는 조합만 乾↔震(복음)·巽↔坤(반음) 궁쌍에서 반응한다. 이 15가지 전부를
64괘 전수에 적용한다(발생 안 하는 괘도 함께 스윕 — 그 자체가 내부 회귀
검증: 해당 없는 괘는 label_before == label_after가 나와야 정상).

★월건4·일진4 선정 근거: 기존 12셋(월건 12지지 전수·대표일진 12개) x
496개(발생 (괘,조합) 쌍) x 6질문유형 전수를 스캔해 "복음괘/반음괘 감점 적용
전후로 라벨이 바뀌는(경계 돌파)" 행 수를 월건별·일진별로 집계한 뒤 상위
4개씩 뽑았다(스캔 스크립트는 진단용, 커밋 대상 아님). 결과: 월건={子,亥,申,酉},
일진={戊子,戊申,己酉,己亥} — 이 4x4 그리드로 재검증한 결과 47,616행 중
27,572건(57.90%)이 경계를 돌파해, 원래 전체 12x12 평균 돌파율(58.28%)과
사실상 같다(즉 이 월건·일진 조합에 유독 유리하게 쏠린 게 아니라, 이
현상 자체가 원래 라벨 경계 돌파율이 높다는 뜻 — -2/-3라는 감점 폭이
길/무난/보통/흉 4단계 경계(폭 2~3점)와 거의 맞먹기 때문).

행마다 label_before(복음괘·반음괘 미적용, 기존 4요소만: 복신·공망·삼합·화효)와
label_after(+is_bokum_gua·is_banum_gua)를 동시에 기록해 이 파일 하나로
전이행렬을 바로 집계할 수 있게 한다.
"""
import csv
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yukhyo_data as yd  # noqa: E402

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yukhyo_judge_golden_ext_bokumbanum.csv")

# ── 스윕 축 값 ────────────────────────────────────────────────────
WOLGEON_SWEEP = ["子", "亥", "申", "酉"]
ILJIN_SWEEP = ["戊子", "戊申", "己酉", "己亥"]

# 발생 15가지 동효조합(0=초효~5=상효) — A라운드1 진단(63조합 전수 스캔)에서
# 실제로 복음괘·반음괘를 만든 고유 조합 그대로(1-indexed 효 번호를 주석에 병기).
DONG_COMBOS_15 = [
    (1, 2),               # 2·3효
    (4, 5),               # 5·6효
    (0, 4, 5),            # 초·5·6효
    (1, 2, 3),             # 2·3·4효
    (1, 2, 4),             # 2·3·5효
    (1, 2, 5),             # 2·3·6효
    (1, 4, 5),             # 2·5·6효
    (2, 4, 5),             # 3·5·6효
    (0, 1, 4, 5),          # 초·2·5·6효
    (0, 2, 4, 5),          # 초·3·5·6효
    (1, 2, 3, 4),          # 2·3·4·5효
    (1, 2, 3, 5),          # 2·3·4·6효
    (1, 2, 4, 5),          # 2·3·5·6효(혼합 8건이 나오는 조합)
    (0, 1, 2, 4, 5),       # 초·2·3·5·6효
    (1, 2, 3, 4, 5),       # 2·3·4·5·6효
]
assert len(DONG_COMBOS_15) == 15


def _gua_of_hexa(hexa6):
    _ha = tuple(hexa6[0:3])
    _sa = tuple(hexa6[3:6])
    _ha_name = next((k for k, v in yd.BAGUA.items() if v["효"] == _ha), None)
    _sa_name = next((k for k, v in yd.BAGUA.items() if v["효"] == _sa), None)
    return _ha_name, _sa_name


def _prep_gua(gua_name):
    sa_name = ha_name = None
    for (sa, ha), name in yd.GUA_64.items():
        if name == gua_name:
            sa_name, ha_name = sa, ha
            break
    nap_ha = yd.NAPGAP[ha_name]
    nap_sa = yd.NAPGAP[sa_name]
    jiji6 = list(nap_ha["내괘_지지"]) + list(nap_sa["외괘_지지"])
    hexa6 = tuple(yd.BAGUA[ha_name]["효"]) + tuple(yd.BAGUA[sa_name]["효"])
    gung_oh = yd.get_gung_ohang(gua_name)
    yukchin6 = [yd.get_yukchin(gung_oh, yd.JIJI_OHANG[j]) for j in jiji6]
    se_pos, eung_pos = yd.SEEUNG[gua_name]
    return ha_name, sa_name, jiji6, hexa6, yukchin6, se_pos, eung_pos


def _row_for(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji):
    ha_name, sa_name, jiji6, hexa6, yukchin6, se_pos, eung_pos = _prep_gua(gua_name)
    dong6 = [i in dong_idx_set for i in range(6)]
    se_ohang = yd.JIJI_OHANG[jiji6[se_pos - 1]]

    byeon_hexa = tuple((1 - hexa6[i]) if dong6[i] else hexa6[i] for i in range(6))
    byeon_ha_name, byeon_sa_name = _gua_of_hexa(byeon_hexa)
    byeon_jiji6 = None
    if byeon_ha_name and byeon_sa_name:
        byeon_jiji6 = list(yd.NAPGAP[byeon_ha_name]["내괘_지지"]) + list(yd.NAPGAP[byeon_sa_name]["외괘_지지"])

    is_bokum_gua = yd.is_bokum_gua(jiji6, byeon_jiji6, dong6) if byeon_jiji6 else False
    is_banum_gua = yd.is_banum_gua(jiji6, byeon_jiji6, dong6) if byeon_jiji6 else False

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
    else:
        yongshin_ohang = yd.JIJI_OHANG[jiji6[yongshin_idx]]
        yongshin_jiji = jiji6[yongshin_idx]
        is_dong_y = dong6[yongshin_idx]
        hwahyo_label = None
        if is_dong_y and byeon_jiji6:
            hwa_jiji = byeon_jiji6[yongshin_idx]
            hwa_ohang = yd.JIJI_OHANG[hwa_jiji]
            hwahyo_label, _ = yd.judge_hwahyo(yongshin_ohang, hwa_ohang, hwa_jiji, iljin_ganji)

    is_gongmang_flag = yd.is_yukhyo_gongmang(yongshin_jiji, iljin_ganji)
    samhap_ohangs = yd.check_samhap_guk(jiji6)
    samhap_match = yongshin_ohang in samhap_ohangs

    base_score = yd._yukhyo_base_score(yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y)

    label_before, _ = yd.judge_yukhyo_advanced(
        yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y,
        is_bokshin=is_bokshin, is_gongmang_flag=is_gongmang_flag,
        samhap_match=samhap_match, hwahyo_label=hwahyo_label,
    )
    label_after, _ = yd.judge_yukhyo_advanced(
        yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y,
        is_bokshin=is_bokshin, is_gongmang_flag=is_gongmang_flag,
        samhap_match=samhap_match, hwahyo_label=hwahyo_label,
        is_bokum_gua=is_bokum_gua, is_banum_gua=is_banum_gua,
    )

    return {
        "gua": gua_name,
        "dong_combo": "-".join(str(i + 1) for i in dong_idx_set),
        "qtype": qtype,
        "target_yukchin": target_yukchin or "",
        "yongshin_idx": "" if is_bokshin else yongshin_idx,
        "is_bokshin": int(is_bokshin),
        "yongshin_jiji": yongshin_jiji,
        "yongshin_ohang": yongshin_ohang,
        "se_pos": se_pos,
        "se_ohang": se_ohang,
        "wolgeon_jj": wolgeon_jj,
        "iljin_ganji": iljin_ganji,
        "is_dong_y": int(is_dong_y),
        "is_gongmang_flag": int(is_gongmang_flag),
        "samhap_match": int(samhap_match),
        "hwahyo_label": hwahyo_label or "",
        "is_bokum_gua": int(is_bokum_gua),
        "is_banum_gua": int(is_banum_gua),
        "base_score": base_score,
        "label_before": label_before,
        "label_after": label_after,
        "changed": int(label_before != label_after),
    }


_LABEL_ORDER = ["흉(凶)", "보통", "무난", "길(吉)"]
_LABEL_RANK = {l: i for i, l in enumerate(_LABEL_ORDER)}


def generate():
    fieldnames = [
        "gua", "dong_combo", "qtype", "target_yukchin", "yongshin_idx", "is_bokshin",
        "yongshin_jiji", "yongshin_ohang", "se_pos", "se_ohang",
        "wolgeon_jj", "iljin_ganji", "is_dong_y", "is_gongmang_flag", "samhap_match",
        "hwahyo_label", "is_bokum_gua", "is_banum_gua", "base_score",
        "label_before", "label_after", "changed",
    ]
    n_rows = 0
    n_changed = 0
    n_bokum_only = n_banum_only = n_both = 0
    jump2 = 0
    upper = lower = 0
    transition = {}

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for gua_name in yd.GUA_64.values():
            for dong_idx_set in DONG_COMBOS_15:
                for qtype in yd.QUESTION_TYPES:
                    for wolgeon_jj in WOLGEON_SWEEP:
                        for iljin_ganji in ILJIN_SWEEP:
                            row = _row_for(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji)
                            if row is None:
                                continue
                            writer.writerow(row)
                            n_rows += 1
                            if row["is_bokum_gua"] and row["is_banum_gua"]:
                                n_both += 1
                            elif row["is_bokum_gua"]:
                                n_bokum_only += 1
                            elif row["is_banum_gua"]:
                                n_banum_only += 1
                            if row["changed"]:
                                n_changed += 1
                                b, a = row["label_before"], row["label_after"]
                                transition[(b, a)] = transition.get((b, a), 0) + 1
                                if abs(_LABEL_RANK[a] - _LABEL_RANK[b]) >= 2:
                                    jump2 += 1
                                if _LABEL_RANK[a] > _LABEL_RANK[b]:
                                    upper += 1
                                else:
                                    lower += 1
    return {
        "n_rows": n_rows, "n_changed": n_changed,
        "n_bokum_only": n_bokum_only, "n_banum_only": n_banum_only, "n_both": n_both,
        "jump2": jump2, "upper": upper, "lower": lower, "transition": transition,
    }


def _write_meta(stats):
    import hashlib
    _md5 = hashlib.md5()
    with open(OUT_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            _md5.update(chunk)
    _size = os.path.getsize(OUT_PATH)
    meta_path = OUT_PATH.replace(".csv", ".meta.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"file={os.path.basename(OUT_PATH)}\n")
        f.write(f"md5={_md5.hexdigest()}\n")
        f.write(f"rows={stats['n_rows']}\n")
        f.write(f"size_bytes={_size}\n")
        f.write(f"changed={stats['n_changed']}\n")
        f.write(f"bokum_only={stats['n_bokum_only']}\n")
        f.write(f"banum_only={stats['n_banum_only']}\n")
        f.write(f"both={stats['n_both']}\n")
        f.write(f"jump2={stats['jump2']}\n")
        f.write(f"upper(개선방향)={stats['upper']}\n")
        f.write(f"lower(악화방향)={stats['lower']}\n")
    return meta_path, _md5.hexdigest(), _size


if __name__ == "__main__":
    stats = generate()
    print(f"골든 확장 생성 완료: {OUT_PATH}")
    print(f"총 행 수: {stats['n_rows']}")
    print(f"변경 건수: {stats['n_changed']} ({stats['n_changed'] / stats['n_rows'] * 100:.2f}%)")
    print(f"복음괘만: {stats['n_bokum_only']} / 반음괘만: {stats['n_banum_only']} / 혼합(둘다): {stats['n_both']}")
    print(f"2단계 이상 점프: {stats['jump2']}")
    print(f"상삼각(개선방향, before<after): {stats['upper']}")
    print(f"하삼각(악화방향, before>after): {stats['lower']}")
    print("전이행렬(변경분만):")
    for (b, a), cnt in sorted(stats["transition"].items(), key=lambda kv: -kv[1]):
        print(f"  {b} -> {a} : {cnt}")
    meta_path, md5_hex, size = _write_meta(stats)
    print(f"파일 크기: {size:,} bytes")
    print(f"MD5: {md5_hex}")
    print(f"메타 파일(커밋 대상): {meta_path}")
