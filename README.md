# minwoo-codex-kit

내 Codex 공통 규칙과 자주 쓰는 작업 절차를 관리하는 개인용 저장소.
새 PC에는 공통 규칙과 필요한 스킬만 설치하고, 프로젝트에는 그 프로젝트의 사실만 추가한다.

## 구성

```text
global/AGENTS.md                  공통 규칙 원본
skills/minwoo-project-context/    프로젝트 AGENTS.md 작성·갱신
skills/minwoo-publication-review/ 공개 전 읽기 전용 점검
templates/AGENTS.md               새 프로젝트용 시작 문서
scripts/install.ps1              Windows 설치 진입점
scripts/install.sh               Unix 계열 설치 진입점
scripts/install.py               공통 설치 로직
tests/                           격리된 설치·복구 테스트
docs/DESIGN.md                   설계 이유, 참고 출처와 경로 확인
docs/VALIDATION.md               이번 배포본의 검증 기록
docs/SKILL-CATALOG.md            선택형 외부 스킬·원본·설치 및 갱신 안내
docs/SKILL-REVIEW.md             수집 자료의 사용 근거와 편입 결정
docs/candidates/                의존성 정리가 필요한 재사용 후보
```

전역 규칙은 항상 적용할 작업 원칙이다. 스킬은 작업이 맞을 때만 본문을 읽는다.
프로젝트 문서에 공통 규칙이나 스킬 전체를 다시 붙이지 않는다.
저장소 주소를 대화에 보여주는 것만으로 모든 프로젝트에 영구 설치되지는 않는다.

## 준비

- Python **3.10 이상**. 외부 Python 패키지는 필요 없다.
- Windows PowerShell 5.1 이상 또는 PowerShell 7. Unix에서는 POSIX `sh`.
- GitHub에서 내려받고 갱신할 때는 Git 또는 GitHub의 ZIP 다운로드를 사용한다.
- 설치 파일은 검토한 로컬 복사본에서 실행한다. 관리자 권한은 필요 없다.

새 PC에서 내려받기:

```powershell
git clone https://github.com/minwoo-106/minwoo-codex-kit.git
cd minwoo-codex-kit
```

이 폴더나 ZIP을 그대로 옮겨도 된다.

## 새 PC에 설치 — Windows

먼저 미리보기로 경로와 변경 대상을 확인한다. 미리보기는 폴더·백업·상태 파일도 만들지 않는다.

```powershell
.\scripts\install.ps1 -Skills minwoo-project-context,minwoo-publication-review -DryRun
.\scripts\install.ps1 -Skills minwoo-project-context,minwoo-publication-review
```

기본 경로:

| 대상 | 설치 위치 |
| --- | --- |
| 전역 규칙 | `$CODEX_HOME/AGENTS.md`, 미설정이면 `~/.codex/AGENTS.md` |
| 개인 스킬 | `~/.agents/skills/<스킬명>/` |
| 설치 상태·백업 | 전역 규칙 폴더의 `.minwoo-codex-kit/` |

`-Skills`를 생략하면 규칙만 설치한다. 이미 전역 규칙을 따로 관리한다면 `-SkipRules`로 스킬만 설치한다.
설치 후 새 Codex 대화에서 적용을 확인하고, 스킬이 안 보이면 Codex를 재시작한다.

PowerShell 실행 정책 때문에 스크립트가 차단되면 정책을 바꾸지 않고 Python 진입점을 쓸 수 있다.

```powershell
python .\scripts\install.py --skill minwoo-project-context --skill minwoo-publication-review --dry-run
python .\scripts\install.py --skill minwoo-project-context --skill minwoo-publication-review
```

설치 경로를 직접 정하는 예:

```powershell
.\scripts\install.ps1 -CodexHome 'D:\CodexProfile' -SkillsRoot 'D:\CodexSkills' -Skills minwoo-project-context -DryRun
```

`-CodexHome`은 환경 변수보다 우선한다. `CODEX_HOME`은 개인 스킬의 공식 기본 경로를 바꾸지 않는다.
`-SkillsRoot`는 파일을 복사할 위치만 바꾸므로, Codex가 읽는 경로를 지정해야 한다.
현재 PC처럼 기존 `~/.codex/skills`를 쓰는 환경에서는 그 경로를 명시할 수 있다.
기존 경로를 자동 이동하거나 같은 스킬을 여러 경로에 중복 설치하지 않는다.
`config.toml`, 승인 모드, 인증 정보, MCP·플러그인 설정은 설치 대상에 포함하지 않는다.

## 새 프로젝트에 적용

