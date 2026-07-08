"""
gemini_client.py — Wrapper Gemini API: rotasi key + error handling
====================================================================
Menggunakan SDK resmi `google-genai` (bukan google-generativeai yang deprecated).
Import: from google import genai

Strategi rotasi: round-robin per eksekusi, dengan retry ke key lain jika gagal.
Index rotasi disimpan di st.session_state["key_index"].
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

# ── System instructions ────────────────────────────────────────────────────
# Digunakan saat grounding aktif (dataset tersedia)
SYSTEM_INSTRUCTION = """
Kamu adalah ThunderChat, asisten analitik untuk dashboard Gebang Thunder.
Tugasmu HANYA menjawab pertanyaan yang berkaitan dengan data yang disediakan dalam konteks ini.
Jawab dalam Bahasa Indonesia dengan narasi yang jelas dan ringkas.
Jangan membuat grafik, tabel, atau visualisasi — hanya teks naratif.
Jika pertanyaan di luar cakupan data yang tersedia, tolak dengan sopan dan arahkan user untuk bertanya seputar data tersebut.
Jangan mengarang angka atau fakta yang tidak ada dalam data.
""".strip()

# Digunakan saat grounding DINONAKTIFKAN (mode testing — tanpa dataset)
SYSTEM_INSTRUCTION_TESTING = """
Kamu adalah ThunderChat, asisten AI dari tim Gebang Thunder.
Kamu sedang berjalan dalam mode testing (dataset belum tersedia).
Jawab pertanyaan pengguna secara umum dan membantu, dalam Bahasa Indonesia.
""".strip()


def ask_gemini(question: str, grounding_context: str, config: dict) -> str:
    """
    Kirim pertanyaan ke Gemini API dengan grounding context.
    Jika satu key gagal, otomatis retry ke key berikutnya (round-robin).

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
        Jawaban naratif dari model, atau fallback message jika semua key gagal.
    """
    api_keys: list[str] = config.get("api_keys", [])
    model_name: str = config.get("model_name", "gemini-3.5-flash")

    if not api_keys:
        msg = (
            "❌ **Konfigurasi Error**: Tidak ada Gemini API key yang terdeteksi. "
            "Pastikan Streamlit Secrets sudah dikonfigurasi dengan benar "
            "dalam format `[gemini] key_1 = \"...\"` dst."
        )
        logger.error("Tidak ada API key tersedia.")
        st.error(msg)
        return FALLBACK_API_ERROR

    # ── Pilih system instruction berdasarkan ada/tidaknya grounding context ─────
    if grounding_context.strip():
        active_instruction = SYSTEM_INSTRUCTION
        full_prompt = f"{grounding_context}\n\n---\n\nPertanyaan: {question}"
        logger.info("Mode: grounding aktif.")
    else:
        active_instruction = SYSTEM_INSTRUCTION_TESTING
        full_prompt = question
        logger.info("Mode: testing (tanpa grounding context).")

    # ── Round-robin start index ───────────────────────────────────────────────
    start_index: int = st.session_state.get("key_index", 0)
    num_keys = len(api_keys)

    last_error: Exception | None = None

    # ── Retry loop: coba semua key, mulai dari start_index ───────────────────
    for attempt in range(num_keys):
        key_index = (start_index + attempt) % num_keys
        current_key = api_keys[key_index]

        logger.info(f"Trying API key index {key_index} (attempt {attempt + 1}/{num_keys}) | model={model_name}")

        try:
            client = genai.Client(api_key=current_key)

            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=active_instruction,
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )

            answer = response.text
            logger.info(f"Gemini response received successfully via key_index={key_index}.")

            # Advance index untuk request berikutnya (setelah key yang berhasil)
            st.session_state["key_index"] = (key_index + 1) % num_keys
            return answer

        except Exception as e:
            last_error = e
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(
                f"Gemini API error on key_index={key_index} "
                f"(attempt {attempt + 1}/{num_keys}): {error_type}: {error_msg}"
            )

            # Tampilkan detail error di UI untuk membantu debugging
            # (dapat dinonaktifkan setelah API berfungsi normal)
            st.warning(
                f"⚠️ **[DEBUG] Key #{key_index + 1} gagal** — "
                f"`{error_type}`: {error_msg}"
            )

            # Lanjut ke key berikutnya
            continue

    # ── Semua key gagal ───────────────────────────────────────────────────────
    logger.error(f"Semua {num_keys} API key gagal. Last error: {last_error}")
    st.error(
        f"❌ **Semua {num_keys} API key gagal digunakan.** "
        f"Periksa log di atas untuk detail error masing-masing key."
    )
    return FALLBACK_API_ERROR
