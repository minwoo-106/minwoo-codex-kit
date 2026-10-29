import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import fc from 'fast-check';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {PGlite} from '@electric-sql/pglite';
import {parseSrt} from '@remotion/captions';

const root = path.dirname(fileURLToPath(import.meta.url));
const seed = 20261029;
const broken = fc.check(fc.property(fc.array(fc.integer({min:-100,max:100})), xs =>
  JSON.stringify(xs.filter(Boolean)) === JSON.stringify(xs)), {seed,numRuns:500});
assert.equal(broken.failed, true, 'broken implementation must be rejected');
fc.assert(fc.property(fc.array(fc.integer()), xs =>
  JSON.stringify(JSON.parse(JSON.stringify(xs))) === JSON.stringify(xs)), {seed,numRuns:500});
console.log('PASS fast-check: bad round-trip rejected; correct round-trip passed (500 runs)');

const Counter = React.createContext(null);
function Display() { return React.createElement('output',null,React.useContext(Counter).count); }
function Panel({count,children}) {
  return React.createElement(Counter.Provider,{value:{count}},children);
}
assert.equal(renderToStaticMarkup(React.createElement(Panel,{count:7},React.createElement(Display))),'<output>7</output>');
const started=[]; const releases=[];
const request = id => { started.push(id); return new Promise(resolve=>releases.push(()=>resolve(id))); };
const pending=Promise.all([request('a'),request('b')]);
assert.deepEqual(started,['a','b']);
releases.forEach(fn=>fn());
assert.deepEqual(await pending,['a','b']);
console.log('PASS React: context composition SSR; independent requests start together (not an app benchmark)');

const db=new PGlite();
try {
  await db.exec("CREATE TABLE notes(id integer PRIMARY KEY, tenant text NOT NULL, body text NOT NULL); INSERT INTO notes VALUES(1,'a','one'),(2,'b','two'); CREATE INDEX notes_tenant ON notes(tenant); CREATE ROLE app_reader; GRANT SELECT,INSERT ON notes TO app_reader; ALTER TABLE notes ENABLE ROW LEVEL SECURITY; CREATE POLICY own_notes ON notes USING (tenant=current_setting('app.tenant')) WITH CHECK (tenant=current_setting('app.tenant')); SET app.tenant='a'; SET ROLE app_reader;");
  assert.deepEqual((await db.query('SELECT id FROM notes ORDER BY id')).rows,[{id:1}]);
  await assert.rejects(db.query("INSERT INTO notes VALUES(3,'b','forbidden')"), /row-level security/i);
  await db.query("INSERT INTO notes VALUES(4,'a','allowed')");
  assert.equal((await db.query('SELECT id FROM notes')).rows.length,2);
  const plan=await db.query("EXPLAIN SELECT * FROM notes WHERE tenant='a'");
  assert.ok(plan.rows.length);
  console.log('PASS PGlite: schema/index/query; RLS allowed and denied under non-owner role');
} finally { await db.close(); }

const {captions}=parseSrt({input:'1\n00:00:00,300 --> 00:00:00,900\n한글 자막\n'});
assert.equal(captions.length,1);
assert.equal(captions[0].startMs,300);
assert.equal(captions[0].endMs,900);
assert.equal(captions[0].text.trim(),'한글 자막');
console.log('PASS SRT: Korean text and millisecond boundaries');
if(process.argv.includes('--render')) {
  const {bundle}=await import('@remotion/bundler');
  const {selectComposition,renderMedia,renderStill,getVideoMetadata}=await import('@remotion/renderer');
  const output=fs.mkdtempSync(path.join(process.env.KIT_TEST_OUTPUT ?? os.tmpdir(),'kit-tools-'));
  const browserExecutable=process.env.KIT_BROWSER_EXECUTABLE;
  const serveUrl=await bundle({entryPoint:path.join(root,'fixtures/captions.jsx'),outDir:path.join(output,'bundle')});
  const composition=await selectComposition({serveUrl,id:'CaptionCheck',browserExecutable});
  const video=path.join(output,'captions.mp4');
  await renderMedia({composition,serveUrl,codec:'h264',outputLocation:video,browserExecutable,concurrency:2});
  for(const frame of [0,15,40]) {
    await renderStill({composition,serveUrl,frame,imageFormat:'png',
      output:path.join(output,'frame-'+frame+'.png'),browserExecutable});
  }
  const metadata=await getVideoMetadata(video);
  assert.equal(metadata.width,640); assert.equal(metadata.height,360);
  assert.equal(metadata.fps,30);
  assert.ok(Math.abs(metadata.durationInSeconds-2)<0.1);
  fs.writeFileSync(path.join(output,'result.json'),JSON.stringify({metadata,seed,video},null,2));
  console.log('PASS actual video: 640x360, 30fps, 2 seconds; no audio in this fixture');
  console.log('OUTPUT '+output);
}
