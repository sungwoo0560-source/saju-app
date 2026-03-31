#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""menu_current_situation() 함수의 데이터 흐름 테스트"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from datetime import datetime

try:
    from saju_engine import SajuCoreEngine
    
    # 제1단계: 샘플 사주 생성
    print("═" * 60)
    print("📊 menu_current_situation() 함수 데이터 흐름 분석")
    print("═" * 60)
    print()
    
    pils = SajuCoreEngine.get_pillars(1990, 3, 15, 10)
    cur_year = datetime.now().year
    cur_age = cur_year - 1990 + 1
    name = "테스트"

    print(f"✅ 1️⃣ 연도·나이 계산 (라인 11507-11508)")
    print(f"   현재연도: {cur_year}")
    print(f"   현재나이: {cur_age}")
    print()

    # 제2단계: 대운·세운 추출
    from saju_interpreter import get_crossing_interpretation, get_ilgan_strength, get_yongshin
    
    cross = get_crossing_interpretation(pils, cur_year)
    dw_ss  = cross.get("dw_ss", "")
    sw_ss  = cross.get("sw_ss", "")
    sw_gil = cross.get("sw_gil", "")
    
    print(f"✅ 2️⃣ 대운·세운 십성 추출 (라인 11515-11522)")
    print(f"   get_crossing_interpretation() 호출")
    print(f"   dw_ss (대운 십성): {dw_ss}")
    print(f"   sw_ss (세운 십성): {sw_ss}")
    print(f"   sw_gil (세운 길흉): {sw_gil}")
    print()

    # 제3단계: 신강신약·용신·기신
    ilgan = pils[1]["cg"]
    sn_info = get_ilgan_strength(ilgan, pils)
    sn = sn_info.get("신강신약", "중화")
    ys_info = get_yongshin(pils)
    yong_ohs = ys_info.get("종합_용신", [])
    gi_ohs = ys_info.get("기신", [])
    yong_str = "·".join(yong_ohs[:2]) if yong_ohs else ""
    gi_str = "·".join(gi_ohs[:1]) if gi_ohs else ""
    
    print(f"✅ 3️⃣ 신강신약·용신·기신 추출 (라인 11524-11544)")
    print(f"   일간: {ilgan}")
    print(f"   신강신약: {sn}")
    print(f"   용신: {yong_ohs}")
    print(f"   기신: {gi_ohs}")
    print(f"   yong_str: {yong_str}")
    print(f"   gi_str: {gi_str}")
    print()

    # 제4단계: 십성 한글 변환
    _SS_KR = {
        "偏財(편재)":"편재","正財(정재)":"정재","食神(식신)":"식신","傷官(상관)":"상관",
        "偏官(편관)":"편관","正官(정관)":"정관","偏印(편인)":"편인","正印(정인)":"정인",
        "比肩(비견)":"비견","劫財(겁재)":"겁재",
    }
    dw_kr = _SS_KR.get(dw_ss, dw_ss)
    sw_kr = _SS_KR.get(sw_ss, sw_ss)
    
    print(f"✅ 4️⃣ 십성 한글 변환 (라인 11538-11544)")
    print(f"   _SS_KR 딕셔너리 변환")
    print(f"   {dw_ss} → {dw_kr}")
    print(f"   {sw_ss} → {sw_kr}")
    print()

    # 제5~7단계: 해석 딕셔너리 건너뛰고, 최종 조립
    print(f"✅ 5️⃣ 해석 텍셋 선택 (라인 11875-11884)")
    print(f"   _HARD_REASON.get('{sw_kr}')")
    print(f"   _DW_CONTEXT.get('{dw_kr}')")
    print(f"   _GIL_COMMENT.get('{sw_gil}')")
    print(f"   _SN_COMMENT에서 '{sn}' 매칭")
    yong_first = yong_ohs[0] if yong_ohs else "없음"
    print(f"   _YONG_RX.get('{yong_first}')")
    print(f"   _GISIN_DETAIL.get('{gi_str}')")
    print()

    print(f"✅ 6️⃣ 마크다운 조립 (라인 11886-11938)")
    print(f"   lines = []")
    print(f"   lines.append('## 🎯 {name}님, 지금 무엇 때문에 힘드신가요?')")
    print(f"   lines.append('*{cur_year}년 · {cur_age}세 · {dw_kr} 대운 · {sw_kr} 세운*')")
    print(f"   lines.append('### 💬 {{hard_q}}')")
    print(f"   lines.append('{{hard_body}}')")
    if dw_kr: print(f"   if dw_ctx: lines.append('{{dw_ctx}}')")
    if sw_gil: print(f"   if gil_cmt: lines.append('{{gil_cmt}}')")
    if sn: print(f"   if sn_cmt: lines.append('{{sn_cmt}}')")
    if yong_str: print(f"   if yong_rx: lines.append('### 🌿 지금 당장 할 수 있는 것')")
    if gi_str: print(f"   if gi_detail: lines.append('### ⚠️ 지금 조심해야 할 것')")
    print()

    print(f"✅ 7️⃣ Streamlit 렌더링 (라인 11932-11938)")
    print(f"   st.markdown(CSS 스타일)")
    print(f"   st.markdown('\\n'.join(lines))")
    print(f"   render_pdf_download_btn('current_situation', ...)")
    print()
    
    print("=" * 60)
    print("✅ 데이터 흐름 테스트 완료!")
    print("=" * 60)

except Exception as e:
    print(f'❌ 오류: {e}')
    import traceback
    traceback.print_exc()
