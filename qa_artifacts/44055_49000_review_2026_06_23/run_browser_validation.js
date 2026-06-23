const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');

const ROOT = process.cwd();
const OUT = path.join(ROOT, 'qa_artifacts/44055_49000_review_2026_06_23');
const db = JSON.parse(fs.readFileSync(path.join(ROOT, 'cpt_database.json'), 'utf8'));
const cases = [
  {name:'after-44055-49000', codes:['44055','49000'], expected:{selectedWrvu:37.22, payableWrvu:24.99, bundled:'49000', state:'BLOCKED'}},
  {name:'regression-44005-49000', codes:['44005','49000'], expected:{selectedWrvu:30.23, payableWrvu:18.00, bundled:'49000'}},
  {name:'regression-44207-44180', codes:['44207','44180'], expected:{selectedWrvu:46.01, payableWrvu:31.12, bundled:'44180'}},
  {name:'mppr-44120-44140', codes:['44120','44140'], expected:{selectedWrvu:42.33, payableWrvu:42.33}}
];

const chrome = spawn('/usr/bin/google-chrome', [
  '--headless=new','--no-sandbox','--disable-gpu','--remote-debugging-port=9224',
  '--window-size=1440,1300','--user-data-dir=/tmp/chrome-freecpt-review-' + Date.now(),'about:blank'
], {stdio:['ignore','pipe','pipe']});

function getJson(url){return new Promise((resolve,reject)=>http.get(url,res=>{let d='';res.on('data',c=>d+=c);res.on('end',()=>{try{resolve(JSON.parse(d))}catch(e){reject(e)}})}).on('error',reject));}
async function waitVersion(){for(let i=0;i<80;i++){try{return await getJson('http://127.0.0.1:9224/json/version')}catch(e){await new Promise(r=>setTimeout(r,250))}}throw new Error('CDP not ready')}
function connect(wsUrl){const ws=new WebSocket(wsUrl);let id=0;const pending=new Map();ws.onmessage=ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result)}};return new Promise((resolve,reject)=>{ws.onopen=()=>resolve({send(method,params={}){const mid=++id;ws.send(JSON.stringify({id:mid,method,params}));return new Promise((resolve,reject)=>pending.set(mid,{resolve,reject}))},close(){ws.close()}});ws.onerror=reject})}

(async()=>{
  await waitVersion();
  const pages=await getJson('http://127.0.0.1:9224/json/list');
  const cdp=await connect((pages.find(p=>p.type==='page')||pages[0]).webSocketDebuggerUrl);
  await cdp.send('Page.enable'); await cdp.send('Runtime.enable');
  const results=[];
  for(const test of cases){
    await cdp.send('Page.navigate',{url:'http://127.0.0.1:8765/'});
    await new Promise(r=>setTimeout(r,2500));
    await cdp.send('Runtime.evaluate',{expression:'(async()=>{ if(window.NCCI_LOAD_PROMISE) await window.NCCI_LOAD_PROMISE; return true; })()', awaitPromise:true, returnByValue:true});
    const rows={}; for(const code of test.codes){ const d=db[code]; rows[code]={description:d.description,work_rvu:Number(d.work_rvu||0),total_rvu:Number(d.total_rvu||0),estimated_medicare_payment:Number(d.estimated_medicare_payment||0),addon_code:!!d.addon_code,bilateral_indicator:Number(d.bilateral_indicator||0)}; }
    const expression = "(() => { clearCase(); const rows = " + JSON.stringify(rows) + "; const add = c => { const d = rows[c]; addProc(c, d.description, Number(d.work_rvu || 0), '', d.bilateral_indicator, '', [], { totalRvu: d.total_rvu, basePayment: d.estimated_medicare_payment, addonCode: d.addon_code, clinicalContext: {} }); }; " + JSON.stringify(test.codes) + ".forEach(add); recalc('validation " + test.name + "'); return {ncciLoadStatus:window.NCCI_LOAD_STATUS,ncciChecks:" + JSON.stringify(test.codes) + ".flatMap((a,i,arr)=>arr.slice(i+1).map(b=>({pair:a+'|'+b, edit:ncciCheck(a,b)}))), totalsDom:{tn:document.getElementById('tn')?.textContent,ts:document.getElementById('ts')?.textContent,rm:document.getElementById('rm')?.textContent},caseLines,audit}; })()";
    const evalResult=await cdp.send('Runtime.evaluate',{expression,returnByValue:true});
    if(evalResult.exceptionDetails) throw new Error(JSON.stringify(evalResult.exceptionDetails));
    const value=evalResult.result.value;
    const selected=+(value.caseLines.reduce((s,l)=>s+Number(l.effWrvu||0),0).toFixed(2));
    const payable=+(value.caseLines.reduce((s,l)=>s+Number(l.payableWrvu||0),0).toFixed(2));
    const bundledLine=test.expected.bundled ? value.caseLines.find(l=>String(l.cpt)===String(test.expected.bundled)) : null;
    const pass = Math.abs(selected-test.expected.selectedWrvu)<0.02 && Math.abs(payable-test.expected.payableWrvu)<0.02 && (!test.expected.bundled || (bundledLine && bundledLine.payableExcluded && Number(bundledLine.payableWrvu||0)===0));
    value.validation={expected:test.expected, actual:{selectedWrvu:selected,payableWrvu:payable,bundledPayableExcluded: bundledLine ? bundledLine.payableExcluded : null, bundledPayableWrvu: bundledLine ? bundledLine.payableWrvu : null}, pass};
    results.push({name:test.name, ...value});
    await cdp.send('Runtime.evaluate',{expression:"document.querySelector('.casebar')?.scrollIntoView({block:'center'});", returnByValue:true});
    await new Promise(r=>setTimeout(r,400));
    const shot=await cdp.send('Page.captureScreenshot',{format:'png'});
    fs.writeFileSync(path.join(OUT, test.name + '.png'), Buffer.from(shot.data,'base64'));
  }
  fs.writeFileSync(path.join(OUT,'browser-validation.json'), JSON.stringify({generatedAt:new Date().toISOString(), results}, null, 2));
  console.log(JSON.stringify(results.map(r=>({name:r.name, pass:r.validation.pass, actual:r.validation.actual, totalsDom:r.totalsDom, ncciChecks:r.ncciChecks})), null, 2));
  cdp.close(); chrome.kill('SIGTERM');
})().catch(err=>{console.error(err); chrome.kill('SIGTERM'); process.exit(1)});
