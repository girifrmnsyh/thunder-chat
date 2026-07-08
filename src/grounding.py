"""
grounding.py — Bangun prompt/context grounding untuk Gemini
=============================================================
Menyusun string context yang dikirim ke model bersama pertanyaan user.
Context berisi representasi data (dari data_loader) ditambah instruksi domain.
"""

import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ── FLAG: Aktifkan/nonaktifkan grounding data ─────────────────────────────────
# Set ke False saat dataset belum tersedia (mode testing — chatbot menjawab
# sebagai model Gemini biasa tanpa konteks data).
# Set ke True ketika dataset sudah siap untuk mengaktifkan kembali grounding.
GROUNDING_ENABLED: bool = False

DOMAIN_HEADER = """
Kamu memiliki akses ke data berikut dari dashboard Gebang Thunder.
Gunakan data ini sebagai SATU-SATUNYA sumber kebenaran untuk menjawab pertanyaan.
Jangan mengarang atau mengasumsikan informasi yang tidak ada di bawah ini.
""".strip()


def build_grounding_context(df: pd.DataFrame | None, agg_context: str) -> str:
    """
    Bangun string context lengkap untuk dikirim ke Gemini.

    Parameters
    ----------
    df : pd.DataFrame | None
        DataFrame dataset (None jika belum tersedia).
    agg_context : str
        Hasil pre-agregasi dari data_loader._build_agg_context().

    Returns
    -------
    str
        String context yang siap disertakan dalam prompt Gemini.
        String kosong jika GROUNDING_ENABLED = False (mode testing).
    """
    # ── Mode testing: grounding dinonaktifkan sementara ───────────────────────
    if not GROUNDING_ENABLED:
        logger.info("Grounding dinonaktifkan (GROUNDING_ENABLED=False). Mode testing aktif.")
        return ""

    if df is None:
        logger.warning("Dataset tidak tersedia — grounding context minimal.")
        return f"{DOMAIN_HEADER}\n\n{agg_context}"

    context_parts = [
        DOMAIN_HEADER,
        "",
        agg_context,
    ]

    # Jika dataset kecil (< 5000 baris), sertakan full data sebagai CSV string
    # agar model bisa menjawab pertanyaan spesifik per-baris
    if len(df) <= 5000:
        context_parts.append("\n=== DATA LENGKAP (CSV) ===")
        context_parts.append(df.to_csv(index=False))
    else:
        # Untuk dataset lebih besar, andalkan agregasi saja
        logger.info("Dataset > 5000 baris — hanya agregasi yang disertakan sebagai context.")

    return "\n".join(context_parts)
