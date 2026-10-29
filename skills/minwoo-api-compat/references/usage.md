# 제한형 OpenAPI 비교

```text
python <스킬>/scripts/check_contract.py old.json new.json
```

Python 3.10+ 표준 라이브러리만 사용한다. OpenAPI 3.0.x/3.1.x JSON의 paths, parameters, requestBody, responses와 기본 객체 스키마(type, enum, properties, required)를 비교한다. 외부 서버·참조를 내려받지 않는다. 스키마 참조·조합·수치 제약 등 지원하지 않는 변경은 review로 보고한다.

종료 코드 1=breaking 발견, 2=입력 오류 또는 수동 review 필요, 0=지원 범위 안에서 breaking 미발견. breaking과 review가 함께 있으면 1이며 보고서에 둘 다 남는다. 추가 속성의 허용 여부·인증·헤더·서버 등의 변화도 무시하지 않고 review로 남긴다.

기존 요청 enum의 축소는 breaking, 응답 enum의 확대는 breaking이다. 새 필수 요청 필드는 breaking, 기존 필수 응답 필드의 보장 제거는 breaking이다. 출력에는 값·인증정보 대신 변경 위치와 이유만 담는다.

이 도구는 전체 JSON Schema 포함 관계를 판정하지 않으며 실제 응답과 명세의 일치도 검사하지 않는다. [OpenAPI 3.1.1 명세](https://spec.openapis.org/oas/v3.1.1.html)를 기준으로 지원 범위를 명시했다.
