import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {validateQuality} from './check_quality.mjs';

export function validateInspection(config,remote=false){
  const c=validateQuality(config,remote);
  c.runs=config.runs??3;
  if(!Number.isInteger(c.runs)||c.runs<1||c.runs>7)throw Error('Expected 1..7 runs');
  c.linkPaths=config.linkPaths??[];
  if(!Array.isArray(c.linkPaths)||c.linkPaths.length>30)throw Error('Expected at most 30 explicit link paths');
  for(const value of c.linkPaths){
    if(typeof value!=='string')throw Error('Link path must be string');
    const u=new URL(value,c.baseURL);
    if(u.origin!==new URL(c.baseURL).origin||u.username||u.password)throw Error('Link checks must use the base origin without credentials');
  }
  if(c.maxLoadMs!==undefined&&(!Number.isFinite(c.maxLoadMs)||c.maxLoadMs<=0))throw Error('Invalid load budget');
  return c;
}
function newOutput(value){
  const out=path.resolve(value);let p=out;
  while(true){if(fs.existsSync(p)&&fs.lstatSync(p).isSymbolicLink())throw Error('Linked output path');const parent=path.dirname(p);if(parent===p)break;p=parent;}
  if(fs.existsSync(out))throw Error('Output already exists');
  fs.mkdirSync(out,{recursive:false});return out;
}
const median=values=>{const a=[...values].sort((a,b)=>a-b);return a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2;};
export async function inspectSite(input,{runtime,browser,out,mode='launch',remote=false}){
  const config=validateInspection(input,remote);
  if(!['launch','performance'].includes(mode))throw Error('Unknown mode');
  const req=createRequire(path.join(path.resolve(runtime),'package.json'));
  const {chromium}=req('playwright');out=newOutput(out);
  const instance=await chromium.launch({headless:true,...(browser?{executablePath:browser}:{})});
  const cases=[],links=[];
  const count=mode==='performance'?config.runs:1;
  async function session(){
    const context=await instance.newContext({viewport:config.viewport,deviceScaleFactor:1,locale:'ko-KR',timezoneId:'UTC',serviceWorkers:'block'});
    const blocked=[];
    await context.route('**/*',route=>{
      if(config.origins.includes(new URL(route.request().url()).origin))return route.continue();
      blocked.push('outside-origin');return route.abort();
    });
    return {context,blocked};
  }
  try{
    for(const c of config.cases){
      const samples=[];
      for(let iteration=0;iteration<count;iteration++){
        const {context,blocked}=await session();const page=await context.newPage();let pageErrors=0;
        page.on('pageerror',()=>pageErrors++);
        const sample={iteration:iteration+1,issues:[],review:[]};
        try{
          const response=await page.goto(new URL(c.path,config.baseURL).href,{waitUntil:'load',timeout:20000});
          sample.status=response?.status()??null;
          if(!response?.ok())sample.issues.push('http-not-success');
          await page.evaluate(()=>document.fonts.ready);
          const observed=await page.evaluate(()=>{
            const n=performance.getEntriesByType('navigation')[0];
            const images=[...document.images].map((im,index)=>({index,loaded:im.complete&&im.naturalWidth>0,naturalWidth:im.naturalWidth,naturalHeight:im.naturalHeight,displayWidth:im.getBoundingClientRect().width,displayHeight:im.getBoundingClientRect().height,loading:im.loading,altPresent:im.hasAttribute('alt')}));
            const anchors=[...document.querySelectorAll('a[href]')];
            const brokenFragments=anchors.filter(a=>{const u=new URL(a.href,location.href);if(u.origin!==location.origin||u.pathname!==location.pathname||u.search!==location.search||!u.hash||u.hash==='#')return false;try{const id=decodeURIComponent(u.hash.slice(1));return !document.getElementById(id)&&![...document.getElementsByName(id)].some(e=>e.tagName==='A');}catch{return true;}}).length;
            const meta=key=>Boolean(document.querySelector('meta[property="'+key+'"]')?.getAttribute('content')?.trim());
            return {timing:n?{ttfbMs:n.responseStart-n.requestStart,domContentLoadedMs:n.domContentLoadedEventEnd,loadMs:n.loadEventEnd,documentTransferBytes:n.transferSize}:null,
              images,brokenFragments,titlePresent:Boolean(document.title.trim()),share:{title:meta('og:title'),description:meta('og:description'),image:meta('og:image')},horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1};
          });
          Object.assign(sample,observed);
          if(!observed.timing||observed.timing.loadMs<=0)sample.issues.push('navigation-timing-incomplete');
          if(observed.images.some(i=>!i.loaded&&i.loading!=='lazy'))sample.issues.push('eager-image-not-loaded');
          if(observed.brokenFragments)sample.issues.push('missing-fragment-target');
          if(!observed.titlePresent)sample.review.push('title-missing');
          if(Object.values(observed.share).some(v=>!v))sample.review.push('sharing-metadata-incomplete');
          if(observed.horizontalOverflow)sample.review.push('horizontal-overflow');
          if(observed.images.some(i=>i.loading==='lazy'&&!i.loaded))sample.review.push('lazy-images-not-yet-observed');
          await page.screenshot({path:path.join(out,c.name+'-'+(iteration+1)+'.png'),fullPage:true});
        }catch{sample.issues.push('navigation-or-inspection-failed');}
        finally{if(pageErrors)sample.issues.push('page-error');if(blocked.length)sample.issues.push('outside-origin-request');await context.close();}
        samples.push(sample);
      }
      const valid=samples.filter(s=>s.timing&&s.issues.length===0);
      const summary=valid.length===count?{medianTtfbMs:median(valid.map(s=>s.timing.ttfbMs)),medianLoadMs:median(valid.map(s=>s.timing.loadMs))}:null;
      const budgetExceeded=summary&&config.maxLoadMs!==undefined&&summary.medianLoadMs>config.maxLoadMs;
      cases.push({name:c.name,samples,summary,budgetExceeded:Boolean(budgetExceeded)});
    }
    if(mode==='launch')for(const [index,link] of config.linkPaths.entries()){
      const {context,blocked}=await session();const page=await context.newPage();let status=null;
      try{status=(await page.goto(new URL(link,config.baseURL).href,{waitUntil:'domcontentloaded',timeout:15000}))?.status()??null;}catch{}
      finally{await context.close();}
      links.push({index,status,passed:status!==null&&status>=200&&status<300&&!blocked.length});
    }
  }finally{await instance.close();}
  const failed=cases.some(c=>c.budgetExceeded||c.samples.some(s=>s.issues.length))||links.some(l=>!l.passed);
  const review=cases.some(c=>c.samples.some(s=>s.review.length));
  const report={mode,status:failed?'issues':review?'review':'observed',browser:instance.version(),viewport:config.viewport,runs:count,cases,links,
    conditions:'fresh browser contexts; no network/CPU throttling; shared host/DNS/OS caches; explicit pages only',
    scope:'Navigation Timing lab samples, rendered img elements and selected HTTP/DOM checks; not Core Web Vitals, user perception, licensing, full crawling or launch approval'};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});return report;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
  try{
    const args=process.argv.slice(2),options={};
    while(args.length){const k=args.shift();if(k==='--allow-remote')options.remote=true;else if(['--runtime','--browser','--out','--config','--mode'].includes(k)&&args.length)options[k.slice(2)]=args.shift();else throw Error('Unknown/missing argument');}
    if(!options.runtime||!options.config||!options.out)throw Error('--runtime --config --out required');
    const r=await inspectSite(JSON.parse(fs.readFileSync(options.config,'utf8')),options);console.log(JSON.stringify(r));process.exitCode=r.status==='issues'?1:r.status==='review'?2:0;
  }catch(e){console.error('Inspection incomplete: '+e.message);process.exitCode=2;}
}
