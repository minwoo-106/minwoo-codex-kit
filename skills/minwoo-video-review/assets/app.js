"use strict";
const $ = id => document.getElementById(id);
const videos = [$("video-0"), $("video-1")];
const notes = [];
const kinds = {technical:"기술 확인", visual:"화면 관찰", judgment:"사용자 판단"};
let manifest, dirty = false, currentCut = 0, fatal = false;
const cut = () => manifest.cuts[currentCut];
const times = i => cut().ranges[manifest.versions[i].id];
const say = message => { $("notice").textContent = message; };
function fail(message) {
  $("error").textContent = message;
  $("error").hidden = false;
}
function pause() { videos.forEach(v => v.pause()); }
function ready() {
  return manifest && !fatal && videos.every((v,i) => Number.isFinite(v.duration) &&
    times(i)[1] <= v.duration + 0.05);
}
function updateReady() {
  const ok = ready();
  $("play").disabled = !ok;
  $("pause").disabled = !ok;
  $("add-note").disabled = !ok;
  if (manifest && !fatal && videos.every(v => Number.isFinite(v.duration))) {
    if (!ok) fail("설정한 컷 구간이 영상 길이를 넘습니다. 설정 파일을 수정하고 서버를 다시 시작하세요.");
  }
}
function displayRanges() {
  if (!manifest) return;
  videos.forEach((v,i) => {
    const [a,b] = times(i);
    $("range-"+i).textContent = a.toFixed(2)+"–"+b.toFixed(2)+"초 · 현재 "+v.currentTime.toFixed(2)+"초";
  });
}
function setCut(index) {
  pause(); currentCut = index;
  $("error").hidden = fatal ? false : true;
  videos.forEach((v,i) => { if (v.readyState >= 1) v.currentTime = times(i)[0]; });
  updateReady(); displayRanges();
}
function monitor() {
  if (manifest && ready()) {
    videos.forEach((v,i) => {
      const [a,b] = times(i);
      if (!v.paused && (v.currentTime >= b || v.currentTime < a - 0.05)) {
        if ($("loop").checked) { v.currentTime = a; if (v.ended) v.play().catch(() => {}); }
        else { v.pause(); v.currentTime = b; }
      }
    });
  }
  displayRanges();
}
function renderNotes() {
  $("count").textContent = notes.length;
  $("export").disabled = !manifest;
  $("save-state").textContent = dirty ? "아직 파일로 저장하지 않은 변경 있음" : (notes.length ? "내보내기 요청됨 · 다운로드 파일 확인" : "저장할 메모 없음");
  $("note-list").replaceChildren();
  notes.forEach(n => {
    const li = document.createElement("li"), meta = document.createElement("p"), body = document.createElement("p");
    const c = manifest.cuts.find(c => c.id === n.cut_id);
    const v = manifest.versions.find(v => v.id === n.version_id);
    meta.className = "note-meta"; body.className = "note-text";
    meta.textContent = c.label+" / "+v.label+" / "+n.at_seconds.toFixed(2)+"초 / "+kinds[n.kind];
    body.textContent = n.text;
    li.append(meta,body); $("note-list").append(li);
  });
}
function validateNotes(data) {
  const identity=data?.review;
  if (!data || data.schema !== 1 || identity?.config_sha256 !== manifest.review.config_sha256 ||
      !Array.isArray(identity?.videos) || identity.videos.length !== manifest.review.videos.length ||
      !manifest.review.videos.every((v,i) => identity.videos[i]?.id===v.id && identity.videos[i]?.sha256===v.sha256))
    throw new Error("설정 또는 영상이 다른 메모입니다.");
  if (!Array.isArray(data.notes) || data.notes.length > 500) throw new Error("메모는 최대 500개입니다.");
  return data.notes.map(n => {
    if (!n || typeof n !== "object") throw new Error("메모 형식이 올바르지 않습니다.");
    const c = manifest.cuts.find(c => c.id === n.cut_id);
    const range = c && Object.hasOwn(c.ranges,n.version_id) ? c.ranges[n.version_id] : null;
    if (!range || typeof n.at_seconds !== "number" || !Number.isFinite(n.at_seconds) ||
        n.at_seconds < range[0] || n.at_seconds > range[1] || !Object.hasOwn(kinds,n.kind) ||
        typeof n.text !== "string" || !n.text.trim() || n.text.length > 2000)
      throw new Error("메모의 컷·시간·종류·내용을 확인하세요.");
    return {cut_id:n.cut_id,version_id:n.version_id,at_seconds:n.at_seconds,kind:n.kind,text:n.text};
  });
}
$("play").addEventListener("click",async () => {
  if (!ready()) return;
  videos.forEach((v,i) => { v.currentTime = times(i)[0]; });
  const results = await Promise.allSettled(videos.map(v => v.play()));
  if (results.some(r => r.status === "rejected")) { pause(); fail("재생하지 못했습니다. 브라우저의 코덱 지원과 영상 파일을 확인하세요."); }
});
$("pause").addEventListener("click",pause);
$("cut").addEventListener("change", () => setCut(Number($("cut").value)));
$("sound").addEventListener("change", () => videos.forEach((v,i) => {
  v.muted = manifest.versions[i].id !== $("sound").value;
}));
videos.forEach((v,i) => {
  v.addEventListener("loadedmetadata", () => {
    if (!Number.isFinite(v.duration)) { fatal=true; updateReady(); fail("영상 길이를 읽지 못했습니다. 길이 정보가 있는 다른 영상 파일을 사용하세요."); return; }
    v.currentTime = times(i)[0]; updateReady(); displayRanges();
  });
  v.addEventListener("error", () => { fatal=true; pause(); updateReady(); fail("영상을 불러오지 못했습니다. 코덱 지원 또는 실행 중 파일 변경 여부를 확인하세요."); });
  v.addEventListener("timeupdate",monitor);
  v.addEventListener("ended", () => {
    if (ready() && $("loop").checked) { v.currentTime=times(i)[0]; v.play().catch(() => {}); }
  });
  v.addEventListener("play", () => { if (!ready()) { v.pause(); return; } const [a,b]=times(i); if(v.currentTime<a || v.currentTime>=b) v.currentTime=a; });
  v.addEventListener("volumechange", () => {
    if (!manifest) return;
    if (!v.muted) {
      videos.forEach((other,j) => {if(i!==j) other.muted=true;});
      $("sound").value=manifest.versions[i].id;
    } else if (videos.every(other=>other.muted)) $("sound").value="";
  });
});
$("note-form").addEventListener("submit",event => {
  event.preventDefault();
  if (!ready()) return;
  if (notes.length >= 500) return say("메모는 최대 500개입니다.");
  const i = Number($("version").value), [a,b] = times(i), value=$("note").value.trim();
  if (!value) return;
  notes.push({cut_id:cut().id,version_id:manifest.versions[i].id,
    at_seconds:Math.max(a,Math.min(b,videos[i].currentTime)),kind:$("kind").value,text:value});
  $("note").value=""; dirty=true; renderNotes(); say("메모를 추가했습니다. JSON으로 내보내면 파일로 저장됩니다.");
});
$("export").addEventListener("click", () => {
  if (!manifest) return;
  const data={schema:1,review:manifest.review,notes};
  const blob = new Blob([JSON.stringify(data,null,2)+"\n"], {type:"application/json"});
  const url=URL.createObjectURL(blob), link=document.createElement("a");
  link.href=url; link.download="review-notes-"+Date.now()+".json"; document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url),1000);
  dirty=false; renderNotes(); say("내보내기를 요청했습니다. 브라우저 다운로드에서 파일을 확인하세요.");
});
$("import").addEventListener("change",async event => {
  const file=event.target.files[0]; if(!file || !manifest) return;
  try {
    if(file.size>2000000) throw new Error("메모 파일이 너무 큽니다.");
    const imported=validateNotes(JSON.parse(await file.text()));
    const existing=new Set(notes.map(n => JSON.stringify(n)));
    const additions=imported.filter(n => {const key=JSON.stringify(n);if(existing.has(key))return false;existing.add(key);return true;});
    if(notes.length+additions.length>500) throw new Error("합친 메모가 500개를 넘습니다.");
    notes.push(...additions); dirty=dirty || additions.length>0; renderNotes();
    say(additions.length+"개를 가져왔습니다. 기존 메모는 유지했습니다.");
  } catch(error) { say(error.message || "메모 파일을 읽지 못했습니다."); }
  event.target.value="";
});
window.addEventListener("beforeunload",event => { if(dirty){event.preventDefault();event.returnValue="";} });
async function init() {
  const response=await fetch("review.json");
  if(!response.ok) throw new Error("설정을 읽지 못했습니다. 서버와 파일 상태를 확인하세요.");
  manifest=await response.json();
  $("title").textContent=manifest.title; document.title=manifest.title+" · 컷 비교";
  manifest.cuts.forEach((c,i) => $("cut").add(new Option(c.label,String(i))));
  $("cut").disabled=false;
  manifest.versions.forEach((v,i) => {
    $("label-"+i).textContent=v.label;
    $("sound").add(new Option(v.label,v.id)); $("version").add(new Option(v.label,String(i)));
    videos[i].src=v.url; videos[i].muted=true;
  });
  renderNotes(); displayRanges();
}
init().catch(error => {fatal=true;fail(error.message);});
setInterval(monitor,50);
