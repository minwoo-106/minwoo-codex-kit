# 0.3.0 외부 후보 검수와 적용

검토일: 2026-10-29. 필요한 것을 모아 두되 전역 규칙은 늘리지 않고, 같은 일을 하는 기존 스킬은 유지했다.

| 추가 스킬 | 사용할 때 | 겹침을 피한 범위 |
| --- | --- | --- |
| minwoo-diff-walkthrough | 변경을 단계별 HTML로 설명 | 일반 code-review를 대체하지 않음 |
| minwoo-dependency-audit | 패키지 공급망·유지보수·취약점 조사 | 코드 보안 전체 감사·자동 업데이트와 분리 |
| minwoo-property-testing | 불변식·왕복 관계·경계값 테스트 | tdd·일반 테스트에 강제되지 않음 |
| minwoo-react-performance | React/Next.js 병목·번들·요청 개선 | 일반 UI 제작·미적 디자인과 분리 |
| minwoo-react-composition | React 공개 API·옵션·상태 공유 구조 | 작은 스타일 수정·성능 측정과 분리 |
| minwoo-postgres-review | PostgreSQL 쿼리·인덱스·RLS 검토 | 운영 DB 자동 수정·일상 데이터 조회와 분리 |
| minwoo-release-notes | 커밋 범위의 사용자용 변경 기록 | work-handoff·배포·GitHub Release 게시와 분리 |
| minwoo-remotion-render | 기존 Remotion 자막·로컬 렌더 | video-review·AI 생성·음성 인식과 분리 |

## 채택 방식과 출처

- [Trail of Bits](https://github.com/trailofbits/skills/tree/2be6433b39e009cd2b6fd3be1895f6b1faa5af9a/plugins): walkthrough 도구·HTML, supply-chain 도구·테스트, property testing 참고 문서를 필요한 폴더만 포함했다. 각 폴더에 CC-BY-SA-4.0 원문과 저작자·변경 표시를 동봉했다. 감사 도구 테스트의 POSIX 가정을 Windows에서도 명시적으로 모사하도록 보완했다.
- [Vercel](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills): React 성능·composition 규칙을 개별 문서로 포함했다. 중복된 대형 AGENTS.md 합본은 제외했다. 각 원본 SKILL.md의 MIT 선언과 저작자를 기록했다.
- [Supabase](https://github.com/supabase/agent-skills/tree/c9be0e931b7930f7d02126d04774d904c381e7d7/skills/supabase-postgres-best-practices): 실제 쿼리·스키마·권한 참고 문서만 포함하고 MIT 고지를 보존했다.
- 릴리스 노트는 독자적으로 작성했다. Composio 후보에서 재배포 라이선스를 확인하지 못해 본문을 복사하지 않았다.
- Remotion은 [공식 문서](https://www.remotion.dev/docs/renderer/render-media)와 [공식 자막 API](https://www.remotion.dev/docs/captions/parse-srt)를 바탕으로 독자적으로 작성했다. 플러그인 검색에서 사용 가능한 설치 경로를 확인하지 못해, 검증 가능한 로컬 도구와 좁은 절차를 제공한다. 플러그인 캐시를 복사하지 않았다.

원본별 파일 경로·커밋·Git blob 식별자는 [upstream-files.json](upstream-files.json)에 있다. 각 스킬 폴더의 UPSTREAM.md와 LICENSE가 해당 폴더의 재배포 조건을 기록한다. 독립적인 kit 전체를 하나의 외부 라이선스로 재지정하지 않았다.

## 포함하지 않은 묶음

- awesome 목록 전체: 발견용 색인이지 품질 보증이나 실행 가능한 단일 스킬이 아니다.
- Superpowers 전체: 기존 tdd·diagnosing-bugs·계획 절차와 겹치고 일괄 승인 흐름이 사용자 방식과 맞지 않았다.
- 일반 웹/UI 감사·디자인 스킬: 이미 보유한 UI 스킬과 역할 중복.
- Copilot 전용 지침·Antfu의 폭넓은 프레임워크 묶음: 플랫폼·프로젝트 전제가 달라 일괄 설치하지 않았다. 필요한 기술을 실제 사용할 때 개별 검토한다.
- Composio gh-fix-ci: 추가 계획 스킬 의존과 승인 절차 중복. 기존 GitHub 도구·디버깅 절차로 처리할 수 있다.
- 대형 전사 모델·클라우드 영상 생성·게시 도구: 이번 로컬 자막/렌더 작업의 필수 의존성이 아니므로 자동 설치하지 않았다.

## 설치와 선택

```powershell
python scripts/install.py --skip-rules --skill minwoo-diff-walkthrough --skill minwoo-dependency-audit --skill minwoo-property-testing --skill minwoo-react-performance --skill minwoo-react-composition --skill minwoo-postgres-review --skill minwoo-release-notes --skill minwoo-remotion-render --dry-run
```

미리보기 확인 후 같은 명령에서 --dry-run을 뺀다. 기존 ~/.codex/skills 환경은 --skills-root로 그 경로를 명시하고, 기본 ~/.agents/skills와 중복 설치하지 않는다. 선택 도구는 [별도 설치](TOOLS.md)한다.

새 대화에서 필요한 스킬이 노출되는지 확인한다. 이름이 보이지 않으면 Codex를 재시작한다. 스킬은 설정·권한을 부여하지 않으며 현재 승인 방식은 그대로 따른다.

## 발동 범위 검토 예

- “랜딩 페이지 색상만 바꿔줘” → 기존 UI 절차. 두 React 추가 스킬을 한꺼번에 읽을 이유 없음.
- “React 검색창 입력 때 목록이 느려” → performance, 실제 원인 진단. 구조 변경이 필요하다는 근거가 생긴 경우에만 composition 추가.
- “다른 테넌트 자료가 보이는 RLS를 검토해줘” → postgres-review. 운영 쿼리 자동 실행으로 확장하지 않음.
- “v1에서 v2까지 사용자 변경점을 써줘” → release-notes. “다음 채팅에서 이어가게”는 기존 work-handoff.
- “두 영상의 같은 컷을 비교해줘” → 기존 video-review. “SRT 넣고 MP4 렌더해줘” → remotion-render.

이 예시는 발동 설명의 수동 검토 기록이다. 새 Codex 세션에서 모델의 자동 선택을 평가한 결과로 주장하지 않는다.
