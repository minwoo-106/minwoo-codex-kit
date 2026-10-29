# 제공된 스냅샷 검사

Python 3.10+ 표준 라이브러리만 쓴다. 네트워크·파일 쓰기·자동 크롤링은 하지 않는다.

```text
python <스킬>/scripts/check_pages.py --manifest <snapshot/manifest.json>
```

```json
{"pages":[{"url":"https://example.test/about","html":"about.html","status":200,"headers":{},"expectIndexable":true}],"robots":"robots.txt","sitemap":"sitemap.xml"}
```

파일은 manifest 폴더 아래 상대 경로만 사용한다. 페이지 최대 100개, 각 입력 최대 2 MiB이며 링크·경로 이탈은 거절한다. HTML 파일과 HTTP 상태·헤더는 실제로 관찰한 자료만 입력한다. 상태나 헤더를 얻지 못했으면 생략하고 review로 남긴다. 비공개 페이지는 expectIndexable=false로 명시한다.

종료 코드 0은 지원 범위에서 발견 없음, 1은 확인할 오류 발견, 2는 review 또는 미완료다. status 필드로 review와 incomplete를 구분한다. 원본을 수정하지 않으며 JSON에는 본문·비밀값 대신 페이지 번호와 문제 코드를 담는다.

- 제목 누락·중복 태그, 오류 HTTP 상태, 기대와 다른 noindex, 복수·잘못된 canonical, JSON-LD 구문 오류를 검사한다.
- 설명·중복 제목·상대 canonical·다른 도메인 canonical·관찰되지 않은 HTTP 정보는 검토 항목이다. canonical 자체는 필수가 아니며 지정이 없어도 색인될 수 있다.
- robots.txt 자동 판정은 단일 wildcard 그룹의 전체 허용·전체 차단에 한정한다. 복잡한 경로·에이전트·패턴은 review로 남기고 공식 해석을 따른다. robots 차단을 비공개 보장의 수단으로 쓰지 않는다.
- sitemap은 표준 namespace의 urlset만 검사한다. 색인 제외 페이지 포함·중복 URL·제공 페이지 누락을 검토한다. 사이트맵에 없다는 사실만으로 크롤링 불가라고 결론내리지 않는다.
- JavaScript 렌더, 외부 링크 상태, 실제 Search Console 색인 상태, 구조화 데이터의 타입별 요건은 별도 확인 대상이다.

근거: [Google 개발자 안내](https://developers.google.com/search/docs/fundamentals/get-started-developers), [robots 메타·헤더](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag), [canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
