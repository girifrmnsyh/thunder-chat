"""
styles.py — Custom CSS ThunderChat
====================================
Mengimplementasikan style guide dari PRD Section 10:
  - Font: Inter (Google Fonts)
  - Background: #F6F8FA
  - Input Prompt: #FFFFFF
  - Primary Text: #0D1117
  - Secondary Text & Border Input: #737373
  - Primary Accent: #2563EB
  - Shadow: tipis, minimalis
  - Referensi shadcn/ui via streamlit-shadcn-ui
"""

import streamlit as st


def inject_custom_css() -> None:
    """Inject seluruh custom CSS ke dalam halaman Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ── Google Fonts: Inter ───────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Global ────────────────────────────────────────────────────────── */
* {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F6F8FA !important;
    color: #0D1117 !important;
}

[data-testid="stMain"] {
    background-color: #F6F8FA !important;
}

/* Sembunyikan elemen bawaan Streamlit yang tidak diperlukan */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Container utama ───────────────────────────────────────────────────────── */
.block-container {
    max-width: 720px !important;
    padding-top: 2rem !important;
    padding-bottom: 6rem !important;  /* ruang untuk input bar */
}

/* ── Hero / Landing ────────────────────────────────────────────────────────── */
.tc-hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
}

.tc-hero-logo {
    font-size: 2rem;
    font-weight: 700;
    color: #2563EB;
    letter-spacing: -0.5px;
    margin-bottom: 0.25rem;
}

.tc-hero-tagline {
    font-size: 1.05rem;
    color: #737373;
    font-weight: 400;
}

/* ── Suggested prompts ─────────────────────────────────────────────────────── */
.tc-prompts {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.5rem;
}

.tc-prompt-chip {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-size: 0.82rem;
    color: #0D1117;
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.tc-prompt-chip:hover {
    border-color: #2563EB;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}

/* ── Chat bubble (user) ────────────────────────────────────────────────────── */
.tc-chat-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}

.tc-chat-user-bubble {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 18px 18px 4px 18px;
    padding: 0.65rem 1rem;
    max-width: 85%;
    font-size: 0.9rem;
    color: #0D1117;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ── Bot answer (tanpa bubble) ─────────────────────────────────────────────── */
.tc-chat-bot {
    margin-bottom: 1.5rem;
    padding-left: 0.25rem;
}

.tc-chat-bot-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #2563EB;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}

.tc-chat-bot-text {
    font-size: 0.92rem;
    color: #0D1117;
    line-height: 1.65;
}

/* ── Input bar (sticky bottom) ─────────────────────────────────────────────── */
.tc-input-wrapper {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 720px;
    background: #F6F8FA;
    padding: 1rem 1.5rem 1.25rem;
    border-top: 1px solid #E5E7EB;
    z-index: 100;
}

/* Override Streamlit text_input default style */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid #737373 !important;
    border-radius: 12px !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.9rem !important;
    color: #0D1117 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    outline: none !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #737373 !important;
}

/* ── Spinner override ──────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: #2563EB !important;
}
</style>
"""
