#!/usr/bin/env python3
"""Patch banking-screen.html with verify-by-exception matching UX."""
from pathlib import Path

path = Path(__file__).parent / "banking-screen.html"
html = path.read_text()

# ── 1. CSS ──────────────────────────────────────────────────────────────────
CSS_ANCHOR = ".rev-mod-ai-col.has-ai-sug .rev-mod-conf{color:var(--ai-text);}"
CSS = """
/* verify-by-exception — guardrails, signals, dismissal */
.rev-guardrail-banner{background:var(--info-bg);border:1px solid #B8DFEF;border-radius:var(--r8);padding:12px 16px;margin-bottom:12px;font-size:14px;line-height:1.45;display:flex;align-items:flex-start;gap:10px;}
.rev-guardrail-banner strong{color:var(--text);}
.rev-ready-banner{background:linear-gradient(90deg,var(--brand-subtle),#fff);border:1px solid var(--lavender);border-radius:var(--r8);padding:14px 18px;margin-bottom:14px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
.rev-ready-banner-main{flex:1;min-width:200px;}
.rev-ready-banner-title{font-size:16px;font-weight:600;color:var(--text);margin:0 0 4px;}
.rev-ready-banner-sub{font-size:14px;color:var(--muted);margin:0;}
.match-signals{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 4px;}
.match-signal-chip{font-size:12px;font-weight:500;padding:2px 8px;border-radius:9999px;background:var(--stone20);color:var(--text);line-height:1.35;}
.match-signal-chip.sig-strong{background:var(--success-bg);color:var(--success);}
.match-signal-chip.sig-rule{background:var(--ai-bg);color:var(--ai-text);}
.field-act-row{display:flex;align-items:center;gap:4px;margin-top:6px;flex-wrap:wrap;}
.field-act-btn{font-size:12px;font-weight:600;padding:4px 8px;border-radius:var(--r4);cursor:pointer;font-family:var(--font);border:1px solid var(--border);background:#fff;color:var(--text);line-height:1.2;}
.field-act-btn:hover{border-color:var(--lavender);background:var(--brand-subtle);}
.field-act-btn.field-act-ok{border-color:var(--success-border);color:var(--success);}
.field-act-btn.field-act-ok:hover{background:var(--success-bg);}
.dismiss-menu-wrap{position:relative;display:inline-flex;}
.dismiss-menu{position:absolute;bottom:calc(100% + 6px);right:0;min-width:240px;background:#fff;border:1px solid var(--border);border-radius:var(--r8);box-shadow:0 8px 24px rgba(0,0,0,.14);padding:6px;z-index:1200;display:none;}
.dismiss-menu.open{display:block;}
.dismiss-menu-opt{display:block;width:100%;text-align:left;padding:8px 10px;border:none;background:none;border-radius:var(--r4);font-size:13px;font-weight:500;color:var(--text);cursor:pointer;font-family:var(--font);line-height:1.35;}
.dismiss-menu-opt:hover{background:var(--stone20);}
.dismiss-menu-opt small{display:block;font-size:12px;font-weight:400;color:var(--muted);margin-top:2px;}
.dismiss-menu-sep{height:1px;background:var(--border);margin:4px 6px;}
.rev-mod-act-verify{background:#fff;border:1px solid var(--success-border);color:#008536;}
.rev-mod-act-verify:hover{background:var(--success-bg);}
.rev-row-actions .rev-mod-act-verify{min-width:56px;}
.hidden-tx-pill{font-size:12px;font-weight:600;color:var(--muted);background:var(--stone20);padding:2px 8px;border-radius:var(--r4);}
.dismissed-log-row{display:flex;align-items:flex-start;gap:12px;padding:14px 16px;border-bottom:1px solid var(--border);}
.dismissed-log-row:last-child{border-bottom:none;}
.dismissed-log-meta{flex:1;min-width:0;}
.dismissed-log-title{font-size:14px;font-weight:600;color:var(--text);margin:0 0 2px;}
.dismissed-log-sub{font-size:13px;color:var(--muted);margin:0;line-height:1.4;}
.dismiss-type-badge{font-size:11px;font-weight:600;padding:2px 7px;border-radius:var(--r4);background:var(--stone20);color:var(--muted);white-space:nowrap;}
"""

