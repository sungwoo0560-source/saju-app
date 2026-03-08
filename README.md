# 만세력 사주 엔진 (개인 사용·홍보용)

로컬 만세력·격국·용신·대운 기반 사주 풀이 웹 앱입니다.  
**개인 사용·홍보용**이며, 모바일에서도 사용할 수 있도록 맞춰 두었습니다.  
정식 출시용 앱은 별도 버전으로 제작합니다.

---

## 1. 로컬에서 실행

```bash
# 가상환경 권장
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
streamlit run manse.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.  
Windows에서는 프로젝트 폴더에서 **`run.bat`** 더블클릭으로도 실행할 수 있습니다.

---

## 2. GitHub 올린 뒤 Streamlit Cloud로 실행 (나만 사용)

**모바일·PC 어디서나** 같은 앱을 쓰려면 GitHub에 올린 뒤 Streamlit Community Cloud에서 실행하면 됩니다.

### 2-1. GitHub에 저장소 만들고 푸시

1. GitHub에서 새 저장소(Repository) 생성 (이름 예: `manse-saju`)
2. 아래 파일들이 **저장소 루트**에 있도록 푸시:
   - `manse.py`
   - `requirements.txt`
   - `.streamlit/config.toml` (선택, 없으면 기본 설정 사용)
3. (선택) 나만 쓰려면 저장소를 **Private**으로 두고, Streamlit Cloud 연결 시 GitHub 권한에서 해당 저장소만 허용

### 2-2. Streamlit Cloud에서 앱 실행

1. **https://share.streamlit.io** 접속 후 로그인 (GitHub 계정 연동)
2. **"New app"** 클릭
3. 설정:
   - **Repository**: `본인아이디/manse-saju` (또는 사용하는 저장소)
   - **Branch**: `main` (또는 사용 중인 기본 브랜치)
   - **Main file path**: `manse.py`
4. **"Deploy!"** 클릭 → 수 분 안에 `https://xxxxx.streamlit.app` 형태의 주소가 생성됨
5. 해당 주소를 **모바일 브라우저·PC**에서 열면 동일한 앱 사용 가능

### 2-3. 수정 후 반영

- GitHub에 `manse.py` 등 수정본을 **push**하면, Streamlit Cloud가 자동으로 다시 배포합니다 (몇 분 소요).

### 참고

- Streamlit Community Cloud 무료 플랜은 **공개(Public) 앱**이 기본입니다. 나만 쓰려면 브라우저에서 해당 URL을 다른 사람에게 공유하지 않거나, 저장소를 Private으로 두고 배포하는 방식으로 사용하면 됩니다.
- 비밀번호 등 추가 보안이 필요하면 Streamlit Cloud 설정이나 별도 인증 방식을 검토하면 됩니다.

---

## 주요 기능

- **양력/음력** 생년월일 입력 (윤달 지원)
- **종합운세, 대운, 과거/미래, 일·월·년 운세, 재물·궁합·직장·건강**
- **만신 상담소** (로컬 엔진 기반 상담)
- **비방록, 12운성, PDF 출력**
- AI API 없이 **로컬 엔진 전용** 동작
- **모바일** 레이아웃·터치에 맞춘 스타일 적용

---

## 환경

- Python 3.10+
- Streamlit, reportlab, korean-lunar-calendar

---

## 라이선스·면책

전통 민속 문화 참고용이며, 상업·출시용은 별도 앱 버전에서 진행합니다.
