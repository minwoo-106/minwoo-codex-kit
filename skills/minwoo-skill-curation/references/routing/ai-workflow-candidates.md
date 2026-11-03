# 디자인·보안·개발 스킬과 도구 후보

검토일: 2026-11-03. 릴스의 10개 항목과 추가 소개 ub-mode를 현재 kit 역할에 맞춰 분류했다. 순위·별 수는 재현하거나 성능 근거로 사용하지 않았다. 아래 검수는 지정 파일 범위이며 전체 저장소/공급망 감사가 아니다.

| 편입 | 항목 | 상태 |
| --- | --- | --- |
| 기존 설치 유지 | Impeccable, Taste Skill(design-taste-frontend) | 로컬 스킬 본문 확인, 복제/업데이트 안 함 |
| 기존 스킬 보강 | Cloudflare 보안, Claude SEO, ub-mode의 일부 관점 | 독자 안내·검사만 추가, 외부 원문/실행기 미설치 |
| 기존 선택 안내 보강 | ECC 변경 영향, Superpowers 리뷰 피드백 | 기존 스킬로 연결, 전체 묶음 미설치 |
| 디자인 비교 후보 | Hallmark | 검토 파일/조건 기록, 설치·시각 비교 전 |
| 별도 환경/분야 참고 | ThinkRail, Claude Mem, TradingAgents | 설치·연결·실행 전 |

## Hallmark

