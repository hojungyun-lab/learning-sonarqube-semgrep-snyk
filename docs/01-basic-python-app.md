# 🐛 01. 실습용 취약점 애플리케이션 생성 (Vulnerable Python App)

## 📌 학습 목표 (Goal)
- 각종 보안/품질 도구(SonarQube, Semgrep, Snyk)가 탐지할 수 있는 **의도적인 결함**이 포함된 파이썬 웹 애플리케이션 데모를 작성합니다.
- 코드를 작성하며 `보안 취약점(Vulnerability)`, `코드 스멜(Code Smell)`, `오래된 패키지(Outdated Dependency)`의 차이를 이해합니다.

## 💡 핵심 개념 (Core Concepts)

### 핵심 애플리케이션 아키텍처 및 의도적 레거시 패턴 도입
보안 툴의 탐지 성능을 검증하기 위해서는 의도된 취약점(Known Vulnerabilities)이 포함된 코드가 선행되어야 합니다. 결함이 없는 코드에서는 스캐너의 탐지 메커니즘을 가시적으로 확인하기 어렵습니다. 따라서 실무에서 빈번하게 발생하는 보안 결함과 안티패턴을 고의로 배치하여, 각 도구들이 이를 어떻게 식별하고 경고하는지를 단계별로 학습하는 것이 목적입니다.

---

## 🛠 실습 코드 (Hands-on)

앞선 가이드에서 만든 `my-secure-app` 디렉터리 내부에 아래 두 개의 파일을 작성합니다.

### 1-1. 의도적으로 오래된 라이브러리 설치 (`Poetry`)
이 환경은 향후 **Snyk(SCA)**가 스캔하여 이미 세상에 알려진 치명적인 취약점(CVE)을 경고해 줄 타겟이 됩니다.

`my-secure-app` 터미널(poetry shell 진입 상태)에서 아래 명령어로 의도적인 버그가 있는 옛날 버전의 패키지들을 강제 설치합니다.

```bash
# 버퍼 오버플로우나 파서 취약점 등이 내포된 구버전 패키지 3종 설치
poetry add fastapi@0.85.0 uvicorn@0.18.2 requests@2.28.1
```

### 1-2. 취약점 투성이의 서버 코드 작성 (`main.py`)
아래 코드는 **SonarQube(코드 스멜)**와 **Semgrep(보안 취약점)**이 탐지해 낼 타겟입니다.

```python
# 파일명: main.py
from fastapi import FastAPI, Header, HTTPException
import sqlite3
import hashlib

app = FastAPI()

# ⚠️ 치명적 결함 1 (Hardcoded Secret): Github 등에 올라가면 공격자에게 즉각 탈취됨
AWS_SECRET_TOKEN = "AKIA-SUPER-SECRET-DEV-KEY-1234"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vulnerable App"}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    # ⚠️ 치명적 결함 2 (SQL Injection): 외부 입력값(user_id)을 검증 없이 SQL 쿼리에 직접 결합
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    # f-string을 이용한 다이렉트 쿼리. 데이터베이스가 통째로 삭제당할 수 있습니다.
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@app.post("/login")
def login(password: str):
    # ⚠️ 치명적 결함 3 (Weak Hashing): 현대 컴퓨터로 수초 만에 크랙되는 MD5 해시 사용
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    # ⚠️ 코드 스멜 (Cognitive Complexity): 불필요하게 깊은 조건문 중첩 (가독성 저하)
    if password != "":
        if len(password) > 3:
            if hashed == "some_db_hash":
               return {"status": "success"}
            else:
               return {"status": "fail"}
    return {"status": "invalid"}
```

---

## 🚀 마무리 및 다음 단계
코드를 얼핏 보면 그럴싸하게 동작하는 API 서버 같지만, 이 안에는 **인젝션, 하드코딩된 크레덴셜, 취약한 암호화 알고리즘, 복잡한 if중첩(코드 스멜)**이 버무려져 있습니다.

**다음 단계:** `02-sonarqube-concept-and-config.md` 에서는 이 코드를 **SonarQube** 에 밀어 넣어 코드 퀄리티 엔진이 코드를 어떻게 질책(?)하는지 확인해 보겠습니다.
