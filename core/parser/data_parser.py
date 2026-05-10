import pandas as pd
from core.engine.calculator import calcular_pva, calcular_pvf, calcular_escalao

def clean_infarmed_dataset(file_path: str) -> pd.DataFrame:
    """
    Lê e higieniza o ficheiro do Infarmed, aplicando as exclusões necessárias,
    tipagem de colunas e injeção do PVA, PVF e Escalão pré-calculados.
    """
    df = pd.read_excel(file_path)
    
    # Exclusões
    df = df.loc[df['Comerc.'] != 'Não comercializado']
    df = df.loc[df['Preço (PVP)'] != 'preço livre']
    df = df.loc[df['Preço (PVP)'].notnull()]
    if 'Genérico' in df.columns:
        df = df.loc[df['Genérico'] == 'Não']
    
    # Tipagem e seleção
    df['Preço (PVP)'] = df['Preço (PVP)'].astype(float)
    df['Nº registo'] = df['Nº registo'].astype(int)
    
    colunas = ['Nº registo', 'Nome do medicamento', 'Preço (PVP)']
    df = df[colunas].copy()
    
    # Injeção de colunas calculadas (truncadas nas próprias funções base)
    df['PVA'] = df['Preço (PVP)'].apply(calcular_pva)
    df['PVF'] = df['Preço (PVP)'].apply(calcular_pvf)
    df['Escalao'] = df['Preço (PVP)'].apply(calcular_escalao)
    
    return df

def parse_cooprofar_template(file_stream) -> pd.DataFrame:
    """
    Faz o parse do template da Cooprofar e padroniza as colunas necessárias.
    """
    df = pd.read_excel(file_stream)
    
    if 'Codigo Nacional' in df.columns:
        df = df.rename(columns={'Codigo Nacional': 'CNP'})
    elif 'Código Nacional' in df.columns:
        df = df.rename(columns={'Código Nacional': 'CNP'})
        
    desig_col = None
    for c in df.columns:
        if str(c).lower().strip() in ['designação', 'designacao', 'nome']:
            desig_col = c
            break
            
    if desig_col:
        df = df.rename(columns={desig_col: 'Designacao_template'})
    else:
        # Fallback if the column is exactly the second column (Column B)
        df = df.rename(columns={df.columns[1]: 'Designacao_template'})
        
    df = df[['CNP', 'Designacao_template', 'PVF', 'PVFCampanha']].copy()
    
    # Garantir tipagem correta para o merge com 'Nº registo'
    df['CNP'] = df['CNP'].astype(int)
    df['PVF'] = df['PVF'].astype(float)
    df['PVFCampanha'] = df['PVFCampanha'].astype(float)
    df['Designacao_template'] = df['Designacao_template'].astype(str).str.title()
    
    return df


