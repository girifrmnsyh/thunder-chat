"""
config.py — Load secrets & daftar API key
==========================================
Membaca API key dari Streamlit Secrets (production) atau
python-dotenv .env (development lokal).
API key TIDAK PERNAH di-hardcode di source code.
"""

import streamlit as st
from dotenv import load_dotenv
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Coba load .env untuk development lokal (diabaikan kalau tidak ada)
load_dotenv()


@st.cache_resource
def load_config() -> dict:
    """
    Memuat konfigurasi aplikasi: daftar API key Gemini dan parameter lain.

    Returns
    -------
    dict
        {
            "api_keys": list[str],   # minimal 1 key
            "model_name": str,
        }
    """
    api_keys: list[str] = []

    # ── Coba baca dari Streamlit Secrets (production & Streamlit Cloud) ──────
    try:
        # Format di secrets.toml:
        #   [gemini]
        #   key_1 = "AIza..."
        #   key_2 = "AIza..."
        #   key_3 = "AIza..."
        secrets_section = st.secrets.get("gemini", {})
        api_keys = [v for k, v in secrets_section.items() if k.startswith("key_")]
        if api_keys:
            logger.info(f"Loaded {len(api_keys)} API key(s) from Streamlit Secrets.")
    except Exception:
        pass  # Streamlit Secrets tidak tersedia (misal: dev lokal tanpa secrets.toml)

    # ── Fallback ke environment variables / .env (development lokal) ─────────
    if not api_keys:
        i = 1
        while True:
            key = os.getenv(f"GEMINI_KEY_{i}")
            if not key:
                break
            api_keys.append(key)
            i += 1
        if api_keys:
            logger.info(f"Loaded {len(api_keys)} API key(s) from environment variables.")

    if not api_keys:
        logger.warning(
            "Tidak ada API key ditemukan. Pastikan secrets.toml atau .env sudah dikonfigurasi."
        )

    return {
        "api_keys": api_keys,
        "model_name": "gemini-3.5-flash",
    }
