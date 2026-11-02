# DB 스킬 참고 후보

검토일: 2026-11-02. 다섯 공식 저장소의 지정 파일·고정 커밋·루트 LICENSE를 확인했다. **외부 스킬은 설치·실행 검증 전**이다. 기존 PostgreSQL 스킬의 공통 절차만 보강했으며 새 자동 발동 스킬·MCP·계정·의존 패키지는 추가하지 않는다.

| 후보 묶음 | 꺼내 볼 때 | 편입 방식 |
| --- | --- | --- |
| Supabase | 서비스 Auth·Storage·클라이언트 연동 | PG 모범 사례는 기존 편입 유지, 나머지는 선택 참고 |
| Neon | Neon 분기·마이그레이션 시험 | 서비스별 참고 |
| Prisma | Prisma 버전에 맞는 설정·마이그레이션 | ORM별 참고 |
| PlanetScale DB 지식 | MySQL 쿼리·스키마 검토 | 엔진별 참고, PG 중복 제외 |
| PlanetScale 운영 점검 | 해당 서비스의 권한·백업·운영 상태 | 서비스별 참고, 승인 계약 제외 |

## Supabase

- 출처: [공식 저장소](https://github.com/supabase/agent-skills), 확인 커밋 `c9be0e931b7930f7d02126d04774d904c381e7d7`.
- 확인 파일: [skills/supabase/SKILL.md](https://github.com/supabase/agent-skills/blob/c9be0e931b7930f7d02126d04774d904c381e7d7/skills/supabase/SKILL.md) · [skills/supabase-postgres-best-practices/SKILL.md](https://github.com/supabase/agent-skills/blob/c9be0e931b7930f7d02126d04774d904c381e7d7/skills/supabase-postgres-best-practices/SKILL.md).
- 공개 조건: [MIT LICENSE](https://github.com/supabase/agent-skills/blob/c9be0e931b7930f7d02126d04774d904c381e7d7/LICENSE). 확인한 저장소 트리에는 별도 NOTICE 경로가 없었다. 기존 Supabase 재배포분의 MIT 고지는 유지한다.
- 역할·겹침·검수 판단: PostgreSQL 모범 사례는 이미 minwoo-postgres-review의 원본으로 편입돼 있어 다시 설치하지 않는다. 넓은 supabase 스킬은 Auth·Storage·Realtime·클라이언트 등 서비스 기능이 실제 필요할 때만 참고한다. 원본에는 광범위 발동, MCP 설정 생성, 로컬 SQL 반복 실행·마이그레이션 생성 흐름이 있으므로 현재 프로젝트의 방식과 대상 범위를 먼저 확인한다. 권한 오류를 이유로 RLS·권한을 무조건 풀지 않는다.
- 도입 조건·대표 시험: Supabase 전용 CLI/MCP·로그인·프로젝트가 필요하다. 필요 시 해당 버전의 로컬/격리 프로젝트에서 실제 익명·사용자·다른 사용자 접근과 마이그레이션 이력을 검증한다. SQL 함수만 흉내 낸 PGlite 결과를 실제 Auth 검증으로 보지 않는다.

## Neon

- 출처: [공식 저장소](https://github.com/neondatabase/agent-skills), 확인 커밋 `d3da7cb5436edbb2bc8c00747fafd31ddf0644f4`.
- 확인 파일: [skills/neon/SKILL.md](https://github.com/neondatabase/agent-skills/blob/d3da7cb5436edbb2bc8c00747fafd31ddf0644f4/skills/neon/SKILL.md) · [skills/neon-postgres-branches/SKILL.md](https://github.com/neondatabase/agent-skills/blob/d3da7cb5436edbb2bc8c00747fafd31ddf0644f4/skills/neon-postgres-branches/SKILL.md).
- 공개 조건: [Apache-2.0 LICENSE](https://github.com/neondatabase/agent-skills/blob/d3da7cb5436edbb2bc8c00747fafd31ddf0644f4/LICENSE). 확인한 저장소 트리에는 별도 NOTICE 경로가 없었다. 기존 Supabase 재배포분의 MIT 고지는 유지한다.
- 역할·겹침·검수 판단: Neon을 사용하는 프로젝트의 분기·마이그레이션 시험 후보다. PostgreSQL 일반 검토는 기존 스킬을 유지한다. 원본 branches 스킬은 조언만이 아니라 브랜치 생성을 목표로 하고 부모 neon 스킬 로딩·설치 안내가 있다. 부모에는 서비스·스택 선택 권장이 있으므로 기존 DB·인증·프레임워크를 유지한다. 실제 데이터 포함 분기와 schema-only(Beta)를 구분하며 기본값으로 운영 데이터를 복제하지 않는다. reset-from-parent는 병합이 아니라 자식 데이터·스키마 교체다.
- 도입 조건·대표 시험: Neon CLI/MCP/API 중 실제 이용 가능한 경로 하나와 해당 프로젝트 인증이 필요하다. 도입 시 부모/참고 파일을 포함해 다시 검수한다. 합성 또는 허용된 마스킹 데이터의 별도 분기에서 생성·식별·변경·복원 범위·만료/정리 비용을 확인한다. 분기를 만들 권한이 없다고 다른 계정/프로젝트를 자동 생성하지 않는다.

## Prisma

- 출처: [공식 저장소](https://github.com/prisma/skills), 확인 커밋 `8ea289b730c2e89f7ff1f518af128b113d842a92`.
- 확인 파일: [prisma-cli/SKILL.md](https://github.com/prisma/skills/blob/8ea289b730c2e89f7ff1f518af128b113d842a92/prisma-cli/SKILL.md) · [prisma-orm-setup/SKILL.md](https://github.com/prisma/skills/blob/8ea289b730c2e89f7ff1f518af128b113d842a92/prisma-orm-setup/SKILL.md).
- 공개 조건: [MIT LICENSE](https://github.com/prisma/skills/blob/8ea289b730c2e89f7ff1f518af128b113d842a92/LICENSE). 확인한 저장소 트리에는 별도 NOTICE 경로가 없었다. 기존 Supabase 재배포분의 MIT 고지는 유지한다.
- 역할·겹침·검수 판단: Prisma 사용 프로젝트의 ORM·마이그레이션 명령 후보다. 확인본 prisma-cli는 ORM 7 전용이며 setup은 기존 6/7을 유지하고 새 앱에는 8을 기본으로 제안한다. 8의 상세 지침은 패키지 소유 prisma-8 스킬로 이어지므로 후보 검수가 그 별도 패키지 검수까지 뜻하지 않는다. 이 기본값을 모든 프로젝트의 업그레이드 지시로 적용하지 않는다. CLI만 보지 말고 클라이언트·설정·잠금 파일을 함께 확인한다.
- 도입 조건·대표 시험: 프로젝트와 호환되는 Node·Prisma CLI/클라이언트·DB가 필요하다. 설치·skills sync·새 DB 생성은 자동 실행하지 않는다. 실제 필요 시 고정 버전의 생성/계획/적용/초기화 명령 차이와 shadow DB 대상을 확인하고 합성 DB에서 마이그레이션 및 이전 앱 호환성을 시험한다. migrate reset/db push 등의 파괴적 동작을 일반 연결 해결책으로 쓰지 않는다.

## PlanetScale DB 지식

- 출처: [공식 저장소](https://github.com/planetscale/database-skills), 확인 커밋 `f6ed002d03084cb39c01d1d58904d47a36f5322a`.
- 확인 파일: [skills/mysql/SKILL.md](https://github.com/planetscale/database-skills/blob/f6ed002d03084cb39c01d1d58904d47a36f5322a/skills/mysql/SKILL.md).
- 공개 조건: [MIT LICENSE](https://github.com/planetscale/database-skills/blob/f6ed002d03084cb39c01d1d58904d47a36f5322a/LICENSE). 확인한 저장소 트리에는 별도 NOTICE 경로가 없었다. 기존 Supabase 재배포분의 MIT 고지는 유지한다.
- 역할·겹침·검수 판단: MySQL 쿼리·인덱스·트랜잭션·스키마 검토의 빈자리를 채울 참고 후보다. PostgreSQL 일반 조언은 기존 스킬과 중복되므로 별도 설치하지 않는다. Vitess·Neki는 해당 분산 DB를 사용할 때만 추가 검수한다. 읽은 MySQL 본문에는 PlanetScale 우선 호스팅 권장과 고정형 설계 조언이 있어 이를 공통 규칙으로 옮기지 않는다. MySQL 버전·collation·workload·측정 근거를 먼저 본다.
- 도입 조건·대표 시험: 실제 선택한 MySQL 호환 엔진·버전의 격리 인스턴스가 필요하다. 이 kit의 PGlite는 MySQL 검증기가 아니다. 도입 시 필요한 참고 파일을 읽고 실제 실행 계획·제약·잠금·데이터 보존을 확인한다. PostgreSQL SQL이나 RLS 절차를 MySQL에 그대로 적용하지 않는다.

## PlanetScale 운영 점검

- 출처: [공식 저장소](https://github.com/planetscale/skills), 확인 커밋 `999045cfbad79222f38a99599eb96bc736feabee`.
- 확인 파일: [planetscale-readonly-inventory/SKILL.md](https://github.com/planetscale/skills/blob/999045cfbad79222f38a99599eb96bc736feabee/planetscale-readonly-inventory/SKILL.md) · [planetscale-postgres-safety-review/SKILL.md](https://github.com/planetscale/skills/blob/999045cfbad79222f38a99599eb96bc736feabee/planetscale-postgres-safety-review/SKILL.md) · [planetscale-change-gates-and-approval-contract/SKILL.md](https://github.com/planetscale/skills/blob/999045cfbad79222f38a99599eb96bc736feabee/planetscale-change-gates-and-approval-contract/SKILL.md).
- 공개 조건: [MIT LICENSE](https://github.com/planetscale/skills/blob/999045cfbad79222f38a99599eb96bc736feabee/LICENSE). 확인한 저장소 트리에는 별도 NOTICE 경로가 없었다. 기존 Supabase 재배포분의 MIT 고지는 유지한다.
- 역할·겹침·검수 판단: PlanetScale 서비스의 역할·백업/PITR·브랜치·연결·관측 상태 점검 후보다. 조사와 변경 분리, 근거 기록, 복원 연습의 공통 개념만 기존 DB 스킬에 직접 작성했다. 원본의 매 변경 ID·승인 계약·자율 모드 예외를 이식하지 않는다. 원본에서 제안으로 분류하는 개발 브랜치 DDL·webhook 시험도 실제 외부 변경일 수 있으므로 사용자 범위에 따른다. Postgres 분기와 Vitess deploy request를 같은 흐름으로 취급하지 않는다.
- 도입 조건·대표 시험: pscale CLI/API 인증 및 서비스별 기능이 필요하고 일부 자료는 선택 MCP를 전제한다. sibling 스킬 참조와 설치 스크립트의 다중 에이전트 경로 쓰기 범위는 실제 도입 전에 확인한다. 현재는 설치 스크립트를 실행하지 않았다. 허용된 대상의 읽기 점검부터 시작하고 접근 실패·미확인 자료를 안전하다는 증거로 삼지 않는다. pg_strict·Traffic Control·네트워크·백업 정책을 자동 변경하지 않는다.

## 사용·갱신 범위

관련 기술을 사용할 때 해당 절만 읽는다. 참고 등록은 설치·인증·운영 접근 권한이 아니다. 실제 도입 시 선택한 커밋/배포와 필요한 부모·참고 파일·실행기·의존성·라이선스 변경을 다시 검수하고, 이미 허용된 범위에서 설치와 대표 시험을 진행한다. 같은 역할을 동시에 발동시키거나 전체 저장소를 일괄 설치하지 않는다.

이번 편입물은 독자적인 한국어 검토 기록과 외부 링크다. 새 외부 스킬 원문·실행 코드·데이터를 복제하지 않았다. 위 지정 파일 이외의 전체 스킬·공급망 감사·서비스 실제 작동까지 검증한 것은 아니다. 공통 절차의 로컬 합성 DB 시험과 공급자별 실전 검증은 별개다.
