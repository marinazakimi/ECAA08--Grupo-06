# Aula 10 – Avaliação do Módulo 1: Motor Integrado de Intertravamento e Diagnóstico

## Sistema SCADA aplicado a um Drone Agrícola de Pulverização — Grupo 06

---

## 1. Objetivo desta Etapa

Esta aula encerra o **Módulo 1 (Lógica Formal & Sistemas Especialistas)** do projeto SCADA-Core Automática, unindo os dois motores construídos separadamente ao longo das aulas anteriores em um único **Motor SCADA Integrado**:

1. **Motor de Intertravamento** (Aulas 03, 04 e 05) — lógica proposicional estática que define os *permissivos* de decolagem e de pulverização a partir de limiares de segurança (bateria, vento, GPS, tanque vazio), com prova formal de que o estado de perigo é logicamente impossível sob a regra de intertravamento.
2. **Motor de Diagnóstico / Sistema Especialista** (Aulas 07, 08 e 09) — base de regras `SE...ENTÃO` avaliada por **Forward Chaining** (diagnóstico contínuo a partir dos sensores) e **Backward Chaining** (verificação de hipóteses específicas), capaz de identificar causas raiz como obstrução de bicos, vazamento ou falha de pulverização.

O ponto central da avaliação é demonstrar que **nenhum dos dois motores isoladamente é suficiente** para garantir a segurança da planta. O intertravamento reage a limiares estáticos de variáveis individuais, mas não enxerga padrões combinados entre variáveis (como *bomba ligada + vazão baixa + pressão alta*, típico de obstrução). O sistema especialista identifica esses padrões, mas não substitui o bloqueio imediato por bateria crítica, vento severo ou perda de GPS. A união dos dois é o que efetivamente impede a planta de entrar em uma combinação operacional de risco — cumprindo o objetivo geral definido na proposta do projeto.

---

## 2. Recapitulação dos Entregáveis do Módulo 1

| Aula | Tema | Entregável |
|---|---|---|
| 02 | Representação Simbólica | Catálogo de Tags (ISA 5.1) e proposições atômicas do processo |
| 03 | Tautologias e Contradições | Prova formal do intertravamento de emergência (Kill Switch × motores armados) |
| 04 | Lógica Proposicional: Conectivos | Blocos de permissivo de decolagem e de pulverização |
| 05 | Formas Normais | Otimização booleana das expressões de intertravamento |
| 07 | Validade e Inferência Lógica | Regras de inferência (Modus Ponens, Modus Tollens) aplicadas ao diagnóstico de falhas |
| 08 | Base de Conhecimento e Regras | Base de regras `SE...ENTÃO` do sistema especialista |
| 09 | Motor de Inferência | Implementação de Forward Chaining e Backward Chaining |
| **10** | **Avaliação do Módulo 1** | **Motor integrado de Intertravamento e Diagnóstico (esta etapa)** |

---

## 3. Arquitetura do Motor Integrado

```text
Telemetria (sensores da estação de solo + drone)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
Motor de Intertravamento   Motor de Diagnóstico
(permissivos estáticos:    (Forward Chaining sobre
 decolagem / pulverização)  fatos derivados dos sensores)
        │                       │
        └───────────┬───────────┘
                     ▼
         Regra de Fusão (comando final)
   liga_bomba = permissivo_pulverização
                AND NOT diagnostico_crítico
                     │
                     ▼
              SCADA / HMI do operador
```

A função `motor_scada_integrado(telemetria)`, implementada no notebook desta aula, recebe a telemetria completa e:

1. Deriva as booleanas de limiar usadas pelo intertravamento a partir dos mesmos parâmetros definidos na Aula 02 (`bateria < 20% → bat_low`, `vento > 8 m/s → wind_high`, `nível ≤ 3% → tanque vazio`);
2. Calcula os permissivos de decolagem e de pulverização (Aula 04);
3. Executa o motor de diagnóstico por Forward Chaining sobre a mesma telemetria (Aula 09);
4. Cruza os dois resultados: o comando final de acionamento da bomba só é liberado se o intertravamento estático **e** o sistema especialista concordarem que não há risco.

---

## 4. Cenários de Validação

O notebook executa o motor integrado sobre sete cenários operacionais representativos: missão ideal, bateria crítica, vento severo na decolagem, possível obstrução dos bicos, possível vazamento, reservatório vazio e acionamento de emergência em voo.

Os cenários de **obstrução** e **vazamento** são os mais reveladores: o intertravamento estático (que só observa bateria, altitude e tanque vazio) libera a bomba normalmente, mas o motor de diagnóstico identifica o padrão de falha e o comando final bloqueia a pulverização — evidenciando exatamente por que a integração entre os dois motores é necessária.

---

## 5. Validação Formal do Motor Integrado

Nos mesmos moldes da prova de contradição da Aula 03, o notebook prova por **exaustão sobre o espaço de fatos-base** do sistema especialista (256 combinações de 8 fatos: bomba ligada, válvula aberta, vazão baixa, pressão alta, pressão baixa, nível crítico, bateria crítica, vento alto) que **em nenhuma combinação de fatos o motor integrado libera a bomba simultaneamente a um diagnóstico crítico**. Essa verificação exaustiva é a demonstração de que a fusão dos dois motores preserva a propriedade de segurança validada isoladamente em cada um deles no restante do módulo.

---

## 6. Painel de Apresentação (simulação de HMI)

Por fim, o notebook implementa uma função de impressão (`imprimir_painel_hmi`) que consolida permissivos, diagnósticos ativos e o comando final de decisão em um único relatório de texto, simulando como essas informações chegariam ao operador na interface de supervisão (HMI) do sistema SCADA.

---

## 7. Implementação

A implementação completa (funções reconstruídas dos dois motores, função de fusão, bateria de cenários, prova de exaustão e painel HMI) está no notebook:

`10_Avaliacao_Motor_Integrado_SCADA.ipynb`

O notebook foi executado integralmente sem erros e contém, em sequência:

1. Reconstrução do motor de intertravamento (operadores lógicos, permissivos de decolagem e pulverização, prova de contradição do estado de perigo);
2. Reconstrução do motor de diagnóstico (base de regras, Forward Chaining, Backward Chaining, conversão de medições em fatos);
3. Função `motor_scada_integrado`, que funde os dois motores em um único comando de decisão;
4. Bateria de sete cenários operacionais consolidados em tabela;
5. Prova formal exaustiva de que a fusão preserva a segurança da planta;
6. Painel de apresentação estilo HMI.

---

## 8. Considerações Finais

A avaliação do Módulo 1 demonstra que a segurança de um sistema SCADA crítico não pode depender de um único paradigma de raciocínio lógico. Limiares estáticos de intertravamento são indispensáveis para reações imediatas (perda de GPS, bateria crítica, emergência), mas insuficientes para diagnosticar falhas cujo sintoma só emerge da combinação de múltiplas variáveis ao longo do tempo — papel que cabe ao sistema especialista baseado em regras.

O motor `motor_scada_integrado` construído nesta etapa representa a interface que o sistema SCADA do drone agrícola utilizará para transformar telemetria bruta em permissivos, diagnósticos e comandos de atuação seguros, servindo de base para os módulos seguintes do projeto (otimização de rotas por grafos, planejamento de manutenção, mitigação de inundação de alarmes por árvores e gestão de permissões por relações de ordem).
