# Planeamento de Tarefas - Motor de Análise de Rentabilidade Farmacêutica

Este documento define as tarefas atómicas e sequenciais para a implementação do sistema descrito no `prdv2.md`. Os agentes devem seguir esta ordem rigorosamente. Nenhuma tarefa pode invocar dependências não estabelecidas em passos prévios.

## Fase 1: Infraestrutura e Padrões Arquiteturais

- [x] **Tarefa 1.1: Criar a árvore de diretórios e ficheiros vazios (Ref: PRD Secção 3)**
  - *Comentário técnico: Estrutura de pastas e ficheiros de código base criada com sucesso.*
  - **Ficheiros a criar/verificar**:
    - Criar as pastas `/ui`, `/core/extractor`, `/core/engine`, `/core/parser` na raiz do projeto.
    - Criar os seguintes ficheiros vazios:
      - `/ui/app.py`
      - `/core/extractor/infarmed_scraper.py`
      - `/core/engine/calculator.py`
      - `/core/parser/data_parser.py`
  - **Inputs/Outputs**: N/A. Estritamente criação de estrutura.

## Fase 2: Módulos de Base e Cache Interno (Infarmed)

- [x] **Tarefa 2.1: Migrar/Implementar o Web Scraper (Ref: PRD Secção 2 - Fluxo Inicialização e ADR 002)**
  - *Comentário técnico: Lógica migrada para `download_infarmed_dataset()` com path return e error handling.*
  - **Ficheiro a editar**: `/core/extractor/infarmed_scraper.py`
  - **Função a implementar**: `download_infarmed_dataset() -> str`
  - **Lógica**: Realizar um POST request para o endpoint estrito (extranet.infarmed.pt) utilizando a lógica existente no ficheiro base `download_infarmed_data.py`. Guardar temporariamente o resultado localmente (ex: `infarmed_dataset.xls`).
  - **Outputs**: Caminho (path) absoluto/relativo do ficheiro descarregado. Deve levantar exceção em caso de status != 200.

- [x] **Tarefa 2.2: Implementar rotinas matemáticas puras (Ref: PRD Secção 5.1 e 5.2)**
  - *Comentário técnico: Lógica migrada para `calculator.py` com truncatura imperativa a 2 casas decimais no retorno.*
  - **Ficheiro a editar**: `/core/engine/calculator.py`
  - **Funções a implementar**: 
    - `calcular_escalao(pvp: float) -> int`
    - `calcular_pva(pvp: float) -> float`
    - `calcular_pvf(pvp: float) -> float`
  - **Lógica**: Transportar a lógica contida em `calcular_pvf.py` e `calcular_pva.py`. Aplicar o escalonamento até Escalão 6.
  - **Inputs**: Valor decimal `pvp`.
  - **Outputs**: O PVA e o PVF retornados por estas funções devem ser **estritamente truncados a 2 casas decimais** (`int(valor * 100) / 100`) antes do `return`. O Escalão devolve um `int`.

- [x] **Tarefa 2.3: Implementar o Parser/Higienização do Infarmed (Ref: PRD Secção 4 - Cache Interno)**
  - *Comentário técnico: O dataset é higienizado com Pandas, injetando PVA, PVF e Escalão.*
  - **Ficheiro a editar**: `/core/parser/data_parser.py`
  - **Função a implementar**: `clean_infarmed_dataset(file_path: str) -> pd.DataFrame`
  - **Lógica**: Ler o Excel. Aplicar exclusões: `Comerc.` != "Não comercializado", `Preço (PVP)` não nulo e != "preço livre", `Genérico` == "Não". Converter `Nº registo` para Int e `Preço (PVP)` para Float. Mapear e injetar colunas utilizando funções da Tarefa 2.2 (`PVA`, `PVF`, `Escalao`).
  - **Inputs**: String (path) proveniente da Tarefa 2.1.
  - **Outputs**: `pd.DataFrame` pronta com colunas finais: `Nº registo`, `Nome do medicamento`, `Preço (PVP)`, `PVA`, `PVF`, `Escalao`.

