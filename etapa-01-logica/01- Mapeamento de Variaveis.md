## Variáveis do Processo

![Sistema Aplicado a Drone Agrícola](marinazakimi/ECAA08--Grupo-06/etapa-01-logica/Diagrama_Variaveis.png)

### Variáveis de Entrada (Sensores)

| Variável | Sensor | Grandeza / Unidade |
|---|---|---|
| Nível do reservatório | Sensor de nível ultrassônico | % ou litros (L) |
| Vazão da calda | Sensor de vazão (fluxômetro) | L/min |
| Pressão de pulverização | Sensor de pressão | bar / psi |
| Posição / rota | Módulo GPS | Coordenadas (lat/long) |
| Altitude de voo | Barômetro / altímetro | metros (m) |
| Velocidade de voo | IMU / GPS | m/s |
| Nível de bateria | Sensor de tensão/corrente | % / Volts (V) |
| Velocidade do vento | Anemômetro | m/s |
| Temperatura e umidade | Sensor ambiental | °C / %UR |

### Variáveis de Saída (Atuadores)

| Variável | Atuador | Ação |
|---|---|---|
| Acionamento da bomba | Bomba de pulverização | Liga/desliga, controle de vazão |
| Abertura dos bicos | Válvulas solenoides | Abre/fecha por seção |
| Controle de altitude | Motores/ESCs | Ajuste de empuxo |
| Controle de rota | Sistema de navegação | Ajuste de trajetória |

