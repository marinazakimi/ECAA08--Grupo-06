# 🚁 ECAA08 - Arquitetura de Sistemas SCADA | Grupo 06

**Definição da Planta:** Sistema SCADA aplicado a um Drone Agrícola de Pulverização

> **Disciplina:** ECAA08 - Arquitetura de Sistemas SCADA  
> **Integrantes:** Arthur, Caique, Luis Felipe, Marina  
> **Data:** 10 de agosto de 2026  

---

## 📋 Resumo

Este documento apresenta a definição da planta escolhida pelo grupo para o desenvolvimento do projeto da disciplina de Sistemas SCADA. Optou-se por um **drone agrícola de pulverização**, tratado como um processo supervisionado, no qual variáveis de operação, sensores e atuadores são monitorados e controlados por meio de uma arquitetura SCADA. O presente documento descreve o processo, os objetivos de supervisão e controle, as variáveis envolvidas, a arquitetura proposta e a justificativa da escolha.

---

## 📑 Sumário

1. [Descrição Geral do Processo](#1-descrição-geral-do-processo)
2. [Objetivo do Sistema de Supervisão e Controle](#2-objetivo-do-sistema-de-supervisão-e-controle)
3. [Variáveis do Processo](#3-variáveis-do-processo)
4. [Arquitetura Proposta](#4-arquitetura-proposta)
5. [Lógica de Controle e Segurança (Etapa 01)](#5-lógica-de-controle-e-segurança-etapa-01)
6. [Justificativa da Escolha](#6-justificativa-da-escolha)
7. [Escopo do Projeto](#7-escopo-do-projeto)
8. [Considerações Finais](#8-considerações-finais)

---

## 1. Descrição Geral do Processo

O sistema escolhido consiste em um **drone agrícola** equipado com um reservatório de calda (mistura de água e defensivo agrícola/fertilizante líquido), sistema de bombeamento e bicos de pulverização, utilizado para aplicação de insumos em lavouras. O processo abrange desde a etapa de preparo e carregamento da calda até a aplicação em voo sobre a área de cultivo.

O sistema pode ser dividido em duas frentes operacionais:

- **Estação de solo (preparo e abastecimento):** responsável pela mistura da calda química, controle de nível dos tanques e abastecimento do drone.
- **Unidade embarcada (drone):** responsável pela pulverização em voo, com controle de vazão, pressão, altitude e rota de aplicação.

## 2. Objetivo do Sistema de Supervisão e Controle

O sistema SCADA a ser projetado terá como objetivo monitorar e, quando aplicável, controlar remotamente as seguintes funções do processo:

- Monitoramento do nível e vazão do reservatório de calda;
- Controle e supervisão da pressão do sistema de pulverização;
- Acompanhamento da velocidade, altitude e posição de voo (GPS);
- Monitoramento do nível de bateria e autonomia restante;
- Supervisão de condições ambientais que impactam a aplicação (vento, temperatura, umidade);
- Geração de alarmes em caso de falhas operacionais (baixa pressão, nível crítico de bateria, obstrução de bicos, desvio de rota);
- Registro histórico de dados (*data logging*) para rastreabilidade da aplicação.

## 3. Variáveis do Processo

Para garantir o controle e a supervisão adequados, as seguintes variáveis (analógicas e discretas) foram mapeadas preliminarmente:

* **Variáveis Analógicas (Sensores):**
  * Nível do reservatório de calda (%)
  * Pressão na linha de pulverização (Bar/PSI)
  * Vazão da bomba de pulverização (L/min)
  * Nível de carga da Bateria (%) e Tensão (V)
  * Altitude de voo (m) e Velocidade (km/h)
* **Variáveis Discretas (Atuadores/Status):**
  * Status da bomba de pulverização (Ligado/Desligado)
  * Status das válvulas dos bicos (Aberta/Fechada)
  * Alarmes de segurança (Ex: Nível Crítico, Falha de Comunicação)

## 4. Arquitetura Proposta

A arquitetura do sistema SCADA seguirá o modelo hierárquico tradicional, adaptado ao contexto do drone agrícola:

1. **Nível de Campo:** sensores e atuadores embarcados no drone e na estação de abastecimento (nível, vazão, pressão, GPS, bateria, bomba, válvulas).
2. **Nível de Aquisição:** microcontrolador/RTU embarcado no drone responsável pela leitura dos sensores e acionamento dos atuadores, com comunicação sem fio (telemetria via rádio ou Wi-Fi) com a estação base.
3. **Nível de Supervisão (Servidor SCADA):** recebe os dados de telemetria, armazena o histórico (*data logging*) e disponibiliza a lógica de alarmes.
4. **Nível de Interface (HMI/Dashboard):** painel de supervisão para o operador acompanhar em tempo real as variáveis do processo, visualizar alarmes e, quando aplicável, enviar comandos de controle.

> 🖼️ *[Inserir aqui o diagrama de arquitetura do sistema — campo, aquisição, servidor SCADA e HMI.]*

## 5. Lógica de Controle e Segurança (Etapa 01)

Com base nos estudos iniciais de Lógica Computacional, o sistema SCADA incorporará:
* **Partida Segura e Intertravamento:** Lógicas booleanas para impedir, por exemplo, que a bomba de pulverização seja acionada se o reservatório estiver vazio, ou que o drone decole com bateria insuficiente.
* **Regras de Diagnóstico:** Motor de inferência para cruzar dados (ex: se a bomba está ligada e a vazão é zero, gerar alarme de "Bico Obstruído" ou "Vazamento").

## 6. Justificativa da Escolha

A escolha do drone agrícola como planta do projeto se justifica pelos seguintes fatores:

- O processo possui variáveis físicas e químicas mensuráveis em tempo real, compatíveis com os conceitos de aquisição de dados abordados na disciplina;
- Permite a aplicação prática de conceitos como alarmes, controle supervisório, histórico de dados e arquitetura em camadas;
- É um tema atual e relevante, alinhado a aplicações reais de automação na agricultura de precisão;
- Possibilita a integração entre um subsistema fixo (estação de abastecimento) e um subsistema móvel (drone), enriquecendo a discussão sobre comunicação e telemetria em sistemas SCADA.

## 7. Escopo do Projeto

Para fins de desenvolvimento dentro do prazo da disciplina, o grupo delimitará o escopo do projeto às seguintes funcionalidades:

- Monitoramento simulado das variáveis de processo (nível, vazão, pressão, bateria);
- Implementação de um painel de supervisão (HMI) com indicadores em tempo real;
- Configuração de alarmes para condições críticas baseados em lógica proposicional;
- Registro histórico de dados (*data logging*);
- *[demais itens a definir pelo grupo]*

## 8. Considerações Finais

A definição da planta apresentada neste documento servirá de base para o desenvolvimento das próximas etapas do projeto, incluindo a especificação detalhada da arquitetura SCADA, a implementação da lógica de aquisição e controle, e o desenvolvimento da interface de supervisão.
