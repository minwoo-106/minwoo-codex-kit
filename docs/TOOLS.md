# 선택 도구 설치와 갱신

스킬 문서만 설치해도 모든 도구가 생기지는 않는다. 기본 설치기는 외부 의존성 없이 동작하고, 이 도구 묶음은 필요한 사용자가 별도로 설치한다.
전역 승인·인증·MCP·플러그인 설정, 시스템 PATH, 프로젝트 package.json을 변경하지 않는다.

준비: Python 3.11 이상, Node.js 22 이상, 변경 설명/릴리스 노트에는 Git.

```powershell
python -X utf8 -B scripts/setup-tools.py --dry-run
python -X utf8 -B scripts/setup-tools.py
```

Unix도 같은 Python 명령을 쓴다. 설치 위치는 $CODEX_HOME/.minwoo-codex-kit/runtimes/<내용 지문>이며 미설정이면 ~/.codex 아래다. 별도 위치는 --runtime-root로 지정한다.
npm이 없는 환경도 지원한다. 공식 npm 11.6.2 압축 파일을 고정 SHA-512로 확인하고 이 런타임 안에만 풀어 사용한다.
Node 패키지는 package-lock.json의 무결성 정보로 npm ci --ignore-scripts를 실행한다. Python은 전용 가상 환경에 버전·wheel 해시를 고정해 설치한다.

| 도구 | 역할 |
| --- | --- |
| Python 표준 라이브러리·Git | 의존성 조사·변경 설명·릴리스 근거 |
| Hypothesis 6.142.4 / fast-check 4.10.2 | Python / JS 속성 기반 테스트 |
| React 19.3.1 | 독립적인 컴포넌트 합성 예제 검증 |
| PGlite 0.5.13 | 격리된 PostgreSQL SQL·RLS 예제 검증 |
| Remotion 패키지 4.0.539 | SRT 파싱·프레임·MP4 렌더 |
| pytest 9.2.0 | 재배포한 감사 도구의 원본 테스트 실행 |
| Playwright 1.62.1 | 새 브라우저 컨텍스트의 실제 DOM 동작·회귀 증거 |

0.5.0 브라우저 검사는 설치된 Edge/Chrome 실행 파일을 지정할 수 있다. 선택 런타임 설치만으로 브라우저 바이너리를 자동 설치하지 않는다. CI는 격리 runner에서 Chromium을 별도로 설치한다. 영상 납품 점검은 Remotion compositor에 포함된 ffprobe를 재사용하며 메타데이터 확인을 청취·화질 검수로 대신하지 않는다. 실전 시험은 [평가 안내](../evals/PRACTICAL.md)를 따른다.

2026-10-29 검토에서 Remotion studio의 Zod 4.5.4에 [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5)가 조회되어 같은 메이저의 수정 버전 **4.6.7**을 overrides에 고정했다. 실제 bundling·자막·렌더를 검증했다. 전체 Node 잠금 파일의 npm audit 조회 결과는 0건이었다. 이는 해당 시점의 알려진 취약점 조회 결과이며 이후의 안전을 보장하지 않는다.

Python 후보의 pytest 8.4.2와 Pygments 2.19.2도 공개 권고에 해당해 각각 **9.2.0**, **2.21.0**으로 교체했다. 근거: [pytest 임시 디렉터리](https://github.com/advisories/GHSA-6w46-j5rx-g56g), [Pygments 정규식](https://github.com/advisories/GHSA-5239-wwwm-4pmq). 최종 9개 Python 패키지의 OSV 조회는 0건이었고 수정 버전에서 원본 테스트 105개가 통과했다.

## 설치 후 실제 실행

설치기가 출력한 런타임 폴더로 이동해 실행한다.

```powershell
node verify.mjs
.\python\Scripts\python.exe -X utf8 -B verify_python.py
node verify.mjs --render
```

Unix의 Python 진입점은 ./python/bin/python이다. 실제 렌더는 호환 Chromium이 없으면 브라우저를 내려받을 수 있다. 기존 브라우저는 KIT_BROWSER_EXECUTABLE에 실행 파일 경로를 지정한다. KIT_TEST_OUTPUT은 검증 결과를 생성할 기존 디렉터리다. 출력은 새로운 kit-tools-* 폴더에 저장된다.
샘플 영상은 640×360, 30fps, 2초, 무음이다. 이 성공을 실제 작품·폰트·음악·프로젝트 성능 검증으로 확대하지 않는다.

원본 의존성 검사 테스트는 전용 Python으로 kit 경로의 skills/minwoo-dependency-audit/scripts를 pytest로 실행한다. gh나 pip-audit는 선택 사항이며 자동 설치·로그인하지 않는다. 없어도 확인 불가 항목을 포함한 보고서를 만들 수 있다.

## 반복 실행·갱신·실패

- 동일한 원본과 실행 환경에서는 같은 지문 경로를 사용하고 파일을 다시 쓰지 않는다. 원본 복사 파일의 해시와 직접 설치 패키지 버전·실행 파일 존재를 확인한다.
- 파일을 직접 수정했거나 미완료/미관리 폴더가 있으면 중단한다. 검사 실패를 무시하고 덮어쓰지 않는다.
- 버전·잠금·검증 샘플이 바뀌면 다른 지문 폴더를 만든다. 기존 런타임은 보존한다. 가상 환경을 다른 경로로 이동하면 실행 경로가 깨질 수 있어 이동하지 않는다.
- 설치 실패 시 미완료 폴더를 진단용으로 남기며 자동 재사용하지 않는다. 내용과 경로를 확인해 해당 폴더만 정리한 뒤 재시도하거나 별도 --runtime-root를 사용한다.
- 의존성을 갱신할 때는 고정 버전·해시·라이선스·취약점 조회 및 대표 작업을 다시 검증한다. npm audit fix --force나 시스템 전체 업데이트를 자동 실행하지 않는다.
- 각 언어 프로젝트에서 테스트를 도입할 때는 그 프로젝트의 테스트 도구·버전을 우선한다. 이 런타임의 패키지를 모든 프로젝트에 강제로 추가하지 않는다.

런타임 존재 검사는 node_modules 전체의 무결성 증명이나 실행 테스트를 대체하지 않는다. 의심되면 새 격리 폴더에 재설치하고 위 검증을 수행한다. 네이티브 Linux/macOS 실행은 이번 검증 범위에 포함하지 않았다.
