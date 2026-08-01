(() => {
  'use strict';

  const REQUIRED_ROUTES = [
    'dashboard',
    'operations',
    'simulator',
    'improvement',
    'finance',
    'github',
    'foundry',
    'appPlatform'
  ];

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const random = (min, max) => min + Math.random() * (max - min);
  const escapeHtml = value => String(value ?? '').replace(
    /[&<>"']/g,
    character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]
  );
  const normalizeText = value => String(value ?? '').replace(/\s/g, '').toLowerCase();
  const locale = (() => {
    try {
      return Intl.getCanonicalLocales(document.documentElement.lang || 'ko-KR')[0] || 'ko-KR';
    } catch {
      return 'ko-KR';
    }
  })();
  const formatNumber = (value, decimals = 0) => Number(value).toLocaleString(
    locale,
    { minimumFractionDigits: decimals, maximumFractionDigits: decimals }
  );
  const isKorean = locale.toLowerCase().startsWith('ko');
  const uiText = isKorean
    ? {
        invalidSpec: '데모 사양을 불러올 수 없습니다.',
        details: '상세 정보',
        demoData: '시연 데이터',
        live: '실시간',
        demoPrediction: '시연 예측',
        businessDecisions: '비즈니스 의사결정',
        platformEvidence: '플랫폼 근거',
        journey: '임원 관점',
        nextScene: '다음 장면',
        finalAction: '다음 실행',
        businessOutcome: '가능해지는 사업 성과',
        businessKpis: '사업 KPI',
        differentiation: '차별화 기능',
        controlEvidence: '통제 증거',
        buyerNextStep: '구매 다음 단계',
        owner: '담당',
        timebox: '기간',
        successCriteria: '성공 기준',
        scenario: '공통 시나리오',
        assessmentPending: 'readiness 진단을 실행하면 미해결 Gap이 표시됩니다.',
        brandSubtitle: customer => `${customer} AI 통합 운영`,
        executiveName: customer => `${customer} 임원`,
        ready: appName => `${appName} 준비 완료`
      }
    : {
        invalidSpec: 'Invalid demo specification.',
        details: 'Details',
        demoData: 'DEMO DATA',
        live: 'LIVE',
        demoPrediction: 'DEMO PREDICTION',
        businessDecisions: 'BUSINESS DECISIONS',
        platformEvidence: 'PLATFORM EVIDENCE',
        journey: 'Executive lens',
        nextScene: 'Next scene',
        finalAction: 'Next action',
        businessOutcome: 'Enabled business outcome',
        businessKpis: 'Business KPIs',
        differentiation: 'Differentiated capabilities',
        controlEvidence: 'Control evidence',
        buyerNextStep: 'Buyer next step',
        owner: 'Owner',
        timebox: 'Timebox',
        successCriteria: 'Success criteria',
        scenario: 'Shared scenario',
        assessmentPending: 'Run the readiness assessment to reveal unresolved gaps.',
        brandSubtitle: customer => `${customer} AI Operations`,
        executiveName: customer => `${customer} Executive`,
        ready: appName => `${appName} ready`
      };

  let spec;
  try {
    spec = JSON.parse($('#demo-spec').textContent);
  } catch (error) {
    console.error('Invalid demo spec JSON', error);
    document.body.innerHTML = `<main style="padding:32px;font-family:sans-serif">${uiText.invalidSpec}</main>`;
    return;
  }

  // The Golden Runtime owns layout and safe defaults. Specs may override only
  // validated brand/accent tokens that were inlined by the renderer.
  document.body.dataset.theme = 'dark-dimmed';
  document.body.dataset.density = 'executive';

  const meta = spec.meta;
  const routeScope = spec.story.routeScope || REQUIRED_ROUTES;
  const routeById = Object.fromEntries(spec.navigation.map(route => [route.id, route]));
  const navigation = spec.navigation.filter(route => routeScope.includes(route.id));
  const guidedJourneys = spec.story.guidedJourneys;
  let currentJourney = guidedJourneys.find(journey => journey.id === spec.story.defaultJourneyId) || guidedJourneys[0];
  const viewTimers = [];
  const viewCleanups = [];
  let sparkSequence = 0;

  function addTimer(timer) {
    viewTimers.push(timer);
    return timer;
  }

  function addCleanup(cleanup) {
    viewCleanups.push(cleanup);
    return cleanup;
  }

  function clearViewLifecycle() {
    viewTimers.splice(0).forEach(timer => {
      clearInterval(timer);
      clearTimeout(timer);
    });
    viewCleanups.splice(0).forEach(cleanup => {
      try {
        cleanup();
      } catch (error) {
        console.error('View cleanup failed', error);
      }
    });
  }

  function semanticColor(name) {
    const semantic = new Set(['brand', 'accent', 'info', 'success', 'warning', 'danger', 'violet']);
    if (semantic.has(name)) return `var(--${name})`;
    return 'var(--brand)';
  }

  function toneClass(tone) {
    return {
      success: 'ok',
      warning: 'warn',
      danger: 'bad',
      info: 'info',
      violet: 'violet',
      ok: 'ok',
      warn: 'warn',
      bad: 'bad'
    }[tone] || 'info';
  }

  function toast(title, subtitle, icon = '✦') {
    const host = $('#toasts');
    if (!host) return;
    const element = document.createElement('div');
    element.className = 'toast';
    element.innerHTML = `
      <div class="toast-icon">${escapeHtml(icon)}</div>
      <div>
        <div class="toast-title">${escapeHtml(title)}</div>
        <div class="toast-sub">${escapeHtml(subtitle)}</div>
      </div>`;
    host.appendChild(element);
    setTimeout(() => {
      element.classList.add('out');
      setTimeout(() => element.remove(), 380);
    }, 4200);
  }

  function statusBadge(status) {
    if (!status) return '';
    const value = typeof status === 'string' ? { label: status, tone: 'info' } : status;
    return `<span class="badge ${toneClass(value.tone)}">${escapeHtml(value.label)}</span>`;
  }

  function heroHtml(hero, actionHtml = '') {
    return `
      <div class="hero">
        <div class="hero-icon">${escapeHtml(hero.icon || '✦')}</div>
        <div>
          <div class="hero-title">${escapeHtml(hero.title)}</div>
          <div class="hero-subtitle">${escapeHtml(hero.subtitle)}</div>
        </div>
        <div class="hero-action">${hero.badge ? statusBadge(hero.badge) : ''}${actionHtml}</div>
      </div>`;
  }

  function sparkline(values, color = 'var(--brand)') {
    const data = values.length > 1 ? values : [0, 1];
    const id = `spark-${++sparkSequence}`;
    const width = 94;
    const height = 42;
    const minimum = Math.min(...data);
    const maximum = Math.max(...data);
    const range = maximum - minimum || 1;
    const points = data.map((value, index) => [
      index / (data.length - 1) * width,
      height - 3 - ((value - minimum) / range) * (height - 7)
    ]);
    const path = points.map(
      (point, index) => `${index ? 'L' : 'M'}${point[0].toFixed(1)},${point[1].toFixed(1)}`
    ).join(' ');
    return `
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <defs>
          <linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="${color}"/>
            <stop offset="1" stop-color="${color}" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path d="${path} L${width},${height} L0,${height} Z" fill="url(#${id})" opacity=".22"/>
        <path d="${path}" fill="none" stroke="${color}" stroke-width="2"/>
      </svg>`;
  }

  function kpiHtml(kpi, routeId, index) {
    const color = semanticColor(kpi.color);
    const direction = kpi.direction === 'down' ? 'down' : kpi.direction === 'warning' ? 'warning-text' : 'up';
    return `
      <div class="panel kpi">
        <div class="kpi-label"><span class="kpi-icon">${escapeHtml(kpi.icon)}</span>${escapeHtml(kpi.label)}</div>
        <div class="kpi-value" id="kpi-${routeId}-${index}" data-value="${Number(kpi.value)}">
          ${formatNumber(kpi.value, kpi.decimals || 0)}${kpi.unit ? ` <small>${escapeHtml(kpi.unit)}</small>` : ''}
        </div>
        <div class="kpi-delta ${direction}">${escapeHtml(kpi.delta)}</div>
        <div class="sparkline">${sparkline(kpi.series || [1, 2, 3, 4], color)}</div>
      </div>`;
  }

  function kpiGridHtml(kpis, routeId) {
    return `<div class="grid kpi-grid">${kpis.map((kpi, index) => kpiHtml(kpi, routeId, index)).join('')}</div>`;
  }

  function lineChart(values, color = 'var(--brand)', width = 760, height = 230) {
    const data = values.length > 1 ? values : [0, 1];
    const minimum = Math.min(...data) - 0.4;
    const maximum = Math.max(...data) + 0.4;
    const range = maximum - minimum || 1;
    const points = data.map((value, index) => [
      24 + index / (data.length - 1) * (width - 48),
      height - 25 - ((value - minimum) / range) * (height - 52)
    ]);
    const path = points.map(
      (point, index) => `${index ? 'L' : 'M'}${point[0].toFixed(1)},${point[1].toFixed(1)}`
    ).join(' ');
    const grid = [0.2, 0.4, 0.6, 0.8].map(value => {
      const y = (20 + value * (height - 42)).toFixed(1);
      return `<line x1="24" x2="${width - 24}" y1="${y}" y2="${y}" stroke="var(--line-soft)" stroke-dasharray="4 6"/>`;
    }).join('');
    const last = points[points.length - 1];
    return `
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        ${grid}
        <path d="${path} L${width - 24},${height - 22} L24,${height - 22} Z" fill="color-mix(in srgb,${color} 13%,transparent)"/>
        <path d="${path}" fill="none" stroke="${color}" stroke-width="3" stroke-linejoin="round"/>
        <circle cx="${last[0]}" cy="${last[1]}" r="5" fill="${color}">
          <animate attributeName="r" values="4;8;4" dur="1.8s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/>
        </circle>
      </svg>`;
  }

  function tableHtml(table, id) {
    const headers = (table.headers || []).map(header => `<th>${escapeHtml(header)}</th>`).join('');
    const rows = (table.rows || []).map(row => {
      const cells = (row.cells || []).map((cell, index) => `<td>${index === 0 ? `<strong>${escapeHtml(cell)}</strong>` : escapeHtml(cell)}</td>`).join('');
      return `
        <tr class="click-row" data-title="${escapeHtml(row.detailTitle || row.cells?.[0] || '')}"
            data-detail="${escapeHtml(row.detail || '')}" data-icon="${escapeHtml(row.icon || '◇')}">
          ${cells}${row.status ? `<td>${statusBadge(row.status)}</td>` : ''}
        </tr>`;
    }).join('');
    return `<table class="data-table" id="${id}"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
  }

  function bindDetailRows(selector) {
    $$(selector).forEach(row => {
      row.onclick = () => toast(
        row.dataset.title || uiText.details,
        row.dataset.detail || meta.demoNote,
        row.dataset.icon || '◇'
      );
    });
  }

  function executiveValueHtml(routeId, sales) {
    return `
      <div class="executive-value" id="executiveValue-${escapeHtml(routeId)}">
        <div>
          <div class="executive-question">${escapeHtml(sales.executiveQuestion)}</div>
          <div class="executive-outcome">${escapeHtml(sales.enabledBusinessOutcome)}
            <span>${uiText.businessOutcome}</span>
          </div>
        </div>
        <div class="business-kpis">
          ${sales.businessKpis.map(kpi => `
            <div class="business-kpi" data-title="${escapeHtml(kpi.label)}" data-detail="${escapeHtml(kpi.detail)}">
              <div class="business-kpi-label">${escapeHtml(kpi.label)}</div>
              <div class="business-kpi-value">${escapeHtml(kpi.value)}</div>
            </div>`).join('')}
        </div>
        <button class="button" id="buyerNext-${escapeHtml(routeId)}" type="button">${escapeHtml(sales.buyerNextStep.action)}</button>
      </div>`;
  }

  function salesEvidenceHtml(routeId, sales) {
    return `
      <details class="panel sales-evidence" id="salesEvidence-${escapeHtml(routeId)}">
        <summary>${uiText.differentiation} · ${uiText.controlEvidence}</summary>
        <div class="capability-grid">
          ${sales.differentiatedCapabilities.map(capability => `
            <div class="capability-card" data-title="${escapeHtml(capability.title)}" data-detail="${escapeHtml(capability.detail)}">
              <b>${escapeHtml(capability.title)}</b><span>${escapeHtml(capability.detail)}</span>
            </div>`).join('')}
        </div>
        <table class="data-table">
          <thead><tr>
            <th>${isKorean ? '서비스' : 'Service'}</th>
            <th>${isKorean ? '통제' : 'Control'}</th>
            <th>${isKorean ? '증거' : 'Evidence'}</th>
            <th>${isKorean ? '상태' : 'Status'}</th>
          </tr></thead>
          <tbody>
            ${sales.controlEvidence.map(item => `
              <tr class="sales-control-row" data-title="${escapeHtml(item.service)}" data-detail="${escapeHtml(item.evidence)}">
                <td><strong>${escapeHtml(item.service)}</strong></td>
                <td>${escapeHtml(item.control)}</td>
                <td>${escapeHtml(item.evidence)}</td>
                <td>${statusBadge(item.status)}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </details>`;
  }

  function bindSalesContract(routeId, sales) {
    $$('.business-kpi').forEach(card => {
      card.onclick = () => toast(card.dataset.title, card.dataset.detail, '₩');
    });
    $$('.capability-card').forEach(card => {
      card.onclick = () => toast(card.dataset.title, card.dataset.detail, '✦');
    });
    $$('.sales-control-row').forEach(row => {
      row.onclick = () => toast(row.dataset.title, row.dataset.detail, '⬡');
    });
    const buyerButton = $(`#buyerNext-${routeId}`);
    if (buyerButton) {
      buyerButton.onclick = () => toast(
        sales.buyerNextStep.action,
        `${uiText.owner}: ${sales.buyerNextStep.owner} · ${uiText.timebox}: ${sales.buyerNextStep.timebox} · ${uiText.successCriteria}: ${sales.buyerNextStep.successCriteria}`,
        '→'
      );
    }
  }

  function scenarioTraceHtml(routeId) {
    const scenario = spec.story.scenarioTrace;
    return `
      <div class="scenario-trace" id="scenarioTrace">
        <div class="scenario-trace-head">
          <div><span class="scenario-id">${escapeHtml(scenario.id)}</span><div class="scenario-title">${escapeHtml(scenario.title)}</div></div>
          <span class="hint">${uiText.scenario}</span>
        </div>
        <div class="scenario-steps">
          ${scenario.steps.map(step => `
            <div class="scenario-step ${step.route === routeId ? 'active' : ''}" data-route="${escapeHtml(step.route)}">
              <b>${escapeHtml(step.label)}</b>
              <span>${escapeHtml(step.owner)} · ${escapeHtml(step.timestamp)}</span>
              ${statusBadge(step.status)}
            </div>`).join('')}
        </div>
      </div>`;
  }

  function businessScenarioTraceHtml(routeId) {
    return spec.story.scenarioTrace.steps[0].route === routeId
      ? scenarioTraceHtml(routeId)
      : '';
  }

  function bindScenarioTrace() {
    $$('.scenario-step').forEach(step => {
      step.onclick = () => {
        location.hash = step.dataset.route;
      };
    });
  }

  function updateKpiTicks(routeId, kpis) {
    kpis.forEach((kpi, index) => {
      if (!kpi.tick) return;
      const element = $(`#kpi-${routeId}-${index}`);
      if (!element) return;
      const current = Number(element.dataset.value);
      const next = current + random(kpi.tick.min, kpi.tick.max);
      const bounded = clamp(
        next,
        kpi.tick.floor ?? -Number.MAX_SAFE_INTEGER,
        kpi.tick.ceiling ?? Number.MAX_SAFE_INTEGER
      );
      element.dataset.value = String(bounded);
      element.innerHTML = `${formatNumber(bounded, kpi.decimals || 0)}${kpi.unit ? ` <small>${escapeHtml(kpi.unit)}</small>` : ''}`;
    });
  }

  function renderDashboard() {
    const data = spec.dashboard;
    return {
      html: `
        ${heroHtml(
          data.hero,
          `<button class="button" id="dashPrimaryAction" type="button">${escapeHtml(data.primaryAction.label)}</button>`
        )}
        ${businessScenarioTraceHtml('dashboard')}
        ${kpiGridHtml(data.kpis, 'dashboard')}
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head">
              <h3>${escapeHtml(data.stream.title)}</h3>
              <div class="chart-legend"><span><i class="legend-dot" style="background:var(--brand)"></i>${escapeHtml(data.stream.label)}</span></div>
            </div>
            <div class="chart-box" id="dashChart"></div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.feedTitle)}</h3><span class="hint">${escapeHtml(data.feedHint)}</span></div>
            <div class="feed" id="dashFeed"></div>
          </div>
        </div>
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.cards.title)}</h3><span class="hint">${escapeHtml(data.cards.hint)}</span></div>
            <div class="detail-cards">
              ${data.cards.items.map(item => `
                <div class="detail-card" data-title="${escapeHtml(item.name)}" data-detail="${escapeHtml(item.detail)}">
                  <div class="detail-card-top"><span class="detail-card-name">${escapeHtml(item.name)}</span><span class="dot-live"></span></div>
                  <div class="detail-card-value">${escapeHtml(item.value)}</div>
                  <div class="detail-card-sub">${escapeHtml(item.sub)}</div>
                </div>`).join('')}
            </div>
            <div class="assumption">${escapeHtml(meta.demoNote)}</div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.table.title)}</h3><span class="hint">${escapeHtml(data.table.hint)}</span></div>
            ${tableHtml(data.table, 'dashTable')}
          </div>
        </div>`,
      init() {
        let streamValues = [...data.stream.values];
        const drawChart = () => {
          const chart = $('#dashChart');
          if (chart) chart.innerHTML = lineChart(streamValues, semanticColor(data.stream.color || 'brand'));
        };
        const feedItems = [...data.feed];
        const renderFeed = () => {
          const host = $('#dashFeed');
          if (!host) return;
          host.innerHTML = feedItems.slice(0, 6).map((item, index) => `
            <div class="feed-item" data-index="${index}">
              <div class="feed-icon">${escapeHtml(item.icon)}</div>
              <div>
                <div class="feed-title">${escapeHtml(item.title)} · ${escapeHtml(item.text)}</div>
                <div class="feed-meta">${index === 0 ? (isKorean ? '방금 전' : 'Just now') : (isKorean ? `${index * 3}분 전` : `${index * 3} min ago`)} · ${uiText.demoData}</div>
              </div>
            </div>`).join('');
          $$('#dashFeed .feed-item').forEach((element, index) => {
            element.onclick = () => toast(feedItems[index].title, feedItems[index].text, feedItems[index].icon);
          });
        };
        drawChart();
        renderFeed();
        addTimer(setInterval(() => {
          const last = streamValues[streamValues.length - 1];
          streamValues.push(clamp(
            last + random(data.stream.tick.min, data.stream.tick.max),
            data.stream.min,
            data.stream.max
          ));
          streamValues.shift();
          drawChart();
          updateKpiTicks('dashboard', data.kpis);
          const learningValue = $('#learningValue');
          const meter = $('#learningMeter');
          if (learningValue) {
            const current = Number(learningValue.dataset.value || data.learningLoop.value);
            const next = current + Math.max(1, Math.floor(random(1, 4)));
            learningValue.dataset.value = String(next);
            learningValue.textContent = `${formatNumber(next)} ${data.learningLoop.unit || ''}`.trim();
            if (meter) meter.style.width = `${clamp(68 + (next - data.learningLoop.value) / 80, 68, 94)}%`;
          }
        }, data.stream.intervalMs || 1900));
        addTimer(setInterval(() => {
          feedItems.unshift(feedItems.pop());
          renderFeed();
        }, data.feedIntervalMs || 3600));
        bindScenarioTrace();
        bindDetailRows('#dashTable .click-row');
        $$('.detail-card').forEach(card => {
          card.onclick = () => toast(card.dataset.title, card.dataset.detail, '✦');
        });
        $('#dashPrimaryAction').onclick = () => {
          toast(data.primaryAction.toastTitle, data.primaryAction.toastText, data.primaryAction.icon || '→');
          location.hash = data.primaryAction.targetRoute;
        };
      }
    };
  }

  function operationFlowSvg(nodes) {
    const width = 1000;
    const start = 90;
    const end = 910;
    const positions = nodes.map((_, index) => start + index / Math.max(1, nodes.length - 1) * (end - start));
    const nodeWidth = clamp(620 / nodes.length, 94, 126);
    return `
      <svg id="opsFlow" viewBox="0 0 ${width} 330" preserveAspectRatio="none">
        <defs>
          <linearGradient id="runtime-rail" x1="0" x2="1">
            <stop offset="0" stop-color="var(--brand)"/>
            <stop offset="1" stop-color="var(--info)"/>
          </linearGradient>
        </defs>
        <line x1="${start}" x2="${end}" y1="142" y2="142" stroke="url(#runtime-rail)" stroke-width="10" stroke-linecap="round" opacity=".42"/>
        <line x1="${start}" x2="${end}" y1="159" y2="159" stroke="var(--line)" stroke-width="2" stroke-dasharray="7 10"/>
        ${nodes.map((node, index) => `
          <g>
            <rect x="${positions[index] - nodeWidth / 2}" y="75" width="${nodeWidth}" height="67" rx="13" fill="var(--surface-strong)" stroke="${index === 1 ? 'var(--brand)' : 'var(--line)'}"/>
            <text x="${positions[index]}" y="101" text-anchor="middle" fill="var(--ink)" font-size="15" font-weight="800">${escapeHtml(node.name)}</text>
            <text x="${positions[index]}" y="122" text-anchor="middle" fill="var(--ink-faint)" font-size="10">${escapeHtml(node.subtitle || '')}</text>
            <circle cx="${positions[index] + nodeWidth / 2 - 16}" cy="89" r="5" fill="var(--success)">
              <animate attributeName="opacity" values="1;.35;1" dur="${1.4 + index * .22}s" repeatCount="indefinite"/>
            </circle>
          </g>`).join('')}
        <path d="M${positions[1] || start} 230 C400 295 610 295 ${positions[positions.length - 2] || end} 230" fill="none" stroke="color-mix(in srgb,var(--accent) 35%,transparent)" stroke-width="2" stroke-dasharray="6 7"/>
        <circle r="6" fill="var(--accent)">
          <animateMotion dur="3.6s" repeatCount="indefinite" path="M${positions[1] || start} 230 C400 295 610 295 ${positions[positions.length - 2] || end} 230"/>
        </circle>
      </svg>`;
  }

  function renderOperations() {
    const data = spec.operations;
    return {
      html: `
        ${heroHtml(
          data.hero,
          `<button class="button" id="reopt" type="button">${escapeHtml(data.action.button)}</button>`
        )}
        ${businessScenarioTraceHtml('operations')}
        ${kpiGridHtml(data.kpis, 'operations')}
        <div class="grid grid-2 space-top" style="grid-template-columns:1.45fr .75fr">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.flow.title)}</h3><span class="hint">${escapeHtml(data.flow.hint)}</span></div>
            <div class="flow-stage">
              ${operationFlowSvg(data.flow.nodes)}
              <div class="flow-mover" id="flowMover">${escapeHtml(data.flow.moverLabel || uiText.live)}</div>
              <div class="flow-event" id="flowEvent">${escapeHtml(data.flow.events[0])}</div>
            </div>
            <div class="node-cards">
              ${data.flow.nodes.map(node => `
                <div class="node-card" data-title="${escapeHtml(node.name)}" data-detail="${escapeHtml(node.detail)}">
                  <div class="node-name">${escapeHtml(node.name)}</div>
                  <div class="node-metric">${escapeHtml(node.metric)}</div>
                  <div class="node-status">${escapeHtml(node.status)}</div>
                </div>`).join('')}
            </div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.table.title)}</h3><span class="hint">${escapeHtml(data.table.hint)}</span></div>
            ${tableHtml(data.table, 'opsTable')}
            <div class="divider"></div>
            <div class="section-label">${escapeHtml(data.action.recommendationLabel)}</div>
            <div class="explanation" id="opsRecommendation">${data.action.recommendationBefore}</div>
            <div class="assumption">${escapeHtml(meta.demoNote)}</div>
          </div>
        </div>`,
      init() {
        let position = 0;
        let direction = 1;
        addTimer(setInterval(() => {
          position += 0.012 * direction;
          if (position >= 1) {
            position = 1;
            direction = -1;
          } else if (position <= 0) {
            position = 0;
            direction = 1;
          }
          const mover = $('#flowMover');
          const event = $('#flowEvent');
          if (!mover || !event) return;
          mover.style.left = `${7 + position * 84}%`;
          const eventIndex = Math.min(data.flow.events.length - 1, Math.floor(position * data.flow.events.length));
          event.textContent = data.flow.events[eventIndex];
        }, 90));
        addTimer(setInterval(() => updateKpiTicks('operations', data.kpis), 2100));
        const actionButton = $('#reopt');
        actionButton.onclick = () => {
          actionButton.disabled = true;
          actionButton.textContent = data.action.running;
          const event = $('#flowEvent');
          if (event) event.textContent = data.action.runningEvent;
          addTimer(setTimeout(() => {
            Object.entries(data.action.kpiUpdates || {}).forEach(([index, value]) => {
              const kpi = data.kpis[Number(index)];
              const element = $(`#kpi-operations-${index}`);
              if (!element || !kpi) return;
              element.dataset.value = String(value);
              element.innerHTML = `${formatNumber(value, kpi.decimals || 0)}${kpi.unit ? ` <small>${escapeHtml(kpi.unit)}</small>` : ''}`;
            });
            const recommendation = $('#opsRecommendation');
            if (recommendation) recommendation.innerHTML = data.action.recommendationAfter;
            const currentEvent = $('#flowEvent');
            if (currentEvent) currentEvent.textContent = data.action.completeEvent;
            if (actionButton) {
              actionButton.disabled = false;
              actionButton.textContent = data.action.complete;
            }
            toast(data.action.toastTitle, data.action.toastText, data.action.toastIcon || '◎');
          }, data.action.durationMs || 1100));
        };
        bindDetailRows('#opsTable .click-row');
        bindScenarioTrace();
        $$('.node-card').forEach(card => {
          card.onclick = () => toast(card.dataset.title, card.dataset.detail, '◇');
        });
      }
    };
  }

  function renderSimulator() {
    const data = spec.simulator;
    return {
      html: `
        ${heroHtml(data.hero)}
        ${businessScenarioTraceHtml('simulator')}
        <div class="grid grid-2">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.inputsTitle)}</h3><span class="hint">${escapeHtml(data.inputsHint)}</span></div>
            <div id="simInputs">
              ${data.inputs.map(input => `
                <div class="slider-row">
                  <div class="slider-label"><span>${escapeHtml(input.label)}</span><b id="sim-label-${escapeHtml(input.id)}"></b></div>
                  <input id="sim-input-${escapeHtml(input.id)}" type="range"
                         min="${Number(input.min)}" max="${Number(input.max)}" step="${Number(input.step || 1)}" value="${Number(input.value)}">
                </div>`).join('')}
            </div>
            <div class="explanation" id="simExplanation"></div>
            <div class="assumption">${escapeHtml(data.assumption || meta.demoNote)}</div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.output.label)}</h3><span class="badge ok" id="simRiskBadge"></span></div>
            <div class="gauge-wrap" id="simGauge">
              <svg viewBox="0 0 236 145">
                <path d="M32 120 A86 86 0 0 1 204 120" fill="none" stroke="var(--line)" stroke-width="17" stroke-linecap="round" pathLength="100"/>
                <path id="simGaugeValue" d="M32 120 A86 86 0 0 1 204 120" fill="none" stroke="var(--success)" stroke-width="17" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="12"/>
              </svg>
              <div class="gauge-center">
                <div class="gauge-value" id="simValue"></div>
                <div class="gauge-label">${uiText.demoPrediction}</div>
              </div>
            </div>
            <div class="mini-stats" id="simSecondary"></div>
          </div>
        </div>
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.histogram.title)}</h3><span class="hint">${escapeHtml(data.histogram.hint)}</span></div>
            <div class="chart-box" id="simHistogram"></div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.history.title)}</h3><span class="hint">${escapeHtml(data.history.hint)}</span></div>
            ${tableHtml(data.history, 'simHistoryTable')}
          </div>
        </div>`,
      init() {
        const initialValues = Object.fromEntries(data.inputs.map(input => [input.id, Number(input.value)]));

        function currentValues() {
          return Object.fromEntries(data.inputs.map(input => [
            input.id,
            Number($(`#sim-input-${input.id}`).value)
          ]));
        }

        function outputValue(values) {
          const penalty = data.inputs.reduce(
            (sum, input) => sum + Math.abs(values[input.id] - input.optimum) * input.weight,
            0
          );
          return clamp(data.output.base - penalty, data.output.min, data.output.max);
        }

        function recommendation(values) {
          for (const rule of data.recommendations || []) {
            if (rule.operator === 'default') return rule.message;
            const value = values[rule.inputId];
            if (rule.operator === '>' && value > rule.threshold) return rule.message;
            if (rule.operator === '<' && value < rule.threshold) return rule.message;
            const input = data.inputs.find(item => item.id === rule.inputId);
            if (rule.operator === 'abs>' && input && Math.abs(value - input.optimum) > rule.threshold) return rule.message;
          }
          return data.defaultRecommendation;
        }

        function renderHistogram(values) {
          const first = data.inputs[0];
          const shift = (values[first.id] - first.optimum) / Math.max(1, first.max - first.min) * 8;
          const bins = Array.from({ length: 17 }, (_, index) => (
            Math.exp(-Math.pow((index - 8 - shift) / 3.1, 2)) * 78 + random(0, 7)
          ));
          const maximum = Math.max(...bins);
          const chart = $('#simHistogram');
          if (!chart) return;
          chart.innerHTML = `
            <svg viewBox="0 0 700 230" preserveAspectRatio="none">
              ${bins.map((value, index) => {
                const barHeight = value / maximum * 170;
                const color = index < 3 || index > 13 ? 'var(--danger)' : index < 5 || index > 11 ? 'var(--warning)' : 'var(--brand)';
                return `<rect x="${24 + index * 39}" y="${195 - barHeight}" width="27" height="${barHeight}" rx="4" fill="${color}" opacity="${0.48 + index * 0.02}"/>`;
              }).join('')}
              <line x1="20" x2="680" y1="196" y2="196" stroke="var(--line)"/>
              <text x="25" y="218" fill="var(--ink-faint)" font-size="11">${escapeHtml(data.histogram.leftLabel)}</text>
              <text x="328" y="218" fill="var(--ink-faint)" font-size="11">${escapeHtml(data.histogram.centerLabel)}</text>
              <text x="626" y="218" fill="var(--ink-faint)" font-size="11">${escapeHtml(data.histogram.rightLabel)}</text>
            </svg>`;
        }

        function update() {
          const values = currentValues();
          data.inputs.forEach(input => {
            const label = $(`#sim-label-${input.id}`);
            if (label) label.textContent = `${formatNumber(values[input.id], input.decimals || 0)}${input.unit}`;
          });
          const output = outputValue(values);
          const outputElement = $('#simValue');
          if (outputElement) outputElement.textContent = `${formatNumber(output, data.output.decimals || 0)}${data.output.unit}`;
          const normalized = clamp((output - data.output.min) / Math.max(0.001, data.output.max - data.output.min), 0, 1);
          const gauge = $('#simGaugeValue');
          if (gauge) {
            gauge.style.strokeDashoffset = String(100 - normalized * 100);
            gauge.style.stroke = output >= data.output.goodThreshold ? 'var(--success)' : output >= data.output.warningThreshold ? 'var(--warning)' : 'var(--danger)';
          }
          const badge = $('#simRiskBadge');
          if (badge) {
            if (output >= data.output.goodThreshold) {
              badge.className = 'badge ok';
              badge.textContent = data.output.goodLabel;
            } else if (output >= data.output.warningThreshold) {
              badge.className = 'badge warn';
              badge.textContent = data.output.warningLabel;
            } else {
              badge.className = 'badge bad';
              badge.textContent = data.output.dangerLabel;
            }
          }
          const secondary = $('#simSecondary');
          if (secondary) {
            secondary.innerHTML = data.secondary.map(metric => {
              const delta = Object.entries(metric.weights || {}).reduce(
                (sum, [inputId, weight]) => sum + (values[inputId] - initialValues[inputId]) * weight,
                0
              );
              const value = metric.base + delta;
              return `
                <div class="mini-stat">
                  <div class="mini-stat-label">${escapeHtml(metric.label)}</div>
                  <div class="mini-stat-value">${formatNumber(value, metric.decimals || 0)}${escapeHtml(metric.unit || '')}</div>
                </div>`;
            }).join('');
          }
          const explanation = $('#simExplanation');
          if (explanation) explanation.innerHTML = recommendation(values);
          renderHistogram(values);
        }

        data.inputs.forEach(input => {
          const element = $(`#sim-input-${input.id}`);
          element.oninput = update;
        });
        update();
        bindScenarioTrace();
        bindDetailRows('#simHistoryTable .click-row');
      }
    };
  }

  function renderImprovement() {
    const data = spec.improvement;
    return {
      html: `
        ${heroHtml(
          data.hero,
          `<button class="button" id="runAnalysis" type="button">${escapeHtml(data.action.button)}</button>`
        )}
        ${businessScenarioTraceHtml('improvement')}
        ${kpiGridHtml(data.kpis, 'improvement')}
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.stepsTitle)}</h3><span class="hint">${escapeHtml(data.stepsHint)}</span></div>
            <div class="steps" id="analysisSteps">
              ${data.steps.map((step, index) => `
                <div class="step">
                  <div class="step-index">${index + 1}</div>
                  <div class="step-copy"><b>${escapeHtml(step.title)}</b><span>${escapeHtml(step.text)}</span></div>
                </div>`).join('')}
            </div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.factorsTitle)}</h3><span class="hint">${escapeHtml(data.factorsHint)}</span></div>
            <div class="bars" id="factorBars">
              ${data.factors.map(factor => `
                <div class="bar">
                  <div class="bar-name">${escapeHtml(factor.label)}</div>
                  <div class="bar-track"><div class="bar-fill" data-width="${Number(factor.width)}" style="background:${semanticColor(factor.color)}"></div></div>
                  <div class="bar-value">${escapeHtml(factor.value)}</div>
                </div>`).join('')}
            </div>
            <div class="divider"></div>
            <div class="explanation" id="analysisSummary">${data.action.summaryBefore}</div>
          </div>
        </div>
        <div class="panel space-top">
          <div class="panel-head"><h3>${escapeHtml(data.impactsTitle)}</h3><span class="hint">${escapeHtml(data.impactsHint)}</span></div>
          <div class="impact-grid">
            ${data.impacts.map(impact => `
              <div class="impact-card" data-title="${escapeHtml(impact.label)}" data-detail="${escapeHtml(impact.detail)}">
                <div class="impact-label">${escapeHtml(impact.label)}</div>
                <div class="impact-value">${escapeHtml(impact.value)}</div>
                <div class="impact-sub">${escapeHtml(impact.sub)}</div>
              </div>`).join('')}
          </div>
        </div>
        <div class="panel space-top">
          <div class="panel-head"><h3>${escapeHtml(data.board.title)}</h3><span class="hint">${escapeHtml(data.board.hint)}</span></div>
          <div class="board" id="improvementBoard">
            ${data.board.columns.map(column => `
              <div class="board-column">
                <div class="board-head"><span>${escapeHtml(column.name)}</span><span>${column.items.length}</span></div>
                ${column.items.map(item => `
                  <div class="board-card" data-title="${escapeHtml(item.title)}" data-detail="${escapeHtml(item.detail)}">${escapeHtml(item.text)}</div>`).join('')}
              </div>`).join('')}
          </div>
        </div>`,
      init() {
        const button = $('#runAnalysis');
        const execute = () => {
          if (!button) return;
          button.disabled = true;
          button.textContent = data.action.running;
          $$('#analysisSteps .step').forEach(step => step.classList.remove('visible'));
          $$('#factorBars .bar-fill').forEach(bar => {
            bar.style.width = '0';
          });
          $$('#analysisSteps .step').forEach((step, index) => {
            addTimer(setTimeout(() => {
              if (step.isConnected) step.classList.add('visible');
            }, 180 + index * 250));
          });
          addTimer(setTimeout(() => {
            $$('#factorBars .bar-fill').forEach((bar, index) => {
              addTimer(setTimeout(() => {
                if (bar.isConnected) bar.style.width = `${bar.dataset.width}%`;
              }, index * 100));
            });
            const summary = $('#analysisSummary');
            if (summary) summary.innerHTML = data.action.summaryAfter;
            if (button) {
              button.disabled = false;
              button.textContent = data.action.complete;
            }
            toast(data.action.toastTitle, data.action.toastText, data.action.toastIcon || '◎');
          }, data.action.durationMs || 1800));
        };
        button.onclick = execute;
        if (data.action.autoRun !== false) addTimer(setTimeout(() => {
          const current = $('#runAnalysis');
          if (current) current.click();
        }, 480));
        bindScenarioTrace();
        $$('.impact-card').forEach(card => {
          card.onclick = () => toast(card.dataset.title, card.dataset.detail, '◎');
        });
        $$('#improvementBoard .board-card').forEach(card => {
          card.onclick = () => toast(card.dataset.title, card.dataset.detail, '▤');
        });
      }
    };
  }

  function renderFinance() {
    const data = spec.finance;
    return {
      html: `
        ${heroHtml(data.hero)}
        ${businessScenarioTraceHtml('finance')}
        <div class="grid grid-2">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.leversTitle)}</h3><span class="hint">${escapeHtml(data.leversHint)}</span></div>
            <div id="financeLevers">
              ${data.levers.map(lever => `
                <div class="slider-row">
                  <div class="slider-label"><span>${escapeHtml(lever.label)}</span><b id="finance-label-${escapeHtml(lever.id)}"></b></div>
                  <input id="finance-input-${escapeHtml(lever.id)}" type="range"
                         min="${Number(lever.min)}" max="${Number(lever.max)}" step="${Number(lever.step || 1)}" value="${Number(lever.value)}">
                </div>`).join('')}
            </div>
            <div class="explanation" id="financeExplanation">${data.explanation}</div>
            <div class="assumption">${escapeHtml(data.assumption || meta.demoNote)}</div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.margin.label)}</h3><span class="badge info" id="marginBadge"></span></div>
            <div class="big-number">
              <div class="big-number-value" id="marginValue"></div>
              <div class="big-number-label">${escapeHtml(data.margin.note)}</div>
            </div>
            <div class="mini-stats" id="financeSummary"></div>
          </div>
        </div>
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.composition.title)}</h3><span class="hint">${escapeHtml(data.composition.hint)}</span></div>
            <div class="donut-wrap">
              <div class="donut">
                <svg id="valueDonut" viewBox="0 0 120 120"></svg>
                <div class="donut-center"><b id="donutCenter"></b><span>${escapeHtml(data.composition.centerLabel)}</span></div>
              </div>
              <div class="donut-legend">
                ${data.composition.segments.map(segment => `
                  <div class="donut-legend-row"><i style="background:${semanticColor(segment.color)}"></i>${escapeHtml(segment.label)}</div>`).join('')}
              </div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.watchlist.title)}</h3><span class="hint">${escapeHtml(data.watchlist.hint)}</span></div>
            ${tableHtml(data.watchlist, 'financeTable')}
          </div>
        </div>`,
      init() {
        const initial = Object.fromEntries(data.levers.map(lever => [lever.id, Number(lever.value)]));
        const currentValues = () => Object.fromEntries(data.levers.map(lever => [
          lever.id,
          Number($(`#finance-input-${lever.id}`).value)
        ]));

        function weightedValue(base, impacts, values) {
          return base + Object.entries(impacts || {}).reduce(
            (sum, [leverId, impact]) => sum + (values[leverId] - initial[leverId]) * impact,
            0
          );
        }

        function update() {
          const values = currentValues();
          data.levers.forEach(lever => {
            const label = $(`#finance-label-${lever.id}`);
            if (label) label.textContent = `${formatNumber(values[lever.id], lever.decimals || 0)}${lever.unit}`;
          });
          const margin = weightedValue(data.margin.base, data.margin.impacts, values);
          $('#marginValue').textContent = `${formatNumber(margin, data.margin.decimals || 0)}${data.margin.unit}`;
          const marginBadge = $('#marginBadge');
          if (margin >= data.margin.goodThreshold) {
            marginBadge.className = 'badge ok';
            marginBadge.textContent = data.margin.goodLabel;
          } else if (margin >= data.margin.warningThreshold) {
            marginBadge.className = 'badge info';
            marginBadge.textContent = data.margin.warningLabel;
          } else {
            marginBadge.className = 'badge warn';
            marginBadge.textContent = data.margin.lowLabel;
          }
          $('#financeSummary').innerHTML = data.summaryMetrics.map(metric => `
            <div class="mini-stat">
              <div class="mini-stat-label">${escapeHtml(metric.label)}</div>
              <div class="mini-stat-value">${formatNumber(weightedValue(metric.base, metric.impacts, values), metric.decimals || 0)}${escapeHtml(metric.unit)}</div>
            </div>`).join('');

          const rawSegments = data.composition.segments.map(segment => Math.max(
            0.1,
            weightedValue(segment.base, segment.impacts, values)
          ));
          const total = rawSegments.reduce((sum, value) => sum + value, 0);
          const percentages = rawSegments.map(value => value / total * 100);
          let offset = 0;
          $('#valueDonut').innerHTML = `
            <circle cx="60" cy="60" r="45" fill="none" stroke="var(--line-soft)" stroke-width="15"/>
            ${percentages.map((value, index) => {
              const segment = data.composition.segments[index];
              const circle = `<circle cx="60" cy="60" r="45" fill="none" stroke="${semanticColor(segment.color)}" stroke-width="15" pathLength="100" stroke-dasharray="${value} ${100 - value}" stroke-dashoffset="${-offset}"/>`;
              offset += value;
              return circle;
            }).join('')}`;
          const centerSegment = percentages[data.composition.centerSegment ?? 1] || percentages[0];
          $('#donutCenter').textContent = `${Math.round(centerSegment)}%`;
          const explanation = $('#financeExplanation');
          if (explanation) explanation.innerHTML = data.explanation.replace(
            '{{value}}',
            formatNumber(margin, data.margin.decimals || 0) + escapeHtml(data.margin.unit)
          );
        }

        data.levers.forEach(lever => {
          $(`#finance-input-${lever.id}`).oninput = update;
        });
        update();
        bindScenarioTrace();
        bindDetailRows('#financeTable .click-row');
      }
    };
  }

  function diffHtml(lines) {
    return lines.map((line, index) => {
      const type = { add: 'add', delete: 'delete', comment: 'comment', keyword: 'keyword' }[line.type] || '';
      return `<span class="line-number">${String(index + 1).padStart(2, '0')}</span><span class="${type}">${escapeHtml(line.text)}</span>`;
    }).join('\n');
  }

  function renderGitHub() {
    const data = spec.github;
    return {
      html: `
        ${heroHtml(
          data.hero,
          `<button class="button info" id="assignIssue" type="button">${escapeHtml(data.action.button)}</button>`
        )}
        ${executiveValueHtml('github', data.sales)}
        ${scenarioTraceHtml('github')}
        ${kpiGridHtml(data.kpis, 'github')}
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3 id="diffTitle"></h3><span class="badge info" id="prStatus"></span></div>
            <div class="code" id="codeDiff"></div>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.stepsTitle)}</h3><span class="hint">${escapeHtml(data.stepsHint)}</span></div>
            <div class="steps" id="devSteps">
              ${data.steps.map((step, index) => `
                <div class="step">
                  <div class="step-index">${index + 1}</div>
                  <div class="step-copy"><b>${escapeHtml(step.title)}</b><span>${escapeHtml(step.text)}</span></div>
                </div>`).join('')}
            </div>
            <div class="pr-card">
              <div class="pr-card-top"><span class="pr-title" id="prTitle"></span><span class="badge warn" id="prGate"></span></div>
              <div class="pr-sub" id="prSub"></div>
            </div>
          </div>
        </div>
        <div class="panel space-top">
          <div class="panel-head"><h3>${escapeHtml(data.issuesTitle)}</h3><span class="hint">${escapeHtml(data.issuesHint)}</span></div>
          <table class="data-table" id="issueTable">
            <thead><tr>${data.issueHeaders.map(header => `<th>${escapeHtml(header)}</th>`).join('')}</tr></thead>
            <tbody>
              ${data.issues.map((issue, index) => `
                <tr class="click-row ${index === 0 ? 'selected' : ''}" data-index="${index}">
                  <td><strong>${escapeHtml(issue.id)} ${escapeHtml(issue.title)}</strong></td>
                  <td>${escapeHtml(issue.product)}</td>
                  <td>${escapeHtml(issue.type)}</td>
                  <td>${escapeHtml(issue.risk)}</td>
                  <td>${statusBadge(issue.status)}</td>
                </tr>`).join('')}
            </tbody>
          </table>
          <div class="assumption">${escapeHtml(data.assumption || meta.demoNote)}</div>
        </div>
        ${salesEvidenceHtml('github', data.sales)}`,
      init() {
        let currentIndex = 0;
        const button = $('#assignIssue');

        function selectIssue(index) {
          currentIndex = index;
          const issue = data.issues[index];
          $$('#issueTable tbody tr').forEach((row, rowIndex) => row.classList.toggle('selected', rowIndex === index));
          $('#diffTitle').textContent = `${issue.id} · ${issue.title}`;
          $('#codeDiff').innerHTML = diffHtml(issue.diffLines);
          $('#prStatus').className = `badge ${issue.highRisk ? 'warn' : 'info'}`;
          $('#prStatus').textContent = issue.highRisk ? data.action.humanLedLabel : data.action.readyLabel;
          $('#prTitle').textContent = data.action.notCreated;
          $('#prGate').className = 'badge warn';
          $('#prGate').textContent = issue.highRisk ? data.action.humanRequired : data.action.awaiting;
          $('#prSub').textContent = issue.context;
          $$('#devSteps .step').forEach(step => step.classList.remove('visible'));
        }

        $$('#issueTable tbody tr').forEach(row => {
          row.onclick = () => {
            const index = Number(row.dataset.index);
            selectIssue(index);
            toast(data.issues[index].id, data.issues[index].title, '⌘');
          };
        });
        bindSalesContract('github', data.sales);
        bindScenarioTrace();
        selectIssue(0);

        button.onclick = () => {
          const issue = data.issues[currentIndex];
          button.disabled = true;
          button.textContent = data.action.running;
          $$('#devSteps .step').forEach(step => step.classList.remove('visible'));
          $('#prStatus').className = 'badge violet';
          $('#prStatus').textContent = data.action.agentRunning;
          $('#prGate').className = 'badge info';
          $('#prGate').textContent = data.action.policyChecks;
          $$('#devSteps .step').forEach((step, index) => {
            addTimer(setTimeout(() => {
              if (step.isConnected) step.classList.add('visible');
            }, 180 + index * 400));
          });
          addTimer(setTimeout(() => {
            $('#prTitle').textContent = issue.highRisk
              ? data.action.planReady.replace('{{issue}}', issue.id)
              : data.action.prReady.replace('{{number}}', String(data.action.prBase + currentIndex)).replace('{{title}}', issue.title);
            $('#prGate').className = `badge ${issue.highRisk ? 'warn' : 'ok'}`;
            $('#prGate').textContent = issue.highRisk ? data.action.humanImplementation : data.action.checksPassed;
            $('#prSub').textContent = issue.highRisk ? data.action.humanResult : data.action.prResult;
            $('#prStatus').className = 'badge ok';
            $('#prStatus').textContent = issue.highRisk ? data.action.planStatus : data.action.prStatus;
            if (button) {
              button.disabled = false;
              button.textContent = data.action.complete;
            }
            toast(
              issue.highRisk ? data.action.humanToastTitle : data.action.prToastTitle,
              issue.highRisk ? data.action.humanToastText : data.action.prToastText,
              '⌘'
            );
          }, data.action.durationMs || 2500));
        };
      }
    };
  }

  function orchestrationPositions(count) {
    return Array.from({ length: count }, (_, index) => {
      const angle = -Math.PI / 2 + index * (Math.PI * 2 / count);
      return {
        left: 50 + Math.cos(angle) * 34,
        top: 50 + Math.sin(angle) * 36
      };
    });
  }

  function renderFoundry() {
    const data = spec.foundry;
    const positions = orchestrationPositions(data.profiles.length);
    const lines = positions.map(position => (
      `<line x1="150" y1="114" x2="${position.left * 3}" y2="${position.top * 2.28}"/>`
    )).join('');
    return {
      html: `
        ${heroHtml(data.hero)}
        ${executiveValueHtml('foundry', data.sales)}
        ${scenarioTraceHtml('foundry')}
        <div class="decision-preview">
          <div class="decision-preview-title">${escapeHtml(data.decisionPreviewTitle)}</div>
          <div class="message-body">${data.orchestration.summary}</div>
        </div>
        ${kpiGridHtml(data.kpis, 'foundry')}
        <div class="agent-layout">
          <div class="stack">
            <div class="panel">
              <div class="panel-head"><h3>${escapeHtml(data.listTitle)}</h3><span class="hint">${escapeHtml(data.listHint)}</span></div>
              <div class="agent-list" id="agentList"></div>
            </div>
            <div class="panel">
              <div class="panel-head"><h3>${escapeHtml(data.orchestration.title)}</h3><button class="button small" id="orchRun" type="button">${escapeHtml(data.orchestration.button)}</button></div>
              <div class="orchestration-flow" id="orchestrationFlow">
                <svg viewBox="0 0 300 228" preserveAspectRatio="none">
                  <g stroke="color-mix(in srgb,var(--brand) 24%,transparent)" stroke-width="1.5" stroke-dasharray="5 6">${lines}</g>
                  <circle class="flow-pulse" r="4">
                    <animateMotion dur="2.8s" repeatCount="indefinite" path="M150 114 ${positions.map(position => `L${position.left * 3} ${position.top * 2.28} L150 114`).join(' ')}"/>
                  </circle>
                </svg>
                <div class="flow-node core" style="left:50%;top:50%" data-node="core">
                  <div class="flow-node-box">✦</div><div class="flow-node-label">${escapeHtml(data.orchestration.coreLabel)}</div>
                </div>
                ${data.profiles.map((profile, index) => `
                  <div class="flow-node" style="left:${positions[index].left}%;top:${positions[index].top}%" data-node="${index}">
                    <div class="flow-node-box">${escapeHtml(profile.icon)}</div>
                    <div class="flow-node-label">${escapeHtml(profile.shortName || profile.name)}</div>
                  </div>`).join('')}
              </div>
            </div>
          </div>
          <div class="panel chat-panel">
            <div class="chat-head">
              <div><div class="chat-title" id="chatTitle"></div><div class="chat-meta" id="chatMeta"></div></div>
              <span class="badge ok"><span class="dot-live"></span>${escapeHtml(data.governedLabel)}</span>
            </div>
            <div class="chat-log" id="chatLog"></div>
            <div class="chips" id="chips"></div>
            <div class="composer">
              <input id="chatInput" placeholder="${escapeHtml(data.placeholder)}">
              <button class="button" id="sendBtn" type="button">${escapeHtml(data.sendLabel)}</button>
            </div>
          </div>
        </div>
        ${salesEvidenceHtml('foundry', data.sales)}`,
      init() {
        let current = 0;
        let conversationVersion = 0;
        const log = $('#chatLog');
        const orchestrationButton = $('#orchRun');

        function bubble(role, html, icon) {
          if (!log || !log.isConnected) return null;
          const element = document.createElement('div');
          element.className = `message ${role}`;
          element.innerHTML = `
            <div class="message-avatar">${role === 'assistant' ? escapeHtml(icon || data.profiles[current].icon) : escapeHtml(meta.initials)}</div>
            <div class="message-body">${html}</div>`;
          log.appendChild(element);
          log.scrollTop = log.scrollHeight;
          return element;
        }

        function typing(icon) {
          if (!log || !log.isConnected) return null;
          const element = document.createElement('div');
          element.className = 'message assistant typing';
          element.innerHTML = `<div class="message-avatar">${escapeHtml(icon)}</div><div class="message-body"><span></span><span></span><span></span></div>`;
          log.appendChild(element);
          log.scrollTop = log.scrollHeight;
          return element;
        }

        function answerFor(question, agentIndex) {
          const normalized = normalizeText(question);
          for (const item of data.profiles[agentIndex].qa) {
            const candidate = normalizeText(item.question);
            if (normalized.includes(candidate) || candidate.includes(normalized)) return item.answer;
          }
          for (const profile of data.profiles) {
            for (const item of profile.qa) {
              if (normalized.includes(normalizeText(item.question))) return item.answer;
            }
          }
          return data.fallback.replace('{{agent}}', escapeHtml(data.profiles[agentIndex].name));
        }

        function ask(question) {
          bubble('user', escapeHtml(question), meta.initials);
          const originAgent = current;
          const originVersion = conversationVersion;
          const icon = data.profiles[originAgent].icon;
          const answer = answerFor(question, originAgent);
          const pending = typing(icon);
          addTimer(setTimeout(() => {
            if (pending && pending.isConnected) pending.remove();
            if (conversationVersion !== originVersion || current !== originAgent) return;
            bubble('assistant', answer, icon);
          }, 650 + random(0, 380)));
        }

        function renderChips() {
          const host = $('#chips');
          if (!host) return;
          host.innerHTML = data.profiles[current].qa.map(item => (
            `<button class="chip" type="button">${escapeHtml(item.question)}</button>`
          )).join('');
          $$('#chips .chip').forEach(chip => {
            chip.onclick = () => ask(chip.textContent);
          });
        }

        function renderList() {
          const host = $('#agentList');
          if (!host) return;
          host.innerHTML = data.profiles.map((profile, index) => `
            <div class="agent-row ${index === current ? 'active' : ''}" data-index="${index}">
              <div class="agent-icon">${escapeHtml(profile.icon)}</div>
              <div style="flex:1"><div class="agent-name">${escapeHtml(profile.name)}</div><div class="agent-sub">${escapeHtml(profile.subtitle)}</div></div>
              <span class="dot-live"></span>
            </div>`).join('');
          $$('#agentList .agent-row').forEach(row => {
            row.onclick = () => selectAgent(Number(row.dataset.index));
          });
        }

        function selectAgent(index) {
          conversationVersion += 1;
          current = index;
          renderList();
          $('#chatTitle').textContent = data.profiles[index].name;
          $('#chatMeta').textContent = data.profiles[index].subtitle;
          if (log) log.innerHTML = '';
          bubble('assistant', data.profiles[index].intro, data.profiles[index].icon);
          renderChips();
          if (orchestrationButton) {
            orchestrationButton.disabled = false;
            orchestrationButton.textContent = data.orchestration.button;
          }
        }

        renderList();
        selectAgent(0);
        bindSalesContract('foundry', data.sales);
        bindScenarioTrace();
        $('#sendBtn').onclick = () => {
          const input = $('#chatInput');
          const value = input.value.trim();
          if (!value) return;
          ask(value);
          input.value = '';
        };
        $('#chatInput').onkeydown = event => {
          if (event.key === 'Enter') $('#sendBtn').click();
        };

        orchestrationButton.onclick = () => {
          const orchestrationVersion = ++conversationVersion;
          orchestrationButton.disabled = true;
          orchestrationButton.textContent = data.orchestration.running;
          if (log) log.innerHTML = '';
          bubble('assistant', data.orchestration.intro, '✦');
          data.orchestration.stages.forEach((stage, index) => {
            addTimer(setTimeout(() => {
              if (conversationVersion !== orchestrationVersion) return;
              $$('.flow-node').forEach(node => node.classList.remove('hot'));
              const node = $(`.flow-node[data-node="${stage.agentIndex}"]`);
              if (node) node.classList.add('hot');
              bubble('assistant', `<b>${escapeHtml(stage.name)}</b> · ${escapeHtml(stage.text)}`, stage.icon);
            }, 520 + index * 520));
          });
          addTimer(setTimeout(() => {
            if (conversationVersion !== orchestrationVersion) return;
            $$('.flow-node').forEach(node => node.classList.remove('hot'));
            const core = $('.flow-node[data-node="core"]');
            if (core) core.classList.add('hot');
            bubble('assistant', data.orchestration.summary, '✦');
            if (orchestrationButton) {
              orchestrationButton.disabled = false;
              orchestrationButton.textContent = data.orchestration.complete;
            }
            toast(data.orchestration.toastTitle, data.orchestration.toastText, '✦');
          }, 800 + data.orchestration.stages.length * 520));
        };
      }
    };
  }

  function renderAppPlatform() {
    const data = spec.appPlatform;
    return {
      html: `
        ${heroHtml(
          data.hero,
          `<div class="evaluation-actions">
             <button class="button violet" id="evalRun" type="button">${escapeHtml(data.evaluation.button)}</button>
             <button class="button info" id="planRemediation" type="button">${escapeHtml(data.evaluation.planButton)}</button>
           </div>`
        )}
        ${executiveValueHtml('appPlatform', data.sales)}
        ${scenarioTraceHtml('appPlatform')}
        <div class="grid adaptive-grid">
          ${data.cards.map((card, index) => `
            <div class="platform-card" data-title="${escapeHtml(card.title)}" data-detail="${escapeHtml(card.detail)}">
              <div class="platform-icon">${escapeHtml(card.icon)}</div>
              <div class="platform-title">${escapeHtml(card.title)}</div>
              <div class="platform-value" ${index === 0 ? 'id="evalScore"' : ''}>${escapeHtml(card.value)}</div>
              <div class="platform-sub">${escapeHtml(card.sub)}</div>
            </div>`).join('')}
        </div>
        <div class="grid grid-2 space-top">
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.controls.title)}</h3><span class="hint">${escapeHtml(data.controls.hint)}</span></div>
            ${tableHtml(data.controls, 'controlTable')}
          </div>
          <div class="panel">
            <div class="panel-head"><h3>${escapeHtml(data.evaluation.title)}</h3><span class="hint">${escapeHtml(data.evaluation.hint)}</span></div>
            <div class="projected-label" id="evalProjection"></div>
            <div class="projected-score" id="evalProjectedScore"></div>
            <div class="trace" id="evalTrace">${escapeHtml(data.evaluation.readyLines.join('\n'))}</div>
            <div class="gap-list" id="gapList"><div class="gap-meta">${uiText.assessmentPending}</div></div>
            <div class="divider"></div>
            <div class="section-label">${escapeHtml(data.memories.title)}</div>
            ${tableHtml(data.memories, 'memoryTable')}
          </div>
        </div>
        <div class="panel space-top">
          <div class="panel-head"><h3>${escapeHtml(data.learningLoop.title)}</h3><span class="hint">${escapeHtml(data.learningLoop.hint)}</span></div>
          <div class="sovereignty">
            ${data.learningLoop.steps.map(step => `
              <div class="sovereignty-step" data-title="${escapeHtml(step.title)}" data-detail="${escapeHtml(step.detail)}">
                <div class="sovereignty-icon">${escapeHtml(step.icon)}</div>
                <div class="sovereignty-title">${escapeHtml(step.title)}</div>
                <div class="sovereignty-sub">${escapeHtml(step.sub)}</div>
              </div>`).join('')}
          </div>
          <div class="assumption">${escapeHtml(data.assumption || meta.demoNote)}</div>
        </div>
        ${salesEvidenceHtml('appPlatform', data.sales)}`,
      init() {
        let assessed = false;
        let phase = 'idle';
        let phaseVersion = 0;
        $$('.platform-card').forEach(card => {
          card.onclick = () => toast(card.dataset.title, card.dataset.detail, '⬡');
        });
        bindDetailRows('#controlTable .click-row');
        bindDetailRows('#memoryTable .click-row');
        bindSalesContract('appPlatform', data.sales);
        bindScenarioTrace();
        $$('.sovereignty-step').forEach(step => {
          step.onclick = () => toast(step.dataset.title, step.dataset.detail, '✦');
        });
        const button = $('#evalRun');
        const planButton = $('#planRemediation');
        const setActionState = disabled => {
          button.disabled = disabled;
          planButton.disabled = disabled;
        };
        const resetAssessment = () => {
          const score = $('#evalScore');
          const projection = $('#evalProjection');
          const projectedScore = $('#evalProjectedScore');
          const gapList = $('#gapList');
          if (score) score.textContent = String(data.evaluation.initialScore);
          if (projection) projection.textContent = '';
          if (projectedScore) projectedScore.textContent = '';
          if (gapList) gapList.innerHTML = `<div class="gap-meta">${uiText.assessmentPending}</div>`;
        };
        const renderGaps = () => {
          const gapList = $('#gapList');
          if (!gapList) return;
          gapList.innerHTML = data.evaluation.gaps.map(gap => `
            <div class="gap-item">
              <div><b>${escapeHtml(gap.title)}</b><div class="gap-meta">${escapeHtml(gap.detail)}</div></div>
              <div class="gap-meta">${escapeHtml(gap.owner)} · ${escapeHtml(gap.effort)}</div>
              ${statusBadge(gap.status)}
            </div>`).join('');
        };
        button.onclick = () => {
          if (phase === 'assessing' || phase === 'planning') return;
          phase = 'assessing';
          assessed = false;
          const version = ++phaseVersion;
          setActionState(true);
          button.textContent = data.evaluation.running;
          planButton.textContent = data.evaluation.planButton;
          resetAssessment();
          const trace = $('#evalTrace');
          if (trace) trace.textContent = '';
          data.evaluation.runLines.forEach((line, index) => {
            addTimer(setTimeout(() => {
              if (phaseVersion !== version) return;
              const currentTrace = $('#evalTrace');
              if (currentTrace) currentTrace.textContent += `${index ? '\n' : ''}${line}`;
            }, index * 250));
          });
          addTimer(setTimeout(() => {
            if (phaseVersion !== version) return;
            assessed = true;
            phase = 'assessed';
            renderGaps();
            if (button) {
              button.textContent = data.evaluation.complete;
            }
            setActionState(false);
            toast(data.evaluation.toastTitle, data.evaluation.toastText, '⬡');
          }, data.evaluation.runLines.length * 250 + 200));
        };
        planButton.onclick = () => {
          if (!assessed) {
            toast(data.evaluation.planBlockedTitle, data.evaluation.planBlockedText, '◇');
            return;
          }
          if (phase === 'assessing' || phase === 'planning') return;
          phase = 'planning';
          const version = ++phaseVersion;
          setActionState(true);
          planButton.textContent = data.evaluation.planning;
          const trace = $('#evalTrace');
          if (trace) trace.textContent = '';
          data.evaluation.remediationLines.forEach((line, index) => {
            addTimer(setTimeout(() => {
              if (phaseVersion !== version) return;
              const currentTrace = $('#evalTrace');
              if (currentTrace) currentTrace.textContent += `${index ? '\n' : ''}${line}`;
            }, index * 250));
          });
          addTimer(setTimeout(() => {
            if (phaseVersion !== version) return;
            phase = 'projected';
            const projection = $('#evalProjection');
            const projectedScore = $('#evalProjectedScore');
            if (projection) projection.textContent = data.evaluation.projectedLabel;
            if (projectedScore) projectedScore.textContent = String(data.evaluation.finalScore);
            if (planButton) {
              planButton.textContent = data.evaluation.planComplete;
            }
            button.textContent = data.evaluation.button;
            setActionState(false);
            toast(data.evaluation.planToastTitle, data.evaluation.planToastText, '✦');
          }, data.evaluation.remediationLines.length * 250 + 200));
        };
      }
    };
  }

  const VIEWS = {
    dashboard: renderDashboard,
    operations: renderOperations,
    simulator: renderSimulator,
    improvement: renderImprovement,
    finance: renderFinance,
    github: renderGitHub,
    foundry: renderFoundry,
    appPlatform: renderAppPlatform
  };

  function updateJourneyChrome(routeId) {
    const bridge = $('#journeyBridge');
    const path = $('#journeyPath');
    const nextButton = $('#nextScene');
    const index = currentJourney.routes.indexOf(routeId);
    path.innerHTML = currentJourney.routes.map(journeyRoute => `
      <button class="journey-path-step ${journeyRoute === routeId ? 'active' : ''}"
              type="button" data-route="${escapeHtml(journeyRoute)}">
        ${escapeHtml(routeById[journeyRoute].name)}
      </button>`).join('');
    $$('#journeyPath .journey-path-step').forEach(step => {
      step.onclick = () => {
        location.hash = step.dataset.route;
      };
    });
    if (index < 0) {
      bridge.textContent = spec.story.frame;
      nextButton.textContent = `${uiText.nextScene}: ${routeById[currentJourney.routes[0]].name}`;
      nextButton.onclick = () => {
        location.hash = currentJourney.routes[0];
      };
      return;
    }
    const nextRoute = currentJourney.routes[index + 1];
    if (nextRoute) {
      bridge.textContent = currentJourney.bridges[index];
      nextButton.textContent = `${uiText.nextScene}: ${routeById[nextRoute].name}`;
      nextButton.onclick = () => {
        location.hash = nextRoute;
      };
      return;
    }
    bridge.textContent = `${currentJourney.finalAction.action} · ${currentJourney.finalAction.successCriteria}`;
    nextButton.textContent = `${uiText.finalAction}: ${currentJourney.finalAction.action}`;
    nextButton.onclick = () => toast(
      currentJourney.finalAction.action,
      `${uiText.owner}: ${currentJourney.finalAction.owner} · ${uiText.timebox}: ${currentJourney.finalAction.timebox} · ${uiText.successCriteria}: ${currentJourney.finalAction.successCriteria}`,
      '→'
    );
  }

  function setupShell() {
    $('#brandMark').textContent = meta.initials;
    $('#brandName').textContent = meta.appName;
    $('#brandSub').textContent = uiText.brandSubtitle(meta.customer);
    $('#sideAvatar').textContent = meta.initials;
    $('#sideUserName').textContent = uiText.executiveName(meta.customer);
    $('#infraLabel').textContent = meta.infrastructureLabel;
    $('#learningLabel').textContent = spec.dashboard.learningLoop.label;
    $('#learningValue').textContent = `${formatNumber(spec.dashboard.learningLoop.value)} ${spec.dashboard.learningLoop.unit || ''}`.trim();
    $('#learningValue').dataset.value = String(spec.dashboard.learningLoop.value);
    $('#learningNote').textContent = spec.dashboard.learningLoop.note;
    const navLink = route => `
      <a data-route="${escapeHtml(route.id)}">
        <span class="nav-icon">${escapeHtml(route.icon)}</span>
        <span class="nav-name">${escapeHtml(route.name)}</span>
        <span class="nav-short">${escapeHtml(route.short)}</span>
      </a>`;
    const businessNavigation = navigation.filter(route => REQUIRED_ROUTES.slice(0, 5).includes(route.id));
    const platformNavigation = navigation.filter(route => REQUIRED_ROUTES.slice(5).includes(route.id));
    $('#nav').innerHTML = `
      <div class="nav-group-label">${uiText.businessDecisions}</div>
      ${businessNavigation.map(navLink).join('')}
      <div class="nav-group-label platform">${uiText.platformEvidence}</div>
      ${platformNavigation.map(navLink).join('')}`;
    $$('#nav a').forEach(link => {
      link.onclick = () => {
        location.hash = link.dataset.route;
      };
    });
    $('#journeyLabel').textContent = uiText.journey;
    const renderJourneyTabs = () => {
      $('#journeyTabs').innerHTML = guidedJourneys.map(journey => `
        <button class="journey-tab ${journey.id === currentJourney.id ? 'active' : ''}"
                type="button" role="tab" aria-selected="${journey.id === currentJourney.id}"
                data-journey="${escapeHtml(journey.id)}" title="${escapeHtml(journey.label)}">
          ${escapeHtml(journey.audience)}
        </button>`).join('');
      $$('#journeyTabs .journey-tab').forEach(tab => {
        tab.onclick = () => {
          currentJourney = guidedJourneys.find(journey => journey.id === tab.dataset.journey) || guidedJourneys[0];
          renderJourneyTabs();
          const target = currentJourney.routes[1] || currentJourney.routes[0];
          if (location.hash.slice(1) === target) navigate();
          else location.hash = target;
        };
      });
    };
    renderJourneyTabs();
  }

  function navigate() {
    const requested = location.hash.slice(1) || 'dashboard';
    const routeId = routeScope.includes(requested) ? requested : 'dashboard';
    const route = routeById[routeId];
    clearViewLifecycle();
    $$('#nav a').forEach(link => link.classList.toggle('active', link.dataset.route === routeId));
    $('#topTitle').textContent = route.name;
    $('#topCrumb').textContent = `${meta.appName} · ${route.crumb || route.short}`;
    updateJourneyChrome(routeId);
    const view = VIEWS[routeId]();
    const host = $('#view');
    host.innerHTML = `<div class="view-enter">${view.html}</div>`;
    host.scrollTop = 0;
    if (view.init) view.init();
  }

  setupShell();
  window.addEventListener('hashchange', navigate);
  window.addEventListener('beforeunload', clearViewLifecycle);

  setInterval(() => {
    const clock = $('#clock');
    if (clock) clock.textContent = new Date().toLocaleTimeString(locale, { hour12: false });
  }, 1000);

  const ambient = spec.ambientNotifications || [];
  if (ambient.length) {
    setInterval(() => {
      const item = ambient[Math.floor(random(0, ambient.length))];
      toast(item.title, item.text, item.icon);
    }, spec.ambientIntervalMs || 11500);
  }
  setTimeout(() => toast(
    uiText.ready(meta.appName),
    meta.demoNote,
    meta.initials
  ), 1700);

  $('#notificationButton').onclick = () => {
    $('#notificationCount').style.display = 'none';
    toast(spec.notification.title, spec.notification.text, spec.notification.icon || '◇');
  };

  navigate();
})();
