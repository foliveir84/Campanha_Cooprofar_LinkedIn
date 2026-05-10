# Pharmacoach UI Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply Pharmacoach visual identity (dark glassmorphism, neon gradients) to Streamlit UI with logo in header and LinkedIn link in sidebar.

**Architecture:** CSS injection via `st.markdown(unsafe_allow_html=True)` for global theme, base64-encoded logos for reliability, modular theme function in `ui/theme.py`.

**Tech Stack:** Streamlit, Python, CSS, base64 encoding.

---

## File Structure

**Files to Create:**
- `ui/theme.py` - Theme CSS generator and logo encoding utilities
- `assets/` - Directory for logo files (optional, can use root paths)

**Files to Modify:**
- `ui/app.py` - Add header with logo, sidebar LinkedIn link, inject theme CSS

---

### Task 1: Create Theme Module (`ui/theme.py`)

**Files:**
- Create: `ui/theme.py`

- [ ] **Step 1: Create theme module with CSS and logo utilities**

```python
"""
Pharmacoach Visual Theme - CSS Injection for Streamlit
"""
import base64
from pathlib import Path


def get_logo_base64(logo_path: str) -> str:
    """Convert logo to base64 for inline embedding."""
    path = Path(logo_path)
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        logo_data = f.read()
    return base64.b64encode(logo_data).decode()


def get_pharmacoach_css() -> str:
    """Return complete CSS theme for Pharmacoach brand."""
    return """
    <style>
    /* Global Background */
    .stApp {
        background: linear-gradient(135deg, #120021 0%, #1a0036 50%, #220044 100%);
    }
    
    /* Header Container */
    .pharmacoach-header {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 20px 0;
        margin-bottom: 10px;
    }
    
    .pharmacoach-logo {
        width: 55px;
        height: 55px;
        object-fit: contain;
        filter: drop-shadow(0 0 8px rgba(141, 61, 255, 0.5));
    }
    
    .pharmacoach-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c431fb 0%, #4fa8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0036 0%, #120021 100%);
    }
    
    section[data-testid="stSidebar"] .stNumberInput label {
        color: #b38cff;
    }
    
    section[data-testid="stSidebar"] input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(141, 61, 255, 0.3);
        color: #e0e0e0;
    }
    
    /* LinkedIn Section in Sidebar */
    .linkedin-section {
        position: fixed;
        bottom: 20px;
        left: 20px;
        text-align: center;
        padding: 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        width: calc(300px - 40px);
    }
    
    .linkedin-logo {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .linkedin-logo:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(79, 168, 255, 0.4);
    }
    
    .linkedin-link {
        color: #4fa8ff;
        text-decoration: none;
        font-size: 0.75rem;
        display: block;
        margin-top: 8px;
    }
    
    .linkedin-link:hover {
        text-decoration: underline;
    }
    
    /* Main Content Cards */
    .stDataFrame, .stFileUploader {
        border-radius: 12px;
        border: 1px solid rgba(141, 61, 255, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #8d3dff 0%, #4fa8ff 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 600;
        transition: box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(141, 61, 255, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #c431fb;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """


def render_header(logo_base64: str) -> str:
    """Return HTML for branded header."""
    if not logo_base64:
        return '<div class="pharmacoach-header"><h1 class="pharmacoach-title">Pharmacoach Engine</h1></div>'
    
    return f"""
    <div class="pharmacoach-header">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Pharmacoach Logo" class="pharmacoach-logo">
        <h1 class="pharmacoach-title">Pharmacoach Engine</h1>
    </div>
    """


def render_linkedin_sidebar() -> str:
    """Return HTML for LinkedIn section in sidebar."""
    linkedin_logo_path = Path(__file__).parent.parent / "LogoLinkedIN.png"
    logo_base64 = get_logo_base64(str(linkedin_logo_path))
    
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="LinkedIn" class="linkedin-logo">'
    else:
        logo_html = '<div style="width:40px;height:40px;background:#0077b5;border-radius:8px;margin:0 auto;"></div>'
    
    return f"""
    <div class="linkedin-section">
        <a href="https://www.linkedin.com/in/foliveir/" target="_blank">
            {logo_html}
            <span class="linkedin-link">linkedin.com/in/foliveir/</span>
        </a>
    </div>
    """
```

- [ ] **Step 2: Commit**

```bash
git add ui/theme.py
git commit -m "feat: add Pharmacoach theme module with CSS and logo utilities"
```

---

### Task 2: Update `ui/app.py` with Theme Integration

**Files:**
- Modify: `ui/app.py:1-97`

- [ ] **Step 1: Add theme imports at top of file**

