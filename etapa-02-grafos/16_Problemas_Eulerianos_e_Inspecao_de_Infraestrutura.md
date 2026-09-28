# Aula 16 — Problemas eulerianos e inspeção da infraestrutura

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

## Modelo da inspeção

O objetivo é percorrer cada trecho de acesso de manutenção uma vez. Usa-se um **multigrafo não dirigido de acesso físico**, independente da orientação de escoamento da calda. O percurso representa um técnico ou veículo de inspeção na estação, com o drone em manutenção; não pressupõe um robô dentro das mangueiras nem voo de pulverização.

Seis locais são conectados por um anel: BASE, TANQUE, BOMBA_SOLO, ABASTECIMENTO, BANCADA_DRONE e LAVAGEM. Acrescentam-se três acessos entre TANQUE, BOMBA_SOLO e ABASTECIMENTO. Dois pares de vértices passam a possuir arestas paralelas, cada qual com ID único.

## Critérios de Euler

Um multigrafo não dirigido admite circuito euleriano se todos os vértices com grau não nulo pertencem a uma mesma componente e todos os graus são pares. Para uma trilha aberta, são necessários exatamente dois vértices ímpares e a partida deve ocorrer em um deles. Vértices isolados sem arestas não afetam a cobertura dos trechos.

No exemplo de nove arestas, os graus são 2, 4, 4, 4, 2, 2. A soma é 18, igual a $2|E|$. Graus pares sozinhos não bastam: dois triângulos desconectados têm todos os graus pares e não admitem um circuito que percorra ambos.

## Hierholzer

O algoritmo mantém uma pilha, consome arestas por ID e retrocede quando não há mais trecho disponível. A inversão da sequência de retrocesso produz a trilha. Com listas de adjacência e conjunto de IDs consumidos, cada incidência é examinada uma quantidade constante de vezes: $O(V+E)$.

O resultado contém a sequência de vértices e a sequência de IDs. Verifica-se que existem dez posições de vértices e nove IDs, cada ID aparece uma vez e cada trecho une exatamente os vértices adjacentes indicados. A verificação por pares de nomes seria insuficiente nas arestas paralelas.

## Exemplo complementar

Remover o último acesso adicional deixa dois vértices ímpares. O circuito fechado deixa de existir, mas há trilha aberta partindo de um deles. Se a tarefa exigisse retorno à base, seria necessário repetir trechos; minimizar essa repetição conduz ao problema do carteiro chinês, que não é resolvido aqui.

Hierholzer constrói uma cobertura sem repetição quando ela existe. Não escolhe o menor percurso entre soluções com tempos de serviço, sentidos proibidos ou repetições obrigatórias. No circuito euleriano, cada aresta é usada uma vez, logo a soma dos pesos de todas as arestas seria a mesma em qualquer circuito.

**Entregável:** implementação que trata paralelas corretamente, verifica conectividade e paridade, gera circuito/trilha e rejeita o caso desconectado.

## Execução

Abra [16_Problemas_Eulerianos_e_Inspecao_de_Infraestrutura.ipynb](16_Problemas_Eulerianos_e_Inspecao_de_Infraestrutura.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
