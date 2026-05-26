import pandas as pd
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine.calculator import evaluate_cooprofar

def test_evaluate_with_zero_rappel_matches_original_logic():
    """Com rappel=0, o resultado deve ser o mesmo logicamente,
    mas com colunas adicionais presentes (Preco_Final_Rappel = Preco_Compra_Regular)."""
    df_template = pd.DataFrame({
        'CNP': [1234567],
        'Designacao_template': ['Paracetamol'],
        'PVF': [10.00],
        'PVFCampanha': [9.00]  # mais barato que regular com desconto
    })
    df_infarmed = pd.DataFrame({
        'Nº registo': [1234567],
        'Preço (PVP)': [6.68],  # Escalão 1
        'Escalao': [1]
    })
    discounts = {1: 8.3}
    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=0.0)

    assert len(result) == 1
    assert 'Preco_Final_Rappel' in result.columns
    assert 'Desconto_Rappel_EUR' in result.columns
    # PVF=10, desconto 8.3%: 10 * (1-0.083) = 9.17
    assert result['Preco_Compra_Regular'].iloc[0] == 9.17
    # Rappel 0 => Final = Regular
    assert result['Preco_Final_Rappel'].iloc[0] == 9.17
    assert result['Desconto_Rappel_EUR'].iloc[0] == 0.00
    # Diferenca = 9.17 - 9.00 = 0.17
    assert result['Diferenca_Absoluta'].iloc[0] == 0.17

def test_evaluate_with_1_percent_rappel_changes_baseline():
    """Rappel de 1% deve incidir sobre o Preco_Compra_Regular."""
    df_template = pd.DataFrame({
        'CNP': [1234567],
        'Designacao_template': ['Paracetamol'],
        'PVF': [10.00],
        'PVFCampanha': [9.10]  # 9.10 < 9.08? Não. Logo NÃO deve aparecer.
    })
    df_infarmed = pd.DataFrame({
        'Nº registo': [1234567],
        'Preço (PVP)': [6.68],
        'Escalao': [1]
    })
    discounts = {1: 8.3}
    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=1.0)
    # Regular = 9.17
    # Rappel = round(9.17 * 0.01, 2) = 0.09
    # Final = 9.08
    # PVFCampanha = 9.10 > 9.08, logo NÃO é vantajoso. Lista deve estar vazia.
    assert len(result) == 0

def test_evaluate_with_rappel_approved_if_campaign_price_below_final():
    """Se PVFCampanha < Preco_Final_Rappel, deve aparecer."""
    df_template = pd.DataFrame({
        'CNP': [1234567],
        'Designacao_template': ['Paracetamol'],
        'PVF': [10.00],
        'PVFCampanha': [9.05]  # 9.05 < 9.08, logo deve aparecer
    })
    df_infarmed = pd.DataFrame({
        'Nº registo': [1234567],
        'Preço (PVP)': [6.68],
        'Escalao': [1]
    })
    discounts = {1: 8.3}
    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=1.0)
    assert len(result) == 1
    assert result['Preco_Final_Rappel'].iloc[0] == 9.08
    assert result['Desconto_Rappel_EUR'].iloc[0] == 0.09
    # Diferenca = 9.08 - 9.05 = 0.03
    assert result['Diferenca_Absoluta'].iloc[0] == 0.03
    assert result['Diferenca_Percentual'].iloc[0] == round((0.03 / 9.08) * 100, 2)
