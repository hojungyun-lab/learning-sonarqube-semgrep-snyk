# 🚀 00. 개발 및 분석 환경 구축 세팅 가이드 (Environment Setup)

## 📌 학습 목표 (Goal)
- 코드 품질 검사를 위한 SonarQube 로컬 관제망을 활성화합니다.
- 지속적 보안 스캐닝을 위한 Semgrep과 Snyk CLI(명령줄 도구)를 설치하고 초기 인증 메커니즘을 구성합니다.

## 💡 핵심 개념 (Core Concepts)
왜 이 도구들을 로컬에 직접 설치하고 환경을 갖추어야 할까요?

1. **Shift-Left 패러다임:** 코드를 커밋하고 배포 서버 엔진에서 에러를 확인하는 것보다(Shift-Right), 로컬 터미널 관점에서 코드를 작성하는 단계에서 잠재적 오류를 먼저 차단(Shift-Left)하는 것이 비용과 업무 스트레스를 압도적으로 덜어줍니다.
2. **도구들의 역할 분담:**
   - `SonarQube` : 코드 내 불필요한 복잡성(스멜)과 구조적 결함을 서버 대시보드로 가시화하는 "정적 품질 분석 서버"
   - `Semgrep` : 복잡한 인프라 구축 없이 로컬 CLI로 빠르고 가볍게 "개발 규칙(Rule)"을 강제하는 스캐너
   - `Snyk` : 개발자가 짠 로직 밖 영역, 즉 "외부에서 가져다 쓰는(Import)" 의존성(라이브러리 패키지)이 가진 전세계에 알려진 치명적 취약점을 찾고 패치를 권고해주는 백신

---

## 🛠 실습 코드 (Hands-on)

### Step 1: 분석 대상이 될 Python 실습 환경 폴더 구성
보안 결함을 테스트할 `my-secure-app` 이라는 작업 디렉터리를 만들고, **Poetry**를 활용하여 프로젝트 패키징 환경을 초기화합니다. (FastAPI 프레임워크 기반을 기준으로 진행합니다)

```bash
mkdir my-secure-app && cd my-secure-app

# 1. Poetry 프로젝트 초기화 (대화형 프롬프트 스킵)
poetry init -n

# 2. 가상 환경 활성화 (환경 진입)
poetry shell

# ※ 터미널 좌측에 (my-secure-app-py3.XX) 등의 가상환경 이름이 표시되면 성공입니다.
```

### Step 2: SonarQube 및 PostgreSQL 구동 (Docker Compose 사용)
SonarQube는 설치 시 기본적으로 내장 평가용 데이터베이스(H2)를 사용합니다. 하지만 **내장 DB는 데이터가 영구 보존되지 않고 플러그인 업그레이드나 확장이 불가능하여 실무에서는 반드시 외부 DB(PostgreSQL 등)와 연동**해야 합니다.

이를 위해 안전하게 데이터를 적재할 PostgreSQL과 SonarQube를 동시에 띄우고 내부망으로 통신시키는 `docker-compose.yml` 방식을 사용합니다.
프로젝트 최상단 폴더에 준비된 `docker-compose.yml`을 활용하여 터미널에서 다음 명령어를 실행하세요.

```bash
# 백그라운드(-d)로 SonarQube 10 엔진과 PostgreSQL 15 데이터베이스 컨테이너를 동시 실행
docker compose up -d
```

> 💡 **심화 학습 (아키텍처):** `docker-compose.yml` 내부를 열어보세요. `SONAR_JDBC_URL=jdbc:postgresql://postgres:5432/sonarqube` 환경변수를 통해 SonarQube가 H2 DB를 버리고 PostgreSQL 컨테이너를 바라보도록 지시하는 실무 표준 아키텍처 구조를 확인할 수 있습니다.

> ⚠️ 도커 구동 후 SonarQube 엔진과 DB가 연동 및 부팅되기까지 약 1~2분 정도 소요될 수 있습니다. 브라우저에서 `http://localhost:9000` 에 접속하여 **초기 로그인 패스워드 (`admin` / `admin`)** 입력 창이 나오는지 확인합니다.

### Step 3: Mac/Linux 환경에 Semgrep 설치
Semgrep은 Python 코드로 작성된 프로젝트이므로 Poetry, pip 혹은 Homebrew를 통해 가볍게 설치됩니다.

```bash
# 권장 설치법 (가상 환경 내부 혹은 전역)
poetry add semgrep --group dev

# 버전 확인하여 설치 정상화 파악
semgrep --version
```

### Step 4: NPM을 통해 Snyk CLI 설치 및 인증
Snyk은 Node.js 기반 CLI로 배포되므로 npm을 사용합니다. 외부 데이터베이스 정보를 계속 업데이트받아야 하므로 보안 인증 과정(OAuth)이 수반됩니다.

```bash
# 1. 전역 설치
npm install -g snyk

# 2. 콘솔 인증 진행 (실행 시 자동으로 웹 브라우저가 열리고 계정 연동 승인)
snyk auth

# ※ 브라우저 창에서 "Snyk CLI is now authenticated." 문구가 나오면 성공
```

---

## 🚀 마무리 및 다음 단계
이제 내 컴퓨터가 단순한 작성 편집 도구를 넘어, 엔터프라이즈 수준의 코드 보안 관측기가 될 준비가 끝났습니다.

**다음 단계:** `01-basic-python-app.md` 에서는 일부러 보안 허점이 있는 간단한 파이썬 프레임워크 애플리케이션 코드를 작성하여 위 도구들의 감시망에 코드를 내던져 보겠습니다.
