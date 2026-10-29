import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
import {inspectSite,validateInspection} from '../skills/minwoo-browser-check/scripts/inspect_site.mjs';

const args=process.argv.slice(2),options={};
while(args.length){const k=args.shift();if(!['--runtime','--browser','--out'].includes(k)||!args.length)throw Error('Arguments');options[k.slice(2)]=args.shift();}
if(!options.runtime||!options.out)throw Error('--runtime --out required');
const out=path.resolve(options.out);fs.mkdirSync(out,{recursive:false});
const results=[];let submissions=0,stored=[];
const head='<meta charset="utf-8"><title>합성 사이트</title><meta property="og:title" content="Example"><meta property="og:description" content="Example"><meta property="og:image" content="/image.svg">';
const page=body=>'<!doctype html><html lang="ko"><head>'+head+'</head><body><main><h1>합성 사이트</h1>'+body+'</main></body></html>';
const form=page('<form><label for="name">이름</label><input id="name" required><button>접수하기</button><p role="status"></p></form><script>let pending=false;document.querySelector("form").onsubmit=async e=>{e.preventDefault();if(pending)return;pending=true;const b=document.querySelector("button");b.disabled=true;try{const r=await fetch("/submit"+location.search,{method:"POST",body:document.querySelector("input").value});document.querySelector("[role=status]").textContent=r.ok?"접수 완료":"접수 실패";}catch{document.querySelector("[role=status]").textContent="연결 실패";}finally{pending=false;b.disabled=false;}};</script>');
const server=http.createServer((req,res)=>{
  const u=new URL(req.url,'http://localhost');
  if(u.pathname==='/submit'){
    submissions++;let body='';req.on('data',c=>body+=c);req.on('end',()=>setTimeout(()=>{if(u.searchParams.has('fail')){res.writeHead(503);res.end('no');}else{stored.push(body);res.end('ok');}},250));return;
  }
  if(u.pathname==='/image.svg'){res.writeHead(200,{'content-type':'image/svg+xml'});res.end('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><rect width="800" height="400" fill="blue"/></svg>');return;}
  const pages={'/':page('<a href="/about">소개</a><a href="#detail">상세</a><h2 id="detail">상세</h2><img src="/image.svg" width="200" height="100" alt="합성 도형">'),'/about':page('소개'),'/fragment':page('<a href="#missing">없는 위치</a>'),'/broken-image':page('<img src="/missing-image" alt="검사">'),'/review':'<html><head><title>검토</title></head><body>검토</body></html>','/form':form};
  res.writeHead(pages[u.pathname]?200:404,{'content-type':'text/html; charset=utf-8'});res.end(pages[u.pathname]||'Not found');
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const baseURL='http://127.0.0.1:'+server.address().port;
const base={baseURL,cases:[{name:'home',path:'/'}]};
async function run(name,config,mode,status){const r=await inspectSite(config,{runtime:options.runtime,browser:options.browser,out:path.join(out,name),mode});assert.equal(r.status,status,name);results.push({case:name,passed:true});return r;}
try{
  const good=await run('launch-good',{...base,linkPaths:['/about']},'launch','observed');
  assert.equal(good.links[0].status,200);assert.equal(good.cases[0].samples[0].images[0].naturalWidth,800);
  assert.equal(good.cases[0].samples[0].images[0].displayWidth,200);
  const broken=await run('broken-link',{...base,linkPaths:['/missing']},'launch','issues');assert.equal(broken.links[0].status,404);
  const fragment=await run('broken-fragment',{...base,cases:[{name:'home',path:'/fragment'}]},'launch','issues');assert.equal(fragment.cases[0].samples[0].brokenFragments,1);
  const img=await run('broken-image',{...base,cases:[{name:'home',path:'/broken-image'}]},'launch','issues');assert(img.cases[0].samples[0].issues.includes('eager-image-not-loaded'));
  await run('missing-share-review',{...base,cases:[{name:'home',path:'/review'}]},'launch','review');
  const perf=await run('performance-samples',{...base,runs:3},'performance','observed');assert.equal(perf.cases[0].samples.length,3);assert(perf.cases[0].summary.medianLoadMs>0);
  const budget=await run('explicit-budget',{...base,runs:1,maxLoadMs:0.000001},'performance','issues');assert(budget.cases[0].budgetExceeded);
  assert.throws(()=>validateInspection({...base,baseURL:'https://example.test'}));assert.throws(()=>validateInspection({...base,linkPaths:['https://elsewhere.test/']}));assert.throws(()=>validateInspection({...base,runs:8}));results.push({case:'input-boundaries',passed:true});
  await assert.rejects(()=>inspectSite(base,{runtime:options.runtime,out:path.join(out,'launch-good')}));results.push({case:'no-overwrite',passed:true});
  const req=createRequire(path.join(path.resolve(options.runtime),'package.json'));const {chromium,expect}=(()=>({chromium:req('playwright').chromium,expect:req('@playwright/test').expect}))();
  const browser=await chromium.launch({headless:true,...(options.browser?{executablePath:options.browser}:{})});
  try{
    const context=await browser.newContext(),p=await context.newPage();
    await p.goto(baseURL+'/form');await p.getByRole('button').click();assert.equal(submissions,0);results.push({case:'form-empty-rejected',passed:true});
    await p.getByLabel('이름').fill('합성 고객');await p.getByRole('button').dblclick();await expect(p.getByRole('status')).toHaveText('접수 완료');assert.equal(submissions,1);assert.deepEqual(stored,['합성 고객']);results.push({case:'form-receipt-and-double-click',passed:true});
    await p.goto(baseURL+'/form?fail=1');await p.getByLabel('이름').fill('실패 고객');await p.getByRole('button').click();await expect(p.getByRole('status')).toHaveText('접수 실패');assert.equal(submissions,2);assert.equal(stored.length,1);results.push({case:'form-server-failure-not-success',passed:true});
    await p.goto(baseURL+'/form');await p.getByLabel('이름').fill('재시도 고객');await p.getByRole('button').click();await expect(p.getByRole('status')).toHaveText('접수 완료');assert.equal(stored.length,2);assert.equal(stored[1],'재시도 고객');results.push({case:'form-retry-receipt',passed:true});await context.close();
  }finally{await browser.close();}
  const summary={passed:true,cases:results.length,results,scope:'real browser on local synthetic routes and in-memory form receipts; not production delivery, visual taste or field performance'};
  fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary,null,2));
}finally{await new Promise(r=>server.close(r));}
