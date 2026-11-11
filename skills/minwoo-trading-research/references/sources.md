# 출처와 재사용 범위

검토일: 2026-11-11. 이 스킬은 개인 자동매매 연구에서 필요한 관측·비교 기준을 독자 작성했다. 아래는 설치 가능한 Codex 스킬이 아니라 공개 거래/연구 프로젝트다. 원본 코드나 문서 본문을 이 폴더에 복제하지 않았고 실행·수익성을 검증했다는 뜻도 아니다.

| 원본 | 확인한 라이선스 | 참고한 개념 | 이 kit의 처리 |
|---|---|---|---|
| [QuantConnect LEAN](https://github.com/QuantConnect/Lean) | [Apache-2.0](https://github.com/QuantConnect/Lean/blob/master/LICENSE) | 신호·포트폴리오·위험·집행 분리 | 개념을 자체 절차에 반영; 코드 미복사 |
| [Microsoft Qlib](https://github.com/microsoft/qlib) | [MIT](https://github.com/microsoft/qlib/blob/main/LICENSE) | 금융 연구와 재현 가능한 비교 | 자체 절차 작성; 코드 미복사 |
| [pysystemtrade](https://github.com/pst-group/pysystemtrade) | [GPL-3.0 라이선스 본문](https://github.com/pst-group/pysystemtrade/blob/develop/LICENSE) | 위험에 따른 크기·전략 배분·비용 고려 | 링크만 제공; 코드 미복사 |
| [Freqtrade](https://github.com/freqtrade/freqtrade) | [GPL-3.0 라이선스 본문](https://github.com/freqtrade/freqtrade/blob/develop/LICENSE) | [미래정보 누출 검사](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md) | 독립된 미래 변조 테스트 관점으로 작성; 코드 미복사 |

상세 문서·의존성·개별 파일은 별도 조건일 수 있다. 실제 코드를 가져오려면 해당 커밋과 파일의 라이선스·NOTICE·저작권·의존성 및 배포 방식부터 확인한다. 저장소 인기, 모델 정확도, 백테스트 수익률을 검증된 실계좌 성과로 표현하지 않는다.

필수 외부 도구·새 패키지는 없다. 대상 프로젝트의 기존 계산 엔진, 읽기 전용 DB/파일 도구, 테스트 도구로 적용한다. 별도 운영 서버·토큰·계좌정보·개인 거래 기록은 이 스킬에 포함하지 않는다.

이 스킬은 일반 코드 진단 스킬의 오류 조사 절차나 관측성 스킬의 로그 수집 구현을 대체하지 않는다. 자동매매의 시간축·비용·위험·실험 공정성 검토에만 적용한다. 자체 작성 본문의 공개 조건은 이 kit 소유자가 정하며 외부 프로젝트 라이선스를 자체 본문 라이선스로 오인하지 않는다.
