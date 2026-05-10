# PharmLogix: Motor de Análise de Rentabilidade Farmacêutica

Bem-vindo à documentação oficial do **PharmLogix**. Este projeto foi desenvolvido para resolver um problema estrito, moroso e manual na gestão farmacêutica: **determinar de forma matemática, determinística e instantânea** se a aquisição de um medicamento é mais rentável através do modelo de Campanha Grossista ou através do modelo de Compra Regular.

## 1. O Problema que o PharmLogix Resolve

No dia-a-dia da gestão de compras de uma farmácia, os gestores lidam com propostas de aquisição (Campanhas) por parte de grossistas como a **Cooprofar** ou a **Empifarma**. O grande desafio é que os referenciais de preço mudam dependendo da entidade:
*   As compras regulares são indexadas ao **Preço de Venda à Farmácia (PVF)**, sobre o qual é aplicado um desconto comercial variável de acordo com o Escalão do medicamento.
*   As campanhas são muitas vezes indexadas ao **Preço de Venda ao Armazém (PVA)**, sujeito a taxas logísticas (Fees), ou oferecem um Preço de Campanha fixo fechado (PVFCampanha).

Fazer o cruzamento de centenas ou milhares de medicamentos presentes num Excel de campanha contra a base de dados em constante mutação do **Infarmed** para perceber qual a margem real e onde se ganha dinheiro é uma tarefa humana incomportável. O **PharmLogix** automatiza este cruzamento na totalidade.

## 2. Pré-Requisitos do Sistema

O PharmLogix é um software construído em Python, focado numa implementação leve e portátil, e que não requer bases de dados SQL, motores externos complexos ou dependências pesadas.

**Requisitos Estritos:**
*   **Sistema Operativo**: Windows, macOS, ou Linux.
*   **Interpretador Python**: Versão `3.9` ou superior (recomendado `3.10`+).
*   **Conectividade**: Acesso à Internet necessário para a recolha automatizada da base de dados do Infarmed.
*   **Dependências Principais (incluídas no `requirements.txt`)**:
    *   `streamlit` (Para a Interface de Utilizador)
    *   `pandas` (Motor central de agregação e matrizes)
    *   `openpyxl` (Para Leitura e Escrita nativa em formato Excel)
    *   `requests` e `beautifulsoup4` (Para o *Scraping* do site do Infarmed)

## 3. Instalação e Setup (Passo-a-Passo)

Este guia destina-se a garantir que consegue colocar a aplicação a funcionar em poucos minutos.

### 3.1. Clonar ou Transferir o Projeto
Coloque a pasta do projeto num diretório da sua preferência no seu computador. Abra um Terminal (Linux/macOS) ou a Linha de Comandos/PowerShell (Windows) e navegue até à raiz do projeto.
```bash
cd caminho/para/o/projeto/streamlit_manual-main
```

### 3.2. Criar um Ambiente Virtual (VENV)
É estritamente recomendado o uso de um ambiente virtual para que as dependências não colidam com outras bibliotecas Python no seu sistema.
```bash
# Criar o ambiente virtual (na pasta 'venv')
python -m venv venv

# Ativar o ambiente virtual (Windows)
venv\Scripts\activate

# Ativar o ambiente virtual (macOS/Linux)
source venv/bin/activate
```

### 3.3. Instalar as Dependências
Com o ambiente virtual ativado, instale as bibliotecas requeridas pelo projeto executando:
```bash
pip install -r requirements.txt
```

## 4. Como Arrancar e Executar o Projeto

Garantindo que o seu ambiente virtual se encontra ativo e que se encontra na **raiz** do projeto (a pasta que contém os ficheiros `TASKS.md`, `.gitignore`, `requirements.txt`), execute o comando de arranque do Streamlit:

```bash
streamlit run ui/app.py
```

**Porquê usar este comando exato?**
O sistema necessita de identificar a pasta principal do projeto como o ponto zero para conseguir carregar as bibliotecas modulares internas da pasta `/core`. O ficheiro `/ui/app.py` tem agora uma proteção injetada para evitar o erro de *Module Not Found*, mas executar o comando pela raiz é sempre a prática correta.

Assim que o comando for introduzido, o seu *browser* principal abrirá automaticamente num endereço local (ex: `http://localhost:8501`) contendo a interface gráfica do motor PharmLogix.

---
Para entender como utilizar o motor, avance para o manual [USAGE.md](USAGE.md). Para explorar a mecânica de código e lógicas de processamento do projeto, consulte a página [ARCHITECTURE.md](ARCHITECTURE.md).