if CSS_ANCHOR not in html:
    raise SystemExit("CSS anchor not found")
html = html.replace(CSS_ANCHOR, CSS_ANCHOR + CSS)

# ── 2. State ────────────────────────────────────────────────────────────────
STATE_ANCHOR = "  dismissedCtx: new Set(),"
STATE_ADD = """
  hiddenTx: new Set(),           // tx ids hidden from matching (Type 5)
  sessionDismissed: new Set(),   // `${txId}:${field}` — Type 1 session dismiss
  declineCounts: {},             // pattern key → count for 3-strike elevation
  dismissMenuOpen: null,         // txId when row dismiss menu open
  showHiddenReview: false,"""

html = html.replace(STATE_ANCHOR, STATE_ANCHOR + STATE_ADD)

# Extend clear list init
CLEAR_ANCHOR = "   note:'Transaction was an internal transfer, not a bill payment.'},\n];"
CLEAR_ADD = """   note:'Transaction was an internal transfer, not a bill payment.'},
  {id:103, type:'match', entity:'supplier', txRef:'TXN-00234', txDesc:'Voltex Electrical', rejectedVal:'#1302 · Voltex Electrical',
   rejectedField:'match', date:'09/10/2025', scope:'object', dismissType:'object',
   note:'Dismissed match to this bill only.', restored:false},
  {id:104, type:'category', entity:'supplier', txRef:'CBA-00133', txDesc:'Uber Eats', rejectedVal:'Staff meals',
   rejectedField:'cat', date:'08/10/2025', scope:'semantic', dismissType:'semantic',
   note:'Never suggest staff meals for Uber Eats.', restored:false},
];"""
html = html.replace(CLEAR_ANCHOR, CLEAR_ADD)