전역 규칙을 설치한 PC에서는 새 프로젝트에도 공통 규칙이 적용된다.
프로젝트 전용 스킬이 필요한 경우에만 로컬 스킬을 추가한다. 전역과 로컬에 같은 이름을 설치하면 중복 표시될 수 있다.

새 프로젝트 폴더가 이미 있는 경우, 시작 문서를 만드는 예:

```powershell
.\scripts\install.ps1 -Scope Project -ProjectPath 'D:\projects\my-project' -DryRun
.\scripts\install.ps1 -Scope Project -ProjectPath 'D:\projects\my-project'
```

시작 문서는 빈 프로젝트 항목을 제공하며 실제 환경 설정을 완성한 문서는 아니다.
개인 스킬로 설치한 `$minwoo-project-context`를 호출해 실제 코드에 맞춰 내용을 채울 수 있다.

기존 팀 프로젝트의 규칙을 유지하면서 스킬만 추가하는 예:

```powershell
.\scripts\install.ps1 -Scope Project -ProjectPath 'D:\projects\my-project' -SkipRules -Skills minwoo-project-context -DryRun
.\scripts\install.ps1 -Scope Project -ProjectPath 'D:\projects\my-project' -SkipRules -Skills minwoo-project-context
```

프로젝트 스킬은 `<프로젝트>/.agents/skills/`, 설치 상태·백업은 `<프로젝트>/.minwoo-codex-kit/`에 둔다.
**프로젝트의 `.gitignore`에 `.minwoo-codex-kit/`를 추가한다.** 백업에는 기존 개인·회사 자료가 들어갈 수 있다.
설치기는 기존 `.gitignore`를 수정하지 않는다. 프로젝트 스킬과 `AGENTS.md`를 팀에 공유할지는 팀 정책을 따른다.
`-Scope Project`는 개인 전역 파일을 변경하지 않으며 `-CodexHome`·`-SkillsRoot`와 함께 사용할 수 없다.

## 기존 파일, 갱신, 복구

- 처음 만나는 파일이 원본과 다르거나, 이전 설치 이후 로컬에서 고친 파일이면 전체 설치를 중단한다. 내용과 설치 상태를 먼저 확인한다.
- 바이트가 같으면 파일을 다시 쓰지 않는다. 같은 설치를 반복해도 파일 수정 시각·상태·백업이 불필요하게 바뀌지 않는다.
- 이전 설치본 그대로인 파일은 새 원본으로 갱신할 수 있다. 교체 전 내용은 항상 백업한다.
- 로컬 수정 내용을 원본에 반영하거나 수동으로 합치는 것을 우선한다. **차이를 확인한 뒤 전체 교체를 원하는 경우에만** `-ReplaceExisting` / `--replace-existing`를 붙인다.
- 선택하지 않은 스킬, 다른 파일, 원본에서 사라진 파일은 자동 삭제하지 않는다. 스킬에서 폐기한 파일이 있으면 설치된 복사본도 별도로 검토한다.
- `AGENTS.override.md`가 있으면 우선 적용될 수 있다는 경고를 낸다. 기존 override를 삭제하거나 고치지 않는다.
- 링크·Windows 정션·reparse point가 포함된 경로와 원본/설치 경로 중첩은 거절한다. 실제 폴더 경로를 사용한다.

갱신은 자동 실행되지 않는다. 원본 저장소를 수정한 뒤에는 요청한 범위에서 검증·커밋·푸시한다.
다른 PC에서는 저장소 폴더에서 작업 상태를 확인하고, 로컬 변경이 없을 때 갱신한다.

```powershell
git status --short
```

출력이 비어 있는지 확인한 뒤:

```powershell
git pull --ff-only
.\scripts\install.ps1 -Skills minwoo-project-context,minwoo-publication-review -DryRun
.\scripts\install.ps1 -Skills minwoo-project-context,minwoo-publication-review
```

사용했던 설치 대상·스킬 선택·경로 옵션을 다시 지정한다. 자동으로 새 스킬 전체를 추가하지 않는다.
전역 규칙은 `global/AGENTS.md`, 스킬은 해당 `skills/<이름>/`에서 편집한다.
설치된 파일만 고친 경우 다음 갱신 시 충돌로 알려준다.

백업은 `.minwoo-codex-kit/backups/<실행 식별자>/`에 남고, `restore-map.json`이 원래 경로와 `.bak` 파일의 대응을 기록한다.
수동 복구가 필요하면 설치기를 멈춘 상태에서 대응 파일의 현재 내용과 백업을 비교한 뒤 원하는 파일만 복사한다.
이후 원본 저장소에도 원하는 내용을 반영해 재설치한다. 상태 파일을 임의로 고쳐 충돌 검사를 우회하지 않는다.

