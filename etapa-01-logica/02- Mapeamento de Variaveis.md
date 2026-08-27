## Variáveis do Processo

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/352f2368-8b4b-4e6c-8aca-5d6075ab47f1" />


# Aula 02 – Variáveis de Processo, Insumos & Representação Simbólica em Lógica Booleana

---

### 1. Objetivo Pedagógico e de Engenharia
Capacitar o futuro Engenheiro de Controle e Automação a identificar, classificar e modelar rigorosamente todas as **variáveis de processo (entradas/sensores e saídas/atuadores)** e os **fluxos de insumos** (calda de pulverização, água de preparo, defensivos, energia elétrica) de um sistema SCADA aplicado a um drone agrícola e sua estação de solo. O estudante aprenderá a mapear grandezas físicas contínuas $\mathbb{R}$ em **proposições lógicas booleanas atomísticas $\mathbb{B}$** através de quantizadores com histerese (*Schmitt Triggers discretos*), sintetizando equações de intertravamento, permissivos de bombeamento e diagnóstico de falhas hidráulicas conforme as normas de instrumentação **ISA 5.1** e segurança funcional **IEC 61131-3**.

---

### 2. Fundamentação Teórica Expandida (Perspectiva Discreta e Contínua)

#### 2.1. Arquitetura de Insumos e Balanço de Massa
O processo agroindustrial de pulverização opera com três classes fundamentais de recursos:
1. **Insumos Químicos e Hídricos:** A *calda de pulverização* é um fluido composto homogêneo resultante da mistura estequiométrica de água (veículo carreador, $>95\%$), defensivos agrícolas (princípio ativo: herbicidas, fungicidas ou inseticidas) e adjuvantes químicos (surfactantes que reduzem a tensão superficial e mitigam a deriva por evaporação). A água de lavagem é empregada para descontaminação pós-operação.
2. **Recursos Energéticos:** Energia elétrica da rede/gerador para alimentação dos Controladores Lógicos Programáveis (CLPs), relés e bombas da Estação de Solo; e bancos de baterias eletroquímicas $\text{LiPo } 12\text{S} / 14\text{S}$ ($44.4\text{ V} - 51.8\text{ V}$) para propulsão dos motores brushless (BLDC), telemetria do microcontrolador de bordo e acionamento PWM da bomba hidráulica.
3. **Materiais de Processo e Manutenção:** Elementos filtrantes de malha fina (50 a 100 mesh) para retenção mecânica de impurezas sólidas protegendo bombas e bicos contra entupimento.

<img width="1536" height="1024" alt="WhatsApp Image 2026-08-27 at 10 22 44" src="https://github.com/user-attachments/assets/99e2eafc-d9ee-4e06-aaeb-d87b21516815" />


#### 2.2. Classificação de Variáveis e Instrumentação ISA 5.1
No sistema SCADA integrado (Estação de Solo + Drone), as grandezas físicas são monitoradas por transmissores analógicos e comutadas por atuadores digitais/modulantes:

## Variáveis de Entrada — Sensores

| Malha / Local | Tag ISA 5.1 | Descrição da Variável | Tipo / Instrumento | Faixa de Operação | Unidade SI / Engenharia |
|:---|:---|:---|:---|:---:|:---:|
| Estação de Solo | `EST_LT_01` | Nível do Tanque de Mistura | Sensor Ultrassônico | $0.0 - 100.0$ | $\%$ ($0 - 500\text{ L}$) |
| Estação de Solo | `EST_WT_01` | Velocidade do Vento na Base | Anemômetro de Conchas | $0.0 - 25.0$ | $\text{m/s}$ ($\text{km/h}$) |
| Estação de Solo | `EST_TT_01` | Temperatura Ambiente | Termoresistência PT100 | $-10.0 - 50.0$ | $^\circ\text{C}$ |
| Drone Embarcado | `DRN_LT_01` | Nível de Calda no VANT | Sensor Ultrassônico/Capacitivo | $0.0 - 100.0$ | $\%$ ($0 - 30\text{ L}$) |
| Drone Embarcado | `DRN_PT_01` | Pressão de Pulverização | Transmissor Piezorresistivo | $0.0 - 6.0$ | $\text{bar}$ ($10^5\text{ Pa}$) |
| Drone Embarcado | `DRN_FT_01` | Vazão de Aplicação | Fluxômetro Eletromagnético | $0.0 - 10.0$ | $\text{L/min}$ ($1.667 \times 10^{-4}\text{ m}^3\text{/s}$) |
| Drone Embarcado | `DRN_ET_01` | Tensão / Carga da Bateria | Sensor Hall & Divisor | $0.0 - 52.0$ | $\text{V} \text{ / } \%$ |
| Drone Embarcado | `DRN_ZT_01` | Altitude Relativa sobre a Copa | Radar LiDAR / Barômetro | $0.0 - 50.0$ | $\text{m}$ |
| Drone Embarcado | `DRN_GPS_01` | Posição e Velocidade de Solo | Módulo GNSS RTK Dual | $\text{Lat/Lon / } 0.0 - 15.0$ | $\text{Graus / m/s}$ |

