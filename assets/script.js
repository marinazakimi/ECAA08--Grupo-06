// ============================================================
// SCADA · AgroDrone — Grupo 06
// nav mobile + tabela de aulas + motor de simulação
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

  /* ---------------- menu mobile ---------------- */
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  navToggle?.addEventListener('click', () => navLinks.classList.toggle('open'));
  navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));

  /* ---------------- memorial das aulas ---------------- */
  const BASE = 'etapa-01-logica/';
  const lessons = [
    { n: '00', title: 'Insumos e Materiais de Processo', desc: 'Calda de pulverização, energia e insumos de manutenção do sistema.', file: '00-%20Insumos.md' },
    { n: '01', title: 'Kick-off & Arquitetura do SCADA-Core', desc: 'Estruturação da classe TagSCADA e separação em camadas.', file: null },
    { n: '02', title: 'Mapeamento de Variáveis de Processo', desc: 'Catálogo de tags ISA 5.1 e proposições atômicas do drone.', file: '02-%20Mapeamento%20de%20Variaveis.md' },
    { n: '03', title: 'Tautologias e Contradições', desc: 'Prova formal do intertravamento de emergência (kill switch × motores).', file: '03_Tautologias_e_Contradicoes.ipynb' },
    { n: '04', title: 'Lógica Proposicional: Conectivos e Permissivos', desc: 'Permissivo de decolagem e de pulverização.', file: '04_Logica_Proposicional_Conectivos_e_Permissivos.ipynb' },
    { n: '05', title: 'Formas Normais e Otimização Booleana', desc: 'Minimização das expressões de intertravamento (Quine–McCluskey).', file: '05_Formas_Normais_e_Otimizacao_Booleana.ipynb' },
    { n: '06', title: 'Quantificadores e Predicados em Redes de Sensores', desc: '∀ / ∃ sobre a barra de pulverização setorizada e a rede de telemetria.', file: '06_%20Quantificadores_e_Predicados_em_Redes_de_Sensores.ipynb' },
    { n: '07', title: 'Validade e Inferência Lógica na Segurança', desc: 'Modus Ponens, Modus Tollens e silogismos aplicados ao diagnóstico.', file: '07_Validade_e_Inferencia_Logica_na_Seguranca.ipynb' },
    { n: '08', title: 'Base de Conhecimento e Regras de Diagnóstico', desc: 'Regras SE...ENTÃO (R1–R8) do sistema especialista.', file: '08_Base_de_Conhecimento_e_Regras_de_Diagnostico.ipynb' },
    { n: '09', title: 'Motor de Inferência (Forward & Backward Chaining)', desc: 'Implementação dos dois algoritmos de encadeamento.', file: '09_Motor_de_Inferencia.ipynb' },
    { n: '10', title: 'Avaliação do Módulo 1 — Motor Integrado', desc: 'Fusão do intertravamento com o sistema especialista e prova exaustiva de segurança.', file: '10_Avalia%C3%A7%C3%A3o%20Integrada%20do%20M%C3%B3dulo%201%20%E2%80%94%20SCADA-Core%20Seguran%C3%A7a%20%26%20Diagn%C3%B3stico.ipynb' },
  ];

  const tbody = document.getElementById('lessonTable');
  if (tbody) {
    tbody.innerHTML = lessons.map(l => `
      <tr>
        <td class="num">${l.n}</td>
        <td class="info"><strong>${l.title}</strong><span>${l.desc}</span></td>
        <td class="file">${l.file
          ? `<a href="${BASE}${l.file}" target="_blank" rel="noopener">Abrir notebook ↗</a>`
          : `<span style="color:var(--muted-dim);">Em andamento</span>`}</td>
      </tr>`).join('');
  }

  /* ---------------- simulador ---------------- */
  const el = id => document.getElementById(id);
  const sliders = {
    nivel: el('s_nivel'), pressao: el('s_pressao'), vazao: el('s_vazao'),
    bateria: el('s_bateria'), vento: el('s_vento'),
  };
  const toggles = {
    bomba: el('s_bomba'), valvula: el('s_valvula'), gps: el('s_gps'),
    motores: el('s_motores'), estop: el('s_estop'),
  };

  const propGrid = el('propGrid');
  const permGrid = el('permGrid');
  const diagList = el('diagList');
  const finalCommand = el('finalCommand');
  const finalWhy = el('finalWhy');
  const simStatus = el('simStatus');
  const simStatusText = el('simStatusText');
  const logBox = el('logBox');

  let lastSignature = '';

  const scenarios = {
    ideal:      { nivel: 62, pressao: 24, vazao: 18, bateria: 86, vento: 32,  bomba: true,  valvula: true,  gps: true,  motores: true,  estop: false },
    bateria:    { nivel: 55, pressao: 20, vazao: 15, bateria: 8,  vento: 20,  bomba: false, valvula: true,  gps: true,  motores: true,  estop: false },
    vento:      { nivel: 60, pressao: 20, vazao: 15, bateria: 70, vento: 120, bomba: false, valvula: true,  gps: true,  motores: true,  estop: false },
    obstrucao:  { nivel: 60, pressao: 52, vazao: 2,  bateria: 80, vento: 20,  bomba: true,  valvula: true,  gps: true,  motores: true,  estop: false },
    vazamento:  { nivel: 60, pressao: 8,  vazao: 2,  bateria: 80, vento: 20,  bomba: true,  valvula: true,  gps: true,  motores: true,  estop: false },
    vazio:      { nivel: 3,  pressao: 20, vazao: 15, bateria: 80, vento: 20,  bomba: true,  valvula: true,  gps: true,  motores: true,  estop: false },
    emergencia: { nivel: 60, pressao: 20, vazao: 15, bateria: 80, vento: 20,  bomba: true,  valvula: true,  gps: true,  motores: true,  estop: true  },
  };

  function applyScenario(name) {
    const s = scenarios[name];
    if (!s) return;
    sliders.nivel.value = s.nivel; sliders.pressao.value = s.pressao; sliders.vazao.value = s.vazao;
    sliders.bateria.value = s.bateria; sliders.vento.value = s.vento;
    toggles.bomba.checked = s.bomba; toggles.valvula.checked = s.valvula; toggles.gps.checked = s.gps;
    toggles.motores.checked = s.motores; toggles.estop.checked = s.estop;
    recompute(true);
  }

  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyScenario(btn.dataset.scenario);
    });
  });

  function deactivateScenarioButtons() {
    document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
  }

  Object.values(sliders).forEach(s => s.addEventListener('input', () => { deactivateScenarioButtons(); recompute(); }));
  Object.values(toggles).forEach(t => t.addEventListener('change', () => { deactivateScenarioButtons(); recompute(); }));

  function chip(label, on) {
    return `<span class="prop-chip${on ? ' on' : ''}">${label}${on ? ' = 1' : ' = 0'}</span>`;
  }

  function pushLog(msg) {
    const t = new Date().toLocaleTimeString('pt-BR', { hour12: false });
    const line = document.createElement('div');
    line.innerHTML = `<span class="t">[${t}]</span> ${msg}`;
    logBox.prepend(line);
    while (logBox.children.length > 8) logBox.removeChild(logBox.lastChild);
  }

  function recompute(forceLog) {
    const nivel   = Number(sliders.nivel.value);
    const pressao = Number(sliders.pressao.value) / 10;
    const vazao   = Number(sliders.vazao.value) / 10;
    const bateria = Number(sliders.bateria.value);
    const vento   = Number(sliders.vento.value) / 10;

    el('v_nivel').textContent   = nivel + ' %';
    el('v_pressao').textContent = pressao.toFixed(1) + ' bar';
    el('v_vazao').textContent   = vazao.toFixed(1) + ' L/min';
    el('v_bateria').textContent = bateria + ' %';
    el('v_vento').textContent   = vento.toFixed(1) + ' m/s';

    const bomba_on   = toggles.bomba.checked;
    const valvula_ok = toggles.valvula.checked;
    const gps_ok     = toggles.gps.checked;
    const estop      = toggles.estop.checked;
    const motores_cmd = toggles.motores.checked;
    // intertravamento de emergência: sob e1 -> ¬m1, o sistema força a desarmar (Aula 03)
    const motores_efetivo = estop ? false : motores_cmd;

    // --- fatos (Aula 02 / Aula 09) ---
    const nivel_baixo    = nivel < 20;
    const nivel_critico  = nivel < 5;
    const vazao_baixa    = vazao < 0.5;
    const vazao_alta     = vazao >= 3.0;
    const pressao_alta   = pressao > 5;
    const pressao_baixa  = pressao < 1;
    const bateria_baixa  = bateria < 20;
    const bateria_critica= bateria < 10;
    const vento_alto     = vento > 8;

    propGrid.innerHTML = [
      chip('nivel_baixo', nivel_baixo), chip('nivel_critico', nivel_critico),
      chip('vazao_baixa', vazao_baixa), chip('vazao_alta', vazao_alta),
      chip('pressao_alta', pressao_alta), chip('pressao_baixa', pressao_baixa),
      chip('bateria_baixa', bateria_baixa), chip('bateria_critica', bateria_critica),
      chip('vento_alto', vento_alto),
    ].join('');

    // --- permissivos / intertravamento (Aulas 03-04) ---
    const p_takeoff = gps_ok && !bateria_baixa && !vento_alto && !estop;
    const alarm_obstr = bomba_on && pressao_alta && vazao_baixa;
    const alarm_rupt  = bomba_on && pressao_baixa && vazao_alta;
    const alarm_cavit = bomba_on && nivel_critico;
    const perm_spray  = !nivel_critico && !alarm_obstr && !alarm_rupt;

    permGrid.innerHTML = [
      chip('P_takeoff', p_takeoff),
      chip('Perm_spray', perm_spray),
      chip('Alarm_obstr', alarm_obstr),
      chip('Alarm_rupt', alarm_rupt),
      chip('Alarm_cavit', alarm_cavit),
      chip('kill_switch (e1)', estop),
    ].join('');

    // --- motor de diagnóstico: forward chaining sobre R1-R8 (Aula 09) ---
    const facts = new Set();
    if (nivel_critico) facts.add('nivel_critico');
    if (vazao_baixa) facts.add('vazao_baixa');
    if (vazao_alta) facts.add('vazao_alta');
    if (pressao_alta) facts.add('pressao_alta');
    if (pressao_baixa) facts.add('pressao_baixa');
    if (bomba_on) facts.add('bomba_ligada');
    if (valvula_ok) facts.add('valvula_aberta');
    if (bateria_critica) facts.add('bateria_critica');
    if (vento_alto) facts.add('vento_alto');

    const rules = [
      { id: 'R1', cond: ['nivel_critico'], concl: 'falta_insumo', label: 'Falta de insumo — nível crítico do reservatório' },
      { id: 'R2', cond: ['bomba_ligada', 'valvula_aberta', 'vazao_baixa'], concl: 'falha_pulverizacao', label: 'Falha de pulverização' },
      { id: 'R3', cond: ['bomba_ligada', 'vazao_baixa', 'pressao_alta'], concl: 'possivel_obstrucao', label: 'Possível obstrução dos bicos' },
      { id: 'R4', cond: ['possivel_obstrucao'], concl: 'interromper_pulverizacao', label: 'Ação: interromper pulverização' },
      { id: 'R5', cond: ['falta_insumo'], concl: 'interromper_pulverizacao', label: 'Ação: interromper pulverização' },
      { id: 'R6', cond: ['bateria_critica'], concl: 'interromper_missao', label: 'Ação: interromper missão — bateria crítica' },
      { id: 'R7', cond: ['vento_alto'], concl: 'suspender_pulverizacao', label: 'Ação: suspender pulverização — vento alto' },
      { id: 'R8', cond: ['bomba_ligada', 'pressao_baixa', 'vazao_baixa'], concl: 'possivel_vazamento_ou_falha_bomba', label: 'Possível vazamento ou falha da bomba' },
    ];

    const fired = [];
    let changed = true;
    while (changed) {
      changed = false;
      for (const r of rules) {
        if (!facts.has(r.concl) && r.cond.every(c => facts.has(c))) {
          facts.add(r.concl);
          fired.push(r);
          changed = true;
        }
      }
    }

    if (fired.length === 0) {
      diagList.className = 'diag-list empty';
      diagList.innerHTML = '<li>Nenhum diagnóstico ativo</li>';
    } else {
      diagList.className = 'diag-list';
      diagList.innerHTML = fired.map(r => `<li><b>${r.id}</b> — ${r.label}</li>`).join('');
    }

    // --- fusão / comando final (Aula 10) ---
    const liga_bomba = perm_spray && fired.length === 0 && !estop;

    let statusClass = 'ok', statusText = 'NOMINAL';
    if (estop) { statusClass = 'crit'; statusText = 'EMERGÊNCIA'; }
    else if (fired.some(r => ['R3','R4','R5','R6','R8'].includes(r.id))) { statusClass = 'crit'; statusText = 'ALARME'; }
    else if (fired.length > 0 || !p_takeoff) { statusClass = 'warn'; statusText = 'CAUTELA'; }

    simStatus.className = 'sim-status ' + statusClass;
    simStatusText.textContent = statusText;

    finalCommand.className = 'final-command ' + (liga_bomba ? 'go' : 'no');
    finalCommand.innerHTML = `LIGA_BOMBA = ${liga_bomba ? 1 : 0}<span class="why" id="finalWhy"></span>`;
    const why = document.getElementById('finalWhy');
    if (estop) why.textContent = 'Botão de emergência acionado — intertravamento força a parada (Aula 03).';
    else if (!perm_spray) why.textContent = 'Permissivo de pulverização reprovado (reservatório crítico ou alarme de obstrução/ruptura).';
    else if (fired.length > 0) why.textContent = 'Sistema especialista detectou ' + fired.length + ' diagnóstico(s) — bomba bloqueada por segurança.';
    else why.textContent = 'Permissivo de pulverização ok e nenhum diagnóstico crítico.';

    const signature = JSON.stringify({ liga_bomba, fired: fired.map(f=>f.id), estop, statusText });
    if (signature !== lastSignature || forceLog) {
      if (estop) pushLog('ESD-100 acionado — motores desarmados, LIGA_BOMBA = 0.');
      else if (fired.length) pushLog(fired.map(f => f.id).join('+') + ' → ' + statusText + ', LIGA_BOMBA = ' + (liga_bomba?1:0));
      else pushLog('Varredura ok — LIGA_BOMBA = ' + (liga_bomba?1:0));
      lastSignature = signature;
    }
  }

  pushLog('SCADA-Core inicializado. Varredura contínua ativa.');
  recompute(true);
});

