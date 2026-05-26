import pandas as pd
import pytest

from core.engine.calculator import evaluate_cooprofar


@pytest.fixture
def sample_data():
    df_template_base = pd.DataFrame({
        'CNP': [1234567],
        'Designacao_template': ['Paracetamol'],
        'PVF': [10.00],
    })
    df_infarmed = pd.DataFrame({
        'Nº registo': [1234567],
        'Preço (PVP)': [6.68],
        'Escalao': [1]
    })
    discounts = {1: 8.3}
    return df_template_base, df_infarmed, discounts


def test_evaluate_with_zero_rappel_matches_original_logic(sample_data):
    """Com rappel=0, o resultado deve ser o mesmo logicamente,
    mas com colunas adicionais presentes (Preco_Final_Rappel = Preco_Compra_Regular)."""
    df_template_base, df_infarmed, discounts = sample_data
    df_template = df_template_base.copy()
    df_template['PVFCampanha'] = [9.00]

    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=0.0)

    expected_regular = round(10.00 * (1 - 0.083), 2)  # 9.17
    expected_desconto_rappel = round(0.0, 2)            # 0.00
    expected_diferenca = round(expected_regular - 9.00, 2)  # 0.17

    assert len(result) == 1
    assert 'Preco_Final_Rappel' in result.columns
    assert 'Desconto_Rappel_EUR' in result.columns
    assert result['Preco_Compra_Regular'].iloc[0] == expected_regular
    assert result['Preco_Final_Rappel'].iloc[0] == expected_regular
    assert result['Desconto_Rappel_EUR'].iloc[0] == expected_desconto_rappel
    assert result['Diferenca_Absoluta'].iloc[0] == expected_diferenca


def test_evaluate_with_1_percent_rappel_changes_baseline(sample_data):
    """Rappel de 1% deve incidir sobre o Preco_Compra_Regular."""
    df_template_base, df_infarmed, discounts = sample_data
    df_template = df_template_base.copy()
    df_template['PVFCampanha'] = [9.10]

    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=1.0)

    expected_regular = round(10.00 * (1 - 0.083), 2)  # 9.17
    expected_rappel = round(expected_regular * 0.01, 2)   # 0.09
    expected_final = round(expected_regular - expected_rappel, 2)  # 9.08

    # PVFCampanha = 9.10 > 9.08, logo NAO e vantajoso. Lista deve estar vazia.
    assert len(result) == 0


def test_evaluate_with_rappel_approved_if_campaign_price_below_final(sample_data):
    """Se PVFCampanha < Preco_Final_Rappel, deve aparecer."""
    df_template_base, df_infarmed, discounts = sample_data
    df_template = df_template_base.copy()
    df_template['PVFCampanha'] = [9.05]

    result = evaluate_cooprofar(df_template, df_infarmed, discounts, rappel_percent=1.0)

    expected_regular = round(10.00 * (1 - 0.083), 2)  # 9.17
    expected_rappel = round(expected_regular * 0.01, 2)   # 0.09
    expected_final = round(expected_regular - expected_rappel, 2)  # 9.08

    assert len(result) == 1
    assert result['Preco_Final_Rappel'].iloc[0] == expected_final
    assert result['Desconto_Rappel_EUR'].iloc[0] == expected_rappel

    expected_diferenca = round(expected_final - 9.05, 2)  # 0.03
    assert result['Diferenca_Absoluta'].iloc[0] == expected_diferenca
    assert result['Diferenca_Percentual'].iloc[0] == round((expected_diferenca / expected_final) * 100, 2)
