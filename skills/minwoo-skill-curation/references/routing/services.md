# 연결 서비스 선택

아래는 현재 환경에서 알려진 기능의 선택 안내다. 계정 연결·권한·데이터 존재의 확인 기록이 아니다. 실제 세션의 도구를 찾아 필요한 범위로 확인하고, 요청한 서비스와 기존 원본을 유지한다.

| 서비스·목적 | 선택 |
| --- | --- |
| Drive 자료 찾기·읽기·파일 관리 | google-drive:google-drive |
| Google 문서·표·슬라이드의 댓글 | google-drive:google-drive-comments |
| Notion 근거 조사·비교·보고 | notion:notion-research-documentation |
| Notion 명세에서 구현 계획·작업 만들기 | notion:notion-spec-to-implementation |
| Notion 추적표·데이터베이스 설계 | notion:notion-database-designer |
| Notion 회의 준비·후속 작업 정리 | notion:notion-meeting-intelligence |
| Notion 주간 변화 요약 | notion:notion-weekly-project-digest |
| Notion 설치 후 초기 연결 설정 요청 | notion:notion-setup |
| Page 내용 작성·직접 수정 | pages:write-page |
| 여러 근거로 Page·Space 내용을 지속 정리 | pages:maintain-space |
| 기존 Page·Space 구조·배치 정리 | pages:organize-space |
| Space와 연결된 반복 작업 검토·설정 | pages:manage-schedules |
| Gmail 읽기·검색·요청된 메일 변경 | 현재 Gmail 도구 |
| 일정 조회·요청된 일정 변경 | 현재 Google Calendar 도구 |
| 연락처 찾기·상세 확인 | 현재 Google Contacts 도구 |
| GitHub 저장소·이슈·PR·CI | 현재 GitHub 도구 |
| Canva 디자인 | 현재 Canva 도구 |

Notion 회의 준비와 주간 보고는 기간·결과물이 다르다. 자료 한 건의 직접 수정에 연구·주간 보고 절차를 모두 적용하지 않는다.
Pages의 직접 수정·근거 유지·구조 정리는 변경의 종류로 나눈다. Page가 선택돼 있다는 사실만으로 쓰기 권한을 추론하지 않는다.
스프레드시트·슬라이드의 Artifact Session은 연결된 산출물을 편집하는 실행 도구다. 저장 위치를 정하기 전에 별도 문서를 만들지 않는다.

## 실행 도구·플러그인 선택

- 라이브러리 문서·예제 검색은 Context7이 실제 연결돼 있을 때 보조로 사용한다. 설치 이름만으로 연결을 가정하지 않는다. 프로젝트 버전과 반환 문서 버전을 대조하고 중요한 API 동작은 공식 문서·실제 코드로 확인한다. 검색 질의에 비밀값·회사 코드·개인 자료를 넣지 않는다. 이용할 수 없으면 공식 문서 검색으로 진행하며 매 작업마다 설치를 요구하지 않는다.
- 목적에 맞는 기존 도구·연결 기능을 먼저 쓴다. 플러그인 검색이 필요하면 plugin-management:plugin-management를 적용한다.
- 적절한 API·CLI가 없고 화면 조작이 필요한 경우 computer-use:computer-use 또는 현재 제공되는 컴퓨터 사용 도구의 안내를 따른다.
- 일반 웹 검색은 현재 검색 도구를 사용한다. 외부 앱·계정 접근이 필요할 때만 새 연결을 찾는다.
- 메일·메신저 발송은 명시적 사용자 지시 범위에서만 한다. 안내표는 발송·권한 확대의 승인이 아니다.
- 보호자 설정·도움 요청 전용 연결 기능은 해당 사용자의 구체적인 요청에서만 도구의 필수 조회·사용 절차를 따른다.
- 앱의 플러그인 목록에 보인다는 사실, 스킬 파일 존재, 연결된 계정, 실제 실행 성공을 서로 구분한다.
