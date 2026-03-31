with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 수정 1: sw_gil 정규화 — "평(平)" → "평" 등
old1 = '''    sw_gil = (cross.get("sw_gil") or cross.get("길흉") or "평")
    dw_age_s = cross.get("dw_start_age", cross.get("시작나이", ""))
    dw_age_e = cross.get("dw_end_age",   cross.get("종료나이", ""))'''

new1 = '''    sw_gil = (cross.get("sw_gil") or cross.get("길흉") or "평")
    # "평(平)" → "평" 정규화
    import re as _re
    sw_gil = _re.sub(r'\([^)]+\)', '', str(sw_gil)).strip()
    dw_age_s = cross.get("dw_start_age", cross.get("시작나이", ""))
    dw_age_e = cross.get("dw_end_age",   cross.get("종료나이", ""))'''

# 수정 2: 기신 처리 — 문자열/리스트 모두 대응
old2 = '''        yong_ohs = ys_info.get("종합_용신", [])
        gi_ohs   = ys_info.get("기신", [])
        yong_str = "·".join(yong_ohs[:2]) if yong_ohs else ""
        gi_str   = "·".join(gi_ohs[:1]) if gi_ohs else ""'''

new2 = '''        yong_ohs = ys_info.get("종합_용신", [])
        _gi_raw  = ys_info.get("기신", [])
        # 기신이 문자열로 반환되는 경우 리스트로 변환
        if isinstance(_gi_raw, list):
            gi_ohs = _gi_raw
        elif isinstance(_gi_raw, str) and _gi_raw:
            # "木·火" 형태면 분리, 아니면 빈 리스트
            gi_ohs = [x.strip() for x in _gi_raw.replace("·", ",").split(",") if x.strip() in ["木","火","土","金","水"]]
        else:
            gi_ohs = []
        yong_str = "·".join(yong_ohs[:2]) if yong_ohs else ""
        gi_str   = "·".join(gi_ohs[:1]) if gi_ohs else ""'''

count = 0
for i, (old, new) in enumerate([(old1, new1), (old2, new2)], 1):
    if old in content:
        content = content.replace(old, new, 1)
        count += 1
        print(f"✅ 수정 {i} 완료")
    else:
        print(f"❌ 수정 {i} 패턴 없음")

with open('manse.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n{count}/2 완료")
