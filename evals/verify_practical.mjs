import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {run,validate} from '../skills/minwoo-browser-check/scripts/check_browser.mjs';
import {rehearse} from '../skills/minwoo-postgres-review/scripts/rehearse.mjs';
const args=process.argv.slice(2);const options={};
while(args.length) options[args.shift().replace(/^--/,'')]=args.shift();
const root=path.resolve(options.fixtures),runtime=path.resolve(options.runtime);
const server=http.createServer((req,res)=>{
  const file=req.url==='/good'?'good.html':req.url==='/bad'?'bad.html':null;
  if(!file){res.writeHead(404).end();return;}
  res.setHeader('Content-Type','text/html');res.end(fs.readFileSync(path.join(root,'browser',file)));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const baseURL='http://127.0.0.1:'+server.address().port;
const steps=route=>[{action:'goto',path:route},{action:'fill',testId:'query',value:'apple'},
  {action:'click',role:'button',name:'Search'},{action:'text',testId:'result',value:'apple'}];
const results=[];
try {
  assert.throws(()=>validate({baseURL:'https://example.invalid',cases:[]}));
  assert.throws(()=>validate({baseURL,cases:[{name:'no assertion',steps:[{action:'goto',path:'/good'}]}]}));
  for(const [route,expected] of [['good',true],['bad',false]]) {
    const out=path.join(root,'browser','evidence-'+route);
    const r=await run({baseURL,cases:[{name:'search',steps:steps('/'+route)}]},
      {runtime,browser:options.browser,out});
    assert.equal(r.passed,expected);assert.ok(fs.statSync(path.join(out,'1/screenshot.png')).size>100);
    results.push({case:'browser-'+route,expected,actual:r.passed,passed:true});
  }
  const read=name=>fs.readFileSync(path.join(root,'migration',name),'utf8');
  for(const [up,expected] of [['good.sql',true],['up.sql',false]]) {
    const r=await rehearse({runtime,setup:read('setup.sql'),up:read(up),down:read('down.sql'),checks:JSON.parse(read('checks.json'))});
    assert.equal(r.passed,expected);
    if(expected) assert.equal(r.rollback,'verified against before assertions');
    fs.writeFileSync(path.join(root,'migration',up+'.report.json'),JSON.stringify(r,null,2));
    results.push({case:'migration-'+up,expected,actual:r.passed,passed:true});
  }
} finally {await new Promise(resolve=>server.close(resolve));}
console.log(JSON.stringify({passed:true,results},null,2));
