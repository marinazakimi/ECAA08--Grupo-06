# Aula 11 — Modelagem da tubulação e dos instrumentos como grafo

**ECAA08 · Grupo 06 · Arthur, Caique, Luis Felipe e Marina**  
**Planta:** drone agrícola de pulverização e estação de solo.

## Objetivo e continuidade da Etapa 1

Representar as conexões pelas quais a calda pode circular, preservando `EST_PMP_01`, `EST_XV_01`, `DRN_PMP_01` e a família `DRN_XV_01`. A rede tem um tanque de solo, uma bomba de recirculação/transferência, um reservatório embarcado, um filtro, uma bomba de pulverização e quatro seções de bicos. As quatro seções retomam o exemplo da Aula 06.

`EST_TQ_01`, `DRN_TQ_01`, os distribuidores e os filtros são identificadores de equipamentos introduzidos nesta etapa; não substituem as tags dos sensores. `EST_LT_01` mede o tanque de solo; `DRN_LT_01` mede o reservatório; `DRN_PT_01` e `DRN_FT_01` monitoram a descarga da bomba. Instrumentos que não transportam calda são atributos, não vértices hidráulicos em série.

## Modelo matemático

O dígrafo ponderado é $G=(V,E,w)$, com $w:E\to\mathbb{R}_{\geq0}$. Um vértice representa um equipamento ou uma seção; um arco representa uma ligação física orientada. O peso mede **comprimento em metros**, sem representar automaticamente perda de carga, tempo ou energia.

O catálogo básico tem $|V|=11$ e $|E|=11$. O lema dos graus determina $\sum_v d^+(v)=\sum_v d^-(v)=11$. A rede física contém o ciclo de recirculação `EST_TQ_01 → EST_PMP_01 → EST_MAN_01 → EST_TQ_01`. Uma rota alternativa pode existir mesmo em um dígrafo sem ciclos: dois ramos podem convergir adiante.

Passeio pode repetir arestas; trilha não repete arestas; caminho simples não repete vértices. O caminho da calda para um bico não representa a trajetória aérea do drone.

## Modos de operação e hipóteses

| Modo | Arestas utilizáveis | Interpretação |
|---|---|---|
| Mistura | e01, e02, e03 | Recirculação no tanque de solo |
| Abastecimento | e01, e02, e04 | Drone no solo, conexão de abastecimento acoplada |
| Voo | e05 a e11 | Abastecimento desconectado; pulverização embarcada |

Consultar o catálogo completo (`modo=None`) não autoriza abrir todas as válvulas ao mesmo tempo. Disponibilidade topológica é diferente do comando do atuador. A seleção de modos é uma hipótese explícita de arranjo hidráulico; comprimentos e diâmetros são dados de simulação.

O segundo filtro `DRN_FLT_02`, e12/e13 e válvulas de isolamento são uma **extensão proposta** para investigar redundância. O modelo básico funciona sem essa extensão. O ramo alternativo mantém a filtragem; não desvia calda por fora do filtro.

![Rede hidráulica](Grafo_Hidraulico.png)

## Representação e exemplo

A classe `GrafoTubulacao` usa listas de adjacência e catálogo de arestas com ID, peso, válvula, diâmetro, modo e disponibilidade. Rejeita extremidades inexistentes, pesos negativos, IDs duplicados e arestas paralelas, em vez de perder informações silenciosamente. A inspeção da Aula 16 usa um multigrafo separado.

`DRN_MAN_01` tem uma entrada e quatro saídas. Isso representa distribuição entre seções; não demonstra quatro caminhos independentes desde o tanque, pois todos compartilham a bomba. As matrizes são exportadas sob demanda para manter uma única fonte de dados.

## Atividades resolvidas e verificações

1. Some os graus: ambos os totais devem ser 11 no catálogo básico.
2. Em voo, e04 deve desaparecer da adjacência operacional. O abastecimento não acompanha o drone.
3. Ative a extensão: a ordem passa a 12 e o tamanho a 13.
4. Diferencie o sensor `DRN_LT_01` do equipamento `DRN_TQ_01`: o primeiro mede; o segundo contém calda.

**Entregável:** classe de modelagem, cadastro, graus e adjacência operacional, executados no notebook correspondente.

## Execução

Abra [11_Modelagem_da_Tubulacao_e_Instrumentos_como_Grafo.ipynb](11_Modelagem_da_Tubulacao_e_Instrumentos_como_Grafo.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
