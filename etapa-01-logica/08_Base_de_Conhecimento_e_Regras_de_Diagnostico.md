# Aula 08 – Sistemas Baseados em Conhecimento: Base de Conhecimento & Regras de Produção SE-ENTÃO

---

### 1. Objetivo Pedagógico e de Engenharia
Capacitar o futuro Engenheiro de Controle e Automação a modelar, estruturar e implementar uma **Base de Conhecimento Especialista** e um **Sistema Baseado em Regras de Produção (RBS - *Rule-Based System*)** no software supervisório SCADA. O estudante aprenderá a formalizar o raciocínio heurístico de diagnóstico através de regras no formato canônico $\text{SE } \langle \text{Condições} \rangle \text{ ENTÃO } \langle \text{Consequentes/Ações} \rangle$, tratando acoplamentos multivariáveis (hidráulicos, elétricos, mecânicos e ambientais) e aplicando algoritmos determinísticos de **resolução de conflito** (prioridade estática, especificidade e recência temporal) para identificação precisa da causa-raiz de anomalias operacionais.

---

### 2. Fundamentação Teórica Expandida (Perspectiva Discreta e Contínua)

#### 2.1. Arquitetura Clássica de um Sistema Baseado em Conhecimento
Em automação industrial de missão crítica, a camada de diagnóstico especialista opera sobre três componentes interconectados:
1. **Memória de Trabalho (WM - *Working Memory*):** Armazena os fatos dinâmicos conhecidos no instante de amostragem discreto $k$, incluindo as grandezas físicas analógicas amostradas $\mathbf{x}[k] \in \mathbb{R}^n$, as proposições quantizadas $\mathbf{p}[k] \in \mathbb{B}^n$ e os fatos inferidos durante o ciclo de varredura.
2. **Base de Conhecimento (KB - *Knowledge Base*):** Conjunto estático de regras declarativas $\mathcal{R} = \{R_1, R_2, \dots, R_m\}$ construído por engenheiros especialistas a partir de modelos físicos do processo, manuais de manutenção e árvores de falhas (FTA - *Fault Tree Analysis*).
3. **Motor de Inferência (*Inference Engine*):** Núcleo computacional que executa o ciclo de três fases: **Casamento de Padrões (*Match*)** $\to$ **Resolução de Conflitos (*Conflict Resolution*)** $\to$ **Execução / Disparo (*Act / Fire*)**.

```
                   SISTEMA SUPERVISÓRIO SCADA - MÓDULO ESPECIALISTA
 +-----------------------------------------------------------------------------------+
 |  TELEMETRIA DO DRONE & ESTAÇÃO DE SOLO                                           |
 |  (DRN_PT_01, DRN_FT_01, DRN_LT_01, DRN_ET_01, EST_LT_01, EST_WT_01)               |
 +-----------------------------------------------------------------------------------+
                                           │
                                           ▼ (Amostragem Ts & Histerese)
 +-----------------------------------------------------------------------------------+
 |  MEMÓRIA DE TRABALHO (WORKING MEMORY - FATOS DINÂMICOS NO INSTANTE k)             |
 |  Fatos = {Bomba_Ligada, Pressao_Alta, Vazao_Baixa, Vento_Moderado, ...}           |
 +-----------------------------------------------------------------------------------+
                 │                                                   ▲
                 │ (1. Casamento de Padrões / Match)                 │ (3. Disparo /
                 ▼                                                   │     Assert de Fatos)
 +─────────────────────────────────+             +───────────────────┴───────────────+
 | BASE DE CONHECIMENTO (KB)       |             | MOTOR DE INFERÊNCIA               |
 | R1: SE Pressao_Alta & ...       | ──────────► | • Identifica Conjunto de Conflito |
 | R2: SE Ruptura_Linha ...        |  (Regras    | • Aplica Prioridade & Especif.    |
 | R3: SE Descarga_LiPo ...        |   Ativadas) | • Dispara Ações Mitigadoras       |
 +─────────────────────────────────+             +───────────────────────────────────+
```

#### 2.2. Sintaxe e Semântica Formal das Regras de Produção
Cada regra $R_i \in \mathcal{R}$ é uma implicação lógica com estrutura:
$$R_i: \text{SE } \phi_i(\mathbf{x}[k]) \text{ ENTÃO } \psi_i(\mathbf{y}[k]), \quad \text{com prioridade } \rho_i \in \mathbb{Z}^+$$

