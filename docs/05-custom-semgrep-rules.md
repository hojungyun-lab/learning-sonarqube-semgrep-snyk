# 🧩 05. 커스텀 Semgrep 룰 작성 및 강제화 (Custom Rules)

## 📌 학습 목표 (Goal)
- Semgrep만의 독창적이고 직관적인 패턴 매칭 연산자(`...`, `$X`)를 이해합니다.
- 조직 내부의 비즈니스 로직이나 코딩 컨벤션을 준수하도록 강제하는 커스텀 `.yml` 룰셋을 작성해 봅니다.
- 발견된 코드의 보안 이슈(SQLi, MD5)를 데모 앱 상에서 실제로 수정해 봅니다.

## 💡 핵심 개념 (Core Concepts)

Semgrep의 가장 큰 장점은 "스캐너 규칙을 작성하기 위해 코딩을 배울 필요가 거의 없다"는 것입니다.
자신이 스캔하고 싶은 코드 형태 그대로가 곧 탬플릿 문법이 됩니다.

**핵심 연산자:**
1.  **생략 연산자 (Ellipsis 연산자 `...`)** : "이 안에 인자가 몇 개가 오든, 리스트가 얼마나 길든 상관없이 무시해라" 라는 뜻입니다. (예: `requests.get(...)` 은 GET 내부에 url, headers, params 뭘 던지든 다 잡습니다)
2.  **메타 변수 (Metavariable `$VAR`)** : 캡처링 그룹입니다. 매칭된 값을 임시 변수로 담아두었다가, 에러 메시지를 출력할 때 `$VAR`을 꺼내어 "너, $VAR을 그따위로 썼구나!" 라고 알려줄 때 사용합니다. (무조건 대문자로 적어야 합니다)

---

## 🛠 실습 코드 (Hands-on)

### 1. 커스텀 룰셋 YAML 작성

`my-secure-app` 최상단 경로에 우리 팀만의 보안 강제 정책 파일을 작성합니다.
*(주석 자체가 룰의 핵심 원리를 설명합니다)*

```yaml
# 파일명: custom-rules.yml
rules:
  - id: prevent-raw-sqlite-fstring
    # 파이썬에서 제공하는 내장 언어 모듈 엔진으로 파싱하라는 뜻
    languages:
      - python
    # 탐지 중요도
    severity: ERROR
    # 개발자에게 노출될 경고 메시지 ($DB_QUERY는 아래에서 치환됨)
    message: |
      [보안 위반] SQL Query에 외부 변수를 직접 포매팅하면 안됩니다. 
      파라미터화된 쿼리(Parameterized Query: `execute(query, (id,))`)를 사용하세요.
      탐지된 쿼리 형태: $DB_QUERY
    # 📝 패턴 탐지 시작: pattern-either를 쓰면 복수 개의 탐지 조건을 OR 연산합니다.
    pattern-either:
      - pattern: |
          # 1. execute 내부에서 f-string 혹은 포매팅(%) 기법을 직접 꽂는 행위 차단
          $CURSOR.execute(f"...{$VAR}...", ...)
      - pattern: |
          # 2. 혹은 변수에 담긴 문자열을 execute에 넣을 때 그 변수가 사전에 f-string으로 오염된 경우 (추적)
          $DB_QUERY = f"...{$VAR}..."
          ...
          $CURSOR.execute($DB_QUERY, ...)
```

### 2. 커스텀 룰 강제 적용 스캔

이제 우리가 방금 만든 YAML 파일을 지정하여 데모 앱을 검사해 봅니다.

```bash
semgrep scan --config="custom-rules.yml" ./main.py
```
우리가 `main.py`에 숨겨놓았던 `$DB_QUERY` 치환 SQL 코드가 [보안 위반] 메시지와 함께 붉은 글씨로 노출되는 것을 확인하세요!

---

### 3. (옵션) 취약점 조치 및 수선 (Remediation)
분석기의 능력을 봤으니 이제 코드를 올바른 형태로 고쳐줍니다. `main.py` 파일을 열어 다음 3개의 보안 포인트를 패치합니다.

```python
# 파일명: main.py 수정 (위험 코드 대체)

# 1. 키 삭제 (하드코딩 제거 - 환경변수로 대체 가정)
# AWS_SECRET_TOKEN = "AKIA-..." (삭제 혹은 os.environ 사용)

# 2. SQL 인젝션 패치 (파라미터 바인딩 사용)
@app.get("/users/{user_id}")
def get_user(user_id: str):
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    # f"SELECT .." 대신 ? 플레이스홀더를 사용한 안전한 쿼리
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    # (...생략...)

# 3. MD5 제거 및 SHA256 상향
@app.post("/login")
def login(password: str):
    # (...생략...)
    # hashlib.md5 대신 sha256 체계 적용
    hashed = hashlib.sha256(password.encode()).hexdigest()
    # (...생략...)
```
수정 완료 후 다시 `semgrep scan` 을 돌려보면 **어떠한 에러도 출력되지 않는(통과) 쾌적한 상태**가 됩니다.

---

## 🚀 마무리 및 다음 단계
이로써 우리는 내가 직접 작성한 비즈니스 로직(Internal Code) 안에 존재하는 냄새나는 코드(SonarQube)와 위험한 보안 구문(Semgrep)을 철벽 방어하는 법을 배웠습니다.

하지만 우리가 import 한 `FastAPI`, `uvicorn` 패키지 자체 깊숙이 존재하는 해커들의 백도어나 알려진 취약점(CVE)은 어떻게 막을까요?
내가 짠 코드가 아니라 외부에서 수입한 장비를 의심해야 합니다. 
**다음 단계:** `06-snyk-auth-and-scanning.md` 에서는 **SCA(Software Composition Analysis)의 강자 Snyk** 의 세계로 넘어갑니다.
