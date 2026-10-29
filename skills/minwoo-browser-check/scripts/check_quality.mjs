import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';

export function validateQuality(config,remote=false) {
  const local=u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname);
  const base=new URL(config.baseURL);
  const origins=[base.origin,...(config.allowedOrigins||[])].map(x=>{
    const u=new URL(x);
    if(!['http:','https:'].includes(u.protocol)||u.username||u.password||(!remote&&!local(u)))throw Error('Unapproved origin');
    return u.origin;
  });
  if(base.username||base.password)throw Error('Credentials in URL');
  if(!Array.isArray(config.cases)||!config.cases.length||config.cases.length>30)throw Error('Expected 1..30 cases');
  const names=new Set();
  for(const c of config.cases){
    if(typeof c.name!=='string'||!/^[a-z0-9][a-z0-9_-]{0,63}$/.test(c.name)||names.has(c.name))throw Error('Unique safe case names required');
    names.add(c.name);
    if(typeof c.path!=='string')throw Error('Invalid page path');
    const target=new URL(c.path,base);
    if(target.username||target.password||!origins.includes(target.origin))throw Error('Invalid page path');
  }
  const viewport=config.viewport||{width:1280,height:720};
  if(![viewport.width,viewport.height].every(x=>Number.isInteger(x)&&x>=200&&x<=3000))throw Error('Invalid viewport');
  return {...config,viewport,origins:[...new Set(origins)]};
}
function safePath(target){
  let p=path.resolve(target);
  while(true){if(fs.existsSync(p)&&fs.lstatSync(p).isSymbolicLink())throw Error('Linked output/baseline path');const next=path.dirname(p);if(next===p)break;p=next;}
  return path.resolve(target);
}
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
export function runQuality(config,{runtime,browser,out,mode='accessibility',baseline,remote=false}){
  config=validateQuality(config,remote);
  if(!['accessibility','baseline','compare'].includes(mode))throw Error('Unknown mode');
  out=safePath(out);if(fs.existsSync(out))throw Error('Evidence folder already exists');
  if(mode!=='accessibility'){
    if(!baseline)throw Error('Baseline path required');
    baseline=safePath(baseline);
    if(baseline===out||baseline.startsWith(out+path.sep)||out.startsWith(baseline+path.sep))throw Error('Separate baseline and evidence folders required');
    if(mode==='baseline'&&fs.existsSync(baseline))throw Error('Baseline exists; create a new reviewed baseline');
    if(mode==='compare'){
      const manifest=JSON.parse(fs.readFileSync(path.join(baseline,'manifest.json'),'utf8'));
      const expected=[...config.cases.map(c=>c.name+'.png'),'environment.json'].sort();
      if(JSON.stringify(Object.keys(manifest).sort())!==JSON.stringify(expected))throw Error('Incomplete baseline');
      for(const [name,digest]of Object.entries(manifest)){
        const file=safePath(path.join(baseline,name));
        if(hash(file)!==digest)throw Error('Baseline changed: '+name);
      }
    }
  }
  const req=createRequire(path.join(path.resolve(runtime),'package.json'));
  const cli=req.resolve('@playwright/test/cli');
  fs.mkdirSync(out,{recursive:false});
  if(mode==='baseline')fs.mkdirSync(baseline,{recursive:false});
  const task={config,mode,baseline,out,browser,runtime:path.resolve(runtime),platform:process.platform,arch:process.arch,osRelease:os.release()};
  fs.writeFileSync(path.join(out,'input.json'),JSON.stringify(task),{flag:'wx'});
  fs.copyFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'quality.spec.cjs'),path.join(out,'quality.spec.cjs'),fs.constants.COPYFILE_EXCL);
  const settings={testDir:out,testMatch:'quality.spec.cjs',workers:1,retries:0,timeout:45000,
    outputDir:path.join(out,'test-results'),reporter:[['json',{outputFile:path.join(out,'results.json')}]],
    updateSnapshots:mode==='baseline'?'all':'none',snapshotPathTemplate:path.join(baseline||out,'{arg}{ext}'),
    use:{browserName:'chromium',headless:true,viewport:config.viewport,deviceScaleFactor:1,locale:'en-US',timezoneId:'UTC',
      colorScheme:'light',reducedMotion:'reduce',serviceWorkers:'block',trace:'retain-on-failure',
      launchOptions:browser?{executablePath:browser}:{}}};
  fs.writeFileSync(path.join(out,'playwright.config.cjs'),'module.exports = '+JSON.stringify(settings),{flag:'wx'});
  const proc=spawnSync(process.execPath,[cli,'test','--config',path.join(out,'playwright.config.cjs')],{cwd:out,encoding:'utf8',timeout:config.cases.length*50000+30000});
  fs.writeFileSync(path.join(out,'runner.log'),(proc.stdout||'')+'\n'+(proc.stderr||''),{flag:'wx'});
  let results;
  try{results=JSON.parse(fs.readFileSync(path.join(out,'results.json'),'utf8'));}catch{throw Error('Test runner incomplete; inspect private evidence');}
  const passed=proc.status===0&&!proc.error&&results.stats.expected===config.cases.length&&results.stats.unexpected===0&&results.stats.skipped===0;
  if(mode==='baseline'&&passed){
    const files=[...config.cases.map(c=>c.name+'.png'),'environment.json'];
    fs.writeFileSync(path.join(baseline,'manifest.json'),JSON.stringify(Object.fromEntries(files.map(n=>[n,hash(path.join(baseline,n))])),null,2)+'\n',{flag:'wx'});
  }
  const report={mode,passed,cases:config.cases.length,status:mode==='baseline'&&passed?'baseline-created':passed?'passed':'failed',
    scope:mode==='accessibility'?'axe automated rules only; manual accessibility review still required':'same-environment screenshot comparison; not a design quality judgment'};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  return report;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
  try{
    const options={},args=process.argv.slice(2);
    while(args.length){const key=args.shift();if(key==='--allow-remote')options.remote=true;
      else if(['--config','--runtime','--browser','--out','--mode','--baseline'].includes(key)&&args.length)options[key.slice(2)]=args.shift();
      else throw Error('Unknown/missing argument');}
    if(!options.config||!options.runtime||!options.out)throw Error('--config --runtime --out required');
    const report=runQuality(JSON.parse(fs.readFileSync(options.config,'utf8')),options);
    console.log(JSON.stringify(report));process.exitCode=report.passed?0:1;
  }catch(e){console.error('Quality check incomplete: '+e.message);process.exitCode=2;}
}
