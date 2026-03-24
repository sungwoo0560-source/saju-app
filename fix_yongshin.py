# fix_yongshin.py
with open("saju_interpreter.py", encoding="utf-8") as f:
    src = f.read()

old = '''    all_yong = list(dict.fromkeys(eokbu_yong + [OH.get(c, "") for c in jokhu.get("need", [])] + ([tongkwan_yong] if tongkwan_yong else [])))

    all_yong = [o for o in all_yong if o]

    # 병약용신(病藥用神): 가장 강한 오행이 병(病)이면 그것을 제어하는 오행이 약(藥)
    byeong_yong = None
    byeong_desc = ""
    if oh_list:
        strongest_oh, strongest_val = oh_list[0]
        if strongest_val >= 40:  # 한 오행이 40% 이상 독점 → 병(病)으로 판단
            # 병(病)을 극하는 오행 = 약(藥)
            byeong_yong = CONTROL_MAP.get(strongest_oh, "")
            byeong_desc = (
                f"{strongest_oh}({OHN.get(strongest_oh, '')}) 기운이 과도({strongest_val:.0f}%)하여 병(病)을 이룸. "
                f"이를 제어하는 {byeong_yong}({OHN.get(byeong_yong, '')}) 기운이 병약용신(病藥用神)입니다."
            )
            if byeong_yong and byeong_yong not in all_yong:
                all_yong.append(byeong_yong)'''

new = '''    # ── 1차 억부, 2차 조후 우선순위 로직 ──────────────────
    # 극열(巳午未) / 극한(亥子丑) 월은 조후가 억부보다 우선
    jokhu_oh = [OH.get(c, "") for c in jokhu.get("need", [])]
    jokhu_oh = [o for o in jokhu_oh if o]
    is_extreme = jokhu.get("hot", False) or wol_jj in ["亥", "子", "丑"]

    if is_extreme and jokhu_oh:
        # 조후 우선: 조후용신 앞에 배치, 억부는 보조
        priority_yong = jokhu_oh + [y for y in eokbu_yong if y not in jokhu_oh]
        jokhu_priority = True
    else:
        # 억부 우선: 억부용신 앞에 배치, 조후는 보조
        priority_yong = eokbu_yong + [y for y in jokhu_oh if y not in eokbu_yong]
        jokhu_priority = False

    # 통관 추가
    if tongkwan_yong and tongkwan_yong not in priority_yong:
        priority_yong.append(tongkwan_yong)

    all_yong = [o for o in priority_yong if o]

    # 병약용신(病藥用神): 가장 강한 오행이 병(病)이면 그것을 제어하는 오행이 약(藥)
    byeong_yong = None
    byeong_desc = ""
    if oh_list:
        strongest_oh, strongest_val = oh_list[0]
        if strongest_val >= 40:  # 한 오행이 40% 이상 독점 → 병(病)으로 판단
            byeong_yong = CONTROL_MAP.get(strongest_oh, "")
            byeong_desc = (
                f"{strongest_oh}({OHN.get(strongest_oh, '')}) 기운이 과도({strongest_val:.0f}%)하여 병(病)을 이룸. "
                f"이를 제어하는 {byeong_yong}({OHN.get(byeong_yong, '')}) 기운이 병약용신(病藥用神)입니다."
            )
            if byeong_yong and byeong_yong not in all_yong:
                all_yong.insert(0, byeong_yong) if is_extreme else all_yong.append(byeong_yong)'''

src = src.replace(old, new)

old2 = '''    return {
        "억부_base": eokbu_base,
        "억부_desc": eokbu_desc,
        "억부_용신": eokbu_yong,
        "조후_desc": jokhu.get("desc", ""),
        "조후_need": jokhu.get("need", []),
        "조후_avoid": jokhu.get("avoid", []),
        "통관_yong": tongkwan_yong,
        "통관_desc": tongkwan_desc,
        "병약_yong": byeong_yong,
        "병약_desc": byeong_desc,
        "기신": kihwa,
        "종합_용신": all_yong,
        "월지": wol_jj,
    }'''

new2 = '''    return {
        "억부_base": eokbu_base,
        "억부_desc": eokbu_desc,
        "억부_용신": eokbu_yong,
        "조후_desc": jokhu.get("desc", ""),
        "조후_need": jokhu.get("need", []),
        "조후_avoid": jokhu.get("avoid", []),
        "조후_우선": jokhu_priority,   # True=조후우선 / False=억부우선
        "통관_yong": tongkwan_yong,
        "통관_desc": tongkwan_desc,
        "병약_yong": byeong_yong,
        "병약_desc": byeong_desc,
        "기신": kihwa,
        "종합_용신": all_yong,
        "월지": wol_jj,
    }'''

src = src.replace(old2, new2)

with open("saju_interpreter.py", "w", encoding="utf-8") as f:
    f.write(src)
print("saju_interpreter.py 수정 완료")

import py_compile
try:
    py_compile.compile("saju_interpreter.py", doraise=True)
    print("문법 OK: saju_interpreter.py")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