# ── 3. Helper functions (after getWhyFile) ──────────────────────────────────
HELPER_ANCHOR = "function whyTipHtml(why,{field,head='Why this suggestion?'}={}){"
HELPER_BLOCK = r'''function suggestOnlyMode(){return !S.automatch;}
function matchPolicyLabel(){
  if(!S.automatch) return 'Suggest only — matches need your approval before committing.';
  if(!S.amToggles.invoicesBills) return 'Invoice and bill matches are held for manual verify.';
  return '';
}
function txIsHidden(tx){return S.hiddenTx.has(tx.id);}
function sessionDismissKey(txId,field){return `${txId}:${field}`;}
function isSessionDismissed(txId,field){return S.sessionDismissed.has(sessionDismissKey(txId,field));}
function txTopMatchConf(tx){
  const m=tx.ai.match, c=tx.ai.cat;
  return Math.max(m?.conf||0, c?.conf||0, ...(MATCHES[tx.id]||[]).map(x=>x.conf||0));
}
function txVerifyRank(tx){
  if(txReviewDone(tx)) return -100;
  if(txIsHidden(tx)) return -200;
  let r=0;
  if(txIsReadyForBulk(tx)) r+=1000;
  r+=txTopMatchConf(tx);
  if(revModMatchSuggest(tx)) r+=80;
  if(revModTaxSuggest(tx)) r+=40;
  if(txHasChanged(tx)) r+=30;
  return r;
}
function getMatchSignals(tx,field){
  const vend=tx.desc.split(/\s[–\-]/)[0].trim();
  const f=tx.ai[field];
  const signals=[];
  if(field==='match'){
    if(Math.abs(tx.amount)>0) signals.push({label:'Amount match',tone:'strong'});
    signals.push({label:'Date within window',tone:''});
    if(vend.length>2) signals.push({label:`Supplier: ${vend.split(' ')[0]}`,tone:''});
    if(S.memory.some(m=>m.active&&m.memType==='match'&&vend.includes(m.entity.split(' ')[0]))) signals.push({label:'Bank rule',tone:'rule'});
    if(MATCHES[tx.id]?.length) signals.push({label:'Open record found',tone:'strong'});
  }else if(field==='cat'){
    if(S.memory.some(m=>m.active&&m.source==='rule'&&vend.includes(m.entity.split(' ')[0]))) signals.push({label:'Saved rule',tone:'rule'});
    else signals.push({label:'Keyword match',tone:''});
    if((f?.conf||0)>=90) signals.push({label:'Prior coding pattern',tone:'strong'});
  }else if(field==='tax'){
    if((f?.conf||0)>=90) signals.push({label:'Vendor tax history',tone:'strong'});
    else signals.push({label:'Category default',tone:''});
    if(tx.ai.cat?.val) signals.push({label:'Linked to category',tone:''});
  }
  return signals;
}
function matchSignalsHtml(signals){
  if(!signals?.length) return '';
  return `<div class="match-signals" aria-label="Match signals">${signals.map(s=>`<span class="match-signal-chip${s.tone==='strong'?' sig-strong':s.tone==='rule'?' sig-rule':''}">${s.label}</span>`).join('')}</div>`;
}
function declinePatternKey(tx,field){
  const f=tx.ai[field];
  const vend=tx.desc.split(/\s[–\-]/)[0].trim();
  return `${vend}|${field}|${f?.rejectedVal||f?.val||''}`;
}
function bumpDeclineCount(tx,field){
  const key=declinePatternKey(tx,field);
  S.declineCounts[key]=(S.declineCounts[key]||0)+1;
  return S.declineCounts[key];
}
function maybeElevationPrompt(tx,field){
  const n=bumpDeclineCount(tx,field);
  if(n!==3) return;
  const f=tx.ai[field];
  const val=f?.rejectedVal||f?.val||'this suggestion';
  const vend=tx.desc.split(/\s[–\-]/)[0].trim();
  showToast(`You've declined "${val}" 3 times. <button type="button" class="fx-textlink" style="font-size:13px" onclick="dismissSuggestion(${tx.id},'overall','${field}');dismissToast(this.closest('.fx-toast').id)">Create permanent exclusion</button>`,8000);
}
function clearFieldSuggestion(tx,field){
  const f=tx.ai[field]; if(!f||f.st==='accepted') return;
  if(f.val){f.rejectedVal=f.val;f.val=null;f.conf=0;}
  f.st='idle';
}
function addDismissLogEntry(tx,field,type,note){
  const f=tx.ai[field]||{};
  S.clearList.push({
    id:Date.now()+Math.floor(Math.random()*1000),
    type:field==='match'?'match':'category',
    txRef:tx.ref,
    txDesc:tx.desc,
    txId:tx.id,
    rejectedField:field,
    rejectedVal:f.rejectedVal||f.val||'—',
    date:new Date().toLocaleDateString('en-AU',{day:'2-digit',month:'2-digit',year:'numeric'}),
    scope:type,
    dismissType:type,
    note:note||'',
    restored:false,
  });
}
function dismissSuggestion(txId,type,field){
  const tx=ftx(txId); if(!tx) return;
  closeDismissMenu();
  if(type==='hide'){
    S.hiddenTx.add(txId);
    S.reviewSel.delete(txId);
    showSuccessToast({title:'Transaction hidden',message:`${tx.ref||'Line'} removed from matching — restore from Hidden list.`});
    render(); return;
  }
  if(field){
    clearFieldSuggestion(tx,field);
    if(type==='once'){
      S.sessionDismissed.add(sessionDismissKey(txId,field));
      maybeElevationPrompt(tx,field);
      showToast('Suggestion dismissed for this transaction.',2500);
    }else if(type==='overall'){
      const vend=tx.desc.split(/\s[–\-]/)[0].trim();
      const val=tx.ai[field]?.rejectedVal||'';
      S.memory.push({id:Date.now(),source:'rejected',memType:field==='match'?'match':'category',active:true,
        entity:vend,
        conditions:[{field:'payee',op:'contains',val:vend}],
        action:field==='match'?{entity:val}:{cat:val,tax:''},
        count:1,last:new Date().toLocaleDateString('en-AU',{day:'2-digit',month:'2-digit',year:'numeric'}),
        note:`Never suggest "${val}" for ${vend}.`,
        summary:`Never suggest ${field==='match'?'match':'category'} "${val}" for ${vend}.`});
      addDismissLogEntry(tx,field,'overall','Permanent exclusion rule created.');
      showToast('Permanent exclusion saved to Memory.',3000);
    }else if(type==='object'){
      addDismissLogEntry(tx,field,'object',`Won't match to ${tx.ai[field]?.rejectedVal||'this record'}.`);
      showToast('Object-level dismissal saved.',2500);
    }else if(type==='semantic'){
      addDismissLogEntry(tx,field,'semantic','Semantic pattern excluded.');
      showToast('Semantic exclusion saved.',2500);
    }
  }else{
    ['cat','match','tax'].forEach(f=>clearFieldSuggestion(tx,f));
    showToast('All suggestions dismissed for this transaction.',2500);
  }
  if(S.matchSel[txId]) delete S.matchSel[txId];
  render();
}
function restoreDismissed(id){
  const e=S.clearList.find(x=>x.id===id); if(!e||e.restored) return;
  e.restored=true;
  if(e.txId&&S.hiddenTx.has(e.txId)) S.hiddenTx.delete(e.txId);
  if(e.txId&&e.rejectedField){
    S.sessionDismissed.delete(sessionDismissKey(e.txId,e.rejectedField));
    const tx=ftx(e.txId);
    if(tx&&e.rejectedVal&&e.rejectedVal!=='—'){
      const f=tx.ai[e.rejectedField];
      if(f&&f.st!=='accepted'){f.val=e.rejectedVal;f.st='idle';f.conf=75;}
    }
  }
  showToast('Suggestion restored — review again when ready.',2500);
  render();
}
function unhideTransaction(txId){
  S.hiddenTx.delete(txId);
  showToast('Transaction restored to matching queue.',2000);
  render();
}
function toggleDismissMenu(txId,ev){
  if(ev) ev.stopPropagation();
  S.dismissMenuOpen=S.dismissMenuOpen===txId?null:txId;
  render();
}
function closeDismissMenu(){
  if(S.dismissMenuOpen){S.dismissMenuOpen=null;render();}
}
function buildDismissMenu(txId){
  const open=S.dismissMenuOpen===txId;
  return `
  <div class="dismiss-menu-wrap" onclick="event.stopPropagation()">
    <button type="button" class="rev-mod-act-reject${open?' act':''}" onclick="toggleDismissMenu(${txId},event)" title="Dismiss options"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><line x1="2" y1="2" x2="10" y2="10"/><line x1="10" y1="2" x2="2" y2="10"/></svg><span>Decline</span></button>
    <div class="dismiss-menu${open?' open':''}" role="menu">
      <button type="button" class="dismiss-menu-opt" onclick="dismissSuggestion(${txId},'once','match')">Dismiss for this one<small>This transaction only</small></button>
      <button type="button" class="dismiss-menu-opt" onclick="dismissSuggestion(${txId},'overall','match')">Never match like this<small>Creates a permanent exclusion rule</small></button>
      <button type="button" class="dismiss-menu-opt" onclick="dismissSuggestion(${txId},'object','match')">Don't match to this record<small>Object-level exclusion</small></button>
      <button type="button" class="dismiss-menu-opt" onclick="dismissSuggestion(${txId},'semantic','match')">Exclude by pattern<small>Vendor + amount pattern</small></button>
      <div class="dismiss-menu-sep"></div>
      <button type="button" class="dismiss-menu-opt" onclick="dismissSuggestion(${txId},'hide')">Hide transaction<small>Remove from matching pool</small></button>
    </div>
  </div>`;
}
function buildFieldActions(tx,field){
  const f=tx.ai[field];
  if(!f||!f.val||f.st!=='idle'||txReviewDone(tx)) return '';
  if(isSessionDismissed(tx.id,field)) return '';
  return `<div class="field-act-row">
    <button type="button" class="field-act-btn field-act-ok" onclick="event.stopPropagation();acceptFieldTx(${tx.id},'${field}')">Verify</button>
    <button type="button" class="field-act-btn" onclick="event.stopPropagation();dismissSuggestion(${tx.id},'once','${field}')">Decline</button>
  </div>`;
}
function acceptFieldTx(txId,field){
  const tx=ftx(txId); if(!tx) return;
  const f=tx.ai[field]; if(!f||!f.val||f.st==='accepted') return;
  f.st='accepted';
  addToContext(txId,field);
  if(field==='match') tx.status='coded';
  const allDone=['cat','match','tax'].every(x=>{const a=tx.ai[x];return !a?.val||a.st==='accepted';});
  if(allDone) markTxReviewDone(txId);
  showSuccessToast({title:'Verified',message:`${field==='match'?'Match':field==='tax'?'Tax code':'Category'} accepted for ${tx.ref||'transaction'}.`});
  render();
}
function buildReviewGuardrailBanner(){
  const parts=[];
  if(suggestOnlyMode()) parts.push('<strong>Suggest only</strong> — automatch is off. Nothing commits until you verify.');
  if(S.automatch&&!S.amToggles.invoicesBills) parts.push('<strong>Invoices & bills</strong> — held for manual verify (auto-allocate off).');
  if(!S.amToggles.suggestRecord&&!S.amToggles.suggestCat) parts.push('Record and category suggestions are limited in settings.');
  if(!parts.length) return '';
  return `<div class="rev-guardrail-banner" role="status"><span aria-hidden="true">⚙</span><div>${parts.join(' · ')}</div></div>`;
}
function buildReadyVerifyBanner(filtered){
  const ready=filtered.filter(t=>!txReviewDone(t)&&txIsReadyForBulk(t));
  const high=filtered.filter(t=>!txReviewDone(t)&&txTopMatchConf(t)>=85);
  if(!ready.length&&!high.length) return '';
  const n=ready.length||high.length;
  return `<div class="rev-ready-banner" role="status">
    <div class="rev-ready-banner-main">
      <p class="rev-ready-banner-title">${ready.length?ready.length:high.length} ready to verify</p>
      <p class="rev-ready-banner-sub">Pre-scored matches ranked by confidence — verify exceptions first, then work through the rest.</p>
    </div>
    ${ready.length?`<button type="button" class="fx-btn fx-btn-success" onclick="setRevFilter('ready')">Show ready (${ready.length})</button>`:''}
    ${S.hiddenTx.size?`<button type="button" class="fx-btn fx-btn-neutral-ghost" onclick="S.showHiddenReview=!S.showHiddenReview;render()">${S.showHiddenReview?'Hide':'Show'} hidden (${S.hiddenTx.size})</button>`:''}
  </div>`;
}
function buildDismissedLogSection(){
  const items=S.clearList.filter(e=>!e.restored);
  if(!items.length) return '';
  return `
  <div style="margin-top:28px" data-recon-target="dismissed-log">
    <h2 class="stg-ai-page-title" style="margin-bottom:8px">Dismissed suggestions</h2>
    <p style="font-size:14px;color:var(--muted);margin:0 0 12px">Restore declined matches or review permanent exclusions.</p>
    <div class="card" style="padding:0;overflow:hidden">
      ${items.map(e=>`
      <div class="dismissed-log-row">
        <div class="dismissed-log-meta">
          <p class="dismissed-log-title">${e.txRef} · ${e.rejectedVal}</p>
          <p class="dismissed-log-sub">${e.txDesc}${e.note?` — ${e.note}`:''}</p>
        </div>
        <span class="dismiss-type-badge">${(e.dismissType||e.scope||'once').replace(/^./,c=>c.toUpperCase())}</span>
        <button type="button" class="fx-btn fx-btn-neutral-ghost fx-btn-sm" onclick="restoreDismissed(${e.id})">Restore</button>
      </div>`).join('')}
    </div>
  </div>`;
}
function whyTipHtml(why,{field,head='Why this suggestion?',signals=null,tx=null}={}){'''

