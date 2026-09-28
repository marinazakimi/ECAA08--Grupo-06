# Relatório de validação — Etapa 02

**Data:** 28 de setembro de 2026 · **Grupo 06**

## Execução

As células de código dos oito notebooks foram executadas na ordem, em um namespace novo por arquivo, usando Python 3.12.14. Foram executadas **86 células de código**, sem exceções. Os arquivos contêm **67 instruções `assert`**, algumas exercitadas repetidamente em laços de cenários. Não se deve interpretar esse total como número de cenários distintos.

| Aula | Células de código | Instruções assert | Resultado |
|---|---:|---:|---|
| 11 | 7 | 7 | PASSOU |
| 12 | 8 | 8 | PASSOU |
| 13 | 11 | 9 | PASSOU |
| 14 | 12 | 5 | PASSOU |
| 15 | 16 | 14 | PASSOU |
| 16 | 5 | 6 | PASSOU |
| 17 | 13 | 7 | PASSOU |
| 18 | 14 | 11 | PASSOU |

Foi feita uma segunda execução independente por `validar_notebooks.py`. As saídas armazenadas foram obtidas da execução efetiva das células; não são resultados esperados preenchidos manualmente.

## Verificações relevantes

- Graus, ordem/tamanho, rejeição de paralelas e separação entre catálogo e modo voo.
- Matrizes rotuladas, somas por coluna, identidade laplaciana, resíduo de balanço e consumo do tanque.
- Árvores BFS, dois caminhos por DFS, origem/destino bloqueados e ausência de caminho com bomba indisponível.
- Custos de Dijkstra conhecidos, retorno à base e recálculo com interdição bidirecional.
- Vazamento sem reserva, vazamento com reserva, isolamento pendente, dupla falha e falha retida.
- Bloqueios de emergência, GPS, vento, bateria, altitude, comunicação, modo, nível, pressão e dados inválidos/ausentes.
- Circuito euleriano, identificação de paralelas por ID, trilha aberta e rejeição de componentes desconectadas.
- TSP: visita única, custo incluindo retorno, 2-Opt não pior que a construção, ótimo exato de 120 ordens e cota AGM.
- Missão rejeitada por recursos insuficientes; logística impedida por capacidade, voo, lote ou caminho indisponível.

## Conferências adicionais

O Dijkstra foi comparado a uma implementação independente de Floyd–Warshall em **40 dígrafos aleatórios de seis vértices**, totalizando **1440 consultas origem–destino**. Foram incluídos pesos zero e pares sem caminho. Todas as distâncias e os custos das rotas reconstruídas coincidiram.

O posto da incidência foi conferido por eliminação com frações exatas: **10** para a rede básica e **11** para a rede com filtro reserva, coerente com os números de componentes do catálogo físico.

A estrutura JSON dos notebooks, IDs de células, contadores de execução, ausência de saídas de erro, anexos de imagem, codificação UTF-8 e nomes sem espaços foram conferidos. Os diagramas foram renderizados e revisados visualmente. Os arquivos principais correspondem aos 18 nomes do ZIP de referência após normalização dos separadores.

## Limites da verificação

A execução foi realizada por Python sobre as células; não foi feita abertura interativa em Jupyter ou Colab, nem validação formal pelo pacote `nbformat`. O formato entregue é notebook 4.5, com metadados de kernel Python e saídas de texto padrão.

Os testes demonstram o comportamento dos algoritmos e cenários modelados. Não validam desempenho hidráulico, cobertura agronômica, autonomia real, latência de comunicação, confirmação de válvulas ou controle de voo. O tempo de cálculo medido na Aula 15 é apenas tempo de processamento local e varia entre execuções.
