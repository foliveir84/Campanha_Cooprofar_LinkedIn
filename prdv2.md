# 1. Visão e Objectivos

O sistema é um motor de análise de rentabilidade farmacêutica que determina deterministicamente se a aquisição de um medicamento deve ocorrer via modelo de Campanha Grossista (indexado ao Preço de Venda ao Armazém - PVA + Fee) ou via modelo de Compra Regular (indexado ao Preço de Venda à Farmácia - PVF + Desconto Comercial).

### Exclusões Explícitas
Para garantir o isolamento do domínio, este sistema **NÃO**:
1. Conecta, lê ou escreve diretamente em bases de dados relacionais persistentes (SQL/NoSQL) ou ERPs locais.
2. Faz web-scraping a nenhum portal exterior que não o endpoint estrito "extranet.infarmed.pt".
3. Guarda histórico de simulações, sessões de utilizador ou ficheiros após o fecho da interface/sessão ativa.
4. Toma decisões probabilísticas ou baseadas em LLMs para a avaliação financeira; a matemática de aprovação é estritamente booleana.

# 2. Utilizadores e Fluxos Críticos

**Fluxo de Inicialização (Boot & Sync)**
1. O sistema arranca a interface.
2. Assíncronamente, aciona o módulo de extração HTTP (POST Request via PrimeFaces JSF) para o endpoint do Infarmed.
3. Sucesso: O ficheiro `infarmed_dataset.xls` é alocado em memória RAM/temp file.
4. Falha: O sistema bloqueia cálculos, exibe erro e ativa a "Janela de Upload Manual do Ficheiro Infarmed".
5. Na barra lateral (Sidebar), as condições de desconto Cooprofar são carregadas por defeito a partir do ficheiro `condicoes_cooprofar.json` (podendo ser editadas pelo utilizador).

**Fluxo de Operação A: Separador Campanha Cooprofar**
1. O utilizador seleciona o separador "Campanha Cooprofar".
2. O utilizador efetua upload do *template* de Campanha Cooprofar.
3. O sistema cruza os produtos com o ficheiro Infarmed para obter o PVP e calcular o Escalão correspondente.
4. A partir do PVF (presente no *template*), aplica o desconto correspondente ao Escalão da configuração Cooprofar.
5. O sistema compara diretamente este PVF com desconto face ao Preço de Campanha (PVFCampanha).
6. São apresentados (e disponibilizados para exportação) apenas os produtos mais vantajosos na campanha (PVFCampanha < PVF com desconto).

**Fluxo de Finalização**
1. O utilizador invoca a ação de "Exportar".
2. O sistema serializa a matriz filtrada para `.xlsx` e disponibiliza para download via browser.

# 3. Arquitectura do Sistema e Padrões de Design

A arquitetura obedece a um padrão modular *Model-View-Controller* modificado (Core-Orchestrator-UI), desacoplando inteiramente os *dataframes* das renderizações gráficas.

*   `/ui`: Módulo Streamlit (`app.py`), exclusivamente responsável pelo *data-binding*, parâmetros de barra lateral e *file uploading*.
*   `/core/extractor`: Módulo de extração HTTP (`infarmed_scraper.py`).
*   `/core/engine`: Funções matemáticas puras (`calculator.py`). Avaliam escalões e margens baseando-se unicamente em tensores numéricos (Pandas/Numpy).
*   `/core/parser`: Rotinas de higienização de input (`data_parser.py`).

### Regras de Ouro (Invioláveis)
1. **Renderização UI**: O parâmetro `use_container_width` está globalmente proibido. Qualquer tabela, gráfico ou contentor deve utilizar estritamente `width='stretch'` ou `width='content'`.
2. **Pureza de Funções**: Nenhuma função no diretório `/core` pode fazer importações do módulo `streamlit`. Erros do *core* devolvem *Exceptions* padrão Python que são capturadas e formatadas na UI.
3. **Parametrização Injetada**: Todos os thresholds monetários (ex: `6.68`, `64.68`) e multiplicadores (ex: `0.92`, `0.004`) são consumidos a partir de um dicionário/dataclass injetado.
4. **Identidade Visual Pharmacoach**: O tema visual (glassmorphism, gradientes neon, paleta roxo-azul) é injetado via CSS no `app.py`. Logos são carregados como base64. A identidade deve ser consistente em todos os componentes.

# 4. Modelo de Dados e Schemas

**Schema Infarmed Dataset (Cache Interno e Higienização)**
O *dataset* em bruto passa obrigatoriamente por `tratar_ficheiro_infarmed.py`, originando uma *dataframe* de MSRM Não Genéricos.
**Filtros de Exclusão (Linhas Descartadas):**
*   `Comerc.` == "Não comercializado"
*   `Preço (PVP)` == "preço livre" ou Nulo/NaN
*   `Genérico` == "Não" (Bloqueio estrito a medicamentos não genéricos)


**Formatação e Injeção de Colunas:**
*   `Nº registo` (Inteiro): CNP.
*   `Nome do medicamento` (String).
*   `Preço (PVP)` (Float).
*   `PVA` e `PVF` (Float): Calculados e **estritamente truncados** a 2 casas decimais (`int(x * 100) / 100`).
*   `Escalao` (Int): Derivado do PVP.

**Schema Input: Templates Campanha**
*   **Cooprofar**: Ficheiro com Código Nacional (CNP), Designação (Coluna B ou título explícito), PVF e Preço de Campanha (PVFCampanha).

