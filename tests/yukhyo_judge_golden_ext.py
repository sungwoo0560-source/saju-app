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

행마다 label_before(복음괘·반음괘만 뺀 나머지 전부 — 복신·공망·삼합·화효·
일파·월파·동효충·원신·기신)와 label_after(+is_bokum_gua·is_banum_gua)를
동시에 기록해 이 파일 하나로 전이행렬을 바로 집계할 수 있게 한다.

★F-골든 편입 라운드: label_before도 이제 tests/yukhyo_judge_common.py
(공용 모듈)를 통해 일파·월파·동효충·원신·기신까지 전부 반영한다 — 예전엔
이 4요소뿐이었다. before/after 둘 다 같은 입력을 공유하고 오직
is_bokum_gua·is_banum_gua만 다르게 넘기므로, 이 diff는 여전히 "복음괘·
반음괘 효과만" 정확히 격리해서 보여준다(다른 요소가 같이 섞여 들어오지
않음).
"""
import csv
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yukhyo_data as yd  # noqa: E402
import yukhyo_judge_common as jc  # noqa: E402

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


def _row_for(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji):
    inputs = jc.compute_judge_inputs(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji)
    if inputs is None:
        return None

    is_bokum_gua = inputs["is_bokum_gua"]
    is_banum_gua = inputs["is_banum_gua"]

    label_before, _ = jc.judge_from_inputs(inputs, is_bokum_gua=False, is_banum_gua=False)
    label_after, _ = jc.judge_from_inputs(inputs, is_bokum_gua=is_bokum_gua, is_banum_gua=is_banum_gua)

    return {
        "gua": gua_name,
        "dong_combo": "-".join(str(i + 1) for i in dong_idx_set),
        "qtype": qtype,
        "target_yukchin": inputs["target_yukchin"] or "",
        "yongshin_idx": "" if inputs["is_bokshin"] else inputs["yongshin_idx"],
        "is_bokshin": int(inputs["is_bokshin"]),
        "yongshin_jiji": inputs["yongshin_jiji"],
        "yongshin_ohang": inputs["yongshin_ohang"],
        "se_pos": inputs["se_pos"],
        "se_ohang": inputs["se_ohang"],
        "wolgeon_jj": wolgeon_jj,
        "iljin_ganji": iljin_ganji,
        "is_dong_y": int(inputs["is_dong_y"]),
        "is_gongmang_flag": int(inputs["is_gongmang_flag"]),
        "samhap_match": int(inputs["samhap_match"]),
        "hwahyo_label": inputs["hwahyo_label"] or "",
        "is_ilpa_flag": int(inputs["is_ilpa_flag"]),
        "is_wolpa_flag": int(inputs["is_wolpa_flag"]),
        "is_donghyo_chung_flag": int(inputs["is_donghyo_chung_flag"]),
        "wonsin_yukchin": inputs["wonsin_yukchin"],
        "is_wonsin_dong": int(inputs["is_wonsin_dong"]),
        "is_wonsin_broken": int(inputs["is_wonsin_broken"]),
        "wonsin_hwahyo_label": inputs["wonsin_hwahyo_label"] or "",
        "gisin_yukchin": inputs["gisin_yukchin"],
        "is_gisin_dong": int(inputs["is_gisin_dong"]),
        "is_gisin_broken": int(inputs["is_gisin_broken"]),
        "is_gisin_wang": int(inputs["is_gisin_wang"]),
        "gisin_hwahyo_label": inputs["gisin_hwahyo_label"] or "",
        "gushin_yukchin": inputs["gushin_yukchin"],
        "is_gushin_dong": int(inputs["is_gushin_dong"]),
        "eung_ohang": inputs["eung_ohang"],
        "is_eung_dong": int(inputs["is_eung_dong"]),
        "is_eung_gongmang": int(inputs["is_eung_gongmang"]),
        "eung_rel": inputs["eung_rel"],
        "is_yukchunggwe": int(inputs["is_yukchunggwe"]),
        "is_yukhapgwe": int(inputs["is_yukhapgwe"]),
        "yongshin_jinshen_label": inputs["yongshin_jinshen_label"] or "",
        "wonsin_jinshen_label": inputs["wonsin_jinshen_label"] or "",
        "gisin_jinshen_label": inputs["gisin_jinshen_label"] or "",
        "bisin_relation": inputs["bisin_relation"] or "",
        "is_bokum_gua": int(is_bokum_gua),
        "is_banum_gua": int(is_banum_gua),
        "base_score": inputs["base_score"],
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
        "hwahyo_label",
        "is_ilpa_flag", "is_wolpa_flag", "is_donghyo_chung_flag",
        "wonsin_yukchin", "is_wonsin_dong", "is_wonsin_broken", "wonsin_hwahyo_label",
        "gisin_yukchin", "is_gisin_dong", "is_gisin_broken", "is_gisin_wang", "gisin_hwahyo_label",
        "gushin_yukchin", "is_gushin_dong",
        "eung_ohang", "is_eung_dong", "is_eung_gongmang", "eung_rel",
        "is_yukchunggwe", "is_yukhapgwe",
        "yongshin_jinshen_label", "wonsin_jinshen_label", "gisin_jinshen_label",
        "bisin_relation",
        "is_bokum_gua", "is_banum_gua", "base_score",
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