## Fase 3: Módulos de Parsing dos Templates (Uploads)

- [x] **Tarefa 3.1: Parser do Template Cooprofar (Ref: PRD Secção 4 - Input)**
  - *Comentário técnico: O parser da Cooprofar foi implementado e padroniza a coluna `Codigo Nacional` para `CNP` com tipagem Int.*
  - **Ficheiro a editar**: `/core/parser/data_parser.py`
  - **Função a implementar**: `parse_cooprofar_template(file_stream) -> pd.DataFrame`
  - **Lógica**: Ler o ficheiro guardado/inserido pelo user. O template deve ler as colunas de "Código Nacional" (CNP), "PVF" e "PVFCampanha".
  - **Inputs**: Objeto de ficheiro em memória.
  - **Outputs**: `pd.DataFrame` validada.

## Fase 4: Motores de Decisão e Rentabilidade

- [x] **Tarefa 4.1: Implementar o Motor Cooprofar (Ref: PRD Secção 5.4)**
  - *Comentário técnico: Engine implementado com cruzamento exato e rentabilidade calculada com arredondamento seguro a 2 casas decimais.*
  - **Ficheiro a editar**: `/core/engine/calculator.py`
  - **Função a implementar**: `evaluate_cooprofar(df_template: pd.DataFrame, df_infarmed: pd.DataFrame, discounts: dict) -> pd.DataFrame`
  - **Lógica**: Fazer *merge* entre template e `df_infarmed` via CNP. Utilizando o PVF do *template*, calcular `Custo_Regular_Cooprofar = PVF * (1 - (discounts[Escalao] / 100))`. Filtrar a DF onde `PVFCampanha < Custo_Regular_Cooprofar`. Calcular `Diferenca_Absoluta` e `Diferenca_Percentual`.
  - **Inputs**: Duas DataFrames (T3.1 e T2.3) e dicionário da config (Escalões -> Desconto).
  - **Outputs**: Matriz de Rentabilidade final.

## Fase 5: Integração da UI (Streamlit Orchestrator)

- [x] **Tarefa 5.1: Orquestrar Boot & Configurações da Sidebar (Ref: PRD Secção 2 e 6)**
  - *Comentário técnico: Interface inicializada com st.session_state e parse de JSON corrigido para renderização reativa.*
  - **Ficheiro a editar**: `/ui/app.py`
  - **Função a implementar**: `main()` (Ponto de entrada Streamlit)
  - **Lógica**:
    - Tentar executar `download_infarmed_dataset()`. Se falhar, renderizar uploader manual de ficheiro Infarmed. Passar ficheiro para `clean_infarmed_dataset()` e guardar DF em `st.session_state`.
    - Ler `condicoes_cooprofar.json`. Gerar os elementos `st.sidebar.number_input` dinâmicos para a Tabela de Descontos (Escalões 1 a 6) de forma a mutar o json/estado dinamicamente.

- [x] **Tarefa 5.2: Orquestrar UI e Exportação (Ref: PRD Secção 6 e ADR 004)**
  - *Comentário técnico: Implementada UI com exportação Excel nativa (`BytesIO`) e restrição `width='stretch'` aplicada aos componentes df.*
  - **Ficheiro a editar**: `/ui/app.py`
  - **Função a implementar**: Continuação da `main()`
  - **Lógica**:
    - Renderizar uploader. Invocar `parse_cooprofar_template()` e de seguida `evaluate_cooprofar()`. Renderizar a tabela de rentabilidade garantindo `st.dataframe(df, width='stretch')`.
    - **Exportação**: Renderizar o componente `st.download_button` instanciando um Excel exportável através de uma função auxiliar `to_excel_bytes(df)`. Nenhuma chamada a métodos proibidos `use_container_width`.