/* ============ DECK DE SLIDES (Apresentação) ============ */
(function () {
  const slidesData = [
    {
      kicker: "Abertura",
      title: "Lógica formal para um drone que decide quando não pulverizar",
      body: `<p>Sistema SCADA para um drone agrícola de pulverização: estação de solo + unidade embarcada, com intertravamento provado por lógica proposicional.</p>
             <ul>
               <li><b>Planta:</b> drone agrícola de pulverização + estação de solo</li>
               <li><b>Equipe:</b> Arthur, Caique, Luis Felipe, Marina</li>
               <li><b>Módulo:</b> 01 — Lógica Formal &amp; Sistemas Especialistas</li>
             </ul>`
    },
    {
      kicker: "O projeto",
      title: "Duas frentes, um mesmo intertravamento",
      body: `<p>Estação de solo (preparo e abastecimento) e unidade embarcada (pulverização em voo) precisam ser enxergadas ao mesmo tempo pelo SCADA.</p>
             <ul>
               <li><b>Monitorar</b> nível, vazão, pressão, bateria, altitude e posição de voo</li>
               <li><b>Bloquear</b> decolagem e pulverização diante de risco</li>
               <li><b>Diagnosticar</b> causa raiz (bico entupido, mangueira rompida, cavitação)</li>
               <li><b>Registrar</b> histórico para rastreabilidade agronômica</li>
             </ul>`
    },
    {
      kicker: "Arquitetura",
      title: "Campo → Aquisição → Servidor SCADA → HMI",
      body: `<p>Sensores e atuadores em campo (solo + drone) alimentam um RTU embarcado, que transmite telemetria para o servidor SCADA — responsável pelo intertravamento, motor de diagnóstico e histórico — exibido na HMI do operador.</p>`
    },
    {
      kicker: "Aula 02 · Representação simbólica",
      title: "Do sensor 4–20 mA à proposição booleana",
      body: `<p>Cada grandeza contínua vira uma proposição <code>p ∈ {0,1}</code> por histerese, evitando <em>chattering</em> perto do limiar (norma ISA 5.1).</p>
             <ul>
               <li><b>DRN_LT_01</b> — nível de calda: crítico &lt; 5%</li>
               <li><b>DRN_PT_01</b> — pressão de pulverização: alta &gt; 5 bar</li>
               <li><b>DRN_ET_01</b> — bateria: crítica &lt; 10%</li>
               <li><b>EST_WT_01</b> — vento: alto &gt; 8 m/s</li>
             </ul>`
    },
    {
      kicker: "Aula 03 · Tautologias e contradições",
      title: "Provando que o estado de perigo é impossível",
      body: `<div class="log-box" style="max-height:none; font-size:0.82rem; line-height:1.8;">
               <div>Φ = (e₁ ∧ m₁) ∧ (e₁ → ¬m₁)</div>
               <div>Φ = (e₁ ∧ m₁) ∧ (¬e₁ ∨ ¬m₁)</div>
               <div>Φ = (F ∧ m₁) ∨ (e₁ ∧ F)</div>
               <div>Φ = F</div>
             </div>
             <p>Como Φ ≡ F, a garantia de segurança ¬Φ ≡ V é uma <b>tautologia invariante</b> — não uma coincidência de teste.</p>`
    },
    {
      kicker: "Aulas 04 e 06 · Permissivos e quantificadores",
      title: "De um conectivo a qualquer número de setores",
      body: `<div class="log-box" style="max-height:none; font-size:0.82rem; line-height:1.9;">
               <div>P_takeoff ≡ gps_ok ∧ ¬bat_low ∧ ¬wind_high ∧ ¬e_stop ∧ (Auto ⊕ Manual)</div>
               <div>∃s ∈ S, Obstruído(s) — existe algum setor obstruído</div>
               <div>∀s ∈ S, ¬Obstruído(s) — a barra inteira está íntegra</div>
             </div>
             <p>A Aula 05 minimiza essas expressões (Quine–McCluskey) para caber em menos de um ciclo de scan, mesmo acima de 400 Hz.</p>`
    },
    {
      kicker: "Laboratório virtual",
      title: "Simulador do motor SCADA integrado",
      body: `<p>Mais abaixo, mexa na telemetria ou dispare um dos sete cenários da Aula 10 e veja em tempo real: fatos derivados, permissivos, diagnósticos ativos e o comando final da bomba.</p>
             <p><a href="#simulador" class="btn btn-ghost">Ir para o simulador ↓</a></p>`
    },
    {
      kicker: "Aulas 07–08 · Sistema especialista",
      title: "Base de regras SE...ENTÃO",
      body: `<ul>
               <li><b>R3</b> — bomba ligada ∧ vazão baixa ∧ pressão alta → possível obstrução</li>
               <li><b>R6</b> — bateria crítica → interromper missão</li>
               <li><b>R7</b> — vento alto → suspender pulverização</li>
               <li><b>R8</b> — bomba ligada ∧ pressão baixa ∧ vazão baixa → vazamento ou falha de bomba</li>
             </ul>
             <p>Avaliadas por <b style="color:var(--ink)">forward chaining</b> a cada novo dado de sensor.</p>`
    },
    {
      kicker: "Aula 09 · Motor de inferência",
      title: "Forward chaining vs. backward chaining",
      body: `<p><b style="color:var(--ink)">Forward chaining</b> parte dos fatos dos sensores e encadeia regras até não haver mais conclusão nova — roda a cada scan no simulador.</p>
             <p><b style="color:var(--ink)">Backward chaining</b> parte de uma hipótese (“há risco de obstrução?”) e verifica recursivamente os fatos que a sustentam — útil em auditoria pós-voo.</p>`
    },
    {
      kicker: "Conclusão",
      title: "Etapa 01 concluída",
      body: `<p>O drone agrícola já possui uma camada de segurança formal determinística, com intertravamento provado por tautologia e diagnóstico por sistema especialista.</p>
             <p><a href="https://github.com/marinazakimi/ECAA08--Grupo-06" target="_blank" rel="noopener" class="btn btn-primary">Repositório no GitHub ↗</a></p>`
    }
  ];

  const track = document.getElementById("deckTrack");
  const dotsWrap = document.getElementById("deckDots");
  const counterEl = document.getElementById("slideCurrent");
  const totalEl = document.getElementById("slideTotal");
  const prevBtn = document.getElementById("prevSlide");
  const nextBtn = document.getElementById("nextSlide");
  const deckEl = document.getElementById("deck");

  if (!track) return; // seção não presente nesta página

  let current = 0;

  track.innerHTML = slidesData.map((s, i) => `
    <div class="slide" data-index="${i}">
      <span class="kicker">${s.kicker}</span>
      <h3>${s.title}</h3>
      ${s.body}
    </div>
  `).join("");

  dotsWrap.innerHTML = slidesData.map((_, i) =>
    `<button data-index="${i}" aria-label="Ir para o slide ${i + 1}"></button>`
  ).join("");

  totalEl.textContent = slidesData.length;
  const dots = [...dotsWrap.querySelectorAll("button")];

  function render() {
    track.style.transform = `translateX(-${current * 100}%)`;
    counterEl.textContent = current + 1;
    dots.forEach((d, i) => d.classList.toggle("active", i === current));
    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === slidesData.length - 1;
  }

  function goTo(i) {
    current = Math.max(0, Math.min(slidesData.length - 1, i));
    render();
  }

  prevBtn.addEventListener("click", () => goTo(current - 1));
  nextBtn.addEventListener("click", () => goTo(current + 1));
  dots.forEach((d) => d.addEventListener("click", () => goTo(Number(d.dataset.index))));

  // Setas do teclado só quando o deck está visível na tela
  let deckVisible = false;
  const observer = new IntersectionObserver(
    (entries) => { deckVisible = entries[0].isIntersecting; },
    { threshold: 0.4 }
  );
  observer.observe(deckEl);

  document.addEventListener("keydown", (e) => {
    if (!deckVisible) return;
    if (e.key === "ArrowRight") goTo(current + 1);
    if (e.key === "ArrowLeft") goTo(current - 1);
  });

  render();
})();
