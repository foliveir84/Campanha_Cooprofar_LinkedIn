import pandas as pd

def calcular_escalao(pvp: float) -> int:
    """Retorna o escalão (1 a 6) com base no PVP."""
    if pvp <= 6.68:
        return 1
    elif pvp <= 9.97:
        return 2
    elif pvp <= 14.10:
        return 3
    elif pvp <= 26.96:
        return 4
    elif pvp <= 64.68:
        return 5
    else:
        return 6

def calcular_pva(pvp: float) -> float:
    """
    Calcula o PVA com base no PVP.
    Retorna o valor truncado a 2 casas decimais.
    """
    if pvp <= 6.68:
        pva = ((pvp - 0.94) / 1.1475) + (0.004 * (pvp / 1.06))
    elif pvp <= 9.97:
        pva = ((pvp - 1.95) / 1.1460) + (0.004 * (pvp / 1.06))
    elif pvp <= 14.10:
        pva = ((pvp - 2.66) / 1.1436) + (0.004 * (pvp / 1.06))
    elif pvp <= 26.96:
        pva = ((pvp - 4.17) / 1.1393) + (0.004 * (pvp / 1.06))
    elif pvp <= 64.68:
        pva = ((pvp - 8.00) / 1.1316) + (0.004 * (pvp / 1.06))
    else:
        pva = ((pvp - 12.73) / 1.1051) + (0.004 * (pvp / 1.06))
        
    return int(pva * 100) / 100

def calcular_pvf(pvp: float) -> float:
    """
    Calcula o PVF com base no PVP (calculando o PVA intermédio).
    Retorna o valor truncado a 2 casas decimais.
    """
    if pvp <= 6.68:
        pva = ((pvp - 0.94) / 1.1475) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 0.25 + (pva * 0.0224)
    elif pvp <= 9.97:
        pva = ((pvp - 1.95) / 1.1460) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 0.52 + (pva * 0.0217)
    elif pvp <= 14.10:
        pva = ((pvp - 2.66) / 1.1436) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 0.71 + (pva * 0.0212)
    elif pvp <= 26.96:
        pva = ((pvp - 4.17) / 1.1393) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 1.12 + (pva * 0.02)
    elif pvp <= 64.68:
        pva = ((pvp - 8.00) / 1.1316) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 2.2 + (pva * 0.0184)
    else:
        pva = ((pvp - 12.73) / 1.1051) + (0.004 * (pvp / 1.06)) 
        pvf = pva + 3.68 + (pva * 0.0118)
        
    return int(pvf * 100) / 100

def evaluate_cooprofar(df_template: pd.DataFrame, df_infarmed: pd.DataFrame, discounts: dict) -> pd.DataFrame:
    """
    Cruza o template da Cooprofar com o Infarmed, aplica os descontos por escalão,
    e retorna apenas os produtos onde a campanha é matematicamente vantajosa.
    """
    df_merged = df_infarmed.merge(df_template, left_on='Nº registo', right_on='CNP', suffixes=('_infarmed', '_template'))
    
    discounts_clean = {int(k): float(v) for k, v in discounts.items()}
    df_merged['Desconto_Percentual'] = df_merged['Escalao'].map(discounts_clean).fillna(0.0)
    
    df_merged['Custo_Regular_Cooprofar'] = df_merged['PVF_template'] * (1 - (df_merged['Desconto_Percentual'] / 100))
    df_merged['Custo_Regular_Cooprofar'] = df_merged['Custo_Regular_Cooprofar'].round(2)
    
    df_vantajosos = df_merged[df_merged['PVFCampanha'] < df_merged['Custo_Regular_Cooprofar']].copy()
    
    df_vantajosos['Diferenca_Absoluta'] = (df_vantajosos['Custo_Regular_Cooprofar'] - df_vantajosos['PVFCampanha']).round(2)
    df_vantajosos['Diferenca_Percentual'] = ((df_vantajosos['Diferenca_Absoluta'] / df_vantajosos['Custo_Regular_Cooprofar']) * 100).round(2)
    
    # 7. Organizar e renomear colunas finais conforme PRD
    df_vantajosos['CNP'] = df_vantajosos['CNP'].astype(str)
    
    colunas_finais = {
        'CNP': 'CNP', 
        'Designacao_template': 'Designacao', 
        'Custo_Regular_Cooprofar': 'Preco_Compra_Regular', 
        'PVFCampanha': 'Preco_Campanha', 
        'Diferenca_Absoluta': 'Diferenca_Absoluta', 
        'Diferenca_Percentual': 'Diferenca_Percentual'
    }
    
    # Adiciono colunas extra uteis que já estavam, mas padronizadas
    df_finais = df_vantajosos.rename(columns=colunas_finais)
    col_ordem = ['CNP', 'Designacao', 'Preco_Compra_Regular', 'Preco_Campanha', 'Diferenca_Absoluta', 'Diferenca_Percentual', 'Preço (PVP)', 'Escalao', 'Desconto_Percentual', 'PVF_template']
    
    return df_finais[col_ordem].sort_values(by='Diferenca_Absoluta', ascending=False)


