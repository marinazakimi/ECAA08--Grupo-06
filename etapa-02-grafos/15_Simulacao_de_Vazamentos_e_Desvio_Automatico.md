# Aula 15 — Simulação de vazamentos e desvio automático

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

## Objetivo

Integrar o diagnóstico lógico da Etapa 1 à atualização da rede. O evento injetado informa um **trecho conhecido pelo simulador**; os sensores globais de pressão e vazão não permitem localizar sozinhos a mangueira rompida. Baixa pressão com baixa vazão continua gerando a hipótese `possivel_vazamento_ou_falha_bomba`, sem declarar certeza causal.

## Sequência implementada

1. Reter a ocorrência da falha e emitir comando simulado de bomba desligada e válvulas de pulverização fechadas.
2. Marcar o trecho e seu ramal como indisponíveis no modelo. Para e05/e06, solicitar o isolamento das duas extremidades do filtro principal.
3. Calcular uma rota candidata por Dijkstra e verificar acesso a **todos os quatro bicos**.
4. Registrar separadamente a confirmação de isolamento, o diagnóstico e a disponibilidade da alternativa.
5. Manter a bomba bloqueada durante a falha retida. A simulação não implementa rearme nem abertura automática da reserva.

O desvio automático desta entrega é o **recálculo e a proposta de reconfiguração**. Uma rota alternativa não autoriza retomar a aplicação com vazamento ativo. A confirmação física de fechamento, a inspeção, a validação hidráulica e o rearme pertencem a uma etapa posterior de implementação.

## Integração lógica

As regras R1–R8 e os limiares da Aula 10 são reconstruídos no notebook, sem importar arquivos da Etapa 1. A fusão foi ampliada: emergência, GPS, bateria, vento, modo, altitude, comunicação e diagnóstico entram no permissivo final da bomba. No código original da Aula 10, o comando da bomba não dependia de todos esses bloqueios globais; a correção está documentada no relatório de análise.

$$P_{bomba}=P_{global}\land P_{voo}\land P_{nivel}\land\neg D_{critico}.$$

No tratamento do vazamento acrescenta-se $\neg F_{retida}$; como a ocorrência permanece retida, a saída fica falsa. Telemetria ausente, não finita, fora de faixa ou com qualidade ruim também bloqueia a autorização.

## Cenários e resultados esperados

| Cenário | Resultado topológico | Comando da bomba |
|---|---|---|
| Falha e06, rede básica | Sem rota até os bicos | Desligado |
| Falha e06, rede redundante | Rota candidata de 2,2 m até o bico A | Desligado, aguarda inspeção |
| Fechamento não confirmado | Alternativa calculada, isolamento pendente | Desligado |
| Falha e07 após perda do ramal principal | Bomba isolada do distribuidor | Desligado |
| Perda da seção A | Outras seções não suprem a seção A | Aplicação completa indisponível |

## Criticidade e tempo de cálculo

Remover cada arco e testar a alcançabilidade identifica **cortes para o par tanque–bico A**. Isso é diferente de afirmar que todos são pontes do grafo não dirigido ou que toda a planta tem conectividade 2. O filtro reserva não duplica bomba, distribuidor nem saída de cada bico.

Mede-se somente o tempo computacional da rotina no computador que executou o notebook. Esse número não inclui detecção, comunicação, movimento de válvulas nem dinâmica do fluido, e não prova atendimento a um prazo de controle em tempo real.

**Entregável:** simulador com estado de falha retido, diário de eventos, recálculo, diagnóstico herdado e testes de falhas simples, duplas e de telemetria.

## Execução

Abra [15_Simulacao_de_Vazamentos_e_Desvio_Automatico.ipynb](15_Simulacao_de_Vazamentos_e_Desvio_Automatico.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
