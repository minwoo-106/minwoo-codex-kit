---
name: minwoo-postgres-review
description: PostgreSQL·Supabase의 느린 쿼리, 인덱스·스키마·RLS·잠금·연결 관리 문제를 조사하거나 DB 설계를 검토할 때 사용한다. DB와 무관한 개발이나 단순 데이터 조회에는 적용하지 않는다.
---

# PostgreSQL 검토

DB 종류·버전, 데이터 규모, 실제 실행 계획, 읽기/쓰기 빈도와 허용된 대상 환경을 확인한다. [참고 목록](references/index.md)에서 해당 문제의 문서만 읽는다.

- 쿼리·인덱스: `query-*.md`
- 스키마·제약: `schema-*.md`
- RLS·권한: `security-*.md`
- 연결·잠금: `conn-*.md`, `lock-*.md`
- 데이터 처리·관측: `data-*.md`, `monitor-*.md`

예시 SQL을 운영 환경에 그대로 실행하지 않는다. EXPLAIN ANALYZE는 실제 쿼리를 실행한다. 특히 쓰기 쿼리·트리거·외부 효과는 단순 읽기 검사가 아니다. 현 작업에서 허용한 격리 환경이나 읽기 전용 계획부터 확인한다.

인덱스는 쓰기 비용·크기·중복을 함께 검토한다. RLS는 소유자/슈퍼유저가 아닌 실제 역할로 허용·차단을 모두 검사한다. Supabase auth 함수·pooler·확장 기능은 해당 환경에서 별도로 확인한다. 로컬 PGlite 검증은 SQL 예시의 기본 동작만 확인하며 운영 PostgreSQL의 동시성·네트워크·Supabase 인증을 검증하지 않는다.

결과에는 SQL, 대상 버전, 근거, 실제 실행 여부, 마이그레이션·복구 고려 사항을 적는다. DB 접속 정보나 운영 데이터를 kit에 저장하지 않는다. [출처](UPSTREAM.md).
