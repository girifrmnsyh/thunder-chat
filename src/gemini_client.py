"""
gemini_client.py — Wrapper Gemini API: rotasi key + error handling
====================================================================
Menggunakan SDK resmi `google-genai` (bukan google-generativeai yang deprecated).
Import: from google import genai

Strategi rotasi: round-robin per eksekusi.
Index rotasi disimpan di st.session_state["key_index"].
Tidak ada retry otomatis ke key lain — langsung fallback saat error (FR6).
"""

import streamlit as st
from google import genai
from google.genai import types
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── Fallback messages ─────────────────────────────────────────────────────────
FALLBACK_API_ERROR = (
    "Maaf, sistem sedang sibuk atau mencapai batas penggunaan. "
    "Silakan coba lagi dalam beberapa saat."
)

SYSTEM_INSTRUCTION = """
Kamu adalah ThunderChat, asisten analitik untuk dashboard Gebang Thunder.
Tugasmu HANYA menjawab pertanyaan yang berkaitan dengan data yang disediakan dalam konteks ini.
Jawab dalam Bahasa Indonesia dengan narasi yang jelas dan ringkas.
Jangan membuat grafik, tabel, atau visualisasi — hanya teks naratif.
Jika pertanyaan di luar cakupan data yang tersedia, tolak dengan sopan dan arahkan user untuk bertanya seputar data tersebut.
Jangan mengarang angka atau fakta yang tidak ada dalam data.
""".strip()


def ask_gemini(question: str, grounding_context: str, config: dict) -> str:
    """
    Kirim pertanyaan ke Gemini API dengan grounding context.

    Parameters
    ----------
    question : str
        Pertanyaan natural language dari user.
    grounding_context : str
        Representasi data (dari grounding.py) sebagai context prompt.
    config : dict
        Konfigurasi dari load_config(), berisi api_keys dan model_name.

    Returns
    -------
    str
        Jawaban naratif dari model, atau fallback message jika error.
    """
    api_keys: list[str] = config.get("api_keys", [])
    model_name: str = config.get("model_name", "gemini-3.5-flash")

    if not api_keys:
        logger.error("Tidak ada API key tersedia.")
        return FALLBACK_API_ERROR

    # ── Round-robin: ambil key berdasarkan index sesi ─────────────────────────
    key_index: int = st.session_state.get("key_index", 0)
    current_key = api_keys[key_index % len(api_keys)]

    # Advance index untuk request berikutnya
    st.session_state["key_index"] = (key_index + 1) % len(api_keys)

    logger.info(f"Using API key index {key_index} | model={model_name}")

    # ── Susun full prompt ─────────────────────────────────────────────────────
    full_prompt = f"{grounding_context}\n\n---\n\nPertanyaan: {question}"

    # ── Panggil Gemini API ────────────────────────────────────────────────────
    try:
        client = genai.Client(api_key=current_key)

        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,        # rendah untuk jawaban faktual/deterministik
                max_output_tokens=1024,
            ),
        )

        answer = response.text
        logger.info("Gemini response received successfully.")
        return answer

    except Exception as e:
        logger.error(f"Gemini API error (key_index={key_index}): {type(e).__name__}: {e}")
        return FALLBACK_API_ERROR
