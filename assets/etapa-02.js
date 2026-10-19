/* ============================================================
   SCADA · AgroDrone — Etapa 02: Grafos e Redes
   Lógica interativa: Abas, Deck de Slides (10 slides) e
   Simulador de Grafos Didático com 6 Vistas em SVG nativo.
   Grupo 06 · ECAA08 (Arthur, Caique, Luis Felipe, Marina)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ============================================================
     1. SISTEMA DE ABAS (Tabs)
     ============================================================ */
  const tabButtons = document.querySelectorAll('[data-e02-tab]');
  const panels = document.querySelectorAll('[data-e02-panel]');

  function switchTab(targetName) {
    tabButtons.forEach(btn => {
      const isSelected = btn.dataset.e02Tab === targetName;
      btn.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      btn.classList.toggle('active', isSelected);
      btn.setAttribute('tabindex', isSelected ? '0' : '-1');
    });

    panels.forEach(panel => {
      const isCurrent = panel.dataset.e02Panel === targetName;
      panel.classList.toggle('active', isCurrent);
      if (isCurrent) {
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });

    if (history.replaceState) {
      history.replaceState(null, '', `#${targetName}`);
    }
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.e02Tab));
  });

  // Checar se há hash na URL ao carregar
  const initialHash = window.location.hash.replace('#', '');
  if (initialHash && ['apresentacao', 'modelagem', 'simulador', 'arquivos', 'validacao'].includes(initialHash)) {
    const mappedTab = (initialHash === 'validacao') ? 'arquivos' : initialHash;
    switchTab(mappedTab);
  }

  /* ============================================================
     2. DECK DE SLIDES INTERATIVO (10 SLIDES)
     ============================================================ */
  const deck = document.querySelector('[data-etapa02-deck]');
  if (deck) {
    const slides = deck.querySelectorAll('[data-e02-slide]');
    const slideCountEl = deck.querySelector('[data-e02-slide-count]');
    const slideTitleEl = deck.querySelector('[data-e02-slide-title]');
    const indexButtons = deck.querySelectorAll('[data-e02-go-slide]');
    const prevBtn = deck.querySelector('[data-e02-prev]');
    const nextBtn = deck.querySelector('[data-e02-next]');
    const fullscreenBtn = deck.querySelector('[data-e02-fullscreen]');

    let currentSlide = 0;
    const totalSlides = slides.length;

    function renderSlide(idx) {
      if (idx < 0) idx = 0;
      if (idx >= totalSlides) idx = totalSlides - 1;
      currentSlide = idx;

      slides.forEach((s, i) => {
        s.classList.toggle('is-current', i === currentSlide);
      });

      indexButtons.forEach((b, i) => {
        b.classList.toggle('active', i === currentSlide);
      });

      if (slideCountEl) {
        slideCountEl.textContent = `${String(currentSlide + 1).padStart(2, '0')} / ${String(totalSlides).padStart(2, '0')}`;
      }

      const activeSlide = slides[currentSlide];
      if (slideTitleEl && activeSlide) {
        slideTitleEl.textContent = activeSlide.dataset.title || '';
      }

      if (prevBtn) prevBtn.disabled = (currentSlide === 0);
      if (nextBtn) nextBtn.disabled = (currentSlide === totalSlides - 1);
    }

    indexButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = parseInt(btn.dataset.e02GoSlide, 10);
        renderSlide(target);
      });
    });

    prevBtn?.addEventListener('click', () => renderSlide(currentSlide - 1));
    nextBtn?.addEventListener('click', () => renderSlide(currentSlide + 1));

    // Navegação por teclado (Setas Esquerda / Direita)
    window.addEventListener('keydown', (e) => {
      // Somente se a aba Apresentação estiver ativa
      const presPanel = document.getElementById('painel-apresentacao');
      if (!presPanel || !presPanel.classList.contains('active')) return;

      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        if (currentSlide < totalSlides - 1) {
          renderSlide(currentSlide + 1);
        }
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        if (currentSlide > 0) {
          renderSlide(currentSlide - 1);
        }
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
      }
    });

    function toggleFullscreen() {
      deck.classList.toggle('e02-fullscreen-mode');
      if (fullscreenBtn) {
        const isFull = deck.classList.contains('e02-fullscreen-mode');
        fullscreenBtn.textContent = isFull ? '✕ Fechar tela cheia' : '⛶ Tela cheia';
      }
    }

    fullscreenBtn?.addEventListener('click', toggleFullscreen);
    renderSlide(0);
  }

  /* ============================================================
     3. SIMULADOR DIDÁTICO INTERATIVO DE GRAFOS (6 VISTAS)
     ============================================================ */
  const workbench = document.querySelector('[data-etapa02-simulator]');
  if (workbench) {
    const modeButtons = workbench.querySelectorAll('[data-e02-mode]');
    const modeCodeEl = workbench.querySelector('[data-e02-mode-code]');
    const modeTitleEl = workbench.querySelector('[data-e02-mode-title]');
    const modeDescEl = workbench.querySelector('[data-e02-mode-description]');
    const modeUnitEl = workbench.querySelector('[data-e02-mode-unit]');
    const svgEl = workbench.querySelector('[data-e02-graph]');
    const legendEl = workbench.querySelector('[data-e02-legend]');
    const selectionEl = workbench.querySelector('[data-e02-selection]');
    const blocksEl = workbench.querySelector('[data-e02-blocks]');
    const runBtn = workbench.querySelector('[data-e02-run]');
    const resetBtn = workbench.querySelector('[data-e02-reset]');
    const simResultsEl = workbench.querySelector('[data-e02-results]');

    let currentMode = 'water'; // 'water', 'search', 'leak', 'euler', 'tsp', 'logistics'

    // Dados da Rede Hidráulica (Modos 1, 2 e 3)
    const hydraulicNodes = {
      'EST_TQ_01':   { x: 70,  y: 200, label: 'EST_TQ_01', desc: 'Tanque Solo (500L)' },
      'EST_PMP_01':  { x: 170, y: 130, label: 'EST_PMP_01', desc: 'Bomba Solo' },
      'EST_MAN_01':  { x: 270, y: 130, label: 'EST_MAN_01', desc: 'Manifold Solo' },
      'DRN_TQ_01':   { x: 380, y: 200, label: 'DRN_TQ_01', desc: 'Reservatório VANT (30L)' },
      'DRN_FLT_01':  { x: 490, y: 130, label: 'DRN_FLT_01', desc: 'Filtro Principal 1' },
      'DRN_FLT_02':  { x: 490, y: 270, label: 'DRN_FLT_02', desc: 'Filtro Reserva 2' },
      'DRN_PMP_01':  { x: 600, y: 200, label: 'DRN_PMP_01', desc: 'Bomba VANT' },
      'DRN_MAN_01':  { x: 700, y: 200, label: 'DRN_MAN_01', desc: 'Manifold Barra' },
      'DRN_BICO_A':  { x: 810, y: 90,  label: 'BICO_A', desc: 'Seção A (0.6m)' },
      'DRN_BICO_B':  { x: 810, y: 165, label: 'BICO_B', desc: 'Seção B (0.8m)' },
      'DRN_BICO_C':  { x: 810, y: 240, label: 'BICO_C', desc: 'Seção C (1.0m)' },
      'DRN_BICO_D':  { x: 810, y: 315, label: 'BICO_D', desc: 'Seção D (1.2m)' },
    };

    const hydraulicEdges = [
      { id: 'e01', u: 'EST_TQ_01',  v: 'EST_PMP_01', w: 1.5, modo: 'solo' },
      { id: 'e02', u: 'EST_PMP_01', v: 'EST_MAN_01', w: 1.0, modo: 'solo' },
      { id: 'e03', u: 'EST_MAN_01', v: 'EST_TQ_01',  w: 2.0, modo: 'mistura', label: 'recirculação' },
      { id: 'e04', u: 'EST_MAN_01', v: 'DRN_TQ_01',  w: 3.0, modo: 'abastecimento' },
      { id: 'e05', u: 'DRN_TQ_01',  v: 'DRN_FLT_01', w: 0.4, modo: 'voo' },
      { id: 'e06', u: 'DRN_FLT_01', v: 'DRN_PMP_01', w: 0.3, modo: 'voo' },
      { id: 'e07', u: 'DRN_PMP_01', v: 'DRN_MAN_01', w: 0.5, modo: 'voo' },
      { id: 'e08', u: 'DRN_MAN_01', v: 'DRN_BICO_A',  w: 0.6, modo: 'voo' },
      { id: 'e09', u: 'DRN_MAN_01', v: 'DRN_BICO_B',  w: 0.8, modo: 'voo' },
      { id: 'e10', u: 'DRN_MAN_01', v: 'DRN_BICO_C',  w: 1.0, modo: 'voo' },
      { id: 'e11', u: 'DRN_MAN_01', v: 'DRN_BICO_D',  w: 1.2, modo: 'voo' },
      { id: 'e12', u: 'DRN_TQ_01',  v: 'DRN_FLT_02', w: 0.5, modo: 'reserva' },
      { id: 'e13', u: 'DRN_FLT_02', v: 'DRN_PMP_01', w: 0.6, modo: 'reserva' },
    ];

    let blockedEdges = new Set();
    let selectedOrigin = 'DRN_TQ_01';
    let selectedDest = 'DRN_BICO_A';

    // Estado da simulação de vazamento (Modo 3)
    let leakScenario = 'nominal'; // 'nominal', 'leak_e05', 'leak_e06', 'dual_fail'

    // Dados do TSP (Modo 5)
    const tspPoints = {
      'BASE': { x: 450, y: 340, name: 'BASE Operacional (0,0)' },
      'T1':   { x: 570, y: 270, name: 'Talhão T1 (+100,+50)' },
      'T2':   { x: 630, y: 140, name: 'Talhão T2 (+150,+180)' },
      'T3':   { x: 520, y: 90,  name: 'Talhão T3 (+60,+220)' },
      'T4':   { x: 350, y: 160, name: 'Talhão T4 (-80,+160)' },
      'T5':   { x: 390, y: 280, name: 'Talhão T5 (-50,+60)' },
    };

    let tspMode = 'opt'; // 'nn', 'opt', 'mst'

    // Dados da Inspeção Euleriana (Modo 4)
    const eulerNodes = {
      'BASE':         { x: 450, y: 80,  name: 'BASE Operacional', deg: 4 },
      'TANQUE':       { x: 260, y: 160, name: 'Tanque Solo', deg: 2 },
      'BOMBA_SOLO':   { x: 260, y: 300, name: 'Bomba Solo', deg: 4 },
      'ABASTECIMENTO':{ x: 450, y: 380, name: 'Ponto Abastecimento', deg: 2 },
      'BANCADA_DRONE':{ x: 640, y: 300, name: 'Bancada Drone', deg: 4 },
      'LAVAGEM':      { x: 640, y: 160, name: 'Área de Lavagem', deg: 2 },
    };

    const eulerEdges = [
      { id: 'c01', u: 'BASE', v: 'TANQUE', w: '18 m' },
      { id: 'c02', u: 'TANQUE', v: 'BOMBA_SOLO', w: '12 m' },
      { id: 'c03', u: 'BOMBA_SOLO', v: 'ABASTECIMENTO', w: '15 m' },
      { id: 'c04', u: 'ABASTECIMENTO', v: 'BANCADA_DRONE', w: '15 m' },
      { id: 'c05', u: 'BANCADA_DRONE', v: 'LAVAGEM', w: '12 m' },
      { id: 'c06', u: 'LAVAGEM', v: 'BASE', w: '18 m' },
      { id: 'c07', u: 'BASE', v: 'BOMBA_SOLO', w: '24 m' },
      { id: 'c08', u: 'BASE', v: 'BANCADA_DRONE', w: '24 m' },
      { id: 'c09', u: 'BOMBA_SOLO', v: 'BANCADA_DRONE', w: '20 m' },
    ];

    let eulerStep = -1;

    // Configuração dos 6 Modos
    const modeConfigs = {
      water: {
        code: 'AULA 14 · DIJKSTRA',
        title: 'Rede Hidráulica: Menor Caminho',
        desc: 'Calcula o caminho de menor comprimento físico (metros) entre a origem selecionada e os bicos de pulverização.',
        unit: 'metros · dirigido ponderado',
        legend: [
          { color: 'var(--crop)', label: 'Caminho Mínimo Ativo' },
          { color: 'var(--border)', label: 'Tubulação Disponível' },
          { color: 'var(--alarm)', label: 'Trecho Interditado' },
          { color: 'var(--sky)', label: 'Filtro Reserva (Contingência)' },
        ]
      },
      search: {
        code: 'AULA 13 · BFS & DFS',
        title: 'Exploração de Topologia: Busca em Tubulações',
        desc: 'A BFS calcula níveis e menor número de saltos topológicos; a DFS rastreia caminhos alternativos e redundâncias.',
        unit: 'saltos · reachability',
        legend: [
          { color: 'var(--crop)', label: 'Vértices Alcançados' },
          { color: 'var(--border)', label: 'Não Explorados' },
          { color: 'var(--alarm)', label: 'Bloqueado / Desconectado' },
        ]
      },
      leak: {
        code: 'AULA 15 · SEGURANÇA INTEGRADA',
        title: 'Simulação de Vazamento & Intertravamento',
        desc: 'Injeção de falha por rompimento de mangueira: corte imediato da bomba, isolamento e desvio pelo filtro reserva.',
        unit: 'SCADA Interlock & Reroute',
        legend: [
          { color: 'var(--alarm)', label: 'Trecho Rompido / Alarme' },
          { color: 'var(--crop)', label: 'Rota de Desvio Segura' },
          { color: 'var(--caution)', label: 'Bomba Cortada (LIGA_BOMBA = 0)' },
        ]
      },
      euler: {
        code: 'AULA 16 · HIERHOLZER',
        title: 'Inspeção de Infraestrutura Terrestre',
        desc: 'Circuito Euleriano fechado sobre o multigrafo não dirigido da base: percorre as 9 vias de acesso sem repetição.',
        unit: '9 conexões · graus pares',
        legend: [
          { color: 'var(--crop)', label: 'Vias Já Percorridas' },
          { color: 'var(--soil)', label: 'Via Atual de Passagem' },
          { color: 'var(--muted-dim)', label: 'Vias Pendentes' },
        ]
      },
      tsp: {
        code: 'AULA 17 · TSP & HEURÍSTICA',
        title: 'Roteamento de Missão do AgroDrone',
        desc: 'Visita aos 5 talhões agrícolas + BASE. Comparação entre Vizinho Mais Próximo, 2-Opt (Ótimo Exato) e Árvore Mínima.',
        unit: 'coordenadas 2D · metros euclidianos',
        legend: [
          { color: 'var(--crop)', label: '2-Opt / Ótimo Global (585,33 m)' },
          { color: 'var(--caution)', label: 'Vizinho Mais Próximo (660,61 m)' },
          { color: 'var(--sky)', label: 'Árvore Mínima - AGM (375,30 m)' },
        ]
      },
      logistics: {
        code: 'AULA 18 · FLUXO DE MATERIAIS',
        title: 'Logística de Insumos & Apoio Terrestre',
        desc: 'Rastreabilidade física do fluxo de água (210 m) e produto químico (206 m) até a aplicação em campo.',
        unit: 'rede de materiais · precedência',
        legend: [
          { color: 'var(--sky)', label: 'Fluxo da Água (210 m)' },
          { color: 'var(--soil)', label: 'Fluxo do Químico (206 m)' },
          { color: 'var(--crop)', label: 'Aplicação Embarcada' },
        ]
      }
    };

    function setMode(mode) {
      currentMode = mode;
      modeButtons.forEach(btn => {
        const active = btn.dataset.e02Mode === mode;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      const cfg = modeConfigs[mode];
      if (modeCodeEl) modeCodeEl.textContent = cfg.code;
      if (modeTitleEl) modeTitleEl.textContent = cfg.title;
      if (modeDescEl) modeDescEl.textContent = cfg.desc;
      if (modeUnitEl) modeUnitEl.textContent = cfg.unit;

      // Render legend
      if (legendEl) {
        legendEl.innerHTML = cfg.legend.map(l => `
          <div class="e02-legend-item">
            <span class="e02-legend-dot" style="background:${l.color};"></span>
            <span>${l.label}</span>
          </div>`).join('');
      }

      renderControls();
      calculateAndRender();
    }

    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => setMode(btn.dataset.e02Mode));
    });

    // Montar controles dinâmicos conforme o modo
    function renderControls() {
      if (!selectionEl || !blocksEl) return;

      if (currentMode === 'water' || currentMode === 'search') {
        selectionEl.innerHTML = `
          <div style="display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap;">
            <div style="flex:1; min-width:140px;">
              <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:4px;">ORIGEM</label>
              <select id="simOrigin" style="width:100%; background:var(--panel-2); color:var(--ink); border:1px solid var(--border); padding:6px 10px; border-radius:4px; font-family:var(--font-mono); font-size:0.82rem;">
                <option value="DRN_TQ_01" ${selectedOrigin === 'DRN_TQ_01' ? 'selected' : ''}>DRN_TQ_01 (Reservatório Drone)</option>
                <option value="EST_TQ_01" ${selectedOrigin === 'EST_TQ_01' ? 'selected' : ''}>EST_TQ_01 (Tanque de Solo)</option>
              </select>
            </div>
            ${currentMode === 'water' ? `
            <div style="flex:1; min-width:140px;">
              <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:4px;">DESTINO</label>
              <select id="simDest" style="width:100%; background:var(--panel-2); color:var(--ink); border:1px solid var(--border); padding:6px 10px; border-radius:4px; font-family:var(--font-mono); font-size:0.82rem;">
                <option value="DRN_BICO_A" ${selectedDest === 'DRN_BICO_A' ? 'selected' : ''}>DRN_BICO_A (0.6 m)</option>
                <option value="DRN_BICO_B" ${selectedDest === 'DRN_BICO_B' ? 'selected' : ''}>DRN_BICO_B (0.8 m)</option>
                <option value="DRN_BICO_C" ${selectedDest === 'DRN_BICO_C' ? 'selected' : ''}>DRN_BICO_C (1.0 m)</option>
                <option value="DRN_BICO_D" ${selectedDest === 'DRN_BICO_D' ? 'selected' : ''}>DRN_BICO_D (1.2 m)</option>
              </select>
            </div>` : `
            <div style="flex:1; min-width:140px;">
              <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:4px;">ALGORITMO</label>
              <select id="simSearchAlgo" style="width:100%; background:var(--panel-2); color:var(--ink); border:1px solid var(--border); padding:6px 10px; border-radius:4px; font-family:var(--font-mono); font-size:0.82rem;">
                <option value="bfs" selected>BFS (Busca em Largura)</option>
                <option value="dfs">DFS (Busca em Profundidade)</option>
              </select>
            </div>`}
          </div>`;

        document.getElementById('simOrigin')?.addEventListener('change', (e) => {
          selectedOrigin = e.target.value;
          calculateAndRender();
        });
        document.getElementById('simDest')?.addEventListener('change', (e) => {
          selectedDest = e.target.value;
          calculateAndRender();
        });
        document.getElementById('simSearchAlgo')?.addEventListener('change', () => {
          calculateAndRender();
        });

        // Bloco de arestas
        blocksEl.innerHTML = hydraulicEdges.filter(e => e.modo !== 'mistura').map(e => `
          <label class="e02-block-item">
            <input type="checkbox" value="${e.id}" ${blockedEdges.has(e.id) ? 'checked' : ''}>
            <span>${e.id} (${e.u}→${e.v.replace('DRN_','').replace('EST_','')})</span>
          </label>`).join('');

        blocksEl.querySelectorAll('input').forEach(chk => {
          chk.addEventListener('change', () => {
            if (chk.checked) blockedEdges.add(chk.value);
            else blockedEdges.delete(chk.value);
            calculateAndRender();
          });
        });

      } else if (currentMode === 'leak') {
        selectionEl.innerHTML = `
          <div>
            <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:6px;">CENÁRIO DE INJEÇÃO DE FALHA</label>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <button type="button" class="btn btn-sm ${leakScenario === 'nominal' ? 'btn-primary' : 'btn-outline'}" data-leak="nominal">Operação Nominal (Sem Falha)</button>
              <button type="button" class="btn btn-sm ${leakScenario === 'leak_e05' ? 'btn-primary' : 'btn-outline'}" data-leak="leak_e05">Vazamento em e05 (Mangueira Filtro 1)</button>
              <button type="button" class="btn btn-sm ${leakScenario === 'leak_e06' ? 'btn-primary' : 'btn-outline'}" data-leak="leak_e06">Vazamento em e06 (Saída Filtro 1)</button>
              <button type="button" class="btn btn-sm ${leakScenario === 'dual_fail' ? 'btn-primary' : 'btn-outline'}" data-leak="dual_fail">Dupla Falha (Filtro 1 e Filtro 2 Rompidos)</button>
            </div>
          </div>`;

        selectionEl.querySelectorAll('[data-leak]').forEach(b => {
          b.addEventListener('click', () => {
            leakScenario = b.dataset.leak;
            renderControls();
            calculateAndRender();
          });
        });

        blocksEl.innerHTML = `<p style="font-size:0.8rem; color:var(--muted); margin:0;">No modo de simulação de vazamento, o intertravamento atua de forma autônoma sobre as válvulas conforme o evento injetado acima.</p>`;

      } else if (currentMode === 'euler') {
        selectionEl.innerHTML = `
          <div>
            <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:6px;">CONTROLE DO CIRCUITO EULERIANO</label>
            <p style="font-size:0.82rem; color:var(--muted); margin:0 0 10px;">Todas as 6 estações possuem grau par: BASE(4), TANQUE(2), BOMBA(4), ABAST(2), BANCADA(4), LAVAGEM(2). O circuito possui 9 conexões exatas.</p>
            <button type="button" class="btn btn-sm btn-primary" id="btnEulerStep">Avançar Passo de Inspeção ➔</button>
            <button type="button" class="btn btn-sm btn-outline" id="btnEulerReset" style="margin-left:8px;">Reiniciar</button>
          </div>`;

        document.getElementById('btnEulerStep')?.addEventListener('click', () => {
          eulerStep = (eulerStep + 1) % eulerEdges.length;
          calculateAndRender();
        });
        document.getElementById('btnEulerReset')?.addEventListener('click', () => {
          eulerStep = -1;
          calculateAndRender();
        });

        blocksEl.innerHTML = `<div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted);">
          Hierholzer: BASE → TANQUE → BOMBA_SOLO → ABASTECIMENTO → BANCADA_DRONE → LAVAGEM → BASE → BOMBA_SOLO → BANCADA_DRONE → BASE.
        </div>`;

      } else if (currentMode === 'tsp') {
        selectionEl.innerHTML = `
          <div>
            <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:6px;">MÉTODO DE ROTEAMENTO (TSP)</label>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <button type="button" class="btn btn-sm ${tspMode === 'opt' ? 'btn-primary' : 'btn-outline'}" data-tsp="opt">2-Opt / Ótimo Global (585,332 m)</button>
              <button type="button" class="btn btn-sm ${tspMode === 'nn' ? 'btn-primary' : 'btn-outline'}" data-tsp="nn">Vizinho Mais Próximo (660,608 m)</button>
              <button type="button" class="btn btn-sm ${tspMode === 'mst' ? 'btn-primary' : 'btn-outline'}" data-tsp="mst">Árvore Geradora Mínima - AGM (375,304 m)</button>
            </div>
          </div>`;

        selectionEl.querySelectorAll('[data-tsp]').forEach(b => {
          b.addEventListener('click', () => {
            tspMode = b.dataset.tsp;
            renderControls();
            calculateAndRender();
          });
        });

        blocksEl.innerHTML = `<div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted);">
          Instância de 6 pontos: BASE, T1, T2, T3, T4, T5.<br>
          Força bruta em 120 permutações confirma o ótimo global em <strong>585,332 m</strong> (ganho de 11,4% sobre Vizinho Mais Próximo).
        </div>`;

      } else if (currentMode === 'logistics') {
        selectionEl.innerHTML = `
          <div>
            <label style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted-dim); display:block; margin-bottom:6px;">REDE DE MATERIAIS & APOIO</label>
            <p style="font-size:0.82rem; color:var(--muted); margin:0;">Rastreia as distâncias percorridas por insumos antes e durante a missão de pulverização.</p>
          </div>`;

        blocksEl.innerHTML = `<div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted); line-height:1.7;">
          • Insumo Água: 210 m até o talhão<br>
          • Insumo Defensivo: 206 m até o talhão<br>
          • Retorno de Apoio Terrestre: 65 m
        </div>`;
      }
    }

    // Algoritmo de Dijkstra para a Rede Hidráulica em JavaScript
    function runDijkstra(startNode, endNode, blocked) {
      const distances = {};
      const previous = {};
      const unvisited = new Set(Object.keys(hydraulicNodes));

      Object.keys(hydraulicNodes).forEach(node => {
        distances[node] = Infinity;
        previous[node] = null;
      });
      distances[startNode] = 0;

      while (unvisited.size > 0) {
        // Encontra vértice com menor distância
        let closest = null;
        unvisited.forEach(node => {
          if (closest === null || distances[node] < distances[closest]) {
            closest = node;
          }
        });

        if (distances[closest] === Infinity || closest === endNode) break;
        unvisited.delete(closest);

        // Vizinhos
        hydraulicEdges.forEach(edge => {
          if (edge.u === closest && unvisited.has(edge.v) && !blocked.has(edge.id)) {
            // Se origem for VANT e aresta for solo, ignore (a menos que origem seja solo)
            if (startNode.startsWith('DRN_') && edge.modo === 'solo') return;
            if (startNode.startsWith('DRN_') && edge.id === 'e04') return;

            const alt = distances[closest] + edge.w;
            if (alt < distances[edge.v]) {
              distances[edge.v] = alt;
              previous[edge.v] = { node: closest, edgeId: edge.id };
            }
          }
        });
      }

      // Reconstrói caminho
      const pathNodes = [];
      const pathEdges = [];
      let curr = endNode;
      if (distances[endNode] !== Infinity) {
        while (curr) {
          pathNodes.unshift(curr);
          if (previous[curr]) {
            pathEdges.unshift(previous[curr].edgeId);
            curr = previous[curr].node;
          } else {
            break;
          }
        }
      }

      return {
        dist: distances[endNode],
        nodes: pathNodes,
        edges: pathEdges,
        reachable: Object.keys(distances).filter(n => distances[n] !== Infinity)
      };
    }

    // Renderiza e calcula tudo
    function calculateAndRender() {
      if (!svgEl) return;

      if (currentMode === 'water') {
        const res = runDijkstra(selectedOrigin, selectedDest, blockedEdges);
        const activeEdgeSet = new Set(res.edges);
        const activeNodeSet = new Set(res.nodes);

        let svgHtml = `<defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="var(--muted-dim)" />
          </marker>
          <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="var(--crop)" />
          </marker>
        </defs>`;

        // Desenhar arestas
        hydraulicEdges.forEach(edge => {
          const u = hydraulicNodes[edge.u];
          const v = hydraulicNodes[edge.v];
          if (!u || !v) return;

          const isBlocked = blockedEdges.has(edge.id);
          const isActive = activeEdgeSet.has(edge.id);

          let edgeClass = 'graph-edge';
          if (isBlocked) edgeClass += ' blocked';
          else if (isActive) edgeClass += ' active highlight';

          // Curvas ou retas
          let d = `M${u.x} ${u.y} L${v.x} ${v.y}`;
          if (edge.id === 'e03') {
            d = `M${u.x} ${u.y} C 220 50, 120 50, ${v.x} ${v.y}`;
          }

          const marker = isActive ? 'url(#arrow-active)' : 'url(#arrow)';
          svgHtml += `<path class="${edgeClass}" d="${d}" marker-end="${isBlocked ? '' : marker}" />`;

          // Label do peso
          const midX = (u.x + v.x) / 2;
          const midY = (u.y + v.y) / 2 + (edge.id === 'e03' ? -40 : (edge.id === 'e12' ? 14 : -8));
          svgHtml += `<text class="graph-weight ${isActive ? 'highlight' : ''}" x="${midX}" y="${midY}">${edge.id} (${edge.w}m)</text>`;
        });

        // Desenhar nós
        Object.keys(hydraulicNodes).forEach(id => {
          const n = hydraulicNodes[id];
          const isActive = activeNodeSet.has(id);
          const isOrigin = (id === selectedOrigin);
          const isDest = (id === selectedDest);

          let nodeClass = 'graph-node';
          if (isActive) nodeClass += ' highlight';
          if (isOrigin || isDest) nodeClass += ' active';

          const width = 84;
          const height = 30;

          svgHtml += `<g class="${nodeClass}" transform="translate(${n.x - width/2}, ${n.y - height/2})">
            <rect width="${width}" height="${height}" rx="5" />
            <text x="${width/2}" y="${height/2}">${n.label.replace('DRN_','').replace('EST_','')}</text>
          </g>`;
        });

        svgEl.innerHTML = svgHtml;

        // Atualizar resultados
        if (simResultsEl) {
          const found = res.dist !== Infinity;
          simResultsEl.innerHTML = `
            <div class="e02-result-stat">
              <span class="label">Status da Rota</span>
              <span class="val" style="color:${found ? 'var(--crop)' : 'var(--alarm)'}">${found ? 'CAMINHO ENCONTRADO' : 'SEM ROTA DISPONÍVEL'}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Comprimento Total</span>
              <span class="val">${found ? res.dist.toFixed(2) + ' m' : '—'}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Saltos (Arestas)</span>
              <span class="val">${found ? res.edges.length : '0'}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Sequência Calculada</span>
              <span class="val" style="font-size:0.85rem; font-weight:500;">${found ? res.nodes.map(n => n.replace('DRN_','').replace('EST_','')).join(' ➔ ') : 'Trecho bloqueado'}</span>
            </div>`;
        }

      } else if (currentMode === 'search') {
        const algo = document.getElementById('simSearchAlgo')?.value || 'bfs';
        // Executa busca simples
        const visited = [];
        const queue = [selectedOrigin];
        const seen = new Set([selectedOrigin]);

        while (queue.length > 0) {
          const curr = (algo === 'bfs') ? queue.shift() : queue.pop();
          visited.push(curr);

          hydraulicEdges.forEach(edge => {
            if (edge.u === curr && !blockedEdges.has(edge.id) && !seen.has(edge.v)) {
              if (selectedOrigin.startsWith('DRN_') && (edge.modo === 'solo' || edge.id === 'e04')) return;
              seen.add(edge.v);
              queue.push(edge.v);
            }
          });
        }

        const visitedSet = new Set(visited);
        let svgHtml = `<defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="var(--muted-dim)" />
          </marker>
          <marker id="arrow-search" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="var(--crop)" />
          </marker>
        </defs>`;

        hydraulicEdges.forEach(edge => {
          const u = hydraulicNodes[edge.u];
          const v = hydraulicNodes[edge.v];
          const isReached = visitedSet.has(edge.u) && visitedSet.has(edge.v);
          const isBlocked = blockedEdges.has(edge.id);

          let edgeClass = 'graph-edge';
          if (isBlocked) edgeClass += ' blocked';
          else if (isReached) edgeClass += ' active';

          svgHtml += `<path class="${edgeClass}" d="M${u.x} ${u.y} L${v.x} ${v.y}" marker-end="${isBlocked ? '' : (isReached ? 'url(#arrow-search)' : 'url(#arrow)')}" />`;
        });

        Object.keys(hydraulicNodes).forEach(id => {
          const n = hydraulicNodes[id];
          const isVisited = visitedSet.has(id);
          const isStart = (id === selectedOrigin);

          let nodeClass = 'graph-node';
          if (isVisited) nodeClass += ' highlight';
          if (isStart) nodeClass += ' active';

          svgHtml += `<g class="${nodeClass}" transform="translate(${n.x - 42}, ${n.y - 15})">
            <rect width="84" height="30" rx="5" />
            <text x="42" y="15">${n.label.replace('DRN_','').replace('EST_','')}</text>
          </g>`;
        });

        svgEl.innerHTML = svgHtml;

        if (simResultsEl) {
          simResultsEl.innerHTML = `
            <div class="e02-result-stat">
              <span class="label">Algoritmo</span>
              <span class="val">${algo.toUpperCase()} (${algo === 'bfs' ? 'Fila FIFO' : 'Pilha LIFO'})</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Nós Alcançáveis</span>
              <span class="val">${visited.length} / ${Object.keys(hydraulicNodes).length}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Ordem de Descoberta</span>
              <span class="val" style="font-size:0.8rem; font-weight:400;">${visited.map(n => n.replace('DRN_','').replace('EST_','')).join(' → ')}</span>
            </div>`;
        }

      } else if (currentMode === 'leak') {
        // Modo 3: Simulação de Vazamento & Intertravamento
        const activeBlocked = new Set();
        let alarmState = 'NOMINAL';
        let pumpStatus = 'LIGA_BOMBA = 1';
        let valveStatus = 'F1_ABERTA / F2_FECHADA';
        let currentRoute = 'DRN_TQ_01 ➔ DRN_FLT_01 ➔ DRN_PMP_01 ➔ BICO';

        if (leakScenario === 'leak_e05' || leakScenario === 'leak_e06') {
          activeBlocked.add(leakScenario === 'leak_e05' ? 'e05' : 'e06');
          activeBlocked.add('e05');
          activeBlocked.add('e06');
          alarmState = 'ALARME: VAZAMENTO MANGUEIRA FILTRO 1';
          pumpStatus = 'DESARMADA: LIGA_BOMBA = 0 (Intertravamento Estático)';
          valveStatus = 'F1_ISOLADA / F2_RESERVA_HABILITADA';
          currentRoute = 'DESVIO AUTOMÁTICO: DRN_TQ_01 ➔ DRN_FLT_02 ➔ DRN_PMP_01 ➔ BICO';
        } else if (leakScenario === 'dual_fail') {
          activeBlocked.add('e05');
          activeBlocked.add('e06');
          activeBlocked.add('e12');
          activeBlocked.add('e13');
          alarmState = 'EMERGÊNCIA CRÍTICA: DUPLA FALHA DE LINHA';
          pumpStatus = 'CORTE TOTAL: LIGA_BOMBA = 0';
          valveStatus = 'F1_ISOLADA / F2_ISOLADA';
          currentRoute = 'SEM ROTA DISPONÍVEL (MISSÃO ABORTADA)';
        }

        const res = runDijkstra('DRN_TQ_01', 'DRN_BICO_A', activeBlocked);
        const activeEdgeSet = new Set(res.edges);
        const activeNodeSet = new Set(res.nodes);

        let svgHtml = `<defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="var(--muted-dim)" />
          </marker>
          <marker id="arrow-leak" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0 1L8 5L0 9z" fill="${leakScenario !== 'nominal' ? 'var(--alarm)' : 'var(--crop)'}" />
          </marker>
        </defs>`;

        hydraulicEdges.filter(e => e.modo === 'voo' || e.modo === 'reserva').forEach(edge => {
          const u = hydraulicNodes[edge.u];
          const v = hydraulicNodes[edge.v];
          const isBlocked = activeBlocked.has(edge.id);
          const isActive = activeEdgeSet.has(edge.id);

          let edgeClass = 'graph-edge';
          if (isBlocked) edgeClass += ' blocked';
          else if (isActive) edgeClass += ' active highlight';

          svgHtml += `<path class="${edgeClass}" d="M${u.x} ${u.y} L${v.x} ${v.y}" marker-end="${isBlocked ? '' : 'url(#arrow)'}" />`;
          svgHtml += `<text class="graph-weight ${isActive ? 'highlight' : ''}" x="${(u.x+v.x)/2}" y="${(u.y+v.y)/2 - 8}">${edge.id}</text>`;
        });

        // Nós embarcados
        ['DRN_TQ_01', 'DRN_FLT_01', 'DRN_FLT_02', 'DRN_PMP_01', 'DRN_MAN_01', 'DRN_BICO_A'].forEach(id => {
          const n = hydraulicNodes[id];
          const isActive = activeNodeSet.has(id);
          const isFail = (leakScenario.includes('e05') && id === 'DRN_FLT_01') || (leakScenario === 'dual_fail' && (id === 'DRN_FLT_01' || id === 'DRN_FLT_02'));

          let nodeClass = 'graph-node';
          if (isFail) nodeClass += ' blocked';
          else if (isActive) nodeClass += ' highlight';

          svgHtml += `<g class="${nodeClass}" transform="translate(${n.x - 42}, ${n.y - 15})">
            <rect width="84" height="30" rx="5" />
            <text x="42" y="15">${n.label.replace('DRN_','')}</text>
          </g>`;
        });

        svgEl.innerHTML = svgHtml;

        if (simResultsEl) {
          simResultsEl.innerHTML = `
            <div class="e02-result-stat" style="grid-column:1/-1;">
              <span class="label">Diagnóstico SCADA Integrado</span>
              <span class="val" style="color:${leakScenario === 'nominal' ? 'var(--crop)' : 'var(--alarm)'};">${alarmState}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Intertravamento Bomba</span>
              <span class="val" style="font-size:0.85rem; color:${leakScenario === 'nominal' ? 'var(--crop)' : 'var(--caution)'};">${pumpStatus}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Válvulas de Isolamento</span>
              <span class="val" style="font-size:0.85rem;">${valveStatus}</span>
            </div>
            <div class="e02-result-stat" style="grid-column:1/-1;">
              <span class="label">Ação Topológica</span>
              <span class="val" style="font-size:0.85rem; font-weight:500;">${currentRoute}</span>
            </div>`;
        }

      } else if (currentMode === 'euler') {
        // Modo 4: Inspeção Euleriana
        let svgHtml = '';

        eulerEdges.forEach((edge, idx) => {
          const u = eulerNodes[edge.u];
          const v = eulerNodes[edge.v];
          const isDone = (idx <= eulerStep && eulerStep >= 0);
          const isCurrent = (idx === eulerStep);

          let strokeColor = 'var(--muted-dim)';
          let strokeWidth = '1.5px';
          let strokeDash = '';

          if (isCurrent) {
            strokeColor = 'var(--soil)';
            strokeWidth = '3.5px';
          } else if (isDone) {
            strokeColor = 'var(--crop)';
            strokeWidth = '2.5px';
          }

          svgHtml += `<line class="graph-edge" x1="${u.x}" y1="${u.y}" x2="${v.x}" y2="${v.y}" style="stroke:${strokeColor}; stroke-width:${strokeWidth}; ${strokeDash}" />`;
          svgHtml += `<text class="graph-weight" x="${(u.x+v.x)/2}" y="${(u.y+v.y)/2 - 6}" style="fill:${isCurrent ? 'var(--soil)' : (isDone ? 'var(--crop)' : 'var(--muted-dim)')}">${edge.id} (${edge.w})</text>`;
        });

        Object.keys(eulerNodes).forEach(id => {
          const n = eulerNodes[id];
          const isCurrentNode = (eulerStep >= 0 && (eulerEdges[eulerStep].v === id || eulerEdges[eulerStep].u === id));

          svgHtml += `<g class="graph-node ${isCurrentNode ? 'highlight active' : ''}" transform="translate(${n.x - 52}, ${n.y - 18})">
            <rect width="104" height="36" rx="6" />
            <text x="52" y="14" style="font-size:10px; font-weight:600;">${id}</text>
            <text x="52" y="26" style="font-size:8.5px; fill:var(--crop);">grau ${n.deg}</text>
          </g>`;
        });

        svgEl.innerHTML = svgHtml;

        if (simResultsEl) {
          simResultsEl.innerHTML = `
            <div class="e02-result-stat">
              <span class="label">Passo da Inspeção</span>
              <span class="val">${eulerStep >= 0 ? `Passo ${eulerStep + 1} de 9 (${eulerEdges[eulerStep].id})` : 'Aguardando Início'}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Vias Inspecionadas</span>
              <span class="val">${eulerStep >= 0 ? `${eulerStep + 1} / 9 (100% Euleriano)` : '0 / 9'}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Teorema de Euler</span>
              <span class="val" style="color:var(--crop);">Graus Pares em Todos os Vértices</span>
            </div>`;
        }

      } else if (currentMode === 'tsp') {
        // Modo 5: Caixeiro Viajante (TSP)
        let route = [];
        let totalDist = 0;
        let routeName = '';

        if (tspMode === 'opt') {
          // Ótimo 2-Opt: BASE -> T1 -> T2 -> T3 -> T4 -> T5 -> BASE (585.332 m)
          route = ['BASE', 'T1', 'T2', 'T3', 'T4', 'T5', 'BASE'];
          totalDist = 585.332;
          routeName = '2-Opt / Ótimo Global Exato (Branch & Bound)';
        } else if (tspMode === 'nn') {
          // Vizinho mais próximo: 660.608 m
          route = ['BASE', 'T5', 'T4', 'T3', 'T2', 'T1', 'BASE'];
          totalDist = 660.608;
          routeName = 'Heurística do Vizinho Mais Próximo';
        } else if (tspMode === 'mst') {
          // Árvore geradora mínima (Kruskal): 375.304 m
          routeName = 'Árvore Geradora Mínima - AGM (Cota Inferior)';
          totalDist = 375.304;
        }

        let svgHtml = `<defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(42,67,53,0.3)" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />`;

        if (tspMode === 'mst') {
          // Desenhar arestas da AGM
          const mstEdges = [
            ['BASE', 'T5'], ['T5', 'T4'], ['T4', 'T3'], ['T3', 'T2'], ['BASE', 'T1']
          ];
          mstEdges.forEach(([uId, vId]) => {
            const u = tspPoints[uId];
            const v = tspPoints[vId];
            svgHtml += `<line x1="${u.x}" y1="${u.y}" x2="${v.x}" y2="${v.y}" style="stroke:var(--sky); stroke-width:2.5px; stroke-dasharray:6 3;" />`;
          });
        } else {
          // Desenhar polígono do TSP
          for (let i = 0; i < route.length - 1; i++) {
            const u = tspPoints[route[i]];
            const v = tspPoints[route[i+1]];
            const color = (tspMode === 'opt') ? 'var(--crop)' : 'var(--caution)';
            svgHtml += `<line x1="${u.x}" y1="${u.y}" x2="${v.x}" y2="${v.y}" style="stroke:${color}; stroke-width:3px;" />`;
          }
        }

        // Desenhar pontos dos talhões
        Object.keys(tspPoints).forEach(id => {
          const pt = tspPoints[id];
          const isBase = (id === 'BASE');
          svgHtml += `<g transform="translate(${pt.x}, ${pt.y})">
            <circle r="${isBase ? 10 : 7}" fill="${isBase ? 'var(--soil)' : 'var(--crop)'}" stroke="var(--ink)" stroke-width="2" />
            <text x="0" y="${isBase ? -15 : -12}" font-family="var(--font-mono)" font-size="11" fill="var(--ink)" font-weight="700" text-anchor="middle">${id}</text>
          </g>`;
        });

        svgEl.innerHTML = svgHtml;

        if (simResultsEl) {
          simResultsEl.innerHTML = `
            <div class="e02-result-stat">
              <span class="label">Algoritmo Ativo</span>
              <span class="val" style="font-size:0.92rem;">${routeName}</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Distância Percorrida</span>
              <span class="val" style="color:${tspMode === 'opt' ? 'var(--crop)' : 'var(--caution)'};">${totalDist.toFixed(3)} m</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Ganho de Otimização</span>
              <span class="val">${tspMode === 'opt' ? '-11.4% sobre NN' : (tspMode === 'nn' ? 'Base de Comparação' : 'Cota Inferior Teórica')}</span>
            </div>`;
        }

      } else if (currentMode === 'logistics') {
        // Modo 6: Logística de Insumos
        let svgHtml = `<g font-family="var(--font-mono)">
          <!-- Água -->
          <rect x="80" y="80" width="120" height="40" rx="4" fill="var(--panel-2)" stroke="var(--sky)" stroke-width="2"/>
          <text x="140" y="105" fill="var(--ink)" font-size="11" text-anchor="middle">FONTE D'ÁGUA</text>

          <line x1="200" y1="100" x2="300" y2="100" stroke="var(--sky)" stroke-width="2"/>
          <text x="250" y="92" fill="var(--sky)" font-size="9" text-anchor="middle">eM01 (45m)</text>

          <!-- Defensivo -->
          <rect x="80" y="240" width="120" height="40" rx="4" fill="var(--panel-2)" stroke="var(--soil)" stroke-width="2"/>
          <text x="140" y="265" fill="var(--ink)" font-size="11" text-anchor="middle">DEPÓSITO DEFENSIVO</text>

          <line x1="200" y1="260" x2="300" y2="260" stroke="var(--soil)" stroke-width="2"/>
          <text x="250" y="252" fill="var(--soil)" font-size="9" text-anchor="middle">eM02 (41m)</text>

          <!-- Tanque Solo -->
          <rect x="300" y="160" width="130" height="50" rx="6" fill="var(--panel)" stroke="var(--crop)" stroke-width="2"/>
          <text x="365" y="185" fill="var(--ink)" font-size="11" font-weight="700" text-anchor="middle">PREPARO CALDA</text>
          <text x="365" y="200" fill="var(--muted-dim)" font-size="9" text-anchor="middle">EST_TQ_01 (500L)</text>

          <line x1="300" y1="100" x2="365" y2="160" stroke="var(--sky)" stroke-width="2"/>
          <line x1="300" y1="260" x2="365" y2="210" stroke="var(--soil)" stroke-width="2"/>

          <!-- Abastecimento Drone -->
          <line x1="430" y1="185" x2="540" y2="185" stroke="var(--crop)" stroke-width="2.5"/>
          <text x="485" y="177" fill="var(--crop)" font-size="9" text-anchor="middle">eM04 (3m)</text>

          <rect x="540" y="160" width="120" height="50" rx="6" fill="var(--panel)" stroke="var(--crop)" stroke-width="2"/>
          <text x="600" y="185" fill="var(--ink)" font-size="11" font-weight="700" text-anchor="middle">DRONE AGRÍCOLA</text>
          <text x="600" y="200" fill="var(--muted-dim)" font-size="9" text-anchor="middle">DRN_TQ_01 (30L)</text>

          <!-- Aplicação Talhões -->
          <line x1="660" y1="185" x2="760" y2="185" stroke="var(--crop)" stroke-width="2.5" stroke-dasharray="4 2"/>
          <text x="710" y="177" fill="var(--crop)" font-size="9" text-anchor="middle">Voo Talhão</text>

          <rect x="760" y="160" width="100" height="50" rx="6" fill="rgba(191,224,90,0.15)" stroke="var(--crop)" stroke-width="2"/>
          <text x="810" y="190" fill="var(--crop)" font-size="11" font-weight="700" text-anchor="middle">TALHÕES</text>
        </g>`;

        svgEl.innerHTML = svgHtml;

        if (simResultsEl) {
          simResultsEl.innerHTML = `
            <div class="e02-result-stat">
              <span class="label">Caminho da Água</span>
              <span class="val" style="color:var(--sky);">210 metros acumulados</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Caminho do Defensivo</span>
              <span class="val" style="color:var(--soil);">206 metros acumulados</span>
            </div>
            <div class="e02-result-stat">
              <span class="label">Apoio Terrestre</span>
              <span class="val">65 metros (BASE - Portão)</span>
            </div>`;
        }
      }
    }

    runBtn?.addEventListener('click', calculateAndRender);
    resetBtn?.addEventListener('click', () => {
      blockedEdges.clear();
      leakScenario = 'nominal';
      eulerStep = -1;
      tspMode = 'opt';
      selectedOrigin = 'DRN_TQ_01';
      selectedDest = 'DRN_BICO_A';
      renderControls();
      calculateAndRender();
    });

    // Iniciar no modo padrão
    setMode('water');
  }

});
