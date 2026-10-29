# 사이트 관찰과 속도 측정

Node 22+, 기존 kit Playwright 런타임과 브라우저를 재사용한다. 새 패키지 설치는 필요 없다.

```text
node <스킬>/scripts/inspect_site.mjs --runtime <runtime> --browser <실행파일> --config <config.json> --mode performance --out <새폴더>
```

```json
{"baseURL":"http://127.0.0.1:3000","viewport":{"width":390,"height":844},"runs":3,"cases":[{"name":"home","path":"/"}],"linkPaths":["/about"]}
```

- performance는 각 페이지를 새 브라우저 컨텍스트에서 1~7회(기본 3회) 관찰하여 TTFB·DOMContentLoaded·load 시점과 중앙값을 기록한다. 선택 maxLoadMs는 사용자가 정한 load 중앙값 기준이며 보편적인 기준이 아니다. 실패한 표본이 있으면 중앙값을 내지 않는다.
- launch는 명시한 페이지와 linkPaths의 같은 origin 경로만 방문한다. 수집한 링크 전체를 순회하지 않는다. 로그아웃·삭제 등 부작용 경로는 입력하지 않는다. 외부 링크·메일·결제·DNS는 검사하거나 변경하지 않는다.
- 페이지 오류, 즉시 로딩 이미지 실패, 같은 문서의 없는 앵커를 검사하고 img의 원본·표시 크기를 기록한다. 지연 로딩 이미지·공유 메타 누락·가로 넘침은 review다. CSS 배경, 이미지 내용·출처·폰트 라이선스는 자동 검사 범위가 아니다.
- 로컬 주소가 기본이며 승인된 원격은 --allow-remote로 지정한다. allowedOrigins는 필요한 리소스만 허용한다. 페이지 코드를 로딩하므로 운영 데이터 변경이 없는 테스트 경로를 우선한다.
- report.json과 화면은 새 폴더에만 쓴다. 화면은 비공개 내용이 있을 수 있어 공개 배포에 넣지 않는다. JSON에는 URL·본문·오류 원문 대신 페이지 이름·위치 번호·문제 코드를 남긴다.
- 종료 0은 지원 범위 관찰 완료(observed), 1은 문제·기준 초과(issues), 2는 수동 검토(review) 또는 미완료다. 0은 사이트 전체 출시 승인이라는 뜻이 아니다.

같은 머신·브라우저·빌드 방식·뷰포트·부하 조건에서 전후를 비교한다. 새 컨텍스트라도 OS/DNS 캐시는 공유하며 네트워크·CPU 제한이나 실제 모바일 기기 시험은 아니다. load는 사용자 준비 완료, LCP·INP·CLS나 실사용 Core Web Vitals를 대체하지 않는다. Lighthouse·실사용 데이터가 필요하면 별도로 확인하고 실제 실행한 경우만 그 결과를 보고한다.

근거: [Navigation Timing](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming), [Lighthouse 측정](https://developer.chrome.com/docs/devtools/lighthouse).
