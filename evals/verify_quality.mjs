import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {validateQuality} from '../skills/minwoo-browser-check/scripts/check_quality.mjs';
import {validate} from '../skills/minwoo-browser-check/scripts/check_browser.mjs';
assert.throws(()=>validateQuality({baseURL:'http://localhost',cases:[{path:'/'}]}));
assert.throws(()=>validateQuality({baseURL:'http://localhost',cases:[{name:'home',path:'http://u:p@localhost/'}]}));
assert.throws(()=>validate({baseURL:'http://localhost',cases:[{name:'bad',steps:[{action:'goto',path:'http://u:p@localhost/'},{action:'visible',testId:'x'}]}]}));
const exec=promisify(execFile),args=process.argv.slice(2),options={};
while(args.length){const key=args.shift();if(!['--runtime','--browser','--out'].includes(key)||!args.length)throw Error('Arguments');options[key.slice(2)]=args.shift();}
if(!options.runtime||!options.out)throw Error('--runtime --out required');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.resolve(options.out);fs.mkdirSync(out,{recursive:false});
let altered=false;
const good='<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Fixture</title></head><body><main><h1>Search</h1><label for="query">Query</label><input id="query"><button>Search</button></main></body></html>';
const bad=good.replace('<label for="query">Query</label>','').replace('<button>Search</button>','<button></button><img src="data:image/png;base64," width="10" height="10">');
const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html'});res.end(req.url==='/bad'?bad:altered?good.replace('<h1>','<h1 style="background: red; padding:40px">'):good);});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const baseURL='http://127.0.0.1:'+server.address().port;
const config=path.join(out,'config.json'),baseline=path.join(out,'baseline');
const writeConfig=p=>fs.writeFileSync(config,JSON.stringify({baseURL,cases:[{name:'home',path:p}]}));
const results=[];
async function run(name,mode,expected,extra=[]){
  const evidence=path.join(out,name);
  const command=[path.join(root,'skills/minwoo-browser-check/scripts/check_quality.mjs'),'--runtime',path.resolve(options.runtime),'--config',config,'--out',evidence,'--mode',mode];
  if(mode!=='accessibility')command.push('--baseline',baseline);
  if(options.browser)command.push('--browser',options.browser);
  command.push(...extra);
  let code=0;try{await exec(process.execPath,command,{timeout:90000});}catch(e){code=e.code;}
  assert.equal(code,expected,name);
  results.push({case:name,expected_exit:expected,actual_exit:code,passed:true});return evidence;
}
try{
  writeConfig('/good');await run('accessibility-good','accessibility',0);
  writeConfig('/bad');const badDir=await run('accessibility-bad','accessibility',1);
  const violations=JSON.parse(fs.readFileSync(path.join(badDir,'home-axe.json'))).violations.map(v=>v.id);
  assert(violations.includes('label')&&violations.includes('button-name'));
  writeConfig('/screen');await run('baseline-created','baseline',0);
  const digest=()=>crypto.createHash('sha256').update(fs.readFileSync(path.join(baseline,'home.png'))).digest('hex');
  const before=digest();await run('visual-same','compare',0);
  altered=true;const diff=await run('visual-changed','compare',1);assert.equal(digest(),before);
  const files=fs.readdirSync(path.join(diff,'test-results'),{recursive:true});assert(files.some(f=>f.endsWith('-diff.png')));
  await run('baseline-overwrite-rejected','baseline',2);
  fs.appendFileSync(path.join(baseline,'home.png'),'changed');await run('baseline-tamper-rejected','compare',2);
  fs.writeFileSync(config,JSON.stringify({baseURL:'https://example.test',cases:[{name:'home',path:'/'}]}));await run('remote-without-opt-in','accessibility',2);
  const summary={passed:true,cases:results.length,results,scope:'real local browser and axe/Playwright screenshot checks on synthetic pages; baseline never silently updated'};
  fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary,null,2));
}finally{await new Promise(resolve=>server.close(resolve));}
