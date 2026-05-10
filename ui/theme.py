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
        return '<div class="pharmacoach-header"><h1 class="pharmacoach-title">Campanha Cooprofar Analyser</h1></div>'

    return f"""
    <div class="pharmacoach-header">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Pharmacoach Logo" class="pharmacoach-logo">
        <h1 class="pharmacoach-title">Campanha Cooprofar Analyser</h1>
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
