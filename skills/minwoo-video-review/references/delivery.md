# 납품 파일 기술 점검

```text
python <스킬>/scripts/check_delivery.py <video.mp4> --ffprobe <실행 파일> --spec <spec.json> --srt <captions.srt>
```

spec 예: {"width":640,"height":360,"fps":30,"duration_min":1.9,"duration_max":2.1,"audio":false}

Python 3.10+, ffprobe가 필요하다. kit의 Remotion 실행 도구에 포함된 플랫폼별 compositor ffprobe 또는 사용자가 설치한 ffprobe를 명시한다. 원본은 수정하지 않고 로컬 컨테이너의 stream/format 정보만 읽는다. 외부 프로토콜과 재생 목록은 사용하지 않는다.

크기·평균 프레임률·길이·음성 스트림 유무를 지정 규격과 비교하고 SRT의 시간 형식, 양의 구간, 영상 범위 이탈을 검사한다. 겹치는 자막은 기본 경고, spec의 no_overlap=true면 실패다. 출력은 파일 이름·SHA-256·관측 규격·검사 결과이며 전체 메타데이터/개인 경로를 공개하지 않는다.

종료 코드 0=기술 검사 통과, 1=불일치, 2=입력/도구 오류. 음성 스트림이 있다고 실제로 들리는지, 평균 fps가 맞는다고 고정 fps인지, 자막 시간이 맞는다고 내용과 발화가 일치하는지 알 수 없다. 손상 프레임·검은 화면·음량·미적 품질·청취는 별도 검사하고 확인하지 않은 항목은 미검사로 적는다.

[ffprobe 공식 안내](https://www.ffmpeg.org/ffprobe.html).
