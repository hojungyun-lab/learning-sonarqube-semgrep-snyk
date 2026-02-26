# 🚧 09. Quality Gate 설정 및 Build Breaker (Enforcement)

## 📌 학습 목표 (Goal)
- 보안 경고를 무시하고 배포(Merge)되는 사태를 막기 위한 **Quality Gate(품질 관문)**의 개념을 정의합니다.
- 각 도구(SonarQube, Semgrep, Snyk)에서 조건에 미달할 경우 파이프라인(Build)을 고의로 실패(Break)시키는 방법을 배웁니다.
- GitHub 레포지토리의 `Branch Protection Rule(브랜치 보호 규칙)`을 연동하여 완벽한 방어선을 구축합니다.

## 💡 핵심 딥다이브 (Deep-Dive)

### 1. Build Breaker (빌드 차단기)의 철학
'보안 도구가 찾아낸 에러'를 화면에 예쁘게 띄워주는 것만으로는 부족합니다. 바쁘거나 모르는 개발자는 경고 스티커가 붙어있어도 `Merge Pull Request` 버튼을 눌러버리기 때문입니다.

**Quality Gate**는 "코드 커버리지가 80% 미만이거나, Critical 취약점이 단 1개라도 있으면 이 PR은 절대 합칠 수 없다"는 강제 계약입니다. 조건을 만족하지 못하면 CI 파이프라인 단계를 강제로 `Failed (빨간색 ❌)` 상태로 종료시켜버립니다. 이것을 **Build Breaker** 라고 부릅니다.

### 2. 도구별 Quality Gate 강제(Enforcement) 전략

**① SonarQube (Quality Gate)**
*   **어디서 설정하나요?** SonarQube 서버 UI 대시보드 (Global Quality Gates 메뉴).
*   **작동 방식:** 스캐너가 분석을 쏘면 서버가 계산 후 "이 코드는 실패(Failed)야" 라는 상태값을 반환합니다. GitHub Action 플러그인은 이 Failed 응답을 받으면 자신의 Step 스크립트를 `exit 1` (에러 종료)로 끊어버립니다.

**② Semgrep (설정 파일 기반 엄격 모드)**
*   **어디서 설정하나요?** `.semgrep.yml` 의 `severity` 혹은 CLI 커맨드 플래그 라인.
*   **작동 방식:** 우리가 작성한 룰 혹은 커뮤니티 룰에 매칭되는 위반 사항이 1건이라도 나올 경우, Semgrep CLI 프로세스 자체가 `exit code 1`을 뿜어 강제 중단시킵니다. (오류가 없으면 `exit 0`).

**③ Snyk (Severity Threshold 설정)**
*   **어디서 설정하나요?** GitHub Actions 워크플로우 `.yml` 내부 명령어 옵션.
*   **작동 방식:** `snyk test --severity-threshold=high` 라고 선언해주면, Low 나 Medium 취약점은 봐주지만, High 등급 이상 1건만 발견돼도 프로세스가 터지도록 유연하게 설계할 수 있습니다.

---

## 🛠 실습 가이드 (Hands-on) : GitHub 강제 차단 설정

이 파이프라인의 에러가 곧바로 "개발자의 합병 차단"으로 이어지기 위해선 GitHub Repository 설정이 수반되어야 합니다.

### Step 1: Branch Protection Rules (브랜치 보호 규칙) 설정
1.  작업 중인 GitHub Repository 웹의 **[Settings]** -> 좌측 **[Branches]** 로 이동.
2.  `Add branch protection rule` 버튼 클릭.
3.  `Branch name pattern` 에 **main** 입력.
4.  **[v] Require status checks to pass before merging** 체크! (핵심)
5.  검색창에 아까 작성한 파이프라인의 Job 이름인 `Semgrep SAST Scanning` 등을 검색하여 필수로 통과해야 할 관문으로 등록합니다.

### Step 2: Snyk에 엄격한 기준 적용 (YAML 수정)
08단계에서 만든 파이프라인 파일을 살짝 고쳐 "High" 등급 이상만 빌드를 터트리도록 제어합니다.

```yaml
# .github/workflows/devsecops-pipeline.yml 중 snyk 파트 발췌
      - name: Snyk 오픈소스 테스트 (High 이상 발견 시 멈춤!)
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          # 명령어를 test -> test --severity-threshold=high 로 확장
          args: --severity-threshold=high
```

---

## 🎉 최종 에필로그 (Epilogue)

축하합니다! 빈 폴더에서 시작하여 다음을 달성해 내었습니다.
1.  **SonarQube**를 통한 코드 리팩터링 및 부채 관리 체계 구축
2.  **Semgrep AST** 기반의 내부 컨벤션(커스텀 룰) 및 보안 취약 코드 통제
3.  **Snyk SCA**를 통한 썩은 사과(외부 라이브러리) 반입 금지
4.  **GitHub Actions**를 통한 3종 검사기 자동화 및 Quality Gate 타격 체계 완료

이 시스템 위에서 개발되는 애플리케이션은, 사람(코드 리뷰어)이 미처 잡아내지 못한 실수조차도 기계가 완벽하게 방어해 내는 진정한 의미의 **DevSecOps** 모던 플레이그라운드가 되었습니다.
