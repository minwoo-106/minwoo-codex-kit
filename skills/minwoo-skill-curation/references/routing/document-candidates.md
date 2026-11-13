# 문서 분야 공개 후보 검토

확인일: 2026-11-13. 참고 목록이며 설치·자동 실행 목록이 아니다. 기존 형식 도구와 [문서 검수](document-quality.md)로 해결되는 작업에는 추가하지 않는다. 아래 원문·실행기·폰트·테마는 kit에 복제하지 않았다. 비교 평가는 이 kit의 독자적인 기준이다.

## 인지도와 품질은 구분

조회 당시 GitHub API의 저장소 별 수는 anthropics/skills 193,700, blader/humanizer 68,413이었다. 전자는 여러 스킬을 묶은 저장소 전체 수치여서 개별 문서 스킬의 사용량이 아니다. 별 수·공식 배포 여부는 발견과 유지보수 판단의 참고이며 한국어 문서 품질의 독립 실험 결과가 아니다. 개별 다운로드·실사용 만족도는 확인하지 않았다.

| 후보 | 쓸 만한 상황 | 현재 판단·겹침·주의 |
| --- | --- | --- |
| Anthropic docx / pdf | OOXML 편집, 표 너비·구조, PDF 읽기·폼 처리 | 현재 형식 플러그인과 겹친다. 새 설치 없이 기술 참고로 보관. 실행 도구·스크립트 호환성은 필요할 때 확인한다. 자연스러운 내부 보고서 디자인을 보장하는 도구는 아니다. |
| Anthropic doc-coauthoring | 긴 기획서·제안서에서 독자가 이해할 수 있는지 검토 | 독자 관점의 확인은 유용하다. 전체 단계별 질문·합의·별도 독자 시험은 자율 작업과 중복될 수 있어 기본 workflow로 설치하지 않는다. 명시적인 공동 집필 요청에서 참고한다. |
| Anthropic internal-comms | 진행·계획·문제를 요약하는 사내 공지·상태 공유 | 문체 스킬·사용자 양식과 역할이 겹친다. 3P 예제는 고정 영어 항목·이모지·엄격한 분량을 요구한다. 그대로 한국어 보고서에 적용하지 않고 내용 구분의 참고로만 둔다. 예제의 Slack·Drive·메일 탐색을 포괄적인 회사 자료 수집 허가로 보지 않는다. |
| Anthropic theme-factory | 제안서·발표 자료에 일관된 색·폰트 테마가 실제로 필요할 때 | 테마 선택 후 확인 대기를 요구한다. 현재 양식을 유지하는 내부 보고서의 기본 경로로 쓰지 않는다. 기존 디자인 도구로 충분하면 추가하지 않는다. |
| blader/humanizer 4.0.0 | 글의 반복·과장·정형 문구를 편집하는 방법 참고 | minwoo-natural-writing과 겹친다. 현재 원문은 일반적인 문장에 알고 있는 구체적 사실을 추가할 수 있게 한다. 사실 보존이 필요한 보고서에는 충돌하므로 원문 전체를 설치하지 않는다. 한국어 문맥에서 문장부호·표현의 일괄 금지도 적용하지 않는다. |
| jhuse25/antislop-docs | 장식·타이포그래피의 여러 선택지를 비교할 때 | 조회 당시 저장소 별 2개로 널리 검증됐다고 볼 근거가 없다. 고유한 시각 요소·반복 메모·별도 설계 문서 등의 요구가 이번 목적과 충돌할 수 있어 보류. ‘anti-slop’ 이름만으로 선택하지 않는다. |

## 고정한 출처와 조건

- Anthropic 확인 커밋: `2c5958ecac7cee2b583967a2c4981d0f4a75c579`.
  - [docx](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/docx/SKILL.md), [pdf](https://github.com/anthropics/skills/tree/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/pdf).
  - [doc-coauthoring](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/doc-coauthoring/SKILL.md), [internal-comms](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/internal-comms/SKILL.md), [3P 예제](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/internal-comms/examples/3p-updates.md), [theme-factory](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/theme-factory/SKILL.md).
  - 확인한 docx·internal-comms·theme-factory의 개별 LICENSE.txt는 Apache-2.0이었다. [internal-comms 라이선스](https://github.com/anthropics/skills/blob/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/internal-comms/LICENSE.txt). 나머지 폴더·폰트·자산의 재배포 조건까지 일괄 승인된 것으로 보지 않는다.
- [Humanizer 4.0.0](https://github.com/blader/humanizer/blob/b48c832f0f809c1b5658edbb838c2521b72f2413/SKILL.md), [MIT 라이선스](https://github.com/blader/humanizer/blob/b48c832f0f809c1b5658edbb838c2521b72f2413/LICENSE). 최신 버전의 사실 추가 방침은 과거 버전과 다르므로 이전 소개만 보고 설치하지 않는다.
- [antislop-docs](https://github.com/jhuse25/anti-slop-design-skills/blob/cf80583a273becde1c212bb1a2a0d133142381f5/skills/antislop-docs/SKILL.md), [MIT 라이선스](https://github.com/jhuse25/anti-slop-design-skills/blob/cf80583a273becde1c212bb1a2a0d133142381f5/LICENSE). 보조 웹 지침·폰트·자산·NOTICE 검토와 실제 설치 시험은 미수행이다.

이번에는 후보 전체를 설치·실행하지 않았다. 본문과 관련 예제의 역할·충돌을 검토했으며 현재 도구의 결과물 시험과 구분한다. 직접 재배포가 필요해지면 해당 버전의 폴더별 라이선스·NOTICE·참고 파일·실행 의존성을 다시 확인한다. 후보 사용을 위해 승인 방식·자동 실행 훅·모델 설정을 바꾸지 않는다.
