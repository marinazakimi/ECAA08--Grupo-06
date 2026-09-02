# Aula 06 – Lógica de Predicados e Quantificadores em Redes de Sensores

## Sistema SCADA aplicado a um Drone Agrícola de Pulverização — Grupo 06

---

### 1. Objetivo Pedagógico e de Engenharia

Capacitar o futuro Engenheiro de Controle e Automação a expressar regras de varredura de estado que **escalam com o número de sensores** da planta, utilizando **Lógica de Predicados** de primeira ordem sobre coleções de ativos industriais — no caso do drone agrícola, os setores da barra de pulverização e a rede completa de telemetria (estação de solo + drone). Em vez de escrever uma expressão booleana fixa por sensor, o estudante aprende a definir predicados parametrizados $P(x)$ e a avaliá-los sobre um domínio $U$ através dos quantificadores $\forall$ (universal) e $\exists$ (existencial).

---

### 2. Fundamentação Teórica Expandida

Enquanto a lógica proposicional (Aulas 03–05) trata sentenças atômicas indivisíveis, a **Lógica de Predicados** permite parametrizar propriedades sobre domínios finitos de ativos:

1. **Predicado $P(x)$:** função booleana $P: U \rightarrow \{0, 1\}$, onde $U$ é o universo de discurso (ex: conjunto de setores de pulverização $\mathcal{S}$, conjunto de sensores da rede $\mathcal{R}$).
2. **Quantificador Universal ($\forall x \in U,\; P(x)$):** verdadeiro se e somente se $P(x)$ é verdadeiro para **todos** os elementos do domínio. Em domínio finito $U = \{x_1, \dots, x_n\}$:
   $$\forall x\, P(x) \equiv P(x_1) \land P(x_2) \land \dots \land P(x_n)$$
3. **Quantificador Existencial ($\exists x \in U,\; P(x)$):** verdadeiro se **ao menos um** elemento do domínio satisfaz $P(x)$. Em domínio finito:
   $$\exists x\, P(x) \equiv P(x_1) \lor P(x_2) \lor \dots \lor P(x_n)$$
4. **Equivalências de De Morgan Quantificadas:**
   $$\neg (\forall x\, P(x)) \equiv \exists x\, \neg P(x) \qquad\qquad \neg (\exists x\, P(x)) \equiv \forall x\, \neg P(x)$$

Essas equivalências são a extensão direta do Teorema de De Morgan já demonstrado sobre proposições atômicas na Aula 02, agora aplicado a coleções inteiras de instrumentos.

---

### 3. Aplicação no Drone Agrícola: Dois Domínios de Varredura

O notebook desta aula trabalha sobre dois domínios distintos, ambos derivados do catálogo de tags da Aula 02:

**Domínio 1 — Barra de Pulverização Setorizada ($\mathcal{S}$).** As válvulas seccionadoras (`DRN_XV_01`) permitem controlar quais setores dos bicos permanecem ativos durante a aplicação. Cada seção recebe seu próprio par de sensores de pressão e vazão (`DRN_PT_01x` / `DRN_FT_01x`). O predicado de interesse é:

$$\text{Obstruido}(s) \iff \text{bomba ligada}(s) \land \text{pressao}(s) \ge 4.5\text{ bar} \land \text{vazao}(s) \le 0.4\text{ L/min}$$

— a mesma condição da regra R3 do motor de diagnóstico (Aula 09), agora parametrizada por setor $s \in \mathcal{S}$.

**Domínio 2 — Rede Completa de Telemetria ($\mathcal{R}$).** Reúne todos os instrumentos da estação de solo e do drone (`EST_LT_01`, `EST_WT_01`, `EST_TT_01`, `DRN_LT_01`, `DRN_PT_01`, `DRN_FT_01`, `DRN_ET_01`, `DRN_ZT_01`, `DRN_GPS_01`). O predicado de interesse é a integridade de comunicação:

$$\text{FalhaComm}(r) \iff \text{sensor } r \text{ está com telemetria intermitente ou ausente}$$

---

### 4. Expressões Formais de Varredura

$$\text{ExisteObstrucao} \equiv \exists s \in \mathcal{S},\; \text{Obstruido}(s)$$
$$\text{BarraIntegra} \equiv \forall s \in \mathcal{S},\; \neg\text{Obstruido}(s)$$
$$\text{RedeIntegra} \equiv \forall r \in \mathcal{R},\; \neg\text{FalhaComm}(r)$$
$$\text{VarreduraPermiteOperacao} \equiv \text{BarraIntegra} \land \text{RedeIntegra}$$

