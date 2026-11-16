# Continuidade e hipóteses — Sistema SCADA do Drone Agrícola

## Identidade do projeto

ECAA08 — Arquitetura de Sistemas SCADA, Grupo 06: Arthur, Caique, Luis Felipe e Marina.
O projeto iniciado em 10 de agosto de 2026 é um **Sistema SCADA aplicado a um Drone Agrícola de Pulverização**.
Lógica, grafos e árvores são etapas do mesmo projeto. A Etapa 3 desenvolve serviços de supervisão e demonstra sua integração.

## Origem das informações

Foram consultados o README inicial, o mapeamento de variáveis da Aula 02, a implementação integrada da Aula 10 e a análise de continuidade da Etapa 2 no ZIP do grupo. As Etapas 1 e 2 não são reescritas por esta entrega.

A pasta de referência do professor foi consultada em 16/11/2026. Na consulta, estavam disponíveis pares Markdown/notebook das aulas 19, 20 e 21 e uma pasta `img`. Usamos a ideia de documentos por aula, notebooks e figuras locais. Os exemplos industriais, equipamentos, dimensões, afirmações normativas e imagens do professor não foram transportados para a planta do drone. As aulas 22–28 seguem a sequência fornecida pelo grupo.

Referência de organização: [repositório do professor](https://github.com/valerio-unifei/ECAA08-2026.2-Projeto/tree/main/etapa-03-arvores).

## Tags e representação nesta etapa

| Origem / tag | Significado aqui | Unidade / observação |
|---|---|---|
| `DRN_LT_01` | Nível da calda embarcada | % |
| `DRN_PT_01` | Pressão de pulverização | bar |
| `DRN_FT_01` | Vazão de pulverização | L/min |
| `DRN_ET_01` | Estado de carga da bateria | %; não é tensão em volts neste modelo |
| `EST_WT_01` | Vento medido na estação | m/s |
| `DRN_GPS_01` | Origem conceitual da posição | Coordenadas locais x/y em metros nos exemplos; `gps_ok` indica qualidade |
| `DRN_ZT_01` | Origem conceitual da altitude | Guarda `alt_ok` fornecida ao supervisor; não inventamos limite numérico |
| `DRN_PMP_01` e `DRN_XV_01` | Bomba e válvulas embarcadas | Modelo de solicitação booleana e feedback; não há conversão para PWM real |

`comm_ok`, `idade_s`, `estabilizado`, `aprovada`, `rota_ok`, `na_faixa`, `rearme` e `inspecao_confirmada` são campos de software do simulador, não novos instrumentos físicos. `is_flying`, `gps_ok`, `alt_ok`, `auto_mode`, `manual_mode` e `e_stop` preservam a ideia dos permissivos anteriores.

## Parâmetros herdados e hipóteses novas

Os materiais anteriores possuem limiares divergentes. Para a continuidade, adotamos a convenção integrada registrada na Aula 10 e no documento de continuidade da Etapa 2:

| Condição | Convenção usada |
|---|---|
| Pressão alta / baixa | >5 bar / <1 bar |
| Vazão baixa | <0,5 L/min, com bomba ativa e operação estabilizada |
| Nível crítico | <5% |
| Bateria crítica | <10% |
| Nível / bateria baixos | <20%; nesta etapa motivam solicitação de retorno se não houver bloqueios prioritários |
| Vento alto | >8 m/s |
| Qualidade temporal | Idade >2 s bloqueia; **hipótese nova** |

Os testes incluem fronteiras estritas. O interlock de vazio ≤3% das etapas anteriores está contido no bloqueio de nível <5% usado aqui, sem alterar seus arquivos. Diagnósticos de vazão e pressão só são avaliados com `estabilizado=True`; a dinâmica de partida não foi implementada.

A retomada de uma falha de pulverização retida exige inspeção confirmada, pulso de rearme e ausência de alarmes ativos com dados válidos. A normalização do vento não exige inspeção de manutenção; o supervisor reavalia os permissivos no próximo tick. A escolha é explícita para distinguir recuperação ambiental de falha retida.

As regras de alarme são hipóteses de diagnóstico. Pressão e vazão baixas não localizam um vazamento nem identificam sua causa com certeza. A classe aprendida da Aula 27 tampouco resolve essa ambiguidade.

## Geometria, recursos e comunicação

- Os seis pontos BASE e T1–T5 vêm da Aula 17, tratados como acessos aos talhões.
- Obstáculos e limites são hipóteses novas, em `cenario.json`.
- Raio de 0,6 m e folga de 1,4 m são parâmetros ilustrativos. O equipamento real e suas dimensões não foram especificados; o valor não é deduzido da área do mapa nem recomendado para operação.
- Distâncias são trajetos geográficos, não dimensões de componentes do drone.
- O modelo não cria rede de tubulações, tanques industriais ou AGVs.
- A LAN de três switches da estação é uma ampliação didática; não foi afirmada como hardware instalado.
- STP/RSTP atua na LAN, não no planejamento de voo. O rádio permanece um canal separado.
- A telemetria de bateria e nível do replay é sintética. Não há prova de autonomia, dose aplicada, esgotamento de tanque ou capacidade de cobertura.

## Interfaces e autoridade de decisão

| Componente | Produz | Não autoriza por si só |
|---|---|---|
| AGM / RRT | Conectividade e caminho geométrico | Decolagem ou aplicação |
| STP / RSTP | Encaminhamento lógico da LAN modelada | Disponibilidade do rádio |
| Petri | Transições e marcações possíveis do modelo | Segurança física ou permissivos contínuos |
| Árvore de comportamento | Solicitação supervisória e justificativa | Acionamento de hardware sem validação local |
| Árvore aprendida | Sugestão de classe | Rearme, eliminação de alarmes ou liberação da bomba |
| HMI | Visualização e decisões do operador no cenário | Operação real nesta entrega |

O simulador acrescenta uma fusão explícita de bloqueios, seguindo a correção conceitual já registrada na Aula 15. Ele não depende de modificar a Aula 10. Em perda de GPS ou telemetria, não presume retorno seguro; mostra pausa/intervenção. A política física de contingência pertence à controladora embarcada e precisaria ser definida em uma implantação real.

## Organização e autoria

Documentos e notebooks das aulas 19–28 ficam na raiz de `etapa-03-arvores`. Imagens originais, código comum, dados e validação ficam em `Arquivos_de_Apoio`. Os notebooks incluem os algoritmos centrais e importam os utilitários comuns. Os arquivos anteriores das aulas 19–22 não integram este pacote.

Não foram copiadas imagens do professor nem feitas alegações de certificação, conformidade SIL ou desempenho medido em equipamentos. As referências conceituais constam nos documentos de cada aula.
