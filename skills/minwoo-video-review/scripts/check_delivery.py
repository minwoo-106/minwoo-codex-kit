"""Read local media metadata and compare explicit delivery criteria. Never modify media."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def subtitles(text,duration):
    intervals=[]
    for block in re.split(r'\n\s*\n',text.replace('\r\n','\n').strip()):
        lines=block.splitlines()
        if not lines: continue
        if lines[0].isdigit(): lines=lines[1:]
        if len(lines)<2: raise ValueError('SRT missing text')
        m=re.fullmatch(r'(\d{2,}):([0-5]\d):([0-5]\d),(\d{3}) --> (\d{2,}):([0-5]\d):([0-5]\d),(\d{3})',lines[0])
        if not m: raise ValueError('Invalid SRT time')
        n=list(map(int,m.groups()))
        seconds=lambda v: v[0]*3600+v[1]*60+v[2]+v[3]/1000
        start,end=seconds(n[:4]),seconds(n[4:])
        if start>=end or end>duration+0.001: raise ValueError('SRT outside media duration or empty interval')
        intervals.append((start,end))
    if not intervals: raise ValueError('No subtitles')
    ordered=sorted(intervals); overlap=any(b[0]<a[1] for a,b in zip(ordered,ordered[1:]))
    return {'cues':len(intervals),'overlap':overlap}


def assess(metadata,spec,srt=None):
    allowed={'width','height','fps','duration_min','duration_max','audio','no_overlap'}
    if not isinstance(spec,dict) or set(spec)-allowed: raise ValueError('Unknown specification key')
    if not set(spec)&(allowed-{'no_overlap'}): raise ValueError('At least one delivery criterion required')
    for key,value in spec.items():
        if key in {'audio','no_overlap'}:
            if not isinstance(value,bool): raise ValueError('Boolean criterion required')
        elif isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
            raise ValueError('Positive numeric criterion required')
    videos=[s for s in metadata['streams'] if s.get('codec_type')=='video']
    if len(videos)!=1: raise ValueError('Expected exactly one video stream')
    stream=videos[0]
    duration=float(metadata.get('format',{}).get('duration',stream.get('duration','nan')))
    fps=float(Fraction(stream.get('avg_frame_rate','0/1')))
    if not math.isfinite(duration) or duration<=0 or fps<=0: raise ValueError('Unknown duration/fps')
    observed={'width':stream['width'],'height':stream['height'],'fps':fps,'duration':duration,
              'audio':any(s.get('codec_type')=='audio' for s in metadata['streams'])}
    failures=[]
    for key in ('width','height','audio'):
        if key in spec and spec[key]!=observed[key]: failures.append(key)
    if 'fps' in spec and abs(spec['fps']-fps)>0.01: failures.append('fps')
    if 'duration_min' in spec and duration<spec['duration_min']: failures.append('duration_min')
    if 'duration_max' in spec and duration>spec['duration_max']: failures.append('duration_max')
    caption=None; warnings=[]
    if srt is not None:
        try:
            caption=subtitles(srt,duration)
            if caption['overlap']:
                (failures if spec.get('no_overlap') else warnings).append('subtitle overlap')
        except ValueError as e: failures.append(str(e))
    elif spec.get('no_overlap'): raise ValueError('SRT required for overlap check')
    return {'passed':not failures,'observed':observed,'failures':failures,'warnings':warnings,
            'subtitles':caption,'scope':'metadata and SRT timing; no decoding, loudness or subjective review'}


def check(video,ffprobe,spec,srt=None):
    if not video.is_file() or video.suffix.lower() not in {'.mp4','.mov','.mkv','.webm'}:
        raise ValueError('Local video container required')
    before=digest(video)
    proc=subprocess.run([str(ffprobe),'-v','error','-protocol_whitelist','file,pipe',
        '-show_streams','-show_format','-of','json',str(video.resolve())],
        capture_output=True,text=True,encoding='utf-8',timeout=60)
    if proc.returncode: raise ValueError('ffprobe failed')
    result=assess(json.loads(proc.stdout),spec,srt)
    if digest(video)!=before: raise ValueError('Media changed during inspection')
    result.update(file=video.name,sha256=before)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video',type=Path); parser.add_argument('--ffprobe',type=Path,required=True)
    parser.add_argument('--spec',type=Path,required=True); parser.add_argument('--srt',type=Path)
    args=parser.parse_args()
    try:
        result=check(args.video,args.ffprobe,json.loads(args.spec.read_text(encoding='utf-8-sig')),
                     args.srt.read_text(encoding='utf-8-sig') if args.srt else None)
        print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(0 if result['passed'] else 1)
    except (OSError,ValueError,KeyError,TypeError,ZeroDivisionError,subprocess.SubprocessError) as e:
        print(json.dumps({'status':'incomplete','error':type(e).__name__})); raise SystemExit(2)
