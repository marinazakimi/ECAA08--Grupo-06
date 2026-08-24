# Aula 03: Tautologias, Contradições e Validação Formal de Intertravamentos

## 1. Fundamentos Matemáticos: Classificação Semântica de Fórmulas Proposicionais

Dada uma fórmula proposicional $W(p_1, p_2, \dots, p_n)$ com $n$ variáveis atômicas, seu espaço de interpretações possui cardinalidade $2^n$.

1. **Tautologia ($\models W$):** Uma fórmula que avalia como **Verdadeira** ($1$) para **todas** as $2^n$ valorações possíveis. Em automação aeronáutica e segurança funcional, uma tautologia representa uma **garantia invariante de segurança** que independe do estado de voo operacional do drone.
2. **Contradição / Insatisfatível ($W \models \bot$):** Uma fórmula que avalia como **Falsa** ($0$) para todas as $2^n$ valorações. Representa a **impossibilidade física e lógica** de ocorrência de um estado perigoso na operação.
3. **Fórmula Contingente / Satisfatível:** Uma fórmula que assume valor Verdadeiro para ao menos uma valoração e Falso para ao menos uma outra. Descreve o comportamento dinâmico operacional padrão do voo.

---

## 2. Modelagem Matemática de Intertravamentos e Prova de Invariante de Segurança

### 2.1. Intertrava de Trip de Emergência do Drone Agrícola
Se houver perda de sinal GPS ($g_1$), bateria em nível crítico ($b_1$), rajada de vento severa ($w_1$) ou acionamento do botão de emergência na estação de solo ($e_1$), a bomba de calda deve ser desativada ($\neg p_1$), os motores devem ser desarmados ou forçados ao pouso de emergência ($\neg m_1$) e o alarme na IHM do piloto acionado ($a_1$):

$$F \equiv g_1 \lor b_1 \lor w_1 \lor e_1$$
$$\text{Regra}_{\text{Trip}} \equiv F \rightarrow (\neg p_1 \land \neg m_1 \land a_1)$$

### 2.2. Prova Formal de Teorema de Segurança Funcional
* **Estado de Perigo Catastrófico ($S_{\text{perigo}}$):** Operação simultânea com botão de emergência (Kill Switch) acionado e motores armados/girando:
$$S_{\text{perigo}} \equiv e_1 \land m_1$$

* **Teorema de Segurança:** Sob a vigência estrita da regra de intertravamento na controladora de voo ($e_1 \rightarrow \neg m_1$), o estado de perigo $S_{\text{perigo}}$ é uma **CONTRADIÇÃO**:

$$\Phi = S_{\text{perigo}} \land (e_1 \rightarrow \neg m_1)$$

**Demonstração por Equivalências Notáveis:**
1. Reescrevendo a implicação pela equivalência material ($A \rightarrow B \equiv \neg A \lor B$):
   $$\Phi = (e_1 \land m_1) \land (\neg e_1 \lor \neg m_1)$$
2. Aplicando a propriedade distributiva da conjunção sobre a disjunção:
   $$\Phi = \big((e_1 \land m_1) \land \neg e_1\big) \lor \big((e_1 \land m_1) \land \neg m_1\big)$$
3. Reordenando pelos axiomas de comutatividade e associatividade:
   $$\Phi = \big((e_1 \land \neg e_1) \land m_1\big) \lor \big(e_1 \land (m_1 \land \neg m_1)\big)$$
4. Pelo Princípio da Não-Contradição ($x \land \neg x \equiv \mathbf{F}$):
   $$\Phi = (\mathbf{F} \land m_1) \lor (e_1 \land \mathbf{F})$$
5. Pelo elemento nulo da conjunção ($\mathbf{F} \land x \equiv \mathbf{F}$):
   $$\Phi = \mathbf{F} \lor \mathbf{F} \equiv \mathbf{F} \quad (\text{Q.E.D.})$$

Portanto, a negação do estado de perigo $\neg \Phi \equiv \neg \mathbf{F} \equiv \mathbf{V}$ é uma **TAUTOLOGIA**.

```mermaid
graph TD
    Interlock["Regra de Intertravamento: e1 -> ¬m1"] --> AND["Conjunção Lógica"]
    Risk["Estado de Perigo: e1 ∧ m1"] --> AND
    AND --> Simpl["Distribuição: (e1 ∧ ¬e1 ∧ m1) ∨ (e1 ∧ m1 ∧ ¬m1)"]
    Simpl --> Zero["(FALSO ∧ m1) ∨ (e1 ∧ FALSO)"]
    Zero --> Result["Resultado: FALSO (Contradição Provada)"]
