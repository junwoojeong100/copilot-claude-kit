# Golden Runtime Internals · Router · Realtime

단일 HTML의 구조와 핵심 JS를 설명하는 내부 참고 자료다. 실제 생성은 이 코드를 복사해 다시 작성하지
않고 `runtime/`과 `scripts/render_demo.py`를 사용한다. 고객별 변경은 `demo-spec.json`에서 수행하며,
이 문서는 bespoke extension이나 Runtime 유지보수 시에만 참고한다.

## 1. HTML 골격 (`<body>`)
```html
<div id="app">
  <aside id="sidebar">
    <div class="brand"><div class="brand-mark" id="brandMark"></div>
      <div><div class="brand-name" id="brandName"></div><div class="brand-sub" id="brandSub"></div></div></div>
    <div class="nav-section">통합 운영 현황</div>
    <nav class="nav" id="nav"></nav>
    <!-- 선택: 'Learning Loop' 위젯(쓸수록 커지는 고객 소유 AI 자산 카운터) -->
    <div class="side-user"><div class="side-avatar" id="sideAvatar"></div>
      <div><div class="side-user-name" id="sideUserName"></div><div class="side-user-role">임원용 · 시연 환경</div></div></div>
  </aside>
  <div id="main">
    <header id="topbar">
      <div><div class="top-title" id="topTitle"></div><div class="top-crumb" id="topCrumb"></div></div>
      <div class="top-spacer"></div>
      <span class="demo-badge">● 시연 데이터</span>
      <div class="top-item architecture"><span class="dot-live"></span><span id="infraLabel"></span></div>
      <div class="top-item mono" id="clock">--:--:--</div>
      <button class="notification-button" id="notificationButton" type="button">◇</button>
    </header>
    <div id="journeyBar">
      <div id="journeyTabs" role="tablist"></div>
      <div id="journeyBridge"></div>
      <div id="journeyPath"></div>
      <button id="nextScene"></button>
    </div>
    <div id="view"></div>
  </div>
</div>
<div class="toasts" id="toasts"></div>
```
> 실명 금지. 사용자 표기는 `{{CUSTOMER}} 임원` 같은 직무/회사명.

## 2. Spec navigation + 사이드바 렌더
```js
const routeScope=spec.story.routeScope || REQUIRED_ROUTES;
const navigation=spec.navigation.filter(route=>routeScope.includes(route.id));
const guidedJourneys=spec.story.guidedJourneys;
const navEl=document.getElementById('nav');
navEl.innerHTML=navigation.map(route=>`<a data-route="${escapeHtml(route.id)}">
  <span class="nav-icon">${escapeHtml(route.icon)}</span>
  <span class="nav-name">${escapeHtml(route.name)}</span>
  <span class="nav-short">${escapeHtml(route.short)}</span></a>`).join('');
navEl.querySelectorAll('a').forEach(link=>link.onclick=()=>{location.hash=link.dataset.route});
```

## 3. 헬퍼 + 타이머/클린업 레지스트리 (★ 누수·null 방지의 핵심)
```js
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const rnd=(a,b)=>a+Math.random()*(b-a);
const fmt=n=>n.toLocaleString('ko-KR');
const viewTimers=[], viewCleanups=[];
function addTimer(t){viewTimers.push(t);return t}            // setInterval/Timeout 전부 등록
function addCleanup(fn){viewCleanups.push(fn)}               // addEventListener 해제 등록
function clearViewLifecycle(){
  viewTimers.splice(0).forEach(timer=>{clearInterval(timer);clearTimeout(timer)});
  viewCleanups.splice(0).forEach(fn=>{try{fn()}catch(error){console.error(error)}});
}
```
규칙: **뷰 안의 모든 `setInterval`/자동 `setTimeout`은 `addTimer(...)`로 감싸고**, 모든 `addEventListener`는
`addCleanup(()=>removeEventListener(...))`로 등록한다. 라우트 전환 시 자동 정리된다.

