# 개발·데이터 도구 참고 후보

검토일: 2026-11-02. 상태: **공식 자료·출처 검토 완료 / 실제 설치·실행 검증 전**.
도구 이름은 설치·MCP 연결·사용 권한의 증거가 아니다. 새 자동 발동 스킬은 만들지 않는다. 아래 해당 후보의 절만 필요한 때 참고한다.

| 후보 | 용도 | 연결 방식 |
| --- | --- | --- |
| [ast-grep](#ast-grep) | 문법 구조로 같은 형태의 코드를 찾아 제한된 범위를 수정한다. | 기존 코드 검색·리팩터링 안내의 선택 실행 도구 |
| [Knip](#knip) | JS/TS의 사용하지 않는 파일·exports·의존성을 조사한다. | 기존 정리·리팩터링 안내 확장; 취약점 감사와 역할 구분 |
| [dependency-cruiser](#dependency-cruiser) | JS/TS 파일 의존 관계와 순환 참조·레이어 규칙을 조사한다. | codebase-design의 모듈 경계 검토를 보조 |
| [Hyperfine](#hyperfine) | 명령을 반복 실행해 처리 시간과 분산을 비교한다. | diagnosing-bugs·성능 개선의 측정 보조 |
| [Bruno](#bruno) | API 요청·테스트 모음을 로컬 파일과 Git으로 관리하고 CLI로 재실행한다. | 기존 HTTP 도구의 보완; minwoo-api-compat은 계약 변경 검토가 필요할 때만 |
| [Datasette](#datasette) | SQLite 데이터를 검색·필터·SQL/API로 탐색하는 자료실을 만든다. | 독립 참고 후보; 표 산출물·대량 적재 구현·PostgreSQL 검토와 구분 |

## ast-grep

- 출처: [공식 저장소](https://github.com/ast-grep/ast-grep), [확인 README](https://github.com/ast-grep/ast-grep/blob/5a204b1ef3facef94de125d990dddc7cf90011c0/README.md). 확인 커밋 `5a204b1ef3facef94de125d990dddc7cf90011c0` (2026-11-02). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 기존 코드 검색·리팩터링 안내의 선택 실행 도구.
- 실행 조건: 언어별 파서·패턴과 해당 플랫폼의 CLI 배포를 확인한다. 문자열 검색은 기존 rg를 우선한다.
- 사용 전 검증: 읽기 전용 검색 결과를 먼저 검토하고 작은 사본에서 치환·diff·회귀 검사를 한다. 패턴 일치만으로 의미·타입 호환성이 보장되지는 않는다.
- 라이선스: MIT. 원문 확인: [LICENSE](https://github.com/ast-grep/ast-grep/blob/5a204b1ef3facef94de125d990dddc7cf90011c0/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## Knip

- 출처: [공식 저장소](https://github.com/webpro-nl/knip), [확인 README](https://github.com/webpro-nl/knip/blob/da07b6e9887f9a1eb08545da29755b7f9d309bca/README.md). 확인 커밋 `da07b6e9887f9a1eb08545da29755b7f9d309bca` (2026-10-31). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 기존 정리·리팩터링 안내 확장; 취약점 감사와 역할 구분.
- 실행 조건: 프로젝트 Node 버전·진입점·프레임워크·모노레포 설정을 확인한다. CLI로 충분하면 별도 MCP를 등록하지 않는다.
- 사용 전 검증: 진입점·동적 로딩·플러그인 때문에 생길 수 있는 오탐을 검토한다. 보고서만 먼저 만들고 삭제·자동 수정은 요청 범위에서 회귀 검사 후 수행한다.
- 라이선스: ISC. 원문 확인: [LICENSE](https://github.com/webpro-nl/knip/blob/da07b6e9887f9a1eb08545da29755b7f9d309bca/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## dependency-cruiser

- 출처: [공식 저장소](https://github.com/sverweij/dependency-cruiser), [확인 README](https://github.com/sverweij/dependency-cruiser/blob/5173200de662c89c6ed0fd687e9a62aedaf792a0/README.md). 확인 커밋 `5173200de662c89c6ed0fd687e9a62aedaf792a0` (2026-11-01). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: codebase-design의 모듈 경계 검토를 보조.
- 실행 조건: Node·프로젝트 설정이 필요하다. 시각화 형식에 따라 Graphviz 등 별도 도구가 필요할 수 있다.
- 사용 전 검증: 작은 모듈 묶음의 그래프를 코드와 대조한다. 타입 전용·동적 참조 설정과 허용된 의존 규칙을 확인하며 검사 결과만으로 구조 전체를 변경하지 않는다.
- 라이선스: MIT. 원문 확인: [LICENSE](https://github.com/sverweij/dependency-cruiser/blob/5173200de662c89c6ed0fd687e9a62aedaf792a0/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## Hyperfine

- 출처: [공식 저장소](https://github.com/sharkdp/hyperfine), [확인 README](https://github.com/sharkdp/hyperfine/blob/c5161524980522320c7d3425e714cc0965a869a5/README.md). 확인 커밋 `c5161524980522320c7d3425e714cc0965a869a5` (2026-10-12). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: diagnosing-bugs·성능 개선의 측정 보조.
- 실행 조건: 플랫폼별 실행 파일·셸 해석과 측정 지표 지원 범위를 확인한다. 모든 플랫폼이 모든 하드웨어 지표를 지원하지 않는다.
- 사용 전 검증: 같은 입력·출력·캐시 조건에서 비교한다. 반복 실행의 부작용이 없는 명령으로 먼저 시험하며 생성·삭제·외부 요청을 무심코 반복하지 않는다. 속도와 결과 정확성을 별도로 확인한다.
- 라이선스: MIT OR Apache-2.0. 원문 확인: [LICENSE-APACHE](https://github.com/sharkdp/hyperfine/blob/c5161524980522320c7d3425e714cc0965a869a5/LICENSE-APACHE) · [LICENSE-MIT](https://github.com/sharkdp/hyperfine/blob/c5161524980522320c7d3425e714cc0965a869a5/LICENSE-MIT). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## Bruno

- 출처: [공식 저장소](https://github.com/usebruno/bruno), [확인 README](https://github.com/usebruno/bruno/blob/bc76f344922c624dae703506f04cc3b3b065efe4/readme.md). 확인 커밋 `bc76f344922c624dae703506f04cc3b3b065efe4` (2026-11-02). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 기존 HTTP 도구의 보완; minwoo-api-compat은 계약 변경 검토가 필요할 때만.
- 실행 조건: 데스크톱 또는 CLI와 테스트 대상 서버가 필요하다. 핵심 저장소 MIT와 별도로 무료·유료 기능 범위를 구분한다.
- 사용 전 검증: 합성 로컬 API로 먼저 검증한다. 인증·환경 값은 공개 요청 모음에 넣지 않는다. 테스트 실행은 실제 요청을 보내므로 운영 데이터 변경을 일으키는 호출은 해당 권한 범위에서만 한다.
- 라이선스: MIT. 원문 확인: [license.md](https://github.com/usebruno/bruno/blob/bc76f344922c624dae703506f04cc3b3b065efe4/license.md). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## Datasette

- 출처: [공식 저장소](https://github.com/simonw/datasette), [확인 README](https://github.com/simonw/datasette/blob/d1cc495a966cafaed3e50dad73cd88e790031704/README.md). 확인 커밋 `d1cc495a966cafaed3e50dad73cd88e790031704` (2026-11-01). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 독립 참고 후보; 표 산출물·대량 적재 구현·PostgreSQL 검토와 구분.
- 실행 조건: 확인 README는 Python 3.11+를 명시한다. SQLite 파일·추가 플러그인·안정 배포 버전 요구를 확인한다.
- 사용 전 검증: 합성 SQLite 사본을 로컬에서 열어 검색·필터를 확인한다. 원본 DB·운영 자료를 자동 노출하지 않으며 게시·외부 접속·쓰기 플러그인은 별도 요청 범위다. 호스팅 완료나 보안 감사 결과로 취급하지 않는다.
- 라이선스: Apache-2.0. 원문 확인: [LICENSE](https://github.com/simonw/datasette/blob/d1cc495a966cafaed3e50dad73cd88e790031704/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## 보관·도입 기준

이번에는 공식 README·루트 라이선스·소스 커밋을 검토했다. 실행 파일·스킬 원문·이미지·폰트·의존 패키지는 복제하거나 설치하지 않았다. 의존성 보안 감사·실제 Windows 동작·성능·다른 엔진과의 호환성은 확인하지 않았다.

필요한 작업이 생기면 기존 도구로 충분한지 판단하고, 선택 후보 하나의 현재 배포·버전·환경과 위 대표 검증을 확인한다. 같은 역할의 스킬을 새로 만들거나 전체 후보를 동시 로딩·설치하지 않는다. 이 안내는 기존 승인 방식과 사용자 요청 범위를 바꾸지 않는다. 실제 시험 후에만 후보의 검증 상태를 갱신한다.