```python
import streamlit as st
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.extractor.infarmed_scraper import download_infarmed_dataset
from core.parser.data_parser import clean_infarmed_dataset, parse_cooprofar_template
from core.engine.calculator import evaluate_cooprofar
from ui.theme import get_pharmacoach_css, get_logo_base64, render_header, render_linkedin_sidebar
import io
import pandas as pd
from pathlib import Path
```

- [ ] **Step 2: Add helper function for logo encoding**

Add after `to_excel_bytes` function:

```python
def get_pharmacoach_logo_base64() -> str:
    """Load and encode Pharmacoach logo."""
    logo_path = Path(__file__).parent.parent / "Logo_Pharmacoach.jpg"
    return get_logo_base64(str(logo_path))
```

- [ ] **Step 3: Update `main()` function - inject CSS and render header**

Replace the beginning of `main()` (after `st.set_page_config`):

```python
def main():
    st.set_page_config(page_title="Pharmacoach Engine", layout="wide", page_icon="💊")
    
    # Inject Pharmacoach theme CSS
    st.markdown(get_pharmacoach_css(), unsafe_allow_html=True)
    
    # Render branded header
    logo_base64 = get_pharmacoach_logo_base64()
    st.markdown(render_header(logo_base64), unsafe_allow_html=True)
```

- [ ] **Step 4: Add LinkedIn to sidebar**

Add at the end of sidebar section (after the escalão inputs, before "Renderização de Resultados"):

```python
    # LinkedIn Section
    st.sidebar.markdown(render_linkedin_sidebar(), unsafe_allow_html=True)
```

- [ ] **Step 5: Update title from "PharmLogix" to "Pharmacoach"**

Change:
```python
st.title("Motor de Análise de Rentabilidade Farmacêutica")
```

To (this line will be replaced by header HTML, so remove it):
```python
# Title rendered via header HTML
```

- [ ] **Step 6: Commit**

```bash
git add ui/app.py
git commit -m "feat: integrate Pharmacoach theme into main app"
```

---

### Task 3: Test Visual Theme

**Files:**
- Test: Manual browser test

- [ ] **Step 1: Start Streamlit server**

```bash
streamlit run ui/app.py
```

Expected: Server starts on `http://localhost:8501`

- [ ] **Step 2: Verify visual elements in browser**

Checklist:
- [ ] Logo Pharmacoach visível no header (esquerda)
- [ ] Título "Pharmacoach Engine" com gradiente roxo-azul
- [ ] Background com gradiente escuro (roxo profundo)
- [ ] Sidebar com inputs estilizados
- [ ] LinkedIn logo e link no fundo da sidebar
- [ ] Botões com gradiente e hover glow
- [ ] Links LinkedIn clicável (abre em nova aba)

- [ ] **Step 3: Verify functional elements still work**

Checklist:
- [ ] Upload Infarmed dataset (auto ou manual)
- [ ] Upload template Cooprofar
- [ ] Tabela de resultados renderiza
- [ ] Exportação Excel funciona

- [ ] **Step 4: Document any CSS issues**

If any styling doesn't apply correctly, note:
- Which selectors need adjustment
- Streamlit version-specific limitations

---

### Task 4: Create Assets Directory (Optional Cleanup)

**Files:**
- Create: `assets/` directory
- Move: Logos for organization

- [ ] **Step 1: Create assets directory**

```bash
mkdir assets
```

- [ ] **Step 2: Move logos (optional, for organization)**

```bash
move Logo_Pharmacoach.jpg assets/
move LogoLinkedIN.png assets/
```

- [ ] **Step 3: Update theme.py paths if moved**

If logos moved to `assets/`:
```python
# In ui/theme.py
linkedin_logo_path = Path(__file__).parent.parent / "assets" / "LogoLinkedIN.png"
```

- [ ] **Step 4: Commit**

```bash
git add assets/
git commit -m "chore: organize logo assets in dedicated directory"
```

---

## Self-Review Checklist

**Spec Coverage:**
- [x] Logo Pharmacoach no Header → Task 2
- [x] LinkedIn na Sidebar → Task 2
- [x] Tema visual (paleta) → Task 1 (CSS)
- [x] CSS Glassmorphism → Task 1
- [x] Manter funcionalidade → Task 3 (tests)

**Placeholder Scan:**
- No TBD/TODO found
- All code steps include actual code
- All file paths are exact

**Type Consistency:**
- Function names consistent: `get_logo_base64`, `get_pharmacoach_css`, `render_header`, `render_linkedin_sidebar`
- Path handling via `pathlib.Path` throughout

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-10-pharmacoach-ui-theme.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
