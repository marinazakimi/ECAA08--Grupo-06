# Aula 14 — Dijkstra e roteamento dinâmico

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

## Objetivo e escolha do grafo

Determinar o caminho de menor custo entre dois vértices com pesos não negativos. Aplicam-se os mesmos passos a duas redes separadas: tubulações, com custo de comprimento de mangueira; e navegação, com distância de corredores aéreos hipotéticos. Não se somam metros de tubulação a metros de voo na mesma decisão.

## Algoritmo

Inicialize $d(s)=0$ e $d(v)=\infty$ para os demais vértices. Retire da fila de prioridade o vértice de menor distância provisória. Para cada arco disponível $(u,v)$, execute a relaxação:

$$d(v)\leftarrow\min\{d(v),d(u)+w(u,v)\}.$$

Se houver melhoria, registre o predecessor de $v$ e insira o novo par na fila. Entradas antigas são ignoradas. Com pesos não negativos, retirar o destino com sua distância atual permite encerrar a busca. Sem caminho, a função retorna `(inf, [])`; não apresenta uma lista contendo apenas o destino como se fosse rota válida.

Com listas de adjacência e heap, o custo usual para esta rede simples é $O((V+E)\log V)$. Alterar disponibilidade e executar novamente é um recálculo completo; não se implementa atualização incremental.

## Exemplo hidráulico

Do tanque a `DRN_BICO_A`, a rota principal mede $0,4+0,3+0,5+0,6=1,8$ m. Bloqueando e06, a extensão pelo filtro reserva mede $0,5+0,6+0,5+0,6=2,2$ m. O ganho de disponibilidade depende de existirem fisicamente o filtro e as válvulas propostas. Não há demonstração de adequação hidráulica somente com comprimentos.

## Exemplo aéreo: BFS versus Dijkstra

| Conexão bidirecional | Distância simulada |
|---|---:|
| BASE–T1 | 300 m |
| BASE–J1 | 80 m |
| J1–T1 | 100 m |
| BASE–J2 | 120 m |
| J2–T1 | 90 m |
| T1–T2 | 70 m |
| J2–T2 | 140 m |

BFS escolhe BASE→T1, com um salto e 300 m. Dijkstra escolhe BASE→J1→T1, com dois saltos e 180 m. Interditando ambos os sentidos de J1–T1, a nova rota usa J2 e mede 210 m. As distâncias representam comprimentos de corredores, sem exigir que o arco de 300 m seja uma reta entre os pontos.

O caminho de retorno também deve existir. O exemplo verifica ida e volta e calcula tempo de deslocamento a 5 m/s; a velocidade é apenas parâmetro de simulação. Uma análise de energia ou vento exigiria outro modelo de custos. Estes trajetos são sugestões de supervisão; sua execução pertence à controladora de voo.

**Entregável:** Dijkstra com predecessor, bloqueio de nós/trechos, recálculo e verificações de custo exato, rota impossível e peso negativo rejeitado.

## Execução

Abra [14_Menor_Caminho_Dijkstra_e_Roteamento_Dinamico.ipynb](14_Menor_Caminho_Dijkstra_e_Roteamento_Dinamico.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
