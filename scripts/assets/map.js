'use strict';
(() => {
  const data = JSON.parse(document.getElementById('plan-data').textContent);
  const plan = data.plan, byId = new Map(), children = new Map(), parents = new Map();
  const $ = id => document.getElementById(id);
  const kinds = {deck:'整套 PPT',section:'大块',block:'小块',page:'页面'};
  const formLabels = {statement:'单一主张',sequence:'流程 / 时序',comparison:'对比',hierarchy:'层级 / 组成',causal:'因果',data:'数据论证',story:'故事 / 案例',list:'并列要点'};
  let selected = plan.deck.id, query = '', depth = 2;
  function add(node, kind, parent) {
    byId.set(node.id, {...node, kind}); children.set(node.id, []);
    if (parent) {parents.set(node.id, parent); children.get(parent).push(node.id);}
  }
  add(plan.deck,'deck');
  plan.sections.forEach(s => {add(s,'section',plan.deck.id);s.blocks.forEach(b => add(b,'block',s.id));});
  plan.pages.forEach(p => add(p,'page',p.block_id));
  const text = (tag, value, cls) => {const e=document.createElement(tag);e.textContent=value ?? '';if(cls)e.className=cls;return e;};
  function button(label, action, cls) {const b=text('button',label,cls);b.type='button';b.addEventListener('click',action);return b;}
  function match(node) {return JSON.stringify(node).toLocaleLowerCase().includes(query);}
  function subtreeMatch(id) {return match(byId.get(id)) || children.get(id).some(subtreeMatch);}
  function path(id) {const out=[];while(id){out.unshift(id);id=parents.get(id);}return out;}
  function select(id, scroll=false) {
    if(!byId.has(id))return;
    selected=id;
    const level=path(id).length-1;
    if(level>depth){depth=level;$('depth').value=String(depth);}
    try {history.replaceState(null,'','#'+encodeURIComponent(id));} catch (_) { /* file viewers may restrict history */ }
    renderTree();renderGraph();renderNarrative();renderDetail();
    if(scroll)$('detail').scrollIntoView({behavior:'smooth',block:'start'});
  }
  function renderTree() {
    const open = new Set([...$('tree').querySelectorAll('details[open]')].map(d=>d.dataset.id));
    $('tree').replaceChildren();
    function branch(id, host) {
      if(query && !subtreeMatch(id))return;
      const node=byId.get(id), kids=children.get(id);
      const b=button(`${node.id} · ${node.title || '待定'}`,()=>select(id),`tree-node ${node.kind}${id===selected?' active':''}`);
      b.setAttribute('aria-current',id===selected?'true':'false');
      if(kids.length){
        const d=document.createElement('details');d.dataset.id=id;
        d.open=Boolean(query)||open.has(id)||path(selected).includes(id)||node.kind==='deck';
        const s=text('summary',`${kinds[node.kind]} · ${node.title || '待定'} (${kids.length})`);
        d.append(s,b);kids.forEach(child=>branch(child,d));host.append(d);
      }else host.append(b);
    }
    branch(plan.deck.id,$('tree'));
    const count=[...byId.values()].filter(match).length;
    $('search-status').textContent=query ? `${count} 个节点匹配；目录保留其上级路径。` : '点击内容名称查看详情，三角按钮展开下级。';
  }
  const NS='http://www.w3.org/2000/svg';
  function svg(tag,attrs={}) {const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,String(v));return e;}
  function wrapped(value,limit=17,rows=2) {
    const chars=Array.from(value||'待定'), out=[];
    for(let i=0;i<Math.min(chars.length,limit*rows);i+=limit)out.push(chars.slice(i,i+limit).join(''));
    if(chars.length>limit*rows)out[out.length-1]+='…';return out;
  }
  function renderGraph() {
    const graph=$('graph');graph.replaceChildren();
    const defs=svg('defs'), marker=svg('marker',{id:'arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});
    marker.append(svg('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#bd7924'}));defs.append(marker);graph.append(defs);
    const positions=new Map();let leaf=0;
    function layout(id,level) {
      const kids=level<depth?children.get(id):[];
      let y;
      if(kids.length){const ys=kids.map(child=>layout(child,level+1));y=(ys[0]+ys[ys.length-1])/2;}
      else {y=50+leaf*125;leaf++;}
      positions.set(id,{x:24+level*300,y,level});return y;
    }
    layout(plan.deck.id,0);
    const width=300*(depth+1),height=Math.max(210,leaf*125+70),zoom=Number($('zoom').value)/100;
    graph.setAttribute('viewBox',`0 0 ${width} ${height}`);graph.style.width=width*zoom+'px';graph.style.height=height*zoom+'px';
    ['整套主张','大块主体','小块内容','逐页主旨'].slice(0,depth+1).forEach((label,i)=>{const t=svg('text',{x:24+i*300,y:25,class:'graph-label'});t.textContent=label;graph.append(t);});
    for(const[id,p]of positions){
      const parent=positions.get(parents.get(id));if(!parent)continue;
      const x=parent.x+250,y=parent.y+42;
      graph.append(svg('path',{class:'hierarchy',d:`M${x},${y} C${x+24},${y} ${p.x-24},${p.y+42} ${p.x},${p.y+42}`}));
    }
    if($('relations').checked){
      plan.relations.filter(r=>r.from===selected||r.to===selected).forEach(r=>{
        const a=positions.get(r.from),b=positions.get(r.to);if(!a||!b)return;
        const x1=a.x+125,y1=a.y+86,x2=b.x+125,y2=b.y+86;
        const curve=svg('path',{class:'logic','marker-end':'url(#arrow)',d:`M${x1},${y1} C${x1+135},${y1+42} ${x2+135},${y2+42} ${x2},${y2}`});
        const title=svg('title');title.textContent=`${data.relations[r.type]}：${r.reason}`;curve.append(title);graph.append(curve);
      });
    }
    for(const[id,p]of positions){
      const node=byId.get(id),group=svg('g',{class:`node ${node.priority==='core'?'core ':''}${id===selected?'selected ':''}${query&&!subtreeMatch(id)?'dim':''}`,transform:`translate(${p.x},${p.y})`,tabindex:0,role:'button','aria-label':`${kinds[node.kind]} ${id} ${node.title || ''}`,'data-kind':node.kind,'data-id':id});
      group.append(svg('rect',{width:250,height:86,rx:8}));
      const tag=svg('text',{x:12,y:18,class:'tag'});tag.textContent=`${id} · ${kinds[node.kind]}${node.priority==='core'?' · 核心':''}`;group.append(tag);
      wrapped(node.title).forEach((line,i)=>{const t=svg('text',{x:12,y:39+i*17});t.textContent=line;group.append(t);});
      const focus=svg('text',{x:12,y:75,class:'node-focus'});focus.textContent=wrapped(node.thesis,20,1)[0];group.append(focus);
      const title=svg('title');title.textContent=node.thesis||node.title||'';group.append(title);
      group.addEventListener('click',()=>select(id));group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(id);}});graph.append(group);
    }
  }
  function field(host,label,value){if(value===undefined||value==='')return;const d=document.createElement('div');d.append(text('dt',label),text('dd',value));host.append(d);}
  function list(host,title,items){if(!items?.length)return;host.append(text('h3',title));const ul=document.createElement('ul');items.forEach(item=>ul.append(text('li',item)));host.append(ul);}
  function renderNarrative(){
    const host=$('story-map');host.replaceChildren();
    plan.sections.forEach((section,i)=>{
      if(i>0){
        const previous=plan.sections[i-1], r=plan.relations.find(r=>(r.from===previous.id&&r.to===section.id)||(r.to===previous.id&&r.from===section.id));
        const link=text('div','','story-link');
        link.append(text('strong',r?`${r.from===previous.id?'→':'←'} ${data.relations[r.type]}`:'→ 讲述顺序'));
        link.append(text('p',r?r.reason:'具体逻辑关系参见节点详情'));host.append(link);
      }
      const card=text('article','',`story-section${selected===section.id?' active':''}`);
      card.append(text('div',`大块 ${String(i+1).padStart(2,'0')} · ${data.priorities[section.priority]||'待定'}`,'story-index'));
      card.append(button(section.title||'待定',()=>select(section.id,true),'section-title'),text('p',section.thesis||'主旨待补充','story-thesis'));
      card.append(text('p','全篇作用：'+(section.role_in_deck||'待补充'),'story-role'),text('p','本块重点：'+(section.focus||'待补充'),'story-focus'));
      section.blocks.forEach((block,blockIndex)=>{
        if(blockIndex>0){const prev=section.blocks[blockIndex-1],r=plan.relations.find(r=>r.from===prev.id&&r.to===block.id);if(r)card.append(text('p',`↓ ${data.relations[r.type]}：${r.reason}`,'block-link'));}
        const b=text('div','',`story-block${selected===block.id?' active':''}`);
        b.append(button(`${block.id} · ${block.title||'待定'}`,()=>select(block.id,true)),text('p',block.thesis||'主旨待补充'));
        b.append(text('p',`重点：${block.focus||'待补充'}`,'story-role'));
        plan.pages.filter(p=>p.block_id===block.id).forEach(p=>{
          const n=plan.pages.findIndex(x=>x.id===p.id)+1;
          b.append(button(`${String(n).padStart(2,'0')} / ${p.id} · ${p.title||'待定'}`,()=>select(p.id,true),`page-chip${selected===p.id?' active':''}`));
        });card.append(b);
      });host.append(card);
    });
    if(!plan.sections.length)host.append(text('p','先讨论整套主张与大块划分，叙事地图会随计划逐步展开。'));
    const pages=$('page-story');pages.replaceChildren();
    plan.pages.forEach((p,i)=>{
      const card=text('article','',`page-story-card${selected===p.id?' active':''}`);
      const b=byId.get(p.block_id),s=byId.get(parents.get(p.block_id));
      card.append(text('div',`${String(i+1).padStart(2,'0')} / ${plan.pages.length} · ${p.id} · ${data.priorities[p.priority]||'待定'}`,'story-index'));
      card.append(text('div',`${s.title||s.id} › ${b.title||b.id}`,'story-tag'));
      card.append(button(p.title||'待定',()=>select(p.id,true)),text('p',p.thesis||'主旨待补充','story-thesis'));
      card.append(text('p','本页任务：'+(p.role_in_deck||'待补充'),'story-role'),text('p','核心重点：'+(p.focus||'待补充'),'story-role'));
      card.append(text('p',`→ ${p.transition||(i===plan.pages.length-1?'结束':'衔接待补充')}`,'transition'));pages.append(card);
    });
  }
  function showView(view){
    for(const name of ['story','hierarchy','pages']){
      $(name==='story'?'story-panel':name==='hierarchy'?'hierarchy-panel':'pages-panel').hidden=name!==view;
      $('view-'+name).setAttribute('aria-pressed',String(name===view));
    }
  }
  function renderDetail(){
    const node=byId.get(selected),host=$('detail');host.replaceChildren();
    host.append(text('div',path(selected).map(id=>byId.get(id).title||id).join(' › '),'breadcrumb'));
    const head=text('div','','detail-head');head.append(text('h2',`${node.id} · ${node.title||'待定'}`),text('span',data.priorities[node.priority]||kinds[node.kind],'tag-badge'));host.append(head);
    host.append(text('p',node.thesis||'主旨待补充','thesis'));
    const dl=document.createElement('dl');
    field(dl,'内容重点',node.focus);field(dl,'在整套 PPT 中的作用',node.role_in_deck);
    field(dl,'在所属内容块中的作用',node.role_in_parent);field(dl,'回答听众什么问题',node.audience_question);
    field(dl,'沟通目标',node.objective);field(dl,'受众',node.audience);field(dl,'场景',node.scenario);
    field(dl,'内容范围',node.scope);field(dl,'叙事主线',node.narrative);
    field(dl,'时长',node.minutes?`${node.minutes} 分钟`:node.duration_minutes?`${node.duration_minutes} 分钟`:undefined);host.append(dl);
    list(host,'听众应记住',node.takeaways);list(host,'需要表达的内容',node.key_points);list(host,'不展开的内容',node.out_of_scope);
    if(children.get(selected).length){host.append(text('h3','下级内容'));const childList=text('div','','relations-list');children.get(selected).forEach(id=>{const n=byId.get(id);const item=text('div','','relation-item');item.append(button(`${id} · ${n.title||'待定'}`,()=>select(id)),text('p',n.thesis||'主旨待补充'));childList.append(item);});host.append(childList);}
    const relations=plan.relations.filter(r=>r.from===selected||r.to===selected);
    host.append(text('h3','与其他内容的逻辑关系'));
    const relationList=text('div','','relations-list');
    for(const r of relations){const item=text('div','','relation-item');item.append(button(`${r.from} ${byId.get(r.from).title||''}`,()=>select(r.from)),text('span',` → ${data.relations[r.type]} → `),button(`${r.to} ${byId.get(r.to).title||''}`,()=>select(r.to)),text('p',r.reason));relationList.append(item);}
    if(!relations.length)relationList.append(text('p','没有单独登记跨节点关系；内容归属见上级路径，逐页衔接见下方。','hint'));host.append(relationList);
    const info=node.information_structure;
    if(info){host.append(text('h3','页内信息结构 · 后续信息图的内容依据'),text('p',`关系类型：${formLabels[info.kind]||info.kind}。此处描述语义关系，不指定版式。`));
      const entities=text('div','','entities');info.entities.forEach(e=>{const item=text('div','','entity');item.append(text('strong',`${e.id} · ${e.label}`),text('p',e.detail));entities.append(item);});host.append(entities);
      list(host,'页内逻辑',info.relations.map(r=>`${r.from} → ${r.to} · ${data.relations[r.type]}：${r.reason}`));
      list(host,'比较维度',info.dimensions);host.append(text('p','阅读顺序：'+info.reading_order.join(' → ')));
    }
    if(node.evidence?.length){host.append(text('h3','事实与依据'));node.evidence.forEach(e=>{const box=text('div','','evidence');box.append(text('strong',e.claim),text('p',`状态：${{verified:'有来源的事实',hypothesis:'假设 / 示意',needs_source:'待补充来源'}[e.status]}`));if(e.note)box.append(text('p','边界：'+e.note));(e.source_refs||[]).forEach(id=>{const s=plan.sources.find(s=>s.id===id);box.append(text('p',`${id} · ${s.title} · ${s.locator}`));});host.append(box);});}
    if(node.notes){host.append(text('h3','讲述提示'),text('p',node.notes));}
    if(node.transition){host.append(text('h3','承接下一页'),text('p',node.transition));}
    if(node.kind==='deck'){
      list(host,'需求与声明边界',[...plan.requirements,...plan.claim_constraints].map(r=>`${r.id}：${r.text}；适用：${(r.applies_to||[]).join('、')||'全篇'}`));
      list(host,'来源登记',plan.sources.map(s=>`${s.id} · ${s.title} · ${s.locator}`));
      list(host,'待解决问题',plan.open_questions.map(q=>`${q.blocking?'[阻塞] ':''}${q.question}`));
    }
    if(node.kind==='page'){const i=plan.pages.findIndex(p=>p.id===selected),bar=text('div','','page-nav');
      if(i>0)bar.append(button('← 上一页',()=>select(plan.pages[i-1].id)));
      bar.append(text('span',`${i+1} / ${plan.pages.length}`));
      if(i<plan.pages.length-1)bar.append(button('下一页 →',()=>select(plan.pages[i+1].id)));host.append(bar);}
  }
  $('title').textContent=plan.deck.title||'内容规划';$('thesis').textContent=plan.deck.thesis||'整套主旨待补充';
  $('objective').textContent=plan.deck.objective||'待补充';$('focus').textContent=plan.deck.focus||'待补充';$('narrative').textContent=plan.deck.narrative||'待补充';
  $('state').textContent=data.draft?'内容草稿 · 等待确认':'内容已确认 · 可交接设计';$('state').classList.toggle('draft',data.draft);
  $('counts').textContent=`${plan.sections.length} 大块 · ${plan.sections.reduce((n,s)=>n+s.blocks.length,0)} 小块 · ${plan.pages.length} 页 · ${plan.deck.duration_minutes||'?'} 分钟`;
  const stageNames={outline:'大纲分块',content:'小块与关系',pages:'逐页内容'},statusNames={confirmed:'已确认',pending:'待确认',stale:'修改后待重新确认'};
  Object.entries(data.status).forEach(([stage,state])=>$('reviews').append(text('span',`${stageNames[stage]}：${statusNames[state]}`)));
  data.findings.forEach(f=>$('findings').append(text('li',`${f.node}：${f.message}`,f.severity)));
  if(!data.findings.length)$('findings').append(text('li','机器检查通过；论证质量和来源真实性仍须人工核对。'));
  for(const view of ['story','hierarchy','pages'])$('view-'+view).addEventListener('click',()=>showView(view));
  $('search').addEventListener('input',e=>{query=e.target.value.trim().toLocaleLowerCase();renderTree();renderGraph();});
  $('depth').addEventListener('change',e=>{depth=Number(e.target.value);showView('hierarchy');renderGraph();});
  $('zoom').addEventListener('input',e=>{$('zoom-label').textContent=e.target.value+'%';showView('hierarchy');renderGraph();});
  $('relations').addEventListener('change',renderGraph);
  $('expand').addEventListener('click',()=>{$('tree').querySelectorAll('details').forEach(d=>d.open=true);});
  $('collapse').addEventListener('click',()=>{$('tree').querySelectorAll('details').forEach(d=>d.open=d.dataset.id===plan.deck.id);});
  $('reset').addEventListener('click',()=>{query='';$('search').value='';depth=2;$('depth').value='2';$('zoom').value='80';$('zoom-label').textContent='80%';showView('story');select(plan.deck.id);$('graph-scroll').scrollTo(0,0);});
  $('print').addEventListener('click',()=>window.print());
  window.addEventListener('hashchange',()=>{try{select(decodeURIComponent(location.hash.slice(1)));}catch(_){/* ignore malformed links */}});
  let initial=plan.deck.id;try{const id=decodeURIComponent(location.hash.slice(1));if(byId.has(id))initial=id;}catch(_){}
  select(initial, initial!==plan.deck.id);
})();
