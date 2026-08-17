# Lógica Proposicional — Conectivos e Blocos de Permissivos

## 1. Fundamentos Matemáticos: Conectivos Lógicos

Na matemática discreta, uma **proposição** é uma sentença declarativa que assume um e apenas um valor-verdade: **Verdadeiro** ($1$) ou **Falso** ($0$).

No contexto da nossa arquitetura SCADA para o Drone Agrícola, as operações sobre as variáveis de telemetria são definidas pelos operadores lógicos fundamentais:
1. **Negação ($\neg A$ ou $\bar{A}$):** Inverte o valor da proposição (ex: indicar que um alarme de bateria crítica não está ativo).
2. **Conjunção ($A \land B$):** Verdadeira se e somente se ambos forem verdadeiros. Modela **permissivos de decolagem** (todas as condições de segurança devem ser atendidas simultaneamente).
3. **Disjunção ($A \lor B$):** Verdadeira se ao menos um for verdadeiro. Modela **falhas ou intertravamentos** (qualquer alarme crítico aciona a parada).
4. **Disjunção Exclusiva ($A \oplus B$):** Verdadeira se exatamente um for verdadeiro. Define modos de voo estritamente excludentes ($\text{Auto} \oplus \text{Manual}$).
5. **Implicação / Condicional ($A \rightarrow B$):** $\neg A \lor B$. Modela regras do tipo "SE houver bloqueio nos bicos, ENTÃO aborte a pulverização".
6. **Bicondicional ($A \leftrightarrow B$):** Modela estados operacionais equivalentes.

---

## 2. Aplicação no Drone Agrícola: Permissivos de Operação

Para garantir a segurança do equipamento e da lavoura, um **permissivo de partida** (*Start Permissive*) é uma condição booleana rigorosa. Sem ela, a controladora de voo recusa o comando de armar os motores.

### 2.1. Permissivo de Decolagem (*Takeoff*)
Para que o drone receba autorização para decolar ($cmd_{\text{takeoff}}$), as seguintes condições devem ser garantidas pelos sensores embarcados:
* Sinal de GPS fixado com precisão: $gps\_ok$
* Nível de bateria seguro (não crítico): $\neg bat\_low$
* Velocidade do vento abaixo do limite operacional: $\neg wind\_high$
* Sem acionamento do botão de emergência na estação (*Kill Switch*): $\neg e\_stop$
* Modo de voo inequivocamente definido: $\text{Auto} \oplus \text{Manual}$

$$P_{\text{takeoff}} \equiv gps\_ok \land \neg bat\_low \land \neg wind\_high \land \neg e\_stop \land (\text{Auto} \oplus \text{Manual})$$

```mermaid
graph LR
    L1["gps_ok (GPS Fixado)"] --> AND["Bloco AND (Conjunção)"]
    L2["¬ bat_low (Bateria OK)"] --> AND
    L3["¬ wind_high (Vento OK)"] --> AND
    L4["¬ e_stop (Sem Emergência)"] --> AND
    L5["Auto XOR Manual"] --> AND


    AND --> Permissivo["Permissivo de Decolagem (True/False)"]
