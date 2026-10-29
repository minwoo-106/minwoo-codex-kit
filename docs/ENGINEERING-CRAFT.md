# 코딩 후보 10개 검수와 편입

2026-10-29. 기존 스킬과 역할을 대조해 새 스킬 7개, 기존 확장 2개, 선택 안내 1개로 반영한다. 설치만으로 모든 구현에 이 절차를 실행하지 않는다.

| 후보 | 편입 | 기존 역할과의 경계 |
| --- | --- | --- |
| 테스트 품질 | minwoo-test-quality 신규 | 속성 기반 입력 생성·TDD·불규칙 실패 원인 분석과 구분 |
| 의존성 업그레이드 | minwoo-dependency-upgrade 신규 | 취약점 조사만 하는 dependency-audit를 실제 버전 이전으로 넓히지 않음 |
| 관측 기능 | minwoo-observability 신규 | 로그·측정·추적 구현. 오류 원인 조사 자체는 diagnosing-bugs |
| 실제 API 계약 | minwoo-api-compat 확장 | 기존 명세 비교 + 실제 소비자/제공자 시험 |
| 불규칙 테스트 실패 | diagnosing-bugs 확장 | 기존 진단 루프에 조건별 참고 문서 추가 |
| 동작 보존 리팩터링 | engineering/refactoring 선택 안내 | 기존 codebase-design·검증·리뷰를 필요에 따라 연결 |
| 백그라운드 작업 | minwoo-async-jobs 신규 | 큐·재시도·중복 부작용·취소의 실행 경계 |
| 상태 흐름 | minwoo-state-flow 신규 | UI/업무 단계·늦은 응답. React 컴포넌트 구조와 구분 |
| 파일/대량 입력 | minwoo-data-ingestion 신규 | 업로드·파싱·부분 적재·재개. 표 분석·DB 검토와 구분 |
| 국제화 | minwoo-i18n 신규 | 앱 리소스·포맷·언어 전환. 일반 번역·말투와 구분 |

web 묶음은 28개, all은 31개다. core/video/documents 묶음은 그대로 유지한다. 개별 스킬 설치도 가능하며 README의 경로·미리보기 안내를 따른다. 공통 AGENTS.md, 승인 방식, 플러그인 연결과 외부 캐시는 설치 범위에 넣지 않는다.

## 공식 자료와 의존성 결정

아래는 구현 기준을 확인한 문서다. 외부 스킬·예제·문장·스크립트를 복제하거나 번역해 배포하지 않고 직접 작성했다. Stryker, Pact, OpenTelemetry, BullMQ, XState, i18next 설치·서비스 연결은 이 kit 설치의 부작용이 아니다. 해당 프로젝트가 필요로 할 때 현재 버전과 기존 도구를 확인해 선택한다.

- [Stryker 변이 종류](https://stryker-mutator.io/docs/mutation-testing-elements/supported-mutators/): 경계·논리 조건의 작은 결함으로 검증력을 확인하되 의미가 같은 변이와 도구 실패를 구분한다.
- [Pact 동작](https://docs.pact.io/getting_started/how_pact_works): 소비자의 기대와 제공자 검증을 구분한다. 로컬 직접 계약 시험을 Pact/Broker 검증으로 표현하지 않는다.
- [OpenTelemetry 신호](https://opentelemetry.io/docs/concepts/signals/): 로그·측정값·추적의 목적을 구분한다. 이번 실전 평가는 로컬 계측으로 제한한다.
- [BullMQ 멱등 작업](https://docs.bullmq.io/patterns/idempotent-jobs): 재시도에 따른 부작용을 고려한다. 단일 DB 내부 원자성과 외부 서비스의 정확히 한 번 처리는 별개다.
- [Playwright 재시도](https://playwright.dev/docs/test-retries): 최초 실패와 재시도 결과를 분리해 해석한다.
- [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/): 잠금 기반 설치를 검증하며 설치 디렉터리 교체의 영향을 고려한다.
- [Stately 전이](https://stately.ai/docs/transitions): 상태·이벤트·전이 개념을 참고하되 특정 버전의 XState API를 스킬에 고정하지 않는다.
- [OWASP 업로드](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html): 파일 이름·형식·크기와 저장 경계를 확인한다. 모든 업로드 방어를 CSV 시험만으로 보장하지 않는다.
- [i18next 복수형](https://www.i18next.com/translation-function/plurals): locale에 맞는 복수형을 적용하며 영어 규칙을 모든 언어에 확장하지 않는다.

기존 diagnosing-bugs의 MIT 고지와 원문을 유지하고 직접 작성한 참고만 추가했다. 기존 외부 codebase-design·tdd·code-review 파일은 변경하지 않았다.

## 검증 범위

[실전 평가](../evals/ENGINEERING.md)와 [검증 기록](VALIDATION.md)에 실제 수행한 범위와 제한을 남긴다. 새 런타임 패키지는 없으며 합성 fixture의 Python 표준 라이브러리·Node/Intl·기존 npm을 사용한다. 공통 도구 묶음의 잠금 파일과 승인 설정은 변경하지 않는다.
