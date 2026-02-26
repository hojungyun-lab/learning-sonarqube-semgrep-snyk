# ⚡ 보안 및 품질 분석 마스터 치트시트 (CHEATSHEET)

이 문서는 실무에서 빈번하게 사용하는 CLI 명령어, 주요 설정 파일 문법 및 스캐닝 설계 패턴을 빠른 참조(Quick Reference) 형태로 요약합니다.

---

## 🔍 SonarQube (코드 품질 및 기술 부채 관리)

코드의 버그, 취약점, **코드 스멜(Code Smell)**을 식별하여 지속적인 코드 품질 관리를 돕는 도구입니다.

### 1-1. 핵심 CLI 명령어
```bash
# 1. 로컬 환경 컴포즈 분산 아키텍처 실행 (PostgreSQL + SonarQube)
# (실무에서는 데이터 영구 보존 및 메모리 확장을 위해 내장 H2 DB 대신 외부 DB 연동이 필수적입니다)
docker compose up -d

# 2. 로컬 코드 디렉토리에서 스캐너(분석기) 실행
# (실행 전 sonar-project.properties 파일이 존재하는 경로에서 구동 필요)
sonar-scanner \
  -Dsonar.projectKey=secure-python-dev \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=<발급받은_서버_토큰값>
```

### 1-2. `sonar-project.properties` 필수 패턴 매핑
```properties
# 프로젝트 고유 식별자 설정 (서버에 매핑되는 기준키)
sonar.projectKey=secure-python-dev
sonar.projectName=Python Security Demo

# 스캔 타겟 소스 디렉토리와 제외(Exclude)할 디렉토리 명시
sonar.sources=src
sonar.exclusions=venv/**, tests/**, **/*.html, **/*.js

# 언어 환경 및 외부 리포트 임포트 패턴
sonar.python.version=3.10
# (옵션) 파이썬 pytest 테스트 커버리지 리포트 파일을 SonarQube에 반영할 때
sonar.python.coverage.reportPaths=coverage.xml
```

---

## 🎯 Semgrep (추상 구문 트리 기반 SAST)

단순 문자열 검색(grep)이나 복잡한 정규표현식의 한계를 넘어선 정적 코드 구조(AST) 패턴 매칭 스캐너입니다.

### 2-1. 핵심 CLI 명령어
```bash
# 1. 외부 레지스트리의 내장 Python 보안 룰셋(ci, p/python)을 활용하여 전체 스캔
semgrep scan --config="p/python"

# 2. 취약점 자동 픽스(Auto-Fix) 기능이 포함된 스캔 실행
semgrep scan --autofix --config="p/python"

# 3. 개발팀 내부적으로 작성한 로컬 YAML 룰(.semgrep.yml) 기준 검사
semgrep scan --config="custom-rule.yaml" ./src
```

### 2-2. 커스텀 룰 작성 문법 패턴 (YAML)
```yaml
# custom-rule.yaml 예시
rules:
  - id: internal-prevent-md5-hashing
    # 탐지 패턴: hashlib.md5 함수 호출 내부에 어떤 인자(...)가 들어가든 매칭
    pattern: hashlib.md5(...)
    message: "경고: md5 해시 알고리즘은 더 이상 안전하지 않습니다. 강력한 hashlib.sha256()을 권장합니다."
    languages:
      - python
    severity: WARNING # 중요도 레벨 (INFO, WARNING, ERROR)
```

---

## 🛡️ Snyk (오픈소스 의존성 취약점 점검 - SCA)

프로젝트 내부의 `requirements.txt` 나 `pyproject.toml`을 스캔하고, 의존(Dependencies) 패키지에 포함된 **알려진 취약점(CVE)**을 탐지 및 제어합니다.

### 3-1. 핵심 CLI 명령어
```bash
# 1. Snyk CLI 인증 브라우저 오픈 (최초 1회 필수)
snyk auth

# 2. 로컬 빌드 환경에서 패키지 스캔
# 주의사항: Python 패키지 스캔 시 Poetry 환경 설치(poetry install)가 선행되어야 간접 의존성(poetry.lock)까지 정밀하게 추적 가능합니다.
snyk test

# 3. 대시보드로 종속성 스냅샷 전송 (브라우저에서 그래프 및 상태 모니터링 관리 시)
snyk monitor

# 4. CI/CD 환경 파이프라인에서 자동화 스크립트로 파싱할 수 있도록 JSON 형태로 내보내기
snyk test --json > snyk_report.json
```

### 3-2. 취약점 조치 패러다임 (Remediation Actions)
1. **업그레이드(Upgrade Workflow):** 가장 이상적인 방법입니다. `snyk test` 결과가 가이드하는 안전한 배포 버전(`Fixed in` 버전)으로 `poetry add` 명령을 통해 상향(Bump)시킵니다.
2. **이슈 면제(Ignore / Exception Handling):** 서드파티 모듈이 즉시 패치할 수 없는 내부 시스템 충돌 이슈가 있거나 방화벽 내부라 공격 벡터가 희박한 경우, 임시로 예외를 등록합니다.
   ```bash
   # id엔 취약점 코드 할당. 30일(expiry) 뒤에 다시 알림 오도록 설정
   snyk ignore --id=SNYK-PYTHON-UVICORN-10522 --expiry=2024-12-31 --reason="내부 어드민 통신망 전용 포트로 익스플로잇 가능성 현저히 낮음"
   ```