- 출처: [Nutlope/hallmark](https://github.com/Nutlope/hallmark), 확인 커밋 `4f6a46c6dc325d40ab268c93e25c7b96676ebccd`.
- 읽은 범위: [skills/hallmark/SKILL.md](https://github.com/Nutlope/hallmark/blob/4f6a46c6dc325d40ab268c93e25c7b96676ebccd/skills/hallmark/SKILL.md) · [skills/hallmark/references/flow.md](https://github.com/Nutlope/hallmark/blob/4f6a46c6dc325d40ab268c93e25c7b96676ebccd/skills/hallmark/references/flow.md) · [skills/hallmark/scripts/sloplint.mjs](https://github.com/Nutlope/hallmark/blob/4f6a46c6dc325d40ab268c93e25c7b96676ebccd/skills/hallmark/scripts/sloplint.mjs) · [package.json](https://github.com/Nutlope/hallmark/blob/4f6a46c6dc325d40ab268c93e25c7b96676ebccd/package.json). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/Nutlope/hallmark/blob/4f6a46c6dc325d40ab268c93e25c7b96676ebccd/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 디자인 비교 후보. 기존 design-taste-frontend·impeccable과 주도 역할이 겹쳐 자동 설치하지 않는다. 테마 선택·화면 검사·출력물 반복 개선 방식은 같은 요구사항으로 비교할 가치가 있다.
- 조건·제외: Node 18+, 렌더 검사에는 puppeteer-core와 Chrome/Chromium이 필요하다. Together API 키 신호에 따른 이미지 생성, 프로젝트 .hallmark 기록, 파일 scaffold, Claude용 훅, 새 문맥 검토 절차가 있다. 후보 등록을 API 비용·다운로드·훅·에이전트 실행 허가로 해석하지 않는다. 절대적인 폰트/레이아웃 금지나 브라우저 사용 강제는 기존 디자인·도구 지침보다 우선하지 않는다.
- 도입 시 검증: 실제 도입 때 부모 참고 파일·theme/capture/imagegen 등 실행 코드를 추가 검수한다. 같은 합성 페이지를 기존 주도 디자인 스킬과 따로 만들어 모바일/데스크톱 실제 화면, 접근성·폼 동작·수정량을 비교한다. lint 통과를 미적 우수성으로 취급하지 않는다.

## Cloudflare Security Audit

- 출처: [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), 확인 커밋 `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`.
- 읽은 범위: [skills/security-audit/SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/SKILL.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 기존 minwoo-security-review에 경계 위반의 근거·확인/미확인/기각 구분·대조군을 보강했다. 별도 중복 보안 스킬은 추가하지 않았다.
- 조건·제외: 원본 전체 감사는 단계별 에이전트·출력 스키마·격리·검증 도구를 요구한다. 이번에는 해당 실행 환경이나 전체 감사 엔진을 설치하지 않았다. 전체 절차를 매 코드 수정에 적용하거나 이미 허용된 수정에 재승인을 강제하지 않는다.
- 도입 시 검증: 합성 취약/안전 코드를 같은 입력으로 비교한다. 외부 배포 조건이 없으면 미확인으로 남긴다. 향후 원본 전체 감사 도입은 참조 스키마·검증기·격리 기능을 별도 확인한다.

## Claude SEO

- 출처: [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo), 확인 커밋 `6be93f45064ffbadced572b5d5c95f55fd263af0`.
- 읽은 범위: [skills/seo-schema/SKILL.md](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-schema/SKILL.md) · [skills/seo-drift/SKILL.md](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-drift/SKILL.md) · [skills/seo-content/SKILL.md](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-content/SKILL.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 기존 minwoo-seo-review의 구조화 데이터·변경 비교와 minwoo-web-copy의 콘텐츠 근거를 보강했다. 새 비교기는 독자 구현이며 원본 스크립트를 복제하지 않았다.
- 조건·제외: 원본은 Claude 플러그인 경로·Python 런타임·브라우저·동료 스킬을 참조하고 일부 기능은 검색/분석 API가 필요하다. 기능별 필수 조건을 확인한다. 지역 SEO·전자상거래·분석 계정 연결은 필요할 때 추가 검수할 후보이며 이번에 구현/연결하지 않았다. 고정 글자 수·자체 점수·검색 기능 상태표·AI 인용 주장·문체/유니코드 정리는 공통 규칙으로 가져오지 않는다.
- 도입 시 검증: 저장된 합성 스냅샷으로 noindex/canonical/제목/JSON-LD 차이와 기준본의 기존 오류를 확인한다. 실제 검색 노출·리치 결과 자격·트래픽은 현재 공식 문서와 허용된 실제 관찰로 따로 확인한다.

## ECC

- 출처: [affaan-m/ECC](https://github.com/affaan-m/ECC), 확인 커밋 `b38be6a7f6350964d59328b52f0624e1d1d552d1`.
- 읽은 범위: [skills/change-impact/SKILL.md](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/skills/change-impact/SKILL.md) · [skills/verification-loop/SKILL.md](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/skills/verification-loop/SKILL.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 변경 전 영향과 실제 diff의 대조를 기존 개발 안내에 연결했다. 기존 API/DB/설계/테스트 스킬 역할을 유지한다. 언어·프레임워크별 개별 스킬은 프로젝트 스택이 정해지면 추가 검수할 참고 묶음이다.
- 조건·제외: 규칙·훅·메모리·MCP·설정 동기화까지 포함하는 큰 배포다. 일부 선택 기능은 Bash/Python과 호스트별 지원 차이가 있다. 전체 설치·고정 커버리지 기준·모든 단계 실행·반복 문서 승인·기존 설정 교체를 채택하지 않는다.
- 도입 시 검증: 선택한 개별 스킬의 본문·부모/참조 파일·실행기·Windows 조건을 별도 확인한다. 대표 변경에서 호출자·테스트·실제 diff가 맞는지 검증한다. 두 스킬 검수로 전체 ECC 검수를 주장하지 않는다.

## Superpowers

- 출처: [obra/superpowers](https://github.com/obra/superpowers), 확인 커밋 `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`.
- 읽은 범위: [skills/receiving-code-review/SKILL.md](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/receiving-code-review/SKILL.md) · [skills/verification-before-completion/SKILL.md](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion/SKILL.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 리뷰 의견을 현재 코드·계약·재현으로 확인하는 부분을 기존 리팩터링 안내에 연결했다. 테스트·진단·계획·검증은 기존 도구와 겹쳐 중복 설치하지 않는다.
- 조건·제외: 전체 묶음은 초기 지침·자동 발동·설계 승인·작업 트리·에이전트 실행 흐름을 포함한다. 모든 작업의 질문/승인, 매 응답 전체 테스트, 표현 금지 목록을 공통 규칙으로 가져오지 않는다. 기존 검증이 유효하고 추가 변경이 없다면 형식적 재실행을 요구하지 않는다.
- 도입 시 검증: 리뷰 지적 중 맞는 것과 틀린 것을 현재 코드로 판별하고, 허용된 수정 후 정상·회귀 사례를 확인한다. 전체 플러그인 도입은 호스트별 bootstrap/hook과 사용 스킬을 다시 검수한다.

## ThinkRail

- 출처: [JetBrains/thinkrail](https://github.com/JetBrains/thinkrail), 확인 커밋 `c469b724025b4e3f0719a701ffa74b4d2fe60812`.
- 읽은 범위: [README.md](https://github.com/JetBrains/thinkrail/blob/c469b724025b4e3f0719a701ffa74b4d2fe60812/README.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [Apache-2.0 LICENSE](https://github.com/JetBrains/thinkrail/blob/c469b724025b4e3f0719a701ffa74b4d2fe60812/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 별도 IDE 참고 후보. pi 에이전트·격리 worktree·프로젝트 지식 기능이며 Codex SKILL.md 추가와는 다르다.
- 조건·제외: 플랫폼별 앱/CLI 배포, Git, 모델 공급자 연결이 필요하다. README의 사용량/오류 보고와 기존 인증 사용 범위를 도입 전에 확인한다. 원격 설치 스크립트를 바로 실행하거나 기존 개발 환경을 이전하지 않는다.
- 도입 시 검증: 합성 저장소에서 작업 공간 생성·변경 격리·기존 작업 보존·병합/정리 범위·Windows 종료/업데이트를 확인한다. 현재는 README·라이선스 검토만 했으며 앱 실행 검증 전이다.

## Claude Mem

- 출처: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem), 확인 커밋 `02584c4ac9d92fea45adf5c61e22c546b5738621`.
- 읽은 범위: [README.md](https://github.com/thedotmack/claude-mem/blob/02584c4ac9d92fea45adf5c61e22c546b5738621/README.md) · [NOTICE](https://github.com/thedotmack/claude-mem/blob/02584c4ac9d92fea45adf5c61e22c546b5738621/NOTICE). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [Apache-2.0 LICENSE](https://github.com/thedotmack/claude-mem/blob/02584c4ac9d92fea45adf5c61e22c546b5738621/LICENSE) · [NOTICE](https://github.com/thedotmack/claude-mem/blob/02584c4ac9d92fea45adf5c61e22c546b5738621/NOTICE). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 세션 간 자동 기억의 참고 후보. 명시적인 인수인계와 큰 파일 검색인 Context Mode와 다르며 필요가 생길 때 선택한다.
- 조건·제외: Node/Bun worker·SQLite·검색 저장소·호스트 훅·기억용 모델 공급자가 연결된다. 현재 README에는 Codex 관련 경로도 있지만 이 PC의 Work 모드 연동을 검증한 것은 아니다. 계정 로그인, 제공자 선택, PATH/훅 쓰기, 선택 Cloud Sync·스크린샷/이미지 처리의 실제 기본값과 비용을 배포별로 확인한다.
- 도입 시 검증: 먼저 가짜 프로젝트 두 개로 기록·검색·다음 세션 회수·프로젝트 분리·제외·삭제·보존 기간을 검증한다. 개인 대화 전체나 회사 코드를 시험 재료로 쓰지 않는다. 이번에는 worker/훅/클라우드 동기화를 설치·활성화하지 않았다.

## TradingAgents

- 출처: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents), 확인 커밋 `c4544913a14ed3df5f1ed7b9e8483270ce20682a`.
- 읽은 범위: [README.md](https://github.com/TauricResearch/TradingAgents/blob/c4544913a14ed3df5f1ed7b9e8483270ce20682a/README.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [Apache-2.0 LICENSE](https://github.com/TauricResearch/TradingAgents/blob/c4544913a14ed3df5f1ed7b9e8483270ce20682a/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 금융 분석·멀티에이전트 연구 프레임워크 참고 후보. 일반 코딩이나 홈페이지 제작에 자동으로 추가하지 않는다.
- 조건·제외: Python·LangGraph 등 패키지, 모델 공급자, 시장/뉴스 데이터에 대한 접근·비용 조건이 있다. README 자체도 연구 목적과 결과 변동성을 밝힌다. 후보 등록은 계좌 연결·실거래·모델/API 호출 권한이 아니다.
- 도입 시 검증: 실제 필요 시 데이터 시점·미래 정보 누출·재현성·평가 기준을 고정한 작은 연구 과제로 검증한다. 모의 결과·백테스트를 실거래 수익 보장으로 표현하지 않는다. 현재는 README·라이선스 확인이며 금융 성능 시험 전이다.

## ub-mode

- 출처: [unclebob/ub-mode](https://github.com/unclebob/ub-mode), 확인 커밋 `3da62bf3fcfd2034de41f30d920d2739e566171f`.
- 읽은 범위: [SKILL.md](https://github.com/unclebob/ub-mode/blob/3da62bf3fcfd2034de41f30d920d2739e566171f/SKILL.md) · [README.md](https://github.com/unclebob/ub-mode/blob/3da62bf3fcfd2034de41f30d920d2739e566171f/README.md). 실행기 전수 감사나 모든 하위 스킬 검수는 아니다.
- 공개 조건: [MIT LICENSE](https://github.com/unclebob/ub-mode/blob/3da62bf3fcfd2034de41f30d920d2739e566171f/LICENSE) (조회한 트리에 별도 NOTICE 경로 없음). 새 원문·자산·코드는 재배포하지 않는다.
- 판단: 도구 기반 품질 측정의 관점을 minwoo-test-quality에 보강했다. 기존 TDD·설계·진단·리팩터링·Git 규칙과 겹치는 부분은 재등록하지 않았다.
- 조건·제외: 원본은 crapper/dryer/mutator/uml-viewer를 연결하며 고정 CRAP/중복 기준, 매 작업 로그와 기본 브랜치 푸시를 제시한다. 이를 공통 실행 지침으로 가져오지 않는다. 동반 저장소 4개는 별도 코드/라이선스 검수 전이다.
- 도입 시 검증: 정상 구현의 통과·의미 있는 변이의 assertion 실패·동등 변이/실행 오류의 분리를 확인한다. 숫자를 맞추기 위한 코드 분할이나 테스트 삭제를 하지 않는다.

## 꺼내 쓰는 방식

관련 기술이 필요할 때 해당 절만 읽는다. 설치를 실행할 때는 현재 배포·지원 환경·원본 변경·필수 파일·실행기를 재확인하고 사용자 범위에 맞춰 필요한 구성만 선택한다. 전역 AGENTS.md·승인 설정·플러그인 캐시·모델 설정을 이 후보 목록 때문에 바꾸지 않는다. 동일 역할의 스킬을 동시에 주도로 실행하지 않는다.

이번에는 원본의 일부 관점을 독자적으로 정리하고 외부 링크를 보관했다. 외부 패키지를 내려받아 실행하거나 API 키를 확인하지 않았다. 상세 실행 검증 결과는 kit의 docs/VALIDATION.md에 기록하며, 로컬 합성 시험을 외부 후보 전체의 검증으로 확대하지 않는다.
