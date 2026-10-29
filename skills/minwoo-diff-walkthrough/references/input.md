# 입력 형식

JSON 필수 필드:
- `title`: 화면 제목
- `steps`: 각 단계의 `message`, `files`(경로 배열), `diff`(원본의 파일별 전체 패치)를 담은 배열
- `explanations`: 단계별 설명 HTML 문자열 배열. 기본 문단·목록·코드 태그만 사용
- `reviews`: 단계별 발견 사항 배열. 없으면 단계마다 빈 배열
- `pr_meta`: PR이 없으면 null. 있으면 실제 `owner`, `repo`, `pr_number`, 40자리 `head_sha`

발견 사항은 `severity`(high/medium/low), `title`, `body`를 갖는다. 줄 연결이 필요하면 `file`, `line`, `side`(LEFT/RIGHT), 선택적 `end_line`을 추가한다. 원본 diff에 없는 파일·줄 번호는 거절된다. 설명 배열의 길이는 단계 수와 같아야 한다.

원본 패치를 JSON에 넣을 때 텍스트를 손으로 재작성하지 말고 프로그램으로 읽어 넣는다. UTF-8과 원래 줄바꿈을 보존한다. 샘플에 실제 고객 코드나 비밀 값을 넣지 않는다.
