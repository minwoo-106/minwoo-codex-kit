# 이 저장소 작업 안내

- `global/AGENTS.md`는 사용자의 공통 규칙 원본이다. 프로젝트별 세부 절차는 `skills/`에 둔다.
- 현재 승인·실행 설정을 바꾸거나 전역 경로에 실제 설치하지 않고, 임시 경로에서 검증한다.
- 설치 동작 변경 후 `python -m unittest discover -s tests -v`를 실행한다.
- 외부 의존성 없이 Python 3.10 이상과 Windows PowerShell 5.1 / PowerShell 7을 지원한다.
- 개인 경로, 로컬 설치 상태, 백업, 회사 자료, 인증 파일은 배포 파일에 포함하지 않는다.
- GitHub 생성·커밋·푸시는 사용자가 요청한 범위에서만 한다.