**Schema Output (Matriz de Rentabilidade)**
*   `CNP` (String): Forçado estritamente a formato de texto para evitar formatações numéricas nos ERPs aquando da exportação.
*   `Designacao` (String): Extraída unicamente a partir dos templates (formato Inicial Maiúscula), ignorando o nome oficial proveniente do Infarmed.
*   `Preco_Compra_Regular` (Float, Formato €. 2 casas decimais) - Corresponde ao PVF com desconto.
*   `Preco_Campanha` (Float, Formato €. 2 casas decimais).
*   `Diferenca_Absoluta` (Float, Regular - Campanha. 2 casas decimais).
*   `Diferenca_Percentual` (Float, Diferenca_Absoluta / Preco_Compra_Regular * 100. Formato %).

# 5. Lógica de Negócio Core (O Motor)

### Passo 5.1: Definição de Escalão `f_E(PVP) -> int`
A matriz de escalões é calculada pelo *boundary* superior estrito (inclusive):
*   PVP ≤ 6.68 -> Escalão 1
*   PVP ≤ 9.97 -> Escalão 2
*   PVP ≤ 14.10 -> Escalão 3
*   PVP ≤ 26.96 -> Escalão 4
*   PVP ≤ 64.68 -> Escalão 5
*   PVP > 64.68 -> Escalão 6

### Passo 5.2: Derivação e Truncatura do PVA e PVF
As rotinas matemáticas base encontram-se segregadas.
**Regra Crítica de Arredondamento (Truncatura)**: O processamento no `tratar_ficheiro_infarmed.py` determina que, ao derivar o PVA e o PVF a partir do PVP, os valores **não sofrem arredondamento tradicional (round)**. São estritamente truncados à 2ª casa decimal: `int(valor * 100) / 100`.

### Passo 5.3: Configuração de Descontos Cooprofar
O sistema carrega os descontos por escalão ($D_E$) a partir do ficheiro `condicoes_cooprofar.json` (Ex: Escalão 1 -> 8.3%). Este mapeamento serve de referencial para o "Preço de Compra Regular".
$$ Custo\_Regular\_Cooprofar = PVF \times (1 - (D_E / 100)) $$

### Passo 5.4: Motor de Decisão (Filtro de Vantagem)

**Motor Cooprofar:**
1. Determina-se o Escalão $E$ via PVP do Infarmed.
2. Aplica-se o desconto $D_E$ configurado ao PVF (presente no template).
**Aprovação (Vantajoso):** $PVFCampanha < Custo\_Regular\_Cooprofar$

# 6. Interfaces, Inputs e Outputs

### Identidade Visual (Pharmacoach Design System)

**Paleta de Cores:**
- `#1a0036` / `#120021` - Background (gradiente roxo profundo)
- `#8d3dff` / `#c431fb` - Primary Purple (acentos, títulos)
- `#4fa8ff` - Blue Accent (links, botões, gradientes)
- `#b38cff` - Soft Glow (textos secundários)

**Elementos de Marca:**
- **Header**: Logo `Logo_Pharmacoach.jpg` (55px) + título "Pharmacoach Engine" com gradiente
- **Sidebar**: Fundo gradiente escuro, inputs com estilo glassmorphism
- **LinkedIn**: Logo `LogoLinkedIN.png` (40px) no fundo da sidebar + link `linkedin.com/in/foliveir/` clicável
- **Botões**: Gradiente roxo-azul com hover glow
- **CSS Injection**: Via `st.markdown(unsafe_allow_html=True)` no `app.py`

### Painel Paramétrico (Sidebar UI)
*   `Tabela_Descontos_Escalao`: Carregada por defeito a partir de `condicoes_cooprofar.json`. Apresentada como campos de edição num formulário na *Sidebar* para permitir alterações on-the-fly pelo utilizador.

### Exportação Final
Ficheiro serializado através do `openpyxl` subjacente do Pandas via `DataFrame.to_excel(index=False)`. Ficheiro deve possuir extensão `.xlsx`. As células não são auto-formatadas visualmente (cores), mantendo a estrita legibilidade de dados para importação em ERPs sequenciais, cumprindo com formato nativo bruto, excepto o cabeçalho fixo estipulado na secção 4.

# 7. ADRs (Decisões de Arquitectura Registadas)

**ADR 001: Abstração do Download do Sistema Infarmed**
*   **Porquê:** A extração assenta no *parsing* do PrimeFaces `ViewState`. Mudanças microscópicas na estrutura HTML do Portal quebrarão o POST Request. Garantimos assim a resiliência com a "Upload Manual Box" como *fallback* mandatário caso o `status_code` HTTP não seja 200, preservando a utilidade a 100% da aplicação.

**ADR 002: Delegação Total da Lógica Contratual à UI (Zero Hardcode)**
*   **Porquê:** Portarias Governamentais relativas a margens das farmácias e *Fees* de acordos comerciais flutuam num quadro temporal curto. Ao transitar tabelas e constantes de descontos/fees para `st.session_state` (sidebar), o custo operacional de manutenção do software atinge zero e impede *deployments* redundantes.

**ADR 003: UI Component Flag Fixation (`width='stretch'`)**
*   **Porquê:** Prevenção de quebra de interface no *roadmap* de versão do Streamlit. Antecipa e resolve *deprecation warnings* planeados para 2026 sem sacrificar controlo granular do *layout* reativo num contexto de analítica de dados tabulares largos.

**ADR 004: Identidade Visual Pharmacoach (Glassmorphism)**
*   **Porquê:** A marca Pharmacoach exige uma identidade visual distintiva (glassmorphism, neon gradients, dark UI premium) que comunica inovação e confiança no setor farmacêutico. O CSS é injetado dinamicamente para permitir evolução da marca sem refatoração do core.