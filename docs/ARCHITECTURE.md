# Arquitetura do Sistema PharmLogix

Este documento detalha a estrutura técnica, o fluxo de dados e as decisões de design que sustentam o motor PharmLogix. É destinado a engenheiros e mantenedores que necessitem compreender a mecânica interna do sistema para manutenção ou expansão.

## 1. Estrutura de Diretórios

O projeto segue uma separação clara de responsabilidades, isolando a interface de utilizador da lógica de negócio e processamento de dados.

```text
/
├── ui/                     # Interface de Utilizador (Streamlit)
│   └── app.py              # Orquestrador da UI e gestão de estado
├── core/                   # Núcleo da Aplicação (Lógica Pura)
│   ├── engine/             # Motores de cálculo e avaliação
│   │   └── calculator.py   # Lógica financeira e matemática
│   ├── parser/             # Higienização e parsing de dados
│   │   └── data_parser.py  # Processamento de Excel e Infarmed
│   └── extractor/          # Comunicação externa
│       └── infarmed_scraper.py # Scraper do portal Infarmed
├── condicoes_cooprofar.json # Configuração padrão de descontos
├── requirements.txt        # Dependências do projeto
└── prdv2.md                # Especificação de requisitos (Histórico)
```

## 2. Fluxo de Dados Principal

O sistema opera num pipeline sequencial que garante a integridade dos dados antes da análise financeira:

1.  **Ingestão da Base de Referência (Infarmed)**:
    - O sistema tenta descarregar automaticamente o dataset oficial do Infarmed via `infarmed_scraper.py`.
    - O ficheiro é processado pelo `data_parser.py`, que aplica filtros de exclusão (apenas MSRM não genéricos e comercializados) e injeta colunas calculadas de PVA, PVF e Escalão.
2.  **Configuração de Contexto**:
    - O `app.py` carrega as taxas e descontos do utilizador (via JSON ou Sidebar) para o `st.session_state`.
    - Inclui descontos por escalão e, opcionalmente, um **Desconto de Rappel** (máx. 1%), guardado dinamicamente em sessão.
3.  **Upload e Parsing de Templates**:
    - O utilizador submete um Excel de campanha Cooprofar.
    - O parser extrai os dados, normaliza descrições (Title Case) e valida códigos CNP.
4.  **Avaliação de Rentabilidade**:
    - O `calculator.py` realiza o cruzamento (merge) entre o template e a base Infarmed.
    - Aplica as fórmulas de custo regular vs. custo campanha.
    - Se Rappel > 0, aplica-o ao preço regular como desconto adicional.
    - O novo **Preço Final Rappel** torna-se o baseline de comparação com o PVFCampanha.
    - Filtra apenas os registos onde a campanha é financeiramente vantajosa.
5.  **Output**:
    - Os resultados são renderizados na UI e convertidos em fluxo de bytes para exportação Excel, agora incluindo colunas de Rappel (valor absoluto e preço final).

## 3. Decisões Técnicas de Relevo

### 3.1. Isolamento Estrito (Core vs UI)
Uma regra inviolável do projeto é que nenhum ficheiro dentro da pasta `core/` importa a biblioteca `streamlit`. Isto garante que a lógica de negócio possa ser testada ou migrada para outros formatos (como uma API ou CLI) sem dependências da interface gráfica.

### 3.2. Precisão Financeira (Truncatura Imperativa)
Ao contrário do arredondamento comercial padrão (`round`), o PharmLogix utiliza **truncatura estrita a duas casas decimais** para o cálculo de PVA e PVF: `int(valor * 100) / 100`. Esta decisão baseia-se na necessidade de replicar exatamente o comportamento dos sistemas de faturação farmacêutica, onde arredondamentos para cima podem gerar discrepâncias legais.

**Nota sobre o Desconto de Rappel**: Ao contrário dos cálculos de PVA/PVF, o valor do rappel é calculado com **arredondamento padrão** (`round(preco * (rappel/100), 2)`) e o preço final é ajustado com `round(..., 2)`, conforme prática comercial para descontos retrocessivos.

### 3.3. Gestão de Memória
A exportação para Excel utiliza `io.BytesIO`. Isto significa que o ficheiro `.xlsx` de resultado é gerado inteiramente na memória RAM e enviado diretamente para o browser do utilizador, evitando a criação de ficheiros temporários no servidor ou disco local, o que aumenta a segurança e performance em ambientes de Cloud.

## 4. Manutenção de Cache
O sistema utiliza o `st.session_state` para manter a base de dados Infarmed (que é pesada) em memória enquanto a sessão do browser estiver ativa. Isto evita downloads repetidos e torna a troca entre separadores instantânea para o utilizador.
