# 디자인·미디어 도구 참고 후보

검토일: 2026-11-02. 상태: **공식 자료·출처 검토 완료 / 실제 설치·실행 검증 전**.
도구 이름은 설치·MCP 연결·사용 권한의 증거가 아니다. 새 자동 발동 스킬은 만들지 않는다. 아래 해당 후보의 절만 필요한 때 참고한다.

| 후보 | 용도 | 연결 방식 |
| --- | --- | --- |
| [Toolcraft](#toolcraft) | 캔버스·레이어·타임라인·출력을 가진 전용 디자인 편집기를 만드는 시작 틀이다. | 독립 프로젝트 템플릿 후보; 실제 화면 구현은 기존 프로젝트·UI 선택 안내 |
| [css-doodle](#css-doodle) | CSS 규칙으로 반복 패턴·배경·장식 아트를 만든다. | 기존 웹 디자인 주도 스킬과 minwoo-web-assets의 시각 자산 보조 |
| [VTracer](#vtracer) | PNG/JPG 같은 래스터 그림을 SVG 경로로 변환한다. | minwoo-web-assets의 자산 준비 보조; imagegen·기존 SVG 편집과 구분 |
| [Manim Community](#manim-community) | 도형·그래프·수식 등의 설명 애니메이션을 코드로 제작한다. | 독립 설명 영상 후보; 완성 영상 편집·합성은 필요할 때 기존 Remotion 흐름 |
| [ScreenToGif](#screentogif) | Windows 화면·스케치 등을 녹화하고 프레임을 편집해 GIF·영상으로 저장한다. | 독립 녹화 앱 후보; minwoo-video-review는 만들어진 영상 비교·검사 |
| [glTF Transform](#gltf-transform) | 기존 glTF/GLB 3D 모델의 구조·텍스처·용량을 조정한다. | minwoo-web-assets의 3D 자산 보조; 모델 원화 제작과 구분 |

## Toolcraft

- 출처: [공식 저장소](https://github.com/pixel-point/toolcraft), [확인 README](https://github.com/pixel-point/toolcraft/blob/4952c4a59dc85a5a29079d81c8666c4898461ab6/README.md). 확인 커밋 `4952c4a59dc85a5a29079d81c8666c4898461ab6` (2026-09-19). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 독립 프로젝트 템플릿 후보; 실제 화면 구현은 기존 프로젝트·UI 선택 안내.
- 실행 조건: Node/npm 기반 앱 생성 과정과 템플릿의 의존성을 검토한다. 일반 홈페이지나 기존 앱을 이 틀로 자동 이전하지 않는다.
- 사용 전 검증: 빈 시험 프로젝트에서 가져오기·편집·저장·출력 흐름을 검증한다. 원본 예시의 자동 설치 문구는 실행 권한이 아니다. AI API 기능을 추가하면 키·비용·전송 경로가 별도로 생길 수 있다.
- 라이선스: MIT. 원문 확인: [LICENSE.md](https://github.com/pixel-point/toolcraft/blob/4952c4a59dc85a5a29079d81c8666c4898461ab6/LICENSE.md). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## css-doodle

- 출처: [공식 저장소](https://github.com/css-doodle/css-doodle), [확인 README](https://github.com/css-doodle/css-doodle/blob/2bfbe268d12b75dd41c23e4323aea677fb036af5/README.md). 확인 커밋 `2bfbe268d12b75dd41c23e4323aea677fb036af5` (2026-10-29). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 기존 웹 디자인 주도 스킬과 minwoo-web-assets의 시각 자산 보조.
- 실행 조건: 브라우저 Web Component다. 별도 CLI의 이미지·영상 내보내기는 다른 배포이므로 따로 검토한다.
- 사용 전 검증: 목표 브라우저·모바일에서 렌더·성능·움직임 설정을 확인한다. 무작위 패턴은 필요에 맞게 재현성을 확보하고 복잡한 장식이 본문 가독성을 해치지 않는지 본다.
- 라이선스: MIT. 원문 확인: [LICENSE](https://github.com/css-doodle/css-doodle/blob/2bfbe268d12b75dd41c23e4323aea677fb036af5/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## VTracer

- 출처: [공식 저장소](https://github.com/visioncortex/vtracer), [확인 README](https://github.com/visioncortex/vtracer/blob/e71343fbcbf469b8a72a255030408a39939162eb/README.md). 확인 커밋 `e71343fbcbf469b8a72a255030408a39939162eb` (2026-10-22). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: minwoo-web-assets의 자산 준비 보조; imagegen·기존 SVG 편집과 구분.
- 실행 조건: 데스크톱·CLI·Python·Node 경로 중 필요한 것만 선택한다. README에 제시된 1.0 계열 배포에는 alpha 표기가 있어 안정성 검증이 필요하다.
- 사용 전 검증: 권한 있는 단순 그림으로 원본 대비 윤곽·색·투명도·노드 수·파일 크기를 확인한다. 사진의 세부나 원본 벡터를 정확하게 복원한다고 가정하지 않는다.
- 라이선스: MIT. 원문 확인: [LICENSE](https://github.com/visioncortex/vtracer/blob/e71343fbcbf469b8a72a255030408a39939162eb/LICENSE). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## Manim Community

- 출처: [공식 저장소](https://github.com/ManimCommunity/manim), [확인 README](https://github.com/ManimCommunity/manim/blob/16ea443e2a5f1d79db0a721161411ce916d6e733/README.md). 확인 커밋 `16ea443e2a5f1d79db0a721161411ce916d6e733` (2026-10-27). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 독립 설명 영상 후보; 완성 영상 편집·합성은 필요할 때 기존 Remotion 흐름.
- 실행 조건: Python과 선택 배포의 렌더 의존성을 확인한다. 수식·텍스트 사용 방식에 따라 LaTeX·폰트 등 추가 조건을 확인한다.
- 사용 전 검증: 짧은 장면으로 프레임·글꼴·음수/경계 입력에 따른 시각 표현을 확인한다. 영상이 출력됐다는 사실과 설명 내용의 정확성을 구분한다. 일반 영상에 새 엔진을 추가하지 않는다.
- 라이선스: MIT. 원문 확인: [LICENSE](https://github.com/ManimCommunity/manim/blob/16ea443e2a5f1d79db0a721161411ce916d6e733/LICENSE) · [LICENSE.community](https://github.com/ManimCommunity/manim/blob/16ea443e2a5f1d79db0a721161411ce916d6e733/LICENSE.community). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## ScreenToGif

- 출처: [공식 저장소](https://github.com/NickeManarin/ScreenToGif), [확인 README](https://github.com/NickeManarin/ScreenToGif/blob/a4d0a67c2131cd048ceec86cd40afc2f1a06f2fd/README.md). 확인 커밋 `a4d0a67c2131cd048ceec86cd40afc2f1a06f2fd` (2026-07-28). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: 독립 녹화 앱 후보; minwoo-video-review는 만들어진 영상 비교·검사.
- 실행 조건: README는 .NET 9 Desktop Runtime 이상을 명시한다. 실제로 선택한 설치본·휴대용 배포의 런타임 조건을 다시 확인한다.
- 사용 전 검증: 합성 화면을 짧게 녹화해 잘림·속도·크기·출력 형식을 확인한다. 화면의 개인 자료가 녹화되지 않게 범위를 정한다. 조작 자동화는 현재 컴퓨터 사용 지침을 따른다.
- 라이선스: MS-PL. 원문 확인: [LICENSE.txt](https://github.com/NickeManarin/ScreenToGif/blob/a4d0a67c2131cd048ceec86cd40afc2f1a06f2fd/LICENSE.txt). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## glTF Transform

- 출처: [공식 저장소](https://github.com/donmccurdy/glTF-Transform), [확인 README](https://github.com/donmccurdy/glTF-Transform/blob/8e2a94a2616d293c4b503d0fb6a4b42e6ec7c62f/README.md). 확인 커밋 `8e2a94a2616d293c4b503d0fb6a4b42e6ec7c62f` (2026-10-16). 조사 시 저장소 archived=false. 최근 push 시각과 기본 브랜치 커밋 일자는 다른 값이다.
- 역할·겹침: minwoo-web-assets의 3D 자산 보조; 모델 원화 제작과 구분.
- 실행 조건: CLI는 Node LTS를 전제로 하며 선택한 압축·변환 기능의 추가 의존성과 대상 엔진 지원을 확인한다.
- 사용 전 검증: 원본 사본으로 파일 크기뿐 아니라 재질·텍스처·스켈레톤·애니메이션·실제 로딩을 비교한다. 모든 최적화가 무손실이거나 모든 뷰어에서 호환된다고 가정하지 않는다.
- 라이선스: MIT. 원문 확인: [LICENSE.md](https://github.com/donmccurdy/glTF-Transform/blob/8e2a94a2616d293c4b503d0fb6a4b42e6ec7c62f/LICENSE.md). 실제 사용·재배포 시 선택한 배포와 포함 의존성·자산의 고지도 확인한다.

## 보관·도입 기준

이번에는 공식 README·루트 라이선스·소스 커밋을 검토했다. 실행 파일·스킬 원문·이미지·폰트·의존 패키지는 복제하거나 설치하지 않았다. 의존성 보안 감사·실제 Windows 동작·성능·다른 엔진과의 호환성은 확인하지 않았다.

필요한 작업이 생기면 기존 도구로 충분한지 판단하고, 선택 후보 하나의 현재 배포·버전·환경과 위 대표 검증을 확인한다. 같은 역할의 스킬을 새로 만들거나 전체 후보를 동시 로딩·설치하지 않는다. 이 안내는 기존 승인 방식과 사용자 요청 범위를 바꾸지 않는다. 실제 시험 후에만 후보의 검증 상태를 갱신한다.
