# lotto.py
# 실행: streamlit run lotto.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
import os
import re
from collections import Counter
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="🎲 AI 로또 엔진", page_icon="🎲", layout="centered")

# 로컬 데이터 저장 경로 (여러 경로 시도)
def _resolve_data_file():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "lotto_data.json"),
        os.path.join(os.getcwd(), "lotto_data.json"),
        r"c:\Users\sungw\OneDrive\Desktop\Project_Saju_313\lotto_data.json",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

DATA_FILE = _resolve_data_file()

# -----------------------------
# 로컬 데이터 저장/불러오기
# -----------------------------
_LOAD_ERROR = None

def load_local_data():
    global _LOAD_ERROR
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                rows = json.load(f)
            return pd.DataFrame(rows).sort_values("draw", ascending=False).reset_index(drop=True)
        except Exception as e:
            _LOAD_ERROR = f"파일 읽기 오류: {e}"
    return None

def save_local_data(df):
    try:
        rows = df[["draw", "nums", "bonus", "date"]].copy()
        rows["nums"] = rows["nums"].apply(lambda x: [int(n) for n in x])
        rows["draw"] = rows["draw"].apply(int)
        rows["bonus"] = rows["bonus"].apply(int)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(rows.to_dict("records"), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# -----------------------------
# 최신 회차 계산
# -----------------------------
def get_expected_latest_draw():
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    first = datetime(2002, 12, 7, 20, 45, 0, tzinfo=kst)
    diff_days = (now - first).days
    draw_no = max(1, diff_days // 7 + 1)
    return draw_no

# -----------------------------
# API 조회 (동행복권 JSON)
# -----------------------------
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.dhlottery.co.kr/gameResult.do?method=byWin",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
})

def get_draw(draw_no):
    url = "https://www.dhlottery.co.kr/common.do"
    params = {"method": "getLottoNumber", "drwNo": int(draw_no)}
    for attempt in range(2):
        try:
            r = SESSION.get(url, params=params, timeout=5)
            content = r.text.strip()
            if not content.startswith("{"):
                return None  # HTML 응답이면 즉시 포기
            js = r.json()
            if js.get("returnValue") == "success":
                nums = [int(js[f"drwtNo{i}"]) for i in range(1, 7)]
                return {
                    "draw": int(draw_no),
                    "nums": nums,
                    "bonus": int(js.get("bnusNo", 0)),
                    "date": js.get("drwNoDate", ""),
                }
        except Exception:
            time.sleep(0.3 * (attempt + 1))
    return None

# -----------------------------
# Fallback 데이터 (날짜 계산 기반 자동 생성 → 매주 자동 갱신)
# ※ 번호는 샘플입니다. 실제 번호는 사이드바에서 직접 입력하세요.
# -----------------------------
def get_builtin_fallback():
    latest = get_expected_latest_draw()
    kst = timezone(timedelta(hours=9))
    base_date = datetime(2002, 12, 7, tzinfo=kst)  # 1회 추첨일

    rows = []
    for i in range(10):
        draw_no = latest - i
        if draw_no < 1:
            break
        draw_date = base_date + timedelta(weeks=(draw_no - 1))
        date_str = draw_date.strftime("%Y-%m-%d")
        # 회차 번호를 시드로 결정론적 샘플 번호 생성 (항상 동일한 결과)
        rng = np.random.default_rng(draw_no * 91237 + 54321)
        nums = sorted(rng.choice(range(1, 46), 6, replace=False).tolist())
        bonus_pool = [n for n in range(1, 46) if n not in nums]
        bonus = int(rng.choice(bonus_pool))
        rows.append({
            "draw": draw_no,
            "nums": [int(n) for n in nums],
            "bonus": bonus,
            "date": date_str,
        })
    return pd.DataFrame(rows)

# -----------------------------
# 데이터 로드 (우선순위: 로컬저장 → API → 내장fallback)
# -----------------------------
@st.cache_data(ttl=1800)
def _fetch_api(count=100):
    """API에서 데이터 가져오기 (캐시됨 / 실패하면 None 반환)"""
    expected = get_expected_latest_draw()
    latest = None
    for d in range(expected + 5, max(expected - 15, 1), -1):
        item = get_draw(d)
        if item:
            latest = d
            break
    if latest is None:
        return None
    rows = []
    fail = 0
    for d in range(latest, max(latest - count, 0), -1):
        item = get_draw(d)
        if item:
            rows.append(item)
            fail = 0
        else:
            fail += 1
        if fail >= 3:
            break
        time.sleep(0.05)
    return rows if rows else None