if HELPER_ANCHOR not in html:
    raise SystemExit("Helper anchor not found")

# Update whyTipHtml signature body
OLD_WHY = """function whyTipHtml(why,{field,head='Why this suggestion?'}={}){
  if(!why) return '';
  const agent=field?revAgentTipHead(field):'';
  const meta=agent&&agent!==head?`<div class="why-tip-meta">${agent}</div>`:'';
  return `<div class="why-tip"><div class="why-tip-head">${head}</div>${meta}<p class="why-tip-body">${why}</p></div>`;
}"""

NEW_WHY = """function whyTipHtml(why,{field,head='Why this suggestion?',signals=null,tx=null}={}){
  if(!why&&!signals?.length) return '';
  const sig=signals||(tx&&field?getMatchSignals(tx,field):[]);
  const agent=field?revAgentTipHead(field):'';
  const meta=agent&&agent!==head?`<div class="why-tip-meta">${agent}</div>`:'';
  return `<div class="why-tip"><div class="why-tip-head">${head}</div>${meta}${matchSignalsHtml(sig)}${why?`<p class="why-tip-body">${why}</p>`:''}</div>`;
}"""

html = html.replace(OLD_WHY, HELPER_BLOCK + NEW_WHY)

# ── 4. sortReviewList ───────────────────────────────────────────────────────
OLD_SORT = """function sortReviewList(list){
  return [...list].sort((a,b)=>{
    const da=txReviewDone(a)?1:0, db=txReviewDone(b)?1:0;
    if(da!==db) return da-db;
    const ca=txHasChanged(a)?0:1, cb=txHasChanged(b)?0:1;
    if(ca!==cb) return ca-cb;
    const ra=txIsReadyForBulk(a)?0:1, rb=txIsReadyForBulk(b)?0:1;
    if(ra!==rb) return ra-rb;
    return b.date.localeCompare(a.date);
  });
}"""

