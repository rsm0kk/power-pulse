# -*- coding: utf-8 -*-
"""전력기기 대시보드 HTML 템플릿. DATA 상수만 주입해서 완성본을 찍어낸다."""

HTML = r"""<!doctype html>
<html lang="ko" data-density="compact">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="data:,">
<title>Power Equipment Pulse · 전력기기 대시보드</title>
<style>
:root{
  color-scheme:light;
  --ink:#172033; --muted:#667085; --line:#d9e0e8; --soft-line:#e9edf2;
  --paper:#ffffff; --canvas:#f3f6f9;
  --navy:#172b4d; --navy-2:#223b66;
  --blue:#175cd3; --blue-soft:#eaf2ff; --blue-ink:#285a9f;
  --green:#087a55; --green-soft:#d3f2e3;
  --red:#b42318; --red-soft:#fee4e2;
  --amber:#8b4e00; --amber-soft:#ffe08a;
  --orange:#b54708; --orange-soft:#fff1e7;
  --shadow:0 12px 30px rgba(23,43,77,.08); --radius:12px;
}
*{box-sizing:border-box}
body{margin:0;background:var(--canvas);color:var(--ink);
  font-family:Arial,"Malgun Gothic","Apple SD Gothic Neo",sans-serif;font-size:13px;line-height:1.35}
button,input,select,textarea{font:inherit}
button{color:inherit;cursor:pointer}
.shell{width:min(1240px,calc(100% - 32px));margin:0 auto;padding:24px 0 20px}

.hero{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end;padding:12px 16px;
  border:1px solid #0f2343;border-radius:var(--radius) var(--radius) 0 0;
  background:linear-gradient(100deg,rgba(255,255,255,.06),transparent 45%),var(--navy);color:#fff}
.eyebrow{margin:0 0 5px;color:#b9d1f5;font-size:12px;font-weight:700;letter-spacing:.1em}
h1{margin:0;font-size:clamp(20px,2vw,26px);font-weight:750;line-height:1.18;letter-spacing:-.03em}
.hero-sub{margin:6px 0 0;color:rgba(255,255,255,.78);font-size:12px}
.as-of{min-width:150px;padding:7px 10px;border:1px solid rgba(255,255,255,.2);border-radius:10px;
  background:rgba(255,255,255,.08);text-align:right}
.as-of strong,.as-of span{display:block}
.as-of strong{font-size:14px;font-variant-numeric:tabular-nums}
.as-of span{color:#b9d1f5;font-size:12px}

.control-panel{position:sticky;top:0;z-index:20;padding:8px 12px;border:1px solid var(--line);border-top:0;
  border-radius:0 0 var(--radius) var(--radius);background:rgba(255,255,255,.97);
  box-shadow:0 8px 20px rgba(23,43,77,.06);backdrop-filter:blur(10px)}
.control-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.control-row+.control-row{margin-top:6px;padding-top:6px;border-top:1px solid var(--soft-line)}
.section-label{flex:0 0 auto;color:var(--muted);font-size:12px;font-weight:700;letter-spacing:.04em}
.chips{display:flex;gap:6px;flex-wrap:wrap;min-width:0}
.chip{--chip-color:#344054;display:inline-flex;align-items:center;gap:6px;padding:6px 11px;
  border:1px solid var(--line);border-radius:999px;background:#fff;font-size:12.5px;font-weight:700;
  transition:border-color .14s ease,background .14s ease,transform .14s ease}
.chip:hover{border-color:var(--chip-color);transform:translateY(-1px)}
.chip[aria-pressed="true"]{border-color:var(--chip-color);
  background:color-mix(in srgb,var(--chip-color) 16%,white);
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--chip-color) 55%,transparent)}
.chip-dot{width:8px;height:8px;border-radius:50%;background:var(--chip-color)}
.chip-count{color:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.spacer{flex:1 1 auto}

.grid{display:grid;gap:10px;margin-top:10px}
.grid.cols-2{grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr)}
.grid.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.panel{padding:12px 14px 14px;border:1px solid var(--line);border-radius:var(--radius);
  background:var(--paper);box-shadow:var(--shadow);min-width:0}
.panel-head{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:10px;
  padding-bottom:7px;border-bottom:1px solid var(--soft-line)}
.panel-title{margin:0;font-size:14px;font-weight:800;letter-spacing:-.015em}
.panel-unit{color:var(--muted);font-size:11px;font-weight:700}

.kpi-label{color:var(--muted);font-size:11.5px;font-weight:700}
.kpi-value{margin-top:5px;font-size:22px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.kpi-value .u{margin-left:2px;font-size:11px;font-weight:700;color:var(--muted)}
.kpi-note{margin-top:5px;color:var(--muted);font-size:11px}

.table-wrap{overflow-x:auto;max-height:460px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
thead th{position:sticky;top:0;z-index:2;padding:7px 8px;border-bottom:1px solid var(--line);background:#f7f9fc;
  color:var(--muted);font-size:11.5px;font-weight:800;text-align:right;white-space:nowrap}
thead th:first-child,tbody td:first-child{text-align:left}
tbody td{padding:7px 8px;border-bottom:1px solid var(--soft-line);text-align:right;white-space:nowrap}
tbody tr:hover{background:#f9fbfd}
tbody td.name{font-weight:700}
tbody td.wrap{white-space:normal;text-align:left}
.pos{color:var(--red);font-weight:700}
.neg{color:var(--blue);font-weight:700}
.flat{color:var(--muted)}
.sub{color:var(--muted);font-size:11px;font-weight:400}

.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 7px;border-radius:999px;
  font-size:10.5px;font-weight:800;letter-spacing:.01em;white-space:nowrap}
.badge.report{background:var(--blue-soft);color:var(--blue-ink)}
.badge.external{background:var(--green-soft);color:var(--green)}
.badge.estimate{background:var(--amber-soft);color:var(--amber)}
.badge.unverified{background:var(--red-soft);color:var(--red)}
.badge.fail{background:var(--red-soft);color:var(--red)}

.slider-zone{display:grid;gap:9px}
.slider-row{display:grid;grid-template-columns:118px minmax(0,1fr) 84px;gap:9px;align-items:center}
.slider-row label{color:var(--muted);font-size:12px;font-weight:700}
input[type="range"]{width:100%;accent-color:var(--blue)}
.slider-value{padding:4px 7px;border:1px solid var(--line);border-radius:8px;background:#f9fbfd;
  text-align:right;font-size:12.5px;font-weight:800;font-variant-numeric:tabular-nums}
.preset-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.preset{padding:5px 10px;border:1px solid var(--line);border-radius:999px;background:#fff;color:var(--muted);
  font-size:11.5px;font-weight:700}
.preset:hover{border-color:var(--blue);color:var(--blue)}
.preset[aria-pressed="true"]{border-color:var(--blue);background:var(--blue);color:#fff}

.chart-wrap{margin-top:4px}
svg.chart{width:100%;height:210px;display:block}
svg.chart.tall{height:250px}
.axis-line{stroke:var(--soft-line);stroke-width:1}
.axis-text{fill:var(--muted);font-size:10px;font-family:inherit}
.ord-tip-q{font-size:10.5px;font-weight:800;font-family:inherit}
.ord-tip-v{font-size:10px;font-weight:700;font-family:inherit;font-variant-numeric:tabular-nums}
#chartOrder{cursor:crosshair}
.series-line{fill:none;stroke:var(--blue);stroke-width:2}
.series-area{fill:var(--blue);opacity:.07}
.bar{fill:var(--blue);opacity:.28}
.bar.us{fill:var(--navy);opacity:.55}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;color:var(--muted);font-size:11px;font-weight:700}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}

.manual-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.manual-row{display:grid;grid-template-columns:minmax(0,1fr) 92px;gap:6px;align-items:center;
  padding:6px 8px;border:1px solid var(--soft-line);border-radius:8px;background:#fbfcfe}
.manual-row label{font-size:11.5px;font-weight:700;color:var(--ink)}
.manual-row .u2{color:var(--muted);font-weight:400;font-size:10.5px}
.manual-row input{width:100%;padding:4px 6px;border:1px solid var(--line);border-radius:6px;text-align:right;
  font-variant-numeric:tabular-nums;font-weight:700}
.manual-prev{grid-column:1/-1;color:var(--muted);font-size:10.5px;margin-top:-2px}
.btn-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.btn{padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;font-size:12px;font-weight:700}
.btn:hover{border-color:var(--blue);color:var(--blue)}
.btn.primary{background:var(--navy);color:#fff;border-color:var(--navy)}
.io-area{width:100%;height:80px;margin-top:8px;padding:6px;border:1px solid var(--line);border-radius:8px;
  font-family:ui-monospace,Consolas,monospace;font-size:11px;display:none}

.status-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;font-size:11px;color:var(--muted)}
.empty{padding:26px 10px;text-align:center;color:var(--muted);font-size:12px}

.source-note{margin-top:12px;padding:10px 12px;border:1px solid var(--soft-line);border-radius:10px;
  background:#fbfcfe;color:var(--muted);font-size:11px;line-height:1.55}
.source-note b{color:var(--ink)}
.source-note a{color:var(--blue)}

@media (max-width:900px){
  .grid.cols-2{grid-template-columns:minmax(0,1fr)}
  .grid.cols-4{grid-template-columns:repeat(2,minmax(0,1fr))}
  .manual-grid{grid-template-columns:minmax(0,1fr)}
}
@media (max-width:520px){
  .hero{grid-template-columns:minmax(0,1fr)}
  .grid.cols-4{grid-template-columns:minmax(0,1fr)}
  .slider-row{grid-template-columns:92px minmax(0,1fr) 72px}
}
@media print{
  body{background:#fff}
  .control-panel{position:static;box-shadow:none;backdrop-filter:none}
  .panel{box-shadow:none;break-inside:avoid}
  .preset-row,.chips,.btn-row{display:none}
}
</style>
</head>
<body>
<div class="shell">

  <header class="hero">
    <div>
      <p class="eyebrow">CAPITAL RESEARCH · 전력기기 섹터</p>
      <h1 id="headline">Power Equipment Pulse</h1>
      <p class="hero-sub">LS ELECTRIC · 효성중공업 · HD현대일렉트릭 · 산일전기 · 일진전기 · 대한전선 · 가온전선<span id="autoTag"></span></p>
    </div>
    <div class="as-of">
      <span>데이터 기준</span>
      <strong id="asOf">-</strong>
      <span id="genAt">-</span>
    </div>
  </header>

  <nav class="control-panel">
    <div class="control-row">
      <span class="section-label">품목</span>
      <div class="chips" id="chipsItem"></div>
      <span class="spacer"></span>
      <span class="section-label" id="countLabel"></span>
    </div>
    <div class="control-row">
      <span class="section-label">대상국</span>
      <div class="chips" id="chipsCnty"></div>
      <span class="spacer"></span>
      <div class="status-row" id="statusRow"></div>
    </div>
  </nav>

  <section class="grid cols-4">
    <div class="panel">
      <div class="kpi-label">수출액 (최근월)</div>
      <div class="kpi-value" id="kpiExp">-</div>
      <div class="kpi-note" id="kpiExpNote">-</div>
    </div>
    <div class="panel">
      <div class="kpi-label">수출단가</div>
      <div class="kpi-value" id="kpiPrice">-</div>
      <div class="kpi-note" id="kpiPriceNote">P 지표 · USD/kg</div>
    </div>
    <div class="panel">
      <div class="kpi-label">수출중량</div>
      <div class="kpi-value" id="kpiVol">-</div>
      <div class="kpi-note" id="kpiVolNote">Q 지표</div>
    </div>
    <div class="panel">
      <div class="kpi-label" id="kpiFredLabel">미국 전력 건설투자</div>
      <div class="kpi-value" id="kpiFred">-</div>
      <div class="kpi-note" id="kpiFredNote">-</div>
    </div>
  </section>

  <section class="grid cols-2">
    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">수출 추이 — 금액(막대) vs 단가(선)</h2>
        <span class="panel-unit" id="tradeChartUnit">단위: 백만USD, USD/kg</span>
      </div>
      <svg class="chart tall" id="chartTrade" viewBox="0 0 660 250" role="img" aria-label="수출 추이"></svg>
      <div class="legend">
        <span><i style="background:var(--navy);opacity:.55"></i>수출금액</span>
        <span><i style="background:var(--blue)"></i>수출단가 USD/kg</span>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">미국 수요 지표</h2>
        <span class="panel-unit">FRED · 최초값=100 지수화</span>
      </div>
      <svg class="chart tall" id="chartFred" viewBox="0 0 660 250" role="img" aria-label="미국 지표"></svg>
      <div class="legend" id="fredLegend"></div>
    </div>
  </section>

  <section class="grid cols-2">
    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">품목별 수출 실적</h2>
        <span class="panel-unit">단위: 백만USD, USD/kg, %</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>품목 / HS</th><th>대상국</th><th>기준월</th><th>수출액</th><th>MoM</th><th>YoY</th><th>단가</th><th>단가YoY</th><th>근거</th>
          </tr></thead>
          <tbody id="tbodyTrade"></tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">시나리오 — 대미 변압기 수출 연환산</h2>
        <span class="panel-unit">실시간 재계산</span>
      </div>
      <div class="slider-zone">
        <div class="slider-row">
          <label for="sPrice">단가 변화 (P)</label>
          <input id="sPrice" type="range" min="-30" max="60" step="1" value="0">
          <output class="slider-value" id="sPriceOut">0%</output>
        </div>
        <div class="slider-row">
          <label for="sVol">물량 변화 (Q)</label>
          <input id="sVol" type="range" min="-30" max="60" step="1" value="0">
          <output class="slider-value" id="sVolOut">0%</output>
        </div>
        <div class="slider-row">
          <label for="sFx">원/달러</label>
          <input id="sFx" type="range" min="1200" max="1700" step="5" value="1380">
          <output class="slider-value" id="sFxOut">1,380</output>
        </div>
      </div>
      <div class="preset-row" id="presets"></div>
      <div class="grid cols-2" style="margin-top:10px">
        <div class="panel" style="box-shadow:none">
          <div class="kpi-label">연환산 수출액</div>
          <div class="kpi-value" id="scnUsd">-</div>
          <div class="kpi-note">최근월 ×12 기준</div>
        </div>
        <div class="panel" style="box-shadow:none">
          <div class="kpi-label">원화 환산</div>
          <div class="kpi-value" id="scnKrw">-</div>
          <div class="kpi-note" id="scnDelta">-</div>
        </div>
      </div>
    </div>
  </section>

  <section class="grid cols-2">
    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">커버리지 7사 분기 실적 (DART)</h2>
        <span class="panel-unit">단위: 십억원, % · 연결기준</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>종목</th><th>티커</th><th>분기</th><th>매출</th><th>YoY</th><th>영업이익</th><th>OPM</th><th>OPM 전년</th><th>근거</th>
          </tr></thead>
          <tbody id="tbodyFin"></tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">최근 공시</h2>
        <span class="panel-unit">DART · 공급계약·실적 필터</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>일자</th><th>종목</th><th>공시</th></tr></thead>
          <tbody id="tbodyDisc"></tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="grid cols-2">
    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">수주잔고 · 신규수주 추이</h2>
        <span class="panel-unit">단위: 억원 · 분기 · 연결기준</span>
      </div>
      <div class="chips" id="chipsOrder" style="margin-bottom:8px"></div>
      <svg class="chart tall" id="chartOrder" viewBox="0 0 660 250" role="img" aria-label="수주잔고·신규수주"></svg>
      <div class="legend" id="orderLegend"></div>
      <div id="orderManual" style="display:none;margin-top:8px">
        <p class="kpi-note" id="orderManualHint"></p>
        <textarea class="io-area" id="orderManualArea" spellcheck="false"
          placeholder="한 줄에 한 분기: 2025Q4=126000&#10;2026Q1=131000  (수주잔고, 억원)"></textarea>
        <div class="btn-row"><button class="btn primary" id="btnOrderSave">효성 수주잔고 저장</button></div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">분기별 변화 — QoQ · YoY</h2>
        <span class="panel-unit" id="orderTblCo">-</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>분기</th><th>수주잔고</th><th>QoQ</th><th>YoY</th><th>신규수주</th><th>QoQ</th><th>YoY</th><th>근거</th>
          </tr></thead>
          <tbody id="tbodyOrder"></tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="grid cols-2">
    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">수기 입력 지표 — 변화폭 자동 계산</h2>
        <span class="panel-unit">API 없는 지표 · 저장 시 직전값 대비 비교</span>
      </div>
      <div class="manual-grid" id="manualGrid"></div>
      <div class="btn-row">
        <button class="btn primary" id="btnSave">저장 (직전값 대비 계산)</button>
        <button class="btn" id="btnExport">JSON 내보내기</button>
        <button class="btn" id="btnImport">JSON 불러오기</button>
      </div>
      <textarea class="io-area" id="ioArea" spellcheck="false"></textarea>
      <p class="kpi-note" id="manualHint"></p>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2 class="panel-title">수집 상태</h2>
        <span class="panel-unit">실패 항목은 재실행 필요</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>소스</th><th>항목</th><th>건수</th><th>상태</th></tr></thead>
          <tbody id="tbodyStatus"></tbody>
        </table>
      </div>
    </div>
  </section>

  <footer class="source-note">
    <b>Source tiering</b> ·
    <span class="badge report">리포트</span> 증권사 리포트에 명시된 수치 ·
    <span class="badge external">외부확인</span> DART/관세청/FRED 원문 확인 ·
    <span class="badge estimate">추정</span> 애널리스트 가정 기반 추정치 ·
    <span class="badge unverified">미검증</span> 근거 미확보(문서에 포함 금지)<br>
    <b>출처</b> 관세청 품목별 국가별 수출입실적(공공데이터포털) · 금융감독원 DART Open API · Federal Reserve Bank of St. Louis (FRED) · 수기 입력분은 애널리스트 직접 입력<br>
    <b>기준일</b> <span id="footAsOf">-</span> · <b>생성</b> <span id="footGen">-</span> · Capital Research · 본 자료는 투자 판단의 참고 자료이며 투자 결과에 대한 책임 소재의 증빙으로 사용될 수 없습니다.
  </footer>
</div>

<script>
/* ============ DATA (빌드 시 주입) ============ */
const DATA = /*__DATA__*/{};

/* ============ helpers ============ */
const GRADE_LABEL={report:"리포트",external:"외부확인",estimate:"추정",unverified:"미검증"};
const fmt=(v,d=1)=>(v===null||v===undefined||!isFinite(v))?"-":Number(v).toLocaleString("ko-KR",{minimumFractionDigits:d,maximumFractionDigits:d});
const fmtSigned=(v,d=1)=>(v===null||v===undefined||!isFinite(v))?"-":((v>0?"+":v<0?"−":"")+fmt(Math.abs(v),d));
const tone=v=>(v===null||v===undefined||!isFinite(v))?"flat":(v>0?"pos":v<0?"neg":"flat");
const pct=(a,b)=>(a===null||b===null||a===undefined||b===undefined||!b)?null:(a/b-1)*100;
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const ymAdd=(ym,n)=>{const y=+ym.slice(0,4),m=+ym.slice(5,7)-1;const d=new Date(y,m+n,1);
  return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0");};

const TRADE=(DATA.trade||[]).slice();
const ITEM_COLOR={"변압기":"#175cd3","차단기·개폐기":"#b54708","전선·케이블":"#087a55","전력변환":"#7a5af8","배전반":"#0e7090"};

const state={item:"전체",cnty:(TRADE.some(r=>r.cnty==="US")?"US":"전체"),
  p:0,q:0,fx:(DATA.baseFx||1380),manual:{},orderCo:null};

/* ============ 필터 ============ */
const itemsAll=[...new Set(TRADE.map(r=>r.group))];
const cntyAll=[...new Set(TRADE.map(r=>r.cnty))];
const rowsFiltered=()=>TRADE.filter(r=>(state.item==="전체"||r.group===state.item)&&(state.cnty==="전체"||r.cnty===state.cnty));

/* 필터 조건에 맞는 월별 합계 시계열 */
function monthlyAgg(){
  const m={};
  rowsFiltered().forEach(r=>{
    if(!m[r.ym])m[r.ym]={ym:r.ym,usd:0,kg:0};
    m[r.ym].usd+=(r.expUsd||0); m[r.ym].kg+=(r.expKg||0);
  });
  return Object.values(m).sort((a,b)=>a.ym<b.ym?-1:1)
    .map(o=>({...o,price:o.kg?o.usd/o.kg:null}));
}
/* 품목×국가 단위 최신월 요약 */
function latestByKey(){
  const k={};
  rowsFiltered().forEach(r=>{
    const key=r.hs+"|"+r.cnty;
    if(!k[key])k[key]={};
    k[key][r.ym]=r;
  });
  const out=[];
  Object.values(k).forEach(byYm=>{
    const yms=Object.keys(byYm).sort();
    const last=yms[yms.length-1]; if(!last)return;
    const cur=byYm[last], prev=byYm[ymAdd(last,-1)], yoy=byYm[ymAdd(last,-12)];
    out.push({...cur,
      mom:prev?pct(cur.expUsd,prev.expUsd):null,
      yoy:yoy?pct(cur.expUsd,yoy.expUsd):null,
      price:cur.expKg?cur.expUsd/cur.expKg:null,
      priceYoy:(yoy&&yoy.expKg&&cur.expKg)?pct(cur.expUsd/cur.expKg,yoy.expUsd/yoy.expKg):null});
  });
  return out.sort((a,b)=>(b.expUsd||0)-(a.expUsd||0));
}

/* ============ render: chips ============ */
function chip(host,label,count,color,pressed,onClick){
  const b=document.createElement("button");
  b.className="chip"; b.style.setProperty("--chip-color",color);
  b.setAttribute("aria-pressed",String(pressed));
  b.innerHTML='<span class="chip-dot"></span>'+esc(label)+'<span class="chip-count">'+count+'</span>';
  b.addEventListener("click",onClick); host.appendChild(b);
}
function renderChips(){
  const hi=document.getElementById("chipsItem"); hi.innerHTML="";
  chip(hi,"전체",TRADE.length,"#172b4d",state.item==="전체",()=>{state.item="전체";render();});
  itemsAll.forEach(g=>chip(hi,g,TRADE.filter(r=>r.group===g).length,ITEM_COLOR[g]||"#344054",
    state.item===g,()=>{state.item=g;render();}));
  const hc=document.getElementById("chipsCnty"); hc.innerHTML="";
  cntyAll.forEach(c=>chip(hc,(DATA.cntyLabel&&DATA.cntyLabel[c])||c,
    TRADE.filter(r=>r.cnty===c).length,c==="US"?"#b42318":"#344054",
    state.cnty===c,()=>{state.cnty=c;render();}));
}

/* ============ render: KPI ============ */
function renderKpi(){
  const ms=monthlyAgg();
  const last=ms[ms.length-1], prev=ms[ms.length-2], yoy=ms.length>12?ms[ms.length-13]:null;
  document.getElementById("countLabel").textContent=rowsFiltered().length+"행 · "+ms.length+"개월";
  if(!last){["kpiExp","kpiPrice","kpiVol"].forEach(id=>document.getElementById(id).textContent="-");return;}
  const e=document.getElementById("kpiExp");
  e.innerHTML=fmt(last.usd/1e6,1)+'<span class="u">백만USD</span>';
  const y=yoy?pct(last.usd,yoy.usd):null, m=prev?pct(last.usd,prev.usd):null;
  document.getElementById("kpiExpNote").innerHTML=last.ym+" · YoY <b class='"+tone(y)+"'>"+fmtSigned(y,1)+"%</b> · MoM <b class='"+tone(m)+"'>"+fmtSigned(m,1)+"%</b>";
  const p=document.getElementById("kpiPrice");
  p.innerHTML=fmt(last.price,2)+'<span class="u">USD/kg</span>';
  p.className="kpi-value "+tone(yoy&&yoy.price?pct(last.price,yoy.price):null);
  document.getElementById("kpiPriceNote").innerHTML="P 지표 · YoY <b class='"+tone(yoy&&yoy.price?pct(last.price,yoy.price):null)+"'>"+fmtSigned(yoy&&yoy.price?pct(last.price,yoy.price):null,1)+"%</b>";
  document.getElementById("kpiVol").innerHTML=fmt(last.kg/1e6,1)+'<span class="u">천톤</span>';
  document.getElementById("kpiVolNote").innerHTML="Q 지표 · YoY <b class='"+tone(yoy?pct(last.kg,yoy.kg):null)+"'>"+fmtSigned(yoy?pct(last.kg,yoy.kg):null,1)+"%</b>";

  const f=(DATA.fred||{})[DATA.headlineFred];
  const kf=document.getElementById("kpiFred");
  if(f&&f.obs&&f.obs.length){
    document.getElementById("kpiFredLabel").textContent=f.short||f.title;
    const o=f.obs, L=o[o.length-1], Y=o.length>12?o[o.length-13]:null;
    kf.innerHTML=fmt(L.v,0)+'<span class="u">'+esc(f.unit||"")+'</span>';
    const yy=Y?pct(L.v,Y.v):null; kf.className="kpi-value "+tone(yy);
    document.getElementById("kpiFredNote").innerHTML=L.d+" · YoY <b class='"+tone(yy)+"'>"+fmtSigned(yy,1)+"%</b>";
  }else{kf.textContent="-";document.getElementById("kpiFredNote").textContent="FRED 미수집";}
}

/* ============ 차트 호버 공용 유틸 (viewBox 폭 660 공통) ============ */
function bindHover(svgId,gId,resolve){
  const svg=document.getElementById(svgId);
  if(svg.dataset.hb)return; svg.dataset.hb="1"; svg.style.cursor="crosshair";
  svg.addEventListener("mouseleave",()=>{const g=document.getElementById(gId);if(g)g.style.display="none";});
  svg.addEventListener("mousemove",e=>{
    const g=document.getElementById(gId);if(!g)return;
    const r=svg.getBoundingClientRect();
    const vx=(e.clientX-r.left)/r.width*660;
    const html=resolve(vx);
    if(html==null){g.style.display="none";return;}
    g.style.display=""; g.innerHTML=html;
  });
}
function tipBox(cx,rows,W,PT){
  const wpx=Math.max.apply(null,rows.map(r=>r.t.length))*6.7+20, hpx=rows.length*13+9;
  const bx=cx>W/2?(cx-wpx-8):(cx+8), by=PT+2;
  let s='<rect x="'+bx.toFixed(1)+'" y="'+by+'" rx="4" width="'+wpx.toFixed(0)+'" height="'+hpx+'" fill="#0b1a33" opacity="0.93"></rect>';
  rows.forEach((r,i)=>{s+='<text x="'+(bx+9).toFixed(1)+'" y="'+(by+15+i*13)+'" fill="'+(r.color||"#fff")
    +'" style="font-size:'+(i?10:10.5)+'px;font-weight:'+(i?700:800)+';font-family:inherit;font-variant-numeric:tabular-nums">'+esc(r.t)+'</text>';});
  return s;
}
let tradeHoverCtx=null,fredHoverCtx=null;
function tradeResolve(vx){
  const c=tradeHoverCtx; if(!c||!c.s.length)return null;
  let i=Math.round((vx-c.PL)/c.bw-0.5); i=Math.max(0,Math.min(c.s.length-1,i));
  const o=c.s[i]; if(!o)return null; const cx=c.xc(i);
  let s='<line x1="'+cx.toFixed(1)+'" x2="'+cx.toFixed(1)+'" y1="'+c.PT+'" y2="'+(c.H-c.PB)+'" stroke="#98a2b3" stroke-dasharray="3 3"></line>';
  s+='<circle cx="'+cx.toFixed(1)+'" cy="'+c.yU(o.usd).toFixed(1)+'" r="3.2" fill="#8a94a6"></circle>';
  if(o.price!=null)s+='<circle cx="'+cx.toFixed(1)+'" cy="'+c.yP(o.price).toFixed(1)+'" r="3.2" fill="#175cd3"></circle>';
  return s+tipBox(cx,[{t:o.ym},{t:"수출금액 "+fmt(o.usd/1e6,1)+" 백만USD",color:"#cbd5e1"},
    {t:"단가 "+(o.price==null?"-":fmt(o.price,2)+" USD/kg"),color:"#a9c7ff"}],c.W,c.PT);
}
function fredResolve(vx){
  const c=fredHoverCtx; if(!c||!c.series.length)return null;
  let i=Math.round((vx-c.PL)/((c.W-c.PL-c.PR)/((c.L-1)||1))); i=Math.max(0,Math.min(c.L-1,i));
  const px=c.x(i); let dots="",rows=[],date="";
  c.series.forEach(sr=>{const j=i-(c.L-sr.pts.length);
    if(j>=0&&j<sr.pts.length){const p=sr.pts[j]; if(p.v!=null){
      dots+='<circle cx="'+px.toFixed(1)+'" cy="'+c.y(p.v).toFixed(1)+'" r="2.8" fill="'+sr.color+'"></circle>';
      rows.push({t:sr.name+"  "+fmt(p.v,1),color:sr.color}); if(!date)date=p.d;}}});
  if(!rows.length)return null;
  let s='<line x1="'+px.toFixed(1)+'" x2="'+px.toFixed(1)+'" y1="'+c.PT+'" y2="'+(c.H-c.PB)+'" stroke="#98a2b3" stroke-dasharray="3 3"></line>'+dots;
  return s+tipBox(px,[{t:date+" · 지수(최초=100)"}].concat(rows),c.W,c.PT);
}

/* ============ render: 수출 차트 ============ */
function renderTradeChart(){
  const svg=document.getElementById("chartTrade");
  const s=monthlyAgg().slice(-24);
  if(s.length<2){svg.innerHTML='<text class="axis-text" x="330" y="125" text-anchor="middle">데이터 없음 — 관세청 수집 확인</text>';return;}
  const W=660,H=250,PL=52,PR=48,PT=14,PB=28;
  const uMax=Math.max(...s.map(o=>o.usd))*1.1||1;
  const pr=s.map(o=>o.price).filter(v=>v!=null);
  const pMin=pr.length?Math.min(...pr)*0.9:0, pMax=pr.length?Math.max(...pr)*1.1:1;
  const bw=(W-PL-PR)/s.length;
  const x=i=>PL+bw*i, xc=i=>PL+bw*(i+0.5);
  const yU=v=>PT+(H-PT-PB)*(1-v/uMax);
  const yP=v=>PT+(H-PT-PB)*(1-(v-pMin)/((pMax-pMin)||1));
  let g="";
  [0,.25,.5,.75,1].forEach(t=>{
    const gy=PT+(H-PT-PB)*t;
    g+='<line class="axis-line" x1="'+PL+'" y1="'+gy+'" x2="'+(W-PR)+'" y2="'+gy+'"></line>'
      +'<text class="axis-text" x="'+(PL-6)+'" y="'+(gy+3)+'" text-anchor="end">'+fmt(uMax*(1-t)/1e6,0)+'</text>'
      +'<text class="axis-text" x="'+(W-PR+6)+'" y="'+(gy+3)+'" text-anchor="start">'+fmt(pMax-(pMax-pMin)*t,1)+'</text>';
  });
  let bars="";
  s.forEach((o,i)=>{const h=Math.max(0,(H-PB)-yU(o.usd));
    bars+='<rect class="bar'+(state.cnty==="US"?" us":"")+'" x="'+(x(i)+bw*0.15).toFixed(1)+'" y="'+yU(o.usd).toFixed(1)+'" width="'+(bw*0.7).toFixed(1)+'" height="'+h.toFixed(1)+'"><title>'+o.ym+" "+fmt(o.usd/1e6,1)+'백만USD</title></rect>';});
  const ptsP=s.map((o,i)=>o.price==null?null:[xc(i),yP(o.price)]).filter(Boolean);
  const lineP=ptsP.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+","+p[1].toFixed(1)).join(" ");
  let xl="";
  const step=Math.ceil(s.length/8);
  s.forEach((o,i)=>{if(i%step===0)xl+='<text class="axis-text" x="'+xc(i).toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+o.ym.slice(2)+'</text>';});
  svg.innerHTML=g+bars+'<path class="series-line" d="'+lineP+'"></path>'+xl+'<g id="tradeHover" style="display:none"></g>';
  tradeHoverCtx={s,xc,yU,yP,PL,PR,PT,PB,H,W,bw};
  bindHover("chartTrade","tradeHover",tradeResolve);
}

/* ============ render: FRED 차트 ============ */
const FRED_COLORS=["#175cd3","#b54708","#087a55","#7a5af8","#b42318","#0e7090"];
function renderFredChart(){
  const svg=document.getElementById("chartFred"), leg=document.getElementById("fredLegend");
  const keys=Object.keys(DATA.fred||{}).filter(k=>(DATA.fred[k].obs||[]).length>3);
  if(!keys.length){svg.innerHTML='<text class="axis-text" x="330" y="125" text-anchor="middle">FRED 데이터 없음</text>';leg.innerHTML="";return;}
  const W=660,H=250,PL=44,PR=10,PT=14,PB=28,N=60;
  const series=keys.map((k,i)=>{
    const o=(DATA.fred[k].obs||[]).slice(-N);
    const base=o.length?o[0].v:1;
    return {k,name:DATA.fred[k].short||DATA.fred[k].title,color:FRED_COLORS[i%FRED_COLORS.length],
      pts:o.map(p=>({d:p.d,v:base?p.v/base*100:null}))};
  });
  const all=series.flatMap(s=>s.pts.map(p=>p.v)).filter(v=>v!=null&&isFinite(v));
  const mn=Math.min(...all)*0.98, mx=Math.max(...all)*1.02;
  const L=Math.max(...series.map(s=>s.pts.length));
  const x=i=>PL+(W-PL-PR)*(i/((L-1)||1));
  const y=v=>PT+(H-PT-PB)*(1-(v-mn)/((mx-mn)||1));
  let g="";
  [0,.25,.5,.75,1].forEach(t=>{const gy=PT+(H-PT-PB)*t;
    g+='<line class="axis-line" x1="'+PL+'" y1="'+gy+'" x2="'+(W-PR)+'" y2="'+gy+'"></line>'
      +'<text class="axis-text" x="'+(PL-6)+'" y="'+(gy+3)+'" text-anchor="end">'+fmt(mx-(mx-mn)*t,0)+'</text>';});
  let paths="";
  series.forEach(s=>{
    const off=L-s.pts.length;
    const d=s.pts.map((p,i)=>(i?"L":"M")+x(i+off).toFixed(1)+","+y(p.v).toFixed(1)).join(" ");
    paths+='<path d="'+d+'" fill="none" stroke="'+s.color+'" stroke-width="1.8"></path>';
  });
  const ref=series[0].pts, off0=L-ref.length, st=Math.ceil(ref.length/6);
  let xl="";
  ref.forEach((p,i)=>{if(i%st===0)xl+='<text class="axis-text" x="'+x(i+off0).toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+p.d.slice(2,7)+'</text>';});
  svg.innerHTML=g+paths+xl+'<g id="fredHover" style="display:none"></g>';
  fredHoverCtx={series,x,y,L,PL,PR,PT,PB,H,W};
  bindHover("chartFred","fredHover",fredResolve);
  leg.innerHTML=series.map(s=>'<span><i style="background:'+s.color+'"></i>'+esc(s.name)+'</span>').join("");
}

/* ============ render: 표 ============ */
function renderTradeTable(){
  const tb=document.getElementById("tbodyTrade"); tb.innerHTML="";
  const rows=latestByKey();
  if(!rows.length){tb.innerHTML='<tr><td colspan="9" class="empty">관세청 데이터가 없습니다. 수집 상태 패널을 확인하세요.</td></tr>';return;}
  rows.forEach(r=>{
    const tr=document.createElement("tr");
    tr.innerHTML='<td class="name">'+esc(r.item)+'<div class="sub">'+esc(r.hs)+" · "+esc(r.detail||"")+'</div></td>'
      +'<td>'+esc((DATA.cntyLabel&&DATA.cntyLabel[r.cnty])||r.cnty)+'</td>'
      +'<td>'+esc(r.ym)+'</td>'
      +'<td>'+fmt(r.expUsd/1e6,1)+'</td>'
      +'<td class="'+tone(r.mom)+'">'+fmtSigned(r.mom,1)+'</td>'
      +'<td class="'+tone(r.yoy)+'">'+fmtSigned(r.yoy,1)+'</td>'
      +'<td>'+fmt(r.price,2)+'</td>'
      +'<td class="'+tone(r.priceYoy)+'">'+fmtSigned(r.priceYoy,1)+'</td>'
      +'<td><span class="badge external">외부확인</span></td>';
    tb.appendChild(tr);
  });
}
function renderFin(){
  const tb=document.getElementById("tbodyFin"); tb.innerHTML="";
  const cs=DATA.companies||[];
  let any=false;
  cs.forEach(c=>{
    const q=(c.quarters||[]).slice().sort((a,b)=>a.q<b.q?-1:1);
    if(!q.length){
      tb.innerHTML+='<tr><td class="name">'+esc(c.name)+'</td><td>'+esc(c.stock||"-")+'</td>'
        +'<td colspan="6" class="sub" style="text-align:left">DART 재무 미수집</td>'
        +'<td><span class="badge fail">실패</span></td></tr>';
      return;
    }
    any=true;
    const cur=q[q.length-1];
    const prevY=q.find(o=>o.q===(String(+cur.q.slice(0,4)-1)+cur.q.slice(4)));
    const opm=cur.rev?cur.op/cur.rev*100:null;
    const opmY=(prevY&&prevY.rev)?prevY.op/prevY.rev*100:null;
    const badge=cur.prov?'<span class="badge estimate">잠정</span>':'<span class="badge external">외부확인</span>';
    tb.innerHTML+='<tr><td class="name">'+esc(c.name)+'</td><td>'+esc(c.stock||"-")+'</td>'
      +'<td>'+esc(cur.q)+(cur.prov?' <span class="sub">잠정</span>':'')+'</td>'
      +'<td>'+fmt(cur.rev/1e9,0)+'</td>'
      +'<td class="'+tone(prevY?pct(cur.rev,prevY.rev):null)+'">'+fmtSigned(prevY?pct(cur.rev,prevY.rev):null,1)+'</td>'
      +'<td>'+fmt(cur.op/1e9,0)+'</td>'
      +'<td class="'+tone(opm)+'">'+fmt(opm,1)+'%</td>'
      +'<td class="sub">'+fmt(opmY,1)+'%</td>'
      +'<td>'+badge+'</td></tr>';
  });
  if(!cs.length)tb.innerHTML='<tr><td colspan="9" class="empty">DART 데이터 없음</td></tr>';
}
function renderDisc(){
  const tb=document.getElementById("tbodyDisc"); tb.innerHTML="";
  const d=(DATA.filings||[]).slice(0,40);
  if(!d.length){tb.innerHTML='<tr><td colspan="3" class="empty">공시 데이터 없음</td></tr>';return;}
  d.forEach(f=>{
    const url=f.rcp?("https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+encodeURIComponent(f.rcp)):null;
    tb.innerHTML+='<tr><td>'+esc(f.date)+'</td><td class="name">'+esc(f.corp)+'</td>'
      +'<td class="wrap">'+(url?'<a href="'+url+'" target="_blank" rel="noopener">'+esc(f.title)+'</a>':esc(f.title))+'</td></tr>';
  });
}
function renderStatus(){
  const tb=document.getElementById("tbodyStatus"); tb.innerHTML="";
  (DATA.status||[]).forEach(s=>{
    tb.innerHTML+='<tr><td class="name">'+esc(s.src)+'</td><td class="wrap sub">'+esc(s.item)+'</td>'
      +'<td>'+(s.n==null?"-":fmt(s.n,0))+'</td>'
      +'<td><span class="badge '+(s.ok?"external":"fail")+'">'+(s.ok?"성공":"실패")+'</span></td></tr>';
  });
  const bad=(DATA.status||[]).filter(s=>!s.ok).length;
  document.getElementById("statusRow").innerHTML=bad
    ? '<span class="badge fail">수집 실패 '+bad+'건</span>'
    : '<span class="badge external">전체 수집 정상</span>';
}

/* ============ 시나리오 ============ */
function renderScenario(){
  const ms=monthlyAgg(); const last=ms[ms.length-1];
  const host=document.getElementById("presets");
  if(!host.dataset.done){
    host.innerHTML="";
    (DATA.presets||[]).forEach(p=>{
      const b=document.createElement("button"); b.className="preset"; b.textContent=p.label;
      b.addEventListener("click",()=>{
        state.p=p.p;state.q=p.q;
        document.getElementById("sPrice").value=p.p; document.getElementById("sVol").value=p.q;
        document.getElementById("sPriceOut").textContent=p.p+"%";
        document.getElementById("sVolOut").textContent=p.q+"%";
        render();
      });
      host.appendChild(b);
    });
    host.dataset.done="1";
  }
  [...host.children].forEach((b,i)=>{const p=(DATA.presets||[])[i];
    b.setAttribute("aria-pressed",String(!!p&&p.p===state.p&&p.q===state.q));});
  if(!last){document.getElementById("scnUsd").textContent="-";document.getElementById("scnKrw").textContent="-";return;}
  const base=last.usd*12;
  const scn=base*(1+state.p/100)*(1+state.q/100);
  document.getElementById("scnUsd").innerHTML=fmt(scn/1e9,2)+'<span class="u">십억USD</span>';
  document.getElementById("scnKrw").innerHTML=fmt(scn*state.fx/1e12,2)+'<span class="u">조원</span>';
  const dl=document.getElementById("scnDelta");
  const dd=pct(scn,base);
  dl.innerHTML="기준 대비 <b class='"+tone(dd)+"'>"+fmtSigned(dd,1)+"%</b> · 기준월 "+last.ym;
}

/* ============ 수기 입력 ============ */
const MKEY="powerpulse_manual_v1";
function loadManual(){
  let saved=null;
  try{saved=JSON.parse(localStorage.getItem(MKEY)||"null");}catch(e){}
  state.manual=saved||JSON.parse(JSON.stringify(DATA.manual||{values:{},prev:{},savedAt:null}));
}
function renderManual(){
  const host=document.getElementById("manualGrid"); host.innerHTML="";
  (DATA.manualFields||[]).forEach(f=>{
    const v=(state.manual.values||{})[f.k], p=(state.manual.prev||{})[f.k];
    const d=(v!=null&&p!=null&&p!==0)?pct(v,p):null;
    const wrap=document.createElement("div"); wrap.className="manual-row";
    wrap.innerHTML='<label for="m_'+f.k+'">'+esc(f.label)+' <span class="u2">'+esc(f.unit||"")+'</span>'
      +(d==null?'':'<div class="sub">직전 '+fmt(p,f.d||1)+' → <b class="'+tone(d)+'">'+fmtSigned(d,1)+'%</b></div>')
      +'</label><input id="m_'+f.k+'" type="number" step="any" value="'+(v==null?"":v)+'">';
    host.appendChild(wrap);
  });
  document.getElementById("manualHint").textContent=
    state.manual.savedAt?("마지막 저장 "+state.manual.savedAt+" · 저장 시 현재값이 '직전값'으로 이동합니다"):
    "값을 넣고 저장하면 다음 저장 때 변화폭이 계산됩니다.";
}
function saveManual(){
  const prev={...(state.manual.values||{})};
  const values={};
  (DATA.manualFields||[]).forEach(f=>{
    const el=document.getElementById("m_"+f.k);
    const raw=el&&el.value!==""?Number(el.value):null;
    if(raw!=null&&isFinite(raw))values[f.k]=raw;
  });
  state.manual={values,prev,savedAt:new Date().toISOString().slice(0,16).replace("T"," ")};
  try{localStorage.setItem(MKEY,JSON.stringify(state.manual));}catch(e){
    alert("브라우저 저장이 막혀 있습니다. [JSON 내보내기]로 값을 따로 보관하세요.");}
  renderManual();
}

/* ============ 수주잔고·신규수주 ============ */
const OKEY="powerpulse_orders_manual_v1";
const qSort=(a,b)=>a.q<b.q?-1:1;
const ORDERS_RAW=(DATA.orders||[]).map(c=>({...c,quarters:(c.quarters||[]).slice().sort(qSort)}));
function loadOrderManual(){let s={};try{s=JSON.parse(localStorage.getItem(OKEY)||"{}")||{};}catch(e){}return s;}
/* 수동(효성) 회사: 저장된 수주잔고 + 매출로 신규수주 유도 */
function orderCompanies(){
  const man=loadOrderManual();
  return ORDERS_RAW.map(c=>{
    const mv=man[c.name];
    if(c.mode==="manual"&&mv&&Object.keys(mv).length){
      const revq={}; (c.quarters||[]).forEach(q=>{if(q.rev!=null)revq[q.q]=q.rev;});
      const labs=[...new Set([...Object.keys(mv),...Object.keys(revq)])].sort();
      let prev=null; const qs=[];
      labs.forEach(lab=>{
        const bk=(mv[lab]!=null&&mv[lab]!=="")?Number(mv[lab]):null;
        const rv=revq[lab]!=null?revq[lab]:null;
        const no=(bk!=null&&prev!=null&&rv!=null)?(bk-prev+rv):null;
        if(bk!=null||rv!=null)qs.push({q:lab,backlog:bk,newOrders:(no!=null?Math.round(no*10)/10:null),rev:rv,man:true});
        if(bk!=null)prev=bk;
      });
      return {...c,quarters:qs};
    }
    return c;
  });
}
function curOrderCo(){
  const cs=orderCompanies();
  return cs.find(c=>c.name===state.orderCo)||cs.find(c=>c.quarters.some(q=>q.backlog!=null))||cs[0];
}
function renderOrderChips(){
  const host=document.getElementById("chipsOrder"); host.innerHTML="";
  const cs=orderCompanies();
  cs.forEach(c=>{
    const n=c.quarters.filter(q=>q.backlog!=null).length;
    const col=c.mode==="manual"?"#b54708":"#172b4d";
    chip(host,c.name,n||"수동",col,state.orderCo===c.name,()=>{state.orderCo=c.name;renderOrders();});
  });
}
function renderOrderChart(){
  const svg=document.getElementById("chartOrder"), leg=document.getElementById("orderLegend");
  const c=curOrderCo();
  const s=(c?c.quarters:[]).filter(q=>q.backlog!=null||q.newOrders!=null).slice(-13);
  if(s.length<1){svg.innerHTML='<text class="axis-text" x="330" y="125" text-anchor="middle">'
    +(c&&c.mode==="manual"?'효성중공업은 자동수집 불가 — 아래에 수주잔고를 입력하세요':'수주 데이터 없음')+'</text>';leg.innerHTML="";return;}
  const W=660,H=250,PL=62,PR=62,PT=14,PB=28;
  const bkMax=Math.max(...s.map(o=>o.backlog||0))*1.12||1;
  const nos=s.map(o=>o.newOrders).filter(v=>v!=null);
  const nMax=nos.length?Math.max(...nos)*1.15:1, nMin=Math.min(0,...(nos.length?nos:[0]));
  const bw=(W-PL-PR)/s.length;
  const x=i=>PL+bw*i, xc=i=>PL+bw*(i+0.5);
  const yB=v=>PT+(H-PT-PB)*(1-v/bkMax);
  const yN=v=>PT+(H-PT-PB)*(1-(v-nMin)/((nMax-nMin)||1));
  let g="";
  [0,.25,.5,.75,1].forEach(t=>{const gy=PT+(H-PT-PB)*t;
    g+='<line class="axis-line" x1="'+PL+'" y1="'+gy+'" x2="'+(W-PR)+'" y2="'+gy+'"></line>'
      +'<text class="axis-text" x="'+(PL-6)+'" y="'+(gy+3)+'" text-anchor="end">'+fmt(bkMax*(1-t),0)+'</text>'
      +'<text class="axis-text" x="'+(W-PR+6)+'" y="'+(gy+3)+'" text-anchor="start">'+fmt(nMax-(nMax-nMin)*t,0)+'</text>';});
  let bars="";
  s.forEach((o,i)=>{if(o.backlog==null)return;const h=Math.max(0,(H-PB)-yB(o.backlog));
    bars+='<rect class="bar" x="'+(x(i)+bw*0.16).toFixed(1)+'" y="'+yB(o.backlog).toFixed(1)+'" width="'+(bw*0.68).toFixed(1)+'" height="'+h.toFixed(1)+'"></rect>';});
  const pts=s.map((o,i)=>o.newOrders==null?null:[xc(i),yN(o.newOrders)]).filter(Boolean);
  const line=pts.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+","+p[1].toFixed(1)).join(" ");
  let dots=""; s.forEach((o,i)=>{if(o.newOrders!=null)dots+='<circle cx="'+xc(i).toFixed(1)+'" cy="'+yN(o.newOrders).toFixed(1)+'" r="2.4" fill="#b42318"></circle>';});
  let xl=""; const step=Math.ceil(s.length/8);
  s.forEach((o,i)=>{if(i%step===0)xl+='<text class="axis-text" x="'+xc(i).toFixed(1)+'" y="'+(H-8)+'" text-anchor="middle">'+esc(o.q.replace("Q","·"))+'</text>';});
  const hov='<g id="ordHover" style="display:none">'
    +'<line id="ordVline" y1="'+PT+'" y2="'+(H-PB)+'" stroke="#98a2b3" stroke-width="1" stroke-dasharray="3 3"></line>'
    +'<circle id="ordHb" r="3.2" fill="#8a94a6"></circle>'
    +'<circle id="ordHn" r="3.2" fill="#b42318"></circle>'
    +'<rect id="ordTipBg" x="0" y="0" rx="4" width="150" height="42" fill="#0b1a33" opacity="0.92"></rect>'
    +'<text id="ordTipQ" class="ord-tip-q" x="0" y="0" fill="#fff"></text>'
    +'<text id="ordTipB" class="ord-tip-v" x="0" y="0" fill="#cbd5e1"></text>'
    +'<text id="ordTipN" class="ord-tip-v" x="0" y="0" fill="#ffb4a8"></text></g>';
  svg.innerHTML=g+bars+'<path d="'+line+'" fill="none" stroke="#b42318" stroke-width="1.8"></path>'+dots+xl+hov;
  leg.innerHTML='<span><i style="background:#8a94a6"></i>수주잔고(좌·억원)</span><span><i style="background:#b42318"></i>신규수주(우·억원, 추정)</span><span style="color:var(--muted)">차트에 마우스를 올리면 값 표시</span>';
  orderHoverCtx={s,W,H,PL,PR,PT,PB,bw,xc,yB,yN,name:(c?c.name:"")};
  bindOrderHover();
}
let orderHoverCtx=null;
function bindOrderHover(){
  const svg=document.getElementById("chartOrder");
  if(svg.dataset.hoverBound)return; svg.dataset.hoverBound="1";
  const hide=()=>{const h=document.getElementById("ordHover"); if(h)h.style.display="none";};
  svg.addEventListener("mouseleave",hide);
  svg.addEventListener("mousemove",e=>{
    const c=orderHoverCtx; if(!c)return;
    const g=document.getElementById("ordHover"); if(!g)return;
    const r=svg.getBoundingClientRect();
    const vx=(e.clientX-r.left)/r.width*c.W;
    let i=Math.round((vx-c.PL)/c.bw-0.5);
    i=Math.max(0,Math.min(c.s.length-1,i));
    const o=c.s[i]; if(!o){hide();return;}
    const cx=c.xc(i);
    g.style.display="";
    const set=(id,a)=>{const el=document.getElementById(id);for(const k in a)el.setAttribute(k,a[k]);};
    set("ordVline",{x1:cx.toFixed(1),x2:cx.toFixed(1)});
    if(o.backlog!=null)set("ordHb",{cx:cx.toFixed(1),cy:c.yB(o.backlog).toFixed(1),style:""}); else set("ordHb",{style:"display:none"});
    if(o.newOrders!=null)set("ordHn",{cx:cx.toFixed(1),cy:c.yN(o.newOrders).toFixed(1),style:""}); else set("ordHn",{style:"display:none"});
    // 오른쪽에 고정된 읽기 상자 (커서가 오른쪽이면 왼쪽으로)
    const bw2=150, bx=cx>c.W/2?(cx-bw2-8):(cx+8), by=c.PT+2;
    set("ordTipBg",{x:bx.toFixed(1),y:by});
    const tq=document.getElementById("ordTipQ"),tb=document.getElementById("ordTipB"),tn=document.getElementById("ordTipN");
    tq.setAttribute("x",(bx+10).toFixed(1));tq.setAttribute("y",by+15);tq.textContent=o.q.replace("Q","·")+" ("+esc(c.name)+")";
    tb.setAttribute("x",(bx+10).toFixed(1));tb.setAttribute("y",by+28);tb.textContent="수주잔고 "+fmt(o.backlog,0)+" 억";
    tn.setAttribute("x",(bx+10).toFixed(1));tn.setAttribute("y",by+39);tn.textContent="신규수주 "+(o.newOrders==null?"-":fmt(o.newOrders,0)+" 억");
  });
}
function renderOrderTable(){
  const tb=document.getElementById("tbodyOrder"); tb.innerHTML="";
  const c=curOrderCo();
  document.getElementById("orderTblCo").textContent=c?(c.name+(c.mode==="manual"?" · 수기입력":"")):"-";
  const q=(c?c.quarters:[]).filter(o=>o.backlog!=null);
  const man=document.getElementById("orderManual");
  if(c&&c.mode==="manual"){
    man.style.display="block";
    document.getElementById("orderManualHint").innerHTML=
      "효성중공업은 DART 수주상황이 건설 진행률표뿐이라 전사 수주잔고 자동수집이 불가합니다. IR 자료의 분기말 수주잔고(억원)를 입력하면 신규수주가 자동 계산됩니다.";
    const area=document.getElementById("orderManualArea");
    if(document.activeElement!==area){
      const saved=(loadOrderManual()[c.name])||{};
      const keys=Object.keys(saved).sort();
      area.value=keys.map(k=>k+"="+saved[k]).join("\n");
    }
  }else man.style.display="none";
  if(!q.length){tb.innerHTML='<tr><td colspan="8" class="empty">'
    +(c&&c.mode==="manual"?'수기 입력 대기 — 아래에 값을 넣어주세요':'수주잔고 데이터 없음')+'</td></tr>';return;}
  const by={}; q.forEach(o=>by[o.q]=o);
  const prevQ=lab=>{const y=+lab.slice(0,4),n=+lab.slice(5);return n>1?(y+"Q"+(n-1)):((y-1)+"Q4");};
  const yoyQ=lab=>((+lab.slice(0,4)-1)+lab.slice(4));
  q.slice(-10).reverse().forEach(o=>{
    const pB=by[prevQ(o.q)], yB=by[yoyQ(o.q)];
    const bQoQ=pB?pct(o.backlog,pB.backlog):null, bYoY=yB?pct(o.backlog,yB.backlog):null;
    const nQoQ=(pB&&pB.newOrders!=null&&o.newOrders!=null)?pct(o.newOrders,pB.newOrders):null;
    const nYoY=(yB&&yB.newOrders!=null&&o.newOrders!=null)?pct(o.newOrders,yB.newOrders):null;
    const bBadge=c.mode==="manual"?'<span class="badge estimate">추정</span>':'<span class="badge external">외부확인</span>';
    tb.innerHTML+='<tr><td class="name">'+esc(o.q.replace("Q","·"))+'</td>'
      +'<td>'+fmt(o.backlog,0)+'</td>'
      +'<td class="'+tone(bQoQ)+'">'+fmtSigned(bQoQ,1)+'</td>'
      +'<td class="'+tone(bYoY)+'">'+fmtSigned(bYoY,1)+'</td>'
      +'<td>'+(o.newOrders==null?"-":fmt(o.newOrders,0))+'</td>'
      +'<td class="'+tone(nQoQ)+'">'+fmtSigned(nQoQ,1)+'</td>'
      +'<td class="'+tone(nYoY)+'">'+fmtSigned(nYoY,1)+'</td>'
      +'<td>'+bBadge+'</td></tr>';
  });
}
function renderOrders(){renderOrderChips();renderOrderChart();renderOrderTable();}
function saveOrderManual(){
  const c=curOrderCo(); if(!c||c.mode!=="manual")return;
  const txt=document.getElementById("orderManualArea").value;
  const mv={};
  txt.split(/[\n,]+/).forEach(line=>{
    const m=line.match(/(\d{4})\s*Q?\s*([1-4])\s*[=:]\s*(-?[\d,\.]+)/i);
    if(m)mv[m[1]+"Q"+m[2]]=Number(m[3].replace(/,/g,""));
  });
  const man=loadOrderManual(); man[c.name]=mv;
  try{localStorage.setItem(OKEY,JSON.stringify(man));}catch(e){alert("브라우저 저장이 막혀 있습니다.");}
  renderOrders();
}

/* ============ render ============ */
function render(){
  renderChips(); renderKpi(); renderTradeChart(); renderFredChart();
  renderTradeTable(); renderFin(); renderDisc(); renderStatus(); renderScenario();
  renderOrders();
}

document.getElementById("asOf").textContent=DATA.asOf||"-";
document.getElementById("genAt").textContent=(DATA.generatedAt||"").slice(0,16);
document.getElementById("footAsOf").textContent=DATA.asOf||"-";
document.getElementById("footGen").textContent=DATA.generatedAt||"-";
if(DATA.headline)document.getElementById("headline").textContent=DATA.headline;

document.getElementById("sPrice").addEventListener("input",e=>{state.p=+e.target.value;
  document.getElementById("sPriceOut").textContent=state.p+"%";renderScenario();});
document.getElementById("sVol").addEventListener("input",e=>{state.q=+e.target.value;
  document.getElementById("sVolOut").textContent=state.q+"%";renderScenario();});
document.getElementById("sFx").addEventListener("input",e=>{state.fx=+e.target.value;
  document.getElementById("sFxOut").textContent=fmt(state.fx,0);renderScenario();});
document.getElementById("sFx").value=state.fx;
document.getElementById("sFxOut").textContent=fmt(state.fx,0);

document.getElementById("btnOrderSave").addEventListener("click",saveOrderManual);
document.getElementById("btnSave").addEventListener("click",saveManual);
document.getElementById("btnExport").addEventListener("click",()=>{
  const t=document.getElementById("ioArea"); t.style.display="block";
  t.value=JSON.stringify(state.manual,null,1); t.select();});
document.getElementById("btnImport").addEventListener("click",()=>{
  const t=document.getElementById("ioArea");
  if(t.style.display!=="block"){t.style.display="block";t.value="";t.placeholder="여기에 JSON 붙여넣고 다시 [JSON 불러오기]";t.focus();return;}
  try{state.manual=JSON.parse(t.value);
    try{localStorage.setItem(MKEY,JSON.stringify(state.manual));}catch(e){}
    renderManual(); t.style.display="none";}
  catch(e){alert("JSON 형식이 아닙니다.");}});

loadManual(); renderManual(); render();
</script>
</body>
</html>
"""
