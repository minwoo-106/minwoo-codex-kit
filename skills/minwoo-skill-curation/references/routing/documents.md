# 문서와 데이터 선택

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
