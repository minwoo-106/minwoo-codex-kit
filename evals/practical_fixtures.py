"""Synthetic fixtures only. No account, private project or production service data."""
import copy
import json
from pathlib import Path
import struct
import subprocess
import zlib

ROOT=Path(__file__).resolve().parents[1]


def write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content if isinstance(content,str) else json.dumps(content,indent=2),encoding='utf-8',newline='\n')


def contract():
    schema={'type':'object','properties':{'name':{'type':'string','enum':['a','b']}},'required':['name']}
    body={'content':{'application/json':{'schema':copy.deepcopy(schema)}}}
    operation={'requestBody':copy.deepcopy(body),'responses':{'200':copy.deepcopy(body)}}
    return {'openapi':'3.1.1','paths':{'/items':{'post':operation}}}


def create(root,runtime):
    root.mkdir(parents=True,exist_ok=False)
    before=contract();after=copy.deepcopy(before)
    op=after['paths']['/items']['post']
    op['requestBody']['required']=True
    op['requestBody']['content']['application/json']['schema']['properties']['name']['enum']=['a']
    op['responses']['200']['content']['application/json']['schema']['required']=[]
    write(root/'api/before.json',before);write(root/'api/after.json',after)
    write(root/'migration/setup.sql',"CREATE TABLE items(id integer PRIMARY KEY,name text NOT NULL); INSERT INTO items VALUES(1,'one');")
    write(root/'migration/good.sql','ALTER TABLE items ADD COLUMN enabled boolean NOT NULL DEFAULT true;')
    write(root/'migration/up.sql',"UPDATE items SET name='changed'; ALTER TABLE items ADD COLUMN enabled boolean NOT NULL DEFAULT true;")
    write(root/'migration/down.sql','ALTER TABLE items DROP COLUMN enabled;')
    write(root/'migration/checks.json',{'before':[{'sql':'SELECT id,name FROM items ORDER BY id','rows':[{'id':1,'name':'one'}]}],
        'after':[{'sql':'SELECT id,name,enabled FROM items ORDER BY id','rows':[{'id':1,'name':'one','enabled':True}]}]})
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Synthetic browser fixture</title>
<label>Query <input data-testid="query"></label><button id="search">Search</button><output data-testid="result"></output>
<script>document.querySelector('#search').onclick=()=>{document.querySelector('output').textContent=RESULT;};</script></html>'''
    write(root/'browser/good.html',html.replace('RESULT',"document.querySelector('input').value"))
    write(root/'browser/bad.html',html.replace('RESULT',"'wrong result'"))
    write(root/'ci/app.py','def ratio(a, b):\n    return a // b\n')
    write(root/'ci/test_app.py',"import unittest\nfrom app import ratio\nclass RatioTest(unittest.TestCase):\n    def test_fraction(self): self.assertEqual(ratio(5,2),2.5)\n    def test_integer(self): self.assertEqual(ratio(6,2),3)\n")
    write(root/'ci/ci.log','Synthetic GitHub Actions log. Commit fixture-before.\nStep: python -m unittest -v\nFAIL test_fraction: 2 != 2.5\nNo live GitHub execution is represented.\n')
    write(root/'video/good.srt','1\n00:00:00,100 --> 00:00:00,800\nSample caption\n')
    write(root/'video/bad.srt','1\n00:00:00,100 --> 00:00:01,800\nSample caption\n')
    write(root/'video/good-spec.json',{'width':64,'height':36,'fps':30,'duration_min':0.9,'duration_max':1.1,'audio':False})
    write(root/'video/spec.json',{'width':64,'height':36,'fps':25,'audio':True})
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',64,36,8,2,0,0,0))
    png+=chunk(b'IDAT',zlib.compress((b'\0'+b'\x20\xa0\x60'*64)*36))+chunk(b'IEND',b'')
    (root/'video/frame.png').write_bytes(png)
    suffix='.exe' if __import__('os').name=='nt' else ''
    candidates=list((runtime/'node_modules/@remotion').glob('compositor-*/ffmpeg'+suffix))
    if len(candidates)!=1: raise ValueError('Expected one installed Remotion ffmpeg')
    ffmpeg=candidates[0];ffprobe=ffmpeg.with_name('ffprobe'+suffix)
    proc=subprocess.run([str(ffmpeg),'-v','error','-loop','1','-i',str(root/'video/frame.png'),
        '-t','1','-r','30','-c:v','libx264','-pix_fmt','yuv420p',str(root/'video/sample.mp4')],
        capture_output=True,timeout=60)
    if proc.returncode: raise RuntimeError('Synthetic media generation failed: '+proc.stderr.decode(errors='replace')[-400:])
    return {'ffprobe':ffprobe}
