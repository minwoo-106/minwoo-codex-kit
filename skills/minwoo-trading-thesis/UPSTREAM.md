# 출처와 각색 범위

- 원저작자/제공자: Anthropic (`anthropics/financial-services`).
- 원본 스킬: `thesis-tracker`.
- 확인 커밋: `60565064557ca77b12f62aa7877f365d111c129d`.
- [원본 SKILL.md](https://github.com/anthropics/financial-services/blob/60565064557ca77b12f62aa7877f365d111c129d/plugins/vertical-plugins/equity-research/skills/thesis-tracker/SKILL.md).
- 원본 Git blob: `f9a3ce9187bdc3410d3f4f3713ce70a6f6b8f221`.
- [원본 라이선스](https://github.com/anthropics/financial-services/blob/60565064557ca77b12f62aa7877f365d111c129d/LICENSE): Apache-2.0. 전문을 [LICENSE](LICENSE)에 보존했다.
- 검토·각색일: 2026-11-12.

이 폴더의 SKILL.md는 원본의 수정·각색본이다. 가설 정의, 지지/반박 증거의 동등한 추적, 변화 기록과 판정표라는 절차를 이어받았다. 기업별 목표주가·비중 증감·주관적 확신 등급 대신 자동매매 실험의 버전·자료 시점·기준선·비용·위험·큰 승자 보존을 기록하도록 한국어로 재구성했다. 분기별 검토 주기를 강제하지 않고 기존 EOD·주간 연구의 기한을 따른다.

각색 및 새 안내 부분도 Apache-2.0으로 제공한다. 원본에 별도의 구체적 저작권 문구가 없어 제공자를 위와 같이 귀속 표시한다. 확인 커밋의 루트 NOTICE와 equity-research의 별도 LICENSE 경로는 존재하지 않았다. 루트 LICENSE 전문과 원본 귀속·수정 사실을 보존한다. 재갱신할 때는 라이선스와 추가 고지를 다시 확인한다.

원본 플러그인·MCP 설정, 훅, 에이전트 실행기, 외부 데이터 연결은 포함하지 않았다. 기존 연구 결과를 읽고 보고서를 작성하는 지침이며, 새 실행 의존성·인증키·네트워크 연결이 필수는 아니다. 다른 프로젝트에서도 고정한 날짜·계좌·종목·전략 매개변수를 가져오지 않고 그 프로젝트의 연구 기준을 사용한다.
