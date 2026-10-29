# 시나리오 실행

Node 22+, Playwright가 설치된 프로젝트/kit 런타임, Chromium 계열 브라우저가 필요하다. kit의 선택 도구 설치기는 Playwright 라이브러리를 제공하며 브라우저는 기존 Edge/Chrome 또는 명시적으로 설치한 Chromium을 사용한다.

```text
node <스킬>/scripts/check_browser.mjs --runtime <package.json과 node_modules 폴더> --browser <브라우저 실행 파일> --config <scenario.json> --out <새 증거 폴더>
```

```json
{"baseURL":"http://127.0.0.1:3000","cases":[{"name":"search","steps":[
  {"action":"goto","path":"/"},
  {"action":"fill","testId":"query","value":"apple"},
  {"action":"click","role":"button","name":"Search"},
  {"action":"text","testId":"result","value":"apple"}
]}]}
```

선택자는 testId 또는 role+name이다. 검사 action은 text(정확한 textContent trim), value, count, visible이며 fill/click/goto를 지원한다. 작업마다 새 컨텍스트를 사용한다. 원격 URL은 승인된 경우 --allow-remote로 명시한다. allowedOrigins는 필요한 리소스의 origin 배열이며 기본값은 baseURL 하나다. 요청은 허용 origin으로만 나가고 서비스 워커는 차단한다. 이 제한 때문에 실패하면 필요한 대상과 권한을 확인해 좁게 추가한다.

아무 검사도 없는 시나리오는 거절한다. report.json, 시나리오별 screenshot.png·trace.zip을 새 폴더에 저장한다. 이미 있는 출력 폴더는 덮어쓰지 않는다. 종료 코드 0=모두 통과, 1=동작 실패, 2=설정/환경 오류. 외부 앱의 완전한 격리를 보장하는 보안 도구는 아니다.

[Playwright 검사](https://playwright.dev/docs/test-assertions), [trace](https://playwright.dev/docs/trace-viewer).
