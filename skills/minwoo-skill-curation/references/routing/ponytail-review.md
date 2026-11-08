# Ponytail 선택 검수 — 2026-11-08

확인 원본: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846), [SKILL.md](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/skills/ponytail/SKILL.md), [MIT LICENSE](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/LICENSE).

기존 구현·표준 기능·설치된 의존성의 재사용 순서와 최소한의 완전한 변경이라는 관점을 참고해 한국어 안내를 독자 작성했다. 원문·플러그인·실행기·훅을 복제하거나 설치하지 않았다. 기존 설계·리뷰·테스트와 역할이 겹쳐 새 스킬은 추가하지 않는다.

원본 자체도 보안·접근성·필요한 오류 처리를 유지하도록 한다. 추가 보완은 재사용 후보의 계약 확인, 부적절한 공통화 방지, 파일 이동·새 의존성에 숨은 부담의 구분, 이번 작업 범위의 마무리 점검이다. 세션 전체 상시 적용, 답변 형식 강제, 강한 모드의 선제적인 범위 반박, 비용 기록·세션 가져오기 기능은 채택하지 않았다. 토론/구현 요청과 기존 승인 방식을 유지한다.

[제작자 실험](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/benchmarks/results/2026-10-07-agentic.md)은 Claude의 무스킬 기준과 비교한 자체 결과다. 날짜 선택기 335→10줄이나 전체 평균을 이 kit의 기대 효과로 사용하지 않는다. 현재 kit 기준과 보강안을 같은 합성 과제로 비교하는 별도 평가를 유지한다.

실행 안내·범위·한계는 저장소의 `evals/SIMPLIFICATION.md`에 있다. 해당 문서는 kit 저장소에서 읽는 검증 기록이며 설치된 스킬의 필수 실행 의존성이 아니다.
