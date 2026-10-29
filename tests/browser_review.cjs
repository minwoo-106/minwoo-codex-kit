/* Optional real-browser smoke test. Requires playwright and a browser, not production dependencies.
   KIT_BROWSER_TEST_ROOT selects a writable parent. KIT_BROWSER_CHANNEL can select msedge.
   Synthetic WebM clips are generated in the browser; no private assets or FFmpeg required. */
const {chromium}=require("playwright");
const fs=require("node:fs"), path=require("node:path"), os=require("node:os");
const {spawn,spawnSync}=require("node:child_process");
const assert=require("node:assert/strict");
const repo=path.resolve(__dirname,"..");
const root=fs.mkdtempSync(path.join(process.env.KIT_BROWSER_TEST_ROOT||os.tmpdir(),"video-review-"));
const python=process.env.KIT_PYTHON||"python";
const tool=path.join(repo,"skills/minwoo-video-review/scripts/serve_review.py");
(async()=>{
  let browser,server;
  try {
    browser=await chromium.launch({headless:true,...(process.env.KIT_BROWSER_CHANNEL?{channel:process.env.KIT_BROWSER_CHANNEL}:{})});
    const page=await browser.newPage({viewport:{width:1280,height:1000},acceptDownloads:true});
    const errors=[];page.on("pageerror",e=>errors.push(e.message));
    const clips=await page.evaluate(async()=>{
      async function record(label,color) {
        const canvas=document.createElement("canvas");canvas.width=640;canvas.height=360;
        const ctx=canvas.getContext("2d"),stream=canvas.captureStream(20),chunks=[];
        const recorder=new MediaRecorder(stream,{mimeType:"video/webm;codecs=vp8"});
        recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
        const finished=new Promise(resolve=>recorder.onstop=resolve);
        recorder.start();
        const start=performance.now();
        await new Promise(resolve=>{
          const timer=setInterval(()=>{
            const elapsed=(performance.now()-start)/1000;
            ctx.fillStyle=color;ctx.fillRect(0,0,640,360);
            ctx.fillStyle="white";ctx.font="36px sans-serif";ctx.fillText(label,40,80);
            ctx.font="24px sans-serif";ctx.fillText(elapsed.toFixed(2)+"s",40,125);
            ctx.fillRect(40+elapsed*100,220,40,40);
            if(elapsed>=3.2){clearInterval(timer);resolve();}
          },50);
        });
        recorder.stop();await finished;stream.getTracks().forEach(t=>t.stop());
        return Array.from(new Uint8Array(await new Blob(chunks,{type:"video/webm"}).arrayBuffer()));
      }
      return Promise.all([record("Before","#284967"),record("After","#476b56")]);
    });
    fs.writeFileSync(path.join(root,"before.webm"),Buffer.from(clips[0]));
    fs.writeFileSync(path.join(root,"after.webm"),Buffer.from(clips[1]));
    const config={schema:1,title:"샘플 영상 · 컷 비교",
      versions:[{id:"before",label:"수정 전",file:"before.webm"},{id:"after",label:"수정 후",file:"after.webm"}],
      cuts:[{id:"opening",label:"오프닝",ranges:{before:[0.2,1.2],after:[0.5,1.7]}},
            {id:"ending",label:"마무리",ranges:{before:[1.2,1.9],after:[1.7,2.4]}},
            {id:"invalid",label:"길이 초과 검사",ranges:{before:[0,99],after:[0,99]}}]};
    const configPath=path.join(root,"review.json");fs.writeFileSync(configPath,JSON.stringify(config));
    server=spawn(python,["-B",tool,"--config",configPath],{stdio:["ignore","pipe","pipe"]});
    const url=await new Promise((resolve,reject)=>{
      let data=""; const timer=setTimeout(()=>reject(new Error("server startup timeout")),15000);
      server.stdout.on("data",chunk=>{data+=chunk;const m=data.match(/http:\/\/127\.0\.0\.1:\d+\/[^\s]+/);if(m){clearTimeout(timer);resolve(m[0]);}});
      server.once("error",reject);server.once("exit",code=>{clearTimeout(timer);reject(new Error("server exited "+code));});
    });
    await page.goto(url);
    await page.waitForFunction(()=>!document.getElementById("play").disabled);
    await page.getByRole("button",{name:"비교 재생",exact:true}).click();
    await page.waitForFunction(()=>document.getElementById("video-0").currentTime>0.35 && document.getElementById("video-1").currentTime>0.65);
    await page.waitForTimeout(2300);
    const looping=await page.locator("video").evaluateAll(v=>v.map(x=>({time:x.currentTime,paused:x.paused})));
    assert(looping.every(x=>!x.paused));assert(looping[0].time>=0.15&&looping[0].time<=1.3);
    assert(looping[1].time>=0.45&&looping[1].time<=1.8);
    await page.getByRole("button",{name:"일시 정지",exact:true}).click();
    await page.locator("#note").fill("샘플 자막 위치 확인");
    await page.getByRole("button",{name:"현재 시점에 메모 추가"}).click();
    assert.equal(await page.locator("#note-list li").count(),1);
    const downloadEvent=page.waitForEvent("download");
    await page.getByRole("button",{name:"메모 JSON 내보내기"}).click();
    const download=await downloadEvent,notesPath=path.join(root,"notes.json");await download.saveAs(notesPath);
    const result=spawnSync(python,["-B",tool,"--config",configPath,"--check-notes",notesPath],{encoding:"utf8"});
    assert.equal(result.status,0,result.stderr);
    const exported=JSON.parse(fs.readFileSync(notesPath));
    assert.equal(exported.notes[0].cut_id,"opening");assert.equal(exported.notes[0].text,"샘플 자막 위치 확인");
    await page.locator("#import").setInputFiles(notesPath);
    await page.waitForFunction(()=>document.getElementById("notice").textContent.startsWith("0개"));
    assert.equal(await page.locator("#note-list li").count(),1);
    const wrong=structuredClone(exported);wrong.review.config_sha256="0".repeat(64);
    const wrongPath=path.join(root,"wrong.json");fs.writeFileSync(wrongPath,JSON.stringify(wrong));
    await page.locator("#import").setInputFiles(wrongPath);
    await page.waitForFunction(()=>document.getElementById("notice").textContent.includes("다른 메모"));
    assert.equal(await page.locator("#note-list li").count(),1);
    await page.locator("#cut").selectOption("1");
    await page.locator("#sound").selectOption("after");
    assert.deepEqual(await page.locator("video").evaluateAll(v=>v.map(x=>x.muted)),[true,false]);
    await page.locator("#loop").uncheck();
    await page.getByRole("button",{name:"비교 재생",exact:true}).click();
    await page.waitForFunction(()=>[...document.querySelectorAll("video")].every(v=>v.paused));
    const endTimes=await page.locator("video").evaluateAll(v=>v.map(x=>x.currentTime));
    assert(Math.abs(endTimes[0]-1.9)<0.1&&Math.abs(endTimes[1]-2.4)<0.1);
    await page.screenshot({path:path.join(root,"desktop.png"),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(root,"mobile.png"),fullPage:true});
    await page.locator("#cut").selectOption("2");
    assert(await page.locator("#play").isDisabled());
    assert((await page.locator("#error").textContent()).includes("영상 길이를 넘습니다"));
    fs.appendFileSync(path.join(root,"after.webm"),"changed");
    assert.equal((await page.request.get(url+"review.json")).status(),409);
    assert.equal(spawnSync(python,["-B",tool,"--config",configPath,"--check-notes",notesPath]).status,1);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({result:"PASS",checks:["synthetic video decode","version-specific loop","cut switch","pause at cut end","audio selection","notes export and hash validation","duplicate import","wrong target rejection","mobile overflow","invalid cut blocked","changed media rejected","no page errors"],artifacts:root}));
  } finally {if(server)server.kill();if(browser)await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
