# fix_share_card.py — 사주 공유 HTML 카드 추가
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

old1 = '''            with st.expander("🔗 이 사주 공유하기", expanded=False):
                st.caption("링크를 열면 같은 사주가 자동으로 불러집니다 (이름·생년월일·성별·결혼·직업 포함)")'''

new1 = '''            with st.expander("🔗 이 사주 공유하기", expanded=False):
                st.caption("링크를 열면 같은 사주가 자동으로 불러집니다 (이름·생년월일·성별·결혼·직업 포함)")

                # ── 사주 공유 카드 (스크린샷용) ──────────────────
                try:
                    _ilgan_card = pils[1]["cg"] if len(pils)>1 else ""
                    _iljj_card  = pils[1]["jj"] if len(pils)>1 else ""
                    _ys_card = get_yongshin(pils) or {}
                    _yong_card = _ys_card.get("종합_용신",[])
                    _gk_card = get_gyeokguk(pils)
                    _gkn_card = _gk_card.get("격국명","") if _gk_card else ""
                    _sn_card = get_ilgan_strength(_ilgan_card, pils)
                    _sn_card_str = _sn_card.get("신강신약","중화") if _sn_card else "중화"
                    _sw_card = get_yearly_luck(pils, datetime.now().year) or {}
                    _sw_ss_card = _sw_card.get("십성_천간","")
                    _sw_gh_card = _sw_card.get("길흉","평")
                    _sw_gan_card= _sw_card.get("세운","")
                    _OHN_CARD = {"木":"목(木)","火":"화(火)","土":"토(土)","金":"금(金)","Water":"수(水)","水":"수(水)"}
                    _OH_CARD = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                                "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
                    _yong_str_card = " · ".join([_OHN_CARD.get(y,y) for y in _yong_card[:2]]) if _yong_card else "-"
                    _GH_COLOR = {"길":"#27ae60","+":"#27ae60","평":"#2980b9","흉":"#e74c3c","-":"#e74c3c"}
                    _gh_color_card = _GH_COLOR.get(_sw_gh_card,"#888")

                    # 팔자 8글자
                    _PIL_NAMES = ["시","일","월","년"]
                    _pil_str_card = " ".join([
                        f"{p.get('cg','')}{p.get('jj','')}"
                        for p in pils[:4]
                    ])

                    # 오행 분포
                    _oh_cnt_card = {"木":0,"火":0,"土":0,"金":0,"水":0}
                    _OH_MAP_CARD = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                                    "己":"土","庚":"金","辛":"金","壬":"水","癸":"水",
                                    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土",
                                    "巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
                    for _p in pils:
                        for _ch in [_p.get("cg",""), _p.get("jj","")]:
                            _o = _OH_MAP_CARD.get(_ch,"")
                            if _o: _oh_cnt_card[_o] = _oh_cnt_card.get(_o,0)+1
                    _oh_bar_card = "".join([
                        f"<span style='margin-right:4px;font-size:11px;'>"
                        f"{'⬛' if _on=='木' else '🟥' if _on=='火' else '🟫' if _on=='土' else '⬜' if _on=='金' else '🟦'}"
                        f"×{_oc}</span>"
                        for _on, _oc in _oh_cnt_card.items() if _oc > 0
                    ])

                    _birth_info_card = ""
                    try:
                        _bm_c = st.session_state.get("birth_month",1)
                        _bd_c = st.session_state.get("birth_day",1)
                        _bh_c = st.session_state.get("birth_hour",12)
                        _birth_info_card = f"{birth_year}년 {_bm_c}월 {_bd_c}일 {_bh_c}시"
                    except Exception:
                        _birth_info_card = f"{birth_year}년생"

                    _cur_yr_card = datetime.now().year
                    _age_card = _cur_yr_card - birth_year + 1

                    _card_html = f"""
<div id="saju-share-card" style="
    background:linear-gradient(135deg,#0d0820 0%,#1a1035 50%,#0d0820 100%);
    border:2px solid #d4af37;
    border-radius:20px;
    padding:24px;
    max-width:400px;
    margin:12px auto;
    font-family:sans-serif;
    box-shadow:0 8px 32px rgba(212,175,55,0.3);
">
  <!-- 헤더 -->
  <div style="text-align:center;margin-bottom:16px;">
    <div style="font-size:10px;color:#d4af37;letter-spacing:4px;font-weight:900;">
      ✨ 만세력 사주 천명풀이 ✨
    </div>
    <div style="font-size:22px;font-weight:900;color:#fff;margin-top:4px;">
      {name}님의 사주
    </div>
    <div style="font-size:11px;color:#aaa;margin-top:2px;">
      {_birth_info_card} · {gender}성 · {_age_card}세
    </div>
  </div>

  <!-- 팔자 8글자 -->
  <div style="display:flex;justify-content:center;gap:8px;margin-bottom:16px;">
    {''.join([
        f"<div style='background:rgba(255,255,255,0.08);border-radius:10px;"
        f"padding:10px 8px;text-align:center;min-width:52px;border:1px solid #d4af3744;'>"
        f"<div style='font-size:9px;color:#d4af37;'>{_PIL_NAMES[i] if i<len(_PIL_NAMES) else ''}주</div>"
        f"<div style='font-size:18px;font-weight:900;color:#fff;'>{pils[i].get('cg','') if i<len(pils) else ''}</div>"
        f"<div style='font-size:18px;font-weight:900;color:#ccc;'>{pils[i].get('jj','') if i<len(pils) else ''}</div>"
        f"</div>"
        for i in range(min(4,len(pils)))
    ])}
  </div>

  <!-- 핵심 정보 3칸 -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:14px;">
    <div style="background:rgba(255,255,255,0.06);border-radius:10px;padding:10px 6px;text-align:center;">
      <div style="font-size:9px;color:#d4af37;">格局</div>
      <div style="font-size:12px;font-weight:900;color:#fff;">{_gkn_card or '-'}</div>
    </div>
    <div style="background:rgba(255,255,255,0.06);border-radius:10px;padding:10px 6px;text-align:center;">
      <div style="font-size:9px;color:#d4af37;">用神</div>
      <div style="font-size:12px;font-weight:900;color:#7fff7f;">{_yong_str_card}</div>
    </div>
    <div style="background:rgba(255,255,255,0.06);border-radius:10px;padding:10px 6px;text-align:center;">
      <div style="font-size:9px;color:#d4af37;">身强弱</div>
      <div style="font-size:12px;font-weight:900;color:#aaaaff;">{_sn_card_str}</div>
    </div>
  </div>

  <!-- 오행 분포 -->
  <div style="background:rgba(255,255,255,0.04);border-radius:10px;
  padding:8px 12px;margin-bottom:14px;text-align:center;">
    <div style="font-size:9px;color:#888;margin-bottom:4px;">오행 분포</div>
    <div>{_oh_bar_card}</div>
  </div>

  <!-- 올해 운기 -->
  <div style="background:rgba(212,175,55,0.1);border:1px solid #d4af3744;
  border-radius:10px;padding:10px 14px;margin-bottom:14px;">
    <div style="font-size:9px;color:#d4af37;margin-bottom:4px;">
      {_cur_yr_card}년 세운
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div style="font-size:14px;font-weight:900;color:#fff;">
        {_sw_gan_card} [{_sw_ss_card}]
      </div>
      <div style="font-size:12px;font-weight:700;color:{_gh_color_card};">
        {_sw_gh_card}
      </div>
    </div>
  </div>

  <!-- 푸터 -->
  <div style="text-align:center;font-size:10px;color:#666;">
    saju-manse.streamlit.app
  </div>
</div>

<div style="text-align:center;margin-top:8px;">
  <div style="font-size:12px;color:#888;background:#111;border-radius:8px;
  padding:8px 12px;display:inline-block;">
    📱 위 카드를 <b style="color:#d4af37">길게 눌러 이미지 저장</b> 후 공유하세요
    <br>💻 PC는 <b style="color:#d4af37">우클릭 → 이미지로 저장</b>
  </div>
</div>
"""
                    st.markdown(_card_html, unsafe_allow_html=True)
                except Exception:
                    pass'''

src = src.replace(old1, new1)

with open("manse.py", "w", encoding="utf-8") as f:
    f.write(src)
print("수정 완료")

import py_compile
try:
    py_compile.compile("manse.py", doraise=True)
    print("문법 OK")
except py_compile.PyCompileError as e:
    print(f"문법 오류: {e}")
