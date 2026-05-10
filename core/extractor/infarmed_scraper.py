import requests
import re
import os

def download_infarmed_dataset() -> str:
    """
    Descarrega o dataset do Infarmed realizando um POST request
    utilizando a lógica do PrimeFaces ViewState.
    Retorna o caminho do ficheiro descarregado ou levanta uma excepção.
    """
    url = "https://extranet.infarmed.pt/CITS-pesquisamedicamento-fo/pesquisaMedicamento.jsf"
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    response = session.get(url, headers=headers)
    response.raise_for_status()
    
    viewstate_match = re.search(r'name="javax\.faces\.ViewState".*?value="([^"]+)"', response.text)
    
    if not viewstate_match:
        viewstate_match = re.search(r'id="javax\.faces\.ViewState".*?value="([^"]+)"', response.text)
        
    if not viewstate_match:
        raise Exception("Erro: Não foi possível extrair o javax.faces.ViewState da página do Infarmed.")
        
    view_state = viewstate_match.group(1)
    
    payload = {
        "form": "form",
        "form:export-all-button": "",
        "javax.faces.ViewState": view_state
    }
    
    post_response = session.post(url, data=payload, headers=headers, stream=True)
    post_response.raise_for_status()
    
    content_type = post_response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        raise Exception("Erro: Resposta devolveu HTML em vez do ficheiro (mismatch de parâmetros do PrimeFaces).")
        
    filename = "infarmed_dataset.xls"
    filepath = os.path.abspath(filename)
    
    with open(filepath, 'wb') as f:
        for chunk in post_response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return filepath
