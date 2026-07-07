"""
data_loader.py — Load & preprocessing CSV dataset
===================================================
Schema-agnostic: auto-detect kolom via pandas.
Tidak ada hardcode nama kolom spesifik (sesuai catatan Section 6 PRD).

Di-cache via @st.cache_data agar hanya load satu kali saat app start.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
from src.utils.logger import get_logger

logger = get_logger(__name__)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")


@st.cache_data(show_spinner=False)
def load_dataset() -> tuple[pd.DataFrame | None, str]:
    """
    Load dataset CSV dan bangun agregasi umum untuk grounding.

    Returns
    -------
    tuple[pd.DataFrame | None, str]
        - df   : DataFrame asli (None jika dataset belum ada)
        - agg  : String berisi hasil agregasi/statistik deskriptif untuk context
    """
    if not os.path.exists(DATASET_PATH):
        logger.warning(f"Dataset tidak ditemukan di: {DATASET_PATH}")
        return None, _placeholder_agg_context()

    try:
        df = pd.read_csv(DATASET_PATH)
        logger.info(f"Dataset loaded: {df.shape[0]} baris, {df.shape[1]} kolom.")

        agg_context = _build_agg_context(df)
        return df, agg_context

    except Exception as e:
        logger.error(f"Gagal load dataset: {e}")
        return None, _placeholder_agg_context()


def _build_agg_context(df: pd.DataFrame) -> str:
    """
    Bangun representasi tekstual dataset untuk context Gemini.
    Schema-agnostic: semua agregasi berdasarkan tipe kolom yang terdeteksi otomatis.

    Pendekatan:
    - Statistik deskriptif untuk kolom numerik
    - Value counts untuk kolom kategorik
    - Sample data (head) untuk gambaran umum
    """
    lines: list[str] = []

    lines.append("=== INFORMASI DATASET ===")
    lines.append(f"Jumlah baris  : {df.shape[0]:,}")
    lines.append(f"Jumlah kolom  : {df.shape[1]}")
    lines.append(f"Nama kolom    : {', '.join(df.columns.tolist())}")
    lines.append("")

    # ── Statistik deskriptif kolom numerik ────────────────────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        lines.append("=== STATISTIK NUMERIK ===")
        desc = df[numeric_cols].describe().round(2)
        lines.append(desc.to_string())
        lines.append("")

    # ── Value counts kolom kategorik (top 10) ─────────────────────────────────
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical_cols:
        lines.append("=== DISTRIBUSI KOLOM KATEGORIK ===")
        for col in categorical_cols[:5]:  # batasi 5 kolom pertama agar tidak overflow token
            vc = df[col].value_counts().head(10)
            lines.append(f"\nKolom '{col}' (top 10):")
            lines.append(vc.to_string())
        lines.append("")

    # ── Sample data (5 baris pertama) ────────────────────────────────────────
    lines.append("=== CONTOH DATA (5 BARIS PERTAMA) ===")
    lines.append(df.head(5).to_string(index=False))

    return "\n".join(lines)


def _placeholder_agg_context() -> str:
    """Placeholder context saat dataset belum tersedia."""
    return (
        "=== INFORMASI DATASET ===\n"
        "Dataset belum tersedia. Harap letakkan file dataset.csv di folder data/.\n"
        "ThunderChat belum dapat menjawab pertanyaan berbasis data."
    )
