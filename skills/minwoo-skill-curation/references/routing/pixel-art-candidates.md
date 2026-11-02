# 도트·픽셀 아트 참고 선반

검토일: 2026-11-02. 상태: **외부 참고 후보 / 설치·실행 검증 전**.
공식 README·라이선스·선택한 설정/스킬과 커밋 정보를 확인했다. 원본 코드·이미지·폰트·스킬 본문은 kit에 복제하지 않았다. 이 문서는 설치되거나 연결된 도구의 목록이 아니다.

## 필요할 때 고르기

| 필요한 결과 | 참고 후보 | 기존 기능과의 경계 |
| --- | --- | --- |
| 불꽃·얼음·번개·검격 등 코드로 조절하는 픽셀 이펙트 | pixelfx | 효과 제작·변형·시트 출력. 일반 원화나 임의 캐릭터 디자인 전체를 대신하지 않음 |
| 도트 원화·타일·프레임별 애니메이션 편집 | Pixelorama | 직접 편집하는 앱. 이미지 생성 서비스나 자동 선택되는 스킬이 아님 |
| 여러 PNG를 텍스처 아틀라스·스프라이트 시트로 포장 | free-tex-packer-core | 이미 있는 그림을 배치·내보내는 라이브러리. 새 그림·이펙트를 생성하지 않음 |

단순 픽셀 이미지 생성은 현재 imagegen 지침, 기존 SVG·코드 자산 수정은 해당 프로젝트 도구를 우선한다. ChatGPT 펫 요청은 work-pets의 전용 규격·검증 흐름을 따른다. pixelfx 시트를 곧바로 펫에 업로드할 수 있다고 가정하지 않는다. pixelfx나 기존 엔진만으로 필요한 시트가 나오면 별도 포장 도구를 추가하지 않는다.

## pixelfx

- 원본: [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx). 확인 커밋: `a84159688af3ca37a4be05a0d422b94451b2e24e`, 해당 커밋 일자 2026-10-31. 조사 시 archived=false.
- [README](https://github.com/patch-gg/pixelfx/blob/a84159688af3ca37a4be05a0d422b94451b2e24e/README.md): 코드 기반 픽셀 효과, 색상·방향·시드 변경, 브라우저 게임 사용과 PNG+JSON 시트 출력을 제공한다.
- [스킬 원문](https://github.com/patch-gg/pixelfx/blob/a84159688af3ca37a4be05a0d422b94451b2e24e/skills/pixelfx/SKILL.md)은 Claude Code 기준이다. Node.js 18+, GIF/MP4 미리보기에는 선택적 ffmpeg를 명시한다. 원본 저장소 작업, 시안 렌더·화면 검토·반복 개선 절차를 포함한다. 즉시 복사·발동하는 Codex 스킬로 등록하지 않았다.
- [LICENSE](https://github.com/patch-gg/pixelfx/blob/a84159688af3ca37a4be05a0d422b94451b2e24e/LICENSE)는 코드·이펙트에 MIT를 명시한다. [NOTICE](https://github.com/patch-gg/pixelfx/blob/a84159688af3ca37a4be05a0d422b94451b2e24e/NOTICE.md)의 원저작자 고지를 보존해야 하며 gallery/fonts의 Patch Pixel 폰트는 MIT 적용 대상에서 제외돼 있다.
- 실제 도입 때: 검토한 버전으로 분리된 작업 사본을 준비하고 효과 하나를 렌더해 투명도·팔레트·루프·프레임 시간·피벗을 확인한다. 엔진 연결까지 요청됐다면 실제 엔진에서 재생해 본다. 원문의 자동 clone·시안 정리·고정 반복 횟수는 현재 요청과 기존 작업 보호 원칙에 맞춰 검토한다.

## Pixelorama

- 원본: [Orama-Interactive/Pixelorama](https://github.com/Orama-Interactive/Pixelorama). 확인 커밋: `fae9327992f1506f340b920e0fa6515a88298079`, 해당 커밋 일자 2026-10-27. 조사 시 archived=false.
- [README](https://github.com/Orama-Interactive/Pixelorama/blob/fae9327992f1506f340b920e0fa6515a88298079/README.md): 레이어·프레임·타임라인·타일맵·팔레트 편집과 PNG/시트/GIF 등의 입출력을 제공한다. Windows·Linux·macOS·웹 배포 경로가 있다. 소스에서 실행하려면 해당 커밋의 Godot 버전 요구를 확인한다.
- [LICENSE](https://github.com/Orama-Interactive/Pixelorama/blob/fae9327992f1506f340b920e0fa6515a88298079/LICENSE)는 MIT다. 추가로 가져오는 폰트·팔레트·확장·외부 그림의 조건까지 확인했다고 주장하지 않는다.
- 실제 도입 때: 공식 안정 배포를 선택하고 작은 프로젝트의 저장·재열기·PNG/시트 출력부터 확인한다. 앱 자동 조작이 필요하면 현재 제공되는 컴퓨터 사용 도구와 지침을 따르며 전용 MCP가 있다고 가정하지 않는다.

## free-tex-packer-core

- 원본: [odrick/free-tex-packer-core](https://github.com/odrick/free-tex-packer-core). 확인 커밋: `f918f61569e669df61825ec1040540f1d8470acb`, 해당 커밋 일자 2026-07-24. 조사 시 archived=false.
- [README](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/README.md): PNG 배치, 패딩·회전·트리밍과 여러 엔진용 메타데이터 출력을 제공하는 Node.js 라이브러리다.
- [LICENSE.md](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/LICENSE.md)는 MIT다. [package.json](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/package.json)에서 sharp·jimp 등의 의존성과 선택적 TinyPNG 연동 관련 패키지를 확인했다. 의존성 취약점·현재 npm 배포와 이 커밋의 동일성은 조사하지 않았다.
- 같은 제작자의 [데스크톱 앱 README](https://github.com/odrick/free-tex-packer/blob/c972c97c522a80c6859a2b836a99d1402d95293e/README.md)는 기능 개선 시간이 없고 중대한 버그만 고친다고 명시한다. 앱 전체의 기본 설치 추천 대신 core를 필요 시 평가할 후보로 남긴다.
- 실제 도입 때: 대상 버전·잠금 파일·네이티브 의존성을 확인한 뒤 크기가 다른 투명 PNG 몇 장을 포장해 프레임 좌표·알파·패딩·회전·피벗 보존을 검사한다. 외부 최적화 서비스가 필요하지 않으면 로컬 작업으로 유지한다.

## 보관과 갱신 원칙

여기는 작업별 후보를 찾는 참고 선반이다. 일반 작업마다 원격을 조회하거나 세 도구를 모두 로딩·설치하지 않는다. 구체적인 결과물이 필요해졌을 때 관련 후보 하나의 현재 소스·버전·실행 조건을 다시 확인하고 기존 사용자 권한 안에서 진행한다. 이 목록만으로 설치·외부 전송·배포 권한이 생기지 않는다.

이번에는 공식 자료와 출처만 검토했다. 효과 렌더·앱 실행·아틀라스 포장·게임 엔진 연동·보안 감사는 실행하지 않았다. 실제 검증 후 상태를 갱신하며, 확인한 소스 커밋과 실제 배포 버전을 구분한다.
