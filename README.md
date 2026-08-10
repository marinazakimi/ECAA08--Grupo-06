# ECAA08--Grupo-06
# Definição da Planta
### Sistema SCADA aplicado a um Drone Agrícola de Pulverização

**Disciplina:** ECAA08- Arquitetura de Sistemas SCADA
**Grupo:** Grupo 06
**Integrantes:** Arthur, Caique, Luis Felipe, Marina
**Data:** 10 de agosto de 2026

---

## Resumo

Este documento apresenta a definição da planta escolhida pelo grupo para o desenvolvimento do projeto da disciplina de Sistemas SCADA. Optou-se por um **drone agrícola de pulverização**, tratado como um processo supervisionado, no qual variáveis de operação, sensores e atuadores são monitorados e controlados por meio de uma arquitetura SCADA. O presente documento descreve o processo, os objetivos de supervisão e controle, as variáveis envolvidas, a arquitetura proposta e a justificativa da escolha.

---

## Sumário

1. [Descrição Geral do Processo](#descrição-geral-do-processo)
2. [Objetivo do Sistema de Supervisão e Controle](#objetivo-do-sistema-de-supervisão-e-controle)
3. [Variáveis do Processo](#variáveis-do-processo)
4. [Arquitetura Proposta](#arquitetura-proposta)
5. [Justificativa da Escolha](#justificativa-da-escolha)
6. [Escopo do Projeto](#escopo-do-projeto)
7. [Considerações Finais](#considerações-finais)

---

## Descrição Geral do Processo

O sistema escolhido consiste em um **drone agrícola** equipado com um reservatório de calda (mistura de água e defensivo agrícola/fertilizante líquido), sistema de bombeamento e bicos de pulverização, utilizado para aplicação de insumos em lavouras. O processo abrange desde a etapa de preparo e carregamento da calda até a aplicação em voo sobre a área de cultivo.

O sistema pode ser dividido em duas frentes operacionais:

- **Estação de solo (preparo e abastecimento):** responsável pela mistura da calda química, controle de nível dos tanques e abastecimento do drone.
- **Unidade embarcada (drone):** responsável pela pulverização em voo, com controle de vazão, pressão, altitude e rota de aplicação.

## Objetivo do Sistema de Supervisão e Controle

O sistema SCADA a ser projetado terá como objetivo monitorar e, quando aplicável, controlar remotamente as seguintes funções do processo:

- Monitoramento do nível e vazão do reservatório de calda;
- Controle e supervisão da pressão do sistema de pulverização;
- Acompanhamento da velocidade, altitude e posição de voo (GPS);
- Monitoramento do nível de bateria e autonomia restante;
- Supervisão de condições ambientais que impactam a aplicação (vento, temperatura, umidade);
- Geração de alarmes em caso de falhas operacionais (baixa pressão, nível crítico de bateria, obstrução de bicos, desvio de rota);
- Registro histórico de dados (data logging) para rastreabilidade da aplicação.

## Variáveis do Processo

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

## Arquitetura Proposta

A arquitetura do sistema SCADA seguirá o modelo hierárquico tradicional, adaptado ao contexto do drone agrícola:

1. **Nível de campo:** sensores e atuadores embarcados no drone e na estação de abastecimento (nível, vazão, pressão, GPS, bateria, bomba, válvulas).
2. **Nível de aquisição:** microcontrolador/RTU embarcado no drone responsável pela leitura dos sensores e acionamento dos atuadores, com comunicação sem fio (telemetria via rádio ou Wi-Fi) com a estação base.
3. **Nível de supervisão (servidor SCADA):** recebe os dados de telemetria, armazena o histórico (data logging) e disponibiliza a lógica de alarmes.
4. **Nível de interface (HMI/Dashboard):** painel de supervisão para o operador acompanhar em tempo real as variáveis do processo, visualizar alarmes e, quando aplicável, enviar comandos de controle.

*[Inserir aqui o diagrama de arquitetura do sistema — campo, aquisição, servidor SCADA e HMI.]*

## Justificativa da Escolha

A escolha do drone agrícola como planta do projeto se justifica pelos seguintes fatores:

- O processo possui variáveis físicas e químicas mensuráveis em tempo real, compatíveis com os conceitos de aquisição de dados abordados na disciplina;
- Permite a aplicação prática de conceitos como alarmes, controle supervisório, histórico de dados e arquitetura em camadas;
- É um tema atual e relevante, alinhado a aplicações reais de automação na agricultura de precisão;
- Possibilita a integração entre um subsistema fixo (estação de abastecimento) e um subsistema móvel (drone), enriquecendo a discussão sobre comunicação e telemetria em sistemas SCADA.

## Escopo do Projeto

Para fins de desenvolvimento dentro do prazo da disciplina, o grupo delimitará o escopo do projeto às seguintes funcionalidades:

- Monitoramento simulado das variáveis de processo (nível, vazão, pressão, bateria);
- Implementação de um painel de supervisão (HMI) com indicadores em tempo real;
- Configuração de alarmes para condições críticas;
- Registro histórico de dados (data logging);
- *[demais itens a definir pelo grupo]*

## Considerações Finais

A definição da planta apresentada neste documento servirá de base para o desenvolvimento das próximas etapas do projeto, incluindo a especificação detalhada da arquitetura SCADA, a implementação da lógica de aquisição e controle, e o desenvolvimento da interface de supervisão.
