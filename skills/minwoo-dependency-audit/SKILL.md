---
name: minwoo-dependency-audit
description: 프로젝트 의존 패키지의 알려진 취약점·유지보수·공급망 위험을 근거와 함께 조사해 달라는 요청에 사용한다. 일반 설치, 앱 보안 전체 감사, 단순 버전 업데이트에는 적용하지 않는다.
---

# 의존성 근거 조사

먼저 manifest와 lockfile의 종류, 공개·사설 의존성을 로컬에서 확인한다. 온라인 수집은 공개 패키지 이름·버전과 저장소 식별자를 npm/PyPI/Go, OSV, deps.dev, GitHub, OpenSSF에 보낸다. 사설 패키지나 회사 식별자를 포함한 경우 해당 목록을 외부에 전송하지 말고 공개 의존성만 남긴 별도 입력을 만들거나 오프라인으로 검토한다. 수집 결과와 캐시는 감사 대상 저장소 밖에 둔다.

Python 3.11 이상, 외부 Python 라이브러리 없이 실행한다. GitHub CLI 인증이 이미 있으면 원본 도구가 GitHub 조회에 사용한다. 새 인증·권한 확대를 자동 수행하지 않는다. gh·pip-audit는 선택 사항이며 없어도 결과의 미확인 범위를 명시할 수 있다. 패키지를 설치하거나 해당 프로젝트 코드를 실행하지 않는다.

```text
python -X utf8 -B <이 스킬>/scripts/collect.py <공개 의존성 프로젝트> --json audit.json --cache <별도 캐시>
python -X utf8 -B <이 스킬>/scripts/render.py audit.json --out audit.md
```

실제 렌더러 인수는 최초 실행 전 `--help`로 확인한다. 네트워크가 없으면 수집에 `--offline`을 붙인다. 캐시 없는 오프라인 결과를 안전하다는 판정으로 사용하지 않는다.

- 직접/전이 의존성, 고정/조회된 최신 버전, 검사됨/미확인 수를 분리한다.
- package-lock·npm-shrinkwrap·uv.lock·Go 모듈 지원과 pnpm/yarn/Poetry 미지원 범위를 확인한다.
- 확인 불가, 오래된 캐시, API 오류, 도구 미설치는 취약점도 안전의 증거도 아니다.
- 근거 URL·조회 시점·영향 버전·대응안을 함께 보고한다. 자동 업그레이드나 lockfile 수정은 이 조사에 포함되지 않는다.
- 출력에 내부 경로·패키지 이름이 남을 수 있다. 공개 보고에는 필요한 공개 정보만 포함한다.

[출처와 변경 사항](UPSTREAM.md).
