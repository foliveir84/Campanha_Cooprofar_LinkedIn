from ui.theme import get_pharmacoach_css, get_logo_base64, render_header, render_linkedin_sidebar
from core.extractor.infarmed_scraper import download_infarmed_dataset
from core.parser.data_parser import clean_infarmed_dataset, parse_cooprofar_template
from core.engine.calculator import evaluate_cooprofar
import json
import streamlit as st
import io
import pandas as pd
import os
import sys
from pathlib import Path

# Garante que a raiz do projeto está no PYTHONPATH para que importe 'core' com sucesso
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Rentabilidade')
    return output.getvalue()


def load_cooprofar_conditions():
    try:
        with open('condicoes_cooprofar.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("Condicoes", {})
    except Exception:
        # Fallback de segurança se o ficheiro estiver corrompido
        return {"1": 8.3, "2": 8.0, "3": 7.7, "4": 7.4, "5": 6.5, "6": 1.0}


def get_pharmacoach_logo_base64() -> str:
    """Load and encode Pharmacoach logo."""
    logo_path = Path(__file__).parent.parent / "Logo_Pharmacoach.jpg"
    return get_logo_base64(str(logo_path))


def main():
    st.set_page_config(page_title="Campanha Cooprofar Analyser",
                       layout="wide", page_icon="💊")

    # Inject Pharmacoach theme CSS
    st.markdown(get_pharmacoach_css(), unsafe_allow_html=True)

    # Render branded header
    logo_base64 = get_pharmacoach_logo_base64()
    st.markdown(render_header(logo_base64), unsafe_allow_html=True)

    # Boot - Inicialização do Cache Infarmed
    if 'df_infarmed' not in st.session_state:
        try:
            with st.spinner("A descarregar dados atualizados do Infarmed (extranet)..."):
                filepath = download_infarmed_dataset()
                st.session_state['df_infarmed'] = clean_infarmed_dataset(
                    filepath)
                st.success(
                    "Base de dados Infarmed carregada em cache com sucesso!")
        except Exception as e:
            st.warning(
                f"Não foi possível descarregar os dados automaticamente: {str(e)}")
            st.info("Por favor, faça o upload manual do ficheiro Infarmed.")

            uploaded_infarmed = st.file_uploader(
                "Ficheiro do Infarmed (.xls)", type=['xls', 'xlsx'])
            if uploaded_infarmed:
                with st.spinner("A processar ficheiro manual..."):
                    st.session_state['df_infarmed'] = clean_infarmed_dataset(
                        uploaded_infarmed)
                    st.success(
                        "Base de dados Infarmed processada e carregada em cache!")
    else:
        st.success("Base de dados Infarmed carregada da sessão.")

    # Sidebar - Configurações
    st.sidebar.header("Configure Abaixo as Suas Condições comerciais")

    # Cooprofar
    st.sidebar.subheader("Descontos Cooprofar (%)")
    if 'discounts' not in st.session_state:
        st.session_state['discounts'] = load_cooprofar_conditions()

    for escalao in range(1, 7):
        key = str(escalao)
        current_val = float(st.session_state['discounts'].get(key, 0.0))
        new_val = st.sidebar.number_input(
            f"Escalão {escalao}",
            value=current_val,
            step=0.1,
            format="%.2f"
        )
        st.session_state['discounts'][key] = new_val

    # LinkedIn Section
    st.sidebar.markdown(render_linkedin_sidebar(), unsafe_allow_html=True)

    # Renderização de Resultados
    if 'df_infarmed' in st.session_state:
        st.header("Comparação de Rentabilidade - Cooprofar")
        upload_coop = st.file_uploader("Template Cooprofar (.xlsx)", type=[
                                       'xls', 'xlsx'], key="coop_upload")
        if upload_coop:
            try:
                df_template_coop = parse_cooprofar_template(upload_coop)
                df_result_coop = evaluate_cooprofar(
                    df_template_coop,
                    st.session_state['df_infarmed'],
                    st.session_state['discounts']
                )
                st.dataframe(df_result_coop, width='stretch', hide_index=True)

                excel_data = to_excel_bytes(df_result_coop)
                st.download_button(
                    label="Exportar para Excel",
                    data=excel_data,
                    file_name="rentabilidade_cooprofar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_coop"
                )
            except Exception as e:
                st.error(
                    f"Erro ao processar Cooprofar:\n Usou o template da Cooprofar no formato XLSX: Correcto? \n {str(e)}")


if __name__ == "__main__":
    main()
