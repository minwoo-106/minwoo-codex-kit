import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

export async function rehearse({runtime,setup,up,checks,down}) {
  if (!Array.isArray(checks.before) || !checks.before.length || !Array.isArray(checks.after) || !checks.after.length)
    throw Error('Nonempty before and after assertions required');
  const require=createRequire(path.join(path.resolve(runtime),'package.json'));
  const {PGlite}=require('@electric-sql/pglite');
  const db=new PGlite();
  const report={passed:false,engine:'PGlite in-memory',checks:[],rollback:down?'not reached':'not tested',
    scope:'synthetic isolated SQL; no production concurrency or Supabase authentication'};
  let stage='setup';
  try {
    await db.exec(setup);
    const verify=async (items,label)=>{
      for(const [index,c] of items.entries()) {
        if(typeof c.sql!=='string' || !Array.isArray(c.rows)) throw Error('Invalid assertion');
        const rows=(await db.query(c.sql)).rows;
        assert.deepEqual(rows,c.rows,'Row assertion failed');
        report.checks.push({stage:label,index,passed:true});
      }
    };
    stage='before'; await verify(checks.before,stage);
    stage='up'; await db.exec(up);
    stage='after'; await verify(checks.after,stage);
    if(down) {
      stage='down'; await db.exec(down);
      stage='restored'; await verify(checks.before,stage);
      report.rollback='verified against before assertions';
    }
    report.passed=true;
  } catch(e) { report.failed_stage=stage; report.error=e.code || e.name; }
  finally { await db.close(); }
  return report;
}

if(process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const options={};const args=process.argv.slice(2);
    while(args.length) { const key=args.shift(); if(!['--runtime','--setup','--up','--checks','--down'].includes(key)||!args.length) throw Error('Invalid arguments'); options[key.slice(2)]=args.shift(); }
    for(const key of ['setup','up','checks','runtime']) if(!options[key]) throw Error('Missing '+key);
    for(const key of ['setup','up','checks','down']) if(options[key]) options[key]=fs.readFileSync(options[key],'utf8');
    options.checks=JSON.parse(options.checks);
    const result=await rehearse(options);console.log(JSON.stringify(result,null,2));process.exitCode=result.passed?0:1;
  } catch(e) {console.error('Rehearsal incomplete: '+e.message);process.exitCode=2;}
}
