"""
components.py — Komponen UI ThunderChat
=========================================
Semua fungsi render UI: hero, suggested prompts, chat bubble, bot answer, input bar.
Menggunakan HTML custom via st.markdown + custom CSS dari styles.py.
"""

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


def render_landing_hero() -> None:
    """Render hero section untuk landing/empty state."""
    st.markdown(
        """
        <div class="tc-hero">
            <div class="tc-hero-logo">⚡ ThunderChat</div>
            <div class="tc-hero-tagline">
                Tanyakan apa saja tentang data Gebang Thunder
            </div>
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
    Render sticky input bar di bagian bawah.
    Submit bisa lewat tombol Enter (on_change) atau klik ikon send.

    Returns
    -------
    str | None
        Teks yang disubmit, atau None jika kosong.
    """
    with st.container():
        st.markdown('<div class="tc-input-wrapper">', unsafe_allow_html=True)
        col_input, col_btn = st.columns([10, 1])

        with col_input:
            user_text = st.text_input(
                label="input",
                placeholder="Apa yang ingin kamu tahu?",
                label_visibility="collapsed",
                key="user_input_field",
            )

        with col_btn:
            submit_clicked = st.button("→", key="submit_btn", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Clear input setelah submit
    if (submit_clicked or _enter_pressed()) and user_text and user_text.strip():
        result = user_text.strip()
        # Reset input field
        st.session_state["user_input_field"] = ""
        return result

    return None


def _enter_pressed() -> bool:
    """
    Deteksi apakah user menekan Enter pada input field.
    Streamlit mengeksekusi ulang script saat input berubah —
    kita gunakan session state untuk membedakan submit vs. mengetik biasa.
    """
    # Streamlit re-runs on every input change; Enter submit tidak bisa dibedakan
    # secara native — tombol submit (→) adalah mekanisme utama selain on_submit form.
    # Untuk UX Enter, gunakan st.form sebagai alternatif (dapat direfactor nanti).
    return False  # Placeholder — lihat TODO di bawah


# TODO: Refactor render_input_bar menggunakan st.form agar Enter natively bekerja:
# with st.form("chat_form", clear_on_submit=True):
#     user_text = st.text_input(...)
#     submitted = st.form_submit_button("Kirim")


def _escape_html(text: str) -> str:
    """Escape karakter HTML dalam teks user untuk mencegah XSS."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )
