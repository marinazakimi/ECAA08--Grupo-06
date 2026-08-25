# 09. Motor de Inferência

## Introdução

Um **motor de inferência** é o componente responsável por analisar fatos conhecidos e aplicar regras lógicas para obter novas conclusões. Em um sistema de diagnóstico, ele permite transformar dados provenientes de sensores em hipóteses de falha, alarmes e ações recomendadas.

No projeto do **Sistema SCADA aplicado a um Drone Agrícola de Pulverização**, o motor de inferência será utilizado para analisar as condições operacionais da planta a partir das variáveis monitoradas pelo sistema, como nível do reservatório, vazão da calda, pressão de pulverização, bateria e condições ambientais.

O objetivo desta etapa é implementar um mecanismo de inferência baseado em regras, utilizando os algoritmos de **Forward Chaining** e **Backward Chaining**, e integrá-lo ao diagnóstico do sistema.

---

## Base de Conhecimento

O motor de inferência utiliza dois elementos principais:

- **Fatos:** informações conhecidas sobre o estado atual do processo;
- **Regras:** relações lógicas do tipo `SE condição ENTÃO conclusão`.

Os fatos podem ser obtidos diretamente dos sensores ou derivados a partir de limites definidos pelo sistema.

### Exemplo de fatos

A partir das medições:

- Nível do reservatório = 4%;
- Vazão = 0,2 L/min;
- Pressão = 5,2 bar;
- Bomba ligada;
- Válvula de pulverização aberta.

O sistema pode gerar os seguintes fatos:

```text
nivel_critico
vazao_baixa
pressao_alta
bomba_ligada
valvula_aberta
```

Esses fatos serão utilizados pelo motor de inferência para determinar possíveis diagnósticos.

---

## Regras de Diagnóstico

As regras representam o conhecimento sobre o funcionamento da planta.

| Regra | Condição | Conclusão |
|---|---|---|
| R1 | Nível crítico | Falta de insumo |
| R2 | Bomba ligada E válvula aberta E vazão baixa | Falha de pulverização |
| R3 | Bomba ligada E vazão baixa E pressão alta | Possível obstrução |
| R4 | Possível obstrução | Interromper pulverização |
| R5 | Falta de insumo | Interromper pulverização |
| R6 | Bateria crítica | Interromper missão |
| R7 | Vento alto | Suspender pulverização |
| R8 | Bomba ligada E pressão baixa E vazão baixa | Possível vazamento ou falha da bomba |

As regras podem ser representadas computacionalmente no formato:

```python
{
    "nome": "R3",
    "condicoes": {"bomba_ligada", "vazao_baixa", "pressao_alta"},
    "conclusao": "possivel_obstrucao"
}
```

---

## Forward Chaining

O **Forward Chaining**, ou encadeamento para frente, inicia a inferência a partir dos fatos conhecidos.

O algoritmo verifica quais regras possuem todas as suas condições satisfeitas. Quando uma regra é ativada, sua conclusão é adicionada ao conjunto de fatos.

O processo continua até que nenhuma nova conclusão possa ser obtida.

### Funcionamento

```text
Fatos iniciais
      ↓
Verificar regras
      ↓
Condições satisfeitas?
      ↓
Adicionar conclusão aos fatos
      ↓
Executar novamente
      ↓
Nenhum novo fato
      ↓
Fim
```

### Exemplo

Considere os fatos:

```text
bomba_ligada
vazao_baixa
pressao_alta
```

E a regra:

```text
SE bomba_ligada
E vazao_baixa
E pressao_alta
ENTÃO possivel_obstrucao
```

O motor conclui:

```text
possivel_obstrucao
```

Em seguida, outra regra pode utilizar essa conclusão:

```text
SE possivel_obstrucao
ENTÃO interromper_pulverizacao
```

Assim, o motor gera uma cadeia de inferências:

```text
bomba_ligada + vazao_baixa + pressao_alta
                    ↓
          possivel_obstrucao
                    ↓
        interromper_pulverizacao
```

O **Forward Chaining** é adequado para a supervisão em tempo real do SCADA, pois os dados dos sensores são atualizados continuamente e o sistema pode verificar automaticamente todas as consequências relacionadas ao estado atual da planta.

---

## Backward Chaining

O **Backward Chaining**, ou encadeamento para trás, parte de uma hipótese ou objetivo que se deseja verificar.

Em vez de iniciar pelos fatos, o algoritmo pergunta:

> Quais condições precisam ser verdadeiras para que esta conclusão seja válida?

Depois, verifica recursivamente se essas condições estão presentes nos fatos ou podem ser obtidas por outras regras.

### Exemplo

Deseja-se verificar:

```text
possivel_obstrucao
```

Existe a regra:

```text
SE bomba_ligada
E vazao_baixa
E pressao_alta
ENTÃO possivel_obstrucao
```

O algoritmo verifica se existem os fatos:

```text
bomba_ligada
vazao_baixa
pressao_alta
```

Caso todos sejam verdadeiros, a hipótese de obstrução é confirmada.

O **Backward Chaining** é útil quando o operador ou o sistema deseja testar especificamente uma hipótese, como:

- Existe uma possível obstrução?
- Existe risco de falta de insumo?
- A missão deve ser interrompida?
- Existe uma falha de pulverização?

---

## Conversão das Variáveis do Processo em Fatos

As variáveis analógicas provenientes dos sensores precisam ser convertidas em fatos lógicos para serem utilizadas pelo motor de inferência.

Uma possível definição de limites é apresentada abaixo.

| Variável | Condição | Fato gerado |
|---|---|---|
| Nível do reservatório | `< 20%` | `nivel_baixo` |
| Nível do reservatório | `< 5%` | `nivel_critico` |
| Vazão | `< 0,5 L/min` com pulverização ativa | `vazao_baixa` |
| Pressão | `> 5 bar` | `pressao_alta` |
| Pressão | `< 1 bar` com bomba ligada | `pressao_baixa` |
| Bateria | `< 20%` | `bateria_baixa` |
| Bateria | `< 10%` | `bateria_critica` |
| Vento | `> 8 m/s` | `vento_alto` |

Os valores apresentados são utilizados como exemplo para a implementação e poderão ser alterados de acordo com os parâmetros definidos para a planta.

---

## Integração do Motor de Diagnóstico

A integração do motor de diagnóstico com o sistema SCADA pode ser representada da seguinte forma:

```text
Sensores
   ↓
Aquisição de dados
   ↓
Conversão das medições em fatos
   ↓
Motor de Inferência
   ↓
Diagnósticos / Alarmes / Ações
   ↓
SCADA / HMI
```

O motor recebe os valores medidos pelos sensores e realiza inicialmente a classificação das condições do processo.

Por exemplo:

```text
Pressão = 5,2 bar
        ↓
pressao_alta
```

Em seguida, os fatos são analisados pelas regras:

```text
bomba_ligada
vazao_baixa
pressao_alta
        ↓
possivel_obstrucao
        ↓
interromper_pulverizacao
```

As conclusões geradas podem ser utilizadas pelo SCADA para:

- Exibir alarmes na HMI;
- Registrar eventos no histórico;
- Informar o diagnóstico ao operador;
- Recomendar ações corretivas;
- Executar intertravamentos;
- Interromper a pulverização quando necessário.

---

## Diagnósticos Considerados

| Diagnóstico | Evidências utilizadas | Ação sugerida |
|---|---|---|
| Falta de insumo | Nível crítico | Interromper pulverização e realizar abastecimento |
| Possível obstrução | Bomba ligada, vazão baixa e pressão alta | Interromper pulverização e verificar bicos/tubulação |
| Possível vazamento ou falha da bomba | Bomba ligada, vazão baixa e pressão baixa | Verificar bomba, mangueiras e conexões |
| Falha de pulverização | Bomba ligada, válvula aberta e vazão baixa | Verificar sistema de pulverização |
| Bateria crítica | Bateria abaixo do limite crítico | Interromper missão e retornar à base |
| Condição ambiental inadequada | Velocidade do vento elevada | Suspender pulverização |

---

## Pseudocódigo do Forward Chaining

```text
entrada: fatos_iniciais, regras

fatos ← fatos_iniciais
alteracao ← verdadeiro

enquanto alteracao:
    alteracao ← falso

    para cada regra:
        se todas as condições da regra pertencem aos fatos:
            se conclusão ainda não pertence aos fatos:
                adicionar conclusão aos fatos
                alteracao ← verdadeiro

retornar fatos
```

---

## Pseudocódigo do Backward Chaining

```text
função backward_chaining(objetivo):

    se objetivo pertence aos fatos:
        retornar verdadeiro

    para cada regra cuja conclusão = objetivo:

        verificar todas as condições da regra

        se todas as condições forem verdadeiras:
            retornar verdadeiro

    retornar falso
```

---

## Implementação

A implementação prática do motor de inferência é apresentada no arquivo:

`03. Motor de Inferência.ipynb`

O notebook contém:

1. Definição da base de fatos;
2. Definição das regras de diagnóstico;
3. Implementação do algoritmo de Forward Chaining;
4. Implementação do algoritmo de Backward Chaining;
5. Conversão das medições dos sensores em fatos;
6. Execução de cenários de diagnóstico;
7. Integração entre o motor de inferência e as variáveis do drone;
8. Exibição das regras ativadas e dos diagnósticos obtidos.

---

## Considerações Finais

A utilização de um motor de inferência permite adicionar uma camada de diagnóstico inteligente ao sistema SCADA.

O **Forward Chaining** é utilizado principalmente para analisar continuamente os dados provenientes dos sensores e identificar automaticamente possíveis condições de falha.

O **Backward Chaining** complementa essa abordagem ao permitir verificar hipóteses específicas a partir de um diagnóstico desejado.

A combinação dos dois métodos possibilita transformar os dados coletados pelos sensores em informações úteis ao operador, permitindo que o sistema não apenas apresente valores de processo, mas também identifique situações anormais, gere diagnósticos e indique possíveis ações corretivas.
