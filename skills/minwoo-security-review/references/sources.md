# 출처와 설계 판단

검토일: 2026-10-29. 이 스킬은 개인 kit에 맞게 직접 작성했다. 아래 스킬·문서의 본문이나 실행 코드를 복제하지 않았다.

- [OpenAI security-best-practices](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-best-practices/SKILL.md): 본문·참고 파일 목록과 같은 커밋의 LICENSE.txt(Apache-2.0)를 확인했다. 스택별 근거, 보안 요청으로 한정한 발동 범위, 위치가 있는 보고의 관점을 참고했다.
- 원문의 보고 후 수정 전 질문 절차는 이미 수정까지 허용한 사용자에게 반복 승인을 요구하는 공통 규칙으로 가져오지 않았다. 전역 승인 설정은 유지한다.
- ID의 예측 불가능성과 실제 접근 권한을 구분했다. 무작위 ID만으로 권한 누락이 해결된다고 판단하지 않는다.
- [OWASP 접근 권한](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP SQL 인젝션 예방](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS 예방](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

특정 프레임워크 버전의 동작이 쟁점이면 그 프레임워크의 공식 문서와 실제 설정을 추가로 확인한다. 이 목록이 모든 위협을 다루는 표준이나 인증은 아니다.
