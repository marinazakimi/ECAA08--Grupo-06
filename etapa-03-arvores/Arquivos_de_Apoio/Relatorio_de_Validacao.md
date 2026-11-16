# Relatório de validação — Etapa 3 SCADA

Método: células sequenciais em processo Python novo por notebook; formato validado com nbformat. Python 3.12.14; Matplotlib 3.10.8.

Executados 10 notebooks, total de **56 células de código**, sem erros. Saídas e figuras salvas nos notebooks.

| Aula | Células de código | Resultado |
|---|---:|---|
| 19 | 6 | APROVADO |
| 20 | 6 | APROVADO |
| 21 | 5 | APROVADO |
| 22 | 5 | APROVADO |
| 23 | 6 | APROVADO |
| 24 | 6 | APROVADO |
| 25 | 6 | APROVADO |
| 26 | 5 | APROVADO |
| 27 | 6 | APROVADO |
| 28 | 5 | APROVADO |

Os critérios estão em [verificacoes.py](verificacoes.py). Resultados quantitativos e ambiente: [Resultados_Validacao.json](Resultados_Validacao.json).

A validação cobre os modelos didáticos; não comprova capacidade de voo, segurança funcional certificada ou funcionamento de dispositivos físicos.


## Limite do ambiente de execução

A inicialização de kernels Jupyter foi impedida pela restrição de criação de sockets deste ambiente. Assim, a validação registrada executa as células sequencialmente em um novo processo Python para cada notebook e valida o formato com nbformat. Não foi validada uma sessão interativa Jupyter. O validador inclui `--jupyter` para essa repetição em outro ambiente.

As figuras foram geradas pelos próprios modelos. O painel HTML é um replay de saídas calculadas; seu JavaScript e sua navegação são verificados separadamente, sem alegação de conexão a equipamento.

## Revisão da entrega

- Links relativos de todos os documentos: destinos existentes.
- Dez pares Markdown/notebook e 12 figuras: conferidos.
- Figuras revisadas visualmente; rótulos da aula 24 ajustados.
- Painel: sintaxe JavaScript e navegação de início/fim/anterior verificadas em DOM simulado; sem teste visual em navegador.
- ZIP original das etapas anteriores: hash SHA-256 preservado.
- Aulas 24 e 28 reexecutadas após ajustes finais de figura e leitura de bateria no pouso.
