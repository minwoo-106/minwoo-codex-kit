# 개발과 검사 선택

일반 코드 수정에는 기존 프로젝트 규칙·코드·테스트부터 확인한다. 아래 모든 절차가 기본 필수 단계인 것은 아니다.

| 문제·결과물 | 먼저 선택 | 다른 역할과의 경계 |
| --- | --- | --- |
| 실패·오류·느려짐의 원인 조사, CI 실패 | diagnosing-bugs | CI라면 포함된 GitHub Actions 참고. 재실행만 반복하지 않음 |
| 테스트부터 기능·버그 구현 | tdd | 사용자가 테스트 우선 흐름을 요청했을 때. 모든 수정의 의무 아님 |
| 파서·정규화·계산의 불변식·왕복 관계 | minwoo-property-testing | 예제 테스트로 충분하면 생략 |
| 정해진 변경 범위 코드 리뷰 | code-review | 변경 설명 화면이나 릴리스 노트와 구분 |
| 모듈 경계·인터페이스 설계 | codebase-design | 작은 수정에 전면 구조 설계를 추가하지 않음 |
| 도메인 용어·CONTEXT.md·ADR | domain-modeling | 전역 규칙이나 작업 인수인계와 구분 |
| 불확실한 설계 질문을 임시 구현으로 확인 | prototype | 실제 제품 구현 완료라고 보고하지 않음 |
| 계획·결정의 약점 질문으로 검토 | grilling | 명시적인 검증·질문 요청에 사용; 일반 작업을 반복 승인 질문으로 바꾸지 않음 |
| React 로딩·재렌더·번들 지연 | minwoo-react-performance | 시각 디자인과 구분하고 측정 근거 확보 |
| React 옵션 난립·컴포넌트 API·상태 공유 | minwoo-react-composition | 성능 도구를 자동 병행하지 않음 |
| API 요청·응답 변경의 소비자 호환성 | minwoo-api-compat | 일반 API 구현·호출에는 자동 적용하지 않음 |
| PostgreSQL·Supabase 쿼리·RLS·스키마·변경 연습 | minwoo-postgres-review | 격리 연습을 운영 DB 변경 권한으로 해석하지 않음 |
| 패키지 취약점·유지보수·공급망 조사 | minwoo-dependency-audit | 앱 전체 보안 감사나 모든 설치의 필수 절차가 아님 |
| 버튼·검색·폼의 브라우저 회귀 | minwoo-browser-check | UI 미적 평가와 구분 |
| 변경을 따라 읽는 HTML 설명 화면 | minwoo-diff-walkthrough | 코드 리뷰를 대체하지 않음 |

GitHub 연결 도구는 저장소·PR·CI의 실제 증거와 승인된 반영을 맡는다. 진단 스킬은 조사 절차를 맡는다. 일반 Git 작업은 현재 제공된 도구 또는 저장소 CLI를 사용하며 새 Git 전용 스킬을 만들 필요는 없다.
관리형 클라우드 실행 환경에서만 cloud-environment:cloud-environment-runtime을 적용한다. 로컬 Windows 작업에 클라우드 전용 초기화를 강제하지 않는다.