* **Antecedente / Premissa (LHS - *Left-Hand Side*):** $\phi_i$ é uma expressão booleana combinacional construída com proposições atômicas $P_j$, quantificadores $(\forall, \exists)$ e conectivos $(\land, \lor, \neg)$:
  $$\phi_i = \bigwedge_{j \in S_i} P_j[k] \lor \bigvee_{l \in T_i} Q_l[k]$$
* **Consequente / Ação (RHS - *Right-Hand Side*):** $\psi_i$ define as operações atômicas executadas quando a regra dispara:
  1. $\text{Assert}(F)$ — Insere um novo fato $F$ na Memória de Trabalho (ex: $\text{Fato}(\text{Causa\_Raiz} = \text{Bico\_Obstruido})$).
  2. $\text{Retract}(F)$ — Remove um fato que se tornou inválido.
  3. $\text{ExecuteAction}(A)$ — Emite um comando de controle ou alarme (ex: desligar bomba, iniciar RTH, buzina na IHM).

#### 2.3. Taxonomia das Regras de Diagnóstico do AgroDrone
A Base de Conhecimento do sistema SCADA integra os 4 subsistemas fundamentais:
1. **Subsistema Hidráulico (Calda & Bombeamento):**
   * *R1 (Obstrução de Bicos):* Bomba acionada + Alta Pressão + Baixa Vazão.
   * *R2 (Ruptura de Tubulação):* Bomba acionada + Baixa Pressão + Alta Vazão.
   * *R3 (Cavitação da Bomba):* Bomba acionada + Nível Crítico no Reservatório.
   * *R4 (Filtro de Sucção Saturado):* Bomba acionada + Alta Corrente na Bomba + Baixa Vazão + Pressão Normal/Baixa.
2. **Subsistema Elétrico & Bateria LiPo:**
   * *R5 (Descarga Rápida / Curto):* Corrente $I_{bat} > 55\text{ A}$ + Taxa de queda $\frac{dV}{dt} < -0.2\text{ V/s}$.
   * *R6 (Desbalanceamento Severo):* $\max(V_{cell}) - \min(V_{cell}) > 0.08\text{ V}$.
   * *R7 (Sobreaquecimento de ESC/Motor):* $\exists m \in \{1..6\}, T_{esc}(m) > 65^\circ\text{C}$.
3. **Subsistema Aerodinâmico e Meteorológico:**
   * *R8 (Risco de Deriva Química Severa):* Vento $v_{wind} > 15\text{ km/h}$ + Pulverização Ativa.
   * *R9 (Perda de Eficiência por Evaporação):* Temperatura $T_{amb} > 32^\circ\text{C}$ + Umidade $UR < 35\%$.
4. **Subsistema de Instrumentação (Validação de Sensores / Sensor Fault):**
   * *R10 (Sensor de Pressão Travado / Frozen):* Bomba desligada + Pressão $> 2.0\text{ bar}$ por mais de $2.0\text{ s}$.

#### 2.4. Mecanismos Formais de Resolução de Conflitos
Quando múltiplos antecedentes tornam-se simultaneamente verdadeiros na Memória de Trabalho, forma-se o **Conjunto de Conflito (*Conflict Set*)** $\mathcal{C} = \{R_{i_1}, R_{i_2}, \dots, R_{i_k}\}$. Três estratégias canônicas determinam a ordem de disparo:
1. **Prioridade Estática (Criticidade de Segurança):**
   $$\rho(R_a) > \rho(R_b) \implies R_a \text{ dispara antes de } R_b$$
   *Nível 4 (Emergência / Risco Imediato de Queda)* $>$ *Nível 3 (Dano a Atuador / Ruptura)* $>$ *Nível 2 (Perda Agronômica)* $>$ *Nível 1 (Informativo)*.
2. **Especificidade de Antecedentes (Princípio da Subsunção):**
   Se o conjunto de condições de $R_a$ é um superconjunto estrito das condições de $R_b$ ($Cond(R_b) \subset Cond(R_a)$), $R_a$ é mais específica e deve ter precedência.
