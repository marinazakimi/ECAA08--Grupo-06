# Aula 12 — Matrizes de incidência, adjacência e custos

**ECAA08 · Grupo 06 · Drone agrícola de pulverização**

## Objetivo

Construir $A$, $W$ e $B$ usando a mesma ordem de vértices e IDs da Aula 11, e verificar a conservação de volume. Considera-se calda incompressível com densidade constante; vazões em L/min permitem um balanço volumétrico equivalente ao balanço de massa após multiplicação pela densidade.

## Definições e convenções

| Matriz | Dimensão no modelo básico | Definição |
|---|---|---|
| Adjacência $A$ | 11 × 11 | 1 quando o arco está disponível no modo consultado |
| Custos $W$ | 11 × 11 | Comprimento do arco, infinito sem ligação, zero na diagonal |
| Incidência $B$ | 11 × 11 | −1 na origem, +1 no destino, zero nos demais nós |

`B` descreve o **catálogo físico**; seus IDs permanecem fixos após uma falha. Em trechos indisponíveis, a vazão deve ser zero. `A` e `W` refletem a disponibilidade operacional. A diagonal zero de `W` significa permanecer no mesmo nó e não introduz uma tubulação de comprimento nulo.

Cada coluna de $B$ soma zero. Para um grafo subjacente com $c$ componentes, $\operatorname{rank}(B)=n-c$ e a dimensão do núcleo é $m-n+c$. No catálogo básico conectado: posto 10 e dimensão 1. O retorno de recirculação explica esse ciclo independente. Com o filtro reserva: $n=12$, $m=13$, dimensão 2; o segundo ciclo é do grafo **não dirigido subjacente**, sem obrigar a existência de um novo ciclo dirigido.

## Balanço com armazenamento

A equação geral adotada é:

$$\frac{d\mathbf V}{dt}=B\mathbf Q+\mathbf u-\mathbf c.$$

Aqui $B\mathbf Q$ é entrada interna menos saída interna; $\mathbf u$ é alimentação externa e $\mathbf c$ é retirada externa, ambas positivas. Para nós sem acúmulo, o lado direito vale zero. **O tanque embarcado esvazia durante o voo**, portanto não é correto impor regime permanente a ele.

No cenário nominal, e05/e06/e07 conduzem 2 L/min; e08 a e11 conduzem 0,5 L/min cada. Os trechos de solo têm vazão zero. Assim, $B\mathbf Q$ resulta em −2 L/min em `DRN_TQ_01`, +0,5 em cada bico e zero nos equipamentos intermediários. A retirada externa pelos bicos cancela esses quatro termos positivos.

Para um reservatório de 30 L, partindo de 24 L e pulverizando por 3 min, restam $24-2\times3=18$ L, ou 60%. A vazão total é medida por `DRN_FT_01`; a divisão igual entre bicos é uma hipótese do cenário.

## Exemplo de inconsistência

Se a vazão e08 for alterada isoladamente de 0,5 para 0,7 L/min, mantendo e07 em 2, o distribuidor apresenta resíduo de −0,2 L/min. A soma global continua zero por construção de $B$; isso **não prova** que todos os nós estejam balanceados. O resíduo pode indicar dados inconsistentes, acúmulo não modelado ou retirada não cadastrada; não identifica sozinho um vazamento.

## Atividades resolvidas e entregável

O notebook imprime as três matrizes, verifica as somas das colunas, calcula o balanço, simula o consumo do tanque e detecta a inconsistência. Também demonstra $BB^T=D-A_u$, em que $A_u$ usa a multiplicidade das conexões do grafo subjacente, inclusive as direções opostas. As assertivas conferem valores numéricos conhecidos e fluxos nulos fora do modo voo.

## Execução

Abra [12_Matrizes_de_Incidencia_Adjacencia_e_Custos.ipynb](12_Matrizes_de_Incidencia_Adjacencia_e_Custos.ipynb) e execute as células em ordem. O notebook é independente e usa somente a biblioteca padrão do Python.