NEW_SORT = """function sortReviewList(list){
  return [...list].sort((a,b)=>{
    const da=txReviewDone(a)?1:0, db=txReviewDone(b)?1:0;
    if(da!==db) return da-db;
    const va=txVerifyRank(a), vb=txVerifyRank(b);
    if(va!==vb) return vb-va;
    const ca=txHasChanged(a)?0:1, cb=txHasChanged(b)?0:1;
    if(ca!==cb) return ca-cb;
    return b.date.localeCompare(a.date);
  });
}"""

html = html.replace(OLD_SORT, NEW_SORT)

# ── 5. reviewInboxList filter hidden ──────────────────────────────────────
OLD_INBOX = """function reviewInboxList(){
  const ctx=ctxList();
  const pending=pendingList();
  const done=TX.filter(t=>S.reviewDone.has(t.id)&&(S.bankFilter==='all'||t.bank===S.bankFilter));
  const seen=new Set();
  const list=[...ctx,...pending.filter(t=>!seen.has(t.id)&&seen.add(t.id)),...done.filter(t=>!seen.has(t.id)&&seen.add(t.id))];
  return list;
}"""

NEW_INBOX = """function reviewInboxList(){
  const ctx=ctxList();
  const pending=pendingList();
  const done=TX.filter(t=>S.reviewDone.has(t.id)&&(S.bankFilter==='all'||t.bank===S.bankFilter));
  const hidden=TX.filter(t=>S.hiddenTx.has(t.id)&&(S.bankFilter==='all'||t.bank===S.bankFilter));
  const seen=new Set();
  let list=[...ctx,...pending.filter(t=>!seen.has(t.id)&&seen.add(t.id)),...done.filter(t=>!seen.has(t.id)&&seen.add(t.id))];
  if(S.showHiddenReview) list=[...hidden.filter(t=>!seen.has(t.id)&&seen.add(t.id)),...list];
  else list=list.filter(t=>!txIsHidden(t));
  return list;
}"""

