# Context Mode 선택 도입

2026-10-30 검수. 긴 로컬 참고 문서의 관련 절 찾기에 쓰는 **선택형 CLI 구성**이다. Context Mode 전체 플러그인/MCP 설치와 구분한다. 기존 규칙·승인·스킬 선택을 유지하며 새 자동 발동 스킬은 만들지 않는다.

## 채택 범위

| 기능 | 결정 |
| --- | --- |
| 공식 CLI의 index/search, SQLite FTS5/BM25 | 선택 도구로 사용 |
| Windows CRLF/BOM 문서 | 원문을 보존하고 검색 사본만 LF로 정규화 |
| 같은 파일 재조회 / 변경된 파일 | 원문 경로·내용 해시로 캐시 재사용 / 별도 색인 |
| 검색 이후 사실 확인 | 결과 제목에 해당하는 원문의 행 범위를 안내 |
| 기존 디버깅·개발 선택 안내 | 조건부 참고 문서와 실행기를 확장 |
| MCP 코드 실행·웹 요청·자동 훅·세션 기록 | 이번 구성에서 활성화하지 않음 |
| 원본 AGENTS.md 강제 라우팅·setup/upgrade/postinstall | 적용·실행하지 않음 |
| 새 스킬·별도 Bun·native SQLite addon·전역 npm 설치 | 추가하지 않음 |

정확한 위치를 아는 rg 검색이 더 빠르고 출력도 작을 수 있다. 짧은 파일·일회성 로그는 기존 도구를 우선한다. Context7은 외부 최신 문서 조회이고 이 도구는 이미 확보한 로컬 문서 검색이다. 자동 대화 기억·세션 복구를 설치했다고 주장하지 않는다.

## 설치와 사용

Python 3.10+, Node.js 24+의 내장 SQLite/FTS5를 확인한다. Windows PowerShell과 Unix 모두 같은 Python 명령을 사용한다.

```text
python -B scripts/setup-context-mode.py --dry-run
python -B scripts/setup-context-mode.py
```

기본 경로는 실제 Codex 홈의 `.minwoo-codex-kit/runtimes/context-mode-1.0.169`다. `--runtime-root`로 변경할 수 있다. 설치기는 공식 npm tarball의 SHA-512를 확인한 후 cli.bundle.mjs, package.json, LICENSE 세 파일만 추출한다. 공식 번들에 포함된 코드를 그대로 사용하며 npm 생명주기 스크립트는 실행하지 않는다. 내장 FTS5가 없으면 추가 패키지로 우회하지 않고 실패한다.

기존 런타임이 같으면 UNCHANGED, 수정·미완료·다른 버전이면 중단한다. 기존 파일은 덮어쓰거나 제거하지 않는다. 일반 스킬 설치는 별도이며 기존 규칙을 유지하려면 아래처럼 필요한 두 스킬만 갱신한다.

```text
python -B scripts/install.py --skill diagnosing-bugs --skill minwoo-skill-curation --skip-rules --dry-run
python -B scripts/install.py --skill diagnosing-bugs --skill minwoo-skill-curation --skip-rules
python <설치된 diagnosing-bugs>/scripts/context_search.py --file <문서.md> --query "retry budget" --query "rollback compatibility"
```

기존 PC가 `~/.codex/skills`를 사용하면 install.py의 `--skills-root`로 그 경로를 명시한다. 사용자 경로에 맞춰 설치하며 같은 스킬을 두 곳에 복제하지 않는다. 런타임 경로를 바꿨다면 검색 실행기에 `--runtime`을 전달한다.

검색 캐시는 OS 임시 폴더의 minwoo-context-mode 아래에 원문 사본과 DB로 남으며 자동으로 지워지지 않는다. `--cache-root`로 작업별 위치를 정할 수 있다. 캐시는 공개 저장소에 넣지 않는다. 정리할 때는 해당 실행이 끝났는지와 정확한 캐시 경로를 확인하고 사용자가 요청한 범위에서 삭제한다. 보존할 자료의 유일한 사본으로 사용하지 않는다.

## 권한과 갱신

공식 CLI를 기존 터미널 도구로 호출한다. Codex config.toml, 승인 정책, 인증, MCP 등록, 자동 훅, 플러그인 캐시는 변경하지 않는다. 정상 실행에 필요한 읽기·캐시 쓰기도 기존 환경 권한을 따른다. 이 구성은 보안 격리 경계를 새로 만들거나 우회하지 않는다.

버전은 1.0.169로 고정했다. 갱신 시 새 배포의 라이선스·CLI·설치 부작용·내장 SQLite 호환성을 검토하고 URL/버전/무결성 값을 함께 갱신한다. 별도 경로에 설치해 실제 검색·원문 보존·동일 질의 결과를 비교한 뒤 실행기를 갱신한다. 원본의 `upgrade` 명령은 훅·설정 자동 보정을 포함하므로 이 구성의 갱신 방법으로 사용하지 않는다. 이전 런타임을 자동 삭제하지 않는다.

## 출처와 검증 범위

- [공식 저장소](https://github.com/mksglu/context-mode), 검토한 원본 커밋 `849c8690bdf86eef60156e13d98efd10fcfd46fb`.
- [npm 1.0.169](https://www.npmjs.com/package/context-mode/v/1.0.169): 실제 설치·시험 대상. 같은 버전의 Git 저장소 번들과 npm 번들의 바이트가 같다고 가정하지 않는다. 다운로드는 설치기의 고정 SHA-512로 검증한다.
- [LICENSE](https://github.com/mksglu/context-mode/blob/849c8690bdf86eef60156e13d98efd10fcfd46fb/LICENSE)는 Elastic License 2.0이다. kit에는 원본 실행 파일·문서를 재배포하지 않고 다운로드 설치기·독자 실행기·안내·합성 평가만 포함한다. 설치 폴더에는 원본 LICENSE와 package.json을 보존한다.
- [Codex MCP 공식 문서](https://learn.chatgpt.com/docs/extend/mcp)는 연결·도구 허용 목록·승인 설정을 구분한다. 이번에는 추가 MCP 실행 권한을 만들 필요가 없는 CLI 경로를 선택했다.
- [실전 비교 절차](../evals/CONTEXT-MODE.md), [검증 기록](VALIDATION.md).

검색량 감소를 전체 대화 토큰·요금 절감이나 정확도 향상으로 일반화하지 않는다. 공식 98% 수치를 이 PC에서 재현했다고 주장하지 않으며 실패한 초기 시험도 검증 기록에 남긴다.
