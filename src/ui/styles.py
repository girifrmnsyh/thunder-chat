"""
styles.py — Custom CSS ThunderChat
====================================
Mengimplementasikan style guide dari PRD Section 10:
  - Font: Inter (Google Fonts / Local)
  - Background: #0D1117
  - Input Prompt: #545454 (gradasi tipis)
  - Primary Text: #f6f8fa
  - Secondary Text & Placeholder: #b4b4b4
  - Primary Accent: #2563EB
"""

import base64
from pathlib import Path
import streamlit as st


def inject_custom_css() -> None:
    """Inject seluruh custom CSS ke dalam halaman Streamlit."""
    font_face = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');"
    
    # Resolving absolute path to assets directory
    base_dir = Path(__file__).parent.parent.parent
    font_path = base_dir / "assets" / "fonts" / "InterVariable.woff2"
    
    if font_path.exists():
        with open(font_path, "rb") as f:
            font_data = base64.b64encode(f.read()).decode("utf-8")
        font_face = f'''
@font-face {{
    font-family: 'Inter';
    src: url(data:font/woff2;charset=utf-8;base64,{font_data}) format('woff2');
    font-weight: 100 900;
    font-style: normal;
}}
'''

    css = f"""
<style>
{font_face}

/* ── Reset & Global ────────────────────────────────────────────────────────── */
* {{
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background-color: #0D1117 !important;
    color: #f6f8fa !important;
}}

[data-testid="stMain"] {{
    background-color: #0D1117 !important;
}}

/* Sembunyikan elemen bawaan Streamlit yang tidak diperlukan */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Top Bar / Header ──────────────────────────────────────────────────────── */
.tc-top-bar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    display: flex;
    align-items: center;
    padding: 1.2rem 2rem;
    background-color: rgba(13, 17, 23, 0.95);
    z-index: 999;
    border-bottom: 1px solid #1f2937;
}}
.tc-top-bar-logo {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.tc-team-name {{
    color: #f6f8fa;
    font-weight: 600;
    font-size: 1.15rem;
}}
.tc-team-number {{
    color: #b4b4b4;
    font-size: 0.95rem;
    font-weight: 400;
}}

/* ── Container utama ───────────────────────────────────────────────────────── */
.block-container {{
    max-width: 720px !important;
    padding-top: 5rem !important;
    padding-bottom: 7rem !important;  /* ruang untuk input bar */
}}

/* ── Hero / Landing Highlight ──────────────────────────────────────────────── */
.tc-hero-highlight {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 4rem;
    padding-bottom: 3rem;
}}
.tc-hero-highlight img {{
    max-width: 90%;
    height: auto;
}}

/* ── Chat bubble (user) ────────────────────────────────────────────────────── */
.tc-chat-user {{
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}}

.tc-chat-user-bubble {{
    background: #2563EB;
    border: none;
    border-radius: 18px 18px 4px 18px;
    padding: 0.65rem 1rem;
    max-width: 85%;
    font-size: 0.95rem;
    color: #f6f8fa;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}}

/* ── Bot answer (tanpa bubble) ─────────────────────────────────────────────── */
.tc-chat-bot {{
    margin-bottom: 1.5rem;
    padding-left: 0.25rem;
}}

.tc-chat-bot-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: #2563EB;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.4rem;
}}

.tc-chat-bot-text {{
    font-size: 0.95rem;
    color: #f6f8fa;
    line-height: 1.7;
}}

/* ── Input bar (st.chat_input override) ────────────────────────────────────── */
[data-testid="stChatInput"] {{
    background-color: #0D1117 !important;
    padding-bottom: 1.5rem !important;
}}
[data-testid="stChatInput"] > div {{
    background: linear-gradient(180deg, #545454 0%, #3e3e3e 100%) !important;
    border: 1px solid #737373 !important;
    border-radius: 24px !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: #f6f8fa !important;
    font-size: 1rem !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: #b4b4b4 !important;
}}
/* Hapus tombol enter */
[data-testid="stChatInputSubmitButton"] {{
    display: none !important;
}}

/* ── Spinner override ──────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {{
    color: #2563EB !important;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)
