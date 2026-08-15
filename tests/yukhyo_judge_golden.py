# -*- coding: utf-8 -*-
"""육효 판정(judge_yukhyo_advanced) 골든 baseline 생성기.

★F-골든 편입 라운드(이 헤더 갱신): 기존엔 복신·공망·삼합·화효 4요소만
judge_yukhyo_advanced에 넘겼다 — 일파·월파·동효충·원신·기신은 계산 자체를
안 해서 기본값("영향 없음")으로 방치돼 있었다(D라운드2 baseline 도입 당시
"육충 도입 직전 스냅샷"이라는 의도적 설계였는데, 이후 육충·원신기신·복음
반음괘가 전부 판정에 편입되고 나서도 이 골든은 갱신 없이 그대로 남아있어
회귀보호 공백이 됐다 — F라운드2에서 실측 확인). 이제 tests/yukhyo_judge_common.py
(공용 모듈, menu_yukhyo와 동일 규칙으로 입력 전부 재구성)를 통해 일파·월파·
동효충·원신(동정·충·화효)·기신(동정·충·왕쇠)까지 전부 계산해 넘긴다 — 이
골든이 이제 judge_yukhyo_advanced의 "완전한" 스냅샷이다(복음괘·반음괘는
발생 동효패턴 자체가 이 8종 스윕에서 구조적으로 0건이라 그대로 미포함 —
tests/yukhyo_judge_golden_ext.py가 그 부분을 전담).

★이전 목적(육충 도입 전 스냅샷)은 이 갱신으로 폐기한다 — 아래 스윕 축
설계(8동효패턴×64괘×6질문×12월건×12일진)는 여전히 유효해 그대로 둔다.
이 스크립트는 yukhyo_data.py의 실제 judge_yukhyo_advanced를 그대로
호출할 뿐 판정 로직을 재구현하거나 바꾸지 않는다.

★난수 미사용 — 전부 결정론적 전수/대표값 순회이므로 같은 스크립트를
다시 돌리면 바이트 단위로 같은 CSV가 나온다(재현성 보장).

━━ 스윕 축 ━━
- 괘(卦): GUA_64의 64괘 전수.
- 동효 패턴: 괘마다 8가지 — "정지괘"(동효 0개) + "단일효동"(초효~상효,
  6가지) + "전효개동"(6효 모두 동). 정확히 "용신 자신이 아닌 위치가
  동한" 케이스를 포함시켜야 육충 후보(c)"동효가 용신을 충"을 나중에
  검증할 수 있어 단일효동 6가지를 전부 넣었다(부분 조합 2^6개 전부는
  아님 — 조합 폭발 방지, 아래 "스코프 한계" 참고).
- 질문유형(qtype): QUESTION_TYPES 6종 전수(용신 육친 5종 + 기타/세효자신).
- 월건(月建): 12지지 전수(get_wolgeon_jj가 원래 지지 하나만 반환하는
  근사 모델이라 12개면 전수).
- 일진(日辰): 60갑자 전체를 다 돌리면 8*64*6*12*60 ≈ 220만 행으로
  너무 커져서 대표 간지 12개로 줄이되, **6순(旬)에서 2개씩** 뽑는다
  (순 s의 60갑자 인덱스 s*10~s*10+9 중 **5번째·6번째**, 즉 s*10+4·
  s*10+5, s=0~5) — 戊辰·己巳·戊寅·己卯·戊子·己丑·戊戌·己亥·戊申·
  己酉·戊午·己未. 6순 전수(공망 6종류 戌亥/申酉/午未/辰巳/寅卯/子丑)를
  정확히 2번씩 덮으면서 12지지도 정확히 1번씩만 나온다(간지 순환
  구조상 항상 그렇게 됨 — 우연이 아님).
  ★왜 하필 5·6번째(戊·己)인가 — 순중공망이 실제로 풀리는(沖空則實)
  날은 그 순 안에서 "공망 지지를 충하는 지지"를 가진 날인데, 60갑자
  순환 구조상 이 조건은 **항상 정확히 그 순의 5번째(戊)·6번째(己)
  날에서만** 성립한다(10일 전수를 스캔해 실측 확인, 나머지 8일은
  전부 0건). 이전 두 버전(①인덱스 0~11 연속=앞 10개가 甲子旬 1개에
  편중 ②각 순의 1·2번째=甲乙일)은 둘 다 이 5·6번째 조건을 놓쳐
  충공즉실 표본이 골든에 0건이었다 — 공망뿐 아니라 충공즉실도 실제
  판정 요소이므로 이 조합을 못 덮으면 골든이 헛돈다.

총 8(동효패턴) × 64(괘) × 6(질문유형) × 12(월건) × 12(대표일진) = 442,368행
(행 수는 이전과 동일 — 대표일진의 "선정 방식"만 바뀌었다).
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yukhyo_data as yd  # noqa: E402
import yukhyo_judge_common as jc  # noqa: E402

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yukhyo_judge_golden_baseline.csv")

# ── 스윕 축 값 ────────────────────────────────────────────────────
WOLGEON_SWEEP = list(yd._JJ12)  # 12지지 전수
# 대표 간지 12개 — 6순(旬)에서 2개씩, 각 순의 5·6번째 날(戊·己일).
# 이 오프셋이어야 충공즉실(沖空則實, 공망 지지를 그날 일진이 충하는 경우)
# 표본이 골든에 실제로 들어온다 — 위 모듈 docstring "★왜 하필 5·6번째"
# 참고(10일 전수 스캔 실측, 5·6번째 외엔 전부 0건).
ILJIN_SWEEP = [
    yd._CG10[_i % 10] + yd._JJ12[_i % 12]
    for _s in range(6) for _i in (_s * 10 + 4, _s * 10 + 5)
]

DONG_PATTERNS = [("정지괘", ())]
for _i in range(6):
    DONG_PATTERNS.append((f"단일효동_{_i}", (_i,)))
DONG_PATTERNS.append(("전효개동", tuple(range(6))))


def _row_for(gua_name, dong_label, dong_idx_set, qtype, wolgeon_jj, iljin_ganji):
    inputs = jc.compute_judge_inputs(gua_name, dong_idx_set, qtype, wolgeon_jj, iljin_ganji)
    if inputs is None:
        return None
    label, _reasons = jc.judge_from_inputs(inputs)

    return {
        "gua": gua_name,
        "dong_pattern": dong_label,
        "qtype": qtype,
        "target_yukchin": inputs["target_yukchin"] or "",
        "yongshin_idx": "" if inputs["is_bokshin"] else inputs["yongshin_idx"],
        "is_bokshin": int(inputs["is_bokshin"]),
        "yongshin_jiji": inputs["yongshin_jiji"],
        "yongshin_ohang": inputs["yongshin_ohang"],
        "se_pos": inputs["se_pos"],
        "se_ohang": inputs["se_ohang"],
        "eung_pos": inputs["eung_pos"],
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
        "base_score": inputs["base_score"],
        "label": label,
    }


def generate():
    fieldnames = [
        "gua", "dong_pattern", "qtype", "target_yukchin", "yongshin_idx", "is_bokshin",
        "yongshin_jiji", "yongshin_ohang", "se_pos", "se_ohang", "eung_pos",
        "wolgeon_jj", "iljin_ganji", "is_dong_y", "is_gongmang_flag", "samhap_match",
        "hwahyo_label",
        "is_ilpa_flag", "is_wolpa_flag", "is_donghyo_chung_flag",
        "wonsin_yukchin", "is_wonsin_dong", "is_wonsin_broken", "wonsin_hwahyo_label",
        "gisin_yukchin", "is_gisin_dong", "is_gisin_broken", "is_gisin_wang", "gisin_hwahyo_label",
        "gushin_yukchin", "is_gushin_dong",
        "eung_ohang", "is_eung_dong", "is_eung_gongmang", "eung_rel",
        "is_yukchunggwe", "is_yukhapgwe",
        "base_score", "label",
    ]
    n_rows = 0
    label_counter = {}
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for gua_name in yd.GUA_64.values():
            for dong_label, dong_idx_set in DONG_PATTERNS:
                for qtype in yd.QUESTION_TYPES:
                    for wolgeon_jj in WOLGEON_SWEEP:
                        for iljin_ganji in ILJIN_SWEEP:
                            row = _row_for(gua_name, dong_label, dong_idx_set, qtype, wolgeon_jj, iljin_ganji)
                            if row is None:
                                continue
                            writer.writerow(row)
                            n_rows += 1
                            label_counter[row["label"]] = label_counter.get(row["label"], 0) + 1
    return n_rows, label_counter


def _write_meta(n_rows, label_counter):
    """CSV 본체(40MB, .gitignore 대상)는 커밋하지 않는다 — 대신 재현
    검증에 필요한 MD5 해시·행 수·라벨 분포만 짧은 텍스트로 남겨 커밋한다.
    다른 사람이 이 스크립트를 다시 돌렸을 때 이 메타 파일과 MD5가
    일치하면 골든이 그대로 재현됐다는 뜻이다."""
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
        f.write(f"rows={n_rows}\n")
        f.write(f"size_bytes={_size}\n")
        f.write("label_distribution=" + ",".join(f"{k}:{v}" for k, v in sorted(label_counter.items())) + "\n")
    return meta_path, _md5.hexdigest(), _size


if __name__ == "__main__":
    n_rows, label_counter = generate()
    print(f"골든 baseline 생성 완료: {OUT_PATH}")
    print(f"총 행 수: {n_rows}")
    print("라벨 분포:", label_counter)
    meta_path, md5_hex, _size = _write_meta(n_rows, label_counter)
    print(f"파일 크기: {_size:,} bytes ({_size / 1024 / 1024:.2f} MB)")
    print(f"MD5: {md5_hex}")
    print(f"메타 파일(커밋 대상): {meta_path}")
