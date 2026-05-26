# Guia de Utilização - PharmLogix

Este manual guia o utilizador final através das funcionalidades do sistema, explicando como preparar os dados e interpretar os resultados de rentabilidade.

## 1. O Início: Base de Dados Infarmed

Ao abrir a aplicação, o sistema tentará automaticamente descarregar a lista atualizada de preços do Infarmed. 

*   **Luz Verde**: Se vir uma mensagem de sucesso, o motor está pronto.
*   **Aviso de Falha**: Se a extranet do Infarmed estiver em manutenção, o sistema pedirá um **Upload Manual**. Nesse caso, deve descarregar o ficheiro Excel do portal Infarmed (Pesquisa Avançada) e submetê-lo no campo indicado.

## 2. Configuração de Condições Comerciais (Sidebar)

Antes de carregar as campanhas, verifique a barra lateral esquerda:
1.  **Descontos Cooprofar**: Estão pré-carregados os descontos por escalão. Pode alterá-los manualmente se tiver acordos específicos. Estes valores definem o seu "Preço de Compra Regular".
2.  **Rappel (%)**: Um campo adicional permite configurar um desconto de rappel (máx. **1%**). Este desconto incide sobre o "Preço Compra Regular" já com desconto do escalão, reduzindo ainda mais o valor final de comparação. Default é `0.0%`.

**Exemplo:**
Se o PVF for 10.00€ e o desconto do escalão for 8.3%, o Preço Compra Regular é 9.17€. Com um rappel de 1%, o Preço Final de Compra (baseline) será 9.08€.

## 3. Analisar Campanha Cooprofar

1.  Selecione o separador **"Campanha Cooprofar"**.
2.  Prepare o seu Excel. O sistema espera encontrar:
    *   **Código Nacional** (ou **CNP**): O CNP de 7 dígitos.
    *   **PVF**: O preço de venda à farmácia base.
    *   **PVFCampanha**: O preço especial da proposta.
    *   **Designação** (ou **nome**): O nome do produto (opcional, mas recomendado).
3.  Faça o upload. O sistema cruzará os dados e mostrará apenas os produtos onde o `PVFCampanha` é inferior ao **Preço Final de Compra** (PVF com desconto de escalão e, se aplicável, rappel).

## 4. Exportação de Resultados

Após o processamento, surgirá um botão **"Exportar para Excel"**.
*   O ficheiro gerado conterá as seguintes colunas (entre outras):
    *   `Preco_Compra_Regular`: Preço após desconto do escalão.
    *   `Desconto_Rappel_EUR`: Valor absoluto do rappel (se > 0).
    *   `Preco_Final_Rappel`: **Preço final de comparação** (baseline).
    *   `Preco_Campanha`: Preço da campanha.
    *   `Diferenca_Absoluta` e `Diferenca_Percentual`: Poupança face ao Preço Final.
*   A coluna "Designacao" no ficheiro exportado virá diretamente do seu template original para facilitar a conferência.

## 5. Resolução de Problemas (FAQ)

### "Erro: Faltam colunas essenciais"
**Causa**: O ficheiro carregado não tem as colunas de preço (PVF ou PVFCampanha).
**Solução**: Garanta que os nomes das colunas no Excel coincidem minimamente com o esperado (ex: "PVF", "PVFCampanha").

### "Os resultados aparecem vazios"
**Causa**: Nenhum produto da campanha é mais barato do que o seu preço de compra regular com desconto.
**Solução**: Verifique se as taxas de desconto na sidebar não estão demasiado elevadas. Se estiver a usar Rappel, confirme que o valor está correto.

### "Erro de Módulo (No module named core)"
**Causa**: Tentativa de executar o programa a partir da pasta errada.
**Solução**: Feche o terminal e execute `streamlit run ui/app.py` a partir da pasta raiz do projeto.
