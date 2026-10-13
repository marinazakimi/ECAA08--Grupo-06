# Aula 18 — Grafos de logística de insumos e aplicação agrícola

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

O nome mantém `Produtos_Acabados` para rastreabilidade com a referência. Na planta agrícola, o resultado é **aplicação registrada por missão e talhão**, não estoque de fertilizante ensacado.

## Duas redes para o mesmo sistema

| Rede | Vértices e arestas | Peso | Pergunta |
|---|---|---|---|
| Materiais $G_M$ | Insumos, preparo, estoque de calda, abastecimento, drone, talhão | Metros estimados entre etapas | Como cada insumo chega à aplicação? |
| Apoio terrestre $G_V$ | Portão, depósito, preparo, base e manutenção | Metros de circulação permitida | Como o veículo de apoio retorna ao portão? |

A mesma classe discreta atende às duas redes, mas as arestas não são intercambiáveis. Um veículo terrestre não percorre a conexão aérea DRONE→TALHÃO. Os pesos descrevem deslocamentos entre etapas; não incluem tempo de mistura, inspeção, carga de bateria ou vazão de abastecimento.

![Logística da planta](Grafo_Logitica.jpeg)

## Fluxo de materiais e precedência

ÁGUA e PRODUTO convergem para PREPARO. Seguem ESTOQUE_CALDA, ABASTECIMENTO, DRONE e TALHÃO. O subgrafo é um DAG, permitindo ordenação topológica pelo algoritmo de Kahn. A ordem demonstra precedência, mas **não verifica estoque nem receita**. O preparo necessita de ambos os insumos; a rota de menor custo de um deles não autoriza omitir o outro.

Da água ao talhão: $12+5+10+3+180=210$ m. Do produto ao talhão: $8+5+10+3+180=206$ m. Esses valores servem para comparar movimentações por origem; não definem composição química, dosagem agronômica ou custo global de produção.

O notebook condiciona um abastecimento de 24 L à disponibilidade de calda, nível de solo pelo menos 20%, drone pousado e capacidade embarcada de 30 L. Um tanque de solo com 250 L passa a 226 L. Ao associar uma missão de aplicação de 5 L, restam 19 L no drone, com área hipotética de 0,5 ha e consumo registrado de 10 L/ha.

## Circulação de apoio e logística reversa

O anel terrestre segue PORTÃO→DEPÓSITO→PREPARO→BASE→MANUTENÇÃO→PORTÃO. O trajeto BASE→MANUTENÇÃO→PORTÃO mede 65 m. O retorno cria um ciclo dirigido, portanto essa rede não admite ordenação topológica.

A troca e recarga de baterias e o encaminhamento de embalagens, água de lavagem e resíduos exigem fluxos próprios. Estão identificados no layout auxiliar como extensão de escopo, sem conectar resíduos de volta à calda limpa. Não se modelam procedimentos químicos de descarte.

## Rastreabilidade SCADA

Cada registro associa lote, missão, talhão, litros abastecidos, aplicados e remanescentes, área e caminho selecionado. A disponibilidade física não comprova mistura pronta; o exemplo exige também `lote_liberado=True`, representando uma confirmação de processo.

Ao bloquear ESTOQUE_CALDA→ABASTECIMENTO, Dijkstra retorna ausência de rota, impedindo planejar a transferência. O estoque permanece cadastrado: uma via indisponível não elimina seu conteúdo do inventário.

**Entregável:** classe `GrafoLogistico`, modelos distintos de materiais e apoio, ordenação topológica, caminhos mínimos, bloqueio e registro de consumo ligados às variáveis da Etapa 1.

## Execução

Abra [18_Grafos_de_Logistica_de_Insumos_e_Produtos_Acabados.ipynb](18_Grafos_de_Logistica_de_Insumos_e_Produtos_Acabados.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