---

## Variáveis de Saída — Atuadores

| Malha / Local | Tag ISA 5.1 | Descrição da Variável | Tipo / Instrumento | Faixa de Operação | Unidade SI / Engenharia |
|:---|:---|:---|:---|:---:|:---:|
| Estação de Solo | `EST_PMP_01` | Bomba de Recirculação | Relé Digital / Contator | $0 \text{ ou } 1$ | $\text{Booleano (Desl/Lig)}$ |
| Estação de Solo | `EST_XV_01` | Válvula de Abastecimento | Solenoide Operada por Piloto | $0 \text{ ou } 1$ | $\text{Booleano (Fech/Aber)}$ |
| Drone Embarcado | `DRN_PMP_01` | Bomba de Pulverização | Driver ESC / PWM de Potência | $0.0 - 100.0$ | $\%$ ($0 - 24\text{ V}$) |
| Drone Embarcado | `DRN_XV_01` | Válvulas Seccionadoras | Solenoides Abre/Fecha Seção | $0 \text{ ou } 1$ | $\text{Booleano (0=Off, 1=On)}$ |

#### 2.3. Dinâmica Temporal Contínua vs Amostragem Discreta do Consumo
A vazão instantânea contínua de calda $q(t)$ em $\text{L/s}$ é integrada no tempo para fornecer o volume consumido $V(t)$ em litros:
$$V(t) = \int_{0}^{t} q(\tau) d\tau \quad [\text{L}]$$

No ambiente digital do SCADA, a telemetria é amostrada com período fixo $T_s > 0$ nos instantes discretos $t_k = k \cdot T_s$ ($k \in \mathbb{Z}^+$). A vazão lida pelo transmissor `DRN_FT_01` no passo $k$ é denotada por $Q[k] = q(k T_s)$ expressa em $\text{L/min}$. A integração numérica trapezoidal discreta do volume consumido acumulado $V_{cons}[k]$ é dada por:
$$V_{cons}[k] = V_{cons}[k-1] + \frac{Q[k] + Q[k-1]}{2} \cdot \left(\frac{T_s}{60}\right) \quad [\text{L}]$$

A dosagem agronômica instantânea aplicada por hectare $D[k]$ ($\text{L/ha}$), em função da velocidade de solo $v_g[k] = \|\mathbf{v}_{GPS}[k]\|$ em $\text{m/s}$ e da largura útil da faixa de pulverização $w$ em metros, é dada por:
$$D[k] = \frac{600 \cdot Q[k]}{v_g[k] \cdot w} \quad [\text{L/ha}]$$

#### 2.4. Mapeamento Simbólico: Binarização por Histerese Discreta
Para a tomada de decisão lógica determinística, as grandezas contínuas $y[k] \in \mathbb{R}$ são mapeadas em proposições booleanas $p[k] \in \mathbb{B} = \{0, 1\}$. Para prevenir comutações rápidas espúrias (*chattering*) induzidas por ruído de medição em torno de um limiar estático $\gamma$, aplica-se a função de quantização com histerese não-linear:
$$p[k] = \mathcal{H}(y[k], \gamma_{low}, \gamma_{high}, p[k-1]) = \begin{cases} 1, & \text{se } y[k] \ge \gamma_{high} \\ 0, & \text{se } y[k] \le \gamma_{low} \\ p[k-1], & \text{se } \gamma_{low} < y[k] < \gamma_{high} \end{cases}$$