def load_data(count=100):
    """항상 신선하게 로컬 파일 먼저 확인 → API → fallback"""
    # 1단계: 로컬 저장 데이터 (캐시 없이 파일을 직접 읽음)
    local = load_local_data()
    if local is not None and len(local) >= 10:
        return local, False

    # 2단계: API 조회 (캐시됨)
    rows = _fetch_api(count)
    if rows:
        df = pd.DataFrame(rows).sort_values("draw", ascending=False).reset_index(drop=True)
        save_local_data(df)
        return df, False

    return get_builtin_fallback(), True

# -----------------------------
# 패턴 분석
# -----------------------------
def analyze_patterns(df):
    n = min(100, len(df))
    recent = df.head(n)

    all_nums = [n for row in recent["nums"] for n in row]
    freq = Counter(all_nums)

    # 호트 / 콜드 번호
    hot = sorted(freq, key=freq.get, reverse=True)[:10]
    cold = sorted(freq, key=freq.get)[:10]

    # 황/짝 비율 트렌드 (20회)
    recent20 = df.head(min(20, len(df)))
    odd_ratios = [sum(n % 2 for n in row) for row in recent20["nums"]]
    avg_odd = round(np.mean(odd_ratios), 1)

    # 합계 트렌드 (20회)
    sums = [sum(row) for row in recent20["nums"]]
    avg_sum = round(np.mean(sums), 1)
    std_sum = round(np.std(sums), 1)

    # 구간 분포 (1-15 / 16-30 / 31-45)
    zone_counts = [[], [], []]
    for row in recent20["nums"]:
        z = [0, 0, 0]
        for n in row:
            if n <= 15:   z[0] += 1
            elif n <= 30: z[1] += 1
            else:         z[2] += 1
        zone_counts[0].append(z[0])
        zone_counts[1].append(z[1])
        zone_counts[2].append(z[2])
    avg_zones = [round(np.mean(z), 1) for z in zone_counts]

    return {
        "hot": hot,
        "cold": cold,
        "avg_odd": avg_odd,
        "avg_sum": avg_sum,
        "std_sum": std_sum,
        "avg_zones": avg_zones,
        "n": n,
    }

# -----------------------------
# 가중치 계산 (3단계: 10회 / 30회 / 100회)
# -----------------------------
def build_weights(df):
    recent_10 = df.head(min(10, len(df)))
    recent_30 = df.head(min(30, len(df)))
    recent_100 = df.head(min(100, len(df)))
    freq10  = Counter(n for row in recent_10["nums"] for n in row)
    freq30  = Counter(n for row in recent_30["nums"] for n in row)
    freq100 = Counter(n for row in recent_100["nums"] for n in row)
    weights = {}
    for n in range(1, 46):
        weights[n] = (1.0
                      + freq10.get(n, 0)  * 2.5   # 최근 10회 강감
                      + freq30.get(n, 0)  * 1.0
                      + freq100.get(n, 0) * 0.3)
    return weights

# -----------------------------
# 연속번호 검사 (4개 이상 연속만 제외)
# -----------------------------
def has_bad_consecutive(game):
    s = sorted(game)
    run = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1] + 1:
            run += 1
            if run >= 4:
                return True
        else:
            run = 1
    return False

# -----------------------------
# 패턴 기반 스마트 번호 생성
# -----------------------------
def generate_games(df, n_games=5):
    pat = analyze_patterns(df)
    weights = build_weights(df)

    numbers = np.array(list(range(1, 46)))
    probs = np.array([weights[n] for n in numbers], dtype=float)
    probs /= probs.sum()

    # 한 번에 맞춥할 목표 범위 설정
    odd_target  = round(pat["avg_odd"])
    sum_lo = max(70,  int(pat["avg_sum"] - pat["std_sum"] * 1.5))
    sum_hi = min(210, int(pat["avg_sum"] + pat["std_sum"] * 1.5))

    # 구간 목표 (avg 기준 ±1 허용)
    z_target = [round(z) for z in pat["avg_zones"]]

    games = []
    tries = 0
    while len(games) < n_games and tries < 30000:
        tries += 1
        pick = sorted(np.random.choice(numbers, 6, replace=False, p=probs).tolist())
        pick = [int(x) for x in pick]

        if pick in games:
            continue
        if has_bad_consecutive(pick):
            continue

        total = sum(pick)
        if total < sum_lo or total > sum_hi:
            continue

        odd = sum(n % 2 for n in pick)
        if abs(odd - odd_target) > 1:
            continue

        # 구간 벨런스
        z = [0, 0, 0]
        for n in pick:
            if n <= 15:   z[0] += 1
            elif n <= 30: z[1] += 1
            else:         z[2] += 1
        if any(abs(z[i] - z_target[i]) > 1 for i in range(3)):
            continue

        games.append(pick)
    return games