html = html.replace(OLD_INBOX, NEW_INBOX)

# ── 6. revConfBadge — pass tx for signals ───────────────────────────────────
html = html.replace(
    "${whyTipHtml(why,{field})}",
    "${whyTipHtml(why,{field,tx})}",
)

# ── 7. revTaxInner / revCodingInner — signals + field actions ───────────────
OLD_TAX_INNER = """  const rev=txRevisionValues(tx,'tax');
  const valHtml=`<div class="rev-agent-val">${rev?rev.newVal:f.val}</div>`;
  return {html:`${valHtml}${revConfBadge(f.conf,getWhy(tx,'tax'),{field:'tax'})}`,cls:''};
}"""

NEW_TAX_INNER = """  const rev=txRevisionValues(tx,'tax');
  const valHtml=`<div class="rev-agent-val">${rev?rev.newVal:f.val}</div>`;
  const sigs=matchSignalsHtml(getMatchSignals(tx,'tax'));
  return {html:`${valHtml}${sigs}${revConfBadge(f.conf,getWhy(tx,'tax'),{field:'tax'})}${buildFieldActions(tx,'tax')}`,cls:''};
}"""

html = html.replace(OLD_TAX_INNER, NEW_TAX_INNER)

OLD_CODE_INNER = """  const whyField=matchRev?'match':(catRev?'cat':(matchOk?'match':'cat'));
  return {html:`${catHtml}${matchHtml}${revConfBadge(conf,whyField==='match'?(matchOk?getWhy(tx,'match'):''):(catOk?getWhy(tx,'cat'):''),{field:whyField==='match'?'match':'cat'})}`,cls:''};
}"""

