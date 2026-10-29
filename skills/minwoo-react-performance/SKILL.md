---
name: minwoo-react-performance
description: React·Next.js의 느린 로딩·불필요한 재렌더·데이터 요청 지연·번들 크기를 측정하고 개선하거나 성능 중심으로 검토할 때 사용한다. 일반 UI 제작·미적 디자인·모든 React 수정에는 적용하지 않는다.
---

# React 성능 검토

먼저 React/Next.js 버전, 렌더링 방식, 실제 병목과 재현 조건을 확인한다. 성능 개선 전후를 같은 조건으로 비교하고 기능·권한·캐시 격리를 지킨다. React Compiler가 해결하는 메모화를 무작정 중복하지 않는다.

[규칙 목록](references/index.md)에서 문제에 해당하는 1~3개 문서를 먼저 읽는다. 전체 규칙을 한 번에 로딩하거나 모든 규칙을 일괄 적용하지 않는다.

- 요청 직렬화: `rules/async-*.md`
- 번들/로딩: `rules/bundle-*.md`
- 서버/인증/캐시: `rules/server-*.md`
- 클라이언트 데이터: `rules/client-*.md`
- 재렌더/표시: `rules/rerender-*.md`, `rules/rendering-*.md`
- JS/고급 패턴: 병목이 확인된 경우에만 해당 규칙

원본의 CRITICAL/HIGH 표시는 정렬용 참고이며 현재 코드의 결함 등급이 아니다. API·프레임워크 버전 조건을 공식 문서와 대조한다. React 19 이상의 API를 18 코드에 쓰지 않는다. 캐시로 사용자 데이터가 섞이거나 숨긴 hydration 경고가 실제 문제를 가리지 않도록 확인한다. 라이브러리 교체·대규모 리팩터링은 요청에 필요한 경우에만 한다.

검증 명령·측정치·남은 제한을 결과에 포함한다. 미적 디자인은 기존 UI 스킬, 컴포넌트 공개 API 구조는 `minwoo-react-composition`의 역할이다. [출처](UPSTREAM.md).