실행 중 일반적인 쓰기 실패가 발생하면 이번 실행의 변경을 되돌리고 백업을 남긴다.
다른 프로그램이 그 사이 수정한 파일은 자동 복구로 덮어쓰지 않고 수동 확인 대상으로 알린다.
프로세스 강제 종료·정전에는 전체 설치의 원자성을 보장하지 않는다. 남은 잠금은 실행 중인 설치기가 없는지 확인한 뒤 처리한다.
설치 대상의 동시 편집은 피한다. 해시와 링크 확인은 악의적인 동시 파일 교체에 대한 보안 경계는 아니다.

## Unix 계열

같은 설치 로직을 `sh`로 실행한다. 실행 권한 설정은 필요 없다.

```sh
sh scripts/install.sh --skill minwoo-project-context --skill minwoo-publication-review --dry-run
sh scripts/install.sh --skill minwoo-project-context --skill minwoo-publication-review
sh scripts/install.sh --scope project --project /path/to/existing-project --dry-run
```

원본·개인 경로가 심볼릭 링크로 구성된 환경에서는 실제 경로를 명시해야 한다.
운영체제별 실제 검증 범위는 [검증 기록](docs/VALIDATION.md)을 참고한다.

## 스킬 추가와 검증

여러 대화에서 사용한 스킬은 [스킬 카탈로그](docs/SKILL-CATALOG.md)에 검수해 정리했다.
외부 스킬 11개는 확인한 원본 커밋·라이선스·설치 조건으로 관리하고, 기본 제공·플러그인 7개는 해당 환경에서 관리한다.
실제 사용 보고와 일부 절차만 수행한 사례는 [검토 기록](docs/SKILL-REVIEW.md)에 구분했다.
영상 검토용 [studio-review 후보](docs/candidates/studio-review.md)는 전용 실행 코드가 필요해 설치 대상에서 제외했다.

**이 kit가 설치하는 스킬은 위의 자체 스킬 두 개다.**
외부 스킬을 모두 자동 설치하지 않으며, 기존 설치·플러그인과 중복되지 않게 필요한 것만 선택한다.
외부 스킬의 본문을 전역 규칙에 붙이지 않고, 사용자 확인을 요구하는 원본 절차가 있는지도 선택 전에 확인한다.

반복되는 작업이 생겼을 때만 `skills/<이름>/SKILL.md`를 추가한다.
YAML 머리말의 `name`은 폴더명과 맞추고 `description`에는 사용할 상황을 짧게 적는다.
공통 원칙을 다시 쓰지 말고 해당 작업에서 판단을 바꾸는 정보만 넣는다. 긴 참고 자료는 필요할 때 읽도록 분리한다.

```powershell
python -m unittest discover -s tests -v
```

테스트는 실제 개인 설정과 분리된 임시 폴더에서 실행한다.
제한된 환경의 임시 폴더 권한이나 Windows 경로 길이 문제가 있으면 짧고 쓰기 가능한 테스트 폴더를 지정한다.

```powershell
$env:KIT_TEST_ROOT = Join-Path (Get-Location) 'work'
New-Item -ItemType Directory -Path $env:KIT_TEST_ROOT -Force | Out-Null
python -m unittest discover -s tests -v
```

호스트가 정션·심볼릭 링크 생성을 허용하지 않으면 해당 실제 파일시스템 테스트는 건너뛴 것으로 표시한다.

## 공개 범위와 참고

이 저장소에는 일반적인 개인 작업 원칙·직접 작성한 스킬·설치 코드와 공개 가능한 출처·검토 기록을 둔다.
실제 `.codex` 폴더 전체, 인증 파일, 설정 원본, 대화 기록, 개인 경로, 회사 전용 규칙·스킬·자료는 넣지 않는다.
`.gitignore`는 이미 추적한 파일이나 Git 이력의 비밀정보를 지우지 않는다. 공개 전 `$minwoo-publication-review` 등으로 대상 파일과 이력을 확인한다.

[jongwony/cc-plugin](https://github.com/jongwony/cc-plugin)과
[jongwony/epistemic-protocols](https://github.com/jongwony/epistemic-protocols)의 구조와 필요 시 절차를 선택하는 철학을 참고했다.
코드·스킬 본문·설치 스크립트는 가져오지 않았다. 세부 출처와 공식 문서는 [설계 기록](docs/DESIGN.md)에 있다.
GitHub 저장소 생성·공개 범위·푸시는 소유자가 결정한다. 공개와 별개로 재배포 라이선스는 아직 지정하지 않았다.
