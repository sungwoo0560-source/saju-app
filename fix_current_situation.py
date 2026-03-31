import re

with open('manse.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 수정 1: cross 데이터 fallback 강화 (대운·세운 십성 정확도) ──
old1 = '''    dw_ss  = cross.get("dw_ss", "")
    sw_ss  = cross.get("sw_ss", "")
    sw_gil = cross.get("sw_gil", "")'''

new1 = '''    # fallback 키 다중 시도 — 반환 형식이 달라도 잡히게
    dw_ss  = (cross.get("dw_ss")  or cross.get("대운_천간십성") or
              cross.get("대운십성") or "")
    sw_ss  = (cross.get("sw_ss")  or cross.get("세운_천간십성") or
              cross.get("세운십성") or "")
    sw_gil = (cross.get("sw_gil") or cross.get("길흉") or "평")
    # 대운 나이 범위 (있으면 표시용)
    dw_age_s = cross.get("dw_start_age", cross.get("시작나이", ""))
    dw_age_e = cross.get("dw_end_age",   cross.get("종료나이", ""))'''

# ── 수정 2: 나이 표시 개선 (한국 나이 + 만 나이 병기) ──
old2 = '''    lines.append(f"## 🎯 {name}님, 지금 무엇 때문에 힘드신가요?")
    lines.append(f"*{cur_year}년 · {cur_age}세 · {dw_kr or ''} 대운 · {sw_kr or ''} 세운*")'''

new2 = '''    _dw_label = f"{dw_kr} 대운" if dw_kr else "대운 미산출"
    _sw_label = f"{sw_kr} 세운" if sw_kr else f"{cur_year}년 세운"
    _age_range = f" ({dw_age_s}~{dw_age_e}세 대운)" if dw_age_s and dw_age_e else ""
    lines.append(f"## 🎯 {name}님, 지금 무엇 때문에 힘드신가요?")
    lines.append(f"*{cur_year}년 · 한국나이 {cur_age}세(만 {cur_age-1}세) · {_dw_label}{_age_range} · {_sw_label}*")'''

# ── 수정 3: 용신 처방 — 2개 오행 모두 활용 ──
old3 = '''    yong_rx = _YONG_RX.get(yong_ohs[0] if yong_ohs else "", "") if yong_ohs else ""
    gi_detail = _GISIN_DETAIL.get(gi_str, "") if gi_str else ""'''

new3 = '''    # 용신 최대 2개 처방 모두 합산
    yong_rx = ""
    for _yoh in (yong_ohs[:2] if yong_ohs else []):
        _rx = _YONG_RX.get(_yoh, "")
        if _rx:
            yong_rx += _rx + "\n\n"
    yong_rx = yong_rx.strip()
    # 기신 — 최대 2개
    gi_str2 = "·".join(gi_ohs[:2]) if gi_ohs else ""
    gi_detail = _GISIN_DETAIL.get(gi_str, _GISIN_DETAIL.get(gi_str2, "")) if (gi_str or gi_str2) else ""'''

# ── 수정 4: 푸터 — 구체적 데이터 명시 ──
old4 = '''    lines.append("*위 분석은 대운·세운 십성 교차 및 사주 원국 데이터를 기반으로 자동 생성됩니다.*")'''

new4 = '''    _data_note = f"일간 {ilgan} · 신강신약 {sn} · 용신 {yong_str or '미산출'} · 기신 {gi_str or '미산출'}"
    lines.append(f"*위 분석은 {_dw_label} × {_sw_label} 교차 및 사주 원국을 기반으로 자동 생성됩니다.*")
    lines.append(f"*[ {_data_note} ]*")'''

# 적용
count = 0
for old, new in [(old1,new1),(old2,new2),(old3,new3),(old4,new4)]:
    if old in content:
        content = content.replace(old, new, 1)
        count += 1
        print(f"✅ 수정 {count} 적용 완료")
    else:
        print(f"❌ 수정 {count} 패턴 미발견 — 확인 필요")

with open('manse.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n총 {count}/4 수정 완료 → manse.py 저장됨")
