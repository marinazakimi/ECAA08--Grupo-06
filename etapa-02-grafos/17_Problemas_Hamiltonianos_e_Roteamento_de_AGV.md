# Aula 17 — Problemas hamiltonianos e roteamento do drone

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

O nome do arquivo mantém `Roteamento_de_AGV` para correspondência com o modelo do professor. O veículo e a aplicação estudados aqui são o **drone agrícola**.

## Formulação e limite do problema

O TSP determina a ordem de visita a cinco pontos de serviço e o retorno à BASE. Um ciclo hamiltoniano visita cada vértice uma vez, exceto a repetição da base para fechar o percurso; um circuito euleriano cobre arestas. Os pontos de serviço são referências de talhões, com coordenadas locais hipotéticas em metros.

O grafo é completo, não dirigido e simétrico; $d_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}$. Assume-se que todos os segmentos são permitidos e que o vento não modifica o custo. Se houver obstáculos, deve-se construir uma matriz de distâncias de corredores permitidos. Visitar um ponto de talhão **não representa cobrir sua área**: faixas, sobreposição e manobras internas não são calculadas pelo TSP.

## Algoritmos

1. **Vizinho mais próximo:** a partir da base, visitar sempre o ponto ainda não visitado mais próximo. Custo de construção $O(n^2)$.
2. **2-Opt:** inverter trechos da sequência e aceitar reduções no custo total, incluindo o retorno à base. A busca termina quando nenhuma troca melhora a solução; isso é um ótimo local, sem garantia geral de ótimo global.
3. **Força bruta:** fixar a base e avaliar as $5!=120$ ordens. Fornece a referência exata desta instância pequena.
4. **Prim:** construir uma árvore geradora mínima (AGM), conectando os seis pontos com cinco arestas. Seu custo é uma cota inferior para o ciclo ótimo, pois remover uma aresta do ciclo produz uma árvore geradora.

A implementação de 2-Opt recalcula cada custo em $O(n)$ e examina $O(n^2)$ candidatos: uma varredura custa $O(n^3)$. O número de varreduras depende da instância; não se afirma um limite total cúbico.

## Recursos da missão

O notebook soma deslocamento e atendimento hipotético de 30 s em cada ponto a 2 L/min. Cinco atendimentos consomem 5 L. A missão inicia com 24 L em um reservatório de capacidade 30 L, preservado da Etapa 1. O cenário usa 75% de bateria, reserva de 20% e consumo fictício de 3 pontos percentuais por minuto. A reserva de planejamento é uma hipótese adicional, não uma estimativa calibrada de autonomia real.

A aceitação exige volume suficiente acima de 1,5 L (5% de 30 L), bateria final estimada pelo menos 20% e permissivos válidos da Etapa 1. O retorno à base já integra a distância do ciclo. Se a missão não couber nos recursos, o exemplo a rejeita; não implementa divisão automática em múltiplas saídas.

## Resultados e entregável

São impressas a rota inicial, a rota melhorada, a solução exata, o desvio percentual para o ótimo, a AGM e o balanço de recursos. Os testes verificam visita única, retorno contabilizado, 2-Opt não pior, cota AGM válida e rejeição de uma missão com calda insuficiente. A igualdade entre heurística e ótimo, quando observada, vale somente para esta instância.

![Ciclo de missão e árvore geradora mínima](Rotas_e_Arvore_Minima.png)

## Execução

Abra [17_Problemas_Hamiltonianos_e_Roteamento_de_AGV.ipynb](17_Problemas_Hamiltonianos_e_Roteamento_de_AGV.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