---

### 3. Formulação Matemática e Exemplo Numérico

#### Vetor de Proposições Atômicas do AgroDrone:
Definem-se as variáveis booleanas elementares no instante $k$:
* $P_{EST\_OK}[k] \iff \text{EST\_LT\_01}[k] \ge 20.0\%$ (Nível suficiente no tanque da estação de solo).
* $P_{DRN\_LOW}[k] \iff \text{DRN\_LT\_01}[k] \le 10.0\%$ (Nível baixo no reservatório do drone).
* $P_{DRN\_EMPTY}[k] \iff \text{DRN\_LT\_01}[k] \le 3.0\%$ (Reservatório em nível crítico/vazio).
* $P_{PRESS\_HIGH}[k] \iff \text{DRN\_PT\_01}[k] \ge 4.5\text{ bar}$ (Sobrepressão hidráulica na linha).
* $P_{PRESS\_LOW}[k] \iff \text{DRN\_PT\_01}[k] \le 1.2\text{ bar}$ (Pressão insuficiente para nebulização).
* $P_{FLOW\_LOW}[k] \iff \text{DRN\_FT\_01}[k] \le 0.4\text{ L/min}$ (Subvazão na tubulação).
* $P_{FLOW\_HIGH}[k] \iff \text{DRN\_FT\_01}[k] \ge 3.0\text{ L/min}$ (Sobrevazão / fluxo livre).
* $P_{PUMP\_ON}[k] \iff \text{DRN\_PMP\_01}[k] > 5.0\%$ (Comando de bomba ativado).

#### Equações Booleanas de Diagnóstico e Intertravamento:
1. **Alarme de Obstrução de Bicos ($Alarm_{obstr}$):**
   $$Alarm_{obstr}[k] = P_{PUMP\_ON}[k] \land P_{PRESS\_HIGH}[k] \land P_{FLOW\_LOW}[k]$$
2. **Alarme de Ruptura de Mangueira / Vazamento Catastrófico ($Alarm_{rupt}$):**
   $$Alarm_{rupt}[k] = P_{PUMP\_ON}[k] \land P_{PRESS\_LOW}[k] \land P_{FLOW\_HIGH}[k]$$
3. **Alarme de Risco de Cavitação da Bomba ($Alarm_{cavit}$):**
   $$Alarm_{cavit}[k] = P_{PUMP\_ON}[k] \land P_{DRN\_EMPTY}[k]$$
4. **Permissivo de Pulverização Segura ($Perm_{spray}$):**
   $$Perm_{spray}[k] = \neg P_{DRN\_EMPTY}[k] \land \neg Alarm_{obstr}[k] \land \neg Alarm_{rupt}[k]$$
5. **Permissivo de Abastecimento da Estação de Solo ($Perm_{abast}$):**
   $$Perm_{abast}[k] = P_{EST\_OK}[k] \land \neg (\text{DRN\_LT\_01}[k] \ge 95.0\%) \land \neg \text{EST\_PMP\_FALHA}[k]$$

#### Exemplo Numérico Manual Passo a Passo:
Considere a seguinte telemetria registrada no passo $k=42$:
* Nível do Tanque do Drone: $\text{DRN\_LT\_01}[42] = 18.5\%$
* Pressão da Linha: $\text{DRN\_PT\_01}[42] = 5.2\text{ bar}$
* Vazão de Aplicação: $\text{DRN\_FT\_01}[42] = 0.25\text{ L/min}$
* Potência da Bomba: $\text{DRN\_PMP\_01}[42] = 65\%$ ($P_{PUMP\_ON} = 1$)
* Velocidade de Voo: $v_g[42] = 4.0\text{ m/s}$, Faixa $w = 3.0\text{ m}$

