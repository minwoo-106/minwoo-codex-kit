const fs=require('node:fs');
const path=require('node:path');
const {createRequire}=require('node:module');
const task=JSON.parse(fs.readFileSync(path.join(__dirname,'input.json'),'utf8'));
const req=createRequire(path.join(task.runtime,'package.json'));
const {test,expect}=req('@playwright/test');
const AxeBuilder=req('@axe-core/playwright').default;
const {config,mode,baseline,out}=task;
test.beforeAll(async({browser})=>{
  if(mode==='accessibility')return;
  const environment={platform:task.platform,arch:task.arch,osRelease:task.osRelease,browser:browser.version(),
    viewport:config.viewport,deviceScaleFactor:1,locale:'en-US',timezoneId:'UTC',colorScheme:'light',reducedMotion:'reduce',
    pages:config.cases.map(c=>({name:c.name,path:c.path}))};
  const file=path.join(baseline,'environment.json');
  if(mode==='baseline')fs.writeFileSync(file,JSON.stringify(environment,null,2)+'\n',{flag:'wx'});
  else expect(environment,'Browser, OS, viewport or page mapping changed; do not silently replace baseline').toEqual(JSON.parse(fs.readFileSync(file,'utf8')));
});
for(const c of config.cases)test(c.name,async({page})=>{
  const blocked=[],errors=[];
  await page.route('**/*',route=>{
    const u=new URL(route.request().url());
    if(config.origins.includes(u.origin))return route.continue();
    blocked.push(u.origin);return route.abort();
  });
  page.on('pageerror',e=>errors.push(e.message));
  const response=await page.goto(new URL(c.path,config.baseURL).href,{waitUntil:'load',timeout:15000});
  expect(response&&response.ok(),'Page must load successfully').toBeTruthy();
  await page.evaluate(()=>document.fonts.ready);
  if(mode==='accessibility'){
    const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
    const summarize=items=>items.map(v=>({id:v.id,impact:v.impact,help:v.help,helpUrl:v.helpUrl,targets:v.nodes.map(n=>n.target)}));
    fs.writeFileSync(path.join(out,c.name+'-axe.json'),JSON.stringify({violations:summarize(results.violations),incomplete:summarize(results.incomplete)},null,2)+'\n',{flag:'wx'});
    await page.screenshot({path:path.join(out,c.name+'.png'),fullPage:true});
    expect(results.violations.map(v=>v.id),'Automated accessibility violations').toEqual([]);
  }else await expect(page).toHaveScreenshot(c.name+'.png',{fullPage:true,animations:'disabled',caret:'hide',maxDiffPixels:0,threshold:0.2,timeout:10000});
  expect(errors,'Page errors').toEqual([]);expect(blocked,'Requests outside allowed origins').toEqual([]);
});