NEW_CODE_INNER = """  const whyField=matchRev?'match':(catRev?'cat':(matchOk?'match':'cat'));
  const sigField=matchOk||matchRev?'match':'cat';
  const sigs=matchSignalsHtml(getMatchSignals(tx,sigField));
  const fa=buildFieldActions(tx,'match')+buildFieldActions(tx,'cat');
  return {html:`${catHtml}${matchHtml}${sigs}${revConfBadge(conf,whyField==='match'?(matchOk?getWhy(tx,'match'):''):(catOk?getWhy(tx,'cat'):''),{field:whyField==='match'?'match':'cat'})}${fa}`,cls:''};
}"""

html = html.replace(OLD_CODE_INNER, NEW_CODE_INNER)

# ── 8. revModTaxCell / revModMatchCell ──────────────────────────────────────
OLD_MOD_TAX = """    return `<div class="rev-mod-tax-sug">
      ${revModTaxCodeHtml(tx,f)}
      ${gst?`<div class="rev-mod-tax-amt">${gst}</div>`:''}
      ${revModConfHtml(f.conf,getWhy(tx,'tax'),{field:'tax'})}
    </div>`;"""

NEW_MOD_TAX = """    return `<div class="rev-mod-tax-sug">
      ${revModTaxCodeHtml(tx,f)}
      ${gst?`<div class="rev-mod-tax-amt">${gst}</div>`:''}
      ${matchSignalsHtml(getMatchSignals(tx,'tax'))}
      ${revModConfHtml(f.conf,getWhy(tx,'tax'),{field:'tax'})}
      ${buildFieldActions(tx,'tax')}
    </div>`;"""

html = html.replace(OLD_MOD_TAX, NEW_MOD_TAX)

OLD_MOD_MATCH = """    return `<div class="rev-mod-match-sug">
      ${catLine}
      ${matchLine}
      ${revModConfHtml(conf,why,{field:whyField==='match'?'match':'cat'})}
    </div>`;"""

NEW_MOD_MATCH = """    return `<div class="rev-mod-match-sug">
      ${catLine}
      ${matchLine}
      ${matchSignalsHtml(getMatchSignals(tx,whyField==='match'?'match':'cat'))}
      ${revModConfHtml(conf,why,{field:whyField==='match'?'match':'cat'})}
      ${buildFieldActions(tx,'match')}
    </div>`;"""

html = html.replace(OLD_MOD_MATCH, NEW_MOD_MATCH)

# ── 9. buildRevModAiBand actions ────────────────────────────────────────────
OLD_BAND = """      <button type="button" class="rev-mod-act-accept" ${canAccept?'':'disabled'} onclick="event.stopPropagation();acceptAllTx(${tx.id},event)"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="2,6 5,9 10,3"/></svg><span>Accept</span></button>
      <button type="button" class="rev-mod-act-reject" onclick="event.stopPropagation();rejectAllSuggestions(${tx.id})"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><line x1="2" y1="2" x2="10" y2="10"/><line x1="10" y1="2" x2="2" y2="10"/></svg><span>Reject</span></button>"""

