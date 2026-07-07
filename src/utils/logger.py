"""
logger.py — Logging internal ThunderChat
==========================================
Log disimpan ke file lokal dan console — TIDAK tampil ke publik/user.
Sesuai NFR Section 8: "logging dasar (request, error, key yang dipakai)
disimpan secara internal saja".
"""

import logging
import os
from datetime import datetime

# ── Direktori log ─────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"thunderchat_{datetime.now().strftime('%Y%m%d')}.log")

# ── Setup root logger (sekali saja) ──────────────────────────────────────────
_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler: file
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler: console (untuk Streamlit Cloud log viewer)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root = logging.getLogger("thunderchat")
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Dapatkan logger dengan namespace `thunderchat.<name>`.

    Parameters
    ----------
    name : str
        Biasanya `__name__` dari modul yang memanggil.

    Returns
    -------
    logging.Logger
    """
    _configure_root_logger()
    # Normalise: hapus prefix "src." agar log lebih bersih
    clean_name = name.replace("src.", "")
    return logging.getLogger(f"thunderchat.{clean_name}")
