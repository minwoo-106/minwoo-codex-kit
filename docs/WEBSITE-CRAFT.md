# 홈페이지 기획·디자인·문구·출시 구성

0.8.0은 홈페이지 제작 후보 5개와 디자인·문구 보강 후보 6개를 역할별로 묶었다. 새 스킬은 4개이며 기존 외부 디자인 스킬·플러그인 캐시는 수정하지 않았다. 아래 지침은 직접 작성했고 외부 문서나 스킬 본문을 복제하지 않았다.

| 후보 | 적용 위치 | 결과와 경계 |
| --- | --- | --- |
| 사이트 기획·콘텐츠 구성 | minwoo-project-context / site-brief | 기존 기획 문서에 페이지 목적·콘텐츠·행동 정리. AGENTS.md로 바꾸지 않음 |
| 브랜드 말투 | 새 minwoo-brand-voice | 원칙과 상황별 예문. 단일 문장 교정에는 미적용 |
| 홈페이지 카피라이팅 | 새 minwoo-web-copy | 첫 화면·서비스·FAQ·행동 문구. 사실·미확인 주장 분리 |
| 디자인 방향 비교 | 기존 21st-ui-explore 등 + web-craft 안내 | 같은 사실·기능을 유지한 서로 다른 시각 방향 |
| 한글 화면 다듬기 | 기존 디자인 검토 + web-craft 안내 | 실제 폰트·모바일 줄바꿈·버튼 잘림 검토 |
| UI 상태별 문구 | 기존 impeccable + web-craft 안내 | 입력·서버 실패·완료를 실제 상태에 맞게 표현 |
| 이미지·폰트 준비와 스타일 통일 | 새 minwoo-web-assets | 출처·라이선스·사용 위치·크기·표현 방향. 기존 이미지 도구로 실행 |
| 웹 속도 측정 | minwoo-browser-check 확장 | 기존 Playwright로 Navigation Timing 반복 측정. 실사용 Web Vitals·Lighthouse 점수와 구분 |
| 폼 전체 흐름 | minwoo-browser-check 확장 | 실패·중복 클릭·재시도와 실제 테스트 접수 증거 연결 |
| 공개 전후 점검 | 새 minwoo-web-launch | 경로·링크·공유 정보·미확인 항목. 배포 실행과 구분 |

## 필요한 것만 선택

진입은 기존 [웹 선택 안내](../skills/minwoo-skill-curation/references/routing/web-ui.md)를 사용한다. 디자인과 문구 보강이 필요할 때만 [web-craft](../skills/minwoo-skill-curation/references/routing/web-craft.md)를 읽는다. 안내·설치 묶음은 모든 스킬의 동시 실행 목록이 아니다.

간단한 소개 페이지에는 결제·회원·CMS·분석 추적을 자동 추가하지 않는다. Vercel과 PostHog는 선택 안내에만 포함하며 이번 스킬 설치로 새 연결·추적 코드·배포를 실행하지 않는다. 기존 승인 방식·공통 규칙·외부 스킬 호출 정책을 유지한다.

## 실제 도구와 제한

기존 Playwright 1.62.1 런타임을 재사용한다. 추가 패키지를 설치하지 않는다. 명시한 페이지·내부 경로만 검사하고 원격 주소에는 명시 옵션이 필요하다. 출력·기준 자료를 덮어쓰지 않는다. 사이트 검사기는 파일·URL 목록 전체를 크롤링하지 않는다.

속도는 통제된 실험실의 Navigation Timing 관찰이다. 같은 조건의 표본과 중앙값을 기록하고 하나라도 실패하면 실패 표본을 숨기지 않는다. 머신 부하·브라우저·OS/DNS 캐시의 영향을 받으며 실제 모바일 성능·LCP·INP·CLS·방문자 체감·전환 개선을 증명하지 않는다. Lighthouse가 필요한 작업은 사용 가능 여부를 확인한 뒤 별도로 실행한다.

창작 결과는 실제 자료를 근거로 사람이 읽어 검토한다. 형식 검사 통과를 카피의 설득력·브랜드 적합성·사용자 테스트 성공으로 표현하지 않는다. 이미지·폰트의 다운로드 가능 여부도 이용 허가의 증거가 아니다.

## 참고

- [공식 스킬 구조와 선택](https://learn.chatgpt.com/docs/build-skills)
- [홈페이지의 목적과 탐색](https://www.nngroup.com/articles/homepage-design-principles/)
- [오류 문구](https://design-system.service.gov.uk/components/error-message/)
- [반응형 이미지](https://web.dev/learn/design/responsive-images)
- [Navigation Timing](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming)

[실행 평가](../evals/SITE-TASKS.md), [검증 결과](VALIDATION.md).
