# Context Mode 비교 평가

```text
python -B scripts/setup-context-mode.py --runtime-root <시험 런타임 부모>
python -B evals/verify_context_mode.py --runtime <Context Mode 런타임> --out <새 결과 폴더>
python -B evals/run_context_mode_tasks.py
python -B evals/run_context_mode_tasks.py --run --runtime <Context Mode 런타임> --out <새 개인 결과 폴더>
```

첫 평가는 모델 호출 없이 합성 문서 약 134KB에서 원문 전체·정확한 제목을 아는 rg·Context Mode를 비교한다. 필요한 사실 검색, 캐시 재사용, 원문 변경 후 갱신, 파일 간 분리, 한글 정확 질의를 검사한다. 측정값은 UTF-8 출력 바이트와 실행 시간이며 모델 과금 토큰이 아니다. rg가 없으면 같은 행 범위의 Python 필터를 사용하고 baseline_tool에 구분한다.

두 번째 평가는 현재 로그인·기본 모델로 새 Codex 세션 네 개를 실행한다. 기존 검색과 Context Mode 각각 실제 재시도 코드 수정(별도 70개 경계 입력 검증)과 마이그레이션 조건 추출(5개 필드 검증)을 수행한다. 원문 보존, 실제 검색 실행, 원문 절 읽기, 최종 결과를 검사한다. 스킬 자동 선택률과 구분하며 저장된 설정은 수정하지 않는다. 시험 세션만 workspace-write로 실행한다.

원시 trace와 오류 출력은 로컬 경로를 포함하므로 공개하지 않는다. 검토한 summary.json만 공개한다. 출력 바이트, 전체 세션 입력 토큰, 캐시 입력 토큰, 경과 시간을 분리한다. 준비·기존 지침 읽기·출력 형식·반복 모델 호출도 수치에 포함된다. 각 방식/과제 1회인 소규모 사례이므로 통계적 우월성이나 미래 작업의 절감률을 증명하지 않는다.

초기 실패·효과 없음도 보존한다. 보완 후 재시험은 새 폴더에 기록하고 변경 이유를 명시한다. 반복해서 유리한 결과만 골라 평균을 만들지 않는다. 실제 코드·결론의 정확성을 절감보다 우선한다.
