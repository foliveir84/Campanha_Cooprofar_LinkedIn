# Equipa de Agentes Autónomos - PharmLogix Engine

Esta equipa foi desenhada com total isolamento de domínios. O objetivo é garantir que a interface gráfica e o motor lógico matemático nunca se sobrepõem, preservando a pureza da arquitetura desenhada no `prd.md`.

## 1. Backend Engineer (`backend_engineer.md`)
- **Domínio:** Pasta `/core/`
- **Responsabilidades:** Extração HTTP, higienização de dataframes (Pandas), cálculo matemático puro (Engine) e parsing de inputs.
- **Proibições Estruturais:** Estritamente proibido de importar ou utilizar o `streamlit` ou interagir com o `st.session_state`.

## 2. Frontend Engineer (`frontend_engineer.md`)
- **Domínio:** Pasta `/ui/` e orquestração do `app.py`.
- **Responsabilidades:** Criação da interface reativa em Streamlit, data-binding, gestão de inputs da Sidebar e invocação dos motores do *Core*.
- **Proibições Estruturais:** Estritamente proibido de escrever cálculos de margens, rentabilidade ou manipulação crua de dataframes de Excel no ficheiro da UI. Tem de consumir as APIs do Backend.

## Regras de Orquestração
1. O **Backend Engineer** atua primeiro e de forma isolada, executando as Fases 1 a 4 do `TASKS.md`.
2. Após o Backend selar os módulos, o **Frontend Engineer** atua em último, assumindo o código existente no `/core/` como "Caixa Negra" funcional, executando apenas a Fase 5.
f