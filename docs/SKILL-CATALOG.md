# 선택형 외부 스킬 카탈로그

검토일: 2026-10-29. 사용자 제공 조사 자료 네 건을 중복 제거하고 공개 원본의 파일·참고 자료·라이선스를 확인했다.
과거 사용 여부는 **제공된 조사 보고의 근거 수준**이며, 아래 커밋은 이번에 확인한 공개 원본이다.
과거 설치 당시 버전이나 현재 설치본과 동일하다고 단정하지 않는다.

## 먼저 고르기

- 작업 시 선택 기준은 [Codex용 분야별 안내](../skills/minwoo-skill-curation/references/routing.md)를 사용한다. 이 문서의 아래 목록은 출처·배포·설치 검토 기록이며 최신 선택 기준을 중복 유지하지 않는다.
- 일반 작업은 전역 규칙을 기본으로 하고 [자체 스킬](NEW-SKILLS.md)은 해당 작업에 맞을 때 선택한다. 분야별 주도·보조 역할은 위 선택 안내에서 관리한다.

0.3.0에서 추가한 8개는 [검수·역할 분리 표](ADOPTED-SKILLS.md)에 정리했다. React 성능/구조는 기존 UI 스킬을 대체하지 않고 해당 문제에서만 선택한다.

이는 선택 안내이며 자동 라우터나 모든 UI 작업의 의무 절차가 아니다.
0.5.0부터 diagnosing-bugs는 기존 내용을 보존한 kit 관리 스킬이며 CI 조사 참조가 추가됐다. [확장 검수](WORKFLOW-REVIEW.md)를 따른다.
현재 요청과 프로젝트 지침이 우선하고, 외부 스킬이 승인 모드·권한을 확대하지 않는다.
이미 합의된 내용을 다시 묻도록 공통 규칙을 늘리지 않는다.

## 검토한 11개

| 스킬 | 사용할 상황 | 제공 자료의 근거 | 의존성·주의할 차이 |
| --- | --- | --- | --- |
| tdd | 테스트부터 구현할 때만 선택 | 사용 보고 | 테스트 경계를 먼저 사용자와 확인하는 원문 절차가 있어 기본 설치에서 제외. 기존 합의 범위와 현재 요청을 우선하며 단계마다 재승인을 요구하는 공통 규칙으로 가져오지 않는다. |
| diagnosing-bugs | 재현이 어려운 오류·성능 문제 | 사용 보고, 별도 자료 한 건은 요약 근거 | 재현 루프에 집중. 일반 수정마다 강제하지 않는다. 보조 HITL 스크립트는 Bash 환경이 필요하며 운영 환경 접근 권한을 주지 않는다. |
| codebase-design | 모듈 경계·인터페이스 설계 | 사용 보고 | 단순 수정에는 생략. 대안 비교 참고 문서에는 병렬 에이전트 절차가 있으므로 사용 환경과 요청 범위를 확인한다. |
| prototype | 설계 질문을 검증하는 임시 구현 | 사용 보고 | 완성 제품과 구분하고 완료 기준을 질문에 한정한다. LOGIC.md·UI.md를 함께 유지한다. |
| frontend-design | 새 UI의 시각 방향을 정할 때 | 사용 보고 | 가벼운 디자인 지침 선택지. 주제가 불명확할 때 확인을 요구하는 절차가 있다. 다른 디자인 주도 스킬과 중복 적용하지 않는다. |
| impeccable | 기존 UI 개선·접근성·완성도 검토 | 사용 보고 | 참고 문서와 실행기가 함께 필요. 실행기가 바이너리를 내려받을 수 있고 프로젝트 문서·훅 관련 기능도 있다. 이번에는 실행·설치·훅 검증을 하지 않았다. |
| design-taste-frontend | 랜딩 페이지·브랜드 표현이 중심일 때 | 문구 관련 일부 절차 사용 보고 | Node 22+와 Chrome·Edge·Chromium 필요. 이미지 검색은 네트워크를 사용한다. 전체 시각 검수 흐름을 실행한 이력으로 간주하지 않는다. |
| ui-ux-pro-max | 색상·서체·UX 근거를 검색할 때 | 검색 스크립트 실행 보고 | Python과 데이터·참고 문서가 필요. Claude용 원본을 직접 설치하지 않고 Codex용 생성 경로를 사용한다. |
| 21st-cli-use | 21st에서 필요한 구성 요소를 찾을 때 | 설치·로그인 상태 확인 보고 | 콘텐츠 검색·가져오기 성공은 확인되지 않았다. Node/npm·CLI·서비스 인증 및 기능별 이용 조건을 별도로 확인한다. |
| 21st-ui-build | 21st를 활용하는 기존 프로젝트 UI 구현 | 일부 안내 적용 보고 | 프로젝트 구성 요소를 우선 재사용. 전체 검색→구현→검증 흐름의 성공 이력으로 확대하지 않는다. |
| 21st-ui-review | 21st 도구를 쓰는 UI 검토 | CLI 실행 보고 | 주관적 디자인 의견과 재현 가능한 결함을 구분. 현재 PC 외 환경에서 동일 CLI 실행을 검증하지 않았다. |

