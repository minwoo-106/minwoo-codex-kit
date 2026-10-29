import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

export function validate(config, remote=false) {
  const local = u => ['127.0.0.1','localhost','[::1]'].includes(u.hostname);
  const base = new URL(config.baseURL);
  const origins = [base.origin, ...(config.allowedOrigins || [])].map(value => {
    const u = new URL(value);
    if (!['http:','https:'].includes(u.protocol) || u.username || u.password || (!remote && !local(u))) throw Error('Unapproved origin');
    return u.origin;
  });
  if (base.username || base.password) throw Error('Credentials in URL');
  if (!Array.isArray(config.cases) || !config.cases.length || config.cases.length>50) throw Error('Expected 1..50 cases');
  const actions = new Set(['goto','fill','click','text','value','count','visible']);
  for (const c of config.cases) {
    if (typeof c.name!=='string' || !Array.isArray(c.steps) || !c.steps.length || c.steps.length>100) throw Error('Invalid case');
    if (!c.steps.some(s=>['text','value','count','visible'].includes(s.action))) throw Error('Case needs an assertion');
    for (const s of c.steps) {
      if (!actions.has(s.action)) throw Error('Unknown action');
      if (s.action==='goto') {
        if (!origins.includes(new URL(s.path,base).origin)) throw Error('Navigation outside allowed origins');
      } else if (!(typeof s.testId==='string' || (typeof s.role==='string' && typeof s.name==='string'))) throw Error('Locator required');
      if (['fill','text','value'].includes(s.action) && typeof s.value!=='string') throw Error('String value required');
      if (s.action==='count' && (!Number.isInteger(s.value) || s.value<0)) throw Error('Count must be nonnegative integer');
    }
  }
  return {base, origins:new Set(origins)};
}

export async function run(config, {runtime,browser,out,remote=false}) {
  const {base,origins}=validate(config,remote);
  const require=createRequire(path.join(path.resolve(runtime),'package.json'));
  const {chromium}=require('playwright');
  if (fs.existsSync(out)) throw Error('Evidence folder already exists');
  fs.mkdirSync(out,{recursive:false});
  const instance=await chromium.launch({headless:true,...(browser?{executablePath:browser}:{})});
  const results=[];
  try {
    for (const [index,c] of config.cases.entries()) {
      const dir=path.join(out,String(index+1)); fs.mkdirSync(dir);
      const context=await instance.newContext({serviceWorkers:'block'});
      const errors=[]; const blocked=[];
      await context.route('**/*',route=>{
        const url=new URL(route.request().url());
        if (origins.has(url.origin)) return route.continue();
        blocked.push(url.origin); return route.abort();
      });
      await context.tracing.start({screenshots:true,snapshots:true});
      const page=await context.newPage();
      page.on('pageerror',e=>errors.push(e.message));
      let step=-1;
      const result={name:c.name,passed:false};
      try {
        for (const [i,s] of c.steps.entries()) {
          step=i;
          if (s.action==='goto') {
            const response=await page.goto(new URL(s.path,base).href,{timeout:15000});
            if (!response || response.status()>=400) throw Error('Navigation failed');
            continue;
          }
          const locator=s.testId ? page.getByTestId(s.testId) : page.getByRole(s.role,{name:s.name,exact:true});
          if (s.action==='fill') await locator.fill(s.value,{timeout:5000});
          else if (s.action==='click') await locator.click({timeout:5000});
          else {
            const end=Date.now()+5000; let ok=false;
            do {
              if (s.action==='count') ok=(await locator.count())===s.value;
              else if (await locator.count()===1) {
                if (s.action==='visible') ok=await locator.isVisible();
                if (s.action==='text') ok=(await locator.textContent({timeout:500})).trim()===s.value;
                if (s.action==='value') ok=(await locator.inputValue({timeout:500}))===s.value;
              }
              if (!ok) await new Promise(resolve=>setTimeout(resolve,50));
            } while (!ok && Date.now()<end);
            if (!ok) throw Error('Assertion failed: '+s.action);
          }
        }
        if (errors.length || blocked.length) throw Error('Page errors or blocked network requests');
        result.passed=true;
      } catch(e) { result.failed_step=step; result.error=e.message; }
      finally {
        result.page_errors=errors; result.blocked_origins=[...new Set(blocked)];
        await page.screenshot({path:path.join(dir,'screenshot.png'),fullPage:true});
        await context.tracing.stop({path:path.join(dir,'trace.zip')});
        await context.close();
      }
      results.push(result);
    }
  } finally { await instance.close(); }
  const report={passed:results.every(r=>r.passed),browser:instance.version(),cases:results,
    scope:'DOM interactions in fresh browser contexts; no design/accessibility certification'};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  return report;
}

if (process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const options={}; const args=process.argv.slice(2);
    while(args.length) { const key=args.shift(); if(key==='--allow-remote') options.remote=true;
      else if(['--runtime','--browser','--config','--out'].includes(key) && args.length) options[key.slice(2)]=args.shift();
      else throw Error('Unknown/missing argument'); }
    if (!options.runtime || !options.config || !options.out) throw Error('--runtime --config --out required');
    const report=await run(JSON.parse(fs.readFileSync(options.config,'utf8')),options);
    console.log(JSON.stringify(report)); process.exitCode=report.passed?0:1;
  } catch(e) { console.error('Browser check incomplete: '+e.message); process.exitCode=2; }
}
