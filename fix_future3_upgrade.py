# fix_future3_upgrade.py — 미래3년 시나리오 상세화
with open("manse.py", encoding="utf-8") as f:
    src = f.read()

# ── 수정: 각 연도 카드 하단에 시나리오별 행동 계획 추가 ──
old1 = '''        if yd["hap_warn"]:
            for hw in yd["hap_warn"]:
                st.markdown(
                    f"""<div style="background:#fff0f0;border-left:4px solid {hw["color"]};border-radius:8px;padding:10px 14px;margin-top:8px;font-size:12px">
<b style="color:{hw["color"]}">{hw["level"]}</b><br>
<span style="color:#333">{hw["desc"]}</span></div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)'''

new1 = '''        if yd["hap_warn"]:
            for hw in yd["hap_warn"]:
                st.markdown(
                    f"""<div style="background:#fff0f0;border-left:4px solid {hw["color"]};border-radius:8px;padding:10px 14px;margin-top:8px;font-size:12px">
<b style="color:{hw["color"]}">{hw["level"]}</b><br>
<span style="color:#333">{hw["desc"]}</span></div>""",
                    unsafe_allow_html=True,
                )

        # ── 시나리오별 구체 행동 계획 ────────────────────────────
        try:
            _yr_sw2 = yd["sw_ss"]
            _yr_dw2 = yd["dw_ss"]
            _yr_y2  = yd["year"]
            _yr_age2= yd["age"]
            _is_gold2 = yd["is_yong_sw"] and yd["is_yong_dw"]
            _is_bad2  = not yd["is_yong_sw"] and not yd["is_yong_dw"]

            # 시나리오 분류
            if _is_gold2:
                _scenario = "황금기"
                _sc_bg = "#1a3d1a"; _sc_tc = "#7fff7f"
                _sc_title = f"🌟 {_yr_y2}년 황금기 — 지금 준비해야 할 것"
            elif _is_bad2:
                _scenario = "수비기"
                _sc_bg = "#3d1a1a"; _sc_tc = "#ffaaaa"
                _sc_title = f"🛡️ {_yr_y2}년 수비기 — 반드시 지켜야 할 것"
            else:
                _scenario = "혼재기"
                _sc_bg = "#1a1a2e"; _sc_tc = "#aaaaff"
                _sc_title = f"⚖️ {_yr_y2}년 혼재기 — 선택과 집중 전략"

            # 십성별 구체 시나리오
            _SS_SCENARIO = {
                "偏財": {
                    "황금기": [
                        "💰 사업 확장·신규 투자 검토 (단 전체 자산의 30% 이내)",
                        "💑 이성 인연 적극 탐색 — 소개팅·모임 참여 늘리기",
                        "📈 부동산·주식 분산 투자 타이밍 검토",
                        "🤝 새로운 파트너십·협업 제안 수락 검토",
                    ],
                    "수비기": [
                        "🚫 투기·도박·고위험 투자 절대 금지",
                        "💳 카드 지출·충동 구매 가계부로 통제",
                        "🏦 비상금 6개월치 별도 계좌에 확보",
                        "⚠️ 이성 관계에서 감정적 결정 자제",
                    ],
                    "혼재기": [
                        "✅ 기회가 오면 잡되 규모는 절반으로",
                        "📊 매월 수입·지출 정기 점검 루틴 만들기",
                        "🎯 한 가지 재물 목표에만 집중",
                    ],
                },
                "正財": {
                    "황금기": [
                        "🏦 적금·부동산 등 안전 자산 집중 확보",
                        "📝 연봉 협상·급여 인상 요청 타이밍",
                        "💍 결혼·계약 등 안정적 약속 맺기 최적",
                        "📋 보험 점검 및 장기 재무 계획 수립",
                    ],
                    "수비기": [
                        "🔒 현금 보유 최우선 — 유동성 확보",
                        "❌ 새로운 계약·약속 최소화",
                        "📉 지출 구조 재점검 — 고정비 절감",
                        "🛡️ 기존 자산 지키기에 집중",
                    ],
                    "혼재기": [
                        "💰 소액 안전 저축 꾸준히 유지",
                        "📊 수입 대비 저축률 20% 이상 목표",
                        "🎯 한 가지 재무 목표에 집중",
                    ],
                },
                "食神": {
                    "황금기": [
                        "🚀 창업·부업·새 프로젝트 시작 최적 타이밍",
                        "🎓 자격증·전문성 강화로 수입 파이프라인 추가",
                        "📢 SNS·콘텐츠로 자신을 브랜딩하기 시작",
                        "💼 좋아하는 일을 수익화하는 전략 실행",
                    ],
                    "수비기": [
                        "⚠️ 섣부른 창업·투자 자제 — 준비 기간으로",
                        "📚 역량 강화·공부에 집중",
                        "🌱 작은 성취를 쌓으며 자신감 회복",
                    ],
                    "혼재기": [
                        "🎯 소규모 테스트로 가능성 확인 후 확장",
                        "📝 아이디어를 행동으로 옮기는 연습",
                        "🤝 같은 분야 사람들과 네트워크 형성",
                    ],
                },
                "傷官": {
                    "황금기": [
                        "💡 혁신적 아이디어 실행 — 다른 방식으로 승부",
                        "🔧 기술·전문성 업그레이드로 경쟁력 강화",
                        "✏️ 창작·발명·특허 등 독창적 성취 도전",
                        "⚠️ 윗사람·고객과 언행 충돌 각별히 주의",
                    ],
                    "수비기": [
                        "🤐 말 조심 — 감정적 언행이 큰 손해로 이어짐",
                        "📝 계약서 세부 조항 반드시 확인",
                        "🏃 이직 충동이 강해지는 시기 — 최소 3개월 숙려",
                        "👥 윗사람·권위자와 불필요한 마찰 피하기",
                    ],
                    "혼재기": [
                        "⚖️ 창의성은 살리되 표현 방식은 신중하게",
                        "📋 중요 결정은 문서로 남기는 습관",
                        "🎯 에너지를 한 가지 혁신에 집중",
                    ],
                },
                "偏官": {
                    "황금기": [
                        "💪 강한 압박을 이겨내는 체력·정신력 훈련",
                        "🏥 정기 건강검진 필수 — 사전 예방이 최선",
                        "⚖️ 법적 분쟁 소지 미리 정리",
                        "🛡️ 보험 보장 범위 점검 및 강화",
                    ],
                    "수비기": [
                        "🚨 건강·사고·관재 3가지 최우선 주의",
                        "🚫 새 사업·이직·큰 결정 이 해에는 보류",
                        "🏦 유동성 자산 최대한 확보",
                        "👨‍⚕️ 이상 증상 즉시 병원 방문",
                    ],
                    "혼재기": [
                        "🛡️ 안전망 먼저 구축 후 도전",
                        "📋 모든 약속·계약 문서화",
                        "💊 건강 관리를 최우선 루틴으로",
                    ],
                },
                "正官": {
                    "황금기": [
                        "📈 승진·이직·공직 도전 타이밍 — 지금이 최적",
                        "🎓 자격증·시험·학위 취득 집중 기간",
                        "🤝 공식적인 관계·계약·결혼 추진",
                        "🏆 조직 내 신뢰 쌓기에 올인",
                    ],
                    "수비기": [
                        "📋 원칙·규정 준수가 최고의 방어",
                        "🤐 조직 내 불평·불만 자제",
                        "🎯 현 자리에서 성과 증명에 집중",
                    ],
                    "혼재기": [
                        "✅ 기회가 왔을 때 원칙대로 행동",
                        "📚 자격·실력으로 준비된 상태 유지",
                        "👥 인맥 관리 꾸준히",
                    ],
                },
                "劫財": {
                    "황금기": [
                        "🏦 현금 보유 최우선 — 투자 최소화",
                        "🚫 보증·동업·연대 책임 절대 거절",
                        "📋 기존 채권·채무 관계 정리",
                        "🤝 신뢰할 수 있는 사람만 곁에 두기",
                    ],
                    "수비기": [
                        "🚨 재물 손실 위험 최고조 — 모든 투자 중단",
                        "🔒 주요 자산 분리 보관",
                        "👀 주변 인물 재검토 — 배신 위험",
                        "📝 금전 거래 반드시 문서화",
                    ],
                    "혼재기": [
                        "💰 소액·안전 자산 위주로만 운용",
                        "⚠️ 새로운 사람과 금전 거래 자제",
                        "🛡️ 현재 자산 방어에 집중",
                    ],
                },
            }

            _scenarios_list = _SS_SCENARIO.get(_yr_sw2, {}).get(_scenario, [
                f"✅ {_scenario} 시기에 맞는 전략으로 꾸준히 나아가십시오.",
                f"📊 용신 기운을 강화하고 기신 기운을 차단하는 생활 습관을 유지하십시오.",
                f"🎯 한 가지 목표에 집중하는 것이 이 시기의 핵심입니다.",
            ])

            _sc_html = "".join(
                f"<div style='padding:5px 0;font-size:12px;color:#fff;"
                f"border-bottom:1px solid rgba(255,255,255,0.08);'>{s}</div>"
                for s in _scenarios_list
            )

            st.markdown(
                f"<div style='background:{_sc_bg};border-radius:10px;"
                f"padding:14px 18px;margin:8px 0;"
                f"border:1px solid {_sc_tc}44;'>"
                f"<div style='font-size:13px;font-weight:900;color:{_sc_tc};"
                f"margin-bottom:10px;'>{_sc_title}</div>"
                f"{_sc_html}"
                f"</div>",
                unsafe_allow_html=True,
            )
        except Exception:
            pass

        st.markdown("</div>", unsafe_allow_html=True)'''

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
