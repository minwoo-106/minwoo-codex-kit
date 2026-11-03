# 구조화 데이터와 변경 전후 점검

구조화 데이터나 배포 전후 검색 노출 차이를 요청했을 때만 읽는다. 전체 SEO 캠페인·외부 계정 연결·자동 크롤링으로 확대하지 않는다.

## 구조화 데이터의 세 층

1. JSON 파싱 가능 여부: 기존 check_pages.py가 검사하는 범위다.
2. 의미와 사실: @context, @type, @id 연결, 중첩 객체·@graph, 타입별 속성, 페이지 본문과의 일치를 확인한다. 중첩 객체마다 @context가 없다는 이유만으로 오류로 보지 않는다. 가격·재고·리뷰·평점·조직·주소를 추정해 채우지 않는다.
3. 검색 기능 자격: 해당 타입에 대한 현재 검색엔진 공식 문서와 테스트 결과로 별도 확인한다. Schema.org에 있는 타입과 Google 리치 결과 지원은 같은 목록이 아니다. 문법·의미가 맞아도 노출은 보장되지 않는다.

공개 HTML·렌더된 본문과 비교하고 관찰하지 못한 JS 렌더나 로그인 전용 내용은 미확인으로 남긴다. 기존 FAQ·리뷰 마크업의 삭제 여부를 오래된 상태표만으로 정하지 않는다. 실제 지역 업체·상품이 없는 페이지에 LocalBusiness·Product 등을 억지로 추가하지 않는다. 평가용 수치·가짜 후기·플레이스홀더를 공개 마크업에 넣지 않는다.

## 기준본과 변경본

동일 URL·언어·기기·로그인 조건·수집 방법의 자료를 비교한다. 수집 시각과 코드 버전, HTTP 상태·헤더 관찰 여부를 기록한다. 소스 HTML과 브라우저 렌더 결과를 서로 같은 측정처럼 비교하지 않는다.

제목·설명·canonical·robots/noindex·JSON-LD·공개 의도·사이트맵 변경을 본다. 의도한 페이지 삭제와 실수로 사라진 페이지를 구분하고, 페이지 목록의 순서나 JSON 객체 키 순서만 달라진 것을 회귀로 세지 않는다. 기준본에도 결함이 있을 수 있으므로 변경 없음은 안전/SEO 통과의 뜻이 아니다.

제공된 두 스냅샷을 네트워크 없이 비교할 때:
```text
python <스킬>/scripts/compare_snapshots.py --before <이전/manifest.json> --after <이후/manifest.json>
```
입력 형식과 크기·경로 제한은 [스냅샷 검사](checks.md)와 같다. 결과는 URL 대신 이전/이후 페이지 번호와 바뀐 필드 이름만 담는다. 파일을 수정하거나 기준본을 자동 교체하지 않는다. 종료 0은 비교 범위 변경 없음, 1은 변경 발견, 2는 비교 미완료다. 각 시점의 기존 검사 결과를 함께 읽는다. HTTP 정보 누락, JSON-LD 구문 오류 등은 별도 검사 결과이며 의미/검색 자격을 자동 판정하지 않는다. robots·sitemap 제공 파일은 텍스트 변경만 비교하므로 공백 변경도 차이로 나올 수 있다.

변경 후 관찰은 원인 증명이 아니다. 유입·순위 변화는 기간·쿼리·페이지·지역·시즌·다른 배포와 함께 확인한다. Search Console/API 권한이나 실제 관찰이 없으면 수치를 지어내지 않는다.

콘텐츠 자체의 유용성·근거는 홈페이지 문구 작업의 minwoo-web-copy 참고 절차로 연결한다. Google AI 검색 노출에 별도 파일/마크업이 필수라고 주장하거나 자체 점수를 실제 검색엔진 점수로 표현하지 않는다.

근거: [Google 구조화 데이터](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), [AI 검색 안내](https://developers.google.com/search/docs/appearance/ai-features). 구성 참고: [Claude SEO schema](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-schema/SKILL.md), [drift](https://github.com/AgriciDaniel/claude-seo/blob/6be93f45064ffbadced572b5d5c95f55fd263af0/skills/seo-drift/SKILL.md). 원문/실행기를 복제하지 않았다.
