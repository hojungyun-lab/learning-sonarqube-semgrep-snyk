# 🛡️ 오픈소스 기반 Python 보안 및 품질 관리 시스템 구축

이 가이드는 **SonarQube Community, Semgrep, Snyk Open Source**를 통합하여 파이썬(Python) 프로젝트의 코드 품질 향상과 보안 취약점 조치를 자동화하는 엔드투엔드(End-to-End) 학습 레포지토리입니다.

## 🎯 프로젝트 개요

실무에서 정적 애플리케이션 보안 테스트(SAST) 및 소프트웨어 구성 분석(SCA) 도구를 언제, 어떻게, 왜 사용해야 하는지 배우는 것을 목표로 설계되었습니다.

### 🛡️ 3대 핵심 보안 도구 (어디에, 왜 사용하는가?)

| 도구 스택 | 분석 영역 | 주요 타겟 및 사용처 (Where) | 도입 목적 (Why) |
|---|---|---|---|
| **SonarQube** | **코드 퀄리티 관리** <br/>(Code Quality & Smell) | **내가 직접 작성한 소스 코드**<br/>(주로 중앙 CI 서버 및 대시보드 연동) | 당장 에러를 유발하지는 않지만 애플리케이션 유지보수를 어렵게 만드는 **코드 스멜(인지적 복잡도, 중복 코드 등)**을 식별하고, 장기적인 **기술 부채(Technical Debt)**를 체계적으로 관리하기 위해 도입합니다. |
| **Semgrep** | **정적 보안 테스트** <br/>(SAST) | **내가 직접 작성한 소스 코드**<br/>(개발자 로컬 PC 및 PR 즉각 리뷰) | 개발자가 무심코 작성한 SQL 인젝션 유발 구문, 하드코딩된 비밀번호 등 **명시적인 보안 결함**을 발견하거나, 팀 내부의 **코딩 컨벤션 규칙을 강력하게 강제화**할 때 사용합니다. 엄청나게 빠릅니다. |
| **Snyk** | **소프트웨어 구성 분석** <br/>(SCA) | **내가 밖에서 가져다 쓴 코드**<br/>(`pyproject.toml`, `poetry.lock` 의존성 트리) | 내가 짠 코드가 아니라 외부에서 수입한 오픈소스 라이브러리(서드파티)에 이미 존재하는 **알려진 해킹 취약점(CVE)**을 색출하고, 안전한 버전으로의 업그레이드를 가이드받기 위해 사용합니다. |

* **학습을 통해 얻을 수 있는 역량**
  * 보안 전문가나 인프라 엔지니어가 아니더라도 로컬과 CI 환경에서 보안 및 품질 검사를 자동화할 수 있습니다.
  * 각각의 특징이 완벽히 다른 3가지 툴의 **역할(Role)**을 이해하고, 내 프로젝트의 사각지대(Blind Spot)를 없앨 수 있습니다.

## 📂 프로젝트 구조

```text
.
├── README.md             // 프로젝트 소개, 시작 가이드, 전체 학습 목차 플래너
├── CHEATSHEET.md         // 핵심 문법 및 룰 패턴 위주의 빠른 참조 요약 카드
├── docs/                 // 단계별 학습 마크다운 문서들
│   ├── 00-environment-setup.md
│   ├── 01-basic-python-app.md
│   ├── 02-sonarqube-concept-and-config.md
│   ├── ... (총 10개 내외의 단계)
├── examples/             // 학습자가 참고할 수 있는 완성본 데모 코드
│   ├── basic-app/        // 기초 단계 실습용 의도적 취약점 코드 (FastAPI 기반)
│   └── final-project/    // 품질 분석 조치가 완료되고 CI 파이프라인이 통합된 앱
```

## 🚀 시작하기

학습을 위해 필수적인 로컬 환경을 검증하고, 기본 뼈대 코드를 구성합니다.

### 1. 필수 의존성 확인
터미널을 열고 본인의 운영체제(macOS 등) 환경에 다음 커맨드라인 도구들이 설치되어 있는지 확인하세요.

```bash
# Python 최신 구동 환경 확인 (3.10 이상 권장)
python3 --version

# Docker 엔진 구동 확인 (SonarQube 분석 서버용 가상 컨테이너)
docker info

# Git 플로우 버전 확인
git --version
```

