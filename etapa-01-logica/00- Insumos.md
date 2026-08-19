## Insumos do Processo

O principal insumo envolvido no processo é a **calda de pulverização**, composta pela mistura de água com defensivos agrícolas, fertilizantes líquidos ou outros produtos destinados à aplicação na lavoura.

Para o escopo deste projeto, a calda será considerada como um único fluido de processo. O sistema SCADA será responsável por supervisionar sua disponibilidade na estação de solo, o abastecimento do drone e seu consumo durante a pulverização.

A supervisão dos insumos permite ao operador acompanhar a quantidade de calda disponível, verificar as condições de aplicação, identificar possíveis falhas no sistema de pulverização e registrar o consumo durante cada operação.

### Insumos na Estação de Solo

Na estação de solo, a calda preparada é armazenada no **tanque de mistura**, responsável por fornecer o produto utilizado no abastecimento do drone.

O nível do tanque é monitorado por um sensor ultrassônico e enviado ao PLC da estação, permitindo que o sistema SCADA apresente ao operador a quantidade de calda disponível.

| Tag | Variável | Instrumento | Faixa | Unidade |
|---|---|---|---|---|
| `EST_LT_01` | Nível do tanque de mistura | Sensor de nível ultrassônico | 0 – 100 | % |

Além do monitoramento do nível, a estação possui atuadores responsáveis pela preparação e transferência da calda.

| Tag | Atuador | Tipo | Função |
|---|---|---|---|
| `EST_PMP_01` | Bomba de mistura/recirculação | Relé | Promover a circulação e homogeneização da calda |
| `EST_XV_01` | Válvula de abastecimento | Solenoide | Liberar ou interromper o abastecimento do drone |

A bomba de mistura permite manter a calda homogeneizada antes do abastecimento. A válvula de abastecimento controla a transferência da calda da estação para o reservatório embarcado no drone.

O sistema também poderá utilizar o nível do tanque como um **permissivo de abastecimento**, impedindo o acionamento da válvula caso a quantidade de calda disponível seja insuficiente.

### Insumos no Drone

Após o abastecimento, a calda fica armazenada no reservatório embarcado do drone. Durante o voo, o sistema monitora o nível do reservatório, a vazão de aplicação e a pressão da linha de pulverização.

| Tag | Variável | Instrumento | Faixa | Unidade |
|---|---|---|---|---|
| `DRN_LT_01` | Nível de líquido no reservatório | Sensor ultrassônico | 0 – 100 | % |
| `DRN_FT_01` | Vazão de aplicação | Fluxômetro | 0 – 10 | L/min |
| `DRN_PT_01` | Pressão da linha | Transmissor de pressão | 0 – 6 | bar |

O **nível do reservatório** permite acompanhar a quantidade de calda ainda disponível no drone.

A **vazão de aplicação** representa a quantidade de calda enviada aos bicos por unidade de tempo, sendo uma das principais variáveis utilizadas para acompanhar o consumo do produto.

A **pressão da linha** permite verificar as condições de funcionamento do sistema de pulverização e auxilia na identificação de situações anormais, como obstruções, vazamentos ou problemas na bomba.

Os principais atuadores envolvidos na aplicação da calda são:

| Tag | Atuador | Controle | Função |
|---|---|---|---|
| `DRN_PMP_01` | Bomba de pulverização | PWM | Controlar o bombeamento e a vazão da calda |
| `DRN_XV_01` | Válvulas seccionadoras | Abre/Fecha | Liberar ou interromper a pulverização em cada seção |

A bomba de pulverização poderá ter sua potência ajustada por PWM, permitindo alterar a vazão de acordo com as necessidades da aplicação. As válvulas seccionadoras permitem controlar quais setores dos bicos permanecem ativos durante a pulverização.

### Monitoramento do Consumo

O sistema SCADA poderá utilizar as medições obtidas pelos sensores para calcular informações adicionais relacionadas ao consumo da calda.

O volume consumido durante determinado intervalo pode ser estimado a partir da vazão de aplicação:

