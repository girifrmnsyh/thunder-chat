"""
app.py — Entry point utama ThunderChat
=======================================
Streamlit app: landing page, input handling, dan orchestrasi
antara UI components, Gemini client, dan data loader.
"""

import streamlit as st

from src.config import load_config
from src.data_loader import load_dataset
from src.gemini_client import ask_gemini
from src.grounding import build_grounding_context
from src.ui.styles import inject_custom_css
from src.ui.components import (
    render_landing_hero,
    render_suggested_prompts,
    render_chat_bubble,
    render_bot_answer,
    render_input_bar,
    render_top_bar,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── Konfigurasi halaman ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="ThunderChat — Gebang Thunder",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Inject CSS kustom ─────────────────────────────────────────────────────────
inject_custom_css()

# ── Init session state ────────────────────────────────────────────────────────
if "key_index" not in st.session_state:
    st.session_state.key_index = 0          # round-robin pointer API key
if "messages" not in st.session_state:
    st.session_state.messages = []          # riwayat percakapan sesi ini
if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = False     # flag untuk animasi Lottie initial load

# ── Load config & dataset (cached) ───────────────────────────────────────────
config = load_config()
df, agg_context = load_dataset()           # load_dataset di-cache via @st.cache_data

# ── Lottie initial load animation ────────────────────────────────────────────
if not st.session_state.app_loaded:
    # TODO: render animasi Lottie di sini saat dataset sudah tersedia
    st.session_state.app_loaded = True

# ── Render UI ─────────────────────────────────────────────────────────────────
render_top_bar()

if not st.session_state.messages:
    # Landing / empty state
    render_landing_hero()
    # selected_prompt = render_suggested_prompts()
    # if selected_prompt:
    #     st.session_state.pending_prompt = selected_prompt
    selected_prompt = None
else:
    # Tampilkan riwayat percakapan sesi ini
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            render_chat_bubble(msg["content"])
        else:
            render_bot_answer(msg["content"])

# ── Input bar (selalu di bawah) ───────────────────────────────────────────────
user_input = render_input_bar()

# Tangani input dari suggested prompt atau dari text input
prompt = user_input or st.session_state.pop("pending_prompt", None)

if prompt:
    logger.info(f"User submitted question (len={len(prompt)})")

    # Simpan pertanyaan user ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("ThunderChat sedang memproses..."):
        grounding_ctx = build_grounding_context(df, agg_context)
        answer = ask_gemini(
            question=prompt,
            grounding_context=grounding_ctx,
            config=config,
        )

    logger.info("Answer received, rendering response.")
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