3. **Recência Temporal (*Recency*):**
   Regras cujos antecedentes casam com fatos produzidos no ciclo $k$ mais recente têm precedência sobre fatos legados de ciclos anteriores.

---

### 3. Formulação Matemática e Exemplo Numérico

#### Base de Regras Formal do SCADA AgroDrone:

| Regra | Nome da Regra | Antecedente Booleano $\phi_i$ | Consequente $\psi_i$ (Ação / Diagnóstico) | Prioridade $\rho$ |
|:---:|:---|:---|:---|:---:|
| $R_1$ | `OBSTRUCAO_BICOS` | $P_{PUMP\_ON} \land P_{PRESS\_HIGH} \land P_{FLOW\_LOW}$ | Assert(`FALHA_OBSTRUCAO_HIDRAULICA`), Inibir Bomba | $3$ |
| $R_2$ | `RUPTURA_TUBULACAO`| $P_{PUMP\_ON} \land P_{PRESS\_LOW} \land P_{FLOW\_HIGH}$ | Assert(`FALHA_RUPTURA_VAZAMENTO`), Corte Imediato Bomba | $4$ |
| $R_3$ | `CAVITACAO_BOMBA` | $P_{PUMP\_ON} \land P_{DRN\_EMPTY}$ | Assert(`ALERTA_CAVITACAO_RESERVATORIO_VAZIO`), Desligar | $3$ |
| $R_4$ | `DESCARGA_CRITICA` | $P_{CORRENTE\_ALTA} \land P_{TAXA\_QUEDA\_RAPIDA}$ | Assert(`EMERGENCIA_BATERIA_RTH`), Comandar Auto-RTH | $4$ |
| $R_5$ | `DERIVA_VENTO` | $P_{VENTO\_ALTO} \land P_{PUMP\_ON}$ | Assert(`ALERTA_DERIVA_SUSPENDER_APLICACAO`), Pausar | $2$ |
| $R_6$ | `SENSOR_PRESS_TRAV`| $\neg P_{PUMP\_ON} \land P_{PRESS\_HIGH}$ | Assert(`FALHA_SENSOR_DRN_PT_01_FROZEN`), Log Manutenção | $1$ |

#### Exemplo Numérico Passo a Passo:
Considere o vetor de telemetria física amostrado no passo $k=100$:
* Pressão: $	ext{DRN\_PT\_01}[100] = 5.4	ext{ bar}$ (Limiar Alto: $4.5	ext{ bar}$)
* Vazão: $	ext{DRN\_FT\_01}[100] = 0.18	ext{ L/min}$ (Limiar Baixo: $0.4	ext{ L/min}$)
* Nível do Tanque: $	ext{DRN\_LT\_01}[100] = 14.0\%$ (Limiar Crítico: $3.0\%$)
* Bomba PWM: $	ext{DRN\_PMP\_01}[100] = 70\%$ ($P_{PUMP\_ON} = 1$)
* Vento: $	ext{EST\_WT\_01}[100] = 18.2	ext{ km/h}$ (Limiar Vento: $15.0	ext{ km/h}$)
* Corrente Bateria: $	ext{DRN\_ET\_01}[100] = 32.0	ext{ A}$ (Normal $< 55	ext{ A}$)

**Resolução e Raciocínio Dedutivo:**
1. **Fase 1: Binarização e Quantização na Memória de Trabalho (WM):**
   * $P_{PRESS\_HIGH} = \mathcal{I}(5.4 \ge 4.5) = 1$
   * $P_{FLOW\_LOW} = \mathcal{I}(0.18 \le 0.4) = 1$
   * $P_{PRESS\_LOW} = \mathcal{I}(5.4 \le 1.2) = 0$
   * $P_{FLOW\_HIGH} = \mathcal{I}(0.18 \ge 3.0) = 0$
   * $P_{DRN\_EMPTY} = \mathcal{I}(14.0 \le 3.0) = 0$
   * $P_{VENTO\_ALTO} = \mathcal{I}(18.2 \ge 15.0) = 1$
   * $P_{CORRENTE\_ALTA} = \mathcal{I}(32.0 \ge 55.0) = 0$

