# 🧹 03. 코드 스멜 제거 및 기술 부채 상환 (Fixing Code Smells)

## 📌 학습 목표 (Goal)
- SonarQube가 찾아낸 `인지적 복잡도(Cognitive Complexity)`의 개념을 이해하고 코드 스멜(Code Smell)이 왜 위험한지 파악합니다.
- 복잡한 if 중첩 코드를 Early Return(조기 반환) 패턴으로 리팩터링하여 기술 부채(Technical Debt)를 상환해 봅니다.

## 💡 핵심 개념 (Core Concepts)

### 1. 코드 스멜(Code Smell)과 기술 부채(Technical Debt) 란?
*   **코드 스멜:** 당장 버그를 일으키지는 않지만, 나중에 버그를 유발할 수 있는 구조적 문제나 가독성 저하 요인입니다 (예: 너무 긴 메서드, 중복된 코드, 마법의 숫자 사용 등).
*   **기술 부채:** 지름길을 택해 코드를 대충 짰을 때 발생하는 비용입니다. 단기적으로는 일정이 빠를 수 있지만, 장기적으로는 이자(유지보수 시간 증가)를 눈덩이처럼 갚아야 하는 빚입니다. 분석기는 이 빚을 "2시간 분량의 기술 부채" 처럼 시간 단위로 산정해 줍니다.

### 2. 인지적 복잡도 (Cognitive Complexity) vs 순환 복잡도 (Cyclomatic Complexity)
*   과거의 분석기는 순환 복잡도(코드의 분기 경로 수)만 쟀으나, SonarQube는 사람이 코드를 읽을 때의 난해함인 **인지적 복잡도**를 측정합니다.
*   **대표적인 원인:** `if` 문, `for` 문, `while` 문 등의 중첩(Nesting)이 깊어질수록 점수가 기하급수적으로 올라가며 경고를 뱉습니다.

---

## 🛠 실습 코드 (Hands-on) : 리팩터링

앞서 작성한 `main.py`의 로그인 라우터에는 깊은 중첩 구조가 존재합니다.

```python
# [AS-IS] 인지적 복잡도가 높은 악취가 나는 코드
@app.post("/login")
def login(password: str):
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    if password != "":         # 1 depth
        if len(password) > 3:  # 2 depth
            if hashed == "some_db_hash": # 3 depth
               return {"status": "success"}
            else:
               return {"status": "fail"}
    return {"status": "invalid"}
```

이 코드를 `Guard Clauses (보호 구문)` 와 `Early Return (조기 반환)` 원칙을 사용하여 리팩터링해 보겠습니다. `main.py` 파일을 열고 아래와 같이 수정하세요.

```python
# [TO-BE] 리팩터링: 인지적 복잡도 해소 (Early Return 패턴 도입)
@app.post("/login")
def login(password: str):
    # 1. 예외 조건(Guard Clause)을 먼저 걸러내어 즉시 반환(실패 시나리오)
    if not password or len(password) <= 3:
        return {"status": "invalid"}

    # 2. 핵심 로직 실행 (더 이상 깊은 들여쓰기가 필요 없음)
    hashed = hashlib.md5(password.encode()).hexdigest()
    
    if hashed != "some_db_hash":
        return {"status": "fail"}
        
    # 3. 모든 관문을 통과한 성공 시나리오
    return {"status": "success"}
```

### 다시 스캐너를 돌려봅시다
수정 후 저장한 뒤, 이전 02 단계의 [로컬 스캐너 실행] 명령어를 다시 한 번 터미널에서 구동합니다.

대시보드를 새로고침 해보면, 인지적 복잡도와 관련된 **Code Smell 하나가 제거되었고, 기술 부채 탕감(Debt -5 min 등)이 반영**된 짜릿한 기분을 느낄 수 있습니다.

---

## 🚀 마무리 및 다음 단계
SonarQube는 이처럼 코드의 안티 패턴을 교정하는 데 특화되어 있지만, 우리가 일부러 남겨둔 최악의 보안 결함(MD5 사용, SQL 인젝션, 키 탈취 등)을 촘촘하게 막는 보안 전문 분석에는 약간의 한계(유료 Taint 기능 부재 등)가 존재합니다.

**다음 단계:** `04-semgrep-intro-and-rules.md` 에서는 이 부족함을 메워줄 강력하고 빠른 SAST 엔진, **Semgrep**의 추상 구문 트리 세계관으로 들어가 보겠습니다.
