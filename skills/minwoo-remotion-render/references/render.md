# 실행과 도구

기존 Remotion 프로젝트는 해당 프로젝트에 고정된 실행 명령을 우선한다. kit의 선택 도구 설치는 저장소의 `docs/TOOLS.md`와 `scripts/setup-tools.py`를 사용한다. kit 도구는 프로젝트 패키지나 전역 PATH를 변경하지 않는다.

`tooling/verify.mjs`와 `tooling/fixtures/captions.jsx`는 실제 렌더를 검증하는 최소 샘플이다. 새 영상을 만들 때 샘플을 완성 작품으로 오해하지 말고 Composition과 자료를 프로젝트에 맞게 작성한다. kit 런타임은 `$CODEX_HOME/.minwoo-codex-kit/runtimes/<고정 지문>`에 설치하며 설치기가 실제 경로를 출력한다.

Node API의 흐름:
1. `@remotion/bundler`의 `bundle({entryPoint})`
2. `@remotion/renderer`의 `selectComposition({serveUrl,id})`
3. `renderStill`로 대표 프레임, `renderMedia({composition,serveUrl,codec:'h264',outputLocation})`로 영상
4. 로컬 메타데이터와 재생 화면으로 결과 확인

패키지는 모두 같은 Remotion 버전을 사용한다. 필요한 Chromium은 최초 렌더 시 내려받을 수 있다. 이미 설치된 호환 브라우저를 명시할 수도 있다. 한글 폰트는 해당 PC/프로젝트에 실제 존재하는 글꼴을 사용하고 최종 출력에서 확인한다.

공식 문서:
- https://www.remotion.dev/docs/bundler/bundle
- https://www.remotion.dev/docs/renderer/select-composition
- https://www.remotion.dev/docs/renderer/render-media
- https://www.remotion.dev/docs/renderer/render-still
- https://www.remotion.dev/docs/captions/parse-srt

Remotion 실행 패키지의 이용 조건은 문서 스킬과 별개다: https://www.remotion.dev/docs/license
