---
name: minwoo-react-composition
description: React 컴포넌트의 불리언 옵션 난립·중복 변형·불편한 공개 API·상태 공유 구조를 개선하거나 재사용 컴포넌트를 설계할 때 사용한다. 단순 UI 스타일 변경이나 성능 측정에는 적용하지 않는다.
---

# React 컴포넌트 구조

현재 호출부와 공개 API, React 버전, 상태 소유자를 확인한다. 기존에 충분한 간단한 컴포넌트를 복잡한 compound 패턴으로 바꾸지 않는다.

[규칙 목록](references/index.md)에서 필요한 것만 선택한다.

- 모드별 불리언이 많으면 `architecture-avoid-boolean-props.md`, `patterns-explicit-variants.md`.
- 여러 하위 요소가 함께 동작하면 `architecture-compound-components.md`, `state-context-interface.md`.
- 상태 구현에 결합된 API면 `state-decouple-implementation.md`, `state-lift-state.md`.
- 합성 API 선택은 `patterns-children-over-render-props.md`. render prop이 필요한 동적 데이터 전달까지 제거하지 않는다.
- React 19가 확인된 경우에만 `react19-no-forwardref.md`. 기존 18 호환 API를 무조건 폐기하지 않는다.

기존 동작·키보드 접근성·ref 전달·제어/비제어 상태의 호환성을 검증한다. 공개 API가 바뀌면 호출부와 이전 방식을 함께 설명한다. 해당 변경의 실제 동작 테스트를 수행하고, 원본 패턴과 닮았다는 이유만으로 완료로 판정하지 않는다. [출처](UPSTREAM.md).