# -----------------------------
# 백테스트
# -----------------------------
def backtest(df):
    if len(df) < 30:
        return None
    rounds = min(15, len(df) - 20)
    scores = []
    for i in range(rounds):
        hist = df.iloc[i + 1:].reset_index(drop=True)
        actual = df.iloc[i]["nums"]
        games = generate_games(hist)
        if not games:
            continue
        best = max(len(set(g) & set(actual)) for g in games)
        scores.append(best)
    if not scores:
        return None
    return round(float(np.mean(scores)), 2)

# ==============================
# 사이드바: 수동 데이터 입력
# ==============================
with st.sidebar:
    st.header("📥 회차 수동 추가")
    st.caption("동행복권 사이트에서 확인한 실제 당첨번호를 입력하세요.")

    with st.form("manual_add"):
        draw_no_in = st.number_input("회차", min_value=1, max_value=9999, value=get_expected_latest_draw(), step=1)
        nums_in = st.text_input("당첨번호 6개", placeholder="예: 3 14 22 31 37 42  (공백·점·콤마 모두 가능)")
        bonus_in = st.number_input("보너스번호", min_value=1, max_value=45, value=1)
        date_in = st.text_input("추첨일 (YYYY-MM-DD)", placeholder="예: 2026-03-07")
        submitted = st.form_submit_button("추가하기", use_container_width=True)

    if submitted:
        try:
            # 공백, 점, 콤마, 슬래시 등 어떤 구분자도 허용
            tokens = re.split(r"[\s.,;/]+", nums_in.strip())
            nums_list = [int(x) for x in tokens if x]
            if len(nums_list) != 6 or any(n < 1 or n > 45 for n in nums_list) or len(set(nums_list)) != 6:
                st.error("번호 6개를 1~45 범위에서 중복 없이 입력하세요.")
            else:
                new_row = {
                    "draw": int(draw_no_in),
                    "nums": sorted(nums_list),
                    "bonus": int(bonus_in),
                    "date": date_in.strip() or "",
                }
                local = load_local_data()
                if local is None:
                    local = get_builtin_fallback()
                # 중복 제거 후 추가
                local = local[local["draw"] != int(draw_no_in)]
                new_df = pd.DataFrame([new_row])
                combined = pd.concat([new_df, local], ignore_index=True)
                combined = combined.sort_values("draw", ascending=False).reset_index(drop=True)
                if save_local_data(combined):
                    st.success(f"✅ {int(draw_no_in)}회 추가 완료!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("저장 실패")
        except Exception as e:
            st.error(f"입력 오류: {e}")

    st.divider()
    if st.button("🔄 캐시 초기화 및 재조회", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "💡 **동행복권 조회 방법**\n\n"
        "[동행복권 바로가기](https://www.dhlottery.co.kr/gameResult.do?method=byWin)\n\n"
        "최신 회차 번호를 확인 후 좌측 폼에 입력하면 자동 저장됩니다."
    )

# ==============================
# 메인 UI
# ==============================
st.title("🎲 AI 로또 추천 엔진")
st.caption("빠른 조회 / 5게임 생성 / 간단 백테스트 / 최근 데이터 보기")

with st.spinner("데이터 불러오는 중..."):
    # 로컬 파일을 항상 직접 확인 (Streamlit 캐시 우회)
    _local = load_local_data()
    if _local is not None and len(_local) >= 10:
        df = _local
        fallback_used = False
    else:
        df, fallback_used = load_data(100)


if fallback_used:
    st.warning(
        "⚠️ 실시간 조회 불가 — 내장 샘플 데이터로 표시 중입니다.\n\n"
        "**최신 데이터 추가 방법:** 좌측 사이드바에서 실제 당첨번호를 직접 입력하면 이후 자동으로 사용됩니다."
    )
else:
    src = "로컈 저장" if _local is not None else "실시간"
    st.success(f"✅ {src} 데이터 {len(df)}회분 로드 완료")

if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

latest = df.iloc[0]

# 최신 당첨번호 표시
st.subheader(f"🏆 {int(latest['draw'])}회 당첨번호")
nums_display = [int(x) for x in latest["nums"]]
bonus_display = int(latest["bonus"])

cols = st.columns(7)
colors = ["#f7c231","#f7c231","#f7c231","#f03d3d","#f03d3d","#717abb","#aaaaaa"]
labels = [str(n) for n in nums_display] + [f"+{bonus_display}"]
for col, label, color in zip(cols, labels, colors):
    col.markdown(
        f"<div style='text-align:center;background:{color};border-radius:50%;width:40px;"
        f"height:40px;line-height:40px;font-weight:bold;color:white;margin:auto'>{label}</div>",
        unsafe_allow_html=True,
    )
st.caption(f"추첨일: {latest['date']}  |  데이터: {len(df)}회분")

st.divider()

# ==============================
# 패턴 분석 섹션
# ==============================
pat = analyze_patterns(df)

with st.expander(f"🔍 최근 {pat['n']}회 패턴 분석", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("평균 합계", f"{pat['avg_sum']}", f"±{pat['std_sum']}")
    c2.metric("평균 홀수 개수", f"{pat['avg_odd']} / 6")
    c3.metric("분석 회차", f"{pat['n']}회분")

    st.markdown("**🔥 핫 번호 (최근 100회 최다 출현)**")
    hot_str = "  ".join(
        f"<span style='background:#e03131;color:white;border-radius:50%;"
        f"padding:4px 9px;font-weight:bold'>{n}</span>"
        for n in pat["hot"]
    )
    st.markdown(hot_str, unsafe_allow_html=True)

    st.markdown("**🧊 콜드 번호 (최근 100회 최소 출현)**")
    cold_str = "  ".join(
        f"<span style='background:#1971c2;color:white;border-radius:50%;"
        f"padding:4px 9px;font-weight:bold'>{n}</span>"
        for n in pat["cold"]
    )
    st.markdown(cold_str, unsafe_allow_html=True)

    z = pat["avg_zones"]
    st.markdown(
        f"**📊 구간 분포 (최근 20회 평균)** — "
        f"저(1-15): **{z[0]}개** / 중(16-30): **{z[1]}개** / 고(31-45): **{z[2]}개**"
    )

st.divider()

# ==============================
# 번호 생성 버튼
# ==============================
n_games = st.slider(
    "🎟️ 게임 수 선택",
    min_value=1, max_value=10, value=5, step=1,
    format="%d게임 (%d,000원)" if False else "%d게임",
    help="1게임 = 1,000원 / 최대 10게임 = 10,000원"
)
st.caption(f"💰 예상 금액: **{n_games:,}게임 × 1,000원 = {n_games * 1000:,}원**")

col1, col2 = st.columns(2)
if col1.button(f"🎯 번호 생성 ({n_games}게임)", use_container_width=True):
    with st.spinner("패턴 분석 후 번호 생성 중..."):
        games = generate_games(df, n_games)
    st.session_state["games"] = games
    if len(games) < n_games:
        st.warning(f"⚠️ {len(games)}게임만 생성됨 (조건이 너무 좁을 수 있음)")

if col2.button("📊 백테스트 실행", use_container_width=True):
    with st.spinner("백테스트 중..."):
        bt = backtest(df)
    st.session_state["bt"] = bt

# 추천번호 출력
if "games" in st.session_state and st.session_state["games"]:
    n_generated = len(st.session_state["games"])
    st.subheader(f"✨ 추천 번호 {n_generated}게임")
    sum_lo = int(pat["avg_sum"] - pat["std_sum"] * 1.5)
    sum_hi = int(pat["avg_sum"] + pat["std_sum"] * 1.5)
    st.caption(
        f"합계 목표: {sum_lo}~{sum_hi}  |  "
        f"홀수 목표: {round(pat['avg_odd'])}개  |  "
        f"구간(저/중/고): {pat['avg_zones'][0]}/{pat['avg_zones'][1]}/{pat['avg_zones'][2]}"
    )
    for i, g in enumerate(st.session_state["games"], 1):
        clean_g = [int(x) for x in g]
        total = sum(clean_g)
        odd_cnt = sum(n % 2 for n in clean_g)
        ball_str = "  ".join(
            f"<span style='background:#4c6ef5;color:white;border-radius:50%;padding:4px 9px;"
            f"font-weight:bold'>{n}</span>"
            for n in clean_g
        )
        st.markdown(
            f"**게임 {i}:** {ball_str} "
            f"<span style='color:gray;font-size:0.85em'>&nbsp; 합:{total} | 홀:{odd_cnt} 짝:{6-odd_cnt}</span>",
            unsafe_allow_html=True
        )

# 백테스트 결과
if "bt" in st.session_state:
    if st.session_state["bt"] is None:
        st.warning("백테스트 데이터 부족 (최소 30회 필요)")
    else:
        st.metric("📈 평균 최고 일치 수 (15라운드)", f"{st.session_state['bt']} / 6")

st.divider()

# 최근 데이터
with st.expander("📋 최근 당첨 데이터 보기"):
    show = df.copy()
    show["회차"] = show["draw"].apply(int)
    show["당첨번호"] = show["nums"].apply(lambda x: "  ".join(map(str, [int(n) for n in x])))
    show["보너스"] = show["bonus"].apply(lambda x: int(x) if pd.notna(x) else "")
    show["추첨일"] = show["date"]
    st.dataframe(
        show[["회차", "추첨일", "당첨번호", "보너스"]],
        width="stretch",
        hide_index=True,
    )