## 확인한 원본

아래 링크는 변경되지 않는 커밋을 가리킨다. **목록 수록은 자동 설치나 전체 실행 검증을 뜻하지 않는다.**
원문·스크립트·데이터는 이 저장소에 복제하지 않았다.

| 스킬 | 공개 원본 폴더 | 확인한 라이선스 |
| --- | --- | --- |
| `tdd` | [mattpocock/skills · skills/engineering/tdd](https://github.com/mattpocock/skills/tree/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/tdd) | [MIT](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/LICENSE) |
| `diagnosing-bugs` | [mattpocock/skills · skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/diagnosing-bugs) | [MIT](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/LICENSE) |
| `codebase-design` | [mattpocock/skills · skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/codebase-design) | [MIT](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/LICENSE) |
| `prototype` | [mattpocock/skills · skills/engineering/prototype](https://github.com/mattpocock/skills/tree/59db609eb1e18aaf59b63284d0e52255aff0c63c/skills/engineering/prototype) | [MIT](https://github.com/mattpocock/skills/blob/59db609eb1e18aaf59b63284d0e52255aff0c63c/LICENSE) |
| `frontend-design` | [anthropics/skills · skills/frontend-design](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design) | [Apache-2.0](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/frontend-design/LICENSE.txt) |
| `impeccable` | [pbakaus/impeccable · .agents/skills/impeccable](https://github.com/pbakaus/impeccable/tree/5e745ace7e151feb2a93d360d0281fe39448b857/.agents/skills/impeccable) | [Apache-2.0](https://github.com/pbakaus/impeccable/blob/5e745ace7e151feb2a93d360d0281fe39448b857/LICENSE) |
| `design-taste-frontend` | [Leonxlnx/taste-skill · skills/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill) | [MIT](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/LICENSE) |
| `ui-ux-pro-max` | [nextlevelbuilder/ui-ux-pro-max-skill · .claude/skills/ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/.claude/skills/ui-ux-pro-max) | [MIT](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/LICENSE) |
| `21st-cli-use` | [21st-dev/codex-plugin · skills/21st-cli-use](https://github.com/21st-dev/codex-plugin/tree/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/skills/21st-cli-use) | [Apache-2.0](https://github.com/21st-dev/codex-plugin/blob/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/LICENSE) |
| `21st-ui-build` | [21st-dev/codex-plugin · skills/21st-ui-build](https://github.com/21st-dev/codex-plugin/tree/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/skills/21st-ui-build) | [Apache-2.0](https://github.com/21st-dev/codex-plugin/blob/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/LICENSE) |
| `21st-ui-review` | [21st-dev/codex-plugin · skills/21st-ui-review](https://github.com/21st-dev/codex-plugin/tree/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/skills/21st-ui-review) | [Apache-2.0](https://github.com/21st-dev/codex-plugin/blob/c0505c7f1c2d9cea6db05e44892b61cb7ce35334/LICENSE) |

라이선스 열은 해당 원본의 명시된 라이선스를 확인한 기록이다. 검색으로 가져오는 이미지·폰트·구성 요소·서비스 결과의 이용 조건까지 포함하지 않는다.
나중에 원문이나 코드를 재배포하면 해당 LICENSE·NOTICE·저작권 고지와 변경 표시 의무를 별도로 검토한다.
원본 경로가 확인된 `codebase-design`·`prototype`도 과거 설치 출처까지 역으로 확정한 것은 아니다.

## 설치 경로 선택

kit의 `scripts/install.ps1`은 **이 저장소의 skills/에 포함된 19개 중 선택한 것만** 설치한다. 카탈로그에만 있는 외부 이름을 `-Skills`에 넣지 않는다.
먼저 기존 `~/.agents/skills`, 기존 환경의 `~/.codex/skills`, 프로젝트 `.agents/skills`, 설치된 플러그인에 같은 스킬이 있는지 확인한다.

새 PC에서 외부 스킬이 필요할 때는 이 문서의 스킬 이름·원본 링크를 지정해 `$skill-installer`에 요청할 수 있다.
스킬 한 파일만 복사하지 말고 해당 폴더의 참고 문서·스크립트·데이터를 함께 확인한다.
기존 설치와 같은 이름이 있으면 먼저 출처와 로컬 변경을 비교한다.

다음은 제공된 공식 설치 도우미가 있는 환경에서 **tdd 하나를 선택해 설치하는 예시**다.
기본 권장 묶음이 아니며 위의 확인 절차를 검토한 뒤 사용한다.
도우미의 기본 대상은 Codex 홈 아래 `skills`이므로 여기서는 대상 경로를 명시한다.

```powershell
$kitCodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillInstaller = Join-Path $kitCodexHome 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
$skillDestination = Join-Path $HOME '.agents/skills'
if (-not (Test-Path -LiteralPath $skillInstaller -PathType Leaf)) {
    throw '이 환경에서 skill-installer 도우미를 찾을 수 없음. 설치된 스킬 안내를 확인하세요.'
}
python $skillInstaller --repo mattpocock/skills --ref 59db609eb1e18aaf59b63284d0e52255aff0c63c --path skills/engineering/tdd --dest $skillDestination
if ($LASTEXITCODE -ne 0) { throw '스킬 설치 실패. 출력과 기존 대상 폴더를 확인하세요.' }
```

Unix에서도 같은 Python 도우미의 `--repo`, `--ref`, `--path`, `--dest`를 사용하며 실제 Codex 홈 경로를 지정한다.
현재 도우미의 인수와 기존 대상 거절 동작을 코드로 확인했다. 이번 검토에서 외부 스킬 설치는 실행하지 않았다.
도우미가 없는 환경에서는 설치된 `skill-installer`의 안내를 확인한다.

개별 선택 시 주의:

- `design-taste-frontend` 원본 폴더명은 `taste-skill`이다. 도우미를 사용한다면 `--name design-taste-frontend`로 설치 이름을 맞춘다.
- `ui-ux-pro-max`의 표에 연결된 `.claude` 폴더는 출처 확인용이다. 본문이 `CLAUDE_PLUGIN_ROOT`를 참조하므로 그대로 복사하는 범용 예시를 제공하지 않는다.
  [공식 CLI 안내](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/cli/README.md)의 `uipro init --ai codex` 생성 흐름을 사용한다.
  [Codex 템플릿](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/src/ui-ux-pro-max/templates/platforms/codex.json)은 프로젝트 `.agents/skills/ui-ux-pro-max`를 지정한다.
  CLI 패키지 버전은 별도로 선택·기록해야 하며 위 소스 커밋이 npm 패키지까지 고정하지 않는다. 이 생성 흐름의 실행 검증은 아직 하지 않았다.
- `impeccable` 실행기와 21st CLI 등 외부 실행 파일은 스킬 소스 커밋을 고정해도 함께 고정되지 않을 수 있다. 실제 실행 버전·다운로드 출처를 확인한다.
- 설치 후 새 대화에서 스킬을 확인하고, 필요한 경우 Codex를 재시작한다. 플러그인 경로의 스킬은 해당 플러그인의 설치·갱신 기능을 사용한다.

## 외부 스킬 갱신

이 카탈로그는 설치 상태 파일이나 일괄 업데이트 도구가 아니다.

1. 현재 설치 위치·출처·버전·직접 수정 여부를 확인한다.
2. 원본의 새 커밋에서 발동 조건, 승인 요구, 실행 파일·네트워크 접근, 라이선스 변경을 비교한다.
3. 기존 설치와 분리된 임시 폴더에 필요한 폴더 전체를 내려받아 차이와 필수 파일을 확인한다. 공식 도우미는 기존 대상에 덮어쓰지 않으며 업데이트 관리자가 아니다.
4. 간단한 대표 작업으로 검증하고, 기존 파일을 백업한 뒤 검토한 변경만 반영한다. 로컬 수정을 잃는 강제 교체나 플러그인 캐시 직접 수정은 하지 않는다.
5. 이 문서의 커밋 링크·검토일·미검증 범위를 갱신한다. 설치 PC의 절대 경로나 인증 정보는 개인 기록에만 둔다.

## 환경에서 제공하는 7개

| 분류 | 이름 | 관리 방식 |
| --- | --- | --- |
| 기본 제공·시스템 | `skill-creator`, `skill-installer`, `imagegen`, `openai-docs` | 새 환경에서 제공 여부 확인. 자체 복사본을 kit에 넣지 않고 해당 환경의 버전을 사용 |
| 플러그인 | `pdf:pdf`, `sites:sites`, `plugin-management:plugin-management` | 해당 플러그인의 설치·연결·갱신 기능 사용. 필요한 도구가 노출되는지 확인 |

네 자료에는 위 7개 모두 사용 보고가 있다. 새 환경에서 항상 제공된다고 보장하지 않는다.
SKILL.md를 복사하는 것만으로 이미지 생성, 사이트 게시, 플러그인 관리 등의 도구나 권한이 생기지 않는다.
현재 설치된 plugin-management 메타데이터는 `Proprietary`로 표시되어 있어 본문을 재배포하지 않는다.
다른 기본 제공·플러그인도 설치 캐시를 통째로 공개하지 않는다.

직접 작성 후보의 검토는 [studio-review 후보](candidates/studio-review.md), 전체 판단 기록은 [스킬 검토 기록](SKILL-REVIEW.md)을 참고한다.