2. **Fase 2: Casamento de Padrões (*Pattern Matching*):**
   * $\phi(R_1) = 1 \land 1 \land 1 = 1 \implies R_1 	ext{ Ativada}$ (Obstrução de Bicos).
   * $\phi(R_2) = 1 \land 0 \land 0 = 0 \implies R_2 	ext{ Inativa}$.
   * $\phi(R_3) = 1 \land 0 = 0 \implies R_3 	ext{ Inativa}$.
   * $\phi(R_4) = 0 \land 0 = 0 \implies R_4 	ext{ Inativa}$.
   * $\phi(R_5) = 1 \land 1 = 1 \implies R_5 	ext{ Ativada}$ (Deriva por Vento).
   * $\phi(R_6) = 0 \land 1 = 0 \implies R_6 	ext{ Inativa}$.

3. **Fase 3: Resolução de Conflitos:**
   * Conjunto de Conflito: $\mathcal{C} = \{R_1 (
ho=3), R_5 (
ho=2)\}$.
   * Critério de Prioridade Estática: $
ho(R_1) = 3 > 
ho(R_5) = 2$.
   * Ordem de Execução: $R_1$ dispara primeiro, isolando a falha hidráulica crítica (corta a bomba). Em seguida, $R_5$ registra o alerta agronômico de vento.

4. **Conclusão:** O sistema SCADA asserta `FALHA_OBSTRUCAO_HIDRAULICA`, emite comando de interrupção do PWM da bomba e impede o sobreaquecimento do motor de pressurização.

---

### 4. Aplicação Prática em Controle e Automação
1. **Mitigação do Fenômeno de Inundação de Alarmes (*Alarm Flood* - Norma ISA 18.2):** Ao cruzar pressão, vazão e status da bomba em uma única regra de produção, o sistema evita disparar 4 alarmes isolados ("Pressão Alta", "Vazão Baixa", "Bomba Sobrecarga", "Erro de Dosagem"), sintetizando-os em um **único diagnóstico de causa-raiz**: *"Obstrução de Bicos Centrífugos"*.
2. **Reconfiguração Automática de Malhas de Controle:** A asserção de fatos pela base de regras aciona blocos de lógica de segurança no CLP, reconfigurando os ganhos do controlador PID de voo ou forçando modos degradados seguros (*Safe-State Fallback*).
3. **Geração de Ordens de Serviço Inteligentes:** O diagnóstico emite relatórios com código de falha padronizado e instrução precisa para a equipe de campo (*"Efetuar retrolavagem e troca de filtros de linha"*).

---

### 5. Mapeamento para Provas e Exames Tecnológicos
* **Algoritmo Rete (Forgy, 1982):** Algoritmo de casamento de padrões compilado em grafo acíclico dirigido (DAG) com nós-$alpha$ (testes em variáveis individuais) e nós-$\beta$ (junções relacionais), otimizando a avaliação de milhares de regras em $O(1)$ por amostra.
* **Sistemas de Manutenção de Verdade (TMS - *Truth Maintenance Systems*):** Gestão de dependências entre fatos e retração não-monotônica quando as premissas deixam de ser válidas.
* **Propriedades da Base de Conhecimento:**
  * *Consistência:* Ausência de regras contraditórias ($A 	o B$ e $A 	o 
eg B$).
  * *Completude:* Existência de pelo menos uma regra para cada estado operacional crítico.
  * *Ortogonalidade:* Minimização de regras redundantes com os mesmos efeitos.

---

### 6. Análise de Erros Conceituais e Numéricos
* **Regras com Dependências Cíclicas Infinitas:** Criar regras encadeadas sem ponto de parada determinístico (ex: $A 	o B$ e $B 	o A$), causando estouro de pilha (*stack overflow*) no motor de inferência.
* **Falta de Retração de Fatos Obsoletos (*Fact Leakage*):** Não remover o fato `FALHA_PRESSAO_ALTA` quando a pressão volta ao valor nominal, mantendo a IHM em estado de alarme permanente.
* **Casamento de Padrões sem Histerese em Variáveis Analógicas:** Avaliar condições diretamente sobre sinais ruidosos ($P > 4.5$), provocando disparos e cancelamentos alternados da regra a cada ciclo de relógio.

---

### 7. Implementação Didática em Python (Notebook)
Implementação de um motor de regras especialista orientado a objetos com suporte a prioridades, casamento de padrões vetorizado, retração dinâmica de fatos e geração de diagnósticos de telemetria.

