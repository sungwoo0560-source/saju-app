# -*- coding: utf-8 -*-
"""육효 판정(judge_yukhyo_advanced) 골든 baseline 생성기.

★목적: 육충(六沖) 도입 "직전" 현재 판정 결과를 대량으로 떠서 파일로 고정해
둔다. 나중에 육충을 얹은 뒤 이 파일과 다시 비교하면 "몇 건이나 라벨이
바뀌었는지"를 정확히 셀 수 있다. 이 스크립트 자체는 판정 로직을 전혀
바꾸지 않는다 — yukhyo_data.py의 기존 함수를 그대로 호출만 한다.

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yukhyo_data as yd  # noqa: E402

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


def _gua_parts(gua_name):
    for (sa, ha), name in yd.GUA_64.items():
        if name == gua_name:
            return sa, ha
    raise ValueError(f"GUA_64에 없는 괘명: {gua_name}")


def _row_for(gua_name, dong_label, dong_idx_set, qtype, wolgeon_jj, iljin_ganji):
    sa_name, ha_name = _gua_parts(gua_name)
    nap_ha = yd.NAPGAP[ha_name]
    nap_sa = yd.NAPGAP[sa_name]
    jiji6 = list(nap_ha["내괘_지지"]) + list(nap_sa["외괘_지지"])
    hexa6 = tuple(yd.BAGUA[ha_name]["효"]) + tuple(yd.BAGUA[sa_name]["효"])
    dong6 = [i in dong_idx_set for i in range(6)]

    gung_oh = yd.get_gung_ohang(gua_name)
    yukchin6 = [yd.get_yukchin(gung_oh, yd.JIJI_OHANG[j]) for j in jiji6]
    se_pos, eung_pos = yd.SEEUNG[gua_name]
    se_ohang = yd.JIJI_OHANG[jiji6[se_pos - 1]]

    target_yukchin = yd.QUESTION_YONGSHIN[qtype]
    if target_yukchin is None:
        yongshin_idx = se_pos - 1
    else:
        yongshin_idx = yd.pick_yongshin_idx(yukchin6, target_yukchin, dong6, se_pos)

    is_bokshin = yongshin_idx is None
    if is_bokshin:
        bokshin_info = yd.get_bokshin(gua_name, target_yukchin, se_pos)
        if bokshin_info is None:
            # 본궁 순괘에도 그 육친이 없는 경우(이론상 없어야 하나 방어)
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
        if is_dong_y:
            byeon_hexa = tuple((1 - hexa6[i]) if dong6[i] else hexa6[i] for i in range(6))
            byeon_sa_name = byeon_ha_name = None
            for (sa, ha), _name in yd.GUA_64.items():
                cand = tuple(yd.BAGUA[ha]["효"]) + tuple(yd.BAGUA[sa]["효"])
                if cand == byeon_hexa:
                    byeon_sa_name, byeon_ha_name = sa, ha
                    break
            if byeon_ha_name and byeon_sa_name:
                byeon_nap_ha = yd.NAPGAP[byeon_ha_name]
                byeon_nap_sa = yd.NAPGAP[byeon_sa_name]
                byeon_jiji6 = list(byeon_nap_ha["내괘_지지"]) + list(byeon_nap_sa["외괘_지지"])
                hwa_jiji = byeon_jiji6[yongshin_idx]
                hwa_ohang = yd.JIJI_OHANG[hwa_jiji]
                hwahyo_label, _ = yd.judge_hwahyo(yongshin_ohang, hwa_ohang, hwa_jiji, iljin_ganji)

    is_gongmang_flag = yd.is_yukhyo_gongmang(yongshin_jiji, iljin_ganji)
    samhap_ohangs = yd.check_samhap_guk(jiji6)
    samhap_match = yongshin_ohang in samhap_ohangs

    base_score = yd._yukhyo_base_score(yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y)
    label, _reasons = yd.judge_yukhyo_advanced(
        yongshin_ohang, se_ohang, wolgeon_jj, iljin_ganji[1], is_dong=is_dong_y,
        is_bokshin=is_bokshin, is_gongmang_flag=is_gongmang_flag,
        samhap_match=samhap_match, hwahyo_label=hwahyo_label,
    )

    return {
        "gua": gua_name,
        "dong_pattern": dong_label,
        "qtype": qtype,
        "target_yukchin": target_yukchin or "",
        "yongshin_idx": "" if is_bokshin else yongshin_idx,
        "is_bokshin": int(is_bokshin),
        "yongshin_jiji": yongshin_jiji,
        "yongshin_ohang": yongshin_ohang,
        "se_pos": se_pos,
        "se_ohang": se_ohang,
        "eung_pos": eung_pos,
        "wolgeon_jj": wolgeon_jj,
        "iljin_ganji": iljin_ganji,
        "is_dong_y": int(is_dong_y),
        "is_gongmang_flag": int(is_gongmang_flag),
        "samhap_match": int(samhap_match),
        "hwahyo_label": hwahyo_label or "",
        "base_score": base_score,
        "label": label,
    }


def generate():
    fieldnames = [
        "gua", "dong_pattern", "qtype", "target_yukchin", "yongshin_idx", "is_bokshin",
        "yongshin_jiji", "yongshin_ohang", "se_pos", "se_ohang", "eung_pos",
        "wolgeon_jj", "iljin_ganji", "is_dong_y", "is_gongmang_flag", "samhap_match",
        "hwahyo_label", "base_score", "label",
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
