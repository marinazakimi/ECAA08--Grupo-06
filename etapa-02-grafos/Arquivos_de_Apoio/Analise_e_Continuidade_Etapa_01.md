# Análise dos materiais e continuidade entre as etapas

**Grupo 06 · ECAA08 · 28 de setembro de 2026**

## Materiais analisados

Foram extraídos e examinados os 18 arquivos de cada ZIP fornecido. Na Etapa 1 há documentos de insumos/variáveis, oito notebooks de lógica (03–10), textos correspondentes e o diagrama de variáveis. Na referência da Etapa 2 há oito pares Markdown/notebook (11–18), um layout auxiliar e uma imagem logística.

Os materiais do professor foram usados como referência curricular e de organização. Atividades, exemplos e sugestões neles contidos foram avaliados no contexto da solicitação do grupo; não foram tratados como novas instruções para executar ações externas.

## O que foi preservado

| Etapa 1 | Continuidade na Etapa 2 |
|---|---|
| Calda como fluido único | Balanço volumétrico em L/min; sem receita química inventada |
| Estação e drone como subsistemas | Modos de mistura, abastecimento e voo |
| Tags de sensores e atuadores | Cadastro e associações do layout auxiliar |
| Permissivos e modos exclusivos | Condições da fusão final da Aula 15 |
| Quantificadores da Aula 06 | Exigência de alcance de todos os bicos e domínio definido |
| Regras R1–R8 das Aulas 09/10 | Diagnóstico por encadeamento progressivo |
| Diagnóstico como hipótese | Não se deduz a localização do vazamento a partir de sinais globais |
| HMI e histórico | Tabelas e registros simulados para futura integração |

## Divergências de parâmetros encontradas

Os valores abaixo são parâmetros dos exemplos acadêmicos recebidos. Não são recomendações de operação de um drone real.

| Variável | Versões anteriores | Convenção desta entrega |
|---|---|---|
| Pressão alta | Aula 02/08: ≥4,5 bar; Aula 09/10: >5 bar; figura: >4,5 bar | >5 bar para as regras herdadas da Aula 10 |
| Pressão baixa | Aula 02/08: ≤1,2 bar; Aula 09/10: <1 bar com bomba ligada | <1 bar com bomba ligada |
| Vazão baixa | Aula 02/06/08: ≤0,4 L/min; Aula 09/10: <0,5 L/min | <0,5 L/min com bomba ligada |
| Vento | Aula 08: 15 km/h; Aula 09/10: >8 m/s; figura: >20 km/h | >8 m/s, conforme implementação integrada |
| Nível de calda | Aula 02: baixo ≤10%, crítico ≤3%; diagnóstico da Aula 10: baixo <20%, crítico <5% | Preservados os níveis do diagnóstico da Aula 10; interlock de vazio continua ≤3% |
| Bateria | Aula 09/10: baixa <20%, crítica <10% | Mesmos valores, em % |
| Reservatórios | Mapeamento da Aula 02: 500 L no solo e 30 L embarcados | Mesmas capacidades de simulação |

Assim, por exemplo, nível de 4% bloqueia a aplicação pelo diagnóstico, embora não satisfaça o interlock de vazio ≤3%. Essa diferença foi mantida explícita, em vez de misturar limiares de diferentes versões. Comparações estritas nas fronteiras também são verificadas no notebook 15.

A figura de variáveis e o texto divergem ainda em unidades/faixas de vento e altitude. A Etapa 2 não depende de um limite de altitude inventado: recebe `alt_ok`. O vento foi padronizado em m/s nos exemplos, sem tratar 8 m/s, 15 km/h e 20 km/h como equivalentes.

## Ajustes lógicos e físicos necessários

1. **Fusão do comando da bomba:** na função `motor_scada_integrado` da Aula 10, a saída da bomba depende do permissivo de pulverização e dos diagnósticos hidráulicos, mas não incorpora diretamente todos os bloqueios de emergência, GPS, bateria, vento e modo. A nova função `avaliar_etapa1` combina esses bloqueios com comunicação válida, voo, altitude, nível e regras R1–R8. Os arquivos originais não foram modificados.

2. **Hipótese não é confirmação:** a regra de baixa vazão/baixa pressão aponta possível vazamento **ou** falha da bomba. A localização e06 é fornecida pelo cenário de injeção de falha. Não há alegação de que os sensores globais localizem o ponto rompido.

3. **Retenção após falha:** com a bomba desligada, os fatos dependentes de “bomba ligada” podem desaparecer no próximo ciclo. Por isso o novo simulador retém o evento de vazamento e mantém o bloqueio, evitando retomada por desaparecimento do sintoma.

4. **Partida da bomba:** os cenários de diagnóstico são fotografias de operação estabilizada. A queda de vazão durante uma partida normal exige estado temporal e temporização, que não estão implementados. O pacote não é um controlador dinâmico de partida.

5. **Inferências de instrumentação:** pressão com bomba desligada pode envolver pressão residual; ausência de alarme não comprova, por si só, sensor ou bateria íntegros. As inferências mais fortes dos exemplos 07/08 não foram reproduzidas como garantias físicas.

6. **Dosagem por área:** o texto da Aula 02 apresenta o fator 600 com velocidade em m/s. Dimensionalmente, para `Q` em L/min, `v` em m/s e largura `w` em metros, a expressão é `D = 10000*Q/(60*v*w)` em L/ha. O fator 600 aplica-se quando `v` está em km/h. A Aula 18 usa diretamente volume aplicado dividido pela área registrada, evitando carregar essa inconsistência.

## Ajustes matemáticos em relação à referência

- Existência de rota alternativa não exige ciclo dirigido. Um DAG pode conter ramos alternativos convergentes.
- A enumeração de todos os caminhos por DFS não é linear no tamanho do grafo em geral; uma DFS de visita única é.
- Minimizar arestas por BFS não equivale a minimizar válvulas, porque o novo modelo não coloca válvula em toda aresta.
- A matriz de incidência conserva IDs físicos; a adjacência operacional considera modo e falhas.
- O reservatório do drone tem acúmulo negativo durante pulverização; não se impõe balanço estacionário a todos os vértices.
- Hierholzer verifica conectividade e paridade e identifica arestas paralelas por ID.
- O resultado do 2-Opt é tratado como ótimo local; a força bruta certifica somente a instância pequena apresentada.
- A implementação didática recalcula custos de 2-Opt; cada varredura é cúbica, sem afirmar um limite cúbico para toda a convergência.
- Cortes dirigidos para tanque–bico são apresentados como tais, sem inferir conectividade global 2 apenas da presença de dois filtros.

## Hipóteses novas identificadas

O filtro reserva, suas válvulas, o arranjo de recirculação/transferência, os distribuidores, os comprimentos de mangueira, os pontos de navegação, as distâncias logísticas, o tempo de atendimento por ponto e o consumo de bateria são hipóteses didáticas adicionais. Todas estão explicitadas nos textos ou no layout auxiliar.

Mantiveram-se os nomes normalizados do professor, inclusive `AGV`, `Produtos_Acabados`, `aux_plantafabril.md` e a grafia `Grafo_Logitica.jpeg`, para permitir conferência arquivo a arquivo. Os títulos internos e os conteúdos foram adaptados ao drone.
