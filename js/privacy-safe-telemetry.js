(function(){
  const DEFAULT_CONFIG={
    enabled:false,
    endpoint:'',
    sampleRate:1,
    maxBatchSize:20,
    flushIntervalMs:15000
  };
  const CPT_RE=/^\d{5}[A-Z]?$/;
  const MODIFIER_RE=/^(22|24|25|50|51|57|58|59|76|77|78|79|80|81|82|AS|RT|LT|XE|XP|XS|XU)$/;
  const EVENT_TYPES=new Set(['case_snapshot','ncci_event','search_event']);
  const queue=[];
  let flushTimer=null;

  function config(){
    return Object.assign({},DEFAULT_CONFIG,window.FCCF_TELEMETRY_CONFIG||{});
  }
  function today(value){
    const d=value?new Date(value):new Date();
    if(Number.isNaN(d.getTime()))return new Date().toISOString().slice(0,10);
    return d.toISOString().slice(0,10);
  }
  function cleanCpt(value){
    const v=String(value||'').trim().toUpperCase();
    return CPT_RE.test(v)?v:'';
  }
  function cleanModifier(value){
    const v=String(value||'').trim().toUpperCase().replace(/^-+/,'');
    return MODIFIER_RE.test(v)?v:'';
  }
  function cleanCategory(value){
    const v=String(value||'').trim();
    return /^[A-Za-z0-9 /&()+.-]{1,80}$/.test(v)?v:'';
  }
  function roundedNumber(value){
    const n=Number(value||0);
    return Number.isFinite(n)?Number(n.toFixed(2)):0;
  }
  function pairKey(a,b){
    const c1=cleanCpt(a),c2=cleanCpt(b);
    return c1&&c2?c1+'+'+c2:'';
  }
  function searchClass(query,selectedCode,results){
    const raw=String(query||'').trim();
    const cpt=cleanCpt(raw);
    if(cpt)return {searchKind:'cpt_exact',searchCode:cpt};
    const firstSelected=cleanCpt(selectedCode);
    const firstResult=cleanCpt((results||[])[0]?.code);
    if(firstSelected)return {searchKind:'controlled_cpt_selection',searchCode:firstSelected};
    if(firstResult)return {searchKind:'controlled_result_match',searchCode:firstResult};
    return {searchKind:raw.length?'unmatched_private_query':'empty',searchCode:''};
  }
  function commonEnvelope(type,payload){
    if(!EVENT_TYPES.has(type))return null;
    return {
      schemaVersion:'case_builder_telemetry.v1',
      eventType:type,
      eventDate:today(payload&&payload.timestamp),
      source:'freecpt_case_builder',
      payload
    };
  }
  function enabled(){
    const cfg=config();
    return !!(cfg.enabled&&cfg.endpoint&&Math.random()<=Number(cfg.sampleRate||1));
  }
  function enqueue(event){
    if(!enabled()||!event)return false;
    queue.push(event);
    if(queue.length>=config().maxBatchSize)flush();
    else scheduleFlush();
    return true;
  }
  function scheduleFlush(){
    if(flushTimer)return;
    flushTimer=setTimeout(flush,config().flushIntervalMs);
  }
  function flush(){
    const cfg=config();
    if(flushTimer){clearTimeout(flushTimer);flushTimer=null}
    if(!cfg.enabled||!cfg.endpoint||!queue.length)return Promise.resolve(false);
    const batch=queue.splice(0,Math.min(queue.length,cfg.maxBatchSize));
    return fetch(cfg.endpoint,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({events:batch})
    }).then(()=>true).catch(()=>{
      batch.slice(0,cfg.maxBatchSize).forEach(item=>queue.unshift(item));
      return false;
    });
  }
  function emitCaseSnapshot(lines,context){
    const procLines=(lines||[]).filter(l=>l&&l.kind==='proc');
    const cpts=procLines.map(l=>cleanCpt(l.cpt)).filter(Boolean).slice(0,12);
    const modifiers=procLines.flatMap(l=>[l.userMod].concat(l.mods||[])).map(cleanModifier).filter(Boolean);
    return enqueue(commonEnvelope('case_snapshot',{
      primaryCpt:cpts[0]||'',
      secondaryCpt:cpts[1]||'',
      tertiaryCpt:cpts[2]||'',
      cptCombination:cpts.join('+'),
      cptCount:cpts.length,
      modifierSelections:[...new Set(modifiers)].sort(),
      modifierCount:modifiers.length,
      specialtyCategory:cleanCategory(context&&context.specialtyCategory),
      ncciWarningCount:procLines.filter(l=>l.engineState==='WARNING').length,
      payableExclusionCount:procLines.filter(l=>l.payableExcluded).length,
      selectedWrvu:roundedNumber(procLines.reduce((s,l)=>s+Number(l.effWrvu||0),0)),
      payableWrvu:roundedNumber(procLines.reduce((s,l)=>s+Number(l.payableWrvu||0),0))
    }));
  }
  function emitNcciEvents(lines){
    const procLines=(lines||[]).filter(l=>l&&l.kind==='proc'&&l.payableExcluded);
    procLines.forEach(line=>{
      const edit=line.payableExclusionEdit||{};
      const p=edit.column1||line.payableExcludedBy||'';
      const pair=pairKey(p,line.cpt);
      if(!pair)return;
      enqueue(commonEnvelope('ncci_event',{
        cptPair:pair,
        column1:cleanCpt(p),
        column2:cleanCpt(line.cpt),
        modifierIndicator:String(edit.modifierIndicator||edit.modifier_indicator||'0'),
        editSeverity:line.engineState==='BLOCKED'?'hard_stop':'warning',
        selectedWrvu:roundedNumber(line.effWrvu),
        payableWrvu:roundedNumber(line.payableWrvu),
        suppressedWrvu:roundedNumber(Number(line.effWrvu||0)-Number(line.payableWrvu||0))
      }));
    });
  }
  function emitSearchEvent(query,options){
    const opts=options||{};
    const classified=searchClass(query,opts.selectedCode,opts.results);
    return enqueue(commonEnvelope('search_event',{
      searchKind:classified.searchKind,
      searchCode:classified.searchCode,
      resultSelected:cleanCpt(opts.selectedCode),
      resultCount:Number.isFinite(Number(opts.resultCount))?Number(opts.resultCount):0,
      success:!!opts.success,
      didYouMeanUsed:!!opts.didYouMeanUsed
    }));
  }
  window.FCCFTelemetry={
    emitCaseSnapshot,
    emitNcciEvents,
    emitSearchEvent,
    flush,
    _sanitize:{cleanCpt,cleanModifier,cleanCategory,searchClass}
  };
})();