### 2. 빈 실습 프로젝트 생성
학습자가 직접 코드를 작성해볼 로컬 스페이스를 준비합니다. 아래 명령어로 초기 구성을 진행합니다.

```bash
# 실습 디렉터리 생성 후 진입
mkdir -p my-secure-app && cd my-secure-app

# 최신 의존성 관리 및 가상환경 구동을 위한 Poetry 프로젝트 초기화
poetry init -n
poetry shell
```

### 3. 최종 데모 앱 엿보기 (선택 사항)
학습이 끝난 후 완성될 형태를 `examples/final-project` 폴더에서 미리 구동해 볼 수 있습니다.

```bash
# 데모 폴더로 이동 (레포지토리 클론 완료 가정)
cd examples/final-project

# Poetry를 통한 의존성 패키지 설치
poetry install

# 로컬 개발 서버 구동 (FastAPI)
poetry run uvicorn main:app --reload

# 웹 브라우저 접속 후 확인 (기본 포트: 8000)
```

## 📚 학습 목차 (커리큘럼)

본 과정은 도구별 핵심 철학에 맞춰 5개의 파트로 구성됩니다.

| # | 범주 (Category) | 주제 (문서 파일명) | 핵심 내용 (Core Focus) |
|---|---|---|---|
| **00** | **환경 준비** | [로컬 개발 및 분석 환경 구축](docs/00-environment-setup.md) | Docker를 이용한 SonarQube 구동, Semgrep/Snyk CLI 전역 설치를 통한 로컬 인프라 세팅. |
| **01** | **환경 준비** | [실습용 취약점 애플리케이션 생성](docs/01-basic-python-app.md) | FastAPI를 이용해 의도적으로 SQL Injection, 밋밋한 예외처리 코드를 가진 데모 앱 작성. |
| **02** | **코드 품질** | [SonarQube 스캐너 연동 및 분석](docs/02-sonarqube-concept-and-config.md) | `sonar-project.properties` 스캔 정책 작성, Scanner 아키텍처 이해, 정적 트래픽 전송. |
| **03** | **코드 품질** | [Technical Debt 및 Code Smell 조치](docs/03-fixing-code-smells.md) | 인지적 복잡도(Cognitive Complexity) 하향화 리팩터링 및 기술 부채를 통제하는 전략 확보. |
| **04** | **SAST 기초** | [Semgrep 개요 및 기본 룰셋 구동](docs/04-semgrep-intro-and-rules.md) | 추상 구문 트리(AST) 이해. 정규표현식을 넘어서는 내장 보안 룰셋(`p/python`) 적용. |
| **05** | **SAST 고급** | [커스텀 Semgrep 룰 작성 및 강제화](docs/05-custom-semgrep-rules.md) | YAML 기반 사내 컨벤션 작성 (`pattern-either`, `metavariable`을 활용한 복합 룰 적용). |
| **06** | **SCA 제어** | [Snyk Open Source 의존성 진단](docs/06-snyk-auth-and-scanning.md) | 서드파티 패키지 의존성 다이어그램 모니터링, 간접 의존성(Transitive Dependency) 체크. |
| **07** | **SCA 제어** | [알려진 취약점(CVE) 패치 및 완화](docs/07-remediating-vulnerabilities.md) | CVSS 스코어 기반 치명도 해석. 버전 업그레이드 조치 및 `.snyk` 무시 정책(Ignore) 작성법. |
| **08** | **오토메이션** | [GitHub Actions DevSecOps 적용](docs/08-github-actions-pipeline.md) | CI 파이프라인(Workflow `.yaml`)에 스캐너 플러그인 통합, Pull Request 분석 이벤트 바인딩. |
| **09** | **오토메이션** | [Quality Gate 설정 및 Build Breaker](docs/09-quality-gate-enforcement.md) | 품질 미달 시 머지(Merge)를 원천 차단하는 Policy 설정 전략 및 빌드 실패 핸들링. |

## 📋 빠른 참조 (Quick Reference)

명령어나 룰셋 문법을 잊어버렸을 때 언제든 꺼내볼 수 있는 핵심 시트입니다.
👉 [CHEATSHEET.md 바로 가기](CHEATSHEET.md)