`V_consumido = Q × Δt`

Onde:

- `V_consumido`: volume de calda consumido, em litros;
- `Q`: vazão média durante o intervalo, em L/min;
- `Δt`: intervalo de tempo considerado, em minutos.

Para uma operação completa, o volume total aplicado poderá ser determinado pelo acúmulo das medições de vazão ao longo do tempo.

A partir dessas informações, o sistema poderá disponibilizar ao operador:

- Nível atual do reservatório;
- Volume estimado de calda restante;
- Vazão instantânea;
- Volume total aplicado;
- Tempo de pulverização;
- Consumo médio durante a operação.

Caso a área pulverizada também seja determinada a partir das informações de navegação do drone, será possível calcular o consumo de calda por hectare:

`Consumo_por_hectare = Volume_aplicado / Area_pulverizada`

O resultado poderá ser apresentado em `L/ha`, facilitando a análise da aplicação realizada.

### Alarmes e Intertravamentos

O sistema SCADA deverá identificar condições anormais relacionadas ao armazenamento e à aplicação da calda.

| Condição | Alarme / Ação |
|---|---|
| Nível do reservatório abaixo do limite mínimo | Alarme de baixo nível de calda |
| Nível do reservatório em estado crítico | Interrupção ou bloqueio da pulverização |
| Bomba acionada e ausência de vazão | Alarme de falha na pulverização |
| Vazão abaixo do valor mínimo esperado | Possível obstrução dos bicos ou da tubulação |
| Pressão acima do limite máximo | Alarme de alta pressão |
| Pressão abaixo do limite mínimo durante a aplicação | Alarme de baixa pressão |
| Nível insuficiente no tanque da estação | Bloqueio do abastecimento |

Os valores utilizados como limites poderão ser configurados e ajustados por meio do sistema SCADA/HMI de acordo com as condições da operação.

Uma possível lógica para identificar uma obstrução pode considerar a bomba de pulverização acionada juntamente com baixa vazão e pressão elevada:

`Alarme_Obstrucao = Bomba_Ligada AND Vazao_Baixa AND Pressao_Alta`

Dessa forma, o sistema evita considerar apenas uma variável isolada para caracterizar uma possível falha.

O nível do reservatório também poderá ser utilizado como permissivo de pulverização. Caso o nível esteja abaixo de um limite crítico, o sistema poderá impedir o acionamento da bomba e das válvulas de pulverização.

### Registro Histórico dos Insumos

Os dados relacionados à utilização da calda poderão ser armazenados no servidor SCADA através do sistema de **data logging**, permitindo manter um histórico das operações realizadas.

Para cada missão poderão ser registrados:

- Data e horário da operação;
- Produto ou tipo de calda utilizado;
- Nível inicial do reservatório;
- Nível final do reservatório;
- Volume total aplicado;
- Vazão média de aplicação;
- Pressão média da linha;
- Tempo total de pulverização;
- Área pulverizada;
- Consumo médio em `L/ha`;
- Alarmes ocorridos durante a aplicação.

O tipo de produto utilizado poderá ser informado manualmente pelo operador através da HMI antes do início da missão, não sendo necessária, dentro do escopo do projeto, a utilização de um sensor específico para identificação química da calda.

### Visualização na HMI

Na interface de supervisão, a seção referente aos insumos poderá apresentar as principais informações do sistema de pulverização em tempo real.

Entre os elementos recomendados estão:

- Indicador do nível do tanque da estação de solo;
- Indicador do nível do reservatório do drone;
- Vazão instantânea em `L/min`;
- Pressão da linha em `bar`;
- Estado da bomba de pulverização;
- Estado das válvulas seccionadoras;
- Volume total consumido;
- Produto atualmente utilizado;
- Alarmes ativos relacionados à pulverização.

Com essas informações, o operador poderá acompanhar o percurso da calda desde sua disponibilidade na estação de solo até sua aplicação na lavoura, permitindo maior controle operacional, rastreabilidade e identificação de condições anormais.
