# ThunderChat ⚡

> Chatbot analitik berbasis Gemini API untuk dashboard **Gebang Thunder**.

ThunderChat adalah web aplikasi yang memungkinkan pengguna bertanya secara *natural language* tentang dataset Gebang Thunder dan mendapatkan jawaban naratif yang akurat — tanpa perlu menavigasi visual Power BI secara manual.

---

## 🚀 Quick Start (Development Lokal)

### 1. Clone & masuk ke direktori
```bash
git clone <repo-url>
cd thunder-chat
```

### 2. Setup environment

**Menggunakan Conda (direkomendasikan):**
```bash
conda env create -f environment.yml
conda activate thunderchat
```

**Atau menggunakan pip:**
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi API Key

Salin template secrets dan isi dengan API key Gemini Anda:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml dan isi nilai API key yang sebenarnya
```

### 4. Letakkan dataset

Salin file `dataset.csv` ke folder `data/`:
```
data/dataset.csv
```

### 5. Jalankan aplikasi
```bash
streamlit run app.py
```

---

## 📁 Struktur Repository

```
thunder-chat/
├── app.py                    # Entry point Streamlit
├── src/
│   ├── config.py             # Load secrets & daftar API key
│   ├── gemini_client.py      # Wrapper Gemini API: rotasi key + error handling
│   ├── data_loader.py        # Load & preprocessing CSV (pandas/numpy/scikit-learn)
│   ├── grounding.py          # Bangun prompt/context grounding
│   ├── ui/
│   │   ├── styles.py         # Custom CSS (shadcn/ui, color palette, font Inter)
│   │   └── components.py     # Komponen UI (chat bubble, input, suggested prompts)
│   └── utils/
│       └── logger.py         # Logging internal (tidak tampil ke publik)
├── data/
│   └── dataset.csv           # Dataset grounding (ad hoc, statis) — TIDAK di-commit jika sensitif
├── assets/
│   ├── loading.json          # File animasi Lottie
│   ├── icons/                # Icon logo & elemen UI
│   └── fonts/                # File font Inter (opsional, CDN dipakai by default)
├── .streamlit/
│   ├── config.toml           # Konfigurasi tema Streamlit
│   └── secrets.toml          # API keys — JANGAN di-commit (.gitignore)
├── .gitignore
├── requirements.txt           # Untuk deployment ke Streamlit Community Cloud
├── environment.yml            # Conda environment untuk development lokal
└── README.md
```

---

## 🔑 Konfigurasi API Key

ThunderChat menggunakan **multi-key round-robin** untuk memaksimalkan kapasitas gratis Gemini API.

**Format `secrets.toml`:**
```toml
[gemini]
key_1 = "AIza..."
key_2 = "AIza..."
key_3 = "AIza..."
```

Daftarkan 3–5 API key dari akun Google berbeda di [Google AI Studio](https://aistudio.google.com/).

---

## 🛡️ Keamanan

- API key **wajib** disimpan via Streamlit Secrets — tidak pernah hardcoded.
- File `secrets.toml` dan `.env` sudah dikecualikan dari Git via `.gitignore`.
- Log internal tidak pernah ditampilkan ke publik/user.

---

## 📦 Tech Stack

| Komponen | Teknologi |
|---|---|
| Framework | Streamlit |
| LLM | Gemini 3.5 Flash via `google-genai` |
| Data Processing | pandas, numpy, scikit-learn |
| UI Components | Custom CSS + streamlit-shadcn-ui |
| Loading Animation | streamlit-lottie |
| Font | Inter (Google Fonts) |
| Deploy Target | Streamlit Community Cloud |

---

## 🔗 Deploy ke Streamlit Community Cloud

1. Push repo ke GitHub (pastikan `secrets.toml` **tidak** ikut ter-push).
2. Buka [share.streamlit.io](https://share.streamlit.io) → New app → pilih repo ini.
3. Set **Main file path**: `app.py`.
4. Buka **Settings → Secrets** → masukkan isi `secrets.toml` di sana.
5. Deploy.

---

## 📋 Dependensi Terbuka

- Dataset (`data/dataset.csv`) belum diserahkan — wajib ada sebelum app berfungsi penuh.
- Suggested prompts di `components.py` perlu diperbarui setelah skema kolom dataset final diketahui.
- File animasi Lottie (`assets/loading.json`) perlu dipilih/dibuat sesuai tone brand.
