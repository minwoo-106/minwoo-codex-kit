# 웹 품질·보안·SEO 후보 검수

검토일: 2026-10-29. 0.7.0에서 새 스킬 2개와 기존 브라우저 스킬 확장으로 구성했다. 외부 플러그인은 스킬 ZIP에 포함하지 않는다.

| 후보 | 편입 방식 | 사용할 때 / 겹침 정리 |
| --- | --- | --- |
| Context7 | 연결된 환경에서 선택 사용 | 라이브러리 문서·예제 조회. 실제 프로젝트 버전을 대조하고 맞지 않으면 공식 문서를 확인한다. 실행·테스트를 대신하지 않는다. |
| 앱 코드 보안 | 새 `minwoo-security-review` | 인증·권한·입력 경로를 코드로 확인. 패키지 취약점은 기존 dependency-audit, 일반 변경 검토는 code-review가 주도한다. |
| 접근성 | 기존 `minwoo-browser-check` 확장 | axe로 자동 위반과 미확정 항목을 수집. 키보드·스크린리더 등의 수동 확인은 별도다. |
| 시각적 회귀 | 기존 `minwoo-browser-check` 확장 | 같은 환경의 기준 이미지와 비교. 미적 방향 선정은 기존 디자인 스킬의 역할이다. |
| 기술 SEO | 새 `minwoo-seo-review` | 제공된 HTML·HTTP 정보·robots·sitemap 검사. 비공개 의도와 실제 검색 노출을 구분한다. |

## 출처·의존성·승인

보안 스킬은 [OpenAI 원본 검토 기록](../skills/minwoo-security-review/references/sources.md)과 OWASP를 참고하여 직접 작성했다. 원문의 본문·코드는 복제하지 않았다. 이미 허용된 수정에 다시 포괄 승인을 요구하는 규칙을 추가하지 않았다.

접근성은 [Deque axe-core Playwright](https://github.com/dequelabs/axe-core-npm/tree/develop/packages/playwright) 4.14.0(MPL-2.0), 화면 비교는 [Playwright 테스트](https://playwright.dev/docs/test-snapshots) 1.62.1(Apache-2.0)을 고정했다. 패키지 원본은 별도 런타임에서 라이선스 고지와 함께 설치하며 스킬에 재배포하지 않는다. 설치 잠금·무결성 해시와 npm audit 0건을 확인했다. 프로젝트 의존성·시스템 PATH·기존 런타임을 덮어쓰지 않는다.

SEO 문서와 도구도 직접 작성했다. 근거는 [Google 개발자 문서](https://developers.google.com/search/docs/fundamentals/get-started-developers), [robots 메타·헤더](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag), [canonical 안내](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)다. canonical 누락을 무조건 오류로 취급하지 않고 robots의 복잡한 규칙은 수동 검토로 남긴다. HTML 검사는 전체 문서 유효성 검사나 구조화 데이터 자격 판정이 아니다.

외부 스킬 저장소를 통째로 설치하지 않는다. 선택 안내는 필요한 분야만 읽게 하고, 같은 역할을 하는 스킬 여러 개를 자동으로 함께 실행하지 않는다. 공통 승인 규칙은 유지하며 이 스킬이 외부 서비스 작업 권한을 추가하지 않는다.

## 실제 확인과 한계

[검증 기록](VALIDATION.md)과 [실행 방법](../evals/WEB-REVIEWS.md)을 참고한다. 접근성·화면 비교 정상/결함 8개, 기존 실행 도구 회귀 8개, 실제 Codex 보안·SEO 보고서, 자연어 선택 6개를 검사했다. 시험 페이지·코드는 합성 자료이며 사용자 서비스의 전체 보안·접근성 준수·검색 순위를 보증하지 않는다.

Context7의 설치·연결 상태는 PC/계정별로 다르다. 사용 가능한 도구가 실제로 제공된 경우에만 호출하며 설치 안내나 로그인 완료만으로 문서 조회 시험이 통과했다고 기록하지 않는다.

이번 PC에서는 사용자 설치·로그인 후 새 Codex 세션의 실제 라이브러리 검색·문서 조회 3회가 성공했다. [검증 요약](../evals/results/2026-10-29-context7-070.json)의 버전 범위를 확인한다.
