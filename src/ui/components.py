"""
components.py — Komponen UI ThunderChat
=========================================
Semua fungsi render UI: hero, suggested prompts, chat bubble, bot answer, input bar.
Menggunakan HTML custom via st.markdown + custom CSS dari styles.py.
"""

import base64
from pathlib import Path
import streamlit as st
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── Suggested prompts default ─────────────────────────────────────────────────
# Akan diperbarui setelah skema dataset final tersedia.
# Saat ini berisi contoh generik yang relevan dengan konteks analitik bisnis.
DEFAULT_SUGGESTED_PROMPTS = [
    "Berapa total keseluruhan data yang tersedia?",
    "Apa tren utama yang terlihat dari data?",
    "Kategori mana yang memiliki nilai tertinggi?",
    "Tampilkan ringkasan statistik dari dataset",
    "Apa insight paling menarik dari data ini?",
]


def render_top_bar() -> None:
    """Render top bar (freeze) dengan logo dan nama tim."""
    logo_svg = ""
    base_dir = Path(__file__).parent.parent.parent
    logo_path = base_dir / "assets" / "icons" / "logo-gt.svg"
    if logo_path.exists():
        with open(logo_path, "r", encoding="utf-8") as f:
            logo_svg = f.read()
    
    st.markdown(
        f"""
        <div class="tc-top-bar">
            <div class="tc-top-bar-logo">
                {logo_svg}
                <div class="tc-team-text">
                    <span class="tc-team-name">Gebang Thunder</span>
                    <span class="tc-team-number">SSDC2026017</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_landing_hero() -> None:
    """Render hero section untuk landing/empty state."""
    base_dir = Path(__file__).parent.parent.parent
    highlight_path = base_dir / "assets" / "icons" / "highlight-teks.svg"
    img_b64 = ""
    if highlight_path.exists():
        with open(highlight_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

    st.markdown(
        f"""
        <div class="tc-hero-highlight">
            <img src="data:image/svg+xml;base64,{img_b64}" alt="Highlight Teks" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_suggested_prompts(
    prompts: list[str] | None = None,
) -> str | None:
    """
    Render suggested prompt chips dan kembalikan prompt yang dipilih user.

    Parameters
    ----------
    prompts : list[str] | None
        Daftar suggested prompt. Default ke DEFAULT_SUGGESTED_PROMPTS.

    Returns
    -------
    str | None
        Prompt yang diklik, atau None jika tidak ada yang diklik.
    """
    prompts = prompts or DEFAULT_SUGGESTED_PROMPTS
    selected: str | None = None

    st.markdown('<div class="tc-prompts">', unsafe_allow_html=True)
    cols = st.columns(len(prompts))
    for i, (col, prompt) in enumerate(zip(cols, prompts)):
        with col:
            if st.button(
                prompt,
                key=f"suggested_prompt_{i}",
                use_container_width=True,
            ):
                selected = prompt
                logger.info(f"Suggested prompt selected: index={i}")
    st.markdown("</div>", unsafe_allow_html=True)

    return selected


def render_chat_bubble(text: str) -> None:
    """Render chat bubble untuk pesan user (rata kanan, background putih)."""
    safe_text = _escape_html(text)
    st.markdown(
        f"""
        <div class="tc-chat-user">
            <div class="tc-chat-user-bubble">{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bot_answer(text: str) -> None:
    """Render jawaban bot sebagai teks naratif (tanpa bubble)."""
    safe_text = _escape_html(text)
    st.markdown(
        f"""
        <div class="tc-chat-bot">
            <div class="tc-chat-bot-label">⚡ ThunderChat</div>
            <div class="tc-chat-bot-text">{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_bar() -> str | None:
    """
    Render sticky input bar di bagian bawah menggunakan st.chat_input.
    """
    return st.chat_input("Apa yang ingin kamu tahu?")


def _escape_html(text: str) -> str:
    """Escape karakter HTML dalam teks user untuk mencegah XSS."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )
