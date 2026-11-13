# 문서와 데이터 선택

보고서·일지·안내문 등 문서 파일의 신규 작성·서식 개편에는 [문서 편집·디자인 검수](document-quality.md)를 함께 읽는다. 형식별 제작 스킬이 작업을 주도하고 이 기준은 내용·양식 검수를 보완한다. 단순 읽기·텍스트 추출·원형 보존 변환에는 새 편집 절차를 적용하지 않는다.

다른 문서 스킬이 실제로 필요할 때만 [공개 후보 검토](document-candidates.md)를 참고한다. 후보를 읽는 것과 설치·실행은 다르며 기존 도구와 같은 역할을 중복 설치하지 않는다.

금융 멀티에이전트 연구를 명시적으로 할 때만 [TradingAgents 후보](ai-workflow-candidates.md#tradingagents)를 검토한다. 일반 표 분석이나 투자 판단에 자동으로 호출·설치하지 않는다.

SQLite 데이터를 반복 탐색할 별도 자료실이 필요할 때만 [개발·데이터 참고 후보](development-tool-candidates.md#datasette)의 Datasette 절을 확인한다. 일반 표·CSV 분석이나 스프레드시트 산출물은 아래 기존 형식 도구로 처리하며 새 서버 설치·게시를 자동 진행하지 않는다.

일반 글·메일·공지·대본의 번역투·반복·내 말투·격식·공손함 편집은 minwoo-natural-writing이 맡는다. 단순 맞춤법은 바로 처리한다. 브랜드 전체 말투 체계는 minwoo-brand-voice, 홈페이지 문구 기획은 minwoo-web-copy가 주도하며 같은 문구에 편집 절차를 중복 적용하지 않는다.

문서 파일이나 연결 서비스에서 편집한다면 문체는 보조 역할이다. 필수 형식 스킬과 사용자가 지정한 저장·발송 범위를 유지한다. 글을 다듬는 요청만으로 메일을 보내거나 게시하지 않는다.

먼저 입력이 아니라 **요청한 출력 형식·저장 위치·현재 편집 대상**으로 경로를 고른다. 이어서 선택한 스킬의 최신 형식 라우팅과 렌더 검증 절차를 따른다.

| 대상 | 필요한 스킬 |
| --- | --- |
| Word·DOCX 파일 제작·편집·서식·변경 추적 | documents:documents |
| PDF 읽기·제작·레이아웃·페이지 검사 | pdf:pdf |
| XLSX·CSV·표 분석·스프레드시트 산출물 | spreadsheets:Spreadsheets |
| 사용자가 지정한 열린 Excel 세션 | spreadsheets:excel-live-control |
| 일반 발표 자료·PPTX·Spaces 발표 자료 | presentations:Presentations |
| Google Docs 원본 | google-drive:google-drive → google-drive:google-docs |
| Google Sheets 원본 | google-drive:google-drive → google-drive:google-sheets |
| Google Slides 원본·템플릿 | presentations:Presentations의 Google 경로 + google-drive:google-slides |
| 원본을 바탕으로 재사용할 개인 산출물 템플릿 | template-creator:template-creator |

화살표는 서비스 진입 후 필요한 형식 안내를 선택한다는 뜻이다. Google 파일을 다룰 때 Google Drive가 공통 진입점이며 구체적인 도구 사용은 해당 스킬을 따른다.
Google Slides는 presentations의 경로 안내가 요구하는 Drive 흐름을 보존한다. Google 문서를 임의로 로컬 파일이나 Spaces 사본으로 대체하지 않는다.
발표 자료의 일반 요청·명시적 파일 요청·기존 문서 수정은 presentations의 우선순위대로 결정한다. 입력이 PPTX라는 이유만으로 출력도 PPTX라고 단정하지 않는다.
열린 문서 편집은 연결 세션·지원 기능을 먼저 조회한다. 문서 제어 도구가 노출됐다는 이유로 열린 파일이나 편집 권한이 있다고 추정하지 않는다.
일반 채팅 답변은 문서로 저장하지 않는다. 저장소 README·AGENTS.md 작업은 저장소 파일에 작성하고 Pages로 옮기지 않는다. Pages·Notion 저장이 목적이면 [연결 서비스](services.md)를 사용한다.
