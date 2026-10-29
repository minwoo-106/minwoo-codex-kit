"""Execute real helper tools on valid and intentionally invalid synthetic artifacts."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from practical_fixtures import create, ROOT

def load(name,relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--browser')
    args=p.parse_args();root=args.out.resolve();runtime=args.runtime.resolve()
    info=create(root,runtime)
    api=load('api','skills/minwoo-api-compat/scripts/check_contract.py')
    media=load('media','skills/minwoo-video-review/scripts/check_delivery.py')
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    before,after=read('api/before.json'),read('api/after.json')
    assert api.compare(before,before)['status']=='no-breaking-detected'
    result=api.compare(before,after);assert result['counts']['breaking']==3
    (root/'api/report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    good=media.check(root/'video/sample.mp4',info['ffprobe'],read('video/good-spec.json'),(root/'video/good.srt').read_text())
    bad=media.check(root/'video/sample.mp4',info['ffprobe'],read('video/spec.json'),(root/'video/bad.srt').read_text())
    assert good['passed'] and not bad['passed'] and len(bad['failures'])==3
    (root/'video/report.json').write_text(json.dumps(bad,indent=2),encoding='utf-8')
    command=['node',str(ROOT/'evals/verify_practical.mjs'),'--runtime',str(runtime),'--fixtures',str(root)]
    if args.browser: command+=['--browser',args.browser]
    proc=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=120)
    if proc.returncode: raise RuntimeError(proc.stderr[-2000:])
    node=json.loads(proc.stdout)
    result={'passed':True,'cases':8,'api_breaking_detected':3,'video_failures_detected':bad['failures'],
        'browser_and_migration':node['results'],'scope':'real helper execution on synthetic artifacts; not model selection'}
    (root/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
