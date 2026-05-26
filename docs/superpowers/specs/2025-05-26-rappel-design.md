# Design Spec: Desconto de Rappel no Motor Cooprofar

**Data:** 2025-05-26
**Status:** Aprovado pelo utilizador
**Scope:** Adição de um desconto de Rappel aplicável ao preço intermédio da compra regular, com impacto no cálculo de vantagem e exportação.

---

## 1. Visão e Objectivos

Adicionar um parâmetro adicional "Rappel" (%) ao sistema de análise de rentabilidade. Este parâmetro representa um desconto de retrocessão (cashback) aplicado ao *preço líquido já com desconto do escalão*. O valor do rappel não pode exceder **1%** (validação a nível de UI e fallback de segurança). O valor default é **0.0%**.

O Preço Líquido Final (após Rappel) passa a ser o novo **baseline** para comparação com o `PVFCampanha`.

### Exemplo
Para PVF = 10.00€, Escalão 1 (Desconto = 8.3%):
- Preço Compra Regular = 10.00 × (1 - 0.083) = 9.17€
- Rappel = 1% → Desconto Rappel = 9.17 × 0.01 = 0.0917€
- **Preço Final Rappel** = 9.17 - 0.0917 = **9.08€** (arredondado a 2 casas)

---

## 2. Componentes Afectados

| Ficheiro | Alteração |
|---|---|
| `app.py` | Novo widget na Sidebar (`rappel_percent`), validação, passagem para `evaluate_cooprofar`. |
| `core/engine/calculator.py` | Expansão de `evaluate_cooprofar(..., rappel_percent=0.0)`, novas colunas, novo critério de vantagem. |

**Não alterados:** `condicoes_cooprofar.json`, `data_parser.py`, `infarmed_scraper.py`.

---

## 3. UI / Sidebar — Input de Rappel

Após o bloco dos 6 descontos por escalão, adiciona-se um separador visual e o campo:

**Nota de layout:** O bloco de Rappel é colocado **antes** da secção LinkedIn na sidebar, de modo a evitar overlap com elementos de posição fixa/sticky. O CSS da secção LinkedIn foi alterado de `position: fixed` para `position: sticky` dentro do fluxo da sidebar.

```python
st.sidebar.markdown("<hr style='border-top: 1px solid #555; margin: 1rem 0;'>", unsafe_allow_html=True)
st.sidebar.subheader("Desconto de Rappel (%)")
if 'rappel_percent' not in st.session_state:
    st.session_state['rappel_percent'] = 0.0
rappel = st.sidebar.number_input(
    "Rappel (%)",
    value=float(st.session_state['rappel_percent']),
    min_value=0.0,
    max_value=1.0,
    step=0.1,
    format="%.2f"
)
st.session_state['rappel_percent'] = rappel
```

A validação do limite é feita nativamente por `max_value=1.0`, eliminando a necessidade de warning manual.

---

## 4. Lógica Matemática (Core)

### 4.1. Preço Compra Regular (existente, renomeado para clareza)
```python
Preco_Compra_Regular = PVF_template × (1 - Desconto_Escalao / 100)
```

### 4.2. Desconto de Rappel (€)
```python
Desconto_Rappel_EUR = round(Preco_Compra_Regular × (rappel_percent / 100), 2)
```

### 4.3. Preço Líquido Final
```python
Preco_Final_Rappel = round(Preco_Compra_Regular - Desconto_Rappel_EUR, 2)
# Ou equivalentemente:
# Preco_Final_Rappel = round(Preco_Compra_Regular × (1 - rappel_percent / 100), 2)
```

### 4.4. Critério de Vantagem (alterado)
```python
Aprovado = PVFCampanha < Preco_Final_Rappel
```

### 4.5. Diferenças
```python
Diferenca_Absoluta = round(Preco_Final_Rappel - PVFCampanha, 2)
Diferenca_Percentual = round((Diferenca_Absoluta / Preco_Final_Rappel) × 100, 2)
```

---

## 5. Schema Output (Excel e DataFrame)

| Coluna | Tipo | Descrição |
|---|---|---|
| `CNP` | String | Código Nacional |
| `Designacao` | String | Nome do produto (formato Inicial Maiúscula do template) |
| `PVF` | Float € | PVF original do template |
| `Escalao` | Int | Escalão derivado do PVP do Infarmed |
| `Desconto_Escalao` | Float % | Percentagem de desconto do escalão aplicada |
| `Preco_Compra_Regular` | Float € | Líquido após desconto do escalão |
| `Desconto_Rappel_EUR` | Float € | Valor absoluto em € do rappel |
| `Preco_Final_Rappel` | Float € | **Baseline final para comparação** |
| `Preco_Campanha` | Float € | Preço da campanha (template) |
| `Diferenca_Absoluta` | Float € | `Preco_Final_Rappel - Preco_Campanha` |
| `Diferenca_Percentual` | Float % | Variação percentual sobre `Preco_Final_Rappel` |

*Nota:* As colunas `Preco_Compra_Regular`, `Desconto_Rappel_EUR` e `Preco_Final_Rappel` são novas ou promovidas a colunas de exportação.

---

## 6. Fluxo de Dados e Reactividade

```
[Utilizador altera Rappel na Sidebar]
        |
        v
[Streamlit Rerun -> Script completo re-executado]
        |
        v
[evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent)]
        |
        v
[Fresh DataFrame -> st.dataframe] + [Excel Download Button]
```

Garantia: O Streamlit reage a toda a alteração de widget, logo a matriz é sempre recalculada de forma determinística.

---

## 7. Decisões de Design (ADRs Aplicáveis)

- **ADR 002 (Delegação Total da Lógica Contratual à UI):** O valor de Rappel é mantido em `st.session_state` e editável a qualquer momento, sem necessidade de deploy.
- **ADR 004 (Pureza de Funções no Core):** Todo o cálculo matemático permanece concentrado em `evaluate_cooprofar`. O `app.py` apenas faz *data binding* e validação visual.