No notebook, um cenário numérico com 4 setores de pulverização (um deles em obstrução: pressão $5.2$ bar, vazão $0.25$ L/min) e 9 sensores de rede (um deles — `DRN_GPS_01` — com falha de comunicação simulada) é avaliado com os operadores `FORALL`/`EXISTS`, confirmando que `ExisteObstrucao = True`, `BarraIntegra = False` e `RedeIntegra = False`.

---

### 5. Aplicação Prática em Controle e Automação

- **Escalabilidade da lógica de alarmes:** a regra R3 do motor de diagnóstico (Aula 09) foi originalmente escrita para uma única linha de pulverização. Com o predicado `Obstruido(s)` e o quantificador $\exists$, a mesma lógica passa a valer para qualquer número de setores instalados na barra, sem necessidade de reescrever a base de regras.
- **Pré-requisito de integridade de rede:** o predicado $\forall r, \neg\text{FalhaComm}(r)$ funciona como uma verificação **anterior** aos permissivos de decolagem e pulverização (Aula 04) — não há sentido em avaliar `gps_ok` ou `bat_low` se o canal de telemetria correspondente está intermitente.
- **Diagnóstico setorial mais preciso:** ao identificar *qual* setor específico está obstruído (e não apenas que "existe uma obstrução" na planta como um todo), a HMI pode direcionar o operador diretamente ao bico com problema.

---

### 6. Mapeamento para Provas e Exames Tecnológicos

- **Equivalências de De Morgan Quantificadas:** $\neg(\forall x\, P(x)) \equiv \exists x\, \neg P(x)$ e $\neg(\exists x\, P(x)) \equiv \forall x\, \neg P(x)$, verificadas computacionalmente no notebook sobre os dois domínios da planta.
- **Redução de quantificadores a álgebra proposicional:** todo $\forall$/$\exists$ sobre um conjunto finito é redutível a uma cadeia de conjunções/disjunções (Aulas 03–05), permitindo reaproveitar toda a álgebra booleana já demonstrada nessas aulas.

---

### 7. Análise de Erros Conceituais e Numéricos

- **Quantificador Universal sobre Domínio Vazio (*Vacuous Truth*):** se a lista de setores estiver vazia (nenhum sensor cadastrado), `FORALL` retorna `True` por definição matemática — o sistema reportaria "todos os setores OK" sem ter verificado sensor algum. É essencial garantir que o domínio nunca esteja vazio em operação real antes de confiar no resultado da varredura.
- **Troca indevida de $\forall$ por $\exists$ no permissivo geral:** usar $\exists s, \neg\text{Obstruido}(s)$ no lugar de $\forall s, \neg\text{Obstruido}(s)$ liberaria a pulverização assim que **um único** setor estivesse saudável, ignorando obstruções nos demais — um erro de modelagem que mascararia falhas reais.
- **Confundir "falha de comunicação" com "leitura fora da faixa":** um sensor com falha de comunicação não fornece leitura confiável alguma; tratá-lo como se estivesse reportando um valor normal (ex: assumir pressão = 0 na ausência de dado) pode mascarar tanto uma obstrução quanto uma ruptura de mangueira.

---

### 8. Entregável da Aula 06

**Módulo de Varredura de Estado:** implementação em Python dos operadores `FORALL` e `EXISTS` genéricos, aplicados sobre a barra de pulverização setorizada e sobre a rede completa de telemetria do sistema SCADA, consolidados na função `motor_varredura_estado()`.

A implementação completa está no notebook:

`06_Quantificadores_e_Predicados_em_Redes_de_Sensores.ipynb`

O notebook contém, em sequência:

1. Definição dos operadores genéricos `FORALL` e `EXISTS`;
2. Modelo da barra de pulverização setorizada e avaliação do predicado de obstrução por setor;
3. Modelo da rede completa de telemetria e avaliação do predicado de falha de comunicação;
4. Verificação computacional das equivalências de De Morgan quantificadas;
5. Função `motor_varredura_estado()`, que consolida os dois domínios em um único resultado de varredura.

---

### 9. Considerações Finais

Este notebook estendeu a lógica proposicional das Aulas 03–05 para a **Lógica de Predicados**, introduzindo os quantificadores $\forall$ e $\exists$ como mecanismo de varredura sobre coleções de sensores. A principal contribuição prática é a generalização das regras de alarme e permissivo: em vez de reescrever expressões booleanas para cada novo sensor ou setor instalado na planta, o sistema SCADA passa a expressar suas regras em função de um domínio de instrumentos, tornando a lógica de segurança escalável. O módulo de varredura aqui implementado complementa o motor de intertravamento (Aula 04) e generaliza a regra de obstrução do motor de diagnóstico (Aula 09), sendo consolidado com os demais motores na avaliação do Módulo 1 (Aula 10).