## 4. 라우터
```js
const VIEWS={};
function navigate(){
  const id=(location.hash.slice(1))||'dashboard';
  const route=navigation.find(item=>item.id===id)||navigation[0];
  clearViewLifecycle();
  $$('#nav a').forEach(link=>link.classList.toggle('active',link.dataset.route===route.id));
  $('#topTitle').textContent=route.name;
  $('#topCrumb').textContent=`${spec.meta.appName} · ${route.crumb||route.short}`;
  const v=document.getElementById('view');
  const def=(VIEWS[route.id]||VIEWS.dashboard)();
  v.innerHTML=`<div class="view-enter">${def.html}</div>`;
  if(def.init)def.init();
  v.scrollTop=0;
}
window.addEventListener('hashchange',navigate);
```

## 5. 전역 틱 (앱 전체 — 정리하지 않음)
```js
setInterval(()=>{$('#clock').textContent=new Date().toLocaleTimeString('ko-KR',{hour12:false})},1000);
function toast(title,subtitle,icon='✦'){
  const el=document.createElement('div');el.className='toast';
  el.innerHTML=`<div class="toast-icon">${escapeHtml(icon)}</div><div>
    <div class="toast-title">${escapeHtml(title)}</div><div class="toast-sub">${escapeHtml(subtitle)}</div></div>`;
  $('#toasts').appendChild(el);setTimeout(()=>{el.classList.add('out');setTimeout(()=>el.remove(),380)},4200);
}
```

## 6. 차트 유틸 (순수 SVG — 외부 라이브러리 금지)
```js
// 스파크라인(KPI 카드 우하단)
let sparkSequence=0;
function sparkline(values,color='var(--brand)'){
  const data=values.length>1?values:[0,1],id=`spark-${++sparkSequence}`,w=94,h=42;
  const mn=Math.min(...data),mx=Math.max(...data),rng=(mx-mn)||1;
  const pts=data.map((v,i)=>[i/(data.length-1)*w, h-4-((v-mn)/rng)*(h-8)]);
  const d=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:100%">
    <defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${color}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
    <path d="${d} L${w},${h} L0,${h} Z" fill="url(#${id})" opacity=".25"/><path d="${d}" fill="none" stroke="${color}" stroke-width="2"/></svg>`;
}
// 카운트업/트윈 — KPI 애니메이션
function countUp(el){const to=parseFloat(el.dataset.count),pre=el.dataset.pre||'',suf=el.dataset.suf||'',dec=(to%1?1:0),t0=performance.now();
  (function f(t){let p=Math.min(1,(t-t0)/1100);p=1-Math.pow(1-p,3);el.textContent=pre+(to*p).toFixed(dec)+suf;if(p<1)requestAnimationFrame(f)})(t0);}
```
- **스트리밍 라인차트**: 데이터 배열을 `addTimer(setInterval(... data.push(); data.shift(); redraw() ,1800))`로 흘린다. 마지막 점에 `<animate>` 펄스.
- **게이지(반원)**: `M30,110 A80,80 0 0,1 …` 아크 + 색상(ok/warn/bad). 슬라이더 oninput으로 갱신.
- **도넛**: `<circle stroke-dasharray>` 누적 오프셋. **막대**: `.bf{width:0;transition}` → 실행 시 `width=%`.

## 7. VIEW 패턴 (각 화면)
```js
VIEWS.dashboard=()=>({
  html:`…`,                       // 템플릿 문자열(컴포넌트 조립)
  init(){
    // 데이터/이벤트 바인딩. 모든 타이머는 addTimer(...), 리스너는 addCleanup(...)
    addTimer(setInterval(()=>{/* KPI 미세 변동 */},2000));
    // 차트/피드/맵 …
  }
});
```

## 8. 부팅
```js
function fit(){} // (앱은 100vh grid라 별도 스케일 불필요)
navigate();      // 초기 라우트 렌더
```

## 정리 — 반드시 지킬 4가지
1. 뷰 타이머는 `addTimer`, 리스너는 `addCleanup`.
2. 비동기 콜백/체인에서 DOM 접근 전 `const el=$('#x'); if(!el)return;`.
3. 외부 차트 라이브러리 금지(SVG 직접).
4. 클릭 가능한 목록 행에는 반드시 `onclick` 바인딩(렌더 직후 `$$().forEach`).
