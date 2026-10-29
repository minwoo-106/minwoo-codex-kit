# 접근성과 화면 변화 검사

기존 프로젝트의 axe/Playwright Test 검사와 기준 화면이 있으면 재사용한다. 별도 실행기가 필요할 때만 아래 도구를 쓴다. Node 22+, kit 런타임의 @axe-core/playwright·@playwright/test와 Chromium 계열 브라우저가 필요하다.

```json
{"baseURL":"http://127.0.0.1:3000","viewport":{"width":1280,"height":720},"cases":[{"name":"home","path":"/"}]}
```

```text
node <스킬>/scripts/check_quality.mjs --runtime <런타임> --browser <Edge/Chrome> --config <검사.json> --mode accessibility --out <새 증거 폴더>
node <스킬>/scripts/check_quality.mjs --runtime <런타임> --browser <Edge/Chrome> --config <검사.json> --mode baseline --baseline <새 기준 폴더> --out <새 증거 폴더>
node <스킬>/scripts/check_quality.mjs --runtime <런타임> --browser <Edge/Chrome> --config <검사.json> --mode compare --baseline <기존 기준 폴더> --out <새 증거 폴더>
```

--browser는 생략하면 Playwright가 설치한 Chromium을 사용한다. 기본 대상은 로컬 서버이며 승인된 원격 대상만 --allow-remote로 지정한다. allowedOrigins로 필요한 리소스 출처만 추가한다. 쿠키·사용자 프로필을 가져오지 않으며 외부 요청과 서비스 워커를 제한한다.

accessibility는 axe의 WCAG 2/2.1 A·AA와 2.2 AA 태그 검사 결과를 기록한다. violations가 없더라도 incomplete 항목과 키보드·초점·보조 기술을 별도로 검토한다. 자동 통과는 접근성 전체 인증이 아니다.

baseline은 **새 폴더에만** 기준 화면을 만든다. 사용자가 기준을 만들도록 요청했거나 작업 범위에 포함된 경우에만 쓴다. 실패를 없애려고 기존 기준을 덮어쓰거나 자동 갱신하지 않는다. 완료된 기준에는 파일 해시와 OS·브라우저 버전·뷰포트·페이지 매핑이 기록된다.
compare는 같은 환경에서 Playwright의 화면 비교를 실행한다. 환경 불일치·기준 누락·기준 파일 변경은 거절한다. 글꼴·브라우저·동적 데이터·애니메이션이 달라지면 차이가 날 수 있으므로 원인을 먼저 확인한다. 의도된 변경이면 검토한 새 기준을 별도 폴더에 만든다.

종료 코드 0=해당 검사 통과 또는 기준 생성 완료, 1=검사 실패, 2=입력·환경·준비 오류다. runner.log·results.json·report.json·axe 결과·실패 diff/trace는 로컬 증거이며 민감 자료를 포함할 수 있다. 스크린샷 비교는 디자인의 좋고 나쁨을 판정하지 않는다.

[Playwright 접근성](https://playwright.dev/docs/accessibility-testing), [화면 비교](https://playwright.dev/docs/test-snapshots).
