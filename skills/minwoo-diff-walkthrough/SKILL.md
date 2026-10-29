---
name: minwoo-diff-walkthrough
description: 커밋·브랜치·PR 변경 내용을 단계별 HTML 설명 화면으로 만들어 달라는 요청에 사용한다. 일반 코드 리뷰나 단순 diff 확인에는 적용하지 않는다.
---

# 변경 설명 화면

1. 비교 기준과 대상 커밋을 확정한다. 작업 트리의 미완료 변경은 사용자가 포함을 요청한 경우에만 별도 범위로 잡는다.
2. `git diff --no-ext-diff --no-textconv --no-color --src-prefix=a/ --dst-prefix=b/ BASE HEAD --`의 UTF-8 원본을 보존한다. 외부 diff 도구를 실행하지 않는다.
3. 변경을 이해하기 좋은 순서로 묶되 파일별 전체 diff를 정확히 한 번씩 포함한다. 설명에는 변경 이유·동작·검증 근거를 쓰고 추측한 결함은 단정하지 않는다.
4. [입력 형식](references/input.md)에 맞춘 JSON을 만들고 실행한다.

```text
python -B <이 스킬>/scripts/render_walkthrough.py --input walkthrough.json --diff changes.patch --output walkthrough.html
```

Python 3.11 이상과 Git이 필요하다. 렌더러는 패치를 검증하며 적용하지 않는다. 완성 HTML의 파일 목록·단계 이동·줄 번호를 실제 브라우저에서 확인한다. 결과는 로컬 파일 링크로 전달한다. 화면의 리뷰 메모는 초안이며 GitHub 전송은 별도 사용자 요청 범위에서만 한다.

원본 도구·템플릿의 [출처와 변경 사항](UPSTREAM.md)을 참고한다.