NEW_BAND = """      <button type="button" class="rev-mod-act-accept rev-mod-act-verify" ${canAccept?'':'disabled'} onclick="event.stopPropagation();acceptAllTx(${tx.id},event)"><svg width="14" height="14" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="2,6 5,9 10,3"/></svg><span>Verify</span></button>
      ${buildDismissMenu(tx.id)}"""

html = html.replace(OLD_BAND, NEW_BAND)

# ── 10. buildReviewRowActions ───────────────────────────────────────────────
OLD_ACTIONS = """    <button type="button" class="fx-btn fx-btn-success fx-btn-sm" ${hasSuggestions&&!exitActive?'':'disabled'} onclick="event.stopPropagation();acceptAllTx(${tx.id},event)" title="Accept all AI suggestions">Accept</button>
    <button type="button" class="fx-btn fx-btn-neutral-ghost fx-btn-sm" ${exitActive?'disabled':''} onclick="event.stopPropagation();openAside(${tx.id},'review','matches')">Review</button>
    <button type="button" class="btn-rev-reject" ${exitActive?'disabled':''} onclick="event.stopPropagation();rejectAllSuggestions(${tx.id})" title="Clear AI suggestions">Reject</button>"""

NEW_ACTIONS = """    <button type="button" class="fx-btn fx-btn-success fx-btn-sm rev-mod-act-verify" ${hasSuggestions&&!exitActive?'':'disabled'} onclick="event.stopPropagation();acceptAllTx(${tx.id},event)" title="Verify all suggestions">Verify</button>
    <button type="button" class="fx-btn fx-btn-neutral-ghost fx-btn-sm" ${exitActive?'disabled':''} onclick="event.stopPropagation();openAside(${tx.id},'review','matches')">Review</button>
    ${buildDismissMenu(tx.id)}"""

html = html.replace(OLD_ACTIONS, NEW_ACTIONS)

# ── 11. buildReviewTab banners ──────────────────────────────────────────────
OLD_REVIEW = """    ${buildReconTodo()}
    ${bulkBar}"""

NEW_REVIEW = """    ${buildReconTodo()}
    ${buildReviewGuardrailBanner()}
    ${buildReadyVerifyBanner(filtered)}
    ${bulkBar}"""

html = html.replace(OLD_REVIEW, NEW_REVIEW, 1)

# ── 12. Aside match signals ─────────────────────────────────────────────────
html = html.replace(
    """        <div class="mi-sub">${m.type} · ${m.date} · ${fmtAbs(m.amount)}</div>
      </div>
    </div>`;}).join('')}""",
    """        <div class="mi-sub">${m.type} · ${m.date} · ${fmtAbs(m.amount)}</div>
        ${matchSignalsHtml(getMatchSignals(tx,'match'))}
      </div>
    </div>`;}).join('')}""",
)

# ── 13. Settings dismissed log ──────────────────────────────────────────────
html = html.replace(
    """    ${memSection}`;""",
    """    ${memSection}
    ${buildDismissedLogSection()}`;""",
)

# ── 14. Global dismiss menu close ───────────────────────────────────────────
if "!window._dismissMenuBound" not in html:
    html = html.replace(
        "if(!window._revFilterMenuBound){",
        """if(!window._dismissMenuBound){
  window._dismissMenuBound=true;
  document.addEventListener('click',()=>{if(S.dismissMenuOpen){S.dismissMenuOpen=null;render();}});
}
if(!window._revFilterMenuBound){""",
    )

# ── 15. acceptAllTx toast message ───────────────────────────────────────────
html = html.replace(
    "message:`${tx.ref||'Transaction'} matched — row stays in your list below`,",
    "message:`${tx.ref||'Transaction'} verified — row stays in your list below`,",
)

path.write_text(html)
print("Patched", path)
