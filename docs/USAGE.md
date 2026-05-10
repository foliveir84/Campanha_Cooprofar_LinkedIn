# Guia de Utilização - PharmLogix

Este manual guia o utilizador final através das funcionalidades do sistema, explicando como preparar os dados e interpretar os resultados de rentabilidade.

## 1. O Início: Base de Dados Infarmed

Ao abrir a aplicação, o sistema tentará automaticamente descarregar a lista atualizada de preços do Infarmed. 

*   **Luz Verde**: Se vir uma mensagem de sucesso, o motor está pronto.
*   **Aviso de Falha**: Se a extranet do Infarmed estiver em manutenção, o sistema pedirá um **Upload Manual**. Nesse caso, deve descarregar o ficheiro Excel do portal Infarmed (Pesquisa Avançada) e submetê-lo no campo indicado.

## 2. Configuração de Condições Comerciais (Sidebar)

Antes de carregar as campanhas, verifique a barra lateral esquerda:
1.  **Descontos Cooprofar**: Estão pré-carregados os descontos por escalão. Pode alterá-los manualmente se tiver acordos específicos. Estes valores definem o seu "Preço de Compra Regular".
2.  **Fee Empifarma**: Define a taxa (ex: 1.0%) que será somada ao PVA do template para calcular o preço final de campanha desse fornecedor.

## 3. Analisar Campanha Cooprofar

1.  Selecione o separador **"Campanha Cooprofar"**.
2.  Prepare o seu Excel. O sistema espera encontrar:
    *   **Código Nacional**: O CNP de 7 dígitos.
    *   **PVF**: O preço de venda à farmácia base.
    *   **PVFCampanha**: O preço especial da proposta.
    *   **Designação**: O nome do produto (opcional, mas recomendado).
3.  Faça o upload. O sistema cruzará os dados e mostrará apenas os produtos onde o `PVFCampanha` é inferior ao `PVF com Desconto`.

## 4. Analisar Campanha Empifarma

1.  Selecione o separador **"Campanha Empifarma"**.
2.  O template da Empifarma é dinâmico. O sistema procura automaticamente a linha onde começa a tabela através da palavra **"artigo"**.
3.  Certifique-se de que o ficheiro contém as colunas: **Artigo** (CNP), **PVA**, **Descrição** e **Classificação**.
4.  **Lógica Especial NETT**: Produtos com classificação "NETT" no Excel são aprovados automaticamente, pois representam preços líquidos promocionais.

## 5. Exportação de Resultados

Em ambos os separadores, após o processamento, surgirá um botão **"Exportar para Excel"**. 
*   O ficheiro gerado conterá a **Diferença Absoluta** (quanto poupa por unidade) e a **Diferença Percentual**.
*   A coluna "Designacao" no ficheiro exportado virá diretamente do seu template original para facilitar a conferência.

## 6. Resolução de Problemas (FAQ)

### "Erro ao processar Empifarma: Não foi possível encontrar a linha de cabeçalho"
**Causa**: O sistema não encontrou a palavra "artigo" em nenhuma célula do ficheiro.
**Solução**: Verifique se o nome da coluna do código nacional é "Artigo" ou se o ficheiro está vazio/protegido.

### "Erro: Faltam colunas essenciais"
**Causa**: O ficheiro carregado não tem as colunas de preço (PVF ou PVA).
**Solução**: Garanta que os nomes das colunas no Excel coincidem minimamente com o esperado (ex: "PVF", "PVA").

### "Os resultados aparecem vazios"
**Causa**: Nenhum produto da campanha é mais barato do que o seu preço de compra regular com desconto.
**Solução**: Verifique se as taxas de desconto na sidebar não estão demasiado elevadas.

### "Erro de Módulo (No module named core)"
**Causa**: Tentativa de executar o programa a partir da pasta errada.
**Solução**: Feche o terminal e execute `streamlit run ui/app.py` a partir da pasta raiz do projeto.
