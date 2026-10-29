# DB 변경·복구 연습

프로젝트가 사용하는 마이그레이션 도구와 동일한 PostgreSQL 임시 인스턴스가 있으면 먼저 사용한다. 준비된 환경이 없고 기본 PostgreSQL SQL만 확인하면 되는 경우 제공 도구가 메모리 내 PGlite를 새로 만들며 원격 연결 옵션은 받지 않는다.

```text
node <스킬>/scripts/rehearse.mjs --runtime <kit 도구 폴더> --setup setup.sql --up up.sql --checks checks.json --down down.sql
```

checks 예: {"before":[{"sql":"SELECT id, name FROM items ORDER BY id","rows":[{"id":1,"name":"one"}]}],"after":[{"sql":"SELECT id, name, enabled FROM items ORDER BY id","rows":[{"id":1,"name":"one","enabled":true}]}]}

setup은 합성 초기 데이터, up/down은 검토할 SQL이다. before 검사를 먼저 통과시킨 뒤 up→after→down→before를 확인한다. down이 없으면 복구 미검증으로 보고한다. 입력 SQL·검사 파일은 수정하지 않으며 종료 시 DB를 닫는다. 실패한 변경도 기존 DB에 영향을 주지 않는다.

행 개수만으로 데이터 보존을 판정하지 말고 주요 값·제약·권한도 검사한다. DROP/데이터 변환처럼 되돌릴 수 없는 변경에는 별도 백업·전진 복구 계획이 필요하다. down 성공도 모든 운영 복구를 보장하지 않는다. 운영 버전·확장·잠금·동시성·대용량·Supabase 인증은 실제 대상과 같은 격리 환경에서 별도로 확인한다.

[PGlite API](https://pglite.dev/docs/api).