**Resolução:**
1. Mapeamento proposicional:
   * $P_{PRESS\_HIGH} = \mathcal{I}(5.2 \ge 4.5) = 1$
   * $P_{FLOW\_LOW} = \mathcal{I}(0.25 \le 0.4) = 1$
   * $P_{DRN\_EMPTY} = \mathcal{I}(18.5 \le 3.0) = 0$
2. Avaliação da Obstrução:
   $$Alarm_{obstr}[42] = 1 \land 1 \land 1 = 1 \quad (\text{Ativado})$$
3. Avaliação da Ruptura:
   $$Alarm_{rupt}[42] = 1 \land \mathcal{I}(5.2 \le 1.2) \land \mathcal{I}(0.25 \ge 3.0) = 1 \land 0 \land 0 = 0 \quad (\text{Desativado})$$
4. Avaliação do Permissivo:
   $$Perm_{spray}[42] = \neg(0) \land \neg(1) \land \neg(0) = 1 \land 0 \land 1 = 0 \quad (\text{Bloqueia Imediatamente a Bomba})$$
5. Dosagem calculada caso estivesse desobstruído com vazão nominal $Q=1.2\text{ L/min}$:
   $$D = \frac{600 \cdot 1.2}{4.0 \cdot 3.0} = \frac{720}{12} = 60.0\text{ L/ha}$$

---

### 4. Aplicação Prática em Controle e Automação
A unificação de insumos, instrumentação e lógica simbólica possibilita:
1. **Controle em Malha Fechada de Dosagem Constante:** Ajuste contínuo do PWM de `DRN_PMP_01` por um controlador PI digital para compensar variações instantâneas de velocidade de solo e vento.
2. **Rastreabilidade e Telemetria Histórica (Data Logging):** Armazenamento em banco de dados de séries temporais com volume total aplicado ($\text{L}$), rendimento operacional ($\text{ha/h}$), consumo médio ($\text{L/ha}$) e registros de alarmes conforme normas do MAPA.
3. **Automação Segura do Abastecimento:** Intertravamento físico da válvula `EST_XV_01` impedindo transbordamentos e operação a seco da bomba de recirculação `EST_PMP_01`.

---

### 5. Mapeamento para Provas e Exames Tecnológicos
* **Norma ISA 5.1 (Simbologia e Identificação):** A primeira letra identifica a variável medida ($L=\text{Level}$, $F=\text{Flow}$, $P=\text{Pressure}$, $T=\text{Temperature}$, $W=\text{Weight/Wind}$, $Z=\text{Position/Height}$); as letras subsequentes indicam a função do instrumento ($T=\text{Transmitter}$, $V=\text{Valve}$, $C=\text{Controller}$, $A=\text{Alarm}$).
* **Formulação de Intertravamentos Combinacionais:** Dedução de equações booleanas a partir de matrizes de causa e efeito (*Cause & Effect Matrix* / C&E Chart).
* **Teorema de De Morgan em Diagnóstico:** Demonstrar que a negação de ausência de falha $(\neg (Alarm_A \lor Alarm_B))$ equivale ao funcionamento simultaneamente saudável de todos os subsistemas $(\neg Alarm_A \land \neg Alarm_B)$.

---

### 6. Análise de Erros Conceituais e Numéricos
* **Ruído de Medição sem Histerese (Efeito Chattering):** Implementar comutação com limiar único $P = (Nivel > 10.0)$, gerando dezenas de transições $0 \leftrightarrow 1$ por segundo em regime turbulento com oscilação de líquido no tanque.
* **Incompatibilidade Dimensional em Fórmulas de Dosagem:** Omitir a constante de conversão $600$ e misturar $\text{L/min}$ com $\text{m/s}$ e $\text{m}$, resultando em erros de dosagem por fatores de escala de até $1000\times$.
* **Integração Retangular Simples (Euler Explícito) sob Altas Variações:** Integrar vazões rápidas via $V[k] = V[k-1] + Q[k] \Delta t$ em vez da regra trapezoidal, acumulando erros de truncamento numérico significativos em missões longas.


